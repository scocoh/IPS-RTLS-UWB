# Name: trigger.py
# Version: 0.1.0
# Created: 971201
# Modified: 250724
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/trigger.py
# Version: 1.0.22-250724 - Fixed Pylance errors: async/await, type annotations, bumped from 1.0.21
from typing import Dict, List, Optional, Callable, Union, Awaitable
from .enums import TriggerDirections, TriggerState
from .models import Tag
from .region import Region3DCollection  # Kept for compatibility; using vertex data instead
from .events import StreamDataEventArgs
from .utils import MQTT_BROKER
import paho.mqtt.publish as publish
import logging
import asyncio

# Force logging configuration for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.handlers = []  # Clear any existing handlers
logger.addHandler(handler)
logger.propagate = False  # Prevent propagation to parent loggers

class TagState:
    def __init__(self, tag_id: str, state: TriggerState):
        self.id = tag_id    # Tag identifier
        self.state = state  # Current state (NotKnown, InSide, OutSide)
        self.cross_sequence: Optional[str] = None  # For OnCross: tracks sequence (None, "Started", "Inside")

class Trigger:
    def __init__(self, i_trg: int = 0, name: str = "", direction: TriggerDirections = TriggerDirections.NotSet, 
                 regions: Optional[Region3DCollection] = None, vertex_regions: Optional[List[dict]] = None, ignore_unknowns: bool = False, tags: Optional[List[Tag]] = None,
                 zone_id: Optional[int] = None, is_portable: bool = False):
        self.i_trg = i_trg                        # Trigger ID
        self.key = None                           # Optional user-defined key
        self.name = name                          # Trigger name
        self.direction = direction                # Trigger direction (e.g., WhileOut)
        self.regions = regions if regions else Region3DCollection() # 3D regions defining trigger area
        self.vertex_regions = vertex_regions if vertex_regions else [] # Vertex data for regions
        self.tags = {tag.id: tag for tag in (tags if tags else [])} # Tags to monitor (if restricted)
        self.zone_id = zone_id                    # Zone ID for validation
        self.is_portable = is_portable            # Flag to indicate if trigger is portable
        self.is_valid = self.validate()           # Validity flag based on regions
        self.ignore_unknowns = ignore_unknowns    # Ignore tags not in self.tags
        self.raise_event_on_first_encounter = True # Fire event on first state check
        self.states: Dict[str, TagState] = {}     # State tracking for tags
        self.trigger_callback: Optional[Callable[[StreamDataEventArgs], Union[None, Awaitable[None]]]] = None # Event callback
        self._zone_validated = False              # Track if zone validation completed

        # Schedule zone validation if needed (will be called by event loop)
        if not self.is_portable and self.zone_id:
            asyncio.create_task(self._auto_validate_zone())

    async def _auto_validate_zone(self):
        """Automatically validate trigger within zone - called during initialization."""
        try:
            await self.validate_trigger_within_zone()
            self._zone_validated = True
            logger.debug(f"Auto zone validation completed for trigger {self.name}")
        except Exception as e:
            logger.error(f"Auto zone validation failed for trigger {self.name}: {e}")
            # Don't raise - let the trigger exist but mark validation failure
            self._zone_validated = False

    def validate(self) -> bool:
        # Check if trigger has at least one region
        self.is_valid = len(self.vertex_regions) > 0 if self.vertex_regions else (self.regions.count() > 0)
        logger.debug(f"Trigger {self.name} (ID: {self.i_trg}) validation: is_valid={self.is_valid}")
        return self.is_valid

    async def validate_trigger_within_zone(self):
        """Validate that the trigger's regions are fully contained within the zone."""
        if not self.is_valid:
            raise Exception(f"Trigger {self.name} has no regions set.")
        if not self.zone_id:
            raise Exception(f"Trigger {self.name} has no associated zone ID for validation.")

        # Fetch zone bounding box (simplified for this example; ideally, fetch from DB)
        # This would typically be done via a database query similar to routes/trigger.py
        # For now, we'll assume the zone's bounding box is fetched elsewhere
        # Placeholder: Replace with actual zone bounding box retrieval
        zone_bbox = await self.get_zone_bounding_box(self.zone_id)

        # Check each region's bounding box against the zone's bounding box
        for region in self.regions:
            if (region.min_x < zone_bbox["min_x"] or region.max_x > zone_bbox["max_x"] or
                region.min_y < zone_bbox["min_y"] or region.max_y > zone_bbox["max_y"] or
                region.min_z < zone_bbox["min_z"] or region.max_z > zone_bbox["max_z"]):
                raise Exception(
                    f"Trigger {self.name} (ID: {self.i_trg}) region "
                    f"(min: ({region.min_x}, {region.min_y}, {region.min_z}), "
                    f"max: ({region.max_x}, {region.max_y}, {region.max_z})) "
                    f"is not fully contained within zone {self.zone_id} boundaries "
                    f"(min: ({zone_bbox['min_x']}, {zone_bbox['min_y']}, {zone_bbox['min_z']}), "
                    f"max: ({zone_bbox['max_x']}, {zone_bbox['max_y']}, {zone_bbox['max_z']}))"
                )

    async def get_zone_bounding_box(self, zone_id: int) -> dict:
        """Fetch the bounding box of a zone (placeholder for actual implementation)."""
        # This should query the database to fetch the zone's vertices and compute the bounding box
        # For now, we'll use a placeholder; integrate with actual database access as in routes/trigger.py
        raise NotImplementedError("Zone bounding box retrieval not implemented in manager/trigger.py")

    def contains_point(self, x: float, y: float, z: float) -> bool:
        # Check if a point is within any trigger region
        if not self.is_valid:
            raise Exception(f"Trigger {self.name} has no regions set.")
        # Prefer vertex_regions if available
        if self.vertex_regions:
            for region in self.vertex_regions:
                vertices = region.get("vertices", [])
                if not vertices or len(vertices) < 3:
                    logger.warning(f"Region for trigger {self.name} (ID: {self.i_trg}) has insufficient vertices")
                    continue
                inside = False
                j = len(vertices) - 1
                for i in range(len(vertices)):
                    v_i = vertices[i]
                    v_j = vertices[j]
                    if ((v_i["y"] > y) != (v_j["y"] > y)) and \
                       (x < (v_j["x"] - v_i["x"]) * (y - v_i["y"]) / (v_j["y"] - v_i["y"]) + v_i["x"]):
                        inside = not inside
                    j = i
                if inside:
                    logger.debug(f"Point ({x}, {y}, {z}) is inside vertex region for trigger {self.name}")
                    return True
            logger.debug(f"Point ({x}, {y}, {z}) is outside all vertex regions for trigger {self.name}")
            return False
        # Fallback to explicit bounding box check
        for region in self.regions:
            # Log data types to debug
            logger.debug(f"Region bounds types for trigger {self.name} (ID: {self.i_trg}): "
                         f"min_x={type(region.min_x)}, max_x={type(region.max_x)}, "
                         f"min_y={type(region.min_y)}, max_y={type(region.max_y)}, "
                         f"min_z={type(region.min_z)}, max_z={type(region.max_z)}")
            inside = (float(region.min_x) <= x <= float(region.max_x) and
                      float(region.min_y) <= y <= float(region.max_y) and
                      float(region.min_z) <= z <= float(region.max_z))
            logger.debug(f"Checking point ({x}, {y}, {z}) against region bounds for trigger {self.name} (ID: {self.i_trg}): "
                         f"min=({region.min_x}, {region.min_y}, {region.min_z}), "
                         f"max=({region.max_x}, {region.max_y}, {region.max_z}), "
                         f"inside={inside}, Region3DCollection.contains_point={region.contains_point(x, y, z)}")
            if inside:
                return True
        logger.debug(f"Point ({x}, {y}, {z}) is outside all regions for trigger {self.name} (ID: {self.i_trg})")
        return False

    async def move_by(self, delta_x: float, delta_y: float, delta_z: float):
        # Shift trigger regions by specified deltas
        if self.regions.count() >= 1:
            self.regions.move_by(delta_x, delta_y, delta_z)
            # Re-validate if non-portable
            if not self.is_portable and self.zone_id:
                await self.validate_trigger_within_zone()

    async def move_to(self, absolute_x: float, absolute_y: float, delta_z: float):
        # Move trigger regions to absolute coordinates
        if self.regions.count() >= 1:
            self.regions.move_to(absolute_x, absolute_y, delta_z)
            # Re-validate if non-portable
            if not self.is_portable and self.zone_id:
                await self.validate_trigger_within_zone()

    async def check_trigger(self, tag: Tag) -> bool:
        # Log entry for debugging trigger evaluation
        logger.debug(f"Checking trigger {self.name} (ID: {self.i_trg}) for tag {tag.id} at ({tag.x}, {tag.y}, {tag.z})")
        logger.debug(f"Current states: {self.states}")
        
        # Validate trigger setup
        if not self.is_valid:
            raise Exception(f"Trigger {self.name} has no regions set.")
        if self.direction == TriggerDirections.NotSet:
            raise Exception(f"Trigger {self.name} direction not set.")
        if self.ignore_unknowns and tag.id not in self.tags:
            logger.debug(f"Tag {tag.id} ignored by trigger {self.name} due to ignore_unknowns")
            return False

        # Get tag's current position
        pt_x, pt_y, pt_z = tag.x, tag.y, tag.z
        # Retrieve or initialize tag's previous state
        s = self.get_state(tag.id)
        # Determine current state (InSide or OutSide) based on position
        new_state = self.point_state(pt_x, pt_y, pt_z)
        logger.debug(f"Tag {tag.id} state: previous={s.state}, new={new_state}")

        # Flag to indicate if an event should fire
        event = False

        # Direction-specific logic follows
        if self.direction == TriggerDirections.OnCross:
            if s.cross_sequence is None:
                if new_state == TriggerState.OutSide:
                    s.cross_sequence = "Started"
                    logger.debug(f"OnCross: sequence started (OutSide)")
                elif new_state == TriggerState.InSide:
                    s.cross_sequence = "Inside"
                    logger.debug(f"OnCross: sequence started (InSide)")
            elif s.cross_sequence == "Started":
                if new_state == TriggerState.InSide:
                    s.cross_sequence = "Inside"
                    logger.debug(f"OnCross: sequence progressed to Inside")
            elif s.cross_sequence == "Inside":
                if new_state == TriggerState.OutSide:
                    event = True
                    s.cross_sequence = None  # Reset sequence
                    logger.debug(f"OnCross triggered: sequence completed (OutSide -> InSide -> OutSide)")
            s.state = new_state

        elif self.direction == TriggerDirections.OnEnter:
            # Only fire if transitioning from OutSide to InSide (ignore NotKnown)
            if s.state == TriggerState.OutSide and new_state == TriggerState.InSide:
                event = True
                logger.debug(f"OnEnter triggered: tag moved from OutSide to InSide")
            s.state = new_state

        elif self.direction == TriggerDirections.OnExit:
            # Only fire if transitioning from InSide to OutSide (ignore NotKnown)
            if s.state == TriggerState.InSide and new_state == TriggerState.OutSide:
                event = True
                logger.debug(f"OnExit triggered: tag moved from InSide to OutSide")
            s.state = new_state

        elif self.direction == TriggerDirections.WhileIn:
            # Stateless: Fire every time the tag is inside the region
            if new_state == TriggerState.InSide:
                event = True
                logger.debug(f"WhileIn triggered: tag inside region")
            else:
                logger.debug(f"WhileIn: tag outside region, no event fired")
            # Do not update state for WhileIn (stateless for performance)

        elif self.direction == TriggerDirections.WhileOut:
            # Stateless: Fire every time the tag is outside the region
            if new_state == TriggerState.OutSide:
                event = True
                logger.debug(f"WhileOut triggered: tag outside region")
            else:
                logger.debug(f"WhileOut: tag inside region, no event fired")
            # Do not update state for WhileOut (stateless for performance)

        # Handle event firing if conditions met
        if event:
            logger.info(f"Event firing for trigger {self.name} (ID: {self.i_trg}) for tag {tag.id}")
            # Call callback if set (e.g., for Manager to send to WebSocket clients)
            if self.trigger_callback:
                callback_result = self.trigger_callback(StreamDataEventArgs(tag=tag))
                if asyncio.iscoroutine(callback_result):
                    await callback_result
            # Publish event to MQTT (full stream)
            try:
                publish.single("home/rtls/trigger", self.name, hostname=MQTT_BROKER)
                logger.info(f"Published MQTT event for trigger {self.name}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT event for trigger {self.name}: {str(e)}")
            logger.debug(f"Updated states after event: {self.states}")
            return True
        logger.debug(f"No event fired for trigger {self.name}")
        logger.debug(f"Updated states: {self.states}")
        return False

    def point_state(self, x: float, y: float, z: float) -> TriggerState:
        # Determine if point is inside any region
        logger.debug(f"Checking point ({x}, {y}, {z}) against trigger {self.name} (ID: {self.i_trg}) regions: {self.regions}")
        for region in self.regions:
            if self.contains_point(x, y, z):
                logger.debug(f"Point ({x}, {y}, {z}) inside region for trigger {self.name} (ID: {self.i_trg}): "
                             f"min=({region.min_x}, {region.min_y}, {region.min_z}), "
                             f"max=({region.max_x}, {region.max_y}, {region.max_z})")
                return TriggerState.InSide
        logger.debug(f"Point ({x}, {y}, {z}) outside all regions of trigger {self.name} (ID: {self.i_trg})")
        return TriggerState.OutSide

    def get_state(self, tag_id: str) -> TagState:
        # Retrieve or create tag state
        if tag_id in self.states:
            return self.states[tag_id]
        s = TagState(tag_id=tag_id, state=TriggerState.NotKnown)
        self.states[tag_id] = s
        return s