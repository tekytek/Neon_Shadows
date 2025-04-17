"""
Character Module - Player character functionality
"""
import json
import time
from rich.console import Console

import inventory
from config import LEVEL_UP_BASE_XP
from districts import ReputationSystem
from skills import CharacterProgression, SkillTree

class Character:
    """Player character class with stats and inventory"""
    
    def __init__(self, name, char_class, stats=None):
        """Initialize a new character"""
        self.name = name
        self.char_class = char_class
        
        # Initialize stats
        self.stats = stats or {
            "strength": 3,
            "intelligence": 3,
            "charisma": 3,
            "reflex": 3
        }
        
        # Core attributes
        self.level = 1
        self.experience = 0
        self.max_health = 10 + self.stats.get("strength", 0) * 2
        self.health = self.max_health
        self.credits = 100
        
        # Create inventory
        self.inventory = inventory.Inventory()
        
        # Character status effects
        self.status_effects = {}
        
        # Reputation system
        self.reputation = ReputationSystem()
        
        # Advanced progression system
        self.skill_tree = SkillTree()
        self.progression = CharacterProgression(self, self.skill_tree)
        
        # Give initial skill points based on class
        initial_skill_points = 3
        initial_perk_points = 1
        self.progression.add_skill_points(initial_skill_points)
        self.progression.add_perk_points(initial_perk_points)
        
        # Combat related attributes
        self.combat_stance = "offensive"  # Default stance: offensive, defensive, tactical, stealth
        self.current_cover = "none"       # Current cover level: none, light, medium, heavy
        
        # Special abilities cooldowns (turns remaining)
        self.ability_cooldowns = {}
        
        # Active effects (drones, temporary buffs, etc.)
        self.active_effects = {
            "drone_damage": 0,      # Extra damage from deployed drone
            "drone_turns": 0,       # Turns remaining for drone
            "analyzed_enemy": None, # Enemy that has been analyzed
            "focus_bonus": 0,       # Critical hit chance bonus
            "defense_bonus": 0      # Bonus to defense value
        }
        
        # Weaknesses and resistances (for advanced combat)
        self.weaknesses = []
        self.resistances = []
        
        # Initialize special abilities based on character class
        self._init_class_abilities()
    
    @classmethod
    def from_dict(cls, data):
        """Create a character from a dictionary (for loading saves)"""
        character = cls(
            name=data.get('name', 'Unknown'),
            char_class=data.get('char_class', 'Drifter'),
            stats=data.get('stats', {})
        )
        
        # Load other attributes
        character.level = data.get('level', 1)
        character.experience = data.get('experience', 0)
        character.max_health = data.get('max_health', 10)
        character.health = data.get('health', character.max_health)
        character.credits = data.get('credits', 0)
        
        # Load inventory
        character.inventory = inventory.Inventory.from_dict(data.get('inventory', {}))
        
        # Load status effects
        character.status_effects = data.get('status_effects', {})
        
        # Load reputation
        if 'reputation' in data:
            character.reputation = ReputationSystem.from_dict(data.get('reputation', {}))
        
        # Load progression data
        if 'progression' in data:
            character.progression = CharacterProgression.from_dict(
                data.get('progression', {}),
                character=character,
                skill_tree=character.skill_tree
            )
            
        # Load combat related attributes
        character.combat_stance = data.get('combat_stance', 'offensive')
        character.current_cover = data.get('current_cover', 'none')
        character.ability_cooldowns = data.get('ability_cooldowns', {})
        character.active_effects = data.get('active_effects', {
            'drone_damage': 0,
            'drone_turns': 0,
            'analyzed_enemy': None
        })
        
        # Re-initialize abilities in case the character class has new ones
        character._init_class_abilities()
        
        return character
    
    def to_dict(self):
        """Convert character to dictionary (for saving)"""
        return {
            'name': self.name,
            'char_class': self.char_class,
            'stats': self.stats,
            'level': self.level,
            'experience': self.experience,
            'max_health': self.max_health,
            'health': self.health,
            'credits': self.credits,
            'inventory': self.inventory.to_dict(),
            'status_effects': self.status_effects,
            'reputation': self.reputation.to_dict(),
            'progression': self.progression.to_dict(),
            'combat_stance': self.combat_stance,
            'current_cover': self.current_cover,
            'ability_cooldowns': self.ability_cooldowns,
            'active_effects': self.active_effects
        }
    
    def add_experience(self, amount, audio_system=None):
        """Add experience and handle level ups"""
        if amount <= 0:
            return
        
        self.experience += amount
        
        # Also award experience to progression system
        progression_rewards = self.progression.award_experience(amount)
        
        # Check for level up
        xp_for_next_level = LEVEL_UP_BASE_XP * (self.level * 1.5)
        
        if self.experience >= xp_for_next_level:
            level_up_info = self.level_up()
            
            # Play level up sound if audio system is available
            if audio_system:
                audio_system.play_sound("level_up")
                
            return level_up_info
        elif progression_rewards["skill_points_gained"] > 0 or progression_rewards["perk_points_gained"] > 0:
            # Even if not a level up, return info about skill/perk points gained
            return {
                "skill_points_gained": progression_rewards["skill_points_gained"],
                "perk_points_gained": progression_rewards["perk_points_gained"]
            }
    
    def level_up(self):
        """Handle character level up"""
        self.level += 1
        
        # Increase max health
        old_max_health = self.max_health
        self.max_health = 10 + (self.stats.get("strength", 0) * 2) + (self.level * 2)
        health_increase = self.max_health - old_max_health
        
        # Heal to full on level up
        self.health = self.max_health
        
        # Award skill points and perks through progression system
        progression_rewards = self.progression.award_experience(0)  # 0 XP because we're just processing the level up
        
        # Return level up info for UI with progression rewards
        return {
            'new_level': self.level,
            'health_increase': health_increase,
            'skill_points_gained': progression_rewards.get('skill_points_gained', 0),
            'perk_points_gained': progression_rewards.get('perk_points_gained', 0)
        }
    
    def use_item(self, item_name, console, audio_system=None):
        """Use an item from inventory"""
        if not self.inventory.has_item(item_name):
            console.print(f"[red]You don't have {item_name}[/red]")
            # Play error sound if available
            if audio_system:
                audio_system.play_sound("skill_failure")
            return False
        
        # Get item information
        item_info = inventory.get_item_info(item_name)
        
        if not item_info:
            console.print(f"[red]Unknown item: {item_name}[/red]")
            # Play error sound if available
            if audio_system:
                audio_system.play_sound("skill_failure")
            return False
        
        # Check if item is usable
        if not item_info.get('usable', False):
            console.print(f"[red]You can't use {item_name}[/red]")
            # Play error sound if available
            if audio_system:
                audio_system.play_sound("skill_failure")
            return False
        
        # Process item effects
        effects = item_info.get('effects', {})
        
        # Health effect
        if 'health' in effects:
            old_health = self.health
            self.health = min(self.max_health, self.health + effects['health'])
            health_gain = self.health - old_health
            
            console.print(f"[green]Restored {health_gain} health[/green]")
        
        # Stat effects
        for stat, value in effects.get('stats', {}).items():
            if stat in self.stats:
                old_value = self.stats[stat]
                
                # Apply stat bonus
                if 'permanent' in effects and effects['permanent']:
                    # Permanent stat increase
                    self.stats[stat] += value
                    console.print(f"[green]Permanently increased {stat} by {value}[/green]")
                else:
                    # Temporary stat boost
                    duration = effects.get('duration', 3)
                    
                    # Add status effect
                    effect_id = f"{stat}_boost_{time.time()}"
                    self.status_effects[effect_id] = {
                        'type': 'stat_boost',
                        'stat': stat,
                        'value': value,
                        'duration': duration,
                        'applied_at': time.time()
                    }
                    
                    console.print(f"[green]Boosted {stat} by {value} for {duration} turns[/green]")
        
        # Special effects
        if 'special' in effects:
            special = effects['special']
            
            if special == 'reveal_map':
                console.print("[green]Map revealed in your current area[/green]")
            elif special == 'remove_status':
                # Remove negative status effects
                removed = 0
                for effect_id in list(self.status_effects.keys()):
                    effect = self.status_effects[effect_id]
                    if effect.get('negative', False):
                        del self.status_effects[effect_id]
                        removed += 1
                
                console.print(f"[green]Removed {removed} negative status effects[/green]")
        
        # Remove the item from inventory
        self.inventory.remove_item(item_name, 1)
        
        # Play appropriate sound effect if audio system is available
        if audio_system:
            # Select sound based on item type
            if 'health' in effects:
                audio_system.play_sound("item_pickup")  # Use pickup sound for healing items
            elif 'special' in effects and effects['special'] == 'reveal_map':
                audio_system.play_sound("skill_success")
            elif 'special' in effects and effects['special'] == 'remove_status':
                audio_system.play_sound("skill_success")
            else:
                # Default item use sound
                audio_system.play_sound("item_pickup")
                
        return True
    
    def apply_status_effects(self):
        """Apply active status effects and remove expired ones"""
        current_time = time.time()
        stats_modified = {}
        
        # Track expired effects to remove
        expired_effects = []
        
        # Process each effect
        for effect_id, effect in self.status_effects.items():
            # Check if effect has expired
            duration = effect.get('duration', 0)
            applied_at = effect.get('applied_at', 0)
            
            if duration > 0 and current_time - applied_at > duration:
                expired_effects.append(effect_id)
                continue
            
            # Apply effect based on type
            effect_type = effect.get('type', '')
            
            if effect_type == 'stat_boost':
                stat = effect.get('stat', '')
                value = effect.get('value', 0)
                
                if stat in self.stats:
                    if stat not in stats_modified:
                        stats_modified[stat] = 0
                    
                    stats_modified[stat] += value
            elif effect_type == 'damage_over_time':
                damage = effect.get('damage', 0)
                self.health = max(0, self.health - damage)
            elif effect_type == 'heal_over_time':
                heal = effect.get('heal', 0)
                self.health = min(self.max_health, self.health + heal)
        
        # Apply stat modifications
        for stat, mod in stats_modified.items():
            self.stats[stat] += mod
        
        # Remove expired effects
        for effect_id in expired_effects:
            del self.status_effects[effect_id]
        
        return {
            'modified_stats': stats_modified,
            'expired_effects': expired_effects
        }
        
    def _init_class_abilities(self):
        """Initialize class-specific abilities based on character class"""
        # Import the abilities configuration
        from combat import CLASS_ABILITIES
        
        # Check if the character class has defined abilities
        if self.char_class in CLASS_ABILITIES:
            # Get abilities for this class
            class_abilities = CLASS_ABILITIES[self.char_class]
            
            # Initialize cooldowns to 0 (ready to use)
            for ability_id in class_abilities:
                self.ability_cooldowns[ability_id] = 0
                
    def get_available_abilities(self):
        """Get list of abilities available to the character that are not on cooldown"""
        # Import the abilities configuration
        from combat import CLASS_ABILITIES
        
        available_abilities = {}
        
        # Check if the character class has defined abilities
        if self.char_class in CLASS_ABILITIES:
            # Get abilities for this class
            class_abilities = CLASS_ABILITIES[self.char_class]
            
            # Add abilities that are not on cooldown
            for ability_id, ability_data in class_abilities.items():
                if self.ability_cooldowns.get(ability_id, 0) <= 0:
                    available_abilities[ability_id] = ability_data
        
        # Check for abilities granted by skills and perks
        if hasattr(self, 'progression'):
            # Get all skill and perk effects
            all_effects = self.progression.calculate_all_effects()
            
            # Check for abilities in the effects
            if 'abilities' in all_effects and all_effects['abilities']:
                for ability_name in all_effects['abilities']:
                    # Skip if this ability is already included from class abilities
                    if ability_name in available_abilities:
                        continue
                        
                    # Create an ability ID for this skill/perk ability
                    ability_id = f"skill_{ability_name.lower().replace(' ', '_')}"
                    
                    # Try to find this ability in any class
                    ability_data = None
                    for class_name, abilities in CLASS_ABILITIES.items():
                        for ab_id, data in abilities.items():
                            if data.get('name') == ability_name:
                                ability_data = data.copy()
                                break
                        if ability_data:
                            break
                    
                    # If not found in any class, create a basic entry
                    if not ability_data:
                        ability_data = {
                            "name": ability_name,
                            "description": f"Special ability acquired through skills/perks",
                            "cooldown": 3  # Default cooldown
                        }
                        
                        # Add some basic effects based on the name
                        if "damage" in ability_name.lower() or "attack" in ability_name.lower():
                            ability_data["damage_multiplier"] = 1.5
                        elif "defense" in ability_name.lower() or "protect" in ability_name.lower():
                            ability_data["defense_boost"] = 3
                        elif "heal" in ability_name.lower():
                            ability_data["self_heal"] = 10
                    
                    # Add to available abilities if not on cooldown
                    if self.ability_cooldowns.get(ability_id, 0) <= 0:
                        available_abilities[ability_id] = ability_data
        
        return available_abilities
    
    def use_ability(self, ability_id, target=None, console=None, audio_system=None):
        """Use a special ability and put it on cooldown
        
        Args:
            ability_id (str): ID of the ability to use
            target (Enemy, optional): Target of the ability
            console (Console, optional): Console for output
            audio_system (AudioSystem, optional): Audio system for sound effects
            
        Returns:
            dict: Results of the ability use
        """
        # Import the abilities configuration
        from combat import CLASS_ABILITIES
        
        # Get all available abilities including those from skills/perks
        available_abilities = self.get_available_abilities()
        
        # Check if the ability exists
        if ability_id not in available_abilities:
            if console:
                console.print(f"[red]Unknown ability: {ability_id}[/red]")
            return {"success": False, "message": "Unknown ability"}
            
        # Check if the ability is on cooldown
        if self.ability_cooldowns.get(ability_id, 0) > 0:
            ability_name = available_abilities[ability_id].get('name', ability_id)
            if console:
                console.print(f"[red]Ability {ability_name} is on cooldown for {self.ability_cooldowns[ability_id]} more turns[/red]")
            return {"success": False, "message": "Ability on cooldown"}
        
        # Use the ability
        ability = available_abilities[ability_id]
        result = {"success": True, "effects": {}}
        
        # Play sound effect if available
        if audio_system:
            audio_system.play_sound("skill_success")
        
        # Process ability effects
        if "damage_multiplier" in ability:
            # Calculate base damage from strength
            base_damage = self.stats.get("strength", 3)
            damage = int(base_damage * ability["damage_multiplier"])
            result["effects"]["damage"] = damage
            
            if console:
                console.print(f"[green]Used {ability['name']} for {damage} damage![/green]")
        
        if "attacks" in ability:
            # Multiple attacks
            attacks = ability["attacks"]
            damage_mult = ability.get("damage_multiplier", 0.5)
            base_damage = self.stats.get("strength", 3)
            damage_per_hit = int(base_damage * damage_mult)
            
            result["effects"]["multi_attack"] = {
                "hits": attacks,
                "damage_per_hit": damage_per_hit
            }
            
            if console:
                console.print(f"[green]Used {ability['name']} for {attacks} attacks of {damage_per_hit} damage each![/green]")
        
        if "self_heal" in ability:
            # Heal the player
            heal_amount = ability["self_heal"]
            old_health = self.health
            self.health = min(self.max_health, self.health + heal_amount)
            actual_heal = self.health - old_health
            
            result["effects"]["heal"] = actual_heal
            
            if console:
                console.print(f"[green]Used {ability['name']} to heal for {actual_heal} health![/green]")
        
        if "status_effect" in ability:
            # Apply status effect to enemy
            status = ability["status_effect"]
            result["effects"]["status"] = status
            
            if console:
                console.print(f"[green]Used {ability['name']} to apply {status} status![/green]")
        
        if "defense_boost" in ability:
            # Apply defense boost as a status effect
            boost = ability["defense_boost"]
            duration = ability.get("duration", 3)
            
            # Add status effect
            effect_id = f"defense_boost_{time.time()}"
            self.status_effects[effect_id] = {
                'type': 'defense_boost',
                'value': boost,
                'duration': duration,
                'applied_at': time.time()
            }
            
            result["effects"]["defense_boost"] = boost
            
            if console:
                console.print(f"[green]Used {ability['name']} to boost defense by {boost} for {duration} turns![/green]")
        
        if "reveal_weakness" in ability:
            # Mark enemy as analyzed
            if target:
                self.active_effects["analyzed_enemy"] = target.name
                target.analyzed = True
                
                if console:
                    console.print(f"[green]Used {ability['name']} to reveal {target.name}'s weaknesses![/green]")
                
                result["effects"]["analyzed"] = True
        
        if "bonus_damage" in ability and "duration" in ability:
            # Deploy a drone or similar effect that deals damage each turn
            damage = ability["bonus_damage"]
            duration = ability["duration"]
            
            self.active_effects["drone_damage"] = damage
            self.active_effects["drone_turns"] = duration
            
            result["effects"]["drone"] = {
                "damage": damage,
                "duration": duration
            }
            
            if console:
                console.print(f"[green]Used {ability['name']} to deploy a drone that will deal {damage} damage for {duration} turns![/green]")
        
        if "self_damage" in ability:
            # Ability that hurts the player
            damage = ability["self_damage"]
            self.health = max(0, self.health - damage)
            
            result["effects"]["self_damage"] = damage
            
            if console:
                console.print(f"[red]{ability['name']} caused you to take {damage} damage![/red]")
        
        if "escape_boost" in ability:
            # Boost escape chance
            result["effects"]["escape_boost"] = ability["escape_boost"]
            
            if console:
                console.print(f"[green]Used {ability['name']} to increase escape chance![/green]")
        
        # Set cooldown
        cooldown = ability.get("cooldown", 3)
        self.ability_cooldowns[ability_id] = cooldown
        
        # Return the results
        return result
    
    def process_combat_effects(self):
        """Process combat-specific effects at the start of the player's turn"""
        results = {
            "messages": [],
            "drone_damage": 0
        }
        
        # Check for drone damage
        if self.active_effects["drone_turns"] > 0:
            drone_damage = self.active_effects["drone_damage"]
            self.active_effects["drone_turns"] -= 1
            
            if self.active_effects["drone_turns"] <= 0:
                self.active_effects["drone_damage"] = 0
                results["messages"].append("Your combat drone has deactivated")
            else:
                results["messages"].append(f"Your combat drone is active for {self.active_effects['drone_turns']} more turns")
                results["drone_damage"] = drone_damage
        
        # Reduce ability cooldowns
        for ability_id in list(self.ability_cooldowns.keys()):
            if self.ability_cooldowns[ability_id] > 0:
                self.ability_cooldowns[ability_id] -= 1
                if self.ability_cooldowns[ability_id] <= 0:
                    results["messages"].append(f"Ability {ability_id} is ready to use again")
        
        return results
