# Name: test_transition_rules_cli.py
# Version: 0.4.2
# Created: 250620
# Modified: 250621
# Creator: ParcoAdmin + Claude
# Description: Enhanced CLI test script for transition rule parsing with semantic zone mapping and device type support
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE
# 
# Version 0.4.2 - Updated for device type support and fixed rule type detection
# Previous: 0.3.1 - Fixed test cases and zone matching
# Previous: 0.2.0 - Enhanced with semantic zone mapping, real device validation, and trigger directions
# Previous: 0.1.0 - Basic zone transition rule parsing tests

import sys
import os
import asyncio
import json

# Add app/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.tetse_rule_interpreter import parse_natural_language

async def test_transition_rules():
    """Test both zone stay and zone transition rule parsing with enhanced semantic mapping"""
    
    test_cases = [
        {
            "input": "If 23001 stays in Living Room for 5 minutes then alert",
            "description": "Zone stay rule with semantic mapping (Living Room → Living Room RL6-Child)",
            "expected_type": "zone_stay"
        },
        {
            "input": "if tag 23001 moves from Living Room to outside send an alert",
            "description": "Semantic mapping: Living Room → Living Room RL6-Child",
            "expected_type": "zone_transition"
        },
        {
            "input": "alert when tag 23001 transitions from Kitchen to outside",
            "description": "Semantic mapping: Kitchen → Kitchen L6-Child",
            "expected_type": "zone_transition"
        },
        {
            "input": "if tag 23001 goes from outside to Bedroom log event",
            "description": "Semantic mapping: Bedroom → Master BR RL6-Child or similar",
            "expected_type": "zone_transition"
        },
        {
            "input": "when tag 23001 leaves Garage and enters Living Room send mqtt",
            "description": "Semantic room-to-room transition",
            "expected_type": "zone_transition"
        },
        {
            "input": "if tag 23001 moves from Bathroom to Kitchen send alert",
            "description": "Semantic mapping: Bathroom → M Bathroom L6-Child, Kitchen → Kitchen L6-Child",
            "expected_type": "zone_transition"
        },
        {
            "input": "if tag 23001 stays outside for 3 minutes alert",
            "description": "Virtual zone alias: outside",
            "expected_type": "zone_stay"
        }
    ]

    print("=" * 80)
    print("TESTING ENHANCED TETSE RULE INTERPRETER v0.4.2")
    print("Testing semantic zone mapping and device type support with real FastAPI endpoints:")
    print("✓ /api/zones_for_ai - Zone hierarchy")
    print("✓ /get_all_devices - Real device list") 
    print("✓ /list_trigger_directions - Trigger context")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: '{test['input']}'")
        print(f"Expected Type: {test['expected_type']}")
        print("-" * 40)
        
        try:
            result = await parse_natural_language(test['input'])
            
            if "error" in result:
                print(f"❌ ERROR: {result['error']}")
            else:
                actual_type = result.get('rule_type', 'unknown')
                if actual_type == test['expected_type']:
                    print(f"✅ SUCCESS: Correctly detected {actual_type} rule")
                else:
                    print(f"❌ TYPE MISMATCH: Expected {test['expected_type']}, got {actual_type}")
                
                print("Parsed Result:")
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Test completed. Check results above.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_transition_rules())