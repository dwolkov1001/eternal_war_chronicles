import pygame

# Цвета для разных типов тайлов
TILE_COLORS = {
    'GRASS': (50, 205, 50),   # Зеленый
    'WATER': (0, 191, 255),   # Синий
    'MOUNTAIN': (139, 137, 137), # Серый
    'FOREST': (34, 139, 34)      # Темно-зеленый
}

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

    def pre_render_map(self, map_data):
        """Pre-renders the entire map to a separate surface for performance."""
        map_height = len(map_data)
        if map_height == 0: return
        map_width = len(map_data[0])

        self.map_surface = pygame.Surface((map_width * TILE_SIZE, map_height * TILE_SIZE))
        for row in range(map_height):
            for col in range(map_width):
                tile = map_data[row][col]
                color = TILE_COLORS.get(tile.tile_type, (255, 255, 255))
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.map_surface, color, rect)

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
            # Получаем мировые float-координаты армии
            army_world_x = army.x * TILE_SIZE
            army_world_y = army.y * TILE_SIZE

            # Трансформируем мировые координаты в экранные
            army_screen_x = (army_world_x - camera.x) * camera.zoom
            army_screen_y = (army_world_y - camera.y) * camera.zoom

            # Проверяем, находится ли армия в поле зрения
            if 0 <= army_screen_x <= self.game_surface.get_width() and \
               0 <= army_screen_y <= self.game_surface.get_height():
                
                # Use a fixed radius for now, or based on zoom
                radius = (TILE_SIZE / 2 * camera.zoom) * 1.2
                
                color = (0, 0, 255) if "Sun" in army.faction.name else (255, 0, 0)
                if army.in_combat:
                    color = (255, 255, 0) # Yellow

                pygame.draw.circle(
                    self.game_surface,
                    color,
                    (round(army_screen_x), round(army_screen_y)),
                    round(radius)
                )

                # Render unit count
                try:
                    font = pygame.font.Font(None, int(18 * camera.zoom))
                    text = font.render(str(len(army.units)), True, (255, 255, 255))
                    text_rect = text.get_rect(center=(round(army_screen_x), round(army_screen_y)))
                    self.game_surface.blit(text, text_rect)
                except pygame.error: # Font size is too small
                    pass

            # Logic for rendering army selection/destination was removed
            # as there is no manual control for now.