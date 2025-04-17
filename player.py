from vector import *
from matrix import Mat4

class Player:
    def __init__(self, player_speed: float, position=Vec3(), rotation=Vec3()):
        self.position = position
        self.rotation = rotation
        self.player_speed = player_speed

        self.model = Mat4.identity()
        self.model = self.model.translation(self.position.x, self.position.y, self.position.z)

        self.target_pos = self.position
        self.tilt = Vec3()
        self.target_tilt = Vec3()

    def player_update(self, keys, delta_time):
        direction = Vec3()


        self.target_tilt = Vec3()

        if keys[0]:  # W
            direction += Vec3(0, 1, 0)
            self.target_tilt.x = 15
        if keys[1]:  # A
            direction += Vec3(1, 0, 0)
            self.target_tilt.z = -15
        if keys[2]:  # S
            direction += Vec3(0, -1, 0)
            self.target_tilt.x = -15
        if keys[3]:  # D
            direction += Vec3(-1, 0, 0)
            self.target_tilt.z = 15

        if direction.length() > 0:
            direction = direction.normalize()
            move_amount = direction * self.player_speed * delta_time
            self.target_pos += move_amount

        lerp_speed = 0.007
        self.position = self.position.lerp(self.target_pos, lerp_speed * delta_time)
        self.tilt = self.tilt.lerp(self.target_tilt, lerp_speed * delta_time)
        self.rotation = self.rotation.lerp(self.tilt, lerp_speed * delta_time)

        # Uppdaterar model matrisen:
        rotation_x = Mat4.rotation_x(math.radians(self.rotation.x))
        rotation_z = Mat4.rotation_z(math.radians(self.rotation.z))
        translation = Mat4.translation(self.position.x, self.position.y, self.position.z)

        self.model = rotation_z * rotation_x * translation