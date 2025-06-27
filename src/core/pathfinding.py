import heapq


def diagonal_distance(a, b):
    """
    Heuristic for an 8-directional grid (Chebyshev distance).
    It's more accurate than Manhattan distance when diagonal movement is allowed.
    """
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def find_path(grid, start, end, path_type='fastest'):
    """
    Finds a path from start to end on a grid using the A* algorithm.
    """
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    # If start and end points are the same, the path is empty.
    if start == end:
        return []

    width = len(grid[0])
    height = len(grid)
    
    # Check if start or end points are outside the grid or on an unwalkable tile
    if not (0 <= start[0] < width and 0 <= start[1] < height and grid[start[1]][start[0]].is_walkable):
        return None
    if not (0 <= end[0] < width and 0 <= end[1] < height and grid[end[1]][end[0]].is_walkable):
        return None

    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = { (x, y): float('inf') for y in range(height) for x in range(width) }
    g_score[start] = 0
    
    f_score = { (x, y): float('inf') for y in range(height) for x in range(width) }
    f_score[start] = diagonal_distance(start, end)

    # Safety break to prevent the game from freezing on unreachable targets
    iteration_limit = 20000 
    iterations = 0

    while open_set:
        iterations += 1
        if iterations > iteration_limit:
            return None # Pathfinding took too long, assume it's unreachable

        _, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
                tile = grid[neighbor[1]][neighbor[0]]
                if not tile.is_walkable:
                    continue
                
                # Determine movement cost
                if path_type == 'fastest':
                    cost = tile.get_movement_cost()
                else: # 'shortest'
                    cost = 1
                
                # Add diagonal movement penalty
                if dx != 0 and dy != 0:
                    cost *= 1.414 # ~sqrt(2)
                
                tentative_g_score = g_score[current] + cost
                
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + diagonal_distance(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None # No path found 