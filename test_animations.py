"""
Test Animation Effects - Demonstrates the various animation effects
"""
from rich.console import Console
from rich.style import Style
import time
import animations
from config import COLORS

def main():
    """Run a demonstration of all animation effects"""
    console = Console()
    console.clear()
    
    console.print("Cyberpunk Animation Test Suite", style=Style(color=COLORS["primary"], bold=True))
    console.print("================================", style=Style(color=COLORS["secondary"]))
    
    # Test typing effect
    console.print("\n[Testing] Typing Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.typing_effect("This is a demonstration of the typing effect that simulates a hacker typing text on the screen...", console, style=Style(color=COLORS["text"]))
    time.sleep(1)
    
    # Test glitch text
    console.print("\n[Testing] Glitch Text Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.glitch_text("System breach detected! Cybersecurity protocols activated.", console, style=Style(color=COLORS["accent"]))
    time.sleep(1)
    
    # Test neon fade in
    console.print("\n[Testing] Neon Fade-in Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.neon_fade_in("NEON SHADOWS", console, style=Style(color=COLORS["primary"], bold=True))
    time.sleep(1)
    
    # Test cyber scan
    console.print("\n[Testing] Cyber Scan Effect:", style=Style(color=COLORS["secondary"], bold=True))
    cyber_text = """SCANNING NEURAL INTERFACE
DETECTING AUGMENTATIONS
ANALYZING THREAT LEVEL
IDENTIFYING TARGET
AUTHORIZATION CONFIRMED"""
    animations.cyber_scan(cyber_text, console, style=Style(color=COLORS["text"]))
    time.sleep(1)
    
    # Test matrix effect
    console.print("\n[Testing] Matrix Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.matrix_effect("ACCESSING THE MATRIX", console, style=Style(color="#00FF00", bold=True))
    time.sleep(1)
    
    # Test loading bar
    console.print("\n[Testing] Loading Bar:", style=Style(color=COLORS["secondary"], bold=True))
    animations.loading_bar(console, length=30, message="Downloading cyberdeck updates", style=Style(color=COLORS["secondary"]))
    time.sleep(1)
    
    # Test hacker transition
    console.print("\n[Testing] Hacker Transition:", style=Style(color=COLORS["secondary"], bold=True))
    console.print("Executing hacker transition in 2 seconds...", style=Style(color=COLORS["text"]))
    time.sleep(2)
    animations.hacker_transition(console, lines=10)
    console.print("Transition complete!", style=Style(color=COLORS["primary"], bold=True))
    time.sleep(1)
    
    # Test neon border
    console.print("\n[Testing] Neon Border:", style=Style(color=COLORS["secondary"], bold=True))
    neon_text = """ACCESS GRANTED
WELCOME TO NEON SHADOWS
USER LEVEL: NETRUNNER"""
    animations.neon_border(neon_text, console, style=Style(color=COLORS["primary"]))
    time.sleep(1)
    
    # Test cyber flicker
    console.print("\n[Testing] Cyber Flicker:", style=Style(color=COLORS["secondary"], bold=True))
    animations.cyber_flicker("WARNING: UNAUTHORIZED ACCESS", console, style=Style(color=COLORS["accent"], bold=True))
    time.sleep(1)
    
    # Test combination of effects
    console.print("\n[Testing] Combined Effects:", style=Style(color=COLORS["secondary"], bold=True))
    animations.hacker_transition(console, lines=3)
    animations.typing_effect("[SYSTEM] Initializing connection...", console, style=Style(color=COLORS["text"]))
    animations.loading_bar(console, length=20, message="Connecting to server", style=Style(color=COLORS["secondary"]))
    animations.neon_fade_in("CONNECTION ESTABLISHED", console, style=Style(color=COLORS["primary"], bold=True))
    
    # Final message
    console.print("\nAll animation tests complete!", style=Style(color=COLORS["primary"], bold=True))
    console.print("Press Enter to return to the main program...")
    input()

if __name__ == "__main__":
    main()