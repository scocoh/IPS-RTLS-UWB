# /home/parcoadmin/parco_fastapi/app/manager/manager.py
# Version: 1.0.17 - Added TriggerEvent broadcasting
from typing import Dict, List
import asyncpg
import asyncio
from datetime import datetime, timedelta
import httpx
from .models import GISData, HeartBeat, Response, ResponseType, Ave, Tag  # Added Tag import
from .enums import eMode, eRunState, TriggerDirections
from .trigger import Trigger
from .sdk_client import SDKClient
from .region import Region3D, Region3DCollection
from .utils import FASTAPI_BASE_URL, track_metrics
from .data_processor import DataProcessor
import logging
import json

logger = logging.getLogger(__name__)

class Manager:
    def __init__(self, name: str):
        self.name = name
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
                response = await client.get(f"{FASTAPI_BASE_URL}/api/get_triggers_by_zone/{zone_id}")
                response.raise_for_status()
                triggers_data = response.json()

                for trigger_data in triggers_data:
                    trigger_id = trigger_data["trigger_id"]
                    trigger_name = trigger_data["name"]
                    direction_name = trigger_data["direction_name"]

                    direction_map = {
                        "WhileIn": TriggerDirections.WhileIn,
                        "WhileOut": TriggerDirections.WhileOut,
                        "OnCross": TriggerDirections.OnCross,
                        "OnEnter": TriggerDirections.OnEnter,
                        "OnExit": TriggerDirections.OnExit
                    }
                    direction = direction_map.get(direction_name, TriggerDirections.NotSet)

                    detail_response = await client.get(f"{FASTAPI_BASE_URL}/api/get_trigger_details/{trigger_id}")
                    detail_response.raise_for_status()
                    trigger_details = detail_response.json()

                    regions = Region3DCollection()
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

                    trigger = Trigger(
                        i_trg=trigger_id,
                        name=trigger_name,
                        direction=direction,
                        regions=regions,
                        ignore_unknowns=False
                    )
                    self.triggers.append(trigger)
                    logger.info(f"Loaded trigger {trigger_name} (ID: {trigger_id}) for zone {zone_id}")

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch triggers for zone {zone_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading triggers for zone {zone_id}: {str(e)}")

    async def start(self):
        self.run_state = eRunState.Starting
        try:
            self.start_date = datetime.now()
            logger.info("------- Manager Started --------")

            if not self.send_sdk_heartbeat:
                logger.warning("Heartbeats are turned off!")

            self.db_pool = await asyncpg.create_pool(self.hist_conn_string)
            
            await self.load_triggers(zone_id=1)
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
                logger.debug("Sleeping for 30 seconds")
                await asyncio.sleep(30)
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

            # Convert GISData to Tag for trigger checking
            tag = Tag(id=msg.id, x=msg.x, y=msg.y, z=msg.z)

            # Check triggers and broadcast events
            for trigger in self.triggers:
                if await trigger.check_trigger(tag):
                    event_message = {
                        "type": "TriggerEvent",
                        "trigger_id": trigger.i_trg,
                        "direction": trigger.direction.name,
                        "tag_id": msg.id,
                        "timestamp": msg.ts.isoformat()
                    }
                    json_message = json.dumps(event_message)
                    for client_id, client in self.sdk_clients.items():
                        if not client.is_closing and client.contains_tag(msg.id):
                            client.q.put_nowait(json_message)
                            logger.debug(f"Sent TriggerEvent to client {client_id}: {json_message}")

            if self.mode == eMode.Subscription:
                await self.queue_sub(msg)
            else:
                await self.queue_full(msg)

            self.tag_count += 1
            self.tag_rate_counter += 1
            self.last_rate_time = track_metrics(self.tag_rate_counter, self.last_rate_time)
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
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Queueing full message: {json_message}")
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.debug("Skipping heartbeat message in queue_full")
                return
        except json.JSONDecodeError:
            pass
        for client in self.sdk_clients.values():
            if not client.is_closing and client.has_request:
                client.q.put_nowait(json_message)

    async def queue_sub(self, msg: GISData):
        message = msg.to_xml()
        json_message = msg.to_json()
        logger.debug(f"Queueing subscription message: {json_message}")
        try:
            msg_dict = json.loads(json_message)
            if msg_dict.get("type") == "HeartBeat":
                logger.debug("Skipping heartbeat message in queue_sub")
                return
        except json.JSONDecodeError:
            pass
        for client_id, client in self.sdk_clients.items():
            if not client.is_closing and client.contains_tag(msg.id):
                logger.debug(f"Client {client_id} subscribed to tag {msg.id}, queuing message")
                client.q.put_nowait(json_message)
            else:
                logger.debug(f"Client {client_id} not subscribed to tag {msg.id} or closing")

    async def monitor_tag_data(self):
        """Monitor tag data and control simulator via WebSocket."""
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
        """Send command to simulator via WebSocket."""
        message = json.dumps({"command": command})
        for client_id, client in list(self.sdk_clients.items()):
            if client_id.startswith("sim_"):
                try:
                    await client.websocket.send_text(message)
                    logger.debug(f"Sent {command} to simulator client {client_id}")
                except Exception as ex:
                    logger.error(f"Failed to signal simulator {client_id}: {str(ex)}")