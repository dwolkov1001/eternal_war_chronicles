import numpy as np
import random
from opensimplex import OpenSimplex

from ..game_objects.tile import Tile, Road
from ..game_objects.territory import Territory
from .pathfinding import find_path
from .terrain_config import TERRAIN_TYPES # Импортируем новый конфиг

def _generate_noise_map(width, height, scale, octaves, persistence, lacunarity, seed):
    """Генерирует карту шума заданного размера и параметров."""
    simplex = OpenSimplex(seed)
    noise_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            amplitude = 1
            frequency = 1
            noise_value = 0
            for _ in range(octaves):
                sample_x = x / scale * frequency
                sample_y = y / scale * frequency
                
                # Используем .noise2 для 2D шума
                noise = simplex.noise2(sample_x, sample_y)
                noise_value += noise * amplitude
                
                amplitude *= persistence
                frequency *= lacunarity
            noise_map[y][x] = noise_value
            
    # Нормализуем карту шума к диапазону [0, 1]
    if np.max(noise_map) != np.min(noise_map):
        noise_map = (noise_map - np.min(noise_map)) / (np.max(noise_map) - np.min(noise_map))
    return noise_map


def _generate_roads(game_map, width, height, walkable_tiles):
    """Generates a road network on the map using A*."""
    if not walkable_tiles:
        return

    # Выбираем ключевые точки интереса, например, будущие города или просто случайные проходимые тайлы
    num_poi = max(10, int((width * height) / 200)) # Больше точек для более связной сети
    points_of_interest = random.sample(walkable_tiles, k=min(len(walkable_tiles), num_poi))

    # Соединяем точки по принципу минимального остовного дерева (упрощенно)
    # или просто последовательно для простоты
    for i in range(len(points_of_interest) - 1):
        start = points_of_interest[i]
        goal = points_of_interest[i+1]

        path = find_path(game_map, start, goal, path_type='fastest')

        if path:
            for x, y in path:
                # Добавляем дорогу, если ее еще нет
                if not any(isinstance(f, Road) for f in game_map[y][x].features):
                    game_map[y][x].add_feature(Road())


def _create_territories(game_map, width, height, num_territories_x=3, num_territories_y=3):
    """Divides the map into territories and assigns tiles to them."""
    territories = []
    territory_id_counter = 0
    
    region_width = width // num_territories_x
    region_height = height // num_territories_y

    for i in range(num_territories_x):
        for j in range(num_territories_y):
            
            start_x = i * region_width
            end_x = (i + 1) * region_width if i < num_territories_x - 1 else width
            
            start_y = j * region_height
            end_y = (j + 1) * region_height if j < num_territories_y - 1 else height

            territory_tiles = []
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    game_map[y][x].territory_id = territory_id_counter
                    territory_tiles.append((x, y))
            
            if not territory_tiles:
                continue

            territory = Territory(
                territory_id=territory_id_counter,
                name=f"Region {territory_id_counter}"
            )
            territory.tiles = territory_tiles
            territories.append(territory)
            territory_id_counter += 1
            
    return territories


def generate_map(width, height, factions=None, seed=None):
    """
    Generates a realistic game map using multiple noise layers for elevation,
    moisture, and temperature. Optionally assigns territory owners from factions.
    """
    if seed is None:
        seed = random.randint(0, 10000)
    
    # 1. Генерируем карты высот, влажности и температуры
    elevation_map = _generate_noise_map(width, height, scale=90, octaves=6, persistence=0.5, lacunarity=2.0, seed=seed)
    moisture_map = _generate_noise_map(width, height, scale=70, octaves=4, persistence=0.5, lacunarity=2.0, seed=seed + 1)
    
    game_map = [[None for _ in range(width)] for _ in range(height)]
    walkable_tiles = []

    # 2. Определяем тип ландшафта для каждого тайла
    for y in range(height):
        for x in range(width):
            e = elevation_map[y][x]
            m = moisture_map[y][x]
            
            terrain_key = "GRASSLAND" # Default

            if e < 0.2:
                terrain_key = "DEEP_WATER"
            elif e < 0.25:
                terrain_key = "WATER"
            elif e < 0.3:
                terrain_key = "SHALLOW_RIVER" # Изобразим как прибрежные отмели/реки
            
            elif e < 0.6: # Равнины и леса
                if m < 0.3:
                    terrain_key = "WASTELAND"
                elif m < 0.6:
                    terrain_key = "PLAINS"
                else:
                    terrain_key = "DECIDUOUS_FOREST"
            
            elif e < 0.8: # Холмы и скалы
                if m < 0.4:
                    terrain_key = "STEPPE"
                else:
                    terrain_key = "HILLS"
            
            else: # Горы
                if m < 0.5:
                    terrain_key = "ROCKS"
                else:
                    terrain_key = "MOUNTAIN_PEAK"
            
            # Особые случаи
            if terrain_key == "DECIDUOUS_FOREST" and e > 0.5 and m > 0.8:
                terrain_key = "SWAMP" # Болота в низинных и влажных лесах
            if terrain_key == "HILLS" and e > 0.75:
                terrain_key = "PLATEAU"
                
            terrain = TERRAIN_TYPES[terrain_key]
            game_map[y][x] = Tile(terrain)
            
            if terrain.is_walkable:
                walkable_tiles.append((x, y))

    # 3. Генерируем дороги
    _generate_roads(game_map, width, height, walkable_tiles)

    # 4. Создаем территории
    territories = _create_territories(game_map, width, height)

    # 5. Назначаем владельцев территориям, если фракции переданы
    if factions is not None and len(factions) > 0:
        for i, territory in enumerate(territories):
            owner = factions[i % len(factions)]
            territory.owner_faction = owner

    # 6. TODO: Размещаем города/деревни в стратегически выгодных местах
    
    return game_map, territories 

def get_tile_type_by_seed(seed, x, y, width, height):
    """
    Возвращает ключ типа тайла по сиду и координатам (x, y), используя ту же логику, что и в generate_map.
    """
    # Генерируем значения шума для elevation и moisture только для нужной точки
    simplex_elev = OpenSimplex(seed)
    simplex_moist = OpenSimplex(seed + 1)
    
    scale_elev = 90
    octaves_elev = 6
    persistence_elev = 0.5
    lacunarity_elev = 2.0
    
    scale_moist = 70
    octaves_moist = 4
    persistence_moist = 0.5
    lacunarity_moist = 2.0

    # elevation
    amplitude = 1
    frequency = 1
    noise_value_elev = 0
    for _ in range(octaves_elev):
        sample_x = x / scale_elev * frequency
        sample_y = y / scale_elev * frequency
        noise = simplex_elev.noise2(sample_x, sample_y)
        noise_value_elev += noise * amplitude
        amplitude *= persistence_elev
        frequency *= lacunarity_elev
    # moisture
    amplitude = 1
    frequency = 1
    noise_value_moist = 0
    for _ in range(octaves_moist):
        sample_x = x / scale_moist * frequency
        sample_y = y / scale_moist * frequency
        noise = simplex_moist.noise2(sample_x, sample_y)
        noise_value_moist += noise * amplitude
        amplitude *= persistence_moist
        frequency *= lacunarity_moist
    # Нормализация невозможна без всей карты, но для анализа достаточно относительных порогов
    # Используем те же пороги, что и в generate_map
    e = noise_value_elev
    m = noise_value_moist
    # Пороговые значения взяты из generate_map, но без нормализации
    terrain_key = "GRASSLAND" # Default
    if e < -0.8:
        terrain_key = "DEEP_WATER"
    elif e < -0.6:
        terrain_key = "WATER"
    elif e < -0.4:
        terrain_key = "SHALLOW_RIVER"
    elif e < 0.2:
        if m < -0.4:
            terrain_key = "WASTELAND"
        elif m < 0.2:
            terrain_key = "PLAINS"
        else:
            terrain_key = "DECIDUOUS_FOREST"
    elif e < 0.6:
        if m < -0.2:
            terrain_key = "STEPPE"
        else:
            terrain_key = "HILLS"
    else:
        if m < 0:
            terrain_key = "ROCKS"
        else:
            terrain_key = "MOUNTAIN_PEAK"
    # Особые случаи (примерно)
    if terrain_key == "DECIDUOUS_FOREST" and e > 0.5 and m > 0.8:
        terrain_key = "SWAMP"
    if terrain_key == "HILLS" and e > 0.75:
        terrain_key = "PLATEAU"
    return terrain_key 