"""
Test script for tactical abilities integration
"""
import time
from rich.console import Console

import combat
import character
from tactical_abilities import handle_tactical_ability

def main():
    """Test the tactical abilities integration"""
    console = Console()
    
    console.print("[bold green]Testing Tactical Abilities Integration[/bold green]")
    
    # Create a test player
    player = character.Character("Tester", "NetRunner")
    player.level = 5  # Higher level for more abilities
    player.stats = {
        "strength": 5,
        "intelligence": 8,
        "charisma": 4,
        "reflex": 6
    }
    
    # Create a test enemy
    enemy = combat.Enemy("Security Bot", 20, 3, 2, enemy_type="cybernetic")
    
    # Initialize a combat state
    combat_state = {
        "player_position": "center",
        "enemy_position": "center",
        "player_cover": "none",
        "enemy_cover": "none",
        "environment": "cyber_den",
        "target_zone": "torso"
    }
    
    # Add a test ability to the player (Neural Overload from NetRunner)
    player.abilities = {
        "neural_overload": combat.CLASS_ABILITIES["NetRunner"]["neural_overload"]
    }
    player.ability_cooldowns = {"neural_overload": 0}  # No cooldown for testing
    
    console.print(f"[bold]Player created:[/bold] {player.name}, class: {player.char_class}")
    console.print(f"[bold]Enemy created:[/bold] {enemy.name}, type: {enemy.enemy_type}")
    console.print(f"[bold]Combat state initialized:[/bold] {combat_state}")
    
    # Test tactical ability handling
    console.print("\n[bold yellow]Testing tactical ability: Neural Overload[/bold yellow]")
    
    # Use the tactical_abilities module to handle the ability
    updated_combat_state, ability_result = handle_tactical_ability(
        player, "neural_overload", enemy, combat_state, console
    )
    
    # Display results
    console.print(f"\n[bold]Ability result:[/bold] {ability_result}")
    console.print(f"[bold]Updated combat state:[/bold] {updated_combat_state}")
    console.print(f"[bold]Enemy health:[/bold] {enemy.health}/{enemy.max_health}")
    
    # Test another ability - System Glitch
    console.print("\n[bold yellow]Testing tactical ability: System Glitch[/bold yellow]")
    player.abilities["system_glitch"] = combat.CLASS_ABILITIES["NetRunner"]["system_glitch"]
    player.ability_cooldowns["system_glitch"] = 0  # No cooldown for testing
    
    # Use the tactical_abilities module to handle the ability
    updated_combat_state, ability_result = handle_tactical_ability(
        player, "system_glitch", enemy, updated_combat_state, console
    )
    
    # Display results
    console.print(f"\n[bold]Ability result:[/bold] {ability_result}")
    console.print(f"[bold]Updated combat state:[/bold] {updated_combat_state}")
    console.print(f"[bold]Enemy health:[/bold] {enemy.health}/{enemy.max_health}")
    
    # Test a third ability - ICE Breaker
    console.print("\n[bold yellow]Testing tactical ability: ICE Breaker[/bold yellow]")
    
    # First set the enemy to have cover
    updated_combat_state["enemy_cover"] = "medium"
    updated_combat_state["enemy_cover_health"] = 5
    
    player.abilities["ice_breaker"] = combat.CLASS_ABILITIES["NetRunner"]["ice_breaker"]
    player.ability_cooldowns["ice_breaker"] = 0  # No cooldown for testing
    
    # Use the tactical_abilities module to handle the ability
    updated_combat_state, ability_result = handle_tactical_ability(
        player, "ice_breaker", enemy, updated_combat_state, console
    )
    
    # Display results
    console.print(f"\n[bold]Ability result:[/bold] {ability_result}")
    console.print(f"[bold]Updated combat state:[/bold] {updated_combat_state}")
    console.print(f"[bold]Enemy health:[/bold] {enemy.health}/{enemy.max_health}")
    
    console.print("\n[bold green]Tactical abilities testing complete![/bold green]")

if __name__ == "__main__":
    main()