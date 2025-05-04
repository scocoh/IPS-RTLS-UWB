# /home/parcoadmin/parco_fastapi/app/models.py
# Name: models.py
# Version: 0.1.1
# Created: 971201
# Modified: 250503
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE
#
# CHANGED: Made zone_id optional in TriggerAddRequest, added portable trigger fields, bumped to 0.1.1

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

# [Other models unchanged]

class DeviceAddRequest(BaseModel):
    device_id: str
    device_type: int
    device_name: Optional[str] = None
    start_date: Optional[datetime] = None

class AssignDeviceRequest(BaseModel):
    device_id: str
    entity_id: str
    reason_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PositionRequest(BaseModel):
    device_id: str
    start_time: datetime
    end_time: datetime
    x: float
    y: float
    z: float

class TextEventRequest(BaseModel):
    device_id: str
    event_data: str
    timestamp: Optional[datetime] = None

class DeviceStateRequest(BaseModel):
    device_id: str
    new_state: str

class AssignDeviceDeleteRequest(BaseModel):
    assignment_id: int

class AssignDeviceEditRequest(BaseModel):
    assignment_id: int
    device_id: str
    entity_id: str
    reason_id: int

class AssignDeviceEndRequest(BaseModel):
    assignment_id: int

class EntityAssignRequest(BaseModel):
    parent_id: str
    child_id: str
    reason_id: int

class EntityAssignEndRequest(BaseModel):
    assignment_id: int

class AssignmentReasonRequest(BaseModel):
    reason: str

class DeviceTypeRequest(BaseModel):
    description: str

class DeviceEndDateRequest(BaseModel):
    device_id: str
    end_date: Optional[datetime] = None

class EntityRequest(BaseModel):
    entity_id: str
    entity_type: int
    entity_name: Optional[str] = None

class EntityTypeRequest(BaseModel):
    type_name: str

class MapRequest(BaseModel):
    map_name: str
    map_path: str
    map_format: str
    map_scale: float
    zone_id: int

class RegionRequest(BaseModel):
    region_id: int
    zone_id: int
    region_name: str
    max_x: float
    max_y: float
    max_z: float
    min_x: float
    min_y: float
    min_z: float
    trigger_id: int

class ResourceRequest(BaseModel):
    resource_type: int
    resource_name: str
    resource_ip: str
    resource_port: int
    resource_rank: int
    resource_fs: bool
    resource_avg: bool

class TriggerAddRequest(BaseModel):
    direction: int
    name: str
    ignore: bool
    zone_id: Optional[int] = None
    vertices: List[Dict[str, float]] = []
    is_portable: bool = False
    assigned_tag_id: Optional[str] = None
    radius_ft: Optional[float] = None
    z_min: Optional[float] = None
    z_max: Optional[float] = None

class TriggerMoveRequest(BaseModel):
    new_x: float
    new_y: float
    new_z: float

class VertexRequest(BaseModel):
    region_id: int
    x: float
    y: float
    z: Optional[float] = None
    order: int

class VertexEditRequest(BaseModel):
    vertex_id: int
    region_id: int
    x: float
    y: float
    z: Optional[float] = None
    order: int

class ZoneRequest(BaseModel):
    zone_type: int
    zone_name: str
    parent_zone: Optional[int] = None