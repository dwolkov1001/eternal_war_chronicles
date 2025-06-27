class Territory:
    """
    Represents a region on the map, composed of multiple tiles.
    It has an owner and a unique ID.
    """
    def __init__(self, territory_id: int, name: str):
        self.id = territory_id
        self.name = name
        self.owner_faction = None
        self.tiles = []

    def __repr__(self):
        owner_name = self.owner_faction.name if self.owner_faction else "None"
        return f"Territory(id={self.id}, name='{self.name}', owner='{owner_name}', tiles={len(self.tiles)})" 