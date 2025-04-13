# /home/parcoadmin/parco_fastapi/app/manager/simulator.py
# Version: 1.0.27 - Re-ensured zone_id in GISData with added logging, bumped from 1.0.26
# Previous: Re-ensured zone_id is included in GISData messages (1.0.26)
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
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class TagConfig:
    def __init__(self, tag_id: str, positions: List[Tuple[float, float, float]], ping_rate: float, move_interval: float = 0):
        self.tag_id = tag_id
        self.positions = positions  # List of (x, y, z) positions; if len > 1, tag moves between them
        self.ping_rate = ping_rate
        self.sleep_interval = 1 / ping_rate
        self.move_interval = move_interval  # Seconds to move from one position to the next (0 means stationary)
        self.sequence_number = 1

    def increment_sequence(self):
        self.sequence_number += 1
        if self.sequence_number > 200:
            self.sequence_number = 1

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

async def send_data(websocket, tag_configs: List[TagConfig], running: List[bool], duration: float, zone_id: int):
    """Send GISData messages for all tags at their specified ping rates for the specified duration."""
    start_time = datetime.now()
    tasks = []
    for tag_config in tag_configs:
        task = asyncio.create_task(send_tag_data(websocket, tag_config, running, start_time, duration, zone_id))
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All tag simulations complete, closing WebSocket.")
    await websocket.close()  # Close WebSocket after all tasks finish

async def send_tag_data(websocket, tag_config: TagConfig, running: List[bool], start_time: datetime, duration: float, zone_id: int):
    """Send GISData messages for a single tag at its specified ping rate."""
    while True:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        if elapsed_time >= duration:
            logger.info(f"Duration {duration} seconds reached for {tag_config.tag_id}, stopping transmission")
            break

        if running[0]:
            logger.debug(f"Elapsed time for {tag_config.tag_id}: {elapsed_time:.2f} seconds")

            # If the tag has multiple positions and a move interval, interpolate the position
            if len(tag_config.positions) > 1 and tag_config.move_interval > 0:
                cycle_time = elapsed_time % (2 * tag_config.move_interval)
                logger.debug(f"Cycle time for {tag_config.tag_id}: {cycle_time:.2f}, move_interval: {tag_config.move_interval}")
                if cycle_time < tag_config.move_interval:
                    t = cycle_time / tag_config.move_interval
                    start_pos = tag_config.positions[0]
                    end_pos = tag_config.positions[1]
                    logger.debug(f"Moving from {start_pos} to {end_pos}, t={t:.2f}")
                else:
                    t = (cycle_time - tag_config.move_interval) / tag_config.move_interval
                    start_pos = tag_config.positions[1]
                    end_pos = tag_config.positions[0]
                    logger.debug(f"Moving from {start_pos} to {end_pos}, t={t:.2f}")

                x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                z = start_pos[2] + t * (end_pos[2] - start_pos[2])
                x = round(x, 2)
                y = round(y, 2)
                z = round(z, 2)
                logger.debug(f"Interpolated position for {tag_config.tag_id}: t={t:.2f}, pos=({x:.2f}, {y:.2f}, {z:.2f})")
            else:
                x, y, z = tag_config.positions[0]
                x = round(x, 2)
                y = round(y, 2)
                z = round(z, 2)
                logger.debug(f"Stationary position for {tag_config.tag_id}: pos=({x:.2f}, {y:.2f}, {z:.2f})")

            mock_data = {
                "type": "GISData",
                "ID": tag_config.tag_id,
                "Type": "Sim",
                "TS": datetime.now().isoformat(),
                "X": x,
                "Y": y,
                "Z": z,
                "Bat": 100,
                "CNF": 95.0,
                "GWID": "SIM-GW",
                "Sequence": tag_config.sequence_number,
                "zone_id": zone_id  # Ensure zone_id is included
            }
            logger.info(f"Sending GISData with zone_id {zone_id} for {tag_config.tag_id}: {mock_data}")
            await websocket.send(json.dumps(mock_data))
            tag_config.increment_sequence()

        remaining_time = duration - (datetime.now() - start_time).total_seconds()
        sleep_time = min(tag_config.sleep_interval, max(remaining_time, 0))
        if sleep_time <= 0:
            logger.info(f"Remaining time {remaining_time:.2f} seconds, stopping transmission for {tag_config.tag_id}")
            break
        await asyncio.sleep(sleep_time)

async def handle_user_input(running: List[bool], receive_task, send_task, websocket):
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
                await websocket.close()  # Close WebSocket on quit
                break
        await asyncio.sleep(0.1)

async def simulator():
    uri = "ws://192.168.210.226:8001/ws/Manager1"

    print("Select simulation mode (v1.0.27):")
    print("1. Single tag at a fixed point")
    print("2. Single tag moving between two points (with linear interpolation)")
    print("3. Multiple tags at fixed points")
    print("4. One tag stationary, one tag moving")
    print("5. Two tags with different ping rates")
    mode = int(input("Enter mode (1-5): ").strip() or 1)
    duration = float(input("Enter duration in seconds (default 30): ").strip() or 30)
    zone_id = int(input("Enter zone ID (default 417): ").strip() or 417)

    tag_configs: List[TagConfig] = []

    if mode == 1:
        tag_id = input("Enter Tag ID (default SIM1): ").strip() or "SIM1"
        x = float(input("Enter X coordinate (default 5): ").strip() or 5)
        y = float(input("Enter Y coordinate (default 5): ").strip() or 5)
        z = float(input("Enter Z coordinate (default 5): ").strip() or 5)
        ping_rate = float(input("Enter ping rate in Hertz (default 0.25): ").strip() or 0.25)
        tag_configs.append(TagConfig(tag_id, [(x, y, z)], ping_rate))

    elif mode == 2:
        tag_id = input("Enter Tag ID (default SIM1): ").strip() or "SIM1"
        print("Enter first position (inside region):")
        x1 = float(input("Enter X coordinate (default 5): ").strip() or 5)
        y1 = float(input("Enter Y coordinate (default 5): ").strip() or 5)
        z1 = float(input("Enter Z coordinate (default 5): ").strip() or 5)
        print("Enter second position (outside region):")
        x2 = float(input("Enter X coordinate (default -1): ").strip() or -1)
        y2 = float(input("Enter Y coordinate (default -1): ").strip() or -1)
        z2 = float(input("Enter Z coordinate (default 1): ").strip() or 1)
        ping_rate = float(input("Enter ping rate in Hertz (default 0.25): ").strip() or 0.25)
        move_interval = float(input("Enter move interval in seconds (default 10): ").strip() or 10)
        tag_configs.append(TagConfig(tag_id, [(x1, y1, z1), (x2, y2, z2)], ping_rate, move_interval))

    elif mode == 3:
        num_tags = int(input("Enter number of tags (default 2): ").strip() or 2)
        for i in range(num_tags):
            tag_id = input(f"Enter Tag ID for tag {i+1} (default SIM{i+1}): ").strip() or f"SIM{i+1}"
            x = float(input(f"Enter X coordinate for tag {i+1} (default {5 + i*10}): ").strip() or (5 + i*10))
            y = float(input(f"Enter Y coordinate for tag {i+1} (default 5): ").strip() or 5)
            z = float(input(f"Enter Z coordinate for tag {i+1} (default 5): ").strip() or 5)
            ping_rate = float(input(f"Enter ping rate in Hertz for tag {i+1} (default 0.25): ").strip() or 0.25)
            tag_configs.append(TagConfig(tag_id, [(x, y, z)], ping_rate))

    elif mode == 4:
        tag_id1 = input("Enter Tag ID for stationary tag (default SIM1): ").strip() or "SIM1"
        x1 = float(input("Enter X coordinate for stationary tag (default 5): ").strip() or 5)
        y1 = float(input("Enter Y coordinate for stationary tag (default 5): ").strip() or 5)
        z1 = float(input("Enter Z coordinate for stationary tag (default 5): ").strip() or 5)
        ping_rate1 = float(input("Enter ping rate in Hertz for stationary tag (default 0.25): ").strip() or 0.25)
        tag_configs.append(TagConfig(tag_id1, [(x1, y1, z1)], ping_rate1))

        tag_id2 = input("Enter Tag ID for moving tag (default SIM2): ").strip() or "SIM2"
        print("Enter first position for moving tag (inside region):")
        x2a = float(input("Enter X coordinate (default 5): ").strip() or 5)
        y2a = float(input("Enter Y coordinate (default 5): ").strip() or 5)
        z2a = float(input("Enter Z coordinate (default 5): ").strip() or 5)
        print("Enter second position for moving tag (outside region):")
        x2b = float(input("Enter X coordinate (default -1): ").strip() or -1)
        y2b = float(input("Enter Y coordinate (default -1): ").strip() or -1)
        z2b = float(input("Enter Z coordinate (default 1): ").strip() or 1)
        ping_rate2 = float(input("Enter ping rate in Hertz for moving tag (default 0.25): ").strip() or 0.25)
        move_interval = float(input("Enter move interval in seconds for moving tag (default 10): ").strip() or 10)
        tag_configs.append(TagConfig(tag_id2, [(x2a, y2a, z2a), (x2b, y2b, z2b)], ping_rate2, move_interval))

    elif mode == 5:
        tag_id1 = input("Enter Tag ID for first tag (default SIM1): ").strip() or "SIM1"
        x1 = float(input("Enter X coordinate for first tag (default 5): ").strip() or 5)
        y1 = float(input("Enter Y coordinate for first tag (default 5): ").strip() or 5)
        z1 = float(input("Enter Z coordinate for first tag (default 5): ").strip() or 5)
        ping_rate1 = float(input("Enter ping rate in Hertz for first tag (default 0.25): ").strip() or 0.25)
        tag_configs.append(TagConfig(tag_id1, [(x1, y1, z1)], ping_rate1))

        tag_id2 = input("Enter Tag ID for second tag (default SIM2): ").strip() or "SIM2"
        x2 = float(input("Enter X coordinate for second tag (default 5): ").strip() or 5)
        y2 = float(input("Enter Y coordinate for second tag (default 5): ").strip() or 5)
        z2 = float(input("Enter Z coordinate for second tag (default 5): ").strip() or 5)
        ping_rate2 = float(input("Enter ping rate in Hertz for second tag (default 0.5): ").strip() or 0.5)
        tag_configs.append(TagConfig(tag_id2, [(x2, y2, z2)], ping_rate2))

    running = [True]

    try:
        async with websockets.connect(uri) as websocket:
            for tag_config in tag_configs:
                handshake = json.dumps({
                    "type": "request",
                    "request": "BeginStream",
                    "reqid": f"sim_init_{tag_config.tag_id}",
                    "params": [{"id": tag_config.tag_id, "data": "true"}],
                    "zone_id": zone_id
                })
                logger.info(f"Simulator targeting zone {zone_id} with handshake for {tag_config.tag_id}: {handshake}")
                await websocket.send(handshake)

            receive_task = asyncio.create_task(receive_messages(websocket, running))
            send_task = asyncio.create_task(send_data(websocket, tag_configs, running, duration, zone_id))  # Pass zone_id
            user_input_task = asyncio.create_task(handle_user_input(running, receive_task, send_task, websocket))

            await asyncio.gather(receive_task, send_task, user_input_task, return_exceptions=True)
    except Exception as ex:
        logger.error(f"Connection error: {str(ex)}")

    logger.info("Simulation complete, exiting.")
    sys.exit(0)  # Exit script cleanly

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(simulator())