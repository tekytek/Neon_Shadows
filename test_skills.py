"""
Simple test script for the skills module
"""
from rich.console import Console
from skills import Skill, Perk, SkillTree, CharacterProgression

console = Console()

def test_skill_tree():
    """Test basic skill tree functionality"""
    console.print("[bold cyan]Testing Skill Tree...[/bold cyan]")
    
    # Create a skill tree
    skill_tree = SkillTree()
    
    # Check that default skills were created
    console.print(f"Loaded {len(skill_tree.skills)} skills")
    for skill_id, skill in list(skill_tree.skills.items())[:3]:  # Show first 3
        console.print(f"  - {skill.name} ({skill_id}): {skill.description}")
    
    # Check that default perks were created
    console.print(f"Loaded {len(skill_tree.perks)} perks")
    for perk_id, perk in list(skill_tree.perks.items())[:3]:  # Show first 3
        console.print(f"  - {perk.name} ({perk_id}): {perk.description}")

def test_character_progression():
    """Test character progression"""
    console.print("\n[bold cyan]Testing Character Progression...[/bold cyan]")
    
    # Mock character class
    class MockCharacter:
        def __init__(self):
            self.name = "Test Runner"
            self.char_class = "NetRunner"
            self.level = 5
            self.stats = {"strength": 5, "intelligence": 8, "reflex": 6, "charisma": 4}
            self.experience = 1000
            self.health = 100
            self.max_health = 100
            self.inventory = []
            self.credits = 1000
            
        def add_experience(self, amount):
            self.experience += amount
            return {"previous_level": 5, "new_level": 6}
    
    # Create character and progression
    character = MockCharacter()
    skill_tree = SkillTree()
    progression = CharacterProgression(character, skill_tree)
    
    # Add some skill points and check
    progression.add_skill_points(5)
    console.print(f"Added 5 skill points, now has {progression.skill_points}")
    
    # Learn a skill
    skill_id = "network_infiltrator"  # A hacking skill
    result, message = progression.learn_skill(skill_id)
    console.print(f"Learned {skill_id}: {result}, {message}")
    
    # Show skill level
    console.print(f"Skill level now: {progression.get_skill_level(skill_id)}")
    
    # Add perk points and learn a perk
    progression.add_perk_points(2)
    console.print(f"Added 2 perk points, now has {progression.perk_points}")
    
    # Get available perks
    available_perks = progression.get_available_perks()
    available_perk_ids = [p[0].perk_id for p in available_perks if p[1]]
    
    if available_perk_ids:
        # Learn the first available perk
        perk_id = available_perk_ids[0]
        result, message = progression.learn_perk(perk_id)
        console.print(f"Learned {perk_id}: {result}, {message}")
    else:
        console.print("No perks available to learn")
    
    # Test specialization
    result, message = progression.set_specialization("NetRunner")
    console.print(f"Set specialization to NetRunner: {result}, {message}")
    
    # Test skill experience gain
    result = progression.gain_skill_experience(skill_id, 200)
    console.print(f"Skill experience result: {result}")
    
    # Test synergy checking
    progression.skills = {
        "network_infiltrator": {"level": 3, "xp": 0},
        "shadow_walker": {"level": 3, "xp": 0}
    }
    progression._check_skill_synergies()
    console.print(f"Active synergies: {progression.active_synergies}")

if __name__ == "__main__":
    console.print("[bold magenta]===== SKILLS MODULE TESTS =====[/bold magenta]")
    test_skill_tree()
    test_character_progression()
    console.print("\n[bold green]All tests completed![/bold green]")