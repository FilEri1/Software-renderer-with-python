import math

# INFO:
# Följande fil innehåller alla vektor operationer projektet kräver för att fungera som det ska.
# Anledningen till att jag skrev upp det här själv var för att göra projekt mer komplett och fritt från bibliotek som
# t.ex: GLM!

class Vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def normalize(self):
        length = math.sqrt(self.x * self.x + self.y * self.y)
        if length == 0:
            return Vec2(0, 0)
        if length == 1:
            return self
        return Vec2(self.x / length, self.y / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    # Används för att skriva ut själva vektorn och inte dess minnes address!
    def __str__(self):
        return f"({self.x}, {self.y})"

class Vec3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def normalize(self):
        length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        if length == 0:
            return Vec3(0, 0, 0)
        if length == 1:
            return  self
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # Används för att beräkna om två vektorer pekar åt samma håll, behöves bara på 3D vektorer! Används för "normaler"
    # vilket är ljus
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    # Används för att skriva ut själva vektorn och inte dess minnes address!
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    # Rotation av 3D vektor https://en.wikipedia.org/wiki/Rotation_matrix -> Basic 3D rotation:
    # Det går att rotera 2D och 4D vektorer också men ser ingen mening med det!
    def rotate_x(self, angle: float):
        old_y = self.y
        old_z = self.z
        self.y = old_y * math.cos(angle) - old_z * math.sin(angle)
        self.z = old_y * math.sin(angle) + old_z * math.cos(angle)

    def rotate_z(self, angle: float):
        old_x = self.x
        old_y = self.y
        self.x = old_x * math.cos(angle) - old_y * math.sin(angle)
        self.y = old_x * math.sin(angle) + old_y * math.cos(angle)

    def rotate_y(self, angle: float):
        old_x = self.x
        old_z = self.z
        self.x = old_x * math.cos(angle) + old_z * math.sin(angle)
        self.z = -old_x * math.sin(angle) + old_z * math.cos(angle)

class Vec4:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __add__(self, other):
        return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, scalar):
        return Vec4(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    def normalize(self):
        length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)
        if length == 0:
            return Vec4(0, 0, 0, 0)
        if length == 1:
            return self
        return Vec4(self.x / length, self.y / length, self.z / length, self.w / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z}, {self.w})"

def dot(self, other):
    return self.x * other.x + self.y * other.y + self.z * other.z