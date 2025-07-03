# Name: config.py
# Version: 0.1.1
# Created: 971201
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend - Updated to use database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import logging
from typing import Dict, Optional
from db_config_helper import config_helper

logger = logging.getLogger(__name__)

# MQTT broker configuration (remains static as it's typically localhost)
MQTT_BROKER = "127.0.0.1"

# Cache for database configurations
_cached_server_config: Optional[Dict] = None
_cached_db_configs: Optional[Dict] = None

async def get_server_config() -> Dict:
    """Get server configuration from database"""
    global _cached_server_config
    if _cached_server_config is None:
        _cached_server_config = await config_helper.get_server_config()
    return _cached_server_config

def get_server_host() -> str:
    """Get server host IP address synchronously (with fallback)"""
    global _cached_server_config
    if _cached_server_config:
        return _cached_server_config.get('host', '192.168.210.226')
    # Fallback if config not loaded yet
    return '192.168.210.226'

async def get_db_configs_async() -> Dict[str, Dict]:
    """Get database configurations asynchronously from server config"""
    global _cached_db_configs
    if _cached_db_configs is None:
        server_config = await get_server_config()
        host = server_config.get('host', '192.168.210.226')
        _cached_db_configs = config_helper.get_database_configs(host)
    return _cached_db_configs

def get_db_configs_sync() -> Dict[str, Dict]:
    """Get database configurations synchronously (with fallback)"""
    global _cached_db_configs
    if _cached_db_configs:
        return _cached_db_configs
    
    # If not cached, use fallback host
    host = get_server_host()
    _cached_db_configs = config_helper.get_database_configs(host)
    return _cached_db_configs

# Backward compatibility: Provide DB_CONFIGS_ASYNC for existing code
# This will use fallback values initially, then get updated when async config is loaded
DB_CONFIGS_ASYNC = config_helper.get_database_configs()

async def initialize_config():
    """Initialize configuration from database - call this during app startup"""
    global DB_CONFIGS_ASYNC
    try:
        logger.info("Initializing configuration from database...")
        server_config = await get_server_config()
        host = server_config.get('host')
        DB_CONFIGS_ASYNC = config_helper.get_database_configs(host)
        logger.info(f"Configuration initialized successfully with host: {host}")
    except Exception as e:
        logger.warning(f"Failed to initialize config from database, using fallbacks: {e}")

def refresh_config():
    """Clear cached configuration to force reload from database"""
    global _cached_server_config, _cached_db_configs
    _cached_server_config = None
    _cached_db_configs = None
    logger.info("Configuration cache cleared")