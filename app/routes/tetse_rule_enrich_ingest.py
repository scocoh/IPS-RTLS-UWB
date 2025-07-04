# Name: tetse_rule_enrich_ingest.py
# Version: 0.1.0
# Created: 971201
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_rule_enrich_ingest.py
# Version: 0.1.4
# Updated: 250704
# Author: ParcoAdmin + QuantumSage AI
# Purpose: End-to-end rule ingestion: NL -> Enrich -> Adapt -> Insert into TETSE

import sys
import asyncio
import json
from datetime import datetime, timezone
import asyncpg
from routes.tetse_rule_enricher import enrich_rule
from dotenv import load_dotenv
import os

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

# Load DB config from .env
load_dotenv("/home/parcoadmin/parco_fastapi/app/.env")

# Get centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']
data_config = db_configs['data']

MAINT_CONN_STRING = os.getenv("MAINT_CONN_STRING", f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}")
DATA_CONN_STRING = os.getenv("DATA_CONN_STRING", f"postgresql://{data_config['user']}:{data_config['password']}@{server_host}:{data_config['port']}/{data_config['database']}")

def adapt_rulebuilder_to_tetse(rule_dict):
    """
    Adapter to transform RuleBuilder format into TETSE DB format.
    """
    adapted = rule_dict.copy()

    # Map entity_id to subject_id if needed
    if "entity_id" in adapted:
        adapted["subject_id"] = adapted.pop("entity_id")

    # If conditions are missing, insert empty dict
    if "conditions" not in adapted:
        adapted["conditions"] = {}

    return adapted

async def insert_rule(adapted_rule: dict):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rule_name = f"TETSE Rule for {adapted_rule['subject_id']} {timestamp}"

    insert_sql = """
    INSERT INTO tlk_rules
    (name, is_enabled, priority, conditions, actions, created_at, updated_at, created_by, updated_by)
    VALUES
    ($1, $2, $3, $4, $5, now(), now(), $6, $7);
    """

    async with asyncpg.create_pool(DATA_CONN_STRING) as pool:
        async with pool.acquire() as conn:
            await conn.execute(
                insert_sql,
                rule_name,
                True,
                adapted_rule.get("priority", 1),
                json.dumps(adapted_rule),
                json.dumps({}),
                "parcoadmin",
                "parcoadmin"
            )
    print("✅ Rule inserted into tlk_rules.")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m routes.tetse_rule_enrich_ingest \"<natural language rule>\"")
        return

    nl_rule = sys.argv[1]
    print("Enriching rule...")
    enriched = enrich_rule(nl_rule)
    print("Enriched JSON:", json.dumps(enriched, indent=2))

    # Apply adapter here:
    adapted = adapt_rulebuilder_to_tetse(enriched["rule"])

    await insert_rule(adapted)

if __name__ == "__main__":
    asyncio.run(main())