from vector import *

fov = 200 # Temp!

def perspective_divide(vec: Vec3) -> Vec2:
    if vec.z == 0:
        return Vec2(0, 0)
    return Vec2(
        (vec.x * fov) / vec.z,
        (vec.y * fov) / vec.z
    )

class Vertex:
    def __init__(self, position: Vec3):
        self.position = position