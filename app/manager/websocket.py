# Version: 250327 /home/parcoadmin/parco_fastapi/app/manager/websocket.py 1.0.14
# 
# Websocket Module for Manager
#   
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncpg
from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
import json

# Configure logging to ensure DEBUG level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

REQUEST_TYPE_MAP = {
    "BeginStream": RequestType.BeginStream,
    "EndStream": RequestType.EndStream,
    "AddTag": RequestType.AddTag,
    "RemoveTag": RequestType.RemoveTag
}

_MANAGER_INSTANCES = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing DB pool")
    try:
        async with asyncpg.create_pool("postgresql://parcoadmin:parcoMCSE04106!@192.168.210.231:5432/ParcoRTLSMaint") as pool:
            logger.debug("DB pool created successfully")
            async with pool.acquire() as conn:
                logger.debug("Acquired DB connection, querying tlkresources")
                managers = await conn.fetch("SELECT X_NM_RES FROM tlkresources")
                logger.debug(f"Queried tlkresources, found {len(managers)} managers")
                for manager in managers:
                    name = manager['x_nm_res']
                    logger.info(f"Manager {name} ready to accept connections")
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        raise
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint(websocket: WebSocket, manager_name: str):
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {websocket.client.host}:{websocket.client.port}")
    async with asyncpg.create_pool("postgresql://parcoadmin:parcoMCSE04106!@192.168.210.231:5432/ParcoRTLSMaint") as pool:
        async with pool.acquire() as conn:
            res = await conn.fetchval("SELECT COUNT(*) FROM tlkresources WHERE X_NM_RES = $1", manager_name)
            if not res:
                logger.error(f"Manager {manager_name} not found in tlkresources")
                await websocket.close(code=1008, reason="Manager not found")
                return
    sdk_client = None
    client_id = None
    is_disconnected = False
    try:
        logger.debug(f"Attempting to accept WebSocket for {manager_name}")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        logger.debug(f"Creating or retrieving Manager instance for {manager_name}")
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name)
            await manager.start()
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        logger.debug(f"Creating SDKClient for {client_id}")
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager
        manager.sdk_clients[client_id] = sdk_client
        logger.debug(f"Starting q_timer for {client_id}")
        sdk_client.start_q_timer()

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")

                try:
                    json_data = json.loads(data)
                    msg_type = json_data.get("type", "")
                    logger.debug(f"Message type for client {client_id}: {msg_type}")

                    if msg_type == "HeartBeat":
                        hb = HeartBeat(ticks=json_data["ts"])
                        sdk_client.heartbeat = hb.ticks
                        logger.debug(f"Processed HeartBeat for client {client_id}, ts: {hb.ticks}")
                        continue

                    elif msg_type == "request":
                        request_type_str = json_data.get("request", "")
                        logger.debug(f"Received request type for client {client_id}: {request_type_str}")
                        req_type = REQUEST_TYPE_MAP.get(request_type_str)
                        if not req_type:
                            logger.error(f"Invalid RequestType for client {client_id}: {request_type_str}")
                            resp = Response(
                                response_type=ResponseType.Unknown,
                                req_id=json_data.get("reqid", ""),
                                message=f"Invalid request type: {request_type_str}"
                            )
                            await websocket.send_text(resp.to_json())
                            logger.debug(f"Sent error response to client {client_id}: {resp.to_json()}")
                            continue
                        req = Request(
                            req_type=req_type,
                            req_id=json_data["reqid"],
                            tags=[Tag(id=tag["id"], send_payload_data=tag["data"] == "true") for tag in json_data.get("params", [])]
                        )
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
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent BeginStream response to client {client_id}: {resp.to_json()}")
                                if resp.message:
                                    await manager.close_client(sdk_client)
                                    break
                            else:
                                resp.message = "Begin stream requests not allowed on existing streams"
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent BeginStream error response to client {client_id}: {resp.to_json()}")
                        elif req.req_type == RequestType.EndStream:
                            await websocket.send_text(resp.to_json())
                            logger.debug(f"Sent EndStream response to client {client_id}: {resp.to_json()}")
                            await manager.close_client(sdk_client)
                            break
                        elif req.req_type == RequestType.AddTag:
                            if manager.mode == eMode.Stream:
                                resp.message = "Request to add tag not valid in this stream resource."
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent AddTag error response to client {client_id}: {resp.to_json()}")
                            else:
                                for t in req.tags:
                                    sdk_client.add_tag(t.id, t)
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent AddTag response to client {client_id}: {resp.to_json()}")
                        elif req.req_type == RequestType.RemoveTag:
                            if manager.mode == eMode.Stream:
                                resp.message = "Request to remove tag not valid in this stream resource."
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent RemoveTag error response to client {client_id}: {resp.to_json()}")
                            else:
                                for t in req.tags:
                                    sdk_client.remove_tag(t.id)
                                await websocket.send_text(resp.to_json())
                                logger.debug(f"Sent RemoveTag response to client {client_id}: {resp.to_json()}")
                                if sdk_client.count == 0:
                                    await manager.close_client(sdk_client)
                                    break
                        else:
                            resp.message = "Unrecognized request."
                            await websocket.send_text(resp.to_json())
                            logger.warning(f"Manager {manager_name}: Unrecognized SDK request ({req.req_type}) from {client_id}")
                            logger.debug(f"Sent unrecognized request response to client {client_id}: {resp.to_json()}")

                    else:
                        logger.warning(f"Unknown message type from client {client_id}: {msg_type}")

                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON message from client {client_id}: {data}")
                    continue

            except WebSocketDisconnect as e:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}: {str(e)}")
                is_disconnected = True
                manager.sdk_child_count -= 1
                if client_id in manager.sdk_clients:
                    del manager.sdk_clients[client_id]
                if manager.log_sdk_connections:
                    logger.info(f"SDK client connection closed - {client_id}")
                # NEW: Ensure q_timer is canceled immediately
                if sdk_client is not None:
                    await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler for /ws/{manager_name}: {str(e)}")
                # NEW: Ensure q_timer is canceled immediately
                if sdk_client is not None:
                    await sdk_client.close()
                break

    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection for /ws/{manager_name}: {str(e)}")
    finally:
        if sdk_client is not None and not is_disconnected:
            await sdk_client.close()
            if client_id in manager.sdk_clients:
                del manager.sdk_clients[client_id]