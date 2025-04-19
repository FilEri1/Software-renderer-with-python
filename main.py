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
from building import *
from target import *

class App:
    def __init__(self, window_width, window_height):
        self.game_running = False
        self.home_running = True

        self.has_unlocked_map = False

        self.window = Window(window_width, window_height)
        self.running = True
        self.renderer = Renderer(self.window)
        self.last_time = sdl2.SDL_GetTicks64()
        self.target_delta = 1000 // 60

        self.progression_speed = 0
        self.max_progression_speed = 0.03

        self.rings = []
        self.spawn_timer = 0
        self.last_spawn_time = sdl2.SDL_GetTicks()
        self.spawn_interval = 5000

        self.spawn_timer_buildings = 0
        self.spawn_interval_buildings = 3000
        self.max_buildings = 5

        self.spawn_timer_targets = 0
        self.spawn_interval_targets = 15000
        self.max_targets = 2

        self.projectiles = []
        self.targets = []

        # Kamera:
        self.camera = Camera(Vec3(0, 15, 105), Vec3(0, 0,0 ))
        self.player = Player(0.0070, Vec3(0, 15, 100))

        self.building = Building(self.max_buildings)

        # Renderer:
        self.renderer.render_start()

    def home_screen(self):
        while self.home_running:
            # Input:
            self.home_running = process_input_home_screen(self.window, self.renderer)
            home_screen_keys = get_home_screen_keys()
            if home_screen_keys[0] == True:
                self.home_running = False
                self.game_running = True
            # Backgrunden:
            self.renderer.render_home_screen(self.has_unlocked_map)

    def run(self):
        while self.running:
            # Input: -------------------------------------------
            # Delta tid används för att begränsa spel loopens frekvens
            current_time = sdl2.SDL_GetTicks64()
            delta_time = current_time - self.last_time

            self.running = process_input(self.window, self.renderer)
            player_keys = get_player_keys()
            #---------------------------------------------------

            # Render: ------------------------------------------
            self.renderer.render(self.camera.position,
                                 self.camera.rotation,
                                 self.player,
                                 self.rings,
                                 self.building.existing_buildings,
                                 self.targets
                                 )
            # --------------------------------------------------

            # Update: ------------------------------------------
            if delta_time >= self.target_delta:
                self.last_time = current_time

                self.spawn_timer += delta_time
                self.spawn_timer_buildings += delta_time
                self.spawn_timer_targets += delta_time

                # Spelaren:

                # Om vi vill testa kameran använd den här raden och kommentera ut player update raden samt camera follow
                #self.camera.update_camera(player_keys, delta_time)

                self.player.player_update(player_keys, delta_time)
                self.camera.follow_player(self.player.position, self.player.rotation, delta_time)

                self.projectiles = self.player.get_projectiles()

                # Fienderna:
                for tgt in self.targets[:]:
                    tgt.update_target(delta_time)

                    hit_idxs = tgt.check_hit(self.projectiles)
                    if hit_idxs:
                        for idx in sorted(hit_idxs, reverse=True):
                            killed = tgt.take_damage(10)
                            self.player.remove_projectile_at_index(idx)
                        if killed:
                            self.targets.remove(tgt)
                            self.player.score += 5
                            continue

                    if tgt.position.z > self.player.position.z + 50:
                        self.targets.remove(tgt)
                        continue

                    if tgt.fleeing and tgt.position.y > 200:
                        self.targets.remove(tgt)
                        self.player.player_health -= 25
                        continue

                if self.spawn_timer_targets >= self.spawn_interval_targets and len(self.targets) < self.max_targets:
                    self.spawn_timer_targets = 0
                    x = random.uniform(-20, 20)
                    y = self.player.position.y + 3
                    z = self.player.position.z - 5

                    new_target = Target(position=Vec3(x, y, z), health=30, flee_z=-100)
                    self.targets.append(new_target)


                # Ringarna:
                for ring in self.rings:

                    ring.position.z += ring.speed * delta_time

                self.to_destroy = [r for r in self.rings if r.position.z >= 100]
                self.rings = [r for r in self.rings if r.position.z < 100]

                for r in self.to_destroy:
                    r.score_ring(self.player, r)

                if current_time - self.last_spawn_time >= self.spawn_interval \
                        and len(self.rings) < 5:
                    self.last_spawn_time = current_time
                    new_ring = Ring(self.player, self.rings, self.building.existing_buildings)
                    new_ring.speed = self.progression_speed
                    self.rings.append(new_ring)

                # Byggnaderna:
                if self.spawn_timer_buildings >= self.spawn_interval_buildings:
                    self.building.update_buildings(self.player, self.rings)
                    self.spawn_timer_buildings = 0

                self.building.move_buildings(delta_time, 0.03, 94.9)

                if self.building.player_crashed(self.player, 1):
                    self.player.player_health = 0

            # --------------------------------------------------

            if self.progression_speed < self.max_progression_speed:
                game_time_seconds = sdl2.SDL_GetTicks() // 1000
                self.progression_speed = min(0.01 + game_time_seconds * 0.00005, self.max_progression_speed)

            if delta_time < self.target_delta:
                sdl2.SDL_Delay(self.target_delta - delta_time)

    def __del__(self):
        sdl2.SDL_Quit()
        sdl2.SDL_DestroyWindow(self.window.sdl_window)

if __name__ == "__main__":
    app = App(800, 600)
    # Home screen:
    app.home_screen()
    # Game Loop:
    if app.game_running:
        app.run()