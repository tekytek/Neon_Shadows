"""
Combat Gadgets Module - Handles deployable gadgets and tech items for combat
"""
import random
from rich.console import Console
from rich.panel import Panel

# Dictionary of available combat gadgets
COMBAT_GADGETS = {
    "proximity_mine": {
        "name": "Proximity Mine",
        "description": "Explosive device that detonates when enemy moves to its position",
        "damage": 12,
        "area_effect": True,
        "duration": 3,
        "cooldown": 2,
        "trigger": "position_change",
        "position_requirement": "any",
        "class_bonus": {"Tech": 4}  # Extra damage for Tech class
    },
    "med_dispenser": {
        "name": "Med Dispenser",
        "description": "Automated medical dispenser that heals over time",
        "healing": 4,
        "area_effect": False,
        "duration": 3,
        "cooldown": 3,
        "trigger": "turn_start",
        "position_requirement": "defensive",
        "class_bonus": {"Fixer": 2}  # Extra healing for Fixer class
    },
    "gun_turret": {
        "name": "Gun Turret",
        "description": "Automated turret that fires at enemies each turn",
        "damage": 5,
        "area_effect": False,
        "duration": 3,
        "cooldown": 3,
        "trigger": "turn_end",
        "position_requirement": "flank_left,flank_right",
        "class_bonus": {"Enforcer": 3}  # Extra damage for Enforcer class
    },
    "smoke_bomb": {
        "name": "Smoke Bomb",
        "description": "Creates a cloud of smoke, reducing enemy accuracy",
        "effect": "reduce_accuracy",
        "effect_value": 20,
        "area_effect": True,
        "duration": 2,
        "cooldown": 2,
        "trigger": "continuous",
        "position_requirement": "any",
        "class_bonus": {"Fixer": {"effect_value": 10}}  # Extra effect value for Fixer
    },
    "neural_scrambler": {
        "name": "Neural Scrambler",
        "description": "Device that interferes with enemy neural implants",
        "effect": "disoriented",
        "area_effect": True,
        "duration": 2,
        "cooldown": 3,
        "trigger": "turn_start",
        "position_requirement": "center",
        "class_bonus": {"NetRunner": {"duration": 1}}  # Extra duration for NetRunner
    },
    "shield_generator": {
        "name": "Shield Generator",
        "description": "Generates a protective energy shield",
        "effect": "damage_reduction",
        "effect_value": 5,
        "area_effect": False,
        "duration": 3,
        "cooldown": 3,
        "trigger": "continuous",
        "position_requirement": "defensive",
        "class_bonus": {"Tech": {"effect_value": 3}}  # Extra damage reduction for Tech
    },
    "emp_device": {
        "name": "EMP Device",
        "description": "Disables electronic equipment and cybernetic enhancements",
        "effect": "disabled",
        "area_effect": True,
        "duration": 1,
        "cooldown": 4,
        "trigger": "activation",
        "position_requirement": "any",
        "class_bonus": {"NetRunner": {"duration": 1}}  # Extra duration for NetRunner
    },
    "targeting_beacon": {
        "name": "Targeting Beacon",
        "description": "Marks the enemy, increasing hit chance and critical chance",
        "effect": "marked",
        "effect_value": {"hit_bonus": 15, "crit_bonus": 10},
        "area_effect": False,
        "duration": 2,
        "cooldown": 2,
        "trigger": "continuous",
        "position_requirement": "center,flank_left,flank_right",
        "class_bonus": {"Enforcer": {"effect_value": {"hit_bonus": 5, "crit_bonus": 5}}}  # Extra bonuses for Enforcer
    }
}

class CombatGadget:
    """Class for handling deployable combat gadgets"""
    
    def __init__(self, gadget_id, owner, position):
        """
        Initialize a combat gadget
        
        Args:
            gadget_id (str): ID of the gadget from COMBAT_GADGETS
            owner: Owner of the gadget
            position (str): Position where the gadget is deployed
        """
        if gadget_id not in COMBAT_GADGETS:
            raise ValueError(f"Unknown gadget: {gadget_id}")
            
        self.gadget_id = gadget_id
        self.data = COMBAT_GADGETS[gadget_id].copy()
        self.owner = owner
        self.position = position
        self.remaining_duration = self.data.get("duration", 1)
        self.active = True
        self.triggered_this_turn = False
        
        # Apply class bonuses if applicable
        owner_class = getattr(owner, "char_class", None)
        if owner_class and owner_class in self.data.get("class_bonus", {}):
            bonus = self.data["class_bonus"][owner_class]
            
            # Handle direct numeric bonuses
            if isinstance(bonus, (int, float)):
                # Apply to damage or healing
                if "damage" in self.data:
                    self.data["damage"] += bonus
                elif "healing" in self.data:
                    self.data["healing"] += bonus
            
            # Handle dictionary bonuses for effects
            elif isinstance(bonus, dict):
                for key, value in bonus.items():
                    if key in self.data:
                        if isinstance(self.data[key], dict) and isinstance(value, dict):
                            # Merge nested dictionaries
                            for k, v in value.items():
                                if k in self.data[key]:
                                    self.data[key][k] += v
                        else:
                            # Add to simple value
                            self.data[key] += value
    
    def can_trigger(self, trigger_type, target_position=None):
        """
        Check if the gadget can trigger on the given condition
        
        Args:
            trigger_type (str): Type of trigger
            target_position (str, optional): Position of the potential target
            
        Returns:
            bool: Whether the gadget can trigger
        """
        # Don't trigger if already triggered this turn or inactive
        if self.triggered_this_turn or not self.active:
            return False
            
        # Check if trigger type matches
        if self.data.get("trigger") != trigger_type and self.data.get("trigger") != "continuous":
            return False
            
        # For position_change triggers, check if target moved to gadget position
        if trigger_type == "position_change" and target_position != self.position:
            return False
            
        return True
    
    def trigger(self, target=None, combat_state=None, console=None):
        """
        Trigger the gadget's effect
        
        Args:
            target: Target of the gadget (if applicable)
            combat_state (dict, optional): Current combat state
            console: Console for output
            
        Returns:
            dict: Result of the gadget activation
        """
        result = {
            "triggered": True,
            "effects": [],
            "damage": 0,
            "healing": 0,
            "expired": False
        }
        
        # Mark as triggered for this turn
        self.triggered_this_turn = True
        
        # Process damage
        if "damage" in self.data and target:
            damage = self.data["damage"]
            
            # Apply damage to target
            if hasattr(target, "take_damage"):
                damage_result = target.take_damage(damage, ignore_defense=False)
                actual_damage = damage_result.get("damage", damage)
                result["damage"] = actual_damage
                
                if console:
                    console.print(f"[bold red]{self.data['name']} deals {actual_damage} damage to {target.name}![/bold red]")
        
        # Process healing
        if "healing" in self.data and self.owner:
            healing = self.data["healing"]
            
            # Apply healing to owner
            if hasattr(self.owner, "health") and hasattr(self.owner, "max_health"):
                self.owner.health = min(self.owner.max_health, self.owner.health + healing)
                result["healing"] = healing
                
                if console:
                    console.print(f"[bold green]{self.data['name']} heals {healing} health![/bold green]")
        
        # Process status effects
        if "effect" in self.data and target:
            effect = self.data["effect"]
            
            # Apply status effect to target
            if hasattr(target, "status_effects"):
                effect_duration = self.data.get("duration", 1)
                
                target.status_effects[effect] = {
                    "duration": effect_duration,
                    "source": f"gadget_{self.gadget_id}"
                }
                
                result["effects"].append(effect)
                
                if console:
                    console.print(f"[bold cyan]{self.data['name']} applies {effect} status to {target.name}![/bold cyan]")
        
        # Check for expiration
        self.remaining_duration -= 1
        if self.remaining_duration <= 0:
            self.active = False
            result["expired"] = True
            
            if console:
                console.print(f"[yellow]{self.data['name']} has expired.[/yellow]")
        
        return result
    
    def reset_trigger(self):
        """Reset the trigger flag for a new turn"""
        self.triggered_this_turn = False

def deploy_gadget(player, gadget_id, combat_state, console=None):
    """
    Deploy a combat gadget
    
    Args:
        player: Player deploying the gadget
        gadget_id (str): ID of the gadget to deploy
        combat_state (dict): Current combat state
        console: Console for output
        
    Returns:
        tuple: Updated combat state, and deployment result
    """
    result = {
        "success": False,
        "message": ""
    }
    
    # Check if gadget exists
    if gadget_id not in COMBAT_GADGETS:
        result["message"] = f"Unknown gadget: {gadget_id}"
        return combat_state, result
    
    # Get gadget data
    gadget_data = COMBAT_GADGETS[gadget_id]
    
    # Check cooldown
    gadget_cooldowns = combat_state.get("gadget_cooldowns", {})
    if gadget_id in gadget_cooldowns and gadget_cooldowns[gadget_id] > 0:
        result["message"] = f"{gadget_data['name']} is still on cooldown for {gadget_cooldowns[gadget_id]} turns"
        return combat_state, result
    
    # Check position requirement
    player_position = combat_state.get("player_position", "center")
    position_req = gadget_data.get("position_requirement", "any")
    
    if position_req != "any" and player_position not in position_req.split(","):
        result["message"] = f"{gadget_data['name']} cannot be deployed from your current position"
        return combat_state, result
    
    # Create the gadget
    gadget = CombatGadget(gadget_id, player, player_position)
    
    # Add to active gadgets in combat state
    if "active_gadgets" not in combat_state:
        combat_state["active_gadgets"] = []
        
    combat_state["active_gadgets"].append(gadget)
    
    # Set cooldown
    if "gadget_cooldowns" not in combat_state:
        combat_state["gadget_cooldowns"] = {}
        
    combat_state["gadget_cooldowns"][gadget_id] = gadget_data.get("cooldown", 2)
    
    # Success message
    result["success"] = True
    result["message"] = f"Deployed {gadget_data['name']} at {player_position} position"
    
    if console:
        console.print(Panel(f"[bold green]{result['message']}[/bold green]"))
        console.print(f"[cyan]{gadget_data['description']}[/cyan]")
    
    # Immediate activation for 'activation' trigger gadgets
    if gadget_data.get("trigger") == "activation":
        if "enemy" in combat_state:
            enemy = combat_state["enemy"]
            trigger_result = gadget.trigger(enemy, combat_state, console)
            result["trigger_result"] = trigger_result
    
    return combat_state, result

def process_gadget_triggers(combat_state, trigger_type, target=None, console=None):
    """
    Process all gadgets that should trigger on the given condition
    
    Args:
        combat_state (dict): Current combat state
        trigger_type (str): Type of trigger event
        target: Target for gadget effects (optional)
        console: Console for output
        
    Returns:
        tuple: Updated combat state, and trigger results
    """
    results = []
    
    # Skip if no active gadgets
    if "active_gadgets" not in combat_state:
        return combat_state, results
    
    target_position = getattr(target, "position", None)
    
    # Check each gadget
    for gadget in combat_state["active_gadgets"]:
        if gadget.can_trigger(trigger_type, target_position):
            result = gadget.trigger(target, combat_state, console)
            results.append({
                "gadget_id": gadget.gadget_id,
                "gadget_name": gadget.data["name"],
                "result": result
            })
    
    # Remove expired gadgets
    combat_state["active_gadgets"] = [g for g in combat_state["active_gadgets"] if g.active]
    
    return combat_state, results

def update_gadget_cooldowns(combat_state):
    """
    Update the cooldowns of all gadgets
    
    Args:
        combat_state (dict): Current combat state
        
    Returns:
        dict: Updated combat state
    """
    if "gadget_cooldowns" not in combat_state:
        return combat_state
        
    # Reduce all cooldowns by 1, remove if 0
    updated_cooldowns = {}
    for gadget_id, cooldown in combat_state["gadget_cooldowns"].items():
        if cooldown > 1:
            updated_cooldowns[gadget_id] = cooldown - 1
    
    combat_state["gadget_cooldowns"] = updated_cooldowns
    
    # Reset trigger flags for active gadgets
    if "active_gadgets" in combat_state:
        for gadget in combat_state["active_gadgets"]:
            gadget.reset_trigger()
    
    return combat_state

def display_available_gadgets(console, combat_state, player):
    """
    Display a list of gadgets available to the player
    
    Args:
        console: Console for output
        combat_state (dict): Current combat state
        player: Player character
    """
    from rich.table import Table
    
    table = Table(title="Available Combat Gadgets")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Effect", style="yellow")
    table.add_column("Cooldown", style="red")
    
    player_class = getattr(player, "char_class", None)
    
    # Get current cooldowns
    cooldowns = combat_state.get("gadget_cooldowns", {})
    
    for gadget_id, data in COMBAT_GADGETS.items():
        # Skip if on cooldown
        current_cooldown = cooldowns.get(gadget_id, 0)
        if current_cooldown > 0:
            continue
            
        # Check player position requirements
        player_position = combat_state.get("player_position", "center")
        position_req = data.get("position_requirement", "any")
        
        if position_req != "any" and player_position not in position_req.split(","):
            continue
        
        # Determine effect text
        effect_text = ""
        if "damage" in data:
            damage_value = data["damage"]
            
            # Apply class bonus if applicable
            if player_class and player_class in data.get("class_bonus", {}) and isinstance(data["class_bonus"][player_class], (int, float)):
                damage_value += data["class_bonus"][player_class]
                
            effect_text = f"Damage: {damage_value}"
        elif "healing" in data:
            healing_value = data["healing"]
            
            # Apply class bonus if applicable
            if player_class and player_class in data.get("class_bonus", {}) and isinstance(data["class_bonus"][player_class], (int, float)):
                healing_value += data["class_bonus"][player_class]
                
            effect_text = f"Healing: {healing_value}"
        elif "effect" in data:
            effect_text = f"Effect: {data['effect']}"
            
            if "effect_value" in data:
                if isinstance(data["effect_value"], dict):
                    effect_values = []
                    for k, v in data["effect_value"].items():
                        effect_values.append(f"{k.replace('_', ' ').title()}: {v}")
                    effect_text += f" ({', '.join(effect_values)})"
                else:
                    effect_text += f" ({data['effect_value']})"
        
        # Add duration
        if "duration" in data:
            duration_value = data["duration"]
            
            # Apply class bonus if applicable
            if player_class and player_class in data.get("class_bonus", {}) and isinstance(data["class_bonus"][player_class], dict) and "duration" in data["class_bonus"][player_class]:
                duration_value += data["class_bonus"][player_class]["duration"]
                
            effect_text += f", Duration: {duration_value} turns"
        
        table.add_row(
            gadget_id,
            data["name"],
            data["description"],
            effect_text,
            str(data.get("cooldown", 0))
        )
    
    console.print(table)

def gadget_help(console):
    """Display help information about gadgets"""
    console.print(Panel("[bold]Combat Gadgets Help[/bold]"))
    console.print("Combat gadgets are deployable tech items that provide tactical advantages in combat.")
    console.print("Each gadget has specific position requirements, effects, and cooldowns.")
    console.print()
    
    console.print("[bold]Gadget Types:[/bold]")
    console.print("- [cyan]Damage Gadgets:[/cyan] Deal damage to enemies (e.g., Proximity Mine, Gun Turret)")
    console.print("- [green]Support Gadgets:[/green] Heal or provide buffs (e.g., Med Dispenser, Shield Generator)")
    console.print("- [yellow]Control Gadgets:[/yellow] Apply status effects (e.g., Smoke Bomb, Neural Scrambler)")
    console.print()
    
    console.print("[bold]Trigger Types:[/bold]")
    console.print("- [red]Activation:[/red] Triggered immediately when deployed")
    console.print("- [blue]Turn Start:[/blue] Triggered at the start of your turn")
    console.print("- [blue]Turn End:[/blue] Triggered at the end of your turn")
    console.print("- [blue]Position Change:[/blue] Triggered when an enemy moves to the gadget's position")
    console.print("- [blue]Continuous:[/blue] Effect applies continuously while gadget is active")
    console.print()
    
    console.print("[bold]Class Bonuses:[/bold]")
    console.print("Each character class gets bonuses with certain gadgets:")
    console.print("- [cyan]NetRunner:[/cyan] Enhanced Neural Scrambler and EMP Device")
    console.print("- [red]Enforcer:[/red] Enhanced Gun Turret and Targeting Beacon")
    console.print("- [green]Fixer:[/green] Enhanced Med Dispenser and Smoke Bomb")
    console.print("- [yellow]Tech:[/yellow] Enhanced Proximity Mine and Shield Generator")