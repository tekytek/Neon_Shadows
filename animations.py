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
    """
    Display text with a typewriter effect
    
    Args:
        text: Text to display (string) or Panel object
        console: Console for output
        style: Style to apply to the text
    """
    # Extra safety - ensure we can gracefully handle any input
    try:
        # Import here to prevent circular imports
        from rich.panel import Panel
        from rich.console import Console
        from rich.text import Text
        
        # Skip animation if disabled in settings
        if not ANIMATION_SETTINGS["enabled"]:
            console.print(text, style=style)
            return
        
        delay = get_animation_delay() * 2  # Slightly slower for readability
        
        # Handle Panel objects specially
        if isinstance(text, Panel):
            # Store the panel for final display
            panel = text
            
            # Extract plain text from panel (robust method)
            plain_text = ""
            if hasattr(panel, 'renderable'):
                if isinstance(panel.renderable, str):
                    plain_text = panel.renderable
                elif hasattr(panel.renderable, 'plain'):
                    # Handle Text objects
                    plain_text = panel.renderable.plain
                else:
                    # Best effort to get string representation
                    plain_text = str(panel.renderable)
            
            # Remove any rich formatting markers like [green] or [/]
            # This is a simple way to handle it, not perfect but works for common cases
            import re
            plain_text = re.sub(r'\[[^\]]*\]', '', plain_text)
            
            # If we couldn't get meaningful text, just show the panel without animation
            if not plain_text:
                console.print(panel)
                return
            
            # Type out the extracted text character by character
            temp_console = Console(width=console.width, no_color=True)
            try:
                for i in range(min(len(plain_text) + 1, 500)):  # Limit to 500 chars for safety
                    with temp_console.capture() as capture:
                        temp_console.print(plain_text[:i], end="")
                    captured_text = capture.get()
                    console.print(captured_text, end="\r")
                    time.sleep(delay)
            except Exception:
                # If any issue during animation, just show the panel
                pass
            
            # Now show the full formatted panel
            console.print()  # Clear the line
            console.print(panel)
        else:
            # For normal text strings
            try:
                # Convert to string if it isn't already
                if not isinstance(text, str):
                    text = str(text)
                
                # Remove any Rich markup to prevent showing tags
                import re
                plain_text = re.sub(r'\[[^\]]*\]', '', text)
                
                # Type out the text character by character
                for i in range(min(len(plain_text) + 1, 500)):  # Limit to 500 chars for safety
                    # Create a Text object to ensure no markup interpretation
                    current_text = Text(plain_text[:i])
                    console.print(current_text, style=style, end="\r")
                    time.sleep(delay)
                
                # Print the final version with proper styling
                console.print()
                # Use a clean Text object for final display to avoid markup issues
                final_text = Text(plain_text)
                console.print(final_text, style=style)
            except Exception:
                # Fallback to direct printing if animation fails
                console.print(text, style=style)
    except Exception as e:
        # Ultimate fallback - if anything goes wrong, just print the text
        try:
            console.print(text, style=style)
        except:
            # If even that fails, try basic printing
            try:
                print(text)
            except:
                # If all else fails, at least show something
                print("Error displaying text content")

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
    # Avoiding characters that might be interpreted as Rich markup
    hacker_chars = "01234567890!@#$%^&*()_+-=|\\;,.?/~`"
    
    for _ in range(lines):
        line = ""
        line_color = random.choice(NEON_COLORS)
        
        for _ in range(width - 1):
            if random.random() < 0.7:  # 70% chance for a character
                line += random.choice(hacker_chars)
            else:
                line += " "
        
        # Use a Text object instead of a string to avoid markup interpretation
        from rich.text import Text
        text_obj = Text(line)
        console.print(text_obj, style=Style(color=line_color))
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
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # Create a Text object to prevent rich markup interpretation even when animation is disabled
        text_obj = Text(text)
        console.print(text_obj, style=style)
        return
    
    delay = get_animation_delay()
    lines = text.split("\n")
    max_length = max(len(line) for line in lines)
    
    # Use rich.text.Text objects to prevent special character interpretation
    
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
            # Create a Text object to prevent rich markup interpretation
            text_obj = Text(noise_line)
            console.print(text_obj, style=Style(color="#00AAFF", bold=False), end="\n")
        
        time.sleep(delay)
        
        # Move cursor back up
        for _ in range(len(lines)):
            sys.stdout.write("\033[F")
    
    # Display with scan lines effect
    for i in range(2):
        for j, line in enumerate(lines):
            # Create a Text object for each line to prevent rich markup interpretation
            text_obj = Text(line)
            
            # Add scan line effect
            if i % 2 == j % 2:
                # Add a slight brightness variation to alternate lines
                console.print(text_obj, style=Style(color="#00FFFF", bold=True), end="\n")
            else:
                console.print(text_obj, style=Style(color="#00CCFF", bold=False), end="\n")
        
        time.sleep(delay)
        
        # Move cursor back up
        for _ in range(len(lines)):
            sys.stdout.write("\033[F")
    
    # Final display with proper style
    for line in lines:
        # Create a Text object for final display
        text_obj = Text(line)
        console.print(text_obj, style=style, end="\n")

def data_corruption(text, console, style=None, corruption_level=0.3):
    """
    Display text with data corruption artifacts
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
        corruption_level: Level of corruption (0.0 to 1.0)
    """
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # Create a Text object to prevent rich markup interpretation even when animation is disabled
        text_obj = Text(text)
        console.print(text_obj, style=style)
        return
    
    delay = get_animation_delay()
    corruption_chars = "█▓▒░▓▒░"
    
    # Start with clean text
    text_obj = Text(text)
    console.print(text_obj, style=style, end="\r")
    time.sleep(delay * 3)
    
    # Apply increasing corruption
    for level in [0.1, 0.3, 0.6, corruption_level]:
        corrupted = ""
        for char in text:
            if char.strip() and random.random() < level:
                corrupted += random.choice(corruption_chars)
            else:
                corrupted += char
        
        text_obj = Text(corrupted)
        console.print(text_obj, style=style, end="\r")
        time.sleep(delay)
    
    # Show mild corruption briefly
    for _ in range(2):
        mild_corrupted = ""
        for char in text:
            if char.strip() and random.random() < 0.1:
                mild_corrupted += random.choice(corruption_chars)
            else:
                mild_corrupted += char
        
        text_obj = Text(mild_corrupted)
        console.print(text_obj, style=style, end="\r")
        time.sleep(delay)
    
    # Final clean display
    text_obj = Text(text)
    console.print(text_obj, style=style)

def code_decryption(text, console, style=None):
    """
    Display text with a code decryption effect, showing characters being deciphered
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
    """
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # Create a Text object to prevent rich markup interpretation even when animation is disabled
        text_obj = Text(text)
        console.print(text_obj, style=style)
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
        text_obj = Text(current)
        console.print(text_obj, style=style, end="\r")
        time.sleep(delay)
    
    # Ensure the final state is fully decrypted
    text_obj = Text(text)
    console.print(text_obj, style=style)

def neural_interface(console, message="NEURAL LINK ESTABLISHED", style=None, duration=2.0):
    """
    Display a neural interface animation with brain wave patterns
    
    Args:
        console: Console for output
        message: Message to display at the end
        style: Style to apply to the text
        duration: Duration of the animation in seconds
    """
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # Create a Text object to prevent rich markup interpretation even when animation is disabled
        text_obj = Text(message)
        console.print(text_obj, style=style)
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
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        if flatline:
            # Create a Text object to prevent rich markup interpretation even when animation is disabled
            text_obj = Text("_____________________")
            console.print(text_obj, style=Style(color="#FF0000"))
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
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # When animations are disabled, just display a simple circuit symbol
        circuit_symbol = "◉─◌─┼─□"
        text_obj = Text(circuit_symbol)
        console.print(text_obj, style=Style(color="#00AAFF"))
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
        from rich.text import Text
        
        for y in range(height):
            # Build the line as a list of characters first
            line_chars = []
            line_styles = []
            
            for x in range(width):
                char = circuit[y][x]
                
                # Add a color pulse that moves across the circuit
                if circuit[y][x] != " ":
                    distance = abs(x - pulse_pos)
                    if distance < 5:
                        intensity = 255 - (distance * 40)
                        color = f"#{intensity:02X}{intensity:02X}FF"
                    else:
                        color = "#00AAFF"
                    
                    line_chars.append(char)
                    line_styles.append((len(line_chars) - 1, 1, Style(color=color)))
                else:
                    line_chars.append(" ")
            
            # Create a Text object with styled spans
            line_text = Text("".join(line_chars))
            for start, length, style in line_styles:
                line_text.stylize(style, start, start + length)
                
            console.print(line_text)
        
        time.sleep(delay)
        
        # Move cursor back to start
        for _ in range(height):
            sys.stdout.write("\033[F")
    
    # Final clean display
    from rich.text import Text
    
    for y in range(height):
        # Create a line manually without rich markup
        line_chars = []
        for x in range(width):
            if circuit[y][x] != " ":
                line_chars.append(circuit[y][x])
            else:
                line_chars.append(" ")
                
        # Create a Text object to prevent markup interpretation
        line_text = Text("".join(line_chars))
        console.print(line_text, style=Style(color="#00AAFF"))

def character_introduction(console, char_class, name=None):
    """
    Display an engaging character introduction animation
    
    Args:
        console: Console for output
        char_class: Character class (NetRunner, Street Samurai, Techie, Fixer)
        name: Character name (optional)
    """
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    from rich.panel import Panel
    from rich.style import Style
    import assets
    
    if not ANIMATION_SETTINGS["enabled"]:
        # When animation is disabled, just display character info
        title = f"Character: {name if name else char_class}"
        content = f"Class: {char_class}\n\n"
        
        if char_class.lower() == "netrunner":
            content += "Specialist in hacking and digital infiltration."
        elif char_class.lower() == "street samurai":
            content += "Augmented fighter with unmatched combat skills."
        elif char_class.lower() == "techie":
            content += "Expert in technology repair and improvised gadgets."
        elif char_class.lower() == "fixer":
            content += "Connected dealer, negotiator, and information broker."
            
        # Create a Text object to prevent markup interpretation
        text_obj = Text(content)
        panel = Panel(text_obj, title=title)
        console.print(panel)
        return
    
    # First display the game logo
    title_art = assets.get_ascii_art('title')
    if title_art:
        # Display the logo with a digital rain effect first
        digital_rain(console, duration=1.0, density=0.2)
        
        # Create a Text object to prevent markup interpretation
        title_text = Text(title_art)
        console.print(title_text, style=Style(color="#FF00FF"))  # Neon pink for logo
        time.sleep(1.0)
        
        # Clear the screen for the character intro
        console.clear()
    
    # Get character ASCII art
    art_name = None
    if char_class.lower() == "netrunner":
        art_name = "netrunner"
    elif char_class.lower() == "street samurai":
        art_name = "street_samurai"
    elif char_class.lower() == "techie":
        art_name = "techie"
    elif char_class.lower() == "fixer":
        art_name = "fixer"
    
    # Fallback to hacker if no specific art found
    char_art = assets.get_ascii_art(art_name if art_name else "hacker")
    
    # Use neural interface animation as intro
    neural_interface(console, message="NEURAL LINK ESTABLISHED", duration=1.5)
    
    # Glitchy scanning effect
    console.print()
    glitch_text("SCANNING NEURAL IDENTITY...", console, style=Style(color="#00FFAA"))
    time.sleep(0.5)
    
    # Character class reveal with typing effect
    console.print()
    # Don't use Rich markup inside typing_effect - create a non-markup version instead
    typing_effect(f"CLASS IDENTIFIED: {char_class.upper()}", console, style=Style(color="#FF00AA", bold=True))
    time.sleep(0.5)
    
    # Name reveal if provided
    if name:
        console.print()
        typing_effect(f"IDENTITY: {name.upper()}", console, style=Style(color="#00AAFF", bold=True))
        time.sleep(0.5)
    
    # Show character art with a neon effect
    console.print()
    if char_art:
        # Create a Text object to prevent markup interpretation
        char_art_text = Text(char_art)
        console.print(char_art_text, style=Style(color="#00FFAA"))
    
    # Class description with typing effect
    console.print()
    description = ""
    if char_class.lower() == "netrunner":
        description = "Specialist in hacking and digital infiltration. Exceptional at bypassing security and manipulating data."
    elif char_class.lower() == "street samurai":
        description = "Augmented fighter with unmatched combat skills. Cybernetic enhancements provide superior strength and reflexes."
    elif char_class.lower() == "techie":
        description = "Expert in technology repair and improvised gadgets. Can create useful tools from scavenged parts."
    elif char_class.lower() == "fixer":
        description = "Connected dealer, negotiator, and information broker. Knows who to talk to and how to make deals."
    
    typing_effect(description, console, style=Style(color="#AAAAFF"))
    
    # Final flourish
    console.print()
    circuit_pattern(console, duration=1.0)
    console.print()
    # Create a Text object to prevent markup interpretation
    final_text = Text("READY FOR OPERATION. GOOD LUCK, RUNNER.")
    typing_effect(final_text, console, style=Style(color="#00FFAA"))
    console.print()

def data_stream(text, console, style=None, stream_chars="10"):
    """
    Display text with a streaming data effect before and after
    
    Args:
        text: Text to display
        console: Console for output
        style: Style to apply to the text
        stream_chars: Characters to use in the data stream
    """
    # Import at the start to ensure it's available for all code paths
    from rich.text import Text
    
    if not ANIMATION_SETTINGS["enabled"]:
        # Create a Text object to prevent rich markup interpretation even when animation is disabled
        text_obj = Text(text)
        console.print(text_obj, style=style)
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
            
            # Create a Text object to prevent rich markup interpretation
            text_obj = Text(streams[s_idx][:20])
            console.print(text_obj, style=Style(color=color))
        
        time.sleep(delay)
        
        # Move cursor back to beginning
        for _ in range(len(streams)):
            sys.stdout.write("\033[F")
    
    # Display the actual text
    # Create a Text object for the main text to prevent rich markup interpretation
    text_obj = Text(text)
    console.print(text_obj, style=style)
    
    # More streaming data after the text (just a brief flash)
    for i in range(5):
        for s_idx, stream in enumerate(streams):
            # Rotate the stream to create flowing effect
            streams[s_idx] = stream[1:] + stream[0]
            
            # Print with varying intensity
            intensity = 155 + int((s_idx / len(streams)) * 100)  # Vary from 155-255
            color = f"#00{intensity:02X}00"  # Green with varying intensity
            
            # Create a Text object to prevent rich markup interpretation
            text_obj = Text(streams[s_idx][:20])
            console.print(text_obj, style=Style(color=color))
        
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