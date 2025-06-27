from ..core.unit_config import UNIT_TYPES

class Unit:
    """
    The base class for all combat units in the game.
    It initializes its attributes based on a unit type from unit_config.
    """
    def __init__(self, unit_type: str):
        if unit_type not in UNIT_TYPES:
            raise ValueError(f"Unknown unit type: {unit_type}")

        config = UNIT_TYPES[unit_type]

        self.unit_type = unit_type
        self.name = config["name"]
        self.max_hp = config["base_hp"]
        self.hp = self.max_hp
        self.attack = config["base_attack"]
        self.defense = config["base_defense"]
        self.counters = config.get("counters", [])
        self.countered_by = config.get("countered_by", [])

    def __repr__(self):
        return f"Unit(type={self.unit_type}, hp={self.hp}/{self.max_hp})" 