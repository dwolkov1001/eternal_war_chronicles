from ..game_objects.tile import Terrain

# ==============================================================================
# СПРАВОЧНИК ТИПОВ ЛАНДШАФТА
# ==============================================================================
# Здесь мы определяем все возможные типы ландшафтов в игре.
# MapGenerator будет использовать этот словарь для создания мира.
# ------------------------------------------------------------------------------
# Параметры:
# - name: Имя типа (для отладки)
# - movement_cost: Базовая стоимость передвижения (1.0 = норма)
# - defense_bonus: Бонус к защите для юнитов на этом тайле
# - is_walkable: Можно ли по нему ходить
# ==============================================================================

TERRAIN_TYPES = {
    # --- Базовые и непроходимые ---
    "GRASSLAND": Terrain(name="Grassland", movement_cost=1.0, defense_bonus=0, is_walkable=True, color=(52, 140, 49), key="GRASSLAND"),
    "WATER": Terrain(name="Water", is_walkable=False, color=(64, 164, 223), key="WATER"),
    "DEEP_WATER": Terrain(name="Deep Water", is_walkable=False, color=(40, 120, 180), key="DEEP_WATER"),
    "MOUNTAIN_PEAK": Terrain(name="Mountain Peak", is_walkable=False, color=(200, 200, 200), key="MOUNTAIN_PEAK"),

    # --- Равнины ---
    "PLAINS": Terrain(name="Plains", movement_cost=1.0, defense_bonus=1, color=(148, 178, 91),
                    unit_modifiers={"light_cavalry": {"attack_bonus": 1, "movement_bonus": 0.1},
                                    "heavy_cavalry": {"attack_bonus": 2, "movement_bonus": 0.1}}, key="PLAINS"),
    "WASTELAND": Terrain(name="Wasteland", movement_cost=1.2, defense_bonus=0, color=(210, 180, 140),
                       unit_modifiers={"archer": {"attack_bonus": -1}, "crossbowman": {"attack_bonus": -1}}, key="WASTELAND"),
    "MEADOW": Terrain(name="Meadow", movement_cost=1.0, defense_bonus=0, color=(118, 158, 71), key="MEADOW"),
    "STEPPE": Terrain(name="Steppe", movement_cost=1.1, defense_bonus=2, color=(188, 188, 131),
                    unit_modifiers={"light_cavalry": {"attack_bonus": 2}, "horse_archer": {"attack_bonus": 1}}, key="STEPPE"),

    # --- Леса ---
    "CONIFEROUS_FOREST": Terrain(name="Coniferous Forest", movement_cost=2.0, defense_bonus=5, color=(0, 100, 0),
                               unit_modifiers={"light_cavalry": {"attack_bonus": -2, "defense_bonus": -1},
                                               "heavy_cavalry": {"attack_bonus": -5, "defense_bonus": -3}}, key="CONIFEROUS_FOREST"),
    "DECIDUOUS_FOREST": Terrain(name="Deciduous Forest", movement_cost=2.5, defense_bonus=7, color=(34, 139, 34),
                                unit_modifiers={"light_cavalry": {"attack_bonus": -4, "defense_bonus": -2},
                                                "heavy_cavalry": {"attack_bonus": -7, "defense_bonus": -5},
                                                "horse_archer": {"attack_bonus": -3}}, key="DECIDUOUS_FOREST"),
    "DARK_FOREST": Terrain(name="Dark Forest", movement_cost=3.5, defense_bonus=10, color=(0, 51, 0), key="DARK_FOREST"),
    "WOODLAND": Terrain(name="Woodland", movement_cost=1.2, defense_bonus=3, color=(85, 107, 47),
                      unit_modifiers={"archer": {"attack_bonus": 1, "defense_bonus": 2},
                                      "spearman": {"defense_bonus": 1}}, key="WOODLAND"),

    # --- Горы ---
    "HILLS": Terrain(name="Hills", movement_cost=3.0, defense_bonus=8, color=(139, 137, 112),
                   unit_modifiers={"archer": {"attack_bonus": 3},
                                   "crossbowman": {"attack_bonus": 2},
                                   "slinger": {"attack_bonus": 2}}, key="HILLS"),
    "ROCKS": Terrain(name="Rocks", movement_cost=4.0, defense_bonus=12, color=(105, 105, 105),
                   unit_modifiers={"heavy_infantry": {"defense_bonus": 3}, "shieldman": {"defense_bonus": 5}}, key="ROCKS"),
    "GORGE": Terrain(name="Gorge", movement_cost=1.4, defense_bonus=3, color=(160, 141, 106), key="GORGE"),
    "PLATEAU": Terrain(name="Plateau", movement_cost=1.8, defense_bonus=10, color=(189, 169, 124),
                     unit_modifiers={"archer": {"attack_bonus": 2}, "crossbowman": {"attack_bonus": 3}}, key="PLATEAU"),

    # --- Водоемы и болота ---
    "SHALLOW_RIVER": Terrain(name="Shallow River", movement_cost=3.5, defense_bonus=-5, color=(100, 180, 230),
                           unit_modifiers={"heavy_infantry": {"defense_bonus": -5}, "heavy_cavalry": {"defense_bonus": -7}}, key="SHALLOW_RIVER"),
    "SWAMP": Terrain(name="Swamp", movement_cost=5.0, defense_bonus=1, color=(82, 95, 83),
                   unit_modifiers={"heavy_infantry": {"attack_bonus": -3, "defense_bonus": -5},
                                   "heavy_cavalry": {"attack_bonus": -5, "defense_bonus": -8},
                                   "light_infantry": {"defense_bonus": 1}}, key="SWAMP"),

    # --- Городские территории (как базовый ландшафт) ---
    "VILLAGE": Terrain(name="Village", movement_cost=1.0, defense_bonus=10, color=(222, 184, 135), key="VILLAGE"),
    "TOWN": Terrain(name="Town", movement_cost=1.0, defense_bonus=15, color=(192, 192, 192), key="TOWN"),
    "CASTLE": Terrain(name="Castle", movement_cost=1.0, defense_bonus=25, color=(128, 128, 128), key="CASTLE"),
    "RUINS": Terrain(name="Ruins", movement_cost=1.3, defense_bonus=8, color=(112, 128, 144),
                   unit_modifiers={"spearman": {"defense_bonus": 3}, "archer": {"defense_bonus": 2}}, key="RUINS"),

    # --- Дороги (для генератора) ---
    "ROAD": Terrain(name="Road", movement_cost=0.4, defense_bonus=0, key="ROAD"),
} 