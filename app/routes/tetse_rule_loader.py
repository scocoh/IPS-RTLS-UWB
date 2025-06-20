# Name: tetse_rule_loader.py
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

# File: tetse_rule_loader.py
# Version: 0.3.4
# Created: 250615
# Modified: 250617
# Refactor: 250616 (Phase 11.9.3 Circular Isolation Recovery)
# Author: ParcoAdmin
# Modified By: AI Assistant
# Purpose: Load TETSE rules from tlk_rules and evaluate against sample context
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Update: Filtered None rules, fixed import; bumped from 0.3.3

import asyncio
import asyncpg
import json
import logging
import os
from fastapi import APIRouter
from routes.temporal_context import get_house_exclusion_context
from routes.tetse_zone_utils import get_zone_descendants_raw
from routes.tetse_rule_parser import parse_tetse_rule
from .tetse_zone_map import load_zone_map
from logging.handlers import RotatingFileHandler

router = APIRouter()

# Setup logging
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("TETSE_RULE_LOADER")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "tetse_rule_loader.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

# DB Connection
DATA_CONN_STRING = os.getenv("DATA_CONN_STRING", "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData")

async def preload_rules():
    """
    Load all enabled rules from tlk_rules table.
    """
    query = "SELECT id, name, conditions FROM tlk_rules WHERE is_enabled = TRUE"
    rules = []
    try:
        async with asyncpg.create_pool(DATA_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(query)
                for row in rows:
                    try:
                        condition_data = row["conditions"]
                        if isinstance(condition_data, str):
                            condition_data = json.loads(condition_data)
                        rule = parse_tetse_rule(row["id"], row["name"], condition_data)
                        if rule:
                            rules.append(rule)
                        else:
                            logger.warning(f"Skipped invalid rule id={row['id']}")
                    except Exception as e:
                        logger.error(f"Failed to parse rule id={row['id']}: {str(e)}")
    except Exception as e:
        logger.error(f"Database load failed: {str(e)}")
    return rules

async def evaluate_house_exclusion_rule(rule):
    """
    Run house exclusion logic for testing purposes.
    """
    subject_id = rule["subject_id"]
    zone_id = rule["zone"]
    duration_sec = rule.get("duration_sec", 600)
    exclude_parent_zone = rule.get("exclude_parent_zone")

    # Simulate entity status
    entity_status = {
        "current_zone_id": 422,
        "timestamp": "2025-06-16T03:25:00Z"
    }

    # Build context request
    context_request = {
        "subject_id": subject_id,
        "zone": zone_id,
        "duration_sec": duration_sec,
        "exclude_parent_zone": exclude_parent_zone,
        "entity_status": entity_status
    }

    context = await get_house_exclusion_context(context_request)
    triggered = context["status"] == "OUTSIDE_THRESHOLD"
    logger.debug(f"Rule evaluation complete for subject {subject_id}: triggered={triggered}, context={context}")
    return {"triggered": triggered, "status": context["status"], "details": context}

async def main():
    logger.info("----- TETSE Rule Loader (Schema Locked) -----")
    rules = await preload_rules()
    for rule in rules:
        logger.info(f"\n--- Evaluating Rule: {rule['name']} (ID {rule['id']}) ---")
        result = await evaluate_house_exclusion_rule(rule)
        logger.info(f"Evaluation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

@router.post("/tetse/reload_rules")
async def api_reload_rules():
    """
    API endpoint to reload rules on demand.
    """
    try:
        await load_zone_map()
        rules = await preload_rules()
        logger.info(f"Reloaded {len(rules)} rules via API")
        return {"status": "success", "message": f"Reloaded {len(rules)} rules"}
    except Exception as e:
        logger.error(f"Failed to reload rules via API: {str(e)}")
        return {"status": "error", "message": str(e)}
