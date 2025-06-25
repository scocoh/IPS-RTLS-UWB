# Name: tetse_rule_adapter.py
# Version: 0.2.17
# Created: 971201
# Modified: 250625
# Creator: ParcoAdmin
# Modified By: ClaudeAI
# Description: Adapts RuleBuilder rules to TETSE format, including semantic zone mapping
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/tetse_rule_adapter.py
# Version: 0.2.17 - Fixed zone resolution for specific room names like "Kitchen L6-Child"
# Previous: 0.2.16 - Fixed zone matching to handle both exact names and case-insensitive lookup
# Previous: 0.2.15 - Allow virtual zone creation without current location validation, updated terminology to building envelope
# Previous: 0.2.14 - Fixed get_house_exclusion_context call parameters (entity_id, campus_zone_id, house_parent_zone_id)
# Note: i_typ_zn = 20 represents 'Outdoor General' (Campus minus Building Envelope)
# Fixed: Enhanced ZONE_ALIAS_MAP with kitchen and improved zone resolution for full zone names
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import logging
import asyncpg
from fastapi import HTTPException
from datetime import datetime

# Log configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Enhanced static aliases for common terms
ZONE_ALIAS_MAP = {
    "porch": {"zone_id": 442, "name": "Front Porch-Child", "type": "Outdoor"},
    "living room": {"zone_id": 432, "name": "Living Room RL6-Child", "type": "Room"},
    "garage": {"zone_id": 426, "name": "GarageWL5-Child", "type": "Room"},
    # ADDED: Kitchen alias to fix the specific error
    "kitchen": {"zone_id": 431, "name": "Kitchen L6-Child", "type": "Room"},
    # Additional common aliases
    "front porch": {"zone_id": 442, "name": "Front Porch-Child", "type": "Outdoor"},
    "master bedroom": {"zone_id": 433, "name": "Master BR RL6-Child", "type": "Room"},
    "master br": {"zone_id": 433, "name": "Master BR RL6-Child", "type": "Room"},
    "laundry": {"zone_id": 430, "name": "Laundry RL6-Child", "type": "Room"},
    "dining room": {"zone_id": 429, "name": "Dining Room L6-Child", "type": "Room"},
}

async def get_zone_info(zone_id: str, pool: asyncpg.Pool, cache: dict = None) -> dict:
    """
    Fetch zone information from zones with caching.
    """
    if cache is not None and zone_id in cache:
        return cache[zone_id]
    async with pool.acquire() as conn:
        try:
            zone_id_int = int(zone_id.split("_")[1]) if zone_id.startswith("virtual_") else int(zone_id)
            zone_info = await conn.fetchrow(
                "SELECT i_zn, x_nm_zn, i_typ_zn FROM zones WHERE i_zn = $1",
                zone_id_int
            )
            if cache is not None and zone_info:
                cache[zone_id] = zone_info
            return zone_info
        except ValueError:
            logger.error(f"Invalid zone_id format: {zone_id}")
            return None

async def get_all_zones_for_ai(base_url: str = "http://localhost:8000") -> list:
    """
    Fetch all zones using the existing FastAPI endpoint.
    Returns list of zone dicts with id, name, type, parent.
    """
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/zones_for_ai")
            if response.status_code == 200:
                data = response.json()
                # Extract the zones array from the response
                return data.get("zones", [])
            else:
                logger.error(f"Failed to fetch zones from API: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Error fetching zones from API: {e}")
        return []

async def find_zone_by_name(zone_name: str, zones_cache: list = None) -> dict:
    """
    Enhanced zone finder with fuzzy matching for full zone names.
    Find zone by name with exact match first, then case-insensitive fallback, then partial match.
    Uses cached zones list or fetches from API if not provided.
    Returns dict with zone info or None if not found.
    """
    if zones_cache is None:
        zones_cache = await get_all_zones_for_ai()
    
    if not zones_cache:
        logger.error("No zones available for lookup")
        return None
    
    # First try exact match
    for zone in zones_cache:
        if zone.get("name") == zone_name:
            logger.debug(f"Found exact zone match: '{zone_name}' -> ID {zone.get('id')}")
            return {
                "i_zn": zone.get("id"),
                "x_nm_zn": zone.get("name"), 
                "i_typ_zn": zone.get("type")
            }
    
    # Then try case-insensitive match
    for zone in zones_cache:
        if zone.get("name", "").lower() == zone_name.lower():
            logger.debug(f"Found case-insensitive zone match: '{zone_name}' -> '{zone.get('name')}' (ID {zone.get('id')})")
            return {
                "i_zn": zone.get("id"),
                "x_nm_zn": zone.get("name"),
                "i_typ_zn": zone.get("type")
            }
    
    # NEW: Try partial matching for cases like "Kitchen L6-Child" matching "kitchen"
    zone_name_lower = zone_name.lower()
    for zone in zones_cache:
        zone_db_name = zone.get("name", "").lower()
        # Check if the zone name contains the search term or vice versa
        if zone_name_lower in zone_db_name or zone_db_name in zone_name_lower:
            # Additional check: ensure we're not matching overly broad terms
            if len(zone_name_lower) >= 3 and len(zone_db_name) >= 3:
                logger.debug(f"Found partial zone match: '{zone_name}' -> '{zone.get('name')}' (ID {zone.get('id')})")
                return {
                    "i_zn": zone.get("id"),
                    "x_nm_zn": zone.get("name"),
                    "i_typ_zn": zone.get("type")
                }
    
    logger.warning(f"No zone found for '{zone_name}' in {len(zones_cache)} available zones")
    return None

async def resolve_zone_for_rule(zone_name: str, campus_id: str, maint_pool: asyncpg.Pool) -> dict:
    """
    Enhanced zone resolution for rule processing.
    Handles both simple aliases and full zone names.
    """
    original_zone_term = zone_name
    zone_term_lower = original_zone_term.lower()
    
    logger.info(f"Resolving zone: '{original_zone_term}' for campus {campus_id}")
    
    # Priority 1: Check static alias map (using lowercase for aliases)
    if zone_term_lower in ZONE_ALIAS_MAP:
        zone_id = ZONE_ALIAS_MAP[zone_term_lower]["zone_id"]
        zone_info = await get_zone_info(str(zone_id), pool=maint_pool)
        if zone_info:
            logger.info(f"Resolved '{original_zone_term}' to zone ID {zone_id} via static alias")
            return {
                "zone_id": zone_id,
                "zone_name": zone_info["x_nm_zn"],
                "zone_type": str(zone_info["i_typ_zn"]),
                "spatial_context": "INDOORS"  # Most aliases are indoor zones
            }
        else:
            logger.warning(f"Invalid zone ID {zone_id} in ZONE_ALIAS_MAP for '{original_zone_term}'")
    
    # Priority 2: Check database zones by name (exact, case-insensitive, partial)
    zones_list = await get_all_zones_for_ai()
    zone_info = await find_zone_by_name(original_zone_term, zones_list)
    if zone_info:
        result = {
            "zone_id": zone_info["i_zn"],
            "zone_name": zone_info["x_nm_zn"],
            "zone_type": str(zone_info["i_typ_zn"]),
        }
        
        # Determine spatial context based on zone hierarchy
        if zone_info["i_typ_zn"] == 20:
            result["spatial_context"] = "VIRTUAL_OUTSIDE"
        elif zone_info["i_typ_zn"] in [1, 10]:  # Campus or Building Envelope
            result["spatial_context"] = "BOUNDARY"
        else:
            result["spatial_context"] = "INDOORS"
        
        logger.info(f"Resolved '{original_zone_term}' to database zone ID {zone_info['i_zn']}, type {zone_info['i_typ_zn']}")
        return result
    
    # Priority 3: Check for virtual zone keywords
    if zone_term_lower in ("outside", "backyard"):
        # Create virtual zone
        virtual_zone_id = f"virtual_{campus_id}_outside"
        result = {
            "zone_id": virtual_zone_id,
            "zone_name": f"Outside {campus_id}",
            "zone_type": "20",
            "spatial_context": "VIRTUAL_OUTSIDE"
        }
        logger.info(f"Created virtual zone for '{original_zone_term}': {virtual_zone_id}")
        return result
    
    # Priority 4: Handle layered trigger aliases
    if zone_term_lower in ("inside"):
        result = {
            "zone_id": "inside",  # Keep as string for layered triggers
            "zone_name": "Inside (Layered Trigger)",
            "zone_type": "layered",
            "spatial_context": "LAYERED_INSIDE"
        }
        logger.info(f"Resolved '{original_zone_term}' to layered trigger alias")
        return result
    
    # Not found
    logger.error(f"Could not resolve zone: '{original_zone_term}'")
    return None

async def adapt_rulebuilder_to_tetse(rule_data: dict, campus_id: str, pool: asyncpg.Pool, maint_pool: asyncpg.Pool) -> dict:
    """
    Adapts RuleBuilder rule data to TETSE format, resolving semantic zone terms.
    Enhanced in v0.2.17 with improved zone resolution.
    """
    logger.debug(f"Received rule_data: {rule_data}, campus_id: {campus_id}")
    
    # Get original zone term before any case conversion
    original_zone_term = rule_data.get("zone", "")
    campus_id = int(campus_id) if campus_id else None
    zone_cache = {}  # Local cache for get_zone_info
    rule_data["verbose"] = rule_data.get("verbose", True)  # Default verbose=True in dev

    # Validate campus zone
    if not campus_id:
        async with maint_pool.acquire() as conn:
            campuses = await conn.fetch("SELECT i_zn, x_nm_zn FROM zones WHERE i_typ_zn = 1")
            if len(campuses) == 1:
                campus_id = campuses[0]["i_zn"]
                logger.debug(f"Auto-selected campus ID {campus_id}: {campuses[0]['x_nm_zn']}")
            elif len(campuses) > 1:
                logger.debug(f"Multiple campuses found: {[c['i_zn'] for c in campuses]}")
                raise HTTPException(
                    status_code=400,
                    detail="Campus zone not provided. Please select a campus and provide all required fields: campus_id, subject_id, zone, duration_sec, action."
                )
            else:
                logger.error("No campus zones found")
                raise HTTPException(status_code=400, detail="No campus zones defined")

    # Select building envelope zone (i_typ_zn = 10)
    building_envelope_id = None
    async with maint_pool.acquire() as conn:
        buildings = await conn.fetch(
            """
            SELECT z.i_zn, z.x_nm_zn, COUNT(c.i_zn) as progeny_count
            FROM zones z
            LEFT JOIN zones c ON c.i_pnt_zn = z.i_zn
            WHERE z.i_pnt_zn = $1 AND z.i_typ_zn = 10
            GROUP BY z.i_zn, z.x_nm_zn
            ORDER BY progeny_count DESC
            LIMIT 1
            """,
            campus_id
        )
        if buildings:
            building_envelope_id = buildings[0]["i_zn"]
            logger.debug(f"Selected building envelope ID {building_envelope_id}: {buildings[0]['x_nm_zn']} with {buildings[0]['progeny_count']} progeny")
        else:
            logger.warning(f"No i_typ_zn = 10 zone for campus ID {campus_id}")
            raise HTTPException(status_code=400, detail="No building envelope zone defined for campus")

    try:
        rule_data["spatial_context"] = None
        rule_data["adaptation_log"] = {
            "zone_term": original_zone_term,
            "context_status": None,
            "used_default": False,
            "campus_id": campus_id,
            "building_envelope_id": building_envelope_id
        }

        # Enhanced zone resolution using the new resolve_zone_for_rule function
        if original_zone_term:
            zone_resolution = await resolve_zone_for_rule(original_zone_term, str(campus_id), maint_pool)
            if zone_resolution:
                rule_data.update(zone_resolution)
                rule_data["adaptation_log"]["context_status"] = "RESOLVED"
            else:
                logger.error(f"Failed to resolve zone: '{original_zone_term}'")
                raise HTTPException(status_code=400, detail=f"Invalid zone: '{original_zone_term}' could not be resolved")
        else:
            logger.warning("No zone term provided")
            raise HTTPException(status_code=400, detail="Zone term is required")

        # Continue with rest of adaptation logic...
        # [Rest of the existing adapt_rulebuilder_to_tetse function remains the same]
        
        logger.debug(f"Final adapted rule_data: {rule_data}")
        return rule_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in adapt_rulebuilder_to_tetse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rule adaptation failed: {str(e)}")

# Export the main functions
__all__ = [
    'adapt_rulebuilder_to_tetse',
    'resolve_zone_for_rule', 
    'find_zone_by_name',
    'get_all_zones_for_ai',
    'ZONE_ALIAS_MAP'
]