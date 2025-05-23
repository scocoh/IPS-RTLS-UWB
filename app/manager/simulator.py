# Name: simulator.py
# Version: 0.1.19
# Created: 971201
# Modified: 250523
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS simulator with PortRedirect and EndStream support
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Simulator
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/simulator.py
# Version: 0.1.19 - Fixed logging AttributeError, preserved all v0.1.18 functionality, added EndStream on stop for control/stream WebSockets, enhanced logging, bumped from 0.1.18
# Previous: Restored moving tag interpolation in send_tag_data from v0.1.0, bumped from 0.1.17
# Previous: Modified to only respond to heartbeats with heartbeat_id, increased HEARTBEAT_RATE_LIMIT to 50, bumped from 0.1.16
# Previous: Reduced HEARTBEAT_RATE_LIMIT from 100 to 10 to save log space, bumped from 0.1.15
# Previous: Fixed AttributeError by replacing websocket.open with websocket.state == websockets.State.OPEN, bumped from 0.1.14
# Previous: Enhanced error handling to ensure clean exit on excessive heartbeat rate error, bumped from 0.1.13
# Previous: Added heartbeat rate tracking to detect excessive heartbeats (>100 messages/sec), bumped from 0.1.12
# Previous: Added rate-limiting to heartbeat processing, bumped from 0.1.11
# Previous: Modified simulator to exit immediately after duration, bumped from 0.1.10
# Previous: Used monotonic time for elapsed time calculations, bumped from 0.1.9
# Previous: Added cancellation of receive_stream_messages task, bumped from 0.1.8
# Previous: Added handling for type="response" messages, bumped from 0.1.7
# Previous: Cancel receive_task before closing WebSocket, bumped from 0.1.6
# Previous: Added logging for stop_simulator command, bumped from 0.1.5
# Previous: Fixed NameError by passing zone_id, bumped from 0.1.4
# Previous: Send simulation data to stream WebSocket after PortRedirect, simplified send_tag_data, bumped from 0.1.3
# Previous: Updated WebSocket URI to ControlManager, bumped from 0.1.2
# Previous: Consolidated BeginStream requests, enhanced PortRedirect logging, bumped from 1.0.28
# Previous: Added PortRedirect handling, bumped from 1.0.27
# Previous: Re-ensured zone_id in GISData with added logging (1.0.27)
#
# Simulator for ParcoRTLS
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import asyncio
import websockets
import json
from datetime import datetime
import logging
import logging.handlers
import sys
import select
import traceback
from typing import List, Tuple, Dict, Deque
from collections import deque
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Log directory
LOG_DIR = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure file handler
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "simulator.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y%m%d %H%M%S'))
logger.handlers = [logging.StreamHandler(), file_handler]
logger.propagate = False

class TagConfig:
    def __init__(self, tag_id: str, positions: List[Tuple[float, float, float]], ping_rate: float, move_interval: float = 0):
        self.tag_id = tag_id
        self.positions = positions
        self.ping_rate = ping_rate
        self.sleep_interval = 1 / ping_rate
        self.move_interval = move_interval
        self.sequence_number = 1

    def increment_sequence(self):
        self.sequence_number += 1
        if self.sequence_number > 200:
            self.sequence_number = 1

# Global variables
current_websocket = None
tag_configs = []
stream_receive_task = None
should_stop = False

async def receive_messages(websocket, running, zone_id):
    global current_websocket
    global tag_configs
    global stream_receive_task
    global should_stop
    heartbeat_timestamps = deque(maxlen=50)
    HEARTBEAT_RATE_LIMIT = 50
    while True:
        if should_stop:
            logger.info("Stopping receive_messages due to should_stop flag")
            break
        try:
            message = await websocket.recv()
            data = json.loads(message)
            logger.debug(f"Received message on control WebSocket: {data}")
            if data.get("type") == "HeartBeat":
                current_time = asyncio.get_event_loop().time()
                heartbeat_timestamps.append(current_time)
                if len(heartbeat_timestamps) == HEARTBEAT_RATE_LIMIT:
                    time_window = current_time - heartbeat_timestamps[0]
                    if time_window < 1.0:
                        should_stop = True
                        raise RuntimeError(f"Heartbeat rate exceeded {HEARTBEAT_RATE_LIMIT} messages per second on control WebSocket")
                if "heartbeat_id" in data:
                    response = json.dumps({"type": "HeartBeat", "ts": data["ts"]})
                    await websocket.send(response)
                    logger.debug(f"Sent heartbeat response: {response}")
                else:
                    logger.debug(f"Ignoring heartbeat without heartbeat_id: {data}")
            elif data.get("type") == "PortRedirect":
                logger.info(f"Received PortRedirect: {data}")
                port = data.get("port")
                stream_type = data.get("stream_type")
                manager_name = data.get("manager_name")
                if port and stream_type and manager_name:
                    new_uri = f"ws://192.168.210.226:{port}/ws/{manager_name}"
                    logger.info(f"Attempting to connect to stream WebSocket: {new_uri}")
                    try:
                        stream_websocket = await websockets.connect(new_uri)
                        current_websocket = stream_websocket
                        handshake = json.dumps({
                            "type": "request",
                            "request": "BeginStream",
                            "reqid": "sim_stream",
                            "params": [{"id": tag_config.tag_id, "data": "true"} for tag_config in tag_configs],
                            "zone_id": zone_id
                        })
                        await stream_websocket.send(handshake)
                        logger.info(f"Sent BeginStream to stream WebSocket: {handshake}")
                        stream_receive_task = asyncio.create_task(receive_stream_messages(stream_websocket, running))
                    except Exception as e:
                        logger.error(f"Failed to connect to stream WebSocket {new_uri}: {str(e)}\n{traceback.format_exc()}")
                else:
                    logger.error(f"Invalid PortRedirect message: {data}")
            elif data.get("type") == "response":
                logger.info(f"Received response on control WebSocket: {data}")
            elif data.get("command") == "start_simulator":
                logger.info("Received start_simulator command from manager")
                running[0] = True
            elif data.get("command") == "stop_simulator":
                logger.info("Received stop_simulator command from manager")
                running[0] = False
            else:
                logger.warning(f"Unhandled message type on control WebSocket: {data.get('type', 'Unknown')}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.info(f"Control WebSocket connection closed as expected: {str(e)}")
            break
        except websockets.exceptions.ConnectionClosed:
            logger.error(f"WebSocket connection closed\n{traceback.format_exc()}")
            break
        except Exception as ex:
            logger.error(f"Error receiving WebSocket message: {str(ex)}\n{traceback.format_exc()}")
            should_stop = True
            raise

async def receive_stream_messages(websocket, running):
    global should_stop
    last_heartbeat_time = 0
    HEARTBEAT_RATE_LIMIT = 50
    HEARTBEAT_RATE_WINDOW = 5
    heartbeat_timestamps = deque(maxlen=50)
    try:
        while websocket.state == websockets.State.OPEN and not should_stop:
            message = await websocket.recv()
            data = json.loads(message)
            logger.debug(f"Received stream WebSocket message: {data}")
            if data.get("type") == "HeartBeat":
                current_time = asyncio.get_event_loop().time()
                heartbeat_timestamps.append(current_time)
                if len(heartbeat_timestamps) == HEARTBEAT_RATE_LIMIT:
                    time_window = current_time - heartbeat_timestamps[0]
                    if time_window < 1.0:
                        should_stop = True
                        raise RuntimeError(f"Heartbeat rate exceeded {HEARTBEAT_RATE_LIMIT} messages per second on stream WebSocket")
                if current_time - last_heartbeat_time >= HEARTBEAT_RATE_WINDOW:
                    if "heartbeat_id" in data:
                        response = json.dumps({"type": "HeartBeat", "ts": data["ts"]})
                        await websocket.send(response)
                        logger.debug(f"Sent heartbeat response on stream WebSocket: {response}")
                        last_heartbeat_time = current_time
                    else:
                        logger.debug(f"Ignoring heartbeat without heartbeat_id: {data}")
                else:
                    logger.debug(f"Rate-limiting heartbeat response: {data}")
            elif data.get("type") == "response":
                logger.info(f"Received response on stream WebSocket: {data}")
                if data.get("request") == "EndStrm":
                    logger.info(f"Received EndStream response on stream WebSocket: {data}")
                    should_stop = True
                    break
            elif data.get("command") == "start_simulator":
                logger.info("Received start_simulator command on stream WebSocket")
                running[0] = True
            elif data.get("command") == "stop_simulator":
                logger.info("Received stop_simulator command on stream WebSocket")
                running[0] = False
                end_stream = {
                    "type": "request",
                    "request": "EndStream",
                    "reqid": ""
                }
                try:
                    await websocket.send(json.dumps(end_stream))
                    logger.info(f"Sent EndStream on stream WebSocket: {end_stream}")
                    file_handler.flush()
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    logger.info(f"Received response to EndStream on stream WebSocket: {data}")
                    file_handler.flush()
                except Exception as e:
                    logger.error(f"Failed to send/receive EndStream on stream WebSocket: {str(e)}")
                    file_handler.flush()
                break
            else:
                logger.warning(f"Unhandled message type on stream WebSocket: {data.get('type', 'Unknown')}")
    except websockets.exceptions.ConnectionClosedOK as e:
        logger.info(f"Stream WebSocket connection closed as expected: {str(e)}")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Stream WebSocket connection closed as expected (placeholder handler)")
    except Exception as ex:
        logger.error(f"Error receiving stream WebSocket message: {str(ex)}\n{traceback.format_exc()}")
        should_stop = True
        raise
    finally:
        if websocket.state == websockets.State.OPEN:
            end_stream = {
                "type": "request",
                "request": "EndStream",
                "reqid": ""
            }
            try:
                await websocket.send(json.dumps(end_stream))
                logger.info(f"Sent EndStream on stream WebSocket: {end_stream}")
                file_handler.flush()
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                logger.info(f"Received response to EndStream on stream WebSocket: {data}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Failed to send/receive EndStream on stream WebSocket: {str(e)}")
                file_handler.flush()
            try:
                await websocket.close()
                logger.info(f"Stream WebSocket closed with code: {websocket.close_code}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Error closing stream WebSocket: {str(e)}")
                file_handler.flush()

async def send_data(websocket, tag_configs: List[TagConfig], running: List[bool], duration: float, zone_id: int):
    start_time = asyncio.get_event_loop().time()
    tasks = []
    for tag_config in tag_configs:
        task = asyncio.create_task(send_tag_data(websocket, tag_config, running, start_time, duration, zone_id))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All tag simulations complete, closing WebSocket.")
    await websocket.close()

async def send_tag_data(websocket, tag_config: TagConfig, running: List[bool], start_time: float, duration: float, zone_id: int):
    global current_websocket
    global should_stop
    while True:
        if should_stop:
            logger.info(f"Stopping send_tag_data for {tag_config.tag_id} due to should_stop flag")
            break
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time >= duration:
            logger.info(f"Duration {duration} seconds reached for {tag_config.tag_id}, stopping transmission")
            break
        if running[0]:
            logger.debug(f"Elapsed time for {tag_config.tag_id}: {elapsed_time:.2f} seconds")
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
                "zone_id": zone_id
            }
            logger.info(f"Sending GISData with zone_id {zone_id} for {tag_config.tag_id}: {mock_data}")
            try:
                await current_websocket.send(json.dumps(mock_data))
                tag_config.increment_sequence()
            except Exception as e:
                logger.error(f"Failed to send GISData for {tag_config.tag_id}: {str(e)}")
                break
        remaining_time = duration - (asyncio.get_event_loop().time() - start_time)
        sleep_time = min(tag_config.sleep_interval, max(remaining_time, 0))
        if sleep_time <= 0:
            logger.info(f"Remaining time {remaining_time:.2f} seconds, stopping transmission for {tag_config.tag_id}")
            break
        await asyncio.sleep(sleep_time)

async def handle_user_input(running: List[bool], receive_task, send_task, websocket):
    print("Press 's' to start, 't' to stop, 'q' to quit")
    while True:
        if should_stop:
            logger.info("Stopping handle_user_input due to should_stop flag")
            break
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
                await websocket.close()
                break
        await asyncio.sleep(0.1)

async def simulator():
    global current_websocket
    global tag_configs
    global stream_receive_task
    global should_stop
    uri = "ws://192.168.210.226:8001/ws/ControlManager"
    print("Select simulation mode (v0.1.19):")
    print("1. Single tag at a fixed point")
    print("2. Single tag moving between two points (with linear interpolation)")
    print("3. Multiple tags at fixed points")
    print("4. One tag stationary, one tag moving")
    print("5. Two tags with different ping rates")
    try:
        mode = int(input("Enter mode (1-5): ").strip() or 1)
    except ValueError as e:
        logger.error(f"Invalid mode input: {str(e)}")
        sys.exit(1)
    duration = float(input("Enter duration in seconds (default 30): ").strip() or 30)
    zone_id = int(input("Enter zone ID (default 417): ").strip() or 417)
    tag_configs = []
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
        tag_id1 = input("Enter Tag ID for stationary tag (default SIM2): ").strip() or "SIM2"
        x1 = float(input("Enter X coordinate for stationary tag (default 32): ").strip() or 32)
        y1 = float(input("Enter Y coordinate for stationary tag (default 32): ").strip() or 32)
        z1 = float(input("Enter Z coordinate for stationary tag (default 5): ").strip() or 5)
        ping_rate1 = float(input("Enter ping rate in Hertz for stationary tag (default 0.25): ").strip() or 0.25)
        tag_configs.append(TagConfig(tag_id1, [(x1, y1, z1)], ping_rate1))
        tag_id2 = input("Enter Tag ID for moving tag (default SIM1): ").strip() or "SIM1"
        print("Enter first position for moving tag (inside region):")
        x2a = float(input("Enter X coordinate (default 32): ").strip() or 32)
        y2a = float(input("Enter Y coordinate (default 32): ").strip() or 32)
        z2a = float(input("Enter Z coordinate (default 5): ").strip() or 5)
        print("Enter second position for moving tag (outside region):")
        x2b = float(input("Enter X coordinate (default 27): ").strip() or 27)
        y2b = float(input("Enter Y coordinate (default 27): ").strip() or 27)
        z2b = float(input("Enter Z coordinate (default 1): ").strip() or 1)
        ping_rate2 = float(input("Enter ping rate in Hertz for moving tag (default 0.25): ").strip() or 0.25)
        move_interval = float(input("Enter move interval in seconds for moving tag (default 0.25): ").strip() or 0.25)
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
    stream_websocket = None
    should_stop = False
    logger.info(f"Starting simulation in mode {mode} with tags: {[tag.tag_id for tag in tag_configs]}, zone_id: {zone_id}, duration: {duration}s")
    file_handler.flush()
    try:
        async with websockets.connect(uri) as websocket:
            current_websocket = websocket
            handshake = json.dumps({
                "type": "request",
                "request": "BeginStream",
                "reqid": "sim_init",
                "params": [{"id": tag_config.tag_id, "data": "true"} for tag_config in tag_configs],
                "zone_id": zone_id
            })
            logger.info(f"Simulator targeting zone {zone_id} with handshake: {handshake}")
            await websocket.send(handshake)
            receive_task = asyncio.create_task(receive_messages(websocket, running, zone_id))
            send_task = asyncio.create_task(send_data(websocket, tag_configs, running, duration, zone_id))
            user_input_task = asyncio.create_task(handle_user_input(running, receive_task, send_task, websocket))
            try:
                await send_task
            except RuntimeError as e:
                logger.error(f"Simulation failed: {str(e)}")
                should_stop = True
                receive_task.cancel()
                user_input_task.cancel()
                if stream_receive_task:
                    stream_receive_task.cancel()
                    try:
                        await stream_receive_task
                    except asyncio.CancelledError:
                        logger.info("Stream receive task successfully canceled")
                try:
                    await receive_task
                except asyncio.CancelledError:
                    logger.info("Receive task successfully canceled")
                try:
                    await user_input_task
                except asyncio.CancelledError:
                    logger.info("User input task successfully canceled")
                if current_websocket and current_websocket.state == websockets.State.OPEN:
                    await current_websocket.close()
                raise
            logger.info("Send task completed, canceling all tasks")
            receive_task.cancel()
            user_input_task.cancel()
            if stream_receive_task:
                stream_receive_task.cancel()
                try:
                    await stream_receive_task
                except asyncio.CancelledError:
                    logger.info("Stream receive task successfully canceled")
            try:
                await receive_task
            except asyncio.CancelledError:
                logger.info("Receive task successfully canceled")
            try:
                await user_input_task
            except asyncio.CancelledError:
                logger.info("User input task successfully canceled")
    except RuntimeError as e:
        logger.error(f"Connection error: {str(e)}")
    except Exception as ex:
        logger.error(f"Unexpected connection error: {str(ex)}\n{traceback.format_exc()}")
    finally:
        if current_websocket and current_websocket.state == websockets.State.OPEN:
            end_stream = {
                "type": "request",
                "request": "EndStream",
                "reqid": ""
            }
            try:
                await current_websocket.send(json.dumps(end_stream))
                logger.info(f"Sent EndStream on control WebSocket: {end_stream}")
                file_handler.flush()
                message = await asyncio.wait_for(current_websocket.recv(), timeout=10.0)
                data = json.loads(message)
                logger.info(f"Received response to EndStream on control WebSocket: {data}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Failed to send/receive EndStream on control WebSocket: {str(e)}")
                file_handler.flush()
            try:
                await current_websocket.close()
                logger.info(f"Control WebSocket closed with code: {current_websocket.close_code}")
                file_handler.flush()
            except Exception as e:
                logger.error(f"Error closing control WebSocket: {str(e)}")
                file_handler.flush()
    logger.info("Simulation complete, exiting.")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(simulator())