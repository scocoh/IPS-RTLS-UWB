from typing import List

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
        # Simplified: Move the centroid to the absolute position
        centroid_x = (self.min_x + self.max_x) / 2
        centroid_y = (self.min_y + self.max_y) / 2
        centroid_z = (self.min_z + self.max_z) / 2
        delta_x = absolute_x - centroid_x
        delta_y = absolute_y - centroid_y
        delta_z = absolute_z - centroid_z
        self.move_by(delta_x, delta_y, delta_z)

class Region3DCollection:
    def __init__(self):
        self.regions: List[Region3D] = []

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
        total_x = sum((r.min_x + r.max_x) / 2 for r in self.regions) / len(self.regions)
        total_y = sum((r.min_y + r.max_y) / 2 for r in self.regions) / len(self.regions)
        total_z = sum((r.min_z + r.max_z) / 2 for r in self.regions) / len(self.regions)
        delta_x = absolute_x - total_x
        delta_y = absolute_y - total_y
        delta_z = absolute_z - total_z
        self.move_by(delta_x, delta_y, delta_z)