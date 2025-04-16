"""
Save System Module - Handles saving and loading game progress
"""
import os
import json
import time
import glob
from datetime import datetime

from config import SAVE_DIR

def ensure_save_directory():
    """Ensure the save directory exists"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_files():
    """Get a list of all save files"""
    ensure_save_directory()
    save_pattern = os.path.join(SAVE_DIR, "*.json")
    return glob.glob(save_pattern)

def get_save_metadata(save_file):
    """Get metadata from a save file"""
    try:
        with open(save_file, 'r') as f:
            save_data = json.load(f)
            return save_data.get('metadata', {})
    except Exception:
        return None

def save_game(save_name, save_data):
    """Save the game to a file"""
    ensure_save_directory()
    
    # Sanitize the save name
    save_name = save_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    save_path = os.path.join(SAVE_DIR, f"{save_name}.json")
    
    try:
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game: {str(e)}")
        return False

def load_game(save_file):
    """Load a game from a save file"""
    try:
        with open(save_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading game: {str(e)}")
        raise
