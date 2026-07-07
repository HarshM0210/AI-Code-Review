import os
import json
import hashlib
from typing import Optional

# Determine cache directory relative to this script
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")

def get_code_hash(code: str) -> str:
    """Computes a secure hash for the given code snippet."""
    return hashlib.md5(code.encode('utf-8')).hexdigest()

def get_cached_result(agent_name: str, code_hash: str) -> Optional[dict]:
    """Retrieves cached JSON result for an agent if available."""
    cache_file = os.path.join(CACHE_DIR, f"{agent_name}_{code_hash}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None

def set_cached_result(agent_name: str, code_hash: str, result: dict) -> None:
    """Stores JSON result to cache for a specific agent."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
        
    cache_file = os.path.join(CACHE_DIR, f"{agent_name}_{code_hash}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
    except IOError as e:
        print(f"Warning: Failed to write to cache: {e}")
