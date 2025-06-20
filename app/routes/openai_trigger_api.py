# Name: openai_trigger_api.py
# Version: 0.2.7
# Created: 250617
# Modified: 250620
# Author: ParcoAdmin + QuantumSage AI
# Modified By: ParcoAdmin
# Purpose: Phase 13.4 - Full Database Insert Layer with TETSE Rule Creation
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/openai_trigger_api.py
# Version: 0.2.7 - Fixed database pool routing: data_pool for tlk_rules (ParcoRTLSData), maint_pool for zones (ParcoRTLSMaint)
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

import os
import logging
import asyncpg
import json
import re
import asyncio
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
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

MAINT_CONN_STRING = "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData"
MAINT_DB_NAME = "ParcoRTLSMaint"

class RuleInput(BaseModel):
    rule_text: str
    campus_id: str
    subject_id: str | None = None
    zone: str | None = None
    duration_sec: int | None = None
    action: str | None = None
    verbose: bool = True

async def get_maint_db_pool():
    """
    Create a connection pool for ParcoRTLSMaint database.
    """
    return await asyncpg.create_pool(
        f"postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/{MAINT_DB_NAME}",
        min_size=1,
        max_size=5
    )

async def get_data_db_pool():
    """
    Create a connection pool for ParcoRTLSData database.
    """
    return await get_async_db_pool("data")

@router.post("/create_rule_live")
async def create_rule_live(input_data: RuleInput, data_pool: asyncpg.Pool = Depends(get_data_db_pool), maint_pool: asyncpg.Pool = Depends(get_maint_db_pool)):
    """
    Create a live TETSE rule from RuleBuilder input with natural language parsing.
    """
    try:
        # Parse natural language rule
        parsed_rule = await parse_natural_language(input_data.rule_text)
        if "error" in parsed_rule:
            logger.warning(f"Parsing failed: {parsed_rule['error']}")
            raise HTTPException(status_code=400, detail=parsed_rule["error"])

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

        # Validate required fields
        required_fields = ["campus_id", "subject_id", "zone", "duration_sec", "action"]
        missing = [field for field in required_fields if not rule_data.get(field) or rule_data.get(field) == '']
        if missing:
            logger.warning(f"Missing required fields: {missing}")
            raise HTTPException(status_code=422, detail=f"Missing or empty required fields: {', '.join(missing)}")

        # Validate zone in ParcoRTLSMaint.zones
        async with maint_pool.acquire() as conn:
            valid_zone = await conn.fetchrow(
                "SELECT i_zn FROM zones WHERE x_nm_zn = $1 OR x_nm_zn = $2",
                rule_data["zone"], rule_data["zone"].replace(" ", "")
            )
            if not valid_zone and rule_data["zone"] not in ("outside", "backyard"):
                logger.warning(f"Invalid zone: {rule_data['zone']}")
                raise HTTPException(status_code=400, detail=f"Invalid zone: {rule_data['zone']} is not a recognized zone or alias")

        # Adapt rule to TETSE format
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
                INSERT INTO tlk_rules (name, conditions, actions, is_enabled, priority, created_at, updated_at, created_by, updated_by)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW(), CURRENT_USER, CURRENT_USER)
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
                json.dumps(conditions),
                json.dumps(actions),
                True,
                tetse_rule.get("priority", 1)
            )

        logger.info(f"Successfully created rule ID {rule_id} for {tetse_rule['subject_id']} in Zone {tetse_rule['zone']}")
        return {"message": "Rule created successfully", "rule_id": rule_id, "rule": tetse_rule}

    except ValidationError as e:
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        logger.error(f"Validation error: {error_messages}")
        raise HTTPException(status_code=422, detail=f"Validation error: {'; '.join(error_messages)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create rule live failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")