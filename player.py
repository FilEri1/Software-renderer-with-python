from vector import *
from matrix import *
from graphics import *
from render import *

class Player:
    def __init__(self, start_pos=(0, 0, 0), color=0xFFFFFFFF):
        self.position = Vec3(*start_pos)
        self.rotation = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.color = color
        self.model = Mat4.identity()
        self.model = Mat4.translation(0, 0, -3)

    def draw_player(self, view_matrix, mesh):
        model_view_matrix = view_matrix * self.model
        transformed_mesh = mesh.transform(model_view_matrix)

        return transformed_mesh

    def player_update(self, keys, delta_time):
        speed = 5.0
        if keys[0]:  # W
            self.position += Vec3(0, 0, 1) * (speed * delta_time)
        if keys[1]:  # A
            self.position += Vec3(-1, 0, 0) * (speed * delta_time)
        if keys[2]:  # S
            self.position += Vec3(0, 0, -1) * (speed * delta_time)
        if keys[3]:  # D
            self.position += Vec3(1, 0, 0) * (speed * delta_time)

        self.model = Mat4.translation(self.position.x, self.position.y, self.position.z)