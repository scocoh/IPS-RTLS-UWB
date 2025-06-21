# Debug script to see exactly what GPT is receiving and outputting
import sys
import os
import asyncio
import json

# Add app/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.tetse_rule_interpreter import (
    get_live_zones, get_live_devices, get_live_device_types, 
    get_live_trigger_directions, build_zone_transition_prompt_with_types,
    detect_rule_type
)

async def debug_gpt_interaction():
    """Debug what GPT is actually receiving for problematic cases"""
    
    # Test the failing case
    input_text = "alert when all tags move from Kitchen to Garage"
    
    print("=" * 80)
    print(f"DEBUGGING GPT INTERACTION FOR: '{input_text}'")
    print("=" * 80)
    
    # Get the same data the interpreter uses
    zones = await get_live_zones()
    devices = await get_live_devices()
    device_types = await get_live_device_types()
    trigger_directions = await get_live_trigger_directions()
    
    rule_type = detect_rule_type(input_text)
    print(f"Detected rule type: {rule_type}")
    
    # Build the exact prompt GPT receives
    system_prompt = build_zone_transition_prompt_with_types(zones, devices, device_types, trigger_directions)
    
    print("\n" + "=" * 40)
    print("SYSTEM PROMPT (first 1000 chars):")
    print("=" * 40)
    print(system_prompt[:1000] + "...")
    
    print("\n" + "=" * 40)
    print("LOOKING FOR DEVICE TYPE PATTERNS IN PROMPT:")
    print("=" * 40)
    
    # Check if device type patterns are in the prompt
    patterns_to_check = ['"all tags"', '"tags"', 'device_type:tag', 'Tag device types']
    for pattern in patterns_to_check:
        if pattern in system_prompt:
            print(f"✅ Found: {pattern}")
        else:
            print(f"❌ Missing: {pattern}")
    
    print("\n" + "=" * 40)
    print("DEVICE TYPES LOADED:")
    print("=" * 40)
    for dt in device_types:
        print(f"Type {dt['i_typ_dev']}: {dt['x_dsc_dev']}")
    
    print("\n" + "=" * 40)
    print("ZONE SAMPLES (Kitchen/Garage):")
    print("=" * 40)
    kitchen_zones = [z for z in zones if 'kitchen' in z['name'].lower()]
    garage_zones = [z for z in zones if 'garage' in z['name'].lower()]
    print(f"Kitchen zones: {kitchen_zones}")
    print(f"Garage zones: {garage_zones}")
    
    print("\n" + "=" * 80)
    print("Debug completed.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(debug_gpt_interaction())