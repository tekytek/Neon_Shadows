"""
Animations Module - Provides animated effects for UI transitions
"""
import os
import sys
import time
import random
import shutil
from rich.console import Console
from rich.style import Style

# Globals for animation settings
ANIMATION_SPEED = {
    "slow": 0.05,
    "medium": 0.03,
    "fast": 0.01,
    "instant": 0.001
}

# Animation settings - default to medium speed
ANIMATION_SETTINGS = {
    "enabled": True,
    "speed": "medium"
}

# Neon color palette for cyberpunk effects
NEON_COLORS = [
    "#FF00FF",  # Neon pink
    "#00FFFF",  # Cyan
    "#00FF00",  # Matrix green
    "#FF0000",  # Red
    "#0000FF",  # Blue
    "#FFFF00",  # Yellow
]

def set_animation_speed(speed):
    """Set the animation speed"""
    if speed in ANIMATION_SPEED:
        ANIMATION_SETTINGS["speed"] = speed
    
def toggle_animations():
    """Toggle animations on/off"""
    ANIMATION_SETTINGS["enabled"] = not ANIMATION_SETTINGS["enabled"]
    return ANIMATION_SETTINGS["enabled"]

def get_animation_delay():
    """Get the current animation delay based on settings"""
    if not ANIMATION_SETTINGS["enabled"]:
        return ANIMATION_SPEED["instant"]
    return ANIMATION_SPEED[ANIMATION_SETTINGS["speed"]]

def glitch_text(text, console, style=None, glitch_chars="!@#$%^&*<>?_-+=|~"):
    """Display text with a glitch effect"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    length = len(text)
    
    # First display with glitches
    for i in range(3):  # Do 3 glitch iterations
        # Create a glitched version of text
        glitched = ""
        for char in text:
            # 30% chance to replace with a glitch character
            if char.strip() and random.random() < 0.3:
                glitched += random.choice(glitch_chars)
            else:
                glitched += char
        
        # Print the glitched text
        console.print(glitched, style=style, end="\r")
        time.sleep(delay)
    
    # Final clean version
    console.print(text, style=style)

def cyber_scan(text, console, style=None):
    """Display text with a scanning effect from top to bottom"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    lines = text.split("\n")
    
    # Clear the area first
    for _ in range(len(lines)):
        console.print(" ", end="\n")
    
    # Move cursor back up
    for _ in range(len(lines)):
        sys.stdout.write("\033[F")  # Move cursor up by one line
    
    # Print line by line with scanning effect
    for line in lines:
        console.print(line, style=style)
        time.sleep(delay)

def neon_fade_in(text, console, style=None):
    """Display text with a neon fade-in effect"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    
    # Fade in using different neon colors
    for color in NEON_COLORS:
        console.print(text, style=Style(color=color), end="\r")
        time.sleep(delay)
    
    # Final version with the specified style
    console.print(text, style=style)

def matrix_effect(text, console, style=None):
    """Display text with a Matrix-like falling effect"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    width = shutil.get_terminal_size().columns
    rain_chars = "01"
    
    # Create a "rain" effect before revealing text
    for i in range(min(8, shutil.get_terminal_size().lines // 4)):
        rain = ""
        for j in range(width):
            if random.random() < 0.1:  # 10% chance of a rain drop
                rain += random.choice(rain_chars)
            else:
                rain += " "
        console.print(rain, style=Style(color="#00FF00"), end="\r")  # Matrix green
        time.sleep(delay)
    
    # Final text display
    console.print(text, style=style)

def typing_effect(text, console, style=None):
    """Display text with a typewriter effect"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay() * 2  # Slightly slower for readability
    
    # Type out the text character by character
    for i in range(len(text) + 1):
        console.print(text[:i], style=style, end="\r")
        time.sleep(delay)
    
    # Add a newline at the end
    console.print()

def loading_bar(console, length=20, message="Loading", style=None):
    """Display a cyberpunk-themed loading bar"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(f"{message}... [Complete]", style=style)
        return
    
    delay = get_animation_delay() * 2
    bar_chars = ["░", "▒", "▓", "█"]
    
    for i in range(length + 1):
        percentage = int(i / length * 100)
        progress = "█" * i + "░" * (length - i)
        console.print(f"{message}... [{progress}] {percentage}%", style=style, end="\r")
        time.sleep(delay)
    
    # Complete message
    console.print(f"{message}... [Complete]", style=style)

def hacker_transition(console, lines=5):
    """Create a hacker-style transition effect between UI screens"""
    if not ANIMATION_SETTINGS["enabled"]:
        return
    
    delay = get_animation_delay()
    width = shutil.get_terminal_size().columns
    
    # Clear screen first
    console.clear()
    
    # Generate random hacker-style lines
    hacker_chars = "01!@#$%^&*()_+-={}[]|\\:;'\"<>,.?/~`"
    
    for _ in range(lines):
        line = ""
        line_color = random.choice(NEON_COLORS)
        
        for _ in range(width - 1):
            if random.random() < 0.7:  # 70% chance for a character
                line += random.choice(hacker_chars)
            else:
                line += " "
        
        console.print(line, style=Style(color=line_color))
        time.sleep(delay)
    
    time.sleep(delay * 3)  # Slight pause after transition
    console.clear()  # Clear again for the next screen

def neon_border(text, console, style=None, border_char="█"):
    """Display text with a neon-colored border"""
    if not ANIMATION_SETTINGS["enabled"]:
        # Just print text with style if animations disabled
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    lines = text.split("\n")
    max_length = max(len(line) for line in lines)
    
    # Add some padding to ensure border doesn't touch text
    padded_lines = ["  " + line + " " * (max_length - len(line) + 2) for line in lines]
    
    # Top border
    top_border = border_char * (max_length + 6)
    
    # Create frames with different neon colors
    for color in NEON_COLORS:
        border_style = Style(color=color)
        
        # Print top border
        console.print(top_border, style=border_style)
        
        # Print each line with border
        for line in padded_lines:
            console.print(f"{border_char} {line} {border_char}", style=border_style)
        
        # Print bottom border
        console.print(top_border, style=border_style)
        
        time.sleep(delay)
        
        # Move cursor back to start of output
        for _ in range(len(padded_lines) + 2):
            sys.stdout.write("\033[F")
    
    # Final version with proper styles
    console.print(top_border, style=style)
    for line in padded_lines:
        console.print(f"{border_char} {line} {border_char}", style=style)
    console.print(top_border, style=style)

def cyber_flicker(text, console, style=None, flicker_count=3):
    """Display text with a flickering neon effect"""
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    
    # Flicker effect
    for _ in range(flicker_count):
        # Display blank
        console.print(" " * len(text), end="\r")
        time.sleep(delay)
        
        # Display text
        console.print(text, style=style, end="\r")
        time.sleep(delay * 2)
    
    # Final display
    console.print(text, style=style)

def digital_rain(console, duration=2.0, density=0.2, chars="01"):
    """
    Display a Matrix-style digital rain effect
    
    Args:
        console: Console for output
        duration: Duration in seconds (float)
        density: Density of characters (0.0 to 1.0)
        chars: Characters to use in the rain effect
    """
    if not ANIMATION_SETTINGS["enabled"]:
        return
    
    # If we're running in the main game (not a test), use a simplified version
    # to avoid input/output issues with terminal clearing
    if os.environ.get("GAME_MODE") == "MAIN":
        # Just print a decorative line of matrix text instead
        lines = []
        width = shutil.get_terminal_size().columns
        height = min(5, shutil.get_terminal_size().lines - 2)
        
        for _ in range(height):
            line = ""
            for _ in range(width):
                if random.random() < density * 2:  # Double density for visible effect
                    intensity = random.randint(100, 255)
                    line += f"[#00{intensity:02X}00]{random.choice(chars)}[/]"
                else:
                    line += " "
            lines.append(line)
        
        for line in lines:
            console.print(line)
        
        time.sleep(duration / 2)  # Shorter wait time
        return
    
    # Full effect for tests and other modes
    delay = get_animation_delay() / 2
    
    # Ensure we have valid terminal dimensions to prevent index errors
    try:
        width = max(1, shutil.get_terminal_size().columns)
        height = max(1, min(15, shutil.get_terminal_size().lines - 5))
    except Exception:
        # Fallback to safe values if terminal size detection fails
        width = 80
        height = 10
    
    # Create an empty matrix with proper bounds checking
    matrix = [[" " for _ in range(width)] for _ in range(height)]
    
    # Setup for animation
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Add new raindrops at the top row
            for x in range(width):
                if random.random() < density:
                    matrix[0][x] = random.choice(chars)
            
            # Move all existing drops down
            for y in range(height-1, 0, -1):
                for x in range(width):
                    if matrix[y-1][x] != " " and random.random() < 0.9:
                        matrix[y][x] = random.choice(chars)
                    elif random.random() < 0.05:  # Random fading
                        matrix[y][x] = " "
            
            # Clear the top row
            for x in range(width):
                # 80% chance to clear a cell in top row after moving it down
                if random.random() < 0.8:
                    matrix[0][x] = " "
            
            # Render the current state
            console.clear()
            for y in range(height):
                line = ""
                for x in range(width):
                    char = matrix[y][x]
                    # Add color variance based on depth
                    if char != " ":
                        intensity = max(0, 255 - (y * 18))  # Fade as it goes down
                        line += f"[#00{intensity:02X}00]{char}[/]"
                    else:
                        line += " "
                console.print(line)
            
            time.sleep(delay)
    except (KeyboardInterrupt, EOFError):
        # Handle interruptions gracefully
        pass
    
    try:
        console.clear()
    except:
        pass

def hologram_effect(text, console, style=None):
    """
    Display text with a holographic flickering effect
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
    """
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    lines = text.split("\n")
    max_length = max(len(line) for line in lines)
    
    # Simulate hologram startup
    for i in range(3):
        # Static noise effect
        noise_lines = []
        for line in lines:
            noise = ""
            for char in line:
                if char.strip():
                    if random.random() < 0.5:
                        noise += random.choice("▓▒░")
                    else:
                        noise += char
                else:
                    noise += " "
            noise_lines.append(noise + " " * (max_length - len(line)))
        
        # Display noise with a blue hologram tint
        for noise_line in noise_lines:
            console.print(noise_line, style=Style(color="#00AAFF", bold=False), end="\n")
        
        time.sleep(delay)
        
        # Move cursor back up
        for _ in range(len(lines)):
            sys.stdout.write("\033[F")
    
    # Display with scan lines effect
    for i in range(2):
        for j, line in enumerate(lines):
            # Add scan line effect
            if i % 2 == j % 2:
                # Add a slight brightness variation to alternate lines
                console.print(line, style=Style(color="#00FFFF", bold=True), end="\n")
            else:
                console.print(line, style=Style(color="#00CCFF", bold=False), end="\n")
        
        time.sleep(delay)
        
        # Move cursor back up
        for _ in range(len(lines)):
            sys.stdout.write("\033[F")
    
    # Final display with proper style
    for line in lines:
        console.print(line, style=style, end="\n")

def data_corruption(text, console, style=None, corruption_level=0.3):
    """
    Display text with data corruption artifacts
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
        corruption_level: Level of corruption (0.0 to 1.0)
    """
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay()
    corruption_chars = "█▓▒░▓▒░"
    
    # Start with clean text
    console.print(text, style=style, end="\r")
    time.sleep(delay * 3)
    
    # Apply increasing corruption
    for level in [0.1, 0.3, 0.6, corruption_level]:
        corrupted = ""
        for char in text:
            if char.strip() and random.random() < level:
                corrupted += random.choice(corruption_chars)
            else:
                corrupted += char
        
        console.print(corrupted, style=style, end="\r")
        time.sleep(delay)
    
    # Show mild corruption briefly
    for _ in range(2):
        mild_corrupted = ""
        for char in text:
            if char.strip() and random.random() < 0.1:
                mild_corrupted += random.choice(corruption_chars)
            else:
                mild_corrupted += char
        
        console.print(mild_corrupted, style=style, end="\r")
        time.sleep(delay)
    
    # Final clean display
    console.print(text, style=style)

def code_decryption(text, console, style=None):
    """
    Display text with a code decryption effect, showing characters being deciphered
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
    """
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay() * 1.5
    encrypted_chars = "!@#$%^&*()_+{}|:<>?~`-=[]\\;',./0123456789ABCDEF"
    
    # Create a mask of which characters are fixed (remain static)
    fixed_chars = [False] * len(text)
    
    # Start with all characters randomized
    for i in range(10):  # Do multiple iterations of decryption
        current = ""
        
        for j, char in enumerate(text):
            if fixed_chars[j] or char == " " or char == "\n":
                # This character is already decrypted or is a space/newline
                current += char
            else:
                # 10% chance to decrypt this character on each pass
                if random.random() < 0.1:
                    fixed_chars[j] = True
                    current += char
                else:
                    # Still encrypted, show a random character
                    current += random.choice(encrypted_chars)
        
        # Print the current state
        console.print(current, style=style, end="\r")
        time.sleep(delay)
    
    # Ensure the final state is fully decrypted
    console.print(text, style=style)

def neural_interface(console, message="NEURAL LINK ESTABLISHED", style=None, duration=2.0):
    """
    Display a neural interface animation with brain wave patterns
    
    Args:
        console: Console for output
        message: Message to display at the end
        style: Style to apply to the text
        duration: Duration of the animation in seconds
    """
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(message, style=style)
        return
    
    delay = get_animation_delay() * 0.5
    width = min(shutil.get_terminal_size().columns - 2, 50)
    
    # Brain wave patterns (simplified EEG-like patterns)
    patterns = [
        "  _/\\_   _/\\__/\\_ ",
        " /    \\_/         \\",
        "_/\\__/\\_   _/\\__  ",
        "        \\_/     \\_/",
        "   _/\\__   _/\\_    ",
        "  /     \\_/    \\__/",
    ]
    
    # Start time
    start_time = time.time()
    
    # Display moving brain wave patterns
    while time.time() - start_time < duration:
        for pattern_idx, pattern in enumerate(patterns):
            # Create a slice of the pattern that "moves" from right to left
            offset = int((time.time() - start_time) * 10) % len(pattern)
            display_pattern = pattern[offset:] + pattern[:offset]
            
            # Adjust the pattern to fit the width
            display_pattern = display_pattern * (width // len(display_pattern) + 2)
            display_pattern = display_pattern[:width]
            
            # Color varies by pattern
            colors = ["#00FFFF", "#00CCFF", "#0088FF"]
            color_idx = pattern_idx % len(colors)
            
            # Print the pattern line
            console.print(display_pattern, style=Style(color=colors[color_idx]), end="\r")
            time.sleep(delay)
    
    # Final message
    if message:
        console.print("\n" + message, style=style)

def heartbeat_monitor(console, heartbeats=5, bpm=80, flatline=False, style=None):
    """
    Display a heartbeat monitor animation
    
    Args:
        console: Console for output
        heartbeats: Number of heartbeats to show
        bpm: Beats per minute (affects speed)
        flatline: Whether to end with a flatline effect
        style: Style to apply to the text
    """
    if not ANIMATION_SETTINGS["enabled"]:
        if flatline:
            console.print("_____________________", style=Style(color="#FF0000"))
        return
    
    delay = 60 / (bpm * 20)  # Convert BPM to delay between frames (20 frames per beat)
    width = min(shutil.get_terminal_size().columns - 5, 50)
    
    # Heartbeat pattern frames (simplification of ECG)
    heartbeat = [
        "_____",
        "_____",
        "_____",
        "___,_",
        "__/|_",
        "_/ |_",
        "/  |_",
        "   |\\",
        "   | \\",
        "   |  \\",
        "   |   \\",
        "   |    \\",
        "   |     \\",
        "   |      \\",
        "   |       \\",
        "   |        \\",
        "   |         \\",
        "   |          \\",
        "   |           \\",
        "   |            _",
    ]
    
    # Animate the monitor
    for _ in range(heartbeats):
        for frame in heartbeat:
            # Pad the pattern to fill the width
            display = frame.ljust(width, "_")
            
            # Print with heart rate color
            console.print(display, style=Style(color="#FF3366"), end="\r")
            time.sleep(delay)
    
    # Flatline animation if requested
    if flatline:
        for i in range(10):
            if i % 2 == 0:
                console.print("_" * width, style=Style(color="#FF0000"), end="\r")
            else:
                console.print(" " * width, end="\r")
            time.sleep(delay * 5)
        
        # Final flatline
        console.print("_" * width, style=Style(color="#FF0000"))
    else:
        # End with a blank line
        console.print(" " * width)

def circuit_pattern(console, duration=2.0, style=None):
    """
    Display an animated circuit board pattern
    
    Args:
        console: Console for output
        duration: Duration of the animation in seconds
        style: Style to apply to the circuit
    """
    if not ANIMATION_SETTINGS["enabled"]:
        return
    
    delay = get_animation_delay() * 0.8
    width = min(shutil.get_terminal_size().columns - 2, 60)
    height = 5
    
    # Circuit elements
    h_line = "─"
    v_line = "│"
    corner_tl = "┌"
    corner_tr = "┐"
    corner_bl = "└"
    corner_br = "┘"
    t_down = "┬"
    t_up = "┴"
    t_right = "├"
    t_left = "┤"
    cross = "┼"
    h_dots = "···"
    v_dots = "⁞"
    
    # Circuit components and nodes
    components = ["◉", "◎", "◈", "◇", "▣", "▢", "□", "▫", "◌"]
    
    # Create an empty circuit grid
    circuit = [[" " for _ in range(width)] for _ in range(height)]
    
    # Function to add a horizontal line segment
    def add_h_segment(grid, y, start_x, length):
        for x in range(start_x, min(start_x + length, width)):
            grid[y][x] = h_line
    
    # Function to add a vertical line segment
    def add_v_segment(grid, x, start_y, length):
        for y in range(start_y, min(start_y + length, height)):
            grid[y][x] = v_line
    
    # Set up initial circuit patterns
    # Add some horizontal lines
    for i in range(2):
        y = random.randint(0, height-1)
        start_x = random.randint(0, width//2)
        length = random.randint(width//4, width//2)
        add_h_segment(circuit, y, start_x, length)
    
    # Add some vertical lines
    for i in range(3):
        x = random.randint(0, width-1)
        start_y = random.randint(0, height-2)
        length = random.randint(1, 2)
        add_v_segment(circuit, x, start_y, length)
    
    # Add some components at intersections or ends
    for i in range(4):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        circuit[y][x] = random.choice(components)
    
    # Add some corner pieces
    for i in range(2):
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)
        corner_type = random.choice([corner_tl, corner_tr, corner_bl, corner_br])
        circuit[y][x] = corner_type
    
    # Animation timing
    start_time = time.time()
    
    # Main animation loop
    while time.time() - start_time < duration:
        # Randomly modify the circuit pattern
        for _ in range(3):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            
            # Higher chance to place a component near existing circuits
            if circuit[y][x] != " " or random.random() < 0.3:
                circuit[y][x] = random.choice(components + [h_line, v_line, t_down, t_up, t_right, t_left, cross])
        
        # Render the current state with a moving "pulse" of energy
        pulse_pos = int(((time.time() - start_time) * 15) % width)
        
        for y in range(height):
            line = ""
            for x in range(width):
                char = circuit[y][x]
                
                # Add a color pulse that moves across the circuit
                if circuit[y][x] != " ":
                    distance = abs(x - pulse_pos)
                    if distance < 5:
                        intensity = 255 - (distance * 40)
                        line += f"[#{intensity:02X}{intensity:02X}FF]{char}[/]"
                    else:
                        line += f"[#00AAFF]{char}[/]"
                else:
                    line += " "
            
            console.print(line)
        
        time.sleep(delay)
        
        # Move cursor back to start
        for _ in range(height):
            sys.stdout.write("\033[F")
    
    # Final clean display
    for y in range(height):
        line = ""
        for x in range(width):
            if circuit[y][x] != " ":
                line += f"[#00AAFF]{circuit[y][x]}[/]"
            else:
                line += " "
        console.print(line)

def data_stream(text, console, style=None, stream_chars="10"):
    """
    Display text with a streaming data effect before and after
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
        stream_chars: Characters to use in the data stream
    """
    if not ANIMATION_SETTINGS["enabled"]:
        console.print(text, style=style)
        return
    
    delay = get_animation_delay() * 0.8
    stream_length = 30
    
    # Create streams of data that will appear to flow
    streams = []
    for _ in range(5):
        stream = ""
        for _ in range(stream_length):
            stream += random.choice(stream_chars)
        streams.append(stream)
    
    # Animate data streams flowing before showing text
    for i in range(20):
        # Move each stream and print it
        for s_idx, stream in enumerate(streams):
            # Rotate the stream to create flowing effect
            streams[s_idx] = stream[1:] + stream[0]
            
            # Print with varying intensity
            intensity = 155 + int((s_idx / len(streams)) * 100)  # Vary from 155-255
            color = f"#00{intensity:02X}00"  # Green with varying intensity
            
            console.print(streams[s_idx][:20], style=Style(color=color))
        
        time.sleep(delay)
        
        # Move cursor back to beginning
        for _ in range(len(streams)):
            sys.stdout.write("\033[F")
    
    # Display the actual text
    console.print(text, style=style)
    
    # More streaming data after the text (just a brief flash)
    for i in range(5):
        for s_idx, stream in enumerate(streams):
            # Rotate the stream to create flowing effect
            streams[s_idx] = stream[1:] + stream[0]
            
            # Print with varying intensity
            intensity = 155 + int((s_idx / len(streams)) * 100)  # Vary from 155-255
            color = f"#00{intensity:02X}00"  # Green with varying intensity
            
            console.print(streams[s_idx][:20], style=Style(color=color))
        
        time.sleep(delay)
        
        # Move cursor back to beginning
        for _ in range(len(streams)):
            sys.stdout.write("\033[F")
    
    # Clear the streams
    for _ in range(len(streams)):
        console.print(" " * 20)
        
    # Move cursor back to beginning
    for _ in range(len(streams)):
        sys.stdout.write("\033[F")