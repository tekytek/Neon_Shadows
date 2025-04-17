"""
Configuration Module - Global settings and constants
"""
import os

# Game information
GAME_TITLE = "NEON SHADOWS"
VERSION = "1.0.0"

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_DIR = os.path.join(BASE_DIR, "saves")

# Colors
COLORS = {
    "primary": "#FF00FF",  # neon pink
    "secondary": "#00FFFF",  # cyan
    "background": "#0A0A0A",  # near black
    "text": "#00FF00",  # matrix green
    "accent": "#FF0000"  # red
}

# Game mechanics
LEVEL_UP_BASE_XP = 100  # Base XP needed for level up
MAX_INVENTORY_ITEMS = 20  # Maximum number of unique items in inventory

# Ollama integration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
USE_OLLAMA = False  # Set to True to use Ollama, False to use fallback content

# Debug mode
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")

# Game settings
GAME_SETTINGS = {
    "difficulty": "normal",  # easy, normal, hard
    "text_speed": "medium",  # slow, medium, fast
    "combat_animations": True,
    
    # Audio settings
    "music_enabled": True,
    "effects_enabled": True,
    "music_volume": 0.5,    # 0.0 to 1.0
    "effects_volume": 0.7,  # 0.0 to 1.0
    
    "auto_save": False,
    "show_hints": True,
    "enable_ollama": USE_OLLAMA
}

# Difficulty settings
DIFFICULTY_SETTINGS = {
    "easy": {
        "player_damage_multiplier": 1.25,
        "enemy_damage_multiplier": 0.75,
        "starting_health_bonus": 5,
        "starting_credits_bonus": 100
    },
    "normal": {
        "player_damage_multiplier": 1.0,
        "enemy_damage_multiplier": 1.0,
        "starting_health_bonus": 0,
        "starting_credits_bonus": 0
    },
    "hard": {
        "player_damage_multiplier": 0.75,
        "enemy_damage_multiplier": 1.25,
        "starting_health_bonus": -2,
        "starting_credits_bonus": -50
    }
}

# Text speed settings (in seconds)
TEXT_SPEED = {
    "slow": 0.05,
    "medium": 0.02,
    "fast": 0.005
}
