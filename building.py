import random

from vector import *

class Building:
    def __init__(self, max_buildings):
        self.max_buildings = max_buildings
        self.existing_buildings = []
        self.max_attempts = 10

    def player_crashed(self, player, margin=1.0):
        for building in self.existing_buildings:

            tolerance = margin * 10
            in_x = abs(player.position.x - building.x) <= tolerance
            in_z = abs(player.position.z - building.z) <= tolerance

            if in_x and in_z:
                return True
        return False

    def is_position_blocked(self, x, rings, clearance=10):
        for ring in rings:
            if abs(x - ring.position.x) < clearance:
                return True
        return False

    def create_building(self, player):
        min_position = Vec3(
            player.position.x -40,
            0,
            -50
        )

        max_position = Vec3(
            player.position.x + 40,
            0,
            -25
        )

        new_building = Vec3(
            round(random.uniform(min_position.x, max_position.x)),
            0,
            round(random.uniform(min_position.z, max_position.z))
        )

        return new_building

    def move_buildings(self, delta_time, speed=0.01, max_z=100):
        for building in self.existing_buildings:
            building.z += speed * delta_time

        self.existing_buildings = [b for b in self.existing_buildings if b.z < max_z]

    def update_buildings(self, player, rings):
        if len(self.existing_buildings) < self.max_buildings:
            for _ in range(self.max_attempts):
                new_building = self.create_building(player)
                if not self.is_position_blocked(new_building.x, rings):
                    self.existing_buildings.append(new_building)
                    break