"""
Inventory Module - Handles player inventory and items
"""
import os
import json

from config import DATA_DIR

class Inventory:
    """Inventory management for the player"""
    
    def __init__(self):
        """Initialize a new inventory"""
        self.items = {}  # Format: {item_name: quantity}
        self._load_items_data()
    
    @classmethod
    def from_dict(cls, data):
        """Create an inventory from a dictionary (for loading saves)"""
        inventory = cls()
        inventory.items = data.get('items', {})
        return inventory
    
    def to_dict(self):
        """Convert inventory to dictionary (for saving)"""
        return {
            'items': self.items
        }
    
    def _load_items_data(self):
        """Load item data from JSON file"""
        self.items_data = {}
        items_file = os.path.join(DATA_DIR, 'items.json')
        
        try:
            if os.path.exists(items_file):
                with open(items_file, 'r') as f:
                    self.items_data = json.load(f)
            else:
                # Create default items if file doesn't exist
                self._create_default_items()
                
                # Save the default items
                with open(items_file, 'w') as f:
                    json.dump(self.items_data, f, indent=2)
        except Exception as e:
            print(f"Error loading items data: {str(e)}")
            # Create default items on error
            self._create_default_items()
    
    def _create_default_items(self):
        """Create default items data"""
        self.items_data = {
            "Stimpack": {
                "description": "Emergency medical stimulant. Restores 5 health immediately.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": True,
                "effects": {
                    "health": 5
                }
            },
            "Med Nanites": {
                "description": "Advanced medical nanobots. Restores 10 health and removes one negative status effect.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": True,
                "effects": {
                    "health": 10,
                    "special": "remove_status"
                }
            },
            "Cyberdeck": {
                "description": "Standard hacking device. Required for bypassing electronic security and accessing networks.",
                "type": "equipment",
                "usable": False
            },
            "ICEbreaker": {
                "description": "Specialized program for breaking through corporate Intrusion Countermeasures Electronics.",
                "type": "software",
                "usable": False
            },
            "Heavy Pistol": {
                "description": "High-caliber handgun. Effective against unarmored targets.",
                "type": "weapon",
                "usable": False,
                "damage": 5
            },
            "Armored Vest": {
                "description": "Ballistic protection. Reduces physical damage.",
                "type": "armor",
                "usable": False,
                "defense": 2
            },
            "Encrypted Phone": {
                "description": "Secure communication device. Untraceable and encrypted.",
                "type": "equipment",
                "usable": False
            },
            "Concealed Pistol": {
                "description": "Small, easily hidden firearm. Lower damage but harder to detect.",
                "type": "weapon",
                "usable": False,
                "damage": 3
            },
            "Multi-tool": {
                "description": "Versatile tool set. Useful for repairs and bypassing physical security.",
                "type": "equipment",
                "usable": False
            },
            "Diagnostic Scanner": {
                "description": "Analyzes electronic systems and cyberware for vulnerabilities.",
                "type": "equipment",
                "usable": False
            },
            "Credchip": {
                "description": "Digital wallet loaded with cryptocurrency. Universal payment method.",
                "type": "currency",
                "usable": False
            },
            "Neural Booster": {
                "description": "Temporary intelligence enhancement. +2 Intelligence for 3 encounters.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": True,
                "effects": {
                    "stats": {"intelligence": 2},
                    "duration": 3
                }
            },
            "Reflex Booster": {
                "description": "Temporary enhancement. +2 Reflex for 3 encounters.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": True,
                "effects": {
                    "stats": {"reflex": 2},
                    "duration": 3
                }
            },
            "Immunity Chip": {
                "description": "Protects against common toxins and pathogens for 24 hours.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": False,
                "effects": {
                    "special": "toxin_immunity",
                    "duration": 10
                }
            },
            "EMP Grenade": {
                "description": "Disables electronic devices and cyberware in a small radius.",
                "type": "consumable",
                "usable": True,
                "usable_in_combat": True,
                "effects": {
                    "special": "emp_disable",
                    "duration": 2
                }
            },
            "Memory Shard": {
                "description": "Storage device for neural data and programs.",
                "type": "storage",
                "usable": False
            },
            "Security Keycard": {
                "description": "Access card for security systems. Grants entry to restricted areas.",
                "type": "key",
                "usable": False
            },
            "Specialized Data Shard": {
                "description": "High-capacity data storage designed for secure extraction of sensitive information.",
                "type": "mission_item",
                "usable": False
            },
            "Facility Access Codes": {
                "description": "Encrypted access codes for an Orison Industries research facility.",
                "type": "mission_item",
                "usable": False
            },
            "Zhi's Location Data": {
                "description": "Digital coordinates and access information for reaching Zhi, a memory specialist.",
                "type": "mission_item",
                "usable": False
            }
        }
    
    def add_item(self, item_name, quantity=1):
        """Add an item to the inventory"""
        if quantity <= 0:
            return False
        
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity
        
        return True
    
    def remove_item(self, item_name, quantity=1):
        """Remove an item from the inventory"""
        if item_name not in self.items or quantity <= 0:
            return False
        
        if self.items[item_name] <= quantity:
            # Remove the item entirely if removing all or more than we have
            del self.items[item_name]
        else:
            # Reduce the quantity
            self.items[item_name] -= quantity
        
        return True
    
    def has_item(self, item_name, quantity=1):
        """Check if the inventory has at least the specified quantity of an item"""
        return item_name in self.items and self.items[item_name] >= quantity
    
    def get_item_count(self, item_name):
        """Get the quantity of a specific item"""
        return self.items.get(item_name, 0)
    
    def get_all_items(self):
        """Get all items and their quantities"""
        return self.items.copy()
    
    def clear(self):
        """Clear the inventory"""
        self.items = {}

def get_item_info(item_name):
    """Get information about an item"""
    # Create a simple inventory to access items data
    temp_inventory = Inventory()
    
    # Return the item data if found
    return temp_inventory.items_data.get(item_name, None)
