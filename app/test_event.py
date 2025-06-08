# Name: test_event.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import websockets
import json

async def send_test_event():
    uri = "ws://192.168.210.226:8998/ws/forward_event"
    async with websockets.connect(uri) as ws:
        event = {
            "type": "Event",
            "entity_id": "Strategy-BOT-42",
            "event_data": {
                "event_type": "TestEvent",
                "timestamp": "2025-05-28T03:30:00Z"
            }
        }
        await ws.send(json.dumps(event))
        print(f"Sent: {event}")
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"Received: {response}")
        except asyncio.TimeoutError:
            print("No response received within 5 seconds")

asyncio.run(send_test_event())