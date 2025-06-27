import json
import os
from ...core.log import log

def load_profile(profile_name: str) -> dict:
    """Loads a personality and tactical profile from a JSON file."""
    # Correctly construct the path to the profiles directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, f"{profile_name}.json")
    
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

def load_knowledge_base(knowledge_base_name: str) -> dict:
    """Loads a knowledge base from a JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(base_dir, f"{knowledge_base_name}.json")
    
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