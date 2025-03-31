# Version: 250327 /home/parcoadmin/parco_fastapi/app/manager/datastream.py 1.0.1
# 
# Datastream Module for Manager
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
import xml.etree.ElementTree as ET
from typing import Optional, Callable, List
from dataclasses import dataclass
import websockets
import httpx
from .enums import ConnectionState, TriggerDirections, RequestType, ResponseType  # Updated: Added ResponseType
from .models import Tag, GISData, HeartBeat, Request, Response
from .trigger import Trigger
from .utils import FASTAPI_BASE_URL, MessageUtilities, track_metrics
from .region import Region3D, Region3DCollection
from .events import StreamDataEventArgs, StreamHeartbeatEventArgs, StreamResponseEventArgs, StreamConnectionEventArgs
import json
from datetime import datetime  # Updated: Moved to top for clarity

logger = logging.getLogger(__name__)

class DataStream:
    def __init__(self, tcp_ip: str = None, port: int = None):
        self.name = ""
        self.is_subscription_based = True
        self.is_averaged = False
        self.resource_type = 0
        self.tcp_ip = tcp_ip
        self.port = port
        self.websocket = None
        self.buffer = ""
        self.is_connected = False
        self.connection_state = ConnectionState.NotKnown
        self.stream_callback: Optional[Callable[[StreamDataEventArgs], None]] = None
        self.heartbeat_callback: Optional[Callable[[StreamHeartbeatEventArgs], None]] = None
        self.response_callback: Optional[Callable[[StreamResponseEventArgs], None]] = None
        self.connection_callback: Optional[Callable[[StreamConnectionEventArgs], None]] = None
        self.triggers: List[Trigger] = []

    def add_trigger(self, trigger: Trigger):
        self.triggers.append(trigger)

    async def load_triggers(self, zone_id: int):
        """Fetch triggers for a given zone and create runtime Trigger instances."""
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
                                max_y=detail["n_max Calc"],
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
                    async def on_trigger(event: StreamDataEventArgs):
                        print(f"Trigger Fired: {event.tag} for trigger {trigger_name}")
                    trigger.trigger_callback = on_trigger
                    self.add_trigger(trigger)
                    logger.info(f"Loaded trigger {trigger_name} (ID: {trigger_id}) for zone {zone_id}")

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch triggers for zone {zone_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading triggers for zone {zone_id}: {str(e)}")

    @property
    def version(self) -> str:
        return "Parco RTLS Version 1.0"

    def address(self, tcp_ip: str, port: int):
        if self.is_connected:
            raise Exception("The TCPIP Address and Port cannot be changed while the underlying connection is open.")
        self.tcp_ip = tcp_ip
        self.port = port

    async def connection_test(self, ip: str, port: int) -> bool:
        try:
            async with websockets.connect(f"ws://{ip}:{port}/ws/test") as ws:
                return True
        except:
            return False

    async def connect(self):
        if self.is_connected:
            raise Exception("RTLS connect method called on an open connection.")
        if not self.tcp_ip or not self.port:
            raise Exception("TCPIP address and port must be set before connecting.")

        try:
            self.websocket = await websockets.connect(f"ws://{self.tcp_ip}:{self.port}/manager/ws/{self.name}")
            self.is_connected = True
            self.connection_state = ConnectionState.Connected
            if self.connection_callback:
                await self.connection_callback(StreamConnectionEventArgs(state="Connected"))
            asyncio.create_task(self.start_reading_live())
        except Exception as ex:
            self.is_connected = False
            self.connection_state = ConnectionState.Disconnected
            if self.connection_callback:
                await self.connection_callback(StreamConnectionEventArgs(state="Disconnected"))
            raise Exception(f"Failed to connect: {str(ex)}")

    async def close(self):
        if not self.websocket:
            raise Exception("RTLS Close method called without an initialized connection.")
        try:
            await self.websocket.close()
            self.is_connected = False
            self.connection_state = ConnectionState.Disconnected
            if self.connection_callback:
                await self.connection_callback(StreamConnectionEventArgs(state="Disconnected"))
        finally:
            self.websocket = None

    async def send_request(self, req: Request):
        if not self.websocket or not self.is_connected:
            raise Exception("Send Request method called without an initialized or open connection.")

        if req.req_type in [RequestType.AddTag, RequestType.RemoveTag] and not req.tags:
            raise Exception(f"{req.req_type.value} request with 0 tags specified.")
        if not req.req_id:
            raise Exception("The request did not contain a request id")

        await self.websocket.send(req.to_xml())  # Existing XML method
        # NEW: JSON method
        await self.websocket.send(req.to_json())

    async def start_tcp_server(self):
        """Placeholder for TCP server based on ParcoTCP.vb."""
        # TODO: Implement TCP server with asyncio.start_server
        pass

    async def start_reading_live(self):
        try:
            while self.is_connected:
                data = await self.websocket.recv()
                await self.live_data_arrived(data)
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            self.connection_state = ConnectionState.Disconnected
            if self.connection_callback:
                await self.connection_callback(StreamConnectionEventArgs(state="Disconnected"))
        except Exception as ex:
            logger.error(f"LiveDataReceived Error: {str(ex)}")
            self.is_connected = False
            self.connection_state = ConnectionState.Disconnected
            if self.connection_callback:
                await self.connection_callback(StreamConnectionEventArgs(state="Disconnected"))

    async def live_data_arrived(self, data: str):
        # Existing XML handling
        self.buffer += data
        temp = ""
        messages = self.buffer.split(MessageUtilities.XMLDefTag)

        for i in range(len(messages)):
            msg = messages[i]
            if len(msg) > 0 and MessageUtilities.ParcoEndTag in msg:
                if i == len(messages) - 1:
                    end_tag_pos = msg.index(MessageUtilities.ParcoEndTag) + len(MessageUtilities.ParcoEndTag)
                    if len(msg) > end_tag_pos:
                        temp = msg[end_tag_pos:]
                        msg = msg[:end_tag_pos]

                if "<type>HeartBeat</type>" in msg:
                    hb = HeartBeat.from_xml(MessageUtilities.XMLDefTag + msg)
                    await self.websocket.send_text(MessageUtilities.XMLDefTag + msg)  # Echo back XML
                    if self.heartbeat_callback:
                        await self.heartbeat_callback(StreamHeartbeatEventArgs(heartbeat=hb))
                elif "<type>response</type>" in msg:
                    resp = Response.from_xml(MessageUtilities.XMLDefTag + msg)
                    if self.response_callback:
                        await self.response_callback(StreamResponseEventArgs(response=resp))
                elif "<type>HeartBeat</type>" not in msg:
                    gis_data = GISData.from_xml(MessageUtilities.XMLDefTag + msg)
                    tag = Tag(
                        id=gis_data.id,
                        x=gis_data.x,
                        y=gis_data.y,
                        z=gis_data.z,
                        timestamp_utc=gis_data.ts,
                        msg_type=gis_data.type,
                        battery=gis_data.bat,
                        conf_factor=gis_data.cnf,
                        gwid=gis_data.gwid,
                        data=gis_data.data,
                        send_payload_data=False
                    )
                    if self.stream_callback:
                        await self.stream_callback(StreamDataEventArgs(tag=tag))
                    for trigger in self.triggers:
                        await trigger.check_trigger(tag)

        self.buffer = temp if temp else MessageUtilities.XMLDefTag + messages[-1] if messages[-1] and MessageUtilities.ParcoEndTag not in messages[-1] else ""

        # NEW: JSON handling
        try:
            json_data = json.loads(data)  # Attempt to parse as JSON
            msg_type = json_data.get("type", "")
            if msg_type == "HeartBeat":
                hb = HeartBeat(ticks=json_data["ts"])
                await self.websocket.send_text(hb.to_json())  # Echo back JSON
                if self.heartbeat_callback:
                    await self.heartbeat_callback(StreamHeartbeatEventArgs(heartbeat=hb))
            elif msg_type == "response":
                resp = Response(
                    response_type=ResponseType(json_data["request"]),
                    req_id=json_data["reqid"],
                    message=json_data.get("msg", "")
                )
                if self.response_callback:
                    await self.response_callback(StreamResponseEventArgs(response=resp))
            else:  # Assume GISData
                gis = json_data["gis"]
                gis_data = GISData(
                    id=gis["id"],
                    type=msg_type,
                    ts=datetime.fromisoformat(gis["ts"]),
                    x=gis["x"],
                    y=gis["y"],
                    z=gis["z"],
                    bat=gis["bat"],
                    cnf=gis["cnf"],
                    gwid=gis["gwid"],
                    data=json_data.get("data", "")
                )
                tag = Tag(
                    id=gis_data.id,
                    x=gis_data.x,
                    y=gis_data.y,
                    z=gis_data.z,
                    timestamp_utc=gis_data.ts,
                    msg_type=gis_data.type,
                    battery=gis_data.bat,
                    conf_factor=gis_data.cnf,
                    gwid=gis_data.gwid,
                    data=gis_data.data,
                    send_payload_data=False
                )
                if self.stream_callback:
                    await self.stream_callback(StreamDataEventArgs(tag=tag))
                for trigger in self.triggers:
                    await trigger.check_trigger(tag)
        except json.JSONDecodeError:
            pass  # If not JSON, fall back to XML handling

# Example Usage of DataStream with Trigger
async def main():
    ds = DataStream(tcp_ip="192.168.210.231", port=8000)
    ds.name = "Manager1"

    await ds.load_triggers(zone_id=1)

    async def on_stream(event: StreamDataEventArgs):
        print(f"Stream Data: {event.tag}")

    async def on_heartbeat(event: StreamHeartbeatEventArgs):
        print(f"Heartbeat: {event.heartbeat.ticks}")

    async def on_response(event: StreamResponseEventArgs):
        print(f"Response: {event.response.response_type}, {event.response.message}")

    async def on_connection(event: StreamConnectionEventArgs):
        print(f"Connection State: {event.state}")

    ds.stream_callback = on_stream
    ds.heartbeat_callback = on_heartbeat
    ds.response_callback = on_response
    ds.connection_callback = on_connection

    await ds.connect()

    req = Request(req_type=RequestType.BeginStream, req_id="123", tags=[])
    await ds.send_request(req)

    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())