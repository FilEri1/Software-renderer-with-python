import math

class Mat4:
    def __init__(self, rows=None):
        if rows:
            self.m = rows
        else:
            # Om vi inte anger en specifik matris så skapar vi en 4X4 matris med alla element = 0
            self.m = [[0.0] * 4 for i in range (4)]

    # Låter oss kalla klassens method utan ett objekt denna funktion är also inte bunden till ett objekt
    # Skapar en EYE matris eller en standard matris där alla diagonala värden från top vänster till botten höger
    # är 1
    @staticmethod
    def identity():
        m = Mat4()
        for i in range (4):
            m.m[i][i] = 1.0
        return m

    def __mul__(self, other):
        if isinstance(other, Mat4):
            result = Mat4()
            for i in range (4):
                for j in range (4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range (4))
            return result
        elif isinstance(other, list) and len(other) == 4:
            return [sum(self.m[i][j] * other[j] for j in range (4)) for i in range (4)]
        else:
            raise RuntimeError("ERROR::Matrix")

    def __str__(self):
        return "\n".join(["[" + " ".join(f"{val: .2f}" for val in row) + "]" for row in self.m])

    # Denna funktionen är den absolut viktigaste för spelet då den används för att flytta varje "objekt" i spelet.
    @staticmethod
    def translation(tx, ty, tz):
        m = Mat4.identity()
        m.m[0][3] = tx
        m.m[1][3] = ty
        m.m[2][3] = tz
        return m

    # Följande tre matriser är rotations matriser och fungerar på samma sätt som våra rotations funktioner för vektorer
    # skillnaden är ju då att vi behöver rotations matriser nu när alla objekt använder sig utav model matriser istället
    # för vektorer för positioner.

    # Rotation x:
    @staticmethod
    def rotation_x(theta):
        m = Mat4.identity()
        c = math.cos(theta)
        s = math.sin(theta)
        m.m[1][1] = c
        m.m[1][2] = -s
        m.m[2][1] = s
        m.m[2][2] = c
        return m

    # Rotation y:
    @staticmethod
    def rotation_y(theta):
        m = Mat4.identity()
        c = math.cos(theta)
        s = math.sin(theta)
        m.m[0][0] = c
        m.m[0][2] = s
        m.m[2][0] = -s
        m.m[2][2] = c
        return m

    # Rotation z:
    @staticmethod
    def rotation_z(theta):
        m = Mat4.identity()
        c = math.cos(theta)
        s = math.sin(theta)
        m.m[0][0] = c
        m.m[0][1] = -s
        m.m[1][0] = s
        m.m[1][1] = c
        return m

    def transpose(self):
        result = Mat4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = self.m[j][i]
        return result