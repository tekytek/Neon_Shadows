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
    choice = Prompt.ask("[bold green]Select an option[/bold green]", choices=["1", "2", "3", "4", "5"])
    
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
    clear_screen()
    display_header(console, "OPTIONS")
    
    console.print(f"[{COLORS['text']}]Options are not available in this version.[/{COLORS['text']}]")
    console.print(f"\n[{COLORS['secondary']}]Press Enter to return to main menu...[/{COLORS['secondary']}]")
    input()

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
