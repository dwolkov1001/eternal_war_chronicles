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

    def render(self, world, camera):
        """
        Главный метод отрисовки.
        """
        self.screen.fill((0, 0, 0))  # Заливаем весь экран черным

        if world.map_data:
            self.render_map(world.map_data, camera)

        # Отрисовываем игровую поверхность на главном экране
        self.screen.blit(self.game_surface, self.game_surface_rect)

    def render_map(self, map_data, camera):
        """Отрисовывает видимую часть карты с учетом камеры."""
        self.game_surface.fill((25, 25, 25))  # Фон для карты

        map_height = len(map_data)
        if map_height == 0:
            return
        map_width = len(map_data[0])
        if map_width == 0:
            return

        # Рассчитываем, какие тайлы видимы в камере
        world_left = camera.x
        world_top = camera.y
        world_right = camera.x + camera.width / camera.zoom
        world_bottom = camera.y + camera.height / camera.zoom

        start_col = max(0, int(world_left / TILE_SIZE))
        start_row = max(0, int(world_top / TILE_SIZE))
        end_col = min(map_width, int(world_right / TILE_SIZE) + 1)
        end_row = min(map_height, int(world_bottom / TILE_SIZE) + 1)

        # Отрисовываем только видимые тайлы
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = map_data[row][col]
                color = TILE_COLORS.get(tile.tile_type, (255, 255, 255))

                # Трансформируем мировые координаты в экранные
                tile_screen_x = (col * TILE_SIZE - camera.x) * camera.zoom
                tile_screen_y = (row * TILE_SIZE - camera.y) * camera.zoom
                
                zoomed_size = TILE_SIZE * camera.zoom
                
                # Добавляем +1 к размеру, чтобы избежать щелей при отдалении
                rect = pygame.Rect(round(tile_screen_x), round(tile_screen_y), zoomed_size + 1, zoomed_size + 1)
                pygame.draw.rect(self.game_surface, color, rect)