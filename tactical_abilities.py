"""
Tactical Abilities Module - Handles class-specific combat abilities
"""
import random
from rich.console import Console

# Constants for combat positions
POSITIONS = ["center", "flank_left", "flank_right", "defensive", "aggressive"]

def apply_tactical_effects(ability_result, combat_state, player, enemy, console=None):
    """
    Process and apply tactical effects from ability usage
    
    Args:
        ability_result (dict): The result of using an ability
        combat_state (dict): Current state of combat (positions, cover, etc.)
        player: The player character
        enemy: The enemy being fought
        console: Console for output
        
    Returns:
        tuple: Updated combat_state, updated ability_result
    """
    effects = ability_result.get("effects", {})
    
    # Skip if ability failed or has no effects
    if not ability_result.get("success", False) or not effects:
        return combat_state, ability_result
    
    # Process position effects
    if "position_effect" in effects:
        position_effect = effects["position_effect"]
        
        # Handle different position effects
        if position_effect == "random":
            new_position = random.choice(POSITIONS)
            combat_state["enemy_position"] = new_position
            
            if console:
                console.print(f"[cyan]Enemy position scrambled to {new_position}[/cyan]")
                
        elif position_effect == "force_center":
            combat_state["enemy_position"] = "center"
            
            if console:
                console.print(f"[cyan]Enemy forced to center position[/cyan]")
                
        elif position_effect == "close_distance":
            combat_state["player_position"] = "center"
            
            if console:
                console.print(f"[cyan]You close the distance to the enemy[/cyan]")
                
        elif position_effect == "improve_position":
            advantageous_positions = ["flank_left", "flank_right", "aggressive"]
            new_position = random.choice(advantageous_positions)
            combat_state["player_position"] = new_position
            
            if console:
                console.print(f"[cyan]You move to a more advantageous position: {new_position}[/cyan]")
    
    # Process cover effects
    if "cover_damage" in effects:
        cover_damage = effects["cover_damage"]
        enemy_cover = combat_state.get("enemy_cover", "none")
        
        if enemy_cover != "none":
            # Reduce cover health
            combat_state["enemy_cover_health"] = max(0, combat_state.get("enemy_cover_health", 0) - cover_damage)
            
            # If cover is destroyed, remove it
            if combat_state["enemy_cover_health"] <= 0:
                combat_state["enemy_cover"] = "none"
                
                if console:
                    console.print(f"[cyan]You destroyed the enemy's {enemy_cover} cover![/cyan]")
            else:
                if console:
                    console.print(f"[cyan]You damaged the enemy's cover! ({combat_state['enemy_cover_health']} health remaining)[/cyan]")
    
    # Process cover creation
    if "create_cover" in effects:
        cover_type = effects["create_cover"]
        cover_health = effects.get("cover_health", 5)
        
        combat_state["player_cover"] = cover_type
        combat_state["player_cover_health"] = cover_health
        
        if console:
            console.print(f"[cyan]You've created {cover_type} cover with {cover_health} health[/cyan]")
    
    # Process cover boost
    if "cover_boost" in effects:
        cover_boost = effects["cover_boost"]
        player_cover = combat_state.get("player_cover", "none")
        
        if player_cover != "none":
            combat_state["player_cover_defense_bonus"] = combat_state.get("player_cover_defense_bonus", 0) + cover_boost
            
            if console:
                console.print(f"[cyan]Your cover's defensive value is increased by {cover_boost}[/cyan]")
    
    # Process target zone specification
    if "target_zone" in effects:
        combat_state["target_zone"] = effects["target_zone"]
        
        if console:
            console.print(f"[cyan]Targeting set to {effects['target_zone']}[/cyan]")
    
    # Return updated state and result
    return combat_state, ability_result

def handle_tactical_ability(player, ability_id, enemy, combat_state, console=None, audio_system=None):
    """
    Process a tactical ability with proper combat state tracking
    
    Args:
        player: The player character
        ability_id (str): ID of the ability to use
        enemy: The enemy being fought
        combat_state (dict): Current state of combat
        console: Console for output
        audio_system: Audio system for sound effects
    
    Returns:
        tuple: Updated combat_state, ability_result
    """
    # Ensure combat_state has all required fields
    if combat_state is None:
        combat_state = {
            "player_position": "center",
            "enemy_position": "center",
            "player_cover": "none",
            "enemy_cover": "none",
            "environment": "standard",
            "target_zone": "torso"
        }
    
    # Get current positions and cover
    player_position = combat_state.get("player_position", "center")
    enemy_position = combat_state.get("enemy_position", "center")
    player_cover = combat_state.get("player_cover", "none")
    enemy_cover = combat_state.get("enemy_cover", "none")
    
    # Set these attributes on player and enemy for consistency
    player.position = player_position
    player.current_cover = player_cover
    enemy.position = enemy_position
    enemy.current_cover = enemy_cover
    
    # Execute the ability
    ability_result = player.use_ability(ability_id, enemy, console, audio_system, combat_state)
    
    # Process tactical effects
    if ability_result.get("success", False):
        combat_state, ability_result = apply_tactical_effects(
            ability_result, combat_state, player, enemy, console
        )
        
        # Update player and enemy with any changes from the ability
        player.position = combat_state.get("player_position", player.position)
        player.current_cover = combat_state.get("player_cover", player.current_cover)
        enemy.position = combat_state.get("enemy_position", enemy.position)
        enemy.current_cover = combat_state.get("enemy_cover", enemy.current_cover)
    
    return combat_state, ability_result

def process_ability_outcomes(player, enemy, ability_result, combat_state, console=None):
    """
    Process the outcomes of using an ability in combat
    
    Args:
        player: The player character
        enemy: The enemy being fought
        ability_result (dict): Results from using an ability
        combat_state (dict): Current combat state
        console: Console for output
        
    Returns:
        dict: Combat impact results (damage, effects, etc.)
    """
    impact = {
        "damage_dealt": 0,
        "healing": 0,
        "status_effects": [],
        "position_changed": False,
        "cover_affected": False
    }
    
    # Skip if ability failed
    if not ability_result.get("success", False):
        return impact
    
    effects = ability_result.get("effects", {})
    
    # Process direct damage
    if "damage" in effects:
        damage = effects["damage"]
        impact["damage_dealt"] += damage
        
        # Apply damage to enemy
        if enemy and damage > 0:
            ignore_defense = effects.get("ignore_defense", False)
            damage_type = effects.get("damage_type", None)
            damage_result = enemy.take_damage(damage, ignore_defense=ignore_defense, damage_type=damage_type)
            
            # Update with actual damage after defenses
            impact["damage_dealt"] = damage_result.get("damage", damage)
            
            if console:
                if ignore_defense:
                    console.print(f"[green]The attack bypasses {enemy.name}'s defenses![/green]")
                    
                if damage_result.get("weakness_applied", False):
                    console.print(f"[green]Critical hit! {enemy.name} is weak against this attack![/green]")
    
    # Process multiple attacks
    if "multi_attack" in effects:
        multi_attack = effects["multi_attack"]
        hits = multi_attack.get("hits", 0)
        damage_per_hit = multi_attack.get("damage_per_hit", 0)
        
        total_damage = 0
        hit_count = 0
        
        for i in range(hits):
            hit_chance = 80  # 80% base hit chance
            
            # Apply accuracy modifiers based on combat state
            if combat_state.get("player_position") in ["flank_left", "flank_right"]:
                hit_chance += 10  # +10% from flanking
                
            if enemy and "target_zone" in combat_state:
                # Target zone accuracy penalties
                from combat import TARGET_ZONES
                target_zone = combat_state["target_zone"]
                if target_zone in TARGET_ZONES:
                    hit_chance -= TARGET_ZONES[target_zone].get("hit_difficulty", 0)
            
            # Roll for hit
            if random.randint(1, 100) <= hit_chance:
                hit_count += 1
                
                # Apply damage for this hit
                if enemy:
                    hit_result = enemy.take_damage(damage_per_hit)
                    total_damage += hit_result.get("damage", damage_per_hit)
        
        impact["damage_dealt"] += total_damage
        
        if console and hit_count > 0:
            console.print(f"[green]{hit_count} hits connect for a total of {total_damage} damage![/green]")
    
    # Process healing
    if "heal" in effects:
        healing = effects["heal"]
        impact["healing"] += healing
        
        if console and healing > 0:
            console.print(f"[green]You recover {healing} health![/green]")
    
    # Process status effects
    if "status" in effects:
        status = effects["status"]
        impact["status_effects"].append(status)
        
        # Apply status to enemy
        if enemy and status:
            duration = effects.get("status_duration", 2)
            enemy.status_effects[status] = {
                "duration": duration,
                "source": "player_ability"
            }
            
            if console:
                console.print(f"[green]Applied {status} status to {enemy.name} for {duration} turns![/green]")
    
    return impact