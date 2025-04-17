"""
Audio Module - Handles music and sound effects for the game
"""
import os
import threading
import pygame
import time
from pathlib import Path

# Initialize pygame mixer
pygame.mixer.init()

# Create directories if they don't exist
os.makedirs('sounds/music', exist_ok=True)
os.makedirs('sounds/effects', exist_ok=True)

# Global variables
current_music = None
music_volume = 0.5
effects_volume = 0.7
music_enabled = True
effects_enabled = True

# Sound effects cache
sound_effects = {}

def initialize():
    """Initialize the audio system"""
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    # Load settings from config if available
    global music_volume, effects_volume, music_enabled, effects_enabled
    try:
        from config import GAME_SETTINGS
        music_volume = GAME_SETTINGS.get('music_volume', 0.5)
        effects_volume = GAME_SETTINGS.get('effects_volume', 0.7)
        music_enabled = GAME_SETTINGS.get('music_enabled', True)
        effects_enabled = GAME_SETTINGS.get('effects_enabled', True)
    except (ImportError, KeyError):
        # Use defaults if settings aren't available
        pass

def play_music(track_name, loop=True):
    """
    Play background music
    
    Args:
        track_name (str): Name of the music track to play
        loop (bool): Whether to loop the music
    """
    if not music_enabled:
        return
        
    global current_music
    
    # Stop any currently playing music
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    # Full path to the music file
    music_path = os.path.join('sounds', 'music', f"{track_name}.mp3")
    
    # Check if the music file exists
    if not os.path.exists(music_path):
        print(f"Warning: Music file not found: {music_path}")
        return
    
    try:
        # Load and play the music
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1 if loop else 0)
        current_music = track_name
    except Exception as e:
        print(f"Error playing music: {e}")

def stop_music():
    """Stop currently playing music"""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    global current_music
    current_music = None

def play_sound(sound_name):
    """
    Play a sound effect
    
    Args:
        sound_name (str): Name of the sound effect to play
    """
    if not effects_enabled:
        return
        
    # Full path to the sound file
    sound_path = os.path.join('sounds', 'effects', f"{sound_name}.wav")
    
    # Check if the sound file exists
    if not os.path.exists(sound_path):
        print(f"Warning: Sound effect not found: {sound_path}")
        return
    
    try:
        # Cache the sound if not already loaded
        if sound_name not in sound_effects:
            sound_effects[sound_name] = pygame.mixer.Sound(sound_path)
        
        # Play the sound
        sound_effects[sound_name].set_volume(effects_volume)
        sound_effects[sound_name].play()
    except Exception as e:
        print(f"Error playing sound effect: {e}")

def set_music_volume(volume):
    """
    Set the music volume
    
    Args:
        volume (float): Volume level (0.0 to 1.0)
    """
    global music_volume
    music_volume = max(0.0, min(1.0, volume))
    pygame.mixer.music.set_volume(music_volume)
    
    # Update settings
    try:
        from settings import update_setting
        update_setting('music_volume', music_volume)
    except ImportError:
        pass

def set_effects_volume(volume):
    """
    Set the sound effects volume
    
    Args:
        volume (float): Volume level (0.0 to 1.0)
    """
    global effects_volume
    effects_volume = max(0.0, min(1.0, volume))
    
    # Update settings
    try:
        from settings import update_setting
        update_setting('effects_volume', effects_volume)
    except ImportError:
        pass

def toggle_music():
    """Toggle music on/off"""
    global music_enabled
    music_enabled = not music_enabled
    
    if not music_enabled and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    elif music_enabled and current_music:
        play_music(current_music)
    
    # Update settings
    try:
        from settings import update_setting
        update_setting('music_enabled', music_enabled)
    except ImportError:
        pass
    
    return music_enabled

def toggle_effects():
    """Toggle sound effects on/off"""
    global effects_enabled
    effects_enabled = not effects_enabled
    
    # Update settings
    try:
        from settings import update_setting
        update_setting('effects_enabled', effects_enabled)
    except ImportError:
        pass
    
    return effects_enabled

def play_ambient_sounds(ambient_type, interval_min=5, interval_max=15):
    """
    Start a thread that plays ambient sounds at random intervals
    
    Args:
        ambient_type (str): Type of ambient sounds to play (e.g., 'city', 'combat')
        interval_min (int): Minimum interval between sounds in seconds
        interval_max (int): Maximum interval between sounds in seconds
    
    Returns:
        threading.Thread: The ambient sounds thread
    """
    import random
    
    def ambient_thread():
        ambient_sounds = [f for f in os.listdir(os.path.join('sounds', 'effects')) 
                         if f.startswith(f"{ambient_type}_") and f.endswith(".wav")]
        
        while effects_enabled:
            if ambient_sounds:
                # Play a random ambient sound
                sound_file = random.choice(ambient_sounds).replace('.wav', '')
                play_sound(sound_file)
                
                # Wait for a random interval
                time.sleep(random.uniform(interval_min, interval_max))
            else:
                # No ambient sounds found, exit thread
                break
    
    # Start the ambient thread
    thread = threading.Thread(target=ambient_thread, daemon=True)
    thread.start()
    return thread

# Create example sound files for testing if they don't exist
def create_example_sounds():
    """Create example sound files for testing"""
    try:
        from scipy.io import wavfile
        import numpy as np
        
        # Create a simple beep sound
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate a 440 Hz sine wave
        beep = np.sin(2 * np.pi * 440 * t) * 0.5
        
        # Save as a WAV file
        wavfile.write(os.path.join('sounds', 'effects', 'beep.wav'), sample_rate, beep.astype(np.float32))
        
        # Create more sound effects
        # Menu selection sound
        menu_select = np.sin(2 * np.pi * 880 * t) * 0.3
        wavfile.write(os.path.join('sounds', 'effects', 'menu_select.wav'), sample_rate, menu_select.astype(np.float32))
        
        # Combat hit sound
        duration = 0.2
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        hit = np.sin(2 * np.pi * 220 * t) * 0.8 * np.exp(-5 * t)
        wavfile.write(os.path.join('sounds', 'effects', 'combat_hit.wav'), sample_rate, hit.astype(np.float32))
        
        # Item pickup sound
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        pickup = np.sin(2 * np.pi * np.linspace(500, 1200, len(t)) * t) * 0.5
        wavfile.write(os.path.join('sounds', 'effects', 'item_pickup.wav'), sample_rate, pickup.astype(np.float32))
        
        # Ambient city sounds
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        city1 = (np.random.rand(len(t)) - 0.5) * 0.2 + np.sin(2 * np.pi * 50 * t) * 0.1
        wavfile.write(os.path.join('sounds', 'effects', 'city_ambient1.wav'), sample_rate, city1.astype(np.float32))
        
        duration = 1.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        city2 = (np.random.rand(len(t)) - 0.5) * 0.3 + np.sin(2 * np.pi * 30 * t) * 0.1
        wavfile.write(os.path.join('sounds', 'effects', 'city_ambient2.wav'), sample_rate, city2.astype(np.float32))
        
        print("Created example sound effects.")
    except ImportError:
        print("Could not create example sounds: scipy not installed")
        
        # Create empty files as placeholders
        for sound in ['beep', 'menu_select', 'combat_hit', 'item_pickup', 'city_ambient1', 'city_ambient2']:
            open(os.path.join('sounds', 'effects', f'{sound}.wav'), 'w').close()