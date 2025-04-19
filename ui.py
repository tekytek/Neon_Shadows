"""
UI Module - Handles display and user interface
"""
import os
import sys
import time
import platform
import shutil
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
    import sys
    
    # If no speed specified, use the setting from config
    if speed is None:
        speed_setting = GAME_SETTINGS.get("text_speed", "medium")
        speed = TEXT_SPEED.get(speed_setting, 0.02)
    
    # If speed is 0 or very small, just print normally
    if speed < 0.001:
        console.print(text)
        return
    
    try:
        # Apply typewriter effect with interrupt handling
        for char in text:
            try:
                console.print(char, end="")
                time.sleep(speed)
            except KeyboardInterrupt:
                # Properly handle Ctrl+C
                console.print("\nKeyboard interrupt detected. Exiting...", style="yellow")
                sys.exit(0)
        
        # Add newline at the end
        console.print("")
    except Exception as e:
        # In case of any errors, fall back to normal print
        console.print(f"\nError in typewriter effect: {str(e)}")
        console.print(text)

def display_splash_screen(console):
    """Display the game's splash screen"""
    clear_screen()
    
    # Try to use animation for digital rain effect
    try:
        import animations
        from config import GAME_SETTINGS
        
        # Only use digital rain if animations are enabled
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            try:
                animations.digital_rain(console, duration=1.5, density=0.2, chars="01")
            except Exception as e:
                # Catch any animation errors but still continue with splash screen
                print(f"Animation error caught: {e}")
                time.sleep(0.5)
    except (ImportError, AttributeError):
        pass
    
    # Display responsive title banner with animation if available
    try:
        import animations
        from config import GAME_SETTINGS
        from rich.text import Text
        
        # Get title ASCII art
        title_art = assets.get_ascii_art('title')
        
        # Apply hologram effect to title if animations enabled
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Let the hologram_effect function handle Text creation
            animations.hologram_effect(title_art, console, style=Style(color=COLORS['primary']))
        else:
            # Create a Text object to prevent markup interpretation
            title_text = Text(title_art)
            console.print(title_text, style=Style(color=COLORS['primary']))
    except (ImportError, AttributeError):
        # Fall back to standard display - this uses Text objects now
        display_responsive_title(console)
    
    # Get terminal width for responsive display
    term_width, term_height = shutil.get_terminal_size()
    
    # Display version only with typing effect if available - removed tagline to prevent duplication
    try:
        import animations
        from config import GAME_SETTINGS
        
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Use style parameter instead of markup to avoid raw formatting codes
            animations.typing_effect(f"Version {VERSION}", console, style=Style(color=COLORS['secondary']))
        else:
            console.print(f"[{COLORS['secondary']}]Version {VERSION}[/{COLORS['secondary']}]")
    except (ImportError, AttributeError):
        console.print(f"[{COLORS['secondary']}]Version {VERSION}[/{COLORS['secondary']}]")
    
    # Bottom line - adapt to terminal width
    separator_width = min(60, term_width - 4)  # Leave a small margin
    console.print("\n" + "=" * separator_width, style=Style(color=COLORS['primary']))
    console.print("Press Enter to continue...", style=Style(color=COLORS['text']))
    import sys
    try:
        # Simple approach - wait for input and properly handle interrupts
        try:
            # Wait for user input with a clear prompt
            input()
        except KeyboardInterrupt:
            # Properly handle Ctrl+C by stopping the program
            console.print("Keyboard interrupt detected. Exiting...", style="yellow")
            sys.exit(0)
        except EOFError:
            # Handle EOF error (Ctrl+D) more gracefully
            console.print("EOF detected. Press Enter to continue or Ctrl+C to exit.", style="yellow")
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)
    except Exception as e:
        # Catch any other input-related issues but don't auto-continue
        console.print(f"Input handling issue: {str(e)}. Press Enter to continue or Ctrl+C to exit.", style="yellow")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

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

def display_responsive_title(console):
    """Display the title banner in a way that adapts to terminal width"""
    # Import Text class for special character handling
    from rich.text import Text
    
    # Get terminal width for responsive display
    term_width, term_height = shutil.get_terminal_size()
    
    # Full banner requires at least 100 columns
    if term_width >= 100:
        # Display full ASCII art title with Text object to prevent markup interpretation
        title_art = assets.get_ascii_art('title')
        title_text = Text(title_art)
        console.print(title_text, style=Style(color=COLORS['primary']))
    else:
        # Display compact alternative for smaller terminals
        compact_title = f"""
    ███╗   ██╗███████╗ ██████╗ ███╗   ██╗
    ████╗  ██║██╔════╝██╔═══██╗████╗  ██║
    ██╔██╗ ██║█████╗  ██║   ██║██╔██╗ ██║
    ██║╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║
    ██║ ╚████║███████╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
    ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗███████╗
    ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝
    ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║███████╗
    ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║╚════██║
    ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝███████║
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝
        """
        # Create a Text object to prevent markup interpretation
        compact_text = Text(compact_title)
        console.print(compact_text, style=Style(color=COLORS['primary']))

def display_ascii_art(console, art_name):
    """Display ASCII art"""
    # Import Text class for special character handling
    from rich.text import Text
    
    # Special case for title banner
    if art_name == 'title':
        display_responsive_title(console)
        return
        
    art = assets.get_ascii_art(art_name)
    if art:
        # Create a Text object to prevent markup interpretation
        art_text = Text(art)
        console.print(art_text, style=Style(color=COLORS['primary']))

def main_menu(console):
    """Display main menu and get user choice"""
    clear_screen()
    
    # Try to use more advanced animation effects if available
    try:
        import animations
        from config import GAME_SETTINGS
        
        # Only use fancy animations if they're enabled in settings
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Use digital rain as a prelude for cyberpunk feel
            try:
                animations.digital_rain(console, duration=1.0, density=0.15, chars="01")
            except Exception as e:
                # Catch any animation errors but continue
                print(f"Animation error caught: {e}")
                time.sleep(0.5)
            
            # Use hacker transition effect
            try:
                animations.hacker_transition(console, lines=3)
            except Exception as e:
                # Catch any animation errors but continue
                print(f"Animation error caught: {e}")
                time.sleep(0.5)
        else:
            # Still use basic hacker transition even if fancy animations are disabled
            animations.hacker_transition(console, lines=2)
    except (ImportError, AttributeError):
        pass
    
    # Display title with hologram effect if available
    try:
        import animations
        from config import GAME_SETTINGS
        from rich.text import Text
        
        # Get title ASCII art
        title_art = assets.get_ascii_art('title')
        
        # Apply hologram effect to title if animations enabled
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Let the hologram_effect function handle Text creation
            animations.hologram_effect(title_art, console, style=Style(color=COLORS['primary']))
        else:
            # Create a Text object to prevent markup interpretation
            title_text = Text(title_art)
            console.print(title_text, style=Style(color=COLORS['primary']))
    except (ImportError, AttributeError):
        # Fall back to standard display - this uses Text objects now
        display_responsive_title(console)
    
    # Display tagline - moved from splash screen to prevent duplication
    try:
        import animations
        from config import GAME_SETTINGS
        
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Use styling without markup for compatibility
            animations.typing_effect("A text-based cyberpunk adventure", console, style=Style(color=COLORS['text']))
            console.print() # Add a newline spacing
        else:
            console.print(f"[{COLORS['text']}]A text-based cyberpunk adventure[/{COLORS['text']}]")
            console.print() # Add a newline spacing
    except (ImportError, AttributeError):
        console.print(f"[{COLORS['text']}]A text-based cyberpunk adventure[/{COLORS['text']}]")
        console.print() # Add a newline spacing
    
    # Create menu panel with cyberpunk-themed items
    menu_items = [
        "1. New Game",
        "2. Load Game",
        "3. Codex",
        "4. Options",
        "5. Credits",
        "6. Quit"
    ]
    
    # Format all menu items with proper style
    menu_text = "\n".join(menu_items)
    
    # Try to use animation for menu display if available
    try:
        import animations
        from config import GAME_SETTINGS
        
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            # Create a panel with cyberpunk-themed title
            menu_panel = Panel(menu_text, title="MAIN MENU", title_align="center", style=Style(color=COLORS['text']))
            
            # Use neon border effect for the menu to make it stand out
            animations.neon_border(menu_panel, console, style=Style(color=COLORS['secondary']), border_char="█")
        else:
            # Use simpler neon fade for basic animation
            menu_panel = Panel(menu_text, title="MAIN MENU", title_align="center", style=Style(color=COLORS['text']))
            animations.neon_fade_in(menu_panel, console)
    except (ImportError, AttributeError):
        # Fall back to standard display if animations not available
        console.print(Panel(menu_text, title="MAIN MENU", title_align="center", style=Style(color=COLORS['text'])))
    
    # Display a cyberpunk-themed prompt with flicker effect if animations are enabled
    try:
        import animations
        from config import GAME_SETTINGS
        import sys
        
        # Display the prompt
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            prompt_text = "[bold green]> Select Option:[/bold green]"
            animations.cyber_flicker(prompt_text, console, flicker_count=2)
        else:
            console.print("[bold green]> Select Option:[/bold green]")
        
        # Handle input more robustly
        try:
            # Terminal is interactive, wait for normal input
            choice = Prompt.ask("")
        except KeyboardInterrupt:
            # Properly handle Ctrl+C to exit the game
            console.print("Keyboard interrupt detected. Exiting...", style="yellow")
            sys.exit(0)
        except EOFError:
            # Handle EOF error (Ctrl+D) with a clear message
            console.print("EOF detected. Using default option (1).", style="yellow")
            choice = "1"  # Default to "New Game" if input fails
    except (ImportError, AttributeError) as e:
        # Fall back to standard prompt
        import sys
        try:
            choice = Prompt.ask("[bold green]Select an option[/bold green]")
        except KeyboardInterrupt:
            # Properly handle Ctrl+C by stopping the program
            console.print("Keyboard interrupt detected. Exiting...", style="yellow")
            sys.exit(0)
        except EOFError:
            # Handle EOF error with a clear message
            console.print("EOF detected. Using default option (1).", style="yellow")
            choice = "1"  # Default to "New Game"
    
    # Check for dev mode activation
    if choice.lower() == "dev":
        return "dev_mode"
    
    # Validate numeric choices
    if choice not in ["1", "2", "3", "4", "5", "6"]:
        try:
            import animations
            from config import GAME_SETTINGS
            
            if GAME_SETTINGS.get("ui_animations_enabled", True):
                # Use data corruption effect for error message
                animations.data_corruption("[bold red]ERROR: Invalid selection. System recalibrating...[/bold red]", 
                                         console, 
                                         style=Style(color=COLORS['accent']), 
                                         corruption_level=0.3)
            else:
                console.print("[bold red]Invalid option. Please try again.[/bold red]")
        except (ImportError, AttributeError):
            console.print("[bold red]Invalid option. Please try again.[/bold red]")
            
        time.sleep(1)
        return main_menu(console)
    
    # Convert numeric choice to action
    actions = {
        "1": "new_game",
        "2": "load_game",
        "3": "codex",
        "4": "options",
        "5": "credits",
        "6": "quit"
    }
    
    # Display selection confirmation with specific effect based on choice
    try:
        import animations
        from config import GAME_SETTINGS
        
        if GAME_SETTINGS.get("ui_animations_enabled", True):
            confirm_texts = {
                "1": "[bold cyan]INITIALIZING NEW GAME PROTOCOL...[/bold cyan]",
                "2": "[bold cyan]ACCESSING SAVE DATA...[/bold cyan]",
                "3": "[bold cyan]LOADING NEURAL CODEX DATABASE...[/bold cyan]",
                "4": "[bold cyan]OPENING SYSTEM CONFIGURATION...[/bold cyan]",
                "5": "[bold cyan]ACCESSING CREATOR INFORMATION...[/bold cyan]",
                "6": "[bold cyan]PREPARING SYSTEM SHUTDOWN...[/bold cyan]"
            }
            
            animations.typing_effect(confirm_texts[choice], console)
            time.sleep(0.5)
    except (ImportError, AttributeError):
        pass
    
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
        
        # UI Animation settings
        table.add_row("8. UI Animations", "Enabled" if GAME_SETTINGS["ui_animations_enabled"] else "Disabled")
        table.add_row("9. UI Animation Speed", GAME_SETTINGS["ui_animation_speed"].capitalize())
        
        table.add_row("10. Auto Save", "Enabled" if GAME_SETTINGS["auto_save"] else "Disabled")
        table.add_row("11. Show Hints", "Enabled" if GAME_SETTINGS["show_hints"] else "Disabled")
        table.add_row("12. Enable Ollama", "Enabled" if GAME_SETTINGS["enable_ollama"] else "Disabled")
        table.add_row("13. Ollama API Endpoint", GAME_SETTINGS["ollama_api_url"])
        table.add_row("14. Reset to Defaults", "")
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
                          choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "0"])
        
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
            # Toggle UI animations
            settings.update_setting("ui_animations_enabled", not GAME_SETTINGS["ui_animations_enabled"])
            # Update animations module if available
            try:
                import animations
                animations.toggle_animations()
            except (ImportError, AttributeError):
                pass
                
        elif choice == "9":
            # Change UI animation speed
            clear_screen()
            display_header(console, "UI ANIMATION SPEED")
            
            console.print(f"[{COLORS['text']}]Select UI animation speed:[/{COLORS['text']}]")
            console.print(f"[{COLORS['secondary']}]1. Slow[/{COLORS['secondary']}] - More dramatic animations")
            console.print(f"[{COLORS['secondary']}]2. Medium[/{COLORS['secondary']}] - Balanced animation speed")
            console.print(f"[{COLORS['secondary']}]3. Fast[/{COLORS['secondary']}] - Quick animations")
            
            speed_choice = Prompt.ask("[bold cyan]Select animation speed[/bold cyan]", choices=["1", "2", "3"])
            
            if speed_choice == "1":
                settings.update_setting("ui_animation_speed", "slow")
                # Update animations module if available
                try:
                    import animations
                    animations.set_animation_speed("slow")
                except (ImportError, AttributeError):
                    pass
            elif speed_choice == "2":
                settings.update_setting("ui_animation_speed", "medium")
                # Update animations module if available
                try:
                    import animations
                    animations.set_animation_speed("medium")
                except (ImportError, AttributeError):
                    pass
            elif speed_choice == "3":
                settings.update_setting("ui_animation_speed", "fast")
                # Update animations module if available
                try:
                    import animations
                    animations.set_animation_speed("fast")
                except (ImportError, AttributeError):
                    pass
                
        elif choice == "10":
            # Toggle auto save
            settings.update_setting("auto_save", not GAME_SETTINGS["auto_save"])
            
        elif choice == "11":
            # Toggle hints
            settings.update_setting("show_hints", not GAME_SETTINGS["show_hints"])
            
        elif choice == "12":
            # Toggle Ollama integration
            new_value = not GAME_SETTINGS["enable_ollama"]
            settings.update_setting("enable_ollama", new_value)
            
            # The update_setting function will handle updating USE_OLLAMA in config.py
            
        elif choice == "13":
            # Configure Ollama API endpoint
            clear_screen()
            display_header(console, "OLLAMA API ENDPOINT")
            
            current_endpoint = GAME_SETTINGS["ollama_api_url"]
            console.print(f"[{COLORS['text']}]Current Ollama API endpoint: {current_endpoint}[/{COLORS['text']}]")
            console.print(f"[{COLORS['secondary']}]Enter the URL of your Ollama API endpoint.[/{COLORS['secondary']}]")
            console.print(f"[{COLORS['text']}]Default is http://localhost:11434/api[/{COLORS['text']}]")
            
            new_endpoint = Prompt.ask("[bold cyan]New API endpoint[/bold cyan]", default=current_endpoint)
            settings.update_setting("ollama_api_url", new_endpoint)
            
            console.print(f"[{COLORS['text']}]Ollama API endpoint updated.[/{COLORS['text']}]")
            time.sleep(1)
            
        elif choice == "14":
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
    
    # Try to use animation transition if available
    try:
        import animations
        animations.hacker_transition(console, lines=2)
    except (ImportError, AttributeError):
        pass
        
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
    
    # Try to use animation for credits display if available
    try:
        import animations
        animations.cyber_scan(Panel(credits_text, title="ABOUT"), console)
    except (ImportError, AttributeError):
        console.print(Panel(credits_text, title="ABOUT"))
        
    console.print(f"\n[{COLORS['secondary']}]Press Enter to return to main menu...[/{COLORS['secondary']}]")
    input()

def display_exit_message(console):
    """Display exit message when quitting the game"""
    clear_screen()
    
    # Try to use animation transition if available
    try:
        import animations
        animations.hacker_transition(console, lines=3)
    except (ImportError, AttributeError):
        pass
    
    farewell_text = f"""
    [{COLORS['text']}]Thank you for playing[/{COLORS['text']}]
    [{COLORS['primary']}]{GAME_TITLE}[/{COLORS['primary']}]
    
    [{COLORS['secondary']}]The neon streets will be waiting for your return...[/{COLORS['secondary']}]
    """
    
    # Try to use animation for exit message if available
    try:
        import animations
        animations.cyber_flicker(Panel(farewell_text, title="GOODBYE"), console, style=Style(color=COLORS["primary"]))
    except (ImportError, AttributeError):
        console.print(Panel(farewell_text, title="GOODBYE"))
        
    time.sleep(2)
    
def display_codex(console, game_engine=None):
    """Display the in-game codex"""
    clear_screen()
    
    # Try to use animation transition if available
    try:
        import animations
        animations.hacker_transition(console, lines=2)
    except (ImportError, AttributeError):
        pass
    
    # Import codex module
    import codex
    
    # Initialize codex
    game_codex = codex.Codex()
    
    # If game engine is provided, use its player for codex discovery status
    if game_engine and hasattr(game_engine, 'player'):
        player = game_engine.player
    else:
        player = None
    
    # Display the codex menu
    codex.display_codex_menu(console, game_codex, player)
    
    # Play selection sound if available
    try:
        if game_engine and game_engine.audio_system:
            game_engine.audio_system.play_sound("menu_back")
    except (AttributeError, Exception):
        pass
