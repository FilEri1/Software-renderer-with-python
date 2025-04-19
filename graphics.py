from vector import *
from matrix import *

fov = 400

def perspective_divide(vec: Vec3) -> Vec2:
    if vec.z == 0: # Vi vill inte dela med z = 0!
        return Vec2(float('inf'), float('inf'))
    return Vec2(
        (vec.x * fov) / vec.z,
        (vec.y * fov) / vec.z
    )

class Vertex: # Håller 3D positionen av en "vertex" eller en 3D vektor utan magnitude vilket då blir en punkt.
    def __init__(self, position: Vec3):
        self.position = position

class Triangle: # Håller 3 vertices för varje triangel
    def __init__(self, v0: Vertex, v1: Vertex, v2: Vertex, color):
        self.vertices = [v0, v1, v2]
        self.color = color

    # Den här funktionen beräknar medel z värdet för trianglarna på en model så att vi sedan kan bestämma vilka trianglar
    # vi vill måla och vilka trianglar som är gömda bakom en annan och inte ska målas!
    def avg_z(self) -> float:
        return (
            self.vertices[0].position.z +
            self.vertices[1].position.z +
            self.vertices[2].position.z
        ) / 3.0

class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles

    def transform(self, matrix: Mat4):
        new_vertices = []

        for vertex in self.vertices:
            pos = [vertex.position.x, vertex.position.y, vertex.position.z, 1.0]
            transformed = matrix * pos
            new_vertices.append(Vertex(Vec3(*transformed[:3])))
        new_triangles = []
        for tri in self.triangles:
            idx0 = self.vertices.index(tri.vertices[0])
            idx1 = self.vertices.index(tri.vertices[1])
            idx2 = self.vertices.index(tri.vertices[2])
            new_triangles.append(Triangle(new_vertices[idx0], new_vertices[idx1], new_vertices[idx2], tri.color))
        return Mesh(new_vertices, new_triangles)

    @staticmethod
    def create_cube_mesh(center, size, color):
        hs = size / 2.0
        vertices = [
            Vertex(Vec3(center.x - hs, center.y - hs, center.z + hs)),
            Vertex(Vec3(center.x + hs, center.y - hs, center.z + hs)),
            Vertex(Vec3(center.x - hs, center.y + hs, center.z + hs)),
            Vertex(Vec3(center.x + hs, center.y + hs, center.z + hs)),
            Vertex(Vec3(center.x - hs, center.y - hs, center.z - hs)),
            Vertex(Vec3(center.x + hs, center.y - hs, center.z - hs)),
            Vertex(Vec3(center.x - hs, center.y + hs, center.z - hs)),
            Vertex(Vec3(center.x + hs, center.y + hs, center.z - hs))
        ]
        triangles = [
            # Framsidan
            Triangle(vertices[0], vertices[1], vertices[2], color),
            Triangle(vertices[1], vertices[3], vertices[2], color),
            # Backre sidan
            Triangle(vertices[4], vertices[6], vertices[5], color),
            Triangle(vertices[5], vertices[6], vertices[7], color),
            # Vänster sida
            Triangle(vertices[0], vertices[2], vertices[4], color),
            Triangle(vertices[2], vertices[6], vertices[4], color),
            # Höger sida
            Triangle(vertices[1], vertices[5], vertices[3], color),
            Triangle(vertices[3], vertices[5], vertices[7], color),
            # Översta sidan
            Triangle(vertices[2], vertices[3], vertices[6], color),
            Triangle(vertices[3], vertices[7], vertices[6], color),
            # Botten
            Triangle(vertices[0], vertices[4], vertices[1], color),
            Triangle(vertices[1], vertices[4], vertices[5], color)
        ]
        return Mesh(vertices, triangles)

    @staticmethod
    def create_box_mesh(center, width, height, depth, color):
        hw = width / 2.0  # half width
        hh = height / 2.0  # half height
        hd = depth / 2.0  # half depth

        vertices = [
            # Front face
            Vertex(Vec3(center.x - hw, center.y - hh, center.z + hd)),
            Vertex(Vec3(center.x + hw, center.y - hh, center.z + hd)),
            Vertex(Vec3(center.x - hw, center.y + hh, center.z + hd)),
            Vertex(Vec3(center.x + hw, center.y + hh, center.z + hd)),

            # Back face
            Vertex(Vec3(center.x - hw, center.y - hh, center.z - hd)),
            Vertex(Vec3(center.x + hw, center.y - hh, center.z - hd)),
            Vertex(Vec3(center.x - hw, center.y + hh, center.z - hd)),
            Vertex(Vec3(center.x + hw, center.y + hh, center.z - hd)),
        ]

        triangles = [
            # Front
            Triangle(vertices[0], vertices[1], vertices[2], color),
            Triangle(vertices[1], vertices[3], vertices[2], color),

            # Back
            Triangle(vertices[4], vertices[6], vertices[5], color),
            Triangle(vertices[5], vertices[6], vertices[7], color),

            # Left
            Triangle(vertices[0], vertices[2], vertices[4], color),
            Triangle(vertices[2], vertices[6], vertices[4], color),

            # Right
            Triangle(vertices[1], vertices[5], vertices[3], color),
            Triangle(vertices[3], vertices[5], vertices[7], color),

            # Top
            Triangle(vertices[2], vertices[3], vertices[6], color),
            Triangle(vertices[3], vertices[7], vertices[6], color),

            # Bottom
            Triangle(vertices[0], vertices[4], vertices[1], color),
            Triangle(vertices[1], vertices[4], vertices[5], color)
        ]

        return Mesh(vertices, triangles)

    @staticmethod
    def create_cylinder_mesh(center=Vec3(0, 0, 0), radius=1.0, height=1.0, color=0xFFFFFFFF):
        segments = 12
        half_h = height / 2.0
        vertices = []
        triangles = []
        # 1) Sidor: två trianglar per segment
        for i in range(segments):
            theta = 2 * math.pi * (i) / segments
            next_th = 2 * math.pi * (i + 1) / segments
            x0, z0 = math.cos(theta) * radius, math.sin(theta) * radius
            x1, z1 = math.cos(next_th) * radius, math.sin(next_th) * radius
            # Hörn på botten
            v0 = Vertex(Vec3(center.x + x0, center.y - half_h, center.z + z0))
            v1 = Vertex(Vec3(center.x + x1, center.y - half_h, center.z + z1))
            # Motsvarande hörn på toppen
            v2 = Vertex(Vec3(center.x + x0, center.y + half_h, center.z + z0))
            v3 = Vertex(Vec3(center.x + x1, center.y + half_h, center.z + z1))
            # Spara vertices
            vertices.extend([v0, v1, v2, v3])
            # Två trianglar för denna “väggbit”
            triangles.append(Triangle(v0, v1, v2, color))
            triangles.append(Triangle(v2, v1, v3, color))
        # 2) Locken
        # Topplockets mittpunkt
        top_center = Vertex(Vec3(center.x, center.y + half_h, center.z))
        bottom_center = Vertex(Vec3(center.x, center.y - half_h, center.z))
        vertices.extend([top_center, bottom_center])
        # Trianglar ut mot kanten för varje segment
        for i in range(segments):
            # index i*4+2 och +3 är de två “övre” hörnen för segment i
            v_top_a = vertices[i * 4 + 2]
            v_top_b = vertices[((i + 1) % segments) * 4 + 2]
            triangles.append(Triangle(top_center, v_top_a, v_top_b, color))
            # index i*4+0 och +1 är de två “nedre” hörnen för segment i
            v_bot_a = vertices[i * 4 + 0]
            v_bot_b = vertices[((i + 1) % segments) * 4 + 0]
            # vänd ordningen så caps face:ar nedåt
            triangles.append(Triangle(bottom_center, v_bot_b, v_bot_a, color))
        return Mesh(vertices, triangles)

    @staticmethod
    def create_tetrahedron_mesh(center=Vec3(0, 0, 0), size=1.0, color=0xFF00FFFF):
        hs = size / 2.0
        sqrt2over3 = math.sqrt(2) / 3 * size
        height = math.sqrt(6) / 3 * size

        # Hörn
        v0 = Vertex(Vec3(center.x, center.y + 2 * sqrt2over3, center.z - height / 3))
        v1 = Vertex(Vec3(center.x - hs, center.y - sqrt2over3, center.z - height / 3))
        v2 = Vertex(Vec3(center.x + hs, center.y - sqrt2over3, center.z - height / 3))
        v3 = Vertex(Vec3(center.x, center.y, center.z + 2 * height / 3))

        triangles = [
            Triangle(v0, v1, v2, color),
            Triangle(v0, v1, v3, color),
            Triangle(v1, v2, v3, color),
            Triangle(v2, v0, v3, color),
        ]

        return Mesh([v0, v1, v2, v3], triangles)

    @staticmethod
    def create_plane_mesh(center=Vec3(0, 0, 0), width=1.0, depth=1.0, color=0x00FF00FF):
        hw = width / 2.0
        hd = depth / 2.0

        v0 = Vertex(Vec3(center.x - hw, center.y, center.z - hd))
        v1 = Vertex(Vec3(center.x + hw, center.y, center.z - hd))
        v2 = Vertex(Vec3(center.x - hw, center.y, center.z + hd))
        v3 = Vertex(Vec3(center.x + hw, center.y, center.z + hd))

        triangles = [
            Triangle(v0, v1, v2, color),
            Triangle(v2, v1, v3, color)
        ]

        return Mesh([v0, v1, v2, v3], triangles)

    @staticmethod
    def create_double_pyramid_mesh(center=Vec3(0, 0, 0), height=1.0, size=1.0, color=0xFFFFFF00):
        hs = size / 2.0

        v0 = Vertex(Vec3(center.x - hs, center.y, center.z - hs))
        v1 = Vertex(Vec3(center.x + hs, center.y, center.z - hs))
        v2 = Vertex(Vec3(center.x + hs, center.y, center.z + hs))
        v3 = Vertex(Vec3(center.x - hs, center.y, center.z + hs))

        top = Vertex(Vec3(center.x, center.y + height, center.z))
        bottom = Vertex(Vec3(center.x, center.y - height, center.z))

        vertices = [v0, v1, v2, v3, top, bottom]

        triangles = [
            Triangle(v0, v1, top, color),
            Triangle(v1, v2, top, color),
            Triangle(v2, v3, top, color),
            Triangle(v3, v0, top, color),

            Triangle(v1, v0, bottom, color),
            Triangle(v2, v1, bottom, color),
            Triangle(v3, v2, bottom, color),
            Triangle(v0, v3, bottom, color),
        ]

        return Mesh(vertices, triangles)

    @staticmethod
    def create_horizontal_double_pyramid_mesh(center=Vec3(0, 0, 0), height=1.0, size=1.0, color=0xFFFFFF00):
        hs = size / 2.0

        # Fyrkantens hörn i XY-planet
        v0 = Vertex(Vec3(center.x - hs, center.y - hs, center.z))
        v1 = Vertex(Vec3(center.x + hs, center.y - hs, center.z))
        v2 = Vertex(Vec3(center.x + hs, center.y + hs, center.z))
        v3 = Vertex(Vec3(center.x - hs, center.y + hs, center.z))

        # Pyramid-topparna i +Z (front) och -Z (bak)
        front = Vertex(Vec3(center.x, center.y, center.z + height))
        back = Vertex(Vec3(center.x, center.y, center.z - height))

        vertices = [v0, v1, v2, v3, front, back]

        triangles = [
            # Främre pyramid
            Triangle(v0, v1, front, color),
            Triangle(v1, v2, front, color),
            Triangle(v2, v3, front, color),
            Triangle(v3, v0, front, color),

            # Bakre pyramid
            Triangle(v1, v0, back, color),
            Triangle(v2, v1, back, color),
            Triangle(v3, v2, back, color),
            Triangle(v0, v3, back, color),
        ]

        return Mesh(vertices, triangles)

    @staticmethod
    def create_static_torus_mesh(center=Vec3(0, 0, 0), major_radius=1.5, minor_radius=0.4, color=0xFFFFAA00):
        major_segments = 8
        minor_segments = 6

        vertices = []
        triangles = []

        for i in range(major_segments):
            theta = (i / major_segments) * 2 * math.pi
            next_theta = ((i + 1) % major_segments) / major_segments * 2 * math.pi

            for j in range(minor_segments):
                phi = (j / minor_segments) * 2 * math.pi
                next_phi = ((j + 1) % minor_segments) / minor_segments * 2 * math.pi

                def point(t, p):
                    cx = math.cos(t)
                    cy = math.sin(t)

                    r = major_radius
                    x = (r + minor_radius * math.cos(p)) * cx
                    y = (r + minor_radius * math.cos(p)) * cy
                    z = minor_radius * math.sin(p)
                    return Vertex(Vec3(center.x + x, center.y + y, center.z + z))

                v0 = point(theta, phi)
                v1 = point(next_theta, phi)
                v2 = point(next_theta, next_phi)
                v3 = point(theta, next_phi)

                idx_base = len(vertices)
                vertices.extend([v0, v1, v2, v3])

                triangles.append(Triangle(vertices[idx_base], vertices[idx_base + 1], vertices[idx_base + 2], color))
                triangles.append(Triangle(vertices[idx_base], vertices[idx_base + 2], vertices[idx_base + 3], color))

        return Mesh(vertices, triangles)

    @staticmethod
    def create_tetrahedron_mesh_length_think(center=Vec3(0, 0, 0), length=1.0, thickness=1.0, color=0xFF00FFFF):
        hs = length / 2.0
        sqrt2over3 = math.sqrt(2) / 3 * thickness
        height = math.sqrt(6) / 3 * thickness

        # Hörn
        v0 = Vertex(Vec3(center.x, center.y + 2 * sqrt2over3, center.z - height / 3))
        v1 = Vertex(Vec3(center.x - hs, center.y - sqrt2over3, center.z - height / 3))
        v2 = Vertex(Vec3(center.x + hs, center.y - sqrt2over3, center.z - height / 3))
        v3 = Vertex(Vec3(center.x, center.y, center.z + 2 * height / 3))

        triangles = [
            Triangle(v0, v1, v2, color),
            Triangle(v0, v1, v3, color),
            Triangle(v1, v2, v3, color),
            Triangle(v2, v0, v3, color),
        ]

        return Mesh([v0, v1, v2, v3], triangles)