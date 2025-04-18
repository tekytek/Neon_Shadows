"""
Combat Positioning Module - Handles advanced positioning and terrain interactions in combat
"""
import random
from rich.console import Console
from rich.table import Table

# Constants for terrain types and their effects
TERRAIN_TYPES = {
    "open": {
        "name": "Open Ground",
        "description": "Exposed area with no natural cover",
        "move_penalty": 0,
        "cover_bonus": 0,
        "special_effect": None
    },
    "debris": {
        "name": "Debris Field",
        "description": "Scattered debris that can be used for partial cover",
        "move_penalty": 1,
        "cover_bonus": 1,
        "special_effect": "can_create_cover"
    },
    "elevated": {
        "name": "Elevated Position",
        "description": "Higher ground providing tactical advantage",
        "move_penalty": 0,
        "cover_bonus": 1,
        "special_effect": "accuracy_bonus"
    },
    "confined": {
        "name": "Confined Space",
        "description": "Narrow area limiting movement but offering protection",
        "move_penalty": 2,
        "cover_bonus": 2,
        "special_effect": "limited_flanking"
    },
    "hazardous": {
        "name": "Hazardous Zone",
        "description": "Area with dangerous elements that can cause damage",
        "move_penalty": 1,
        "cover_bonus": 0,
        "special_effect": "damage_per_turn"
    },
    "tech_rich": {
        "name": "Tech-Rich Area",
        "description": "Area with hackable technology for netrunners",
        "move_penalty": 0,
        "cover_bonus": 0,
        "special_effect": "netrunner_bonus"
    },
    "shadows": {
        "name": "Shadows",
        "description": "Darkened area offering stealth advantages",
        "move_penalty": 0,
        "cover_bonus": 0,
        "special_effect": "stealth_bonus"
    }
}

# Position advantage modifiers
POSITION_ADVANTAGES = {
    "flank_left": {
        "name": "Left Flank",
        "attack_bonus": 15,
        "defense_penalty": 0,
        "crit_bonus": 5,
        "description": "Attacking from the left side gives better angle"
    },
    "flank_right": {
        "name": "Right Flank",
        "attack_bonus": 15,
        "defense_penalty": 0,
        "crit_bonus": 5,
        "description": "Attacking from the right side gives better angle"
    },
    "aggressive": {
        "name": "Aggressive Stance",
        "attack_bonus": 20,
        "defense_penalty": 10,
        "crit_bonus": 10,
        "description": "Close-in aggressive position for maximum damage"
    },
    "defensive": {
        "name": "Defensive Position",
        "attack_bonus": -5,
        "defense_penalty": -15,  # Negative penalty = bonus
        "crit_bonus": 0,
        "description": "Cautious position prioritizing defense"
    },
    "center": {
        "name": "Center Position",
        "attack_bonus": 0,
        "defense_penalty": 0,
        "crit_bonus": 0,
        "description": "Balanced position with no special modifiers"
    }
}

# Movement costs between positions
MOVEMENT_COSTS = {
    "center": {
        "flank_left": 1,
        "flank_right": 1,
        "aggressive": 2,
        "defensive": 1,
        "center": 0
    },
    "flank_left": {
        "center": 1,
        "flank_right": 3,
        "aggressive": 2,
        "defensive": 2,
        "flank_left": 0
    },
    "flank_right": {
        "center": 1,
        "flank_left": 3,
        "aggressive": 2,
        "defensive": 2,
        "flank_right": 0
    },
    "aggressive": {
        "center": 1,
        "flank_left": 2,
        "flank_right": 2,
        "defensive": 3,
        "aggressive": 0
    },
    "defensive": {
        "center": 1,
        "flank_left": 2,
        "flank_right": 2,
        "aggressive": 3,
        "defensive": 0
    }
}

def get_tactical_move_options(current_position, action_points=2, terrain=None):
    """
    Get available positions that can be moved to with current action points
    
    Args:
        current_position (str): Current position of the character
        action_points (int): Number of action points available
        terrain (str, optional): Current terrain type
        
    Returns:
        dict: Dictionary of available positions and their cost
    """
    available_moves = {}
    
    # Get base movement costs from current position
    base_costs = MOVEMENT_COSTS.get(current_position, {})
    
    # Apply terrain movement penalty
    terrain_penalty = 0
    if terrain and terrain in TERRAIN_TYPES:
        terrain_penalty = TERRAIN_TYPES[terrain].get("move_penalty", 0)
    
    # Check each potential move
    for target_pos, cost in base_costs.items():
        # Skip current position
        if target_pos == current_position:
            continue
            
        # Apply terrain penalty
        adjusted_cost = cost + terrain_penalty
        
        # Check if move is possible with current action points
        if adjusted_cost <= action_points:
            available_moves[target_pos] = adjusted_cost
            
    return available_moves

def get_position_modifiers(position, character_class=None, terrain=None):
    """
    Get combat modifiers based on position, class and terrain
    
    Args:
        position (str): Current position
        character_class (str, optional): Character class
        terrain (str, optional): Current terrain type
        
    Returns:
        dict: Dictionary of modifiers
    """
    modifiers = {
        "attack_bonus": 0,
        "defense_bonus": 0,
        "crit_bonus": 0,
        "special_effects": []
    }
    
    # Apply position modifiers
    if position in POSITION_ADVANTAGES:
        pos_data = POSITION_ADVANTAGES[position]
        modifiers["attack_bonus"] += pos_data.get("attack_bonus", 0)
        modifiers["defense_bonus"] -= pos_data.get("defense_penalty", 0)  # Negative penalty = bonus
        modifiers["crit_bonus"] += pos_data.get("crit_bonus", 0)
    
    # Apply terrain effects
    if terrain and terrain in TERRAIN_TYPES:
        terrain_data = TERRAIN_TYPES[terrain]
        modifiers["defense_bonus"] += terrain_data.get("cover_bonus", 0) * 5  # Each cover point is worth 5% defense
        
        # Add special terrain effects
        special_effect = terrain_data.get("special_effect")
        if special_effect:
            modifiers["special_effects"].append(special_effect)
            
            # Apply class-specific terrain bonuses
            if special_effect == "netrunner_bonus" and character_class == "NetRunner":
                modifiers["attack_bonus"] += 10
            elif special_effect == "stealth_bonus" and character_class == "Fixer":
                modifiers["crit_bonus"] += 15
    
    return modifiers

def calculate_flanking_bonus(attacker_position, defender_position):
    """
    Calculate bonus for flanking based on relative positions
    
    Args:
        attacker_position (str): Position of the attacker
        defender_position (str): Position of the defender
        
    Returns:
        int: Flanking bonus percentage
    """
    # No flanking bonus if both are in the same position type
    if attacker_position == defender_position:
        return 0
        
    # Maximum flanking advantage when attacking defensive from aggressive
    if attacker_position == "aggressive" and defender_position == "defensive":
        return 25
        
    # Good flanking when on opposite flanks
    if (attacker_position == "flank_left" and defender_position == "flank_right") or \
       (attacker_position == "flank_right" and defender_position == "flank_left"):
        return 20
        
    # Moderate flanking in other position mismatches
    if ((attacker_position in ["flank_left", "flank_right"]) and defender_position == "center") or \
       (attacker_position == "aggressive" and defender_position == "center"):
        return 10
        
    # Default small advantage for any position mismatch
    return 5

def display_tactical_position_info(console, position, terrain=None):
    """
    Display information about a tactical position
    
    Args:
        console: Console for output
        position (str): Current position
        terrain (str, optional): Current terrain type
    """
    pos_data = POSITION_ADVANTAGES.get(position, {"name": "Unknown", "description": "No data available"})
    
    table = Table(title=f"[bold cyan]Position: {pos_data['name']}[/bold cyan]")
    table.add_column("Attribute", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Description", pos_data.get("description", ""))
    table.add_row("Attack Bonus", f"{pos_data.get('attack_bonus', 0)}%")
    
    defense_mod = -pos_data.get("defense_penalty", 0)
    table.add_row("Defense Bonus", f"{defense_mod}%")
    
    table.add_row("Critical Hit Bonus", f"{pos_data.get('crit_bonus', 0)}%")
    
    # Add terrain info if provided
    if terrain and terrain in TERRAIN_TYPES:
        terrain_data = TERRAIN_TYPES[terrain]
        table.add_row("", "")
        table.add_row("[bold]Terrain[/bold]", f"[bold]{terrain_data['name']}[/bold]")
        table.add_row("Description", terrain_data.get("description", ""))
        table.add_row("Movement Penalty", f"{terrain_data.get('move_penalty', 0)} AP")
        table.add_row("Cover Bonus", f"{terrain_data.get('cover_bonus', 0) * 5}%")
        
        special = terrain_data.get("special_effect")
        if special:
            table.add_row("Special Effect", special.replace("_", " ").title())
    
    console.print(table)

def get_optimal_position(character, enemy, combat_state):
    """
    Calculate the optimal position for a character against an enemy
    
    Args:
        character: Character seeking optimal position
        enemy: Enemy being fought
        combat_state: Current combat state
        
    Returns:
        str: Name of the optimal position
    """
    char_class = getattr(character, "char_class", None)
    current_position = getattr(character, "position", "center")
    enemy_position = getattr(enemy, "position", "center")
    terrain = combat_state.get("terrain", "open")
    
    # Class-specific preferences
    class_position_preferences = {
        "NetRunner": ["center", "defensive"],      # NetRunners prefer safety
        "Enforcer": ["aggressive", "center"],      # Enforcers like to get in close
        "Fixer": ["flank_left", "flank_right"],    # Fixers prefer flanking
        "Tech": ["defensive", "center"]            # Techs prefer safety
    }
    
    # Score each position
    position_scores = {}
    for position in POSITION_ADVANTAGES.keys():
        score = 0
        
        # Get position modifiers
        mods = get_position_modifiers(position, char_class, terrain)
        
        # Add scores for the modifiers
        score += mods["attack_bonus"] * 0.5
        score += mods["defense_bonus"] * 0.3
        score += mods["crit_bonus"] * 0.2
        
        # Add flanking bonus
        flanking_bonus = calculate_flanking_bonus(position, enemy_position)
        score += flanking_bonus * 0.5
        
        # Preference for class-specific positions
        if char_class in class_position_preferences:
            preferences = class_position_preferences[char_class]
            if position in preferences:
                score += 10 * (len(preferences) - preferences.index(position))
        
        # Movement cost penalty
        move_cost = MOVEMENT_COSTS.get(current_position, {}).get(position, 3)
        score -= move_cost * 5
        
        # Store the score
        position_scores[position] = score
    
    # Return highest scoring position
    if position_scores:
        return max(position_scores, key=position_scores.get)
    
    return current_position

def apply_terrain_effects(character, terrain, console=None):
    """
    Apply effects from terrain to a character
    
    Args:
        character: Character to apply effects to
        terrain (str): Type of terrain
        console: Console for output
        
    Returns:
        dict: Effects applied
    """
    effects = {"damage": 0, "bonuses": [], "penalties": []}
    
    if terrain not in TERRAIN_TYPES:
        return effects
        
    terrain_data = TERRAIN_TYPES[terrain]
    special_effect = terrain_data.get("special_effect", None)
    
    # Apply damage from hazardous terrain
    if special_effect == "damage_per_turn":
        damage = random.randint(1, 3)
        # Check if character has health attribute
        if hasattr(character, "health") and hasattr(character, "max_health"):
            character.health -= damage
            effects["damage"] = damage
            
            if console:
                console.print(f"[bold red]Hazardous terrain causes {damage} damage![/bold red]")
    
    # Apply netrunner bonus
    if special_effect == "netrunner_bonus" and getattr(character, "char_class", "") == "NetRunner":
        effects["bonuses"].append("netrunner_terrain")
        
        if console:
            console.print("[bold cyan]The tech-rich environment enhances your netrunning abilities![/bold cyan]")
    
    # Apply stealth bonus
    if special_effect == "stealth_bonus" and getattr(character, "combat_stance", "") == "stealth":
        effects["bonuses"].append("enhanced_stealth")
        
        if console:
            console.print("[bold cyan]The shadows enhance your stealth capabilities![/bold cyan]")
    
    return effects

def generate_combat_terrain(environment):
    """
    Generate terrain layout for combat based on environment
    
    Args:
        environment (str): Combat environment type
        
    Returns:
        dict: Terrain layout for combat area
    """
    # Default terrain is open
    terrain_map = {
        "center": "open",
        "flank_left": "open",
        "flank_right": "open",
        "aggressive": "open",
        "defensive": "open"
    }
    
    # Environment-specific terrain
    if environment == "warehouse":
        terrain_map = {
            "center": "open",
            "flank_left": "debris",
            "flank_right": "debris",
            "aggressive": "confined",
            "defensive": "elevated"
        }
    elif environment == "street":
        terrain_map = {
            "center": "open",
            "flank_left": "debris",
            "flank_right": "debris",
            "aggressive": "hazardous",
            "defensive": "elevated"
        }
    elif environment == "nightclub":
        terrain_map = {
            "center": "open",
            "flank_left": "shadows",
            "flank_right": "tech_rich",
            "aggressive": "confined",
            "defensive": "elevated"
        }
    elif environment == "corp_office":
        terrain_map = {
            "center": "tech_rich",
            "flank_left": "open",
            "flank_right": "open",
            "aggressive": "confined",
            "defensive": "elevated"
        }
    elif environment == "junkyard":
        terrain_map = {
            "center": "hazardous",
            "flank_left": "debris",
            "flank_right": "debris",
            "aggressive": "hazardous",
            "defensive": "elevated"
        }
    elif environment == "cyber_den":
        terrain_map = {
            "center": "tech_rich",
            "flank_left": "shadows",
            "flank_right": "confined",
            "aggressive": "debris",
            "defensive": "tech_rich"
        }
    elif environment == "alley":
        terrain_map = {
            "center": "confined",
            "flank_left": "shadows",
            "flank_right": "shadows",
            "aggressive": "hazardous",
            "defensive": "debris"
        }
    
    return terrain_map