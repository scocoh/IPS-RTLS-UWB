# /home/parcoadmin/parco_fastapi/app/manager/models.py
# Version: 1.0.3 - Added zone_id field to GISData, bumped from 1.0.2
# Previous: Added Sequence field to GISData (1.0.2)
#
# Model Module for Manager
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET
from .utils import MessageUtilities
from .enums import RequestType, ResponseType
import json

class Tag(BaseModel):
    id: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    timestamp_utc: Optional[datetime] = None
    msg_type: str = ""
    battery: int = -1
    conf_factor: float = -1.0
    gwid: str = ""
    data: str = ""
    send_payload_data: bool = False

    @property
    def has_data(self) -> bool:
        return bool(self.data)

    def to_xml(self) -> str:
        return f'<tagid data="{str(self.send_payload_data).lower()}">{self.id}</tagid>'

    def to_json(self) -> str:
        """Converts Tag to JSON string."""
        data = MessageUtilities.json_base()
        data.update({
            "id": self.id,
            "data": str(self.send_payload_data).lower()
        })
        return json.dumps(data)

    def __str__(self) -> str:
        return f"{self.id} ({self.x},{self.y},{self.z})"

class GISData(BaseModel):
    id: str
    type: str
    ts: datetime
    x: float
    y: float
    z: float
    bat: int = -1
    cnf: float = -1.0
    gwid: str = ""
    data: str = ""
    sequence: Optional[int] = None
    zone_id: Optional[int] = None  # NEW: Added zone_id field

    def to_xml(self) -> str:
        root = ET.Element("parco", version="1.0")
        ET.SubElement(root, "type").text = self.type
        gis = ET.SubElement(root, "gis")
        ET.SubElement(gis, "id").text = self.id
        ET.SubElement(gis, "ts").text = self.ts.isoformat()
        ET.SubElement(gis, "gwid").text = self.gwid
        ET.SubElement(gis, "cnf").text = str(self.cnf)
        ET.SubElement(gis, "x").text = str(self.x)
        ET.SubElement(gis, "y").text = str(self.y)
        ET.SubElement(gis, "z").text = str(self.z)
        ET.SubElement(gis, "bat").text = str(self.bat)
        ET.SubElement(root, "data").text = self.data
        if self.sequence is not None:
            ET.SubElement(root, "sequence").text = str(self.sequence)
        if self.zone_id is not None:  # NEW: Include zone_id in XML
            ET.SubElement(root, "zone_id").text = str(self.zone_id)
        return MessageUtilities.XMLDefTag + ET.tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_str: str):
        root = ET.fromstring(xml_str)
        gis = root.find("gis")
        sequence = root.find("sequence")
        sequence_value = int(sequence.text) if sequence is not None else None
        zone_id = root.find("zone_id")
        zone_id_value = int(zone_id.text) if zone_id is not None else None  # NEW: Parse zone_id
        return cls(
            id=gis.find("id").text,
            type=root.find("type").text,
            ts=datetime.fromisoformat(gis.find("ts").text),
            x=float(gis.find("x").text),
            y=float(gis.find("y").text),
            z=float(gis.find("z").text),
            bat=int(gis.find("bat").text) if gis.find("bat").text else -1,
            cnf=float(gis.find("cnf").text) if gis.find("cnf").text else -1.0,
            gwid=gis.find("gwid").text or "",
            data=root.find("data").text or "",
            sequence=sequence_value,
            zone_id=zone_id_value  # NEW: Set zone_id
        )

    def validate(self) -> bool:
        """Validates that all required GISData fields are present and not None."""
        required = [self.id, self.type, self.ts, self.x, self.y, self.z, self.bat, self.cnf, self.gwid]
        return all(field is not None for field in required)

    def to_json(self) -> str:
        """Converts GISData to JSON string."""
        data = MessageUtilities.json_base()
        data.update({
            "type": self.type,
            "gis": {
                "id": self.id,
                "ts": self.ts.isoformat(),
                "gwid": self.gwid,
                "cnf": self.cnf,
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "bat": self.bat
            },
            "data": self.data
        })
        if self.sequence is not None:
            data["Sequence"] = self.sequence
        if self.zone_id is not None:  # NEW: Include zone_id in JSON
            data["zone_id"] = self.zone_id
        return json.dumps(data)

class HeartBeat(BaseModel):
    ticks: int

    def to_xml(self) -> str:
        root = ET.Element("parco", version="1.0")
        ET.SubElement(root, "type").text = "HeartBeat"
        ET.SubElement(root, "ts").text = str(self.ticks)
        return MessageUtilities.XMLDefTag + ET.tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_str: str):
        root = ET.fromstring(xml_str)
        return cls(ticks=int(root.find("ts").text))

    def to_json(self) -> str:
        """Converts HeartBeat to JSON string."""
        data = MessageUtilities.json_base()
        data.update({
            "type": "HeartBeat",
            "ts": self.ticks
        })
        return json.dumps(data)

class Request(BaseModel):
    req_type: RequestType
    req_id: str
    tags: List[Tag] = []

    def to_xml(self) -> str:
        root = ET.Element("parco", version="1.0")
        ET.SubElement(root, "type").text = "request"
        ET.SubElement(root, "request").text = self.req_type.value
        ET.SubElement(root, "reqid").text = self.req_id
        params = ET.SubElement(root, "params")
        for tag in self.tags:
            params.append(ET.fromstring(tag.to_xml()))
        return MessageUtilities.XMLDefTag + ET.tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_str: str):
        root = ET.fromstring(xml_str)
        req_type = RequestType(root.find("request").text)
        req_id = root.find("reqid").text
        tags = []
        for tag_elem in root.findall(".//tagid"):
            tag_id = tag_elem.text
            data = tag_elem.get("data") == "true"
            tags.append(Tag(id=tag_id, send_payload_data=data))
        return cls(req_type=req_type, req_id=req_id, tags=tags)

    def to_json(self) -> str:
        """Converts Request to JSON string."""
        data = MessageUtilities.json_base()
        data.update({
            "type": "request",
            "request": self.req_type.value,
            "reqid": self.req_id,
            "params": [json.loads(tag.to_json()) for tag in self.tags]
        })
        return json.dumps(data)

class Response(BaseModel):
    response_type: ResponseType
    req_id: str
    message: str = ""

    def to_xml(self) -> str:
        root = ET.Element("parco", version="1.0")
        ET.SubElement(root, "type").text = "response"
        ET.SubElement(root, "request").text = self.response_type.value
        ET.SubElement(root, "reqid").text = self.req_id
        ET.SubElement(root, "msg").text = self.message
        return MessageUtilities.XMLDefTag + ET.tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_str: str):
        root = ET.fromstring(xml_str)
        response_type = ResponseType(root.find("request").text)
        req_id = root.find("reqid").text
        message = root.find("msg").text or ""
        return cls(response_type=response_type, req_id=req_id, message=message)

    def to_json(self) -> str:
        """Converts Response to JSON string."""
        data = MessageUtilities.json_base()
        data.update({
            "type": "response",
            "request": self.response_type.value,
            "reqid": self.req_id,
            "msg": self.message
        })
        return json.dumps(data)

class Ave:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z