"""
UI Module - Handles display and user interface
"""
import os
import sys
import time
import platform
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.prompt import Prompt
from rich.columns import Columns
from rich.style import Style

import assets
from config import GAME_TITLE, VERSION, COLORS

def clear_screen():
    """Clear the terminal screen"""
    # Check if Windows or Unix
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def typewriter_print(console, text, speed=None):
    """Print text with a typewriter effect based on settings"""
    from config import GAME_SETTINGS, TEXT_SPEED
    
    # If no speed specified, use the setting from config
    if speed is None:
        speed_setting = GAME_SETTINGS.get("text_speed", "medium")
        speed = TEXT_SPEED.get(speed_setting, 0.02)
    
    # If speed is 0 or very small, just print normally
    if speed < 0.001:
        console.print(text)
        return
    
    # Apply typewriter effect
    for char in text:
        console.print(char, end="")
        time.sleep(speed)
    
    # Add newline at the end
    console.print("")

def display_splash_screen(console):
    """Display the game's splash screen"""
    clear_screen()
    
    # Display ASCII art title
    console.print(assets.get_ascii_art('title'), style=Style(color=COLORS['primary']))
    
    # Display version and credits
    console.print(f"[{COLORS['secondary']}]Version {VERSION}[/{COLORS['secondary']}]")
    console.print(f"[{COLORS['text']}]A text-based cyberpunk adventure[/{COLORS['text']}]")
    
    # Bottom line
    console.print("\n" + "=" * 60, style=Style(color=COLORS['primary']))
    console.print(f"[{COLORS['text']}]Press Enter to continue...[/{COLORS['text']}]")
    input()

def display_header(console, title_text):
    """Display a header with the given title"""
    console.print("\n" + "=" * 60, style=Style(color=COLORS['primary']))
    console.print(f"[bold {COLORS['primary']}]{title_text}[/bold {COLORS['primary']}]".center(60))
    console.print("=" * 60 + "\n", style=Style(color=COLORS['primary']))

def display_status_bar(console, player):
    """Display the player status bar"""
    # Create a table for status display
    table = Table(show_header=False, box=None, padding=(0, 1))
    
    table.add_column("Label", style=f"bold {COLORS['secondary']}")
    table.add_column("Value", style=COLORS['text'])
    
    # Add player info rows
    table.add_row("NAME", player.name)
    table.add_row("CLASS", player.char_class)
    table.add_row("LEVEL", str(player.level))
    
    # Create health display with color based on health percentage
    health_percent = (player.health / player.max_health) * 100
    health_color = COLORS['text']
    
    if health_percent < 25:
        health_color = COLORS['accent']
    elif health_percent < 50:
        health_color = "yellow"
    
    health_display = f"[{health_color}]{player.health}/{player.max_health}[/{health_color}]"
    table.add_row("HEALTH", health_display)
    
    # Add credits
    table.add_row("CREDITS", str(player.credits))
    
    # Create a second table for stats
    stats_table = Table(show_header=False, box=None, padding=(0, 1))
    
    stats_table.add_column("Stat", style=f"bold {COLORS['secondary']}")
    stats_table.add_column("Value", style=COLORS['text'])
    
    for stat, value in player.stats.items():
        stats_table.add_row(stat.upper(), str(value))
    
    # Display both tables side by side
    console.print(Columns([table, stats_table]), justify="center")
    console.print("\n" + "-" * 60, style=Style(color=COLORS['primary']))

def display_ascii_art(console, art_name):
    """Display ASCII art"""
    art = assets.get_ascii_art(art_name)
    if art:
        console.print(art, style=Style(color=COLORS['primary']))

def main_menu(console):
    """Display main menu and get user choice"""
    clear_screen()
    
    # Display title ASCII art
    console.print(assets.get_ascii_art('title'), style=Style(color=COLORS['primary']))
    
    # Create menu panel
    menu_items = [
        f"[{COLORS['text']}]1. New Game[/{COLORS['text']}]",
        f"[{COLORS['text']}]2. Load Game[/{COLORS['text']}]",
        f"[{COLORS['text']}]3. Options[/{COLORS['text']}]",
        f"[{COLORS['text']}]4. Credits[/{COLORS['text']}]",
        f"[{COLORS['text']}]5. Quit[/{COLORS['text']}]"
    ]
    
    menu_text = "\n".join(menu_items)
    console.print(Panel(menu_text, title=f"[{COLORS['secondary']}]MAIN MENU[/{COLORS['secondary']}]"))
    
    # Get user choice
    choice = Prompt.ask("[bold green]Select an option[/bold green]")
    
    # Check for dev mode activation
    if choice.lower() == "dev":
        return "dev_mode"
    
    # Validate numeric choices
    if choice not in ["1", "2", "3", "4", "5"]:
        console.print("[bold red]Invalid option. Please try again.[/bold red]")
        time.sleep(1)
        return main_menu(console)
    
    # Convert numeric choice to action
    actions = {
        "1": "new_game",
        "2": "load_game",
        "3": "options",
        "4": "credits",
        "5": "quit"
    }
    
    return actions[choice]

def options_menu(console):
    """Display options menu"""
    import settings
    from config import GAME_SETTINGS
    
    while True:
        clear_screen()
        display_header(console, "OPTIONS")
        
        # Create options table
        from rich.table import Table
        table = Table(show_header=False, box=None, padding=(0, 2))
        
        table.add_column("Option", style=f"bold {COLORS['secondary']}")
        table.add_column("Value", style=COLORS['text'])
        
        # Add rows for each setting
        table.add_row("1. Difficulty", GAME_SETTINGS["difficulty"].capitalize())
        table.add_row("2. Text Speed", GAME_SETTINGS["text_speed"].capitalize())
        table.add_row("3. Combat Animations", "Enabled" if GAME_SETTINGS["combat_animations"] else "Disabled")
        
        # Audio settings
        table.add_row("4. Music", "Enabled" if GAME_SETTINGS["music_enabled"] else "Disabled")
        table.add_row("5. Sound Effects", "Enabled" if GAME_SETTINGS["effects_enabled"] else "Disabled")
        table.add_row("6. Music Volume", f"{int(GAME_SETTINGS['music_volume'] * 100)}%")
        table.add_row("7. Sound Effects Volume", f"{int(GAME_SETTINGS['effects_volume'] * 100)}%")
        
        table.add_row("8. Auto Save", "Enabled" if GAME_SETTINGS["auto_save"] else "Disabled")
        table.add_row("9. Show Hints", "Enabled" if GAME_SETTINGS["show_hints"] else "Disabled")
        table.add_row("10. Enable Ollama", "Enabled" if GAME_SETTINGS["enable_ollama"] else "Disabled")
        table.add_row("11. Reset to Defaults", "")
        table.add_row("0. Back to Main Menu", "")
        
        # Display the table
        console.print(table)
        
        # Display additional information based on current settings
        if GAME_SETTINGS["difficulty"] == "easy":
            console.print(f"[{COLORS['text']}]Easy difficulty: Increased player damage, reduced enemy damage, and bonus starting resources.[/{COLORS['text']}]")
        elif GAME_SETTINGS["difficulty"] == "hard":
            console.print(f"[{COLORS['text']}]Hard difficulty: Reduced player damage, increased enemy damage, and fewer starting resources.[/{COLORS['text']}]")
        
        # Get user choice
        choice = Prompt.ask("[bold cyan]Select an option to change[/bold cyan]", 
                          choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "0"])
        
        if choice == "0":
            # Save settings before returning to menu
            settings.save_settings()
            break
            
        elif choice == "1":
            # Change difficulty
            clear_screen()
            display_header(console, "DIFFICULTY SETTINGS")
            
            console.print(f"[{COLORS['text']}]Select game difficulty:[/{COLORS['text']}]")
            console.print(f"[{COLORS['secondary']}]1. Easy[/{COLORS['secondary']}] - Increased player damage, reduced enemy damage")
            console.print(f"[{COLORS['secondary']}]2. Normal[/{COLORS['secondary']}] - Balanced experience")
            console.print(f"[{COLORS['secondary']}]3. Hard[/{COLORS['secondary']}] - Reduced player damage, increased enemy damage")
            
            diff_choice = Prompt.ask("[bold cyan]Select difficulty[/bold cyan]", choices=["1", "2", "3"])
            
            if diff_choice == "1":
                settings.update_setting("difficulty", "easy")
            elif diff_choice == "2":
                settings.update_setting("difficulty", "normal")
            elif diff_choice == "3":
                settings.update_setting("difficulty", "hard")
                
        elif choice == "2":
            # Change text speed
            clear_screen()
            display_header(console, "TEXT SPEED SETTINGS")
            
            console.print(f"[{COLORS['text']}]Select text display speed:[/{COLORS['text']}]")
            console.print(f"[{COLORS['secondary']}]1. Slow[/{COLORS['secondary']}] - More time to read each line")
            console.print(f"[{COLORS['secondary']}]2. Medium[/{COLORS['secondary']}] - Balanced reading pace")
            console.print(f"[{COLORS['secondary']}]3. Fast[/{COLORS['secondary']}] - Quick text display")
            
            speed_choice = Prompt.ask("[bold cyan]Select text speed[/bold cyan]", choices=["1", "2", "3"])
            
            if speed_choice == "1":
                settings.update_setting("text_speed", "slow")
            elif speed_choice == "2":
                settings.update_setting("text_speed", "medium")
            elif speed_choice == "3":
                settings.update_setting("text_speed", "fast")
                
        elif choice == "3":
            # Toggle combat animations
            settings.update_setting("combat_animations", not GAME_SETTINGS["combat_animations"])
            
        elif choice == "4":
            # Toggle music
            settings.update_setting("music_enabled", not GAME_SETTINGS["music_enabled"])
            # Call audio module function if available
            try:
                import audio
                audio.toggle_music()
            except (ImportError, AttributeError):
                pass
            
        elif choice == "5":
            # Toggle sound effects
            settings.update_setting("effects_enabled", not GAME_SETTINGS["effects_enabled"])
            # Call audio module function if available
            try:
                import audio
                audio.toggle_effects()
            except (ImportError, AttributeError):
                pass
                
        elif choice == "6":
            # Change music volume
            clear_screen()
            display_header(console, "MUSIC VOLUME")
            
            current_volume = int(GAME_SETTINGS["music_volume"] * 100)
            console.print(f"[{COLORS['text']}]Current music volume: {current_volume}%[/{COLORS['text']}]")
            
            console.print(f"[{COLORS['secondary']}]Select new volume:[/{COLORS['secondary']}]")
            console.print(f"[{COLORS['text']}]1. Mute (0%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]2. Low (25%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]3. Medium (50%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]4. High (75%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]5. Maximum (100%)[/{COLORS['text']}]")
            
            vol_choice = Prompt.ask("[bold cyan]Select volume level[/bold cyan]", choices=["1", "2", "3", "4", "5"])
            
            volume_levels = {
                "1": 0.0,
                "2": 0.25,
                "3": 0.5,
                "4": 0.75,
                "5": 1.0
            }
            
            settings.update_setting("music_volume", volume_levels[vol_choice])
            
            # Apply volume change if audio module is available
            try:
                import audio
                audio.set_music_volume(volume_levels[vol_choice])
            except (ImportError, AttributeError):
                pass
                
        elif choice == "7":
            # Change sound effects volume
            clear_screen()
            display_header(console, "SOUND EFFECTS VOLUME")
            
            current_volume = int(GAME_SETTINGS["effects_volume"] * 100)
            console.print(f"[{COLORS['text']}]Current sound effects volume: {current_volume}%[/{COLORS['text']}]")
            
            console.print(f"[{COLORS['secondary']}]Select new volume:[/{COLORS['secondary']}]")
            console.print(f"[{COLORS['text']}]1. Mute (0%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]2. Low (25%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]3. Medium (50%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]4. High (75%)[/{COLORS['text']}]")
            console.print(f"[{COLORS['text']}]5. Maximum (100%)[/{COLORS['text']}]")
            
            vol_choice = Prompt.ask("[bold cyan]Select volume level[/bold cyan]", choices=["1", "2", "3", "4", "5"])
            
            volume_levels = {
                "1": 0.0,
                "2": 0.25,
                "3": 0.5,
                "4": 0.75,
                "5": 1.0
            }
            
            settings.update_setting("effects_volume", volume_levels[vol_choice])
            
            # Apply volume change if audio module is available
            try:
                import audio
                audio.set_effects_volume(volume_levels[vol_choice])
            except (ImportError, AttributeError):
                pass
            
        elif choice == "8":
            # Toggle auto save
            settings.update_setting("auto_save", not GAME_SETTINGS["auto_save"])
            
        elif choice == "9":
            # Toggle hints
            settings.update_setting("show_hints", not GAME_SETTINGS["show_hints"])
            
        elif choice == "10":
            # Toggle Ollama integration
            new_value = not GAME_SETTINGS["enable_ollama"]
            settings.update_setting("enable_ollama", new_value)
            
            # The update_setting function will handle updating USE_OLLAMA in config.py
            
        elif choice == "11":
            # Reset to defaults
            if Prompt.ask("[bold red]Reset all settings to defaults?[/bold red]", choices=["y", "n"]) == "y":
                settings.reset_to_defaults()
                
                # Apply audio settings if audio module is available
                try:
                    import audio
                    audio.set_music_volume(GAME_SETTINGS["music_volume"])
                    audio.set_effects_volume(GAME_SETTINGS["effects_volume"])
                    
                    if GAME_SETTINGS["music_enabled"]:
                        audio.toggle_music()
                    if GAME_SETTINGS["effects_enabled"]:
                        audio.toggle_effects()
                except (ImportError, AttributeError):
                    pass
                    
                console.print(f"[{COLORS['text']}]Settings reset to defaults.[/{COLORS['text']}]")
                time.sleep(1)

def display_credits(console):
    """Display game credits"""
    clear_screen()
    display_header(console, "CREDITS")
    
    credits_text = f"""
    [{COLORS['primary']}]{GAME_TITLE}[/{COLORS['primary']}]
    [{COLORS['secondary']}]Version {VERSION}[/{COLORS['secondary']}]
    
    [{COLORS['text']}]A text-based cyberpunk adventure game[/{COLORS['text']}]
    
    [{COLORS['secondary']}]Developed with:[/{COLORS['secondary']}]
    [{COLORS['text']}]- Python 3[/{COLORS['text']}]
    [{COLORS['text']}]- Rich library for terminal formatting[/{COLORS['text']}]
    [{COLORS['text']}]- Pygame for audio playback[/{COLORS['text']}]
    [{COLORS['text']}]- Ollama for dynamic storytelling[/{COLORS['text']}]
    
    [{COLORS['primary']}]Thanks for playing![/{COLORS['primary']}]
    """
    
    console.print(Panel(credits_text, title="ABOUT"))
    console.print(f"\n[{COLORS['secondary']}]Press Enter to return to main menu...[/{COLORS['secondary']}]")
    input()

def display_exit_message(console):
    """Display exit message when quitting the game"""
    clear_screen()
    
    farewell_text = f"""
    [{COLORS['text']}]Thank you for playing[/{COLORS['text']}]
    [{COLORS['primary']}]{GAME_TITLE}[/{COLORS['primary']}]
    
    [{COLORS['secondary']}]The neon streets will be waiting for your return...[/{COLORS['secondary']}]
    """
    
    console.print(Panel(farewell_text, title="GOODBYE"))
    time.sleep(2)
