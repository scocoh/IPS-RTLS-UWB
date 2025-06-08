# Name: test_forwarding_client.py
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

# /home/parcoadmin/parco_fastapi/app/test_forwarding_client.py
import asyncio
import websockets
import json

async def test_forwarding():
    uri = "ws://192.168.210.226:8998/ws/forward_event"
    async with websockets.connect(uri) as ws:
        print(f"Connected to {uri}")
        # Send a test event
        event = {
            "entity_id": "Strategy-BOT-42",
            "event_data": {
                "entity_id": "Strategy-BOT-42",
                "event_type_id": 1,
                "reason_id": None,
                "value": None,
                "unit": None,
                "ts": "2025-05-26T14:12:48.457276Z",
                "id": 41
            }
        }
        await ws.send(json.dumps(event))
        print(f"Sent event: {event}")
        response = await ws.recv()
        print(f"Received response: {response}")

        # Wait 30 seconds to respect the heartbeat rate limit
        print("Waiting 30 seconds before sending heartbeat...")
        await asyncio.sleep(30)

        # Send a heartbeat
        heartbeat = {
            "type": "HeartBeat",
            "ts": 987654321,
            "heartbeat_id": "test-heartbeat"
        }
        await ws.send(json.dumps(heartbeat))
        print(f"Sent heartbeat: {heartbeat}")
        response = await ws.recv()
        print(f"Received heartbeat response: {response}")

        # Wait 30 seconds to respect the rate limit
        print("Waiting 30 seconds before sending EndStream...")
        await asyncio.sleep(30)

        # Send EndStream
        end_stream = {
            "type": "request",
            "request": "EndStream",
            "reqid": ""
        }
        await ws.send(json.dumps(end_stream))
        print(f"Sent EndStream: {end_stream}")
        response = await ws.recv()
        print(f"Received EndStream response: {response}")

asyncio.run(test_forwarding())