"""
Districts Module - Manages city districts and reputation systems
"""
import json
import os
import time
from typing import Dict, List, Optional, Tuple
import random

class District:
    """Represents a district in the cyberpunk city"""
    
    def __init__(self, district_id: str, name: str, description: str, 
                 danger_level: int = 1, available_shops: List[str] = None,
                 available_quests: List[str] = None, connected_districts: List[str] = None,
                 ascii_art: str = None, location_choices: List[Dict] = None,
                 map_position: Dict = None):
        """Initialize a district"""
        self.district_id = district_id  # Unique identifier
        self.name = name
        self.description = description
        self.danger_level = danger_level  # 1-5 scale
        self.available_shops = available_shops or []
        self.available_quests = available_quests or []
        self.connected_districts = connected_districts or []  # Districts you can travel to from here
        self.ascii_art = ascii_art  # ASCII art representation of the district
        self.location_choices = location_choices or []  # Special actions available in this district
        self.map_position = map_position or {"x": 0, "y": 0}  # Position on the city map overview
    
    def to_dict(self) -> Dict:
        """Convert district to dictionary (for saving)"""
        return {
            'district_id': self.district_id,
            'name': self.name,
            'description': self.description,
            'danger_level': self.danger_level,
            'available_shops': self.available_shops,
            'available_quests': self.available_quests,
            'connected_districts': self.connected_districts,
            'ascii_art': self.ascii_art,
            'location_choices': self.location_choices,
            'map_position': self.map_position
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a district from a dictionary"""
        return cls(
            district_id=data.get('district_id', ''),
            name=data.get('name', 'Unknown District'),
            description=data.get('description', ''),
            danger_level=data.get('danger_level', 1),
            available_shops=data.get('available_shops', []),
            available_quests=data.get('available_quests', []),
            connected_districts=data.get('connected_districts', []),
            ascii_art=data.get('ascii_art'),
            location_choices=data.get('location_choices', []),
            map_position=data.get('map_position', {"x": 0, "y": 0})
        )
        
    def get_location_choices(self) -> List[Dict]:
        """Get the special location-based choices available in this district"""
        return self.location_choices

class Faction:
    """Represents a faction in the game world"""
    
    def __init__(self, faction_id: str, name: str, description: str, 
                 home_district: str = None, rival_factions: List[str] = None,
                 allied_factions: List[str] = None, controlled_districts: List[str] = None,
                 faction_type: str = "gang"):
        """Initialize a faction"""
        self.faction_id = faction_id
        self.name = name
        self.description = description
        self.home_district = home_district  # Primary district where this faction is headquartered
        self.rival_factions = rival_factions or []
        self.allied_factions = allied_factions or []
        self.controlled_districts = controlled_districts or []  # Districts where this faction has strong influence
        self.faction_type = faction_type  # Type: gang, corp, government, underworld, etc.
        
    def to_dict(self) -> Dict:
        """Convert faction to dictionary (for saving)"""
        return {
            'faction_id': self.faction_id,
            'name': self.name,
            'description': self.description,
            'home_district': self.home_district,
            'rival_factions': self.rival_factions,
            'allied_factions': self.allied_factions,
            'controlled_districts': self.controlled_districts,
            'faction_type': self.faction_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a faction from a dictionary"""
        return cls(
            faction_id=data.get('faction_id', ''),
            name=data.get('name', 'Unknown Faction'),
            description=data.get('description', ''),
            home_district=data.get('home_district'),
            rival_factions=data.get('rival_factions', []),
            allied_factions=data.get('allied_factions', []),
            controlled_districts=data.get('controlled_districts', []),
            faction_type=data.get('faction_type', 'gang')
        )

class ReputationSystem:
    """Manages player reputation across different districts and factions"""
    
    def __init__(self):
        """Initialize reputation system"""
        # District reputations (neutral = 0, -100 to +100 scale)
        self.district_reputation: Dict[str, int] = {}
        
        # Faction reputations (neutral = 0, -100 to +100 scale)
        self.faction_reputation: Dict[str, int] = {}
        
        # Track reputation history (last 10 changes)
        self.reputation_history: List[Dict] = []
        
        # Track reputation milestones reached
        self.reputation_milestones: Dict[str, List[int]] = {
            "district": {},
            "faction": {}
        }
        
        # Initialize default faction relationships
        self._initialize_default_factions()
    
    def _initialize_default_factions(self):
        """Initialize default factions and reputations"""
        # Initialize all faction reputations to 0 (neutral)
        default_factions = [
            "arasaka", "militech", "biotech_inc", "aquatech", 
            "police", "coast_guard", "street_gangs", "fixers", "netrunners",
            "tunnel_rats", "jade_fist", "chrome_kings", "voodoo_boys", "maelstrom",
            "smugglers_guild", "pirates_syndicate", "deep_collective", "eco_collective", "sea_nomads"
        ]
        
        for faction in default_factions:
            if faction not in self.faction_reputation:
                self.faction_reputation[faction] = 0
    
    def record_reputation_change(self, target_type: str, target_id: str, amount: int, reason: str = None):
        """Record a reputation change in history"""
        timestamp = time.time()
        entry = {
            "timestamp": timestamp,
            "target_type": target_type,  # 'district' or 'faction'
            "target_id": target_id,
            "amount": amount,
            "reason": reason or "Unknown reason"
        }
        
        self.reputation_history.append(entry)
        if len(self.reputation_history) > 20:  # Keep only last 20 entries
            self.reputation_history.pop(0)
    
    def check_reputation_milestone(self, target_type: str, target_id: str, new_value: int) -> Optional[Dict]:
        """Check if a new reputation milestone has been reached
        
        Returns:
            Optional[Dict]: Milestone data if reached, None otherwise
        """
        # Define reputation thresholds that trigger events
        milestones = [
            {"value": -80, "description": "Despised", "threshold_type": "negative"},
            {"value": -60, "description": "Hated", "threshold_type": "negative"},
            {"value": -40, "description": "Disliked", "threshold_type": "negative"},
            {"value": -20, "description": "Suspicious", "threshold_type": "negative"},
            {"value": 20, "description": "Accepted", "threshold_type": "positive"},
            {"value": 40, "description": "Respected", "threshold_type": "positive"},
            {"value": 60, "description": "Honored", "threshold_type": "positive"},
            {"value": 80, "description": "Revered", "threshold_type": "positive"}
        ]
        
        # Initialize milestone tracking for this target if not already present
        milestone_dict = self.reputation_milestones[target_type]
        if target_id not in milestone_dict:
            milestone_dict[target_id] = []
        
        # Check if we've hit a new milestone
        for milestone in milestones:
            threshold = milestone["value"]
            if threshold not in milestone_dict[target_id]:
                if (threshold > 0 and new_value >= threshold) or (threshold < 0 and new_value <= threshold):
                    milestone_dict[target_id].append(threshold)
                    
                    return {
                        "target_type": target_type,
                        "target_id": target_id,
                        "threshold": threshold,
                        "description": milestone["description"],
                        "threshold_type": milestone["threshold_type"]
                    }
        
        return None
                
    def get_district_reputation(self, district_id: str) -> int:
        """Get reputation in a specific district"""
        return self.district_reputation.get(district_id, 0)
    
    def get_faction_reputation(self, faction_id: str) -> int:
        """Get reputation with a specific faction"""
        return self.faction_reputation.get(faction_id, 0)
    
    def modify_district_reputation(self, district_id: str, amount: int, reason: str = None) -> Dict:
        """
        Modify reputation in a district
        
        Args:
            district_id: The district ID
            amount: Amount to change (positive or negative)
            reason: Optional reason for reputation change
            
        Returns:
            Dict with reputation results and any triggered milestones
        """
        results = {
            "old_value": 0,
            "new_value": 0,
            "change": amount,
            "milestone": None
        }
        
        if district_id not in self.district_reputation:
            self.district_reputation[district_id] = 0
        
        results["old_value"] = self.district_reputation[district_id]
        self.district_reputation[district_id] += amount
        
        # Clamp value between -100 and 100
        self.district_reputation[district_id] = max(-100, min(100, self.district_reputation[district_id]))
        results["new_value"] = self.district_reputation[district_id]
        
        # Record the change in history
        self.record_reputation_change("district", district_id, amount, reason)
        
        # Check if a milestone was reached
        milestone = self.check_reputation_milestone("district", district_id, results["new_value"])
        if milestone:
            results["milestone"] = milestone
        
        return results
    
    def modify_faction_reputation(self, faction_id: str, amount: int, district_manager=None, reason: str = None) -> Dict:
        """
        Modify reputation with a faction and handle faction relationships
        
        Args:
            faction_id: The faction ID
            amount: Amount to change (positive or negative)
            district_manager: Optional DistrictManager to handle faction district effects
            reason: Optional reason for reputation change
            
        Returns:
            Dict with reputation changes, secondary effects, and any triggered milestones
        """
        results = {
            "primary_change": {
                "old_value": 0,
                "new_value": 0,
                "change": amount,
                "milestone": None
            },
            "ripple_effects": {},
            "district_effects": {}
        }
        
        # Update primary faction reputation
        if faction_id not in self.faction_reputation:
            self.faction_reputation[faction_id] = 0
        
        results["primary_change"]["old_value"] = self.faction_reputation[faction_id]
        self.faction_reputation[faction_id] += amount
        
        # Clamp value between -100 and 100
        self.faction_reputation[faction_id] = max(-100, min(100, self.faction_reputation[faction_id]))
        results["primary_change"]["new_value"] = self.faction_reputation[faction_id]
        
        # Record the change in history
        self.record_reputation_change("faction", faction_id, amount, reason)
        
        # Check if a milestone was reached
        milestone = self.check_reputation_milestone("faction", faction_id, results["primary_change"]["new_value"])
        if milestone:
            results["primary_change"]["milestone"] = milestone
        
        # Apply ripple effects to rival and allied factions (if this is a significant reputation change)
        if abs(amount) >= 10:
            # Get faction data
            faction_data = self._get_faction_data(faction_id)
            
            if faction_data:
                # Negatively impact reputation with rival factions
                for rival in faction_data.get('rivals', []):
                    ripple = -amount // 2  # Rival factions are affected oppositely at half strength
                    if rival in self.faction_reputation:
                        old_rep = self.faction_reputation[rival]
                        self.faction_reputation[rival] += ripple
                        # Clamp value between -100 and 100
                        self.faction_reputation[rival] = max(-100, min(100, self.faction_reputation[rival]))
                        new_rep = self.faction_reputation[rival]
                        
                        self.record_reputation_change("faction", rival, ripple, 
                                                    f"Ripple effect from {faction_id} reputation change")
                        
                        results["ripple_effects"][rival] = {
                            "old_value": old_rep,
                            "new_value": new_rep,
                            "change": ripple
                        }
                        
                        # Check if a milestone was reached
                        milestone = self.check_reputation_milestone("faction", rival, new_rep)
                        if milestone:
                            results["ripple_effects"][rival]["milestone"] = milestone
                
                # Positively impact reputation with allied factions
                for ally in faction_data.get('allies', []):
                    ripple = amount // 3  # Allied factions are affected similarly at 1/3 strength
                    if ally in self.faction_reputation:
                        old_rep = self.faction_reputation[ally]
                        self.faction_reputation[ally] += ripple
                        # Clamp value between -100 and 100
                        self.faction_reputation[ally] = max(-100, min(100, self.faction_reputation[ally]))
                        new_rep = self.faction_reputation[ally]
                        
                        self.record_reputation_change("faction", ally, ripple, 
                                                    f"Allied effect from {faction_id} reputation change")
                        
                        results["ripple_effects"][ally] = {
                            "old_value": old_rep,
                            "new_value": new_rep,
                            "change": ripple
                        }
                        
                        # Check if a milestone was reached
                        milestone = self.check_reputation_milestone("faction", ally, new_rep)
                        if milestone:
                            results["ripple_effects"][ally]["milestone"] = milestone
                
                # Apply district reputation changes in controlled districts
                if district_manager:
                    for district_id in faction_data.get('districts', []):
                        district_ripple = amount // 4  # District reputation changes at 1/4 strength
                        
                        district_result = self.modify_district_reputation(
                            district_id, 
                            district_ripple, 
                            f"Faction control effect from {faction_id}")
                        
                        results["district_effects"][district_id] = district_result
        
        return results
    
    def _get_faction_data(self, faction_id: str) -> Dict:
        """Get faction relationship data"""
        # This would ideally come from a loaded faction data file, but for now we'll hard-code some relationships
        faction_relationships = {
            "arasaka": {
                "rivals": ["militech", "chrome_kings", "voodoo_boys", "deep_collective"],
                "allies": ["police", "biotech_inc"],
                "districts": ["corporate", "downtown", "neon_gardens"]
            },
            "militech": {
                "rivals": ["arasaka", "maelstrom", "deep_collective"],
                "allies": ["police", "chrome_kings"],
                "districts": ["tech_row", "industrial"]
            },
            "biotech_inc": {
                "rivals": ["eco_collective", "voodoo_boys"],
                "allies": ["arasaka", "police"],
                "districts": ["neon_gardens", "upscale"]
            },
            "aquatech": {
                "rivals": ["eco_collective", "sea_nomads"],
                "allies": ["arasaka"],
                "districts": ["floating_district", "corporate"]
            },
            "police": {
                "rivals": ["street_gangs", "maelstrom", "tunnel_rats", "jade_fist", "voodoo_boys", "smugglers_guild", "deep_collective"],
                "allies": ["arasaka", "militech", "biotech_inc"],
                "districts": ["downtown", "upscale", "corporate"]
            },
            "coast_guard": {
                "rivals": ["smugglers_guild", "sea_nomads", "pirates_syndicate"],
                "allies": ["police", "aquatech"],
                "districts": ["floating_district"]
            },
            "street_gangs": {
                "rivals": ["corporate", "police", "chrome_kings"],
                "allies": ["fixers", "tunnel_rats"],
                "districts": ["outskirts", "undercity", "industrial"]
            },
            "tunnel_rats": {
                "rivals": ["police", "chrome_kings"],
                "allies": ["maelstrom", "street_gangs"],
                "districts": ["undercity", "outskirts"]
            },
            "jade_fist": {
                "rivals": ["maelstrom", "police", "pirates_syndicate"],
                "allies": ["fixers", "smugglers_guild"],
                "districts": ["chinatown", "nightmarket"]
            },
            "chrome_kings": {
                "rivals": ["maelstrom", "tunnel_rats", "voodoo_boys", "deep_collective"],
                "allies": ["militech"],
                "districts": ["tech_row", "entertainment"]
            },
            "smugglers_guild": {
                "rivals": ["police", "coast_guard", "pirates_syndicate"],
                "allies": ["jade_fist", "fixers", "sea_nomads"],
                "districts": ["smugglers_den", "black_market", "industrial"]
            },
            "pirates_syndicate": {
                "rivals": ["jade_fist", "police", "coast_guard", "smugglers_guild"],
                "allies": ["voodoo_boys", "deep_collective"],
                "districts": ["black_market", "digital_depths"]
            },
            "voodoo_boys": {
                "rivals": ["police", "arasaka", "chrome_kings"],
                "allies": ["netrunners", "deep_collective", "pirates_syndicate"],
                "districts": ["virtual_quarter"]
            },
            "deep_collective": {
                "rivals": ["arasaka", "militech", "police", "chrome_kings"],
                "allies": ["voodoo_boys", "maelstrom", "pirates_syndicate"],
                "districts": ["digital_depths"]
            },
            "fixers": {
                "rivals": [],  # Fixers try to stay neutral with everyone
                "allies": ["jade_fist", "chrome_kings", "smugglers_guild"],
                "districts": ["downtown", "nightmarket"]
            },
            "netrunners": {
                "rivals": ["arasaka", "police"],
                "allies": ["voodoo_boys", "fixers", "deep_collective"],
                "districts": ["virtual_quarter", "tech_row", "digital_depths"]
            },
            "maelstrom": {
                "rivals": ["police", "chrome_kings", "jade_fist"],
                "allies": ["tunnel_rats", "deep_collective"],
                "districts": ["industrial", "wasteland"]
            },
            "eco_collective": {
                "rivals": ["biotech_inc", "aquatech"],
                "allies": ["sea_nomads"],
                "districts": ["neon_gardens", "residential"]
            },
            "sea_nomads": {
                "rivals": ["coast_guard", "aquatech"],
                "allies": ["eco_collective", "smugglers_guild"],
                "districts": ["floating_district"]
            }
        }
        
        return faction_relationships.get(faction_id, {})
    
    def get_reputation_title(self, reputation: int) -> str:
        """Get a title based on reputation score"""
        if reputation <= -80:
            return "Despised"
        elif reputation <= -60:
            return "Hated"
        elif reputation <= -40:
            return "Disliked"
        elif reputation <= -20:
            return "Suspicious"
        elif reputation < 20:
            return "Neutral"
        elif reputation < 40:
            return "Accepted"
        elif reputation < 60:
            return "Respected"
        elif reputation < 80:
            return "Honored"
        else:
            return "Revered"
    
    def has_access(self, district_id: str) -> bool:
        """Check if player has access to a district based on reputation"""
        rep = self.get_district_reputation(district_id)
        return rep > -60  # Very negative reputation locks you out
    
    def get_price_modifier(self, district_id: str, faction_id: str = None) -> float:
        """
        Get price modifier for goods in a district or from a faction based on reputation
        
        Args:
            district_id: The district ID
            faction_id: Optional faction ID
            
        Returns:
            Float price modifier (1.0 = normal price)
        """
        district_rep = self.get_district_reputation(district_id)
        
        # Base modifier from district reputation
        # Scale from 1.5x (despised) to 0.8x (revered)
        district_mod = 1.0 - (district_rep / 500)  # 100 rep = 20% discount, -100 rep = 20% markup
        
        # If faction is specified, include faction reputation in calculation
        if faction_id:
            faction_rep = self.get_faction_reputation(faction_id)
            faction_mod = 1.0 - (faction_rep / 400)  # 100 rep = 25% discount, -100 rep = 25% markup
            
            # Average district and faction modifiers, with faction having slightly more weight
            return (district_mod * 0.4) + (faction_mod * 0.6)
        
        return district_mod
    
    def get_combat_advantage(self, faction_id: str) -> Dict:
        """
        Get combat advantages based on faction reputation
        
        Args:
            faction_id: The faction ID
            
        Returns:
            Dict with bonuses: {"damage_bonus": float, "defense_bonus": float}
        """
        reputation = self.get_faction_reputation(faction_id)
        
        # Calculate advantage based on reputation level
        if reputation >= 50:  # Highly favored
            return {"damage_bonus": 0.0, "defense_bonus": 0.15, "status": "ally"}
        elif reputation >= 20:  # Favored
            return {"damage_bonus": 0.0, "defense_bonus": 0.05, "status": "friendly"}
        elif reputation <= -50:  # Highly hostile
            return {"damage_bonus": 0.15, "defense_bonus": -0.05, "status": "hostile"}
        elif reputation <= -20:  # Hostile
            return {"damage_bonus": 0.05, "defense_bonus": 0.0, "status": "unfriendly"}
        else:  # Neutral
            return {"damage_bonus": 0.0, "defense_bonus": 0.0, "status": "neutral"}
    
    def get_dialog_options(self, faction_id: str) -> List[str]:
        """
        Get available dialog options based on faction reputation
        
        Args:
            faction_id: The faction ID
            
        Returns:
            List of dialog option types available
        """
        reputation = self.get_faction_reputation(faction_id)
        
        # Base options always available
        options = ["neutral", "information"]
        
        # Add options based on reputation level
        if reputation >= 60:  # Highly respected
            options.extend(["special_missions", "faction_secrets", "special_deals"])
        elif reputation >= 40:  # Respected
            options.extend(["missions", "discounts", "faction_aid"])
        elif reputation >= 20:  # Accepted
            options.extend(["basic_missions", "fair_prices"])
        elif reputation <= -40:  # Disliked or worse
            options.extend(["threaten", "bribe", "intimidate"])
        
        return options
    
    def get_district_specific_events(self, district_id: str, reputation: int = None) -> List[Dict]:
        """
        Get special district events based on reputation
        
        Args:
            district_id: The district ID
            reputation: Optional reputation override (if None, uses current reputation)
            
        Returns:
            List of special events available in this district
        """
        if reputation is None:
            reputation = self.get_district_reputation(district_id)
        
        events = []
        
        # Base events available in most districts
        if reputation <= -60:  # Hated
            events.append({
                "id": "targeted_ambush",
                "name": "Targeted Ambush",
                "description": "You're specifically targeted by local gangs due to your negative reputation.",
                "type": "combat"
            })
        
        elif reputation <= -20:  # Suspicious
            events.append({
                "id": "suspicious_treatment",
                "name": "Suspicious Treatment",
                "description": "Locals are wary of you, prices are higher, and some services are unavailable.",
                "type": "social"
            })
        
        elif reputation >= 40:  # Respected
            events.append({
                "id": "friendly_contact",
                "name": "Friendly Contact",
                "description": "A local approaches you with information and offers assistance.",
                "type": "information"
            })
        
        elif reputation >= 80:  # Revered
            events.append({
                "id": "district_influence",
                "name": "District Influence",
                "description": "Your reputation grants you significant advantages in this district, including discounts, information, and protection.",
                "type": "benefit"
            })
            
        # District-specific events
        if district_id == "downtown":
            if reputation >= 50:
                events.append({
                    "id": "downtown_contacts",
                    "name": "Downtown Contacts",
                    "description": "Your positive reputation gives you access to influential contacts in the city's heart.",
                    "type": "social"
                })
            elif reputation <= -50:
                events.append({
                    "id": "downtown_harassment",
                    "name": "Police Harassment",
                    "description": "The police frequently stop and search you due to your negative reputation.",
                    "type": "social"
                })
        
        elif district_id == "undercity":
            if reputation >= 50:
                events.append({
                    "id": "undercity_safe_house",
                    "name": "Undercity Safe House",
                    "description": "You've been granted access to a secure location in the Undercity where you can rest safely.",
                    "type": "benefit"
                })
            elif reputation <= -50:
                events.append({
                    "id": "undercity_hunted",
                    "name": "Hunted in the Dark",
                    "description": "The Tunnel Rats have marked you for death in their territory.",
                    "type": "combat"
                })
        
        elif district_id == "tech_row":
            if reputation >= 50:
                events.append({
                    "id": "tech_row_prototype",
                    "name": "Prototype Access",
                    "description": "A tech developer offers you the chance to test experimental technology.",
                    "type": "benefit"
                })
        
        elif district_id == "digital_depths":
            if reputation >= 60:
                events.append({
                    "id": "digital_depths_backdoor",
                    "name": "Digital Backdoor",
                    "description": "You've been granted a special access key that bypasses normal security in the digital realm.",
                    "type": "benefit"
                })
            elif reputation <= -60:
                events.append({
                    "id": "digital_depths_trace",
                    "name": "Digital Trace",
                    "description": "Your negative reputation has made you a target for advanced AI security systems throughout the Digital Depths.",
                    "type": "technology"
                })
        
        elif district_id == "floating_district":
            if reputation >= 50:
                events.append({
                    "id": "floating_district_hidden_market",
                    "name": "Hidden Market Access",
                    "description": "Your positive reputation grants you access to the exclusive underwater market.",
                    "type": "shopping"
                })
        
        return events
    
    def get_faction_specific_events(self, faction_id: str, reputation: int = None) -> List[Dict]:
        """
        Get special faction events based on reputation
        
        Args:
            faction_id: The faction ID
            reputation: Optional reputation override (if None, uses current reputation)
            
        Returns:
            List of special events available with this faction
        """
        if reputation is None:
            reputation = self.get_faction_reputation(faction_id)
        
        events = []
        
        # Base events available for most factions
        if reputation <= -80:  # Despised
            events.append({
                "id": "kill_order",
                "name": "Kill Order",
                "description": f"The {faction_id} has placed a bounty on your head.",
                "type": "hostility"
            })
        
        elif reputation <= -40:  # Disliked
            events.append({
                "id": "faction_harassment",
                "name": "Faction Harassment",
                "description": f"Members of the {faction_id} regularly harass you in their territory.",
                "type": "social"
            })
        
        elif reputation >= 60:  # Honored
            events.append({
                "id": "faction_backing",
                "name": "Faction Backing",
                "description": f"The {faction_id} provides you with protection and resources.",
                "type": "benefit"
            })
        
        elif reputation >= 90:  # Nearly maxed
            events.append({
                "id": "faction_request",
                "name": "Special Request",
                "description": f"A leader of the {faction_id} approaches you with a special mission.",
                "type": "mission"
            })
            
        # Faction-specific events
        if faction_id == "arasaka":
            if reputation >= 75:
                events.append({
                    "id": "arasaka_prototype",
                    "name": "Arasaka Prototype Access",
                    "description": "Your high standing with Arasaka has granted you access to experimental corporate technology.",
                    "type": "technology"
                })
            elif reputation <= -75:
                events.append({
                    "id": "arasaka_blacklist",
                    "name": "Corporate Blacklist",
                    "description": "Arasaka has blacklisted you from all corporate services and placed a security alert on your identity.",
                    "type": "social"
                })
        
        elif faction_id == "voodoo_boys":
            if reputation >= 75:
                events.append({
                    "id": "voodoo_netrunning",
                    "name": "Voodoo NetRunning Techniques",
                    "description": "The Voodoo Boys have shared some of their unique netrunning methods with you.",
                    "type": "technology"
                })
        
        elif faction_id == "deep_collective":
            if reputation >= 80:
                events.append({
                    "id": "deep_collective_ai",
                    "name": "AI Companion",
                    "description": "The Deep Collective has granted you a personal AI companion that assists with digital operations.",
                    "type": "technology"
                })
        
        elif faction_id == "jade_fist":
            if reputation >= 70:
                events.append({
                    "id": "jade_fist_training",
                    "name": "Jade Fist Combat Training",
                    "description": "You've been invited to train in the Jade Fist's secret combat techniques.",
                    "type": "combat"
                })
        
        elif faction_id == "eco_collective":
            if reputation >= 60:
                events.append({
                    "id": "eco_biotech",
                    "name": "Eco-Biotech Access",
                    "description": "The Eco Collective shares their sustainable biotechnology with you.",
                    "type": "technology"
                })
        
        return events
    
    def to_dict(self) -> Dict:
        """Convert reputation data to dictionary (for saving)"""
        return {
            'district_reputation': self.district_reputation,
            'faction_reputation': self.faction_reputation,
            'reputation_history': self.reputation_history,
            'reputation_milestones': self.reputation_milestones
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create reputation system from a dictionary"""
        reputation = cls()
        reputation.district_reputation = data.get('district_reputation', {})
        reputation.faction_reputation = data.get('faction_reputation', {})
        reputation.reputation_history = data.get('reputation_history', [])
        
        # Handle milestones with a default if not present in saved data
        if 'reputation_milestones' in data:
            reputation.reputation_milestones = data['reputation_milestones']
        else:
            reputation.reputation_milestones = {
                "district": {},
                "faction": {}
            }
            
        return reputation

class DistrictManager:
    """Manages all districts in the cyberpunk city"""
    
    def __init__(self):
        """Initialize the district manager"""
        self.districts: Dict[str, District] = {}
        self.factions: Dict[str, Faction] = {}
        self.current_district: Optional[str] = None
        self.load_districts()
        self.load_factions()
    
    def load_districts(self) -> None:
        """Load districts from JSON file"""
        try:
            if os.path.exists('data/districts.json'):
                with open('data/districts.json', 'r') as f:
                    data = json.load(f)
                    for district_data in data:
                        district = District.from_dict(district_data)
                        self.districts[district.district_id] = district
                        
                    # Set default district if none is loaded
                    if not self.current_district and self.districts:
                        self.current_district = next(iter(self.districts))
            else:
                self.create_default_districts()
        except Exception as e:
            print(f"Error loading districts: {e}")
            self.create_default_districts()
    
    def load_factions(self) -> None:
        """Load factions from JSON file or create defaults"""
        try:
            if os.path.exists('data/factions.json'):
                with open('data/factions.json', 'r') as f:
                    data = json.load(f)
                    for faction_data in data:
                        faction = Faction.from_dict(faction_data)
                        self.factions[faction.faction_id] = faction
            else:
                self.create_default_factions()
        except Exception as e:
            print(f"Error loading factions: {e}")
            self.create_default_factions()
    
    def create_default_districts(self) -> None:
        """Create default districts if none are loaded"""
        # Create the default districts
        self.add_district(
            District(
                district_id="downtown",
                name="Downtown",
                description="The heart of the city, towering skyscrapers and corporate headquarters. High security, but opportunities for those who know where to look.",
                danger_level=3,  # Moderate danger
                connected_districts=["industrial", "residential", "nightmarket", "corporate", "chinatown"],
                ascii_art="downtown",
                map_position={"x": 2, "y": 2},
                location_choices=[
                    {"id": "visit_bar", "text": "Visit the Neon Dragon Bar", "type": "social"},
                    {"id": "hack_public_terminal", "text": "Hack a public terminal", "type": "tech"},
                    {"id": "corporate_job", "text": "Look for corporate contract work", "type": "job"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="industrial",
                name="Industrial Zone",
                description="Factories and warehouses dominate this polluted district. Home to smugglers and underground operations.",
                danger_level=4,  # High danger
                connected_districts=["downtown", "outskirts", "nightmarket", "tech_row"],
                ascii_art="industrial",
                map_position={"x": 3, "y": 1},
                location_choices=[
                    {"id": "scavenge_parts", "text": "Scavenge for tech parts", "type": "resource"},
                    {"id": "smuggler_contact", "text": "Meet with smuggler contact", "type": "criminal"},
                    {"id": "gang_territory", "text": "Navigate gang territory", "type": "combat"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="residential",
                name="Residential Sector",
                description="Dense apartment blocks where most of the city's population lives. Varying levels of safety depending on the block.",
                danger_level=2,  # Lower danger
                connected_districts=["downtown", "outskirts", "entertainment", "chinatown"],
                ascii_art="residential",
                map_position={"x": 1, "y": 3},
                location_choices=[
                    {"id": "visit_apartment", "text": "Return to your apartment", "type": "rest"},
                    {"id": "local_gossip", "text": "Gather local gossip", "type": "info"},
                    {"id": "help_neighbor", "text": "Help a neighbor in trouble", "type": "social"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="outskirts",
                name="City Outskirts",
                description="The fringe of the city, lawless and dangerous. Only the desperate or the powerful venture here willingly.",
                danger_level=5,  # Extremely dangerous
                connected_districts=["industrial", "residential", "wasteland", "undercity"],
                ascii_art="outskirts",
                map_position={"x": 0, "y": 4},
                location_choices=[
                    {"id": "scavenger_hunt", "text": "Join a scavenger hunt", "type": "resource"},
                    {"id": "illegal_cyberware", "text": "Purchase illegal cyberware", "type": "upgrade"},
                    {"id": "gang_confrontation", "text": "Confront a dangerous gang", "type": "combat"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="corporate",
                name="Corporate Sector",
                description="The pristine and heavily guarded zone where the elite live and work. Access is strictly controlled.",
                danger_level=1,  # Safest area
                connected_districts=["downtown", "upscale", "tech_row"],
                ascii_art="corporate",
                map_position={"x": 3, "y": 3},
                location_choices=[
                    {"id": "corporate_infiltration", "text": "Infiltrate a corporate building", "type": "stealth"},
                    {"id": "elite_networking", "text": "Network with corporate elites", "type": "social"},
                    {"id": "security_bypass", "text": "Bypass advanced security systems", "type": "tech"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="nightmarket",
                name="Night Market",
                description="A vibrant, crowded marketplace that comes alive after dark. Every item imaginable can be found here - legal or otherwise.",
                danger_level=3,
                connected_districts=["downtown", "industrial", "entertainment", "tech_row", "chinatown"],
                ascii_art="market",
                map_position={"x": 2, "y": 1},
                location_choices=[
                    {"id": "haggle_items", "text": "Haggle for unusual items", "type": "shopping"},
                    {"id": "food_stalls", "text": "Sample exotic street food", "type": "social"},
                    {"id": "pickpocket", "text": "Practice your pickpocketing skills", "type": "criminal"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="entertainment",
                name="Entertainment District",
                description="Neon lights and pulsing music fill this district of clubs, casinos, and virtual reality arcades. Pleasure and vice of all kinds await.",
                danger_level=2,
                connected_districts=["residential", "nightmarket", "upscale", "virtual_quarter"],
                ascii_art="bar_exterior",
                map_position={"x": 1, "y": 2},
                location_choices=[
                    {"id": "vr_gaming", "text": "Compete in VR championships", "type": "recreation"},
                    {"id": "club_connections", "text": "Make connections at an exclusive club", "type": "social"},
                    {"id": "gambling", "text": "Try your luck at the neon casino", "type": "chance"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="upscale",
                name="Upscale District",
                description="Clean streets and modernist architecture define this affluent area. Home to successful freelancers, corporate managers, and anyone who's made it big enough to afford real safety.",
                danger_level=1,
                connected_districts=["corporate", "entertainment", "virtual_quarter"],
                ascii_art="corporate_office",
                map_position={"x": 2, "y": 3},
                location_choices=[
                    {"id": "high_society", "text": "Infiltrate high society", "type": "social"},
                    {"id": "gallery_exhibition", "text": "Attend a cybernetic art exhibition", "type": "culture"},
                    {"id": "luxury_theft", "text": "Plan a high-end theft", "type": "criminal"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="wasteland",
                name="The Wasteland",
                description="The toxic, irradiated zone beyond the city limits. Mutated wildlife, desperate outcasts, and hidden treasures await those brave or foolish enough to venture here.",
                danger_level=5,
                connected_districts=["outskirts", "undercity"],
                ascii_art="alley",
                map_position={"x": 0, "y": 5},
                location_choices=[
                    {"id": "resource_expedition", "text": "Hunt for rare resources", "type": "exploration"},
                    {"id": "mutant_hunt", "text": "Hunt dangerous mutated creatures", "type": "combat"},
                    {"id": "outcast_camp", "text": "Find an outcast settlement", "type": "discovery"}
                ]
            )
        )
        
        # New Districts
        self.add_district(
            District(
                district_id="chinatown",
                name="Chinatown",
                description="Ancient traditions blend with cutting-edge tech in this cultural enclave. Street food vendors, medicine shops, and traditional markets operate alongside hacker collectives and black market cyberware dealers.",
                danger_level=3,
                connected_districts=["downtown", "residential", "nightmarket"],
                ascii_art="street",
                map_position={"x": 1, "y": 1},
                location_choices=[
                    {"id": "medicine_shop", "text": "Visit traditional medicine shop", "type": "shopping"},
                    {"id": "data_broker", "text": "Meet with a data broker", "type": "info"},
                    {"id": "triad_business", "text": "Handle business with the Jade Fist Triad", "type": "criminal"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="tech_row",
                name="Tech Row",
                description="The cutting edge of technology development. Research labs, prototype workshops, and tech startups fill this district. Security is tight, but the rewards for infiltration are substantial.",
                danger_level=3,
                connected_districts=["corporate", "industrial", "nightmarket", "virtual_quarter"],
                ascii_art="tech_shop",
                map_position={"x": 3, "y": 2},
                location_choices=[
                    {"id": "tech_heist", "text": "Plan a tech prototype heist", "type": "criminal"},
                    {"id": "debug_work", "text": "Take on debugging contract work", "type": "job"},
                    {"id": "ai_consultation", "text": "Consult with rogue AI collective", "type": "tech"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="undercity",
                name="Undercity",
                description="A vast network of tunnels, abandoned subway stations, and underground structures beneath the city. Home to those who've fallen through society's cracks and prefer to stay hidden.",
                danger_level=4,
                connected_districts=["outskirts", "wasteland"],
                ascii_art="subway",
                map_position={"x": 0, "y": 3},
                location_choices=[
                    {"id": "black_clinic", "text": "Visit an underground medical clinic", "type": "health"},
                    {"id": "tunnel_rats", "text": "Meet with the Tunnel Rats gang", "type": "criminal"},
                    {"id": "relic_hunter", "text": "Join relic hunters exploring ancient infrastructure", "type": "exploration"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="virtual_quarter",
                name="Virtual Quarter",
                description="Physical and digital realms blur in this district dedicated to virtual reality and augmented experiences. VR cafes, augmented reality parks, and digital consciousness research facilities dominate the landscape.",
                danger_level=2,
                connected_districts=["entertainment", "upscale", "tech_row", "digital_depths"],
                ascii_art="cyberspace",
                map_position={"x": 2, "y": 0},
                location_choices=[
                    {"id": "deep_dive", "text": "Deep dive in illegal VR simulation", "type": "recreation"},
                    {"id": "digital_ghost", "text": "Track down a digital ghost", "type": "tech"},
                    {"id": "zero_day_market", "text": "Browse the zero-day exploit market", "type": "criminal"}
                ]
            )
        )
        
        # New Districts (Expansion)
        self.add_district(
            District(
                district_id="digital_depths",
                name="Digital Depths",
                description="Beneath the Virtual Quarter lies the unauthorized depths of cyberspace. Rogue AIs, digital phantoms, and the most skilled netrunners frequent this district. The distinction between reality and digital constructs is nonexistent here.",
                danger_level=4,
                connected_districts=["virtual_quarter", "tech_row", "black_market"],
                ascii_art="deep_cyberspace",
                map_position={"x": 3, "y": 0},
                location_choices=[
                    {"id": "ai_commune", "text": "Visit the AI commune", "type": "tech"},
                    {"id": "black_ice_diving", "text": "Navigate the Black ICE security zones", "type": "combat"},
                    {"id": "construct_exploration", "text": "Explore digital consciousness constructs", "type": "discovery"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="black_market",
                name="Black Market Nexus",
                description="A hidden commercial zone where anything can be bought or sold. Constantly changing location to avoid authorities, those in the know can always find it. Illegal cyberware, weapons, and underground services thrive here.",
                danger_level=4,
                connected_districts=["nightmarket", "digital_depths", "undercity", "smugglers_den"],
                ascii_art="black_market",
                map_position={"x": 1, "y": 0},
                location_choices=[
                    {"id": "arms_dealer", "text": "Meet with an arms dealer", "type": "shopping"},
                    {"id": "identity_broker", "text": "Purchase a new identity", "type": "criminal"},
                    {"id": "military_tech", "text": "Browse military-grade technology", "type": "shopping"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="smugglers_den",
                name="Smuggler's Den",
                description="A maze of warehouses and hidden docks. The primary entry point for illegal goods entering the city. Heavily controlled by various criminal factions who maintain an uneasy truce to keep business flowing.",
                danger_level=3,
                connected_districts=["industrial", "black_market", "nightmarket"],
                ascii_art="warehouse",
                map_position={"x": 4, "y": 1},
                location_choices=[
                    {"id": "smuggle_run", "text": "Join a smuggling operation", "type": "job"},
                    {"id": "fence_goods", "text": "Fence stolen goods", "type": "criminal"},
                    {"id": "customs_bribe", "text": "Bribe customs official", "type": "social"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="floating_district",
                name="Floating District",
                description="A collection of barges, ships, and artificial islands off the coast. Initially a refugee settlement, it's now a thriving community outside mainstream city control. Known for innovative tech recycling and a unique cultural blend.",
                danger_level=2,
                connected_districts=["nightmarket", "smugglers_den", "industrial"],
                ascii_art="floating_city",
                map_position={"x": 5, "y": 2},
                location_choices=[
                    {"id": "salvage_tech", "text": "Salvage technology from the water", "type": "resource"},
                    {"id": "floating_market", "text": "Browse the floating markets", "type": "shopping"},
                    {"id": "ocean_farm", "text": "Visit the aqua-culture farms", "type": "discovery"}
                ]
            )
        )
        
        self.add_district(
            District(
                district_id="neon_gardens",
                name="Neon Gardens",
                description="A district where bioluminescent plants and genetically modified flora merge with technology. Vibrant and beautiful, it serves as both a high-end recreational area and a cutting-edge biotech research zone.",
                danger_level=1,
                connected_districts=["upscale", "entertainment", "residential"],
                ascii_art="garden",
                map_position={"x": 1, "y": 4},
                location_choices=[
                    {"id": "botanical_tour", "text": "Tour the bioluminescent gardens", "type": "recreation"},
                    {"id": "gene_therapy", "text": "Visit a gene therapy clinic", "type": "health"},
                    {"id": "biotech_research", "text": "Participate in biotech research", "type": "job"}
                ]
            )
        )
        
        # Set default current district
        self.current_district = "downtown"
        
        # Save districts to file
        self.save_districts()
    
    def add_district(self, district: District) -> None:
        """Add a new district"""
        self.districts[district.district_id] = district
    
    def get_district(self, district_id: str) -> Optional[District]:
        """Get a district by ID"""
        return self.districts.get(district_id)
    
    def get_current_district(self) -> Optional[District]:
        """Get the current district object"""
        if self.current_district:
            return self.get_district(self.current_district)
        return None
    
    def set_current_district(self, district_id: str) -> bool:
        """Set the current district"""
        if district_id in self.districts:
            self.current_district = district_id
            return True
        return False
    
    def get_connected_districts(self) -> List[District]:
        """Get a list of districts connected to the current one"""
        current = self.get_current_district()
        if not current:
            return []
        
        connected = []
        for district_id in current.connected_districts:
            district = self.get_district(district_id)
            if district:
                connected.append(district)
        
        return connected
    
    def can_travel_to(self, district_id: str) -> bool:
        """Check if player can travel to a district from current position"""
        current = self.get_current_district()
        if not current:
            return False
        
        return district_id in current.connected_districts
    
    def generate_map_display(self) -> List[str]:
        """
        Generate a visual ASCII map of the city showing all districts and connections
        
        Returns:
            List[str]: Lines of the map display
        """
        # Find map dimensions
        max_x = max_y = 0
        for district in self.districts.values():
            max_x = max(max_x, district.map_position["x"])
            max_y = max(max_y, district.map_position["y"])
        
        # Create map grid (6x6 cells per district)
        width = (max_x + 2) * 10
        height = (max_y + 2) * 5
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw connections between districts
        for district in self.districts.values():
            src_x = district.map_position["x"] * 10 + 5
            src_y = district.map_position["y"] * 5 + 2
            
            for conn_id in district.connected_districts:
                if conn_id in self.districts:
                    conn = self.districts[conn_id]
                    dst_x = conn.map_position["x"] * 10 + 5
                    dst_y = conn.map_position["y"] * 5 + 2
                    
                    # Draw connection line
                    self._draw_line(grid, src_x, src_y, dst_x, dst_y, '·')
        
        # Draw districts
        current = self.get_current_district()
        for district in self.districts.values():
            x = district.map_position["x"] * 10
            y = district.map_position["y"] * 5
            
            # Mark current district with different style
            is_current = current and district.district_id == current.district_id
            grid[y][x:x+10] = list('┌' + '─'*8 + '┐')
            
            # Show district name
            name = district.name[:8].center(8)
            grid[y+1][x:x+10] = list('│' + name + '│')
            
            # Show danger level with visual indicator
            danger = ''.join(['█' if i <= district.danger_level else '░' for i in range(1, 6)])
            danger_display = danger.center(8)
            grid[y+2][x:x+10] = list('│' + danger_display + '│')
            
            # Mark connections
            connection_count = len(district.connected_districts)
            conn_indicator = f"[{connection_count}]".center(8)
            grid[y+3][x:x+10] = list('│' + conn_indicator + '│')
            
            grid[y+4][x:x+10] = list('└' + '─'*8 + '┘')
        
        # Convert grid to string lines
        map_lines = [''.join(row) for row in grid]
        
        return map_lines
    
    def _draw_line(self, grid, x1, y1, x2, y2, char):
        """Draw a line on the grid using Bresenham's algorithm"""
        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = abs(y2 - y1)
        error = dx // 2
        y = y1
        y_step = 1 if y1 < y2 else -1
        
        for x in range(x1, x2 + 1):
            if steep:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = char
            else:
                if 0 <= y < len(grid[0]) and 0 <= x < len(grid):
                    grid[x][y] = char
            
            error -= dy
            if error < 0:
                y += y_step
                error += dx
    
    def get_district_location_choices(self, district_id: str = None) -> List[Dict]:
        """
        Get location-specific choices for the given district or current district
        
        Args:
            district_id (str, optional): District ID to get choices for. If None, uses current district.
            
        Returns:
            List[Dict]: List of location choice dictionaries
        """
        if district_id is None:
            current = self.get_current_district()
            if not current:
                return []
            district_id = current.district_id
        
        district = self.get_district(district_id)
        if not district:
            return []
        
        return district.get_location_choices()
        
    def save_districts(self) -> None:
        """Save districts to JSON file"""
        try:
            # Make sure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Convert districts to list of dictionaries
            district_data = [district.to_dict() for district in self.districts.values()]
            
            with open('data/districts.json', 'w') as f:
                json.dump(district_data, f, indent=2)
        except Exception as e:
            print(f"Error saving districts: {e}")
    
    def create_default_factions(self) -> None:
        """Create default factions if none are loaded"""
        # Major corporate factions
        self.add_faction(
            Faction(
                faction_id="arasaka",
                name="Arasaka Corporation",
                description="A powerful Japanese multinational security corporation specializing in corporate security, private military contracting, and manufacturing.",
                home_district="corporate",
                rival_factions=["militech", "chrome_kings", "voodoo_boys", "deep_collective"],
                allied_factions=["police", "biotech_inc"],
                controlled_districts=["corporate", "downtown", "neon_gardens"],
                faction_type="corp"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="militech",
                name="Militech International",
                description="A powerful American weapons manufacturer and private military contractor, often at odds with Arasaka.",
                home_district="tech_row",
                rival_factions=["arasaka", "maelstrom", "deep_collective"],
                allied_factions=["police", "chrome_kings"],
                controlled_districts=["tech_row", "industrial"],
                faction_type="corp"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="biotech_inc",
                name="BioTech Incorporated",
                description="A leading biotechnology corporation specializing in genetic enhancement, medical implants, and synthetic biology. Their breakthroughs are revolutionary but often morally questionable.",
                home_district="neon_gardens",
                rival_factions=["eco_collective", "voodoo_boys"],
                allied_factions=["arasaka", "police"],
                controlled_districts=["neon_gardens", "upscale"],
                faction_type="corp"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="aquatech",
                name="AquaTech Conglomerate",
                description="A maritime technology corporation that specializes in oceanic engineering, water purification, and floating architecture. They control most of the city's water infrastructure.",
                home_district="floating_district",
                rival_factions=["eco_collective", "sea_nomads"],
                allied_factions=["arasaka"],
                controlled_districts=["floating_district", "corporate"],
                faction_type="corp"
            )
        )
        
        # Government/Law Enforcement
        self.add_faction(
            Faction(
                faction_id="police",
                name="NCPD (Neo-Shanghai Police Department)",
                description="The city's police force, stretched thin and often corrupt. Still, they maintain order in the more affluent areas.",
                home_district="downtown",
                rival_factions=["street_gangs", "maelstrom", "tunnel_rats", "voodoo_boys", "smugglers_guild", "deep_collective"],
                allied_factions=["arasaka", "militech", "biotech_inc"],
                controlled_districts=["downtown", "upscale", "corporate"],
                faction_type="government"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="coast_guard",
                name="Augmented Coast Guard",
                description="The militarized law enforcement division that patrols the city's coastal areas. They use advanced technology to monitor maritime activities and are especially hostile to smugglers.",
                home_district="floating_district",
                rival_factions=["smugglers_guild", "sea_nomads", "pirates_syndicate"],
                allied_factions=["police", "aquatech"],
                controlled_districts=["floating_district"],
                faction_type="government"
            )
        )
        
        # Street Gangs
        self.add_faction(
            Faction(
                faction_id="maelstrom",
                name="Maelstrom",
                description="A gang known for extreme cybernetic modification and violent, unpredictable behavior.",
                home_district="industrial",
                rival_factions=["police", "chrome_kings", "jade_fist"],
                allied_factions=["tunnel_rats", "deep_collective"],
                controlled_districts=["industrial", "wasteland"],
                faction_type="gang"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="tunnel_rats",
                name="Tunnel Rats",
                description="A gang that lives in the forgotten tunnels and subway systems beneath the city. Experts in underground navigation and survival.",
                home_district="undercity",
                rival_factions=["police", "chrome_kings"],
                allied_factions=["maelstrom", "street_gangs"],
                controlled_districts=["undercity", "outskirts"],
                faction_type="gang"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="jade_fist",
                name="Jade Fist Triad",
                description="A traditional yet technologically sophisticated criminal organization with deep roots in Chinatown.",
                home_district="chinatown",
                rival_factions=["maelstrom", "police", "pirates_syndicate"],
                allied_factions=["fixers", "smugglers_guild"],
                controlled_districts=["chinatown", "nightmarket"],
                faction_type="gang"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="chrome_kings",
                name="Chrome Kings",
                description="A gang of high-end cybernetic enthusiasts who value style and technological superiority. Control much of the illegal tech market.",
                home_district="tech_row",
                rival_factions=["maelstrom", "tunnel_rats", "voodoo_boys", "deep_collective"],
                allied_factions=["militech"],
                controlled_districts=["tech_row", "entertainment"],
                faction_type="gang"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="smugglers_guild",
                name="Smugglers Guild",
                description="A loose association of smugglers, transporters, and black market logistics experts who control the flow of illegal goods in and out of the city.",
                home_district="smugglers_den",
                rival_factions=["police", "coast_guard", "pirates_syndicate"],
                allied_factions=["jade_fist", "fixers", "sea_nomads"],
                controlled_districts=["smugglers_den", "black_market", "industrial"],
                faction_type="gang"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="pirates_syndicate",
                name="Digital Pirates Syndicate",
                description="High-tech thieves who specialize in data theft, corporate espionage, and digital heists. They maintain a physical presence in the city but operate primarily through the digital realm.",
                home_district="black_market",
                rival_factions=["jade_fist", "police", "coast_guard", "smugglers_guild"],
                allied_factions=["voodoo_boys", "deep_collective"],
                controlled_districts=["black_market", "digital_depths"],
                faction_type="gang"
            )
        )
        
        # Hackers/Netrunners
        self.add_faction(
            Faction(
                faction_id="voodoo_boys",
                name="Voodoo Boys",
                description="Elite netrunners who have turned the virtual world into a mystical realm. They delve deeper into cyberspace than anyone else dares.",
                home_district="virtual_quarter",
                rival_factions=["police", "arasaka", "chrome_kings"],
                allied_factions=["netrunners", "deep_collective", "pirates_syndicate"],
                controlled_districts=["virtual_quarter"],
                faction_type="netrunner"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="deep_collective",
                name="Deep Collective",
                description="A secretive group of netrunners, AI sympathizers, and digital consciousness pioneers who operate in the deepest layers of cyberspace. They're rumored to collaborate with emergent AIs.",
                home_district="digital_depths",
                rival_factions=["arasaka", "militech", "police", "chrome_kings"],
                allied_factions=["voodoo_boys", "maelstrom", "pirates_syndicate"],
                controlled_districts=["digital_depths"],
                faction_type="netrunner"
            )
        )
        
        # Neutral/Independent
        self.add_faction(
            Faction(
                faction_id="fixers",
                name="Fixer Network",
                description="Independent middlemen who connect clients with contractors for all sorts of jobs - legal or otherwise.",
                home_district="downtown",
                rival_factions=[],
                allied_factions=["jade_fist", "chrome_kings", "smugglers_guild"],
                controlled_districts=["downtown", "nightmarket"],
                faction_type="neutral"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="netrunners",
                name="Netrunner Collective",
                description="A loose association of hackers, data miners, and digital specialists who sell their services to the highest bidder.",
                home_district="virtual_quarter",
                rival_factions=["arasaka", "police"],
                allied_factions=["voodoo_boys", "fixers", "deep_collective"],
                controlled_districts=["virtual_quarter", "tech_row", "digital_depths"],
                faction_type="netrunner"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="eco_collective",
                name="Eco Collective",
                description="Environmental activists and scientists using advanced technology to combat corporate pollution and ecological destruction. They have a significant presence in the Neon Gardens.",
                home_district="neon_gardens",
                rival_factions=["biotech_inc", "aquatech"],
                allied_factions=["sea_nomads"],
                controlled_districts=["neon_gardens", "residential"],
                faction_type="neutral"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="sea_nomads",
                name="Sea Nomads",
                description="A community of maritime wanderers who live on self-sufficient floating vessels. They maintain independence from the city's power structures through sustainable technology and resource sharing.",
                home_district="floating_district",
                rival_factions=["coast_guard", "aquatech"],
                allied_factions=["eco_collective", "smugglers_guild"],
                controlled_districts=["floating_district"],
                faction_type="neutral"
            )
        )
        
        # Save factions to file
        self.save_factions()
        
    def add_faction(self, faction: Faction) -> None:
        """Add a new faction"""
        self.factions[faction.faction_id] = faction
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """Get a faction by ID"""
        return self.factions.get(faction_id)
    
    def get_factions_in_district(self, district_id: str) -> List[Faction]:
        """Get all factions that control or are based in a district"""
        result = []
        for faction in self.factions.values():
            if district_id in faction.controlled_districts or faction.home_district == district_id:
                result.append(faction)
        return result
    
    def get_faction_by_name(self, faction_name: str) -> Optional[Faction]:
        """Find a faction by its name (case-insensitive partial match)"""
        faction_name_lower = faction_name.lower()
        for faction in self.factions.values():
            if faction_name_lower in faction.name.lower():
                return faction
        return None
    
    def save_factions(self) -> None:
        """Save factions to JSON file"""
        try:
            # Make sure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Convert factions to list of dictionaries
            faction_data = [faction.to_dict() for faction in self.factions.values()]
            
            with open('data/factions.json', 'w') as f:
                json.dump(faction_data, f, indent=2)
        except Exception as e:
            print(f"Error saving factions: {e}")
    
    def to_dict(self) -> Dict:
        """Convert district manager to dictionary (for saving)"""
        return {
            'current_district': self.current_district
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create district manager from a dictionary"""
        manager = cls()
        manager.current_district = data.get('current_district')
        return manager

# Create default ASCII art for districts
def add_district_ascii_art():
    """Add ASCII art for districts to the assets module"""
    from data.ascii_art import ASCII_ART