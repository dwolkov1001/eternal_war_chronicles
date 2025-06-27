class Tile:
    """
    Класс, представляющий один тайл (клетку) на игровой карте.
    Содержит все характеристики, влияющие на геймплей.
    """
    def __init__(self,
                 tile_type,
                 movement_cost=1,
                 defense_bonus=0,
                 visibility_modifier=1.0,
                 morale_modifier=0,
                 supply_yield=0,
                 attrition_chance=0.0,
                 special_properties=None):
        self.tile_type = tile_type  # например, 'GRASS', 'WATER', 'MOUNTAIN'
        self.movement_cost = movement_cost  # Стоимость передвижения по тайлу
        self.defense_bonus = defense_bonus  # Бонус к защите
        self.visibility_modifier = visibility_modifier # Множитель видимости (1.0 - норма)
        self.morale_modifier = morale_modifier # Бонус/штраф к морали
        self.supply_yield = supply_yield # Количество припасов, которое можно получить
        self.attrition_chance = attrition_chance # Шанс небоевых потерь
        self.special_properties = special_properties if special_properties is not None else [] # Флаги: 'ambush', 'flammable'

        self.is_walkable = movement_cost > 0 