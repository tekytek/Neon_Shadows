"""
Generate simpler music tracks for the game (shorter and less complex)
"""
import os
import numpy as np
from scipy.io import wavfile

# Create directory for music
os.makedirs('sounds/music', exist_ok=True)

def generate_simple_music():
    """Generate simple music tracks for testing"""
    sample_rate = 44100
    
    # Ambient track
    print("Generating ambient track...")
    duration = 10
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base pad
    base_freq = 55  # A1
    pad = np.sin(2 * np.pi * base_freq * t) * 0.15
    
    # Add higher chords
    for note in [1.0, 1.5, 2.0]:  # Root, fifth, octave
        freq = base_freq * note
        pad += np.sin(2 * np.pi * freq * t) * 0.1
    
    # Add slight modulation
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t)
    pad = pad * modulation
    
    # Add gentle noise
    noise = (np.random.rand(len(t)) - 0.5) * 0.1
    ambient = pad + noise
    
    # Normalize and save
    ambient = ambient / np.max(np.abs(ambient)) * 0.8
    ambient_int = (ambient * 32767).astype(np.int16)
    wavfile.write('sounds/music/cyberpunk_ambient.wav', sample_rate, ambient_int)
    
    # Combat track
    print("Generating combat track...")
    duration = 10
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base beat at 140 BPM
    bpm = 140
    beat_time = 60 / bpm
    
    # Kick drum pattern
    kick = np.zeros_like(t)
    for i in range(int(duration / beat_time)):
        beat_pos = i * beat_time
        if i % 2 == 0:  # Every other beat
            idx = int(beat_pos * sample_rate)
            if idx < len(kick):
                kick_env = np.exp(-np.linspace(0, 15, int(0.1 * sample_rate)))
                end_idx = min(idx + len(kick_env), len(kick))
                kick_env = kick_env[:end_idx-idx]
                kick[idx:end_idx] = kick_env * 0.8
    
    # Bass line
    bass = np.zeros_like(t)
    bass_freq = 60
    for i, time in enumerate(t):
        # Simple rhythm
        beat_phase = (time % (beat_time * 4)) / (beat_time * 4)
        if beat_phase < 0.25 or (beat_phase > 0.5 and beat_phase < 0.75):
            bass[i] = np.sin(2 * np.pi * bass_freq * time) * 0.4
    
    # Create a simple arpeggio
    arp = np.zeros_like(t)
    arp_notes = [220, 277.2, 329.6, 440]  # A3, D4, E4, A4
    note_duration = beat_time / 4  # 16th notes
    
    for i, time in enumerate(t):
        note_idx = int((time % (beat_time * 2)) / note_duration) % len(arp_notes)
        note_phase = (time % note_duration) / note_duration
        if note_phase < 0.8:  # Note on for 80% of duration
            note_env = np.exp(-note_phase * 5) * 0.3
            arp[i] = np.sin(2 * np.pi * arp_notes[note_idx] * time) * note_env
    
    # Combine and add distortion effect
    combat = kick + bass + arp
    combat = np.tanh(combat * 1.5) * 0.8
    
    # Normalize and save
    combat = combat / np.max(np.abs(combat)) * 0.8
    combat_int = (combat * 32767).astype(np.int16)
    wavfile.write('sounds/music/cyberpunk_combat.wav', sample_rate, combat_int)
    
    # Menu music (simpler)
    print("Generating menu music...")
    duration = 10
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Slow pad
    menu = np.zeros_like(t)
    for freq_mult in [1.0, 1.5, 2.0, 3.0]:  # Simple chord
        freq = 110 * freq_mult  # A2 and harmonics
        menu += np.sin(2 * np.pi * freq * t) * 0.2 * np.exp(-0.1 * t)
    
    # Add slow arpeggio
    menu_notes = [220, 330, 440, 550]
    note_duration = 0.5  # Half-second notes
    
    for i, time in enumerate(t):
        note_idx = int(time / note_duration) % len(menu_notes)
        note_phase = (time % note_duration) / note_duration
        if note_phase < 0.8:  # Note on for 80% of duration
            note_env = np.sin(np.pi * note_phase) * 0.3
            menu[i] += np.sin(2 * np.pi * menu_notes[note_idx] * time) * note_env
    
    # Normalize and save
    menu = menu / np.max(np.abs(menu)) * 0.8
    menu_int = (menu * 32767).astype(np.int16)
    wavfile.write('sounds/music/menu_theme.wav', sample_rate, menu_int)
    
    # Boss combat music (more intense)
    print("Generating boss music...")
    duration = 10
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Faster beat at 160 BPM
    bpm = 160
    beat_time = 60 / bpm
    
    # Aggressive bass
    boss_bass = np.zeros_like(t)
    bass_freq = 50  # Lower bass
    
    for i, time in enumerate(t):
        # Rhythmic pattern
        beat_phase = (time % (beat_time * 2)) / (beat_time * 2)
        
        if beat_phase < 0.2 or (0.5 < beat_phase < 0.6) or (0.75 < beat_phase < 0.85):
            env = np.exp(-(beat_phase % 0.25) * 10) * 0.6
            # Use square wave for more aggressive sound
            boss_bass[i] = np.sign(np.sin(2 * np.pi * bass_freq * time)) * env
    
    # Add distorted lead
    lead = np.zeros_like(t)
    lead_freq = 220
    
    for i, time in enumerate(t):
        # Rising pattern
        if 2 < time < 4 or 6 < time < 8:
            freq_mod = 1 + ((time % 4) / 4) * 0.5  # Pitch rises by 50%
            lead[i] = np.sin(2 * np.pi * lead_freq * freq_mod * time) * 0.4
    
    # Hard-hitting drums
    drums = np.zeros_like(t)
    for i in range(int(duration / beat_time)):
        beat_pos = i * beat_time
        idx = int(beat_pos * sample_rate)
        
        if idx < len(drums):
            # Kick on every beat
            kick_env = np.exp(-np.linspace(0, 20, int(0.1 * sample_rate)))
            end_idx = min(idx + len(kick_env), len(drums))
            kick_env = kick_env[:end_idx-idx]
            drums[idx:end_idx] += kick_env * 0.8
            
            # Snare on off-beats
            if i % 2 == 1:
                snare_env = np.exp(-np.linspace(0, 15, int(0.1 * sample_rate)))
                noise = np.random.rand(len(snare_env)) * 0.5
                end_idx = min(idx + len(snare_env), len(drums))
                snare_env = snare_env[:end_idx-idx]
                noise = noise[:end_idx-idx]
                drums[idx:end_idx] += snare_env * noise
    
    # Combine and add heavy distortion
    boss = boss_bass + lead + drums
    boss = np.tanh(boss * 2.0) * 0.8
    
    # Normalize and save
    boss = boss / np.max(np.abs(boss)) * 0.9
    boss_int = (boss * 32767).astype(np.int16)
    wavfile.write('sounds/music/boss_combat.wav', sample_rate, boss_int)
    
    print("Music generation complete!")

if __name__ == "__main__":
    generate_simple_music()