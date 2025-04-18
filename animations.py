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