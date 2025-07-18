# Name: dashboard_manager.py
# Version: 0.1.3
# Created: 250713
# Modified: 250713
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: FastAPI routes for Dashboard Manager API endpoints - Enhanced with subprocess service management
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Dashboard Manager API Routes

Provides RESTful API endpoints for managing and monitoring the Dashboard Manager.
Follows established ParcoRTLS route patterns and integrates with the DashboardManager class.
Enhanced with data source discovery and management endpoints.
Enhanced with subprocess service management for actual service control.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
import asyncio
import logging
import os
import sys
from pathlib import Path
import asyncpg
import httpx
from datetime import datetime

# NEW IMPORTS FOR SUBPROCESS MANAGEMENT
import subprocess
import psutil
import signal
import time
import socket

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

# Type checking imports
if TYPE_CHECKING:
    from manager.manager_dashboard import DashboardManager

# Import the Dashboard Manager
try:
    from manager.manager_dashboard import DashboardManager
    HAS_DASHBOARD_MANAGER = True
except ImportError:
    HAS_DASHBOARD_MANAGER = False
    DashboardManager = None

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard-manager",
    tags=["dashboard-manager"]
)

# Global Dashboard Manager instance - Fixed type annotation
_dashboard_manager_instance: Optional[Any] = None

# NEW GLOBAL PROCESS TRACKING
_running_processes: Dict[str, subprocess.Popen] = {}

# Database configuration
db_configs = get_db_configs_sync()
maint_config = db_configs['maint']
MAINT_CONN_STRING = f"postgresql://{maint_config['user']}:{maint_config['password']}@{maint_config['host']}:{maint_config['port']}/{maint_config['database']}"

# Data source configuration
DATA_SOURCES_DIR = "/home/parcoadmin/parco_fastapi/app/DataSources"
DATA_SOURCE_RESOURCE_TYPES = range(2101, 2200)  # Resource types 2101-2199

async def get_dashboard_manager():
    """Get or create the Dashboard Manager instance"""
    global _dashboard_manager_instance
    
    if not HAS_DASHBOARD_MANAGER or DashboardManager is None:
        raise HTTPException(status_code=503, detail="Dashboard Manager not available")
    
    if _dashboard_manager_instance is None:
        _dashboard_manager_instance = DashboardManager("DashboardManager", zone_id=1)
        # Auto-start if not already started
        if _dashboard_manager_instance and hasattr(_dashboard_manager_instance, 'is_healthy'):
            if not _dashboard_manager_instance.is_healthy():
                await _dashboard_manager_instance.start()
    
    return _dashboard_manager_instance

async def get_database_connection():
    """Get database connection pool"""
    try:
        return await asyncpg.create_pool(MAINT_CONN_STRING)
    except Exception as e:
        logger.error(f"Failed to create database connection: {str(e)}")
        raise HTTPException(status_code=503, detail="Database connection failed")

async def query_data_sources_from_db():
    """Query data sources from tlkresources and tlkresourcetypes tables"""
    try:
        async with await get_database_connection() as pool:
            async with pool.acquire() as conn:
                # Query data sources and their types
                query = """
                SELECT 
                    r.i_res,
                    r.i_typ_res,
                    r.x_nm_res,
                    r.x_ip,
                    r.i_prt,
                    rt.x_dsc_res
                FROM tlkresources r
                LEFT JOIN tlkresourcetypes rt ON r.i_typ_res = rt.i_typ_res
                WHERE r.i_typ_res BETWEEN $1 AND $2
                ORDER BY r.i_res
                """
                
                rows = await conn.fetch(query, 2101, 2199)
                
                data_sources = []
                for row in rows:
                    data_sources.append({
                        "id": row['i_res'],
                        "resource_type": row['i_typ_res'],
                        "name": row['x_nm_res'],
                        "host": row['x_ip'],
                        "port": row['i_prt'],
                        "type_description": row['x_dsc_res']
                    })
                
                return data_sources
                
    except Exception as e:
        logger.error(f"Error querying data sources from database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

def check_data_source_directory(source_name: str):
    """Check if data source directory exists and scan for files"""
    try:
        # Try exact match first
        source_dir = Path(DATA_SOURCES_DIR) / source_name
        
        # If exact match doesn't exist, try removing common suffixes
        if not source_dir.exists():
            # Remove common suffixes like "Inbound", "Outbound", "Stream"
            base_name = source_name
            suffixes_to_remove = ["Inbound", "Outbound", "Stream", "Service"]
            
            for suffix in suffixes_to_remove:
                if base_name.endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break
            
            source_dir = Path(DATA_SOURCES_DIR) / base_name
        
        result = {
            "directory_exists": source_dir.exists(),
            "service_file": None,
            "config_found": False,
            "readme_found": False,
            "requirements_found": False,
            "directory_path": str(source_dir) if source_dir.exists() else None
        }
        
        if result["directory_exists"]:
            # Check for service file
            service_files = list(source_dir.glob("*_service.py")) + list(source_dir.glob("*service.py"))
            if service_files:
                result["service_file"] = service_files[0].name
            
            # Check for config directory or files
            config_dir = source_dir / "config"
            config_files = list(source_dir.glob("*.conf")) + list(source_dir.glob("*.json"))
            if config_dir.exists():
                config_files.extend(list(config_dir.glob("*.conf")) + list(config_dir.glob("*.json")))
            result["config_found"] = len(config_files) > 0
            
            # Check for README
            readme_files = list(source_dir.glob("README*"))
            result["readme_found"] = len(readme_files) > 0
            
            # Check for requirements
            requirements_files = list(source_dir.glob("requirements*"))
            result["requirements_found"] = len(requirements_files) > 0
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking directory for {source_name}: {str(e)}")
        return {
            "directory_exists": False,
            "service_file": None,
            "config_found": False,
            "readme_found": False,
            "requirements_found": False,
            "error": str(e)
        }

async def check_service_status(host: str, port: int, timeout: float = 5.0):
    """Check if a service is running by attempting HTTP connection"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            start_time = asyncio.get_event_loop().time()
            
            # Try a basic HTTP request
            try:
                response = await client.get(f"http://{host}:{port}/")
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return {
                    "status": "online",
                    "response_time": round(response_time, 2),
                    "status_code": response.status_code,
                    "error_message": None
                }
            except httpx.ConnectError:
                return {
                    "status": "offline",
                    "response_time": None,
                    "status_code": None,
                    "error_message": "Connection refused"
                }
            except httpx.TimeoutException:
                return {
                    "status": "timeout",
                    "response_time": None,
                    "status_code": None,
                    "error_message": "Request timeout"
                }
                
    except Exception as e:
        logger.error(f"Error checking service status for {host}:{port}: {str(e)}")
        return {
            "status": "error",
            "response_time": None,
            "status_code": None,
            "error_message": str(e)
        }

async def perform_health_checks(source_name: str, host: str, port: int):
    """Perform comprehensive health checks on a data source"""
    try:
        # Check port accessibility
        status_result = await check_service_status(host, port)
        port_accessible = status_result["status"] == "online"
        
        # Check directory structure
        dir_result = check_data_source_directory(source_name)
        config_valid = dir_result["config_found"] and dir_result["service_file"] is not None
        
        # Determine overall health
        service_responding = port_accessible
        overall_healthy = port_accessible and config_valid
        
        return {
            "healthy": overall_healthy,
            "status": "healthy" if overall_healthy else ("unreachable" if not port_accessible else "unhealthy"),
            "checks": {
                "port_accessible": port_accessible,
                "service_responding": service_responding,
                "config_valid": config_valid,
                "directory_exists": dir_result["directory_exists"]
            },
            "details": {
                "service_status": status_result,
                "directory_scan": dir_result
            }
        }
        
    except Exception as e:
        logger.error(f"Error performing health checks for {source_name}: {str(e)}")
        return {
            "healthy": False,
            "status": "error",
            "checks": {
                "port_accessible": False,
                "service_responding": False,
                "config_valid": False,
                "directory_exists": False
            },
            "error": str(e)
        }

# ============================================================================
# NEW SUBPROCESS MANAGEMENT HELPER FUNCTIONS
# ============================================================================

def get_service_config(source_id: str) -> Optional[Dict[str, str]]:
    """Get service configuration for a data source."""
    service_configs = {
        "AllTraqAppAPI": {
            "service_file": "alltraq_service.py",
            "working_dir": "/home/parcoadmin/parco_fastapi/app/DataSources/AllTraqAppAPI",
            "python_path": "python"
        },
        "AllTraqAppAPIInbound": {
            "service_file": "alltraq_service.py",
            "working_dir": "/home/parcoadmin/parco_fastapi/app/DataSources/AllTraqAppAPI",
            "python_path": "python"
        }
        # Future data sources can be added here
    }
    return service_configs.get(source_id)

def is_process_running(source_id: str) -> bool:
    """Check if a data source process is currently running."""
    if source_id not in _running_processes:
        return False
    
    process = _running_processes[source_id]
    if process.poll() is None:  # Process is still running
        return True
    else:
        # Process has terminated, remove from tracking
        del _running_processes[source_id]
        return False

def kill_process_by_name(process_name: str) -> bool:
    """Kill process by name as backup method."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if process_name in ' '.join(proc.info['cmdline'] or []):
                proc.terminate()
                proc.wait(timeout=5)
                return True
    except Exception as e:
        logger.warning(f"Error killing process {process_name}: {e}")
    return False

# ============================================================================
# EXISTING ENDPOINTS (PRESERVED FROM v0.1.2)
# ============================================================================

@router.get("/status")
async def get_manager_status():
    """
    Get Dashboard Manager status and statistics.
    
    Returns:
        dict: Complete manager status including health, performance, and configuration
        
    Raises:
        HTTPException (503): If Dashboard Manager is not available
        HTTPException (500): On unexpected errors
    """
    try:
        manager = await get_dashboard_manager()
        stats = manager.get_dashboard_stats()
        
        # Add health status
        stats['healthy'] = manager.is_healthy()
        stats['timestamp'] = asyncio.get_event_loop().time()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting manager status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_manager(background_tasks: BackgroundTasks):
    """
    Start the Dashboard Manager.
    
    Returns:
        dict: Success message and manager status
        
    Raises:
        HTTPException (500): If manager fails to start
    """
    try:
        manager = await get_dashboard_manager()
        
        if manager.is_healthy():
            return {"message": "Dashboard Manager is already running", "status": "started"}
        
        success = await manager.start()
        if success:
            return {"message": "Dashboard Manager started successfully", "status": "started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start Dashboard Manager")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting manager: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_manager():
    """
    Stop the Dashboard Manager.
    
    Returns:
        dict: Success message and manager status
        
    Raises:
        HTTPException (500): If manager fails to stop
    """
    try:
        global _dashboard_manager_instance
        
        if _dashboard_manager_instance is None:
            return {"message": "Dashboard Manager is not running", "status": "stopped"}
        
        success = await _dashboard_manager_instance.shutdown()
        if success:
            _dashboard_manager_instance = None
            return {"message": "Dashboard Manager stopped successfully", "status": "stopped"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop Dashboard Manager")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping manager: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_manager():
    """
    Restart the Dashboard Manager.
    
    Returns:
        dict: Success message and manager status
        
    Raises:
        HTTPException (500): If manager fails to restart
    """
    try:
        # Stop first
        await stop_manager()
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Start again
        result = await start_manager(BackgroundTasks())
        result["message"] = "Dashboard Manager restarted successfully"
        
        return result
        
    except Exception as e:
        logger.error(f"Error restarting manager: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_manager_health():
    """
    Get Dashboard Manager health status.
    
    Returns:
        dict: Health status and basic metrics
    """
    try:
        manager = await get_dashboard_manager()
        
        return {
            "healthy": manager.is_healthy(),
            "run_state": manager.run_state.name,
            "customers_active": len(manager.dashboard_customers),
            "queue_size": manager.message_queue.qsize() if hasattr(manager, 'message_queue') else 0,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.warning(f"Health check failed: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

@router.get("/customers")
async def get_customer_stats():
    """
    Get customer statistics and configuration.
    
    Returns:
        dict: Customer statistics including routing information
    """
    try:
        manager = await get_dashboard_manager()
        stats = manager.get_dashboard_stats()
        
        return stats.get('customer_stats', {})
        
    except Exception as e:
        logger.error(f"Error getting customer stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{customer_id}")
async def get_customer_config(customer_id: int):
    """
    Get configuration for a specific customer.
    
    Args:
        customer_id: Customer ID to get configuration for
        
    Returns:
        dict: Customer configuration details
        
    Raises:
        HTTPException (404): If customer not found
    """
    try:
        manager = await get_dashboard_manager()
        
        if customer_id not in manager.dashboard_customers:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        customer = manager.dashboard_customers[customer_id]
        
        return {
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name,
            "is_active": customer.is_active,
            "router_stats": customer.message_router.get_routing_statistics() if customer.message_router else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/stats")
async def get_message_stats():
    """
    Get message processing statistics.
    
    Returns:
        dict: Message flow and processing statistics
    """
    try:
        manager = await get_dashboard_manager()
        stats = manager.get_dashboard_stats()
        
        # Create message statistics
        dashboard_stats = stats.get('dashboard_manager', {})
        
        message_stats = {
            "total_received": dashboard_stats.get('messages_processed', 0),
            "total_processed": dashboard_stats.get('messages_processed', 0),
            "total_routed": dashboard_stats.get('messages_routed', 0),
            "dashboard_sent": dashboard_stats.get('messages_routed', 0),
            "queue_size": dashboard_stats.get('queue_size', 0),
            "processing_rate": dashboard_stats.get('routing_rate', 0),
            "routing_rate": dashboard_stats.get('routing_rate', 0),
            "messages_per_second": dashboard_stats.get('messages_processed', 0) / 60,  # Rough estimate
            "avg_processing_time": 5.0,  # Placeholder
            "active_customers": dashboard_stats.get('customers_active', 0),
            "connected_clients": stats.get('clients', {}).get('total_websocket_clients', 0),
            "last_message_time": None,  # TODO: Track this
            "error_count": 0,  # TODO: Track this
            "category_breakdown": {},  # TODO: Implement this
            "recent_errors": []  # TODO: Implement this
        }
        
        return message_stats
        
    except Exception as e:
        logger.error(f"Error getting message stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients")
async def get_client_connections():
    """
    Get current client connections.
    
    Returns:
        list: List of connected clients with details
    """
    try:
        manager = await get_dashboard_manager()
        stats = manager.get_dashboard_stats()
        
        # Extract client information
        client_stats = stats.get('clients', {})
        
        # Create mock client data for now
        # TODO: Implement actual client tracking
        connections = []
        
        websocket_count = client_stats.get('total_websocket_clients', 0)
        sdk_count = client_stats.get('total_sdk_clients', 0)
        
        for i in range(websocket_count):
            connections.append({
                "client_id": f"dashboard_{i+1:03d}",
                "client_type": "Dashboard",
                "customer_id": 1,
                "ip_address": "192.168.210.100",
                "connect_time": "2025-07-13T02:00:00Z",
                "last_activity": "2025-07-13T02:43:00Z",
                "messages_sent": 100 * (i + 1),
                "messages_received": 10 * (i + 1),
                "user_agent": "Mozilla/5.0"
            })
        
        for i in range(sdk_count):
            connections.append({
                "client_id": f"sdk_{i+1:03d}",
                "client_type": "SDK",
                "customer_id": None,
                "ip_address": "192.168.210.101",
                "connect_time": "2025-07-13T01:00:00Z",
                "last_activity": "2025-07-13T02:43:00Z",
                "messages_sent": 500 * (i + 1),
                "messages_received": 50 * (i + 1),
                "user_agent": "ParcoRTLS-SDK/1.0"
            })
        
        return connections
        
    except Exception as e:
        logger.error(f"Error getting client connections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics():
    """
    Get performance metrics and system resource usage.
    
    Returns:
        dict: Performance metrics including CPU, memory, and throughput
    """
    try:
        manager = await get_dashboard_manager()
        stats = manager.get_dashboard_stats()
        
        return {
            "manager_stats": stats,
            "system_metrics": {
                "cpu_usage": 15.0,  # Placeholder
                "memory_usage": 45.0,  # Placeholder
                "disk_usage": 60.0,  # Placeholder
                "network_io": 1.2  # Placeholder
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug")
async def get_debug_info():
    """
    Get debug information for troubleshooting.
    
    Returns:
        dict: Debug information including internal state
    """
    try:
        manager = await get_dashboard_manager()
        
        debug_info = {
            "manager_instance": str(manager),
            "has_message_router": hasattr(manager, 'dashboard_customers'),
            "customer_count": len(manager.dashboard_customers) if hasattr(manager, 'dashboard_customers') else 0,
            "database_ready": manager.database.is_database_ready() if hasattr(manager, 'database') else False,
            "run_state": manager.run_state.name if hasattr(manager, 'run_state') else 'Unknown',
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Error getting debug info: {str(e)}")
        return {"error": str(e), "timestamp": asyncio.get_event_loop().time()}

@router.post("/test/connection")
async def test_dashboard_connection():
    """
    Test Dashboard Manager connection and functionality.
    
    Returns:
        dict: Test results
    """
    try:
        manager = await get_dashboard_manager()
        
        test_results = {
            "manager_healthy": manager.is_healthy(),
            "database_connected": manager.database.is_database_ready() if hasattr(manager, 'database') else False,
            "customers_loaded": len(manager.dashboard_customers) if hasattr(manager, 'dashboard_customers') else 0,
            "processing_active": hasattr(manager, 'processing_task') and manager.processing_task is not None,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return {
            "success": all([
                test_results["manager_healthy"],
                test_results["database_connected"]
            ]),
            "results": test_results
        }
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

# ============================================================================
# DATA SOURCE DISCOVERY ENDPOINTS (PRESERVED FROM v0.1.2)
# ============================================================================

@router.get("/data-sources/discover")
async def discover_data_sources():
    """
    Discover available data sources from database and directory structure.
    
    Returns:
        dict: {
            "sources": [
                {
                    "id": "AllTraqAppAPI",
                    "name": "AllTraqAppAPIInbound", 
                    "type": "Inbound AllTraq GeoTraqr",
                    "resource_type": 2101,
                    "host": "192.168.210.226",
                    "port": 18002,
                    "directory_exists": true,
                    "config_found": true,
                    "service_file": "alltraq_service.py"
                }
            ],
            "total_discovered": 1,
            "timestamp": "2025-07-13T12:00:00Z"
        }
    """
    try:
        logger.info("Starting data source discovery")
        
        # Query database for data sources
        db_sources = await query_data_sources_from_db()
        logger.debug(f"Found {len(db_sources)} data sources in database")
        
        discovered_sources = []
        
        for db_source in db_sources:
            # Check directory structure for each source
            source_name = db_source["name"]
            dir_info = check_data_source_directory(source_name)
            
            # Combine database and directory information
            source_info = {
                "id": source_name,
                "name": source_name,
                "type": db_source["type_description"] or f"Resource Type {db_source['resource_type']}",
                "resource_type": db_source["resource_type"],
                "host": db_source["host"],
                "port": db_source["port"],
                "directory_exists": dir_info["directory_exists"],
                "config_found": dir_info["config_found"],
                "service_file": dir_info["service_file"],
                "readme_found": dir_info["readme_found"],
                "requirements_found": dir_info["requirements_found"]
            }
            
            # Add error info if directory scan failed
            if "error" in dir_info:
                source_info["directory_error"] = dir_info["error"]
            
            discovered_sources.append(source_info)
            logger.debug(f"Processed source: {source_name}")
        
        result = {
            "sources": discovered_sources,
            "total_discovered": len(discovered_sources),
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        logger.info(f"Discovery completed: {len(discovered_sources)} sources found")
        return result
        
    except Exception as e:
        logger.error(f"Error during data source discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@router.get("/data-sources/{source_id}/status")
async def get_data_source_status(source_id: str):
    """
    Get current status of a specific data source.
    
    Args:
        source_id: Data source identifier (e.g., "AllTraqAppAPI")
        
    Returns:
        dict: {
            "source_id": "AllTraqAppAPI",
            "status": "online|offline|error",
            "port": 18002,
            "last_check": "2025-07-13T12:00:00Z",
            "response_time": 45.2,
            "error_message": null,
            "process_running": true,
            "port_accessible": true,
            "pid": 12345
        }
    """
    try:
        logger.info(f"Checking status for data source: {source_id}")
        
        # Find the data source in database
        db_sources = await query_data_sources_from_db()
        source_info = None
        
        for source in db_sources:
            if source["name"] == source_id:
                source_info = source
                break
        
        if not source_info:
            raise HTTPException(status_code=404, detail=f"Data source '{source_id}' not found")
        
        # Check service status
        status_result = await check_service_status(source_info["host"], source_info["port"])
        
        # Check if process is running
        process_running = is_process_running(source_id)
        
        # Try to connect to service port to verify it's responding
        port_accessible = False
        response_time = None
        
        try:
            start_time = time.time()
            # Simple socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((source_info["host"], source_info["port"]))
            sock.close()
            
            if result == 0:
                port_accessible = True
                response_time = (time.time() - start_time) * 1000  # ms
                
        except Exception:
            pass
        
        status = "online" if (process_running and port_accessible) else "offline"
        
        result = {
            "source_id": source_id,
            "status": status,
            "host": source_info["host"],
            "port": source_info["port"],
            "last_check": datetime.now().isoformat() + "Z",
            "response_time": response_time,
            "status_code": status_result["status_code"],
            "error_message": status_result["error_message"],
            "process_running": process_running,
            "port_accessible": port_accessible,
            "pid": _running_processes[source_id].pid if source_id in _running_processes else None
        }
        
        logger.debug(f"Status check completed for {source_id}: {status}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking status for {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/data-sources/{source_id}/health")
async def check_data_source_health(source_id: str):
    """
    Perform health check on a specific data source.
    
    Args:
        source_id: Data source identifier
        
    Returns:
        dict: {
            "source_id": "AllTraqAppAPI", 
            "healthy": true,
            "status": "healthy|unhealthy|unreachable",
            "checks": {
                "port_accessible": true,
                "service_responding": true,
                "config_valid": true
            },
            "timestamp": "2025-07-13T12:00:00Z"
        }
    """
    try:
        logger.info(f"Performing health check for data source: {source_id}")
        
        # Find the data source in database
        db_sources = await query_data_sources_from_db()
        source_info = None
        
        for source in db_sources:
            if source["name"] == source_id:
                source_info = source
                break
        
        if not source_info:
            raise HTTPException(status_code=404, detail=f"Data source '{source_id}' not found")
        
        # Perform comprehensive health checks
        health_result = await perform_health_checks(source_id, source_info["host"], source_info["port"])
        
        result = {
            "source_id": source_id,
            "healthy": health_result["healthy"],
            "status": health_result["status"],
            "checks": health_result["checks"],
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        # Add detailed information if available
        if "details" in health_result:
            result["details"] = health_result["details"]
        
        # Add error information if present
        if "error" in health_result:
            result["error"] = health_result["error"]
        
        logger.debug(f"Health check completed for {source_id}: {health_result['status']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during health check for {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# ============================================================================
# ENHANCED SERVICE MANAGEMENT ENDPOINTS (NEW SUBPROCESS IMPLEMENTATION)
# ============================================================================

@router.post("/data-sources/{source_id}/start")
async def start_data_source(source_id: str):
    """
    Start a data source service using subprocess management.
    
    Args:
        source_id: Data source identifier
        
    Returns:
        dict: {
            "success": true,
            "message": "Service AllTraqAppAPI started successfully",
            "status": "running",
            "pid": 12345
        }
    """
    try:
        logger.info(f"Attempting to start data source: {source_id}")
        
        # Check if already running
        if is_process_running(source_id):
            return {
                "success": False,
                "message": f"Service {source_id} is already running",
                "status": "running"
            }
        
        # Get service configuration
        config = get_service_config(source_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Unknown data source: {source_id}")
        
        # Verify service file exists
        service_path = Path(config["working_dir"]) / config["service_file"]
        if not service_path.exists():
            raise HTTPException(status_code=404, detail=f"Service file not found: {service_path}")
        
        # Start the process
        cmd = [config["python_path"], config["service_file"]]
        process = subprocess.Popen(
            cmd,
            cwd=config["working_dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Store process for tracking
        _running_processes[source_id] = process
        
        # Give it a moment to start
        await asyncio.sleep(1)
        
        # Check if it started successfully
        if process.poll() is None:  # Still running
            logger.info(f"Successfully started {source_id} service (PID: {process.pid})")
            return {
                "success": True,
                "message": f"Service {source_id} started successfully",
                "status": "running",
                "pid": process.pid
            }
        else:
            # Process died immediately
            stdout, stderr = process.communicate()
            del _running_processes[source_id]
            return {
                "success": False,
                "message": f"Service {source_id} failed to start",
                "error": stderr.decode() if stderr else "Unknown error",
                "status": "failed"
            }
            
    except Exception as e:
        logger.error(f"Error starting {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-sources/{source_id}/stop")
async def stop_data_source(source_id: str):
    """
    Stop a data source service using subprocess management.
    
    Args:
        source_id: Data source identifier
        
    Returns:
        dict: {
            "success": true,
            "message": "Service AllTraqAppAPI stopped successfully",
            "status": "stopped"
        }
    """
    try:
        logger.info(f"Attempting to stop data source: {source_id}")
        
        # Check if we're tracking the process
        if source_id in _running_processes:
            process = _running_processes[source_id]
            
            if process.poll() is None:  # Process is running
                # Try graceful shutdown first
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    # Wait up to 5 seconds for graceful shutdown
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    process.wait()
                
                del _running_processes[source_id]
                logger.info(f"Successfully stopped {source_id} service")
                
                return {
                    "success": True,
                    "message": f"Service {source_id} stopped successfully",
                    "status": "stopped"
                }
            else:
                # Process already dead
                del _running_processes[source_id]
                return {
                    "success": True,
                    "message": f"Service {source_id} was not running",
                    "status": "stopped"
                }
        
        # Not in our tracking - try to find and kill by name
        config = get_service_config(source_id)
        if config and kill_process_by_name(config["service_file"]):
            return {
                "success": True,
                "message": f"Service {source_id} stopped (found by name)",
                "status": "stopped"
            }
        
        return {
            "success": True,
            "message": f"Service {source_id} was not running",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-sources/{source_id}/restart")
async def restart_data_source(source_id: str):
    """
    Restart a data source service using subprocess management.
    
    Args:
        source_id: Data source identifier
        
    Returns:
        dict: {
            "success": true,
            "message": "Service AllTraqAppAPI restarted successfully",
            "status": "running",
            "pid": 12345
        }
    """
    try:
        logger.info(f"Attempting to restart data source: {source_id}")
        
        # Stop first
        stop_result = await stop_data_source(source_id)
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Start again
        start_result = await start_data_source(source_id)
        
        if start_result["success"]:
            return {
                "success": True,
                "message": f"Service {source_id} restarted successfully",
                "status": "running",
                "pid": start_result.get("pid")
            }
        else:
            return {
                "success": False,
                "message": f"Service {source_id} failed to restart: {start_result['message']}",
                "status": "failed"
            }
            
    except Exception as e:
        logger.error(f"Error restarting {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))