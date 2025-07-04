# Name: tetse_rule_loader.py
# Version: 0.1.1
# Created: 971201
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# TECHNICAL DEBT: zone 422 is hardcoded
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

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

import asyncio
import asyncpg
import json
import logging
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

# DB Connection using centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
data_config = db_configs['data']
DATA_CONN_STRING = f"postgresql://{data_config['user']}:{data_config['password']}@{server_host}:{data_config['port']}/{data_config['database']}"

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
                logger.info(f"Found {len(rows)} enabled rules in database")
                for row in rows:
                    try:
                        condition_data = row["conditions"]
                        if isinstance(condition_data, str):
                            condition_data = json.loads(condition_data)
                        
                        # Enhanced debug logging
                        logger.debug(f"Processing rule id={row['id']}, name={row['name']}")
                        logger.debug(f"Raw condition_data: {condition_data}")
                        logger.debug(f"Subject_id: {condition_data.get('subject_id')}")
                        logger.debug(f"Rule_type: {condition_data.get('rule_type', 'zone_stay')}")
                        
                        rule = parse_tetse_rule(row["id"], row["name"], condition_data)
                        
                        logger.debug(f"Parsed rule result: {rule is not None}")
                        if rule:
                            logger.debug(f"Successfully parsed rule: {rule}")
                            rules.append(rule)
                        else:
                            logger.warning(f"FAILED to parse rule id={row['id']}, name={row['name']}, skipping")
                            logger.warning(f"Failed rule condition_data was: {condition_data}")
                            
                    except Exception as e:
                        logger.error(f"Exception while parsing rule id={row['id']}: {str(e)}")
                        logger.error(f"Exception rule condition_data was: {condition_data}")
                        
                logger.info(f"Successfully parsed {len(rules)} out of {len(rows)} rules")
                        
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
    current_zone_id = 422  # Test zone
    campus_zone_id = 422   # Campus zone ID
    house_parent_zone_id = zone_id  # Use rule zone as house parent
    exclusion_duration_min = duration_sec // 60  # Convert seconds to minutes

    # Call function with correct parameters
    context = await get_house_exclusion_context(
        entity_id=subject_id,
        campus_zone_id=campus_zone_id,
        house_parent_zone_id=house_parent_zone_id,
        exclusion_duration_min=exclusion_duration_min,
        current_zone_id=current_zone_id
    )
    
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