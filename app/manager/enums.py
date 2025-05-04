# Name: enums.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

from enum import Enum

class eMode(Enum):
    Subscription = 0
    Stream = 1

class eRunState(Enum):
    Stopped = "Stopped"
    Starting = "Starting"
    Started = "Started"
    Stopping = "Stopping"

class EventLogEntryType(Enum):
    Information = "Information"
    Warning = "Warning"
    Error = "Error"
    FailureAudit = "FailureAudit"

class RequestType(Enum):
    BeginStream = "BgnStrm"
    EndStream = "EndStrm"
    AddTag = "AddTag"
    RemoveTag = "RemTag"

class ResponseType(Enum):
    BeginStream = "BgnStrm"
    EndStream = "EndStrm"
    AddTag = "AddTag"
    RemoveTag = "RemTag"
    Unknown = "Unknown"  # NEW: Added for fallback

class ConnectionState(Enum):
    NotKnown = "NotKnown"
    Connected = "Connected"
    Disconnected = "Disconnected"
    Blocking = "Blocking"

class TriggerDirections(Enum):
    NotSet = 0
    WhileIn = 1
    WhileOut = 2
    OnCross = 3
    OnEnter = 4
    OnExit = 5

class TriggerState(Enum):
    NotKnown = 0
    InSide = 1
    OutSide = 2