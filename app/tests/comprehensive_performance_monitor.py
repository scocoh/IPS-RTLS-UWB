#!/usr/bin/env python3
# Name: comprehensive_performance_monitor.py
# Version: 0.1.0
# Created: 250720
# Modified: 250720
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Comprehensive performance monitoring for FastAPI and system resources during load testing
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Testing
# Status: Active
# Dependent: TRUE

"""
Comprehensive Performance Monitor for ParcoRTLS
==============================================

This script monitors system performance while running FastAPI load tests.
Combines API testing with real-time system monitoring for complete analysis.
"""

import asyncio
import aiohttp
import psutil
import subprocess
import time
import json
import threading
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import signal

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ParcoRTLS configuration
try:
    from server_config import SERVER_IP, SERVER_PORT_MAIN
    BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT_MAIN}"
except ImportError:
    BASE_URL = "http://192.168.210.226:8000"

@dataclass
class SystemSnapshot:
    """System performance snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: float
    network_bytes_recv: float
    fastapi_processes: List[Dict]
    database_connections: int
    load_average: List[float]

class PerformanceMonitor:
    def __init__(self):
        self.base_url = BASE_URL
        self.monitoring = False
        self.snapshots: List[SystemSnapshot] = []
        self.monitor_thread = None
        self.initial_disk_io = None
        self.initial_network_io = None
        self.test_start_time = None
        
    def get_fastapi_processes(self) -> List[Dict]:
        """Get FastAPI process information"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('fastapi' in str(cmd).lower() or 'uvicorn' in str(cmd).lower() for cmd in proc.info['cmdline']):
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'cmdline': ' '.join(proc.info['cmdline'][:3])  # First 3 parts of command
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error getting FastAPI processes: {e}")
        return processes
    
    def get_database_connections(self) -> int:
        """Get PostgreSQL connection count"""
        try:
            result = subprocess.run([
                'sudo', '-u', 'postgres', 'psql', '-t', '-c',
                "SELECT count(*) FROM pg_stat_activity WHERE datname IN ('ParcoRTLSMaint', 'ParcoRTLSData', 'ParcoRTLSHistR');"
            ], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception as e:
            print(f"Error getting DB connections: {e}")
        return 0
    
    def take_system_snapshot(self) -> SystemSnapshot:
        """Take a complete system performance snapshot"""
        # Get current I/O counters
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # Calculate deltas if we have initial values
        disk_read_mb = 0
        disk_write_mb = 0
        net_sent = 0
        net_recv = 0
        
        if self.initial_disk_io and disk_io:
            disk_read_mb = (disk_io.read_bytes - self.initial_disk_io.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self.initial_disk_io.write_bytes) / (1024 * 1024)
        
        if self.initial_network_io and network_io:
            net_sent = (network_io.bytes_sent - self.initial_network_io.bytes_sent) / (1024 * 1024)
            net_recv = (network_io.bytes_recv - self.initial_network_io.bytes_recv) / (1024 * 1024)
        
        memory = psutil.virtual_memory()
        
        return SystemSnapshot(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_available_mb=memory.available / (1024 * 1024),
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_bytes_sent=net_sent,
            network_bytes_recv=net_recv,
            fastapi_processes=self.get_fastapi_processes(),
            database_connections=self.get_database_connections(),
            load_average=list(os.getloadavg())
        )
    
    def start_monitoring(self):
        """Start background monitoring"""
        self.monitoring = True
        # Capture initial I/O counters
        self.initial_disk_io = psutil.disk_io_counters()
        self.initial_network_io = psutil.net_io_counters()
        
        def monitor_loop():
            while self.monitoring:
                try:
                    snapshot = self.take_system_snapshot()
                    self.snapshots.append(snapshot)
                    time.sleep(1)  # Take snapshot every second
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 Performance monitoring started...")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("📊 Performance monitoring stopped.")
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time since test start"""
        if not self.test_start_time:
            return "00:00"
        elapsed = time.time() - self.test_start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def print_realtime_stats(self):
        """Print current system stats with elapsed time"""
        if not self.snapshots:
            return
            
        latest = self.snapshots[-1]
        elapsed = self.get_elapsed_time()
        print(f"\n⚡ REAL-TIME PERFORMANCE [{latest.timestamp}] | Elapsed: {elapsed}")
        print(f"   CPU: {latest.cpu_percent:5.1f}%  |  Memory: {latest.memory_percent:5.1f}%  |  Load Avg: {latest.load_average[0]:.2f}")
        print(f"   Disk I/O: R:{latest.disk_io_read_mb:6.1f}MB W:{latest.disk_io_write_mb:6.1f}MB  |  Network: ↑{latest.network_bytes_sent:6.1f}MB ↓{latest.network_bytes_recv:6.1f}MB")
        print(f"   FastAPI Processes: {len(latest.fastapi_processes)}  |  DB Connections: {latest.database_connections}")
    
    async def run_api_load_test(self, endpoint: str, concurrent_requests: int, duration_seconds: int) -> Dict[str, Any]:
        """Run API load test while monitoring performance"""
        elapsed = self.get_elapsed_time()
        print(f"\n🚀 Starting load test [{elapsed}]: {concurrent_requests} concurrent requests to {endpoint} for {duration_seconds}s")
        
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        completed_requests = 0
        successful_requests = 0
        errors = []
        
        async def make_request(session):
            nonlocal completed_requests, successful_requests
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    completed_requests += 1
                    if response.status == 200:
                        successful_requests += 1
                        await response.json()  # Consume response
                    return response.status
            except Exception as e:
                completed_requests += 1
                errors.append(str(e))
                return "ERROR"
        
        # Start concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            while time.perf_counter() < end_time:
                # Maintain concurrent_requests number of active requests
                while len(tasks) < concurrent_requests and time.perf_counter() < end_time:
                    task = asyncio.create_task(make_request(session))
                    tasks.append(task)
                
                # Wait for at least one task to complete
                if tasks:
                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=0.1)
                    tasks = list(pending)
                
                # Print real-time stats every few requests
                if completed_requests % 50 == 0:
                    self.print_realtime_stats()
        
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        actual_duration = time.perf_counter() - start_time
        elapsed_final = self.get_elapsed_time()
        print(f"✅ Load test completed [{elapsed_final}]: {completed_requests} requests in {actual_duration:.1f}s")
        
        return {
            "endpoint": endpoint,
            "concurrent_requests": concurrent_requests,
            "duration_seconds": actual_duration,
            "total_requests": completed_requests,
            "successful_requests": successful_requests,
            "failed_requests": completed_requests - successful_requests,
            "requests_per_second": completed_requests / actual_duration,
            "success_rate_percent": (successful_requests / completed_requests) * 100 if completed_requests > 0 else 0,
            "errors": errors[:5]  # Show first 5 errors
        }
    
    def analyze_performance_data(self) -> Dict[str, Any]:
        """Analyze collected performance data"""
        if not self.snapshots:
            return {}
        
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_percent for s in self.snapshots]
        load_values = [s.load_average[0] for s in self.snapshots]
        
        return {
            "monitoring_duration_seconds": len(self.snapshots),
            "cpu_usage": {
                "average": sum(cpu_values) / len(cpu_values),
                "peak": max(cpu_values),
                "minimum": min(cpu_values)
            },
            "memory_usage": {
                "average": sum(memory_values) / len(memory_values),
                "peak": max(memory_values),
                "minimum": min(memory_values)
            },
            "load_average": {
                "average": sum(load_values) / len(load_values),
                "peak": max(load_values),
                "minimum": min(load_values)
            },
            "disk_io_total_mb": {
                "read": self.snapshots[-1].disk_io_read_mb if self.snapshots else 0,
                "write": self.snapshots[-1].disk_io_write_mb if self.snapshots else 0
            },
            "network_total_mb": {
                "sent": self.snapshots[-1].network_bytes_sent if self.snapshots else 0,
                "received": self.snapshots[-1].network_bytes_recv if self.snapshots else 0
            },
            "database_connections": {
                "average": sum(s.database_connections for s in self.snapshots) / len(self.snapshots),
                "peak": max(s.database_connections for s in self.snapshots)
            }
        }
    
    def print_performance_report(self, test_results: List[Dict], performance_analysis: Dict):
        """Print comprehensive performance report"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE PERFORMANCE REPORT")
        print(f"{'='*80}")
        
        # API Performance Summary
        print(f"\n📈 API LOAD TEST RESULTS:")
        total_requests = sum(r["total_requests"] for r in test_results)
        total_successful = sum(r["successful_requests"] for r in test_results)
        avg_rps = sum(r["requests_per_second"] for r in test_results) / len(test_results)
        
        print(f"   Total Requests: {total_requests:,}")
        print(f"   Successful Requests: {total_successful:,}")
        print(f"   Overall Success Rate: {(total_successful/total_requests)*100:.1f}%")
        print(f"   Average Requests/Second: {avg_rps:.1f}")
        
        # System Performance Summary
        if performance_analysis:
            print(f"\n🖥️  SYSTEM PERFORMANCE DURING TESTS:")
            cpu = performance_analysis["cpu_usage"]
            memory = performance_analysis["memory_usage"]
            load = performance_analysis["load_average"]
            
            print(f"   CPU Usage: Avg {cpu['average']:.1f}% | Peak {cpu['peak']:.1f}% | Min {cpu['minimum']:.1f}%")
            print(f"   Memory Usage: Avg {memory['average']:.1f}% | Peak {memory['peak']:.1f}% | Min {memory['minimum']:.1f}%")
            print(f"   Load Average: Avg {load['average']:.2f} | Peak {load['peak']:.2f} | Min {load['minimum']:.2f}")
            
            disk = performance_analysis["disk_io_total_mb"]
            network = performance_analysis["network_total_mb"]
            db = performance_analysis["database_connections"]
            
            print(f"   Disk I/O: {disk['read']:.1f}MB read, {disk['write']:.1f}MB write")
            print(f"   Network: {network['sent']:.1f}MB sent, {network['received']:.1f}MB received")
            print(f"   DB Connections: Avg {db['average']:.1f} | Peak {db['peak']:.0f}")
        
        # Individual Test Results
        print(f"\n📊 DETAILED TEST RESULTS:")
        for i, result in enumerate(test_results, 1):
            print(f"   Test {i}: {result['concurrent_requests']} concurrent → {result['requests_per_second']:.1f} RPS ({result['success_rate_percent']:.1f}% success)")
        
        # Performance Insights
        print(f"\n💡 PERFORMANCE INSIGHTS:")
        if performance_analysis:
            if cpu['peak'] > 80:
                print("   ⚠️  High CPU usage detected - consider optimization")
            if memory['peak'] > 80:
                print("   ⚠️  High memory usage detected - monitor for leaks")
            if load['peak'] > 2:
                print("   ⚠️  High system load - check system resources")
            if cpu['peak'] < 50 and avg_rps > 100:
                print("   ✅ Excellent performance - system handles load well")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    async def run_comprehensive_test(self):
        """Run comprehensive performance monitoring with API load tests"""
        print("FastAPI Comprehensive Performance Monitor")
        print("="*80)
        print(f"Testing API at: {self.base_url}")
        
        # Set test start time for elapsed clock
        self.test_start_time = time.time()
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Elapsed: 00:00")
        
        # Test if server is responsive
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/list_trigger_directions") as response:
                    if response.status != 200:
                        print(f"❌ API not responsive: {response.status}")
                        return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return
        
        elapsed = self.get_elapsed_time()
        print(f"✅ API server is responsive | Elapsed: {elapsed}")
        
        # Start performance monitoring
        self.start_monitoring()
        
        # Wait a moment for baseline
        await asyncio.sleep(2)
        
        try:
            # Run load tests with increasing intensity
            test_results = []
            
            test_scenarios = [
                ("/api/list_trigger_directions", 5, 10),   # Light load
                ("/api/list_zones", 15, 15),               # Medium load  
                ("/api/get_all_devices", 25, 20),          # Heavy load
                ("/api/zones_for_ai", 35, 25)              # Maximum load
            ]
            
            for i, (endpoint, concurrent, duration) in enumerate(test_scenarios, 1):
                elapsed = self.get_elapsed_time()
                print(f"\n{'='*60}")
                print(f"🔄 Test {i}/4 [{elapsed}]: Preparing {concurrent} concurrent requests...")
                
                result = await self.run_api_load_test(endpoint, concurrent, duration)
                test_results.append(result)
                
                # Brief cooldown between tests
                if i < len(test_scenarios):  # Don't cooldown after last test
                    elapsed = self.get_elapsed_time()
                    print(f"💤 Cooldown period [{elapsed}]...")
                    await asyncio.sleep(3)
            
        finally:
            # Stop monitoring and analyze
            self.stop_monitoring()
        
        # Generate comprehensive report
        elapsed = self.get_elapsed_time()
        print(f"\n📊 Generating final report [{elapsed}]...")
        performance_analysis = self.analyze_performance_data()
        self.print_performance_report(test_results, performance_analysis)

async def main():
    """Main execution function"""
    monitor = PerformanceMonitor()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Test interrupted by user")
        monitor.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await monitor.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())