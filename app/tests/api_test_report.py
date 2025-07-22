#!/usr/bin/env python3
# Name: api_test_report.py
# Version: 0.1.0
# Created: 250720
# Modified: 250720
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: API test report generator for ParcoRTLS - Tests key functionality with curl equivalent commands
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
API Test Report Generator for ParcoRTLS
=======================================

This script tests key API functionality and generates a comprehensive report.
Equivalent to running curl commands but with detailed analysis and formatting.
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ParcoRTLS configuration
try:
    from server_config import SERVER_IP, SERVER_PORT_MAIN
    BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT_MAIN}"
except ImportError:
    BASE_URL = "http://192.168.210.226:8000"

class APITestResult:
    def __init__(self, test_name: str, curl_command: str, endpoint: str):
        self.test_name = test_name
        self.curl_command = curl_command
        self.endpoint = endpoint
        self.response_data: Optional[Any] = None
        self.status_code: Optional[int] = None
        self.response_time_ms: float = 0.0
        self.error: Optional[str] = None
        self.success: bool = False

class ParcoRTLSAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results: List[APITestResult] = []
        
    async def execute_test(self, test_name: str, endpoint: str, params: Optional[Dict] = None) -> APITestResult:
        """Execute a single API test"""
        
        # Build curl command for display
        url = f"{self.base_url}{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            url += f"?{param_str}"
        
        curl_command = f'curl -X GET "{url}"'
        
        result = APITestResult(test_name, curl_command, endpoint)
        
        start_time = time.perf_counter()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                    end_time = time.perf_counter()
                    result.response_time_ms = round((end_time - start_time) * 1000, 2)
                    result.status_code = response.status
                    
                    if response.status == 200:
                        result.response_data = await response.json()
                        result.success = True
                    else:
                        result.response_data = await response.text()
                        result.success = False
                        
        except Exception as e:
            end_time = time.perf_counter()
            result.response_time_ms = round((end_time - start_time) * 1000, 2)
            result.error = str(e)
            result.success = False
            
        self.test_results.append(result)
        return result
    
    def print_test_header(self, category: str):
        """Print formatted test category header"""
        print(f"\n{'='*80}")
        print(f"{category.upper()}")
        print(f"{'='*80}")
    
    def print_test_result(self, result: APITestResult):
        """Print formatted test result"""
        print(f"\n## Test: {result.test_name}")
        print(f"**Curl Command:**")
        print(f"```bash")
        print(f"{result.curl_command}")
        print(f"```")
        
        print(f"\n**Response:**")
        print(f"- Status: {result.status_code}")
        print(f"- Response Time: {result.response_time_ms}ms")
        print(f"- Success: {'✅' if result.success else '❌'}")
        
        if result.error:
            print(f"- Error: {result.error}")
        
        print(f"\n**Response Data:**")
        print(f"```json")
        if result.response_data:
            if isinstance(result.response_data, dict) or isinstance(result.response_data, list):
                print(json.dumps(result.response_data, indent=2))
            else:
                print(result.response_data)
        else:
            print("No response data")
        print(f"```")
        print("-" * 80)
    
    def generate_summary_report(self):
        """Generate summary report at the end"""
        print(f"\n{'='*80}")
        print("SUMMARY REPORT")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - successful_tests
        
        print(f"\n**Overall Results:**")
        print(f"- Total Tests: {total_tests}")
        print(f"- Successful: {successful_tests} ✅")
        print(f"- Failed: {failed_tests} ❌")
        print(f"- Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Response time analysis
        response_times = [r.response_time_ms for r in self.test_results if r.success]
        if response_times:
            print(f"\n**Performance Analysis:**")
            print(f"- Average Response Time: {sum(response_times)/len(response_times):.2f}ms")
            print(f"- Fastest Response: {min(response_times):.2f}ms")
            print(f"- Slowest Response: {max(response_times):.2f}ms")
        
        # Test category breakdown
        print(f"\n**Test Results by Category:**")
        categories = {}
        for result in self.test_results:
            # Extract category from test name
            if "Real-Time" in result.test_name:
                category = "Real-Time Tracking"
            elif "Historical" in result.test_name:
                category = "Historical Tracking"
            elif "Zone" in result.test_name:
                category = "Zone Management"
            elif "Quick Test" in result.test_name:
                category = "Quick Test"
            else:
                category = "Other"
                
            if category not in categories:
                categories[category] = {"total": 0, "success": 0}
            categories[category]["total"] += 1
            if result.success:
                categories[category]["success"] += 1
        
        for category, stats in categories.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            print(f"- {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Failed tests details
        failed_results = [r for r in self.test_results if not r.success]
        if failed_results:
            print(f"\n**Failed Tests Details:**")
            for result in failed_results:
                print(f"- {result.test_name}: Status {result.status_code}")
                if result.error:
                    print(f"  Error: {result.error}")
        
        print(f"\n**Recommendations:**")
        if failed_tests == 0:
            print("- All tests passed! API is functioning correctly.")
        else:
            print("- Check failed endpoints for issues")
            print("- Verify database connectivity")
            print("- Ensure test tags (23026, 23027, 23028, 23029) exist in system")
            print("- Note: Historical data is from July 15th, adjust time ranges accordingly")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def run_comprehensive_test(self):
        """Run all API tests"""
        print("ParcoRTLS API Comprehensive Test Report")
        print("="*80)
        print(f"Testing API at: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Real-Time Tray Tracking Tests
        self.print_test_header("Real-Time Tray Tracking")
        
        tests = [
            ("Real-Time: Where is tag 23026?", "/api/get_tag_current_zone/23026"),
            ("Real-Time: Where is tag 23027?", "/api/get_tag_current_zone/23027"),
            ("Real-Time: Where is tag 23028?", "/api/get_tag_current_zone/23028")
        ]
        
        for test_name, endpoint in tests:
            result = await self.execute_test(test_name, endpoint)
            self.print_test_result(result)
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Historical Tray Tracking Tests
        self.print_test_header("Historical Tray Tracking")
        
        historical_tests = [
            ("Historical: Tag 23026 last 7 days", "/api/get_tag_last_known_zone/23026", {"hours_back": 168}),
            ("Historical: Tag 23029 last 7 days", "/api/get_tag_last_known_zone/23029", {"hours_back": 168})
        ]
        
        for test_name, endpoint, params in historical_tests:
            result = await self.execute_test(test_name, endpoint, params)
            self.print_test_result(result)
            await asyncio.sleep(0.5)
        
        # Zone Management Tests
        self.print_test_header("Zone Management")
        
        zone_tests = [
            ("Zone: Get all zones", "/api/list_zones"),
            ("Zone: Get LB Sterile area details", "/api/get_zone_by_id/520"),
            ("Zone: Find zones at coordinate point", "/api/zones_by_point", {"x": 170, "y": 140, "z": 0})
        ]
        
        for test_name, endpoint, *params in zone_tests:
            param_dict = params[0] if params else None
            result = await self.execute_test(test_name, endpoint, param_dict)
            self.print_test_result(result)
            await asyncio.sleep(0.5)
        
        # Quick Test for Steve
        self.print_test_header("Quick Test for Steve")
        
        result = await self.execute_test("Quick Test: Main functionality test", "/api/get_tag_current_zone/23026")
        self.print_test_result(result)
        
        # Generate summary report
        self.generate_summary_report()

async def main():
    """Main execution function"""
    print("Checking API connectivity...")
    
    try:
        # Quick connectivity test
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/list_trigger_directions") as response:
                if response.status == 200:
                    print("✅ API server is responsive")
                    print()
                    
                    # Run comprehensive tests
                    tester = ParcoRTLSAPITester()
                    await tester.run_comprehensive_test()
                else:
                    print(f"❌ API responded with status: {response.status}")
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print(f"Please ensure FastAPI server is running at {BASE_URL}")

if __name__ == "__main__":
    asyncio.run(main())