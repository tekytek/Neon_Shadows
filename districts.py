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
                 ascii_art: str = None):
        """Initialize a district"""
        self.district_id = district_id  # Unique identifier
        self.name = name
        self.description = description
        self.danger_level = danger_level  # 1-5 scale
        self.available_shops = available_shops or []
        self.available_quests = available_quests or []
        self.connected_districts = connected_districts or []  # Districts you can travel to from here
        self.ascii_art = ascii_art  # ASCII art representation of the district
    
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
            'ascii_art': self.ascii_art
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
            ascii_art=data.get('ascii_art')
        )

class ReputationSystem:
    """Manages player reputation across different districts and factions"""
    
    def __init__(self):
        """Initialize reputation system"""
        # District reputations (neutral = 0, -100 to +100 scale)
        self.district_reputation: Dict[str, int] = {}
        
        # Faction reputations (neutral = 0, -100 to +100 scale)
        self.faction_reputation: Dict[str, int] = {}
    
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
    
    def modify_faction_reputation(self, faction_id: str, amount: int) -> int:
        """
        Modify reputation with a faction
        
        Args:
            faction_id: The faction ID
            amount: Amount to change (positive or negative)
            
        Returns:
            New reputation value
        """
        if faction_id not in self.faction_reputation:
            self.faction_reputation[faction_id] = 0
        
        self.faction_reputation[faction_id] += amount
        
        # Clamp value between -100 and 100
        self.faction_reputation[faction_id] = max(-100, min(100, self.faction_reputation[faction_id]))
        
        return self.faction_reputation[faction_id]
    
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
    
    def get_price_modifier(self, district_id: str) -> float:
        """Get price modifier for goods in a district based on reputation"""
        rep = self.get_district_reputation(district_id)
        
        # Scale from 1.5x (despised) to 0.8x (revered)
        return 1.0 - (rep / 500)  # 100 rep = 20% discount, -100 rep = 20% markup
    
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
    """Manages all districts in the city"""
    
    def __init__(self):
        """Initialize the district manager"""
        self.districts: Dict[str, District] = {}
        self.current_district: Optional[str] = None
        self.load_districts()
    
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
    
    def create_default_districts(self) -> None:
        """Create default districts if none are loaded"""
        # Create the default districts
        self.add_district(
            District(
                district_id="downtown",
                name="Downtown",
                description="The heart of the city, towering skyscrapers and corporate headquarters. High security, but opportunities for those who know where to look.",
                danger_level=3,  # Moderate danger
                connected_districts=["industrial", "residential"],
                ascii_art="downtown"
            )
        )
        
        self.add_district(
            District(
                district_id="industrial",
                name="Industrial Zone",
                description="Factories and warehouses dominate this polluted district. Home to smugglers and underground operations.",
                danger_level=4,  # High danger
                connected_districts=["downtown", "outskirts"],
                ascii_art="industrial"
            )
        )
        
        self.add_district(
            District(
                district_id="residential",
                name="Residential Sector",
                description="Dense apartment blocks where most of the city's population lives. Varying levels of safety depending on the block.",
                danger_level=2,  # Lower danger
                connected_districts=["downtown", "outskirts"],
                ascii_art="residential"
            )
        )
        
        self.add_district(
            District(
                district_id="outskirts",
                name="City Outskirts",
                description="The fringe of the city, lawless and dangerous. Only the desperate or the powerful venture here willingly.",
                danger_level=5,  # Extremely dangerous
                connected_districts=["industrial", "residential"],
                ascii_art="outskirts"
            )
        )
        
        self.add_district(
            District(
                district_id="corporate",
                name="Corporate Sector",
                description="The pristine and heavily guarded zone where the elite live and work. Access is strictly controlled.",
                danger_level=1,  # Safest area
                connected_districts=["downtown"],
                ascii_art="corporate"
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