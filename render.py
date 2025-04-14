import ctypes

import sdl2
import numpy as np
from sdl2 import SDL_CreateRenderer, SDL_GetError
from sdl2.examples.draw import draw_rects

import graphics
from window import Window
from vector import *
from graphics import *

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
        steps = abs(dx) if abs(dx) > abs(dy) else abs(dy)

        x_increment = float(dx / steps)
        y_increment = float(dy / steps)

        for i in range (0, int(steps + 1)):
            self.set_pixel(int(x0), int(y0), color)
            x0 += x_increment
            y0 += y_increment

    # Betydligt mycket bättre algorithm för att rita linjer: (https://github.com/encukou/bresenham/blob/master/bresenham.py)
    # Bresenham är snabbare då den inte använder division för att beräkna ökningen
    def bresenham(self, x0, y0, x1, y1, color):
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

    # Själva render loopen:
    def render(self):
        # Exempel på enkelt perspektiv:
        #   self.clear_color_buffer(0xFF000000)
        #
        #   y_values = np.linspace(-1, 1, num=9)
        #   x_values = np.linspace(-1, 1, num=9)
        #   z_values = np.linspace(-1, 1, num=9)
        #
        #   for y in y_values:
        #       for x in x_values:
        #           for z in z_values:
        #               world_x = x
        #               world_y = y
        #               world_z = z - 3 # - 3 = Camera!
        #
        #               point = Vec3(float(world_x), float(world_y), float(world_z))
        #               projected_point = perspective_divide(point)
        #
        #               self.draw_rectangle(
        #                   int(projected_point.x + self.window.window_width//2),
        #                   int(projected_point.y + self.window.window_height//2),
        #                   4,
        #                   4,
        #                   0xFF00FFFF
        #               )



        self.present()

    def __del__(self):
        sdl2.SDL_DestroyRenderer(self.sdl_renderer)
        sdl2.SDL_DestroyTexture(self.buffer_texture)