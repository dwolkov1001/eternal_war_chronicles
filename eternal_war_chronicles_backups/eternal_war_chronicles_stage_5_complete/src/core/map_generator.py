import numpy as np
import random
from ..game_objects.tile import Tile

TILE_TYPES = ['GRASS', 'WATER', 'MOUNTAIN', 'FOREST']

def generate_map(width, height, tile_types):
    """
    Generates a game map of a given size with different tile types.
    """
    # Simple random generation for now
    map_layout = np.random.choice(tile_types, size=(height, width), p=[0.7, 0.1, 0.1, 0.1])
    
    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            tile_type = map_layout[y, x]
            if tile_type == 'WATER':
                tile = Tile(tile_type=tile_type, movement_cost=0) # Impassable
            else:
                tile = Tile(tile_type=tile_type)
            row.append(tile)
        game_map.append(row)
        
    return game_map 