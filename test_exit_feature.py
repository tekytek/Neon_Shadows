#!/usr/bin/env python3
"""
Test script to verify the exit functionality of the game
"""
import time
from rich.console import Console

import ui
from animations import cyber_flicker
from rich.panel import Panel

console = Console()
print("Testing exit message functionality...")

# Test direct call to display_exit_message
print("1. Testing display_exit_message...")
ui.display_exit_message(console)
print("Exit message displayed successfully!")

# Test cyber_flicker with Panel specifically
print("\n2. Testing cyber_flicker with Panel directly...")
farewell_text = """
Thank you for playing
NEON SHADOWS

The neon streets will be waiting for your return...
"""
cyber_flicker(Panel(farewell_text, title="GOODBYE"), console)
print("Cyber flicker with Panel completed successfully!")

print("\nAll tests passed successfully!")