from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET  # Add this import
from .utils import MessageUtilities
from .enums import RequestType, ResponseType  # Add these imports

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
        return MessageUtilities.XMLDefTag + ET.tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_str: str):
        root = ET.fromstring(xml_str)
        gis = root.find("gis")
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
            data=root.find("data").text or ""
        )

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

class Ave:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z