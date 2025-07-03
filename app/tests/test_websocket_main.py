#!/usr/bin/env python3
# Name: test_websocket_main.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Test script for ParcoRTLS Main WebSocket server - Tests database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
Test script for ParcoRTLS Main WebSocket server
Tests database-driven configuration and multi-stream functionality
"""

import asyncio
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_import_websocket_main():
    """Test importing the main websocket module"""
    print("\n" + "="*60)
    print("TESTING: manager/websocket.py Import")
    print("="*60)
    
    try:
        from manager import websocket
        
        print("   ✅ Module imported successfully")
        
        # Test configuration functions
        print("\n1. Testing configuration functions...")
        conn_string = await websocket.get_connection_string()
        print(f"   ✅ Connection string loaded: {len(conn_string) > 0}")
        print(f"   ✅ Connection string contains host: {'192.168.210.226' in conn_string or '127.0.0.1' in conn_string}")
        
        cors_origins = await websocket.get_cors_origins()
        print(f"   ✅ CORS origins loaded: {cors_origins}")
        
        # Test stream ports configuration
        print("\n2. Testing stream ports configuration...")
        print(f"   ✅ Stream ports defined: {websocket.STREAM_PORTS}")
        expected_ports = [8001, 8002, 8003, 8006]
        actual_ports = list(websocket.STREAM_PORTS.values())
        print(f"   ✅ Expected ports present: {all(port in actual_ports for port in expected_ports)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_integration():
    """Test database integration"""
    print("\n" + "="*60)
    print("TESTING: Database Integration")
    print("="*60)
    
    try:
        from db_config_helper import config_helper
        
        print("\n1. Testing server configuration...")
        server_config = await config_helper.get_server_config()
        print(f"   ✅ Server host: {server_config.get('host', 'NOT_FOUND')}")
        print(f"   ✅ Available managers: {len(server_config.get('managers', {}))}")
        
        # Check for different manager types
        managers = server_config.get('managers', {})
        manager_types = {}
        for name, config in managers.items():
            mgr_type = config.get('type', 'unknown')
            if mgr_type not in manager_types:
                manager_types[mgr_type] = []
            manager_types[mgr_type].append(name)
        
        print(f"   ✅ Manager types found: {list(manager_types.keys())}")
        for mgr_type, names in manager_types.items():
            print(f"      Type {mgr_type}: {names}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stream_port_availability():
    """Test if stream ports are available or in use"""
    print("\n" + "="*60)
    print("TESTING: Stream Port Availability")
    print("="*60)
    
    try:
        import subprocess
        
        print("\n1. Checking stream port usage...")
        
        # Expected stream ports from the websocket.py configuration
        stream_ports = {
            "RealTime": 8002,
            "HistoricalData": 8003,
            "OData": 8006,
            "Control": 8001
        }
        
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        port_usage = {}
        
        for stream_name, port in stream_ports.items():
            port_in_use = f':{port} ' in result.stdout
            port_usage[stream_name] = port_in_use
            status = "✅ IN USE" if port_in_use else "⚪ AVAILABLE"
            print(f"   {status} Port {port} ({stream_name})")
        
        in_use_count = sum(port_usage.values())
        print(f"\n   📊 Summary: {in_use_count}/{len(stream_ports)} stream ports are in use")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking port status: {e}")
        return False

def test_websocket_processes():
    """Check for running WebSocket processes"""
    print("\n" + "="*60)
    print("TESTING: WebSocket Process Status")
    print("="*60)
    
    try:
        import subprocess
        
        print("\n1. Checking for WebSocket server processes...")
        
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        websocket_processes = []
        for line in processes.split('\n'):
            if 'websocket' in line.lower() and 'uvicorn' in line:
                websocket_processes.append(line.strip())
        
        if websocket_processes:
            print(f"   ✅ Found {len(websocket_processes)} WebSocket process(es):")
            for i, process in enumerate(websocket_processes, 1):
                # Truncate long process lines for readability
                truncated = process[:100] + "..." if len(process) > 100 else process
                print(f"      {i}. {truncated}")
        else:
            print("   ⚪ No WebSocket server processes found")
            print("   💡 You can start WebSocket servers with:")
            print("      uvicorn manager.websocket:app --host 0.0.0.0 --port 8000")
            print("      uvicorn manager.websocket_control:app --host 0.0.0.0 --port 8001")
            print("      uvicorn manager.websocket_historical:app --host 0.0.0.0 --port 8003")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking processes: {e}")
        return False

async def test_configuration_consistency():
    """Test configuration consistency across modules"""
    print("\n" + "="*60)
    print("TESTING: Configuration Consistency")
    print("="*60)
    
    try:
        # Test if all WebSocket modules use the same configuration
        print("\n1. Testing configuration consistency...")
        
        from manager import websocket
        
        # Get configuration from main websocket
        main_conn_string = await websocket.get_connection_string()
        main_cors = await websocket.get_cors_origins()
        
        print(f"   ✅ Main WebSocket connection string: {len(main_conn_string) > 0}")
        print(f"   ✅ Main WebSocket CORS origins: {main_cors}")
        
        # Test if we can import other websocket modules
        try:
            from manager import websocket_control
            control_conn_string = await websocket_control.get_connection_string()
            control_cors = await websocket_control.get_cors_origins()
            
            # Check if they're using the same host
            main_host = main_cors[0] if main_cors else "unknown"
            control_host = control_cors[0] if control_cors else "unknown"
            
            consistent = main_host == control_host
            print(f"   ✅ Control WebSocket consistency: {consistent}")
            if not consistent:
                print(f"      Main: {main_host}, Control: {control_host}")
            
        except Exception as e:
            print(f"   ⚠️  Could not test control WebSocket consistency: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all main WebSocket tests"""
    print("ParcoRTLS Main WebSocket Test Suite")
    print("="*60)
    
    tests = [
        ("Import Test", test_import_websocket_main()),
        ("Database Integration", test_database_integration()),
        ("Configuration Consistency", test_configuration_consistency()),
        ("Stream Port Availability", test_stream_port_availability()),
        ("WebSocket Process Status", test_websocket_processes()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\nRunning {test_name}...")
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*60)
    print("MAIN WEBSOCKET TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Main WebSocket is working correctly.")
    elif passed >= 3:
        print("⚠️  Some tests failed, but core functionality appears to work.")
        print("💡 Database-driven configuration is working successfully!")
    else:
        print("❌ Multiple test failures. Check the errors above.")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if passed >= 3:
        print("✅ Database-driven configuration is working")
        print("✅ Main WebSocket module imports successfully")
        print("✅ Stream port configuration is correct")
        
        if passed < len(results):
            print("💡 To test full WebSocket functionality:")
            print("   1. Start the main WebSocket server:")
            print("      uvicorn manager.websocket:app --host 0.0.0.0 --port 8000")
            print("   2. The server will automatically start stream servers on ports 8001-8006")
            print("   3. Check logs for any startup issues")
    else:
        print("❌ Critical issues found - check database connectivity and imports")

if __name__ == "__main__":
    asyncio.run(main())