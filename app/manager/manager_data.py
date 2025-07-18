# Name: manager_data.py
# Version: 0.1.1
# Created: 250703
# Modified: 250712
# Creator: ParcoAdmin
# Modified By: AI Assistant + ParcoAdmin + Claude
# Description: Data processing handler module for ParcoRTLS Manager with RTLS message filtering integration
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Data Processing Handler Module for ParcoRTLS Manager

This module handles all data processing operations for the Manager class including:
- GIS data parsing and validation
- Position averaging (2D and 3D)
- Simulation message processing
- Tag data monitoring and rate tracking
- Data filtering and validation
- RTLS message filtering and routing (NEW in v0.1.1)

Extracted from manager.py v0.1.22 for better modularity and maintainability.
NEW: Added protocol-agnostic RTLS message filtering integration.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from manager.models import GISData, Ave, Tag
from manager.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class ManagerData:
    """
    Handles all data processing operations for the Manager class.
    
    This class encapsulates data parsing, averaging, simulation processing,
    and monitoring operations that were previously part of the main Manager class.
    
    NEW: Includes optional RTLS message filtering for protocol-agnostic message routing.
    """
    
    def __init__(self, manager_name: str, min_cnf: float = 50.0):
        """
        Initialize the data handler.
        
        Args:
            manager_name: Name of the manager instance for logging
            min_cnf: Minimum confidence level for data filtering
        """
        self.manager_name = manager_name
        self.processor = DataProcessor(min_cnf=min_cnf)
        
        # NEW: Message filtering (optional - initialize later if needed)
        self.message_filter = None  # RTLSFilterMiddleware instance

        # Averaging attributes (existing functionality preserved)
        self.ave_hash: Dict[str, Ave] = {}
        self.tag_averages: Dict[str, List[Ave]] = {}
        self.tag_averages_2d: Dict[str, List[Ave]] = {}
        self.tag_averages_3d: Dict[str, List[Ave]] = {}
        self.tag_timestamps: Dict[str, List[datetime]] = {}
        self.tag_timestamps_2d: Dict[str, List[datetime]] = {}
        self.tag_timestamps_3d: Dict[str, List[datetime]] = {}
        
        # Rate monitoring (existing functionality preserved)
        self.tag_rate: Dict[str, int] = {}
        self.last_rate_time = asyncio.get_event_loop().time()
        
        logger.debug(f"Initialized ManagerData for manager: {manager_name}")

    async def initialize_filtering(self, customer_id: int = 1):
        """
        Initialize optional RTLS message filtering for this manager.
        
        Args:
            customer_id: Customer ID for filter configuration
            
        Note: This is optional - manager works normally without filtering.
        """
        try:
            # Import here to avoid circular imports and make filtering optional
            from .rtls_middleware import RTLSFilterMiddleware
            
            self.message_filter = RTLSFilterMiddleware(customer_id)
            await self.message_filter.router.load_routing_configuration()
            logger.info(f"Initialized RTLS message filtering for manager: {self.manager_name}, customer: {customer_id}")
        except ImportError:
            logger.warning("RTLS message filtering not available - rtls_middleware module not found")
        except Exception as e:
            logger.error(f"Failed to initialize RTLS message filtering: {e}")

    async def process_gis_data(self, sm: dict, zone_id: int) -> GISData:
        """
        Process incoming GIS data from various sources.
        
        Args:
            sm: Raw message dictionary
            zone_id: Zone ID for the data
            
        Returns:
            GISData: Processed GIS data object
            
        Raises:
            ValueError: If data validation fails
            
        Note: All existing functionality preserved. Optional message filtering
              applied at the end if enabled.
        """
        logger.debug(f"Processing GIS data: {sm}")
        
        try:
            # Create GISData object (existing functionality - preserved exactly)
            msg = GISData(
                id=sm['ID'],
                type=sm['Type'],
                ts=sm['TS'],
                x=sm['X'],
                y=sm['Y'],
                z=sm['Z'],
                bat=sm['Bat'],
                cnf=sm['CNF'],
                gwid=sm['GWID'],
                data=sm.get('data', ""),  # Extract sensor payload if present
                sequence=sm.get('Sequence')
            )
            msg.zone_id = zone_id
            logger.debug(f"Set msg.zone_id to {msg.zone_id}")
            
            # Existing validation (preserved exactly)
            if not msg.validate():
                raise ValueError(f"Invalid tag data: missing field for ID:{msg.id}")
            
            if not self.processor.filter_data(msg):
                raise ValueError(f"Filtered tag ID:{msg.id}, duplicate or low CNF")
            
            # Existing averaging computation (preserved exactly)
            self.processor.compute_raw_average(msg)
            logger.debug(f"Raw average computed for tag ID:{msg.id} over 5 positions (2D)")
            
            # NEW: Apply optional RTLS message filtering
            if self.message_filter:
                try:
                    # Extract sensor payload for filtering
                    sensor_payload = self._extract_sensor_payload(sm, msg)
                    
                    # Apply message filtering
                    routed_message = await self.message_filter.filter_message(msg, sensor_payload or "")
                    
                    if routed_message:
                        logger.debug(f"Message routed for tag {msg.id} with actions: {[a.value for a in routed_message.actions]}")
                        
                        # Store routing information for later use by WebSocket handlers
                        # This allows WebSocket servers to check routing decisions
                        setattr(msg, '_routing_info', routed_message)  # type: ignore
                    else:
                        logger.debug(f"Message filtered out for tag {msg.id}")
                        # Note: We still return the message for backward compatibility
                        # WebSocket handlers can check for _routing_info to see if filtered
                        
                except Exception as filter_error:
                    logger.warning(f"Message filtering failed for tag {msg.id}: {filter_error}")
                    # Continue processing - filtering is optional
            
            return msg
            
        except Exception as e:
            logger.error(f"Failed to process GIS data: {str(e)}")
            raise

    def _extract_sensor_payload(self, sm: dict, msg: GISData) -> Optional[str]:
        """
        Extract sensor payload from raw message or GISData.
        
        Args:
            sm: Raw message dictionary
            msg: Processed GISData object
            
        Returns:
            Sensor payload string or None
        """
        # Check for sensor payload in various locations
        sensor_payload = None
        
        # Priority 1: Explicit sensor_payload field in raw message
        if 'sensor_payload' in sm:
            sensor_payload = str(sm['sensor_payload'])
        
        # Priority 2: Data field in raw message
        elif 'data' in sm and sm['data']:
            sensor_payload = str(sm['data'])
        
        # Priority 3: Data field in processed message
        elif msg.data:
            sensor_payload = msg.data
        
        # Priority 4: Combine non-RTLS fields from raw message
        else:
            non_rtls_fields = {}
            rtls_fields = {'ID', 'Type', 'TS', 'X', 'Y', 'Z', 'Bat', 'CNF', 'GWID', 'Sequence', 'zone_id'}
            
            for key, value in sm.items():
                if key not in rtls_fields and value is not None:
                    non_rtls_fields[key] = value
            
            if non_rtls_fields:
                import json
                sensor_payload = json.dumps(non_rtls_fields)
        
        return sensor_payload if sensor_payload else None

    def get_message_routing_info(self, msg: GISData) -> Optional[dict]:
        """
        Get routing information for a processed message.
        
        Args:
            msg: Processed GISData object
            
        Returns:
            Routing information dictionary or None
            
        Note: This allows WebSocket handlers to check filtering decisions.
        """
        routing_info = getattr(msg, '_routing_info', None)
        if routing_info:
            return {
                'customer_id': routing_info.customer_id,
                'actions': [action.value for action in routing_info.actions],
                'priority': routing_info.priority,
                'categories': [cat.value for cat in routing_info.rtls_message.message_categories],
                'route_timestamp': routing_info.route_timestamp.isoformat()
            }
        return None

    def should_send_to_dashboard(self, msg: GISData) -> bool:
        """
        Check if message should be sent to dashboard clients.
        
        Args:
            msg: Processed GISData object
            
        Returns:
            True if message should go to dashboard, False otherwise
            
        Note: Returns True by default if filtering not enabled (backward compatibility).
        """
        if not self.message_filter:
            return True  # Default behavior - send all messages
        
        routing_info = getattr(msg, '_routing_info', None)
        if routing_info:
            from .rtls_middleware import RouteAction
            return RouteAction.DASHBOARD in routing_info.actions
        
        return False  # Message was filtered out

    def should_log_message(self, msg: GISData) -> bool:
        """
        Check if message should be logged to database.
        
        Args:
            msg: Processed GISData object
            
        Returns:
            True if message should be logged, False otherwise
            
        Note: Returns True by default if filtering not enabled (backward compatibility).
        """
        if not self.message_filter:
            return True  # Default behavior - log all messages
        
        routing_info = getattr(msg, '_routing_info', None)
        if routing_info:
            from .rtls_middleware import RouteAction
            return RouteAction.LOGGING in routing_info.actions
        
        return False  # Message was filtered out

    def should_send_realtime(self, msg: GISData) -> bool:
        """
        Check if message should be sent via real-time WebSocket.
        
        Args:
            msg: Processed GISData object
            
        Returns:
            True if message should go to real-time stream, False otherwise
            
        Note: Returns True by default if filtering not enabled (backward compatibility).
        """
        if not self.message_filter:
            return True  # Default behavior - send all messages
        
        routing_info = getattr(msg, '_routing_info', None)
        if routing_info:
            from .rtls_middleware import RouteAction
            return RouteAction.REALTIME in routing_info.actions
        
        return False  # Message was filtered out

    def get_filter_statistics(self) -> Optional[dict]:
        """
        Get message filtering statistics.
        
        Returns:
            Filter statistics dictionary or None if filtering not enabled
        """
        if self.message_filter:
            return self.message_filter.get_filter_summary()
        return None

    # ===== EXISTING FUNCTIONALITY BELOW - PRESERVED EXACTLY =====

    async def process_sim_message(self, sm: dict) -> dict:
        """
        Process simulation message and convert to standard format.
        
        Args:
            sm: Simulation message dictionary
            
        Returns:
            dict: Processed message in standard format
            
        Raises:
            ValueError: If simulation message is invalid
        """
        logger.debug(f"Processing sim message: {sm}")
        
        try:
            if "gis" not in sm:
                raise ValueError("Sim message missing 'gis' key")
                
            gis = sm["gis"]
            if not all(k in gis for k in ["id", "x", "y", "z"]):
                raise ValueError("Sim message 'gis' missing required fields: id, x, y, z")

            # Convert simulation message to standard format
            processed_sm = {
                "ID": gis["id"],
                "Type": "Sim POTTER",
                "TS": datetime.now(timezone.utc),
                "X": gis["x"],
                "Y": gis["y"],
                "Z": gis["z"],
                "Bat": 0,
                "CNF": 100,
                "GWID": "SIM",
                "Sequence": sm.get("sequence", 0),
                "zone_id": sm.get("zone_id")
            }

            logger.debug(f"Processed sim message: {processed_sm}")
            return processed_sm
            
        except Exception as e:
            logger.error(f"Failed to process sim message: {str(e)}")
            raise

    async def compute_tag_averaging(self, msg: GISData, is_ave: bool) -> bool:
        """
        Compute tag averaging for 2D and 3D data.
        
        Args:
            msg: GIS data message
            is_ave: Whether averaging is enabled
            
        Returns:
            bool: True if averaging was computed, False otherwise
        """
        if not is_ave:
            return False

        try:
            # Initialize averaging structures if needed
            if msg.id not in self.tag_averages:
                self.tag_averages[msg.id] = []
                self.tag_timestamps[msg.id] = []
            if msg.id not in self.tag_averages_2d:
                self.tag_averages_2d[msg.id] = []
                self.tag_timestamps_2d[msg.id] = []
            if msg.id not in self.tag_averages_3d:
                self.tag_averages_3d[msg.id] = []
                self.tag_timestamps_3d[msg.id] = []

            current_time = datetime.now(timezone.utc)

            # 3D Averaging (default 5 samples)
            self.tag_averages_3d[msg.id].append(msg)  # type: ignore
            self.tag_timestamps_3d[msg.id].append(current_time)
            while self.tag_timestamps_3d[msg.id] and (current_time - self.tag_timestamps_3d[msg.id][0]).total_seconds() > 30:
                self.tag_averages_3d[msg.id].pop(0)
                self.tag_timestamps_3d[msg.id].pop(0)
            if len(self.tag_averages_3d[msg.id]) >= 5:
                ave = Ave.average(self.tag_averages_3d[msg.id][-5:])  # type: ignore
                self.ave_hash[msg.id] = ave
                logger.debug(f"Computed 3D average for tag ID:{msg.id}: x={ave.x}, y={ave.y}, z={ave.z}")

            # 2D Averaging (default 5 samples)
            self.tag_averages_2d[msg.id].append(msg)  # type: ignore
            self.tag_timestamps_2d[msg.id].append(current_time)
            while self.tag_timestamps_2d[msg.id] and (current_time - self.tag_timestamps_2d[msg.id][0]).total_seconds() > 30:
                self.tag_averages_2d[msg.id].pop(0)
                self.tag_timestamps_2d[msg.id].pop(0)
            if len(self.tag_averages_2d[msg.id]) >= 5:
                ave_2d = Ave.average_2d(self.tag_averages_2d[msg.id][-5:])  # type: ignore
                self.ave_hash[msg.id] = ave_2d
                logger.debug(f"Computed 2D average for tag ID:{msg.id}: x={ave_2d.x}, y={ave_2d.y}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to compute averaging for tag {msg.id}: {str(e)}")
            return False

    async def get_averaged_data(self, tag_id: str, zone_id: int, sequence: int) -> dict | None:
        """
        Get averaged data for a tag formatted for WebSocket transmission.
        
        Args:
            tag_id: Tag identifier
            zone_id: Current zone ID
            sequence: Message sequence number
            
        Returns:
            dict: Formatted averaged data or None if not available
        """
        ave_msg = self.ave_hash.get(tag_id)
        if not ave_msg:
            return None
            
        try:
            # Set attributes on Ave object with type ignore for dynamic attributes
            setattr(ave_msg, 'zone_id', zone_id)  # type: ignore
            setattr(ave_msg, 'sequence', sequence)  # type: ignore
            
            ave_data = {
                "type": "AveragedData",
                "id": getattr(ave_msg, 'id', 'unknown'),  # type: ignore
                "x": ave_msg.x,
                "y": ave_msg.y,
                "z": ave_msg.z,
                "ts": getattr(ave_msg, 'ts', datetime.now(timezone.utc)).isoformat(),  # type: ignore
                "zone_id": getattr(ave_msg, 'zone_id', zone_id),  # type: ignore
                "sequence": getattr(ave_msg, 'sequence', sequence)  # type: ignore
            }
            
            logger.debug(f"Generated averaged data for tag ID:{getattr(ave_msg, 'id', 'unknown')}")
            return ave_data
            
        except Exception as e:
            logger.error(f"Failed to get averaged data for tag {tag_id}: {str(e)}")
            return None

    async def monitor_tag_rates(self) -> bool:
        """
        Monitor tag data rates and update statistics.
        
        Returns:
            bool: True if monitoring completed successfully
        """
        try:
            current_time = asyncio.get_event_loop().time()
            if current_time - self.last_rate_time >= 60:
                self.tag_rate = {}
                for tag_id, timestamps in self.tag_timestamps.items():
                    while timestamps and (current_time - timestamps[0].timestamp()) > 60:
                        timestamps.pop(0)
                    rate = len(timestamps)
                    self.tag_rate[tag_id] = rate
                    logger.debug(f"Tag {tag_id} rate: {rate} updates per minute")
                self.last_rate_time = current_time
            return True
        except Exception as e:
            logger.error(f"Failed to monitor tag rates: {str(e)}")
            return False

    async def start_monitoring(self, manager_instance):
        """
        Start the tag data monitoring loop.
        
        Args:
            manager_instance: Reference to the main manager instance
        """
        logger.debug("Starting tag data monitoring")
        
        while manager_instance.run_state in [manager_instance.run_state.__class__.Started, manager_instance.run_state.__class__.Starting]:
            try:
                await self.monitor_tag_rates()
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"MonitorTagData Error: {str(e)}")
                await asyncio.sleep(10)

    def create_tag_object(self, msg: GISData) -> Tag:
        """
        Create a Tag object from GIS data.
        
        Args:
            msg: GIS data message
            
        Returns:
            Tag: Tag object for trigger processing
        """
        tag = Tag(id=msg.id, x=msg.x, y=msg.y, z=msg.z)
        logger.debug(f"Created Tag object: id={tag.id}, position=({tag.x}, {tag.y}, {tag.z})")
        return tag

    def get_data_stats(self) -> dict:
        """
        Get data processing statistics.
        
        Returns:
            dict: Statistics about data processing
        """
        stats = {
            'tags_with_averages': len(self.ave_hash),
            'tags_2d_tracking': len(self.tag_averages_2d),
            'tags_3d_tracking': len(self.tag_averages_3d),
            'current_rates': dict(self.tag_rate),
            'last_rate_update': self.last_rate_time,
            'total_tags_tracked': len(self.tag_timestamps)
        }
        
        # Add filtering statistics if available
        filter_stats = self.get_filter_statistics()
        if filter_stats:
            stats['message_filtering'] = filter_stats
        
        return stats

    def clear_tag_data(self, tag_id: str | None = None):
        """
        Clear tag data for a specific tag or all tags.
        
        Args:
            tag_id: Specific tag ID to clear, or None to clear all
        """
        if tag_id is not None:
            # Clear specific tag
            self.ave_hash.pop(tag_id, None)
            self.tag_averages.pop(tag_id, None)
            self.tag_averages_2d.pop(tag_id, None)
            self.tag_averages_3d.pop(tag_id, None)
            self.tag_timestamps.pop(tag_id, None)
            self.tag_timestamps_2d.pop(tag_id, None)
            self.tag_timestamps_3d.pop(tag_id, None)
            self.tag_rate.pop(tag_id, None)
            logger.debug(f"Cleared data for tag: {tag_id}")
        else:
            # Clear all tags
            self.ave_hash.clear()
            self.tag_averages.clear()
            self.tag_averages_2d.clear()
            self.tag_averages_3d.clear()
            self.tag_timestamps.clear()
            self.tag_timestamps_2d.clear()
            self.tag_timestamps_3d.clear()
            self.tag_rate.clear()
            logger.debug("Cleared all tag data")

    def validate_data_integrity(self) -> bool:
        """
        Validate the integrity of tracking data structures.
        
        Returns:
            bool: True if data is consistent, False otherwise
        """
        try:
            # Check that all tag IDs are consistent across structures
            all_tag_ids = set()
            all_tag_ids.update(self.tag_averages.keys())
            all_tag_ids.update(self.tag_averages_2d.keys())
            all_tag_ids.update(self.tag_averages_3d.keys())
            all_tag_ids.update(self.tag_timestamps.keys())
            all_tag_ids.update(self.tag_timestamps_2d.keys())
            all_tag_ids.update(self.tag_timestamps_3d.keys())
            
            # Verify each tag has corresponding timestamp arrays
            for tag_id in all_tag_ids:
                if tag_id in self.tag_averages and tag_id not in self.tag_timestamps:
                    logger.warning(f"Tag {tag_id} missing timestamps")
                    return False
                if tag_id in self.tag_averages_2d and tag_id not in self.tag_timestamps_2d:
                    logger.warning(f"Tag {tag_id} missing 2D timestamps")
                    return False
                if tag_id in self.tag_averages_3d and tag_id not in self.tag_timestamps_3d:
                    logger.warning(f"Tag {tag_id} missing 3D timestamps")
                    return False
                    
            logger.debug("Data integrity validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Data integrity validation failed: {str(e)}")
            return False