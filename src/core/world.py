from ..game_objects.faction import Faction
from ..game_objects.army import Army
from ..game_objects.unit import Unit

class GameWorld:
    """
    Stores and manages the state of all game objects and the map.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map_data = [] # Should be filled by a generator
        self.factions = []
        self.armies = []
        self.territories = []

    def add_faction(self, faction: Faction):
        """Adds a faction to the world."""
        if faction not in self.factions:
            self.factions.append(faction)

    def add_army(self, army: Army):
        """Adds an army to the world."""
        if army not in self.armies:
            self.armies.append(army)

    def remove_army(self, army: Army):
        """Removes an army from the world."""
        if army in self.armies:
            self.armies.remove(army)
        # Also remove from faction's list if it's still there
        if hasattr(army, 'faction') and army.faction and hasattr(army.faction, 'armies') and army in army.faction.armies:
            army.faction.armies.remove(army)

    # Этот метод больше не используется, вся логика обновления в Game.
    # def update(self, time_multiplier):
    #     """Обновляет состояние всех объектов в мире."""
    #     for army in self.armies:
    #         army.move(time_multiplier) 