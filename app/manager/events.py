# Name: events.py
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

from dataclasses import dataclass
from .models import Tag, HeartBeat, Response

@dataclass
class StreamDataEventArgs:
    tag: Tag

@dataclass
class StreamHeartbeatEventArgs:
    heartbeat: HeartBeat

@dataclass
class StreamResponseEventArgs:
    response: Response

@dataclass
class StreamConnectionEventArgs:
    state: str