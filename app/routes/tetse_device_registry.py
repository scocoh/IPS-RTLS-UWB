# Name: tetse_device_registry.py
# Version: 0.1.10
# Created: 250623
# Modified: 250704
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: TETSE Device Registry - Maps physical tags to virtual subjects with database persistence
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
TETSE Device Registry
Manages mapping between physical devices (23001) and virtual subjects (23001v/Eddy)
Uses database persistence with virtual device types and zones.

Virtual Device Ranges:
- Device IDs: 900-999 (e.g., "23001v")
- Device Type: 901 ("Virtual Tag")
- Zone IDs: 9000-9999 (e.g., 9901)
- Zone Type: 901 ("Virtual Subject Zone")
"""

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

import logging
import asyncpg
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from database.db import get_async_db_pool

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api/tetse/devices", tags=["tetse_device_registry"])

# Virtual device/zone ranges
VIRTUAL_DEVICE_TYPE = 901  # "Virtual Tag"
VIRTUAL_ZONE_TYPE = 901    # "Virtual Subject Zone"
VIRTUAL_DEVICE_RANGE = (900, 999)
VIRTUAL_ZONE_RANGE = (9000, 9999)

class DeviceMapping(BaseModel):
    physical_id: str  # e.g., "23001"
    virtual_id: str   # e.g., "900v"
    subject_name: str # e.g., "Eddy" - stored separately, not in x_nm_dev
    virtual_zone_id: int # e.g., 9902
    current_zone_id: Optional[int] = None

class CreateMappingRequest(BaseModel):
    physical_id: str
    subject_name: str
    campus_id: int = 422

async def get_maint_pool():
    """Get ParcoRTLSMaint database pool using centralized configuration"""
    server_host = get_server_host()
    db_configs = get_db_configs_sync()
    maint_config = db_configs['maint']
    conn_string = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"
    
    return await asyncpg.create_pool(
        conn_string,
        min_size=1,
        max_size=10
    )

async def get_next_virtual_device_id() -> str:
    """Generate next available virtual device ID in range 900-999"""
    pool = await get_maint_pool()
    async with pool.acquire() as conn:
        # Find highest virtual device ID - check existing virtual devices
        result = await conn.fetchval("""
            SELECT MAX(CAST(SUBSTRING(x_id_dev FROM '^([0-9]+)') AS INTEGER))
            FROM devices 
            WHERE i_typ_dev = $1 
            AND x_id_dev ~ '^[0-9]+v$'
            AND CAST(SUBSTRING(x_id_dev FROM '^([0-9]+)') AS INTEGER) BETWEEN $2 AND $3
        """, VIRTUAL_DEVICE_TYPE, VIRTUAL_DEVICE_RANGE[0], VIRTUAL_DEVICE_RANGE[1])
        
        if result is None:
            next_id = VIRTUAL_DEVICE_RANGE[0]
        else:
            next_id = result + 1
            
        if next_id > VIRTUAL_DEVICE_RANGE[1]:
            raise HTTPException(status_code=400, detail="Virtual device range exhausted")
            
        return f"{next_id}v"
    
    await pool.close()

async def get_next_virtual_zone_id() -> int:
    """Generate next available virtual zone ID in range 9000-9999"""
    pool = await get_maint_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval("""
            SELECT MAX(i_zn) 
            FROM zones 
            WHERE i_typ_zn = $1 
            AND i_zn BETWEEN $2 AND $3
        """, VIRTUAL_ZONE_TYPE, VIRTUAL_ZONE_RANGE[0], VIRTUAL_ZONE_RANGE[1])
        
        if result is None:
            return VIRTUAL_ZONE_RANGE[0]
        else:
            next_id = result + 1
            if next_id > VIRTUAL_ZONE_RANGE[1]:
                raise HTTPException(status_code=400, detail="Virtual zone range exhausted")
            return next_id
    
    await pool.close()

@router.post("/mapping", response_model=DeviceMapping)
async def create_device_mapping(request: CreateMappingRequest):
    """
    Create mapping between physical device and virtual subject
    
    Creates:
    - Virtual device in devices table
    - Virtual zone in zones table  
    - Returns mapping information
    """
    try:
        pool = await get_maint_pool()
        
        # Check if physical device exists
        async with pool.acquire() as conn:
            physical_device = await conn.fetchrow("""
                SELECT x_id_dev, i_typ_dev, x_nm_dev, zone_id
                FROM devices 
                WHERE x_id_dev = $1
            """, request.physical_id)
            
            if not physical_device:
                raise HTTPException(status_code=404, detail=f"Physical device {request.physical_id} not found")
        
        # Generate virtual IDs
        virtual_device_id = await get_next_virtual_device_id()
        virtual_zone_id = await get_next_virtual_zone_id()
        
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Create virtual zone
                await conn.execute("""
                    INSERT INTO zones (i_zn, x_nm_zn, i_typ_zn, i_pnt_zn)
                    VALUES ($1, $2, $3, $4)
                """, virtual_zone_id, f"Virtual Subject Zone - {request.subject_name}", 
                    VIRTUAL_ZONE_TYPE, request.campus_id)
                
                # Create virtual device - FIXED: store physical_id in x_nm_dev for mapping
                # Store subject_name in zone name for reference
                await conn.execute("""
                    INSERT INTO devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, f_log, zone_id)
                    VALUES ($1, $2, $3, NOW(), false, $4)
                """, virtual_device_id, VIRTUAL_DEVICE_TYPE, request.physical_id, virtual_zone_id)
        
        await pool.close()
        
        return DeviceMapping(
            physical_id=request.physical_id,
            virtual_id=virtual_device_id,
            subject_name=request.subject_name,
            virtual_zone_id=virtual_zone_id,
            current_zone_id=physical_device["zone_id"]
        )
        
    except Exception as e:
        logger.error(f"Error creating device mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mapping/{physical_id}", response_model=Optional[DeviceMapping])
async def get_device_mapping(physical_id: str):
    """Get mapping for physical device ID"""
    try:
        pool = await get_maint_pool()
        
        async with pool.acquire() as conn:
            # Find virtual device mapped to physical device - FIXED: proper mapping logic
            mapping = await conn.fetchrow("""
                SELECT 
                    p.x_id_dev as physical_id,
                    v.x_id_dev as virtual_id,
                    SUBSTRING(z.x_nm_zn FROM 'Virtual Subject Zone - (.*)') as subject_name,
                    v.zone_id as virtual_zone_id,
                    p.zone_id as current_zone_id
                FROM devices p
                LEFT JOIN devices v ON v.x_nm_dev = p.x_id_dev AND v.i_typ_dev = $1
                LEFT JOIN zones z ON z.i_zn = v.zone_id AND z.i_typ_zn = $3
                WHERE p.x_id_dev = $2
            """, VIRTUAL_DEVICE_TYPE, physical_id, VIRTUAL_ZONE_TYPE)
            
            if not mapping or not mapping["virtual_id"]:
                return None
                
        await pool.close()
        
        return DeviceMapping(**dict(mapping))
        
    except Exception as e:
        logger.error(f"Error getting device mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings", response_model=List[DeviceMapping])
async def get_all_mappings():
    """Get all device mappings"""
    try:
        pool = await get_maint_pool()
        
        async with pool.acquire() as conn:
            mappings = await conn.fetch("""
                SELECT 
                    p.x_id_dev as physical_id,
                    v.x_id_dev as virtual_id,
                    SUBSTRING(z.x_nm_zn FROM 'Virtual Subject Zone - (.*)') as subject_name,
                    v.zone_id as virtual_zone_id,
                    p.zone_id as current_zone_id
                FROM devices v
                JOIN devices p ON p.x_id_dev = v.x_nm_dev
                LEFT JOIN zones z ON z.i_zn = v.zone_id AND z.i_typ_zn = $2
                WHERE v.i_typ_dev = $1
                ORDER BY v.x_id_dev
            """, VIRTUAL_DEVICE_TYPE, VIRTUAL_ZONE_TYPE)
        
        await pool.close()
        
        return [DeviceMapping(**dict(mapping)) for mapping in mappings]
        
    except Exception as e:
        logger.error(f"Error getting all mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mapping/{physical_id}/zone")
async def update_subject_zone(physical_id: str, zone_id: int):
    """Update virtual subject's current zone based on physical device position"""
    try:
        pool = await get_maint_pool()
        
        async with pool.acquire() as conn:
            # Update virtual device zone
            result = await conn.execute("""
                UPDATE devices 
                SET zone_id = $1
                FROM devices p
                WHERE devices.x_nm_dev = p.x_id_dev 
                AND p.x_id_dev = $2
                AND devices.i_typ_dev = $3
            """, zone_id, physical_id, VIRTUAL_DEVICE_TYPE)
            
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail=f"No mapping found for device {physical_id}")
        
        await pool.close()
        
        return {"success": True, "message": f"Updated zone for {physical_id} to {zone_id}"}
        
    except Exception as e:
        logger.error(f"Error updating subject zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/mapping/{physical_id}")
async def delete_device_mapping(physical_id: str):
    """Delete device mapping and associated virtual resources"""
    try:
        pool = await get_maint_pool()
        
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Get virtual device info
                virtual_device = await conn.fetchrow("""
                    SELECT v.x_id_dev, v.zone_id
                    FROM devices v
                    JOIN devices p ON p.x_id_dev = v.x_nm_dev
                    WHERE p.x_id_dev = $1 AND v.i_typ_dev = $2
                """, physical_id, VIRTUAL_DEVICE_TYPE)
                
                if not virtual_device:
                    raise HTTPException(status_code=404, detail=f"No mapping found for {physical_id}")
                
                # Delete virtual device
                await conn.execute("""
                    DELETE FROM devices WHERE x_id_dev = $1
                """, virtual_device["x_id_dev"])
                
                # Delete virtual zone
                await conn.execute("""
                    DELETE FROM zones WHERE i_zn = $1 AND i_typ_zn = $2
                """, virtual_device["zone_id"], VIRTUAL_ZONE_TYPE)
        
        await pool.close()
        
        return {"success": True, "message": f"Deleted mapping for {physical_id}"}
        
    except Exception as e:
        logger.error(f"Error deleting mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))