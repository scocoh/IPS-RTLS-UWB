# /home/parcoadmin/parco_fastapi/app/manager/test_client.py
# Version: 1.0.2 - Display sequence number from GISData messages
#
# Test Client for ParcoRTLS
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import asyncio
import websockets
import json
import logging

logger = logging.getLogger(__name__)

async def test_client():
    uri = "ws://localhost:8001/ws/Manager1"

    # Get user input for tag ID to subscribe to
    tag_id = input("Enter Tag ID to subscribe to (default SIM1): ").strip() or "SIM1"
    logger.info(f"Subscribing to Tag ID: {tag_id}")

    async with websockets.connect(uri) as websocket:
        # Send subscription request for the specified tag
        subscription = {
            "type": "request",
            "request": "BeginStream",
            "reqid": "test1",
            "params": [{"id": tag_id, "data": "true"}]
        }
        await websocket.send(json.dumps(subscription))
        logger.info(f"Sent subscription: {json.dumps(subscription)}")

        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("type") == "GISData":
                sequence = data.get("Sequence", "N/A")
                logger.info(f"Received GISData: Sequence {sequence}, {message}")
            else:
                logger.info(f"Received: {message}")

            # Respond to heartbeats
            if data.get("type") == "HeartBeat":
                response = {"type": "HeartBeat", "ts": data["ts"]}
                await websocket.send(json.dumps(response))
                logger.debug(f"Sent heartbeat response: {json.dumps(response)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_client())