class Army:
    """
    Класс, представляющий армию, состоящую из множества юнитов.
    """
    def __init__(self, units=None, position=(0, 0)):
        self.units = units if units is not None else []
        self.position = position 