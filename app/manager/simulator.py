# /home/parcoadmin/parco_fastapi/app/manager/simulator.py
# Version: 1.0.18 - Added sequence number to GISData messages
#
# Simulator for ParcoRTLS
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import asyncio
import websockets
import json
from datetime import datetime
import logging
import sys
import select

logger = logging.getLogger(__name__)

async def receive_messages(websocket, running):
    """Handle incoming WebSocket messages (e.g., heartbeats, start/stop commands)."""
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("type") == "HeartBeat":
                response = json.dumps({"type": "HeartBeat", "ts": data["ts"]})
                await websocket.send(response)
                logger.debug(f"Sent heartbeat response: {response}")
            elif data.get("command") == "start_simulator":
                logger.info("Received start command from manager")
                running[0] = True
            elif data.get("command") == "stop_simulator":
                logger.info("Received stop command from manager")
                running[0] = False
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed")
            break
        except Exception as ex:
            logger.error(f"Error receiving WebSocket message: {str(ex)}")

async def send_data(websocket, tag_id, x, y, z, sleep_interval, running):
    """Send GISData messages at the specified ping rate with a sequence number."""
    sequence_number = 1  # Start at 1
    while True:
        if running[0]:
            mock_data = {
                "type": "GISData",
                "ID": tag_id,
                "Type": "Sim",
                "TS": datetime.now().isoformat(),
                "X": x,
                "Y": y,
                "Z": z,
                "Bat": 100,
                "CNF": 95.0,
                "GWID": "SIM-GW",
                "Sequence": sequence_number  # Add sequence number
            }
            await websocket.send(json.dumps(mock_data))
            logger.info(f"Sent data: {mock_data}")

            # Increment sequence number, reset to 1 after 200
            sequence_number += 1
            if sequence_number > 200:
                sequence_number = 1

        await asyncio.sleep(sleep_interval)

async def handle_user_input(running, receive_task, send_task):
    """Handle user input for start/stop/quit in a separate task."""
    print("Press 's' to start, 't' to stop, 'q' to quit")
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            user_input = sys.stdin.readline().strip().lower()
            if user_input == 's':
                logger.info("Starting data transmission")
                running[0] = True
            elif user_input == 't':
                logger.info("Stopping data transmission")
                running[0] = False
            elif user_input == 'q':
                logger.info("Quitting simulator")
                receive_task.cancel()
                send_task.cancel()
                break
        await asyncio.sleep(0.1)  # Small sleep to prevent CPU overload

async def simulator():
    uri = "ws://localhost:8001/ws/Manager1"

    # Get user input for tag ID, X/Y/Z, and ping rate
    tag_id = input("Enter Tag ID (default SIM1): ").strip() or "SIM1"
    x = float(input("Enter X coordinate (default 250401): ").strip() or 250401)
    y = float(input("Enter Y coordinate (default 162800): ").strip() or 162800)
    z = float(input("Enter Z coordinate (default 123456): ").strip() or 123456)
    ping_rate = float(input("Enter ping rate in Hertz (default 1): ").strip() or 1)
    sleep_interval = 1 / ping_rate  # Convert Hertz to sleep interval in seconds

    logger.info(f"Using Tag ID: {tag_id}, X: {x}, Y: {y}, Z: {z}, Ping Rate: {ping_rate} Hz (sleep interval: {sleep_interval}s)")

    running = [True]  # Start sending data immediately, mutable list for sharing between tasks

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # Send handshake for the specified tag
                handshake = json.dumps({
                    "type": "request",
                    "request": "BeginStream",
                    "reqid": "sim_init",
                    "params": [{"id": tag_id, "data": "true"}]
                })
                await websocket.send(handshake)
                logger.info(f"Sent handshake: {handshake}")

                # Start separate tasks for receiving messages, sending data, and handling user input
                receive_task = asyncio.create_task(receive_messages(websocket, running))
                send_task = asyncio.create_task(send_data(websocket, tag_id, x, y, z, sleep_interval, running))
                user_input_task = asyncio.create_task(handle_user_input(running, receive_task, send_task))

                # Wait for tasks to complete (e.g., on quit)
                await asyncio.gather(receive_task, send_task, user_input_task, return_exceptions=True)

        except Exception as ex:
            logger.error(f"Connection error: {str(ex)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(simulator())