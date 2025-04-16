"""
Character Module - Player character functionality
"""
import json
import time
from rich.console import Console

import inventory
from config import LEVEL_UP_BASE_XP

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
            'status_effects': self.status_effects
        }
    
    def add_experience(self, amount):
        """Add experience and handle level ups"""
        if amount <= 0:
            return
        
        self.experience += amount
        
        # Check for level up
        xp_for_next_level = LEVEL_UP_BASE_XP * (self.level * 1.5)
        
        if self.experience >= xp_for_next_level:
            self.level_up()
    
    def level_up(self):
        """Handle character level up"""
        self.level += 1
        
        # Increase max health
        old_max_health = self.max_health
        self.max_health = 10 + (self.stats.get("strength", 0) * 2) + (self.level * 2)
        health_increase = self.max_health - old_max_health
        
        # Heal to full on level up
        self.health = self.max_health
        
        # Return level up info for UI
        return {
            'new_level': self.level,
            'health_increase': health_increase
        }
    
    def use_item(self, item_name, console):
        """Use an item from inventory"""
        if not self.inventory.has_item(item_name):
            console.print(f"[red]You don't have {item_name}[/red]")
            return False
        
        # Get item information
        item_info = inventory.get_item_info(item_name)
        
        if not item_info:
            console.print(f"[red]Unknown item: {item_name}[/red]")
            return False
        
        # Check if item is usable
        if not item_info.get('usable', False):
            console.print(f"[red]You can't use {item_name}[/red]")
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
