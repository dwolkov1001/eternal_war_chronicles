import logging

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

class Combat:
    """
    Управляет состоянием и логикой одного конкретного сражения между двумя армиями.
    """
    def __init__(self, army1, army2):
        self.army1 = army1
        self.army2 = army2
        self.round_number = 0
        self.army1.in_combat = True
        self.army2.in_combat = True
        logger.info(f"Начался бой между {self.army1.faction.name} и {self.army2.faction.name}!")

    def tick(self):
        """
        Симулирует один раунд (тик) боя. Урон рассчитывается и применяется одновременно.
        Возвращает кортеж (статус_боя, победитель, проигравший), где статус: 'ongoing' или 'finished'.
        """
        self.round_number += 1
        logger.info("") # Пустая строка для визуального разделения
        logger.info(f"--- РАУНД {self.round_number} ---")

        if not self.army1.units or not self.army2.units:
            return self._check_for_winner()

        # 1. Запомнить состояние до боя и рассчитать атаку
        army1_initial_count = len(self.army1.units)
        army2_initial_count = len(self.army2.units)
        army1_total_attack = sum(unit.attack for unit in self.army1.units)
        army2_total_attack = sum(unit.attack for unit in self.army2.units)

        logger.info(f"Армия {self.army1.faction.name} ({army1_initial_count} юнитов) атакует с силой {army1_total_attack}.")
        logger.info(f"Армия {self.army2.faction.name} ({army2_initial_count} юнитов) атакует с силой {army2_total_attack}.")

        # 2. Применение урона к каждой армии
        damage_to_army2 = self._apply_damage(self.army2, army1_total_attack)
        damage_to_army1 = self._apply_damage(self.army1, army2_total_attack)

        logger.info(f"Армия {self.army2.faction.name} получает {damage_to_army2} урона.")
        logger.info(f"Армия {self.army1.faction.name} получает {damage_to_army1} урона.")

        # 3. Удаление "убитых" юнитов
        army1_lost_units = self._cleanup_units(self.army1)
        army2_lost_units = self._cleanup_units(self.army2)
        
        # 4. Логирование потерь
        from collections import Counter

        if not army1_lost_units and not army2_lost_units:
            logger.info("No losses this round.")
        else:
            if army1_lost_units:
                lost_counts = Counter(unit.name for unit in army1_lost_units)
                lost_summary = ", ".join([f"{name} (x{count})" for name, count in lost_counts.items()])
                logger.info(f"{self.army1.faction.name}'s army lost {len(army1_lost_units)} units: {lost_summary}")
            
            if army2_lost_units:
                lost_counts = Counter(unit.name for unit in army2_lost_units)
                lost_summary = ", ".join([f"{name} (x{count})" for name, count in lost_counts.items()])
                logger.info(f"{self.army2.faction.name}'s army lost {len(army2_lost_units)} units: {lost_summary}")

        return self._check_for_winner()

    def _apply_damage(self, target_army, total_damage):
        """Равномерно распределяет урон по всем юнитам в армии. Возвращает фактически нанесенный урон."""
        if not target_army.units:
            return 0

        # Учитываем общую защиту армии как снижение входящего урона
        total_defense = sum(unit.defense for unit in target_army.units)
        effective_damage = max(0, total_damage - total_defense)
        
        if effective_damage == 0:
            return 0

        # Распределяем урон, начиная с первого юнита в списке ("первый ряд")
        remaining_damage = effective_damage
        for unit in target_army.units:
            if remaining_damage <= 0:
                break
            damage_to_unit = min(unit.hp, remaining_damage)
            unit.hp -= damage_to_unit
            remaining_damage -= damage_to_unit
        
        return effective_damage


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
            logger.info(f"{self.army1.faction.name}'s army has won the battle!")
            return 'finished', self.army1, self.army2
        elif not army1_alive and army2_alive:
            logger.info(f"{self.army2.faction.name}'s army has won the battle!")
            return 'finished', self.army2, self.army1
        elif not army1_alive and not army2_alive:
            logger.info("Both armies have been destroyed!")
            return 'finished', None, None
        else:
            # If both armies are still alive, the combat is ongoing.
            return 'ongoing', None, None