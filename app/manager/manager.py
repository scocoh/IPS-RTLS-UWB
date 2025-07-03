# Name: manager.py
# Version: 0.1.23
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Streamlined Python script for ParcoRTLS backend + Event Engine (TETSE) WebSocket support
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/manager.py
# Version: 0.1.23 - Fully modularized manager with all components extracted, bumped from 0.1.22
# Version: 0.1.22 - Modularized database operations into manager_database.py, bumped from 0.1.21
# Version: 0.1.21 - Added database-driven configuration support, bumped from 0.1.20
# Version: 0.1.20 - Restored region bounds handling in load_triggers, fixed ex to e in process_sim_message, simplified logging to FileHandler, added debug logging for trigger 147 issue

"""
Streamlined Manager Class for ParcoRTLS Backend

This is the main orchestrator class that coordinates all modular components:
- Database operations (ManagerDatabase)
- Heartbeat management (ManagerHeartbeat)  
- Data processing (ManagerData)
- Trigger engine (ManagerTriggers)
- Client management (ManagerClients)

All heavy lifting has been extracted to dedicated modules for better maintainability,
testing, and debugging. This manager now serves as a clean coordinator.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, List
from fastapi import WebSocket

# Core imports
from manager.enums import eMode, eRunState
from manager.models import GISData

# Modular component imports
from manager.manager_database import ManagerDatabase
from manager.manager_heartbeat import ManagerHeartbeat
from manager.manager_data import ManagerData
from manager.manager_triggers import ManagerTriggers
from manager.manager_clients import ManagerClients

# Ensure log directory exists
LOG_DIR = "/home/parcoadmin/parco_fastapi/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# StreamHandler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

# FileHandler for persistent logging
try:
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "manager.log"))
except Exception as e:
    logger.error(f"Failed to create manager.log: {e}, falling back to manager_fallback.log")
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "manager_fallback.log"))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

# Set handlers
logger.handlers = []
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.propagate = False

class Manager:
    """
    Main Manager class that orchestrates all ParcoRTLS backend operations.
    
    This streamlined manager coordinates modular components for:
    - Database operations and configuration
    - Heartbeat management and client health
    - Data processing and averaging
    - Trigger loading and evaluation
    - Client management and event broadcasting
    """
    
    # Static clients for backward compatibility
    clients: Dict[str, List[WebSocket]] = {}

    def __init__(self, name: str, zone_id: int):
        """
        Initialize the manager with all modular components.
        
        Args:
            name: Manager instance name
            zone_id: Zone ID for this manager instance
        """
        # Core attributes
        self.name = name
        self.zone_id = zone_id
        self.zone_id_locked = False
        self.run_state = eRunState.Stopped
        self.start_date = None
        
        # Configuration attributes (loaded from database)
        self.sdk_ip = None
        self.sdk_port = None
        self.is_ave = False
        self.mode = eMode.Subscription
        self.resrc_type = 0
        self.resrc_type_name = ""
        
        # Initialize all modular components
        self.database = ManagerDatabase(name)
        self.heartbeat = ManagerHeartbeat(name)
        self.data = ManagerData(name)
        self.triggers = ManagerTriggers(name)
        self.client_manager = ManagerClients(name)
        
        # Legacy compatibility - expose modular attributes
        self.sdk_clients = self.client_manager.sdk_clients
        self.kill_list = self.client_manager.kill_list
        
        logger.debug(f"Initialized streamlined Manager with name={name}, zone_id={zone_id}")
        file_handler.flush()

    async def start(self) -> bool:
        """
        Start the manager and all its components.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        logger.debug(f"Manager {self.name} starting: Setting run_state to Starting, zone_id={self.zone_id}")
        file_handler.flush()
        
        try:
            self.start_date = datetime.now()
            self.run_state = eRunState.Starting
            
            logger.info("------- Manager Started --------")
            logger.info(f"Manager starting with zone_id: {self.zone_id}")
            file_handler.flush()
            
            # 1. Initialize database and load configuration
            if not await self.database.initialize_connection_strings():
                logger.warning("Database configuration fallback used")
                
            if not await self.database.load_config_from_db(eMode):
                logger.warning("Database configuration defaults used")
                
            # Update manager attributes from database configuration
            config = self.database.get_config_values()
            self.sdk_ip = config['sdk_ip']
            self.sdk_port = config['sdk_port']
            self.is_ave = config['is_ave']
            self.mode = config['mode']
            self.resrc_type = config['resrc_type']
            self.resrc_type_name = config['resrc_type_name']
            
            # 2. Create database pool
            if not await self.database.create_database_pool():
                logger.error("Failed to create database pool")
                file_handler.flush()
                raise Exception("Database pool creation failed")
            
            logger.debug("Database initialization complete")
            file_handler.flush()
            
            # 3. Load triggers for the current zone
            current_zone_id = self.get_current_zone_id()
            if current_zone_id is not None:
                if not await self.triggers.load_triggers(zone_id=current_zone_id):
                    logger.warning(f"Failed to load triggers for zone {current_zone_id}")
                else:
                    logger.debug("Triggers loaded successfully")
            else:
                logger.warning(f"Skipping trigger loading because zone_id is None for manager {self.name}")
            
            file_handler.flush()
            
            # 4. Start heartbeat loop
            if not await self.heartbeat.start_heartbeat_loop(self):
                logger.warning("Failed to start heartbeat loop")
            else:
                logger.debug("Heartbeat loop started")
            
            # 5. Start data monitoring
            asyncio.create_task(self.data.start_monitoring(self))
            logger.debug("Data monitoring started")
            file_handler.flush()
            
            # 6. Set run state to started
            self.run_state = eRunState.Started
            logger.debug(f"Run state set to {self.run_state}")
            file_handler.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"Start Error: {str(e)}")
            file_handler.flush()
            self.run_state = eRunState.Stopped
            return False

    async def shutdown(self) -> bool:
        """
        Shutdown the manager and all its components gracefully.
        
        Returns:
            bool: True if shutdown completed successfully
        """
        logger.info("Manager shutting down...")
        file_handler.flush()
        
        try:
            # Set run state to stopped (this will stop loops)
            self.run_state = eRunState.Stopped
            
            # Stop heartbeat loop
            await self.heartbeat.stop_heartbeat_loop()
            
            # Shutdown all clients
            await self.client_manager.shutdown_all_clients()
            
            # Close database connections
            await self.database.close_connections()
            
            logger.info("Manager shutdown complete")
            file_handler.flush()
            return True
            
        except Exception as e:
            logger.error(f"Error during manager shutdown: {str(e)}")
            file_handler.flush()
            return False

    async def parser_data_arrived(self, sm: dict) -> bool:
        """
        Main entry point for processing incoming data.
        
        Args:
            sm: Raw message dictionary
            
        Returns:
            bool: True if processed successfully
        """
        logger.debug(f"Parser data arrived: {sm}")
        file_handler.flush()
        
        try:
            zone_id = sm.get('zone_id', self.zone_id)
            logger.debug(f"Extracted zone_id from sm: {zone_id}, manager zone_id: {self.zone_id}")
            
            # Process GIS data
            msg = await self.data.process_gis_data(sm, zone_id)
            
            # Load triggers if needed for this zone
            if not any(t.zone_id == zone_id for t in self.triggers.triggers):
                logger.debug(f"No triggers loaded for zone {zone_id}, loading now")
                await self.triggers.load_triggers(zone_id)
                logger.debug(f"Loaded triggers for zone {zone_id} based on GISData message")
            
            # Compute averaging if enabled
            if self.is_ave:
                await self.data.compute_tag_averaging(msg, self.is_ave)
            
            # Store position data (skip for simulation data)
            if msg.type != "Sim POTTER" and self.database.is_database_ready():
                msg_data = {
                    'id': msg.id, 'ts': msg.ts, 'x': msg.x, 'y': msg.y, 
                    'z': msg.z, 'cnf': msg.cnf, 'gwid': msg.gwid, 'bat': msg.bat
                }
                await self.database.store_position_history(msg_data)
            
            # Create tag object and evaluate triggers
            tag = self.data.create_tag_object(msg)
            events = await self.triggers.evaluate_triggers(tag, zone_id, self.database)
            
            # Broadcast trigger events
            for event in events:
                await self.client_manager.broadcast_trigger_event(event, msg.id)
            
            # Broadcast averaged data if available
            if self.is_ave:
                ave_data = await self.data.get_averaged_data(msg.id, zone_id, msg.sequence or 0)
                if ave_data:
                    await self.client_manager.broadcast_averaged_data(msg.id, ave_data)
            
            return True
            
        except Exception as e:
            logger.error(f"ParserDataArrived Error: {str(e)}")
            file_handler.flush()
            return False

    async def process_sim_message(self, sm: dict) -> bool:
        """
        Process simulation message.
        
        Args:
            sm: Simulation message dictionary
            
        Returns:
            bool: True if processed successfully
        """
        logger.debug(f"Processing sim message: {sm}")
        file_handler.flush()
        
        try:
            processed_sm = await self.data.process_sim_message(sm)
            return await self.parser_data_arrived(processed_sm)
            
        except Exception as e:
            logger.error(f"ProcessSimMessage Error: {str(e)}")
            file_handler.flush()
            return False

    def get_current_zone_id(self) -> int:
        """Get the current zone ID."""
        logger.debug(f"Returning current zone_id: {self.zone_id}")
        file_handler.flush()
        return getattr(self, 'zone_id')

    # Client Management Methods (for backward compatibility)
    async def add_client_instance(self, reqid: str, websocket: WebSocket) -> bool:
        """Add WebSocket client (instance method)."""
        return await self.client_manager.add_websocket_client(reqid, websocket)

    async def remove_client_instance(self, reqid: str, websocket: WebSocket) -> bool:
        """Remove WebSocket client (instance method)."""
        return await self.client_manager.remove_websocket_client(reqid, websocket)

    async def broadcast_event_instance(self, entity_id: str, data: dict) -> int:
        """Broadcast event to entity subscribers (instance method)."""
        return await self.client_manager.broadcast_event(entity_id, data)

    # Static Methods (for backward compatibility with existing code)
    @staticmethod
    async def add_client(reqid: str, websocket: WebSocket):
        """Add WebSocket client (static method for backward compatibility)."""
        await ManagerClients.add_client_static(Manager.clients, reqid, websocket)

    @staticmethod
    async def remove_client(reqid: str, websocket: WebSocket):
        """Remove WebSocket client (static method for backward compatibility)."""
        await ManagerClients.remove_client_static(Manager.clients, reqid, websocket)

    @staticmethod
    async def broadcast_event(entity_id: str, data: dict) -> int:
        """Broadcast event (static method for backward compatibility)."""
        return await ManagerClients.broadcast_event_static(Manager.clients, entity_id, data)

    async def load_triggers(self, zone_id: int) -> bool:
        """Load triggers for a zone (delegates to trigger handler)."""
        return await self.triggers.load_triggers(zone_id)

    async def close_client(self, client):
        """Close an SDK client (delegates to heartbeat handler)."""
        await self.heartbeat._close_client(self, client)

    # Component Access Methods
    def get_database_handler(self) -> ManagerDatabase:
        """Get the database handler component."""
        return self.database

    def get_heartbeat_handler(self) -> ManagerHeartbeat:
        """Get the heartbeat handler component."""
        return self.heartbeat

    def get_data_handler(self) -> ManagerData:
        """Get the data handler component."""
        return self.data

    def get_trigger_handler(self) -> ManagerTriggers:
        """Get the trigger handler component."""
        return self.triggers

    def get_client_handler(self) -> ManagerClients:
        """Get the client handler component."""
        return self.client_manager

    # Statistics and Status Methods
    def get_manager_stats(self) -> dict:
        """
        Get comprehensive manager statistics.
        
        Returns:
            dict: Complete manager statistics
        """
        return {
            'manager_info': {
                'name': self.name,
                'zone_id': self.zone_id,
                'run_state': self.run_state.name,
                'is_averaging': self.is_ave,
                'mode': self.mode.name if self.mode else 'Unknown',
                'sdk_ip': self.sdk_ip,
                'sdk_port': self.sdk_port,
                'start_date': self.start_date.isoformat() if self.start_date else None
            },
            'database': {
                'ready': self.database.is_database_ready(),
                'connection_strings': self.database.get_connection_strings()
            },
            'heartbeat': self.heartbeat.get_heartbeat_stats(),
            'data': self.data.get_data_stats(),
            'triggers': self.triggers.get_trigger_stats(),
            'clients': self.client_manager.get_client_stats()
        }

    def is_healthy(self) -> bool:
        """
        Check if the manager and all components are healthy.
        
        Returns:
            bool: True if all components are healthy
        """
        try:
            return (
                self.run_state == eRunState.Started and
                self.database.is_database_ready() and
                self.heartbeat.is_heartbeat_running() and
                self.data.validate_data_integrity() and
                self.triggers.validate_trigger_integrity() and
                self.client_manager.validate_client_integrity()
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def __str__(self) -> str:
        """String representation of the manager."""
        return f"Manager(name={self.name}, zone_id={self.zone_id}, state={self.run_state.name})"

    def __repr__(self) -> str:
        """Detailed representation of the manager."""
        return (f"Manager(name='{self.name}', zone_id={self.zone_id}, "
                f"state={self.run_state.name}, healthy={self.is_healthy()})")

# Legacy compatibility - expose manager components as separate imports
# This allows existing code to continue working while migration happens
__all__ = [
    'Manager',
    'ManagerDatabase', 
    'ManagerHeartbeat',
    'ManagerData',
    'ManagerTriggers', 
    'ManagerClients'
]