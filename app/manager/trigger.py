# Version: 250327 /home/parcoadmin/parco_fastapi/app/manager/trigger.py 1.0.11
#
# Trigger Module for Manager for ParcoRTLS
#   
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from typing import Dict, List, Optional, Callable
from .enums import TriggerDirections, TriggerState
from .models import Tag
from .region import Region3DCollection
from .events import StreamDataEventArgs  # Updated import
from .utils import MQTT_BROKER
import paho.mqtt.publish as publish
import logging

logger = logging.getLogger(__name__)

class TagState:
    def __init__(self, tag_id: str, state: TriggerState):
        self.id = tag_id
        self.state = state

class Trigger:
    def __init__(self, i_trg: int = 0, name: str = "", direction: TriggerDirections = TriggerDirections.NotSet, regions: Optional[Region3DCollection] = None, ignore_unknowns: bool = False, tags: Optional[List[Tag]] = None):
        self.i_trg = i_trg
        self.key = None
        self.name = name
        self.direction = direction
        self.regions = regions if regions else Region3DCollection()
        self.tags = {tag.id: tag for tag in (tags if tags else [])}
        self.is_valid = self.validate()
        self.ignore_unknowns = ignore_unknowns
        self.raise_event_on_first_encounter = True
        self.states: Dict[str, TagState] = {}
        self.trigger_callback: Optional[Callable[[StreamDataEventArgs], None]] = None

    def validate(self) -> bool:
        self.is_valid = self.regions.count() > 0
        return self.is_valid

    def contains_point(self, x: float, y: float, z: float) -> bool:
        if not self.is_valid:
            raise Exception(f"Trigger {self.name} has no regions set.")
        for region in self.regions:
            if region.contains_point(x, y, z):
                return True
        return False

    def move_by(self, delta_x: float, delta_y: float, delta_z: float):
        if self.regions.count() >= 1:
            self.regions.move_by(delta_x, delta_y, delta_z)

    def move_to(self, absolute_x: float, absolute_y: float, absolute_z: float):
        if self.regions.count() >= 1:
            self.regions.move_to(absolute_x, absolute_y, absolute_z)

    async def check_trigger(self, tag: Tag) -> bool:
        if not self.is_valid:
            raise Exception(f"Trigger {self.name} has no regions set.")
        if self.direction == TriggerDirections.NotSet:
            raise Exception(f"Trigger {self.name} direction not set.")
        if self.ignore_unknowns and tag.id not in self.tags:
            return False

        pt_x, pt_y, pt_z = tag.x, tag.y, tag.z
        s = self.get_state(tag.id)
        new_state = self.point_state(pt_x, pt_y, pt_z)
        event = False
        first_encounter = s.state == TriggerState.NotKnown and not self.raise_event_on_first_encounter

        if self.direction == TriggerDirections.OnCross:
            if new_state != s.state:
                event = True
            s.state = new_state
        elif self.direction == TriggerDirections.OnEnter:
            if new_state != s.state and new_state == TriggerState.InSide:
                event = True
            s.state = new_state
        elif self.direction == TriggerDirections.OnExit:
            if new_state != s.state and new_state == TriggerState.OutSide:
                event = True
            s.state = new_state
        elif self.direction == TriggerDirections.WhileIn:
            if self.point_state(pt_x, pt_y, pt_z) == TriggerState.InSide:
                event = True
        elif self.direction == TriggerDirections.WhileOut:
            if self.point_state(pt_x, pt_y, pt_z) == TriggerState.OutSide:
                event = True

        if event and not first_encounter:
            if self.trigger_callback:
                await self.trigger_callback(StreamDataEventArgs(tag=tag))
            # Publish MQTT event to align with trigger.py
            try:
                publish.single("home/rtls/trigger", self.name, hostname=MQTT_BROKER)
                logger.info(f"Published MQTT event for trigger {self.name}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT event for trigger {self.name}: {str(e)}")
            return True
        return False

    def point_state(self, x: float, y: float, z: float) -> TriggerState:
        for region in self.regions:
            if region.contains_point(x, y, z):
                return TriggerState.InSide
        return TriggerState.OutSide

    def get_state(self, tag_id: str) -> TagState:
        if tag_id in self.states:
            return self.states[tag_id]
        s = TagState(tag_id=tag_id, state=TriggerState.NotKnown)
        self.states[tag_id] = s
        return s