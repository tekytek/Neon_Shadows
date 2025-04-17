"""
Generate synthetic music for testing purposes
"""
import os
import numpy as np
from scipy.io import wavfile

# Create directory for music
os.makedirs('sounds/music', exist_ok=True)

def generate_cyberpunk_music(duration=60, sample_rate=44100, filename='cyberpunk_ambient'):
    """
    Generate a synthetic cyberpunk ambient music track
    
    Args:
        duration (int): Duration in seconds
        sample_rate (int): Sample rate in Hz
        filename (str): Output filename without extension
    """
    print(f"Generating {duration}s of synthetic cyberpunk music...")
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base ambient pad (lowpass filtered noise)
    noise = np.random.rand(len(t)) * 2 - 1
    pad = np.zeros_like(noise)
    
    # Simple lowpass filter
    alpha = 0.01
    for i in range(1, len(noise)):
        pad[i] = alpha * noise[i] + (1 - alpha) * pad[i-1]
    
    # Scale pad
    pad = pad * 0.1
    
    # Create pulsing bass
    bass_freq = 55  # A1
    bass_pulse_rate = 0.5  # pulses per second
    bass = np.sin(2 * np.pi * bass_freq * t) * 0.15 * (0.6 + 0.4 * np.sin(2 * np.pi * bass_pulse_rate * t))
    
    # Create arpeggiator notes (minor scale: root, minor third, fifth, octave)
    arp_base_freq = 220  # A3
    arp_freqs = [arp_base_freq, arp_base_freq * 1.2, arp_base_freq * 1.5, arp_base_freq * 2]
    
    # 16th note arpeggiator at 120 BPM
    bpm = 120
    beats_per_second = bpm / 60
    sixteenth_note = 0.25 / beats_per_second
    
    arp = np.zeros_like(t)
    for i, time in enumerate(t):
        # Determine which 16th note we're on
        note_index = int(time / sixteenth_note) % 16
        
        # Select note from our scale
        arp_note_index = [0, 3, 2, 3, 1, 3, 2, 3, 0, 3, 2, 3, 1, 2, 1, 0][note_index]
        freq = arp_freqs[arp_note_index]
        
        # Calculate amplitude envelope (quick attack, medium decay)
        note_position = (time % sixteenth_note) / sixteenth_note
        envelope = 0
        if note_position < 0.05:  # Attack
            envelope = note_position / 0.05
        else:  # Decay
            envelope = np.exp(-(note_position - 0.05) * 5)
        
        # Add to arpeggiator
        arp[i] = 0.1 * envelope * np.sin(2 * np.pi * freq * time)
    
    # Create distant atmospheric pads
    pad_freq = arp_base_freq / 2
    pad_chords = [
        [1.0, 1.2, 1.5],     # Minor triad
        [1.0, 1.25, 1.5],    # Major triad
        [1.0, 1.2, 1.6],     # Minor with flat 6th
        [1.0, 1.2, 1.5, 1.8]  # Minor 7th
    ]
    
    # Chord progression changes every 4 seconds
    chord_progression = []
    for i in range(int(duration / 4)):
        chord_idx = i % len(pad_chords)
        chord_progression.extend([chord_idx] * int(4 * sample_rate))
    
    # Trim to exact size
    if len(chord_progression) > len(t):
        chord_progression = chord_progression[:len(t)]
    else:
        # Pad with last chord if needed
        chord_progression.extend([chord_progression[-1]] * (len(t) - len(chord_progression)))
    
    # Generate pad sound
    atmospheric_pad = np.zeros_like(t)
    for i, time in enumerate(t):
        chord = pad_chords[chord_progression[i]]
        for note_mult in chord:
            freq = pad_freq * note_mult
            atmospheric_pad[i] += 0.05 * np.sin(2 * np.pi * freq * time)
    
    # Apply slow modulation to the pad
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    atmospheric_pad = atmospheric_pad * modulation
    
    # Glitch effects (random clicks and pops)
    glitch = np.zeros_like(t)
    for i in range(int(duration / 2)):  # glitch every ~2 seconds on average
        glitch_time = np.random.uniform(0, duration)
        glitch_duration = np.random.uniform(0.01, 0.1)  # 10-100ms
        
        start_idx = int(glitch_time * sample_rate)
        end_idx = min(start_idx + int(glitch_duration * sample_rate), len(glitch))
        
        glitch_type = np.random.choice(['click', 'sweep', 'stutter'])
        
        if glitch_type == 'click':
            glitch[start_idx:end_idx] = (np.random.rand(end_idx - start_idx) * 2 - 1) * 0.2
        elif glitch_type == 'sweep':
            sweep_t = np.linspace(0, 1, end_idx - start_idx)
            sweep_freq = np.random.uniform(500, 2000)
            glitch[start_idx:end_idx] = 0.1 * np.sin(2 * np.pi * sweep_freq * sweep_t * sweep_t)
        elif glitch_type == 'stutter':
            if end_idx - start_idx > 100:
                stutter = np.random.rand(10) * 0.2
                stutter_pattern = np.tile(stutter, (end_idx - start_idx) // 10 + 1)[:end_idx - start_idx]
                glitch[start_idx:end_idx] = stutter_pattern
    
    # Mix all elements together
    music = pad + bass + arp + atmospheric_pad + glitch
    
    # Normalize
    music = music / np.max(np.abs(music)) * 0.8
    
    # Convert to 16-bit PCM
    music_int = (music * 32767).astype(np.int16)
    
    # Save as WAV
    output_path = os.path.join('sounds', 'music', f"{filename}.wav")
    wavfile.write(output_path, sample_rate, music_int)
    print(f"Generated music saved to {output_path}")
    
    # Also save a shorter preview version for testing
    if duration > 10:
        preview_path = os.path.join('sounds', 'music', f"{filename}_preview.wav")
        wavfile.write(preview_path, sample_rate, music_int[:int(10 * sample_rate)])
        print(f"Preview version saved to {preview_path}")

def generate_combat_music(duration=45, sample_rate=44100, filename='cyberpunk_combat'):
    """
    Generate a synthetic cyberpunk combat music track
    
    Args:
        duration (int): Duration in seconds
        sample_rate (int): Sample rate in Hz
        filename (str): Output filename without extension
    """
    print(f"Generating {duration}s of synthetic combat music...")
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Faster BPM for combat
    bpm = 150
    beats_per_second = bpm / 60
    
    # Create a driving bassline
    bass_pattern = []
    for i in range(4):  # 4 bar pattern
        if i % 2 == 0:
            bass_pattern.extend([0, 0, 0, 0, 7, 7, 0, 0, 5, 5, 5, 5, 0, 0, 0, 0])
        else:
            bass_pattern.extend([0, 0, 0, 0, 3, 3, 0, 0, 8, 8, 7, 7, 5, 5, 3, 3])
    
    # Base frequency for bass (C2)
    bass_base_freq = 65.41
    
    # Generate the bassline
    bass_note_duration = 1 / (beats_per_second * 4)  # 16th notes
    bass = np.zeros_like(t)
    
    for i, time in enumerate(t):
        pattern_position = int(time / bass_note_duration) % len(bass_pattern)
        note = bass_pattern[pattern_position]
        
        if note > 0:
            # Get frequency for this note
            freq = bass_base_freq * 2 ** (note / 12)
            
            # Calculate amplitude envelope
            note_position = (time % bass_note_duration) / bass_note_duration
            envelope = 0
            if note_position < 0.1:  # Attack
                envelope = note_position / 0.1
            else:  # Decay
                envelope = np.exp(-(note_position - 0.1) * 10)
            
            # Distorted square wave
            raw_wave = np.sign(np.sin(2 * np.pi * freq * time)) 
            bass[i] = 0.25 * envelope * raw_wave
            
            # Add a subtle sub-bass sine wave
            bass[i] += 0.1 * envelope * np.sin(2 * np.pi * freq * 0.5 * time)
    
    # Create aggressive percussion
    kick_pattern = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    snare_pattern = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    hihat_pattern = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    glitch_pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    
    drums = np.zeros_like(t)
    drum_note_duration = 1 / (beats_per_second * 4)  # 16th notes
    
    for i, time in enumerate(t):
        pattern_position = int(time / drum_note_duration) % 16
        
        # Kick drum
        if kick_pattern[pattern_position]:
            # Basic kick: sine wave with exponential decay and frequency drop
            note_position = (time % drum_note_duration) / drum_note_duration
            envelope = np.exp(-note_position * 20)
            freq = 60 * (1 - note_position * 0.5)
            drums[i] += 0.6 * envelope * np.sin(2 * np.pi * freq * time)
        
        # Snare drum
        if snare_pattern[pattern_position]:
            note_position = (time % drum_note_duration) / drum_note_duration
            envelope = np.exp(-note_position * 15)
            # Mix of noise and sine
            noise = np.random.rand() * 2 - 1
            drums[i] += 0.4 * envelope * (0.7 * noise + 0.3 * np.sin(2 * np.pi * 180 * time))
        
        # Hi-hat
        if hihat_pattern[pattern_position]:
            note_position = (time % drum_note_duration) / drum_note_duration
            envelope = np.exp(-note_position * 50)
            # Filtered noise for hi-hat
            noise = np.random.rand() * 2 - 1
            drums[i] += 0.15 * envelope * noise
        
        # Glitch percussion
        if glitch_pattern[pattern_position]:
            note_position = (time % drum_note_duration) / drum_note_duration
            envelope = np.exp(-note_position * 30)
            # Digital artifacts sound
            glitch_sound = np.sin(2 * np.pi * 2000 * time * (1 + np.sin(2 * np.pi * 50 * time)))
            drums[i] += 0.2 * envelope * glitch_sound
    
    # Create tense pad background
    pad_freq = 220  # A3
    pad_chord = [1.0, 1.19, 1.5]  # Minor triad
    
    pad = np.zeros_like(t)
    for freq_mult in pad_chord:
        freq = pad_freq * freq_mult
        # Modulated pad with subtle dissonance
        modulation = 1.0 + 0.001 * np.sin(2 * np.pi * 0.1 * t)
        pad += 0.05 * np.sin(2 * np.pi * freq * t * modulation)
    
    # Add tension with rising tone every few bars
    tension = np.zeros_like(t)
    bar_duration = 4 / beats_per_second
    
    for i in range(0, int(duration / (4 * bar_duration))):
        start_time = i * 4 * bar_duration
        if i % 2 == 1:  # Every other 4-bar section
            for j, time in enumerate(t):
                if start_time <= time < start_time + 2 * bar_duration:
                    # Rising tone
                    local_time = time - start_time
                    progress = local_time / (2 * bar_duration)
                    freq = 500 + 2000 * progress
                    envelope = np.sin(np.pi * progress) * 0.2
                    tension[j] += envelope * np.sin(2 * np.pi * freq * time)
    
    # Mix all elements together
    music = bass + drums + pad + tension
    
    # Normalize
    music = music / np.max(np.abs(music)) * 0.9
    
    # Add slight distortion/compression effect
    music = np.tanh(music * 1.2)
    
    # Convert to 16-bit PCM
    music_int = (music * 32767).astype(np.int16)
    
    # Save as WAV
    output_path = os.path.join('sounds', 'music', f"{filename}.wav")
    wavfile.write(output_path, sample_rate, music_int)
    print(f"Generated combat music saved to {output_path}")
    
    # Also save a shorter preview version for testing
    if duration > 10:
        preview_path = os.path.join('sounds', 'music', f"{filename}_preview.wav")
        wavfile.write(preview_path, sample_rate, music_int[:int(10 * sample_rate)])
        print(f"Preview version saved to {preview_path}")

if __name__ == "__main__":
    # Generate shorter music tracks for testing
    generate_cyberpunk_music(duration=20, filename="cyberpunk_ambient")
    generate_cyberpunk_music(duration=20, filename="cyberpunk_noir")
    generate_combat_music(duration=20, filename="cyberpunk_combat")
    generate_combat_music(duration=20, filename="cyberpunk_boss")
    
    print("Music generation complete!")