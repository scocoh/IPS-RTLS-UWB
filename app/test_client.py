import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8001/ws/Manager1"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")

        # Send a BeginStream request (JSON)
        request = {
            "version": "1.0",
            "type": "request",
            "request": "BeginStream",
            "reqid": "test123",
            "params": [{"id": "Tag1", "data": "false"}]
        }
        await websocket.send(json.dumps(request))
        print(f"Sent: {json.dumps(request)}")

        # Receive and print responses for 30 seconds
        try:
            async for message in websocket:
                print(f"Received: {message}")
                # NEW: Handle HeartBeat by echoing it back
                try:
                    msg = json.loads(message)
                    if msg.get("type") == "HeartBeat":
                        await websocket.send(json.dumps(msg))
                        print(f"Sent HeartBeat response: {json.dumps(msg)}")
                except json.JSONDecodeError:
                    pass
        except websockets.ConnectionClosed:
            print("Connection closed")

asyncio.run(test_client())