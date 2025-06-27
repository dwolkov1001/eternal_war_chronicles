import numpy as np
from src.game_objects.tile import Tile

def generate_map(width, height):
    """
    Генерирует игровую карту заданного размера.
    """
    # Создаем карту, где 1 = земля, 0 = вода
    map_layout = np.random.choice([0, 1], size=(height, width), p=[0.2, 0.8])
    
    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            if map_layout[y, x] == 1:
                # Это земля (трава)
                tile = Tile(tile_type='GRASS')
            else:
                # Это вода
                tile = Tile(tile_type='WATER', movement_cost=0) # Непроходимый
            row.append(tile)
        game_map.append(row)
        
    return game_map 