from sys import flags

from vector import *
from matrix import Mat4
from graphics import *

class Player:
    def __init__(self, player_speed: float, position=Vec3(), rotation=Vec3()):
        self.position = position
        self.rotation = rotation
        self.player_speed = player_speed
        self.player_health = 100

        self.model = Mat4.identity()
        self.model = self.model.translation(self.position.x, self.position.y, self.position.z)

        self.target_pos = self.position
        self.tilt = Vec3()
        self.target_tilt = Vec3()

        self.score = 0
        # Skeppets delar:
        self.body_mesh = Mesh.create_horizontal_double_pyramid_mesh(Vec3(), height=0.5, size=0.8, color=0xFFBDB9B9)
        self.body_mat = Mat4.identity()

        self.right_wing_mesh = Mesh.create_tetrahedron_mesh_length_think(Vec3(), length=3, thickness=0.25, color=0xFFBDB9B9)
        self.right_wing_model = Mat4.identity()
        right_wing_rot = Mat4.identity()
        right_wing_rot = Mat4.rotation_x(70)
        right_wing_trans = Mat4.identity()
        right_wing_trans = Mat4.translation(0.8, -0.5, -1)

        self.right_wing_model = right_wing_rot * right_wing_trans

        self.left_wing_mesh = Mesh.create_tetrahedron_mesh_length_think(Vec3(), length=3, thickness=0.25, color=0xFBDB9B9)
        self.left_wing_model = Mat4.identity()
        left_wing_rot = Mat4.identity()
        left_wing_rot = Mat4.rotation_x(70)
        left_wing_trans = Mat4.identity()
        left_wing_trans = Mat4.translation(-0.8, -0.5, -1)

        self.left_wing_model = left_wing_rot * left_wing_trans

        self.right_min_wing = Mesh.create_tetrahedron_mesh_length_think(Vec3(), length=2.2, thickness=0.25, color=0xFF8578FF)
        self.r_m_w_model = Mat4.identity()

        r_m_w_rot = Mat4.identity()
        r_m_w_rot_y = Mat4.rotation_y(250)
        r_m_w_rot_z = Mat4.rotation_z(80.5)

        r_m_w_rot = r_m_w_rot_y * r_m_w_rot_z

        r_m_w_trans = Mat4.identity()
        r_m_w_trans = Mat4.translation(-0.2, 0, -0.6)

        self.r_m_w_model = r_m_w_rot * r_m_w_trans

        self.left_min_wing = Mesh.create_tetrahedron_mesh_length_think(Vec3(), length=2, thickness=0.2, color=0xFF8578FF)
        self.l_m_w_model = Mat4.identity()

        l_m_w_rot = Mat4.identity()
        l_m_w_rot = Mat4.rotation_z(80)

        l_m_w_trans = Mat4.identity()
        l_m_w_trans = Mat4.translation(0, -0.6, 0)

        self.l_m_w_model = l_m_w_rot * l_m_w_trans

        self.parts = [
            (self.right_wing_mesh, self.right_wing_model),
            (self.left_wing_mesh, self.left_wing_model),
            (self.right_min_wing, self.r_m_w_model),
            (self.left_min_wing, self.l_m_w_model),
            (self.body_mesh, self.body_mat)
        ]

        # Projektil:
        self.projectile_mesh = Mesh.create_tetrahedron_mesh_length_think(Vec3(), 2.0, 0.5,
                                                                         0xFF0000FF)
        self.projectiles = []
        self.shoot_timer = 0
        self.shoot_cooldown = 100

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

        if self.shoot_timer <= 0:
            if keys[4]:  # Space
                projectile_position = Vec3(self.position.x, self.position.y, self.position.z + 8)

                projectile_dir = Vec3(
                    math.sin(math.radians(self.rotation.z) / 2),
                    math.sin(math.radians(self.rotation.x)),
                    -math.cos(math.radians(self.rotation.z))
                ).normalize()

                projectile_speed = 1

                projectile_data = {
                    "position": projectile_position,
                    "direction": projectile_dir,
                    "speed": projectile_speed,
                    "model": Mat4.translation(projectile_position.x, projectile_position.y, projectile_position.z)
                }

                self.projectiles.append(projectile_data)

                self.shoot_timer = self.shoot_cooldown

        else:
            self.shoot_timer -= delta_time

        if direction.length() > 0:
            direction = direction.normalize()
            move_amount = direction * self.player_speed * delta_time
            self.target_pos += move_amount

        if self.target_pos.y < 7:
            self.target_pos.y = 7

        lerp_speed = 0.007
        self.position = self.position.lerp(self.target_pos, lerp_speed * delta_time)
        self.tilt = self.tilt.lerp(self.target_tilt, lerp_speed * delta_time)
        self.rotation = self.rotation.lerp(self.tilt, lerp_speed * delta_time)

        rotation_x = Mat4.rotation_x(math.radians(self.rotation.x))
        rotation_z = Mat4.rotation_z(math.radians(self.rotation.z))

        translation = Mat4.translation(self.position.x, self.position.y, self.position.z)

        self.model = rotation_z * rotation_x * translation

        updated_projectiles = []
        if self.projectiles:
            for proj in self.projectiles:
                proj['position'] += proj['direction'] * proj['speed'] * delta_time
                proj['model'] = Mat4.translation(proj['position'].x, proj['position'].y, proj['position'].z)

                if proj['position'].z > -100:
                    updated_projectiles.append(proj)
            self.projectiles = updated_projectiles

    def get_projectiles(self):
        return [proj['position'] for proj in self.projectiles]

    def remove_projectile_at_index(self, idx: int):
        if 0 <= idx < len(self.projectiles):
            self.projectiles.pop(idx)