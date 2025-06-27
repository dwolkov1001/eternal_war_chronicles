import itertools
from .unit import Unit
from ..core.log import log
from ..core.pathfinding import find_path
from ..misc.enums import Stance

class Army:
    """Represents a group of units, controlled by a faction."""
    
    def __init__(self, faction, x, y, units=None):
        self.id = id(self)
        self.faction = faction
        self.x = x
        self.y = y
        self.units = units if units is not None else []
        self.target_entity = None # The army object we are targeting
        self.path = [] # list of (x, y) tuples for movement
        self.speed = 5.0 # tiles per second
        self.in_combat = False
        self.stance = Stance.IDLE
        self.collision_radius = 0.75 # tiles
        # Для антиспама логирования: запоминаем последний тайл, в котором уже писали лог
        self._last_logged_tile = (int(self.x), int(self.y))

    def set_target(self, target_entity):
        """Sets a target entity for the army and clears any existing path."""
        self.target_entity = target_entity
        self.path = [] # Clear path when new target is set
        self.stance = Stance.IDLE
        if target_entity:
            log.debug(f"Army {self.id} of {self.faction.name} is now targeting army {target_entity.id}.")
        else:
            log.debug(f"Army {self.id} of {self.faction.name} has cleared its target.")

    def set_path(self, path):
        """
        Sets or updates a pre-calculated path for the army to follow.
        If the army is already moving, it tries to update the path smoothly.
        """
        if not path:
            self.path = []
            self.stance = Stance.IDLE
            return

        # Smooth path update
        if self.path and len(self.path) > 1 and len(path) > 1:
            # If we are heading to the same next waypoint, just update the rest of the path
            if self.path[0] == path[0]:
                self.path = path
                return

        # Full path reset
        self.path = path
        self.stance = Stance.MOVING
        # This log can be spammy, so it's commented out for now.
        # log.debug(f"Army {self.id} received a path of {len(path)} steps and is now {self.stance}.")

    def get_distance_to(self, other_army):
        """Calculates the distance to another army."""
        return ((self.x - other_army.x)**2 + (self.y - other_army.y)**2)**0.5

    def get_total_attribute(self, attribute):
        """Calculates the sum of a given attribute for all units in the army."""
        return sum(getattr(unit, attribute) for unit in self.units)

    def take_damage(self, total_damage):
        """Distributes damage among units in the army."""
        if not self.units:
            return []

        damage_per_unit = total_damage / len(self.units)
        lost_units = []
        
        # Take a copy of the list to modify it while iterating
        for unit in list(self.units):
            lost_unit = unit.take_damage(damage_per_unit)
            if lost_unit:
                lost_units.append(lost_unit)
                self.units.remove(unit)
        return lost_units

    def update(self, delta_time, world):
        """Updates the army's position based on its path."""
        if self.in_combat or not self.path:
            return

        target_x, target_y = self.path[0]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance == 0:
             # We might be exactly on the waypoint, pop and continue
            self.path.pop(0)
            if not self.path:
                log.debug(f"Army {self.id} has completed its path.")
                self.target_entity = None # Path is complete
                self.stance = Stance.IDLE
            return

        # Get the tile we are currently on
        current_tile_x, current_tile_y = int(self.x), int(self.y)
        tile = world.map_data[current_tile_y][current_tile_x]
        
        # Calculate movement speed considering terrain cost
        move_speed = self.speed * delta_time / tile.get_movement_cost()

        if move_speed >= distance:
            # We can reach the waypoint in this frame
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
            if not self.path:
                log.debug(f"Army {self.id} has completed its path.")
                self.target_entity = None # Path is complete
                self.stance = Stance.IDLE
        else:
            # Move towards the waypoint
            self.x += (dx / distance) * move_speed
            self.y += (dy / distance) * move_speed

        # ---- Логирование позиции (только при смене тайла) ----
        current_tile = (int(self.x), int(self.y))
        if current_tile != self._last_logged_tile:
            self._last_logged_tile = current_tile
            log.debug(f"Army {self.id} moved to tile {current_tile} (Faction: {self.faction.name}).")

    @property
    def total_hp(self):
        """Total HP of all units in the army."""
        return sum(unit.hp for unit in self.units)
    
    @property
    def max_hp(self):
        """Maximum possible HP of all units in the army."""
        return sum(unit.max_hp for unit in self.units)

    @property
    def attack_power(self):
        """Total attack power of the army."""
        return self.get_total_attribute('attack')

    @property
    def defense_power(self):
        """Total defense power of the army."""
        return self.get_total_attribute('defense')

    @property
    def is_destroyed(self):
        """Checks if the army has any units left."""
        return not self.units

    def get_color(self):
        """Returns the faction's color."""
        return self.faction.color 