# Name: tetse_rule_parser.py
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

# File: tetse_rule_parser.py
# Version: 0.2.3
# Created: 250616
# Modified: 250617
# Author: ParcoAdmin + AI Assistant
# Purpose: Parse enriched rule JSON, map zone names to IDs using cached zone map
# Update: Skipped empty conditions, allowed int zone IDs; bumped from 0.2.2

import logging
import json
from pydantic import BaseModel, ValidationError
from .tetse_zone_map import get_zone_hierarchy

logger = logging.getLogger("TETSE_RULE_PARSER")
logger.setLevel(logging.DEBUG)

class RuleObject(BaseModel):
    id: int
    name: str
    subject_id: str | None = None
    zone: int | None = None
    duration_sec: int
    priority: int
    conditions: dict
    action: str

def parse_tetse_rule(id: int, name: str, conditions: dict) -> dict | None:
    """
    Parse TETSE rule from tlk_rules table.
    Args:
        id: Rule ID
        name: Rule name
        conditions: JSON conditions dict
    Returns:
        Parsed rule dict or None if invalid
    """
    logger.debug(f"Parsing TETSE rule id={id}, name={name}, conditions={conditions}")
    try:
        # Skip empty conditions
        if not conditions:
            logger.warning(f"Skipping rule id={id} with empty conditions")
            return None

        rule_data = {
            "subject_id": conditions.get("subject_id"),
            "zone": conditions.get("zone"),
            "duration_sec": conditions.get("duration_sec", 600),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Validate with Pydantic
        try:
            rule = RuleObject(id=id, name=name, **rule_data)
        except ValidationError as e:
            logger.error(f"Validation failed for rule id={id}: {str(e)}")
            return None

        # Resolve zone name to ID if necessary
        zone_id = resolve_zone_id(rule.zone)
        if zone_id is None:
            logger.error(f"Zone '{rule.zone}' not found in zone hierarchy for rule id={id}")
            return None
        rule_data["zone"] = zone_id

        # Resolve exclude_parent_zone if present
        if "exclude_parent_zone" in rule.conditions:
            exclude_zone_input = rule.conditions["exclude_parent_zone"]
            exclude_zone_id = resolve_zone_id(exclude_zone_input)
            if exclude_zone_id is None:
                logger.error(f"Exclude zone '{exclude_zone_input}' not found for rule id={id}")
                return None
            rule_data["conditions"]["exclude_parent_zone"] = exclude_zone_id

        parsed = rule.model_dump()
        logger.debug(f"Parsed rule object: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"Failed parsing rule id={id}: {str(e)}")
        return None

def parse_rule(raw_rule):
    """
    Parse and normalize rule JSON (already enriched by GPT).
    Returns: parsed rule dict or raises ValueError.
    """
    try:
        rule_data = raw_rule.get("rule") or raw_rule
        logger.debug(f"Raw incoming rule_data: {rule_data}")

        subject_id = rule_data.get("subject_id") or rule_data.get("entity_id")
        zone_input = rule_data.get("zone")
        duration_sec = rule_data.get("duration_sec")
        priority = rule_data.get("priority", 1)
        conditions = rule_data.get("conditions", {})
        action = rule_data.get("action", "alert")

        if not subject_id or not zone_input or not duration_sec:
            raise ValueError("Missing required fields in rule.")

        zone_id = resolve_zone_id(zone_input)
        if zone_id is None:
            raise ValueError(f"Zone '{zone_input}' not found in zone hierarchy.")

        if "exclude_parent_zone" in conditions:
            exclude_zone_input = conditions["exclude_parent_zone"]
            exclude_zone_id = resolve_zone_id(exclude_zone_input)
            if exclude_zone_id is None:
                raise ValueError(f"Exclude zone '{exclude_zone_input}' not found.")
            conditions["exclude_parent_zone"] = exclude_zone_id

        parsed = {
            "subject_id": subject_id,
            "zone": zone_id,
            "duration_sec": int(duration_sec),
            "conditions": conditions,
            "priority": int(priority),
            "action": action
        }
        logger.debug(f"Parsed rule: {parsed}")
        return parsed

    except Exception as e:
        logger.error(f"Failed to parse rule: {e}")
        raise

def resolve_zone_id(input_val):
    """
    Resolve zone identifier: accepts int ID or str name.
    """
    if input_val is None:
        return None
    zone_map = get_zone_hierarchy()
    logger.debug(f"Zone map for input {input_val}: {zone_map}")

    # Accept integer ID directly
    try:
        val_int = int(input_val)
        if val_int in zone_map or not zone_map:  # Allow ID if map is empty
            return val_int
        logger.debug(f"Zone ID {val_int} not found in zone map")
    except (ValueError, TypeError):
        pass

    # Resolve by name (case insensitive)
    name_lookup = {zinfo["name"].lower(): zid for zid, zinfo in zone_map.items()}
    zone_id = name_lookup.get(str(input_val).lower())
    if zone_id is None:
        logger.debug(f"Zone name '{input_val}' not found in name lookup")
    return zone_id
