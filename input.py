import sdl2
import ctypes

from window import Window
from render import Renderer

home_screen_keys = [False, False, False] # Håller alternativen i hemma skärmen
player_input_keys = [False, False, False, False, False, False] # Håller WASD för spelaren

event = sdl2.SDL_Event()

def process_input_home_screen(window: Window, renderer: Renderer) -> bool:
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
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE: # Stänger spelet om vi tryker på ESCAPE
                return False
            # WASD:
            if event.key.keysym.sym == sdl2.SDLK_1:
                home_screen_keys[0] = True


    return True

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
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE: # Stänger spelet om vi tryker på ESCAPE
                return False
            # WASD:
            if event.key.keysym.sym == sdl2.SDLK_w:
                player_input_keys[0] = True
            elif event.key.keysym.sym == sdl2.SDLK_a:
                player_input_keys[1] = True
            elif event.key.keysym.sym == sdl2.SDLK_s:
                player_input_keys[2] = True
            elif event.key.keysym.sym == sdl2.SDLK_d:
                player_input_keys[3] = True
            elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                player_input_keys[4] = True
            elif event.key.keysym.sym == sdl2.SDLK_z:
                player_input_keys[5] = True

        if event.type == sdl2.SDL_KEYUP:
            # WASD vi sätter keys = False när vi släpper en knapp!
            if event.key.keysym.sym == sdl2.SDLK_w:
                player_input_keys[0] = False
            elif event.key.keysym.sym == sdl2.SDLK_a:
                player_input_keys[1] = False
            elif event.key.keysym.sym == sdl2.SDLK_s:
                player_input_keys[2] = False
            elif event.key.keysym.sym == sdl2.SDLK_d:
                player_input_keys[3] = False
            elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                player_input_keys[4] = False
            elif event.key.keysym.sym == sdl2.SDLK_z:
                player_input_keys[5] = False

    return True

def get_player_keys():
    return player_input_keys

def get_home_screen_keys():
    return home_screen_keys