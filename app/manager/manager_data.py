# Name: manager_data.py
# Version: 0.1.0
# Created: 250703
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Data processing handler module for ParcoRTLS Manager - Extracted from manager.py v0.1.22
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

Extracted from manager.py v0.1.22 for better modularity and maintainability.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List
from manager.models import GISData, Ave, Tag
from manager.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class ManagerData:
    """
    Handles all data processing operations for the Manager class.
    
    This class encapsulates data parsing, averaging, simulation processing,
    and monitoring operations that were previously part of the main Manager class.
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
        
        # Averaging attributes
        self.ave_hash: Dict[str, Ave] = {}
        self.tag_averages: Dict[str, List[Ave]] = {}
        self.tag_averages_2d: Dict[str, List[Ave]] = {}
        self.tag_averages_3d: Dict[str, List[Ave]] = {}
        self.tag_timestamps: Dict[str, List[datetime]] = {}
        self.tag_timestamps_2d: Dict[str, List[datetime]] = {}
        self.tag_timestamps_3d: Dict[str, List[datetime]] = {}
        
        # Rate monitoring
        self.tag_rate: Dict[str, int] = {}
        self.last_rate_time = asyncio.get_event_loop().time()
        
        logger.debug(f"Initialized ManagerData for manager: {manager_name}")

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
        """
        logger.debug(f"Processing GIS data: {sm}")
        
        try:
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
                data="",
                sequence=sm.get('Sequence')
            )
            msg.zone_id = zone_id
            logger.debug(f"Set msg.zone_id to {msg.zone_id}")
            
            if not msg.validate():
                raise ValueError(f"Invalid tag data: missing field for ID:{msg.id}")
            
            if not self.processor.filter_data(msg):
                raise ValueError(f"Filtered tag ID:{msg.id}, duplicate or low CNF")
            
            self.processor.compute_raw_average(msg)
            logger.debug(f"Raw average computed for tag ID:{msg.id} over 5 positions (2D)")
            
            return msg
            
        except Exception as e:
            logger.error(f"Failed to process GIS data: {str(e)}")
            raise

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
        return {
            'tags_with_averages': len(self.ave_hash),
            'tags_2d_tracking': len(self.tag_averages_2d),
            'tags_3d_tracking': len(self.tag_averages_3d),
            'current_rates': dict(self.tag_rate),
            'last_rate_update': self.last_rate_time,
            'total_tags_tracked': len(self.tag_timestamps)
        }

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