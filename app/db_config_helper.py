# Name: db_config_helper.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Database configuration helper for ParcoRTLS - reads server config from tlkresources table
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Configuration Helper
# Status: Active
# Dependent: TRUE

import asyncpg
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Fallback configuration for when database is not available
FALLBACK_CONFIG = {
    'host': '192.168.210.226',
    'db_port': 5432,
    'db_user': 'parcoadmin',
    'db_password': 'parcoMCSE04106!',
    'mqtt_broker': '127.0.0.1'
}

class DatabaseConfigHelper:
    """Helper class to read server configuration from tlkresources table"""
    
    def __init__(self):
        self._cached_config = None
        self._conn_string = None
    
    def get_fallback_conn_string(self) -> str:
        """Get fallback database connection string for initial connection"""
        return (f"postgresql://{FALLBACK_CONFIG['db_user']}:"
                f"{FALLBACK_CONFIG['db_password']}@"
                f"{FALLBACK_CONFIG['host']}:"
                f"{FALLBACK_CONFIG['db_port']}/ParcoRTLSMaint")
    
    async def get_server_config(self, manager_name: Optional[str] = None) -> Dict[str, any]: # type: ignore
        """
        Get server configuration from tlkresources table
        
        Args:
            manager_name: Specific manager to get config for (optional)
            
        Returns:
            Dictionary with server configuration
        """
        if self._cached_config:
            return self._cached_config
            
        try:
            conn_string = self.get_fallback_conn_string()
            async with asyncpg.create_pool(conn_string) as pool:
                async with pool.acquire() as conn:
                    if manager_name:
                        # Get specific manager configuration
                        row = await conn.fetchrow(
                            """
                            SELECT r.X_IP, r.I_PRT, r.I_TYP_RES, r.X_NM_RES,
                                   rt.X_DSC_RES
                            FROM tlkresources r
                            JOIN tlkresourcetypes rt ON r.I_TYP_RES = rt.I_TYP_RES
                            WHERE r.X_NM_RES = $1
                            """,
                            manager_name
                        )
                        if row:
                            config = {
                                'host': row['x_ip'],
                                'port': row['i_prt'],
                                'resource_type': row['i_typ_res'],
                                'name': row['x_nm_res'],
                                'description': row['x_dsc_res']
                            }
                        else:
                            logger.warning(f"Manager {manager_name} not found in tlkresources, using fallback")
                            config = FALLBACK_CONFIG.copy()
                    else:
                        # Get all server configurations
                        rows = await conn.fetch(
                            """
                            SELECT r.X_IP, r.I_PRT, r.I_TYP_RES, r.X_NM_RES,
                                   rt.X_DSC_RES
                            FROM tlkresources r
                            JOIN tlkresourcetypes rt ON r.I_TYP_RES = rt.I_TYP_RES
                            ORDER BY r.I_RNK
                            """
                        )
                        
                        # Extract primary server IP (most common IP in table)
                        ips = [row['x_ip'] for row in rows if row['x_ip']]
                        primary_ip = max(set(ips), key=ips.count) if ips else FALLBACK_CONFIG['host']
                        
                        config = {
                            'host': primary_ip,
                            'db_port': FALLBACK_CONFIG['db_port'],
                            'db_user': FALLBACK_CONFIG['db_user'],
                            'db_password': FALLBACK_CONFIG['db_password'],
                            'mqtt_broker': FALLBACK_CONFIG['mqtt_broker'],
                            'managers': {}
                        }
                        
                        # Add manager-specific configurations
                        for row in rows:
                            config['managers'][row['x_nm_res']] = {
                                'ip': row['x_ip'],
                                'port': row['i_prt'],
                                'type': row['i_typ_res'],
                                'description': row['x_dsc_res']
                            }
                    
                    self._cached_config = config
                    logger.info(f"Loaded server configuration from database: primary_ip={config.get('host', 'unknown')}")
                    return config
                    
        except Exception as e:
            logger.error(f"Failed to load configuration from database: {e}")
            logger.info("Using fallback configuration")
            config = FALLBACK_CONFIG.copy()
            if manager_name:
                config['name'] = manager_name
                config['port'] = 8001  # Default manager port
            return config
    
    def get_database_configs(self, host: Optional[str] = None) -> Dict[str, Dict]:
        """
        Get database configuration dictionaries for different databases
        
        Args:
            host: Server IP address (uses fallback if None)
            
        Returns:
            Dictionary of database configurations
        """
        if not host:
            host = FALLBACK_CONFIG['host']
            
        return {
            "maint": {
                "database": "ParcoRTLSMaint",
                "user": FALLBACK_CONFIG['db_user'],
                "password": FALLBACK_CONFIG['db_password'],
                "host": host,
                "port": FALLBACK_CONFIG['db_port']
            },
            "data": {
                "database": "ParcoRTLSData",
                "user": FALLBACK_CONFIG['db_user'],
                "password": FALLBACK_CONFIG['db_password'],
                "host": host,
                "port": FALLBACK_CONFIG['db_port']
            },
            "hist_r": {
                "database": "ParcoRTLSHistR",
                "user": FALLBACK_CONFIG['db_user'],
                "password": FALLBACK_CONFIG['db_password'],
                "host": host,
                "port": FALLBACK_CONFIG['db_port']
            },
            "hist_p": {
                "database": "ParcoRTLSHistP",
                "user": FALLBACK_CONFIG['db_user'],
                "password": FALLBACK_CONFIG['db_password'],
                "host": host,
                "port": FALLBACK_CONFIG['db_port']
            },
            "hist_o": {
                "database": "ParcoRTLSHistO",
                "user": FALLBACK_CONFIG['db_user'],
                "password": FALLBACK_CONFIG['db_password'],
                "host": host,
                "port": FALLBACK_CONFIG['db_port']
            }
        }
    
    def get_connection_string(self, database: str, host: Optional[str] = None) -> str:
        """
        Get connection string for a specific database
        
        Args:
            database: Database name
            host: Server IP address (uses fallback if None)
            
        Returns:
            PostgreSQL connection string
        """
        if not host:
            host = FALLBACK_CONFIG['host']
            
        return (f"postgresql://{FALLBACK_CONFIG['db_user']}:"
                f"{FALLBACK_CONFIG['db_password']}@"
                f"{host}:{FALLBACK_CONFIG['db_port']}/{database}")

# Global instance
config_helper = DatabaseConfigHelper()

def get_connection(db_name: str):
    """Helper to get psycopg2 connection for the given database"""
    cfg = config_helper.get_database_configs().get(db_name.lower())
    if not cfg:
        raise ValueError(f"No database config found for '{db_name}'")
    
    import psycopg2
    return psycopg2.connect(
        dbname=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"]
    )

__all__ = ["get_connection"]
