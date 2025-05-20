# Name: manager.py
# Version: 0.1.13
# Created: 971201
# Modified: 250519
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/manager.py
# Version: 0.1.13 - Replaced RotatingFileHandler with LineLimitedFileHandler for 999-line limit, fixed f-string and trigge typo in process_sim_message, fixed selftoupper typo and syntax error in __init__, bumped from 0.1.12
# Previous: Enhanced heartbeat logging to trace sources, bumped from 0.1.11
# Previous: Disabled client heartbeat responses, tightened server-side throttling, added heartbeat source logging, bumped from 0.1.10
# Previous: Fixed heartbeat timestamp, tightened rate-limiting to 1 per 30s, prevented feedback loops, bumped from 0.1.9
# Previous: Added explicit flush() calls after key log messages to ensure log writing, bumped from 0.1.8
# Previous: Added rate-limiting for incoming heartbeat responses from SDK clients to prevent feedback loop, bumped from 0.1.7
# Previous: Fixed rapid heartbeat issue by adding rate-limiting for SDK clients in heartbeat_loop, bumped from 0.1.6
# Previous: Fixed NameError by adding deque import, added file logging with rotation, forwarded GISData messages to WebSocket clients, bumped from 0.1.5
# Previous: Restructured heartbeat_loop to ensure 60-second sleep interval and clean up stale clients, bumped from 0.1.4
# Previous: Enhanced process_sim_message with logging and validation; Fixed rapid heartbeat loop in heartbeat_loop, bumped from 0.1.3
# Previous: Skip trigger loading in start() if zone_id is None to avoid HTTP 422 error, bumped from 0.1.2
# Documentation: PortRedirect handling implemented in websocket_control.py (v0.1.38) for simulator redirection to RealTimeManager on port 8002
# Previous: Added import traceback to fix undefined variable error, bumped from 0.1.1
# Previous: Added debug logging to start() method, bumped from 0.1.0
# Previous: Suppressed WhileIn events for a tag triggering its own portable trigger, enhanced event message, bumped from 1.0.44 (1.0.45)
# Previous: Reverted to using FastAPIService for trigger loading after fix, bumped from 1.0.43 (1.0.44)
# Previous: Fixed trigger loading using direct HTTP request, bumped from 1.0.42 (1.0.43)
# Previous: Forced logging output for debugging, added WebSocket client management and Sim message processing, bumped from 1.0.41 (1.0.42)
# Previous: Enhanced logging for Sim messages, trigger loading, and event generation, bumped from 1.0.40 (1.0.41)
# Previous: Updated load_triggers to use FastAPIService.get_trigger_details, bumped from 1.0.39 (1.0.40)
# Previous: Integrated FastAPIService for trigger loading, added TODOs for configuration (1.0.39)
# Previous: Added dynamic zone assignment for portable triggers (1.0.37)
# Previous: Added PortableTrigger support, updated trigger movement logic (1.0.36)
# Previous: Send TriggerEvent to all subscribed clients regardless of zone_id (1.0.35)
# Previous: Ensure triggers are loaded for GISData zone_id (1.0.34)
# Previous: Fixed zone_id handling in parser_data_arrived and ensured it's preserved in Sim messages (1.0.33)

from typing import Dict, List
import asyncpg
import asyncio
from datetime import datetime, timedelta
import httpx
import traceback
from .models import GISData, HeartBeat, Response, ResponseType, Ave, Tag
from .enums import eMode, eRunState, TriggerDirections
from .trigger import Trigger
from .portable_trigger import PortableTrigger
from .sdk_client import SDKClient
from .region import Region3D, Region3DCollection
from .utils import FASTAPI_BASE_URL, track_metrics
from .data_processor import DataProcessor
from .fastapi_service import FastAPIService
import logging
import json
from fastapi import WebSocket
import os
from collections import deque
from .line_limited_logging import LineLimitedFileHandler

# Ensure log directory exists
LOG_DIR = "/home/parcoadmin/parco_fastapi/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging with both StreamHandler and LineLimitedFileHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# StreamHandler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

# LineLimitedFileHandler for persistent logging with line limit
file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "manager.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s:%(name)s:%(message)s'))

# Set handlers
logger.handlers = []
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.propagate = False

class Manager:
    def __init__(self, name: str, zone_id: int):
        # Core attributes for Manager instance
        self.name = name
        self.zone_id = zone_id
        self.zone_id_locked = False
        self.sdk_ip = None
        self.sdk_port = None
        self.is_ave = False
        self.ave_factor = 0.25
        self.sdk_child_count = 0
        self.mode = eMode.Subscription
        self.run_state = eRunState.Stopped
        self.send_sdk_heartbeat = True
        self.log_sdk_connections = True
        self.tag_count = 0
        self.start_date = None
        self.resrc_type = 0
        self.resrc_type_name = ""
        self.ave_hash: Dict[str, Ave] = {}
        self.sdk_clients: Dict[str, SDKClient] = {}
        self.clients: Dict[str, List[WebSocket]] = {}
        self.kill_list: List[SDKClient] = []
        self.last_heartbeat = 0
        self.conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"
        self.hist_conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSHistR"
        self.db_pool = None
        self.response_callback = None
        self.triggers: List[Trigger] = []
        self.processor = DataProcessor(min_cnf=50.0)
        self.tag_rate_counter = 0
        self.last_rate_time = asyncio.get_event_loop().time()
        self.tag_rate_timestamps: List[float] = []
        self.tcp_server = None
        self._heartbeat_task = None
        self.last_tag_time = 0
        self.simulator_active = False
        self.tag_rate = {}
        self.tag_averages: Dict[str, List[Ave]] = {}
        self.tag_averages_2d: Dict[str, List[Ave]] = {}
        self.tag_averages_3d: Dict[str, List[Ave]] = {}
        self.tag_timestamps: Dict[str, List[datetime]] = {}
        self.tag_timestamps_2d: Dict[str, List[datetime]] = {}
        self.tag_timestamps_3d: Dict[str, List[datetime]] = {}
        self.service = FastAPIService()
        # Rate-limiting for heartbeats
        self.HEARTBEAT_INTERVAL = 30.0  # Heartbeat every 30 seconds
        self.HEARTBEAT_RATE_LIMIT = 1   # Max 1 heartbeat per 30s
        self.ws_heartbeat_timestamps: Dict[str, deque] = {}  # For WebSocket clients
        self.sdk_heartbeat_timestamps: Dict[str, deque] = {}  # For SDK clients

    async def load_config_from_db(self):
        logger.debug(f"Loading config for manager {self.name} from DB")
        file_handler.flush()
        async with asyncpg.create_pool(self.conn_string) as pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT r.X_IP, r.I_PRT, r.F_AVG, r.F_FS, r.I_TYP_RES, rt.X_DSC_RES
                    FROM tlkresources r
                    JOIN tlkresourcetypes rt ON r.I_TYP_RES = rt.I_TYP_RES
                    WHERE r.X_NM_RES = $1
                    """,
                    self.name
                )
                if row:
                    self.sdk_ip = row['x_ip']
                    self.sdk_port = row['i_prt']
                    self.is_ave = row['f_avg'] if row['f_avg'] is not None else False
                    self.mode = eMode.Stream if row['f_fs'] else eMode.Subscription
                    self.resrc_type = row['i_typ_res']
                    self.resrc_type_name = row['x_dsc_res']
                    logger.debug(f"Config loaded: mode={self.mode}, ip={self.sdk_ip}, port={self.sdk_port}")
                    file_handler.flush()
                else:
                    self.sdk_ip = "127.0.0.1"
                    self.sdk_port = 5000
                    self.mode = eMode.Subscription
                    logger.debug("No config found, using defaults")
                    file_handler.flush()

    async def load_triggers(self, zone_id: int):
        logger.debug(f"Loading triggers for zone {zone_id}")
        file_handler.flush()
        try:
            triggers_data = await self.service.get_triggers_by_zone(zone_id)
            logger.debug(f"Retrieved triggers data: {triggers_data}")
            file_handler.flush()

            self.triggers = [t for t in self.triggers if t.zone_id != zone_id]
            logger.debug(f"Cleared existing triggers for zone {zone_id}, remaining triggers: {len(self.triggers)}")
            file_handler.flush()

            for trigger_data in triggers_data:
                trigger_id = trigger_data["trigger_id"]
                trigger_name = trigger_data["name"]
                direction_id = trigger_data.get("direction_id")
                is_portable = trigger_data.get("is_portable", False)
                assigned_tag_id = trigger_data.get("assigned_tag_id")
                radius_ft = trigger_data.get("radius_ft")
                z_min = trigger_data.get("z_min")
                z_max = trigger_data.get("z_max")

                direction_map = {
                    1: TriggerDirections.WhileIn,
                    2: TriggerDirections.WhileOut,
                    3: TriggerDirections.OnCross,
                    4: TriggerDirections.OnEnter,
                    5: TriggerDirections.OnExit
                }
                direction = direction_map.get(direction_id, TriggerDirections.NotSet)
                logger.debug(f"Mapping direction_id {direction_id} to {direction} for trigger {trigger_name}")
                file_handler.flush()

                if is_portable:
                    trigger = PortableTrigger(
                        tag_id=assigned_tag_id,
                        radius_ft=radius_ft,
                        z_min=z_min,
                        z_max=z_max,
                        i_trg=trigger_id,
                        name=trigger_name,
                        direction=direction,
                        zone_id=zone_id
                    )
                    logger.debug(f"Created PortableTrigger {trigger_name} for tag {assigned_tag_id}")
                    file_handler.flush()
                else:
                    trigger_details = await self.service.get_trigger_details(trigger_id)
                    logger.debug(f"Trigger details for {trigger_id}: {trigger_details}")
                    file_handler.flush()

                    regions = Region3DCollection()
                    if isinstance(trigger_details, dict) and "vertices" in trigger_details:
                        vertices = trigger_details["vertices"]
                        if vertices and len(vertices) >= 3:
                            regions = Region3DCollection.from_vertices(vertices)
                    else:
                        for detail in trigger_details:
                            if "n_min_x" in detail and "n_max_x" in detail:
                                regions.add(Region3D(
                                    min_x=detail["n_min_x"],
                                    max_x=detail["n_max_x"],
                                    min_y=detail["n_min_y"],
                                    max_y=detail["n_max_y"],
                                    min_z=detail["n_min_z"],
                                    max_z=detail["n_max_z"]
                                ))
                                logger.debug(f"Added region for trigger {trigger_id}: min=({detail['n_min_x']}, {detail['n_min_y']}, {detail['n_min_z']}), max=({detail['n_max_x']}, {detail['n_max_y']}, {detail['n_max_z']})")
                                file_handler.flush()

                    if len(regions.regions) == 0:
                        logger.warning(f"No regions loaded for trigger {trigger_name} (ID: {trigger_id})")
                        file_handler.flush()

                    trigger = Trigger(
                        i_trg=trigger_id,
                        name=trigger_name,
                        direction=direction,
                        regions=regions,
                        ignore_unknowns=False,
                        zone_id=zone_id
                    )
                self.triggers.append(trigger)
                logger.info(f"Loaded trigger {trigger_name} (ID: {trigger_id}) for zone {zone_id} with direction {direction}")
                file_handler.flush()

        except Exception as e:
            logger.error(f"Failed to fetch triggers for zone {zone_id}: {str(e)}")
            file_handler.flush()

    def get_current_zone_id(self) -> int:
        return getattr(self, 'zone_id')

    async def start(self):
        logger.debug(f"Manager {self.name} starting: Setting run_state to Starting")
        file_handler.flush()
        try:
            self.start_date = datetime.now()
            logger.info("------- Manager Started --------")
            logger.info(f"Manager starting with zone_id: {self.zone_id}")
            file_handler.flush()
            if not self.send_sdk_heartbeat:
                logger.warning("Heartbeats are turned off!")
                file_handler.flush()
            logger.debug(f"Creating DB pool with hist_conn_string: {self.hist_conn_string}")
            file_handler.flush()
            self.db_pool = await asyncpg.create_pool(self.hist_conn_string)
            logger.debug("DB pool created successfully")
            file_handler.flush()
            current_zone_id = self.get_current_zone_id()
            logger.debug(f"Loading triggers for zone_id: {current_zone_id}")
            file_handler.flush()
            if current_zone_id is not None:
                await self.load_triggers(zone_id=current_zone_id)
                logger.debug("Triggers loaded successfully")
                file_handler.flush()
            else:
                logger.warning(f"Skipping trigger loading in start() because zone_id is None for manager {self.name}")
                file_handler.flush()
            self.run_state = eRunState.Started
            logger.debug(f"Run state set to {self.run_state}")
            file_handler.flush()
            if self._heartbeat_task is None:
                logger.debug("Starting heartbeat loop task")
                file_handler.flush()
                self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                logger.debug("Heartbeat loop started")
                file_handler.flush()
            logger.debug("Starting monitor_tag_data task")
            file_handler.flush()
            asyncio.create_task(self.monitor_tag_data())
            logger.debug("monitor_tag_data task started")
            file_handler.flush()
        except Exception as ex:
            logger.error(f"Start Error: {str(ex)}\n{traceback.format_exc()}")
            file_handler.flush()
            self.run_state = eRunState.Stopped
            raise

    async def heartbeat_loop(self):
        logger.debug("Entering heartbeat_loop")
        file_handler.flush()
        while self.run_state in [eRunState.Started, eRunState.Starting]:
            try:
                logger.debug(f"Heartbeat loop iteration, run_state: {self.run_state}, clients: {len(self.sdk_clients)}")
                file_handler.flush()
                if not self.send_sdk_heartbeat:
                    logger.debug("Heartbeats disabled, exiting loop")
                    file_handler.flush()
                    return

                # Process heartbeats
                to_kill = []
                current_time = asyncio.get_event_loop().time()
                hb = HeartBeat(ticks=int(current_time * 1000))
                json_message = json.dumps({
                    "type": "HeartBeat",
                    "ts": hb.ticks,
                    "heartbeat_id": str(int(datetime.now().timestamp() * 1000))
                })
                logger.info(f"Manager sending heartbeat to {len(self.sdk_clients)} SDK clients and {sum(len(clients) for clients in self.clients.values())} WebSocket clients, ts: {hb.ticks}, message: {json_message}")
                file_handler.flush()

                # Initialize rate-limiting for WebSocket and SDK clients
                for reqid in self.clients:
                    if reqid not in self.ws_heartbeat_timestamps:
                        self.ws_heartbeat_timestamps[reqid] = deque(maxlen=self.HEARTBEAT_RATE_LIMIT)
                for client_id in self.sdk_clients:
                    if client_id not in self.sdk_heartbeat_timestamps:
                        self.sdk_heartbeat_timestamps[client_id] = deque(maxlen=self.HEARTBEAT_RATE_LIMIT)

                # Process SDK clients with strict rate-limiting
                clients_to_process = list(self.sdk_clients.items())
                for client_id, client in clients_to_process:
                    if client.is_closing:
                        logger.debug(f"Skipping SDK client {client_id}: already closing")
                        file_handler.flush()
                        continue
                    if client.heartbeat < self.last_heartbeat and client.heartbeat != 0:
                        logger.debug(f"SDK client {client_id} failed heartbeat check, marking to kill")
                        file_handler.flush()
                        client.is_closing = True
                        to_kill.append(client)
                        continue

                    # Rate-limit SDK client heartbeats
                    timestamps = self.sdk_heartbeat_timestamps[client_id]
                    timestamps.append(current_time)
                    if len(timestamps) == self.HEARTBEAT_RATE_LIMIT:
                        time_window = current_time - timestamps[0]
                        if time_window < self.HEARTBEAT_INTERVAL:
                            logger.warning(f"Heartbeat rate exceeded {self.HEARTBEAT_RATE_LIMIT} messages per {self.HEARTBEAT_INTERVAL}s for SDK client {client_id}")
                            file_handler.flush()
                            continue

                    try:
                        if client.heartbeat == 0:
                            client.heartbeat = self.last_heartbeat
                        client.failed_heartbeat = False
                        await client.websocket.send_text(json_message)
                        logger.debug(f"Sent heartbeat to SDK client {client_id}: {json_message}")
                        file_handler.flush()
                    except Exception as ex:
                        logger.error(f"Failed to send heartbeat to SDK client {client_id}: {str(ex)}")
                        file_handler.flush()
                        client.failed_heartbeat = True
                        client.is_closing = True
                        to_kill.append(client)

                # Process WebSocket clients with strict rate-limiting
                for reqid, clients in list(self.clients.items()):
                    timestamps = self.ws_heartbeat_timestamps[reqid]
                    timestamps.append(current_time)
                    if len(timestamps) == self.HEARTBEAT_RATE_LIMIT:
                        time_window = current_time - timestamps[0]
                        if time_window < self.HEARTBEAT_INTERVAL:
                            logger.warning(f"Heartbeat rate exceeded {self.HEARTBEAT_RATE_LIMIT} messages per {self.HEARTBEAT_INTERVAL}s for WebSocket clients with reqid {reqid}")
                            file_handler.flush()
                            continue

                    for client in clients:
                        try:
                            await client.send_json(json.loads(json_message))
                            logger.debug(f"Sent heartbeat to WebSocket client {reqid}: {json_message}")
                            file_handler.flush()
                        except Exception as ex:
                            logger.error(f"Failed to send heartbeat to WebSocket client {reqid}: {str(ex)}")
                            file_handler.flush()
                            clients.remove(client)
                            if not clients:
                                del self.clients[reqid]
                                del self.ws_heartbeat_timestamps[reqid]

                self.last_heartbeat = hb.ticks
                logger.debug(f"Updated last_heartbeat to {self.last_heartbeat}")
                file_handler.flush()

                # Send EndStream response to SDK clients marked for killing
                if to_kill:
                    resp = Response(
                        response_type=ResponseType.EndStream,
                        req_id="",
                        message=f"Failed to respond to heart beat {self.last_heartbeat}"
                    )
                    json_resp_message = resp.to_json()
                    for client in to_kill:
                        try:
                            await client.websocket.send_text(json_resp_message)
                            logger.info(f"SDK Client Heartbeat Failure response sent for {client.client_id}")
                            file_handler.flush()
                        except Exception as ex:
                            logger.error(f"Failed to send EndStream to SDK client {client.client_id}: {str(ex)}")
                            file_handler.flush()

                # Clean up SDK clients marked for killing
                for client in self.kill_list:
                    if client in self.sdk_clients.values():
                        await self.close_client(client)

                self.kill_list = to_kill

                # Clean up stale SDK clients
                for client_id, client in list(self.sdk_clients.items()):
                    if client.is_closing or client.failed_heartbeat:
                        await self.close_client(client)
                        if client_id in self.sdk_heartbeat_timestamps:
                            del self.sdk_heartbeat_timestamps[client_id]

                # Sleep for HEARTBEAT_INTERVAL
                elapsed_time = asyncio.get_event_loop().time() - current_time
                sleep_time = max(0, self.HEARTBEAT_INTERVAL - elapsed_time)
                logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
                file_handler.flush()
                await asyncio.sleep(sleep_time)
                logger.debug("Finished sleeping")
                file_handler.flush()
            except Exception as ex:
                logger.error(f"Heartbeat loop error: {str(ex)}\n{traceback.format_exc()}")
                file_handler.flush()
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
        logger.debug("Exiting heartbeat_loop")
        file_handler.flush()

    async def close_client(self, client: SDKClient):
        logger.debug(f"Closing SDK client {client.client_id}")
        file_handler.flush()
        try:
            if client and not client.is_closing:
                await client.close()
            if client.client_id in self.sdk_clients:
                del self.sdk_clients[client.client_id]
                logger.debug(f"SDK client {client.client_id} removed from sdk_clients")
                file_handler.flush()
        except Exception as ex:
            logger.error(f"CloseClient Error: {str(ex)}")
            file_handler.flush()

    async def parser_data_arrived(self, sm: dict):
        logger.debug(f"Parser data arrived: {sm}")
        file_handler.flush()
        try:
            zone_id = sm.get('zone_id', self.zone_id)
            logger.debug(f"Extracted zone_id from sm: {zone_id}, manager zone_id: {self.zone_id}")
            file_handler.flush()

            msg = GISData(
                id=sm['ID'],
                type=sm['Type'],
                ts=sm['TS'],
                x=sm['X'],
                y=sm['Y'],
                z=sm['Z'],
                bat=sm['Bat'],
                cnf=sm['CNF'],
                gwid=sm['GWID'],
                data="",
                sequence=sm.get('Sequence')
            )
            msg.zone_id = zone_id
            logger.debug(f"Set msg.zone_id to {msg.zone_id}")
            file_handler.flush()

            if not any(t.zone_id == zone_id for t in self.triggers):
                logger.debug(f"No triggers loaded for zone {zone_id}, loading now")
                file_handler.flush()
                await self.load_triggers(zone_id)
                logger.debug(f"Loaded triggers for zone {zone_id} based on GISData message")
                file_handler.flush()

            if not msg.validate():
                logger.debug(f"Invalid tag data: missing field for ID:{msg.id}")
                file_handler.flush()
                return

            if not self.processor.filter_data(msg):
                logger.debug(f"Filtered tag ID:{msg.id}, duplicate or low CNF")
                file_handler.flush()
                return

            self.processor.compute_raw_average(msg)
            logger.debug(f"Raw average for tag ID:{msg.id} over 5 positions (2D)")
            file_handler.flush()

            if self.is_ave:
                self.tag_ave(msg)

            if msg.type != "Sim POTTER":
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO positionhistory (X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z, CNF, GWID, BAT)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """,
                        msg.id, msg.ts, msg.x, msg.y, msg.z, msg.cnf, msg.gwid, str(msg.bat)
                    )
                    logger.debug(f"Stored real data for tag ID:{msg.id} in positionhistory")
                    file_handler.flush()
            else:
                logger.debug(f"Skipped DB storage for simulated tag ID:{msg.id}")
                file_handler.flush()

            tag = Tag(id=msg.id, x=msg.x, y=msg.y, z=msg.z)
            logger.debug(f"Created Tag object: id={tag.id}, position=({tag.x}, {tag.y}, {tag.z})")
            file_handler.flush()

            for trigger in self.triggers:
                if trigger.is_portable and tag.id == trigger.assigned_tag_id:
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                f"{FASTAPI_BASE_URL}/api/zones_by_point",
                                params={"x": tag.x, "y": tag.y, "z": tag.z}
                            )
                            response.raise_for_status()
                            zones = response.json()
                            if zones:
                                new_zone_id = min(
                                    zones,
                                    key=lambda z: (z["n_max_x"] - z["n_min_x"]) * (z["n_max_y"] - z["n_min_y"])
                                )["zone_id"]
                                if new_zone_id != trigger.zone_id:
                                    trigger.zone_id = new_zone_id
                                    async with self.db_pool.acquire() as conn:
                                        await conn.execute(
                                            "UPDATE triggers SET i_zn = $1 WHERE i_trg = $2",
                                            new_zone_id, trigger.i_trg
                                        )
                                    logger.debug(f"Updated portable trigger {trigger.name} to zone {new_zone_id}")
                                    file_handler.flush()
                    except Exception as e:
                        logger.error(f"Failed to update zone for trigger {trigger.name}: {str(e)}")
                        file_handler.flush()

            logger.debug(f"Checking {len(self.triggers)} triggers for tag {tag.id} at ({tag.x}, {tag.y}, {tag.z})")
            file_handler.flush()
            for trigger in self.triggers:
                if trigger.zone_id != msg.zone_id:
                    logger.debug(f"Skipping trigger {trigger.name} (ID: {trigger.i_trg}) - zone mismatch (trigger zone: {trigger.zone_id}, message zone: {msg.zone_id})")
                    file_handler.flush()
                    continue
                if trigger.is_portable and tag.id == trigger.assigned_tag_id:
                    if hasattr(trigger, 'update_position_from_tag'):
                        trigger.update_position_from_tag(tag)
                    else:
                        trigger.move_to(tag.x, tag.y, tag.z)
                        logger.debug(f"Moved portable trigger {trigger.name} to ({tag.x}, {tag.y}, {tag.z})")
                        file_handler.flush()
                
                logger.debug(f"Evaluating trigger {trigger.name} (ID: {trigger.i_trg}) with direction {trigger.direction.name}")
                file_handler.flush()
                trigger_fired = await trigger.check_trigger(tag)
                logger.debug(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired: {trigger_fired}")
                file_handler.flush()
                if trigger_fired:
                    if (trigger.is_portable and 
                        trigger.direction == TriggerDirections.WhileIn and 
                        tag.id == trigger.assigned_tag_id):
                        logger.debug(f"Suppressed WhileIn event for tag {tag.id} on its own trigger {trigger.name} (ID: {trigger.i_trg})")
                        file_handler.flush()
                        continue

                    logger.info(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired for tag {tag.id} at position ({tag.x}, {tag.y}, {tag.z})")
                    file_handler.flush()
                    event_message = {
                        "type": "TriggerEvent",
                        "trigger_id": trigger.i_trg,
                        "trigger_name": trigger.name,
                        "tag_id": tag.id,
                        "assigned_tag_id": trigger.assigned_tag_id if trigger.is_portable else None,
                        "x": tag.x,
                        "y": tag.y,
                        "z": tag.z,
                        "zone_id": msg.zone_id,
                        "direction": trigger.direction.name,
                        "timestamp": msg.ts.isoformat()
                    }
                    logger.debug(f"Event message created: {event_message}")
                    file_handler.flush()
                    for client_id, client in self.sdk_clients.items():
                        client_contains_tag = client.contains_tag(msg.id)
                        logger.debug(f"Client {client_id}: is_closing={client.is_closing}, contains_tag={client_contains_tag}, zone_id={client.zone_id}")
                        file_handler.flush()
                        if not client.is_closing and client_contains_tag:
                            logger.info(f"Sending TriggerEvent to SDK client {client_id}: {event_message}")
                            file_handler.flush()
                            await client.websocket.send_json(event_message)
                        else:
                            logger.debug(f"Skipping SDK client {client_id}: closing={client.is_closing}, contains_tag={client_contains_tag}")
                            file_handler.flush()
                    for reqid, clients in self.clients.items():
                        for client in clients:
                            try:
                                await client.send_json(event_message)
                                logger.debug(f"Sent TriggerEvent to WebSocket client {reqid}: {event_message}")
                                file_handler.flush()
                            except Exception as e:
                                logger.error(f"Failed to send TriggerEvent to WebSocket client {reqid}: {str(e)}")
                                file_handler.flush()

            if self.mode == eMode.Subscription:
                await self.queue_sub(msg)
            else:
                await self.queue_full(msg)

            self.tag_count += 1
            self.tag_rate_counter += 1
            self.tag_rate_timestamps.append(asyncio.get_event_loop().time())
            self.last_rate_time = track_metrics(self.tag_rate_counter, self.last_rate_time, self.tag_rate_timestamps)
            self.last_tag_time = asyncio.get_event_loop().time()
        except Exception as ex:
            logger.warning(f"ParserDataArrived Error: {str(ex)}")
            file_handler.flush()

    def tag_ave(self, msg: GISData):
        logger.debug(f"Computing tag average for ID:{msg.id}")
        file_handler.flush()
        if msg.id in self.ave_hash:
            a = self.ave_hash[msg.id]
            x = round((1.0 - self.ave_factor) * a.x + (msg.x * self.ave_factor), 1)
            y = round((1.0 - self.ave_factor) * a.y + (msg.y * self.ave_factor), 1)
            a.x = x
            a.y = y
            msg.x = x
            msg.y = y
        else:
            a = Ave(x=msg.x, y=msg.y, z=msg.z)
            self.ave_hash[msg.id] = a

    async def queue_full(self, msg: GISData):
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Queueing full GISData message: {json_message}")
        file_handler.flush()
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.info(f"Ignoring heartbeat message in queue_full: {json_message}")
                file_handler.flush()
                return  # Prevent heartbeat processing
            msg_dict["zone_id"] = getattr(msg, 'zone_id', self.zone_id)
            logger.debug(f"Set zone_id in queue_full: {msg_dict['zone_id']}")
            file_handler.flush()
            json_message = json.dumps(msg_dict)
            logger.debug(f"Queueing full message with zone_id: {json_message}")
            file_handler.flush()
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON message in queue_full")
            file_handler.flush()
            return
        for client_id, client in self.sdk_clients.items():
            if not client.is_closing and client.has_request and client.zone_id == msg.zone_id:
                client.q.put_nowait(json_message)
        for reqid, clients in self.clients.items():
            for client in clients:
                try:
                    await client.send_json(json.loads(json_message))
                    logger.debug(f"Sent GISData to WebSocket client {reqid}: {json_message}")
                    file_handler.flush()
                except Exception as e:
                    logger.error(f"Failed to send GISData to WebSocket client {reqid}: {str(e)}")
                    file_handler.flush()

    async def queue_sub(self, msg: GISData):
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Queueing subscription GISData message: {json_message}")
        file_handler.flush()
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.info(f"Ignoring heartbeat message in queue_sub: {json_message}")
                file_handler.flush()
                return  # Prevent heartbeat processing
            msg_dict["zone_id"] = getattr(msg, 'zone_id', self.zone_id)
            logger.debug(f"Set zone_id in queue_sub: {msg_dict['zone_id']}")
            file_handler.flush()
            json_message = json.dumps(msg_dict)
            logger.debug(f"Queueing subscription message for tag {msg.id} with zone_id: {json_message}")
            file_handler.flush()
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON message in queue_sub")
            file_handler.flush()
            return
        for client_id, client in self.sdk_clients.items():
            tag_match = client.contains_tag(msg.id)
            zone_match = client.zone_id == msg.zone_id
            if not client.is_closing and tag_match and zone_match:
                logger.debug(f"Client {client_id} subscribed to tag {msg.id} in zone {msg.zone_id}, queuing message")
                file_handler.flush()
                client.q.put_nowait(json_message)
            else:
                logger.debug(f"Skipping client {client_id}: closing={client.is_closing}, tag_match={tag_match}, zone_match={zone_match} (client zone: {client.zone_id})")
                file_handler.flush()
        for reqid, clients in self.clients.items():
            for client in clients:
                try:
                    await client.send_json(json.loads(json_message))
                    logger.debug(f"Sent GISData to WebSocket client {reqid}: {json_message}")
                    file_handler.flush()
                except Exception as e:
                    logger.error(f"Failed to send GISData to WebSocket client {reqid}: {str(e)}")
                    file_handler.flush()

    async def monitor_tag_data(self):
        logger.debug("Starting tag data monitor")
        file_handler.flush()
        while self.run_state == eRunState.Started:
            try:
                current_time = asyncio.get_event_loop().time()
                if current_time - self.last_tag_time > 5.0:
                    if not self.simulator_active:
                        logger.info("No real tag data for 5s, signaling simulator to start")
                        file_handler.flush()
                        await self.signal_simulator("start_simulator")
                        self.simulator_active = True
                elif self.simulator_active:
                    logger.info("Real tag data resumed, signaling simulator to stop")
                    file_handler.flush()
                    await self.signal_simulator("stop_simulator")
                    self.simulator_active = False
                await asyncio.sleep(1.0)
            except Exception as ex:
                logger.error(f"Tag data monitor error: {str(ex)}")
                file_handler.flush()
                await asyncio.sleep(1.0)

    async def signal_simulator(self, command: str):
        message = json.dumps({"command": command})
        for client_id, client in list(self.sdk_clients.items()):
            if client_id.startswith("sim_"):
                try:
                    await client.websocket.send_text(message)
                    logger.debug(f"Sent {command} to simulator client {client_id}")
                    file_handler.flush()
                except Exception as ex:
                    logger.error(f"Failed to signal simulator {client_id}: {str(ex)}")
                    file_handler.flush()

    async def add_client(self, reqid: str, websocket: WebSocket):
        logger.debug(f"Adding WebSocket client for reqid {reqid}")
        file_handler.flush()
        if reqid not in self.clients:
            self.clients[reqid] = []
        self.clients[reqid].append(websocket)

    async def remove_client(self, reqid: str, websocket: WebSocket):
        logger.debug(f"Removing WebSocket client for reqid {reqid}")
        file_handler.flush()
        if reqid in self.clients:
            self.clients[reqid].remove(websocket)
            if not self.clients[reqid]:
                del self.clients[reqid]
                if reqid in self.ws_heartbeat_timestamps:
                    del self.ws_heartbeat_timestamps[reqid]

    async def process_sim_message(self, message: dict):
        logger.debug(f"Processing Sim message: {message}")
        file_handler.flush()
        try:
            gis = message.get("gis", {})
            tag_id = gis.get("id")
            x = gis.get("x", 0.0)
            y = gis.get("y", 0.0)
            z = gis.get("z", 0.0)
            zone_id = message.get("zone_id")
            if not tag_id or zone_id is None:
                logger.warning(f"Invalid Sim message: missing tag_id or zone_id: {message}")
                file_handler.flush()
                return

            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or not isinstance(z, (int, float)):
                logger.warning(f"Invalid coordinates in Sim message for tag {tag_id}: x={x}, y={y}, z={z}")
                file_handler.flush()
                return

            tag = Tag(id=tag_id, x=x, y=y, z=z, zone_id=zone_id)
            
            if not any(t.zone_id == zone_id for t in self.triggers):
                logger.debug(f"No triggers loaded for zone {zone_id}, loading now")
                file_handler.flush()
                await self.load_triggers(zone_id)
                logger.debug(f"Loaded triggers for zone {zone_id} to evaluate Sim message")
                file_handler.flush()
            else:
                logger.debug(f"Triggers already loaded for zone {zone_id}, count: {len([t for t in self.triggers if t.zone_id == zone_id])}")
                file_handler.flush()

            self.last_tag_time = asyncio.get_event_loop().time()
            logger.debug(f"Updated last_tag_time to {self.last_tag_time} for tag {tag_id}")
            file_handler.flush()

            for trigger in self.triggers:
                if trigger.zone_id != zone_id:
                    logger.debug(f"Skipping trigger {trigger.name} (ID: {trigger.i_trg}) - zone mismatch (trigger zone: {trigger.zone_id}, message zone: {zone_id})")
                    file_handler.flush()
                    continue
                if trigger.is_portable and tag.id == trigger.assigned_tag_id:
                    if hasattr(trigger, 'update_position_from_tag'):
                        trigger.update_position_from_tag(tag)
                    else:
                        trigger.move_to(tag.x, tag.y, tag.z)
                        logger.debug(f"Moved portable trigger {trigger.name} to ({tag.x}, {tag.y}, {tag.z})")
                        file_handler.flush()
                
                logger.debug(f"Evaluating trigger {trigger.name} (ID: {trigger.i_trg}) with direction {trigger.direction.name}")
                file_handler.flush()
                trigger_fired = await trigger.check_trigger(tag)
                logger.debug(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired: {trigger_fired}")
                file_handler.flush()
                if trigger_fired:
                    if (trigger.is_portable and 
                        trigger.direction == TriggerDirections.WhileIn and 
                        tag.id == trigger.assigned_tag_id):
                        logger.debug(f"Suppressed WhileIn event for tag {tag.id} on its own trigger {trigger.name} (ID: {trigger.i_trg})")
                        file_handler.flush()
                        continue

                    logger.info(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired for tag {tag.id} at position ({tag.x}, {tag.y}, {tag.z})")
                    file_handler.flush()
                    event_message = {
                        "type": "TriggerEvent",
                        "trigger_id": trigger.i_trg,
                        "trigger_name": trigger.name,
                        "tag_id": tag.id,
                        "assigned_tag_id": trigger.assigned_tag_id if trigger.is_portable else None,
                        "x": tag.x,
                        "y": tag.y,
                        "z": tag.z,
                        "zone_id": zone_id,
                        "direction": trigger.direction.name,
                        "timestamp": datetime.now().isoformat()
                    }
                    logger.debug(f"Event message created: {event_message}")
                    file_handler.flush()
                    for reqid, clients in self.clients.items():
                        for client in clients:
                            try:
                                await client.send_json(event_message)
                                logger.debug(f"Sent TriggerEvent to WebSocket client {reqid}: {event_message}")
                                file_handler.flush()
                            except Exception as e:
                                logger.error(f"Failed to send TriggerEvent to WebSocket client {reqid}: {str(e)}")
                                file_handler.flush()

        except Exception as e:
            logger.error(f"Failed to process Sim message: {str(e)}")
            file_handler.flush()