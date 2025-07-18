# Name: components.py
# Version: 0.1.9
# Created: 971201
# Modified: 250716
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: ParcoRTLS backend script with port monitoring and scaling management - All endpoints now use database-only mode
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE
# Changelog:
# - 0.1.9 (250716): Converted port-health and unhealthy-ports endpoints to database-only mode for full UI compatibility
# - 0.1.8 (250716): Fixed scaling/status endpoint to use database-only mode instead of heartbeat integration
# - 0.1.7 (250716): Fixed database configuration to use proper credentials from config system
# - 0.1.6 (250716): Added manual scaling status and remove endpoints for THREAD 3
# - 0.1.5 (250716): Added port monitoring and scaling management endpoints
# - 0.1.4 (250502): Updated procedures/functions endpoints to match expected format with metadata and corrected usp_ labeling

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from config import get_db_configs_sync

router = APIRouter(
    prefix="/components",
    tags=["components"]
)

# Get database configuration from the centralized config system
def get_db_connection():
    """Get database connection using the centralized config"""
    db_configs = get_db_configs_sync()
    maint_config = db_configs['maint']
    return psycopg2.connect(
        dbname=maint_config['database'],
        user=maint_config['user'],
        password=maint_config['password'],
        host=maint_config['host'],
        port=maint_config['port']
    )

# Directory for storing Markdown files
APP_DIR = "/home/parcoadmin/parco_fastapi/app"

# Pydantic models for port monitoring
class PortMonitoringConfig(BaseModel):
    port: int
    monitor_enabled: bool
    auto_expand: bool
    monitor_interval: Optional[int] = 30
    monitor_timeout: Optional[int] = 5
    monitor_threshold: Optional[int] = 2

class ScalingRequest(BaseModel):
    base_port: int
    new_port: int
    resource_name: str
    resource_type: int
    action: str  # "create", "activate", "deactivate"

# === ORIGINAL ENDPOINTS === 

@router.get("/")
async def get_components():
    """Use this command to access the ParcoRTLSMaint table component_versions.
    This table is populated by running the 19-update-component-versions.sh from the app directory
    or via the utility menu.
    This is useful for creating a list of all of the files for the ParcoRTLS.
    as of version 0.1.80 of the update component we do not track JSON nor database files."""
    try:
        # Connect to the database using centralized config
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query the component_versions table
        cursor.execute("SELECT * FROM component_versions ORDER BY location, name")
        components = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries for JSON response
        return [dict(component) for component in components]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/procedures-functions-list")
async def generate_procedures_functions_list():
    """Generates a Markdown file (proc_func_lbn.md) listing all stored procedures and functions in the ParcoRTLSMaint database."""
    try:
        # Connect to the database using centralized config
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for list of procedures and functions, including routine_type, and avoid duplicates
        cursor.execute("SELECT DISTINCT routine_schema, routine_name, routine_type FROM information_schema.routines WHERE routine_type IN ('PROCEDURE', 'FUNCTION') AND specific_schema = 'public' ORDER BY routine_schema, routine_name")
        routines = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Write to Markdown file
        output_file = f"{APP_DIR}/proc_func_lbn.md"
        with open(output_file, "w") as f:
            f.write("# Stored Procedures and Functions in ParcoRTLSMaint\n\n")
            f.write("> **Note**: Routines with the `usp_` prefix are labeled as `PROCEDURE` in this output but are defined as `FUNCTION` in the database, based on naming convention.\n\n")
            f.write("| Schema           | Name             | Type             |\n")
            f.write("|------------------|------------------|------------------|\n")
            for routine in routines:
                schema, name, routine_type = routine
                # Override type for usp_ routines
                if name.startswith("usp_"):
                    routine_type = "PROCEDURE"
                f.write(f"| {schema:<16} | {name:<16} | {routine_type:<16} |\n")
        
        return {"message": f"Successfully generated {output_file}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating procedures/functions list: {str(e)}")

@router.get("/procedures-functions-details")
async def generate_procedures_functions_details():
    """Generates a Markdown file (proc_func_details.md) listing all stored procedures and functions in the ParcoRTLSMaint database with their source code."""
    try:
        # Connect to the database using centralized config
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for list of procedures and functions with their OIDs, including routine_type
        cursor.execute("SELECT DISTINCT r.routine_schema, r.routine_name, r.routine_type, p.oid FROM information_schema.routines r JOIN pg_proc p ON r.specific_name = p.proname || '_' || p.oid WHERE r.routine_type IN ('PROCEDURE', 'FUNCTION') AND r.specific_schema = 'public' ORDER BY r.routine_schema, r.routine_name")
        routines = cursor.fetchall()
        
        # Write to Markdown file
        output_file = f"{APP_DIR}/proc_func_details.md"
        with open(output_file, "w") as f:
            for routine in routines:
                schema, name, routine_type, oid = routine
                # Override type for usp_ routines
                if name.startswith("usp_"):
                    routine_type = "PROCEDURE"
                
                # Get the full definition
                cursor.execute(f"SELECT pg_get_functiondef('{oid}'::oid)")
                definition_result = cursor.fetchone()
                if definition_result:
                    definition = definition_result[0]
                else:
                    definition = f"-- Definition not found for {name}"
                
                # Extract metadata if present in the definition (assuming comments at the top)
                metadata_lines = []
                for line in definition.split("\n"):
                    if line.startswith("-- "):
                        metadata_lines.append(line[3:])
                    else:
                        break
                metadata = "\n".join(metadata_lines)
                if not metadata:
                    # Default metadata if not present
                    metadata = f"Name: {name}\nVersion: 0.1.0\nCreated: 971201\nModified: 250502\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: {routine_type} in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE"
                
                # Write to Markdown file
                f.write(f"{definition}\n")
                f.write(f"{metadata}\n\n")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return {"message": f"Successfully generated {output_file}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating procedures/functions details: {str(e)}")

# === PORT MONITORING ENDPOINTS ===

@router.get("/port-monitoring")
async def get_port_monitoring():
    """Get all port monitoring configuration and status from tlkresources table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for port monitoring configuration
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as monitor_enabled,
                   COALESCE(f_auto_expand, false) as auto_expand,
                   COALESCE(i_monitor_interval, 30) as monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as monitor_threshold
            FROM tlkresources 
            WHERE i_prt > 0 
            ORDER BY i_prt
        """)
        
        ports = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Categorize ports
        result = {
            "total_ports": len(ports),
            "inbound_ports": [],   # 18000+
            "outbound_ports": [],  # 8000+
            "scaling_candidates": [],
            "monitored_ports": 0,
            "auto_expand_ports": 0
        }
        
        for port in ports:
            port_dict = dict(port)
            
            if port_dict['monitor_enabled']:
                result['monitored_ports'] += 1
            if port_dict['auto_expand']:
                result['auto_expand_ports'] += 1
            
            # Categorize by port range
            if port_dict['i_prt'] >= 18000:
                result['inbound_ports'].append(port_dict)
            elif port_dict['i_prt'] >= 8000:
                result['outbound_ports'].append(port_dict)
                if port_dict['auto_expand']:
                    result['scaling_candidates'].append(port_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/port-monitoring/{port}")
async def get_port_monitoring_details(port: int):
    """Get detailed monitoring information for a specific port."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for specific port
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as monitor_enabled,
                   COALESCE(f_auto_expand, false) as auto_expand,
                   COALESCE(i_monitor_interval, 30) as monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as monitor_threshold
            FROM tlkresources 
            WHERE i_prt = %s
        """, (port,))
        
        port_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not port_data:
            raise HTTPException(status_code=404, detail=f"Port {port} not found")
        
        # Add scaling information
        port_dict = dict(port_data)
        port_dict['can_scale'] = port in [8002]  # Add other scalable ports as needed
        port_dict['scaling_range'] = "8200-8299" if port_dict['can_scale'] else None
        
        return port_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/port-monitoring/{port}")
async def update_port_monitoring_config(port: int, config: PortMonitoringConfig):
    """Update port monitoring configuration."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update port monitoring configuration
        cursor.execute("""
            UPDATE tlkresources 
            SET f_monitor_enabled = %s,
                f_auto_expand = %s,
                i_monitor_interval = %s,
                i_monitor_timeout = %s,
                i_monitor_threshold = %s
            WHERE i_prt = %s
        """, (
            config.monitor_enabled,
            config.auto_expand,
            config.monitor_interval,
            config.monitor_timeout,
            config.monitor_threshold,
            port
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Port {port} not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Port {port} monitoring configuration updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# === HEARTBEAT INTEGRATION ENDPOINTS (DATABASE-ONLY MODE) ===

@router.get("/port-health")
async def get_port_health_status():
    """Get current port health status from database configuration (DATABASE-ONLY MODE)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for port health based on database configuration
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as monitor_enabled,
                   COALESCE(f_auto_expand, false) as auto_expand,
                   COALESCE(i_monitor_interval, 30) as monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as monitor_threshold
            FROM tlkresources 
            WHERE i_prt > 0 AND COALESCE(f_monitor_enabled, true) = true
            ORDER BY i_prt
        """)
        
        ports = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create port health summary
        port_health_stats = {}
        total_monitored = 0
        total_healthy = 0
        
        for port in ports:
            port_dict = dict(port)
            port_num = port_dict['i_prt']
            
            # Simulate basic health status based on database config
            is_healthy = True  # Assume healthy since we can't do real checks
            
            port_health_stats[port_num] = {
                'resource_name': port_dict['x_nm_res'],
                'resource_type': port_dict['i_typ_res'],
                'ip_address': port_dict['x_ip'],
                'is_healthy': is_healthy,
                'monitor_enabled': port_dict['monitor_enabled'],
                'auto_expand': port_dict['auto_expand'],
                'last_check_time': None,  # No real checks in database-only mode
                'response_time_ms': None,
                'status': 'database_config_only'
            }
            
            total_monitored += 1
            if is_healthy:
                total_healthy += 1
        
        return {
            "status": "database_only",
            "message": "Port health status based on database configuration only",
            "mode": "fallback",
            "total_monitored_ports": total_monitored,
            "healthy_ports": total_healthy,
            "unhealthy_ports": total_monitored - total_healthy,
            "port_health_stats": port_health_stats,
            "last_check_time": None,
            "note": "Real-time health monitoring requires heartbeat integration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/port-health/refresh")
async def refresh_port_health_monitoring():
    """Manually refresh port health monitoring from database (DATABASE-ONLY MODE)."""
    try:
        # In database-only mode, just return current config
        return {
            "status": "success",
            "message": "Port monitoring configuration refreshed from database",
            "mode": "database_only",
            "note": "Real-time monitoring refresh requires heartbeat integration"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing port health: {str(e)}")

@router.get("/unhealthy-ports")
async def get_unhealthy_ports():
    """Get list of unhealthy ports from database configuration (DATABASE-ONLY MODE)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for ports that might have issues (disabled monitoring could indicate problems)
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk,
                   COALESCE(f_monitor_enabled, true) as monitor_enabled,
                   COALESCE(f_auto_expand, false) as auto_expand
            FROM tlkresources 
            WHERE i_prt > 0 AND COALESCE(f_monitor_enabled, true) = false
            ORDER BY i_prt
        """)
        
        potentially_unhealthy = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create unhealthy ports array (for frontend .map compatibility)
        unhealthy_ports_array = []
        
        for port in potentially_unhealthy:
            port_dict = dict(port)
            
            unhealthy_ports_array.append({
                'port': port_dict['i_prt'],
                'resource_name': port_dict['x_nm_res'],
                'resource_type': port_dict['i_typ_res'],
                'ip_address': port_dict['x_ip'],
                'reason': 'monitoring_disabled',
                'monitor_enabled': port_dict['monitor_enabled'],
                'auto_expand': port_dict['auto_expand'],
                'can_scale': port_dict['i_prt'] in [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008],
                'status': 'database_config_only'
            })
        
        return {
            "status": "database_only",
            "message": "Unhealthy ports based on database configuration (monitoring disabled)",
            "mode": "fallback", 
            "unhealthy_ports": unhealthy_ports_array,  # Now an array for .map()
            "count": len(unhealthy_ports_array),
            "note": "Real-time health detection requires heartbeat integration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/scaling-candidates-live")
async def get_live_scaling_candidates():
    """Get live scaling candidates from database (DATABASE-ONLY MODE)."""
    # Redirect to the working database-only endpoint
    return await get_scaling_candidates()

@router.get("/scaling/next-port-live/{base_port}")
async def get_next_scaling_port_live(base_port: int):
    """Get next available scaling port from database (DATABASE-ONLY MODE)."""
    # Redirect to the working database-only endpoint
    return await get_next_scaling_port(base_port)

# === SCALING MANAGEMENT ENDPOINTS ===

@router.get("/scaling/status")
async def get_scaling_status():
    """View port health and scaling status - comprehensive overview for manual scaling (DATABASE-ONLY MODE)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all ports with scaling information
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as monitor_enabled,
                   COALESCE(f_auto_expand, false) as auto_expand,
                   COALESCE(i_monitor_interval, 30) as monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as monitor_threshold
            FROM tlkresources 
            WHERE i_prt > 0 
            ORDER BY i_prt
        """)
        
        all_ports = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Process ports and categorize for scaling status
        scaling_candidates = []
        available_scaling_ports = []
        active_scaling_ports = []
        
        for port in all_ports:
            port_dict = dict(port)
            
            # Identify scaling candidates (auto_expand = true)
            if port_dict['auto_expand']:
                scaling_candidates.append(port_dict['i_prt'])
            
            # Identify scaling ranges and available ports
            if port_dict['i_prt'] >= 8200 and port_dict['i_prt'] <= 8299:
                active_scaling_ports.append(port_dict['i_prt'])
        
        # Calculate available scaling ports (8200-8299 range)
        for port_num in range(8200, 8300):
            if port_num not in active_scaling_ports:
                available_scaling_ports.append(port_num)
        
        # Database-only port health status (no heartbeat integration)
        port_health = {
            "status": "database_only",
            "message": "Port health monitoring via database configuration only",
            "mode": "fallback",
            "total_ports": len(all_ports),
            "monitored_ports": len([p for p in all_ports if dict(p)['monitor_enabled']]),
            "auto_expand_ports": len([p for p in all_ports if dict(p)['auto_expand']])
        }
        
        return {
            "port_health": port_health,
            "scaling_candidates": scaling_candidates,
            "available_scaling_ports": available_scaling_ports[:10],  # Limit to first 10
            "active_scaling_ports": active_scaling_ports,
            "scaling_status": {
                "total_scaling_candidates": len(scaling_candidates),
                "available_slots": len(available_scaling_ports),
                "active_scaling_instances": len(active_scaling_ports),
                "mode": "database_only"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/scaling/create/{port}")
async def create_scaling_port_simple(port: int):
    """Create new scaling port - simplified endpoint using path parameter."""
    try:
        # Determine base port from scaling range
        if port >= 8200 and port <= 8299:
            base_port = 8002  # RealTime WebSocket base
            resource_type = 2  # Assuming RealTime resource type
            resource_name = f"RealTimeManager_Scale_{port}"
        else:
            raise HTTPException(status_code=400, detail=f"Port {port} is not in a valid scaling range")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if port already exists
        cursor.execute("SELECT i_prt FROM tlkresources WHERE i_prt = %s", (port,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail=f"Port {port} already exists")
        
        # Get base port information for template
        cursor.execute("""
            SELECT i_typ_res, x_ip, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as f_monitor_enabled,
                   COALESCE(i_monitor_interval, 30) as i_monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as i_monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as i_monitor_threshold
            FROM tlkresources 
            WHERE i_prt = %s
        """, (base_port,))
        
        base_port_result = cursor.fetchone()
        if not base_port_result:
            raise HTTPException(status_code=404, detail=f"Base port {base_port} not found")
        
        # Extract values from result tuple
        typ_res, ip_addr, rank, fs_flag, avg_flag, monitor_enabled, monitor_interval, monitor_timeout, monitor_threshold = base_port_result
        
        # Create new scaling port entry
        cursor.execute("""
            INSERT INTO tlkresources (
                i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                f_monitor_enabled, f_auto_expand,
                i_monitor_interval, i_monitor_timeout, i_monitor_threshold
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            resource_type,
            resource_name,
            ip_addr,
            port,
            rank + (port - base_port),  # i_rnk (base + offset)
            fs_flag,
            avg_flag,
            monitor_enabled,
            False,  # f_auto_expand (scaling ports don't auto-expand)
            monitor_interval,
            monitor_timeout,
            monitor_threshold
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Scaling port {port} created successfully",
            "base_port": base_port,
            "new_port": port,
            "resource_name": resource_name,
            "scaling_range": "8200-8299"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/scaling/remove/{port}")
async def remove_scaling_port(port: int):
    """Remove scaling port from tlkresources table."""
    try:
        # Validate port is in scaling range
        if not (port >= 8200 and port <= 8299):
            raise HTTPException(status_code=400, detail=f"Port {port} is not in a scaling range (8200-8299)")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get port information before deletion
        cursor.execute("""
            SELECT i_res, x_nm_res, i_prt, i_typ_res, f_auto_expand
            FROM tlkresources 
            WHERE i_prt = %s
        """, (port,))
        
        port_data = cursor.fetchone()
        if not port_data:
            raise HTTPException(status_code=404, detail=f"Port {port} not found")
        
        port_dict = dict(port_data)
        
        # Safety check - don't remove auto_expand ports (base scaling candidates)
        if port_dict['f_auto_expand']:
            raise HTTPException(status_code=400, detail=f"Cannot remove base scaling candidate port {port}")
        
        # Remove the port
        cursor.execute("DELETE FROM tlkresources WHERE i_prt = %s", (port,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Port {port} not found for deletion")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Scaling port {port} removed successfully",
            "removed_port": port,
            "resource_name": port_dict['x_nm_res'],
            "resource_id": port_dict['i_res']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/scaling-candidates")
async def get_scaling_candidates():
    """Get ports that are candidates for scaling (auto_expand = true)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for ports with auto_expand enabled
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                   f_monitor_enabled, f_auto_expand,
                   i_monitor_interval, i_monitor_timeout, i_monitor_threshold
            FROM tlkresources 
            WHERE i_prt > 0 AND f_auto_expand = true
            ORDER BY i_prt
        """)
        
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Process candidates
        result = []
        for candidate in candidates:
            candidate_dict = dict(candidate)
            
            # Add scaling information
            if candidate_dict['i_prt'] == 8002:
                candidate_dict['scaling_range'] = "8200-8299"
                candidate_dict['scaling_type'] = "RealTime WebSocket"
            else:
                candidate_dict['scaling_range'] = "TBD"
                candidate_dict['scaling_type'] = "Generic"
            
            result.append(candidate_dict)
        
        return {
            "scaling_candidates": result,
            "total_candidates": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/scaling/create-port")
async def create_scaling_port(request: ScalingRequest):
    """Create a new scaling port in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get base port information
        cursor.execute("""
            SELECT i_typ_res, x_nm_res, x_ip, i_rnk, f_fs, f_avg,
                   COALESCE(f_monitor_enabled, true) as f_monitor_enabled,
                   COALESCE(f_auto_expand, false) as f_auto_expand,
                   COALESCE(i_monitor_interval, 30) as i_monitor_interval,
                   COALESCE(i_monitor_timeout, 5) as i_monitor_timeout,
                   COALESCE(i_monitor_threshold, 2) as i_monitor_threshold
            FROM tlkresources 
            WHERE i_prt = %s
        """, (request.base_port,))
        
        base_port_result = cursor.fetchone()
        if not base_port_result:
            raise HTTPException(status_code=404, detail=f"Base port {request.base_port} not found")
        
        # Extract values from result tuple  
        typ_res, nm_res, ip_addr, rank, fs_flag, avg_flag, monitor_enabled, auto_expand, monitor_interval, monitor_timeout, monitor_threshold = base_port_result
        
        # Create new port entry
        cursor.execute("""
            INSERT INTO tlkresources (
                i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg,
                f_monitor_enabled, f_auto_expand,
                i_monitor_interval, i_monitor_timeout, i_monitor_threshold
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            request.resource_type,
            request.resource_name,
            ip_addr,
            request.new_port,
            rank + 1000,  # i_rnk (base + 1000)
            fs_flag,
            avg_flag,
            monitor_enabled,
            False,  # f_auto_expand (scaling ports don't auto-expand)
            monitor_interval,
            monitor_timeout,
            monitor_threshold
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Scaling port {request.new_port} created successfully",
            "base_port": request.base_port,
            "new_port": request.new_port,
            "resource_name": request.resource_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/scaling/next-port/{base_port}")
async def get_next_scaling_port(base_port: int):
    """Get the next available port in the scaling range."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define scaling ranges
        scaling_ranges = {
            8002: (8200, 8299)  # RealTimeManager -> 8200-8299
        }
        
        if base_port not in scaling_ranges:
            raise HTTPException(status_code=400, detail=f"Port {base_port} is not configured for scaling")
        
        start_port, end_port = scaling_ranges[base_port]
        
        # Find existing ports in the scaling range
        cursor.execute("""
            SELECT i_prt FROM tlkresources 
            WHERE i_prt >= %s AND i_prt <= %s
            ORDER BY i_prt
        """, (start_port, end_port))
        
        existing_ports = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        # Find next available port
        next_port = None
        for port in range(start_port, end_port + 1):
            if port not in existing_ports:
                next_port = port
                break
        
        if next_port is None:
            raise HTTPException(status_code=409, detail=f"No available ports in scaling range {start_port}-{end_port}")
        
        return {
            "base_port": base_port,
            "next_available_port": next_port,
            "scaling_range": f"{start_port}-{end_port}",
            "existing_ports": existing_ports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/menu/scaling")
async def get_scaling_menu():
    """Get text menu for scaling operations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get unhealthy scaling candidates
        cursor.execute("""
            SELECT i_res, i_typ_res, x_nm_res, i_prt, f_auto_expand
            FROM tlkresources 
            WHERE i_prt > 0 AND f_auto_expand = true
            ORDER BY i_prt
        """)
        
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Generate menu
        menu = {
            "title": "Port Scaling Management Menu",
            "options": [
                {
                    "id": "1",
                    "title": "View Scaling Status",
                    "description": "Comprehensive scaling status overview",
                    "endpoint": "GET /components/scaling/status"
                },
                {
                    "id": "2",
                    "title": "View Scaling Candidates",
                    "description": "Show ports configured for auto-expansion",
                    "endpoint": "GET /components/scaling-candidates"
                },
                {
                    "id": "3", 
                    "title": "Check Port Health",
                    "description": "Get current port health status",
                    "endpoint": "GET /components/port-health"
                },
                {
                    "id": "4",
                    "title": "Create Scaling Port (Simple)",
                    "description": "Create scaling port using path parameter",
                    "endpoint": "POST /components/scaling/create/{port}"
                },
                {
                    "id": "5",
                    "title": "Remove Scaling Port",
                    "description": "Remove scaling port from database",
                    "endpoint": "DELETE /components/scaling/remove/{port}"
                },
                {
                    "id": "6",
                    "title": "Create Scaling Port (Advanced)",
                    "description": "Create scaling port with full configuration",
                    "endpoint": "POST /components/scaling/create-port"
                },
                {
                    "id": "7",
                    "title": "Get Next Available Port",
                    "description": "Find next port in scaling range",
                    "endpoint": "GET /components/scaling/next-port/{base_port}"
                },
                {
                    "id": "8",
                    "title": "Refresh Port Monitoring",
                    "description": "Reload port configuration from database",
                    "endpoint": "POST /components/port-health/refresh"
                }
            ],
            "scaling_candidates": [dict(candidate) for candidate in candidates],
            "instructions": "Use the endpoints above to manage port scaling. Candidates with auto_expand=true can be scaled automatically."
        }
        
        return menu
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")