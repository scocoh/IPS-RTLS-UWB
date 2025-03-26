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