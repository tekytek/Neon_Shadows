"""
Districts Module - Manages city districts and reputation systems
"""
import json
import os
from typing import Dict, List, Optional, Tuple

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
        
        # Initialize default faction relationships
        self._initialize_default_factions()
    
    def _initialize_default_factions(self):
        """Initialize default factions and reputations"""
        # Initialize all faction reputations to 0 (neutral)
        default_factions = [
            "corporate", "police", "street_gangs", "fixers", "netrunners",
            "tunnel_rats", "jade_fist", "chrome_kings", "voodoo_boys", "maelstrom"
        ]
        
        for faction in default_factions:
            if faction not in self.faction_reputation:
                self.faction_reputation[faction] = 0
                
    def get_district_reputation(self, district_id: str) -> int:
        """Get reputation in a specific district"""
        return self.district_reputation.get(district_id, 0)
    
    def get_faction_reputation(self, faction_id: str) -> int:
        """Get reputation with a specific faction"""
        return self.faction_reputation.get(faction_id, 0)
    
    def modify_district_reputation(self, district_id: str, amount: int) -> int:
        """
        Modify reputation in a district
        
        Args:
            district_id: The district ID
            amount: Amount to change (positive or negative)
            
        Returns:
            New reputation value
        """
        if district_id not in self.district_reputation:
            self.district_reputation[district_id] = 0
        
        self.district_reputation[district_id] += amount
        
        # Clamp value between -100 and 100
        self.district_reputation[district_id] = max(-100, min(100, self.district_reputation[district_id]))
        
        return self.district_reputation[district_id]
    
    def modify_faction_reputation(self, faction_id: str, amount: int, district_manager=None) -> Dict:
        """
        Modify reputation with a faction and handle faction relationships
        
        Args:
            faction_id: The faction ID
            amount: Amount to change (positive or negative)
            district_manager: Optional DistrictManager to handle faction district effects
            
        Returns:
            Dict with reputation changes and secondary effects
        """
        results = {
            "primary_change": 0,
            "ripple_effects": {}
        }
        
        # Update primary faction reputation
        if faction_id not in self.faction_reputation:
            self.faction_reputation[faction_id] = 0
        
        self.faction_reputation[faction_id] += amount
        
        # Clamp value between -100 and 100
        self.faction_reputation[faction_id] = max(-100, min(100, self.faction_reputation[faction_id]))
        results["primary_change"] = amount
        
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
                        results["ripple_effects"][rival] = ripple
                
                # Positively impact reputation with allied factions
                for ally in faction_data.get('allies', []):
                    ripple = amount // 3  # Allied factions are affected similarly at 1/3 strength
                    if ally in self.faction_reputation:
                        old_rep = self.faction_reputation[ally]
                        self.faction_reputation[ally] += ripple
                        # Clamp value between -100 and 100
                        self.faction_reputation[ally] = max(-100, min(100, self.faction_reputation[ally]))
                        results["ripple_effects"][ally] = ripple
                
                # Apply district reputation changes in controlled districts
                if district_manager:
                    for district_id in faction_data.get('districts', []):
                        district_ripple = amount // 4  # District reputation changes at 1/4 strength
                        old_district_rep = self.get_district_reputation(district_id)
                        self.modify_district_reputation(district_id, district_ripple)
                        results["ripple_effects"][f"district_{district_id}"] = district_ripple
        
        return results
    
    def _get_faction_data(self, faction_id: str) -> Dict:
        """Get faction relationship data"""
        # This would ideally come from a loaded faction data file, but for now we'll hard-code some relationships
        faction_relationships = {
            "corporate": {
                "rivals": ["street_gangs", "netrunners", "voodoo_boys", "maelstrom"],
                "allies": ["police", "fixers"],
                "districts": ["corporate", "upscale", "tech_row"]
            },
            "police": {
                "rivals": ["street_gangs", "netrunners", "tunnel_rats", "jade_fist", "voodoo_boys", "maelstrom"],
                "allies": ["corporate", "fixers"],
                "districts": ["downtown", "upscale", "corporate"]
            },
            "street_gangs": {
                "rivals": ["corporate", "police", "chrome_kings"],
                "allies": ["fixers", "tunnel_rats"],
                "districts": ["outskirts", "undercity", "industrial"]
            },
            "fixers": {
                "rivals": [],  # Fixers try to stay neutral with everyone
                "allies": ["corporate", "street_gangs", "netrunners"],
                "districts": ["downtown", "nightmarket"]
            },
            "netrunners": {
                "rivals": ["corporate", "police"],
                "allies": ["fixers", "voodoo_boys"],
                "districts": ["virtual_quarter", "tech_row"]
            },
            "tunnel_rats": {
                "rivals": ["police", "corporate", "chrome_kings"],
                "allies": ["street_gangs"],
                "districts": ["undercity", "outskirts"]
            },
            "jade_fist": {
                "rivals": ["police", "maelstrom"],
                "allies": ["fixers"],
                "districts": ["chinatown"]
            },
            "chrome_kings": {
                "rivals": ["street_gangs", "tunnel_rats", "voodoo_boys"],
                "allies": ["corporate"],
                "districts": ["tech_row", "entertainment"]
            },
            "voodoo_boys": {
                "rivals": ["corporate", "chrome_kings", "police"],
                "allies": ["netrunners"],
                "districts": ["virtual_quarter"]
            },
            "maelstrom": {
                "rivals": ["police", "corporate", "jade_fist"],
                "allies": ["street_gangs"],
                "districts": ["industrial", "wasteland"]
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
    
    def to_dict(self) -> Dict:
        """Convert reputation data to dictionary (for saving)"""
        return {
            'district_reputation': self.district_reputation,
            'faction_reputation': self.faction_reputation
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create reputation system from a dictionary"""
        reputation = cls()
        reputation.district_reputation = data.get('district_reputation', {})
        reputation.faction_reputation = data.get('faction_reputation', {})
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
                connected_districts=["entertainment", "upscale", "tech_row"],
                ascii_art="cyberspace",
                map_position={"x": 2, "y": 0},
                location_choices=[
                    {"id": "deep_dive", "text": "Deep dive in illegal VR simulation", "type": "recreation"},
                    {"id": "digital_ghost", "text": "Track down a digital ghost", "type": "tech"},
                    {"id": "zero_day_market", "text": "Browse the zero-day exploit market", "type": "criminal"}
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
                rival_factions=["militech", "chrome_kings", "voodoo_boys"],
                allied_factions=["police"],
                controlled_districts=["corporate", "downtown"],
                faction_type="corp"
            )
        )
        
        self.add_faction(
            Faction(
                faction_id="militech",
                name="Militech International",
                description="A powerful American weapons manufacturer and private military contractor, often at odds with Arasaka.",
                home_district="tech_row",
                rival_factions=["arasaka", "maelstrom"],
                allied_factions=["police", "chrome_kings"],
                controlled_districts=["tech_row", "industrial"],
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
                rival_factions=["street_gangs", "maelstrom", "tunnel_rats", "voodoo_boys"],
                allied_factions=["arasaka", "militech"],
                controlled_districts=["downtown", "upscale", "corporate"],
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
                allied_factions=["tunnel_rats"],
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
                rival_factions=["maelstrom", "police"],
                allied_factions=["fixers"],
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
                rival_factions=["maelstrom", "tunnel_rats", "voodoo_boys"],
                allied_factions=["militech"],
                controlled_districts=["tech_row", "entertainment"],
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
                allied_factions=["netrunners"],
                controlled_districts=["virtual_quarter"],
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
                allied_factions=["jade_fist", "chrome_kings"],
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
                allied_factions=["voodoo_boys", "fixers"],
                controlled_districts=["virtual_quarter", "tech_row"],
                faction_type="netrunner"
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