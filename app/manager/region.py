# /home/parcoadmin/parco_fastapi/app/manager/region.py
# Name: region.py
# Version: 0.1.75
# Created: 971201
# Modified: 250709
# Creator: ParcoAdmin
# Modified By: ParcoAdmin & Claude
# Description: Region management with hybrid polygon containment
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# Version: 0.1.75 - Added hybrid polygon containment methods for accurate trigger detection
# Version: 1.0.2-250430 - Convert vertex coordinates to floats in from_vertices, added logging, bumped from 1.0.1

from typing import List, Tuple, Optional
import logging

# Force logging configuration for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.handlers = []
logger.addHandler(handler)
logger.propagate = False

class Region3D:
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float, min_z: float, max_z: float, vertices: Optional[List[Tuple[float, float, float]]] = None):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z
        self.vertices = vertices  # NEW: Store vertices for polygon containment

    def contains_point(self, x: float, y: float, z: float) -> bool:
        """Original bounding box containment check - PRESERVED for backwards compatibility"""
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y and
                self.min_z <= z <= self.max_z)

    def contains_point_in_2d(self, x: float, y: float) -> bool:
        """Original 2D bounding box containment check - PRESERVED for backwards compatibility"""
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y)

    def contains_point_polygon_2d(self, x: float, y: float) -> bool:
        """Check if point is inside polygon using ray casting algorithm (2D only)"""
        if not self.vertices or len(self.vertices) < 3:
            logger.warning("Insufficient vertices for 2D polygon check, falling back to bounding box")
            return self.contains_point_in_2d(x, y)
        
        inside = False
        j = len(self.vertices) - 1
        
        for i in range(len(self.vertices)):
            xi, yi = self.vertices[i][0], self.vertices[i][1]
            xj, yj = self.vertices[j][0], self.vertices[j][1]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        logger.debug(f"2D polygon check: point ({x}, {y}) inside = {inside}")
        return inside

    def contains_point_polygon_3d(self, x: float, y: float, z: float) -> bool:
        """Check if point is inside 3D polygon (projects to 2D + Z bounds check)"""
        if not self.vertices or len(self.vertices) < 3:
            logger.warning("Insufficient vertices for 3D polygon check, falling back to bounding box")
            return self.contains_point(x, y, z)
        
        # First check Z bounds
        if z < self.min_z or z > self.max_z:
            logger.debug(f"3D polygon check: point ({x}, {y}, {z}) outside Z bounds [{self.min_z}, {self.max_z}]")
            return False
        
        # Then check 2D polygon projection
        inside_2d = self.contains_point_polygon_2d(x, y)
        logger.debug(f"3D polygon check: point ({x}, {y}, {z}) inside = {inside_2d}")
        return inside_2d

    def contains_point_hybrid(self, x: float, y: float, z: float = None) -> bool:
        """Hybrid containment: Fast bounding box pre-filter + precise polygon check"""
        # Fast bounding box pre-filter
        if z is not None:
            if not self.contains_point(x, y, z):
                logger.debug(f"Hybrid check: point ({x}, {y}, {z}) outside bounding box")
                return False
        else:
            if not self.contains_point_in_2d(x, y):
                logger.debug(f"Hybrid check: point ({x}, {y}) outside 2D bounding box")
                return False
        
        # If no vertices available, fall back to bounding box result
        if not self.vertices or len(self.vertices) < 3:
            logger.debug("Hybrid check: no vertices available, using bounding box result")
            return True  # Already passed bounding box check above
        
        # Precise polygon containment check
        if z is not None:
            result = self.contains_point_polygon_3d(x, y, z)
        else:
            result = self.contains_point_polygon_2d(x, y)
        
        logger.debug(f"Hybrid check final result: point ({x}, {y}, {z}) inside = {result}")
        return result

    def move_by(self, delta_x: float, delta_y: float, delta_z: float):
        self.min_x += delta_x
        self.max_x += delta_x
        self.min_y += delta_y
        self.max_y += delta_y
        self.min_z += delta_z
        self.max_z += delta_z
        
        # Also move vertices if present
        if self.vertices:
            self.vertices = [(x + delta_x, y + delta_y, z + delta_z) for x, y, z in self.vertices]

    def move_to(self, absolute_x: float, absolute_y: float, absolute_z: float):
        # Move the centroid to the absolute position
        centroid_x, centroid_y, centroid_z = self.box_centroid()
        delta_x = absolute_x - centroid_x
        delta_y = absolute_y - centroid_y
        delta_z = absolute_z - centroid_z
        self.move_by(delta_x, delta_y, delta_z)

    def box_centroid(self) -> Tuple[float, float, float]:
        """Calculate the centroid of the bounding box surrounding the region.

        Returns:
            Tuple[float, float, float]: The (x, y, z) coordinates of the centroid.
        """
        centroid_x = (self.min_x + self.max_x) / 2
        centroid_y = (self.min_y + self.max_y) / 2
        centroid_z = (self.min_z + self.max_z) / 2
        return (centroid_x, centroid_y, centroid_z)

class Region3DCollection:
    def __init__(self):
        self.regions: List[Region3D] = []

    @classmethod
    def from_vertices(cls, vertices: List[dict]) -> 'Region3DCollection':
        """Create a Region3DCollection from a list of vertices.

        Args:
            vertices: List of dictionaries with 'x', 'y', and optional 'z' keys.

        Returns:
            Region3DCollection: A collection containing a single Region3D defined by the vertices.
        """
        collection = cls()
        if not vertices or len(vertices) < 3:
            logger.warning("Insufficient vertices to create Region3D: returning empty collection")
            return collection
        
        # Convert vertex coordinates to floats to handle string inputs
        xs = [float(v["x"]) for v in vertices]
        ys = [float(v["y"]) for v in vertices]
        zs = [float(v.get("z", 0.0)) for v in vertices]
        
        # Convert to tuple format for polygon containment
        vertex_tuples = [(xs[i], ys[i], zs[i]) for i in range(len(vertices))]
        
        # Log the data types for debugging
        logger.debug(f"Vertex coordinates types: xs={type(xs[0])}, ys={type(ys[0])}, zs={type(zs[0])}")
        logger.debug(f"Vertex coordinates: xs={xs}, ys={ys}, zs={zs}")
        
        region = Region3D(
            min_x=min(xs),
            max_x=max(xs),
            min_y=min(ys),
            max_y=max(ys),
            min_z=min(zs),
            max_z=max(zs),
            vertices=vertex_tuples  # NEW: Pass vertices for polygon containment
        )
        
        logger.debug(f"Created Region3D: min=({region.min_x}, {region.min_y}, {region.min_z}), "
                     f"max=({region.max_x}, {region.max_y}, {region.max_z}), vertices={len(vertex_tuples)}")
        collection.add(region)
        return collection

    def add(self, region: Region3D):
        self.regions.append(region)

    def count(self) -> int:
        return len(self.regions)

    def __iter__(self):
        return iter(self.regions)

    def move_by(self, delta_x: float, delta_y: float, delta_z: float):
        for region in self.regions:
            region.move_by(delta_x, delta_y, delta_z)

    def move_to(self, absolute_x: float, absolute_y: float, absolute_z: float):
        # Compute composite centroid
        if not self.regions:
            return
        total_x = sum(r.box_centroid()[0] for r in self.regions) / len(self.regions)
        total_y = sum(r.box_centroid()[1] for r in self.regions) / len(self.regions)
        total_z = sum(r.box_centroid()[2] for r in self.regions) / len(self.regions)
        delta_x = absolute_x - total_x
        delta_y = absolute_y - total_y
        delta_z = absolute_z - total_z
        self.move_by(delta_x, delta_y, delta_z)