"""
Центральный справочник всех типов юнитов в игре.
Этот файл содержит базовые характеристики, стоимость и другие параметры
для каждого юнита.
"""

# ==============================================================================
# СЛОВАРЬ ТИПОВ ЮНИТОВ
# ==============================================================================
# Структура:
#   "ID_ЮНИТА": {
#       "name": "Название",
#       "description": "Описание",
#       "base_hp": Базовое здоровье одной единицы,
#       "base_attack": Базовая атака,
#       "base_defense": Базовая защита,
#       "cost": Стоимость найма,
#       "counters": ["ID_ЮНИТА_КОТОРОГО_КОНТРИТ"],
#       "countered_by": ["ID_ЮНИТА_КОТОРЫЙ_КОНТРИТ_ЭТОГО"],
#       # ... другие параметры, например, скорость, дальность атаки и т.д.
#   }
# ==============================================================================

UNIT_TYPES = {
    # --- Пехота ---
    "militia": {
        "name": "Ополченец",
        "description": "Плохо обученный и снаряженный, но дешевый юнит. Эффективен только в большом количестве.",
        "base_hp": 80,
        "base_attack": 4,
        "base_defense": 1,
        "cost": 10,
        "counters": [],
        "countered_by": ["heavy_infantry", "light_cavalry", "archers"]
    },
    "spearman": {
        "name": "Копейщик",
        "description": "Дисциплинированный пехотинец, обученный борьбе с кавалерией.",
        "base_hp": 100,
        "base_attack": 5,
        "base_defense": 3,
        "cost": 25,
        "counters": ["light_cavalry", "heavy_cavalry"],
        "countered_by": ["swordsman", "archer"]
    },
    "swordsman": {
        "name": "Мечник",
        "description": "Универсальный пехотинец, хорош против другой пехоты.",
        "base_hp": 120,
        "base_attack": 6,
        "base_defense": 4,
        "cost": 35,
        "counters": ["spearman", "axeman"],
        "countered_by": ["heavy_cavalry", "crossbowman"]
    },
    "axeman": {
        "name": "Топорщик",
        "description": "Эффективен против тяжелобронированных целей, но сам уязвим.",
        "base_hp": 110,
        "base_attack": 7,
        "base_defense": 2,
        "cost": 40,
        "counters": ["shieldman", "heavy_infantry"],
        "countered_by": ["swordsman", "light_cavalry"]
    },
     "shieldman": {
        "name": "Щитоносец",
        "description": "Тяжелый пехотинец с огромным щитом, отличная защита, но низкая атака.",
        "base_hp": 150,
        "base_attack": 2,
        "base_defense": 8,
        "cost": 50,
        "counters": ["archer", "slinger"],
        "countered_by": ["axeman", "crossbowman"]
    },

    # --- Кавалерия ---
    "light_cavalry": {
        "name": "Легкая кавалерия",
        "description": "Быстрый юнит для разведки и атак на фланги, эффективен против стрелков и легкой пехоты.",
        "base_hp": 90,
        "base_attack": 6,
        "base_defense": 2,
        "cost": 50,
        "counters": ["archer", "slinger", "militia"],
        "countered_by": ["spearman", "heavy_cavalry"]
    },
    "heavy_cavalry": {
        "name": "Тяжелая кавалерия",
        "description": "Мощный удар, способный прорвать строй врага. Уязвимы для копейщиков.",
        "base_hp": 140,
        "base_attack": 8,
        "base_defense": 6,
        "cost": 80,
        "counters": ["swordsman", "light_cavalry"],
        "countered_by": ["spearman", "pikeman"]
    },
    "horse_archer": {
        "name": "Конный лучник",
        "description": "Мобильный стрелок, способный изматывать врага постоянными атаками.",
        "base_hp": 80,
        "base_attack": 5, # Атака считается дальней
        "base_defense": 1,
        "cost": 65,
        "counters": ["heavy_infantry", "spearman"],
        "countered_by": ["light_cavalry", "archer"]
    },
    
    # --- Стрелки ---
    "archer": {
        "name": "Лучник",
        "description": "Стрелок, эффективный на расстоянии, но очень уязвимый в ближнем бою.",
        "base_hp": 70,
        "base_attack": 5, # Атака считается дальней
        "base_defense": 1,
        "cost": 30,
        "counters": ["spearman", "heavy_infantry"],
        "countered_by": ["light_cavalry", "shieldman"]
    },
    "crossbowman": {
        "name": "Арбалетчик",
        "description": "Медленный, но мощный стрелок, способный пробивать тяжелую броню.",
        "base_hp": 85,
        "base_attack": 7, # Атака считается дальней
        "base_defense": 2,
        "cost": 45,
        "counters": ["shieldman", "heavy_cavalry", "swordsman"],
        "countered_by": ["light_cavalry", "militia"]
    },
    "slinger": {
        "name": "Пращник",
        "description": "Дешевый и быстрый стрелок с низкой дальностью и уроном.",
        "base_hp": 60,
        "base_attack": 3, # Атака считается дальней
        "base_defense": 0,
        "cost": 15,
        "counters": [],
        "countered_by": ["shieldman", "light_cavalry"]
    },
} 