class Unit:
    """
    The base class for all combat units in the game.
    """
    def __init__(self, name: str, max_hp: int, attack: int, defense: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    def __repr__(self):
        return f"Unit(name={self.name}, hp={self.hp}/{self.max_hp})" 