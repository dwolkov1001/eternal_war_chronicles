import pygame
import sys
import os

# Adjust the path to include the project's root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .world import World
from ..game_objects.army import Army
from ..game_objects.unit import Unit
from ..game_objects.faction import Faction
from .combat import Combat
from .log import log
from ..ai.general_ai import GeneralAI
from .camera import Camera
from .renderer import Renderer, TILE_SIZE
from .map_generator import generate_map, TILE_TYPES

class Game:
    """
    The main game class, managing the game loop, state, and rendering.
    """
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Eternal War Chronicles")

        self.running = True
        self.clock = pygame.time.Clock()
        self.paused = False

        self.world = World(100, 100) # World size in tiles
        self.world.map_data = generate_map(self.world.width, self.world.height, TILE_TYPES)
        self.renderer = Renderer(self.screen)
        self.renderer.pre_render_map(self.world.map_data) # Pre-render the map once
        self.camera = Camera(self.renderer.game_surface.get_width(), self.renderer.game_surface.get_height())

        self.active_combats = []
        self.ai_generals = []

        self.combat_tick_rate = 1.0  # seconds
        self.time_since_last_combat_tick = 0.0

        self._setup_world()

    def _setup_world(self):
        """Creates initial factions and armies in the world."""
        log.info("Setting up the world...")

        # Unit templates
        spearman_template = {"name": "Spearman", "max_hp": 100, "attack": 10, "defense": 5}
        archer_template = {"name": "Archer", "max_hp": 70, "attack": 12, "defense": 2}
        knight_template = {"name": "Knight", "max_hp": 150, "attack": 15, "defense": 10}

        # Factions
        faction1 = Faction("Order of the Sun", "Blue")
        faction2 = Faction("Shadow Syndicate", "Red")
        self.world.add_faction(faction1)
        self.world.add_faction(faction2)

        # Create armies with different unit compositions
        army1_units = [Unit(**spearman_template) for _ in range(10)] + [Unit(**archer_template) for _ in range(5)]
        army1 = Army(faction1, 10, 10, army1_units)
        self.world.add_army(army1)
        self.ai_generals.append(GeneralAI("aggressive_general", army1))

        army2_units = [Unit(**spearman_template) for _ in range(8)] + [Unit(**knight_template) for _ in range(4)]
        army2 = Army(faction2, self.world.width - 10, self.world.height - 10, army2_units)
        self.world.add_army(army2)
        self.ai_generals.append(GeneralAI("aggressive_general", army2))
        
        log.info("World setup complete.")


    def run(self):
        """Starts the main game loop."""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            if self.paused:
                delta_time = 0

            self._handle_input()
            self._update_ai(delta_time)
            self._update_armies(delta_time)
            self._handle_collisions()
            self._update_combats(delta_time)
            self._render()

        pygame.quit()
        sys.exit()

    def _handle_input(self):
        """Handles user input and system events."""
        map_width_pixels = self.world.width * TILE_SIZE
        map_height_pixels = self.world.height * TILE_SIZE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.VIDEORESIZE:
                self.renderer.calculate_game_surface()
                self.camera.width = self.renderer.game_surface.get_width()
                self.camera.height = self.renderer.game_surface.get_height()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    log.info(f"Game {'paused' if self.paused else 'resumed'}.")
                if event.key in [pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS]:
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                elif event.button == 5: # Scroll down
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)

        # Handle camera movement with keys
        keys = pygame.key.get_pressed()
        move_dx, move_dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dx -= self.camera.move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dx += self.camera.move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_dy -= self.camera.move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_dy += self.camera.move_speed
        
        if move_dx != 0 or move_dy != 0:
            self.camera.move(move_dx, move_dy, map_width_pixels, map_height_pixels)

    def _update_ai(self, delta_time):
        """Updates all AI generals."""
        for general in self.ai_generals:
            general.update(self.world)

    def _update_armies(self, delta_time):
        """Updates all armies in the world."""
        # Create a copy of the list to iterate over, as it might be modified during combat resolution
        for army in list(self.world.armies):
            army.update(delta_time, self.world)

    def _handle_collisions(self):
        """Detects collisions between armies and initiates combat."""
        armies_to_check = list(self.world.armies)
        for i, army1 in enumerate(armies_to_check):
            for army2 in armies_to_check[i+1:]:
                if army1.faction != army2.faction:
                    # Check if they are already fighting each other
                    is_in_combat = False
                    for combat in self.active_combats:
                        if (combat.army1 == army1 and combat.army2 == army2) or \
                           (combat.army1 == army2 and combat.army2 == army1):
                            is_in_combat = True
                            break
                    
                    if not is_in_combat and army1.get_distance_to(army2) < army1.collision_radius + army2.collision_radius:
                        log.info(f"Collision detected! Armies of {army1.faction.name} and {army2.faction.name} are now in combat.")
                        army1.in_combat = True
                        army2.in_combat = True
                        army1.set_target(None) # Stop movement
                        army2.set_target(None)
                        new_combat = Combat(army1, army2)
                        self.active_combats.append(new_combat)

    def _update_combats(self, delta_time):
        """Updates the state of all active combats."""
        self.time_since_last_combat_tick += delta_time
        if self.time_since_last_combat_tick < self.combat_tick_rate:
            return  # Not time for the next combat tick yet

        self.time_since_last_combat_tick -= self.combat_tick_rate

        for combat in list(self.active_combats):
            status, winner, loser = combat.tick()

            if status == 'finished':
                log.info(f"Combat finished. Winner: {winner.faction.name if winner else 'Draw'}. Loser: {loser.faction.name if loser else 'Draw'}.")
                
                # In a draw, both are losers.
                if winner is None and loser is None:
                    if combat.army1 in self.world.armies:
                        self.world.remove_army(combat.army1)
                    if combat.army2 in self.world.armies:
                        self.world.remove_army(combat.army2)
                else:
                    # Remove loser from the world
                    if loser:
                        self.world.remove_army(loser)
                    
                    # Mark surviving winner as not in combat
                    if winner and winner in self.world.armies:
                        winner.in_combat = False

                self.active_combats.remove(combat)


    def _render(self):
        """Renders all game objects to the screen."""
        self.renderer.render(self.world, self.camera)
        pygame.display.flip() 

if __name__ == '__main__':
    game = Game()
    game.run() 