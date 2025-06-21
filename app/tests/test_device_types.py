# Test script for device type functionality
import sys
import os
import asyncio
import json

# Add app/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.tetse_rule_interpreter import parse_natural_language

async def test_device_types():
    """Test device type functionality with various patterns"""
    
    test_cases = [
        {
            "input": "when any tag moves from inside to outside send an alert",
            "description": "Any tag transition (should work)",
            "expected_subject": "device_type:tag"
        },
        {
            "input": "if any tag stays outside for 5 minutes alert",
            "description": "Any tag zone stay (should work)",
            "expected_subject": "device_type:tag"
        },
        {
            "input": "alert when all tags move from Kitchen to Garage",
            "description": "All tags transition (debugging)",
            "expected_subject": "device_type:tag"
        },
        {
            "input": "when all tags transition from Living Room to outside send mqtt",
            "description": "All tags with different zones",
            "expected_subject": "device_type:tag"
        },
        {
            "input": "if tags move from outside to inside log event",
            "description": "Just 'tags' (no 'any' or 'all')",
            "expected_subject": "device_type:tag"
        },
        {
            "input": "alert when any device moves from Living Room to Kitchen",
            "description": "Any device (not just tags)",
            "expected_subject": "device_type:any"
        },
        {
            "input": "when tag 23001 moves from Kitchen to Garage send alert",
            "description": "Specific tag (should still work)",
            "expected_subject": "23001"
        }
    ]

    print("=" * 80)
    print("TESTING DEVICE TYPE FUNCTIONALITY v0.4.0")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: '{test['input']}'")
        print(f"Expected subject_id: {test['expected_subject']}")
        print("-" * 40)
        
        try:
            result = await parse_natural_language(test['input'])
            
            if "error" in result:
                print(f"❌ ERROR: {result['error']}")
            else:
                actual_subject = result.get('subject_id', 'unknown')
                if actual_subject == test['expected_subject']:
                    print(f"✅ SUCCESS: Correctly parsed subject_id")
                else:
                    print(f"⚠️  PARTIAL: Got subject_id '{actual_subject}', expected '{test['expected_subject']}'")
                
                print("Parsed Result:")
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Test completed. Check results above.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_device_types())