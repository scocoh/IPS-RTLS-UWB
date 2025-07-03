# Name: heartbeat_manager.py
# Version: 0.1.5
# Created: 250526
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & TC
# Description: Manages heartbeat logic for ParcoRTLS WebSocket servers
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# Version History:
# - v0.1.5: Fixed return type annotation for validate_response method, bumped from 0.1.4
# - v0.1.4: Reverted logger to use __name__ for consistency, bumped from 0.1.3
# - v0.1.3: Fixed state check for FastAPI WebSocket, ensured proper disconnection, bumped from 0.1.2
# - v0.1.2: Added violation tracking in check_timeout, added is_connected method, bumped from 0.1.1
# - v0.1.1: Added violation tracking in check_timeout, added is_connected method, bumped from 0.1.0
# - v0.1.0: Initial implementation of HeartbeatManager

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)

class HeartbeatManager:
    def __init__(self, websocket, client_id="unknown", interval=30, timeout=5):
        self.websocket = websocket                  # WebSocket connection
        self.client_id = client_id                  # Tag or user ID
        self.interval = interval                    # Time between heartbeats
        self.timeout = timeout                      # Max wait for response
        self.heartbeat_id = None                    # Last heartbeat ID sent
        self.last_heartbeat = None                  # Timestamp of last sent heartbeat
        self.last_received_time = datetime.utcnow() # Timestamp of last valid response
        self.violation_count = 0                    # Heartbeat violations counter
        self._connected = True                      # Track connection state

    async def start(self, manager_instance=None):
        """
        Compatibility method for websocket servers.
        
        Args:
            manager_instance: Optional manager instance (ignored for compatibility)
            
        Returns:
            bool: True if started successfully
        """
        logger = logging.getLogger(__name__)
        logger.info("HeartbeatManager.start() called - compatibility mode")
        return True

    async def send_heartbeat(self):
        """Send a heartbeat with a unique timestamp ID."""
        if not self._connected:
            return
        self.heartbeat_id = str(int(time.time() * 1000))
        heartbeat_msg = {
            "type": "HeartBeat",
            "ts": int(time.time() * 1000),
            "data": {
                "heartbeat_id": self.heartbeat_id
            }
        }
        try:
            await self.websocket.send_json(heartbeat_msg)
            self.last_heartbeat = datetime.utcnow()
            logger.info(f"[{self.client_id}] Sent heartbeat ID: {self.heartbeat_id}")
        except Exception as e:
            logger.error(f"[{self.client_id}] Failed to send heartbeat: {e}")
            self._connected = False

    async def check_timeout(self):
        """Check if the client has failed to respond in time."""
        if not self._connected:
            return
        now = datetime.utcnow()
        if self.last_heartbeat and (now - self.last_heartbeat) > timedelta(seconds=self.timeout):
            self.violation_count += 1
            logger.warning(f"[{self.client_id}] No response to heartbeat ID {self.heartbeat_id}. Violations: {self.violation_count}")
            if self.violation_count >= 3:
                logger.error(f"[{self.client_id}] Disconnect: too many heartbeat violations.")
                try:
                    await self.websocket.send_json({
                        "type": "EndStream",
                        "reason": "Too many invalid heartbeats"
                    })
                    await self.websocket.close()
                    self._connected = False
                except Exception as e:
                    logger.error(f"[{self.client_id}] Error during forced disconnect: {e}")
                    self._connected = False

    def validate_response(self, message: dict) -> Optional[bool]:
        """
        Validate the incoming heartbeat response.

        Returns:
        - True if valid
        - None if ignored
        - False if invalid and should disconnect
        """
        if not self._connected:
            return False
        if message.get("type") != "HeartBeat":
            return None

        received_id = message.get("data", {}).get("heartbeat_id")
        if received_id == self.heartbeat_id:
            self.violation_count = 0
            self.last_received_time = datetime.utcnow()
            logger.info(f"[{self.client_id}] Valid heartbeat response ID: {received_id}")
            return True
        else:
            self.violation_count += 1
            logger.warning(f"[{self.client_id}] Invalid heartbeat ID: {received_id}. Violations: {self.violation_count}")
            if self.violation_count >= 3:
                logger.error(f"[{self.client_id}] Disconnect: too many invalid heartbeats.")
                return False
            return None

    def too_frequent(self) -> Optional[bool]:
        """Return True if client is sending heartbeats too frequently."""
        if not self._connected:
            return False
        now = datetime.utcnow()
        seconds_since_last = (now - self.last_received_time).total_seconds()
        if seconds_since_last < self.interval:
            self.violation_count += 1
            logger.warning(f"[{self.client_id}] Heartbeat too frequent ({seconds_since_last:.2f}s). Violations: {self.violation_count}")
            if self.violation_count >= 3:
                logger.error(f"[{self.client_id}] Disconnect: too many frequent heartbeats.")
                return False
            return True
        return False

    def is_connected(self) -> bool:
        """Return True if the WebSocket is still connected."""
        return self._connected and self.websocket.state == WebSocketState.CONNECTED