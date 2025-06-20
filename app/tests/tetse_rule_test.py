# Name: tetse_rule_test.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_rule_test.py
# Version: 0.1.0
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: CLI Test Harness for TETSE Rule Evaluation Engine

import asyncio
import logging

from routes.tetse_rule_engine import evaluate_house_exclusion_rule

# Setup basic console logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Sample test rule (adapt to your real test data)
sample_rule = {
    "entity_id": "Eddy",
    "zone": 422,
    "duration_sec": 600,  # 10 minutes
    "action": "alert",
    "conditions": {
        "exclude_parent_zone": 423
    }
}

async def main():
    print("----- Running TETSE Rule Engine Test -----")
    result = await evaluate_house_exclusion_rule(sample_rule)
    print("\n----- Rule Evaluation Result -----")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
