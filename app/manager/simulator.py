# Name: simulator.py
# Version: 0.1.32
# Created: 971201
# Modified: 250723
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude + Grok
# Description: Python script for ParcoRTLS simulator - Fixed Pylance type errors in interpolate_positions return type and position inputs
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Simulator
# Status: Active
# Dependent: TRUE

#!/usr/bin/env python3
"""
ParcoRTLS Simulator - Generates test position data for RTLS development
Version: 0.1.32 - Fixed Pylance type errors in interpolate_positions return type and position inputs, bumped from 0.1.31
Version: 0.1.31 - Added speed-based interpolation, multi-segment paths, and movement behaviors for modes 2 and 4, bumped from 0.1.30
Version: 0.1.30 - Modified tag ID generation for mode 3 to start at SIM10# (e.g., SIM101), bumped from 0.1.29
Version: 0.1.29 - Fixed smooth movement interpolation for moving tags, bumped from 0.1.28
Version: 0.1.28 - Restored proper sequence number management from v0.1.21, bumped from 0.1.27
Version: 0.1.27 - Updated to use centralized IP configuration system, bumped from 0.1.26
"""

import asyncio
import json
import logging
import math
from logging.handlers import RotatingFileHandler
import os
import select
import sys
import time
import traceback
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Any
import websockets

# Import centralized configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Configure logging
logger = logging.getLogger("simulator")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler with rotation
log_directory = "/home/parcoadmin/parco_fastapi/app/logs"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, "simulator.log")
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configuration
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", get_server_host())
CONTROL_PORT = int(os.getenv("CONTROL_PORT", "8001"))
STREAM_PORT = int(os.getenv("STREAM_PORT", "8002"))

# Global variables
current_websocket = None
stream_websocket = None
stream_receive_task = None
should_stop = False
tag_configs = []

@dataclass
class TagConfig:
    """Configuration for a simulated tag"""
    tag_id: str
    positions: List[Tuple[float, float, float]]
    ping_rate: float = 0.25  # Hz
    speed_fps: float = 5.0  # Feet per second
    movement_behavior: str = 'bounce'  # 'bounce', 'stop', 'restart'
    sleep_interval: float = 1.0
    sequence_number: int = 1  # Proper sequence number management
    
    def __post_init__(self):
        self.sleep_interval = 1.0 / self.ping_rate

    def increment_sequence(self):
        """Proper sequence number increment with rollover"""
        self.sequence_number += 1
        if self.sequence_number > 200:
            self.sequence_number = 1

def interpolate_positions(positions: List[Tuple[float, float, float]], 
                         elapsed: float, 
                         speed_fps: float,
                         movement_behavior: str) -> Tuple[Tuple[float, float, float], dict[str, Any]]:
    """Interpolate position along multi-segment path using speed (feet per second)"""
    if not positions or len(positions) < 2 or speed_fps <= 0:
        x, y, z = positions[0] if positions else (0.0, 0.0, 0.0)
        return (x, y, z), {"segment_index": 0, "t": 0, "seg_dist": 0, "total_distance": 0}

    # Calculate segment distances and total distance
    distances = []
    total_distance = 0
    for i in range(len(positions) - 1):
        dx = positions[i + 1][0] - positions[i][0]
        dy = positions[i + 1][1] - positions[i][1]
        dz = positions[i + 1][2] - positions[i][2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        distances.append(dist)
        total_distance += dist

    # Total time for one full traversal
    total_time = total_distance / speed_fps
    if total_time == 0:
        return positions[0], {"segment_index": 0, "t": 0, "seg_dist": 0, "total_distance": 0}

    # Determine direction and time based on behavior
    if movement_behavior == 'stop' and elapsed >= total_time:
        # Stay at final position
        x, y, z = positions[-1]
        return (x, y, z), {"segment_index": len(positions) - 2, "t": 1, "seg_dist": distances[-1], "total_distance": total_distance}
    elif movement_behavior == 'restart':
        time_remaining = elapsed % total_time
    else:  # bounce (default)
        cycle_time = elapsed % (2 * total_time)
        time_remaining = cycle_time if cycle_time < total_time else (2 * total_time - cycle_time)

    # Find current segment
    segment_index = 0
    while segment_index < len(distances):
        seg_time = distances[segment_index] / speed_fps
        if time_remaining < seg_time:
            break
        time_remaining -= seg_time
        segment_index += 1

    # Handle boundary cases
    start = positions[segment_index] if segment_index < len(positions) else positions[-2]
    end = positions[segment_index + 1] if segment_index + 1 < len(positions) else positions[-1]
    seg_dist = distances[segment_index] if segment_index < len(distances) else distances[-1]

    # Calculate interpolation parameter
    t = (time_remaining * speed_fps / seg_dist) if seg_dist > 0 else 0

    # Linear interpolation
    x = start[0] + (end[0] - start[0]) * t
    y = start[1] + (end[1] - start[1]) * t
    z = start[2] + (end[2] - start[2]) * t

    debug = {
        "segment_index": segment_index,
        "t": round(t, 3),
        "seg_dist": round(seg_dist, 2),
        "total_distance": round(total_distance, 2),
        "total_time": round(total_time, 2),
        "speed_fps": speed_fps
    }

    return (x, y, z), debug

async def receive_messages(websocket, running: List[bool], zone_id: int):
    """Handle messages from Control WebSocket"""
    global stream_websocket, stream_receive_task, should_stop
    last_heartbeat_time = 0
    HEARTBEAT_RATE_LIMIT = 50
    HEARTBEAT_RATE_WINDOW = 5
    heartbeat_timestamps = deque(maxlen=50)
    
    try:
        while websocket.state == websockets.State.OPEN and not should_stop:
            message = await websocket.recv()
            data = json.loads(message)
            logger.debug(f"Received control WebSocket message: {data}")
            
            if data.get("type") == "HeartBeat":
                current_time = asyncio.get_event_loop().time()
                heartbeat_timestamps.append(current_time)
                if len(heartbeat_timestamps) == HEARTBEAT_RATE_LIMIT:
                    time_window = current_time - heartbeat_timestamps[0]
                    if time_window < 1.0:
                        should_stop = True
                        raise RuntimeError(f"Heartbeat rate exceeded {HEARTBEAT_RATE_LIMIT} messages per second on control WebSocket")
                
                if current_time - last_heartbeat_time > 1:
                    logger.debug(f"Control WebSocket HeartBeat from manager at {datetime.now()}")
                    last_heartbeat_time = current_time
                
                heartbeat_id = data.get("heartbeat_id")
                if heartbeat_id:
                    heartbeat_response = {
                        "type": "HeartBeat",
                        "heartbeat_id": heartbeat_id,
                        "ts": int(time.time() * 1000),
                        "source": "simulator"
                    }
                    await websocket.send(json.dumps(heartbeat_response))
                    logger.debug(f"Responded to control heartbeat with ID: {heartbeat_id}")
            
            elif data.get("type") == "PortRedirect":
                redirect_port = data.get("port")
                redirect_zone = data.get("zone")
                if redirect_port:
                    logger.info(f"Received PortRedirect to port {redirect_port}, zone {redirect_zone}")
                    new_uri = f"ws://{WEBSOCKET_HOST}:{redirect_port}/ws/RealTimeManager"
                    logger.info(f"Connecting to stream WebSocket at {new_uri}")
                    try:
                        stream_websocket = await websockets.connect(new_uri, max_size=2**20)
                        logger.info(f"Connected to stream WebSocket at port {redirect_port}")
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
    except websockets.exceptions.ConnectionClosed:
        logger.error(f"WebSocket connection closed\n{traceback.format_exc()}")
    except Exception as ex:
        logger.error(f"Error receiving WebSocket message: {str(ex)}\n{traceback.format_exc()}")
        should_stop = True
        raise

async def receive_stream_messages(websocket, running):
    """Handle messages from Stream WebSocket"""
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
                
                if current_time - last_heartbeat_time > 1:
                    logger.debug(f"Stream WebSocket HeartBeat from manager at {datetime.now()}")
                    last_heartbeat_time = current_time
                
                heartbeat_id = data.get("heartbeat_id")
                if heartbeat_id:
                    heartbeat_response = {
                        "type": "HeartBeat",
                        "heartbeat_id": heartbeat_id,
                        "ts": int(time.time() * 1000),
                        "source": "simulator"
                    }
                    await websocket.send(json.dumps(heartbeat_response))
                    logger.debug(f"Responded to stream heartbeat with ID: {heartbeat_id}")
            
            elif data.get("type") == "TriggerEvent":
                trigger_id = data.get("trigger_id")
                trigger_name = data.get("trigger_name")
                tag_id = data.get("tag_id")
                direction = data.get("direction")
                zone_id = data.get("zone_id")
                logger.info(f"TriggerEvent: {trigger_name} (ID:{trigger_id}) for tag {tag_id} zone {zone_id} direction {direction}")
            
            elif data.get("type") == "response":
                logger.info(f"Received response on stream WebSocket: {data}")
            
            else:
                logger.debug(f"Unhandled message type on stream WebSocket: {data.get('type', 'Unknown')}")
                
    except websockets.exceptions.ConnectionClosedOK as e:
        logger.info(f"Stream WebSocket connection closed as expected: {str(e)}")
    except websockets.exceptions.ConnectionClosed:
        logger.error(f"Stream WebSocket connection closed\n{traceback.format_exc()}")
    except Exception as ex:
        logger.error(f"Error receiving stream WebSocket message: {str(ex)}\n{traceback.format_exc()}")
        should_stop = True
        raise

async def send_tag_data(websocket, tag_config: TagConfig, running: List[bool], 
                       duration: float, zone_id: int, start_time: float):
    """Send position data for a single tag with speed-based interpolation"""
    global stream_websocket, should_stop
    
    while (asyncio.get_event_loop().time() - start_time) < duration and running[0] and not should_stop:
        current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - start_time
        
        # Interpolate position using speed-based movement
        (x, y, z), debug = interpolate_positions(
            tag_config.positions, 
            elapsed_time, 
            tag_config.speed_fps,
            tag_config.movement_behavior
        )
        
        # Round to 2 decimal places for consistency
        x = round(x, 2)
        y = round(y, 2)
        z = round(z, 2)
        
        logger.debug(f"Interpolated position for {tag_config.tag_id}: segment={debug['segment_index']}, t={debug['t']:.2f}, pos=({x:.2f}, {y:.2f}, {z:.2f}), dist={debug['seg_dist']:.2f}/{debug['total_distance']:.2f}")
        
        # Send GISData message
        message = {
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
        
        target_websocket = stream_websocket if stream_websocket else websocket
        if target_websocket and target_websocket.state == websockets.State.OPEN:
            try:
                await target_websocket.send(json.dumps(message))
                tag_config.increment_sequence()
                target_type = "stream" if stream_websocket else "control"
                logger.info(f"Sending GISData with zone_id {zone_id} for {tag_config.tag_id}: pos=({x:.2f}, {y:.2f}, {z:.2f})")
            except Exception as e:
                logger.error(f"Failed to send data for tag {tag_config.tag_id}: {str(e)}")
                break
        
        remaining_time = duration - (asyncio.get_event_loop().time() - start_time)
        sleep_time = min(tag_config.sleep_interval, max(remaining_time, 0))
        if sleep_time <= 0:
            logger.info(f"Remaining time {remaining_time:.2f} seconds, stopping transmission for {tag_config.tag_id}")
            break
        await asyncio.sleep(sleep_time)

async def send_data(websocket, tag_configs: List[TagConfig], running: List[bool], 
                   duration: float, zone_id: int):
    """Send data for all configured tags"""
    start_time = asyncio.get_event_loop().time()
    tasks = []
    
    for tag_config in tag_configs:
        task = asyncio.create_task(
            send_tag_data(websocket, tag_config, running, duration, zone_id, start_time)
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"All send tasks completed after {elapsed_time:.2f} seconds")

async def handle_user_input(running: List[bool], receive_task, send_task, websocket):
    """Handle keyboard input during simulation"""
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
    uri = f"ws://{WEBSOCKET_HOST}:{CONTROL_PORT}/ws/ControlManager"
    print("Select simulation mode (v0.1.32):")
    print("1. Single tag at a fixed point")
    print("2. Single tag moving between points (with speed-based interpolation)")
    print("3. Multiple tags at fixed points")
    print("4. One tag stationary, one tag moving")
    print("5. Two tags with different ping rates")
    print("6. TETSE Debug Mode")
    try:
        mode = int(input("Enter mode (1-6): ").strip() or 1)
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
        num_positions = int(input("Enter number of positions (minimum 2, default 2): ").strip() or 2)
        if num_positions < 2:
            num_positions = 2
        positions = []
        for i in range(num_positions):
            print(f"Enter position {i+1}:")
            x = float(input(f"Enter X coordinate (default {5.0 if i == 0 else -1.0}): ").strip() or (5.0 if i == 0 else -1.0))
            y = float(input(f"Enter Y coordinate (default {5.0 if i == 0 else -1.0}): ").strip() or (5.0 if i == 0 else -1.0))
            z = float(input(f"Enter Z coordinate (default {5.0 if i == 0 else 1.0}): ").strip() or (5.0 if i == 0 else 1.0))
            positions.append((x, y, z))
        ping_rate = float(input("Enter ping rate in Hertz (default 0.25): ").strip() or 0.25)
        speed_fps = float(input("Enter speed in feet per second (default 5.0): ").strip() or 5.0)
        movement_behavior = input("Enter movement behavior (bounce, stop, restart; default bounce): ").strip() or "bounce"
        if movement_behavior not in ['bounce', 'stop', 'restart']:
            movement_behavior = 'bounce'
        tag_configs.append(TagConfig(tag_id, positions, ping_rate, speed_fps, movement_behavior))
    elif mode == 3:
        num_tags = int(input("Enter number of tags (default 2): ").strip() or 2)
        for i in range(num_tags):
            tag_id = input(f"Enter Tag ID for tag {i+1} (default SIM10{i+1}): ").strip() or f"SIM10{i+1}"
            x = float(input(f"Enter X coordinate for tag {i+1} (default {5 + i*10}): ").strip() or float(5 + i*10))
            y = float(input(f"Enter Y coordinate for tag {i+1} (default 5): ").strip() or 5.0)
            z = float(input(f"Enter Z coordinate for tag {i+1} (default 5): ").strip() or 5.0)
            ping_rate = float(input(f"Enter ping rate in Hertz for tag {i+1} (default 0.25): ").strip() or 0.25)
            tag_configs.append(TagConfig(tag_id, [(x, y, z)], ping_rate))
    elif mode == 4:
        tag_id1 = input("Enter Tag ID for stationary tag (default 23001): ").strip() or "23001"
        x1 = float(input("Enter X coordinate for stationary tag (default 105): ").strip() or 105.0)
        y1 = float(input("Enter Y coordinate for stationary tag (default 140): ").strip() or 140.0)
        z1 = float(input("Enter Z coordinate for stationary tag (default 5): ").strip() or 5.0)
        ping_rate1 = float(input("Enter ping rate in Hertz for stationary tag (default 0.1): ").strip() or 0.1)
        tag_configs.append(TagConfig(tag_id1, [(x1, y1, z1)], ping_rate1))
        tag_id2 = input("Enter Tag ID for moving tag (default 23002): ").strip() or "23002"
        num_positions = int(input("Enter number of positions for moving tag (minimum 2, default 2): ").strip() or 2)
        if num_positions < 2:
            num_positions = 2
        positions = []
        for i in range(num_positions):
            print(f"Enter position {i+1} for moving tag:")
            x = float(input(f"Enter X coordinate (default {114.0 if i == 0 else 105.0}): ").strip() or (114.0 if i == 0 else 105.0))
            y = float(input(f"Enter Y coordinate (default {126.0 if i == 0 else 140.0}): ").strip() or (126.0 if i == 0 else 140.0))
            z = float(input(f"Enter Z coordinate (default {5.0 if i == 0 else 1.0}): ").strip() or (5.0 if i == 0 else 1.0))
            positions.append((x, y, z))
        ping_rate2 = float(input("Enter ping rate in Hertz for moving tag (default 0.1): ").strip() or 0.1)
        speed_fps = float(input("Enter speed in feet per second for moving tag (default 5.0): ").strip() or 5.0)
        movement_behavior = input("Enter movement behavior for moving tag (bounce, stop, restart; default bounce): ").strip() or "bounce"
        if movement_behavior not in ['bounce', 'stop', 'restart']:
            movement_behavior = 'bounce'
        tag_configs.append(TagConfig(tag_id2, positions, ping_rate2, speed_fps, movement_behavior))
    elif mode == 5:
        tag_id1 = input("Enter Tag ID for first tag (default SIM1): ").strip() or "SIM1"
        x1 = float(input("Enter X coordinate for first tag (default 5): ").strip() or 5.0)
        y1 = float(input("Enter Y coordinate for first tag (default 5): ").strip() or 5.0)
        z1 = float(input("Enter Z coordinate for first tag (default 5): ").strip() or 5.0)
        ping_rate1 = float(input("Enter ping rate in Hertz for first tag (default 0.25): ").strip() or 0.25)
        tag_configs.append(TagConfig(tag_id1, [(x1, y1, z1)], ping_rate1))
        tag_id2 = input("Enter Tag ID for second tag (default SIM2): ").strip() or "SIM2"
        x2 = float(input("Enter X coordinate for second tag (default 5): ").strip() or 5.0)
        y2 = float(input("Enter Y coordinate for second tag (default 5): ").strip() or 5.0)
        z2 = float(input("Enter Z coordinate for second tag (default 5): ").strip() or 5.0)
        ping_rate2 = float(input("Enter ping rate in Hertz for second tag (default 0.5): ").strip() or 0.5)
        tag_configs.append(TagConfig(tag_id2, [(x2, y2, z2)], ping_rate2))
    elif mode == 6:
        # Option 6: Specific test for TETSE debug at your specified coordinates
        tag_id = "23001"
        x = 100.5
        y = 200.7
        z = 1.0
        ping_rate = 0.75
        # Use existing zone 422 (6005Campus) to test TETSE evaluation
        zone_id = 422  # Existing zone: "6005Campus"
        tag_configs.append(TagConfig(tag_id, [(x, y, z)], ping_rate))
        print(f"Option 6: TETSE Debug - tag {tag_id} at ({x}, {y}, {z}) with ping rate {ping_rate}Hz in zone_id {zone_id} (6005Campus)")
        duration = 10  # Override duration to 10 seconds
    running = [True]
    stream_websocket = None
    should_stop = False
    logger.info(f"Starting simulation in mode {mode} with tags: {[tag.tag_id for tag in tag_configs]}, zone_id: {zone_id}, duration: {duration}s")
    file_handler.flush()
    retries = 3
    retry_delay = 5
    for attempt in range(retries):
        try:
            async with websockets.connect(uri, max_size=2**20) as websocket:
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
                return
        except Exception as ex:
            logger.error(f"Connection attempt {attempt + 1} failed: {str(ex)}\n{traceback.format_exc()}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached, exiting.")
                sys.exit(1)
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
    try:
        asyncio.run(simulator())
    except KeyboardInterrupt:
        print("\nSimulation terminated by user")
    except Exception as e:
        logger.error(f"Simulator error: {e}")
        sys.exit(1)