import json
import os
from ..core.log import log

class GeneralAI:
    """
    The 'brain' of an army. It loads a personality profile and a knowledge base
    from JSON files and makes decisions based on them.
    """
    def __init__(self, profile_name: str, army):
        self.army = army
        self.profile = self._load_profile(profile_name)
        self.knowledge_base = self._load_knowledge_base()
        self.name = self.profile.get("name", "Unnamed General")
        self.target_army = None
        log.info(f"General {self.name} (Faction: {self.army.faction.name}) has taken command of an army.")

    def _load_profile(self, profile_name: str) -> dict:
        """Loads the general's personality and tactical profile from a JSON file."""
        # Correctly construct the path to the profiles directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(base_dir, 'profiles', f"{profile_name}.json")
        
        log.debug(f"Loading AI profile from: {profile_path}")
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log.error(f"AI profile not found at {profile_path}. AI will be inert.")
            return {}
        except json.JSONDecodeError:
            log.error(f"Failed to decode AI profile at {profile_path}. AI will be inert.")
            return {}

    def _load_knowledge_base(self) -> dict:
        """Loads the knowledge base specified in the general's profile."""
        if not self.profile:
            return {}
            
        knowledge_base_filename = self.profile.get("knowledge_base_path")
        if not knowledge_base_filename:
            log.warning(f"No knowledge_base_path defined for general {self.name}.")
            return {}

        base_dir = os.path.dirname(os.path.abspath(__file__))
        kb_path = os.path.join(base_dir, 'profiles', knowledge_base_filename)
        
        log.debug(f"Loading AI knowledge base from: {kb_path}")
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log.error(f"Knowledge base not found at {kb_path}.")
            return {}
        except json.JSONDecodeError:
            log.error(f"Failed to decode knowledge base at {kb_path}.")
            return {}

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

        # If no target, find the closest enemy army
        if self.target_army is None:
            closest_enemy = None
            min_distance = float('inf')

            for other_army in world.armies:
                if other_army.faction != self.army.faction:
                    distance = self.army.get_distance_to(other_army)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = other_army
            
            if closest_enemy:
                self.target_army = closest_enemy
                log.info(f"General {self.name} has acquired a new target: {self.target_army.faction.name}'s army (ID: {self.target_army.id}).")

        # If we have a valid target, move towards it.
        if self.target_army:
            self.army.set_target(self.target_army)
            # The army will now continuously update its own destination to follow the target.
            # No need to call set_destination or log from the AI's update loop.

    def __repr__(self):
        return f"GeneralAI(name='{self.name}', army_id={self.army.id})" 