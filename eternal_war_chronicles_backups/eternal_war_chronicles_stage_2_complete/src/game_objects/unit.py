class Unit:
    """
    Базовый класс для всех боевых единиц в игре.
    """
    def __init__(self, hp, attack, defense):
        self.hp = hp
        self.attack = attack
        self.defense = defense 