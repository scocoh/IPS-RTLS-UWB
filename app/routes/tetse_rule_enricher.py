# Name: tetse_rule_enricher.py
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

# File: tetse_rule_enricher.py
# Version: 0.4.0
# Created: 250616
# Modified: 250616 
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Clean output directly to parser-ready form

# Version: (Phase 11.7 — Enrichment Output Injection)

import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

from .tetse_zone_map import get_zone_hierarchy

logger = logging.getLogger("TETSE_RULE_ENRICHER")
logger.setLevel(logging.DEBUG)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt (unchanged)
SYSTEM_PROMPT = """
You are a rule-building assistant for a real-time location system.
The user will describe a rule in natural language.

You must analyze the input and produce a valid RuleBuilder JSON.
The output must always contain:
- entity_id (string)
- zone (integer zone_id)
- duration_sec (integer, seconds)
- action (string, e.g. "alert")
- conditions (object)
- priority (integer, default 1)

Use only the following valid zone list:
{zone_hints}

Example output:
{{
  "rule": {{
    "entity_id": "Eddy",
    "zone": 422,
    "duration_sec": 600,
    "action": "alert",
    "conditions": {{ "exclude_parent_zone": 423 }},
    "priority": 1
  }}
}}

ALWAYS produce strict JSON.
"""

# Build dynamic prompt based on loaded zone map
def build_prompt(user_input):
    zones = get_zone_hierarchy()
    hints = "\n".join([f"- {zid}: {zinfo['name']}" for zid, zinfo in zones.items()])
    return SYSTEM_PROMPT.format(zone_hints=hints) + f"\n\nUser Input: {user_input}\n"

def enrich_rule(user_input):
    prompt = build_prompt(user_input)
    logger.debug("Submitting GPT enrichment request...")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(zone_hints="")},
            {"role": "user", "content": user_input}
        ],
        response_format="json"
    )

    # Parse GPT output (model should return pure JSON)
    content = response.choices[0].message.content
    logger.debug(f"Raw GPT Output: {content}")

    try:
        rule_data = json.loads(content)
        injected = inject_clean_output(rule_data)
        return injected
    except Exception as e:
        logger.error(f"Failed to parse enrichment output: {e}")
        return {}

def inject_clean_output(raw_json):
    """
    Normalize GPT output directly to parser-ready structure.
    Convert entity_id -> subject_id, ensure conditions object exists.
    """
    rule_obj = raw_json.get("rule", {})

    subject_id = rule_obj.pop("entity_id", None) or rule_obj.get("subject_id")
    rule_obj["subject_id"] = subject_id

    rule_obj.setdefault("conditions", {})
    rule_obj.setdefault("priority", 1)
    rule_obj.setdefault("action", "alert")

    logger.debug(f"Injected Clean Output: {rule_obj}")
    return rule_obj
