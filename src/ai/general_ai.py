import json
import os
import time
from ..core.log import log
from ..core.pathfinding import find_path
from .profiles.profile_manager import load_profile, load_knowledge_base

class GeneralAI:
    """
    The 'brain' of an army. It loads a personality profile and a knowledge base
    from JSON files and makes decisions based on them.
    """
    def __init__(self, profile_name: str, army):
        self.army = army
        self.profile = load_profile(profile_name)
        self.knowledge_base = load_knowledge_base("base_knowledge")
        self.unreachable_targets = {} # key: target_id, value: timestamp
        self.unreachable_cooldown = 30.0 # seconds
        self.name = self.profile.get("name", "Unnamed General")
        self.target_army = None
        
        # Cooldown for path recalculation to prevent performance issues
        self.path_recalc_cooldown = 2.0  # seconds
        self.last_recalc_time = 0
        
        log.info(f"General {self.name} (Faction: {self.army.faction.name}) has taken command of an army.")

    def update(self, world):
        """
        The main decision-making loop for the AI general.
        Called once per game tick.
        """
        # Simple logic for now: if aggressive, find the nearest enemy and attack.
        aggression = self.profile.get("personality", {}).get("aggression", 0.5)

        if aggression < 0.75:
            return

        # If already in combat, do nothing. The Combat class handles it.
        if self.army.in_combat:
            self.target_army = None # Clear target when combat starts
            return

        # Check if the current target is still valid
        if self.target_army and self.target_army not in world.armies:
            log.info(f"General {self.name}'s target has been defeated or disbanded. Acquiring new target.")
            self.target_army = None

        # Clear expired unreachable targets
        current_time = time.time()
        self.unreachable_targets = {
            target_id: ts 
            for target_id, ts in self.unreachable_targets.items() 
            if current_time - ts < self.unreachable_cooldown
        }

        # If no target, find the closest enemy army
        if self.target_army is None:
            # This logic could be improved with personality traits, e.g.,
            # a 'cautious' general might not attack a stronger army.
            closest_enemy = self._find_closest_enemy(world)
            if closest_enemy:
                self.target_army = closest_enemy
                log.info(f"General {self.name} has acquired a new target: "
                         f"{self.target_army.faction.name}'s army (ID: {self.target_army.id}).")
        
        # If we have a target, recalculate the path periodically.
        if self.target_army and (current_time - self.last_recalc_time > self.path_recalc_cooldown):
            self.last_recalc_time = current_time # Update timer immediately

            # Check if the target is on the unreachable list
            if self.target_army.id in self.unreachable_targets:
                return # Do not attempt to pathfind to a known unreachable target

            start_pos = (int(self.army.x), int(self.army.y))
            goal_pos = (int(self.target_army.x), int(self.target_army.y))

            # For now, AI uses the true world map.
            # In the future, it will use its 'knowledge_map'.
            path = find_path(world.map_data, start_pos, goal_pos)
            
            if path is not None:
                # If the path is empty, it means we are at or next to the target.
                # The army will handle stopping or engaging in combat.
                # If the path has content, set it.
                if path:
                    log.debug(f"General {self.name} recalculated a path to the target.")
                self.army.set_path(path)
            else:
                # path is None, which means it's truly unreachable
                log.warning(f"General {self.name} could not find a path to the target. Caching as unreachable.")
                self.unreachable_targets[self.target_army.id] = time.time()
                self.target_army = None

    def _find_closest_enemy(self, world):
        """Finds the closest enemy army."""
        closest_enemy = None
        min_distance = float('inf')
        for other_army in world.armies:
            if other_army.faction != self.army.faction and other_army.id not in self.unreachable_targets:
                distance = self.army.get_distance_to(other_army)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = other_army
        return closest_enemy

    def __repr__(self):
        return f"GeneralAI(name='{self.name}', army_id={self.army.id})" 