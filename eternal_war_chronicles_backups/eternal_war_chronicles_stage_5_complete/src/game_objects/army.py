import math
import itertools

class Army:
    """
    Represents an army composed of multiple units.
    """
    id_iter = itertools.count()

    def __init__(self, faction, x: int, y: int, units=None):
        self.id = next(self.id_iter)
        self.faction = faction
        self.units = units if units is not None else []
        self.x = x
        self.y = y
        
        self.destination_x = None
        self.destination_y = None
        self.target_entity = None # The entity (e.g., another army) this army is pursuing
        self.speed = 5.0  # tiles per second
        
        self.in_combat = False
        self.collision_radius = 2.0

    def set_target(self, target_entity):
        """Sets a target entity for the army to pursue."""
        self.target_entity = target_entity

    def set_destination(self, x: int, y: int):
        """Sets the army's destination. Stops pursuing a target if one was set."""
        self.target_entity = None # Manual destination overrides target following
        self.destination_x = x
        self.destination_y = y

    def get_distance_to(self, other_army):
        """Calculates the distance to another army."""
        dx = self.x - other_army.x
        dy = self.y - other_army.y
        return math.sqrt(dx**2 + dy**2)

    def update(self, dt, world):
        """Moves the army, automatically pursuing a target or moving to a destination."""
        if self.in_combat:
            self.target_entity = None
            self.destination_x = None
            return

        # If pursuing a target entity, update the destination to its current position
        if self.target_entity:
            self.destination_x = self.target_entity.x
            self.destination_y = self.target_entity.y
            
        if self.destination_x is None:
            return

        # Get the terrain cost of the current tile
        current_tile = world.map_data[int(self.y)][int(self.x)]
        movement_cost = current_tile.movement_cost

        # Don't move if on an impassable tile
        if movement_cost == 0:
            return

        dx = self.destination_x - self.x
        dy = self.destination_y - self.y
        
        distance = math.sqrt(dx**2 + dy**2)

        # Adjust speed based on terrain
        step = self.speed * dt * movement_cost
        
        if distance < step:
            self.x = self.destination_x
            self.y = self.destination_y
            self.destination_x = None
            self.destination_y = None
        else:
            self.x += dx / distance * step
            self.y += dy / distance * step

    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)

    def __repr__(self):
        return f"Army(id={self.id}, faction='{self.faction.name}', units={len(self.units)})"

    @property
    def color(self):
        """Возвращает цвет фракции."""
        return self.faction.color 