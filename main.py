import sdl2
import ctypes
import random

# Egna filer:
from input import *
from render import  *
from window import *

from camera import *
from player import *
from ring import *
from background_buildings import *

class App:
    def __init__(self, window_width, window_height):
        self.window = Window(window_width, window_height)
        self.running = True
        self.renderer = Renderer(self.window)
        self.last_time = sdl2.SDL_GetTicks()
        self.target_delta = 1000 // 60
        self.rings = []
        self.spawn_timer = 0
        self.spawn_interval = 1000

        # Kamera:
        self.camera = Camera(Vec3(0, 15, 105), Vec3(0, 0,0 ))
        self.player = Player(0.0035, Vec3(0, 15, 100))

        self.buildings = Background_buildings(3)

        # Renderer:
        self.renderer.render_start()


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
            self.renderer.render(self.camera.position, self.camera.rotation, self.player, self.rings)
            # --------------------------------------------------

            # Update: ------------------------------------------
            if delta_time >= self.target_delta:
                self.last_time = current_time

                self.player.player_update(player_keys, delta_time)
                self.camera.follow_player(self.player.position, self.player.rotation, delta_time)

                # Om vi vill testa kameran använd den här raden och kommentera ut player update raden!
                #self.camera.update_camera(player_keys, delta_time)

                for ring in self.rings:
                    ring.position.z += 0.01 * delta_time

                self.to_destroy = [r for r in self.rings if r.position.z >= 100]
                self.rings = [r for r in self.rings if r.position.z < 100]

                for r in self.to_destroy:
                    r.score_ring(self.player, r)


                self.spawn_timer += delta_time

                if self.spawn_timer >= self.spawn_interval and len(self.rings) < 5:
                    new_ring = Ring(self.player, self.rings)
                    self.rings.append(new_ring)
                    self.spawn_timer = 0

                self.buildings.update_buildings(self.player, delta_time)

            # --------------------------------------------------

            if delta_time < self.target_delta:
                sdl2.SDL_Delay(self.target_delta - delta_time)

    def __del__(self):
        sdl2.SDL_Quit()
        sdl2.SDL_DestroyWindow(self.window.sdl_window)

if __name__ == "__main__":
    app = App(800, 600)
    # Game Loop:
    app.run()