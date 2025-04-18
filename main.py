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
from config import DEBUG_MODE, GAME_SETTINGS

# Try to import audio module
try:
    import audio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

def main():
    """Main entry point for the game"""
    # Initialize the console
    console = Console()
    
    # Initialize audio if available
    if AUDIO_AVAILABLE and GAME_SETTINGS["music_enabled"]:
        audio.initialize()
        # Play menu theme music
        audio.play_music("menu_theme")
    
    # Display intro and splash screen
    ui.clear_screen()
    ui.display_splash_screen(console)
    
    # Main menu loop
    while True:
        choice = ui.main_menu(console)
        
        if choice == "new_game":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
                # Stop menu music and switch to ambient music
                if GAME_SETTINGS["music_enabled"]:
                    audio.stop_music()
                    # Wait a moment before starting new music
                    time.sleep(0.5)
                    audio.play_music("cyberpunk_ambient")
            
            game = game_engine.GameEngine()
            game.new_game(console)
            game.game_loop(console)
            
            # Return to menu music after game ends
            if AUDIO_AVAILABLE and GAME_SETTINGS["music_enabled"]:
                audio.stop_music()
                time.sleep(0.5)
                audio.play_music("menu_theme")
                
        elif choice == "load_game":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
            
            game = game_engine.GameEngine()
            if game.load_game(console):
                # Stop menu music and switch to ambient music
                if AUDIO_AVAILABLE and GAME_SETTINGS["music_enabled"]:
                    audio.stop_music()
                    time.sleep(0.5)
                    audio.play_music("cyberpunk_ambient")
                
                game.game_loop(console)
                
                # Return to menu music after game ends
                if AUDIO_AVAILABLE and GAME_SETTINGS["music_enabled"]:
                    audio.stop_music()
                    time.sleep(0.5)
                    audio.play_music("menu_theme")
                    
        elif choice == "codex":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
                
            ui.display_codex(console)
            
        elif choice == "options":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
                
            ui.options_menu(console)
            
        elif choice == "credits":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
                
            ui.display_credits(console)
            
        elif choice == "dev_mode":
            # Play special sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_select")
                
            # Show developer tools
            import dev_tools
            
            # Create game engine for developer tools
            game = game_engine.GameEngine()
            
            # Show developer tools menu
            dev_tools.dev_menu(console, game)
            
        elif choice == "quit":
            # Play menu selection sound if available
            if AUDIO_AVAILABLE and GAME_SETTINGS["effects_enabled"]:
                audio.play_sound("menu_back")
                
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
    except EOFError:
        # Handle EOF error (which can occur in non-interactive environments)
        console = Console()
        ui.clear_screen()
        console.print("\n[bold yellow]Input stream ended unexpectedly (EOF). This can happen in non-interactive terminals.[/bold yellow]")
        console.print("[cyan]If you are running this on a Raspberry Pi, try using 'python3 main.py < /dev/tty' to ensure input works correctly.[/cyan]")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        console = Console()
        ui.clear_screen()
        console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
        
        # Always print traceback for better debugging
        import traceback
        console.print("[yellow]===== Debug Traceback =====[/yellow]")
        tb_text = traceback.format_exc()
        console.print(f"[yellow]{tb_text}[/yellow]")
        console.print("[yellow]=========================[/yellow]")
        
        console.print("[cyan]Please report this issue to the developers.[/cyan]")
        sys.exit(1)
