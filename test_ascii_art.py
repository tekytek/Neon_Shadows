#!/usr/bin/env python3
"""
Test script to display all ASCII art from the game
"""

import time
import sys
from data.ascii_art import ASCII_ART
from rich.console import Console
from rich.text import Text

console = Console()

def main():
    """Main function to display all ASCII art"""
    console.print("\n[bold cyan]Cyberpunk Adventure ASCII Art Test[/bold cyan]")
    console.print("[yellow]Displaying all ASCII art elements...[/yellow]\n")
    
    # Get all art names
    art_names = list(ASCII_ART.keys())
    art_names.sort()  # Sort alphabetically
    
    # Display each art piece
    for name in art_names:
        console.print(f"\n[bold magenta]===== {name.upper()} =====[/bold magenta]")
        # Create a Text object to prevent rich markup interpretation
        art_text = Text(ASCII_ART[name])
        console.print(art_text)
        time.sleep(0.5)  # Pause between displays
    
    console.print("\n[bold green]All ASCII art displayed successfully![/bold green]")

if __name__ == "__main__":
    main()