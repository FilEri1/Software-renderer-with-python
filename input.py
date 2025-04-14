import sdl2
import ctypes

from window import Window
from render import Renderer

event = sdl2.SDL_Event()

def process_input(window: Window, renderer: Renderer) -> bool:
    while sdl2.SDL_PollEvent(ctypes.byref(event)):
        if event.type == sdl2.SDL_QUIT:
            return  False
        if event.type == sdl2.SDL_WINDOWEVENT:
            if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                width = ctypes.c_int()
                height = ctypes.c_int()
                sdl2.SDL_GetWindowSize(window.sdl_window, width, height)
                print(f"Fönstrets nya mått: x: {width} y: {height}")
                window.window_width = width.value
                window.window_height = height.value
                renderer.resize_buffer(window.window_width, window.window_height)

        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                return False

    return True