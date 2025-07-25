# Name: llm_bridge.py
# Version: 0.2.1
# Created: 250617
# Modified: 250724
# Author: ParcoAdmin + QuantumSage AI
# Modified By: ParcoAdmin
# Purpose: Restores construct_prompt() for WebSocket Event AI

import os
import logging
import re
from dotenv import load_dotenv
from openai import AsyncOpenAI
from manager.line_limited_logging import LineLimitedFileHandler
from datetime import datetime

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY is missing from .env file")

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("manager.llm_bridge")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
file_handler = LineLimitedFileHandler(
    os.path.join(LOG_DIR, "llm_bridge.log"),
    max_lines=999,
    backup_count=4
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Initialize OpenAI client
client = AsyncOpenAI(api_key=api_key)

async def ask_openai(prompt: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    try:
        logger.debug(f"Sending prompt to OpenAI: {prompt[:100]}...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only JSON objects as specified, with no additional text or markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature
        )
        content = response.choices[0].message.content
        if content is None:
            error_msg = "❌ OpenAI returned empty content"
            logger.error(error_msg)
            return error_msg
        
        content = content.strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        logger.debug(f"OpenAI response: {content[:100]}...")
        return content
    except Exception as e:
        error_msg = f"❌ OpenAI API error: {str(e)}"
        logger.error(error_msg)
        return error_msg

# Restored construct_prompt() for WebSocket Event AI
async def construct_prompt(data):
    try:
        event_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        event_time_str = event_time.strftime("%I:%M %p")
    except Exception:
        event_time_str = "unknown"

    timeline_str = "Recent events processed by TETSE rule engine."
    zone_hierarchy = "unknown"
    zone = data.get('zone', '').lower()
    if zone in ["living room", "kitchen", "bedroom", "room 204", "hallway", "wing", "building"]:
        zone_hierarchy = "indoors (room -> wing -> building)"
    elif zone in ["backyard", "front yard", "yard"]:
        zone_hierarchy = "outdoors (yard -> front/back)"

    prompt = f'''
A real-time location system (ParcoRTLS with TETSE) detected:
- Entity: {data.get("entity", "unknown")}
- Triggered Event: {data.get("trigger", "unknown")}
- Zone: {zone} ({zone_hierarchy})
- Time: {event_time_str}
- Duration: {data.get("duration_sec", 0)} sec
- Prior State: {data.get("prior_state", "unknown")}
- Sequence ID: {data.get("sequence_id", "unknown")}

Explain what likely occurred, any context, and what action might be needed.
'''

    return prompt