"""
Skills Module - Advanced character progression system with skills and perks
"""
import json
import time
from typing import Dict, List, Optional, Any, Tuple

class Skill:
    """Represents a specific skill that a character can learn or improve"""
    
    def __init__(self, skill_id: str, name: str, description: str, max_level: int = 5, 
                 prerequisites: List[Dict] = None, effects: Dict = None, category: str = "general"):
        """
        Initialize a skill
        
        Args:
            skill_id: Unique identifier for the skill
            name: Display name for the skill
            description: Description of what the skill does
            max_level: Maximum level this skill can reach (default: 5)
            prerequisites: List of prerequisite skills/stats needed {"type": "skill|stat", "id": "skill_id|stat_name", "level": min_level}
            effects: Dictionary of effects this skill provides at different levels
            category: Category of skill (combat, hacking, social, stealth, etc.)
        """
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.max_level = max_level
        self.prerequisites = prerequisites or []
        self.effects = effects or {}
        self.category = category
        
    def to_dict(self) -> Dict:
        """Convert skill to dictionary for saving"""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "max_level": self.max_level,
            "prerequisites": self.prerequisites,
            "effects": self.effects,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a skill from a dictionary"""
        return cls(
            skill_id=data.get("skill_id", "unknown"),
            name=data.get("name", "Unknown Skill"),
            description=data.get("description", ""),
            max_level=data.get("max_level", 5),
            prerequisites=data.get("prerequisites", []),
            effects=data.get("effects", {}),
            category=data.get("category", "general")
        )
    
    def get_effects_at_level(self, level: int) -> Dict:
        """Get the effects this skill provides at a specific level"""
        # Start with level 1 effects as the base
        combined_effects = self.effects.get("1", {}).copy()
        
        # Add effects from each level up to the current one
        for lvl in range(2, level + 1):
            level_effects = self.effects.get(str(lvl), {})
            for effect_type, effect_value in level_effects.items():
                if effect_type in combined_effects:
                    # If effect already exists, increase it (for numerical effects)
                    if isinstance(effect_value, (int, float)) and isinstance(combined_effects[effect_type], (int, float)):
                        combined_effects[effect_type] += effect_value
                    else:
                        # For non-numerical effects, replace with the higher level one
                        combined_effects[effect_type] = effect_value
                else:
                    # Add new effect
                    combined_effects[effect_type] = effect_value
        
        return combined_effects
    
    def get_level_description(self, level: int) -> str:
        """Get a description of what this skill provides at a specific level"""
        if str(level) in self.effects:
            effect_descr = []
            for effect_type, effect_value in self.effects[str(level)].items():
                if effect_type == "stat_bonus":
                    for stat, bonus in effect_value.items():
                        effect_descr.append(f"+{bonus} to {stat}")
                elif effect_type == "damage_bonus":
                    effect_descr.append(f"+{effect_value} damage")
                elif effect_type == "defense_bonus":
                    effect_descr.append(f"+{effect_value} defense")
                elif effect_type == "critical_chance":
                    effect_descr.append(f"+{effect_value}% critical hit chance")
                elif effect_type == "ability":
                    effect_descr.append(f"New ability: {effect_value}")
                else:
                    effect_descr.append(f"{effect_type}: {effect_value}")
            
            return ", ".join(effect_descr)
        else:
            return "No additional effects at this level"


class Perk:
    """Represents a special ability or trait that provides unique benefits"""
    
    def __init__(self, perk_id: str, name: str, description: str, effects: Dict,
                 prerequisites: List[Dict] = None, category: str = "general",
                 one_time_use: bool = False):
        """
        Initialize a perk
        
        Args:
            perk_id: Unique identifier for the perk
            name: Display name for the perk
            description: Description of what the perk does
            effects: Dictionary of effects this perk provides
            prerequisites: List of prerequisite skills/stats/perks needed
            category: Category of perk (combat, hacking, social, etc.)
            one_time_use: Whether this perk can only be used once
        """
        self.perk_id = perk_id
        self.name = name
        self.description = description
        self.effects = effects
        self.prerequisites = prerequisites or []
        self.category = category
        self.one_time_use = one_time_use
        
    def to_dict(self) -> Dict:
        """Convert perk to dictionary for saving"""
        return {
            "perk_id": self.perk_id,
            "name": self.name,
            "description": self.description,
            "effects": self.effects,
            "prerequisites": self.prerequisites,
            "category": self.category,
            "one_time_use": self.one_time_use
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a perk from a dictionary"""
        return cls(
            perk_id=data.get("perk_id", "unknown"),
            name=data.get("name", "Unknown Perk"),
            description=data.get("description", ""),
            effects=data.get("effects", {}),
            prerequisites=data.get("prerequisites", []),
            category=data.get("category", "general"),
            one_time_use=data.get("one_time_use", False)
        )


class SkillTree:
    """Manages the collection of skills and perks available in the game"""
    
    def __init__(self):
        """Initialize the skill tree"""
        self.skills = {}  # Dictionary of skill_id -> Skill object
        self.perks = {}   # Dictionary of perk_id -> Perk object
        
        # Load default skills and perks
        self._load_default_skills()
        self._load_default_perks()
    
    def _load_default_skills(self):
        """Load the default set of skills if none exist"""
        try:
            with open("data/skills.json", "r") as f:
                skills_data = json.load(f)
                
            for skill_id, skill_data in skills_data.items():
                skill_data["skill_id"] = skill_id
                self.skills[skill_id] = Skill.from_dict(skill_data)
                
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or has errors, create default skills
            self._create_default_skills()
    
    def _create_default_skills(self):
        """Create a set of default skills"""
        # Combat skills
        self.skills["melee_master"] = Skill(
            skill_id="melee_master",
            name="Melee Master",
            description="Improves your ability with melee weapons",
            max_level=5,
            prerequisites=[],
            effects={
                "1": {"damage_bonus": 1},
                "2": {"damage_bonus": 1},
                "3": {"damage_bonus": 2, "critical_chance": 5},
                "4": {"damage_bonus": 2},
                "5": {"damage_bonus": 3, "critical_chance": 10, "ability": "Blade Fury"}
            },
            category="combat"
        )
        
        self.skills["cyber_reflexes"] = Skill(
            skill_id="cyber_reflexes",
            name="Cyber Reflexes",
            description="Enhanced neural reflexes improve your combat mobility",
            max_level=5,
            prerequisites=[],
            effects={
                "1": {"dodge_chance": 5},
                "2": {"stat_bonus": {"reflex": 1}},
                "3": {"dodge_chance": 5, "defense_bonus": 1},
                "4": {"stat_bonus": {"reflex": 1}},
                "5": {"dodge_chance": 10, "ability": "Matrix Dodge"}
            },
            category="combat"
        )
        
        # Hacking skills
        self.skills["network_infiltrator"] = Skill(
            skill_id="network_infiltrator",
            name="Network Infiltrator",
            description="Improves your ability to hack into secure systems",
            max_level=5,
            prerequisites=[],
            effects={
                "1": {"hacking_bonus": 10},
                "2": {"stat_bonus": {"intelligence": 1}},
                "3": {"hacking_bonus": 15, "ability": "Backdoor Access"},
                "4": {"electronics_bonus": 10},
                "5": {"hacking_bonus": 25, "ability": "System Overload"}
            },
            category="hacking"
        )
        
        self.skills["drone_master"] = Skill(
            skill_id="drone_master",
            name="Drone Master",
            description="Improves your ability to control and deploy drones",
            max_level=4,
            prerequisites=[
                {"type": "skill", "id": "network_infiltrator", "level": 2}
            ],
            effects={
                "1": {"drone_damage": 2},
                "2": {"drone_duration": 1},
                "3": {"drone_damage": 3},
                "4": {"drone_count": 1, "ability": "Swarm Protocol"}
            },
            category="hacking"
        )
        
        # Social skills
        self.skills["street_cred"] = Skill(
            skill_id="street_cred",
            name="Street Cred",
            description="Increases your reputation on the streets",
            max_level=5,
            prerequisites=[],
            effects={
                "1": {"reputation_gain": 5},
                "2": {"stat_bonus": {"charisma": 1}},
                "3": {"vendor_discount": 5},
                "4": {"reputation_gain": 10},
                "5": {"stat_bonus": {"charisma": 1}, "ability": "Call In A Favor"}
            },
            category="social"
        )
        
        # Stealth skills
        self.skills["shadow_walker"] = Skill(
            skill_id="shadow_walker",
            name="Shadow Walker",
            description="Improves your ability to move unseen",
            max_level=5,
            prerequisites=[],
            effects={
                "1": {"stealth_bonus": 10},
                "2": {"noise_reduction": 15},
                "3": {"stealth_bonus": 15},
                "4": {"stat_bonus": {"reflex": 1}},
                "5": {"stealth_bonus": 25, "ability": "Ghost Protocol"}
            },
            category="stealth"
        )
        
        # Tech skills
        self.skills["cyber_surgeon"] = Skill(
            skill_id="cyber_surgeon",
            name="Cyber Surgeon",
            description="Improves your ability to heal and repair",
            max_level=4,
            prerequisites=[],
            effects={
                "1": {"healing_bonus": 10},
                "2": {"stat_bonus": {"intelligence": 1}},
                "3": {"self_heal": 2},
                "4": {"ability": "Emergency Protocol"}
            },
            category="tech"
        )
        
        # Save the default skills
        self.save_skills()
    
    def _load_default_perks(self):
        """Load the default set of perks if none exist"""
        try:
            with open("data/perks.json", "r") as f:
                perks_data = json.load(f)
                
            for perk_id, perk_data in perks_data.items():
                perk_data["perk_id"] = perk_id
                self.perks[perk_id] = Perk.from_dict(perk_data)
                
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or has errors, create default perks
            self._create_default_perks()
    
    def _create_default_perks(self):
        """Create a set of default perks"""
        # Combat perks
        self.perks["adrenaline_junkie"] = Perk(
            perk_id="adrenaline_junkie",
            name="Adrenaline Junkie",
            description="Gain increased damage when low on health",
            effects={
                "damage_mult_low_health": 1.5,
                "health_threshold": 30  # % of max health
            },
            prerequisites=[
                {"type": "stat", "id": "strength", "level": 5}
            ],
            category="combat"
        )
        
        self.perks["cyber_berserk"] = Perk(
            perk_id="cyber_berserk",
            name="Cyber Berserk",
            description="Unlock a berserk mode ability that increases damage but disables defense",
            effects={
                "ability": "Cyber Berserk",
                "damage_mult": 2.0,
                "defense_mult": 0.0,
                "duration": 3  # turns
            },
            prerequisites=[
                {"type": "skill", "id": "melee_master", "level": 3}
            ],
            category="combat"
        )
        
        # Hacking perks
        self.perks["ice_breaker"] = Perk(
            perk_id="ice_breaker",
            name="ICE Breaker",
            description="Allows you to bypass security on electronic devices",
            effects={
                "bypass_security_level": 2,
                "hacking_time_reduction": 0.5  # 50% time reduction
            },
            prerequisites=[
                {"type": "skill", "id": "network_infiltrator", "level": 3}
            ],
            category="hacking"
        )
        
        # Social perks
        self.perks["silver_tongue"] = Perk(
            perk_id="silver_tongue",
            name="Silver Tongue",
            description="Your smooth talking gets you better deals and information",
            effects={
                "vendor_bonus": 15,  # % discount
                "dialogue_options": "silver_tongue"  # Special dialogue options
            },
            prerequisites=[
                {"type": "stat", "id": "charisma", "level": 6}
            ],
            category="social"
        )
        
        # Stealth perks
        self.perks["ghost"] = Perk(
            perk_id="ghost",
            name="Ghost",
            description="You leave no trace and make no sound",
            effects={
                "detection_chance_reduction": 0.7,  # 70% reduction
                "noise_level": 0.3  # 30% of normal
            },
            prerequisites=[
                {"type": "skill", "id": "shadow_walker", "level": 4}
            ],
            category="stealth"
        )
        
        # Tech perks
        self.perks["field_medic"] = Perk(
            perk_id="field_medic",
            name="Field Medic",
            description="Allows you to heal in combat without using an item",
            effects={
                "ability": "Field Medic",
                "healing": 15,
                "cooldown": 4  # turns
            },
            prerequisites=[
                {"type": "skill", "id": "cyber_surgeon", "level": 3}
            ],
            category="tech"
        )
        
        # Save the default perks
        self.save_perks()
    
    def save_skills(self):
        """Save skills to a JSON file"""
        skills_data = {}
        for skill_id, skill in self.skills.items():
            skills_data[skill_id] = skill.to_dict()
            
        try:
            with open("data/skills.json", "w") as f:
                json.dump(skills_data, f, indent=4)
        except Exception as e:
            print(f"Error saving skills: {e}")
    
    def save_perks(self):
        """Save perks to a JSON file"""
        perks_data = {}
        for perk_id, perk in self.perks.items():
            perks_data[perk_id] = perk.to_dict()
            
        try:
            with open("data/perks.json", "w") as f:
                json.dump(perks_data, f, indent=4)
        except Exception as e:
            print(f"Error saving perks: {e}")
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID"""
        return self.skills.get(skill_id)
    
    def get_perk(self, perk_id: str) -> Optional[Perk]:
        """Get a perk by ID"""
        return self.perks.get(perk_id)
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a specific category"""
        return [skill for skill in self.skills.values() if skill.category == category]
    
    def get_perks_by_category(self, category: str) -> List[Perk]:
        """Get all perks in a specific category"""
        return [perk for perk in self.perks.values() if perk.category == category]
    
    def check_prerequisites(self, prerequisites: List[Dict], character) -> Tuple[bool, str]:
        """
        Check if a character meets the prerequisites for a skill or perk
        
        Args:
            prerequisites: List of prerequisite dictionaries
            character: Character object to check against
            
        Returns:
            (bool, str): Whether the character meets the prerequisites and a message if not
        """
        if not prerequisites:
            return True, ""
            
        for prereq in prerequisites:
            prereq_type = prereq.get("type")
            prereq_id = prereq.get("id")
            prereq_level = prereq.get("level", 1)
            
            if prereq_type == "stat":
                stat_value = character.stats.get(prereq_id, 0)
                if stat_value < prereq_level:
                    return False, f"Requires {prereq_id.capitalize()} of {prereq_level}, you have {stat_value}"
                    
            elif prereq_type == "skill":
                # Access skills through the progression object instead of directly
                char_skill_level = 0
                if hasattr(character, 'progression') and hasattr(character.progression, 'skills'):
                    char_skill_level = character.progression.skills.get(prereq_id, {}).get("level", 0)
                if char_skill_level < prereq_level:
                    skill_name = self.get_skill(prereq_id).name if self.get_skill(prereq_id) else prereq_id
                    return False, f"Requires {skill_name} level {prereq_level}, you have level {char_skill_level}"
                    
            elif prereq_type == "perk":
                # Access perks through the progression object instead of directly
                has_perk = False
                if hasattr(character, 'progression') and hasattr(character.progression, 'perks'):
                    has_perk = prereq_id in character.progression.perks
                if not has_perk:
                    perk_name = self.get_perk(prereq_id).name if self.get_perk(prereq_id) else prereq_id
                    return False, f"Requires {perk_name} perk"
                    
            elif prereq_type == "level":
                if character.level < prereq_level:
                    return False, f"Requires character level {prereq_level}, you are level {character.level}"
        
        return True, ""


class CharacterProgression:
    """Manages a character's skills, perks, and progression"""
    
    def __init__(self, character=None, skill_tree=None):
        """
        Initialize character progression
        
        Args:
            character: Character object to attach to
            skill_tree: SkillTree object with available skills and perks
        """
        self.character = character
        self.skill_tree = skill_tree or SkillTree()
        
        # Character's current skills and levels
        self.skills = {}  # Dictionary of skill_id -> {"level": int, "xp": int}
        
        # Character's acquired perks
        self.perks = []  # List of perk_ids
        
        # Skill points and perk points available to spend
        self.skill_points = 0
        self.perk_points = 0
    
    def to_dict(self) -> Dict:
        """Convert progression data to dictionary for saving"""
        return {
            "skills": self.skills,
            "perks": self.perks,
            "skill_points": self.skill_points,
            "perk_points": self.perk_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict, character=None, skill_tree=None):
        """Create progression from a dictionary"""
        progression = cls(character, skill_tree)
        
        progression.skills = data.get("skills", {})
        progression.perks = data.get("perks", [])
        progression.skill_points = data.get("skill_points", 0)
        progression.perk_points = data.get("perk_points", 0)
        
        return progression
    
    def add_skill_points(self, points: int):
        """Add skill points for the character to spend"""
        self.skill_points += points
    
    def add_perk_points(self, points: int):
        """Add perk points for the character to spend"""
        self.perk_points += points
    
    def can_learn_skill(self, skill_id: str) -> Tuple[bool, str]:
        """Check if the character can learn or improve a skill"""
        # Check if skill exists
        skill = self.skill_tree.get_skill(skill_id)
        if not skill:
            return False, "Skill does not exist"
        
        # Check if character has skill points
        if self.skill_points <= 0:
            return False, "Not enough skill points"
        
        # Get current level of the skill
        current_level = self.skills.get(skill_id, {}).get("level", 0)
        
        # Check if skill is at max level
        if current_level >= skill.max_level:
            return False, f"Skill is already at maximum level ({skill.max_level})"
        
        # Check prerequisites
        meets_prereqs, prereq_message = self.skill_tree.check_prerequisites(
            skill.prerequisites, self.character
        )
        if not meets_prereqs:
            return False, prereq_message
        
        return True, ""
    
    def learn_skill(self, skill_id: str) -> Tuple[bool, str]:
        """
        Learn a new skill or improve an existing one
        
        Returns:
            (bool, str): Success status and message
        """
        can_learn, message = self.can_learn_skill(skill_id)
        if not can_learn:
            return False, message
        
        # Initialize skill if not present
        if skill_id not in self.skills:
            self.skills[skill_id] = {"level": 0, "xp": 0}
        
        # Increment skill level
        self.skills[skill_id]["level"] += 1
        
        # Deduct skill point
        self.skill_points -= 1
        
        # Get the skill object
        skill = self.skill_tree.get_skill(skill_id)
        
        # Apply skill effects
        level = self.skills[skill_id]["level"]
        effects = skill.get_effects_at_level(level)
        self._apply_skill_effects(effects)
        
        return True, f"Successfully learned {skill.name} (Level {level})"
    
    def can_learn_perk(self, perk_id: str) -> Tuple[bool, str]:
        """Check if the character can learn a perk"""
        # Check if perk exists
        perk = self.skill_tree.get_perk(perk_id)
        if not perk:
            return False, "Perk does not exist"
        
        # Check if character has perk points
        if self.perk_points <= 0:
            return False, "Not enough perk points"
        
        # Check if character already has the perk
        if perk_id in self.perks:
            return False, "You already have this perk"
        
        # Check prerequisites
        meets_prereqs, prereq_message = self.skill_tree.check_prerequisites(
            perk.prerequisites, self.character
        )
        if not meets_prereqs:
            return False, prereq_message
        
        return True, ""
    
    def learn_perk(self, perk_id: str) -> Tuple[bool, str]:
        """
        Learn a new perk
        
        Returns:
            (bool, str): Success status and message
        """
        can_learn, message = self.can_learn_perk(perk_id)
        if not can_learn:
            return False, message
        
        # Add perk to character
        self.perks.append(perk_id)
        
        # Deduct perk point
        self.perk_points -= 1
        
        # Get the perk object
        perk = self.skill_tree.get_perk(perk_id)
        
        # Apply perk effects
        self._apply_perk_effects(perk.effects)
        
        return True, f"Successfully learned {perk.name} perk"
    
    def _apply_skill_effects(self, effects: Dict):
        """Apply skill effects to the character"""
        if not self.character:
            return
            
        # Apply stat bonuses
        if "stat_bonus" in effects:
            for stat, bonus in effects["stat_bonus"].items():
                if stat in self.character.stats:
                    self.character.stats[stat] += bonus
        
        # If the skill provides a new ability, it will be handled by the combat system
        # based on the character's skills when abilities are loaded
    
    def _apply_perk_effects(self, effects: Dict):
        """Apply perk effects to the character"""
        if not self.character:
            return
            
        # Most perk effects will be applied dynamically during gameplay
        # based on the character's perks when relevant systems check them
    
    def get_skill_level(self, skill_id: str) -> int:
        """Get the character's level in a specific skill"""
        return self.skills.get(skill_id, {}).get("level", 0)
    
    def has_perk(self, perk_id: str) -> bool:
        """Check if the character has a specific perk"""
        return perk_id in self.perks
    
    def get_available_skills(self) -> List[Tuple[Skill, bool, str]]:
        """
        Get all skills available to the character with availability status
        
        Returns:
            List of (Skill, can_learn, message) tuples
        """
        results = []
        
        for skill_id, skill in self.skill_tree.skills.items():
            can_learn, message = self.can_learn_skill(skill_id)
            results.append((skill, can_learn, message))
        
        return results
    
    def get_available_perks(self) -> List[Tuple[Perk, bool, str]]:
        """
        Get all perks available to the character with availability status
        
        Returns:
            List of (Perk, can_learn, message) tuples
        """
        results = []
        
        for perk_id, perk in self.skill_tree.perks.items():
            can_learn, message = self.can_learn_perk(perk_id)
            results.append((perk, can_learn, message))
        
        return results
    
    def award_experience(self, xp_amount: int) -> Dict:
        """
        Award experience points for progression and determine if level up occurs
        
        Returns:
            Dict with level up information
        """
        # First, pass to character's base XP system
        level_up_info = None
        if self.character:
            level_up_info = self.character.add_experience(xp_amount)
        
        # Check for progression rewards based on levels
        results = {
            "skill_points_gained": 0,
            "perk_points_gained": 0,
            "level_up": level_up_info is not None
        }
        
        if level_up_info:
            # Award skill points (typically 2 per level)
            skill_points = 2
            self.skill_points += skill_points
            results["skill_points_gained"] = skill_points
            
            # Award perk points every few levels
            new_level = level_up_info.get("new_level", 0)
            if new_level % 3 == 0:  # Perk point every 3 levels
                self.perk_points += 1
                results["perk_points_gained"] = 1
        
        return results
    
    def calculate_all_effects(self) -> Dict:
        """
        Calculate all effects from skills and perks
        
        Returns:
            Dictionary of effects
        """
        effects = {
            "damage_bonus": 0,
            "defense_bonus": 0,
            "critical_chance": 0,
            "dodge_chance": 0,
            "stealth_bonus": 0,
            "hacking_bonus": 0,
            "healing_bonus": 0,
            "stat_bonuses": {
                "strength": 0,
                "intelligence": 0,
                "charisma": 0,
                "reflex": 0
            },
            "abilities": []
        }
        
        # Calculate skill effects
        for skill_id, skill_data in self.skills.items():
            skill = self.skill_tree.get_skill(skill_id)
            if not skill:
                continue
                
            level = skill_data.get("level", 0)
            if level <= 0:
                continue
                
            # Get effects for this skill at current level
            skill_effects = skill.get_effects_at_level(level)
            
            # Apply numerical effects
            for effect_type, effect_value in skill_effects.items():
                if effect_type == "damage_bonus":
                    effects["damage_bonus"] += effect_value
                elif effect_type == "defense_bonus":
                    effects["defense_bonus"] += effect_value
                elif effect_type == "critical_chance":
                    effects["critical_chance"] += effect_value
                elif effect_type == "dodge_chance":
                    effects["dodge_chance"] += effect_value
                elif effect_type == "stealth_bonus":
                    effects["stealth_bonus"] += effect_value
                elif effect_type == "hacking_bonus":
                    effects["hacking_bonus"] += effect_value
                elif effect_type == "healing_bonus":
                    effects["healing_bonus"] += effect_value
                elif effect_type == "stat_bonus":
                    for stat, bonus in effect_value.items():
                        effects["stat_bonuses"][stat] += bonus
                elif effect_type == "ability":
                    effects["abilities"].append(effect_value)
        
        # Calculate perk effects (conditionally applied in gameplay)
        for perk_id in self.perks:
            perk = self.skill_tree.get_perk(perk_id)
            if not perk:
                continue
                
            # For perks, we mostly track which ones the character has
            # The actual effects are applied conditionally during gameplay
            if "ability" in perk.effects:
                effects["abilities"].append(perk.effects["ability"])
        
        return effects