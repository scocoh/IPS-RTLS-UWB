# Name: tetse_reload.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# File: tetse_reload.py
# Version: 0.2.1
# Created: 250616
# Modified: 250616
# Author: ParcoAdmin
# Purpose: Isolate reload_rules callable to avoid circular import (Phase 11.9.3)
# Location: /home/parcoadmin/parco_fastapi/app/routes

import asyncio
import logging
import os
from routes import tetse_rule_loader
from logging.handlers import RotatingFileHandler

# Setup logging
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("TETSE_RELOAD")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "tetse_reload.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Shared singleton rule cache
ACTIVE_TETSE_RULES = []

async def reload_rules():
    """
    Reload rules from DB into shared cache.
    """
    global ACTIVE_TETSE_RULES
    try:
        rules = await tetse_rule_loader.preload_rules()
        ACTIVE_TETSE_RULES.clear()  # Clear existing rules
        ACTIVE_TETSE_RULES.extend(rules)  # Add new rules
        logger.info(f"Reloaded {len(ACTIVE_TETSE_RULES)} TETSE rules")
        logger.debug(f"Active rules: {[r.get('name', 'unnamed') for r in ACTIVE_TETSE_RULES]}")
    except Exception as e:
        logger.error(f"Failed to reload rules: {str(e)}")

# Initialize immediately at startup
asyncio.create_task(reload_rules())