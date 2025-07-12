# Name: sdk_client.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

""" # Name: sdk_client.py
# Version: 0.1.2
# Created: 971201
# Modified: 250709
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Python script for ParcoRTLS backend - Added last_message_type tracking for heartbeat filtering
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE
"""

from queue import Queue
import asyncio
from typing import Dict, Optional, TYPE_CHECKING
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from .models import Tag
import logging

if TYPE_CHECKING:
    from .models import Request

logger = logging.getLogger(__name__)

class SDKClient:
    def __init__(self, websocket: WebSocket, client_id: str, zone_id: Optional[int] = None):
        self.websocket = websocket
        self.client_id = client_id
        self._zone_id = zone_id  # NEW: Zone ID this client is subscribed to
        logger.debug(f"Initialized SDKClient {client_id} with zone_id={self._zone_id}")
        self.heartbeat = 0
        self.failed_heartbeat = False
        self.received_data = False
        self.began_listening = datetime.utcnow()
        self.request_msg: Optional['Request'] = None  # Can be None or Request object
        self.tags: Dict[str, Tag] = {}
        self.is_closing = False
        self.sent_req = False
        self.sent_begin_msg = False
        self.q = Queue(maxsize=10000)
        self.parent = None
        self.last_sent_message = None
        self.q_timer_task = None
        self._is_closed = False

        self.last_message_type: Optional[str] = None  # Tracks last message type received from client (e.g., HeartBeat, GISData)

    @property
    def zone_id(self) -> Optional[int]:
        return self._zone_id

    @zone_id.setter
    def zone_id(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            logger.error(f"Invalid zone_id for client {self.client_id}: {value}, must be an integer")
            raise ValueError("zone_id must be an integer")
        logger.debug(f"Setting zone_id for client {self.client_id} to {value}")
        self._zone_id = value

    async def q_timer(self):
        while not self.is_closing:
            try:
                logger.debug(f"q_timer for client {self.client_id}: checking queue, size={self.q.qsize()}")
                while not self.q.empty():
                    if self.is_closing:
                        logger.debug(f"q_timer for client {self.client_id}: exiting due to client closing")
                        return
                    msg = self.q.get_nowait()
                    if msg == self.last_sent_message:
                        logger.debug(f"q_timer for client {self.client_id}: skipping duplicate message: {msg}")
                        continue
                    await self.websocket.send_text(msg)
                    self.last_sent_message = msg
                    logger.debug(f"q_timer sent message to client {self.client_id}: {msg}")
            except WebSocketDisconnect:
                logger.debug(f"q_timer for client {self.client_id}: WebSocket disconnected, exiting")
                self.is_closing = True
                return
            except Exception as ex:
                logger.error(f"Hall QTimer Err for client {self.client_id}: {str(ex)}")
                self.is_closing = True
                return
            logger.debug(f"q_timer for client {self.client_id}: sleeping for 5 seconds")
            await asyncio.sleep(5)
            logger.debug(f"q_timer for client {self.client_id}: finished sleeping")

    def start_q_timer(self):
        """Start the q_timer task and store it."""
        if self.q_timer_task is None or self.q_timer_task.done():
            self.q_timer_task = asyncio.create_task(self.q_timer())
            logger.debug(f"Started q_timer task for client {self.client_id}")

    async def close(self):
        """Cancel the q_timer task and close the WebSocket."""
        if self.is_closing:
            logger.debug(f"Client {self.client_id} already closing, skipping close")
            return
        self.is_closing = True
        if self.q_timer_task and not self.q_timer_task.done():
            self.q_timer_task.cancel()
            try:
                await self.q_timer_task
            except asyncio.CancelledError:
                logger.debug(f"q_timer task for client {self.client_id} cancelled")
        if not self._is_closed:
            try:
                await self.websocket.close()
                logger.debug(f"Closed WebSocket for client {self.client_id}")
                self._is_closed = True
            except Exception as ex:
                logger.debug(f"Error closing WebSocket for client {self.client_id}: {str(ex)}")
                self._is_closed = True

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
