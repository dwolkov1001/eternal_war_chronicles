import pygame
import sys
import os
import random

# Adjust the path to include the project's root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .world import GameWorld
from ..game_objects.army import Army
from ..game_objects.unit import Unit
from ..game_objects.faction import Faction
from .combat import Combat
from .log import log
from ..ai.general_ai import GeneralAI
from .camera import Camera
from .renderer import Renderer, TILE_SIZE
from .map_generator import generate_map
from ..misc.enums import Stance, CombatType

class Game:
    """
    The main game class, managing the game loop, state, and rendering.
    """
    def __init__(self, width=1280, height=720, map_seed=None):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Eternal War Chronicles")

        self.running = True
        self.clock = pygame.time.Clock()
        self.paused = False

        self.world = GameWorld(width=100, height=100)
        
        # Сначала создаём фракции
        faction1 = Faction("Order of the Sun", "Blue")
        faction2 = Faction("Shadow Syndicate", "Red")
        factions = [faction1, faction2]
        # Генерируем seed карты
        if map_seed is None:
            map_seed = random.randint(0, 1000000)
        self.map_seed = map_seed
        log.info(f"Map seed: {self.map_seed}")
        # Генерируем карту с учётом фракций и сида
        game_map, territories = generate_map(self.world.width, self.world.height, factions, seed=self.map_seed)
        self.world.map_data = game_map
        self.world.territories = territories
        
        # Инициализация рендерера
        self.renderer = Renderer(self.screen)
        self.renderer.pre_render_map(self.world.map_data) # Pre-render the map once
        self.camera = Camera(self.renderer.game_surface.get_width(), self.renderer.game_surface.get_height())

        self.active_combats = []
        self.ai_generals = []

        self.combat_tick_rate = 1.0  # seconds
        self.time_since_last_combat_tick = 0.0

        # Добавляем фракции в мир
        for faction in factions:
            self.world.add_faction(faction)

        self._setup_world()

    def _find_valid_spawn_point(self, search_rect, max_attempts=100):
        """Finds a random walkable tile within a given rectangle."""
        for _ in range(max_attempts):
            x = random.randint(search_rect.left, search_rect.right - 1)
            y = random.randint(search_rect.top, search_rect.bottom - 1)
            if self.world.map_data[y][x].is_walkable:
                log.debug(f"Found valid spawn point at ({x}, {y})")
                return x, y
        log.warning(f"Could not find a valid spawn point in {search_rect} after {max_attempts} attempts.")
        return None # Could not find a valid point

    def _setup_world(self):
        """Creates initial factions and armies in the world."""
        log.info("Setting up the world...")

        # Используем уже созданные фракции
        faction1 = self.world.factions[0]
        faction2 = self.world.factions[1]
        log.info(f"Faction 1: {faction1.name} (color: {faction1.color})")
        log.info(f"Faction 2: {faction2.name} (color: {faction2.color})")

        # Define spawn areas to ensure armies start far apart
        spawn_area_1 = pygame.Rect(0, 0, self.world.width // 4, self.world.height)
        spawn_area_2 = pygame.Rect(self.world.width * 3 // 4, 0, self.world.width // 4, self.world.height)

        spawn_pos_1 = self._find_valid_spawn_point(spawn_area_1)
        spawn_pos_2 = self._find_valid_spawn_point(spawn_area_2)

        if not spawn_pos_1 or not spawn_pos_2:
            log.error("Failed to find valid spawn points for one or both armies. Aborting setup.")
            # Fallback to default positions if spawn fails, though this is not ideal
            spawn_pos_1 = (10, 10)
            spawn_pos_2 = (self.world.width - 10, self.world.height - 10)

        # Армия 1: Пехотный кулак с лучниками
        army1_units = [Unit("shieldman") for _ in range(3)] + \
                      [Unit("spearman") for _ in range(7)] + \
                      [Unit("archer") for _ in range(5)]
        army1 = Army(faction1, spawn_pos_1[0], spawn_pos_1[1], army1_units)
        self.world.add_army(army1)
        self.ai_generals.append(GeneralAI("aggressive_general", army1))

        # Армия 2: Кавалерийский налет с поддержкой арбалетчиков
        army2_units = [Unit("swordsman") for _ in range(5)] + \
                      [Unit("light_cavalry") for _ in range(4)] + \
                      [Unit("crossbowman") for _ in range(3)]
        army2 = Army(faction2, spawn_pos_2[0], spawn_pos_2[1], army2_units)
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
                elif event.key == pygame.K_v:
                    self.renderer.toggle_political_mode()
                    self.renderer.pre_render_map(self.world.map_data, self.world.territories)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                elif event.button == 5: # Scroll down
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)
                elif event.button == 1: # Left click - логируем инфу о клетке
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    rel_x = mouse_x - self.renderer.game_surface_rect.left
                    rel_y = mouse_y - self.renderer.game_surface_rect.top
                    if 0 <= rel_x < self.renderer.game_surface.get_width() and 0 <= rel_y < self.renderer.game_surface.get_height():
                        # Переводим координаты относительно game_surface в мировые
                        world_x = int(self.camera.x + rel_x / self.camera.zoom)
                        world_y = int(self.camera.y + rel_y / self.camera.zoom)
                        tile_x = world_x // TILE_SIZE
                        tile_y = world_y // TILE_SIZE
                        if 0 <= tile_x < self.world.width and 0 <= tile_y < self.world.height:
                            tile = self.world.map_data[tile_y][tile_x]
                            terrain = tile.base_terrain
                            features = [f.__class__.__name__ for f in tile.features]
                            territory_id = tile.territory_id
                            owner = None
                            for terr in self.world.territories:
                                if terr.id == territory_id:
                                    owner = getattr(terr, 'owner_faction', None)
                                    break
                            log.info(f"TILE INFO: ({tile_x}, {tile_y}) | type: {terrain.name} (key: {terrain.key}) | walkable: {tile.is_walkable} | move_cost: {tile.get_movement_cost()} | defense: {tile.get_defense_bonus()} | features: {features} | territory: {territory_id} | owner: {getattr(owner, 'name', None)}")

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
                        # Determine combat type based on stances
                        if army1.stance == Stance.MOVING and army2.stance == Stance.MOVING:
                            combat_type = CombatType.MEETING_ENGAGEMENT
                            log.info(f"Collision: A meeting engagement between {army1.faction.name} and {army2.faction.name}!")
                            defender, attacker = None, None
                        else:
                            combat_type = CombatType.POSITIONAL_ASSAULT
                            # Determine who is the attacker and who is the defender
                            if army1.stance == Stance.IDLE and army2.stance == Stance.MOVING:
                                defender, attacker = army1, army2
                            elif army2.stance == Stance.IDLE and army1.stance == Stance.MOVING:
                                defender, attacker = army2, army1
                            else: # Default case (e.g., both IDLE), treat army1 as defender for consistency
                                defender, attacker = army1, army2
                            log.info(f"Collision: {attacker.faction.name} is assaulting the position of {defender.faction.name}!")

                        army1.in_combat = True
                        army2.in_combat = True
                        army1.set_target(None) # Stop movement
                        army2.set_target(None)
                        new_combat = Combat(army1, army2, self.world, combat_type)
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