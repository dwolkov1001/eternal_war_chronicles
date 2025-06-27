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
        # Передаем в камеру размеры игровой поверхности, а не всего окна
        game_surface_size = self.renderer.game_surface.get_size()
        self.camera = Camera(game_surface_size[0], game_surface_size[1])
        
        # Генерация мира
        self.map_width_tiles, self.map_height_tiles = 100, 100  # Размеры карты в тайлах
        self.world.map_data = generate_map(self.map_width_tiles, self.map_height_tiles)

        self.selected_army = None

    def screen_to_world_coords(self, screen_pos, tile_coords=False):
        """
        Преобразует экранные координаты в мировые.
        :param screen_pos: Кортеж (x, y) координат на экране.
        :param tile_coords: Если True, возвращает координаты в тайлах (int). 
                            Иначе, возвращает мировые координаты (float).
        """
        game_surface_pos_x = screen_pos[0] - self.renderer.game_surface_rect.x
        game_surface_pos_y = screen_pos[1] - self.renderer.game_surface_rect.y

        world_x = self.camera.x + game_surface_pos_x / self.camera.zoom
        world_y = self.camera.y + game_surface_pos_y / self.camera.zoom

        if tile_coords:
            return int(world_x / TILE_SIZE), int(world_y / TILE_SIZE)
        else:
            return world_x / TILE_SIZE, world_y / TILE_SIZE

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
        
        zoomed = False
        lmb_or_rmb_clicked = False # Флаг для клика ЛКМ или ПКМ

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key in [pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS]:
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                    zoomed = True
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)
                    zoomed = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    lmb_or_rmb_clicked = True

                if event.button == 1: # Левая кнопка мыши - выбор армии
                    clicked_tile = self.screen_to_world_coords(event.pos, tile_coords=True)
                    
                    # Ищем, попали ли мы по какой-либо армии
                    clicked_army = None
                    for army in self.world.armies:
                        if army.position == clicked_tile:
                            clicked_army = army
                            break
                    
                    # Сначала всё сбрасываем.
                    for army in self.world.armies:
                        army.selected = False
                    self.selected_army = None

                    # Если мы действительно попали по армии, выбираем её
                    if clicked_army:
                        clicked_army.selected = True
                        self.selected_army = clicked_army
                
                elif event.button == 3: # Правая кнопка мыши - задание цели
                    if self.selected_army:
                        # Цель теперь в мировых координатах (float)
                        destination_world = self.screen_to_world_coords(event.pos)
                        self.selected_army.destination = destination_world
                
                elif event.button == 4:
                    self.camera.zoom_in(map_width_pixels, map_height_pixels)
                    zoomed = True
                elif event.button == 5:
                    self.camera.zoom_out(map_width_pixels, map_height_pixels)
                    zoomed = True

            if event.type == pygame.VIDEORESIZE:
                self.renderer.calculate_game_surface()
                game_surface_size = self.renderer.game_surface.get_size()
                self.camera.width = game_surface_size[0]
                self.camera.height = game_surface_size[1]
                zoomed = True 

        # Управление перемещением камеры с зажатыми клавишами
        move_dx, move_dy = 0, 0
        keys = pygame.key.get_pressed()
        
        # Проверяем, был ли клик мыши в этом кадре
        if not lmb_or_rmb_clicked:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_dx -= 5
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_dx += 5
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move_dy -= 5
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move_dy += 5

        if move_dx != 0 or move_dy != 0:
            self.camera.move(move_dx, move_dy, map_width_pixels, map_height_pixels)

        if zoomed:
            self.camera.move(0, 0, map_width_pixels, map_height_pixels)

    def update(self):
        """Обновляет состояние игры."""
        for army in self.world.armies:
            army.move()

    def render(self):
        """Отрисовывает все игровые объекты на экране."""
        self.renderer.render(self.world, self.camera)
        pygame.display.flip() 