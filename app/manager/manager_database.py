# Name: manager_database.py
# Version: 0.1.1
# Created: 250703
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Database handler module for ParcoRTLS Manager - Updated with centralized IP configuration
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Database Handler Module for ParcoRTLS Manager

This module handles all database operations for the Manager class including:
- Connection string initialization using database-driven configuration
- Database pool management
- Configuration loading from database
- Position history storage
- Database queries and updates

Extracted from manager.py v0.1.21 for better modularity and maintainability.
Updated to use centralized IP configuration system.
"""

import asyncpg
import sys
import os
import logging
from typing import Optional

# Add path for centralized configuration and db_config_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync
from db_config_helper import config_helper  # type: ignore

logger = logging.getLogger(__name__)

class ManagerDatabase:
    """
    Handles all database operations for the Manager class.
    
    This class encapsulates database connection management, configuration loading,
    and data storage operations that were previously part of the main Manager class.
    """
    
    def __init__(self, manager_name: str):
        """
        Initialize the database handler.
        
        Args:
            manager_name: Name of the manager instance for configuration lookup
        """
        self.manager_name = manager_name
        self.conn_string: Optional[str] = None
        self.hist_conn_string: Optional[str] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Configuration attributes that will be loaded from database
        self.sdk_ip: Optional[str] = None
        self.sdk_port: Optional[int] = None
        self.is_ave: bool = False
        self.mode = None  # Will be set from eMode enum
        self.resrc_type: int = 0
        self.resrc_type_name: str = ""
        
        logger.debug(f"Initialized ManagerDatabase for manager: {manager_name}")

    async def initialize_connection_strings(self) -> bool:
        """
        Initialize database connection strings using database-driven configuration.
        
        Returns:
            bool: True if successful, False if fallback was used
        """
        if self.conn_string is None or self.hist_conn_string is None:
            try:
                server_config = await config_helper.get_server_config()
                host = server_config.get('host', get_server_host())
                self.conn_string = config_helper.get_connection_string("ParcoRTLSMaint", host)
                self.hist_conn_string = config_helper.get_connection_string("ParcoRTLSHistR", host)
                logger.info(f"Connection strings configured for host: {host}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load connection strings from database, using fallback: {e}")
                # Fallback to centralized configuration
                server_host = get_server_host()
                db_configs = get_db_configs_sync()
                maint_config = db_configs['maint']
                hist_config = db_configs['hist']
                self.conn_string = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"
                self.hist_conn_string = f"postgresql://{hist_config['user']}:{hist_config['password']}@{server_host}:{hist_config['port']}/{hist_config['database']}"
                return False
        return True

    async def create_database_pool(self) -> bool:
        """
        Create the database connection pool using the historical database connection string.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure connection strings are initialized
            await self.initialize_connection_strings()
            
            if not self.hist_conn_string:
                logger.error("Historical connection string not available for pool creation")
                return False
                
            self.db_pool = await asyncpg.create_pool(self.hist_conn_string)
            logger.debug("Database pool created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database pool: {str(e)}")
            return False

    async def load_config_from_db(self, emode_enum) -> bool:
        """
        Load manager configuration from database.
        
        Args:
            emode_enum: The eMode enum class for setting mode
            
        Returns:
            bool: True if configuration was loaded successfully, False if defaults used
        """
        logger.debug(f"Loading config for manager {self.manager_name} from DB")
        
        try:
            # Ensure connection strings are initialized
            await self.initialize_connection_strings()
            
            if not self.conn_string:
                logger.error("Main connection string not available for config loading")
                return False
            
            async with asyncpg.create_pool(self.conn_string) as pool:
                async with pool.acquire() as conn:
                    row = await conn.fetchrow(
                        """
                        SELECT r.X_IP, r.I_PRT, r.F_AVG, r.F_FS, r.I_TYP_RES, rt.X_DSC_RES
                        FROM tlkresources r
                        JOIN tlkresourcetypes rt ON r.I_TYP_RES = rt.I_TYP_RES
                        WHERE r.X_NM_RES = $1
                        """,
                        self.manager_name
                    )
                    if row:
                        self.sdk_ip = row['x_ip']
                        self.sdk_port = row['i_prt']
                        self.is_ave = row['f_avg'] if row['f_avg'] is not None else False
                        self.mode = emode_enum.Stream if row['f_fs'] else emode_enum.Subscription
                        self.resrc_type = row['i_typ_res']
                        self.resrc_type_name = row['x_dsc_res']
                        logger.debug(f"Config loaded: mode={self.mode}, ip={self.sdk_ip}, port={self.sdk_port}")
                        return True
                    else:
                        # Use defaults
                        self.sdk_ip = "127.0.0.0"
                        self.sdk_port = 5000
                        self.mode = emode_enum.Subscription
                        logger.debug("No config found, using defaults")
                        return False
        except Exception as e:
            logger.error(f"Failed to load config from database: {str(e)}")
            # Set defaults on error
            self.sdk_ip = "127.0.0.0"
            self.sdk_port = 5000
            self.mode = emode_enum.Subscription if emode_enum else None
            return False

    async def store_position_history(self, msg_data: dict) -> bool:
        """
        Store position data in the position history table.
        
        Args:
            msg_data: Dictionary containing message data with keys:
                     id, ts, x, y, z, cnf, gwid, bat
                     
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_pool:
            logger.error("Database pool not available for position history storage")
            return False
            
        try:
            async with self.db_pool.acquire() as conn:  # type: ignore
                await conn.execute(
                    """
                    INSERT INTO positionhistory (X_ID_DEV, D_POS_BGN, N_X, N_Y, N_Z, CNF, GWID, BAT)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    msg_data['id'], 
                    msg_data['ts'], 
                    msg_data['x'], 
                    msg_data['y'], 
                    msg_data['z'], 
                    msg_data['cnf'], 
                    msg_data['gwid'], 
                    str(msg_data['bat'])
                )
                logger.debug(f"Stored position data for tag ID:{msg_data['id']} in positionhistory")
                return True
        except Exception as e:
            logger.error(f"Failed to store position history: {str(e)}")
            return False

    async def update_trigger_zone(self, trigger_id: int, new_zone_id: int) -> bool:
        """
        Update the zone for a portable trigger.
        
        Args:
            trigger_id: ID of the trigger to update
            new_zone_id: New zone ID to assign
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_pool:
            logger.error("Database pool not available for trigger zone update")
            return False
            
        try:
            async with self.db_pool.acquire() as conn:  # type: ignore
                await conn.execute(
                    "UPDATE triggers SET i_zn = $1 WHERE i_trg = $2",
                    new_zone_id, trigger_id
                )
                logger.debug(f"Updated trigger {trigger_id} to zone {new_zone_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update trigger zone: {str(e)}")
            return False

    async def close_connections(self) -> None:
        """
        Close all database connections and pools.
        """
        try:
            if self.db_pool:
                await self.db_pool.close()
                self.db_pool = None
                logger.debug("Database pool closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

    def get_connection_strings(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get the current connection strings.
        
        Returns:
            tuple: (main_connection_string, historical_connection_string)
        """
        return self.conn_string, self.hist_conn_string

    def is_database_ready(self) -> bool:
        """
        Check if database is ready for operations.
        
        Returns:
            bool: True if database pool is available, False otherwise
        """
        return self.db_pool is not None

    def get_config_values(self) -> dict:
        """
        Get all loaded configuration values.
        
        Returns:
            dict: Configuration values loaded from database
        """
        return {
            'sdk_ip': self.sdk_ip,
            'sdk_port': self.sdk_port,
            'is_ave': self.is_ave,
            'mode': self.mode,
            'resrc_type': self.resrc_type,
            'resrc_type_name': self.resrc_type_name
        }