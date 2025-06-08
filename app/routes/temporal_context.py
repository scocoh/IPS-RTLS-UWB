# Name: temporal_context.py
# Version: 0.1.2
# Created: 250601
# Modified: 250601
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: TETSE helper to fetch the last N events, determine the current zone, calculate time in zone, and assign symbolic status (indoors/outdoors) based on zone hierarchy
# Location: /home/parcoadmin/parco_fastapi/app/routes/temporal_context.py
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncpg
from datetime import datetime, timezone
import logging
import os
from manager.line_limited_logging import LineLimitedFileHandler

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.temporal_context")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "temporal_context.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Database connection string
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData"

# Zone hierarchy configuration
ZONE_HIERARCHY = {
    "indoors": ["Living Room", "Kitchen", "Bedroom", "Room 204", "Hallway", "Wing", "Building"],
    "outdoors": ["Backyard", "Front Yard", "Yard"]
}

# Mock current time for testing (remove in production)
TEST_CURRENT_TIME = datetime.fromisoformat("2025-06-01T12:04:00+00:00")

async def get_temporal_context(entity_id: str, n_events: int = 5) -> dict:
    """
    Fetches the last N events for an entity, determines current zone, time in zone,
    and assigns symbolic status (indoors/outdoors).

    Args:
        entity_id (str): The ID of the entity (e.g., 'Eddy', 'Tag123').
        n_events (int): Number of recent events to fetch (default: 5).

    Returns:
        dict: Temporal context including last zone, current status, time in zone, and recent events.
    """
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                # Fetch the last N events from event_log
                events = await conn.fetch(
                    """
                    SELECT el.entity_id, el.event_type_id, tet.name AS event_type, el.ts, el.value, el.unit, el.reason_id
                    FROM event_log el
                    JOIN tlk_event_type tet ON el.event_type_id = tet.id
                    WHERE el.entity_id = $1
                    ORDER BY el.ts DESC
                    LIMIT $2
                    """,
                    entity_id, n_events
                )
                
                # Initialize context
                context = {
                    "last_zone": None,
                    "current_status": None,
                    "time_in_zone": None,
                    "recent_events": []
                }

                if not events:
                    logger.warning(f"No events found for entity {entity_id}")
                    return context

                # Process recent events
                for event in events:
                    event_dict = dict(event)
                    # Extract zone from unit if it starts with "zone:"
                    zone = None
                    if event_dict["event_type"] in ["ZoneEntry", "ZoneExit"] and event_dict["unit"] and event_dict["unit"].startswith("zone:"):
                        zone = event_dict["unit"][5:]  # Remove "zone:" prefix
                    
                    event_summary = {
                        "event_type": event_dict["event_type"],
                        "timestamp": event_dict["ts"].isoformat(),
                        "zone": zone,
                        "value": event_dict["value"],
                        "unit": event_dict["unit"]
                    }
                    context["recent_events"].append(event_summary)

                # Determine current zone and time in zone
                latest_event = events[0]
                current_time = TEST_CURRENT_TIME  # Use mocked time for testing
                # current_time = datetime.now(timezone.utc)  # Uncomment in production
                
                if latest_event["event_type"] == "ZoneEntry":
                    zone = latest_event["unit"][5:] if latest_event["unit"] and latest_event["unit"].startswith("zone:") else None
                    context["last_zone"] = zone
                    time_in_zone = current_time - latest_event["ts"]
                    context["time_in_zone"] = f"{int(time_in_zone.total_seconds() // 60)} minutes"
                elif latest_event["event_type"] == "ZoneExit":
                    context["last_zone"] = None  # Entity not in any zone
                    context["time_in_zone"] = "0 minutes"
                else:
                    context["last_zone"] = None
                    context["time_in_zone"] = None

                # Assign symbolic status (indoors/outdoors)
                if context["last_zone"]:
                    for status, zones in ZONE_HIERARCHY.items():
                        if context["last_zone"] in zones:
                            context["current_status"] = status
                            break
                    if not context["current_status"]:
                        context["current_status"] = "unknown"
                        logger.warning(f"Zone {context['last_zone']} not found in ZONE_HIERARCHY")

                logger.debug(f"Temporal context for {entity_id}: {context}")
                return context

    except Exception as e:
        logger.error(f"Error fetching temporal context for {entity_id}: {str(e)}")
        return {
            "last_zone": None,
            "current_status": None,
            "time_in_zone": None,
            "recent_events": [],
            "error": str(e)
        }