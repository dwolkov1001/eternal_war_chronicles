import math

class Army:
    """
    Класс, представляющий армию, состоящую из множества юнитов.
    """
    def __init__(self, faction, position=(0, 0), units=None):
        self.faction = faction
        self.units = units if units is not None else []
        self.tile_position = position # Позиция в тайлах (x, y)
        self.world_position = (position[0] + 0.5, position[1] + 0.5) # Позиция в мировых координатах (плавающая)
        
        self.destination = None # Цель в мировых координатах
        self.selected = False
        self.speed = 0.05 # Скорость перемещения (в тайлах за кадр)

    def move(self):
        """Двигает армию к цели."""
        if not self.destination:
            return

        dest_x, dest_y = self.destination
        pos_x, pos_y = self.world_position

        # Вектор направления
        dx = dest_x - pos_x
        dy = dest_y - pos_y
        
        distance = math.sqrt(dx**2 + dy**2)

        # Если мы уже достаточно близко, останавливаемся
        if distance < self.speed:
            self.world_position = self.destination
            self.tile_position = (int(self.destination[0]), int(self.destination[1]))
            self.destination = None
        else:
            # Движемся в направлении цели
            self.world_position = (pos_x + dx / distance * self.speed, 
                                   pos_y + dy / distance * self.speed)
            self.tile_position = (int(self.world_position[0]), int(self.world_position[1]))

    @property
    def position(self):
        """Возвращает позицию в тайлах для обратной совместимости."""
        return self.tile_position 