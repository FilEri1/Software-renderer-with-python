import random

from vector import *

class Ring:
    def __init__(self, player, existing_rings, existing_buildings):
        ring_start_pos = Vec3()

        self.player = player
        self.position = Vec3()

        self.min_distance = 20
        self.spawn_attempts = 5

        self.existing_rings = existing_rings
        self.existing_buildings = existing_buildings
        self.position = self.gen_position(existing_rings, existing_buildings)

        self.speed = 0

        self.radius = 3

    def gen_position(self, existing_rings, existing_buildings):
        for _ in range(self.spawn_attempts):
            pos = self.rand_position_near_player()

            no_close_rings = all((pos - ring.position).length() >= self.min_distance for ring in existing_rings)
            no_building_conflict = all(abs(pos.x - building.x) > 20 for building in existing_buildings)

            if no_close_rings and no_building_conflict:
                return pos

        return self.rand_position_near_player()

    def rand_position_near_player(self):
        spread_x = 10
        spread_y = 10
        min_y = 7
        max_z = 0
        min_z = -20

        if self.existing_rings:
            base_pos = self.existing_rings[-1].position
            z_pos = base_pos.z + random.uniform(-80, -30)
            y_pos = base_pos.y + random.uniform((base_pos.y - spread_y), (base_pos.y + spread_y))
        else:
            base_pos = self.player.position
            z_pos = 0
            y_pos = 10

        raw_y = random.uniform(base_pos.y - spread_y, base_pos.y + spread_y)
        y_pos = max(raw_y, min_y)

        if z_pos < -125:
            z_pos = -125

        return Vec3(
            round(random.uniform(base_pos.x - spread_x, base_pos.x + spread_x)),
            round(y_pos),
            round(z_pos)
        )

    def score_ring(self, player, ring):
        d_x = player.position.x - ring.position.x
        d_y = player.position.y - ring.position.y

        if d_x * d_x + d_y * d_y <= self.radius * self.radius:
            player.score += 1
            if player.player_health < 100:
                player.player_health += 10
        else:
            if player.player_health > 0:
                player.player_health -= 10