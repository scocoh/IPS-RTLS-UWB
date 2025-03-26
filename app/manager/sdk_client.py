from queue import Queue
import asyncio
from typing import Dict
from datetime import datetime  # Add this import
from fastapi import WebSocket
from .models import Tag
import logging

logger = logging.getLogger(__name__)

class SDKClient:
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.buffer = ""
        self.heartbeat = 0
        self.failed_heartbeat = False
        self.received_data = False
        self.began_listening = datetime.utcnow()
        self.request_msg = None
        self.tags: Dict[str, Tag] = {}
        self.is_closing = False
        self.sent_req = False
        self.sent_begin_msg = False
        self.q = Queue(maxsize=10000)
        self.parent = None

    async def q_timer(self):
        while not self.is_closing:
            try:
                while not self.q.empty():
                    msg = self.q.get_nowait()
                    await self.websocket.send_text(msg)
            except Exception as ex:
                logger.error(f"Hall QTimer Err: {str(ex)}")
            await asyncio.sleep(1)

    def contains_tag(self, tag_id: str) -> bool:
        return tag_id in self.tags

    def add_tag(self, tag_id: str, tag: Tag) -> bool:
        if tag_id not in self.tags:
            self.tags[tag_id] = tag
            return True
        return False

    def remove_tag(self, tag_id: str) -> bool:
        if tag_id in self.tags:
            del self.tags[tag_id]
            return True
        return False

    @property
    def has_request(self) -> bool:
        return self.sent_req

    @property
    def count(self) -> int:
        return len(self.tags)