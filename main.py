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
    # Check for input stream issues early
    try:
        if not sys.stdin.isatty():
            print("WARNING: Running in a non-interactive terminal environment.")
            print("If you experience input issues, try running with: python3 main.py < /dev/tty")
    except Exception:
        # This check itself might fail in certain environments, so we just continue
        pass
    
    # Initialize the console with settings optimized for terminal compatibility
    # Set highlight=False to prevent formatting tags from appearing in some terminals
    console = Console(highlight=False)
    
    # Look for Raspberry Pi environment
    is_raspberry_pi = False
    try:
        # Check for Raspberry Pi-specific files
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    is_raspberry_pi = True
                    console.print("Raspberry Pi detected. Using compatible input mode.", style="yellow")
    except Exception:
        pass  # Continue without detection
        
    # Initialize audio if available
    try:
        if AUDIO_AVAILABLE and GAME_SETTINGS["music_enabled"]:
            audio.initialize()
            # Play menu theme music
            audio.play_music("menu_theme")
    except Exception as e:
        console.print(f"Audio initialization warning: {str(e)}", style="yellow")
        console.print("Continuing without audio...", style="yellow")
    
    # Display intro and splash screen
    ui.clear_screen()
    ui.display_splash_screen(console)
    
    # Flag to track first menu display
    first_menu_display = True
    
    # Main menu loop
    while True:
        choice = ui.main_menu(console, skip_title=not first_menu_display)
        
        # After first display, we don't need to show the title again
        if first_menu_display:
            first_menu_display = False
        
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
        console = Console(highlight=False)  # Disable highlighting to prevent formatting issues
        ui.clear_screen()
        console.print("\nGame terminated by user. Exiting...", style="bold cyan")
        sys.exit(0)
    except EOFError:
        # Handle EOF error (which can occur in non-interactive environments)
        console = Console(highlight=False)  # Disable highlighting to prevent formatting issues
        ui.clear_screen()
        console.print("\nInput stream ended unexpectedly (EOF). This can happen in non-interactive terminals.", style="bold yellow")
        console.print("If you are running this on a Raspberry Pi, try using 'python3 main.py < /dev/tty' to ensure input works correctly.", style="cyan")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        console = Console(highlight=False)  # Disable highlighting to prevent formatting issues
        ui.clear_screen()
        console.print(f"\nAn error occurred: {str(e)}", style="bold red")
        
        # Always print traceback for better debugging
        import traceback
        console.print("===== Debug Traceback =====", style="yellow")
        tb_text = traceback.format_exc()
        console.print(tb_text, style="yellow")
        console.print("=========================", style="yellow")
        
        console.print("Please report this issue to the developers.", style="cyan")
        sys.exit(1)
