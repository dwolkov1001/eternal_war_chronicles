from abc import ABC, abstractmethod


class Feature(ABC):
    """Абстрактный базовый класс для всех объектов, которые можно разместить на тайле."""
    pass


class Road(Feature):
    """Объект 'Дорога', который можно разместить на тайле для ускорения передвижения."""
    def __init__(self, road_type='dirt', movement_modifier=0.5):
        self.road_type = road_type  # 'dirt' или 'stone'
        self.movement_modifier = movement_modifier  # Множитель стоимости передвижения
        self.color = (139, 69, 19)  # Коричневый цвет для дороги


class Bridge(Feature):
    """Объект 'Мост', который делает непроходимый тайл (реку) проходимым."""
    pass


class Trap(Feature):
    """Объект 'Ловушка'."""
    def __init__(self, damage=10, detection_chance=0.25):
        self.damage = damage
        self.detection_chance = detection_chance


class Terrain:
    """
    Представляет базовый тип ландшафта тайла.
    """
    def __init__(self, name, movement_cost=1, defense_bonus=0, visibility_modifier=1.0,
                 morale_modifier=0, supply_yield=0, attrition_chance=0.0,
                 special_properties=None, is_walkable=True, color=(128, 128, 128),
                 unit_modifiers=None, key=None): # Серый цвет по умолчанию
        self.name = name
        self.movement_cost = movement_cost
        self.defense_bonus = defense_bonus
        self.visibility_modifier = visibility_modifier
        self.morale_modifier = morale_modifier
        self.supply_yield = supply_yield
        self.attrition_chance = attrition_chance
        self.special_properties = special_properties if special_properties is not None else []
        self.is_walkable = is_walkable
        self.color = color
        self.unit_modifiers = unit_modifiers if unit_modifiers is not None else {}
        self.key = key


class Tile:
    """
    Класс, представляющий один тайл (клетку) на игровой карте.
    Работает как контейнер, состоящий из базового ландшафта и списка объектов.
    """
    def __init__(self, base_terrain: Terrain, features: list[Feature] = None, territory_id: int = None):
        self.base_terrain = base_terrain
        self.features = features if features is not None else []
        self.territory_id = territory_id

    def add_feature(self, feature: Feature):
        """Добавляет объект (улучшение) на тайл."""
        if feature not in self.features:
            self.features.append(feature)

    @property
    def is_walkable(self) -> bool:
        """Определяет, можно ли пройти по тайлу."""
        # Если на тайле есть мост или дорога, он всегда проходим.
        if any(isinstance(f, (Bridge, Road)) for f in self.features):
            return True
        return self.base_terrain.is_walkable

    def get_movement_cost(self) -> float:
        """
        Рассчитывает итоговую стоимость передвижения по тайлу,
        учитывая базовый ландшафт и все объекты на нем.
        """
        cost = self.base_terrain.movement_cost
        
        # Если на тайле есть дорога, она становится основной для расчета стоимости
        road_found = False
        for feature in self.features:
            if isinstance(feature, Road):
                cost *= feature.movement_modifier
                road_found = True

        # Если тайл непроходим (и на нем нет дороги/моста), стоимость - бесконечность
        if not self.is_walkable:
            return float('inf')
        
        # Стоимость не может быть нулевой или отрицательной
        return max(0.1, cost)

    def get_defense_bonus(self) -> int:
        """
        Рассчитывает итоговый бонус к защите.
        В будущем может учитывать постройки.
        """
        return self.base_terrain.defense_bonus

    def get_unit_modifiers(self) -> dict:
        """
        Возвращает словарь модификаторов для юнитов.
        В будущем может учитывать постройки.
        """
        return self.base_terrain.unit_modifiers

    def __repr__(self):
        return f"Tile({self.base_terrain.name}, features={[f.__class__.__name__ for f in self.features]}, territory={self.territory_id})" 