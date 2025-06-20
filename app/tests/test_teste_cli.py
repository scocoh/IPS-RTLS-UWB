# Name: test_teste_cli.py
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

# File: test_tetse_cli.py
# Version: 0.2.4
# Created: 250616
# Updated: 250617
# Author: ParcoAdmin + AI Assistant
# Purpose: Test TETSE rule interpreter CLI
# Update: Created to test subject_id parsing, includes valid tag 23001

import sys
import os
import asyncio
import json

# Add app/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.tetse_rule_interpreter import parse_natural_language

async def test():
    tests = [
        {
            "input": "If Eddy stays in 6005BOL2-Child for 5 minutes then alert",
            "description": "Invalid subject (Eddy)"
        },
        {
            "input": "If 23001 stays in 6005BOL2-Child for 5 minutes then alert",
            "description": "Valid tag 23001"
        }
    ]

    for test in tests:
        print(f"\nTesting: {test['description']}")
        print(f"Input: {test['input']}")
        result = await parse_natural_language(test['input'])
        print("Result:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
