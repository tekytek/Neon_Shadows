#!/usr/bin/env python3
"""
Test for Panel objects in typing_effect animation
"""
import time
import sys
import animations
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Set up environment
print("Testing typing_effect with Panel objects...")
console = Console()

# Test 1: Basic string
print("\nTest 1: Basic string")
animations.typing_effect("This is a basic string test", console)
time.sleep(1)

# Test 2: Panel with string
print("\nTest 2: Panel with string content")
panel = Panel("This is a panel with a simple string")
animations.typing_effect(panel, console)
time.sleep(1)

# Test 3: Panel with formatted content
print("\nTest 3: Panel with formatted content")
panel = Panel("[green]This is green[/] and [red]this is red[/]", title="Formatted Panel")
animations.typing_effect(panel, console)
time.sleep(1)

# Test 4: Panel with Text object
print("\nTest 4: Panel with Text object")
text = Text("This is a Text object inside a Panel")
text.stylize("bold magenta")
panel = Panel(text, title="Text Object Panel")
animations.typing_effect(panel, console)
time.sleep(1)

# Test 5: Edge case - Empty panel
print("\nTest 5: Empty panel")
panel = Panel("")
animations.typing_effect(panel, console)
time.sleep(1)

# Test 6: Edge case - Very long content
print("\nTest 6: Very long content")
long_text = "This is a very long text " * 20
panel = Panel(long_text, title="Long Text")
animations.typing_effect(panel, console)

print("\nAll tests completed successfully!")
print("The typing_effect function now correctly handles Panel objects.")