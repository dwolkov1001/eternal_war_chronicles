class Faction:
    """
    Класс, представляющий фракцию или сторону конфликта.
    """
    def __init__(self, name, color, armies=None):
        self.name = name
        self.color = color
        self.armies = armies if armies is not None else [] 