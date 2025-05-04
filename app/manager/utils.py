# Name: utils.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/utils.py
# Version: 1.0.2 - Fixed track_metrics to calculate actual tags/sec rate over a 10-second window
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
import asyncio  # For asyncio.get_event_loop().time()
import logging  # For logging functionality
import json     # For JSON support

class MessageUtilities:
    # XML constants for message formatting
    XMLDefTag = '<?xml version="1.0" encoding="UTF-8" ?>'
    ParcoV1Tag = '<parco version="1.0">'
    ParcoEndTag = '</parco>'
    # JSON constants for message formatting
    JSON_VERSION = {"version": "1.0"}  # Base JSON header

    @staticmethod
    def json_base() -> dict:
        """Returns a base JSON object with version."""
        return {"version": "1.0"}

# Constants for API and MQTT
FASTAPI_BASE_URL = "http://192.168.210.226:8000"
MQTT_BROKER = "localhost"

# Metrics tracking function to calculate tag rate
def track_metrics(counter: int, last_time: float, timestamps: list = None) -> float:
    """
    Tracks and logs the tag processing rate (tags/sec) over a 10-second window.
    
    Args:
        counter (int): Total number of tags processed (cumulative count).
        last_time (float): Last time the rate was updated (Unix timestamp).
        timestamps (list): List of tag arrival timestamps (Unix timestamps).
    
    Returns:
        float: Updated last_time (current time if rate logged, else unchanged).
    """
    logger = logging.getLogger(__name__)
    current_time = asyncio.get_event_loop().time()
    
    # If timestamps are provided, calculate the actual rate over a 10-second window
    if timestamps:
        window_start = current_time - 10  # 10-second window
        # Filter timestamps within the window
        recent_timestamps = [ts for ts in timestamps if ts >= window_start]
        # Calculate rate: (number of tags - 1) / time span
        if len(recent_timestamps) > 1:
            time_span = (recent_timestamps[-1] - recent_timestamps[0])  # Seconds
            rate = (len(recent_timestamps) - 1) / time_span if time_span > 0 else 0
        else:
            rate = 0
        logger.debug(f"Tag rate: {rate:.2f} tags/sec, total count: {counter}")
    else:
        # Fallback to old behavior: log counter as rate (not accurate, for compatibility)
        if current_time - last_time >= 1.0:  # Every second
            logger.debug(f"Tag count: {counter} tags (rate calculation unavailable without timestamps)")
            return current_time  # Reset last_time
        return last_time  # Keep old last_time if not yet 1 second

    return current_time  # Always update last_time when using timestamps