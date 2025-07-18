# Name: alltraq_service.py
# Version: 0.1.2
# Created: 250713
# Modified: 250713
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: AllTraq API polling service - Connects to AllTraq WebSocket server on port 18002 - Fixed WebSocket .closed attribute error
# Location: /home/parcoadmin/parco_fastapi/app/DataSources/AllTraqAppAPI
# Role: Service
# Status: Active
# Dependent: TRUE

# AllTraq is a registered trademark of ABG Tag and Traq Inc (Oklahoma) Serial Num 87037989 for Goods & Service IC 009

import asyncio
import logging
import json
import httpx
import websockets
from datetime import datetime
from typing import List, Dict, Optional, Any
import time
import sys
import os
import configparser

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%y%m%d %H%M%S'
)
logger = logging.getLogger("alltraq_service")

def get_server_host() -> str:
    """Get server host with fallback"""
    try:
        from config import get_server_host as config_get_server_host # type: ignore
        return config_get_server_host()
    except ImportError:
        logger.warning("Could not import get_server_host from config, using fallback")
        return "192.168.210.226"
    except Exception as e:
        logger.warning(f"Error getting server host from config: {e}, using fallback")
        return "192.168.210.226"

class AllTraqConfig:
    """Configuration loader for AllTraq service"""
    
    def __init__(self, config_path: str = "config/alltraq.conf"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from alltraq.conf file"""
        try:
            self.config.read(self.config_path)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {str(e)}")
            raise
    
    @property
    def api_base_url(self) -> str:
        return self.config.get('api', 'base_url')
    
    @property
    def bearer_token(self) -> str:
        return self.config.get('api', 'bearer_token')
    
    @property
    def batch_size(self) -> int:
        return self.config.getint('api', 'batch_size')
    
    @property
    def poll_interval(self) -> float:
        return self.config.getfloat('api', 'poll_interval')
    
    @property
    def timeout(self) -> int:
        return self.config.getint('api', 'timeout')
    
    @property
    def client_id(self) -> str:
        return self.config.get('integration', 'client_id')
    
    @property
    def tag_prefix(self) -> str:
        return self.config.get('integration', 'tag_prefix')
    
    @property
    def serials(self) -> List[str]:
        """Get tag serials from config file"""
        serials_str = self.config.get('tags', 'serials')
        return [s.strip() for s in serials_str.split(',') if s.strip()]

# Default zone for AllTraq data
DEFAULT_ZONE_ID = 451

class AllTraqService:
    """AllTraq API polling service that connects to ParcoRTLS WebSocket"""
    
    def __init__(self, config_path: str = "config/alltraq.conf"):
        self.config = AllTraqConfig(config_path)
        self.devices: List[Dict] = []
        self.websocket: Optional[Any] = None
        self.running = False
        self.heartbeat_task = None
        
        # Build URLs using centralized configuration
        server_host = get_server_host()
        self.fastapi_base_url = f"http://{server_host}:8000"
        self.websocket_url = f"ws://{server_host}:18002/ws/AllTraqAppAPIInbound"
        
        logger.info(f"AllTraqService initialized with server host: {server_host}")
        
    async def get_alltraq_devices(self) -> List[Dict]:
        """Get AllTraq devices from FastAPI endpoint"""
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(f"{self.fastapi_base_url}/api/get_device_by_type/27")
                if response.status_code == 200:
                    devices = response.json()
                    logger.info(f"Retrieved {len(devices)} AllTraq devices from FastAPI")
                    return devices
                else:
                    logger.error(f"Failed to get devices: HTTP {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error getting AllTraq devices: {str(e)}")
            return []
    
    async def connect_websocket(self) -> bool:
        """Connect to AllTraq WebSocket server"""
        try:
            logger.info(f"Connecting to AllTraq WebSocket: {self.websocket_url}")
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info("Connected to AllTraq WebSocket server")
            
            # Send BeginStream request
            await self.send_begin_stream()
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            return False
    
    async def send_begin_stream(self):
        """Send BeginStream request to subscribe to AllTraq data"""
        try:
            # Use devices from FastAPI, fallback to config serials if needed
            device_ids = []
            if self.devices:
                device_ids = [device["x_id_dev"] for device in self.devices]
            else:
                device_ids = self.config.serials
                logger.warning("Using device serials from config file as fallback")
            
            # Create params for all devices
            params = []
            for device_id in device_ids:
                params.append({
                    "id": device_id, 
                    "data": "true"
                })
            
            begin_stream_msg = {
                "type": "request",
                "request": "BeginStream", 
                "reqid": self.config.client_id,
                "params": params,
                "zone_id": DEFAULT_ZONE_ID
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(begin_stream_msg))
                logger.info(f"Sent BeginStream for {len(params)} AllTraq devices")
                
                # Wait for response
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                logger.info(f"BeginStream response: {response}")
            else:
                logger.error("WebSocket not connected, cannot send BeginStream")
            
        except Exception as e:
            logger.error(f"Failed to send BeginStream: {str(e)}")
    
    async def poll_alltraq_api(self, device_batch: List[str]) -> Optional[List[Dict]]:
        """Poll AllTraq API for device status"""
        try:
            # Create comma-separated serial list
            serial_list = ",".join(device_batch)
            url = f"{self.config.api_base_url}/{serial_list}"
            
            headers = {
                "Authorization": f"Bearer {self.config.bearer_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Retrieved data for {len(data)} devices from AllTraq API")
                    return data
                elif response.status_code == 401:
                    logger.error("AllTraq API authentication failed - check bearer token")
                    return None
                else:
                    logger.warning(f"AllTraq API returned {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error polling AllTraq API: {str(e)}")
            return None
    
    def transform_alltraq_data(self, alltraq_data: Dict) -> Optional[Dict]:
        """Transform AllTraq API response to ParcoRTLS GIS format"""
        try:
            # Extract data from AllTraq response
            serial_number = alltraq_data.get("serialNumber")
            tracking_location = alltraq_data.get("trackingLocation", {})
            
            if not serial_number or not tracking_location:
                logger.debug(f"Incomplete AllTraq data for {serial_number}")
                return None
            
            # Parse coordinates
            coordinates = tracking_location.get("coordinates", "")
            if not coordinates:
                logger.debug(f"No coordinates for device {serial_number}")
                return None
            
            try:
                # AllTraq coordinates format: "74.28,33.03" 
                coord_parts = coordinates.split(",")
                if len(coord_parts) != 2:
                    logger.warning(f"Invalid coordinate format for {serial_number}: {coordinates}")
                    return None
                    
                x = float(coord_parts[0])
                y = float(coord_parts[1])
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse coordinates for {serial_number}: {coordinates} - {str(e)}")
                return None
            
            # Get timestamp
            updated_on = tracking_location.get("updatedOn", datetime.now().isoformat())
            
            # Transform to ParcoRTLS GIS format
            gis_data = {
                "type": "GISData",
                "ID": str(serial_number),
                "Type": "AllTraq",
                "TS": updated_on,
                "X": x,
                "Y": y,
                "Z": 0.0,
                "Bat": 100,  # AllTraq doesn't provide battery info
                "CNF": 95.0, # Confidence level
                "GWID": "AllTraq-API",
                "Sequence": int(time.time() % 1000),
                "zone_id": DEFAULT_ZONE_ID
            }
            
            return gis_data
            
        except Exception as e:
            logger.error(f"Error transforming AllTraq data: {str(e)}")
            return None
    
    async def send_gis_data(self, gis_data: Dict):
        """Send GIS data to WebSocket server"""
        try:
            if self.websocket:
                await self.websocket.send(json.dumps(gis_data))
                logger.debug(f"Sent GIS data for device {gis_data['ID']}")
            else:
                logger.warning("WebSocket not connected, cannot send GIS data")
        except Exception as e:
            logger.error(f"Failed to send GIS data: {str(e)}")
    
    async def handle_heartbeat(self, message: Dict):
        """Handle heartbeat from WebSocket server"""
        try:
            if message.get("type") == "HeartBeat":
                heartbeat_id = message.get("heartbeat_id")
                ts = message.get("ts")
                
                # Respond to heartbeat
                heartbeat_response = {
                    "type": "HeartBeat",
                    "heartbeat_id": heartbeat_id,
                    "ts": ts,
                    "source": "alltraq_service"
                }
                
                if self.websocket:
                    await self.websocket.send(json.dumps(heartbeat_response))
                    logger.debug(f"Responded to heartbeat {heartbeat_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to handle heartbeat: {str(e)}")
            return False
        return False
    
    async def websocket_listener(self):
        """Listen for WebSocket messages (heartbeats, responses)"""
        try:
            while self.running and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    if not await self.handle_heartbeat(data):
                        logger.debug(f"Received WebSocket message: {data}")
                        
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from WebSocket: {message}")
                    
        except Exception as e:
            logger.error(f"WebSocket listener error: {str(e)}")
    
    async def polling_loop(self):
        """Main polling loop for AllTraq API"""
        try:
            while self.running:
                # Determine device list to use
                device_serials = []
                if self.devices:
                    device_serials = [device["x_id_dev"] for device in self.devices]
                else:
                    device_serials = self.config.serials
                    logger.debug("Using device serials from config file")
                
                if not device_serials:
                    logger.warning("No devices available, sleeping...")
                    await asyncio.sleep(self.config.poll_interval)
                    continue
                
                # Create batches of devices
                for i in range(0, len(device_serials), self.config.batch_size):
                    if not self.running:
                        break
                        
                    batch = device_serials[i:i + self.config.batch_size]
                    logger.info(f"Polling batch {i//self.config.batch_size + 1}: {len(batch)} devices")
                    
                    # Poll AllTraq API
                    alltraq_data = await self.poll_alltraq_api(batch)
                    
                    if alltraq_data:
                        # Process each device's data
                        for device_data in alltraq_data:
                            gis_data = self.transform_alltraq_data(device_data)
                            if gis_data:
                                await self.send_gis_data(gis_data)
                    
                    # Small delay between batches
                    await asyncio.sleep(0.5)
                
                # Wait for next polling interval
                logger.info(f"Completed polling cycle, sleeping {self.config.poll_interval} seconds")
                await asyncio.sleep(self.config.poll_interval)
                
        except Exception as e:
            logger.error(f"Polling loop error: {str(e)}")
    
    async def start(self):
        """Start the AllTraq service"""
        logger.info("Starting AllTraq Service")
        
        try:
            # Get AllTraq devices from FastAPI
            self.devices = await self.get_alltraq_devices()
            if not self.devices:
                logger.warning("No AllTraq devices found from FastAPI, will use config serials")
            
            # Connect to WebSocket
            if not await self.connect_websocket():
                logger.error("Failed to connect to WebSocket, cannot start service") 
                return False
            
            self.running = True
            
            # Start WebSocket listener and polling loop
            listener_task = asyncio.create_task(self.websocket_listener())
            polling_task = asyncio.create_task(self.polling_loop())
            
            device_count = len(self.devices) if self.devices else len(self.config.serials)
            logger.info(f"AllTraq Service started - monitoring {device_count} devices")
            
            # Wait for tasks to complete
            await asyncio.gather(listener_task, polling_task, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the AllTraq service"""
        logger.info("Stopping AllTraq Service")
        self.running = False
        
        if self.websocket:
            try:
                # Send EndStream
                end_stream_msg = {
                    "type": "request",
                    "request": "EndStream",
                    "reqid": self.config.client_id
                }
                await self.websocket.send(json.dumps(end_stream_msg))
                await self.websocket.close()
                logger.info("WebSocket connection closed")
            except Exception as e:
                logger.error(f"Error closing WebSocket: {str(e)}")

async def main():
    """Main entry point"""
    service = AllTraqService()
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())