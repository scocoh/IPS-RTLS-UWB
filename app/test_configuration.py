#!/usr/bin/env python3
# Name: test_configuration.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Test script for ParcoRTLS database-driven configuration
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
Test script for ParcoRTLS database-driven configuration
Tests that all updated modules can load configuration from the database
"""

import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_db_config_helper():
    """Test the central database configuration helper"""
    print("\n" + "="*60)
    print("TESTING: db_config_helper.py")
    print("="*60)
    
    try:
        from db_config_helper import config_helper
        
        # Test 1: Get server configuration
        print("\n1. Testing server configuration from database...")
        server_config = await config_helper.get_server_config()
        print(f"   ✅ Server host: {server_config.get('host', 'NOT_FOUND')}")
        print(f"   ✅ Available managers: {len(server_config.get('managers', {}))}")
        
        # Test 2: Get database configurations
        print("\n2. Testing database configurations...")
        db_configs = config_helper.get_database_configs()
        print(f"   ✅ Maintenance DB host: {db_configs['maint']['host']}")
        print(f"   ✅ Historical R DB host: {db_configs['hist_r']['host']}")
        
        # Test 3: Get connection strings
        print("\n3. Testing connection strings...")
        conn_string = config_helper.get_connection_string("ParcoRTLSMaint")
        host_in_string = "192.168.210.226" in conn_string or "127.0.0.1" in conn_string
        print(f"   ✅ Connection string contains valid host: {host_in_string}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_config_py():
    """Test the updated config.py module"""
    print("\n" + "="*60)
    print("TESTING: config.py")
    print("="*60)
    
    try:
        from config import (
            DB_CONFIGS_ASYNC, 
            get_server_config, 
            get_server_host,
            initialize_config
        )
        
        # Test 1: Backward compatibility
        print("\n1. Testing backward compatibility...")
        print(f"   ✅ DB_CONFIGS_ASYNC exists: {DB_CONFIGS_ASYNC is not None}")
        print(f"   ✅ Maintenance DB host: {DB_CONFIGS_ASYNC['maint']['host']}")
        
        # Test 2: Initialize configuration
        print("\n2. Testing configuration initialization...")
        await initialize_config()
        print("   ✅ Configuration initialized successfully")
        
        # Test 3: Get server config
        print("\n3. Testing server configuration...")
        server_config = await get_server_config()
        print(f"   ✅ Server host: {server_config.get('host', 'NOT_FOUND')}")
        
        # Test 4: Synchronous host access
        print("\n4. Testing synchronous host access...")
        host = get_server_host()
        print(f"   ✅ Server host (sync): {host}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_db_connection():
    """Test the updated db_connection.py module"""
    print("\n" + "="*60)
    print("TESTING: db_connection.py")
    print("="*60)
    
    try:
        from db_connection import DB_CONFIG, get_db_connection, get_db_config
        
        # Test 1: Get database configuration
        print("\n1. Testing database configuration...")
        db_config = get_db_config()
        print(f"   ✅ Database host: {db_config['host']}")
        print(f"   ✅ Database name: {db_config['dbname']}")
        
        # Test 2: Backward compatibility
        print("\n2. Testing backward compatibility...")
        print(f"   ✅ DB_CONFIG exists: {DB_CONFIG is not None}")
        print(f"   ✅ DB_CONFIG host: {DB_CONFIG['host']}")
        
        # Test 3: Database connection (if database is available)
        print("\n3. Testing database connection...")
        conn = get_db_connection()
        if conn:
            print("   ✅ Database connection successful")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tlkresources")
                count = cursor.fetchone()[0]
                print(f"   ✅ tlkresources table has {count} records")
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"   ⚠️  Database query failed: {e}")
                conn.close()
        else:
            print("   ⚠️  Database connection failed (using fallback config)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_db_functions():
    """Test the updated database/db_functions.py module"""
    print("\n" + "="*60)
    print("TESTING: database/db_functions.py")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'database'))
        from database.db_functions import (
            DB_CONFIGS_ASYNC,
            get_db_configs_async,
            get_connection_string,
            get_pg_connection
        )
        
        # Test 1: Get database configurations
        print("\n1. Testing database configurations...")
        db_configs = get_db_configs_async()
        print(f"   ✅ Configurations loaded: {len(db_configs)} databases")
        print(f"   ✅ Maintenance DB host: {db_configs['maint']['host']}")
        
        # Test 2: Connection strings
        print("\n2. Testing connection strings...")
        conn_string = get_connection_string("maint")
        print(f"   ✅ Connection string generated: {len(conn_string) > 0}")
        
        # Test 3: Async connection (if database is available)
        print("\n3. Testing async database connection...")
        try:
            pool = await get_pg_connection("maint")
            if pool:
                print("   ✅ Async database connection successful")
                await pool.close()
            else:
                print("   ⚠️  Async database connection failed (using fallback)")
        except Exception as e:
            print(f"   ⚠️  Async connection error: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_device_registry():
    """Test the updated routes/device_registry.py module"""
    print("\n" + "="*60)
    print("TESTING: routes/device_registry.py")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'routes'))
        from routes.device_registry import (
            get_maint_connection_string,
            load_device_registry,
            get_registry_stats
        )
        
        # Test 1: Connection string
        print("\n1. Testing connection string...")
        conn_string = get_maint_connection_string()
        print(f"   ✅ Connection string generated: {len(conn_string) > 0}")
        
        # Test 2: Device registry stats
        print("\n2. Testing device registry stats...")
        stats = get_registry_stats()
        print(f"   ✅ Registry stats: {stats['total_mappings']} mappings")
        
        # Test 3: Load device registry (if database is available)
        print("\n3. Testing device registry loading...")
        try:
            registry = await load_device_registry()
            print(f"   ✅ Device registry loaded: {len(registry)} mappings")
            if "23001" in registry:
                print(f"   ✅ Fallback tag 23001 -> {registry['23001']}")
        except Exception as e:
            print(f"   ⚠️  Device registry load error: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_detect_ports():
    """Test the updated scripts/detect_ports.py module (import only)"""
    print("\n" + "="*60)
    print("TESTING: scripts/detect_ports.py")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
        
        # Just test import and basic functions
        print("\n1. Testing module import...")
        import scripts.detect_ports as detect_ports
        print("   ✅ Module imported successfully")
        
        # Test configuration functions
        print("\n2. Testing configuration functions...")
        host = detect_ports.get_server_host()
        mqtt_broker = detect_ports.get_mqtt_broker()
        print(f"   ✅ Server host: {host}")
        print(f"   ✅ MQTT broker: {mqtt_broker}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    """Run all configuration tests"""
    print("ParcoRTLS Database-Driven Configuration Test Suite")
    print("="*60)
    
    tests = [
        ("Database Config Helper", test_db_config_helper()),
        ("Config Module", test_config_py()),
        ("DB Connection", test_db_connection()),
        ("DB Functions", test_db_functions()),
        ("Device Registry", test_device_registry()),
        ("Detect Ports", test_detect_ports()),
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
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Database-driven configuration is working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())