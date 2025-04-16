import ctypes
import math

import sdl2
import numpy as np
from sdl2 import SDL_CreateRenderer, SDL_GetError

from window import Window
from vector import *
from graphics import *
from matrix import *
from camera import *

class Renderer:
    def __init__(self, window: Window):
        self.window = window
        self.sdl_renderer = SDL_CreateRenderer(
            self.window.sdl_window,
            -1, # -1 Betyder att SDL väljer vilken grafik enhet den ska använda själv
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        if not self.sdl_renderer:

            raise RuntimeError(f"ERROR::SDL::{sdl2.SDL_GetError()}")

        self.rotation = 0 # TEMP

        # NP använder höjd och bredd inte tvärt om av någon anledning, tydligen är def för att Matriser använder (y, x)?
        self.color_buffer = np.zeros((self.window.window_height, self.window.window_width), dtype=np.uint32) # Vi använder uint32 för att få hexadecimaler för ARGB
        self.buffer_texture = sdl2.SDL_CreateTexture( # Vi skapar en texture som vi sedan kan updatera varje "frame"
            self.sdl_renderer,
            sdl2.SDL_PIXELFORMAT_ARGB8888, # Pixel formatet vi vill använda Transparent, röd, grön och blå och att varje färg är 8 bit.
            sdl2.SDL_TEXTUREACCESS_STREAMING, # Skapar en texture som kan updateras ofta
            self.window.window_width,
            self.window.window_height
        )
        if not self.buffer_texture:
            raise RuntimeError(f"ERROR::SDL::{sdl2.SDL_GetError()}")

    def clear_color_buffer(self, color):
        self.color_buffer.fill(color)

    # Kopierar texturen och presenterar sedan den till skärmen så att vi ser det vi vill måla:
    def present(self):
        self.update_color_buffer()
        sdl2.SDL_RenderClear(self.sdl_renderer)
        sdl2.SDL_RenderCopy(self.sdl_renderer, self.buffer_texture, None, None)
        sdl2.SDL_RenderPresent(self.sdl_renderer)

    def update_color_buffer(self):
        pixels_ptr = ctypes.c_void_p()
        pitch = ctypes.c_int()

        if sdl2.SDL_LockTexture(self.buffer_texture, None, ctypes.byref(pixels_ptr), ctypes.byref(pitch)) != 0:
            raise RuntimeError(f"ERROR::SDL::{SDL_GetError()}")

        ctypes.memmove(pixels_ptr, self.color_buffer.ctypes.data, self.color_buffer.nbytes)

        sdl2.SDL_UnlockTexture(self.buffer_texture)

    # Tar 1 x och y värde istället för att använda np för att np använder sig av (y, x) och inte (x, y)
    # vilket bara leder till bekymmer!
    def set_pixel(self, x: int, y: int, color):
        if 0 <= x < self.window.window_width and 0 <= y < self.window.window_height:
            self.color_buffer[y, x] = color

    def draw_rectangle(self, x_pos: int, y_pos: int, width: int, height: int, color):
        for y in range (y_pos, height + y_pos, 1):
            for x in range (x_pos, width + x_pos, 1):
                self.set_pixel(x, y, color)

    # Skapar texturen på nytt om skärmens storlek ändras:
    def resize_buffer(self, new_width: int, new_height: int):
        self.color_buffer = np.zeros((new_height, new_width), dtype=np.uint32)
        self.buffer_texture = sdl2.SDL_CreateTexture(
            self.sdl_renderer,
            sdl2.SDL_PIXELFORMAT_ARGB8888,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            new_width,
            new_height
        )

    # Hyfsat snabb algorithm för att rita sträck: (https://gist.github.com/Sakshibadoni/5331e2983854b6073a58980fb20c5b08)
    def dda(self, x0: int, y0: int, x1: int, y1: int, color):
        # Beräkna skillnaden mellan slutet och början d = delta:
        dx = x1 - x0
        dy = y1 - y0

        # Bestämmer antalet steg som kräves för hela linjen
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            self.set_pixel(x0, y0, color)
            return

        x_increment = float(dx / steps)
        y_increment = float(dy / steps)

        for i in range (0, int(steps + 1)):
            self.set_pixel(int(x0), int(y0), color)
            x0 += x_increment
            y0 += y_increment

    # Betydligt mycket bättre algorithm för att rita linjer: (https://github.com/encukou/bresenham/blob/master/bresenham.py)
    # Bresenham är snabbare då den inte använder division för att beräkna ökningen
    def bresenham(self, x0, y0, x1, y1, color):
        window_width = self.window.window_width
        window_height = self.window.window_height

        # Hoppar över linjer utanför skärmen
        if (x0 < 0 and x1 < 0) or (x0 >= window_width and x1 >= window_width) or \
                (y0 < 0 and y1 < 0) or (y0 >= window_height and y1 >= window_height):
            return

        dx = x1 - x0
        dy = y1 - y0

        x_sign = 1 if dx > 0 else -1
        y_sign = 1 if dy > 0 else -1

        dx = abs(dx)
        dy = abs(dy)

        if dx > dy:
            xx, xy, yx, yy = x_sign, 0, 0, y_sign
        else:
            dx, dy = dy, dx
            xx, xy, yx, yy = 0, y_sign, x_sign, 0

        d = 2 * dy - dx
        y = 0

        for x in range(dx + 1):
            px, py =  x0 + x * xx + y * yx, y0 + x * xy + y * yy
            self.set_pixel(px, py, color)
            if d >= 0:
                y += 1
                d -= 2 * dx
            d += 2 * dy

    def wire_frame_triangle(self, triangle: Triangle, color):
        # Perspektivprojektera varje vertex
        p0 = perspective_divide(triangle.vertices[0].position)
        p1 = perspective_divide(triangle.vertices[1].position)
        p2 = perspective_divide(triangle.vertices[2].position)

        # Flytta till skärmkoordinater
        half_width = self.window.window_width // 2
        half_height = self.window.window_height // 2

        x0, y0 = int(p0.x + half_width), int(p0.y + half_height)
        x1, y1 = int(p1.x + half_width), int(p1.y + half_height)
        x2, y2 = int(p2.x + half_width), int(p2.y + half_height)

        # Rita kanterna
        self.bresenham(x0, y0, x1, y1, color)
        self.bresenham(x1, y1, x2, y2, color)
        self.bresenham(x2, y2, x0, y0, color)

    def fill_triangle(self, v0: Vec3, v1: Vec3, v2: Vec3, color):
        # Sorterar punkterna beroende på y värdet eller höjden för att avgöra vilken typ av triangel vi arbetar med
        vertices = sorted([v0, v1, v2], key=lambda v: v.y)
        v0, v1, v2 = vertices

        if abs(v0.y - v2.y) < 0.0001:
            return

        if abs(v0.y - v1.y) < 0.0001:
            self.bresenham(int(v0.x), int(v0.y), int(v1.x), int(v1.y), color)

            dy = v2.y - v0.y
            if dy == 0: return
            dx_left = (v2.x - v0.x) / dy
            dx_right = (v2.x - v1.x) / dy
            x_left, x_right = v0.x, v1.x

            for y in range(int(v0.y), int(v2.y) + 1):
                self.bresenham(round(x_left), y, round(x_right), y, color)
                x_left += dx_left
                x_right += dx_right

        elif abs(v1.y - v2.y) < 0.0001:
            self.bresenham(int(v1.x), int(v1.y), int(v2.x), int(v2.y), color)

            dy = v1.y - v0.y
            if dy == 0: return
            dx_left = (v1.x - v0.x) / dy
            dx_right = (v2.x - v0.x) / dy
            x_left, x_right = v0.x, v0.x

            for y in range(int(v0.y), int(v1.y) + 1):
                self.bresenham(round(x_left), y, round(x_right), y, color)
                x_left += dx_left
                x_right += dx_right

        else:
            denominator = v2.y - v0.y
            if abs(denominator) < 1e-6:
                return
            t = (v1.y - v0.y) / denominator
            split_x = v0.x + t * (v2.x - v0.x)
            split_point = Vec3(split_x, v1.y, 0)

            self.fill_triangle(v0, v1, split_point, color)
            self.fill_triangle(v1, split_point, v2, color)

    # Själva render loopen:
    def render(self, camera_pos: Vec3, camera_rotation: Vec3):
        # Rensar varje pixel:
        self.clear_color_buffer(0xFF000000)
        # Kameran:
        # Skapa view-matrisen (kameran)
        forward = Camera.get_forward_vector(camera_rotation)
        target = camera_pos + forward
        view_matrix = Mat4.look_at(camera_pos, target, Vec3(0, 1, 0))
        # Ljusinställningar:
        min_brightness = 0.5

        self.rotation += 0.005 # Test

        # Render kod:
        # Ladda upp varje objekt som ska renderas:
        cube1 = Mesh.create_cube_mesh(center=Vec3(0, 0, 0.5), size=1, color=0xFFFF0000)
        cube2 = Mesh.create_cube_mesh(center=Vec3(0, 0, 0.5), size=1, color=0xFF0F0FF0)

        # Skapa en model matris för varje objekt:
        model_matrix1 = (
                Mat4.translation(0, 0, -2)
        )
        model_matrix2 = (
                Mat4.translation(0, 0, 6)
        )

        # Skapa ett View * Model matrix:
        model_view_matrix1 = view_matrix * model_matrix1
        model_view_matrix2 = view_matrix * model_matrix2

        print(f"{camera_pos}")

        # Ge varje objekt en ny position utifrån model view:
        transformed_mesh1 = cube1.transform(model_view_matrix1)
        transformed_mesh2 = cube2.transform(model_view_matrix2)

        # Lista över alla objekt som ska målas:
        scene_meshes = [transformed_mesh1, transformed_mesh2]

        # Koden här under sköter sig själv och behöver inte manuellt ändras på:

        # Ljus: -----------------------------------
        world_light_dir = Vec3(0, 1, 0).normalize()
        view_rotation = Mat4.identity()
        for i in range(3):
            for j in range(3):
                view_rotation.m[i][j] = view_matrix.m[i][j]

        view_rotation_inv = view_rotation.transpose()
        light_dir_vec = (view_rotation_inv * [world_light_dir.x, world_light_dir.y, world_light_dir.z, 0])[:3]
        light_dir = Vec3(*light_dir_vec).normalize()
        # ------------------------------------------

        # Den här for loopen går igenom alla objekt i våran scenen och beräknar deras ljus, gör backface culling och
        # ritar till slut ut dom.
        for mesh in scene_meshes:
            mesh.triangles.sort(key=lambda tri: -tri.avg_z())
            for tri in mesh.triangles:
                v0 = tri.vertices[0].position
                v1 = tri.vertices[1].position
                v2 = tri.vertices[2].position

                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = edge1.cross(edge2).normalize()
                #view_vector = (v0 - camera_pos).normalize()
                #if normal.dot(view_vector) < 0:
                #    continue

                intensity = max(normal.dot(light_dir), min_brightness)
                original_color = tri.color
                a = (original_color >> 24) & 0xFF
                r = (original_color >> 16) & 0xFF
                g = (original_color >> 8) & 0xFF
                b = original_color & 0xFF
                r_adj = int(r * intensity)
                g_adj = int(g * intensity)
                b_adj = int(b * intensity)
                adjusted_color = (a << 24) | (r_adj << 16) | (g_adj << 8) | b_adj
                proj_v0 = perspective_divide(v0)
                proj_v1 = perspective_divide(v1)
                proj_v2 = perspective_divide(v2)
                half_width = self.window.window_width // 2
                half_height = self.window.window_height // 2
                screen_v0 = Vec2(proj_v0.x + half_width, proj_v0.y + half_height)
                screen_v1 = Vec2(proj_v1.x + half_width, proj_v1.y + half_height)
                screen_v2 = Vec2(proj_v2.x + half_width, proj_v2.y + half_height)
                min_x = min(screen_v0.x, screen_v1.x, screen_v2.x)
                max_x = max(screen_v0.x, screen_v1.x, screen_v2.x)
                min_y = min(screen_v0.y, screen_v1.y, screen_v2.y)
                max_y = max(screen_v0.y, screen_v1.y, screen_v2.y)

                if max_x < 0 or min_x >= self.window.window_width or max_y < 0 or min_y >= self.window.window_height:
                    continue

                # Rita triangeln
                self.fill_triangle(screen_v0, screen_v1, screen_v2, adjusted_color)

        # Visar resultatet av alla operationer, ändra inte!:
        self.present()

    # Tar bort allt som tillhör rendern när vi är klara
    def __del__(self):
        sdl2.SDL_DestroyRenderer(self.sdl_renderer)
        sdl2.SDL_DestroyTexture(self.buffer_texture)