#!/usr/bin/env python3
"""
Cyberpunk Adventure - A text-based adventure game with rich narrative and Ollama-powered storylines
"""
import os
import sys
import time
from rich.console import Console
from rich.prompt import Prompt

import game_engine
import ui
from config import DEBUG_MODE

def main():
    """Main entry point for the game"""
    # Initialize the console
    console = Console()
    
    # Display intro and splash screen
    ui.clear_screen()
    ui.display_splash_screen(console)
    
    # Main menu loop
    while True:
        choice = ui.main_menu(console)
        
        if choice == "new_game":
            game = game_engine.GameEngine()
            game.new_game(console)
            game.game_loop(console)
        elif choice == "load_game":
            game = game_engine.GameEngine()
            if game.load_game(console):
                game.game_loop(console)
        elif choice == "options":
            ui.options_menu(console)
        elif choice == "credits":
            ui.display_credits(console)
        elif choice == "quit":
            ui.display_exit_message(console)
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Handle clean exit with CTRL+C
        console = Console()
        ui.clear_screen()
        console.print("\n[bold cyan]Game terminated by user. Exiting...[/bold cyan]")
        sys.exit(0)
    except Exception as e:
        # Handle unexpected errors
        if DEBUG_MODE:
            raise
        console = Console()
        ui.clear_screen()
        console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
        console.print("[cyan]Please report this issue to the developers.[/cyan]")
        sys.exit(1)
