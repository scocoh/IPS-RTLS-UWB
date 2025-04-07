# /home/parcoadmin/parco_fastapi/app/manager/region.py
# Version: 1.0.1 - Added box_centroid method and refactored move_to; added from_vertices method
from typing import List, Tuple

class Region3D:
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float, min_z: float, max_z: float):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z

    def contains_point(self, x: float, y: float, z: float) -> bool:
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y and
                self.min_z <= z <= self.max_z)

    def move_by(self, delta_x: float, delta_y: float, delta_z: float):
        self.min_x += delta_x
        self.max_x += delta_x
        self.min_y += delta_y
        self.max_y += delta_y
        self.min_z += delta_z
        self.max_z += delta_z

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
            return collection  # Empty collection if vertices are insufficient
        xs = [v["x"] for v in vertices]
        ys = [v["y"] for v in vertices]
        zs = [v.get("z", 0.0) for v in vertices]
        region = Region3D(
            min_x=min(xs),
            max_x=max(xs),
            min_y=min(ys),
            max_y=max(ys),
            min_z=min(zs),
            max_z=max(zs)
        )
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