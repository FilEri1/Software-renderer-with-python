from vector import *
from matrix import *

class Camera:
    def __init__(self, position=Vec3(0, 0, 0), rotation=Vec3(0, 0, 0)):
        self.position = position
        self.rotation = rotation

        self.move_speed = 0.02

        self.camera = Vec3()

    def update_camera(self, keys, delta_time):
        forward = Camera.get_forward_vector(self.rotation)
        right = Vec3(0, 1, 0).cross(forward).normalize()

        direction = Vec3()

        # WASD & SPACE & Z
        if keys[0]:
            direction += forward
        if keys[1]:
            direction += right
        if keys[2]:
            direction -= forward
        if keys[3]:
            direction -= right
        if keys[4]:
            direction += Vec3(0, 1, 0)
        if keys[5]:
            direction -= Vec3(0, 1, 0)

        self.position += direction * delta_time * self.move_speed

    @staticmethod
    def get_forward_vector(camera_rotation: Vec3):
        yaw_rad = math.radians(camera_rotation.y)
        pitch_rad = math.radians(camera_rotation.x)
        return Vec3(
            -math.sin(yaw_rad) * math.cos(pitch_rad),  # -x for right
            math.sin(pitch_rad),
            -math.cos(yaw_rad) * math.cos(pitch_rad)  # -z for forward
        ).normalize()