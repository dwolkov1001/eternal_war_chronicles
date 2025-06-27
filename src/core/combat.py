import logging
from ..misc.enums import Stance, CombatType
from ..game_objects.army import Army
import random

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Предотвращаем передачу сообщений в корневой логгер, чтобы избежать двойного вывода
logger.propagate = False

# Если у логгера нет обработчиков, добавляем новый
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [COMBAT] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

COUNTER_BONUS = 1.5 # Бонус к атаке для контр-юнита

class Combat:
    """
    Управляет состоянием и логикой одного конкретного сражения между двумя армиями.
    """
    def __init__(self, army1, army2, world, combat_type):
        self.army1 = army1
        self.army2 = army2
        self.world = world
        self.combat_type = combat_type
        self.round_number = 0
        self.army1.in_combat = True
        self.army2.in_combat = True
        
        if self.combat_type == CombatType.MEETING_ENGAGEMENT:
            logger.info(f"Начался встречный бой между {self.army1.faction.name} и {self.army2.faction.name}!")
        elif self.combat_type == CombatType.POSITIONAL_ASSAULT:
            # Определяем, кто защитник, для красивого лога
            if army1.stance == Stance.IDLE:
                defender, attacker = army1, army2
            else:
                defender, attacker = army2, army1
            logger.info(f"{attacker.faction.name} атакует позиции {defender.faction.name}!")

    def tick(self):
        """
        Симулирует один раунд (тик) боя. Урон рассчитывается и применяется одновременно.
        Возвращает кортеж (статус_боя, победитель, проигравший), где статус: 'ongoing' или 'finished'.
        """
        self.round_number += 1

        if not self.army1.units or not self.army2.units:
            return self._check_for_winner()

        # 1. Запомнить состояние до боя
        army1_initial_count = len(self.army1.units)
        army2_initial_count = len(self.army2.units)
        
        # 2. Тактический бой: юниты сражаются друг с другом
        # Для простоты, каждый юнит из каждой армии атакует случайного врага
        # В будущем это можно усложнить (линии фронта, цели)
        total_damage_to_army1 = 0
        total_damage_to_army2 = 0

        for unit1 in self.army1.units:
            if not self.army2.units: break
            target_unit = random.choice(self.army2.units)
            damage = self._resolve_unit_attack(unit1, target_unit, self.army2)
            target_unit.hp -= damage
            total_damage_to_army2 += damage
        
        for unit2 in self.army2.units:
            if not self.army1.units: break
            target_unit = random.choice(self.army1.units)
            damage = self._resolve_unit_attack(unit2, target_unit, self.army1)
            target_unit.hp -= damage
            total_damage_to_army1 += damage

        # 3. Удаление "убитых" юнитов
        army1_lost_units = self._cleanup_units(self.army1)
        army2_lost_units = self._cleanup_units(self.army2)
        
        # 4. Формирование сжатого лога
        log_msg = (
            f"РАУНД {self.round_number}: "
            f"{self.army1.faction.name} ({army1_initial_count}) vs {self.army2.faction.name} ({army2_initial_count}) | "
            f"Урон: {total_damage_to_army1}/{total_damage_to_army2} | "
            f"Потери: {len(army1_lost_units)}/{len(army2_lost_units)}"
        )
        
        logger.info(log_msg)

        return self._check_for_winner()

    def _resolve_unit_attack(self, attacker_unit, defender_unit, defender_army):
        """Рассчитывает урон от одного юнита другому, учитывая все бонусы."""
        
        attack_power = attacker_unit.attack
        defense_power = defender_unit.defense

        # 1. Бонус контр-юнита
        if defender_unit.unit_type in attacker_unit.counters:
            attack_power *= COUNTER_BONUS

        # 2. Бонусы и штрафы от ландшафта (только для позиционных боев)
        if self.combat_type == CombatType.POSITIONAL_ASSAULT:
            # Определяем, кто защищается
            defending_army_instance = None
            if self.army1.stance == Stance.IDLE: defending_army_instance = self.army1
            elif self.army2.stance == Stance.IDLE: defending_army_instance = self.army2
            
            if defending_army_instance:
                tile_x, tile_y = int(defending_army_instance.x), int(defending_army_instance.y)
                combat_tile = self.world.map_data[tile_y][tile_x]
                
                # a) Общий бонус защиты от ландшафта
                terrain_defense_bonus = combat_tile.get_defense_bonus()
                defense_share = terrain_defense_bonus / len(defending_army_instance.units) if defending_army_instance.units else 0
                defense_power += defense_share

                # b) Специфичные модификаторы для юнитов
                unit_modifiers = combat_tile.get_unit_modifiers()
                
                # Модификатор для атакующего
                if attacker_unit.unit_type in unit_modifiers:
                    mods = unit_modifiers[attacker_unit.unit_type]
                    attack_power += mods.get("attack_bonus", 0)
                    # Можно добавить и атакующему бонус к защите, если он, например, в лесу
                    defense_power += mods.get("defense_bonus", 0)
                
                # Модификатор для защищающегося
                if defender_unit.unit_type in unit_modifiers:
                    mods = unit_modifiers[defender_unit.unit_type]
                    # У защищающегося свой бонус к атаке (например, контратака)
                    attack_power += mods.get("attack_bonus", 0) 
                    defense_power += mods.get("defense_bonus", 0)

                # 3. Итоговый урон по процентной формуле.
        # Решает проблему "бессмертия" юнитов с высокой защитой.
        if attack_power + defense_power > 0:
            damage = attack_power * (attack_power / (attack_power + defense_power))
        else:
            damage = 0

        # Гарантированный минимальный урон, чтобы предотвратить патовые ситуации.
        # Если юнит вообще атаковал, он должен нанести хотя бы 1 ед. урона.
        if attack_power > 0 and damage < 1:
            damage = 1
            
        return int(round(damage))


    def _cleanup_units(self, army):
        """Удаляет юнитов с hp <= 0 и возвращает список уничтоженных."""
        dead_units = [unit for unit in army.units if unit.hp <= 0]
        army.units = [unit for unit in army.units if unit.hp > 0]
        return dead_units


    def _check_for_winner(self):
        """Checks if the combat is over and returns the status, winner, and loser."""
        army1_alive = bool(self.army1.units)
        army2_alive = bool(self.army2.units)

        if army1_alive and not army2_alive:
            logger.info(f"Армия {self.army1.faction.name} победила, уничтожив врага. Осталось юнитов: {len(self.army1.units)}.")
            return 'finished', self.army1, self.army2
        elif not army1_alive and army2_alive:
            logger.info(f"Армия {self.army2.faction.name} победила, уничтожив врага. Осталось юнитов: {len(self.army2.units)}.")
            return 'finished', self.army2, self.army1
        elif not army1_alive and not army2_alive:
            logger.info("Обе армии были уничтожены в бою!")
            return 'finished', None, None
        else:
            # If both armies are still alive, the combat is ongoing.
            return 'ongoing', None, None