# Name: manager_heartbeat.py
# Version: 0.1.0
# Created: 250703
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Heartbeat handler module for ParcoRTLS Manager - Extracted from manager.py v0.1.22
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Heartbeat Handler Module for ParcoRTLS Manager

This module handles all heartbeat operations for the Manager class including:
- Heartbeat loop management
- Rate limiting for clients
- Client cleanup and failure handling
- SDK and WebSocket client heartbeat processing

Extracted from manager.py v0.1.22 for better modularity and maintainability.
"""

import asyncio
import json
import logging
from datetime import datetime
from collections import deque
from typing import Dict, List
from fastapi import WebSocket
from manager.models import HeartBeat, Response, ResponseType
from manager.sdk_client import SDKClient

logger = logging.getLogger(__name__)

class ManagerHeartbeat:
    """
    Handles all heartbeat operations for the Manager class.
    
    This class encapsulates heartbeat loop management, rate limiting,
    and client cleanup operations that were previously part of the main Manager class.
    """
    
    def __init__(self, manager_name: str):
        """
        Initialize the heartbeat handler.
        
        Args:
            manager_name: Name of the manager instance for logging
        """
        self.manager_name = manager_name
        self.send_sdk_heartbeat = True
        self.last_heartbeat = 0
        self._heartbeat_task = None
        
        # Rate-limiting configuration
        self.HEARTBEAT_INTERVAL = 30.0  # Heartbeat every 30 seconds
        self.HEARTBEAT_RATE_LIMIT = 1   # Max 1 heartbeat per 30s
        
        # Rate-limiting storage
        self.ws_heartbeat_timestamps: Dict[str, deque] = {}  # For WebSocket clients
        self.sdk_heartbeat_timestamps: Dict[str, deque] = {}  # For SDK clients
        
        logger.debug(f"Initialized ManagerHeartbeat for manager: {manager_name}")

    async def start(self, manager_instance=None) -> bool:
        """
        Compatibility method for existing websocket servers.
        
        Args:
            manager_instance: Optional manager instance reference
            
        Returns:
            bool: True if started successfully
        """
        if manager_instance:
            return await self.start_heartbeat_loop(manager_instance)
        else:
            logger.warning("start() called without manager instance - heartbeat not started")
            return False

    async def start_heartbeat_loop(self, manager_instance) -> bool:
        """
        Start the heartbeat loop task.
        
        Args:
            manager_instance: Reference to the main manager instance
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if self._heartbeat_task is None:
                logger.debug("Starting heartbeat loop task")
                self._heartbeat_task = asyncio.create_task(self.heartbeat_loop(manager_instance))
                logger.debug("Heartbeat loop started")
                return True
            else:
                logger.warning("Heartbeat loop already running")
                return False
        except Exception as e:
            logger.error(f"Failed to start heartbeat loop: {str(e)}")
            return False

    async def stop_heartbeat_loop(self) -> bool:
        """
        Stop the heartbeat loop task.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self._heartbeat_task and not self._heartbeat_task.done():
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
                self._heartbeat_task = None
                logger.debug("Heartbeat loop stopped")
                return True
            return True
        except Exception as e:
            logger.error(f"Error stopping heartbeat loop: {str(e)}")
            return False

    async def heartbeat_loop(self, manager_instance):
        """
        Main heartbeat loop that manages SDK and WebSocket client heartbeats.
        
        Args:
            manager_instance: Reference to the main manager instance
        """
        logger.debug("Entering heartbeat_loop")
        
        while manager_instance.run_state in [manager_instance.run_state.__class__.Started, manager_instance.run_state.__class__.Starting]:
            try:
                logger.debug(f"Heartbeat loop iteration, run_state: {manager_instance.run_state}, clients: {len(manager_instance.sdk_clients)}")
                
                if not self.send_sdk_heartbeat:
                    logger.debug("Heartbeats disabled, exiting loop")
                    return

                # Process heartbeats
                to_kill = []
                current_time = asyncio.get_event_loop().time()
                hb = HeartBeat(ticks=int(current_time * 1000))
                json_message = json.dumps({
                    "type": "HeartBeat",
                    "ts": hb.ticks,
                    "heartbeat_id": str(int(datetime.now().timestamp() * 1000))
                })
                
                logger.info(f"Manager sending heartbeat to {len(manager_instance.sdk_clients)} SDK clients and {sum(len(clients) for clients in manager_instance.clients.values())} WebSocket clients, ts: {hb.ticks}, message: {json_message}")

                # Initialize rate-limiting for WebSocket and SDK clients
                self._initialize_rate_limiting(manager_instance)

                # Process SDK clients with strict rate-limiting
                to_kill.extend(await self._process_sdk_clients(manager_instance, current_time, json_message))

                # Process WebSocket clients with strict rate-limiting
                await self._process_websocket_clients(manager_instance, current_time, json_message)

                self.last_heartbeat = hb.ticks
                logger.debug(f"Updated last_heartbeat to {self.last_heartbeat}")

                # Send EndStream response to SDK clients marked for killing
                if to_kill:
                    await self._send_endstream_responses(to_kill)

                # Clean up SDK clients marked for killing
                await self._cleanup_sdk_clients(manager_instance, to_kill)

                # Sleep for HEARTBEAT_INTERVAL
                elapsed_time = asyncio.get_event_loop().time() - current_time
                sleep_time = max(0, self.HEARTBEAT_INTERVAL - elapsed_time)
                logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                logger.debug("Finished sleeping")
                
            except Exception as e:
                logger.error(f"Heartbeat loop error: {str(e)}")
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                
        logger.debug("Exiting heartbeat_loop")

    def _initialize_rate_limiting(self, manager_instance):
        """Initialize rate limiting for all clients."""
        for reqid in manager_instance.clients:
            if reqid not in self.ws_heartbeat_timestamps:
                self.ws_heartbeat_timestamps[reqid] = deque(maxlen=self.HEARTBEAT_RATE_LIMIT)
        for client_id in manager_instance.sdk_clients:
            if client_id not in self.sdk_heartbeat_timestamps:
                self.sdk_heartbeat_timestamps[client_id] = deque(maxlen=self.HEARTBEAT_RATE_LIMIT)

    async def _process_sdk_clients(self, manager_instance, current_time: float, json_message: str) -> List[SDKClient]:
        """
        Process SDK clients for heartbeats.
        
        Returns:
            List of SDK clients to be killed
        """
        to_kill = []
        clients_to_process = list(manager_instance.sdk_clients.items())
        
        for client_id, client in clients_to_process:
            if client.is_closing:
                logger.debug(f"Skipping SDK client {client_id}: already closing")
                continue
                
            if client.heartbeat < self.last_heartbeat and client.heartbeat != 0:
                logger.debug(f"SDK client {client_id} failed heartbeat check, marking to kill")
                client.is_closing = True
                to_kill.append(client)
                continue

            # Rate-limit SDK client heartbeats
            timestamps = self.sdk_heartbeat_timestamps[client_id]
            timestamps.append(current_time)
            if len(timestamps) == self.HEARTBEAT_RATE_LIMIT:
                time_window = current_time - timestamps[0]
                if time_window < self.HEARTBEAT_INTERVAL:
                    logger.warning(f"Heartbeat rate exceeded {self.HEARTBEAT_RATE_LIMIT} messages per {self.HEARTBEAT_INTERVAL}s for SDK client {client_id}")
                    continue

            try:
                if client.heartbeat == 0:
                    client.heartbeat = self.last_heartbeat
                client.failed_heartbeat = False
                await client.websocket.send_text(json_message)
                logger.debug(f"Sent heartbeat to SDK client {client_id}: {json_message}")
            except Exception as e:
                logger.error(f"Failed to send heartbeat to SDK client {client_id}: {str(e)}")
                client.failed_heartbeat = True
                client.is_closing = True
                to_kill.append(client)
                
        return to_kill

    async def _process_websocket_clients(self, manager_instance, current_time: float, json_message: str):
        """Process WebSocket clients for heartbeats."""
        for reqid, clients in list(manager_instance.clients.items()):
            timestamps = self.ws_heartbeat_timestamps[reqid]
            timestamps.append(current_time)
            if len(timestamps) == self.HEARTBEAT_RATE_LIMIT:
                time_window = current_time - timestamps[0]
                if time_window < self.HEARTBEAT_INTERVAL:
                    logger.warning(f"Heartbeat rate exceeded {self.HEARTBEAT_RATE_LIMIT} messages per {self.HEARTBEAT_INTERVAL}s for WebSocket clients with reqid {reqid}")
                    continue

            for client in clients:
                try:
                    await client.send_json(json.loads(json_message))
                    logger.debug(f"Sent heartbeat to WebSocket client {reqid}: {json_message}")
                except Exception as e:
                    logger.error(f"Failed to send heartbeat to WebSocket client {reqid}: {str(e)}")
                    clients.remove(client)
                    if not clients:
                        del manager_instance.clients[reqid]
                        del self.ws_heartbeat_timestamps[reqid]

    async def _send_endstream_responses(self, to_kill: List[SDKClient]):
        """Send EndStream responses to clients marked for killing."""
        resp = Response(
            response_type=ResponseType.EndStream,
            req_id="",
            message=f"Failed to respond to heart beat {self.last_heartbeat}"
        )
        json_resp_message = resp.to_json()
        for client in to_kill:
            try:
                await client.websocket.send_text(json_resp_message)
                logger.info(f"SDK Client Heartbeat Failure response sent for {client.client_id}")
            except Exception as e:
                logger.error(f"Failed to send EndStream to SDK client {client.client_id}: {str(e)}")

    async def _cleanup_sdk_clients(self, manager_instance, to_kill: List[SDKClient]):
        """Clean up SDK clients marked for killing."""
        # Clean up SDK clients marked for killing
        for client in manager_instance.kill_list:
            if client in manager_instance.sdk_clients.values():
                await self._close_client(manager_instance, client)

        manager_instance.kill_list = to_kill

        # Clean up stale SDK clients
        for client_id, client in list(manager_instance.sdk_clients.items()):
            if client.is_closing or client.failed_heartbeat:
                await self._close_client(manager_instance, client)
                if client_id in self.sdk_heartbeat_timestamps:
                    del self.sdk_heartbeat_timestamps[client_id]

    async def _close_client(self, manager_instance, client: SDKClient):
        """Close an SDK client and remove it from tracking."""
        logger.debug(f"Closing SDK client {client.client_id}")
        try:
            if client and not client.is_closing:
                await client.close()
            if client.client_id in manager_instance.sdk_clients:
                del manager_instance.sdk_clients[client.client_id]
                logger.debug(f"SDK client {client.client_id} removed from sdk_clients")
        except Exception as e:
            logger.error(f"CloseClient Error: {str(e)}")

    def is_heartbeat_running(self) -> bool:
        """Check if heartbeat loop is currently running."""
        return self._heartbeat_task is not None and not self._heartbeat_task.done()

    def set_heartbeat_enabled(self, enabled: bool):
        """Enable or disable heartbeat processing."""
        self.send_sdk_heartbeat = enabled
        logger.debug(f"Heartbeat enabled set to: {enabled}")

    def get_heartbeat_stats(self) -> dict:
        """Get heartbeat statistics."""
        return {
            'last_heartbeat': self.last_heartbeat,
            'interval': self.HEARTBEAT_INTERVAL,
            'rate_limit': self.HEARTBEAT_RATE_LIMIT,
            'enabled': self.send_sdk_heartbeat,
            'running': self.is_heartbeat_running(),
            'ws_clients_tracked': len(self.ws_heartbeat_timestamps),
            'sdk_clients_tracked': len(self.sdk_heartbeat_timestamps)
        }