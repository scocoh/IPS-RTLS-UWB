# Name: websocket_historical.py
# Version: 0.1.9
# Created: 250513
# Modified: 250516
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS HistoricalData WebSocket server on port 8003
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/websocket_historical.py
# Version: 0.1.9 - Moved manager.start() to lifespan to ensure heartbeat loop runs, bumped from 0.1.8
# Previous: Adjusted proximity time window to 15 minutes, bumped from 0.1.6
# Previous: Improved proximity logic to find closest timestamp within 5 minutes, bumped from 0.1.5
# Previous: Fixed schema mismatch in FetchHistoricalData queries (removed CNF, GWID, BAT; simplified range_hallway query), bumped from 0.1.4
# Previous: Added FetchHistoricalData to connect to ParcoRTLSHistR, ParcoRTLSHistO, and ParcoRTLSHistP, bumped from 0.1.3
# Previous: Removed websockets.serve, updated logging to YYMMDD HHMMSS, bumped from 0.1.2
# Previous: Updated RESOURCE_TYPE to 11 for HistoricalData, bumped from 0.1.1
# Previous: Initial implementation for HistoricalData with subcategory filtering, tlkresourcetypes integration
# Note: The tlkresourcetypes and tlkresources configurations defined here (i_typ_res=11 for HistoricalData, port 8003, etc.) should be the default for future deployments.
# Note: This server uses ParcoRTLSHistR (2D/3D), ParcoRTLSHistO (range/hallway), and ParcoRTLSHistP (proximity) for historical data, while configuration uses ParcoRTLSMaint.
# Note: Supports NewTriggerViewer and NewTriggerDemo.js by providing historical GISData and TriggerEvent messages with subcategory filtering (e.g., R-2D, R-3D).
# Note: IP address (192.168.210.226) is hardcoded; inspired by DataStream.TCPIP and Resource.TCPIP properties from the VB.NET ParcoRTLS SDK, this could be made configurable in the future.

import asyncio
import logging
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import json
from datetime import datetime, timedelta
from .manager import Manager
from .sdk_client import SDKClient
from .models import HeartBeat, Response, ResponseType, Request, Tag
from .enums import RequestType, eMode
from .constants import REQUEST_TYPE_MAP, NEW_REQUEST_TYPES

# Configure logging with YYMMDD HHMMSS timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%y%m%d %H%M%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Feature flags
ENABLE_MULTI_PORT = True

# Stream type for this server
STREAM_TYPE = "HistoricalData"
RESOURCE_TYPE = 11  # Historical Data FS

# Database connection strings
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"  # For configuration
HIST_R_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSHistR"  # 2D/3D data
HIST_O_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSHistO"  # Range/hallway data
HIST_P_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSHistP"  # Proximity data

async def filter_data(data: dict, subcategory: str) -> dict:
    if subcategory == "R-2D" and data.get("type") in ["GISData", "Vertices"]:
        data_copy = data.copy()
        if "z" in data_copy:
            del data_copy["z"]
        if "data" in data_copy and isinstance(data_copy["data"], list):
            data_copy["data"] = [
                {k: v for k, v in item.items() if k != "z"} for item in data_copy["data"]
            ]
    return data

async def fetch_historical_data(data_type: str, tag_id: str, start_time: str, end_time: str, tag_id_2: str = None):
    """
    Fetch historical data based on data_type:
    - 2D_3D: From ParcoRTLSHistR (positionhistory).
    - range_hallway: From ParcoRTLSHistO (positionhistory).
    - proximity: From ParcoRTLSHistP (compute distance between two tags' positions within a 15-minute window).
    """
    logger.debug(f"Fetching historical data: data_type={data_type}, tag_id={tag_id}, start_time={start_time}, end_time={end_time}, tag_id_2={tag_id_2}")
    try:
        # Validate timestamps
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        if data_type == "2D_3D":
            async with asyncpg.create_pool(HIST_R_CONN_STRING) as pool:
                async with pool.acquire() as conn:
                    query = """
                        SELECT X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z
                        FROM positionhistory
                        WHERE X_ID_DEV = $1 AND D_POS_BGN BETWEEN $2 AND $3
                        ORDER BY D_POS_BGN
                    """
                    rows = await conn.fetch(query, tag_id, start_dt, end_dt)
                    return [{"tag_id": r["x_id_dev"], "timestamp": r["d_pos_bgn"].isoformat(),
                             "x": r["n_x"], "y": r["n_y"], "z": r["n_z"]} for r in rows]

        elif data_type == "range_hallway":
            async with asyncpg.create_pool(HIST_O_CONN_STRING) as pool:
                async with pool.acquire() as conn:
                    query = """
                        SELECT X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z
                        FROM positionhistory
                        WHERE X_ID_DEV = $1 AND D_POS_BGN BETWEEN $2 AND $3
                        ORDER BY D_POS_BGN
                    """
                    rows = await conn.fetch(query, tag_id, start_dt, end_dt)
                    return [{"tag_id": r["x_id_dev"], "timestamp": r["d_pos_bgn"].isoformat(),
                             "x": r["n_x"], "y": r["n_y"], "z": r["n_z"]} for r in rows]

        elif data_type == "proximity":
            if not tag_id_2:
                logger.error("Proximity data requires a second tag_id")
                return []
            async with asyncpg.create_pool(HIST_P_CONN_STRING) as pool:
                async with pool.acquire() as conn:
                    # Fetch positions for both tags
                    query = """
                        SELECT X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z
                        FROM positionhistory
                        WHERE X_ID_DEV IN ($1, $2) AND D_POS_BGN BETWEEN $3 AND $4
                        ORDER BY D_POS_BGN
                    """
                    rows = await conn.fetch(query, tag_id, tag_id_2, start_dt, end_dt)
                    positions = [{"tag_id": r["x_id_dev"], "timestamp": r["d_pos_bgn"],
                                  "x": r["n_x"], "y": r["n_y"], "z": r["n_z"]} for r in rows]

                    tag1_positions = [p for p in positions if p["tag_id"] == tag_id]
                    tag2_positions = [p for p in positions if p["tag_id"] == tag_id_2]
                    result = []

                    # Find closest timestamp in tag2_positions for each tag1 position
                    for p1 in tag1_positions:
                        t1 = p1["timestamp"]
                        closest_p2 = None
                        min_time_diff = timedelta(minutes=15)  # 15-minute window
                        for p2 in tag2_positions:
                            t2 = p2["timestamp"]
                            time_diff = abs(t1 - t2)
                            if time_diff <= min_time_diff:
                                closest_p2 = p2
                                min_time_diff = time_diff
                        if closest_p2:
                            # Calculate Euclidean distance (3D)
                            distance = ((p1["x"] - closest_p2["x"])**2 + (p1["y"] - closest_p2["y"])**2 + (p1["z"] - closest_p2["z"])**2)**0.5
                            result.append({
                                "tag_id_1": tag_id,
                                "tag_id_2": tag_id_2,
                                "timestamp": t1.isoformat(),
                                "distance": round(distance, 2)
                            })
                    return result

        else:
            logger.error(f"Unsupported data_type: {data_type}")
            return []

    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}\n{traceback.format_exc()}")
        return []

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan: Initializing DB pool")
    try:
        # Use ParcoRTLSMaint for configuration (tlkresources)
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            logger.debug("DB pool created successfully")
            async with pool.acquire() as conn:
                managers = await conn.fetch("SELECT X_NM_RES, i_typ_res FROM tlkresources WHERE i_typ_res = $1", RESOURCE_TYPE)
                logger.debug(f"Queried tlkresources, found {len(managers)} managers for i_typ_res={RESOURCE_TYPE}")
                for manager in managers:
                    logger.info(f"Manager {manager['x_nm_res']} (type {manager['i_typ_res']}) ready")
                    # Start the manager instance for each resource type
                    manager_name = manager['x_nm_res']
                    if manager_name not in _MANAGER_INSTANCES:
                        manager_instance = Manager(manager_name, zone_id=None)
                        _MANAGER_INSTANCES[manager_name] = manager_instance
                        logger.debug(f"Starting manager {manager_name}")
                        await manager_instance.start()
                        logger.debug(f"Manager {manager_name} started successfully")
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}\n{traceback.format_exc()}")
        raise
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.210.226:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
logger.debug("CORS middleware added with allow_origins: http://192.168.210.226:3000")

_MANAGER_INSTANCES = {}
_WEBSOCKET_CLIENTS = {}

@app.websocket("/ws/{manager_name}")
async def websocket_endpoint_historical(websocket: WebSocket, manager_name: str):
    logger.info(f"WebSocket connection attempt for /ws/{manager_name} from {websocket.client.host}:{websocket.client.port}")
    async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
        async with pool.acquire() as conn:
            manager_info = await conn.fetchrow(
                "SELECT i_typ_res FROM tlkresources WHERE X_NM_RES = $1 AND i_typ_res = $2", 
                manager_name, RESOURCE_TYPE)
            if not manager_info:
                logger.error(f"Manager {manager_name} not found or invalid type")
                await websocket.close(code=1008, reason="Manager not found")
                return
    sdk_client = None
    client_id = None
    is_disconnected = False
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for /ws/{manager_name}")
        if manager_name not in _MANAGER_INSTANCES:
            manager = Manager(manager_name, zone_id=None)
            _MANAGER_INSTANCES[manager_name] = manager
        else:
            manager = _MANAGER_INSTANCES[manager_name]
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        sdk_client = SDKClient(websocket, client_id)
        sdk_client.parent = manager
        manager.sdk_clients[client_id] = sdk_client
        sdk_client.start_q_timer()

        if manager_name not in _WEBSOCKET_CLIENTS:
            _WEBSOCKET_CLIENTS[manager_name] = []
        _WEBSOCKET_CLIENTS[manager_name].append(sdk_client)

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message from client {client_id}: {data}")
                json_data = json.loads(data)
                msg_type = json_data.get("type", "")
                subcategory = json_data.get("subcategory", "R-3D")

                if msg_type == "HeartBeat":
                    hb = HeartBeat(ticks=json_data["ts"])
                    sdk_client.heartbeat = hb.ticks
                    await websocket.send_text(json.dumps({"type": "HeartBeat", "ts": hb.ticks}))
                    logger.debug(f"Processed HeartBeat for client {client_id}, ts: {hb.ticks}")
                    continue

                elif msg_type == "request":
                    request_type = json_data.get("request", "")
                    req_id = json_data.get("reqid", "")

                    if request_type == "FetchHistoricalData":
                        data_type = json_data.get("data_type", "2D_3D")
                        tag_id = json_data.get("tag_id")
                        start_time = json_data.get("start_time")
                        end_time = json_data.get("end_time")
                        tag_id_2 = json_data.get("tag_id_2") if data_type == "proximity" else None
                        if not all([tag_id, start_time, end_time]):
                            resp = Response(
                                response_type=ResponseType.Unknown,
                                req_id=req_id,
                                message="Missing required fields: tag_id, start_time, end_time"
                            )
                            await websocket.send_text(resp.to_json())
                            continue
                        data = await fetch_historical_data(data_type, tag_id, start_time, end_time, tag_id_2)
                        response = {
                            "type": "HistoricalData",
                            "data_type": data_type,
                            "data": data,
                            "reqid": req_id
                        }
                        await websocket.send_text(json.dumps(response))
                        logger.info(f"Sent historical data response to client {client_id}: {response}")
                        continue

                    req_type = REQUEST_TYPE_MAP.get(request_type)
                    if not req_type:
                        resp = Response(
                            response_type=ResponseType.Unknown,
                            req_id=req_id,
                            message=f"Invalid request type: {request_type}"
                        )
                        await websocket.send_text(resp.to_json())
                        logger.debug(f"Sent error response to client {client_id}: {resp.to_json()}")
                        continue

                    req = Request(
                        req_type=req_type,
                        req_id=req_id,
                        tags=[Tag(id=tag["id"], send_payload_data=tag["data"] == "true") 
                              for tag in json_data.get("params", [])]
                    )
                    sdk_client.request_msg = req
                    resp = Response(response_type=ResponseType(req.req_type.value), req_id=req_id)

                    if req.req_type == RequestType.BeginStream:
                        if not req.tags:
                            resp.message = "Begin stream requests must contain at least one tag."
                        else:
                            for t in req.tags:
                                sdk_client.add_tag(t.id, t)
                        sdk_client.sent_begin_msg = True
                        sdk_client.sent_req = True
                        await websocket.send_text(resp.to_json())
                        if resp.message:
                            await manager.close_client(sdk_client)
                            break
                    elif req.req_type == RequestType.EndStream:
                        await websocket.send_text(resp.to_json())
                        await manager.close_client(sdk_client)
                        break
                    else:
                        resp.message = "Request not supported in HistoricalData stream."
                        await websocket.send_text(resp.to_json())

                elif msg_type == "GISData":
                    filtered_data = await filter_data(json_data, subcategory)
                    await manager.parser_data_arrived(filtered_data)
                    await websocket.send_text(json.dumps(filtered_data))
                    logger.debug(f"Sent filtered GISData to client {client_id}: {filtered_data}")
                elif msg_type == "TriggerEvent":
                    filtered_data = await filter_data(json_data, subcategory)
                    await websocket.send_text(json.dumps(filtered_data))
                    logger.debug(f"Sent TriggerEvent to client {client_id}: {filtered_data}")
                else:
                    logger.warning(f"Unknown message type from client {client_id}: {msg_type}")

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for /ws/{manager_name}")
                is_disconnected = True
                await sdk_client.close()
                break
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}\n{traceback.format_exc()}")
                break
    finally:
        if sdk_client and not is_disconnected:
            await sdk_client.close()
        if client_id in manager.sdk_clients:
            del manager.sdk_clients[client_id]
        if manager_name in _WEBSOCKET_CLIENTS and sdk_client in _WEBSOCKET_CLIENTS[manager_name]:
            _WEBSOCKET_CLIENTS[manager_name].remove(sdk_client)