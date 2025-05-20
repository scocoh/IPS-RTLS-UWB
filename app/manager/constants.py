# Name: constants.py
# Version: 0.1.0
# Created: 250513
# Modified: 250513
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Shared constants for ParcoRTLS WebSocket servers
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

from .enums import RequestType

# Map of supported WebSocket request types
REQUEST_TYPE_MAP = {
    "BeginStream": RequestType.BeginStream,
    "EndStream": RequestType.EndStream,
    "AddTag": RequestType.AddTag,
    "RemoveTag": RequestType.RemoveTag,
    "CreateStream": "CreateStream",
    "FetchMaps": "FetchMaps",
    "FetchZones": "FetchZones",
    "FetchVertices": "FetchVertices",
    "FetchRegions": "FetchRegions",
    "FetchTriggers": "FetchTriggers",
    "FetchResourceTypes": "FetchResourceTypes",
    "FetchZoneTypes": "FetchZoneTypes",
    "FetchTrigDirections": "FetchTrigDirections",
    "FetchDeviceAssmts": "FetchDeviceAssmts",
    "FetchEntities": "FetchEntities",
    "FetchAssmtReasons": "FetchAssmtReasons",
    "FetchEntityTypes": "FetchEntityTypes"
}

# List of fetch request types for database queries
NEW_REQUEST_TYPES = [
    "FetchMaps", "FetchZones", "FetchVertices", "FetchRegions", "FetchTriggers",
    "FetchResourceTypes", "FetchZoneTypes", "FetchTrigDirections",
    "FetchDeviceAssmts", "FetchEntities", "FetchAssmtReasons", "FetchEntityTypes"
]