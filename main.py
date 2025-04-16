import sdl2
import ctypes

# Moduler:

# Egna filer:
from input import *
from render import  *
from window import *

from camera import *

class App:
    def __init__(self, window_width, window_height):
        self.window = Window(window_width, window_height)
        self.running = True
        self.renderer = Renderer(self.window)
        self.last_time = sdl2.SDL_GetTicks()
        self.target_delta = 1000 // 60

        # Kamera:
        self.camera = Camera(Vec3(0, 0, 10), Vec3(0, 0,0 ))

    def run(self):
        while self.running:
            # Input: -------------------------------------------
            # Delta tid används för att begränsa spel loopens frekvens
            current_time = sdl2.SDL_GetTicks()
            delta_time = current_time - self.last_time

            self.running = process_input(self.window, self.renderer)
            player_keys = get_player_keys()
            #---------------------------------------------------

            # Render: ------------------------------------------
            self.renderer.render(self.camera.position, self.camera.rotation)
            # --------------------------------------------------

            # Update: ------------------------------------------
            if delta_time >= self.target_delta:
                self.last_time = current_time

                self.camera.update_camera(player_keys, delta_time)

            # --------------------------------------------------

            if delta_time < self.target_delta:
                sdl2.SDL_Delay(self.target_delta - delta_time)

    def __del__(self):
        sdl2.SDL_Quit()
        sdl2.SDL_DestroyWindow(self.window.sdl_window)

if __name__ == "__main__":
    app = App(1000, 800)
    # Game Loop:
    app.run()