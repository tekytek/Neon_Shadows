"""
Combat Module - Handles combat encounters and mechanics
"""
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from config import COLORS

class Enemy:
    """Enemy class for combat encounters"""
    
    def __init__(self, name, health, damage, defense):
        """Initialize an enemy"""
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.defense = defense
        self.weaknesses = []
        self.resistances = []
    
    def take_damage(self, amount):
        """Apply damage to the enemy, considering defense"""
        actual_damage = max(1, amount - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def is_defeated(self):
        """Check if the enemy is defeated"""
        return self.health <= 0
    
    def attack(self):
        """Generate an attack from the enemy"""
        # Base damage with slight randomization
        damage_mod = random.uniform(0.8, 1.2)
        return round(self.damage * damage_mod)

def display_combat_status(console, player, enemy):
    """Display combat status for player and enemy"""
    # Create a table for the combat display
    table = Table(show_header=False, box=None, padding=(0, 1))
    
    table.add_column("Entity", style=f"bold {COLORS['secondary']}")
    table.add_column("Health", style=COLORS['text'])
    
    # Player health with color based on percentage
    player_health_percent = (player.health / player.max_health) * 100
    player_health_color = COLORS['text']
    
    if player_health_percent < 25:
        player_health_color = COLORS['accent']
    elif player_health_percent < 50:
        player_health_color = "yellow"
    
    player_health_display = f"[{player_health_color}]{player.health}/{player.max_health}[/{player_health_color}]"
    
    # Enemy health with color based on percentage
    enemy_health_percent = (enemy.health / enemy.max_health) * 100
    enemy_health_color = COLORS['text']
    
    if enemy_health_percent < 25:
        enemy_health_color = COLORS['accent']
    elif enemy_health_percent < 50:
        enemy_health_color = "yellow"
    
    enemy_health_display = f"[{enemy_health_color}]{enemy.health}/{enemy.max_health}[/{enemy_health_color}]"
    
    # Add rows to the table
    table.add_row("YOU", player_health_display)
    table.add_row(enemy.name.upper(), enemy_health_display)
    
    console.print(table)
    console.print("-" * 60, style=f"{COLORS['primary']}")

def run_combat(console, player, enemy):
    """Run a complete combat encounter"""
    # Initialize combat
    turn = 1
    combat_active = True
    result = None
    
    while combat_active:
        # Clear screen and show status
        console.clear()
        console.print(Panel(f"[{COLORS['accent']}]COMBAT: {player.name} vs {enemy.name}[/{COLORS['accent']}]"))
        
        # Display health status
        display_combat_status(console, player, enemy)
        
        # Player's turn
        console.print(f"[{COLORS['primary']}]TURN {turn}[/{COLORS['primary']}]")
        console.print(f"[{COLORS['secondary']}]Your move:[/{COLORS['secondary']}]")
        
        # Display combat options
        console.print(f"[{COLORS['text']}]1. Attack[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]2. Use Item[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]3. Attempt to Escape[/{COLORS['text']}]")
        
        choice = Prompt.ask("[bold green]Choose your action[/bold green]", choices=["1", "2", "3"])
        
        if choice == "1":
            # Attack
            # Determine attack damage based on strength and a random factor
            base_damage = player.stats.get("strength", 3)
            damage_mod = random.uniform(0.8, 1.5)
            attack_damage = round(base_damage * damage_mod)
            
            # Apply damage to enemy
            actual_damage = enemy.take_damage(attack_damage)
            
            console.print(f"[{COLORS['text']}]You attack {enemy.name} for [{COLORS['accent']}]{actual_damage}[/{COLORS['accent']}] damage![/{COLORS['text']}]")
            
            # Check if enemy is defeated
            if enemy.is_defeated():
                console.print(f"[{COLORS['primary']}]You defeated {enemy.name}![/{COLORS['primary']}]")
                combat_active = False
                result = "victory"
        
        elif choice == "2":
            # Use Item
            items = player.inventory.get_all_items()
            
            if not items:
                console.print(f"[{COLORS['accent']}]You have no items to use![/{COLORS['accent']}]")
                time.sleep(1)
                continue
            
            # Display usable items
            console.print(f"[{COLORS['secondary']}]Available items:[/{COLORS['secondary']}]")
            
            usable_items = {}
            item_idx = 1
            
            for item_name, count in items.items():
                # Only show items that can be used in combat
                item_info = get_item_info(item_name)
                if item_info and item_info.get("usable_in_combat", False):
                    usable_items[str(item_idx)] = item_name
                    console.print(f"[{COLORS['text']}]{item_idx}. {item_name} (x{count})[/{COLORS['text']}]")
                    item_idx += 1
            
            if not usable_items:
                console.print(f"[{COLORS['accent']}]You have no usable items for combat![/{COLORS['accent']}]")
                time.sleep(1)
                continue
            
            console.print(f"[{COLORS['text']}]0. Back to combat options[/{COLORS['text']}]")
            
            item_choice = Prompt.ask("[bold green]Choose an item to use[/bold green]", 
                                    choices=list(usable_items.keys()) + ["0"])
            
            if item_choice == "0":
                continue
            
            selected_item = usable_items[item_choice]
            player.use_item(selected_item, console)
        
        elif choice == "3":
            # Attempt to escape
            # Escape chance based on reflex stat
            escape_chance = min(70, 30 + (player.stats.get("reflex", 3) * 5))
            escape_roll = random.randint(1, 100)
            
            if escape_roll <= escape_chance:
                console.print(f"[{COLORS['primary']}]You successfully escaped from combat![/{COLORS['primary']}]")
                combat_active = False
                result = "escape"
            else:
                console.print(f"[{COLORS['accent']}]Escape failed! {enemy.name} blocks your retreat![/{COLORS['accent']}]")
        
        # If combat is still active, enemy takes their turn
        if combat_active and not enemy.is_defeated():
            time.sleep(1)  # Pause for effect
            
            # Enemy attack
            enemy_damage = enemy.attack()
            
            # Player defense based on reflex
            player_defense = player.stats.get("reflex", 0) // 2
            actual_damage = max(1, enemy_damage - player_defense)
            
            # Apply damage to player
            player.health = max(0, player.health - actual_damage)
            
            console.print(f"[{COLORS['accent']}]{enemy.name} attacks you for {actual_damage} damage![/{COLORS['accent']}]")
            
            # Check if player is defeated
            if player.health <= 0:
                console.print(f"[{COLORS['accent']}]You have been defeated by {enemy.name}![/{COLORS['accent']}]")
                combat_active = False
                result = "defeat"
            
            # Short pause before next turn
            time.sleep(1.5)
        
        # Increment turn counter
        turn += 1
    
    # Combat is over, show result message
    if result == "victory":
        console.print(f"[{COLORS['primary']}]Victory! You defeated {enemy.name}.[/{COLORS['primary']}]")
    elif result == "defeat":
        console.print(f"[{COLORS['accent']}]Defeat! {enemy.name} has defeated you.[/{COLORS['accent']}]")
    elif result == "escape":
        console.print(f"[{COLORS['secondary']}]You escaped from {enemy.name}.[/{COLORS['secondary']}]")
    
    time.sleep(2)
    return result

def get_item_info(item_name):
    """Get information about an item"""
    # Import here to avoid circular imports
    from inventory import get_item_info as inventory_get_item_info
    return inventory_get_item_info(item_name)
