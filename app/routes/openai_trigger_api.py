# Name: openai_trigger_api.py
# Version: 0.4.0
# Created: 250617
# Modified: 250705
# Author: ParcoAdmin + QuantumSage AI
# Modified By: ParcoAdmin + Claude
# Purpose: Enhanced TETSE Rule Management with delete functionality, proximity conditions, layered triggers, and zone transitions
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# Version: 0.4.0 - Added delete_tetse_rule and delete_tetse_rules endpoints for rule deletion, bumped from 0.3.3
# Version: 0.3.3 - Added get_tetse_rules endpoint for TETSE to Triggers tab
# Version: 0.3.1 - Added get_tetse_rules endpoint for TETSE to Triggers tab


"""
/home/parcoadmin/parco_fastapi/app/routes/openai_trigger_api.py
# Version: 0.4.0 - Enhanced TETSE rule management with delete functionality and improved error handling
# Previous: 0.3.0 - Enhanced rule creation with proximity conditions, layered triggers, zone transitions, and backward compatibility
# Previous: 0.2.7 - Fixed database pool routing: data_pool for tlk_rules (ParcoRTLSData), maint_pool for zones (ParcoRTLSMaint)
# Previous: 0.2.6 - Pass maint_pool to adapt_rulebuilder_to_tetse
# Previous: 0.2.5 - Fixed zone validation to use 'zones' in ParcoRTLSMaint
# Previous: 0.2.4 - Improved parse_natural_language validation
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

# Import centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host, get_db_configs_sync

import logging
import asyncpg
import json
import re
import asyncio
import time
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
from typing import List
from database.db import get_async_db_pool
from .tetse_rule_interpreter import parse_natural_language
from .tetse_rule_adapter import adapt_rulebuilder_to_tetse
from .llm_bridge import ask_openai
from .mqtt_actions import MQTTClient
from manager.line_limited_logging import LineLimitedFileHandler

LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("manager.openai_trigger_api")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "openai_trigger_api.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

router = APIRouter(tags=["tetse_ai"])

# Database connections using centralized configuration
server_host = get_server_host()
db_configs = get_db_configs_sync()
data_config = db_configs['data']
maint_config = db_configs['maint']
MAINT_CONN_STRING = f"postgresql://{data_config['user']}:{data_config['password']}@{server_host}:{data_config['port']}/{data_config['database']}"
MAINT_DB_NAME = maint_config['database']

class RuleInput(BaseModel):
    rule_text: str
    campus_id: str
    subject_id: str | None = None
    zone: str | None = None
    duration_sec: int | None = None
    action: str | None = None
    verbose: bool = True

class DeleteRulesInput(BaseModel):
    rule_ids: List[int]

async def get_maint_db_pool():
    """
    Create a connection pool for ParcoRTLSMaint database using centralized configuration.
    """
    server_host = get_server_host()
    db_configs = get_db_configs_sync()
    maint_config = db_configs['maint']
    conn_string = f"postgresql://{maint_config['user']}:{maint_config['password']}@{server_host}:{maint_config['port']}/{maint_config['database']}"
    
    return await asyncpg.create_pool(
        conn_string,
        min_size=1,
        max_size=5
    )

async def get_data_db_pool():
    """
    Create a connection pool for ParcoRTLSData database.
    """
    return await get_async_db_pool("data")

async def handle_zone_entry_monitoring_rule(parsed_rule, input_data, data_pool, maint_pool):
    """
    Handle zone entry monitoring rules - creates zone-based triggers for device entry detection
    """
    try:
        subject_id = parsed_rule["subject_id"]
        zone = parsed_rule["zone"]
        device_types = parsed_rule["device_types"]
        action = parsed_rule["action"]
        
        # Resolve zone using existing zone resolution system
        from .tetse_rule_adapter import resolve_zone_for_rule
        zone_info = await resolve_zone_for_rule(zone, input_data.campus_id, maint_pool)
        
        if not zone_info:
            raise HTTPException(status_code=400, detail=f"Could not resolve zone: {zone}")
        
        # Create rule name with timestamp
        rule_name = f"zone_entry_{subject_id}_{int(time.time())}"
        
        # Store in tlk_rules table
        conditions = {
            "rule_type": "zone_entry_monitoring",
            "subject_id": subject_id,
            "zone": zone_info["zone_name"],
            "zone_id": zone_info["zone_id"],
            "device_types": device_types,
            "trigger_direction": 4  # On Enter
        }
        
        actions = {
            "type": action,
            "message": f"Zone entry detected for {subject_id} in {zone_info['zone_name']}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        async with data_pool.acquire() as conn:
            rule_id = await conn.fetchval(
                """
                INSERT INTO tlk_rules (name, conditions, actions, rule_type, created_by, updated_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                rule_name,
                json.dumps(conditions),
                json.dumps(actions),
                "zone_entry_monitoring",
                "parcoadmin",
                "parcoadmin"
            )
        
        logger.info(f"Successfully created zone entry monitoring rule ID {rule_id}")
        
        return {
            "success": True,
            "message": "Zone entry monitoring rule created successfully",
            "rule_id": rule_id,
            "rule_type": "zone_entry_monitoring",
            "conditions": conditions,
            "actions": actions,
            "note": "Zone entry rules can be converted to zone-based triggers for real-time monitoring"
        }
        
    except Exception as e:
        logger.error(f"Error creating zone entry monitoring rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create zone entry monitoring rule: {str(e)}")

@router.get("/get_tetse_rules")
async def get_tetse_rules(data_pool: asyncpg.Pool = Depends(get_data_db_pool)):
    """
    Fetch all TETSE rules from tlk_rules table for conversion to portable triggers.
    
    Returns:
        list: Array of TETSE rules with id, name, rule_type, conditions, and parsed fields
    """
    try:
        logger.info("Fetching TETSE rules from tlk_rules table")
        
        # Query all enabled rules from tlk_rules table in ParcoRTLSData
        query = """
            SELECT id, name, rule_type, conditions, actions, is_enabled, created_at
            FROM tlk_rules 
            WHERE is_enabled = TRUE
            ORDER BY created_at DESC
        """
        
        async with data_pool.acquire() as conn:
            rows = await conn.fetch(query)
            
        tetse_rules = []
        for row in rows:
            try:
                # Parse conditions JSON
                conditions = row["conditions"]
                if isinstance(conditions, str):
                    conditions = json.loads(conditions)
                
                # Extract key fields from conditions
                rule_type = conditions.get("rule_type", "zone_stay")
                subject_id = conditions.get("subject_id")
                
                # Build rule object
                rule = {
                    "id": row["id"],
                    "name": row["name"],
                    "rule_type": rule_type,
                    "subject_id": subject_id,
                    "is_enabled": row["is_enabled"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "conditions": conditions,
                    "raw_conditions": row["conditions"]  # Keep original for debugging
                }
                
                # Add type-specific fields for display
                if rule_type == "proximity_condition":
                    rule["proximity_distance"] = conditions.get("proximity_distance", 6.0)
                    rule["proximity_target"] = conditions.get("proximity_target")
                    rule["condition"] = conditions.get("condition")
                elif rule_type == "zone_transition":
                    rule["from_zone"] = conditions.get("from_zone")
                    rule["to_zone"] = conditions.get("to_zone")
                elif rule_type == "layered_trigger":
                    rule["from_condition"] = conditions.get("from_condition")
                    rule["to_condition"] = conditions.get("to_condition")
                elif rule_type == "zone_stay":
                    rule["zone"] = conditions.get("zone")
                    rule["duration_sec"] = conditions.get("duration_sec", 600)
                
                tetse_rules.append(rule)
                logger.debug(f"Processed TETSE rule {row['id']}: {rule['name']} ({rule_type})")
                
            except Exception as parse_error:
                logger.error(f"Failed to parse TETSE rule {row['id']}: {str(parse_error)}")
                # Include failed rules with error info
                tetse_rules.append({
                    "id": row["id"],
                    "name": row["name"],
                    "rule_type": "parse_error",
                    "subject_id": "ERROR",
                    "error": str(parse_error),
                    "raw_conditions": row["conditions"]
                })
        
        logger.info(f"Successfully fetched {len(tetse_rules)} TETSE rules")
        return tetse_rules
        
    except Exception as e:
        logger.error(f"Error fetching TETSE rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch TETSE rules: {str(e)}")

@router.delete("/delete_tetse_rule/{rule_id}")
async def delete_tetse_rule(rule_id: int, data_pool: asyncpg.Pool = Depends(get_data_db_pool)):
    """
    Delete a single TETSE rule from tlk_rules table by ID.
    
    Args:
        rule_id: The ID of the rule to delete
        
    Returns:
        dict: Success message with deleted rule information
        
    Raises:
        HTTPException: If rule not found or deletion fails
    """
    try:
        logger.info(f"Attempting to delete TETSE rule {rule_id}")
        
        async with data_pool.acquire() as conn:
            # First check if rule exists and get its info
            rule_info = await conn.fetchrow(
                "SELECT id, name, rule_type FROM tlk_rules WHERE id = $1",
                rule_id
            )
            
            if not rule_info:
                logger.warning(f"TETSE rule {rule_id} not found")
                raise HTTPException(status_code=404, detail=f"TETSE rule {rule_id} not found")
            
            # Delete the rule
            deleted_count = await conn.execute(
                "DELETE FROM tlk_rules WHERE id = $1",
                rule_id
            )
            
            # Check if deletion was successful
            if deleted_count == "DELETE 0":
                logger.error(f"Failed to delete TETSE rule {rule_id} - no rows affected")
                raise HTTPException(status_code=500, detail=f"Failed to delete TETSE rule {rule_id}")
            
        logger.info(f"Successfully deleted TETSE rule {rule_id}: {rule_info['name']}")
        
        return {
            "success": True,
            "message": f"TETSE rule {rule_id} deleted successfully",
            "deleted_rule": {
                "id": rule_info["id"],
                "name": rule_info["name"],
                "rule_type": rule_info["rule_type"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting TETSE rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete TETSE rule {rule_id}: {str(e)}")

@router.delete("/delete_tetse_rules")
async def delete_tetse_rules(input_data: DeleteRulesInput, data_pool: asyncpg.Pool = Depends(get_data_db_pool)):
    """
    Delete multiple TETSE rules from tlk_rules table by IDs.
    
    Args:
        input_data: Object containing list of rule IDs to delete
        
    Returns:
        dict: Summary of deletion results with success/failure details
        
    Raises:
        HTTPException: If deletion process fails
    """
    try:
        rule_ids = input_data.rule_ids
        logger.info(f"Attempting to delete {len(rule_ids)} TETSE rules: {rule_ids}")
        
        if not rule_ids:
            raise HTTPException(status_code=400, detail="No rule IDs provided")
        
        # Validate rule IDs are positive integers
        invalid_ids = [rid for rid in rule_ids if not isinstance(rid, int) or rid <= 0]
        if invalid_ids:
            raise HTTPException(status_code=400, detail=f"Invalid rule IDs: {invalid_ids}")
        
        async with data_pool.acquire() as conn:
            # Get information about rules that exist
            existing_rules = await conn.fetch(
                "SELECT id, name, rule_type FROM tlk_rules WHERE id = ANY($1)",
                rule_ids
            )
            
            existing_ids = {rule["id"] for rule in existing_rules}
            missing_ids = [rid for rid in rule_ids if rid not in existing_ids]
            
            if missing_ids:
                logger.warning(f"Some TETSE rules not found: {missing_ids}")
            
            # Delete existing rules
            if existing_ids:
                deleted_count_result = await conn.execute(
                    "DELETE FROM tlk_rules WHERE id = ANY($1)",
                    list(existing_ids)
                )
                
                # Parse the result to get actual count
                deleted_count = int(deleted_count_result.split()[-1]) if deleted_count_result.startswith("DELETE") else 0
            else:
                deleted_count = 0
        
        # Prepare results
        successful_deletions = [
            {"id": rule["id"], "name": rule["name"], "rule_type": rule["rule_type"]}
            for rule in existing_rules
        ]
        
        logger.info(f"Successfully deleted {deleted_count} TETSE rules")
        
        return {
            "success": True,
            "message": f"Bulk deletion completed: {deleted_count} rules deleted",
            "summary": {
                "requested": len(rule_ids),
                "deleted": deleted_count,
                "not_found": len(missing_ids)
            },
            "deleted_rules": successful_deletions,
            "missing_rule_ids": missing_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk delete TETSE rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete TETSE rules: {str(e)}")

# Also add this helper endpoint to test database connection
@router.get("/test_tetse_db")
async def test_tetse_db(data_pool: asyncpg.Pool = Depends(get_data_db_pool)):
    """
    Test connection to ParcoRTLSData database and check tlk_rules table.
    """
    try:
        async with data_pool.acquire() as conn:
            # Test basic connection
            result = await conn.fetchval("SELECT NOW()")
            
            # Check if tlk_rules table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'tlk_rules'
                )
            """)
            
            # Count rules
            rule_count = 0
            if table_exists:
                rule_count = await conn.fetchval("SELECT COUNT(*) FROM tlk_rules")
            
            return {
                "database_connected": True,
                "current_time": result.isoformat(),
                "tlk_rules_table_exists": table_exists,
                "total_rules": rule_count,
                "message": "Database connection successful"
            }
            
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")

@router.post("/create_rule_live")
async def create_rule_live(input_data: RuleInput, data_pool: asyncpg.Pool = Depends(get_data_db_pool), maint_pool: asyncpg.Pool = Depends(get_maint_db_pool)):
    """
    Create a live TETSE rule from RuleBuilder input with enhanced natural language parsing.
    Supports: zone_stay, zone_transition, layered_trigger, and proximity_condition rules.
    """
    try:
        # Parse natural language rule
        parsed_rule = await parse_natural_language(input_data.rule_text)
        if "error" in parsed_rule:
            logger.warning(f"Parsing failed: {parsed_rule['error']}")
            raise HTTPException(status_code=400, detail=parsed_rule["error"])
        
        rule_type = parsed_rule.get("rule_type", "zone_stay")
        logger.info(f"Creating {rule_type} rule: {parsed_rule}")
        
        # Handle different rule types
        if rule_type == "proximity_condition":
            return await handle_proximity_condition_rule(parsed_rule, input_data, data_pool, maint_pool)
        elif rule_type == "layered_trigger":
            return await handle_layered_trigger_rule(parsed_rule, input_data, data_pool, maint_pool)
        elif rule_type == "zone_transition":
            return await handle_zone_transition_rule(parsed_rule, input_data, data_pool, maint_pool)
        elif rule_type == "zone_entry_monitoring":
            return await handle_zone_entry_monitoring_rule(parsed_rule, input_data, data_pool, maint_pool)
        else:
            # Legacy zone_stay rule handling
            return await handle_zone_stay_rule(parsed_rule, input_data, data_pool, maint_pool)
            
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")

async def handle_proximity_condition_rule(parsed_rule, input_data, data_pool, maint_pool):
    """
    Handle proximity condition rules like "if tag 23001 goes outside without me, send an alert"
    Creates proximity condition rule in tlk_rules table for future portable trigger implementation
    """
    try:
        subject_id = parsed_rule["subject_id"]
        proximity_target = parsed_rule["proximity_target"]  # e.g., "device_type:personnel_badge"
        proximity_distance = parsed_rule["proximity_distance"]  # e.g., 6.0
        zone_transition = parsed_rule["zone_transition"]  # {"from": "inside", "to": "outside"}
        action = parsed_rule["action"]
        
        # Create rule name with timestamp
        rule_name = f"proximity_{subject_id}_{int(time.time())}"
        
        conditions = {
            "rule_type": "proximity_condition",
            "subject_id": subject_id,
            "condition": parsed_rule["condition"],
            "proximity_target": proximity_target,
            "proximity_distance": proximity_distance,
            "zone_transition": zone_transition
        }
        
        actions = {
            "type": action,
            "message": f"Proximity condition triggered for {subject_id}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into tlk_rules table
        insert_query = """
            INSERT INTO tlk_rules (name, rule_type, conditions, actions, is_enabled, priority, created_at, updated_at, created_by, updated_by)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), CURRENT_USER, CURRENT_USER)
            RETURNING id
        """
        
        async with data_pool.acquire() as conn:
            result = await conn.fetchrow(
                insert_query,
                rule_name,
                "proximity_condition", 
                json.dumps(conditions),
                json.dumps(actions),
                True,
                1
            )
        
        rule_id = result["id"]
        logger.info(f"Successfully created proximity condition rule ID {rule_id}")
        
        return {
            "success": True,
            "message": f"Proximity condition rule created successfully",
            "rule_id": rule_id,
            "rule_type": "proximity_condition",
            "conditions": conditions,
            "actions": actions,
            "note": "Proximity rules leverage ParcoRTLS portable trigger architecture for real-time evaluation"
        }
        
    except Exception as e:
        logger.error(f"Error handling proximity condition rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create proximity rule: {str(e)}")

async def handle_layered_trigger_rule(parsed_rule, input_data, data_pool, maint_pool):
    """
    Handle layered trigger rules like "if tag 23001 moves from inside to outside send alert"
    Uses BOL2 + CL1 trigger combination logic for sophisticated spatial intelligence
    """
    try:
        subject_id = parsed_rule["subject_id"]
        from_condition = parsed_rule["from_condition"]  # "inside", "outside", "off_campus"
        to_condition = parsed_rule["to_condition"]
        trigger_layers = parsed_rule["trigger_layers"]
        action = parsed_rule["action"]
        
        rule_name = f"layered_{subject_id}_{from_condition}_to_{to_condition}_{int(time.time())}"
        
        conditions = {
            "rule_type": "layered_trigger",
            "subject_id": subject_id,
            "from_condition": from_condition,
            "to_condition": to_condition,
            "trigger_layers": trigger_layers
        }
        
        actions = {
            "type": action,
            "message": f"Layered trigger: {subject_id} moved from {from_condition} to {to_condition}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into tlk_rules table
        insert_query = """
            INSERT INTO tlk_rules (name, rule_type, conditions, actions, is_enabled, priority, created_at, updated_at, created_by, updated_by)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), CURRENT_USER, CURRENT_USER)
            RETURNING id
        """
        
        async with data_pool.acquire() as conn:
            result = await conn.fetchrow(
                insert_query,
                rule_name,
                "layered_trigger",
                json.dumps(conditions),
                json.dumps(actions),
                True,
                1
            )
        
        rule_id = result["id"]
        logger.info(f"Successfully created layered trigger rule ID {rule_id}")
        
        return {
            "success": True,
            "message": f"Layered trigger rule created successfully",
            "rule_id": rule_id,
            "rule_type": "layered_trigger", 
            "conditions": conditions,
            "actions": actions,
            "trigger_layers": trigger_layers,
            "note": "Layered triggers use ParcoRTLS BOL2 + CL1 zone architecture for inside/outside detection"
        }
        
    except Exception as e:
        logger.error(f"Error handling layered trigger rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create layered trigger rule: {str(e)}")

async def handle_zone_transition_rule(parsed_rule, input_data, data_pool, maint_pool):
    """
    Handle zone transition rules like "if tag 23001 moves from Kitchen to Living Room send alert"
    """
    try:
        subject_id = parsed_rule["subject_id"]
        from_zone = parsed_rule["from_zone"]
        to_zone = parsed_rule["to_zone"]
        action = parsed_rule["action"]
        
        rule_name = f"transition_{subject_id}_{int(time.time())}"
        
        conditions = {
            "rule_type": "zone_transition",
            "subject_id": subject_id,
            "from_zone": from_zone,
            "to_zone": to_zone
        }
        
        actions = {
            "type": action,
            "message": f"Zone transition: {subject_id} moved from {from_zone} to {to_zone}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into tlk_rules table
        insert_query = """
            INSERT INTO tlk_rules (name, rule_type, conditions, actions, is_enabled, priority, created_at, updated_at, created_by, updated_by)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), CURRENT_USER, CURRENT_USER)
            RETURNING id
        """
        
        async with data_pool.acquire() as conn:
            result = await conn.fetchrow(
                insert_query,
                rule_name,
                "zone_transition",
                json.dumps(conditions),
                json.dumps(actions),
                True,
                1
            )
        
        rule_id = result["id"]
        logger.info(f"Successfully created zone transition rule ID {rule_id}")
        
        return {
            "success": True,
            "message": f"Zone transition rule created successfully",
            "rule_id": rule_id,
            "rule_type": "zone_transition",
            "conditions": conditions,
            "actions": actions
        }
        
    except Exception as e:
        logger.error(f"Error handling zone transition rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create zone transition rule: {str(e)}")

async def handle_zone_stay_rule(parsed_rule, input_data, data_pool, maint_pool):
    """
    Handle legacy zone stay rules like "if tag 23001 stays in Kitchen for 5 minutes then alert"
    Maintains backward compatibility with existing RuleBuilder.js
    """
    try:
        # Merge parsed rule with input data, prioritizing explicit fields
        rule_data = {
            "rule_text": input_data.rule_text,
            "campus_id": input_data.campus_id,
            "subject_id": input_data.subject_id or parsed_rule.get("subject_id"),
            "zone": input_data.zone or parsed_rule.get("zone"),
            "duration_sec": input_data.duration_sec or parsed_rule.get("duration_sec", 300),
            "action": input_data.action or parsed_rule.get("action", "alert"),
            "verbose": input_data.verbose
        }

        # Validate required fields for legacy rules
        required_fields = ["campus_id", "subject_id", "zone", "duration_sec", "action"]
        missing = [field for field in required_fields if not rule_data.get(field) or rule_data.get(field) == '']
        if missing:
            logger.warning(f"Missing required fields: {missing}")
            raise HTTPException(status_code=422, detail=f"Missing or empty required fields: {', '.join(missing)}")

        # Enhanced zone validation supporting layered trigger aliases
        zone_valid = False
        if rule_data["zone"] in ["outside", "backyard", "inside"]:
            # Virtual zones supported by layered trigger architecture
            zone_valid = True
            logger.info(f"Using layered trigger alias: {rule_data['zone']}")
        else:
            # Validate actual zone in ParcoRTLSMaint.zones
            async with maint_pool.acquire() as conn:
                valid_zone = await conn.fetchrow(
                    "SELECT i_zn FROM zones WHERE x_nm_zn = $1 OR x_nm_zn = $2",
                    rule_data["zone"], rule_data["zone"].replace(" ", "")
                )
                if valid_zone:
                    zone_valid = True
                    logger.info(f"Validated zone: {rule_data['zone']}")

        if not zone_valid:
            logger.warning(f"Invalid zone: {rule_data['zone']}")
            raise HTTPException(status_code=400, detail=f"Invalid zone: {rule_data['zone']} is not a recognized zone or alias")

        # Adapt rule to TETSE format (existing logic)
        tetse_rule = await adapt_rulebuilder_to_tetse(
            rule_data=rule_data,
            campus_id=rule_data["campus_id"],
            pool=data_pool,
            maint_pool=maint_pool
        )
        logger.debug(f"Adapted rule for DB insert: {tetse_rule}")

        # Prepare rule for insertion
        rule_name = f"Rule for {tetse_rule['subject_id']} in Zone {tetse_rule['zone']} {datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        conditions = tetse_rule.get("conditions", tetse_rule)  # Use full rule as conditions if none specified
        actions = {"action_type": tetse_rule["action"], "parameters": tetse_rule}

        # Insert into tlk_rules in ParcoRTLSData
        async with data_pool.acquire() as conn:
            rule_id = await conn.fetchval(
                """
                INSERT INTO tlk_rules (name, rule_type, conditions, actions, is_enabled, priority, created_at, updated_at, created_by, updated_by)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), CURRENT_USER, CURRENT_USER)
                ON CONFLICT (name) DO UPDATE
                SET conditions = EXCLUDED.conditions,
                    actions = EXCLUDED.actions,
                    is_enabled = EXCLUDED.is_enabled,
                    priority = EXCLUDED.priority,
                    updated_at = NOW(),
                    updated_by = CURRENT_USER
                RETURNING id
                """,
                rule_name,
                "zone_stay",
                json.dumps(conditions),
                json.dumps(actions),
                True,
                tetse_rule.get("priority", 1)
            )

        logger.info(f"Successfully created zone stay rule ID {rule_id} for {tetse_rule['subject_id']} in Zone {tetse_rule['zone']}")
        return {
            "success": True,
            "message": "Zone stay rule created successfully", 
            "rule_id": rule_id, 
            "rule_type": "zone_stay",
            "rule": tetse_rule
        }

    except ValidationError as e:
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        logger.error(f"Validation error: {error_messages}")
        raise HTTPException(status_code=422, detail=f"Validation error: {'; '.join(error_messages)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling zone stay rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create zone stay rule: {str(e)}")