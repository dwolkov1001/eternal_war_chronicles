class GameWorld:
    """
    Хранит и управляет состоянием всего игрового мира, включая карту, фракции и армии.
    """
    def __init__(self):
        self.map_data = None
        self.factions = []
        self.armies = []
        self.current_time = 0 