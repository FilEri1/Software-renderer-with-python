import sdl2
from sdl2 import SDL_WINDOWPOS_CENTERED

class Window:
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        # Start SDL's video modul:
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO):
            raise RuntimeError(f"ERROR::SDL::{sdl2.SDL_GetError().decode()}")

        # Skapar fönstret kollar dessutom om det inte kunde skapas:
        flags = (
            sdl2.SDL_WINDOW_RESIZABLE
        )
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"Game",
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            window_width,
            window_height,
            flags
        )
        if not self.sdl_window:
            raise RuntimeError(f"ERROR::SDL::{sdl2.SDL_GetError().decode()}")