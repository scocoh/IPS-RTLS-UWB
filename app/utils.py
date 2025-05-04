# Name: utils.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

from fastapi import HTTPException
import asyncio
import logging

logger = logging.getLogger(__name__)

async def system_status():
    try:
        fastapi_status = await asyncio.create_subprocess_exec(
            "systemctl", "is-active", "fastapi",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        fastapi_output, _ = await fastapi_status.communicate()
        fastapi_running = fastapi_output.decode().strip() == "active"

        mqtt_status = await asyncio.create_subprocess_exec(
            "systemctl", "is-active", "mosquitto",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        mqtt_output, _ = await mqtt_status.communicate()
        mqtt_running = mqtt_output.decode().strip() == "active"

        return {
            "FastAPI": "Running ✅" if fastapi_running else "Stopped ❌",
            "Mosquitto": "Running ✅" if mqtt_running else "Stopped ❌"
        }
    except Exception as e:
        logger.error(f"Error checking system status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check system status")