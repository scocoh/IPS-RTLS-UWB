# Name: fastapi_service.py
# Version: 0.1.1
# Created: 971201
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/fastapi_service.py
# Version: 0.1.3-250430 - Fixed BASE_URL access by removing staticmethod, updated BASE_URL to 192.168.210.226:8000, added logging, bumped from 0.1.2
# Previous: Added timeout=10.0 to API calls, included response.text in HTTP error logs, bumped from 0.1.1 (0.1.2)
# Previous: Switched to async httpx, added get_trigger_details (0.1.1)

import httpx
import logging
import sys
import os

# Add centralized configuration imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Force logging configuration for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.handlers = []
logger.addHandler(handler)
logger.propagate = False

class FastAPIService:
    def __init__(self):
        # Use centralized configuration for server host
        server_host = get_server_host()
        self.BASE_URL = f"http://{server_host}:8000"

    async def get_triggers_by_zone(self, zone_id: int) -> list:
        """
        Fetch triggers for a specific zone.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/get_triggers_by_zone_with_id/{zone_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get triggers for zone {zone_id}: {e}, response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get triggers for zone {zone_id}: {e}")
            return []

    async def get_trigger_details(self, trigger_id: int) -> list:
        """
        Fetch trigger details (e.g., regions) for a specific trigger.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/get_trigger_details/{trigger_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get trigger details for trigger {trigger_id}: {e}, response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get trigger details for trigger {trigger_id}: {e}")
            return []

    async def get_zone_list(self) -> list:
        """
        Fetch all zones.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/list_zones",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get zones: {e}, response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get zones: {e}")
            return []

    async def get_devices_list(self) -> list:
        """
        Fetch all devices.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/get_all_devices",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get devices: {e}, response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get devices: {e}")
            return []

    async def get_entity_list(self) -> list:
        """
        Fetch all entities (optional).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/list_entities",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get entities: {e}, response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            return []

    async def heartbeat_check(self) -> bool:
        """
        Simple FastAPI server heartbeat check.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/heartbeat",
                    timeout=10.0
                )
                return response.status_code == 200
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed FastAPI heartbeat check: {e}, response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed FastAPI heartbeat check: {e}")
            return False