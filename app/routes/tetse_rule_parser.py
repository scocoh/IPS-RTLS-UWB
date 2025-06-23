# Name: tetse_rule_parser.py
# Version: 0.3.0
# Created: 971201
# Modified: 250621
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Enhanced TETSE rule parser supporting all v0.1.92+ rule types
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/tetse_rule_parser.py
# Version: 0.3.0 - Enhanced to support all v0.1.92+ rule types: zone_stay, zone_transition, layered_trigger, proximity_condition
# Previous: 0.2.3 - Parse enriched rule JSON, map zone names to IDs using cached zone map
# Previous: 0.2.2 - Skipped empty conditions, allowed int zone IDs
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
import json
from pydantic import BaseModel, ValidationError
from .tetse_zone_map import get_zone_hierarchy

logger = logging.getLogger("TETSE_RULE_PARSER")
logger.setLevel(logging.DEBUG)

# Enhanced Pydantic models for all rule types
class LegacyRuleObject(BaseModel):
    """Legacy rule object for backward compatibility"""
    id: int
    name: str
    subject_id: str | None = None
    zone: int | None = None
    duration_sec: int
    priority: int
    conditions: dict
    action: str

class EnhancedRuleObject(BaseModel):
    """Enhanced rule object supporting all v0.1.92+ rule types"""
    id: int
    name: str
    rule_type: str = "zone_stay"
    subject_id: str | None = None
    zone: int | str | None = None  # Can be int (legacy) or string (layered/transitions)
    from_zone: str | None = None   # For zone_transition rules
    to_zone: str | None = None     # For zone_transition rules
    from_condition: str | None = None  # For layered_trigger rules
    to_condition: str | None = None    # For layered_trigger rules
    condition: str | None = None   # For proximity_condition rules
    proximity_target: str | None = None  # For proximity_condition rules
    proximity_distance: float | None = None  # For proximity_condition rules
    zone_transition: dict | None = None  # For proximity_condition rules
    trigger_layers: dict | None = None   # For layered_trigger rules
    duration_sec: int = 600
    priority: int = 1
    conditions: dict = {}
    action: str = "alert"

def parse_tetse_rule(id: int, name: str, conditions: dict) -> dict | None:
    """
    Enhanced TETSE rule parser supporting all v0.1.92+ rule types.
    
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

        # Detect rule type from conditions
        rule_type = conditions.get("rule_type", "zone_stay")
        logger.debug(f"Detected rule type: {rule_type} for rule id={id}")

        # Route to appropriate parser based on rule type
        if rule_type == "zone_stay":
            return parse_zone_stay_rule(id, name, conditions)
        elif rule_type == "zone_transition":
            return parse_zone_transition_rule(id, name, conditions)
        elif rule_type == "layered_trigger":
            return parse_layered_trigger_rule(id, name, conditions)
        elif rule_type == "proximity_condition":
            return parse_proximity_condition_rule(id, name, conditions)
        else:
            # Try legacy parsing for backward compatibility
            logger.debug(f"Unknown rule type '{rule_type}', attempting legacy parsing")
            return parse_legacy_rule(id, name, conditions)
            
    except Exception as e:
        logger.error(f"Failed parsing rule id={id}: {str(e)}")
        return None

def parse_zone_stay_rule(id: int, name: str, conditions: dict) -> dict | None:
    """Parse zone stay rules (legacy and enhanced)"""
    try:
        rule_data = {
            "rule_type": "zone_stay",
            "subject_id": conditions.get("subject_id"),
            "zone": conditions.get("zone"),
            "duration_sec": conditions.get("duration_sec", 600),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Handle zone resolution
        if rule_data["zone"] is not None:
            if isinstance(rule_data["zone"], str) and rule_data["zone"] in ("outside", "inside", "backyard"):
                # Keep layered aliases as strings
                logger.debug(f"Keeping layered alias: {rule_data['zone']}")
            else:
                # Resolve zone name to ID
                zone_id = resolve_zone_id(rule_data["zone"])
                if zone_id is None:
                    logger.error(f"Zone '{rule_data['zone']}' not found for rule id={id}")
                    return None
                rule_data["zone"] = zone_id

        # Validate with enhanced model
        rule = EnhancedRuleObject(id=id, name=name, **rule_data)
        
        # Handle exclude_parent_zone if present
        if "exclude_parent_zone" in rule_data["conditions"]:
            exclude_zone_input = rule_data["conditions"]["exclude_parent_zone"]
            exclude_zone_id = resolve_zone_id(exclude_zone_input)
            if exclude_zone_id is None:
                logger.error(f"Exclude zone '{exclude_zone_input}' not found for rule id={id}")
                return None
            rule_data["conditions"]["exclude_parent_zone"] = exclude_zone_id

        parsed = rule.model_dump()
        logger.debug(f"Parsed zone stay rule: {parsed}")
        return parsed
        
    except ValidationError as e:
        logger.error(f"Zone stay rule validation failed for rule id={id}: {str(e)}")
        return None

def parse_zone_transition_rule(id: int, name: str, conditions: dict) -> dict | None:
    """Parse zone transition rules"""
    try:
        rule_data = {
            "rule_type": "zone_transition",
            "subject_id": conditions.get("subject_id"),
            "from_zone": conditions.get("from_zone"),
            "to_zone": conditions.get("to_zone"),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Validate with enhanced model (zones kept as strings for transitions)
        rule = EnhancedRuleObject(id=id, name=name, **rule_data)
        
        parsed = rule.model_dump()
        logger.debug(f"Parsed zone transition rule: {parsed}")
        return parsed
        
    except ValidationError as e:
        logger.error(f"Zone transition rule validation failed for rule id={id}: {str(e)}")
        return None

def parse_layered_trigger_rule(id: int, name: str, conditions: dict) -> dict | None:
    """Parse layered trigger rules"""
    try:
        rule_data = {
            "rule_type": "layered_trigger",
            "subject_id": conditions.get("subject_id"),
            "from_condition": conditions.get("from_condition"),
            "to_condition": conditions.get("to_condition"),
            "trigger_layers": conditions.get("trigger_layers", {}),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Validate with enhanced model
        rule = EnhancedRuleObject(id=id, name=name, **rule_data)
        
        parsed = rule.model_dump()
        logger.debug(f"Parsed layered trigger rule: {parsed}")
        return parsed
        
    except ValidationError as e:
        logger.error(f"Layered trigger rule validation failed for rule id={id}: {str(e)}")
        return None

def parse_proximity_condition_rule(id: int, name: str, conditions: dict) -> dict | None:
    """Parse proximity condition rules"""
    try:
        rule_data = {
            "rule_type": "proximity_condition",
            "subject_id": conditions.get("subject_id"),
            "condition": conditions.get("condition"),
            "proximity_target": conditions.get("proximity_target"),
            "proximity_distance": conditions.get("proximity_distance", 6.0),
            "zone_transition": conditions.get("zone_transition", {}),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Validate with enhanced model
        rule = EnhancedRuleObject(id=id, name=name, **rule_data)
        
        parsed = rule.model_dump()
        logger.debug(f"Parsed proximity condition rule: {parsed}")
        return parsed
        
    except ValidationError as e:
        logger.error(f"Proximity condition rule validation failed for rule id={id}: {str(e)}")
        return None

def parse_legacy_rule(id: int, name: str, conditions: dict) -> dict | None:
    """Parse legacy rules for backward compatibility"""
    try:
        rule_data = {
            "subject_id": conditions.get("subject_id"),
            "zone": conditions.get("zone"),
            "duration_sec": conditions.get("duration_sec", 600),
            "priority": conditions.get("priority", 1),
            "conditions": conditions.get("conditions", {}),
            "action": conditions.get("action", "alert")
        }

        # Validate with legacy model (requires integer zone)
        rule = LegacyRuleObject(id=id, name=name, **rule_data)

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
        logger.debug(f"Parsed legacy rule: {parsed}")
        return parsed
        
    except ValidationError as e:
        logger.error(f"Legacy rule validation failed for rule id={id}: {str(e)}")
        return None

def parse_rule(raw_rule):
    """
    Parse and normalize rule JSON (already enriched by GPT).
    Returns: parsed rule dict or raises ValueError.
    Enhanced for v0.1.92+ rule types.
    """
    try:
        rule_data = raw_rule.get("rule") or raw_rule
        logger.debug(f"Raw incoming rule_data: {rule_data}")

        # Detect rule type
        rule_type = rule_data.get("rule_type", "zone_stay")
        
        if rule_type == "zone_stay":
            # Legacy zone stay rule parsing
            subject_id = rule_data.get("subject_id") or rule_data.get("entity_id")
            zone_input = rule_data.get("zone")
            duration_sec = rule_data.get("duration_sec")
            priority = rule_data.get("priority", 1)
            conditions = rule_data.get("conditions", {})
            action = rule_data.get("action", "alert")

            if not subject_id or not zone_input or not duration_sec:
                raise ValueError("Missing required fields in rule.")

            # Handle layered aliases
            if zone_input in ("outside", "inside", "backyard"):
                zone_id = zone_input  # Keep as string
            else:
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
                "rule_type": rule_type,
                "subject_id": subject_id,
                "zone": zone_id,
                "duration_sec": int(duration_sec),
                "conditions": conditions,
                "priority": int(priority),
                "action": action
            }
        else:
            # Enhanced rule types - pass through with minimal processing
            parsed = rule_data.copy()
            
        logger.debug(f"Parsed rule: {parsed}")
        return parsed

    except Exception as e:
        logger.error(f"Failed to parse rule: {e}")
        raise

def resolve_zone_id(input_val):
    """
    Enhanced zone resolver supporting both legacy int IDs and v0.1.92+ string zones.
    """
    if input_val is None:
        return None
        
    # Handle layered trigger aliases
    if input_val in ("outside", "inside", "off_campus", "backyard"):
        logger.debug(f"Keeping layered trigger alias: {input_val}")
        return input_val
        
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
    if zone_map:
        name_lookup = {zinfo["name"].lower(): zid for zid, zinfo in zone_map.items()}
        zone_id = name_lookup.get(str(input_val).lower())
        if zone_id is not None:
            return zone_id
    
    logger.debug(f"Zone name '{input_val}' not found in name lookup")
    return None