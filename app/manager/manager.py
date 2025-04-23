# /home/parcoadmin/parco_fastapi/app/manager/manager.py
# Version: 1.0.37-250423 - Added dynamic zone assignment for portable triggers, bumped from 1.0.36
# Previous: Added PortableTrigger support, updated trigger movement logic (1.0.36)
# Previous: Send TriggerEvent to all subscribed clients regardless of zone_id (1.0.35)
# Previous: Ensure triggers are loaded for GISData zone_id (1.0.34)
# Previous: Fixed zone_id handling in parser_data_arrived and ensured it's preserved in Sim messages (1.0.33)

from typing import Dict, List
import asyncpg
import asyncio
from datetime import datetime, timedelta
import httpx
from .models import GISData, HeartBeat, Response, ResponseType, Ave, Tag
from .enums import eMode, eRunState, TriggerDirections
from .trigger import Trigger
from .portable_trigger import PortableTrigger
from .sdk_client import SDKClient
from .region import Region3D, Region3DCollection
from .utils import FASTAPI_BASE_URL, track_metrics
from .data_processor import DataProcessor
import logging
import json

logger = logging.getLogger(__name__)

class Manager:
    def __init__(self, name: str, zone_id: int):  # zone_id required, no default
        # Core attributes for Manager instance
        self.name = name              # Name of this manager instance
        self.zone_id = zone_id        # Zone ID this manager operates in, must be specified
        self.zone_id_locked = False   # Flag to lock zone_id after first subscription
        self.sdk_ip = None            # IP address for SDK connections
        self.sdk_port = None          # Port for SDK connections
        self.is_ave = False           # Flag for averaging tag positions
        self.ave_factor = 0.25        # Factor used in position averaging
        self.sdk_child_count = 0      # Number of SDK child connections
        self.mode = eMode.Subscription # Operation mode (Subscription or Stream)
        self.run_state = eRunState.Stopped # Current runtime state
        self.send_sdk_heartbeat = True # Enable/disable heartbeat sending
        self.log_sdk_connections = True # Enable/disable SDK connection logging
        self.tag_count = 0            # Total number of tags processed
        self.start_date = None        # Timestamp when manager started
        self.resrc_type = 0           # Resource type ID
        self.resrc_type_name = ""     # Resource type name
        self.ave_hash: Dict[str, Ave] = {} # Hash for averaged tag positions
        self.sdk_clients: Dict[str, SDKClient] = {} # Active SDK clients with zone_id
        self.kill_list: List[SDKClient] = [] # Clients marked for termination
        self.last_heartbeat = 0       # Last heartbeat timestamp
        self.conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint" # Maintenance DB connection
        self.hist_conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSHistR" # History DB connection
        self.db_pool = None           # Database connection pool
        self.response_callback = None # Callback for responses
        self.triggers: List[Trigger] = [] # List of active triggers
        self.processor = DataProcessor(min_cnf=50.0) # Data processor instance
        self.tag_rate_counter = 0     # Counter for tag rate calculation
        self.last_rate_time = asyncio.get_event_loop().time() # Last tag rate update time
        self.tag_rate_timestamps: List[float] = [] # Timestamps for tag arrivals
        self.tcp_server = None        # TCP server instance (if used)
        self._heartbeat_task = None   # Heartbeat task reference
        self.last_tag_time = 0        # Last tag data receipt time
        self.simulator_active = False # Simulator state flag
        self.tag_rate = {}            # Tag rate data
        self.tag_averages: Dict[str, List[Ave]] = {} # 3D averages for tags
        self.tag_averages_2d: Dict[str, List[Ave]] = {} # 2D averages for tags
        self.tag_averages_3d: Dict[str, List[Ave]] = {} # Additional 3D averages
        self.tag_timestamps: Dict[str, List[datetime]] = {} # Timestamps for tags
        self.tag_timestamps_2d: Dict[str, List[datetime]] = {} # 2D timestamps
        self.tag_timestamps_3d: Dict[str, List[datetime]] = {} # 3D timestamps

    async def load_config_from_db(self):
        logger.debug(f"Loading config for manager {self.name} from DB")
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
                else:
                    self.sdk_ip = "127.0.0.1"
                    self.sdk_port = 5000
                    self.mode = eMode.Subscription
                    logger.debug("No config found, using defaults")

    async def load_triggers(self, zone_id: int):
        logger.debug(f"Loading triggers for zone {zone_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{FASTAPI_BASE_URL}/api/get_triggers_by_zone_with_id/{zone_id}")
                response.raise_for_status()
                triggers_data = response.json()
                logger.debug(f"Retrieved triggers data: {triggers_data}")

                # Clear existing triggers for this zone_id
                self.triggers = [t for t in self.triggers if t.zone_id != zone_id]
                logger.debug(f"Cleared existing triggers for zone {zone_id}, remaining triggers: {len(self.triggers)}")

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
                    else:
                        detail_response = await client.get(f"{FASTAPI_BASE_URL}/api/get_trigger_details/{trigger_id}")
                        detail_response.raise_for_status()
                        trigger_details = detail_response.json()
                        logger.debug(f"Trigger details for {trigger_id}: {trigger_details}")

                        regions = Region3DCollection()
                        if isinstance(trigger_details, dict) and "vertices" in trigger_details:
                            vertices = trigger_details["vertices"]
                            if vertices and len(vertices) >= 3:
                                x_coords = [v["x"] for v in vertices]
                                y_coords = [v["y"] for v in vertices]
                                z_coords = [v["z"] for v in vertices]
                                min_x, max_x = min(x_coords), max(x_coords)
                                min_y, max_y = min(y_coords), max(y_coords)
                                min_z, max_z = min(z_coords), max(z_coords)
                                regions.add(Region3D(
                                    min_x=min_x,
                                    max_x=max_x,
                                    min_y=min_y,
                                    max_y=max_y,
                                    min_z=min_z,
                                    max_z=max_z
                                ))
                                logger.debug(f"Added region for trigger {trigger_id}: min=({min_x}, {min_y}, {min_z}), max=({max_x}, {max_y}, {max_z})")
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

                        if len(regions.regions) == 0:
                            logger.warning(f"No regions loaded for trigger {trigger_name} (ID: {trigger_id})")

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

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch triggers for zone {zone_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading triggers for zone {zone_id}: {str(e)}")

    def get_current_zone_id(self) -> int:
        return getattr(self, 'zone_id')

    async def start(self):
        self.run_state = eRunState.Starting
        try:
            self.start_date = datetime.now()
            logger.info("------- Manager Started --------")
            logger.info(f"Manager starting with zone_id: {self.zone_id}")

            if not self.send_sdk_heartbeat:
                logger.warning("Heartbeats are turned off!")

            self.db_pool = await asyncpg.create_pool(self.hist_conn_string)
            
            current_zone_id = self.get_current_zone_id()
            logger.debug(f"Loading triggers for zone_id: {current_zone_id}")
            await self.load_triggers(zone_id=current_zone_id)
            
            self.run_state = eRunState.Started
            if self._heartbeat_task is None:
                self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                logger.debug("Heartbeat loop started")
            asyncio.create_task(self.monitor_tag_data())
        except Exception as ex:
            logger.error(f"Start Error: {str(ex)}")
            raise

    async def heartbeat_loop(self):
        logger.debug("Entering heartbeat_loop")
        while self.run_state in [eRunState.Started, eRunState.Starting]:
            logger.debug(f"Heartbeat loop iteration, run_state: {self.run_state}, clients: {len(self.sdk_clients)}")
            try:
                if not self.send_sdk_heartbeat:
                    logger.debug("Heartbeats disabled, exiting loop")
                    return

                to_kill = []
                hb = HeartBeat(ticks=int(datetime.now().timestamp() * 1000))
                message = hb.to_xml()
                json_message = hb.to_json()
                logger.debug(f"Sending heartbeat to {len(self.sdk_clients)} clients, ts: {hb.ticks}")
                for client_id, client in list(self.sdk_clients.items()):
                    if client.is_closing:
                        logger.debug(f"Skipping client {client_id}: already closing")
                        continue
                    if client.heartbeat < self.last_heartbeat and client.heartbeat != 0:
                        logger.debug(f"Client {client_id} failed heartbeat check, marking to kill")
                        client.is_closing = True
                        to_kill.append(client)
                    else:
                        try:
                            if client.heartbeat == 0:
                                client.heartbeat = self.last_heartbeat
                            client.failed_heartbeat = False
                            await client.websocket.send_text(json_message)
                            logger.debug(f"Sent heartbeat to client {client_id}")
                        except Exception as ex:
                            logger.debug(f"Failed to send heartbeat to client {client_id}: {str(ex)}")
                            client.failed_heartbeat = True
                            client.is_closing = True
                            to_kill.append(client)

                self.last_heartbeat = hb.ticks
                logger.debug(f"Updated last_heartbeat to {self.last_heartbeat}")

                if to_kill:
                    resp = Response(
                        response_type=ResponseType.EndStream,
                        req_id="",
                        message=f"Failed to respond to heart beat {self.last_heartbeat}"
                    )
                    resp_message = resp.to_xml()
                    json_resp_message = resp.to_json()
                    for client in to_kill:
                        try:
                            await client.websocket.send_text(json_resp_message)
                            logger.info(f"SDK Client Heartbeat Failure response sent for {client.client_id}")
                        except:
                            pass

                for client in self.kill_list:
                    if client in self.sdk_clients.values():
                        await self.close_client(client)

                self.kill_list = to_kill

            except Exception as ex:
                logger.error(f"SDK HeartBeat Timer Error: {str(ex)}")

            if self.run_state == eRunState.Started and self.send_sdk_heartbeat:
                logger.debug("Sleeping for 60 seconds")
                await asyncio.sleep(60)
                logger.debug("Finished sleeping")
        logger.debug("Exiting heartbeat_loop")

    async def close_client(self, client: SDKClient):
        logger.debug(f"Closing client {client.client_id}")
        try:
            if client and not client.is_closing:
                await client.close()
                if client.client_id in self.sdk_clients:
                    del self.sdk_clients[client.client_id]
                    logger.debug(f"Client {client.client_id} removed from sdk_clients")
        except Exception as ex:
            logger.error(f"CloseClient Error: {str(ex)}")

    async def parser_data_arrived(self, sm: dict):
        logger.debug(f"Parser data arrived: {sm}")
        try:
            # Extract zone_id from the incoming sm dictionary
            zone_id = sm.get('zone_id', self.zone_id)
            logger.debug(f"Extracted zone_id from sm: {zone_id}, manager zone_id: {self.zone_id}")

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
            # Explicitly set zone_id on the GISData object
            msg.zone_id = zone_id
            logger.debug(f"Set msg.zone_id to {msg.zone_id}")

            # Ensure triggers are loaded for the zone_id of the incoming message
            if not any(t.zone_id == zone_id for t in self.triggers):
                logger.debug(f"No triggers loaded for zone {zone_id}, loading now")
                await self.load_triggers(zone_id)
                logger.debug(f"Loaded triggers for zone {zone_id} based on GISData message")

            if not msg.validate():
                logger.debug(f"Invalid tag data: missing field for ID:{msg.id}")
                return

            if not self.processor.filter_data(msg):
                logger.debug(f"Filtered tag ID:{msg.id}, duplicate or low CNF")
                return

            self.processor.compute_raw_average(msg)
            logger.debug(f"Raw average for tag ID:{msg.id} over 5 positions (2D)")

            if self.is_ave:
                self.tag_ave(msg)

            if msg.type != "Sim":
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO positionhistory (X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z, CNF, GWID, BAT)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """,
                        msg.id, msg.ts, msg.x, msg.y, msg.z, msg.cnf, msg.gwid, str(msg.bat)
                    )
                    logger.debug(f"Stored real data for tag ID:{msg.id} in positionhistory")
            else:
                logger.debug(f"Skipped DB storage for simulated tag ID:{msg.id}")

            tag = Tag(id=msg.id, x=msg.x, y=msg.y, z=msg.z)
            logger.debug(f"Created Tag object: id={tag.id}, position=({tag.x}, {tag.y}, {tag.z})")

            # --- NEW: Dynamic zone assignment for portable triggers (optional, revert if not applied) ---
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
                                # Prioritize smallest zone (child)
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
                    except Exception as e:
                        logger.error(f"Failed to update zone for trigger {trigger.name}: {str(e)}")
            # --- END NEW ---

            logger.debug(f"Checking {len(self.triggers)} triggers for tag {tag.id} at ({tag.x}, {tag.y}, {tag.z})")
            for trigger in self.triggers:
                if trigger.zone_id != msg.zone_id:
                    logger.debug(f"Skipping trigger {trigger.name} (ID: {trigger.i_trg}) - zone mismatch (trigger zone: {trigger.zone_id}, message zone: {msg.zone_id})")
                    continue
                if trigger.is_portable and tag.id == trigger.assigned_tag_id:
                    if hasattr(trigger, 'update_position_from_tag'):
                        trigger.update_position_from_tag(tag)
                    else:
                        trigger.move_to(tag.x, tag.y, tag.z)
                        logger.debug(f"Moved portable trigger {trigger.name} to ({tag.x}, {tag.y}, {tag.z})")
                
                logger.debug(f"Evaluating trigger {trigger.name} (ID: {trigger.i_trg}) with direction {trigger.direction.name}")
                trigger_fired = await trigger.check_trigger(tag)
                logger.debug(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired: {trigger_fired}")
                if trigger_fired:
                    logger.debug(f"Trigger {trigger.name} fired for tag {tag.id}")
                    event_message = {
                        "type": "TriggerEvent",
                        "trigger_id": trigger.i_trg,
                        "direction": trigger.direction.name,
                        "tag_id": msg.id,
                        "timestamp": msg.ts.isoformat()
                    }
                    logger.debug(f"Event message created: {event_message}")
                    for client_id, client in self.sdk_clients.items():
                        client_contains_tag = client.contains_tag(msg.id)
                        logger.debug(f"Client {client_id}: is_closing={client.is_closing}, contains_tag={client_contains_tag}, zone_id={client.zone_id}")
                        if not client.is_closing and client_contains_tag:
                            logger.debug(f"Sending TriggerEvent to client {client_id}: {event_message}")
                            await client.websocket.send_json(event_message)
                        else:
                            logger.debug(f"Skipping client {client_id}: closing={client.is_closing}, contains_tag={client_contains_tag}")

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

    def tag_ave(self, msg: GISData):
        logger.debug(f"Computing tag average for ID:{msg.id}")
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
        # Convert GISData to JSON and ensure zone_id is included
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Original JSON message from GISData: {json_message}")
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.debug("Skipping heartbeat message in queue_full")
                return
            # Add zone_id to the message, preferring msg.zone_id
            msg_dict["zone_id"] = getattr(msg, 'zone_id', self.zone_id)
            logger.debug(f"Set zone_id in queue_full: {msg_dict['zone_id']}")
            json_message = json.dumps(msg_dict)
            logger.debug(f"Queueing full message with zone_id: {json_message}")
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON message in queue_full")
            return
        for client_id, client in self.sdk_clients.items():
            if not client.is_closing and client.has_request and client.zone_id == msg.zone_id:
                client.q.put_nowait(json_message)

    async def queue_sub(self, msg: GISData):
        # Convert GISData to JSON and ensure zone_id is included
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Original JSON message from GISData: {json_message}")
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.debug("Skipping heartbeat message in queue_sub")
                return
            # Add zone_id to the message, preferring msg.zone_id
            msg_dict["zone_id"] = getattr(msg, 'zone_id', self.zone_id)
            logger.debug(f"Set zone_id in queue_sub: {msg_dict['zone_id']}")
            json_message = json.dumps(msg_dict)
            logger.debug(f"Queueing subscription message for tag {msg.id} with zone_id: {json_message}")
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON message in queue_sub")
            return
        for client_id, client in self.sdk_clients.items():
            tag_match = client.contains_tag(msg.id)
            zone_match = client.zone_id == msg.zone_id
            if not client.is_closing and tag_match and zone_match:
                logger.debug(f"Client {client_id} subscribed to tag {msg.id} in zone {msg.zone_id}, queuing message")
                client.q.put_nowait(json_message)
            else:
                logger.debug(f"Skipping client {client_id}: closing={client.is_closing}, tag_match={tag_match}, zone_match={zone_match} (client zone: {client.zone_id})")

    async def monitor_tag_data(self):
        logger.debug("Starting tag data monitor")
        while self.run_state == eRunState.Started:
            try:
                current_time = asyncio.get_event_loop().time()
                if current_time - self.last_tag_time > 5.0:
                    if not self.simulator_active:
                        logger.info("No real tag data for 5s, signaling simulator to start")
                        await self.signal_simulator("start_simulator")
                        self.simulator_active = True
                elif self.simulator_active:
                    logger.info("Real tag data resumed, signaling simulator to stop")
                    await self.signal_simulator("stop_simulator")
                    self.simulator_active = False
                await asyncio.sleep(1.0)
            except Exception as ex:
                logger.error(f"Tag data monitor error: {str(ex)}")
                await asyncio.sleep(1.0)

    async def signal_simulator(self, command: str):
        message = json.dumps({"command": command})
        for client_id, client in list(self.sdk_clients.items()):
            if client_id.startswith("sim_"):
                try:
                    await client.websocket.send_text(message)
                    logger.debug(f"Sent {command} to simulator client {client_id}")
                except Exception as ex:
                    logger.error(f"Failed to signal simulator {client_id}: {str(ex)}")