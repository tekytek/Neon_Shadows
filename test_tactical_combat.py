"""
Test script for the enhanced tactical combat system
"""
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

import combat
import character
from tactical_abilities import handle_tactical_ability
import combat_positioning
import combat_gadgets

def main():
    """Test the enhanced tactical combat system"""
    console = Console()
    
    console.print("[bold green]CYBERPUNK TACTICAL COMBAT SIMULATOR[/bold green]")
    console.print("[cyan]Testing advanced combat mechanics with positioning, terrain and gadgets[/cyan]")
    
    # Create test player
    player = character.Character("TestRunner", "NetRunner")
    player.level = 5
    player.stats = {
        "strength": 5,
        "intelligence": 8,
        "charisma": 4,
        "reflex": 6
    }
    player.health = 30
    player.max_health = 30
    
    # Create a test enemy
    enemy = combat.Enemy("Security Bot", 20, 3, 2, enemy_type="cybernetic")
    
    # Set up the environment - choose randomly from available environments
    environments = ["warehouse", "street", "nightclub", "corp_office", "junkyard", "cyber_den", "alley"]
    environment = random.choice(environments)
    
    # Generate terrain based on environment
    terrain_map = combat_positioning.generate_combat_terrain(environment)
    
    # Initialize a combat state
    combat_state = {
        "player_position": "center",
        "enemy_position": "center",
        "player_cover": "none",
        "enemy_cover": "none",
        "environment": environment,
        "target_zone": "torso",
        "active_hazards": [],
        "terrain_map": terrain_map,
        "current_terrain": terrain_map["center"],
        "enemy": enemy,
        "player": player,
        "player_action_points": 2,
        "enemy_action_points": 2,
        "turn_counter": 1
    }
    
    # Add abilities to the player
    player.abilities = {
        # Add NetRunner abilities
        "neural_overload": combat.CLASS_ABILITIES["NetRunner"]["neural_overload"],
        "system_glitch": combat.CLASS_ABILITIES["NetRunner"]["system_glitch"],
        "ice_breaker": combat.CLASS_ABILITIES["NetRunner"]["ice_breaker"],
        
        # Add some other class abilities for testing
        "breaching_charge": combat.CLASS_ABILITIES["Enforcer"]["breaching_charge"],
        "suppressive_fire": combat.CLASS_ABILITIES["Enforcer"]["suppressive_fire"]
    }
    
    # No cooldowns for testing
    player.ability_cooldowns = {
        "neural_overload": 0,
        "system_glitch": 0,
        "ice_breaker": 0,
        "breaching_charge": 0,
        "suppressive_fire": 0
    }
    
    # Setup combat gadget cooldowns
    combat_state["gadget_cooldowns"] = {}
    
    # Display setup information
    console.print(f"[bold]Player created:[/bold] {player.name}, class: {player.char_class}")
    console.print(f"[bold]Enemy created:[/bold] {enemy.name}, type: {enemy.enemy_type}")
    console.print(f"[bold]Combat environment:[/bold] {environment}")
    console.print(f"[bold]Starting position:[/bold] {combat_state['player_position']}")
    console.print(f"[bold]Current terrain:[/bold] {combat_state['current_terrain']}")
    
    # Display tactical information
    display_combat_state(console, combat_state)
    
    # Run combat simulation
    simulate_tactical_combat(console, combat_state)
    
    console.print("\n[bold green]Tactical combat testing complete![/bold green]")

def display_combat_state(console, combat_state):
    """Display the current tactical combat state"""
    console.print(Panel(f"[bold cyan]COMBAT STATE - Turn {combat_state.get('turn_counter', 1)}[/bold cyan]"))
    
    # Create the tactical map display
    map_table = Table(title=f"[bold]Tactical Map - {combat_state['environment'].title()}[/bold]")
    
    # Set up columns for each position
    positions = ["flank_left", "center", "flank_right"]
    for pos in positions:
        map_table.add_column(pos.replace("_", " ").title())
    
    # Create row with terrain information
    terrain_cells = []
    for pos in positions:
        terrain_type = combat_state["terrain_map"].get(pos, "open")
        terrain_info = combat_positioning.TERRAIN_TYPES.get(terrain_type, {})
        
        # Add player or enemy marker if they're at this position
        occupants = []
        if combat_state["player_position"] == pos:
            occupants.append("[bold green]P[/bold green]")
        if combat_state["enemy_position"] == pos:
            occupants.append("[bold red]E[/bold red]")
            
        occupant_str = " ".join(occupants) if occupants else ""
        
        # Check for gadgets at this position
        gadgets_at_pos = []
        if "active_gadgets" in combat_state:
            for gadget in combat_state["active_gadgets"]:
                if gadget.position == pos:
                    gadgets_at_pos.append("[bold yellow]G[/bold yellow]")
        
        gadget_str = " ".join(gadgets_at_pos) if gadgets_at_pos else ""
        
        # Combine all information
        terrain_name = terrain_info.get("name", terrain_type.title())
        cell_content = f"{terrain_name}\n{occupant_str} {gadget_str}"
        
        # Add special styling based on terrain
        if terrain_type == "hazardous":
            cell_style = "red"
        elif terrain_type == "elevated":
            cell_style = "cyan"
        elif terrain_type == "tech_rich":
            cell_style = "bright_blue"
        elif terrain_type == "shadows":
            cell_style = "dim"
        else:
            cell_style = "white"
            
        terrain_cells.append(f"[{cell_style}]{cell_content}[/{cell_style}]")
    
    map_table.add_row(*terrain_cells)
    
    # Display the map
    console.print(map_table)
    
    # Display player and enemy stats
    player = combat_state.get("player")
    enemy = combat_state.get("enemy")
    
    stats_table = Table()
    stats_table.add_column("Entity", style="bold")
    stats_table.add_column("Health", style="red")
    stats_table.add_column("Position", style="cyan")
    stats_table.add_column("Cover", style="yellow")
    stats_table.add_column("Terrain", style="green")
    stats_table.add_column("Status", style="magenta")
    
    # Player stats
    player_terrain = combat_state["terrain_map"].get(combat_state["player_position"], "open")
    player_status = ", ".join(player.status_effects.keys()) if hasattr(player, "status_effects") and player.status_effects else "None"
    
    stats_table.add_row(
        f"[bold green]{player.name} ({player.char_class})[/bold green]",
        f"{player.health}/{player.max_health}",
        combat_state["player_position"].replace("_", " ").title(),
        combat_state["player_cover"],
        player_terrain,
        player_status
    )
    
    # Enemy stats
    enemy_terrain = combat_state["terrain_map"].get(combat_state["enemy_position"], "open")
    enemy_status = ", ".join(enemy.status_effects.keys()) if hasattr(enemy, "status_effects") and enemy.status_effects else "None"
    
    stats_table.add_row(
        f"[bold red]{enemy.name} ({enemy.enemy_type})[/bold red]",
        f"{enemy.health}/{enemy.max_health}",
        combat_state["enemy_position"].replace("_", " ").title(),
        combat_state["enemy_cover"],
        enemy_terrain,
        enemy_status
    )
    
    console.print(stats_table)
    
    # Display active gadgets
    if "active_gadgets" in combat_state and combat_state["active_gadgets"]:
        gadget_table = Table(title="Active Gadgets")
        gadget_table.add_column("Name", style="yellow")
        gadget_table.add_column("Position", style="cyan")
        gadget_table.add_column("Duration", style="green")
        
        for gadget in combat_state["active_gadgets"]:
            gadget_table.add_row(
                gadget.data["name"],
                gadget.position.replace("_", " ").title(),
                str(gadget.remaining_duration)
            )
            
        console.print(gadget_table)
    
    # Display action points
    ap_text = f"Player Action Points: {combat_state.get('player_action_points', 0)} | "
    ap_text += f"Enemy Action Points: {combat_state.get('enemy_action_points', 0)}"
    console.print(f"[bold cyan]{ap_text}[/bold cyan]")

def simulate_tactical_combat(console, combat_state):
    """Simulate tactical combat with user choices"""
    turn = 1
    combat_active = True
    
    while combat_active and turn <= 10:  # Limit to 10 turns for the test
        # Update turn counter
        combat_state["turn_counter"] = turn
        
        # Display current state
        console.print("\n" + "="*60)
        console.print(f"[bold cyan]TURN {turn}[/bold cyan]")
        console.print("="*60)
        
        display_combat_state(console, combat_state)
        
        # Player's turn
        console.print("\n[bold green]Player's Turn[/bold green]")
        
        # Reset action points
        combat_state["player_action_points"] = 2
        
        # Process terrain effects
        if "current_terrain" in combat_state:
            terrain_type = combat_state["current_terrain"]
            effects = combat_positioning.apply_terrain_effects(combat_state["player"], terrain_type, console)
            
            # Check if player died from terrain
            if combat_state["player"].health <= 0:
                console.print("[bold red]You have been defeated by the hazardous environment![/bold red]")
                combat_active = False
                break
        
        # Process gadget triggers for turn start
        combat_state, trigger_results = combat_gadgets.process_gadget_triggers(
            combat_state, "turn_start", combat_state["enemy"], console
        )
        
        while combat_state["player_action_points"] > 0 and combat_active:
            # Show available actions
            console.print(f"\n[cyan]Action Points: {combat_state['player_action_points']}[/cyan]")
            console.print("[bold]Choose an action:[/bold]")
            console.print("1) Use Tactical Ability")
            console.print("2) Move to New Position")
            console.print("3) Deploy Gadget")
            console.print("4) Attack")
            console.print("5) Take Cover")
            console.print("6) Change Target Zone")
            console.print("7) End Turn")
            
            choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":  # Use Ability
                # Show available abilities
                console.print("\n[bold]Available Abilities:[/bold]")
                available_abilities = {}
                i = 1
                
                for ability_id, ability_data in player.abilities.items():
                    if player.ability_cooldowns.get(ability_id, 0) <= 0:
                        console.print(f"{i}) {ability_data['name']} - {ability_data['description']}")
                        available_abilities[str(i)] = ability_id
                        i += 1
                
                if available_abilities:
                    ability_choice = Prompt.ask("Choose ability", choices=list(available_abilities.keys()) + ["c"])
                    
                    if ability_choice != "c":
                        ability_id = available_abilities[ability_choice]
                        
                        # Use the ability
                        updated_combat_state, ability_result = handle_tactical_ability(
                            player, ability_id, enemy, combat_state, console
                        )
                        
                        # Update the combat state
                        combat_state = updated_combat_state
                        
                        # Use up an action point if ability was used successfully
                        if ability_result.get("success", False):
                            combat_state["player_action_points"] -= 1
                            
                            # Check if enemy is defeated
                            if enemy.is_defeated():
                                console.print("[bold green]Enemy defeated![/bold green]")
                                combat_active = False
                                break
                else:
                    console.print("[yellow]No abilities available (all on cooldown)[/yellow]")
            
            elif choice == "2":  # Move
                # Show available moves
                console.print("\n[bold]Available Positions:[/bold]")
                current_pos = combat_state["player_position"]
                terrain_type = combat_state["terrain_map"].get(current_pos, "open")
                
                available_moves = combat_positioning.get_tactical_move_options(
                    current_pos, combat_state["player_action_points"], terrain_type
                )
                
                move_options = {}
                i = 1
                
                for pos, cost in available_moves.items():
                    terrain = combat_state["terrain_map"].get(pos, "open")
                    terrain_info = combat_positioning.TERRAIN_TYPES.get(terrain, {})
                    
                    console.print(f"{i}) {pos.replace('_', ' ').title()} - Cost: {cost} AP, " +
                               f"Terrain: {terrain_info.get('name', terrain.title())}")
                    move_options[str(i)] = (pos, cost)
                    i += 1
                
                if move_options:
                    move_choice = Prompt.ask("Choose position to move to", choices=list(move_options.keys()) + ["c"])
                    
                    if move_choice != "c":
                        new_pos, cost = move_options[move_choice]
                        
                        # Update player position
                        combat_state["player_position"] = new_pos
                        
                        # Update current terrain
                        combat_state["current_terrain"] = combat_state["terrain_map"].get(new_pos, "open")
                        
                        # Use up action points
                        combat_state["player_action_points"] -= cost
                        
                        console.print(f"[green]Moved to {new_pos.replace('_', ' ').title()}[/green]")
                        
                        # Check for position-triggered gadgets
                        combat_state, trigger_results = combat_gadgets.process_gadget_triggers(
                            combat_state, "position_change", combat_state["player"], console
                        )
                        
                        # Check if player died from triggered gadget
                        if combat_state["player"].health <= 0:
                            console.print("[bold red]You have been defeated by a triggered gadget![/bold red]")
                            combat_active = False
                            break
                else:
                    console.print("[yellow]No moves available with current action points[/yellow]")
            
            elif choice == "3":  # Deploy Gadget
                # Show available gadgets
                console.print("\n[bold]Available Gadgets:[/bold]")
                combat_gadgets.display_available_gadgets(console, combat_state, player)
                
                gadget_id = Prompt.ask("Enter gadget ID to deploy (or 'c' to cancel)")
                
                if gadget_id != "c" and gadget_id in combat_gadgets.COMBAT_GADGETS:
                    # Deploy the gadget
                    updated_combat_state, result = combat_gadgets.deploy_gadget(
                        player, gadget_id, combat_state, console
                    )
                    
                    # Update the combat state
                    combat_state = updated_combat_state
                    
                    # Use an action point if deployment was successful
                    if result.get("success", False):
                        combat_state["player_action_points"] -= 1
                        
                        # Check if enemy was defeated by immediate gadget activation
                        if enemy.is_defeated():
                            console.print("[bold green]Enemy defeated by gadget![/bold green]")
                            combat_active = False
                            break
            
            elif choice == "4":  # Attack
                # Get flanking bonus based on positions
                flanking_bonus = combat_positioning.calculate_flanking_bonus(
                    combat_state["player_position"], combat_state["enemy_position"]
                )
                
                # Get position modifiers
                position_mods = combat_positioning.get_position_modifiers(
                    combat_state["player_position"], player.char_class, 
                    combat_state["terrain_map"].get(combat_state["player_position"], "open")
                )
                
                # Calculate damage with modifiers
                damage = 5 + position_mods["attack_bonus"] // 5  # Convert percentage to flat damage
                
                # Apply flanking bonus
                damage += int(damage * (flanking_bonus / 100))
                
                # Apply target zone modifiers
                target_zone = combat_state.get("target_zone", "torso")
                target_zone_data = getattr(combat, "TARGET_ZONES", {}).get(target_zone, {})
                damage_mult = target_zone_data.get("damage_mult", 1.0)
                damage = int(damage * damage_mult)
                
                # Roll for critical hit
                crit_chance = 5 + position_mods["crit_bonus"]
                is_critical = random.randint(1, 100) <= crit_chance
                
                if is_critical:
                    damage = int(damage * 1.5)
                    console.print("[bold yellow]Critical hit![/bold yellow]")
                
                # Apply damage to enemy
                damage_result = enemy.take_damage(damage, is_critical=is_critical)
                actual_damage = damage_result.get("damage", damage)
                
                console.print(f"[bold green]You attack the enemy's {target_zone} for {actual_damage} damage![/bold green]")
                
                # Use an action point
                combat_state["player_action_points"] -= 1
                
                # Check if enemy is defeated
                if enemy.is_defeated():
                    console.print("[bold green]Enemy defeated![/bold green]")
                    combat_active = False
                    break
            
            elif choice == "5":  # Take Cover
                # Show available cover options based on position
                console.print("\n[bold]Available Cover Options:[/bold]")
                current_pos = combat_state["player_position"]
                terrain_type = combat_state["terrain_map"].get(current_pos, "open")
                
                # Determine available cover types based on terrain
                cover_options = {
                    "1": ("light", 3),     # Light cover, 3 health
                    "2": ("medium", 5),    # Medium cover, 5 health
                }
                
                # Special terrain might offer better cover
                if terrain_type == "debris":
                    cover_options["3"] = ("heavy", 8)   # Heavy cover, 8 health
                elif terrain_type == "confined":
                    cover_options["3"] = ("full", 10)   # Full cover, 10 health
                
                for key, (cover_type, health) in cover_options.items():
                    console.print(f"{key}) {cover_type.title()} Cover - {health} health")
                
                cover_choice = Prompt.ask("Choose cover type", choices=list(cover_options.keys()) + ["c"])
                
                if cover_choice != "c":
                    cover_type, health = cover_options[cover_choice]
                    
                    # Update player cover
                    combat_state["player_cover"] = cover_type
                    combat_state["player_cover_health"] = health
                    
                    console.print(f"[green]You take {cover_type} cover with {health} health[/green]")
                    
                    # Use an action point
                    combat_state["player_action_points"] -= 1
            
            elif choice == "6":  # Change Target Zone
                # Show available target zones
                console.print("\n[bold]Available Target Zones:[/bold]")
                target_zones = getattr(combat, "TARGET_ZONES", {})
                
                zone_options = {}
                i = 1
                
                for zone, data in target_zones.items():
                    console.print(f"{i}) {zone.title()} - Damage: x{data.get('damage_mult', 1.0)}, " +
                               f"Difficulty: +{data.get('hit_difficulty', 0)}")
                    zone_options[str(i)] = zone
                    i += 1
                
                zone_choice = Prompt.ask("Choose target zone", choices=list(zone_options.keys()) + ["c"])
                
                if zone_choice != "c":
                    new_zone = zone_options[zone_choice]
                    
                    # Update target zone
                    combat_state["target_zone"] = new_zone
                    
                    console.print(f"[green]Target zone set to {new_zone.title()}[/green]")
                    
                    # This is a free action (no AP cost)
            
            elif choice == "7":  # End Turn
                break
        
        # Process gadget triggers for turn end
        combat_state, trigger_results = combat_gadgets.process_gadget_triggers(
            combat_state, "turn_end", combat_state["enemy"], console
        )
        
        # Check if enemy is defeated by end-of-turn gadget effect
        if enemy.is_defeated():
            console.print("[bold green]Enemy defeated by gadget![/bold green]")
            combat_active = False
            break
        
        # Update gadget cooldowns
        combat_state = combat_gadgets.update_gadget_cooldowns(combat_state)
        
        # Update ability cooldowns
        for ability_id, cooldown in player.ability_cooldowns.items():
            if cooldown > 0:
                player.ability_cooldowns[ability_id] = cooldown - 1
        
        # Enemy's turn (simplified for testing)
        if combat_active:
            console.print("\n[bold red]Enemy's Turn[/bold red]")
            time.sleep(1)  # Pause for effect
            
            # Reset enemy action points
            combat_state["enemy_action_points"] = 2
            
            # Simple AI for enemy
            while combat_state["enemy_action_points"] > 0 and combat_active:
                # Choose a random action weighted by effectiveness
                action_weights = {
                    "attack": 50,
                    "move": 25,
                    "take_cover": 25
                }
                
                actions = list(action_weights.keys())
                weights = [action_weights[a] for a in actions]
                
                action = random.choices(actions, weights=weights, k=1)[0]
                
                if action == "attack":
                    # Calculate damage
                    base_damage = enemy.damage
                    
                    # Get position modifiers
                    position_mods = combat_positioning.get_position_modifiers(
                        combat_state["enemy_position"], None, 
                        combat_state["terrain_map"].get(combat_state["enemy_position"], "open")
                    )
                    
                    # Apply position modifier
                    damage = base_damage + position_mods["attack_bonus"] // 10
                    
                    # Roll for critical hit
                    crit_chance = 5 + position_mods["crit_bonus"]
                    is_critical = random.randint(1, 100) <= crit_chance
                    
                    if is_critical:
                        damage = int(damage * 1.5)
                        console.print("[bold red]Critical hit![/bold red]")
                    
                    # Check for player cover
                    if combat_state["player_cover"] != "none" and combat_state["player_cover_health"] > 0:
                        # Damage goes to cover first
                        cover_damage = min(damage, combat_state["player_cover_health"])
                        combat_state["player_cover_health"] -= cover_damage
                        damage -= cover_damage
                        
                        console.print(f"[yellow]Enemy attack hits your cover for {cover_damage} damage![/yellow]")
                        
                        # Check if cover is destroyed
                        if combat_state["player_cover_health"] <= 0:
                            console.print("[red]Your cover is destroyed![/red]")
                            combat_state["player_cover"] = "none"
                    
                    # Apply remaining damage to player
                    if damage > 0:
                        player.health -= damage
                        console.print(f"[bold red]Enemy attacks for {damage} damage![/bold red]")
                        
                        # Check if player is defeated
                        if player.health <= 0:
                            console.print("[bold red]You have been defeated![/bold red]")
                            combat_active = False
                            break
                    
                    # Use an action point
                    combat_state["enemy_action_points"] -= 1
                
                elif action == "move":
                    # Get optimal position
                    optimal_position = combat_positioning.get_optimal_position(enemy, player, combat_state)
                    
                    # Move to the optimal position if different
                    if optimal_position != combat_state["enemy_position"]:
                        old_position = combat_state["enemy_position"]
                        combat_state["enemy_position"] = optimal_position
                        
                        console.print(f"[red]Enemy moves from {old_position.replace('_', ' ').title()} " +
                                   f"to {optimal_position.replace('_', ' ').title()}[/red]")
                        
                        # Use an action point
                        combat_state["enemy_action_points"] -= 1
                        
                        # Check for position-triggered gadgets
                        combat_state, trigger_results = combat_gadgets.process_gadget_triggers(
                            combat_state, "position_change", combat_state["enemy"], console
                        )
                        
                        # Check if enemy died from triggered gadget
                        if enemy.is_defeated():
                            console.print("[bold green]Enemy defeated by a triggered gadget![/bold green]")
                            combat_active = False
                            break
                    else:
                        # No good move, try something else
                        continue
                
                elif action == "take_cover":
                    # Only take cover if not already in cover
                    if combat_state["enemy_cover"] == "none":
                        # Choose a cover type
                        cover_types = ["light", "medium"]
                        cover_health = {"light": 3, "medium": 5}
                        
                        cover_type = random.choice(cover_types)
                        health = cover_health[cover_type]
                        
                        # Update enemy cover
                        combat_state["enemy_cover"] = cover_type
                        combat_state["enemy_cover_health"] = health
                        
                        console.print(f"[red]Enemy takes {cover_type} cover with {health} health[/red]")
                        
                        # Use an action point
                        combat_state["enemy_action_points"] -= 1
                    else:
                        # Already in cover, try something else
                        continue
            
            # Process enemy status effects
            status_result = enemy.process_status_effects()
            if status_result.get("messages"):
                for msg in status_result["messages"]:
                    console.print(msg)
            
            # Check if enemy died from status effects
            if enemy.is_defeated():
                console.print("[bold green]Enemy defeated by status effects![/bold green]")
                combat_active = False
        
        # Next turn
        turn += 1
    
    # Combat ended
    if turn > 10:
        console.print("[yellow]Combat test ended after 10 turns[/yellow]")
    
    if player.health <= 0:
        console.print("[bold red]You were defeated![/bold red]")
    elif enemy.is_defeated():
        console.print("[bold green]You were victorious![/bold green]")
    else:
        console.print("[yellow]Combat ended in a stalemate[/yellow]")
    
    # Show final state
    display_combat_state(console, combat_state)

if __name__ == "__main__":
    main()