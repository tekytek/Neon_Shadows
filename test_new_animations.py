#!/usr/bin/env python3
"""
Test New Cyberpunk Animation Effects - Demonstrates the newly added animation effects
"""
from rich.console import Console
from rich.style import Style
import time
import animations
from config import COLORS

def main():
    """Run a focused demonstration of the new animation effects"""
    console = Console()
    console.clear()
    
    console.print("Cyberpunk New Animations Test Suite", style=Style(color=COLORS["primary"], bold=True))
    console.print("====================================", style=Style(color=COLORS["secondary"]))
    
    # Test Digital Rain animation (Matrix-style)
    console.print("\n[Testing] Digital Rain Animation:", style=Style(color=COLORS["secondary"], bold=True))
    console.print("Initializing digital rain sequence...", style=Style(color=COLORS["text"]))
    time.sleep(1)
    
    # Short duration for testing purposes
    animations.digital_rain(console, duration=2.0, density=0.3, chars="01")
    console.print("Digital rain sequence complete.", style=Style(color=COLORS["primary"]))
    time.sleep(1)
    
    # Test Code Decryption Effect
    console.print("\n[Testing] Code Decryption Effect:", style=Style(color=COLORS["secondary"], bold=True))
    decryption_text = "SECURITY CREDENTIALS ACQUIRED - ACCESS GRANTED TO MAINFRAME"
    animations.code_decryption(decryption_text, console, style=Style(color="#00FF88", bold=True))
    time.sleep(1)
    
    # Test Neural Interface Animation
    console.print("\n[Testing] Neural Interface Animation:", style=Style(color=COLORS["secondary"], bold=True))
    animations.neural_interface(console, message="NEURAL LINK ESTABLISHED", 
                             style=Style(color="#00FFFF", bold=True), 
                             duration=2.0)
    time.sleep(1)
    
    # Test Heartbeat Monitor Effect
    console.print("\n[Testing] Heartbeat Monitor Effect:", style=Style(color=COLORS["secondary"], bold=True))
    animations.heartbeat_monitor(console, heartbeats=3, bpm=100, flatline=False, 
                              style=Style(color="#FF3366"))
    time.sleep(1)
    
    # Test Circuit Pattern Animation
    console.print("\n[Testing] Circuit Pattern Animation:", style=Style(color=COLORS["secondary"], bold=True))
    animations.circuit_pattern(console, duration=2.0, 
                            style=Style(color="#00AAFF"))
    time.sleep(1)
    
    # Test Data Stream Effect
    console.print("\n[Testing] Data Stream Effect:", style=Style(color=COLORS["secondary"], bold=True))
    stream_text = "DATA RETRIEVAL COMPLETE"
    animations.data_stream(stream_text, console, style=Style(color="#00FF88", bold=True))
    time.sleep(1)
    
    # Test Hologram Effect
    console.print("\n[Testing] Hologram Effect:", style=Style(color=COLORS["secondary"], bold=True))
    hologram_text = """HOLOGRAPHIC INTERFACE v3.1
SECURITY CLEARANCE: ALPHA
NEURAL LINK ESTABLISHED
ACCESS GRANTED"""
    
    animations.hologram_effect(hologram_text, console, style=Style(color="#00FFFF", bold=True))
    time.sleep(1)
    
    # Test Data Corruption Effect
    console.print("\n[Testing] Data Corruption Effect:", style=Style(color=COLORS["secondary"], bold=True))
    corruption_text = "WARNING: SECURITY BREACH DETECTED. NEURAL FIREWALL COMPROMISED."
    animations.data_corruption(corruption_text, console, style=Style(color=COLORS["accent"], bold=True), corruption_level=0.4)
    time.sleep(1)
    
    # Demonstrate a full cyberpunk hacking sequence with all new effects
    console.print("\n[Testing] Complete Cyberpunk Hacking Sequence:", style=Style(color=COLORS["secondary"], bold=True))
    console.print("Starting advanced hacking sequence in 2 seconds...", style=Style(color=COLORS["text"]))
    time.sleep(2)
    
    # Step 1: Neural interface connection
    animations.neural_interface(console, message="INITIATING NEURAL LINK", 
                             style=Style(color="#00FFFF", bold=True), 
                             duration=1.5)
    
    # Step 2: Circuit pattern animation showing the system's architecture
    animations.circuit_pattern(console, duration=1.5)
    
    # Step 3: Digital rain as a prelude to intrusion
    animations.digital_rain(console, duration=1.0, density=0.25, chars="01")
    
    # Step 4: Heartbeat monitor showing tension
    animations.heartbeat_monitor(console, heartbeats=3, bpm=120, flatline=False)
    
    # Step 5: Connecting message with typing effect
    animations.typing_effect("[SYSTEM] Establishing connection to corporate database...", 
                          console, style=Style(color="#00FF00"))
    
    # Step 6: Loading sequence
    animations.loading_bar(console, length=20, message="Bypassing security protocols", 
                       style=Style(color=COLORS["secondary"]))
    
    # Step 7: Code decryption of security credentials
    animations.code_decryption("DECRYPTING SECURITY CREDENTIALS", 
                            console, style=Style(color="#00FF88"))
    
    # Step 8: Data stream showing data flow
    animations.data_stream("ACCESSING SECURE DATA", console, 
                        style=Style(color="#00FF88", bold=True))
    
    # Step 9: Data corruption when breaching security
    animations.data_corruption("⚠ ALERT: INTRUSION DETECTED - SECURITY COUNTERMEASURES ACTIVE ⚠", 
                           console, style=Style(color=COLORS["accent"], bold=True), 
                           corruption_level=0.5)
    
    # Step 10: Holographic success message
    success_message = """INTRUSION SUCCESSFUL       
ACCESS LEVEL: ADMINISTRATOR
CORPORATE DATABASE UNLOCKED"""
    animations.hologram_effect(success_message, console, style=Style(color="#00FFFF", bold=True))
    
    # Final message
    console.print("\nAll new animation tests complete!", style=Style(color=COLORS["primary"], bold=True))
    console.print("Press Enter to return to the main program...")
    input()

if __name__ == "__main__":
    main()