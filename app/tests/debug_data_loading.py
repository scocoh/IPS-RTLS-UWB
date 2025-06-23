# Name: debug_data_loading.py
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

# Debug script to check what data is being loaded
import sys
import os
import asyncio
import json
import aiohttp

# Add app/ to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def debug_data_loading():
    """Debug what data is actually being loaded from the FastAPI endpoints"""
    
    print("=" * 80)
    print("DEBUGGING DATA LOADING FOR TETSE RULE INTERPRETER")
    print("=" * 80)
    
    # Test zones endpoint
    print("\n1. Testing /api/zones_for_ai endpoint:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/zones_for_ai") as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    zones = data.get("zones", [])
                    print(f"   Zones found: {len(zones)}")
                    if zones:
                        print("   First 5 zones:")
                        for i, zone in enumerate(zones[:5]):
                            print(f"     {i+1}. {zone}")
                        # Look for Living Room specifically
                        living_rooms = [z for z in zones if 'living room' in z.get('name', '').lower()]
                        if living_rooms:
                            print(f"   Living Room zones found: {living_rooms}")
                        else:
                            print("   No Living Room zones found")
                    else:
                        print("   No zones in response")
                else:
                    print(f"   Error: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Test devices endpoint  
    print("\n2. Testing /api/get_all_devices endpoint:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/get_all_devices") as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    devices = await resp.json()
                    print(f"   Devices found: {len(devices)}")
                    if devices:
                        print("   First 5 devices:")
                        for i, device in enumerate(devices[:5]):
                            print(f"     {i+1}. {device}")
                        # Look for device 23001 specifically
                        device_23001 = [d for d in devices if d.get('x_id_dev') == '23001']
                        if device_23001:
                            print(f"   Device 23001 found: {device_23001}")
                        else:
                            print("   Device 23001 NOT found")
                            # Show available device IDs
                            device_ids = [d.get('x_id_dev') for d in devices[:10]]
                            print(f"   Sample device IDs: {device_ids}")
                    else:
                        print("   No devices in response")
                else:
                    print(f"   Error: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Test trigger directions endpoint
    print("\n3. Testing /api/list_trigger_directions endpoint:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/list_trigger_directions") as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    directions = await resp.json()
                    print(f"   Trigger directions found: {len(directions)}")
                    if directions:
                        print("   Trigger directions:")
                        for direction in directions:
                            print(f"     {direction}")
                    else:
                        print("   No directions in response")
                else:
                    print(f"   Error: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Debug completed. Check results above.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(debug_data_loading())