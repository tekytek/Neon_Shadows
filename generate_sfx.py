"""
Generate sound effects for the game
"""
import os
import numpy as np
from scipy.io import wavfile

# Create directories
os.makedirs('sounds/effects', exist_ok=True)

def generate_sound_effects():
    """Generate a set of sound effects for the game"""
    sample_rate = 44100
    
    # Menu select sound
    duration = 0.15
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    select = np.sin(2 * np.pi * np.linspace(1000, 1500, len(t)) * t) * 0.5
    wavfile.write('sounds/effects/menu_select.wav', sample_rate, (select * 32767).astype(np.int16))
    
    # Menu back sound
    duration = 0.15
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    back = np.sin(2 * np.pi * np.linspace(1500, 1000, len(t)) * t) * 0.5
    wavfile.write('sounds/effects/menu_back.wav', sample_rate, (back * 32767).astype(np.int16))
    
    # Combat hit sound
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-10 * t)
    hit = np.sin(2 * np.pi * 150 * t) * envelope * 0.8
    noise = np.random.rand(len(t)) * envelope * 0.3
    hit_sound = hit + noise
    wavfile.write('sounds/effects/combat_hit.wav', sample_rate, (hit_sound * 32767).astype(np.int16))
    
    # Player damage sound
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-8 * t)
    damage = np.sin(2 * np.pi * 200 * t) * envelope * 0.7
    distortion = np.sin(2 * np.pi * 600 * t) * envelope * 0.4
    damage_sound = damage + distortion
    wavfile.write('sounds/effects/player_damage.wav', sample_rate, (damage_sound * 32767).astype(np.int16))
    
    # Item pickup sound
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-5 * t)
    pickup = np.sin(2 * np.pi * np.linspace(500, 1500, len(t)) * t) * envelope * 0.6
    wavfile.write('sounds/effects/item_pickup.wav', sample_rate, (pickup * 32767).astype(np.int16))
    
    # Credits pickup sound
    duration = 0.4
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-5 * t)
    credits = np.sin(2 * np.pi * np.linspace(700, 1200, len(t)) * t) * envelope * 0.6
    wavfile.write('sounds/effects/credits_pickup.wav', sample_rate, (credits * 32767).astype(np.int16))
    
    # Level up sound
    duration = 0.8
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    env1 = np.exp(-4 * (t - 0.1)**2) * 0.7
    env2 = np.exp(-4 * (t - 0.3)**2) * 0.8
    env3 = np.exp(-4 * (t - 0.6)**2) * 0.9
    level_up = (np.sin(2 * np.pi * 500 * t) * env1 + 
                np.sin(2 * np.pi * 700 * t) * env2 + 
                np.sin(2 * np.pi * 1000 * t) * env3)
    wavfile.write('sounds/effects/level_up.wav', sample_rate, (level_up * 32767).astype(np.int16))
    
    # Skill check success sound
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    success = (np.sin(2 * np.pi * 600 * t) * np.exp(-5 * (t - 0.1)**2) * 0.7 +
              np.sin(2 * np.pi * 900 * t) * np.exp(-5 * (t - 0.3)**2) * 0.8)
    wavfile.write('sounds/effects/skill_success.wav', sample_rate, (success * 32767).astype(np.int16))
    
    # Skill check failure sound
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    failure = (np.sin(2 * np.pi * 300 * t) * np.exp(-5 * (t - 0.1)**2) * 0.6 +
              np.sin(2 * np.pi * 200 * t) * np.exp(-5 * (t - 0.3)**2) * 0.7)
    wavfile.write('sounds/effects/skill_failure.wav', sample_rate, (failure * 32767).astype(np.int16))
    
    # Door open sound
    duration = 0.6
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    door = np.random.rand(len(t)) * np.exp(-10 * (t - 0.1)**2) * 0.6
    creak = np.sin(2 * np.pi * np.linspace(300, 100, len(t)) * t) * np.exp(-3 * t) * 0.4
    door_sound = door + creak
    wavfile.write('sounds/effects/door_open.wav', sample_rate, (door_sound * 32767).astype(np.int16))
    
    # Typing sound
    duration = 0.05
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    typing = np.random.rand(len(t)) * np.exp(-20 * t) * 0.3
    wavfile.write('sounds/effects/typing.wav', sample_rate, (typing * 32767).astype(np.int16))
    
    # Shop transaction sound
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    transaction = (np.sin(2 * np.pi * 800 * t) * np.exp(-10 * (t - 0.1)**2) * 0.6 +
                  np.sin(2 * np.pi * 600 * t) * np.exp(-10 * (t - 0.3)**2) * 0.5)
    wavfile.write('sounds/effects/shop_transaction.wav', sample_rate, (transaction * 32767).astype(np.int16))
    
    # Ambient city sounds (shorter versions)
    # Distant traffic
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    traffic = (np.random.rand(len(t)) - 0.5) * 0.2 * np.exp(-0.5 * t) + np.sin(2 * np.pi * 50 * t) * 0.1
    wavfile.write('sounds/effects/city_traffic.wav', sample_rate, (traffic * 32767).astype(np.int16))
    
    # Crowd murmur
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    crowd = (np.random.rand(len(t)) - 0.5) * 0.25 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
    wavfile.write('sounds/effects/city_crowd.wav', sample_rate, (crowd * 32767).astype(np.int16))
    
    # Distant siren
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    siren = np.sin(2 * np.pi * (400 + 50 * np.sin(2 * np.pi * 1 * t)) * t) * 0.2 * np.exp(-0.5 * t)
    wavfile.write('sounds/effects/city_siren.wav', sample_rate, (siren * 32767).astype(np.int16))
    
    print("Generated all sound effects successfully")

if __name__ == "__main__":
    generate_sound_effects()