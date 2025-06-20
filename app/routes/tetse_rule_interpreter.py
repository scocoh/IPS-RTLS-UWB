# Name: tetse_rule_interpreter.py
# Version: 0.2.3
# Created: 971201
# Modified: 250619
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Parses natural language rules for TETSE in ParcoRTLS with site-aware zones and devices
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/tetse_rule_interpreter.py
# Version: 0.2.3 - Added support for 'outside'/'backyard' aliases, improved error handling
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

# Pydantic Rule Model
class RuleObject(BaseModel):
    subject_id: str
    zone: str
    duration_sec: int
    action: str

# Default fallback SYSTEM_PROMPT
DEFAULT_PROMPT = """
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract rule information from natural language requests.

Rules must include:
- subject_id (alphanumeric, no spaces, must be a valid device ID)
- zone (string zone name, must be a valid zone or alias)
- duration_sec (integer, seconds, minimum 1)
- action (must be one of: alert, log, mqtt)

Output valid JSON in this format:
{ "subject_id": "...", "zone": "...", "duration_sec": ..., "action": "..." }

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
            async with session.get("http://127.0.0.1:8000/api/devices_for_ai") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    devices = data.get("devices", [])
                    logger.info(f"Loaded {len(devices)} devices for AI prompt injection.")
                    return devices
    except Exception as e:
        logger.error(f"Failed to load devices for AI: {str(e)}")
    return []

def build_system_prompt(zones, devices):
    zone_list = [f"- {z['name']} (id={z['id']})" for z in zones] if zones else ["- None"]
    zone_block = "\n".join(zone_list)
    device_list = [f"- {d['id']} (name={d['name']})" for d in devices] if devices else ["- None"]
    device_block = "\n".join(device_list)

    prompt = f"""
You are a strict TETSE rule parser for ParcoRTLS. Your job is to extract rule information from natural language requests.

Valid zones at this site:
{zone_block}
Valid zone aliases: outside, backyard (map to virtual i_typ_zn=20 zones)

Valid device IDs (tags, used as subject_id):
{device_block}

Rules must include:
- subject_id (must exactly match one of the device IDs listed above, or return error if none available)
- zone (must exactly match one of the zone names listed above or be an alias: outside, backyard)
- duration_sec (integer, seconds, minimum 1)
- action (must be one of: alert, log, mqtt)

Output valid JSON in this exact format:
{{ "subject_id": "...", "zone": "...", "duration_sec": ..., "action": "..." }}

If the subject_id does not match a listed device ID, the zone does not match a listed zone or alias, or parsing fails, respond with:
{{ "error": "Could not parse rule: invalid subject or zone" }}
"""
    return prompt

async def parse_natural_language(input_text: str) -> dict:
    """
    GPT-powered live rule parser for RuleBuilder.
    Site-aware with dynamic zone and device injection.
    """
    try:
        zones = await get_live_zones()
        devices = await get_live_devices()
        SYSTEM_PROMPT = build_system_prompt(zones, devices)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
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

        rule = RuleObject(**parsed)
        return rule.model_dump()

    except Exception as e:
        logger.error(f"Interpreter failure: {str(e)}")
        return {"error": f"Internal parsing failure: {str(e)}"}