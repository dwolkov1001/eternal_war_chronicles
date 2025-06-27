import pygame
from src.core.renderer import Renderer, TILE_SIZE
from src.core.world import GameWorld
from src.core.map_generator import generate_map
from src.core.camera import Camera

class Game:
    """
    Основной класс игры, управляющий главным циклом, состоянием игры и рендерингом.
    """
    def __init__(self):
        pygame.init()
        # Возвращаемся к фиксированному размеру окна
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Хроники Вечной Войны")

        self.running = True
        self.clock = pygame.time.Clock()
        
        # Управление временем
        self.time_multiplier = 1.0  # 1.0 = нормальная скорость, >1.0 = ускорение, <1.0 = замедление
        self.paused = False

        # Создание основных компонентов
        self.world = GameWorld()
        self.renderer = Renderer(self.screen)
        self.camera = Camera(self.renderer.game_surface.get_width(), self.renderer.game_surface.get_height())
        
        # Генерация мира
        self.map_width_tiles, self.map_height_tiles = 100, 100  # Размеры карты в тайлах
        self.world.map_data = generate_map(self.map_width_tiles, self.map_height_tiles)

    def run(self):
        """Запускает главный игровой цикл."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        """Обрабатывает пользовательский ввод и системные события."""
        map_width_pixels = self.map_width_tiles * TILE_SIZE
        map_height_pixels = self.map_height_tiles * TILE_SIZE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Управление камерой (Клавиатура и Мышь)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Зум с клавиатуры (основной и Numpad)
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)

            # Зум с колеса мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесо вверх
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                elif event.button == 5:  # Колесо вниз
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)

        # Управление перемещением камеры с зажатыми клавишами
        move_dx, move_dy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dx -= self.camera.move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dx += self.camera.move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_dy -= self.camera.move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_dy += self.camera.move_speed

        # Применяем движение
        if move_dx != 0 or move_dy != 0:
            self.camera.move(move_dx, move_dy, map_width_pixels, map_height_pixels)

    def update(self):
        """Обновляет состояние игры. Будет расширяться в будущем."""
        pass

    def render(self):
        """Отрисовывает все игровые объекты на экране."""
        self.renderer.render(self.world, self.camera)
        pygame.display.flip() 