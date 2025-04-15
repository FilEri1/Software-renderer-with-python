from vector import *

fov = 400 # Temp!

def perspective_divide(vec: Vec3) -> Vec2:
    if vec.z == 0: # Vi vill inte dela med z = 0!
        return Vec2(float('inf'), float('int'))
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