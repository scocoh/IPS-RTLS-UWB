# Name: tetse_realtime_loop.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_realtime_loop.py
# Version: 0.3.0 (Phase 6A Realtime Loop Prototype)
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Wire rule loader + subject registry into real-time rule evaluation loop.
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Status: CLI-safe test harness for Phase 6 integration

import asyncio
import asyncpg
import json
import logging

from routes.tetse_rule_engine import evaluate_house_exclusion_rule
from routes.subject_registry import get_subject_current_zone

# Setup logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Postgres connection string for ParcoRTLSData
DATA_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData"

async def preload_rules():
    """
    Load all TETSE rules into memory at startup (fully schema-locked).
    """
    try:
        async with asyncpg.create_pool(DATA_CONN_STRING) as pool:
            async with pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, name, conditions
                    FROM tlk_rules
                    WHERE is_enabled = TRUE
                    ORDER BY id;
                """)

        rules = []
        for row in results:
            try:
                conditions = json.loads(row['conditions'])
                rule = {
                    "id": row['id'],
                    "name": row['name'],
                    "subject_id": conditions["subject_id"],
                    "zone": int(conditions["zone"]),
                    "duration_sec": int(conditions["duration_sec"]),
                    "conditions": {
                        "exclude_parent_zone": int(conditions["conditions"]["exclude_parent_zone"])
                    }
                }
                rules.append(rule)
            except Exception as parse_error:
                logging.error(f"Failed to parse rule id={row['id']}: {str(parse_error)}")

        return rules

    except Exception as db_error:
        logging.error(f"Database error during rule preload: {str(db_error)}")
        return []

async def realtime_evaluate(subject_id: str, all_rules: list):
    """
    Called upon simulated live event for subject_id.
    Filters relevant rules and evaluates them.
    """
    matching_rules = [rule for rule in all_rules if rule["subject_id"] == subject_id]

    if not matching_rules:
        logging.info(f"No rules applicable for subject_id: {subject_id}")
        return

    for rule in matching_rules:
        result = await evaluate_house_exclusion_rule(rule)
        print(f"Subject: {subject_id} | Rule: {rule['name']} | Evaluation: {result}")

async def main():
    print("----- TETSE Real-Time Loop Test -----")

    # Preload all rules into memory at startup
    all_rules = await preload_rules()
    print(f"Preloaded {len(all_rules)} TETSE rules.")

    # Simulated incoming live event:
    test_subject = "Eddy"

    # Call evaluation on simulated live event
    await realtime_evaluate(test_subject, all_rules)

if __name__ == "__main__":
    asyncio.run(main())
