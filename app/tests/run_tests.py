#!/usr/bin/env python3
# Name: run_tests.py
# Version: 0.1.0
# Created: 250702
# Modified: 250702
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Test runner for ParcoRTLS test suite
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
ParcoRTLS Test Runner
====================

Runs all available tests in the ParcoRTLS test suite.

Usage:
    cd /home/parcoadmin/parco_fastapi/app/tests
    python3 run_tests.py
    
    or from app directory:
    cd /home/parcoadmin/parco_fastapi/app
    python3 -m tests.run_tests
"""

import asyncio
import sys
import os
import importlib
import traceback
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def run_test_module(module_name):
    """Run a specific test module"""
    print(f"\n{'='*80}")
    print(f"RUNNING TEST MODULE: {module_name}")
    print(f"{'='*80}")
    
    try:
        # Import the test module
        module = importlib.import_module(f"tests.{module_name}")
        
        # Check if module has a main function
        if hasattr(module, 'main'):
            print(f"Executing {module_name}.main()...")
            if asyncio.iscoroutinefunction(module.main):
                await module.main()
            else:
                module.main()
            return True
        else:
            print(f"⚠️  {module_name} does not have a main() function")
            return False
            
    except Exception as e:
        print(f"❌ Error running {module_name}: {e}")
        traceback.print_exc()
        return False

async def discover_and_run_tests():
    """Discover and run all test modules"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all test modules
    test_modules = []
    for filename in os.listdir(test_dir):
        if filename.startswith('test_') and filename.endswith('.py'):
            module_name = filename[:-3]  # Remove .py extension
            test_modules.append(module_name)
    
    if not test_modules:
        print("❌ No test modules found!")
        return []
    
    print(f"🔍 Discovered {len(test_modules)} test module(s): {', '.join(test_modules)}")
    
    results = []
    for module_name in sorted(test_modules):
        success = await run_test_module(module_name)
        results.append((module_name, success))
    
    return results

def print_summary(results):
    """Print test results summary"""
    print(f"\n{'='*80}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for module_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{module_name:<30} {status}")
    
    print(f"\nOverall Results: {passed}/{total} test modules passed")
    
    if passed == total:
        print("🎉 All test modules completed successfully!")
    elif passed > 0:
        print("⚠️  Some test modules failed - see details above")
    else:
        print("❌ All test modules failed - check configuration and dependencies")
    
    return passed == total

async def main():
    """Main test runner function"""
    print("ParcoRTLS Test Suite Runner")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        results = await discover_and_run_tests()
        success = print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())