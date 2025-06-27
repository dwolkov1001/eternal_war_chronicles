from enum import Enum, auto


class Stance(Enum):
    """
    Определяет тактическое состояние (стойку) отряда.
    """
    # --- Базовые стойки (Этап 6) ---
    IDLE = auto()  # Бездействие, ожидание приказов
    MOVING = auto()  # Движение к цели

    # --- Продвинутые стойки (Этап 9, 12 и далее) ---

    # Боевые
    CHARGE = auto()  # Натиск/Атака с разбега
    SKIRMISH = auto()  # Перестрелка/Стычка
    HOLD_POSITION = auto()  # Держать позицию/Оборона
    SIEGE = auto()  # Осада укреплений
    AMBUSH = auto()  # Засада
    RETREAT = auto()  # Организованное отступление

    # Поддержки и логистики
    SUPPLY = auto()  # Снабжение/Перевозка
    ESCORT = auto()  # Сопровождение
    HEAL = auto()  # Лечение
    GUARD = auto()  # Охрана точки/объекта

    # Стратегические и полевые
    MARCH = auto()  # Форсированный марш
    CAMPING = auto()  # Лагерь/Отдых
    SCOUT = auto()  # Разведка
    WORKING = auto()  # Работа/Строительство
    FORAGE = auto()  # Фуражировка/Поиск припасов
    PATROL = auto()  # Патрулирование


class CombatType(Enum):
    """
    Определяет тип начавшегося боя на основе стоек армий.
    """
    MEETING_ENGAGEMENT = auto()  # Встречный бой
    POSITIONAL_ASSAULT = auto()  # Атака на подготовленную позицию 