import asyncio
import logging
import xml.etree.ElementTree as ET  # Add this import
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncpg
from .manager import Manager
from .sdk_client import SDKClient
from .utils import MessageUtilities
from .models import HeartBeat, Response, ResponseType, Request
from .enums import RequestType, eMode  # Add eMode import

logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI()

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    async with asyncpg.create_pool("host=localhost user=postgres password=parco dbname=ParcoRTLSMaint") as pool:
        async with pool.acquire() as conn:
            managers = await conn.fetch("SELECT X_NM_RES FROM tlkresources")
            for manager in managers:
                name = manager['x_nm_res']
                logger.info(f"Manager {name} ready to accept connections")
    yield  # Application runs here
    # Shutdown logic (optional)
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# WebSocket Endpoint
@app.websocket("/ws/{manager_name}")
async def websocket_endpoint(websocket: WebSocket, manager_name: str):
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {websocket.client.host}:{websocket.client.port}")
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        manager = Manager(manager_name)
        await manager.start()
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager
        manager.sdk_clients[client_id] = sdk_client
        asyncio.create_task(sdk_client.q_timer())
        asyncio.create_task(manager.heartbeat_loop())

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data}")
                sdk_client.buffer += data

                if len(sdk_client.buffer) <= len(MessageUtilities.XMLDefTag):
                    continue

                messages = sdk_client.buffer.split(MessageUtilities.XMLDefTag)
                xml_def_frag = False
                xml_def_frag_content = ""

                for i in range(len(messages)):
                    msg = messages[i]
                    if len(msg) > 0 and MessageUtilities.ParcoEndTag in msg:
                        if i == len(messages) - 1:
                            end_tag_pos = msg.index(MessageUtilities.ParcoEndTag) + len(MessageUtilities.ParcoEndTag)
                            if len(msg) > end_tag_pos:
                                xml_def_frag = True
                                xml_def_frag_content = msg[end_tag_pos:]
                                msg = msg[:end_tag_pos]

                        if "<type>HeartBeat</type>" in msg:
                            root = ET.fromstring(MessageUtilities.XMLDefTag + msg)
                            ticks = int(root.find("ts").text)
                            sdk_client.heartbeat = ticks
                            await websocket.send_text(MessageUtilities.XMLDefTag + msg)
                            logger.debug(f"Sent HeartBeat response: {MessageUtilities.XMLDefTag + msg}")
                        else:
                            if "<type>response</type>" in msg:
                                resp = Response.from_xml(MessageUtilities.XMLDefTag + msg)
                                if sdk_client.parent.response_callback:
                                    await sdk_client.parent.response_callback(resp)
                            elif "<type>HeartBeat</type>" not in msg:
                                req = Request.from_xml(MessageUtilities.XMLDefTag + msg)
                                sdk_client.request_msg = req
                                resp = Response(response_type=ResponseType(req.req_type.value), req_id=req.req_id)

                                if req.req_type == RequestType.BeginStream:
                                    if not sdk_client.sent_begin_msg:
                                        if manager.mode == eMode.Stream:
                                            pass
                                        else:
                                            if not req.tags:
                                                resp.message = "Begin stream requests must contain at least one tag for Subscription resources."
                                            else:
                                                for t in req.tags:
                                                    sdk_client.add_tag(t.id, t)
                                        sdk_client.sent_begin_msg = True
                                        sdk_client.sent_req = True
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent BeginStream response: {resp.to_xml()}")
                                        if resp.message:
                                            await manager.close_client(sdk_client)
                                            logger.warning(f"SDK Client {client_id} with reqid={resp.req_id} failed to subscribe with 0 items")
                                    else:
                                        resp.message = "Begin stream requests not allowed on existing streams"
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent BeginStream error response: {resp.to_xml()}")
                                elif req.req_type == RequestType.EndStream:
                                    await websocket.send_text(resp.to_xml())
                                    logger.debug(f"Sent EndStream response: {resp.to_xml()}")
                                    await manager.close_client(sdk_client)
                                elif req.req_type == RequestType.AddTag:
                                    if manager.mode == eMode.Stream:
                                        resp.message = "Request to add tag not valid in this stream resource."
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent AddTag error response: {resp.to_xml()}")
                                    else:
                                        for t in req.tags:
                                            sdk_client.add_tag(t.id, t)
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent AddTag response: {resp.to_xml()}")
                                elif req.req_type == RequestType.RemoveTag:
                                    if manager.mode == eMode.Stream:
                                        resp.message = "Request to remove tag not valid in this stream resource."
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent RemoveTag error response: {resp.to_xml()}")
                                    else:
                                        for t in req.tags:
                                            sdk_client.remove_tag(t.id)
                                        await websocket.send_text(resp.to_xml())
                                        logger.debug(f"Sent RemoveTag response: {resp.to_xml()}")
                                        if sdk_client.count == 0:
                                            await manager.close_client(sdk_client)
                                else:
                                    resp.message = "Unrecognized request."
                                    await websocket.send_text(resp.to_xml())
                                    logger.warning(f"Manager {manager_name}: Unrecognized SDK request ({req.req_type}) from {client_id}")
                                    logger.debug(f"Sent unrecognized request response: {resp.to_xml()}")

                sdk_client.buffer = xml_def_frag_content if xml_def_frag else MessageUtilities.XMLDefTag + messages[-1] if messages[-1] and MessageUtilities.ParcoEndTag not in messages[-1] else ""

            except WebSocketDisconnect as e:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}: {str(e)}")
                manager.sdk_child_count -= 1
                if client_id in manager.sdk_clients:
                    del manager.sdk_clients[client_id]
                if manager.log_sdk_connections:
                    logger.info(f"SDK client connection closed - {client_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler for /ws/{manager_name}: {str(e)}")
                await websocket.close(code=1011, reason=f"Server error: {str(e)}")
                break

    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection for /ws/{manager_name}: {str(e)}")
        await websocket.close(code=1011, reason=f"Server error: {str(e)}")