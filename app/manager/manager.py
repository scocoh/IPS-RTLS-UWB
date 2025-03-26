from typing import Dict, List
import asyncpg
import asyncio
from datetime import datetime
from .models import GISData, HeartBeat, Response, ResponseType, Ave
from .enums import eMode, eRunState, TriggerDirections
from .trigger import Trigger
from .sdk_client import SDKClient
from .region import Region3D, Region3DCollection
from .utils import FASTAPI_BASE_URL
import httpx
import logging

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
        # Updated connection strings to use parcoadmin user and correct password
        self.conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.231:5432/ParcoRTLSMaint"
        self.hist_conn_string = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.231:5432/ParcoRTLSHistR"
        self.db_pool = None
        self.response_callback = None
        self.triggers: List[Trigger] = []

    async def load_config_from_db(self):
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
                else:
                    self.sdk_ip = "127.0.0.1"
                    self.sdk_port = 5000
                    self.mode = eMode.Subscription

    async def load_triggers(self, zone_id: int):
        """Fetch triggers for a given zone and create runtime Trigger instances."""
        try:
            async with httpx.AsyncClient() as client:
                # Fetch triggers for the zone
                response = await client.get(f"{FASTAPI_BASE_URL}/api/get_triggers_by_zone/{zone_id}")
                response.raise_for_status()
                triggers_data = response.json()

                for trigger_data in triggers_data:
                    trigger_id = trigger_data["trigger_id"]
                    trigger_name = trigger_data["name"]
                    direction_name = trigger_data["direction_name"]

                    # Map direction_name to TriggerDirections
                    direction_map = {
                        "WhileIn": TriggerDirections.WhileIn,
                        "WhileOut": TriggerDirections.WhileOut,
                        "OnCross": TriggerDirections.OnCross,
                        "OnEnter": TriggerDirections.OnEnter,
                        "OnExit": TriggerDirections.OnExit
                    }
                    direction = direction_map.get(direction_name, TriggerDirections.NotSet)

                    # Fetch trigger details to get regions and vertices
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
                        ignore_unknowns=False  # Adjust based on trigger settings if available
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
            
            # Load triggers for a specific zone (e.g., zone_id=1)
            await self.load_triggers(zone_id=1)  # Replace with desired zone_id

            self.run_state = eRunState.Started
        except Exception as ex:
            logger.error(f"Start Error: {str(ex)}")
            raise

    async def heartbeat_loop(self):
        while self.run_state in [eRunState.Started, eRunState.Starting]:
            try:
                if not self.send_sdk_heartbeat:
                    return

                to_kill = []
                hb = HeartBeat(ticks=int(datetime.now().timestamp() * 1000))
                message = hb.to_xml()

                for client_id, client in list(self.sdk_clients.items()):
                    if client.is_closing:
                        continue
                    if client.heartbeat < self.last_heartbeat and client.heartbeat != 0:
                        client.is_closing = True
                        to_kill.append(client)
                    else:
                        try:
                            if client.heartbeat == 0:
                                client.heartbeat = self.last_heartbeat
                            client.failed_heartbeat = False
                            await client.websocket.send_text(message)
                        except:
                            client.failed_heartbeat = True
                            client.is_closing = True
                            to_kill.append(client)

                self.last_heartbeat = hb.ticks

                if to_kill:
                    resp = Response(
                        response_type=ResponseType.EndStream,
                        req_id="",
                        message=f"Failed to respond to heart beat {self.last_heartbeat}"
                    )
                    for client in to_kill:
                        try:
                            await client.websocket.send_text(resp.to_xml())
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
                await asyncio.sleep(15)

    async def close_client(self, client: SDKClient):
        try:
            if client:
                client.is_closing = True
                await client.websocket.close()
                if client.client_id in self.sdk_clients:
                    del self.sdk_clients[client.client_id]
        except Exception as ex:
            logger.error(f"CloseClient Error: {str(ex)}")

    async def parser_data_arrived(self, sm: dict):
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
                data=""
            )
            if self.is_ave:
                self.tag_ave(msg)

            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO positionhistory (X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z, CNF, GWID, BAT)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    msg.id, msg.ts, msg.x, msg.y, msg.z, msg.cnf, msg.gwid, str(msg.bat)
                )

            if self.mode == eMode.Subscription:
                await self.queue_sub(msg)
            else:
                await self.queue_full(msg)

            self.tag_count += 1
        except Exception as ex:
            logger.warning(f"ParserDataArrived Error: {str(ex)}")

    def tag_ave(self, msg: GISData):
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
        for client in self.sdk_clients.values():
            if not client.is_closing and client.has_request:
                client.q.put_nowait(message)

    async def queue_sub(self, msg: GISData):
        message = msg.to_xml()
        for client in self.sdk_clients.values():
            if not client.is_closing and client.contains_tag(msg.id):
                client.q.put_nowait(message)