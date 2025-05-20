# Name: remote_ws_client.py
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

# /home/parcoadmin/parco_fastapi/app/remote_ws_client.py
# Version: 0.1.0 - Initial implementation for remote FastAPI WebSocket client
# Description: This script sets up a FastAPI application on the remote site that connects to the on-premise
# ParcoRTLS Manager's WebSocket endpoint (`ws://192.168.210.226:8001/ws/Manager1`). It subscribes to real-time
# `TriggerEvent` messages for specific tags and zones, processes these messages, and exposes them to local clients
# (e.g., HomeAssistant, TriggerDemo apps, or custom applications) via a local WebSocket endpoint (`/ws/events`)
# and a REST endpoint (`/recent_events`). The script includes reconnection logic to handle network interruptions
# and ensures the connection remains active by responding to `HeartBeat` messages from the Manager.

import asyncio
import json
import logging
import websockets
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

# Configure logging for debugging and monitoring
# This sets up a basic logging configuration with DEBUG level, ensuring all debug, info, and error messages
# are logged. The logger is named after the module (`__name__`) to provide context in log messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the FastAPI application for the remote site
# This creates a new FastAPI instance that will serve as the web server for local clients. It will host a WebSocket
# endpoint (`/ws/events`) for real-time event streaming and a REST endpoint (`/recent_events`) for accessing recent
# `TriggerEvent` messages. The FastAPI app runs on the remote site, typically on port 8000.
app = FastAPI()

# Global list to store recent TriggerEvent messages
# This list acts as an in-memory storage for the most recent `TriggerEvent` messages received from the Manager.
# It is limited to 100 events to prevent excessive memory usage. For production use, this could be replaced with
# a database (e.g., SQLite, Redis) for persistence and scalability.
recent_events = []

# Define the Manager's WebSocket URL (on-premise)
# This URL points to the on-premise Manager's WebSocket endpoint, running on port 8001. The remote FastAPI will
# connect to this URL to subscribe to `TriggerEvent` messages. In a production environment, this URL could be
# configured via an environment variable (e.g., `MANAGER_WS_URL=ws://192.168.210.226:8001/ws/Manager1`) for flexibility.
MANAGER_WS_URL = "ws://192.168.210.226:8001/ws/Manager1"

async def connect_to_manager():
    """
    Establishes a WebSocket connection to the on-premise Manager and handles incoming messages.
    
    This function runs in an infinite loop to ensure the connection is maintained even if it drops due to network
    issues. It implements exponential backoff for reconnection attempts, starting with a 5-second delay and doubling
    up to a maximum of 60 seconds. Upon connecting, it sends a `BeginStream` request to subscribe to events for
    tags `SIM1` and `SIM2` in zone 417. It then listens for incoming messages, processes `HeartBeat` messages to keep
    the connection alive, and forwards `TriggerEvent` messages to local clients via the `/ws/events` endpoint.
    """
    reconnect_delay = 5  # Initial delay in seconds for reconnection attempts
    max_delay = 60  # Maximum delay in seconds for reconnection attempts
    while True:
        try:
            logger.info(f"Attempting to establish a WebSocket connection to the Manager at {MANAGER_WS_URL}")
            async with websockets.connect(MANAGER_WS_URL) as ws:
                # Reset the reconnect delay since the connection was successful
                reconnect_delay = 5
                logger.info("Successfully connected to the Manager's WebSocket endpoint")

                # Send a BeginStream request to subscribe to events
                # This request subscribes to events for tags SIM1 and SIM2 in zone 417. The `data: "true"` parameter
                # ensures that payload data is included in the responses. The `reqid` is a unique identifier for this
                # request, allowing the Manager to correlate responses.
                subscription = {
                    "type": "request",
                    "request": "BeginStream",
                    "reqid": "remote_api_1",
                    "params": [
                        {"id": "SIM1", "data": "true"},
                        {"id": "SIM2", "data": "true"}
                    ],
                    "zone_id": 417
                }
                await ws.send(json.dumps(subscription))
                logger.debug(f"Sent subscription request to Manager: {subscription}")

                # Continuously process incoming messages from the Manager
                while True:
                    try:
                        message = await ws.recv()
                        logger.debug(f"Received message from Manager: {message}")
                        data = json.loads(message)

                        # Handle HeartBeat messages to maintain the connection
                        # The Manager sends periodic `HeartBeat` messages to ensure the connection remains active.
                        # The client must respond with a matching `HeartBeat` message to avoid being disconnected.
                        if data.get("type") == "HeartBeat":
                            response = {"type": "HeartBeat", "ts": data["ts"]}
                            await ws.send(json.dumps(response))
                            logger.debug(f"Sent HeartBeat response to Manager: {response}")
                            continue

                        # Handle TriggerEvent messages and broadcast to local clients
                        # When a `TriggerEvent` message is received (e.g., a tag entering a zone), it is added to the
                        # `recent_events` list for access via the REST endpoint and broadcast to all connected local
                        # clients via the `/ws/events` WebSocket endpoint.
                        if data.get("type") == "TriggerEvent":
                            recent_events.append(data)
                            if len(recent_events) > 100:
                                recent_events.pop(0)  # Keep only the last 100 events
                            logger.info(f"Received TriggerEvent from Manager: {data}")

                            # Broadcast the event to all connected local clients
                            for client in local_ws_clients:
                                try:
                                    await client.send_text(json.dumps(data))
                                except WebSocketDisconnect:
                                    local_ws_clients.remove(client)
                                    logger.debug(f"Removed disconnected local client: {client.client.host}")

                        # Handle BeginStream response to confirm subscription
                        # The Manager sends a response to the `BeginStream` request to confirm that the subscription
                        # was successful. This is logged for monitoring purposes.
                        if data.get("type") == "response" and data.get("response") == "BeginStream":
                            logger.info("Subscription confirmed by Manager")

                    except websockets.exceptions.ConnectionClosed:
                        logger.error("WebSocket connection to Manager closed unexpectedly")
                        break
                    except Exception as e:
                        logger.error(f"Error processing message from Manager: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Failed to connect to Manager at {MANAGER_WS_URL}: {str(e)}")
            logger.info(f"Retrying connection in {reconnect_delay} seconds...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_delay)  # Exponential backoff

# Global list to track local WebSocket clients connected to /ws/events
# This list stores all WebSocket clients (e.g., HomeAssistant, TriggerDemo apps) connected to the local
# `/ws/events` endpoint, allowing the remote FastAPI to broadcast `TriggerEvent` messages to them in real time.
local_ws_clients = []

@app.websocket("/ws/events")
async def local_ws_endpoint(websocket: WebSocket):
    """
    Local WebSocket endpoint for clients to receive real-time TriggerEvent messages.

    This endpoint allows local clients (e.g., HomeAssistant, TriggerDemo apps, custom applications) to connect and
    receive `TriggerEvent` messages forwarded from the on-premise Manager. When a client connects, it is added to the
    `local_ws_clients` list. The client remains connected until it disconnects, at which point it is removed from the
    list to prevent sending messages to closed connections.
    """
    await websocket.accept()
    logger.debug(f"Local client connected to /ws/events: {websocket.client.host}")
    local_ws_clients.append(websocket)
    try:
        while True:
            # Keep the connection open by listening for messages (though we don't expect any)
            # The client can send messages, but we primarily use this connection to push events to the client.
            await websocket.receive_text()
    except WebSocketDisconnect:
        local_ws_clients.remove(websocket)
        logger.debug(f"Local client disconnected from /ws/events: {websocket.client.host}")

@app.on_event("startup")
async def startup_event():
    """
    Starts the WebSocket client connection to the Manager when the FastAPI application starts.

    This event handler ensures that the remote FastAPI begins connecting to the on-premise Manager's WebSocket
    endpoint as soon as the FastAPI server starts. It creates an asynchronous task to run the `connect_to_manager`
    function, which handles the connection and message processing in the background.
    """
    asyncio.create_task(connect_to_manager())

@app.get("/recent_events")
async def get_recent_events():
    """
    REST endpoint to fetch recent TriggerEvent messages.

    This endpoint allows local clients (e.g., HomeAssistant) to retrieve the most recent `TriggerEvent` messages
    received from the Manager. The events are stored in the `recent_events` list, which is limited to 100 events
    to manage memory usage. Clients can poll this endpoint periodically to check for new events.
    """
    return recent_events