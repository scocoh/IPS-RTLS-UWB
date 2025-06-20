# Name: tetse_enrich_parse_test.py
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

# File: tests/tetse_enrich_parse_test.py
# Version: 0.1.0
# Phase 11.8 — Full Enrich+Parse Pipeline Test

import sys
import asyncio
import json
from routes.tetse_rule_enricher import enrich_rule
from routes.tetse_rule_parser import parse_rule

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m tests.tetse_enrich_parse_test 'Your rule sentence here'")
        return

    user_input = sys.argv[1]
    print("----- Enrichment -----")
    enriched = enrich_rule(user_input)
    print(json.dumps(enriched, indent=2))

    print("----- Parse -----")
    parsed = parse_rule(enriched)
    print(json.dumps(parsed, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
