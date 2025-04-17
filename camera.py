from vector import *
from matrix import *

class Camera:
    def __init__(self, position=Vec3(0, 0, 0), rotation=Vec3(0, 0, 0)):
        self.position = position
        self.rotation = rotation

        self.move_speed = 0.02

        self.camera = Vec3()

        # Följ spelaren variabler:
        self.fixed_position = self.position
        self.target_position = Vec3()

        self.last_player_position_x = 0

        self.last_player_position_x = 0.0
        self.current_look_ahead = 0.0

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
            -math.sin(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            -math.cos(yaw_rad) * math.cos(pitch_rad)
        ).normalize()

    def follow_player(self, player_position: Vec3, player_rotation: Vec3, delta_time):
        inverted_x = -player_position.x

        dx = player_position.x - self.last_player_position_x

        threshold = 0.01
        target_look = 0.0
        if dx > threshold:
            target_look = 2.0
        elif dx < -threshold:
            target_look = -2.0
        else:
            target_look = 0.0

        look_smoothing = 0.005
        center_smoothing = 0.0009

        current_smoothing = look_smoothing if target_look != 0.0 else center_smoothing

        self.current_look_ahead += (target_look - self.current_look_ahead) * current_smoothing * delta_time

        target_x = inverted_x + self.current_look_ahead

        self.target_position = Vec3(
            target_x,
            player_position.y + 1,
            self.fixed_position.z
        )

        smoothing = 0.005
        self.position = self.position.lerp(
            self.target_position,
            smoothing * delta_time
        )
        self.position.z = self.fixed_position.z

        self.last_player_position_x = player_position.x

        return self.position