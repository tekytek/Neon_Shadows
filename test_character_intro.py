#!/usr/bin/env python3
"""
Test script for the character introduction animation
"""

import time
import sys
from rich.console import Console

import animations
from animations import character_introduction
import assets

console = Console()

def test_netrunner():
    """Test the NetRunner introduction animation"""
    console.print("\n[bold cyan]Testing NetRunner Introduction...[/bold cyan]")
    character_introduction(console, "NetRunner", "Zero_Cool")
    input("\nPress Enter to continue...")

def test_street_samurai():
    """Test the Street Samurai introduction animation"""
    console.print("\n[bold cyan]Testing Street Samurai Introduction...[/bold cyan]")
    character_introduction(console, "Street Samurai", "Blade")
    input("\nPress Enter to continue...")
    
def test_techie():
    """Test the Techie introduction animation"""
    console.print("\n[bold cyan]Testing Techie Introduction...[/bold cyan]")
    character_introduction(console, "Techie", "Gadget")
    input("\nPress Enter to continue...")
    
def test_fixer():
    """Test the Fixer introduction animation"""
    console.print("\n[bold cyan]Testing Fixer Introduction...[/bold cyan]")
    character_introduction(console, "Fixer", "Shadow")
    input("\nPress Enter to continue...")

def test_animations_disabled():
    """Test character introduction with animations disabled"""
    console.print("\n[bold cyan]Testing with animations disabled...[/bold cyan]")
    animations.ANIMATION_SETTINGS["enabled"] = False
    
    character_introduction(console, "NetRunner", "Zero_Cool")
    input("\nPress Enter to continue to next class...")
    
    character_introduction(console, "Street Samurai", "Blade")
    input("\nPress Enter to continue to next class...")
    
    character_introduction(console, "Techie", "Gadget")
    input("\nPress Enter to continue to next class...")
    
    character_introduction(console, "Fixer", "Shadow")
    input("\nPress Enter to continue...")
    
    # Re-enable animations
    animations.ANIMATION_SETTINGS["enabled"] = True

def main():
    """Main function to test character introduction animations"""
    console.print("[bold magenta]Character Introduction Animation Test[/bold magenta]")
    console.print("[yellow]This test will showcase the character introduction animations for each class.[/yellow]\n")
    
    # Test each character class
    test_netrunner()
    test_street_samurai()
    test_techie()
    test_fixer()
    
    # Test with animations disabled
    test_animations_disabled()
    
    console.print("\n[bold green]All character introduction animations tested successfully![/bold green]")

if __name__ == "__main__":
    main()