# Name: dashboard.py
# Version: 0.1.2
# Created: 250711
# Modified: 250712
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: FastAPI routes for ParcoRTLS Dashboard with dynamic device categories
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

from fastapi import APIRouter, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

# Database connection parameters for ParcoRTLSDashboard
DASHBOARD_DB_PARAMS = {
    "dbname": "ParcoRTLSDashboard",
    "user": "parcoadmin",
    "password": "parcoMCSE04106!",
    "host": "localhost",
    "port": "5432"
}

def get_dashboard_connection():
    """Get connection to ParcoRTLSDashboard database"""
    try:
        conn = psycopg2.connect(
            dbname=DASHBOARD_DB_PARAMS["dbname"],
            user=DASHBOARD_DB_PARAMS["user"],
            password=DASHBOARD_DB_PARAMS["password"],
            host=DASHBOARD_DB_PARAMS["host"],
            port=DASHBOARD_DB_PARAMS["port"]
        )
        return conn
    except Exception as e:
        logger.error(f"Dashboard database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@router.get("/metrics")
async def get_dashboard_metrics():
    """Get all dashboard metrics (tag counts, receiver counts, etc.)"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT metric_name, metric_value, metric_type, last_updated 
            FROM dashboard_metrics 
            ORDER BY metric_name
        """)
        
        metrics = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(metric) for metric in metrics]
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")

@router.get("/locations")
async def get_dashboard_locations():
    """Get all dashboard locations with their counts"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, location_name, location_type, display_order, is_active
            FROM dashboard_locations 
            WHERE is_active = true
            ORDER BY display_order, location_name
        """)
        
        locations = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(location) for location in locations]
    except Exception as e:
        logger.error(f"Error fetching dashboard locations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching locations: {str(e)}")

@router.get("/device_categories/{customer_id}")
async def get_device_categories(customer_id: int):
    """Get device categories for a specific customer"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                ddc.id, ddc.category_key, ddc.category_label, ddc.metric_name,
                ddc.display_order, ddc.icon_name, ddc.is_active,
                dm.metric_value
            FROM dashboard_device_categories ddc
            LEFT JOIN dashboard_metrics dm ON ddc.metric_name = dm.metric_name
            WHERE ddc.customer_id = %s AND ddc.is_active = true
            ORDER BY ddc.display_order, ddc.category_label
        """, (customer_id,))
        
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(category) for category in categories]
    except Exception as e:
        logger.error(f"Error fetching device categories for customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching device categories: {str(e)}")

@router.get("/customer_config/{customer_id}")
async def get_customer_config(customer_id: int):
    """Get customer configuration"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT customer_id, customer_name, dashboard_title, created_at, updated_at
            FROM dashboard_customer_config 
            WHERE customer_id = %s
        """, (customer_id,))
        
        config = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        return dict(config)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer config for {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching customer config: {str(e)}")

@router.post("/device_categories")
async def add_device_category(
    customer_id: int,
    category_key: str,
    category_label: str,
    metric_name: str,
    display_order: int = 0,
    icon_name: str = "device"
):
    """Add new device category for a customer"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO dashboard_device_categories 
            (customer_id, category_key, category_label, metric_name, display_order, icon_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, category_key, category_label, metric_name, display_order, icon_name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Device category '{category_label}' added successfully"}
    except Exception as e:
        logger.error(f"Error adding device category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding device category: {str(e)}")

@router.put("/device_categories/{category_id}")
async def update_device_category(
    category_id: int,
    category_label: Optional[str] = None,
    metric_name: Optional[str] = None,
    display_order: Optional[int] = None,
    icon_name: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Update device category"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if category_label is not None:
            update_fields.append("category_label = %s")
            values.append(category_label)
        if metric_name is not None:
            update_fields.append("metric_name = %s")
            values.append(metric_name)
        if display_order is not None:
            update_fields.append("display_order = %s")
            values.append(display_order)
        if icon_name is not None:
            update_fields.append("icon_name = %s")
            values.append(icon_name)
        if is_active is not None:
            update_fields.append("is_active = %s")
            values.append(is_active)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(category_id)
        
        query = f"""
            UPDATE dashboard_device_categories 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Device category {category_id} not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Device category {category_id} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating device category: {str(e)}")

@router.delete("/device_categories/{category_id}")
async def delete_device_category(category_id: int):
    """Delete device category (soft delete by setting is_active = false)"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dashboard_device_categories 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (category_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Device category {category_id} not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Device category {category_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting device category: {str(e)}")

@router.get("/activity")
async def get_dashboard_activity(limit: int = 50):
    """Get recent dashboard activity feed"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                da.id, da.activity_type, da.description, da.device_id, 
                da.severity, da.event_timestamp,
                dl.location_name
            FROM dashboard_activity da
            LEFT JOIN dashboard_locations dl ON da.location_id = dl.id
            ORDER BY da.event_timestamp DESC
            LIMIT %s
        """, (limit,))
        
        activity = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(item) for item in activity]
    except Exception as e:
        logger.error(f"Error fetching dashboard activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}")

@router.get("/autoclave")
async def get_dashboard_autoclave():
    """Get autoclave cycle data for the current year"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                dc.cycle_date, dc.cycle_count, dc.cycle_type,
                dl.location_name
            FROM dashboard_autoclave dc
            LEFT JOIN dashboard_locations dl ON dc.location_id = dl.id
            WHERE EXTRACT(YEAR FROM dc.cycle_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            ORDER BY dc.cycle_date
        """)
        
        autoclave_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(item) for item in autoclave_data]
    except Exception as e:
        logger.error(f"Error fetching autoclave data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching autoclave data: {str(e)}")

@router.get("/alerts")
async def get_dashboard_alerts():
    """Get dashboard alerts summary"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE alert_timestamp::date = CURRENT_DATE) as today_count,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM alert_timestamp) = EXTRACT(MONTH FROM CURRENT_DATE)
                                AND EXTRACT(YEAR FROM alert_timestamp) = EXTRACT(YEAR FROM CURRENT_DATE)) as month_count,
                COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM alert_timestamp) = EXTRACT(YEAR FROM CURRENT_DATE)) as year_count
            FROM dashboard_alerts
            WHERE status = 'active'
        """)
        
        alert_counts = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return dict(alert_counts) if alert_counts else {"today_count": 0, "month_count": 0, "year_count": 0}
    except Exception as e:
        logger.error(f"Error fetching alert counts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.get("/sensors")
async def get_dashboard_sensors():
    """Get current sensor readings"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                ds.sensor_id, ds.sensor_type, ds.reading_value, ds.unit_of_measure,
                ds.status, ds.last_reading,
                dl.location_name
            FROM dashboard_sensors ds
            LEFT JOIN dashboard_locations dl ON ds.location_id = dl.id
            ORDER BY ds.last_reading DESC
        """)
        
        sensors = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(sensor) for sensor in sensors]
    except Exception as e:
        logger.error(f"Error fetching sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sensors: {str(e)}")

@router.get("/overview/{customer_id}")
async def get_dashboard_overview(customer_id: int = 1):
    """Get complete dashboard overview data for a specific customer"""
    try:
        metrics = await get_dashboard_metrics()
        locations = await get_dashboard_locations()
        device_categories = await get_device_categories(customer_id)
        activity = await get_dashboard_activity(10)  # Limited for overview
        autoclave = await get_dashboard_autoclave()
        alerts = await get_dashboard_alerts()
        sensors = await get_dashboard_sensors()
        customer_config = await get_customer_config(customer_id)
        
        return {
            "customer_config": customer_config,
            "metrics": metrics,
            "locations": locations,
            "device_categories": device_categories,
            "recent_activity": activity,
            "autoclave_data": autoclave,
            "alert_summary": alerts,
            "sensor_readings": sensors,
            "last_updated": "2025-07-12T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard overview for customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching overview: {str(e)}")

@router.post("/metrics/{metric_name}")
async def update_dashboard_metric(metric_name: str, value: int):
    """Update a specific dashboard metric"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dashboard_metrics 
            SET metric_value = %s, last_updated = CURRENT_TIMESTAMP
            WHERE metric_name = %s
        """, (value, metric_name))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"Metric '{metric_name}' updated to {value}"}
    except Exception as e:
        logger.error(f"Error updating metric {metric_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating metric: {str(e)}")

@router.post("/activity")
async def add_dashboard_activity(
    activity_type: str,
    description: str,
    device_id: Optional[str] = None,
    location_id: Optional[int] = None,
    severity: str = "info"
):
    """Add new activity item to dashboard feed"""
    try:
        conn = get_dashboard_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO dashboard_activity (activity_type, description, device_id, location_id, severity)
            VALUES (%s, %s, %s, %s, %s)
        """, (activity_type, description, device_id, location_id, severity))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Activity added successfully"}
    except Exception as e:
        logger.error(f"Error adding activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding activity: {str(e)}")