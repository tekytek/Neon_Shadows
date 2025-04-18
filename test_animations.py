#!/usr/bin/env python3
"""
Animation Test Module - Runs headless animation tests to verify functionality
"""
import sys
import time
from rich.console import Console
from rich.style import Style
import animations
from config import COLORS

def run_headless_tests():
    """Run minimal animation tests that don't require user input"""
    import os
    console = Console(file=open(os.devnull, 'w'))  # Suppress output for headless mode
    
    # Test typing effect
    animations.typing_effect("Test typing animation", console)
    
    # Test glitch text
    animations.glitch_text("Test glitch animation", console)
    
    # Test loading bar
    animations.loading_bar(console, length=10, message="Testing")
    
    # Test neon fade-in
    animations.neon_fade_in("Test neon fade", console)
    
    # Test cyber scan
    animations.cyber_scan("Test scan", console)
    
    # Return success
    return True

def interactive_test():
    """Run a demo of all animations with visual output"""
    console = Console()
    console.clear()
    
    console.print("Cyberpunk Animation Test Suite", style=Style(color=COLORS["primary"], bold=True))
    console.print("================================", style=Style(color=COLORS["secondary"]))
    
    # Test typing effect
    console.print("\n[Testing] Typing Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.typing_effect("This is a demonstration of the typing effect that simulates a hacker typing text on the screen...", 
                          console, style=Style(color=COLORS["text"]))
    
    # Test glitch text
    console.print("\n[Testing] Glitch Text Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.glitch_text("System breach detected! Cybersecurity protocols activated.", 
                        console, style=Style(color=COLORS["accent"]))
    time.sleep(1)
    
    # Test neon fade-in
    console.print("\n[Testing] Neon Fade-in Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.neon_fade_in("NEON SHADOWS", console, style=Style(color=COLORS["primary"], bold=True))
    time.sleep(1)
    
    # Test cyber scan
    console.print("\n[Testing] Cyber Scan Effect:", style=Style(color=COLORS["secondary"], bold=True))
    scan_text = """SCANNING NEURAL INTERFACE
DETECTING AUGMENTATIONS
ANALYZING THREAT LEVEL
IDENTIFYING TARGET
AUTHORIZATION CONFIRMED"""
    animations.cyber_scan(scan_text, console, style=Style(color=COLORS["secondary"]))
    time.sleep(1)
    
    # Test matrix effect
    console.print("\n[Testing] Matrix Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.matrix_effect("ACCESSING THE MATRIX", console, style=Style(color="#00FF00", bold=True))
    time.sleep(1)
    
    # Test loading bar
    console.print("\n[Testing] Loading Bar:", style=Style(color=COLORS["secondary"], bold=True))
    animations.loading_bar(console, length=20, message="Downloading cyberdeck updates", 
                       style=Style(color=COLORS["primary"]))
    time.sleep(1)
    
    # Test digital rain effect
    console.print("\n[Testing] Digital Rain Effect:", style=Style(color=COLORS["secondary"], bold=True))
    console.print("Displaying digital rain matrix in 2 seconds...", style=Style(color=COLORS["text"]))
    time.sleep(2)
    
    animations.digital_rain(console, duration=2.0, density=0.2)
    
    # Test hacker transition
    console.print("\n[Testing] Hacker Transition:", style=Style(color=COLORS["secondary"], bold=True))
    console.print("Performing hacker transition in 2 seconds...", style=Style(color=COLORS["text"]))
    time.sleep(2)
    
    animations.hacker_transition(console, lines=5)
    
    # Test neon border
    console.print("\n[Testing] Neon Border:", style=Style(color=COLORS["secondary"], bold=True))
    border_text = """   ACCESS GRANTED            
   WELCOME TO NEON SHADOWS   
   USER LEVEL: NETRUNNER     """
    animations.neon_border(border_text, console, style=Style(color=COLORS["primary"]))
    time.sleep(1)
    
    # Test cyber flicker
    console.print("\n[Testing] Cyber Flicker Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.cyber_flicker("CONNECTION ESTABLISHED", console, 
                          style=Style(color=COLORS["accent"], bold=True))
    time.sleep(1)
    
    # Test code decryption
    console.print("\n[Testing] Code Decryption Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.code_decryption("SECURITY CREDENTIALS ACQUIRED", console, style=Style(color="#00FF88", bold=True))
    time.sleep(1)
    
    # Test neural interface
    console.print("\n[Testing] Neural Interface Animation:", style=Style(color=COLORS["secondary"], bold=True))
    animations.neural_interface(console, message="NEURAL LINK ESTABLISHED", 
                             style=Style(color="#00FFFF", bold=True), 
                             duration=2.0)
    time.sleep(1)
    
    # Test heartbeat monitor
    console.print("\n[Testing] Heartbeat Monitor Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.heartbeat_monitor(console, heartbeats=3, bpm=100, flatline=False, 
                              style=Style(color="#FF3366"))
    time.sleep(1)
    
    # Final message
    console.print("\nAll animation tests complete!", style=Style(color=COLORS["primary"], bold=True))
    console.print("Press Enter to return to the main program...")
    input()

if __name__ == "__main__":
    import os
    
    # Check if we should run in headless mode
    if len(sys.argv) > 1 and sys.argv[1] == "--headless":
        # Run minimal tests for verification only
        try:
            success = run_headless_tests()
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"Animation test failed: {str(e)}")
            sys.exit(1)
    else:
        # Run interactive demo
        interactive_test()