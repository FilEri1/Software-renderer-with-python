import random

from vector import *

class Background_buildings:
    def __init__(self, max_buildings):
        self.max_buildings = max_buildings
        self.current_buildings: int = 0
        self.buildings = []

    def create_building(self, player):
        min_position = Vec3(
            player.position.x - 30,
            0
            -50
        )

        max_position = Vec3(
            player.position.x + 30,
            0,
            25
        )

        building_position = Vec3(
            random.uniform(min_position.x, max_position.x),
            random.uniform(min_position.y, max_position.y),
            random.uniform(min_position.z, max_position.z)
        )

        return building_position

    def update_buildings(self, player, delta_time):
        if self.current_buildings < self.max_buildings:
            new_building = self.create_building(player)
            self.buildings.append(new_building)
            self.current_buildings += 1

        for building in self.buildings:
            building.z += 5 * delta_time