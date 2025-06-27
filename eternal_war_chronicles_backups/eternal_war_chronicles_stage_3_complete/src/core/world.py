from src.game_objects.faction import Faction
from src.game_objects.army import Army
import random

class GameWorld:
    """
    Хранит и управляет состоянием всего игрового мира, включая карту, фракции и армии.
    """
    def __init__(self):
        self.map_data = None
        self.factions = []
        self.armies = []
        self.current_time = 0 
        self._create_test_factions_and_armies()

    def _create_test_factions_and_armies(self):
        """Создает тестовые данные для отладки."""
        # Фракция 1: "Королевство Севера" (синие)
        faction1 = Faction(name="Королевство Севера", color=(0, 0, 255))
        army1_1 = Army(faction=faction1, position=(random.randint(10, 30), random.randint(10, 30)))
        army1_2 = Army(faction=faction1, position=(random.randint(10, 30), random.randint(10, 30)))
        faction1.armies.extend([army1_1, army1_2])

        # Фракция 2: "Орден Пламени" (красные)
        faction2 = Faction(name="Орден Пламени", color=(255, 0, 0))
        army2_1 = Army(faction=faction2, position=(random.randint(70, 90), random.randint(70, 90)))
        army2_2 = Army(faction=faction2, position=(random.randint(70, 90), random.randint(70, 90)))
        faction2.armies.extend([army2_1, army2_2])

        self.factions.extend([faction1, faction2])
        self.armies.extend([army1_1, army1_2, army2_1, army2_2]) 