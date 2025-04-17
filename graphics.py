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
