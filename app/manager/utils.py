# Version: 250327 /home/parcoadmin/parco_fastapi/app/manager/utils.py 1.0.1
# 
# Utils Module for Manager
#   
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import xml.etree.ElementTree as ET
import asyncio  # NEW: Added for asyncio.get_event_loop().time()
import logging  # NEW: Added for logging functionality
import json  # NEW: Added for JSON support

class MessageUtilities:
    XMLDefTag = '<?xml version="1.0" encoding="UTF-8" ?>'
    ParcoV1Tag = '<parco version="1.0">'
    ParcoEndTag = '</parco>'
    # NEW: JSON constants and utilities
    JSON_VERSION = {"version": "1.0"}  # Base JSON header

    @staticmethod
    def json_base() -> dict:
        """Returns a base JSON object with version."""
        return {"version": "1.0"}

# Constants
FASTAPI_BASE_URL = "http://192.168.210.226:8000"
MQTT_BROKER = "localhost"

# NEW: Added metrics tracking function
def track_metrics(counter: int, last_time: float) -> float:
    """Tracks and logs tag processing rate; returns updated last_time."""
    current_time = asyncio.get_event_loop().time()
    if current_time - last_time >= 1.0:  # Every second
        logger = logging.getLogger(__name__)
        logger.debug(f"Tag rate: {counter} tags/sec")
        return current_time  # Reset last_time
    return last_time  # Keep old last_time if not yet 1 second