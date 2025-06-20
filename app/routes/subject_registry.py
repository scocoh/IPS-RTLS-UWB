# Name: subject_registry.py
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

# File: subject_registry.py
# Version: 0.2.0 (Phase 6B.1 Subject Registry)
# Created: 250615
# Modified: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Map subject_id to live tag/device state for TETSE evaluations.
# Status: Prototype (Static)

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ==========================================================================================
# SUBJECT REGISTRY - NOW SUPPORTS REAL-TIME STATE UPDATES
# ==========================================================================================

# Simple in-memory subject-to-zone state
SUBJECT_STATE = {
    "Eddy": {
        "assigned_tag": "23001",
        "current_zone_id": 422  # Initial state at boot
    }
    # Add additional subjects as needed
}

async def get_subject_current_zone(subject_id: str) -> int:
    """
    Returns current_zone_id for given subject_id.
    """
    try:
        subject = SUBJECT_STATE.get(subject_id)
        if not subject:
            logger.warning(f"Subject {subject_id} not found in registry.")
            return None
        return subject["current_zone_id"]
    except Exception as e:
        logger.error(f"Error in subject lookup: {str(e)}")
        return None

async def update_subject_zone(subject_id: str, new_zone_id: int):
    """
    Real-time state update for subject's current_zone_id.
    """
    try:
        if subject_id not in SUBJECT_STATE:
            logger.warning(f"Cannot update unknown subject {subject_id}. Ignoring update.")
            return

        SUBJECT_STATE[subject_id]["current_zone_id"] = new_zone_id
        logger.info(f"Updated subject {subject_id} to zone {new_zone_id}")

    except Exception as e:
        logger.error(f"Error updating subject state: {str(e)}")