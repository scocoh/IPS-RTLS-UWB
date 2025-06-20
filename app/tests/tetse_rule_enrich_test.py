# Name: tetse_rule_enrich_test.py
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

# File: tetse_rule_enrich_test.py
# Version: 0.1.0
# Created: 250615
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Test harness for TETSE Rule Enricher module
# Location: /home/parcoadmin/parco_fastapi/app/tests

import sys
import json
import asyncio
import logging
from routes.tetse_rule_enricher import enrich_rule

# Setup logging
logger = logging.getLogger("TETSE_ENRICH_TEST")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m routes.tetse_rule_enrich_test '<natural_language_prompt>'")
        sys.exit(1)

    user_input = sys.argv[1]
    logger.info("Submitting enrichment request...")

    rulebuilder_json = enrich_rule(user_input)
    
    print("\n----- Enriched RuleBuilder JSON -----")
    print(json.dumps(rulebuilder_json, indent=4))
    print("------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
