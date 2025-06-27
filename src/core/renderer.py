import pygame
from ..game_objects.tile import Road # Import Road to check for it

# TILE_SIZE можно сделать настраиваемым параметром в будущем
TILE_SIZE = 16  # Базовый размер одного тайла в пикселях

class Renderer:
    """
    Класс, отвечающий за отрисовку всех игровых объектов на экране.
    """
    def __init__(self, screen):
        self.screen = screen
        self.game_surface = None
        self.game_surface_rect = None
        self.map_surface = None # Surface for the pre-rendered map
        self.calculate_game_surface()
        self.political_mode = False

    def calculate_game_surface(self):
        """
        Рассчитывает размеры и положение центральной квадратной игровой области.
        """
        screen_w, screen_h = self.screen.get_size()
        # Выбираем меньшую сторону для размера квадрата
        side_length = min(screen_w, screen_h)
        
        # Создаем поверхность (Surface) для отрисовки игровой области
        self.game_surface = pygame.Surface((side_length, side_length))
        
        # Рассчитываем положение этой поверхности, чтобы она была по центру
        top_left_x = (screen_w - side_length) // 2
        top_left_y = (screen_h - side_length) // 2
        self.game_surface_rect = self.game_surface.get_rect(topleft=(top_left_x, top_left_y))

    def toggle_political_mode(self):
        self.political_mode = not self.political_mode

    def pre_render_map(self, map_data, territories=None, factions=None):
        """Pre-renders the entire map to a separate surface for performance."""
        map_height = len(map_data)
        if map_height == 0: return
        map_width = len(map_data[0])

        self.map_surface = pygame.Surface((map_width * TILE_SIZE, map_height * TILE_SIZE))
        for row in range(map_height):
            for col in range(map_width):
                tile = map_data[row][col]
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                # --- Политический режим ---
                if self.political_mode and territories is not None:
                    territory_id = tile.territory_id
                    owner_color = (80, 80, 80) # Default gray
                    if territory_id is not None:
                        for t in territories:
                            if t.id == territory_id and t.owner_faction is not None:
                                # Попробуем взять цвет фракции (строка или tuple)
                                c = t.owner_faction.color
                                if isinstance(c, str):
                                    if c.lower() == "blue": owner_color = (0, 120, 255)
                                    elif c.lower() == "red": owner_color = (220, 40, 40)
                                    else: owner_color = (80, 80, 80)
                                else:
                                    owner_color = c
                    pygame.draw.rect(self.map_surface, owner_color, rect)
                else:
                    # 1. Отрисовка базового ландшафта
                    base_color = tile.base_terrain.color
                    pygame.draw.rect(self.map_surface, base_color, rect)

        # 2. Второй проход: "умная" отрисовка всех дорог
        # Мы делаем это в отдельном цикле, чтобы иметь доступ ко всей карте
        # и корректно проверять соседей для каждого тайла.
        for row in range(map_height):
            for col in range(map_width):
                tile = map_data[row][col]
                if any(isinstance(f, Road) for f in tile.features):
                    road_color = (139, 69, 19) # Стандартный цвет дороги
                    road_width = max(2, TILE_SIZE // 4)

                    center_x = col * TILE_SIZE + TILE_SIZE // 2
                    center_y = row * TILE_SIZE + TILE_SIZE // 2
                    
                    # Рисуем "узел" в центре каждого дорожного тайла
                    pygame.draw.circle(self.map_surface, road_color, (center_x, center_y), road_width // 2)

                    # Соединяем с соседями (проверяем только "вперед", чтобы не рисовать линии дважды)
                    # Сосед справа
                    if col + 1 < map_width and any(isinstance(f, Road) for f in map_data[row][col + 1].features):
                        pygame.draw.line(self.map_surface, road_color, (center_x, center_y), (center_x + TILE_SIZE, center_y), road_width)
                    # Сосед снизу
                    if row + 1 < map_height and any(isinstance(f, Road) for f in map_data[row + 1][col].features):
                        pygame.draw.line(self.map_surface, road_color, (center_x, center_y), (center_x, center_y + TILE_SIZE), road_width)
                    # Сосед снизу-справа (диагональ)
                    if row + 1 < map_height and col + 1 < map_width and any(isinstance(f, Road) for f in map_data[row + 1][col + 1].features):
                         pygame.draw.line(self.map_surface, road_color, (center_x, center_y), (center_x + TILE_SIZE, center_y + TILE_SIZE), road_width)
                    # Сосед снизу-слева (диагональ)
                    if row + 1 < map_height and col - 1 >= 0 and any(isinstance(f, Road) for f in map_data[row + 1][col - 1].features):
                         pygame.draw.line(self.map_surface, road_color, (center_x, center_y), (center_x - TILE_SIZE, center_y + TILE_SIZE), road_width)

    def render(self, world, camera):
        """
        Главный метод отрисовки.
        """
        self.screen.fill((0, 0, 0))  # Заливаем весь экран черным

        if self.map_surface:
            self.render_map(camera)

        if world.armies:
            self.render_armies(world.armies, camera)

        # Отрисовываем игровую поверхность на главном экране
        self.screen.blit(self.game_surface, self.game_surface_rect)

    def render_map(self, camera):
        """Renders the visible part of the pre-rendered map."""
        self.game_surface.fill((25, 25, 25))  # Фон для карты

        # Calculate the visible portion of the map surface
        source_rect = pygame.Rect(camera.x, camera.y, 
                                  camera.width / camera.zoom, 
                                  camera.height / camera.zoom)

        # Scale the visible portion to fit the game surface
        scaled_surface = pygame.transform.scale(self.map_surface.subsurface(source_rect), self.game_surface.get_size())
        self.game_surface.blit(scaled_surface, (0, 0))

    def render_armies(self, armies, camera):
        """Отрисовывает армии на игровой поверхности."""
        for army in armies:
            # 1. Используем точные координаты армии (float), а не округляем до целого тайла
            #    Это позволяет корректно отображать фактическое положение армии между тайлами
            army_world_x = (army.x + 0.5) * TILE_SIZE
            army_world_y = (army.y + 0.5) * TILE_SIZE

            # 3. Трансформируем мировые координаты в экранные
            army_screen_x = (army_world_x - camera.x) * camera.zoom
            army_screen_y = (army_world_y - camera.y) * camera.zoom

            # 4. Проверяем, находится ли армия в поле зрения
            if 0 <= army_screen_x <= self.game_surface.get_width() and \
               0 <= army_screen_y <= self.game_surface.get_height():
                
                # Радиус круга армии
                radius = (TILE_SIZE / 2 * camera.zoom) * 1.2
                
                # Цвет армии
                color = (0, 0, 255) if "Sun" in army.faction.name else (255, 0, 0)
                if army.in_combat:
                    color = (255, 255, 0) # Yellow

                # Рисуем круг армии
                pygame.draw.circle(
                    self.game_surface,
                    color,
                    (round(army_screen_x), round(army_screen_y)),
                    round(radius)
                )

                # Отрисовка количества юнитов
                try:
                    font = pygame.font.Font(None, int(18 * camera.zoom))
                    text = font.render(str(len(army.units)), True, (255, 255, 255))
                    text_rect = text.get_rect(center=(round(army_screen_x), round(army_screen_y)))
                    self.game_surface.blit(text, text_rect)
                except pygame.error: # Font size is too small
                    pass

            # Logic for rendering army selection/destination was removed
            # as there is no manual control for now.