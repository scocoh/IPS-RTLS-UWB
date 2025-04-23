# /home/parcoadmin/parco_fastapi/app/manager/portable_trigger.py
# Version: 1.0.0-250420
# Purpose: Defines PortableTrigger class for ParcoRTLS portable trigger support
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from .trigger import Trigger
from .region import Region3D, Region3DCollection
import logging

logger = logging.getLogger(__name__)

class PortableTrigger(Trigger):
    def __init__(self, tag_id: str, radius_ft: float = 3.0, z_min: float = 0.0, z_max: float = 10.0, **kwargs):
        super().__init__(is_portable=True, **kwargs)
        self.assigned_tag_id = tag_id
        self.radius = radius_ft
        self.z_min = z_min
        self.z_max = z_max
        self.regions = Region3DCollection()
        self.regions.add(Region3D(
            min_x=-radius_ft, max_x=radius_ft,
            min_y=-radius_ft, max_y=radius_ft,
            min_z=z_min, max_z=z_max
        ))
        self.is_valid = self.validate()
        logger.debug(f"Initialized PortableTrigger for tag {tag_id} with radius {radius_ft}ft, z_range [{z_min}, {z_max}]")

    def update_position_from_tag(self, tag):
        if tag.id == self.assigned_tag_id:
            self.move_to(tag.x, tag.y, tag.z)
            logger.debug(f"Updated PortableTrigger {self.name} position to ({tag.x}, {tag.y}, {tag.z}) for tag {tag.id}")