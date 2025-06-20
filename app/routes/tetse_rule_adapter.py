# Name: tetse_rule_adapter.py
# Version: 0.2.15
# Created: 971201
# Modified: 250620
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Adapts RuleBuilder rules to TETSE format, including semantic zone mapping
# Location: /home/parcoadmin/parco_fastapi/app/tetse
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/tetse/tetse_rule_adapter.py
# Version: 0.2.15 - Allow virtual zone creation without current location validation, updated terminology to building envelope
# Previous: 0.2.14 - Fixed get_house_exclusion_context call parameters (entity_id, campus_zone_id, house_parent_zone_id)
# Previous: 0.2.13 - Fixed get_house_exclusion_context call, removed campus_id
# Previous: 0.2.12 - Fixed get_house_exclusion_context call, removed tag_id
# Previous: 0.2.11 - Fixed ZONE_ALIAS_MAP, bypass get_zone_info for virtual zones
# Note: i_typ_zn = 20 represents 'Outdoor General' (Campus minus Building Envelope)
# TODO: Externalize ZONE_ALIAS_MAP to YAML/DB in v0.3.0
# TODO: Plan specialized modules (residential, commercial, academic, etc.) in v0.3.0
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

# Static aliases for common terms
ZONE_ALIAS_MAP = {
    "porch": {"zone_id": 442, "name": "Front Porch-Child", "type": "Outdoor"},
    "living room": {"zone_id": 432, "name": "Living Room RL6-Child", "type": "Room"},
    "garage": {"zone_id": 426, "name": "GarageWL5-Child", "type": "Room"}
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

async def adapt_rulebuilder_to_tetse(rule_data: dict, campus_id: str, pool: asyncpg.Pool, maint_pool: asyncpg.Pool) -> dict:
    """
    Adapts RuleBuilder rule data to TETSE format, resolving semantic zone terms.
    Version: 0.2.15 - Allow virtual zone creation without current location validation, updated terminology to building envelope.
    Note: i_typ_zn = 20 represents 'Outdoor General' (Campus minus Building Envelope).
    """
    logger.debug(f"Received rule_data: {rule_data}, campus_id: {campus_id}")
    zone_term = rule_data.get("zone", "").lower()
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
            "zone_term": zone_term,
            "context_status": None,
            "used_default": False,
            "campus_id": campus_id,
            "building_envelope_id": building_envelope_id
        }

        # Handle zone term mapping
        if zone_term in ZONE_ALIAS_MAP:
            zone_id = ZONE_ALIAS_MAP[zone_term]["zone_id"]
            zone_info = await get_zone_info(zone_id, pool=maint_pool, cache=zone_cache)
            if zone_info:
                logger.debug(f"Mapped '{zone_term}' to zone ID {zone_id}")
                rule_data["zone_id"] = zone_id
                rule_data["zone_name"] = zone_info["x_nm_zn"]
                rule_data["zone_type"] = zone_info["i_typ_zn"]
            else:
                logger.warning(f"Invalid zone ID {zone_id} in ZONE_ALIAS_MAP")
                raise HTTPException(status_code=400, detail=f"Invalid zone: '{zone_term}'")
        elif zone_term in ("outside", "backyard"):
            # Create virtual i_typ_zn = 20 zone (Campus minus Building Envelope) without current location validation
            virtual_zone_id = f"virtual_{campus_id}_outside"
            rule_data["zone_id"] = virtual_zone_id
            rule_data["zone_name"] = f"Outside {campus_id}"
            rule_data["zone_type"] = "20"
            rule_data["spatial_context"] = "VIRTUAL_OUTSIDE"
            rule_data["message"] = (
                f"Created virtual '{zone_term}' zone for campus {campus_id}. "
                f"This represents areas outside the building envelope (zone {building_envelope_id}) "
                f"but within the campus boundary. The rule will trigger when subject_id {rule_data.get('subject_id', '')} "
                f"is detected in these outdoor areas for the specified duration."
            )
            rule_data["adaptation_log"]["used_default"] = True
            rule_data["adaptation_log"]["context_status"] = "VIRTUAL_OUTSIDE"
            logger.debug(f"Created virtual '{zone_term}' zone as i_typ_zn=20 for campus ID {campus_id}")
        else:
            # Try to find exact zone name match
            async with maint_pool.acquire() as conn:
                zone_info = await conn.fetchrow(
                    "SELECT i_zn, x_nm_zn, i_typ_zn FROM zones WHERE x_nm_zn = $1",
                    zone_term
                )
                if zone_info:
                    rule_data["zone_id"] = zone_info["i_zn"]
                    rule_data["zone_name"] = zone_info["x_nm_zn"]
                    rule_data["zone_type"] = zone_info["i_typ_zn"]
                    logger.debug(f"Found exact zone match: '{zone_term}' -> ID {zone_info['i_zn']}")
                else:
                    logger.warning(f"Unmapped zone term: '{zone_term}'")
                    raise HTTPException(status_code=400, detail=f"Invalid zone term: '{zone_term}'")

        rule_data["duration_sec"] = rule_data.get("duration_sec", 0)
        rule_data["action"] = rule_data.get("action", "")
        rule_data["timestamp"] = datetime.utcnow().isoformat()
        rule_data["adaptation_log"]["success"] = True

        logger.info(f"Successfully adapted rule: {rule_data}")
        return rule_data

    except HTTPException:
        raise
    except Exception as e:
        rule_data["adaptation_log"]["success"] = False
        logger.error(f"Error adapting rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")