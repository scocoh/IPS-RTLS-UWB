# Name: tetse_rule_engine.py
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

# File: tetse_rule_engine.py
# Version: 0.2.2 (Phase 5C - Subject Registry Integrated)
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Fully decoupled rule evaluation engine using subject state
# Status: Production-ready for Phase 5C

from datetime import datetime
import logging

from routes.temporal_context import get_house_exclusion_context
from routes.subject_registry import get_subject_current_zone

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def evaluate_house_exclusion_rule(rule: dict) -> dict:
    """
    Evaluate a TETSE rule that checks for house zone exclusion using subject state.

    Args:
        rule (dict): Fully parsed rule with subject_id, zone, duration_sec, and conditions.

    Returns:
        dict: {
            "triggered": bool,
            "status": str,
            "details": dict
        }
    """
    try:
        subject_id = rule.get("subject_id")
        campus_zone_id = int(rule.get("zone"))
        duration_sec = int(rule.get("duration_sec", 600))
        exclusion_minutes = duration_sec // 60
        conditions = rule.get("conditions", {})
        house_parent_zone_id = int(conditions.get("exclude_parent_zone", 0))

        # NEW: Lookup current zone dynamically from subject_registry
        current_zone_id = await get_subject_current_zone(subject_id)
        if current_zone_id is None:
            logger.error(f"Unable to resolve current zone for subject {subject_id}.")
            return {
                "triggered": False,
                "status": "UNKNOWN_SUBJECT",
                "details": {}
            }

        # Directly inject current_zone_id into house exclusion evaluator
        context = await get_house_exclusion_context(
            entity_id=subject_id,
            campus_zone_id=campus_zone_id,
            house_parent_zone_id=house_parent_zone_id,
            exclusion_duration_min=exclusion_minutes,
            # Inject dynamic zone
            current_zone_id=current_zone_id
        )

        if context["status"] == "OUTSIDE":
            triggered = True
        else:
            triggered = False

        logger.debug(f"Rule evaluation complete for subject {subject_id}: triggered={triggered}, context={context}")

        return {
            "triggered": triggered,
            "status": context["status"],
            "details": context
        }

    except Exception as e:
        logger.error(f"Error evaluating rule: {str(e)}")
        return {
            "triggered": False,
            "status": "ERROR",
            "details": {"error": str(e)}
        }
