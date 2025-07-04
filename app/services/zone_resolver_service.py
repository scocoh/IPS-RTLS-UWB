# Name: zone_resolver_service.py
# Version: 0.1.1
# Created: 250623
# Modified: 250703
# Creator: ParcoAdmin + Claude & AI Assistant
# Description: Zone resolution service for converting coordinates to zones - Updated to use centralized configuration
# Location: /home/parcoadmin/parco_fastapi/app/services/
# Role: Service
# Status: Active
# Dependent: TRUE

import logging
import httpx
from typing import Optional, Dict, Any
import asyncpg
import sys
import os

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

logger = logging.getLogger(__name__)

class ZoneResolverService:
    """
    Service to resolve coordinates to zones for proper data flow.
    This ensures the simulator doesn't need to provide zone_id - it's resolved from position.
    Updated to use centralized configuration instead of hardcoded IP addresses.
    """
    
    def __init__(self, fastapi_base_url: Optional[str] = None):
        # Use centralized configuration for FastAPI base URL
        if fastapi_base_url is None:
            server_host = get_server_host()
            self.fastapi_base_url = f"http://{server_host}:8000"
        else:
            self.fastapi_base_url = fastapi_base_url
            
        # Use centralized configuration for database connection
        db_configs = get_db_configs_sync()
        maint_config = db_configs['maint']
        self.conn_string = f"postgresql://{maint_config['user']}:{maint_config['password']}@{maint_config['host']}:{maint_config['port']}/{maint_config['database']}"
    
    async def resolve_zone_from_coordinates(self, x: float, y: float, z: float, campus_id: int = 422) -> Optional[int]:
        """
        Resolve coordinates to actual zone ID.
        
        Args:
            x, y, z: Tag coordinates
            campus_id: Campus zone ID (default 422 for 6005Campus)
            
        Returns:
            Resolved zone ID or campus_id if no specific zone found
        """
        try:
            # Try to resolve to specific zone using FastAPI endpoint
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(
                    f"{self.fastapi_base_url}/api/zones_by_point",
                    params={"x": x, "y": y, "z": z}
                )
                
                if response.status_code == 200:
                    zones = response.json()
                    if zones:
                        # Return the smallest zone (most specific)
                        specific_zone = min(
                            zones,
                            key=lambda z: (z["n_max_x"] - z["n_min_x"]) * (z["n_max_y"] - z["n_min_y"])
                        )
                        logger.debug(f"Resolved coordinates ({x}, {y}, {z}) to zone {specific_zone['zone_id']}")
                        return specific_zone["zone_id"]
        
        except Exception as e:
            logger.warning(f"Zone resolution failed for ({x}, {y}, {z}): {str(e)}")
        
        # Fallback to campus zone
        logger.debug(f"Using campus fallback zone {campus_id} for coordinates ({x}, {y}, {z})")
        return campus_id
    
    async def get_zone_hierarchy(self, zone_id: int) -> Dict[str, Any]:
        """
        Get zone hierarchy information for TETSE virtual zone logic.
        
        Args:
            zone_id: Zone ID to analyze
            
        Returns:
            Dictionary with zone hierarchy info
        """
        try:
            async with asyncpg.create_pool(self.conn_string) as pool:
                async with pool.acquire() as conn:
                    # Get zone info and parent hierarchy
                    zone_info = await conn.fetchrow("""
                        WITH RECURSIVE zone_hierarchy AS (
                            SELECT i_zn, x_nm_zn, i_typ_zn, i_pnt_zn, 0 as level
                            FROM zones WHERE i_zn = $1
                            UNION ALL
                            SELECT z.i_zn, z.x_nm_zn, z.i_typ_zn, z.i_pnt_zn, zh.level + 1
                            FROM zones z
                            JOIN zone_hierarchy zh ON z.i_zn = zh.i_pnt_zn
                            WHERE zh.level < 10
                        )
                        SELECT 
                            MIN(CASE WHEN i_typ_zn = 1 THEN i_zn END) as campus_id,
                            MIN(CASE WHEN i_typ_zn = 10 THEN i_zn END) as building_envelope_id,
                            MAX(CASE WHEN level = 0 THEN i_zn END) as current_zone_id,
                            MAX(CASE WHEN level = 0 THEN i_typ_zn END) as current_zone_type
                        FROM zone_hierarchy
                    """, zone_id)
                    
                    if zone_info:
                        return {
                            "zone_id": zone_id,
                            "campus_id": zone_info["campus_id"],
                            "building_envelope_id": zone_info["building_envelope_id"],
                            "current_zone_type": zone_info["current_zone_type"],
                            "is_inside_building": zone_info["building_envelope_id"] is not None and 
                                               zone_id != zone_info["campus_id"],
                            "semantic_zone": self._determine_semantic_zone(zone_info)
                        }
        
        except Exception as e:
            logger.error(f"Failed to get zone hierarchy for {zone_id}: {str(e)}")
        
        # Fallback
        return {
            "zone_id": zone_id,
            "campus_id": 422,  # Default campus
            "building_envelope_id": 423,  # Default building
            "current_zone_type": 1,
            "is_inside_building": False,
            "semantic_zone": "outside"
        }
    
    def _determine_semantic_zone(self, zone_info: Dict) -> str:
        """
        Determine semantic zone (inside/outside) from zone hierarchy.
        """
        zone_id = zone_info.get("zone_id")
        campus_id = zone_info.get("campus_id")
        building_envelope_id = zone_info.get("building_envelope_id")
        
        # If we're in the campus but not in building envelope = outside
        if zone_id == campus_id:
            return "outside"
        elif building_envelope_id and zone_id != building_envelope_id:
            # We're in a zone that has a building envelope parent = inside
            return "inside"
        elif zone_id == building_envelope_id:
            # We're exactly at building envelope = inside
            return "inside"
        else:
            # Default to outside for campus-level zones
            return "outside"

# Global instance
zone_resolver = ZoneResolverService()