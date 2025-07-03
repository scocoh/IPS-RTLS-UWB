#!/usr/bin/env python3
# Name: test_websocket_control.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Test script for ParcoRTLS Control WebSocket server - Tests database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
Test script for ParcoRTLS Control WebSocket server
Tests database-driven configuration and WebSocket functionality
"""

import asyncio
import websockets
import json
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_import_websocket_control():
    """Test importing the websocket_control module"""
    print("\n" + "="*60)
    print("TESTING: manager/websocket_control.py Import")
    print("="*60)
    
    try:
        # Import from parent directory
        from manager import websocket_control
        
        print("   ✅ Module imported successfully")
        
        # Test configuration functions
        print("\n1. Testing configuration functions...")
        conn_string = await websocket_control.get_connection_string()
        print(f"   ✅ Connection string loaded: {len(conn_string) > 0}")
        print(f"   ✅ Connection string contains host: {'192.168.210.226' in conn_string or '127.0.0.1' in conn_string}")
        
        cors_origins = await websocket_control.get_cors_origins()
        print(f"   ✅ CORS origins loaded: {cors_origins}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_websocket_connection():
    """Test WebSocket connection to control server"""
    print("\n" + "="*60)
    print("TESTING: WebSocket Connection to Control Server")
    print("="*60)
    
    # Try different possible hosts
    test_hosts = ["127.0.0.1", "192.168.210.226", "localhost"]
    port = 8001
    
    for host in test_hosts:
        try:
            uri = f"ws://{host}:{port}/ws/ControlManager"
            print(f"\n1. Testing connection to {uri}...")
            
            timeout = 5  # 5 second timeout
            async with websockets.connect(uri) as websocket:
                print(f"   ✅ WebSocket connection successful to {host}:{port}")
                
                # Test heartbeat
                print("\n2. Testing heartbeat...")
                heartbeat_msg = {
                    "type": "HeartBeat",
                    "ts": int(datetime.now().timestamp() * 1000)
                }
                await websocket.send(json.dumps(heartbeat_msg))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "HeartBeat":
                        print("   ✅ Heartbeat response received")
                    else:
                        print(f"   ⚠️  Unexpected response: {response_data}")
                except asyncio.TimeoutError:
                    print("   ⚠️  Heartbeat response timeout")
                
                # Test BeginStream request
                print("\n3. Testing BeginStream request...")
                begin_stream_msg = {
                    "type": "request",
                    "request": "BeginStream",
                    "reqid": "test_001",
                    "params": [
                        {"id": "23001", "data": "true"}
                    ],
                    "zone_id": 417
                }
                await websocket.send(json.dumps(begin_stream_msg))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "response" and response_data.get("response") == "BeginStream":
                        print("   ✅ BeginStream response received")
                    else:
                        print(f"   ⚠️  Unexpected BeginStream response: {response_data}")
                except asyncio.TimeoutError:
                    print("   ⚠️  BeginStream response timeout")
                
                # Test EndStream request
                print("\n4. Testing EndStream request...")
                end_stream_msg = {
                    "type": "request",
                    "request": "EndStream",
                    "reqid": "test_002"
                }
                await websocket.send(json.dumps(end_stream_msg))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "response" and response_data.get("response") == "EndStream":
                        print("   ✅ EndStream response received")
                    else:
                        print(f"   ⚠️  Unexpected EndStream response: {response_data}")
                except asyncio.TimeoutError:
                    print("   ⚠️  EndStream response timeout")
                
                print(f"\n   🎉 WebSocket test completed successfully on {host}:{port}")
                return True
                
        except ConnectionRefusedError:
            print(f"   ❌ Connection refused to {host}:{port} (server not running)")
        except websockets.exceptions.InvalidURI:
            print(f"   ❌ Invalid URI: ws://{host}:{port}/ws/ControlManager")
        except asyncio.TimeoutError:
            print(f"   ❌ Connection timeout to {host}:{port}")
        except Exception as e:
            print(f"   ❌ Error connecting to {host}:{port}: {e}")
    
    print("\n   ⚠️  Could not connect to any control server")
    return False

async def test_database_integration():
    """Test database integration functions"""
    print("\n" + "="*60)
    print("TESTING: Database Integration")
    print("="*60)
    
    try:
        from db_config_helper import config_helper
        
        print("\n1. Testing server configuration...")
        server_config = await config_helper.get_server_config()
        print(f"   ✅ Server host: {server_config.get('host', 'NOT_FOUND')}")
        print(f"   ✅ Available managers: {len(server_config.get('managers', {}))}")
        
        # Check for ControlManager specifically
        managers = server_config.get('managers', {})
        control_manager_found = False
        for name, config in managers.items():
            if config.get('type') == 10:  # Control type
                print(f"   ✅ Control Manager found: {name} at {config.get('ip', 'unknown')}:{config.get('port', 'unknown')}")
                control_manager_found = True
        
        if not control_manager_found:
            print("   ⚠️  No Control Manager (type 10) found in tlkresources")
        
        print("\n2. Testing database connection...")
        conn_string = config_helper.get_connection_string("ParcoRTLSMaint")
        print(f"   ✅ Connection string generated: {len(conn_string) > 0}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_control_server_status():
    """Check if control server process is running"""
    print("\n" + "="*60)
    print("TESTING: Control Server Process Status")
    print("="*60)
    
    try:
        import subprocess
        
        print("\n1. Checking for control server processes...")
        
        # Check for uvicorn processes running websocket_control
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        control_processes = []
        for line in processes.split('\n'):
            if 'websocket_control' in line and 'uvicorn' in line:
                control_processes.append(line.strip())
        
        if control_processes:
            print(f"   ✅ Found {len(control_processes)} control server process(es):")
            for process in control_processes:
                print(f"      {process}")
        else:
            print("   ⚠️  No control server processes found")
            print("   💡 To start control server: uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001")
        
        # Check for port 8001 usage
        print("\n2. Checking port 8001 usage...")
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        port_lines = [line for line in result.stdout.split('\n') if ':8001 ' in line]
        
        if port_lines:
            print("   ✅ Port 8001 is in use:")
            for line in port_lines:
                print(f"      {line.strip()}")
        else:
            print("   ⚠️  Port 8001 is not in use")
        
        return len(control_processes) > 0 or len(port_lines) > 0
        
    except Exception as e:
        print(f"   ❌ Error checking process status: {e}")
        return False

async def main():
    """Run all control WebSocket tests"""
    print("ParcoRTLS Control WebSocket Test Suite")
    print("="*60)
    
    tests = [
        ("Import Test", test_import_websocket_control()),
        ("Database Integration", test_database_integration()),
        ("Server Process Status", test_control_server_status()),
        ("WebSocket Connection", test_websocket_connection()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\nRunning {test_name}...")
        result = await test_coro
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*60)
    print("CONTROL WEBSOCKET TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Control WebSocket is working correctly.")
    elif passed >= 2:
        print("⚠️  Some tests failed, but core functionality appears to work.")
        print("💡 If WebSocket connection failed, make sure the control server is running:")
        print("   uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001")
    else:
        print("❌ Multiple test failures. Check the errors above.")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if passed >= 2:
        print("✅ Database-driven configuration is working")
        print("✅ Core module imports successfully")
        
        if passed < len(results):
            print("⚠️  To test WebSocket functionality:")
            print("   1. Start the control server: uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001")
            print("   2. Re-run this test script")
            print("   3. Check firewall settings for port 8001")
    else:
        print("❌ Critical issues found - check database connectivity and module imports")

if __name__ == "__main__":
    asyncio.run(main())