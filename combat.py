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

# Define combat stances
STANCES = {
    "offensive": {
        "name": "Offensive",
        "damage_mod": 1.3,
        "defense_mod": 0.7,
        "crit_chance_mod": 10,
        "description": "Increases damage dealt but reduces defense"
    },
    "defensive": {
        "name": "Defensive",
        "damage_mod": 0.7,
        "defense_mod": 1.5,
        "counter_chance": 20,
        "description": "Reduces damage dealt but increases defense and enables counter-attacks"
    },
    "tactical": {
        "name": "Tactical",
        "damage_mod": 1.0,
        "defense_mod": 1.0,
        "analyze_bonus": True,
        "description": "Balanced stance that allows analyzing enemies and tactical advantages"
    },
    "stealth": {
        "name": "Stealth",
        "damage_mod": 1.5,
        "defense_mod": 0.6,
        "first_hit_bonus": True,
        "description": "High damage on first hit with chance to avoid detection, but low defense if detected"
    }
}

# Define status effects
STATUS_EFFECTS = {
    "bleeding": {
        "name": "Bleeding",
        "damage_per_turn": 2,
        "duration": 3,
        "description": "Taking damage over time"
    },
    "stunned": {
        "name": "Stunned",
        "skip_turn": True,
        "duration": 1,
        "description": "Skip next turn"
    },
    "weakened": {
        "name": "Weakened",
        "damage_mod": 0.7,
        "duration": 2,
        "description": "Reduced damage output"
    },
    "vulnerable": {
        "name": "Vulnerable",
        "defense_mod": 0.7,
        "duration": 2,
        "description": "Reduced defense"
    },
    "strengthened": {
        "name": "Strengthened",
        "damage_mod": 1.3,
        "duration": 2,
        "description": "Increased damage output"
    },
    "protected": {
        "name": "Protected",
        "defense_mod": 1.3,
        "duration": 2,
        "description": "Increased defense"
    },
    "focused": {
        "name": "Focused",
        "crit_mod": 15,
        "duration": 2,
        "description": "Increased critical hit chance"
    }
}

# Define special abilities by class
CLASS_ABILITIES = {
    "NetRunner": {
        "system_shock": {
            "name": "System Shock",
            "damage_multiplier": 1.5,
            "status_effect": "stunned",
            "cooldown": 3,
            "description": "Hack enemy systems to deal bonus damage and stun them"
        },
        "firewall": {
            "name": "Firewall",
            "defense_boost": 5,
            "duration": 2,
            "cooldown": 4,
            "description": "Create digital protection that boosts defense"
        },
        "backdoor": {
            "name": "Backdoor",
            "status_effect": "vulnerable",
            "cooldown": 3,
            "description": "Exploit weaknesses to make the enemy vulnerable"
        }
    },
    "Solo": {
        "rapid_fire": {
            "name": "Rapid Fire",
            "attacks": 3,
            "damage_multiplier": 0.6,
            "cooldown": 4,
            "description": "Fire multiple times in quick succession"
        },
        "adrenaline_surge": {
            "name": "Adrenaline Surge",
            "self_heal": 10,
            "status_effect": "strengthened",
            "cooldown": 5,
            "description": "Surge of adrenaline heals and strengthens"
        },
        "precision_shot": {
            "name": "Precision Shot",
            "damage_multiplier": 2.0,
            "ignore_defense": True,
            "cooldown": 3,
            "description": "Carefully aimed shot that ignores defense"
        }
    },
    "Fixer": {
        "analyze_weakness": {
            "name": "Analyze Weakness",
            "reveal_weakness": True,
            "status_effect": "vulnerable",
            "cooldown": 3,
            "description": "Identify and expose enemy weaknesses"
        },
        "smooth_talk": {
            "name": "Smooth Talk",
            "escape_boost": 40,
            "cooldown": 4,
            "description": "Greatly increase chance to escape combat"
        },
        "street_medicine": {
            "name": "Street Medicine",
            "self_heal": 15,
            "remove_status": True,
            "cooldown": 4,
            "description": "Apply street medicine to heal and remove negative status effects"
        }
    },
    "Techie": {
        "deploy_drone": {
            "name": "Deploy Drone",
            "bonus_damage": 3,
            "duration": 3,
            "cooldown": 4,
            "description": "Deploy combat drone that deals additional damage each turn"
        },
        "overcharge": {
            "name": "Overcharge",
            "damage_multiplier": 1.8,
            "self_damage": 3,
            "cooldown": 3,
            "description": "Overcharge your weapon for massive damage, but hurts yourself"
        },
        "jury_rig": {
            "name": "Jury Rig",
            "self_heal": 8,
            "status_effect": "protected",
            "cooldown": 3,
            "description": "Quickly repair your gear for healing and protection"
        }
    }
}

# Define cover types
COVER_TYPES = {
    "none": {
        "name": "No Cover",
        "defense_bonus": 0,
        "description": "Fully exposed"
    },
    "light": {
        "name": "Light Cover",
        "defense_bonus": 2,
        "description": "Partially obscured by light barriers"
    },
    "medium": {
        "name": "Medium Cover",
        "defense_bonus": 4,
        "description": "Protected by substantial cover"
    },
    "heavy": {
        "name": "Heavy Cover",
        "defense_bonus": 6,
        "description": "Well fortified position"
    }
}

class Enemy:
    """Enemy class for combat encounters"""
    
    def __init__(self, name, health, damage, defense, enemy_type="standard", weaknesses=None, resistances=None):
        """Initialize an enemy"""
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.defense = defense
        self.weaknesses = weaknesses or []
        self.resistances = resistances or []
        self.status_effects = {}
        self.enemy_type = enemy_type
        self.current_stance = "offensive"
        self.current_cover = "none"
        self.analyzed = False  # Track if player has analyzed this enemy
        
        # Set type-specific attributes
        if enemy_type == "berserker":
            self.damage += 2
            self.defense -= 1
            self.behavior_pattern = "aggressive"
        elif enemy_type == "tactician":
            self.defense += 2
            self.behavior_pattern = "adaptive"
        elif enemy_type == "tank":
            self.health += 5
            self.max_health += 5
            self.defense += 3
            self.damage -= 1
            self.behavior_pattern = "defensive"
        elif enemy_type == "rogue":
            self.damage += 1
            self.behavior_pattern = "evasive"
        else:
            self.behavior_pattern = "standard"
    
    @classmethod
    def from_enemy_data(cls, enemy_name, enemy_data):
        """Create an enemy from data loaded from enemies.json"""
        return cls(
            name=enemy_name,
            health=enemy_data.get("health", 10),
            damage=enemy_data.get("damage", 3),
            defense=enemy_data.get("defense", 0),
            enemy_type=enemy_data.get("enemy_type", "standard"),
            weaknesses=enemy_data.get("weaknesses", []),
            resistances=enemy_data.get("resistances", [])
        )
    
    def take_damage(self, amount, ignore_defense=False, is_critical=False, damage_type=None):
        """Apply damage to the enemy, considering defense, status, weaknesses and resistances
        
        Args:
            amount (int): Base damage amount
            ignore_defense (bool): Whether to ignore enemy defense
            is_critical (bool): Whether this is a critical hit
            damage_type (str, optional): Type of damage (e.g., 'physical', 'hacking', 'emp')
            
        Returns:
            int: Actual damage dealt
        """
        # Check if defense should be ignored (e.g., precision attacks)
        defense_value = 0 if ignore_defense else self.defense
        
        # Apply vulnerabilities
        if "vulnerable" in self.status_effects:
            defense_value = int(defense_value * STATUS_EFFECTS["vulnerable"]["defense_mod"])
        
        # Apply cover bonus
        if hasattr(self, "current_cover"):
            defense_value += COVER_TYPES[self.current_cover]["defense_bonus"]
        
        # Calculate actual damage
        actual_damage = max(1, amount - defense_value)
        
        # Apply damage type modifiers (weaknesses and resistances)
        damage_multiplier = 1.0
        weakness_applied = False
        resistance_applied = False
        
        if damage_type:
            # Check for weakness to this damage type
            if damage_type in self.weaknesses:
                # 50% more damage against weaknesses
                damage_multiplier *= 1.5
                weakness_applied = True
                
            # Check for resistance to this damage type
            if damage_type in self.resistances:
                # 30% less damage against resistances
                damage_multiplier *= 0.7
                resistance_applied = True
        
        # Apply damage type multiplier
        actual_damage = int(actual_damage * damage_multiplier)
        
        # Critical hits deal 50% more damage
        if is_critical:
            actual_damage = int(actual_damage * 1.5)
            
        # Apply damage and return the amount dealt
        self.health = max(0, self.health - actual_damage)
        
        # Return damage and information about weaknesses/resistances
        return {
            "damage": actual_damage,
            "weakness_applied": weakness_applied,
            "resistance_applied": resistance_applied
        }
    
    def is_defeated(self):
        """Check if the enemy is defeated"""
        return self.health <= 0
    
    def attack(self, target_stance="offensive"):
        """Generate an attack from the enemy"""
        # Apply stance modifiers
        stance_mod = STANCES[self.current_stance]["damage_mod"]
        
        # Check for weakened status
        status_mod = 1.0
        if "weakened" in self.status_effects:
            status_mod = STATUS_EFFECTS["weakened"]["damage_mod"]
        
        # Check for strengthened status
        if "strengthened" in self.status_effects:
            status_mod = STATUS_EFFECTS["strengthened"]["damage_mod"]
        
        # Base damage with slight randomization
        damage_mod = random.uniform(0.8, 1.2)
        base_damage = self.damage * damage_mod * stance_mod * status_mod
        
        # Check for critical hit (10% chance)
        is_critical = random.randint(1, 100) <= 10
        if is_critical:
            base_damage *= 1.5
            
        # Return damage details
        return {
            "damage": round(base_damage),
            "critical": is_critical
        }
    
    def choose_action(self, player):
        """AI decision making based on behavior pattern"""
        # Update stance based on behavior pattern and current situation
        if self.behavior_pattern == "aggressive":
            # Berserkers favor offensive stance, especially when wounded
            if self.health < self.max_health * 0.3:
                self.current_stance = "offensive"  # Go all out when close to death
            elif random.random() < 0.8:  # 80% chance to stay offensive
                self.current_stance = "offensive"
            else:
                self.current_stance = "tactical"
                
        elif self.behavior_pattern == "defensive":
            # Tanks prefer defensive stance
            if self.health < self.max_health * 0.5:
                self.current_stance = "defensive"  # More defensive when wounded
            elif random.random() < 0.7:  # 70% chance to stay defensive
                self.current_stance = "defensive"
            else:
                self.current_stance = "tactical"
                
        elif self.behavior_pattern == "adaptive":
            # Tacticians counter the player's stance
            if player.combat_stance == "offensive":
                self.current_stance = "defensive"  # Counter offensive with defensive
            elif player.combat_stance == "defensive":
                self.current_stance = "tactical"   # Counter defensive with tactical
            else:
                self.current_stance = "offensive"  # Counter tactical with offensive
                
        elif self.behavior_pattern == "evasive":
            # Rogues prefer stealth and tactical
            if self.health < self.max_health * 0.4:
                if random.random() < 0.6:
                    self.current_stance = "stealth"  # Try to hide when wounded
                else:
                    self.current_stance = "tactical"
            elif random.random() < 0.6:
                self.current_stance = "stealth"
            else:
                self.current_stance = "tactical"
                
        else:  # standard
            # Randomly choose with some weighting
            stances = ["offensive", "defensive", "tactical"]
            weights = [0.4, 0.3, 0.3]
            self.current_stance = random.choices(stances, weights=weights, k=1)[0]
        
        # Choose cover if available (simulated)
        cover_choices = ["none", "light", "medium", "heavy"]
        cover_weights = [0.4, 0.3, 0.2, 0.1]  # Heavier cover is rarer
        self.current_cover = random.choices(cover_choices, weights=cover_weights, k=1)[0]
        
        return {
            "stance": self.current_stance,
            "cover": self.current_cover
        }
    
    def process_status_effects(self):
        """Process all active status effects and return messages"""
        messages = []
        status_to_remove = []
        
        for status, data in self.status_effects.items():
            effect = STATUS_EFFECTS[status]
            
            # Decrement duration
            self.status_effects[status]["turns"] -= 1
            
            # Apply effect
            if status == "bleeding":
                damage = effect["damage_per_turn"]
                self.health = max(0, self.health - damage)
                messages.append(f"{self.name} takes {damage} bleeding damage")
                
            # Check if status has expired
            if self.status_effects[status]["turns"] <= 0:
                status_to_remove.append(status)
                messages.append(f"{self.name} is no longer {effect['name'].lower()}")
        
        # Remove expired statuses
        for status in status_to_remove:
            del self.status_effects[status]
            
        return messages

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

def display_stance_info(console, stance):
    """Display information about a combat stance"""
    stance_data = STANCES[stance]
    console.print(f"[{COLORS['secondary']}]{stance_data['name']} Stance:[/{COLORS['secondary']}] {stance_data['description']}")
    
    # Show stance modifiers
    mods = []
    if 'damage_mod' in stance_data:
        mod_text = "+" if stance_data['damage_mod'] > 1 else "-"
        percent = abs(int((stance_data['damage_mod'] - 1) * 100))
        mods.append(f"{mod_text}{percent}% damage")
        
    if 'defense_mod' in stance_data:
        mod_text = "+" if stance_data['defense_mod'] > 1 else "-"
        percent = abs(int((stance_data['defense_mod'] - 1) * 100))
        mods.append(f"{mod_text}{percent}% defense")
        
    if 'crit_chance_mod' in stance_data:
        mods.append(f"+{stance_data['crit_chance_mod']}% crit chance")
        
    if 'counter_chance' in stance_data:
        mods.append(f"{stance_data['counter_chance']}% counter chance")
    
    if mods:
        console.print(f"[{COLORS['text']}]Effects: {', '.join(mods)}[/{COLORS['text']}]")

def display_cover_info(console, cover):
    """Display information about cover level"""
    cover_data = COVER_TYPES[cover]
    console.print(f"[{COLORS['secondary']}]Cover: {cover_data['name']}[/{COLORS['secondary']}] - {cover_data['description']}")
    
    if cover_data['defense_bonus'] > 0:
        console.print(f"[{COLORS['text']}]Defense bonus: +{cover_data['defense_bonus']}[/{COLORS['text']}]")

def run_combat(console, player, enemy, player_damage_multiplier=1.0, use_animations=True, audio_system=None):
    """Run a complete combat encounter"""
    # Initialize combat
    turn = 1
    combat_active = True
    result = None
    
    # Play combat music if audio system is available
    if audio_system:
        audio_system.stop_music()
        audio_system.play_music("cyberpunk_combat")
    
    # Set initial cover for player and enemy
    player.current_cover = "none"
    enemy.current_cover = "none"
    
    # Drone damage from previous turn
    persistent_drone_damage = 0
    
    while combat_active:
        # Clear screen and show status
        console.clear()
        console.print(Panel(f"[{COLORS['accent']}]COMBAT: {player.name} vs {enemy.name}[/{COLORS['accent']}]"))
        
        # Display health status
        display_combat_status(console, player, enemy)
        
        # Process player's combat effects at the start of their turn
        combat_effects = player.process_combat_effects()
        
        # Display messages from combat effects
        for message in combat_effects.get("messages", []):
            console.print(f"[{COLORS['text']}]{message}[/{COLORS['text']}]")
        
        # Get drone damage for this turn
        persistent_drone_damage = combat_effects.get("drone_damage", 0)
        
        # Process enemy status effects
        status_messages = enemy.process_status_effects()
        for message in status_messages:
            console.print(f"[{COLORS['accent']}]{message}[/{COLORS['accent']}]")
            
        # Check if enemy is defeated by status effects
        if enemy.is_defeated():
            console.print(f"[{COLORS['primary']}]{enemy.name} has been defeated by ongoing effects![/{COLORS['primary']}]")
            combat_active = False
            result = "victory"
            break
            
        # Display current stances and cover
        console.print(f"[{COLORS['primary']}]TURN {turn}[/{COLORS['primary']}]")
        console.print(f"[{COLORS['secondary']}]Your stance: {STANCES[player.combat_stance]['name']}[/{COLORS['secondary']}]")
        console.print(f"[{COLORS['secondary']}]Enemy stance: {STANCES[enemy.current_stance]['name']}[/{COLORS['secondary']}]")
        
        # Display cover information
        display_cover_info(console, player.current_cover)
        
        # If enemy is analyzed, show more information
        if enemy.analyzed or (player.active_effects.get("analyzed_enemy") == enemy.name):
            console.print(f"[{COLORS['primary']}]ANALYZED: {enemy.name}[/{COLORS['primary']}]")
            if enemy.weaknesses:
                console.print(f"[{COLORS['text']}]Weaknesses: {', '.join(enemy.weaknesses)}[/{COLORS['text']}]")
            if enemy.resistances:
                console.print(f"[{COLORS['text']}]Resistances: {', '.join(enemy.resistances)}[/{COLORS['text']}]")
        
        # Player's turn
        console.print(f"[{COLORS['secondary']}]Your move:[/{COLORS['secondary']}]")
        
        # Display combat options
        console.print(f"[{COLORS['text']}]1. Attack[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]2. Use Item[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]3. Change Stance[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]4. Take Cover[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]5. Special Ability[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]6. Attempt to Escape[/{COLORS['text']}]")
        
        choice = Prompt.ask("[bold green]Choose your action[/bold green]", choices=["1", "2", "3", "4", "5", "6"])
        
        # Check for stunned status
        if "stunned" in player.status_effects:
            console.print(f"[{COLORS['accent']}]You are stunned and cannot act this turn![/{COLORS['accent']}]")
            time.sleep(1.5)
            # Skip to enemy turn
            pass
        
        elif choice == "1":
            # Attack
            # Determine attack damage based on strength and a random factor
            base_damage = player.stats.get("strength", 3)
            damage_mod = random.uniform(0.8, 1.5)
            
            # Apply stance modifier to damage
            stance_damage_mod = STANCES[player.combat_stance]["damage_mod"]
            
            # Apply difficulty multiplier to player damage
            attack_damage = round(base_damage * damage_mod * stance_damage_mod * player_damage_multiplier)
            
            # Apply combat animation if enabled
            if use_animations:
                # Show attack animation
                attack_frames = [
                    f"[{COLORS['text']}]Attacking...[/{COLORS['text']}]",
                    f"[{COLORS['text']}]Attacking...[/{COLORS['text']}] *",
                    f"[{COLORS['text']}]Attacking...[/{COLORS['text']}] **",
                    f"[{COLORS['text']}]Attacking...[/{COLORS['text']}] ***"
                ]
                
                for frame in attack_frames:
                    console.print(frame, end="\r")
                    time.sleep(0.1)
                
                console.print(" " * 30, end="\r")  # Clear the line
            
            # Determine if attack is a critical hit
            crit_chance = 5  # Base 5% chance
            
            # Add stance crit modifier if applicable
            if "crit_chance_mod" in STANCES[player.combat_stance]:
                crit_chance += STANCES[player.combat_stance]["crit_chance_mod"]
                
            # Add focused effect if active
            if "focused" in player.status_effects:
                crit_chance += STATUS_EFFECTS["focused"]["crit_mod"]
                
            is_critical = random.randint(1, 100) <= crit_chance
            
            # Choose damage type based on player's stance or weapon
            damage_type = None
            if player.combat_stance == "offensive":
                damage_type = "physical"
            elif player.combat_stance == "tactical":
                # For tactical stance, try to use a weakness if analyzed
                if enemy.analyzed and enemy.weaknesses:
                    damage_type = enemy.weaknesses[0]  # Use the first weakness
            
            # Apply damage to enemy with appropriate damage type
            damage_result = enemy.take_damage(attack_damage, ignore_defense=False, is_critical=is_critical, damage_type=damage_type)
            actual_damage = damage_result["damage"]
            
            # Show weakness/resistance messages
            if damage_result["weakness_applied"]:
                console.print(f"[{COLORS['primary']}]Critical hit! {enemy.name} is weak against {damage_type}![/{COLORS['primary']}]")
            
            if damage_result["resistance_applied"]:
                console.print(f"[{COLORS['accent']}]{enemy.name} resists {damage_type} damage![/{COLORS['accent']}]")
            
            # Add drone damage if active
            if persistent_drone_damage > 0:
                drone_result = enemy.take_damage(persistent_drone_damage)
                drone_damage = drone_result["damage"]
                console.print(f"[{COLORS['text']}]Your combat drone deals an additional {drone_damage} damage![/{COLORS['text']}]")
                actual_damage += drone_damage
                
            # Play combat hit sound if audio system is available
            if audio_system:
                audio_system.play_sound("combat_hit")
                
            # Display attack result with critical hit message if applicable
            if is_critical:
                console.print(f"[{COLORS['primary']}]CRITICAL HIT![/{COLORS['primary']}]")
                console.print(f"[{COLORS['text']}]You attack {enemy.name} for [{COLORS['accent']}]{actual_damage}[/{COLORS['accent']}] damage![/{COLORS['text']}]")
            else:
                console.print(f"[{COLORS['text']}]You attack {enemy.name} for [{COLORS['accent']}]{actual_damage}[/{COLORS['accent']}] damage![/{COLORS['text']}]")
            
            # Random chance to apply bleeding status (15% chance)
            if random.randint(1, 100) <= 15:
                # Add bleeding status effect to enemy
                enemy.status_effects["bleeding"] = {
                    "turns": STATUS_EFFECTS["bleeding"]["duration"]
                }
                console.print(f"[{COLORS['primary']}]Your attack caused {enemy.name} to start bleeding![/{COLORS['primary']}]")
            
            # Check if enemy is defeated
            if enemy.is_defeated():
                if use_animations:
                    # Show defeat animation
                    for i in range(3):
                        console.print(f"[{COLORS['primary']}]{enemy.name} is defeated![/{COLORS['primary']}]")
                        time.sleep(0.2)
                        console.print(" " * 30, end="\r")  # Clear the line
                        time.sleep(0.1)
                
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
            player.use_item(selected_item, console, audio_system)
        
        elif choice == "3":
            # Change stance
            console.print(f"[{COLORS['secondary']}]Select your combat stance:[/{COLORS['secondary']}]")
            
            # Display available stances
            available_stances = list(STANCES.keys())
            for i, stance in enumerate(available_stances, 1):
                console.print(f"[{COLORS['text']}]{i}. {STANCES[stance]['name']}[/{COLORS['text']}]")
                display_stance_info(console, stance)
                console.print("")  # Empty line for spacing
                
            console.print(f"[{COLORS['text']}]0. Back to combat options[/{COLORS['text']}]")
            
            stance_choice = Prompt.ask("[bold green]Choose a stance[/bold green]", 
                                    choices=[str(i) for i in range(len(available_stances) + 1)])
            
            if stance_choice == "0":
                continue
                
            # Set the new stance
            selected_stance = available_stances[int(stance_choice) - 1]
            player.combat_stance = selected_stance
            
            console.print(f"[{COLORS['primary']}]You switch to {STANCES[selected_stance]['name']} stance![/{COLORS['primary']}]")
            
            # Play appropriate sound if audio system is available
            if audio_system:
                audio_system.play_sound("skill_success")
            
            # First hit bonus for stealth stance
            if selected_stance == "stealth" and "first_hit_bonus" in STANCES[selected_stance]:
                console.print(f"[{COLORS['text']}]Your next attack will have increased damage.[/{COLORS['text']}]")
            
        elif choice == "4":
            # Take cover
            console.print(f"[{COLORS['secondary']}]Select cover level:[/{COLORS['secondary']}]")
            
            # Display available cover types
            available_covers = list(COVER_TYPES.keys())
            for i, cover in enumerate(available_covers, 1):
                console.print(f"[{COLORS['text']}]{i}. {COVER_TYPES[cover]['name']}[/{COLORS['text']}]")
                console.print(f"[{COLORS['text']}]   {COVER_TYPES[cover]['description']}[/{COLORS['text']}]")
                if COVER_TYPES[cover]['defense_bonus'] > 0:
                    console.print(f"[{COLORS['text']}]   Defense bonus: +{COVER_TYPES[cover]['defense_bonus']}[/{COLORS['text']}]")
                console.print("")  # Empty line for spacing
                
            console.print(f"[{COLORS['text']}]0. Back to combat options[/{COLORS['text']}]")
            
            cover_choice = Prompt.ask("[bold green]Choose cover[/bold green]", 
                                    choices=[str(i) for i in range(len(available_covers) + 1)])
            
            if cover_choice == "0":
                continue
                
            # Set the new cover
            selected_cover = available_covers[int(cover_choice) - 1]
            
            # Heavier cover is harder to find (chance of finding it)
            cover_chance = {
                "none": 100,
                "light": 85,
                "medium": 60,
                "heavy": 30
            }
            
            # Intelligence helps find better cover
            int_bonus = min(15, player.stats.get("intelligence", 0) * 3)
            cover_roll = random.randint(1, 100)
            
            if cover_roll <= (cover_chance[selected_cover] + int_bonus):
                player.current_cover = selected_cover
                console.print(f"[{COLORS['primary']}]You take {COVER_TYPES[selected_cover]['name']} cover![/{COLORS['primary']}]")
                
                # Play appropriate sound if audio system is available
                if audio_system:
                    audio_system.play_sound("skill_success")
            else:
                # Failed to find good cover
                fallback_cover = "light" if selected_cover in ["medium", "heavy"] else "none"
                player.current_cover = fallback_cover
                console.print(f"[{COLORS['accent']}]You couldn't find {COVER_TYPES[selected_cover]['name']} cover.[/{COLORS['accent']}]")
                console.print(f"[{COLORS['text']}]You take {COVER_TYPES[fallback_cover]['name']} cover instead.[/{COLORS['text']}]")
                
                # Play appropriate sound if audio system is available
                if audio_system:
                    audio_system.play_sound("skill_failure")
        
        elif choice == "5":
            # Use special ability
            available_abilities = player.get_available_abilities()
            
            if not available_abilities:
                console.print(f"[{COLORS['accent']}]You have no abilities available![/{COLORS['accent']}]")
                time.sleep(1)
                continue
            
            # Display available abilities
            console.print(f"[{COLORS['secondary']}]Available abilities:[/{COLORS['secondary']}]")
            
            ability_options = {}
            ability_idx = 1
            
            for ability_id, ability_data in available_abilities.items():
                ability_options[str(ability_idx)] = ability_id
                console.print(f"[{COLORS['text']}]{ability_idx}. {ability_data['name']}[/{COLORS['text']}]")
                console.print(f"[{COLORS['text']}]   {ability_data['description']}[/{COLORS['text']}]")
                ability_idx += 1
            
            console.print(f"[{COLORS['text']}]0. Back to combat options[/{COLORS['text']}]")
            
            ability_choice = Prompt.ask("[bold green]Choose an ability to use[/bold green]", 
                                    choices=list(ability_options.keys()) + ["0"])
            
            if ability_choice == "0":
                continue
            
            selected_ability = ability_options[ability_choice]
            ability_result = player.use_ability(selected_ability, enemy, console, audio_system)
            
            # Process the ability results
            if ability_result["success"]:
                # Handle ability effects
                effects = ability_result.get("effects", {})
                
                # Apply damage effects
                if "damage" in effects:
                    damage = effects["damage"]
                    # For abilities, we can determine a relevant damage type based on ability class
                    ability_data = available_abilities[selected_ability]
                    damage_type = ability_data.get("damage_type", None)
                    
                    damage_result = enemy.take_damage(damage, damage_type=damage_type)
                    actual_damage = damage_result["damage"]
                    
                    # Show weakness/resistance messages
                    if damage_result["weakness_applied"]:
                        console.print(f"[{COLORS['primary']}]The ability exploits {enemy.name}'s weakness to {damage_type}![/{COLORS['primary']}]")
                    
                    if damage_result["resistance_applied"]:
                        console.print(f"[{COLORS['accent']}]{enemy.name} resists {damage_type} damage from your ability![/{COLORS['accent']}]")
                        
                    console.print(f"[{COLORS['text']}]The ability deals {actual_damage} damage to {enemy.name}![/{COLORS['text']}]")
                
                # Apply multi-attack effects
                if "multi_attack" in effects:
                    multi_attack = effects["multi_attack"]
                    hits = multi_attack["hits"]
                    damage_per_hit = multi_attack["damage_per_hit"]
                    
                    total_damage = 0
                    for i in range(hits):
                        if enemy.is_defeated():
                            break
                        
                        # Define the damage type for multi-attacks (can be none)
                        damage_result = enemy.take_damage(damage_per_hit)
                        actual_damage = damage_result["damage"]
                        total_damage += actual_damage
                        
                        if audio_system:
                            audio_system.play_sound("combat_hit")
                            
                        console.print(f"[{COLORS['text']}]Hit {i+1}: {actual_damage} damage[/{COLORS['text']}]")
                        time.sleep(0.3)
                    
                    console.print(f"[{COLORS['text']}]Total multi-attack damage: {total_damage}[/{COLORS['text']}]")
                
                # Apply status effects to enemy
                if "status" in effects:
                    status = effects["status"]
                    # Add status to enemy
                    enemy.status_effects[status] = {
                        "turns": STATUS_EFFECTS[status]["duration"]
                    }
                    console.print(f"[{COLORS['primary']}]{enemy.name} is now {STATUS_EFFECTS[status]['name'].lower()}![/{COLORS['primary']}]")
                
                # Check if enemy is defeated by ability
                if enemy.is_defeated():
                    console.print(f"[{COLORS['primary']}]Your ability defeats {enemy.name}![/{COLORS['primary']}]")
                    combat_active = False
                    result = "victory"
            else:
                # Ability failed
                console.print(f"[{COLORS['accent']}]{ability_result.get('message', 'Ability failed!')}[/{COLORS['accent']}]")
                
                # Play error sound if available
                if audio_system:
                    audio_system.play_sound("skill_failure")
        
        elif choice == "6":
            # Attempt to escape
            # Escape chance based on reflex stat
            escape_chance = min(70, 30 + (player.stats.get("reflex", 3) * 5))
            
            # Apply any escape boost from abilities
            available_abilities = player.get_available_abilities()
            for ability_id, ability_data in available_abilities.items():
                if "smooth_talk" in ability_id:  # Check for the Fixer's Smooth Talk ability
                    # Use the ability
                    ability_result = player.use_ability(ability_id, enemy, console, audio_system)
                    if ability_result["success"] and "escape_boost" in ability_result.get("effects", {}):
                        escape_boost = ability_result["effects"]["escape_boost"]
                        escape_chance += escape_boost
                        console.print(f"[{COLORS['primary']}]Your smooth talking increases escape chance by {escape_boost}%![/{COLORS['primary']}]")
            
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
            
            # Enemy chooses action based on AI behavior
            enemy_action = enemy.choose_action(player)
            
            # Display enemy stance change if applicable
            if enemy_action["stance"] != enemy.current_stance:
                enemy.current_stance = enemy_action["stance"]
                console.print(f"[{COLORS['accent']}]{enemy.name} switches to {STANCES[enemy.current_stance]['name']} stance![/{COLORS['accent']}]")
                
            # Display enemy cover change if applicable
            if enemy_action["cover"] != enemy.current_cover:
                enemy.current_cover = enemy_action["cover"]
                console.print(f"[{COLORS['accent']}]{enemy.name} takes {COVER_TYPES[enemy.current_cover]['name']} cover![/{COLORS['accent']}]")
            
            # Check if enemy is stunned
            if "stunned" in enemy.status_effects:
                console.print(f"[{COLORS['primary']}]{enemy.name} is stunned and cannot act this turn![/{COLORS['primary']}]")
                time.sleep(1.5)
                continue
                
            # Random chance for enemy to use a special attack (15% chance)
            special_attack_chance = 15
            use_special = random.randint(1, 100) <= special_attack_chance
            
            if use_special:
                # Choose a random enemy special attack based on type
                special_attacks = {
                    "berserker": {
                        "name": "Rage Strike",
                        "damage_mult": 1.8,
                        "self_damage": 2,
                        "message": "flies into a rage and launches a powerful attack!"
                    },
                    "tactician": {
                        "name": "Calculated Strike",
                        "damage_mult": 1.4,
                        "ignore_cover": True,
                        "message": "analyzes your position and finds a weakness in your defense!"
                    },
                    "tank": {
                        "name": "Crushing Blow",
                        "damage_mult": 1.5,
                        "stun_chance": 25,
                        "message": "delivers a crushing blow that threatens to stun you!"
                    },
                    "rogue": {
                        "name": "Backstab",
                        "damage_mult": 2.0,
                        "condition": "stealth",
                        "message": "emerges from the shadows with a deadly strike!"
                    },
                    "standard": {
                        "name": "Power Attack",
                        "damage_mult": 1.5,
                        "message": "winds up for a powerful strike!"
                    }
                }
                
                # Get the appropriate special attack for this enemy type
                special_attack = special_attacks.get(enemy.enemy_type, special_attacks["standard"])
                
                # Check if conditions for the special attack are met
                conditions_met = True
                if "condition" in special_attack:
                    if special_attack["condition"] == "stealth" and enemy.current_stance != "stealth":
                        conditions_met = False
                
                if conditions_met:
                    # Enemy uses special attack
                    console.print(f"[{COLORS['accent']}]{enemy.name} {special_attack['message']}[/{COLORS['accent']}]")
                    
                    # Calculate damage
                    attack_result = enemy.attack(player.combat_stance)
                    base_damage = attack_result["damage"]
                    damage = int(base_damage * special_attack.get("damage_mult", 1.0))
                    
                    # Apply self damage if applicable
                    if "self_damage" in special_attack:
                        enemy.health = max(0, enemy.health - special_attack["self_damage"])
                        console.print(f"[{COLORS['text']}]{enemy.name} takes {special_attack['self_damage']} self-damage from the reckless attack.[/{COLORS['text']}]")
                    
                    # Check if attack ignores cover
                    ignore_cover = special_attack.get("ignore_cover", False)
                    
                    # Player defense calculation
                    defense_value = player.stats.get("reflex", 0) // 2
                    
                    # Apply player stance defense modifier
                    stance_defense_mod = STANCES[player.combat_stance]["defense_mod"]
                    defense_value = int(defense_value * stance_defense_mod)
                    
                    # Apply cover bonus if not ignored
                    if not ignore_cover:
                        defense_value += COVER_TYPES[player.current_cover]["defense_bonus"]
                    
                    # Calculate final damage
                    actual_damage = max(1, damage - defense_value)
                    
                    # Apply damage to player
                    player.health = max(0, player.health - actual_damage)
                    
                    # Play sound effect
                    if audio_system:
                        audio_system.play_sound("player_damage")
                    
                    # Handle critical hit display
                    if attack_result["critical"]:
                        console.print(f"[{COLORS['accent']}]CRITICAL HIT! {enemy.name} hits you with {special_attack['name']} for {actual_damage} damage![/{COLORS['accent']}]")
                    else:
                        console.print(f"[{COLORS['accent']}]{enemy.name} hits you with {special_attack['name']} for {actual_damage} damage![/{COLORS['accent']}]")
                    
                    # Handle stun chance if applicable
                    if "stun_chance" in special_attack and random.randint(1, 100) <= special_attack["stun_chance"]:
                        # Add stunned status to player
                        player.status_effects["stunned"] = {
                            "turns": STATUS_EFFECTS["stunned"]["duration"]
                        }
                        console.print(f"[{COLORS['accent']}]You are stunned for {STATUS_EFFECTS['stunned']['duration']} turn(s)![/{COLORS['accent']}]")
                else:
                    # Fallback to regular attack
                    use_special = False
            
            # Regular attack if not using special
            if not use_special:
                # Enemy attack
                attack_result = enemy.attack(player.combat_stance)
                enemy_damage = attack_result["damage"]
                
                # Player defense calculation
                defense_value = player.stats.get("reflex", 0) // 2
                
                # Apply player stance defense modifier
                stance_defense_mod = STANCES[player.combat_stance]["defense_mod"]
                defense_value = int(defense_value * stance_defense_mod)
                
                # Apply cover bonus
                defense_value += COVER_TYPES[player.current_cover]["defense_bonus"]
                
                # Calculate final damage
                actual_damage = max(1, enemy_damage - defense_value)
                
                # Check for counter-attack if in defensive stance
                counter_attack = False
                if player.combat_stance == "defensive" and "counter_chance" in STANCES["defensive"]:
                    counter_chance = STANCES["defensive"]["counter_chance"]
                    if random.randint(1, 100) <= counter_chance:
                        counter_attack = True
                
                # Apply damage to player
                player.health = max(0, player.health - actual_damage)
                
                # Play player damage sound if audio system is available
                if audio_system:
                    audio_system.play_sound("player_damage")
                
                # Display attack message with critical info if applicable
                if attack_result["critical"]:
                    console.print(f"[{COLORS['accent']}]CRITICAL HIT! {enemy.name} attacks you for {actual_damage} damage![/{COLORS['accent']}]")
                else:
                    console.print(f"[{COLORS['accent']}]{enemy.name} attacks you for {actual_damage} damage![/{COLORS['accent']}]")
                
                # Handle counter-attack
                if counter_attack:
                    # Calculate counter damage
                    counter_damage = max(1, int(player.stats.get("strength", 3) * 0.7))
                    # Use physical damage type for counter-attacks
                    damage_result = enemy.take_damage(counter_damage, damage_type="physical")
                    enemy_actual_damage = damage_result["damage"]
                    console.print(f"[{COLORS['primary']}]You counter-attack for {enemy_actual_damage} damage![/{COLORS['primary']}]")
                    
                    # Play counter-attack sound
                    if audio_system:
                        audio_system.play_sound("combat_hit")
                    
                    # Check if enemy is defeated by counter
                    if enemy.is_defeated():
                        console.print(f"[{COLORS['primary']}]Your counter-attack defeats {enemy.name}![/{COLORS['primary']}]")
                        combat_active = False
                        result = "victory"
            
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
        # Play victory sound
        if audio_system:
            audio_system.play_sound("combat_hit")  # Play hit sound again on final hit
            time.sleep(0.3)
            audio_system.play_sound("level_up")    # Use level up as victory fanfare
            # Resume ambient music
            audio_system.stop_music()
            time.sleep(0.5)
            audio_system.play_music("cyberpunk_ambient")
            
        console.print(f"[{COLORS['primary']}]Victory! You defeated {enemy.name}.[/{COLORS['primary']}]")
    elif result == "defeat":
        # Play defeat sound
        if audio_system:
            audio_system.play_sound("player_damage")  # Play damage sound on defeat
            
        console.print(f"[{COLORS['accent']}]Defeat! {enemy.name} has defeated you.[/{COLORS['accent']}]")
    elif result == "escape":
        # Sound for escape
        if audio_system:
            audio_system.play_sound("door_open")  # Use door sound for escape
            # Resume ambient music
            audio_system.stop_music()
            time.sleep(0.5)
            audio_system.play_music("cyberpunk_ambient")
            
        console.print(f"[{COLORS['secondary']}]You escaped from {enemy.name}.[/{COLORS['secondary']}]")
    
    time.sleep(2)
    return result

def get_item_info(item_name):
    """Get information about an item"""
    # Import here to avoid circular imports
    from inventory import get_item_info as inventory_get_item_info
    return inventory_get_item_info(item_name)
