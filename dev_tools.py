"""
Developer Tools Module - Provides developer-only options for testing
"""
import os
import time
import random

import ui
import character
import inventory
import districts
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from config import COLORS


def dev_menu(console, game_engine):
    """Display the developer tools menu and handle selections"""
    ui.clear_screen()
    ui.display_header(console, "DEVELOPER TOOLS")
    
    console.print("[bold red]WARNING: These options are for testing only![/bold red]\n")
    
    # Display options
    console.print("[cyan]1. Quick Character Creator[/cyan]")
    console.print("[cyan]2. Test Map Navigation[/cyan]")
    console.print("[cyan]3. Test Combat[/cyan]")
    console.print("[cyan]4. Test Inventory[/cyan]")
    console.print("[cyan]5. Add Credits[/cyan]")
    console.print("[cyan]6. Add Items[/cyan]")
    console.print("[cyan]7. Level Up[/cyan]")
    console.print("[cyan]8. Set Reputation[/cyan]")
    console.print("[cyan]0. Return to Main Menu[/cyan]")
    
    # Get user choice
    choice = Prompt.ask("[bold green]Select an option[/bold green]", 
                          choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
    
    if choice == "0":
        return
    elif choice == "1":
        quick_character_creator(console, game_engine)
    elif choice == "2":
        test_map_navigation(console, game_engine)
    elif choice == "3":
        test_combat(console, game_engine)
    elif choice == "4":
        test_inventory(console, game_engine)
    elif choice == "5":
        add_credits(console, game_engine)
    elif choice == "6":
        add_items(console, game_engine)
    elif choice == "7":
        level_up(console, game_engine)
    elif choice == "8":
        set_reputation(console, game_engine)
    
    # Return to dev menu after completing an action
    dev_menu(console, game_engine)


def quick_character_creator(console, game_engine):
    """Create a test character quickly"""
    ui.clear_screen()
    ui.display_header(console, "QUICK CHARACTER CREATOR")
    
    # Pre-defined character templates
    templates = {
        "1": {
            "name": "NetRunner",
            "class": "NetRunner",
            "stats": {"strength": 3, "intelligence": 8, "charisma": 4, "reflex": 5},
            "items": ["Cyberdeck", "ICEbreaker", "Credchip", "Stimpack"]
        },
        "2": {
            "name": "Enforcer",
            "class": "Solo",
            "stats": {"strength": 8, "intelligence": 3, "charisma": 4, "reflex": 5},
            "items": ["Assault Rifle", "Body Armor", "Stimpack", "Credchip"]
        },
        "3": {
            "name": "Fixer",
            "class": "Fixer",
            "stats": {"strength": 4, "intelligence": 5, "charisma": 8, "reflex": 3},
            "items": ["Pistol", "Smart Glasses", "Credchip", "Lockpick Set"]
        }
    }
    
    # Display templates
    console.print("[cyan]1. NetRunner (High Intelligence)[/cyan]")
    console.print("[cyan]2. Solo (High Strength)[/cyan]")
    console.print("[cyan]3. Fixer (High Charisma)[/cyan]")
    console.print("[cyan]4. Create Custom[/cyan]")
    
    choice = Prompt.ask("[bold green]Select a template[/bold green]", 
                        choices=["1", "2", "3", "4"])
    
    if choice in templates:
        # Use pre-defined template
        template = templates[choice]
        
        # Create character
        game_engine.player = character.Character(
            name=template["name"],
            char_class=template["class"],
            stats=template["stats"]
        )
        
        # Add starting items
        for item in template["items"]:
            game_engine.player.inventory.add_item(item)
        
        # Add some starting credits
        game_engine.player.credits = 500
        
        # Initialize choice history
        import choice_history
        game_engine.choice_history = choice_history.ChoiceHistory()
        
        # Set current node to the first story node
        game_engine.current_node = "start"
        
        # Set the starting district
        game_engine.district_manager.set_current_district("downtown")
        
        console.print("[bold green]Character created successfully![/bold green]")
        time.sleep(1)
        
    elif choice == "4":
        # Custom character
        name = Prompt.ask("[bold cyan]Enter character name[/bold cyan]")
        
        # Class options
        console.print("[cyan]Available classes:[/cyan]")
        console.print("1. NetRunner (Tech specialist)")
        console.print("2. Solo (Combat specialist)")
        console.print("3. Fixer (Social specialist)")
        console.print("4. Techie (Crafting specialist)")
        
        class_choice = Prompt.ask("[bold cyan]Select a class[/bold cyan]", 
                                 choices=["1", "2", "3", "4"])
        
        class_map = {
            "1": "NetRunner",
            "2": "Solo",
            "3": "Fixer",
            "4": "Techie"
        }
        
        char_class = class_map[class_choice]
        
        # Custom stats
        console.print("[cyan]Distribute stat points (total: 20)[/cyan]")
        
        strength = IntPrompt.ask("[bold cyan]Strength[/bold cyan]", default=5)
        intelligence = IntPrompt.ask("[bold cyan]Intelligence[/bold cyan]", default=5)
        charisma = IntPrompt.ask("[bold cyan]Charisma[/bold cyan]", default=5)
        reflex = IntPrompt.ask("[bold cyan]Reflex[/bold cyan]", default=5)
        
        # Create character
        game_engine.player = character.Character(
            name=name,
            char_class=char_class,
            stats={
                "strength": strength,
                "intelligence": intelligence,
                "charisma": charisma,
                "reflex": reflex
            }
        )
        
        # Add starting items based on class
        if char_class == "NetRunner":
            starting_items = ["Cyberdeck", "ICEbreaker", "Credchip", "Stimpack"]
        elif char_class == "Solo":
            starting_items = ["Assault Rifle", "Body Armor", "Stimpack", "Credchip"]
        elif char_class == "Fixer":
            starting_items = ["Pistol", "Smart Glasses", "Credchip", "Lockpick Set"]
        elif char_class == "Techie":
            starting_items = ["Toolkit", "Scrap Parts", "Credchip", "Diagnostic Scanner"]
        else:
            starting_items = ["Credchip", "Stimpack"]
        
        for item in starting_items:
            game_engine.player.inventory.add_item(item)
        
        # Add some starting credits
        game_engine.player.credits = 500
        
        # Initialize choice history
        import choice_history
        game_engine.choice_history = choice_history.ChoiceHistory()
        
        # Set current node to the first story node
        game_engine.current_node = "start"
        
        # Set the starting district
        game_engine.district_manager.set_current_district("downtown")
        
        console.print("[bold green]Character created successfully![/bold green]")
        time.sleep(1)


def test_map_navigation(console, game_engine):
    """Test the map navigation system"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    # Handle map travel
    game_engine.handle_map_travel(console)


def test_combat(console, game_engine):
    """Test the combat system with different enemies"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    ui.clear_screen()
    ui.display_header(console, "COMBAT TEST")
    
    # List of enemy templates with varying difficulty
    enemies = [
        {"name": "Street Thug", "health": 8, "damage": 2, "defense": 1},  # Easy
        {"name": "Gang Member", "health": 12, "damage": 3, "defense": 2},  # Medium
        {"name": "Cyborg Enforcer", "health": 18, "damage": 4, "defense": 3},  # Hard
        {"name": "Rogue Security Bot", "health": 25, "damage": 5, "defense": 4},  # Very Hard
        {"name": "Corporate Assassin", "health": 35, "damage": 7, "defense": 5}   # Extreme
    ]
    
    # Display enemy options
    for i, enemy in enumerate(enemies, 1):
        difficulty = ["Easy", "Medium", "Hard", "Very Hard", "Extreme"][i-1]
        console.print(f"[cyan]{i}. {enemy['name']} ({difficulty})[/cyan]")
    
    console.print("[cyan]0. Back[/cyan]")
    
    # Get user choice
    choice = Prompt.ask("[bold green]Select an enemy to fight[/bold green]", 
                        choices=["0", "1", "2", "3", "4", "5"])
    
    if choice == "0":
        return
    
    # Create combat node with selected enemy
    enemy_idx = int(choice) - 1
    enemy_data = enemies[enemy_idx]
    
    combat_node = {
        "type": "combat",
        "text": f"TEST COMBAT: You are facing a {enemy_data['name']}!",
        "enemy": enemy_data,
        "rewards": {
            "experience": 50 * (enemy_idx + 1),
            "credits": 20 * (enemy_idx + 1),
            "items": {"Stimpack": 1} if random.random() < 0.3 else {}
        },
        "victory_node": game_engine.current_node or "start",
        "escape_node": game_engine.current_node or "start",
        "escape_consequences": {
            "health_loss": (enemy_idx + 1) * 2
        }
    }
    
    # Run the combat encounter
    game_engine.handle_combat(console, combat_node)


def test_inventory(console, game_engine):
    """Test the inventory system"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    # Open inventory screen
    game_engine.handle_inventory(console)


def add_credits(console, game_engine):
    """Add credits to the player"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    ui.clear_screen()
    ui.display_header(console, "ADD CREDITS")
    
    # Show current credits
    console.print(f"[cyan]Current credits: {game_engine.player.credits}[/cyan]")
    
    # Get amount to add
    amount = IntPrompt.ask("[bold cyan]Enter amount to add[/bold cyan]", default=100)
    
    # Add credits
    game_engine.player.credits += amount
    
    console.print(f"[bold green]Added {amount} credits. New total: {game_engine.player.credits}[/bold green]")
    time.sleep(1)


def add_items(console, game_engine):
    """Add items to the player's inventory"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    ui.clear_screen()
    ui.display_header(console, "ADD ITEMS")
    
    # Common items list
    common_items = [
        "Stimpack", "Medkit", "Cyberware Upgrade", "Neural Implant",
        "Pistol", "Assault Rifle", "Shotgun", "Sniper Rifle",
        "Light Armor", "Medium Armor", "Heavy Armor", "Stealth Suit",
        "Cyberdeck", "ICEbreaker", "Neural Link", "Toolkit",
        "Lockpick Set", "Scrap Parts", "Encrypted Data", "Smart Glasses"
    ]
    
    # Display item options
    for i, item in enumerate(common_items, 1):
        console.print(f"[cyan]{i}. {item}[/cyan]")
    
    console.print("[cyan]0. Back[/cyan]")
    
    # Get user choice
    choice = Prompt.ask("[bold green]Select an item to add[/bold green]", 
                        choices=[str(i) for i in range(len(common_items) + 1)])
    
    if choice == "0":
        return
    
    # Get quantity
    quantity = IntPrompt.ask("[bold cyan]How many to add?[/bold cyan]", default=1)
    
    # Add the item
    item_idx = int(choice) - 1
    item_name = common_items[item_idx]
    
    game_engine.player.inventory.add_item(item_name, quantity)
    
    console.print(f"[bold green]Added {quantity} {item_name} to inventory.[/bold green]")
    time.sleep(1)


def level_up(console, game_engine):
    """Give the player experience to level up"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    ui.clear_screen()
    ui.display_header(console, "LEVEL UP")
    
    # Show current level and experience
    console.print(f"[cyan]Current level: {game_engine.player.level}[/cyan]")
    console.print(f"[cyan]Current XP: {game_engine.player.experience}[/cyan]")
    
    # Calculate XP needed for next level
    from config import LEVEL_UP_BASE_XP
    xp_for_next_level = LEVEL_UP_BASE_XP * (game_engine.player.level * 1.5)
    xp_needed = xp_for_next_level - game_engine.player.experience
    
    console.print(f"[cyan]XP needed for next level: {xp_needed}[/cyan]")
    
    # Options
    console.print("\n[cyan]1. Add enough XP for next level[/cyan]")
    console.print("[cyan]2. Add custom XP amount[/cyan]")
    console.print("[cyan]3. Add multiple levels (5000 XP)[/cyan]")
    console.print("[cyan]0. Back[/cyan]")
    
    choice = Prompt.ask("[bold green]Select an option[/bold green]", 
                        choices=["0", "1", "2", "3"])
    
    if choice == "0":
        return
    elif choice == "1":
        # Add enough XP for next level
        xp_to_add = max(xp_needed, 1)
        game_engine.player.add_experience(
            xp_to_add, 
            audio_system=game_engine.audio_system if game_engine.audio_enabled else None
        )
        console.print(f"[bold green]Added {xp_to_add} XP. New level: {game_engine.player.level}[/bold green]")
    elif choice == "2":
        # Add custom XP amount
        xp_to_add = IntPrompt.ask("[bold cyan]Enter XP to add[/bold cyan]", default=100)
        game_engine.player.add_experience(
            xp_to_add, 
            audio_system=game_engine.audio_system if game_engine.audio_enabled else None
        )
        console.print(f"[bold green]Added {xp_to_add} XP. New level: {game_engine.player.level}[/bold green]")
    elif choice == "3":
        # Add multiple levels (5000 XP)
        xp_to_add = 5000
        game_engine.player.add_experience(
            xp_to_add, 
            audio_system=game_engine.audio_system if game_engine.audio_enabled else None
        )
        console.print(f"[bold green]Added {xp_to_add} XP. New level: {game_engine.player.level}[/bold green]")
    
    time.sleep(1)


def set_reputation(console, game_engine):
    """Modify player reputation in districts and factions"""
    # Make sure a character exists
    if not game_engine.player:
        console.print("[bold red]Error: No character loaded. Create a character first.[/bold red]")
        time.sleep(2)
        return
    
    ui.clear_screen()
    ui.display_header(console, "SET REPUTATION")
    
    # Get all districts
    district_options = []
    for district_id, district in game_engine.district_manager.districts.items():
        district_options.append((district_id, district.name))
    
    # Display district options
    console.print("[bold cyan]Select a district to modify reputation:[/bold cyan]")
    
    for i, (district_id, name) in enumerate(district_options, 1):
        # Get current reputation
        current_rep = game_engine.player.reputation.get_district_reputation(district_id)
        rep_title = game_engine.player.reputation.get_reputation_title(current_rep)
        console.print(f"[cyan]{i}. {name} - Current: {rep_title} ({current_rep})[/cyan]")
    
    console.print("[cyan]0. Back[/cyan]")
    
    # Get user choice
    choice = Prompt.ask("[bold green]Select a district[/bold green]", 
                        choices=[str(i) for i in range(len(district_options) + 1)])
    
    if choice == "0":
        return
    
    # Get the selected district
    district_idx = int(choice) - 1
    district_id, district_name = district_options[district_idx]
    
    # Display current reputation
    current_rep = game_engine.player.reputation.get_district_reputation(district_id)
    rep_title = game_engine.player.reputation.get_reputation_title(current_rep)
    console.print(f"[cyan]Current reputation in {district_name}: {rep_title} ({current_rep})[/cyan]")
    
    # Options for reputation change
    console.print("\n[cyan]1. Set to maximum (100)[/cyan]")
    console.print("[cyan]2. Set to high (75)[/cyan]")
    console.print("[cyan]3. Set to neutral (0)[/cyan]")
    console.print("[cyan]4. Set to low (-50)[/cyan]")
    console.print("[cyan]5. Set to minimum (-100)[/cyan]")
    console.print("[cyan]6. Set custom value[/cyan]")
    
    rep_choice = Prompt.ask("[bold green]Select an option[/bold green]", 
                           choices=["1", "2", "3", "4", "5", "6"])
    
    # Determine reputation value
    if rep_choice == "1":
        new_rep = 100
    elif rep_choice == "2":
        new_rep = 75
    elif rep_choice == "3":
        new_rep = 0
    elif rep_choice == "4":
        new_rep = -50
    elif rep_choice == "5":
        new_rep = -100
    else:  # Custom value
        new_rep = IntPrompt.ask("[bold cyan]Enter reputation value (-100 to 100)[/bold cyan]", default=0)
        new_rep = max(-100, min(100, new_rep))  # Clamp value
    
    # Set reputation
    change = new_rep - current_rep
    game_engine.player.reputation.modify_district_reputation(district_id, change)
    
    new_title = game_engine.player.reputation.get_reputation_title(new_rep)
    console.print(f"[bold green]Reputation in {district_name} set to {new_title} ({new_rep})[/bold green]")
    time.sleep(1)


def is_dev_mode_activated(input_sequence):
    """Check if the special key combination for dev mode has been entered"""
    # The secret key combination is "d e v"
    return input_sequence == "dev"