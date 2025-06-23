# Name: tetse_rule_interpreter.py
# Version: 0.5.5
# Created: 971201
# Modified: 250622
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Parses natural language rules for TETSE in ParcoRTLS with layered trigger and proximity support
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/tetse_rule_interpreter.py
# Version: 0.5.5. - Fixed compound transition rules
# Version: 0.5.4 - Fixed rule type detection for zone transitions vs layered triggers and enhanced compound condition support
# Previous: 0.5.3 - Added back "any tag" example for outside→inside transitions
# Previous: 0.5.2 - Fixed device type mapping and added "any device" example for outside→inside
# Previous: 0.5.1 - Fixed bidirectional layered trigger support (outside → inside)
# Previous: 0.4.1 - Enhanced device type pattern recognition and more flexible zone matching
# Previous: 0.4.0 - Added device type support for "any tag" rules
# Previous: 0.3.2 - Fixed endpoint URLs for device and trigger direction loading
# Previous: 0.3.1 - Fixed semantic zone matching and validation logic
# Previous: 0.3.0 - Added transition rule support for "moves from X to Y" patterns
# Previous: 0.2.3 - Added support for 'outside'/'backyard' aliases, improved error handling
# Previous: 0.2.2 - Changed entity_id to subject_id, handled empty device list
# Previous: 0.2.1 - Initial GPT-4o implementation
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import os
import json
import logging
import aiohttp
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load env key
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger("TETSE_RULE_INTERPRETER")
logger.setLevel(logging.DEBUG)

# Pydantic Rule Models
class ZoneStayRule(BaseModel):
    rule_type: str = "zone_stay"
    subject_id: str  # Can be specific ID or device type pattern like "device_type:1"
    zone: str
    duration_sec: int
    action: str

class ZoneTransitionRule(BaseModel):
    rule_type: str = "zone_transition"
    subject_id: str  # Can be specific ID or device type pattern like "device_type:1"
    from_zone: str
    to_zone: str
    action: str

class LayeredTriggerRule(BaseModel):
    rule_type: str = "layered_trigger"
    subject_id: str
    from_condition: str  # "inside", "outside", "off_campus"
    to_condition: str    # "inside", "outside", "off_campus" 
    trigger_layers: dict # BOL2 and CL1 trigger configuration
    action: str

class ProximityConditionRule(BaseModel):
    rule_type: str = "proximity_condition"
    subject_id: str
    condition: str  # "outside_without_proximity", "inside_without_proximity", etc.
    proximity_target: str  # "device_type:personnel_badge" or specific device ID
    proximity_distance: float  # Distance in feet
    zone_transition: dict  # {"from": "inside", "to": "outside"}
    action: str

# Default fallback SYSTEM_PROMPT for zone stay rules
DEFAULT_PROMPT = """
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract rule information from natural language requests.

Rules must include:
- subject_id (alphanumeric, no spaces, must be a valid device ID)
- zone (string zone name, must be a valid zone or alias)
- duration_sec (integer, seconds, minimum 1)
- action (must be one of: alert, log, mqtt)

Output valid JSON in this format:
{ "rule_type": "zone_stay", "subject_id": "...", "zone": "...", "duration_sec": ..., "action": "..." }

If the subject_id or zone is invalid, or parsing fails, respond with:
{ "error": "Could not parse rule: invalid subject or zone" }
"""

async def get_live_zones():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/zones_for_ai") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    zones = data.get("zones", [])
                    logger.info(f"Loaded {len(zones)} zones for AI prompt injection.")
                    return zones
    except Exception as e:
        logger.error(f"Failed to load zones for AI: {str(e)}")
    return []

async def get_live_devices():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/get_all_devices") as resp:
                if resp.status == 200:
                    devices = await resp.json()
                    # Transform to match expected format
                    formatted_devices = [
                        {
                            "id": device["x_id_dev"], 
                            "name": device["x_nm_dev"] or device["x_id_dev"],
                            "type": device["i_typ_dev"]
                        } 
                        for device in devices
                    ]
                    logger.info(f"Loaded {len(formatted_devices)} devices for AI prompt injection.")
                    return formatted_devices
    except Exception as e:
        logger.error(f"Failed to load devices for AI: {str(e)}")
    return []

async def get_live_device_types():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/list_device_types") as resp:
                if resp.status == 200:
                    device_types = await resp.json()
                    logger.info(f"Loaded {len(device_types)} device types for AI prompt injection.")
                    return device_types
    except Exception as e:
        logger.error(f"Failed to load device types for AI: {str(e)}")
    return []

async def get_live_trigger_directions():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/list_trigger_directions") as resp:
                if resp.status == 200:
                    directions = await resp.json()
                    logger.info(f"Loaded {len(directions)} trigger directions for AI prompt injection.")
                    return directions
    except Exception as e:
        logger.error(f"Failed to load trigger directions for AI: {str(e)}")
    return []

def detect_rule_type(input_text: str) -> str:
    """
    Enhanced rule type detection with compound condition support
    Priority: proximity_condition > zone_transition > layered_trigger > zone_stay
    
    COMPOUND RULES SUPPORT:
    - Room-to-outside + proximity conditions = proximity_condition
    - Specific room transitions = zone_transition  
    - Pure inside/outside transitions = layered_trigger
    - Duration in zone = zone_stay
    
    FIXED: Prioritize zone_transition over layered_trigger for specific room transitions
    """
    text_lower = input_text.lower()
    
    logger.debug(f"Detecting rule type for: '{input_text}'")
    
    # 1. HIGHEST PRIORITY: Proximity conditions (with or without specific rooms)
    proximity_keywords = [
        'without me', 'without being near', 'without proximity', 'without personnel',
        'not near', 'away from', 'separated from', 'alone',
        'without a personnel', 'no personnel', 'there is no personnel',
        'with a personnel', 'there is a personnel', 'with personnel',
        'near personnel', 'close to personnel', 'personnel nearby'
    ]
    
    for keyword in proximity_keywords:
        if keyword in text_lower:
            logger.debug(f"Detected proximity condition rule with keyword: '{keyword}'")
            return 'proximity_condition'
    
    # 2. Check for compound conditions (AND/OR logic)
    compound_indicators = [
        ' and there is no ', ' and there is a ', ' and no ', ' and with ',
        ' without ', ' with ', ' near ', ' not near '
    ]
    
    has_transition = ' from ' in text_lower and ' to ' in text_lower
    has_compound = any(indicator in text_lower for indicator in compound_indicators)
    
    if has_transition and has_compound:
        # This is likely a proximity condition with spatial transition
        logger.debug("Detected compound rule with transition + proximity condition")
        return 'proximity_condition'
    
    # 3. ZONE TRANSITION: Check for specific room/zone transitions BEFORE layered trigger
    if has_transition:
        # Check if this mentions specific rooms/zones (not just inside/outside)
        specific_zones = [
            'living room', 'kitchen', 'bedroom', 'bathroom', 'garage', 'dining room',
            'hall', 'porch', 'office', 'basement', 'attic', 'closet', 'pantry',
            'family room', 'den', 'study', 'laundry', 'entry', 'foyer', 'master br',
            'front hall', 'front porch', 'back porch', 'utility room'
        ]
        
        # If it mentions specific zones, it's a zone transition
        for zone in specific_zones:
            if zone in text_lower:
                logger.debug(f"Detected zone transition rule with specific zone: '{zone}'")
                return 'zone_transition'
        
        # Also check transition keywords
        transition_keywords = [
            'moves from', 'transitions from', 'goes from', 'travels from',
            'leaves', 'exits', 'moves to', 'enters from', 'coming from',
            'move from', 'transition from', 'go from', 'travel from'
        ]
        
        for keyword in transition_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected zone transition rule with keyword: '{keyword}'")
                return 'zone_transition'
        
        # Check if this is a pure inside/outside layered trigger
        if (('inside' in text_lower and 'outside' in text_lower) and 
            not any(zone in text_lower for zone in specific_zones)):
            logger.debug("Detected layered trigger rule with pure inside/outside transition")
            return 'layered_trigger'
        else:
            # Default: if it has from/to but no specific zones detected, still zone_transition
            logger.debug("Detected zone transition rule with from/to pattern")
            return 'zone_transition'
    
    # 4. LAYERED TRIGGER: Pure inside/outside transitions without specific rooms
    if ('inside' in text_lower or 'outside' in text_lower):
        # Check if this is PURE inside/outside (no specific room names)
        specific_zones = [
            'living room', 'kitchen', 'bedroom', 'bathroom', 'garage', 'dining room',
            'hall', 'porch', 'office', 'basement', 'attic', 'closet', 'pantry',
            'family room', 'den', 'study', 'laundry', 'entry', 'foyer'
        ]
        
        has_specific_zone = any(zone in text_lower for zone in specific_zones)
        
        if not has_specific_zone and ('from' in text_lower or 'to' in text_lower):
            # Pure inside/outside transition
            logger.debug("Detected layered trigger rule with inside/outside without specific zones")
            return 'layered_trigger'
    
    # 5. Other transition keywords without from/to
    transition_keywords = [
        'moves from', 'transitions from', 'goes from', 'travels from',
        'leaves', 'exits', 'moves to', 'enters from', 'coming from',
        'move from', 'transition from', 'go from', 'travel from'
    ]
    
    for keyword in transition_keywords:
        if keyword in text_lower:
            logger.debug(f"Detected zone transition rule with keyword: '{keyword}'")
            return 'zone_transition'
    
    # 6. DEFAULT: Zone stay rule
    logger.debug("Detected zone stay rule (no transition or proximity keywords found)")
    return 'zone_stay'

def build_proximity_condition_prompt(zones, devices, device_types, trigger_directions):
    """Build GPT prompt for proximity condition rules with enhanced compound condition support"""
    zone_list = [f"- {z['name']} (id={z['id']})" for z in zones] if zones else ["- None"]
    zone_block = "\n".join(zone_list)
    device_list = [f"- {d['id']} (name={d['name']}, type={d['type']})" for d in devices] if devices else ["- None"]
    device_block = "\n".join(device_list)
    
    # Build device type information
    if device_types:
        type_list = [f"- {dt['i_typ_dev']}: {dt['x_dsc_dev']}" for dt in device_types]
        type_block = "\n".join(type_list)
        
        # Identify personnel badge and tag types
        personnel_types = [dt['i_typ_dev'] for dt in device_types if 'personnel' in dt['x_dsc_dev'].lower() or 'badge' in dt['x_dsc_dev'].lower()]
        tag_types = [dt['i_typ_dev'] for dt in device_types if 'tag' in dt['x_dsc_dev'].lower()]
        personnel_info = f"Personnel/Badge device types: {personnel_types}" if personnel_types else "Personnel/Badge device types: [4] (Personnel Badge)"
        tag_info = f"Tag device types: {tag_types}" if tag_types else "Tag device types: [1, 2] (Tag types)"
    else:
        type_block = "- 1: Tag\n- 4: Personnel Badge\n- 6: Receiver"
        personnel_info = "Personnel/Badge device types: [4] (Personnel Badge)"
        tag_info = "Tag device types: [1, 2] (Tag types)"

    prompt = f"""
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract PROXIMITY CONDITION rule information from natural language requests.

This system uses LAYERED TRIGGER ARCHITECTURE:
- INSIDE = Within Building Outside L2 (BOL2) zones (type=10)
- OUTSIDE = Exited BOL2 but still in Campus L1 (CL1) zones (type=1) 
- OFF-CAMPUS = Not in CL1 zones

Valid zones at this site:
{zone_block}

Valid device IDs and types:
{device_block}

DEVICE TYPE INFORMATION:
{type_block}
{personnel_info}
{tag_info}

PROXIMITY CONDITION PARSING (ENHANCED v0.5.5):
When users mention proximity requirements (without me, without personnel, with tag, etc.):

SUBJECT_ID PATTERNS:
- Specific device: "tag 23001" → "23001"
- Device type: "any tag", "all tags" → "device_type:tag"
- Dog tags: "dog tag", "any dog tag" → "device_type:tag" (assuming tags are used for dogs)

PROXIMITY TARGET PATTERNS (ENHANCED v0.5.5):
- "without me" → "device_type:personnel_badge" (assumes user has personnel badge)
- "without personnel" → "device_type:personnel_badge"
- "without being near a personnel badge" → "device_type:personnel_badge"
- "without proximity to personnel" → "device_type:personnel_badge"
- "with me" → "device_type:personnel_badge"
- "with personnel" → "device_type:personnel_badge"
- "near personnel" → "device_type:personnel_badge"
- "with tag 23003" → "23003" (specific tag ID)
- "with tag [ID]" → "[ID]" (any specific tag ID)
- "without tag 23003" → "23003" (specific tag ID, negative condition)
- "without tag [ID]" → "[ID]" (any specific tag ID, negative condition)
- "near tag 23003" → "23003" (specific tag ID)

CONDITION PATTERNS (ENHANCED v0.5.5):
- "goes outside without X" → condition: "outside_without_proximity"
- "goes outside and there is no X" → condition: "outside_without_proximity"  
- "goes outside with X" → condition: "outside_with_proximity"
- "goes outside and there is a X" → condition: "outside_with_proximity"
- "moves inside without X" → condition: "inside_without_proximity"
- "moves inside with X" → condition: "inside_with_proximity"
- "leaves building without X" → condition: "outside_without_proximity"
- "goes from inside to outside with X" → condition: "outside_with_proximity"
- "goes from inside to outside without X" → condition: "outside_without_proximity"

ZONE TRANSITION PATTERNS (ENHANCED):
- "from Living Room to outside" → zone_transition: {{"from": "Living Room RL6-Child", "to": "outside"}}
- "from Kitchen to outside" → zone_transition: {{"from": "Kitchen L6-Child", "to": "outside"}}  
- "from inside to outside" → zone_transition: {{"from": "inside", "to": "outside"}}
- "from X to Y" → zone_transition: {{"from": "X", "to": "Y"}}

DEFAULT PROXIMITY DISTANCE: 6.0 feet (adjustable range: 3-12 feet)

Output valid JSON in this exact format:
{{
  "rule_type": "proximity_condition",
  "subject_id": "...",
  "condition": "outside_without_proximity",
  "proximity_target": "device_type:personnel_badge",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "inside", "to": "outside"}},
  "action": "alert"
}}

EXAMPLES (ENHANCED v0.5.5):
Input: "if tag 23001 goes outside without me, send an alert"
Output: {{
  "rule_type": "proximity_condition",
  "subject_id": "23001", 
  "condition": "outside_without_proximity",
  "proximity_target": "device_type:personnel_badge",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "inside", "to": "outside"}},
  "action": "alert"
}}

Input: "if tag 23001 goes from inside to outside with tag 23003 send an alert"
Output: {{
  "rule_type": "proximity_condition",
  "subject_id": "23001",
  "condition": "outside_with_proximity",
  "proximity_target": "23003",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "inside", "to": "outside"}},
  "action": "alert"
}}

Input: "when tag 23001 moves from Living Room to outside with tag 23003 alert"
Output: {{
  "rule_type": "proximity_condition",
  "subject_id": "23001",
  "condition": "outside_with_proximity",
  "proximity_target": "23003",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "Living Room RL6-Child", "to": "outside"}},
  "action": "alert"
}}

Input: "when all tags transition from Living Room to outside send mqtt and there is no personnel tag"
Output: {{
  "rule_type": "proximity_condition",
  "subject_id": "device_type:tag",
  "condition": "outside_without_proximity",
  "proximity_target": "device_type:personnel_badge",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "Living Room RL6-Child", "to": "outside"}},
  "action": "mqtt"
}}

Input: "alert when any dog tag moves outside without being near a personnel badge"
Output: {{
  "rule_type": "proximity_condition",
  "subject_id": "device_type:tag",
  "condition": "outside_without_proximity", 
  "proximity_target": "device_type:personnel_badge",
  "proximity_distance": 6.0,
  "zone_transition": {{"from": "inside", "to": "outside"}},
  "action": "alert"
}}

If the subject_id, proximity_target, or condition cannot be parsed, respond with:
{{ "error": "Could not parse rule: invalid subject, proximity target, or condition" }}
"""
    return prompt

def build_layered_trigger_prompt(zones, devices, device_types, trigger_directions):
    """Build GPT prompt for layered trigger rules (inside/outside without proximity)"""
    zone_list = [f"- {z['name']} (id={z['id']})" for z in zones] if zones else ["- None"]
    zone_block = "\n".join(zone_list)
    device_list = [f"- {d['id']} (name={d['name']}, type={d['type']})" for d in devices] if devices else ["- None"]
    device_block = "\n".join(device_list)
    
    prompt = f"""
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract LAYERED TRIGGER rule information.

LAYERED TRIGGER ARCHITECTURE:
This system uses sophisticated spatial intelligence with layered zones:
- INSIDE = Within Building Outside L2 (BOL2) zones (type=10) 
- OUTSIDE = Exited BOL2 but still in Campus L1 (CL1) zones (type=1)
- OFF-CAMPUS = Not in CL1 zones

Valid zones at this site:
{zone_block}

Valid device IDs:
{device_block}

DEVICE TYPE PATTERNS FOR LAYERED TRIGGERS:
- "any tag", "all tags", "tags" → use "device_type:tag"
- "any device", "all devices", "devices" → use "device_type:any"  
- "any receiver", "receivers" → use "device_type:receiver"
- "any personnel badge", "personnel badges" → use "device_type:personnel_badge"

IMPORTANT: Always use "device_type:any" for "any device" patterns, never "device_type:device"

LAYERED TRIGGER CRITERIA (v0.5.4):
Only use layered triggers for PURE inside/outside transitions WITHOUT specific room names.
If specific rooms are mentioned (Living Room, Kitchen, etc.), this should be zone_transition instead.

LAYERED TRIGGER LOGIC:
- inside → outside: Uses BOL2 "On Exit" (direction=5) + CL1 "While In" (direction=1)
- outside → inside: Uses BOL2 "On Enter" (direction=4) + CL1 "While In" (direction=1)
- inside → off_campus: Uses CL1 "On Exit" (direction=5)
- off_campus → inside: Uses CL1 "On Enter" (direction=4) + BOL2 "While In" (direction=1)

Output valid JSON in this exact format:
{{
  "rule_type": "layered_trigger",
  "subject_id": "...",
  "from_condition": "inside",
  "to_condition": "outside", 
  "trigger_layers": {{
    "bol2_trigger": {{"zone_type": 10, "direction": 5}},
    "cl1_trigger": {{"zone_type": 1, "direction": 1}}
  }},
  "action": "alert"
}}

EXAMPLES (v0.5.4):
Input: "if tag 23001 moves from inside to outside send alert"
Output: {{
  "rule_type": "layered_trigger",
  "subject_id": "23001",
  "from_condition": "inside",
  "to_condition": "outside",
  "trigger_layers": {{
    "bol2_trigger": {{"zone_type": 10, "direction": 5}},
    "cl1_trigger": {{"zone_type": 1, "direction": 1}}
  }},
  "action": "alert"
}}

Input: "when any tag goes from outside to inside log event"
Output: {{
  "rule_type": "layered_trigger",
  "subject_id": "device_type:tag",
  "from_condition": "outside", 
  "to_condition": "inside",
  "trigger_layers": {{
    "bol2_trigger": {{"zone_type": 10, "direction": 4}},
    "cl1_trigger": {{"zone_type": 1, "direction": 1}}
  }},
  "action": "log"
}}

Input: "if any device moves from outside to inside send mqtt"
Output: {{
  "rule_type": "layered_trigger",
  "subject_id": "device_type:any",
  "from_condition": "outside",
  "to_condition": "inside", 
  "trigger_layers": {{
    "bol2_trigger": {{"zone_type": 10, "direction": 4}},
    "cl1_trigger": {{"zone_type": 1, "direction": 1}}
  }},
  "action": "mqtt"
}}

If parsing fails, respond with:
{{ "error": "Could not parse layered trigger rule" }}
"""
    return prompt

def build_zone_stay_prompt(zones, devices, device_types):
    """Build GPT prompt for zone stay rules with device type support"""
    zone_list = [f"- {z['name']} (id={z['id']})" for z in zones] if zones else ["- None"]
    zone_block = "\n".join(zone_list)
    device_list = [f"- {d['id']} (name={d['name']}, type={d['type']})" for d in devices] if devices else ["- None"]
    device_block = "\n".join(device_list)
    
    # Build device type information
    if device_types:
        type_list = [f"- {dt['i_typ_dev']}: {dt['x_dsc_dev']}" for dt in device_types]
        type_block = "\n".join(type_list)
        
        # Identify tag types
        tag_types = [dt['i_typ_dev'] for dt in device_types if 'tag' in dt['x_dsc_dev'].lower()]
        tag_info = f"Tag device types: {tag_types}" if tag_types else "Tag device types: [1, 2, 4] (common)"
    else:
        type_block = "- 1: Tag\n- 6: Receiver\n- 18: Cable Drop"
        tag_info = "Tag device types: [1, 2, 4] (common)"

    prompt = f"""
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract ZONE STAY rule information from natural language requests.

LAYERED SPATIAL INTELLIGENCE:
- INSIDE = Within Building Outside L2 (BOL2) zones (type=10)
- OUTSIDE = Campus L1 (CL1) zones but outside BOL2 (type=1 excluding type=10)  
- OFF-CAMPUS = Not in CL1 zones

Valid zones at this site:
{zone_block}

ZONE MATCHING RULES:
1. EXACT MATCH: If the input zone exactly matches a zone name from the list above, use it directly
2. PARTIAL MATCH: If input contains a room name (Living Room, Kitchen, Bedroom, etc.), find the zone containing that name
3. LAYERED ALIASES: 
   - "outside" → use "outside" (layered: CL1 zones excluding BOL2)
   - "inside" → use "inside" (layered: BOL2 zones)

Valid device IDs and types:
{device_block}

DEVICE TYPE INFORMATION:
{type_block}
{tag_info}

SUBJECT_ID PARSING RULES:
1. SPECIFIC DEVICE: Use exact device ID if mentioned (e.g., "23001")
2. DEVICE TYPE PATTERNS (IMPORTANT - BE FLEXIBLE):
   - "any tag", "all tags", "tags" → use "device_type:tag" 
   - "any device", "all devices", "devices" → use "device_type:any"
   - "any receiver", "receivers" → use "device_type:receiver"

CRITICAL: When device type patterns are used, be MORE FLEXIBLE with zone matching. If a zone can be reasonably mapped (even partially), accept it.

ZONE STAY PARSING RULES:
- subject_id: Specific device ID OR device type pattern
- zone: Use exact zone name, partial match, or layered alias
- duration_sec: Extract from phrases like "5 minutes" = 300 seconds, "2 min" = 120 seconds
- action: Extract from "alert", "log", "mqtt", "send alert", "send notification"

Output valid JSON in this exact format:
{{ "rule_type": "zone_stay", "subject_id": "...", "zone": "...", "duration_sec": ..., "action": "..." }}

EXAMPLES:
Input: "If 23001 stays in Living Room for 5 minutes then alert"
Output: {{ "rule_type": "zone_stay", "subject_id": "23001", "zone": "Living Room RL6-Child", "duration_sec": 300, "action": "alert" }}

Input: "if any tag stays outside for 3 minutes alert"
Output: {{ "rule_type": "zone_stay", "subject_id": "device_type:tag", "zone": "outside", "duration_sec": 180, "action": "alert" }}

Input: "when all tags stay in Kitchen for 2 minutes log"
Output: {{ "rule_type": "zone_stay", "subject_id": "device_type:tag", "zone": "Kitchen L6-Child", "duration_sec": 120, "action": "log" }}

If the subject_id or zone cannot be matched, respond with:
{{ "error": "Could not parse rule: invalid subject or zone" }}

IMPORTANT: Be GENEROUS with zone matching for device type patterns. If zones can be reasonably interpreted, accept them.
"""
    return prompt

def build_zone_transition_prompt_with_types(zones, devices, device_types, trigger_directions):
    """Build GPT prompt for zone transition rules with device type support and enhanced zone validation"""
    zone_list = [f"- {z['name']} (id={z['id']})" for z in zones] if zones else ["- None"]
    zone_block = "\n".join(zone_list)
    device_list = [f"- {d['id']} (name={d['name']}, type={d['type']})" for d in devices] if devices else ["- None"]
    device_block = "\n".join(device_list)
    
    # Build device type information
    if device_types:
        type_list = [f"- {dt['i_typ_dev']}: {dt['x_dsc_dev']}" for dt in device_types]
        type_block = "\n".join(type_list)
        
        # Identify tag types
        tag_types = [dt['i_typ_dev'] for dt in device_types if 'tag' in dt['x_dsc_dev'].lower()]
        tag_info = f"Tag device types: {tag_types}" if tag_types else "Tag device types: [1, 2, 4] (common)"
    else:
        type_block = "- 1: Tag\n- 6: Receiver\n- 18: Cable Drop"
        tag_info = "Tag device types: [1, 2, 4] (common)"
    
    # Format trigger directions
    if trigger_directions:
        directions_list = [f"- {d['i_dir']}: {d['x_dir']}" for d in trigger_directions]
        directions_block = "\n".join(directions_list)
    else:
        directions_block = "- 4: On Enter (default)\n- 5: On Exit\n- 3: On Cross"
    
    prompt = f"""
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract ZONE TRANSITION rule information from natural language requests.

LAYERED SPATIAL INTELLIGENCE:
- INSIDE = Within Building Outside L2 (BOL2) zones (type=10)
- OUTSIDE = Campus L1 (CL1) zones but outside BOL2 (type=1 excluding type=10)
- OFF-CAMPUS = Not in CL1 zones

Valid zones at this site:
{zone_block}

SEMANTIC ZONE MATCHING (ENHANCED v0.5.4):
When users refer to common room names, intelligently map them to actual zones from the list above:

1. EXACT MATCH: If input zone exactly matches a zone name, use it directly
2. PARTIAL MATCH MAPPING:
   - "Living Room" → Find zone containing "Living Room" (e.g., "Living Room RL6-Child")
   - "Kitchen" → Find zone containing "Kitchen" (e.g., "Kitchen L6-Child") 
   - "Bedroom" → Find zone containing "Bedroom" or "BR" (e.g., "Master BR RL6-Child")
   - "Garage" → Find zone containing "Garage" (e.g., "Garage RL6-Child")
   - "Bathroom" → Find zone containing "Bathroom" (e.g., "M Bathroom L6-Child")
   - "Dining Room" → Find zone containing "Dining" (e.g., "Dining Room L6-Child")
   - "Porch" → Find zone containing "Porch" (e.g., "Front Porch-Child")
   - "Hall" → Find zone containing "Hall" (e.g., "Front Hall L6-Child")

3. LAYERED ZONE ALIASES:
   - "outside" → use "outside" (layered: CL1 zones excluding BOL2)
   - "inside" → use "inside" (layered: BOL2 zones)

Valid device IDs and types:
{device_block}

DEVICE TYPE INFORMATION:
{type_block}
{tag_info}

SUBJECT_ID PARSING RULES:
1. SPECIFIC DEVICE: Use exact device ID if mentioned (e.g., "23001")
2. DEVICE TYPE PATTERNS (IMPORTANT - BE FLEXIBLE):
   - "any tag", "all tags", "tags" → use "device_type:tag"
   - "any device", "all devices", "devices" → use "device_type:any"
   - "any receiver", "receivers" → use "device_type:receiver"

CRITICAL: When device type patterns are used, be MORE FLEXIBLE with zone matching. If a zone can be reasonably mapped (even partially), accept it.

AVAILABLE TRIGGER DIRECTIONS:
{directions_block}

TRANSITION PARSING RULES:
- subject_id: Specific device ID OR device type pattern
- from_zone: Use exact zone name, partial match, or layered alias
- to_zone: Use exact zone name, partial match, or layered alias  
- action: Extract from "alert", "log", "mqtt", "send alert", "notify"

Output valid JSON in this exact format:
{{ "rule_type": "zone_transition", "subject_id": "...", "from_zone": "...", "to_zone": "...", "action": "..." }}

EXAMPLES WITH DEVICE TYPES (v0.5.4):
Input: "if tag 23001 moves from Living Room to outside send an alert"
Output: {{ "rule_type": "zone_transition", "subject_id": "23001", "from_zone": "Living Room RL6-Child", "to_zone": "outside", "action": "alert" }}

Input: "when any tag moves from Kitchen to outside send mqtt"
Output: {{ "rule_type": "zone_transition", "subject_id": "device_type:tag", "from_zone": "Kitchen L6-Child", "to_zone": "outside", "action": "mqtt" }}

Input: "when all tags transition from Living Room to outside send mqtt"
Output: {{ "rule_type": "zone_transition", "subject_id": "device_type:tag", "from_zone": "Living Room RL6-Child", "to_zone": "outside", "action": "mqtt" }}

Input: "alert when all tags transition from Kitchen to Garage"  
Output: {{ "rule_type": "zone_transition", "subject_id": "device_type:tag", "from_zone": "Kitchen L6-Child", "to_zone": "Garage RL6-Child", "action": "alert" }}

Input: "if any device transitions from Bedroom to Hall send log"
Output: {{ "rule_type": "zone_transition", "subject_id": "device_type:any", "from_zone": "Master BR RL6-Child", "to_zone": "Front Hall L6-Child", "action": "log" }}

If the subject_id or zones cannot be matched, respond with:
{{ "error": "Could not parse rule: invalid subject or zone" }}

IMPORTANT: Be GENEROUS with zone matching for device type patterns. If zones can be reasonably interpreted, accept them.
"""
    return prompt

async def parse_natural_language(input_text: str) -> dict:
    """
    Enhanced GPT-powered rule parser supporting layered triggers, proximity conditions, zone transitions, and zone stay rules.
    Site-aware with dynamic zone, device, device type, and trigger direction injection.
    
    Enhanced in v0.5.4:
    - Fixed rule type detection prioritization
    - Better compound condition support
    - Enhanced zone transition vs layered trigger detection
    """
    try:
        # Detect rule type from input text
        rule_type = detect_rule_type(input_text)
        logger.info(f"Detected rule type: {rule_type} for input: '{input_text}'")
        
        # Get live data from your FastAPI endpoints
        zones = await get_live_zones()
        devices = await get_live_devices()
        device_types = await get_live_device_types()
        trigger_directions = await get_live_trigger_directions()
        
        # Log the actual data being used
        logger.debug(f"Zones loaded: {len(zones)} zones")
        logger.debug(f"Devices loaded: {len(devices)} devices")
        logger.debug(f"Device types loaded: {len(device_types)} types")
        if devices:
            logger.debug(f"Sample devices: {devices[:3]}")
        if zones:
            logger.debug(f"Sample zones: {zones[:3]}")
        if device_types:
            logger.debug(f"Device types: {device_types}")
        
        # Build appropriate prompt based on rule type
        if rule_type == 'proximity_condition':
            system_prompt = build_proximity_condition_prompt(zones, devices, device_types, trigger_directions)
        elif rule_type == 'layered_trigger':
            system_prompt = build_layered_trigger_prompt(zones, devices, device_types, trigger_directions)
        elif rule_type == 'zone_transition':
            system_prompt = build_zone_transition_prompt_with_types(zones, devices, device_types, trigger_directions)
        else:
            system_prompt = build_zone_stay_prompt(zones, devices, device_types)

        logger.debug(f"Using rule type: {rule_type}")
        logger.debug(f"System prompt length: {len(system_prompt)} characters")

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Natural language rule: {input_text}"}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        logger.debug(f"GPT raw output: {content}")
        parsed = json.loads(content)

        if "error" in parsed:
            logger.warning(f"Parsing failed: {parsed['error']}")
            return {"error": parsed["error"]}

        # Validate with appropriate Pydantic model
        try:
            if parsed.get('rule_type') == 'proximity_condition':
                rule = ProximityConditionRule(**parsed)
            elif parsed.get('rule_type') == 'layered_trigger':
                rule = LayeredTriggerRule(**parsed)
            elif parsed.get('rule_type') == 'zone_transition':
                rule = ZoneTransitionRule(**parsed)
            else:
                rule = ZoneStayRule(**parsed)
        except Exception as validation_error:
            logger.error(f"Pydantic validation failed: {str(validation_error)}")
            return {"error": f"Rule validation failed: {str(validation_error)}"}
        
        result = rule.model_dump()
        logger.info(f"Successfully parsed {rule_type} rule: {result}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failure: {str(e)}")
        return {"error": f"Invalid JSON response from AI: {str(e)}"}
    except Exception as e:
        logger.error(f"Interpreter failure: {str(e)}", exc_info=True)
        return {"error": f"Internal parsing failure: {str(e)}"}

# Diagnostic function for testing rule type detection
def test_rule_type_detection(test_cases: list) -> dict:
    """
    Test rule type detection with various inputs
    Enhanced in v0.5.4 for better debugging
    """
    results = {}
    for case in test_cases:
        detected_type = detect_rule_type(case)
        results[case] = detected_type
        logger.info(f"Test case: '{case}' → Detected: {detected_type}")
    return results

# Test cases for v0.5.4 validation
TEST_CASES_V054 = [
    "when all tags transition from Living Room to outside send mqtt",  # Should be zone_transition
    "if tag 23001 moves from inside to outside send alert",  # Should be layered_trigger
    "when all tags transition from Living Room to outside send mqtt and there is no personnel tag",  # Should be proximity_condition
    "if tag 23001 goes outside without me, send an alert",  # Should be proximity_condition
    "if tag 23001 stays in Kitchen for 5 minutes alert",  # Should be zone_stay
    "when any device moves from Kitchen to Garage log event",  # Should be zone_transition
    "if any tag goes from outside to inside send mqtt"  # Should be layered_trigger
]