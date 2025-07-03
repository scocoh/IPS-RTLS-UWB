# Name: models.py
# Version: 0.1.3
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & TC
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/models.py
# Version: 0.1.1 - Added Config to Request model to allow extra fields for backward compatibility, bumped from 0.1.0
# Version: 0.1.0 - Added zone_id field to GISData, bumped from 1.0.3
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
        if gis is None:
            raise ValueError("Invalid GISData XML: missing 'gis' element")
            
        sequence = root.find("sequence")
        sequence_value = int(sequence.text) if sequence is not None and sequence.text else None
        zone_id = root.find("zone_id")
        zone_id_value = int(zone_id.text) if zone_id is not None and zone_id.text else None  # NEW: Parse zone_id
        
        # Safely get text values with defaults
        id_elem = gis.find("id")
        type_elem = root.find("type")
        ts_elem = gis.find("ts")
        x_elem = gis.find("x")
        y_elem = gis.find("y")
        z_elem = gis.find("z")
        bat_elem = gis.find("bat")
        cnf_elem = gis.find("cnf")
        gwid_elem = gis.find("gwid")
        data_elem = root.find("data")
        
        return cls(
            id=id_elem.text if id_elem is not None and id_elem.text else "",
            type=type_elem.text if type_elem is not None and type_elem.text else "",
            ts=datetime.fromisoformat(ts_elem.text) if ts_elem is not None and ts_elem.text else datetime.now(),
            x=float(x_elem.text) if x_elem is not None and x_elem.text else 0.0,
            y=float(y_elem.text) if y_elem is not None and y_elem.text else 0.0,
            z=float(z_elem.text) if z_elem is not None and z_elem.text else 0.0,
            bat=int(bat_elem.text) if bat_elem is not None and bat_elem.text else -1,
            cnf=float(cnf_elem.text) if cnf_elem is not None and cnf_elem.text else -1.0,
            gwid=gwid_elem.text if gwid_elem is not None and gwid_elem.text else "",
            data=data_elem.text if data_elem is not None and data_elem.text else "",
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
        ts_elem = root.find("ts")
        return cls(ticks=int(ts_elem.text) if ts_elem is not None and ts_elem.text else 0)

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
    
    class Config:
        # Allow extra fields to be passed but ignore them
        # This maintains backward compatibility with websocket handlers
        # that pass zone_id in the JSON data
        extra = "allow"

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
        request_elem = root.find("request")
        req_id_elem = root.find("reqid")
        
        if request_elem is None or req_id_elem is None:
            raise ValueError("Invalid Request XML: missing required elements")
            
        req_type = RequestType(request_elem.text)
        req_id = req_id_elem.text if req_id_elem.text else ""
        tags = []
        for tag_elem in root.findall(".//tagid"):
            tag_id = tag_elem.text if tag_elem.text else ""
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
        request_elem = root.find("request")
        req_id_elem = root.find("reqid")
        msg_elem = root.find("msg")
        
        if request_elem is None or req_id_elem is None:
            raise ValueError("Invalid Response XML: missing required elements")
            
        response_type = ResponseType(request_elem.text)
        req_id = req_id_elem.text if req_id_elem.text else ""
        message = msg_elem.text if msg_elem is not None and msg_elem.text else ""
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

    @staticmethod
    def average(items: List['GISData']) -> 'Ave':
        """Compute 3D average position from a list of GISData items."""
        if not items:
            return Ave()
        sum_x = sum(item.x for item in items)
        sum_y = sum(item.y for item in items)
        sum_z = sum(item.z for item in items)
        count = len(items)
        return Ave(sum_x / count, sum_y / count, sum_z / count)

    @staticmethod
    def average_2d(items: List['GISData']) -> 'Ave':
        """Compute 2D average position (x, y only) from a list of GISData items."""
        if not items:
            return Ave()
        sum_x = sum(item.x for item in items)
        sum_y = sum(item.y for item in items)
        count = len(items)
        return Ave(sum_x / count, sum_y / count, 0.0)