# Name: manager_heartbeat.py
# Version: 0.1.2
# Created: 971201
# Modified: 250716
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & AI Assistant
# Description: Heartbeat handler module for ParcoRTLS Manager - Fixed excessive port health monitoring console messages with response time thresholds
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
- Port health monitoring for dynamic scaling

Extracted from manager.py v0.1.22 for better modularity and maintainability.
"""

import asyncio
import json
import logging
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
from fastapi import WebSocket
from manager.models import HeartBeat, Response, ResponseType
from manager.sdk_client import SDKClient
import asyncpg
import socket
import time

logger = logging.getLogger(__name__)

class ManagerHeartbeat:
    """
    Handles all heartbeat operations for the Manager class.

    This class encapsulates heartbeat loop management, rate limiting,
    client cleanup operations, and port health monitoring for dynamic scaling.
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

        # Port health monitoring configuration (defaults, can be overridden from database)
        self.PORT_HEALTH_CHECK_INTERVAL = 30.0  # Check port health every 30 seconds
        self.PORT_HEALTH_TIMEOUT = 5.0  # Timeout for port health checks
        self.PORT_HEALTH_FAILURE_THRESHOLD = 2  # Consecutive failures before marking unhealthy
        
        # Port health response time thresholds (milliseconds)
        self.PORT_HEALTH_WARNING_THRESHOLD = 200.0   # 200ms = warning
        self.PORT_HEALTH_UNHEALTHY_THRESHOLD = 750.0  # 750ms = unhealthy
        
        # Port health monitoring storage
        self.port_health_monitor: Dict[int, Dict] = {}  # Port monitoring data
        self.port_health_initialized = False  # Track if ports have been loaded
        self.last_database_error = None  # Track last database error for debugging
        
        # Scaling configuration
        self.SCALING_PORT_RANGE_START = 8200  # Start of dynamic port range
        self.SCALING_PORT_RANGE_END = 8299    # End of dynamic port range
        self.SCALING_TARGET_PORTS = [8002]    # Ports that can be scaled (RealTimeManager)
        
        # Port monitoring will be driven by f_monitor_enabled column in tlkresources table
        
        logger.debug(f"Initialized ManagerHeartbeat for manager: {manager_name}")

    async def initialize_port_monitoring(self, manager_instance) -> bool:
        """
        Initialize port health monitoring by loading ports from tlkresources table.
        
        Args:
            manager_instance: Reference to the main manager instance
            
        Returns:
            bool: True if successfully initialized
        """
        try:
            if self.port_health_initialized:
                logger.debug("Port monitoring already initialized")
                return True
                
            # Get database connection from manager instance
            if not hasattr(manager_instance, 'database') or not manager_instance.database.is_database_ready():
                logger.warning("Database not ready for port monitoring initialization")
                return False
                
            # Load ports from tlkresources table
            connection_strings = manager_instance.database.get_connection_strings()
            
            # Handle both dict and tuple formats for connection strings
            if isinstance(connection_strings, dict):
                connection_string = connection_strings.get('maint')
            elif isinstance(connection_strings, tuple):
                # If it's a tuple, assume it's the maint connection string
                connection_string = connection_strings[0] if connection_strings else None
            else:
                connection_string = str(connection_strings)
                
            if not connection_string:
                logger.error("No maintenance database connection string available")
                return False
                
            async with asyncpg.create_pool(connection_string) as pool:
                async with pool.acquire() as conn:
                    # Load ports with optional monitoring configuration
                    ports_query = """
                        SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                               COALESCE(i_monitor_interval, 30) as monitor_interval,
                               COALESCE(i_monitor_timeout, 5) as monitor_timeout,
                               COALESCE(i_monitor_threshold, 2) as monitor_threshold,
                               COALESCE(f_monitor_enabled, true) as monitor_enabled
                        FROM tlkresources 
                        WHERE i_prt > 0 
                        ORDER BY i_prt
                    """
                    
                    ports_result = await conn.fetch(ports_query)
                    
                    for row in ports_result:
                        port_num = row['i_prt']
                        resource_name = row['x_nm_res']
                        resource_type = row['i_typ_res']
                        ip_address = row['x_ip']
                        is_fs = row['f_fs']  # FastAPI service flag
                        
                        # Get monitoring configuration from database (if columns exist)
                        monitor_interval = row.get('monitor_interval', 30)
                        monitor_timeout = row.get('monitor_timeout', 5)
                        monitor_threshold = row.get('monitor_threshold', 2)
                        monitor_enabled = row.get('monitor_enabled', True)
                        
                        # Skip if monitoring is disabled in database OR port is 0
                        if not monitor_enabled or port_num <= 0:
                            logger.debug(f"Skipping port {port_num} ({resource_name}) - monitoring disabled or invalid port")
                            continue
                        
                        # Initialize port health monitoring
                        self.port_health_monitor[port_num] = {
                            'resource_name': resource_name,
                            'resource_type': resource_type,
                            'ip_address': ip_address,
                            'is_fs': is_fs,
                            'monitor_enabled': monitor_enabled,
                            'monitor_interval': monitor_interval,
                            'monitor_timeout': monitor_timeout,
                            'monitor_threshold': monitor_threshold,
                            'consecutive_failures': 0,
                            'last_success_time': None,
                            'last_failure_time': None,
                            'response_times': deque(maxlen=10),
                            'is_healthy': True,
                            'total_checks': 0,
                            'total_failures': 0,
                            'last_check_time': None,
                            'is_scaling_candidate': port_num in self.SCALING_TARGET_PORTS
                        }
                        
                        logger.debug(f"Added port {port_num} ({resource_name}) to health monitoring")
                    
                    self.port_health_initialized = True
                    self.last_database_error = None  # Clear any previous errors
                    logger.info(f"Port health monitoring initialized for {len(self.port_health_monitor)} ports based on database f_monitor_enabled settings")
                    return True
                    
        except Exception as e:
            self.last_database_error = {
                'error': str(e),
                'timestamp': datetime.now(),
                'operation': 'initialize_port_monitoring'
            }
            logger.error(f"Failed to initialize port monitoring: {str(e)}")
            return False

    async def refresh_port_monitoring(self, manager_instance) -> bool:
        """
        Manually refresh the port list from the database.
        
        Args:
            manager_instance: Reference to the main manager instance
            
        Returns:
            bool: True if successfully refreshed
        """
        try:
            logger.info("Manually refreshing port monitoring from database")
            
            # Reset initialization flag to force reload
            self.port_health_initialized = False
            
            # Clear existing monitoring data
            old_port_count = len(self.port_health_monitor)
            self.port_health_monitor.clear()
            
            # Re-initialize
            success = await self.initialize_port_monitoring(manager_instance)
            
            if success:
                new_port_count = len(self.port_health_monitor)
                logger.info(f"Port monitoring refreshed: {old_port_count} → {new_port_count} ports")
                return True
            else:
                logger.error("Failed to refresh port monitoring")
                return False
                
        except Exception as e:
            self.last_database_error = {
                'error': str(e),
                'timestamp': datetime.now(),
                'operation': 'refresh_port_monitoring'
            }
            logger.error(f"Error refreshing port monitoring: {str(e)}")
            return False

    def get_unhealthy_ports(self) -> Dict[int, Dict]:
        """
        Get list of unhealthy ports for scaling decisions.
        
        Returns:
            dict: Dictionary of unhealthy ports with their details
        """
        unhealthy_ports = {}
        
        for port, port_info in self.port_health_monitor.items():
            if not port_info['is_healthy']:
                unhealthy_ports[port] = {
                    'resource_name': port_info['resource_name'],
                    'resource_type': port_info['resource_type'],
                    'consecutive_failures': port_info['consecutive_failures'],
                    'total_failures': port_info['total_failures'],
                    'is_scaling_candidate': port_info['is_scaling_candidate'],
                    'last_failure_time': port_info['last_failure_time'],
                    'can_scale': port in self.SCALING_TARGET_PORTS
                }
        
        return unhealthy_ports

    def get_scaling_candidates(self) -> Dict[int, Dict]:
        """
        Get ports that are candidates for scaling (8000+ range, especially 8002).
        
        Returns:
            dict: Dictionary of ports that can be scaled
        """
        scaling_candidates = {}
        
        for port, port_info in self.port_health_monitor.items():
            # Focus on 8000+ ports for scaling
            if port >= 8000 and port < 9000:
                avg_response_time = sum(port_info['response_times']) / len(port_info['response_times']) if port_info['response_times'] else 0
                
                scaling_candidates[port] = {
                    'resource_name': port_info['resource_name'],
                    'resource_type': port_info['resource_type'],
                    'is_healthy': port_info['is_healthy'],
                    'consecutive_failures': port_info['consecutive_failures'],
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'is_scaling_candidate': port_info['is_scaling_candidate'],
                    'can_scale': port in self.SCALING_TARGET_PORTS,
                    'scaling_range': f"{self.SCALING_PORT_RANGE_START}-{self.SCALING_PORT_RANGE_END}" if port in self.SCALING_TARGET_PORTS else None
                }
        
        return scaling_candidates

    def get_next_scaling_port(self, base_port: int) -> Optional[int]:
        """
        Get the next available port in the scaling range.
        
        Args:
            base_port: Base port that needs scaling (e.g., 8002)
            
        Returns:
            int: Next available port in scaling range, or None if none available
        """
        if base_port not in self.SCALING_TARGET_PORTS:
            return None
            
        # For port 8002, scale to 8200-8299 range
        for port in range(self.SCALING_PORT_RANGE_START, self.SCALING_PORT_RANGE_END + 1):
            if port not in self.port_health_monitor:
                return port
                
        return None

    async def check_port_health(self, port: int, ip_address: str) -> tuple[bool, float]:
        """
        Check if a port is healthy by attempting to connect to it.
        
        Args:
            port: Port number to check
            ip_address: IP address to connect to
            
        Returns:
            tuple: (is_healthy, response_time_ms)
        """
        start_time = time.time()
        
        # Get port-specific timeout from database config
        port_info = self.port_health_monitor.get(port, {})
        timeout = port_info.get('monitor_timeout', self.PORT_HEALTH_TIMEOUT)
        
        try:
            # Create socket connection with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Attempt connection
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            is_healthy = (result == 0)
            
            # Only log based on response time thresholds (no more excessive logging)
            if is_healthy:
                if response_time_ms >= self.PORT_HEALTH_UNHEALTHY_THRESHOLD:
                    logger.warning(f"Port {port} health check: SLOW ({response_time_ms:.2f}ms)")
                elif response_time_ms >= self.PORT_HEALTH_WARNING_THRESHOLD:
                    logger.info(f"Port {port} health check: WARNING ({response_time_ms:.2f}ms)")
                # No logging for fast responses (0-199ms) - this fixes the excessive console spam
            else:
                logger.debug(f"Port {port} health check: UNHEALTHY - connection failed ({response_time_ms:.2f}ms)")
                
            return is_healthy, response_time_ms
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            logger.debug(f"Port {port} health check failed: {str(e)} ({response_time_ms:.2f}ms)")
            return False, response_time_ms

    async def update_port_health_stats(self, port: int, is_healthy: bool, response_time_ms: float):
        """
        Update port health statistics with response time threshold logging.
        
        Args:
            port: Port number
            is_healthy: Whether the port check was successful
            response_time_ms: Response time in milliseconds
        """
        if port not in self.port_health_monitor:
            logger.warning(f"Port {port} not in health monitor")
            return
            
        port_stats = self.port_health_monitor[port]
        current_time = datetime.now()
        
        # Update basic stats
        port_stats['total_checks'] += 1
        port_stats['last_check_time'] = current_time
        port_stats['response_times'].append(response_time_ms)
        
        if is_healthy:
            port_stats['consecutive_failures'] = 0
            port_stats['last_success_time'] = current_time
            
            # Mark as healthy if it was previously unhealthy
            if not port_stats['is_healthy']:
                port_stats['is_healthy'] = True
                logger.info(f"SCALING: Port {port} ({port_stats['resource_name']}) is now healthy")
                
        else:
            port_stats['consecutive_failures'] += 1
            port_stats['total_failures'] += 1
            port_stats['last_failure_time'] = current_time
            
            # Check if we should mark as unhealthy (use database threshold)
            if port_stats['consecutive_failures'] >= port_stats['monitor_threshold']:
                if port_stats['is_healthy']:  # Only log if status is changing
                    port_stats['is_healthy'] = False
                    logger.warning(f"SCALING: Port {port} ({port_stats['resource_name']}) unresponsive after {port_stats['consecutive_failures']} consecutive failures")
                    
                    # Special handling for port 8002 (RealTimeManager)
                    if port == 8002:
                        logger.warning(f"SCALING: Port 8002 unresponsive, prepare port 8200+ for dynamic scaling")

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
                if not self.send_sdk_heartbeat:
                    logger.debug("Heartbeats disabled, exiting loop")
                    return

                # Initialize port monitoring if not already done
                if not self.port_health_initialized:
                    await self.initialize_port_monitoring(manager_instance)

                # Heartbeat tracking
                to_kill = []
                current_time = asyncio.get_event_loop().time()
                hb = HeartBeat(ticks=int(current_time * 1000))
                json_message = json.dumps({
                    "type": "HeartBeat",
                    "ts": hb.ticks,
                    "heartbeat_id": str(int(datetime.now().timestamp() * 1000))
                })

                logger.info(f"Manager sending heartbeat to {len(manager_instance.sdk_clients)} SDK clients and {sum(len(clients) for clients in manager_instance.clients.values())} WebSocket clients, ts: {hb.ticks}, message: {json_message}")

                self._initialize_rate_limiting(manager_instance)

                to_kill.extend(await self._process_sdk_clients(manager_instance, current_time, json_message))
                await self._process_websocket_clients(manager_instance, current_time, json_message)

                # Perform port health checks
                await self._perform_port_health_checks()

                self.last_heartbeat = hb.ticks

                if to_kill:
                    await self._send_endstream_responses(to_kill)

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

    async def _perform_port_health_checks(self):
        """Perform health checks on all monitored ports."""
        if not self.port_health_initialized:
            return
            
        for port, port_info in self.port_health_monitor.items():
            try:
                is_healthy, response_time = await self.check_port_health(port, port_info['ip_address'])
                await self.update_port_health_stats(port, is_healthy, response_time)
            except Exception as e:
                logger.error(f"Error checking port {port} health: {str(e)}")

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
                continue

            # Missed heartbeat
            if client.heartbeat < self.last_heartbeat and client.heartbeat != 0:
                client.is_closing = True
                to_kill.append(client)
                continue

            # Only rate-limit if last message was a heartbeat
            if getattr(client, 'last_message_type', '') == "HeartBeat":
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
            for client in clients:
                try:
                    await client.send_json(json.loads(json_message))
                    logger.debug(f"Sent heartbeat to WebSocket client {reqid}: {json_message}")
                except Exception as e:
                    logger.error(f"Failed to send heartbeat to WebSocket client {reqid}: {str(e)}")
                    clients.remove(client)
                    if not clients:
                        del manager_instance.clients[reqid]
                        if reqid in self.ws_heartbeat_timestamps:
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
        for client in manager_instance.kill_list:
            if client in manager_instance.sdk_clients.values():
                await self._close_client(manager_instance, client)

        manager_instance.kill_list = to_kill

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
        """Get heartbeat statistics including port health monitoring."""
        port_health_stats = {}
        unhealthy_ports = []
        scaling_candidates = []
        
        for port, port_info in self.port_health_monitor.items():
            avg_response_time = sum(port_info['response_times']) / len(port_info['response_times']) if port_info['response_times'] else 0
            
            port_stats = {
                'resource_name': port_info['resource_name'],
                'resource_type': port_info['resource_type'],
                'is_healthy': port_info['is_healthy'],
                'monitor_enabled': port_info.get('monitor_enabled', True),
                'consecutive_failures': port_info['consecutive_failures'],
                'total_checks': port_info['total_checks'],
                'total_failures': port_info['total_failures'],
                'avg_response_time_ms': round(avg_response_time, 2),
                'last_check_time': port_info['last_check_time'].isoformat() if port_info['last_check_time'] else None,
                'last_success_time': port_info['last_success_time'].isoformat() if port_info['last_success_time'] else None,
                'last_failure_time': port_info['last_failure_time'].isoformat() if port_info['last_failure_time'] else None,
                'is_scaling_candidate': port_info.get('is_scaling_candidate', False),
                'can_scale': port in self.SCALING_TARGET_PORTS
            }
            
            port_health_stats[port] = port_stats
            
            # Track unhealthy ports
            if not port_info['is_healthy']:
                unhealthy_ports.append(port)
                
            # Track scaling candidates
            if port in self.SCALING_TARGET_PORTS:
                scaling_candidates.append(port)
        
        # Database error information
        database_error_info = None
        if self.last_database_error:
            database_error_info = {
                'error': self.last_database_error['error'],
                'timestamp': self.last_database_error['timestamp'].isoformat(),
                'operation': self.last_database_error['operation']
            }
        
        return {
            'last_heartbeat': self.last_heartbeat,
            'interval': self.HEARTBEAT_INTERVAL,
            'rate_limit': self.HEARTBEAT_RATE_LIMIT,
            'enabled': self.send_sdk_heartbeat,
            'running': self.is_heartbeat_running(),
            'ws_clients_tracked': len(self.ws_heartbeat_timestamps),
            'sdk_clients_tracked': len(self.sdk_heartbeat_timestamps),
            'port_health_monitoring': {
                'initialized': self.port_health_initialized,
                'ports_monitored': len(self.port_health_monitor),
                'check_interval': self.PORT_HEALTH_CHECK_INTERVAL,
                'failure_threshold': self.PORT_HEALTH_FAILURE_THRESHOLD,
                'warning_threshold_ms': self.PORT_HEALTH_WARNING_THRESHOLD,
                'unhealthy_threshold_ms': self.PORT_HEALTH_UNHEALTHY_THRESHOLD,
                'unhealthy_ports': unhealthy_ports,
                'scaling_candidates': scaling_candidates,
                'scaling_range': f"{self.SCALING_PORT_RANGE_START}-{self.SCALING_PORT_RANGE_END}",
                'last_database_error': database_error_info,
                'port_stats': port_health_stats
            }
        }