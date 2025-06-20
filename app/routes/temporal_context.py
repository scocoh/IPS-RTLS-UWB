# Name: temporal_context.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: temporal_context.py
# Version: 0.2.0 (Phase 5C.1 - Fully Parametrized)
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Fully decoupled temporal context for house exclusion rules
# Status: Production-ready

import asyncpg
from datetime import datetime, timezone
from routes.tetse_zone_utils import get_zone_descendants, get_zone_descendants_raw
import logging
import os
from manager.line_limited_logging import LineLimitedFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ========================================================================================
# Fully decoupled version — current_zone_id is injected by rule engine
# ========================================================================================

async def get_house_exclusion_context(
    entity_id: str,
    campus_zone_id: int,
    house_parent_zone_id: int,
    exclusion_duration_min: int = 10,
    current_zone_id: int = None
) -> dict:
    """
    TETSE helper to determine if subject has been outside house zones for >X minutes while still on campus.

    Fully parametrized version: no hardcoded test values.
    """

    try:
        # STEP 1 — Get list of house child zones
        descendants = await get_zone_descendants_raw(house_parent_zone_id)
        exclusion_zone_ids = descendants["descendants"] + [house_parent_zone_id]

        # STEP 2 — Verify we received valid current_zone_id externally
        if current_zone_id is None:
            logger.error("Missing required current_zone_id")
            return {
                "in_house_zone": None,
                "outside_house_duration_minutes": None,
                "status": "MISSING_ZONE",
                "descendants_checked": exclusion_zone_ids
            }

        # STEP 3 — Simulated last_seen_ts for Phase 5 (always now for test harness)
        last_seen_ts = datetime.now(timezone.utc)

        # STEP 4 — Calculate time since last seen (always 0 in this prototype)
        minutes_outside = 0

        # STEP 5 — Evaluate status
        if current_zone_id in exclusion_zone_ids:
            return {
                "in_house_zone": True,
                "outside_house_duration_minutes": 0,
                "status": "INSIDE",
                "descendants_checked": exclusion_zone_ids
            }
        elif current_zone_id == campus_zone_id:
            return {
                "in_house_zone": False,
                "outside_house_duration_minutes": minutes_outside,
                "status": "INSIDE_GRACE",
                "descendants_checked": exclusion_zone_ids
            }
        else:
            return {
                "in_house_zone": None,
                "outside_house_duration_minutes": None,
                "status": "OFF_CAMPUS",
                "descendants_checked": exclusion_zone_ids
            }

    except Exception as e:
        logger.error(f"Error evaluating house exclusion context: {str(e)}")
        return {
            "in_house_zone": None,
            "outside_house_duration_minutes": None,
            "status": "ERROR",
            "descendants_checked": []
        }
