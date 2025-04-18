"""
Settings Module - Handles loading and saving game settings
"""
import os
import json
import importlib
from config import BASE_DIR, GAME_SETTINGS

# Settings file path
SETTINGS_FILE = os.path.join(BASE_DIR, "game_settings.json")

def load_settings():
    """Load game settings from file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                loaded_settings = json.load(f)
                
                # Update global settings
                for key, value in loaded_settings.items():
                    if key in GAME_SETTINGS:
                        GAME_SETTINGS[key] = value
                
                # If we loaded settings, update the USE_OLLAMA value in config
                if "enable_ollama" in loaded_settings:
                    # We need to update the USE_OLLAMA in config.py
                    import config
                    config.USE_OLLAMA = loaded_settings["enable_ollama"]
                
                return True
        return False
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        return False

def save_settings():
    """Save current game settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(GAME_SETTINGS, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        return False

def update_setting(key, value):
    """Update a specific game setting"""
    if key in GAME_SETTINGS:
        GAME_SETTINGS[key] = value
        
        # If we're updating enable_ollama, we need to update the config module
        if key == "enable_ollama":
            import config
            config.USE_OLLAMA = value
            
        return True
    return False

def get_setting(key):
    """Get a specific game setting"""
    return GAME_SETTINGS.get(key)

def reset_to_defaults():
    """Reset settings to default values"""
    # Import the original default value
    import config
    original_ollama_setting = config.USE_OLLAMA
    
    # Reset to defaults
    GAME_SETTINGS["difficulty"] = "normal"
    GAME_SETTINGS["text_speed"] = "medium"
    GAME_SETTINGS["combat_animations"] = True
    
    # Audio settings
    GAME_SETTINGS["music_enabled"] = True
    GAME_SETTINGS["effects_enabled"] = True
    GAME_SETTINGS["music_volume"] = 0.5
    GAME_SETTINGS["effects_volume"] = 0.7
    
    # UI Animation settings
    GAME_SETTINGS["ui_animations_enabled"] = True
    GAME_SETTINGS["ui_animation_speed"] = "medium"
    
    GAME_SETTINGS["auto_save"] = False
    GAME_SETTINGS["show_hints"] = True
    GAME_SETTINGS["enable_ollama"] = original_ollama_setting
    
    # Save changes
    save_settings()
    
    return True

# Initialize settings on import
load_settings()