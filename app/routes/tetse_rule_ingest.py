# Name: tetse_rule_ingest.py
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

# File: tetse_rule_ingest.py
# Version: 0.3.0
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: CLI utility to ingest RuleBuilder rules into TETSE tlk_rules with unique rule names
# Location: /home/parcoadmin/parco_fastapi/app/routes/

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

import json
import asyncio
import asyncpg
import logging
from datetime import datetime
from routes.tetse_rule_adapter import adapt_rulebuilder_to_tetse

# Database connection using centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
data_config = db_configs['data']
maint_config = db_configs['maint']
DATA_CONN_STRING = f"postgresql://{data_config['user']}:{data_config['password']}@{server_host}:{data_config['port']}/{data_config['database']}"
MAINT_CONN_STRING = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"

# Setup logging
logger = logging.getLogger("TETSE_INGEST")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

async def insert_tetse_rule(adapted_rule: dict):
    """
    Insert adapted rule into tlk_rules with unique name.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    rule_name = f"TETSE Rule for {adapted_rule['subject_id']} {timestamp}"

    async with asyncpg.create_pool(DATA_CONN_STRING) as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tlk_rules (name, is_enabled, priority, conditions, actions, created_at, updated_at, created_by, updated_by)
                VALUES ($1, $2, $3, $4, $5, now(), now(), $6, $7)
            """,
            rule_name,
            True,  # is_enabled
            adapted_rule.get("priority", 1),
            json.dumps(adapted_rule),
            json.dumps({}),
            "parcoadmin",
            "parcoadmin"
            )

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m routes.tetse_rule_ingest '<JSON_STRING>'")
        sys.exit(1)

    raw_json = sys.argv[1]
    logger.info("Parsing RuleBuilder JSON input...")

    try:
        rulebuilder_data = json.loads(raw_json)
        
        # Create database pools for the adapter function
        data_pool = await asyncpg.create_pool(DATA_CONN_STRING)
        maint_pool = await asyncpg.create_pool(MAINT_CONN_STRING)
        
        # Get campus_id from rule data or use default
        campus_id = rulebuilder_data.get("campus_id", "422")  # Default campus
        
        # Call adapter with required parameters
        adapted_rule = await adapt_rulebuilder_to_tetse(
            rule_data=rulebuilder_data,
            campus_id=campus_id,
            pool=data_pool,
            maint_pool=maint_pool
        )
        
        logger.info(f"Adapted Rule: {adapted_rule}")
        await insert_tetse_rule(adapted_rule)
        logger.info("✅ Rule successfully inserted into tlk_rules.")
        
        # Close pools
        await data_pool.close()
        await maint_pool.close()

    except Exception as e:
        logger.error(f"Error processing rule: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())