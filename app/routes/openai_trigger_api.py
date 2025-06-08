# Name: openai_trigger_api.py
# Version: 0.1.3
# Created: 250531
# Modified: 250601
# Creator: ParcoAdmin
# Role: Backend API Route
# Status: Active
# Description: FastAPI route that receives trigger input, evaluates rules from tlk_rules, and asks OpenAI to explain it using llm_bridge
# Location: /app/routes/openai_trigger_api.py
# Dependent: Requires llm_bridge.py, temporal_context.py, mqtt_actions.py

import os
import logging
import asyncpg
import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from routes.llm_bridge import ask_openai
from routes.temporal_context import get_temporal_context
from routes.mqtt_actions import MQTTClient
from manager.line_limited_logging import LineLimitedFileHandler

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.openai_trigger_api")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "openai_trigger_api.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

router = APIRouter()

# Database connection string
MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData"

class TriggerInput(BaseModel):
    entity: str
    trigger: str
    zone: str
    timestamp: str
    duration_sec: int
    prior_state: str
    sequence_id: int

async def construct_prompt(data: TriggerInput) -> str:
    """
    Constructs a detailed prompt for OpenAI, including temporal context, zone hierarchy,
    and event time differences for intelligent reasoning.

    Args:
        data (TriggerInput): The trigger event data.

    Returns:
        str: The enhanced prompt for OpenAI.
    """
    # Fetch temporal context for the entity
    try:
        temporal_context = await get_temporal_context(data.entity, n_events=5)
    except Exception as e:
        logger.error(f"Failed to fetch temporal context for {data.entity}: {str(e)}")
        temporal_context = {
            "last_zone": None,
            "current_status": None,
            "time_in_zone": None,
            "recent_events": []
        }
    
    # Parse timestamp
    try:
        event_time = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
        event_time_str = event_time.strftime("%I:%M %p")
    except ValueError as e:
        logger.warning(f"Invalid timestamp {data.timestamp}: {str(e)}")
        event_time = datetime.now(timezone.utc)
        event_time_str = event_time.strftime("%I:%M %p")
    
    # Build recent timeline
    timeline = []
    for event in temporal_context["recent_events"]:
        try:
            event_ts = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
            time_diff = (event_time - event_ts).total_seconds() / 60  # Minutes
            timeline.append(
                f"- {event['event_type']} in {event['zone'] or 'unknown zone'} at {event_ts.strftime('%I:%M %p')} "
                f"({abs(time_diff):.1f} minutes {'before' if time_diff > 0 else 'after'} the trigger)"
            )
        except Exception as e:
            logger.warning(f"Error processing event {event}: {str(e)}")
    timeline_str = "\n".join(timeline) if timeline else "No recent events found."

    # Determine zone hierarchy and symbolic status
    zone_hierarchy = "unknown"
    if data.zone in ["Living Room", "Kitchen", "Bedroom", "Room 204", "Hallway", "Wing", "Building"]:
        zone_hierarchy = "indoors (room -> wing -> building)"
    elif data.zone in ["Backyard", "Front Yard", "Yard"]:
        zone_hierarchy = "outdoors (yard -> front/back)"
    
    # Construct symbolic summary
    symbolic_summary = (
        f"{data.entity} was last detected in {temporal_context['last_zone'] or 'an unknown zone'} "
        f"({temporal_context['current_status'] or 'unknown status'}) for {temporal_context['time_in_zone'] or 'unknown duration'}. "
        f"The current trigger event '{data.trigger}' occurred in {data.zone} ({zone_hierarchy}) at {event_time_str}."
    )

    # Build the enhanced prompt
    prompt = f"""
A real-time location system (ParcoRTLS) with TETSE (Temporal Entity Trigger State Engine) detected the following event:
- Entity: {data.entity}
- Triggered Event: {data.trigger}
- Zone: {data.zone} ({zone_hierarchy})
- Time: {event_time_str} ({data.timestamp})
- Duration in Zone: {data.duration_sec} seconds
- Previous State: {data.prior_state}
- Sequence ID: {data.sequence_id}

**Symbolic Summary:**
{symbolic_summary}

**Recent Timeline:**
{timeline_str}

**Zone Hierarchy Context:**
- Indoor zones (e.g., Living Room, Kitchen) are part of wing -> building.
- Outdoor zones (e.g., Backyard, Front Yard) are part of yard -> front/back.

**Task:**
Based on the provided temporal context, zone hierarchy, and event timeline:
1. Explain the trigger event in plain English for a user interface.
2. Assess whether it is likely that {data.entity} triggered this event, considering their location and recent movements.
3. If the event suggests an external entity (e.g., an animal detected outdoors while {data.entity} is indoors), describe the likely scenario.
4. Suggest any actions (e.g., trigger MQTT deterrents via Home Assistant) if predefined rules are met, such as an animal detected in the Backyard while {data.entity} is indoors.

Provide a clear, concise, and decision-relevant response to guide the user.
"""
    logger.debug(f"Constructed prompt for sequence_id {data.sequence_id}")
    return prompt

async def evaluate_rules(trigger_data: TriggerInput, temporal_context: dict) -> list:
    """
    Evaluates rules from tlk_rules table against the trigger data and temporal context.

    Args:
        trigger_data (TriggerInput): The trigger event data.
        temporal_context (dict): Temporal context from get_temporal_context.

    Returns:
        list: List of actions to execute based on matching rules.
    """
    actions = []
    try:
        async with asyncpg.create_pool(MAINT_CONN_STRING, min_size=1, max_size=5) as pool:
            async with pool.acquire() as conn:
                rules = await conn.fetch(
                    """
                    SELECT name, conditions, actions
                    FROM tlk_rules
                    WHERE is_enabled = TRUE
                    ORDER BY priority DESC
                    """
                )
                
                for rule in rules:
                    # Parse JSONB fields if they are strings
                    conditions = rule["conditions"]
                    if isinstance(conditions, str):
                        conditions = json.loads(conditions)
                    rule_actions = rule["actions"]
                    if isinstance(rule_actions, str):
                        rule_actions = json.loads(rule_actions)

                    rule_matched = True

                    # Check all conditions
                    if "trigger" in conditions and conditions["trigger"] != trigger_data.trigger:
                        rule_matched = False
                    if "zone" in conditions and conditions["zone"] != trigger_data.zone:
                        rule_matched = False
                    if "entity_status" in conditions and conditions["entity_status"] != temporal_context.get("current_status"):
                        rule_matched = False

                    if rule_matched:
                        logger.info(f"Rule matched: {rule['name']} for sequence_id {trigger_data.sequence_id}")
                        actions.extend(rule_actions)
                    else:
                        logger.debug(f"Rule not matched: {rule['name']} for sequence_id {trigger_data.sequence_id}")

    except Exception as e:
        logger.error(f"Error evaluating rules for sequence_id {trigger_data.sequence_id}: {str(e)}")
    
    return actions

@router.post("/explain_trigger")
async def explain_trigger(request: Request, trigger_data: TriggerInput):
    try:
        prompt = await construct_prompt(trigger_data)
        explanation = await ask_openai(prompt)
        
        if explanation.startswith("❌ OpenAI API error:"):
            logger.error(f"OpenAI API error for sequence_id {trigger_data.sequence_id}: {explanation}")
            raise HTTPException(status_code=500, detail=explanation)
        
        # Fetch temporal context
        temporal_context = await get_temporal_context(trigger_data.entity)
        
        # Evaluate rules and execute actions
        actions = await evaluate_rules(trigger_data, temporal_context)
        mqtt_client = MQTTClient()
        try:
            mqtt_client.connect()
            for action in actions:
                try:
                    if action["action_type"] == "mqtt_publish":
                        params = action["parameters"]
                        mqtt_client.publish(params["topic"], params["payload"])
                        explanation += f"\n[Action Taken: Published to MQTT topic {params['topic']} with payload {params['payload']}]"
                    else:
                        explanation += f"\n[Action Skipped: Unsupported action type {action['action_type']}]"
                except Exception as e:
                    explanation += f"\n[Action Failed: MQTT error for action {action['action_type']} - {str(e)}]"
        except Exception as e:
            explanation += f"\n[Action Failed: MQTT connection error - {str(e)}]"
        finally:
            mqtt_client.disconnect()
        
        logger.info(f"Processed trigger {trigger_data.sequence_id}: {explanation}")
        return {"explanation": explanation}
    
    except Exception as e:
        logger.error(f"Error processing trigger {trigger_data.sequence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")