import math

from vector import *
from matrix import *
from graphics import *

class Target:
    def __init__(self, position: Vec3=(0, 0, 0), health=100, flee_z=-100):
        self.position = position
        self.health = health
        self.hit_radius = 10
        self.flee_z = flee_z
        self.fleeing = False
        self.tilt_angle = 0
        self.speed = 0.01
        self.mesh = Mesh.create_horizontal_double_pyramid_mesh(Vec3(), 5, 5, 0xFFFF0000)
        self.model = Mat4.identity()
        self.rotation_angle = 0

    def update_target(self, delta_time):
        self.position.z -= self.speed * delta_time
        self.rotation_angle += 1 * delta_time

        if not self.fleeing and self.position.z < self.flee_z:
            self.fleeing = True
            self.tilt_angle = 30

        if self.fleeing:
            self.position.y += self.speed * delta_time * 10

        spin = Mat4.rotation_y(math.radians(self.rotation_angle))

        if self.fleeing:
            tilt = Mat4.rotation_x(math.radians(-self.tilt_angle))
            trans = Mat4.translation(self.position.x, self.position.y, self.position.z)
            self.model = tilt * spin * trans
        else:
            trans = Mat4.translation(self.position.x, self.position.y, self.position.z)
            self.model = spin * trans

    def check_hit(self, projectile_positions):
        hit_indices = []
        for i, proj_pos in enumerate(projectile_positions):
            if (proj_pos - self.position).length() < self.hit_radius:
                hit_indices.append(i)
        return hit_indices

    def take_damage(self, damage: int):
        self.health -= damage
        return self.health <= 0

    def is_destroyed(self):
        return self.health <= 0