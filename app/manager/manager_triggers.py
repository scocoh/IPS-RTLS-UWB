# Name: manager_triggers.py
# Version: 0.1.1
# Created: 250703
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Trigger engine handler module for ParcoRTLS Manager - Extracted from manager.py v0.1.22
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Trigger Engine Handler Module for ParcoRTLS Manager

This module handles all trigger operations for the Manager class including:
- Trigger loading from database via FastAPI service
- Trigger evaluation and firing
- Portable trigger management and movement
- Zone-based trigger filtering
- Event message generation and broadcasting

Extracted from manager.py v0.1.22 for better modularity and maintainability.
"""

import asyncio
import logging
import traceback
import httpx
from datetime import datetime
from typing import List, Dict
from manager.models import Tag
from manager.enums import TriggerDirections
from manager.trigger import Trigger
from manager.portable_trigger import PortableTrigger
from manager.region import Region3D, Region3DCollection
from manager.utils import FASTAPI_BASE_URL
from manager.fastapi_service import FastAPIService

logger = logging.getLogger(__name__)

class ManagerTriggers:
    """
    Handles all trigger operations for the Manager class.
    
    This class encapsulates trigger loading, evaluation, portable trigger management,
    and event generation operations that were previously part of the main Manager class.
    """
    
    def __init__(self, manager_name: str):
        """
        Initialize the trigger handler.
        
        Args:
            manager_name: Name of the manager instance for logging
        """
        self.manager_name = manager_name
        self.triggers: List[Trigger] = []
        self.service = FastAPIService()
        
        logger.debug(f"Initialized ManagerTriggers for manager: {manager_name}")

    async def load_triggers(self, zone_id: int) -> bool:
        """
        Load triggers for a specific zone from the database.
        
        Args:
            zone_id: Zone ID to load triggers for
            
        Returns:
            bool: True if triggers loaded successfully, False otherwise
        """
        logger.debug(f"Loading triggers for zone {zone_id}")
        
        try:
            triggers_data = await self.service.get_triggers_by_zone(zone_id)
            logger.debug(f"Retrieved triggers data for zone {zone_id}: {triggers_data}")

            # Clear existing triggers for this zone
            self.triggers = [t for t in self.triggers if t.zone_id != zone_id]
            logger.debug(f"Cleared existing triggers for zone {zone_id}, remaining triggers: {len(self.triggers)}")

            for trigger_data in triggers_data:
                trigger = await self._create_trigger_from_data(trigger_data, zone_id)
                if trigger:
                    self.triggers.append(trigger)
                    logger.info(f"Loaded trigger {trigger.name} (ID: {trigger.i_trg}) for zone {zone_id} with direction {trigger.direction}")

            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch triggers for zone {zone_id}: {str(e)}\n{traceback.format_exc()}")
            return False

    async def _create_trigger_from_data(self, trigger_data: dict, zone_id: int) -> Trigger | None:
        """
        Create a trigger object from database data.
        
        Args:
            trigger_data: Raw trigger data from database
            zone_id: Zone ID for the trigger
            
        Returns:
            Trigger: Created trigger object or None if creation failed
        """
        try:
            trigger_id = trigger_data["trigger_id"]
            trigger_name = trigger_data["name"]
            direction_id = trigger_data.get("direction_id")
            is_portable = trigger_data.get("is_portable", False)
            assigned_tag_id = trigger_data.get("assigned_tag_id")
            radius_ft = trigger_data.get("radius_ft")
            z_min = trigger_data.get("z_min")
            z_max = trigger_data.get("z_max")

            logger.debug(f"Processing trigger ID {trigger_id}")

            # Map direction ID to TriggerDirections enum
            direction_map = {
                1: TriggerDirections.WhileIn,
                2: TriggerDirections.WhileOut,
                3: TriggerDirections.OnCross,
                4: TriggerDirections.OnEnter,
                5: TriggerDirections.OnExit
            }
            direction = direction_map.get(direction_id or 0, TriggerDirections.NotSet)
            logger.debug(f"Mapping direction_id {direction_id} to {direction} for trigger {trigger_name}")

            if is_portable:
                trigger = PortableTrigger(
                    tag_id=assigned_tag_id or "",  # type: ignore
                    radius_ft=radius_ft or 0.0,  # type: ignore
                    z_min=z_min or 0.0,  # type: ignore
                    z_max=z_max or 0.0,  # type: ignore
                    i_trg=trigger_id,
                    name=trigger_name,
                    direction=direction,
                    zone_id=zone_id
                )
                logger.debug(f"Created PortableTrigger {trigger_name} for tag {assigned_tag_id}")
                return trigger
            else:
                # Load trigger details for static triggers
                trigger_details = await self.service.get_trigger_details(trigger_id)
                logger.debug(f"Trigger details for {trigger_id}: {trigger_details}")

                regions = Region3DCollection()
                if isinstance(trigger_details, dict) and "vertices" in trigger_details:
                    vertices = trigger_details.get("vertices", [])  # type: ignore
                    logger.debug(f"Vertices for trigger {trigger_id}: {vertices}")
                    if vertices and len(vertices) >= 3:
                        regions = Region3DCollection.from_vertices(vertices)
                    else:
                        logger.warning(f"Insufficient vertices for trigger {trigger_name} (ID: {trigger_id}): {len(vertices)}")
                        return None
                else:
                    for detail in trigger_details:
                        if "n_min_x" in detail and "n_max_x" in detail:
                            regions.add(Region3D(
                                min_x=detail["n_min_x"],
                                max_x=detail["n_max_x"],
                                min_y=detail["n_min_y"],
                                max_y=detail["n_max_y"],
                                min_z=detail["n_min_z"],
                                max_z=detail["n_max_z"]
                            ))
                            logger.debug(f"Added region for trigger {trigger_id}: min=({detail['n_min_x']}, {detail['n_min_y']}, {detail['n_min_z']}), max=({detail['n_max_x']}, {detail['n_max_y']}, {detail['n_max_z']})")

                if len(regions.regions) == 0:
                    logger.warning(f"No regions loaded for trigger {trigger_name} (ID: {trigger_id})")
                    return None

                trigger = Trigger(
                    i_trg=trigger_id,
                    name=trigger_name,
                    direction=direction,
                    regions=regions,
                    ignore_unknowns=False,
                    zone_id=zone_id
                )
                logger.debug(f"Created Trigger object for {trigger_name} (ID: {trigger_id})")
                return trigger
                
        except Exception as e:
            logger.error(f"Failed to create trigger from data: {str(e)}")
            return None

    async def evaluate_triggers(self, tag: Tag, msg_zone_id: int, database_handler) -> List[dict]:
        """
        Evaluate all triggers for a given tag and return fired events.
        
        Args:
            tag: Tag object to evaluate
            msg_zone_id: Zone ID from the message
            database_handler: Database handler for trigger updates
            
        Returns:
            List[dict]: List of trigger event messages
        """
        events = []
        
        try:
            logger.debug(f"Checking {len(self.triggers)} triggers for tag {tag.id} at ({tag.x}, {tag.y}, {tag.z})")
            
            for trigger in self.triggers:
                # Skip triggers not in the current zone
                if trigger.zone_id != msg_zone_id:
                    logger.debug(f"Skipping trigger {trigger.name} (ID: {trigger.i_trg}) - zone mismatch (trigger zone: {trigger.zone_id}, message zone: {msg_zone_id})")
                    continue
                
                # Handle portable trigger movement
                if trigger.is_portable and tag.id == getattr(trigger, 'assigned_tag_id', None):  # type: ignore
                    await self._handle_portable_trigger_movement(trigger, tag, database_handler)
                
                # Evaluate trigger
                logger.debug(f"Evaluating trigger {trigger.name} (ID: {trigger.i_trg}) with direction {trigger.direction.name}")
                trigger_fired = await trigger.check_trigger(tag)
                logger.debug(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired: {trigger_fired}")
                
                if trigger_fired:
                    # Suppress WhileIn events for tags triggering their own portable triggers
                    if (trigger.is_portable and 
                        trigger.direction == TriggerDirections.WhileIn and 
                        tag.id == getattr(trigger, 'assigned_tag_id', None)):  # type: ignore
                        logger.debug(f"Suppressed WhileIn event for tag {tag.id} on its own trigger {trigger.name} (ID: {trigger.i_trg})")
                        continue

                    logger.info(f"Trigger {trigger.name} (ID: {trigger.i_trg}) fired for tag {tag.id} at position ({tag.x}, {tag.y}, {tag.z})")
                    
                    event_message = self._create_trigger_event(trigger, tag, msg_zone_id)
                    events.append(event_message)
                    
        except Exception as e:
            logger.error(f"Failed to evaluate triggers: {str(e)}")
            
        return events

    async def _handle_portable_trigger_movement(self, trigger: Trigger, tag: Tag, database_handler):
        """
        Handle movement of portable triggers and zone updates.
        
        Args:
            trigger: Portable trigger to move
            tag: Tag that owns the trigger
            database_handler: Database handler for zone updates
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{FASTAPI_BASE_URL}/api/zones_by_point",
                    params={"x": tag.x, "y": tag.y, "z": tag.z}
                )
                response.raise_for_status()
                zones = response.json()
                if zones:
                    new_zone_id = min(
                        zones,
                        key=lambda z: (z["n_max_x"] - z["n_min_x"]) * (z["n_max_y"] - z["n_min_y"])
                    )["zone_id"]
                    if new_zone_id != trigger.zone_id:
                        trigger.zone_id = new_zone_id
                        await database_handler.update_trigger_zone(trigger.i_trg, new_zone_id)
                        logger.debug(f"Updated portable trigger {trigger.name} to zone {new_zone_id}")
                        
            # Move trigger to tag position
            # Check if this is a PortableTrigger instance to satisfy type checker
            if isinstance(trigger, PortableTrigger):
                trigger.update_position_from_tag(tag)
            else:
                # Fallback for regular triggers with move_to method
                trigger.move_to(tag.x, tag.y, tag.z)
            logger.debug(f"Moved portable trigger {trigger.name} to ({tag.x}, {tag.y}, {tag.z})")
                
        except Exception as e:
            logger.error(f"Failed to update zone for trigger {trigger.name}: {str(e)}")
    def _create_trigger_event(self, trigger: Trigger, tag: Tag, zone_id: int) -> dict:
        """
        Create a trigger event message.
        
        Args:
            trigger: Trigger that fired
            tag: Tag that triggered the event
            zone_id: Current zone ID
            
        Returns:
            dict: Trigger event message
        """
        event_message = {
            "type": "TriggerEvent",
            "trigger_id": trigger.i_trg,
            "trigger_name": trigger.name,
            "tag_id": tag.id,
            "assigned_tag_id": getattr(trigger, 'assigned_tag_id', None) if trigger.is_portable else None,  # type: ignore
            "x": tag.x,
            "y": tag.y,
            "z": tag.z,
            "zone_id": zone_id,
            "direction": trigger.direction.name,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"Event message created: {event_message}")
        return event_message

    async def reload_triggers_for_zone(self, zone_id: int) -> bool:
        """
        Reload triggers for a specific zone.
        
        Args:
            zone_id: Zone ID to reload triggers for
            
        Returns:
            bool: True if reload successful
        """
        logger.info(f"Reloading triggers for zone {zone_id}")
        return await self.load_triggers(zone_id)

    def get_triggers_for_zone(self, zone_id: int) -> List[Trigger]:
        """
        Get all triggers for a specific zone.
        
        Args:
            zone_id: Zone ID to get triggers for
            
        Returns:
            List[Trigger]: Triggers for the zone
        """
        return [t for t in self.triggers if t.zone_id == zone_id]

    def get_portable_triggers(self) -> List[Trigger]:
        """
        Get all portable triggers.
        
        Returns:
            List[Trigger]: All portable triggers
        """
        return [t for t in self.triggers if t.is_portable]

    def get_static_triggers(self) -> List[Trigger]:
        """
        Get all static (non-portable) triggers.
        
        Returns:
            List[Trigger]: All static triggers
        """
        return [t for t in self.triggers if not t.is_portable]

    def get_trigger_by_id(self, trigger_id: int) -> Trigger | None:
        """
        Get a trigger by its ID.
        
        Args:
            trigger_id: Trigger ID to search for
            
        Returns:
            Trigger: Trigger object or None if not found
        """
        for trigger in self.triggers:
            if trigger.i_trg == trigger_id:
                return trigger
        return None

    def clear_triggers_for_zone(self, zone_id: int) -> int:
        """
        Clear all triggers for a specific zone.
        
        Args:
            zone_id: Zone ID to clear triggers for
            
        Returns:
            int: Number of triggers removed
        """
        initial_count = len(self.triggers)
        self.triggers = [t for t in self.triggers if t.zone_id != zone_id]
        removed_count = initial_count - len(self.triggers)
        logger.debug(f"Cleared {removed_count} triggers for zone {zone_id}")
        return removed_count

    def clear_all_triggers(self) -> int:
        """
        Clear all triggers.
        
        Returns:
            int: Number of triggers removed
        """
        count = len(self.triggers)
        self.triggers.clear()
        logger.debug(f"Cleared all {count} triggers")
        return count

    def get_trigger_stats(self) -> dict:
        """
        Get trigger statistics.
        
        Returns:
            dict: Statistics about loaded triggers
        """
        portable_count = sum(1 for t in self.triggers if t.is_portable)
        static_count = len(self.triggers) - portable_count
        
        zones = set(t.zone_id for t in self.triggers if t.zone_id is not None)
        
        return {
            'total_triggers': len(self.triggers),
            'portable_triggers': portable_count,
            'static_triggers': static_count,
            'zones_with_triggers': len(zones),
            'zone_list': sorted([z for z in zones if z is not None])
        }

    def validate_trigger_integrity(self) -> bool:
        """
        Validate the integrity of loaded triggers.
        
        Returns:
            bool: True if all triggers are valid, False otherwise
        """
        try:
            for trigger in self.triggers:
                if not hasattr(trigger, 'i_trg') or trigger.i_trg is None:
                    logger.error(f"Trigger missing ID: {trigger}")
                    return False
                if not hasattr(trigger, 'name') or not trigger.name:
                    logger.error(f"Trigger {trigger.i_trg} missing name")
                    return False
                if not hasattr(trigger, 'zone_id') or trigger.zone_id is None:
                    logger.error(f"Trigger {trigger.i_trg} missing zone_id")
                    return False
                if not hasattr(trigger, 'direction'):
                    logger.error(f"Trigger {trigger.i_trg} missing direction")
                    return False
                    
            logger.debug("Trigger integrity validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Trigger integrity validation failed: {str(e)}")
            return False