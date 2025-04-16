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
