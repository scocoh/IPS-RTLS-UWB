# Name: subject_registry.py
# Version: 0.1.2
# Created: 971201
# Modified: 250623
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: ParcoRTLS backend script - Database-driven subject registry using TETSE device registry with direct device table support
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: subject_registry.py
# Version: 0.1.2 - FIXED: Added direct database query for physical devices before API fallback
# v0.1.1 - Updated to use tetse_device_registry.py FastAPI endpoints instead of hardcoded subjects
# Created: 250615
# Modified: 250623
# Author: ParcoAdmin + QuantumSage AI
# Purpose: Map subject_id to live tag/device state for TETSE evaluations using database persistence.
# Status: Production

import logging
import httpx
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ==========================================================================================
# SUBJECT REGISTRY - DATABASE-DRIVEN VIA TETSE DEVICE REGISTRY + DIRECT DEVICE LOOKUP
# ==========================================================================================

TETSE_DEVICE_API_BASE = "http://localhost:8000/api/tetse/devices"

async def get_maint_pool():
    """Get ParcoRTLSMaint database pool"""
    return await asyncpg.create_pool(
        "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint",
        min_size=1,
        max_size=10
    )

async def get_subject_current_zone(subject_id: str) -> Optional[int]:
    """
    Returns current_zone_id for given subject_id.
    
    Supports both:
    - Physical device IDs (e.g., "23001") - queries devices table directly
    - Virtual subject names (e.g., "Eddy") - uses TETSE device registry
    
    FIXED: Now checks devices table first for physical devices before API calls.
    """
    try:
        # FIRST: Try direct database lookup for physical devices
        try:
            pool = await get_maint_pool()
            async with pool.acquire() as conn:
                device_record = await conn.fetchrow("""
                    SELECT x_id_dev, zone_id 
                    FROM devices 
                    WHERE x_id_dev = $1
                """, subject_id)
                
                if device_record:
                    zone_id = device_record["zone_id"]
                    logger.debug(f"Found physical device {subject_id} in zone {zone_id}")
                    await pool.close()
                    return zone_id
                    
            await pool.close()
            
        except Exception as db_error:
            logger.warning(f"Direct database lookup failed for {subject_id}: {str(db_error)}")
        
        # SECOND: Fall back to TETSE device registry API for virtual devices
        async with httpx.AsyncClient() as client:
            # Try as physical device ID in registry
            response = await client.get(f"{TETSE_DEVICE_API_BASE}/mapping/{subject_id}")
            
            if response.status_code == 200:
                mapping = response.json()
                if mapping:
                    logger.debug(f"Found mapping for physical device {subject_id}: {mapping}")
                    return mapping.get("current_zone_id")
            
            # Try as virtual subject name
            response = await client.get(f"{TETSE_DEVICE_API_BASE}/mappings")
            
            if response.status_code == 200:
                mappings = response.json()
                for mapping in mappings:
                    if mapping.get("subject_name") == subject_id:
                        logger.debug(f"Found mapping for subject name {subject_id}: {mapping}")
                        return mapping.get("current_zone_id")
            
            logger.warning(f"Subject {subject_id} not found in devices table or TETSE device registry.")
            return None
            
    except Exception as e:
        logger.error(f"Error in subject lookup: {str(e)}")
        return None

async def update_subject_zone(subject_id: str, new_zone_id: int):
    """
    Real-time state update for subject's current_zone_id.
    
    Updates both physical devices (devices table) and virtual devices (TETSE registry).
    Supports both physical device IDs and subject names.
    """
    try:
        # FIRST: Try to update physical device in devices table
        try:
            pool = await get_maint_pool()
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    UPDATE devices 
                    SET zone_id = $1 
                    WHERE x_id_dev = $2
                """, new_zone_id, subject_id)
                
                if result != "UPDATE 0":
                    logger.info(f"Updated physical device {subject_id} to zone {new_zone_id}")
                    await pool.close()
                    return
                    
            await pool.close()
            
        except Exception as db_error:
            logger.warning(f"Direct database update failed for {subject_id}: {str(db_error)}")
        
        # SECOND: Fall back to TETSE device registry for virtual devices
        async with httpx.AsyncClient() as client:
            # Try to update as physical device ID first
            response = await client.put(
                f"{TETSE_DEVICE_API_BASE}/mapping/{subject_id}/zone",
                params={"zone_id": new_zone_id}
            )
            
            if response.status_code == 200:
                logger.info(f"Updated subject {subject_id} to zone {new_zone_id}")
                return
            
            # If not found as physical device, try to find by subject name
            mappings_response = await client.get(f"{TETSE_DEVICE_API_BASE}/mappings")
            
            if mappings_response.status_code == 200:
                mappings = mappings_response.json()
                for mapping in mappings:
                    if mapping.get("subject_name") == subject_id:
                        physical_id = mapping.get("physical_id")
                        update_response = await client.put(
                            f"{TETSE_DEVICE_API_BASE}/mapping/{physical_id}/zone",
                            params={"zone_id": new_zone_id}
                        )
                        
                        if update_response.status_code == 200:
                            logger.info(f"Updated subject {subject_id} (physical {physical_id}) to zone {new_zone_id}")
                            return
            
            logger.warning(f"Cannot update unknown subject {subject_id}. No mapping found.")

    except Exception as e:
        logger.error(f"Error updating subject state: {str(e)}")

async def get_physical_to_virtual_mapping(physical_id: str) -> Optional[dict]:
    """
    Get complete mapping information for a physical device.
    Returns dict with physical_id, virtual_id, subject_name, zones.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TETSE_DEVICE_API_BASE}/mapping/{physical_id}")
            
            if response.status_code == 200:
                mapping = response.json()
                return mapping
            
            return None
            
    except Exception as e:
        logger.error(f"Error getting mapping for {physical_id}: {str(e)}")
        return None

async def create_subject_mapping(physical_id: str, subject_name: str, campus_id: int = 422) -> Optional[dict]:
    """
    Create new subject mapping through TETSE device registry.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TETSE_DEVICE_API_BASE}/mapping",
                json={
                    "physical_id": physical_id,
                    "subject_name": subject_name,
                    "campus_id": campus_id
                }
            )
            
            if response.status_code == 200:
                mapping = response.json()
                logger.info(f"Created subject mapping: {mapping}")
                return mapping
            else:
                logger.error(f"Failed to create mapping: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Error creating subject mapping: {str(e)}")
        return None