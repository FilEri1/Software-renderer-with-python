import ctypes
import math
from numba import njit

import sdl2
import numpy as np
from sdl2 import SDL_CreateRenderer, SDL_GetError

from window import Window
from vector import *
from graphics import *
from matrix import *
from camera import *
from player import *


@njit
def draw_scanline_numba(buffer, x0, x1, y, color):
    if x0 > x1:
        x0, x1 = x1, x0
    for x in range(x0, x1 + 1):
        if 0 <= x < buffer.shape[1] and 0 <= y < buffer.shape[0]:
            buffer[y, x] = color

@njit
def fill_triangle_numba(buffer, width, height, x0, y0, x1, y1, x2, y2, color):
    # Sortera så att y0 <= y1 <= y2
    if y0 > y1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    if y0 > y2:
        x0, y0, x2, y2 = x2, y2, x0, y0
    if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1

    def edge_interpolate(y_start, y_end, x_start, x_end):
        if y_end == y_start:
            return np.empty(0, dtype=np.float32)
        num_steps = int(y_end) - int(y_start)
        slope = (x_end - x_start) / (y_end - y_start)
        return np.array([x_start + slope * (y - y_start) for y in range(int(y_start), int(y_end))], dtype=np.float32)

    x01 = edge_interpolate(y0, y1, x0, x1)
    x12 = edge_interpolate(y1, y2, x1, x2)
    x02 = edge_interpolate(y0, y2, x0, x2)

    x012 = np.concatenate((x01, x12)).astype(np.float32)

    y_start = int(y0)
    y_end = int(y2)

    if len(x02) != (y_end - y_start):
        return

    for i in range(y_end - y_start):
        y = y_start + i
        if y < 0 or y >= height:
            continue

        xa = x02[i]
        xb = x012[i] if i < len(x012) else x012[-1]

        x_start = int(min(xa, xb))
        x_end = int(max(xa, xb))

        for x in range(x_start, x_end + 1):
            if 0 <= x < width:
                buffer[y, x] = color

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

        # Spelaren:
        self.player_mesh = None

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

    def fill_triangle(self, v0: Vec2, v1: Vec2, v2: Vec2, color):
        # Sortera efter y så att v0.y mindre än v1.y och mindre än v2.y
        vertices = sorted([v0, v1, v2], key=lambda v: v.y)
        v0, v1, v2 = vertices

        def edge_interpolate(y_start, y_end, x_start, x_end):
            if y_end - y_start == 0:
                return []
            slope = (x_end - x_start) / (y_end - y_start)
            return [x_start + slope * (y - y_start) for y in range(int(y_start), int(y_end))]

        x01 = edge_interpolate(v0.y, v1.y, v0.x, v1.x)
        x12 = edge_interpolate(v1.y, v2.y, v1.x, v2.x)
        x02 = edge_interpolate(v0.y, v2.y, v0.x, v2.x)

        x012 = x01 + x12

        y_start = int(v0.y)
        y_end = int(v2.y)
        if y_end - y_start == 0:
            return

        midpoint = int(v1.y)
        if len(x02) != (y_end - y_start):
            return

        for i in range(y_end - y_start):
            y = y_start + i
            if y < 0 or y >= self.window.window_height:
                continue

            xa = x02[i]
            xb = x012[i] if i < len(x012) else x012[-1]  # undvik index error

            draw_scanline_numba(self.color_buffer, int(xa), int(xb), y, color)

    def clear_color_buffer_gradient(self, top_color, bottom_color):
        h, w = self.color_buffer.shape
        for y in range(h):
            t = y / (h - 1)
            a = int((1 - t) * ((top_color >> 24) & 0xFF) + t * ((bottom_color >> 24) & 0xFF))
            r = int((1 - t) * ((top_color >> 16) & 0xFF) + t * ((bottom_color >> 16) & 0xFF))
            g = int((1 - t) * ((top_color >> 8) & 0xFF) + t * ((bottom_color >> 8) & 0xFF))
            b = int((1 - t) * (top_color & 0xFF) + t * (bottom_color & 0xFF))
            color = (a << 24) | (r << 16) | (g << 8) | b
            self.color_buffer[y, :] = color

    def render_start(self):
        # Spelaren:
        # self.player_mesh = Mesh.create_cube_mesh(center=Vec3(0, 0, 0.5), size=1, color=0xFFFF0FFF)
        # Gräset:
        self.grass_mesh = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF305F33)
        self.grass_mesh2 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF36753B)
        self.grass_mesh3 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF3C7B40)
        self.grass_mesh4 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF438245)
        self.grass_mesh5 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF3F7A39)
        self.grass_mesh6 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF376F32)
        self.grass_mesh7 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF30632A)
        self.grass_mesh8 = Mesh.create_plane_mesh(Vec3(0, 0, 0), 1000, 15, 0xFF30632A)
    # Själva render loopen:
    def render(self, camera_pos: Vec3, camera_rotation: Vec3, player, rings):
        # Rensar varje pixel:
        self.clear_color_buffer_gradient(0xFF3A83D4, 0xFF0B2D5A)
        # Kameran:
        # Skapa view-matrisen (kameran)
        forward = Camera.get_forward_vector(camera_rotation)
        target = camera_pos + forward
        view_matrix = Mat4.look_at(camera_pos, target, Vec3(0, 1, 0))
        # Ljusinställningar:
        min_brightness = 0.5

        # Render kod:
        # Ladda upp varje objekt som ska renderas:
        # Gräset:
        grass_x = player.position.x

        grass_model = Mat4.identity()
        grass_model = grass_model.translation(grass_x, 0, 0)
        grass_view_model = grass_model * view_matrix
        grass_transformed_mesh = self.grass_mesh.transform(grass_view_model)

        grass_model2 = Mat4.identity()
        grass_model2 = grass_model2.translation(grass_x, 0, 15)
        grass_view_model2 = grass_model2 * view_matrix
        grass_transformed_mesh2 = self.grass_mesh2.transform(grass_view_model2)

        grass_model3 = Mat4.identity()
        grass_model3 = grass_model3.translation(grass_x, 0, 30)
        grass_view_model3 = grass_model3 * view_matrix
        grass_transformed_mesh3 = self.grass_mesh3.transform(grass_view_model3)

        grass_model4 = Mat4.identity()
        grass_model4 = grass_model4.translation(grass_x, 0, 45)
        grass_view_model4 = grass_model4 * view_matrix
        grass_transformed_mesh4 = self.grass_mesh4.transform(grass_view_model4)

        grass_model5 = Mat4.identity()
        grass_model5 = grass_model5.translation(grass_x, 0, 60)
        grass_view_model5 = grass_model5 * view_matrix
        grass_transformed_mesh5 = self.grass_mesh5.transform(grass_view_model5)

        grass_model6 = Mat4.identity()
        grass_model6 = grass_model6.translation(grass_x, 0, 75)
        grass_view_model6 = grass_model6 * view_matrix
        grass_transformed_mesh6 = self.grass_mesh6.transform(grass_view_model6)

        grass_model7 = Mat4.identity()
        grass_model7 = grass_model7.translation(grass_x, 0, 90)
        grass_view_model7 = (grass_model7 * view_matrix)
        grass_transformed_mesh7 = self.grass_mesh7.transform(grass_view_model7)

        grass_model8 = Mat4.identity()
        grass_model8 = grass_model8.translation(grass_x, 0, -15)
        grass_view_model8 = (grass_model8 * view_matrix)
        grass_transformed_mesh8 = self.grass_mesh8.transform(grass_view_model8)

        scene_meshes = [
            grass_transformed_mesh,
            grass_transformed_mesh2,
            grass_transformed_mesh3,
            grass_transformed_mesh4,
            grass_transformed_mesh5,
            grass_transformed_mesh6,
            grass_transformed_mesh7,
            grass_transformed_mesh8,
        ]

        # Ringarna:
        if rings:
            first_ring = max(rings, key=lambda r: r.position.z)

            for ring in rings:
                if ring == first_ring:
                    ring_color = 0xFFFCF403
                else:
                    ring_color = 0xFFFF0000

                ring_mesh = Mesh.create_static_torus_mesh(Vec3(), major_radius=2.5, minor_radius=0.4, color=ring_color)

                model = Mat4.identity()
                model = model.translation(ring.position.x, ring.position.y, ring.position.z)
                ring_model_view = model * view_matrix
                ring_transformed_mesh = ring_mesh.transform(ring_model_view)
                scene_meshes.append(ring_transformed_mesh)

        # Spelaren:
        base_view_model = player.model * view_matrix

        for mesh, local_mat in player.parts:
            model_view = base_view_model * local_mat
            scene_meshes.append(mesh.transform(model_view))


        # Koden här under sköter sig själv och behöver inte manuellt ändras på:
        # Ljus: -----------------------------------
        world_light_dir = Vec3(0, -1, 0).normalize()
        view_rotation = Mat4.identity()
        for i in range(3):
            for j in range(3):
                view_rotation.m[i][j] = view_matrix.m[i][j]

        view_rotation_inv = view_rotation.transpose()
        light_dir_vec = (view_rotation_inv * [world_light_dir.x, world_light_dir.y, world_light_dir.z, 0])[:3]
        light_dir = Vec3(*light_dir_vec).normalize()
        # ------------------------------------------

        # Den här for loopen går igenom alla objekt i våran scenen och beräknar deras ljus, gör backface culling och
        # ritar till slut ut dom för varje mesh->triangel.
        for mesh in scene_meshes:
            mesh.triangles.sort(key=lambda tri: -tri.avg_z())
            for tri in mesh.triangles:
                v0 = tri.vertices[0].position
                v1 = tri.vertices[1].position
                v2 = tri.vertices[2].position

                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = edge1.cross(edge2).normalize()
                view_vector = (v0 - camera_pos).normalize()

                if normal.dot(view_vector) > 0:
                    continue

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
                #self.fill_triangle(screen_v0, screen_v1, screen_v2, adjusted_color)
                # Använd Numba istället, testa gamla methoden och se skillnaden!:
                fill_triangle_numba(
                    self.color_buffer,
                    self.window.window_width,
                    self.window.window_height,
                    screen_v0.x, screen_v0.y,
                    screen_v1.x, screen_v1.y,
                    screen_v2.x, screen_v2.y,
                    adjusted_color
                )

        # Visar resultatet av alla operationer, ändra inte!:
        self.present()

    # Tar bort allt som tillhör rendern när vi är klara
    def __del__(self):
        sdl2.SDL_DestroyRenderer(self.sdl_renderer)
        sdl2.SDL_DestroyTexture(self.buffer_texture)