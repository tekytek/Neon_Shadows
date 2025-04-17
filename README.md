# Neon Shadows: Cyberpunk Text Adventure

A text-based cyberpunk adventure game built in Python with rich narrative, choice-based gameplay, and Ollama-powered storylines.

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Game Features](#game-features)
4. [Code Structure](#code-structure)
5. [Technical Details](#technical-details)
6. [Ollama Integration](#ollama-integration)
7. [Future Enhancements](#future-enhancements)

## Overview

Neon Shadows is an immersive text-based adventure game set in a dystopian cyberpunk future. Players navigate through a branching narrative, make consequential choices, manage inventory, and engage in combat encounters while exploring the neon-lit streets of Neo-Shanghai in the year 2077.

The game features:
- Rich narrative with multiple story branches
- Character creation with different classes and stats
- Inventory management system
- Text-based combat mechanics
- Dynamic content generation using Ollama (optional)
- Save/load game functionality

## Installation

```
# Clone the repository
git clone https://github.com/yourusername/neon-shadows.git
cd neon-shadows

# Install required packages
pip install -r requirements.txt

# Run the game
python main.py
```

Required packages:
- rich (for enhanced terminal display)
- requests (for API communication)

## Game Features

### Character Creation
Players can create characters with different classes:
- NetRunner (hacking specialist)
- Enforcer (combat specialist)
- Fixer (social specialist)
- Tech (technical specialist)

Each class has different starting stats and equipment.

### Stats System
Characters have four primary stats:
- Strength: Affects combat damage and health
- Intelligence: Affects hacking ability and tech interactions
- Charisma: Affects social interactions and prices
- Reflex: Affects combat evasion and initiative

### Inventory System
Players can collect, use, and manage various items:
- Consumables (stimpacks, boosters)
- Weapons
- Armor
- Mission items
- Equipment

### Combat System
Turn-based combat with options to:
- Attack enemies
- Use items
- Attempt to escape

### Story & Choices
The game features a branching narrative with choices that:
- Can be locked behind stat requirements
- May require specific items
- Have consequences (gain/lose items, health, credits)
- Lead to different story paths

### Save/Load System
Players can save their progress and load saved games.

## Code Structure

The codebase is organized into modular components:

### Main Files

#### `main.py`
The entry point for the game. Initializes the console and manages the main menu loop.
```python
def main():
    """Main entry point for the game"""
    # Initialize the console
    console = Console()
    
    # Display intro and splash screen
    ui.clear_screen()
    ui.display_splash_screen(console)
    
    # Main menu loop
    while True:
        choice = ui.main_menu(console)
        
        if choice == "new_game":
            game = game_engine.GameEngine()
            game.new_game(console)
            game.game_loop(console)
        elif choice == "load_game":
            game = game_engine.GameEngine()
            if game.load_game(console):
                game.game_loop(console)
        elif choice == "options":
            ui.options_menu(console)
        elif choice == "credits":
            ui.display_credits(console)
        elif choice == "quit":
            ui.display_exit_message(console)
            sys.exit(0)
```

#### `game_engine.py`
The core game loop and game state manager. Orchestrates all game components.
```python
class GameEngine:
    """Main game engine that orchestrates all game components"""
    
    def __init__(self):
        """Initialize the game engine"""
        self.player = None
        self.current_node = None
        self.story_manager = story.StoryManager()
        self.game_over = False
        self.ollama = ollama_integration.OllamaIntegration()
```

#### `character.py`
Manages player character stats, inventory, and abilities.
```python
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
```

#### `story.py`
Manages story nodes and progression through the narrative.
```python
class StoryManager:
    """Manages story nodes and progression"""
    
    def __init__(self):
        """Initialize the story manager"""
        self.nodes = {}
        self.load_story_nodes()
    
    def load_story_nodes(self):
        """Load story nodes from JSON file"""
        story_file = os.path.join(DATA_DIR, 'story_nodes.json')
        
        try:
            if os.path.exists(story_file):
                with open(story_file, 'r') as f:
                    self.nodes = json.load(f)
            else:
                # Create default story if file doesn't exist
                self.create_default_story()
                
                # Save the default story
                with open(story_file, 'w') as f:
                    json.dump(self.nodes, f, indent=2)
        except Exception as e:
            print(f"Error loading story nodes: {str(e)}")
            # Create default story on error
            self.create_default_story()
```

### Game Systems

#### `inventory.py`
Handles player inventory and item management.
```python
class Inventory:
    """Inventory management for the player"""
    
    def __init__(self):
        """Initialize a new inventory"""
        self.items = {}  # Format: {item_name: quantity}
        self._load_items_data()
```

#### `combat.py`
Manages combat encounters and mechanics.
```python
class Enemy:
    """Enemy class for combat encounters"""
    
    def __init__(self, name, health, damage, defense):
        """Initialize an enemy"""
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.defense = defense
        self.weaknesses = []
        self.resistances = []

def run_combat(console, player, enemy):
    """Run a complete combat encounter"""
    # Initialize combat
    turn = 1
    combat_active = True
    result = None
    
    while combat_active:
        # Clear screen and show status
        console.clear()
        console.print(Panel(f"[{COLORS['accent']}]COMBAT: {player.name} vs {enemy.name}[/{COLORS['accent']}]"))
        
        # Display health status
        display_combat_status(console, player, enemy)
        
        # Player's turn
        console.print(f"[{COLORS['primary']}]TURN {turn}[/{COLORS['primary']}]")
        console.print(f"[{COLORS['secondary']}]Your move:[/{COLORS['secondary']}]")
        
        # Display combat options
        console.print(f"[{COLORS['text']}]1. Attack[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]2. Use Item[/{COLORS['text']}]")
        console.print(f"[{COLORS['text']}]3. Attempt to Escape[/{COLORS['text']}]")
```

#### `save_system.py`
Handles saving and loading game progress.
```python
def save_game(save_name, save_data):
    """Save the game to a file"""
    ensure_save_directory()
    
    # Sanitize the save name
    save_name = save_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    save_path = os.path.join(SAVE_DIR, f"{save_name}.json")
    
    try:
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game: {str(e)}")
        return False

def load_game(save_file):
    """Load a game from a save file"""
    try:
        with open(save_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading game: {str(e)}")
        raise
```

### UI and Display

#### `ui.py`
Handles user interface and display elements.
```python
def display_splash_screen(console):
    """Display the game's splash screen"""
    clear_screen()
    
    # Display ASCII art title
    console.print(assets.get_ascii_art('title'), style=Style(color=COLORS['primary']))
    
    # Display version and credits
    console.print(f"[{COLORS['secondary']}]Version {VERSION}[/{COLORS['secondary']}]")
    console.print(f"[{COLORS['text']}]A text-based cyberpunk adventure[/{COLORS['text']}]")
    
    # Bottom line
    console.print("\n" + "=" * 60, style=Style(color=COLORS['primary']))
    console.print(f"[{COLORS['text']}]Press Enter to continue...[/{COLORS['text']}]")
    input()
```

#### `assets.py`
Manages ASCII art and other visual assets.
```python
def get_ascii_art(art_name):
    """Get ASCII art by name"""
    return ASCII_ART.get(art_name, "")
```

### AI Integration

#### `ollama_integration.py`
Handles dynamic content generation with Ollama LLM.
```python
class OllamaIntegration:
    """Integration with Ollama for dynamic story generation"""
    
    def __init__(self):
        """Initialize Ollama integration"""
        self.api_url = OLLAMA_API_URL
        self.model = OLLAMA_MODEL
        self.console = Console()
    
    def generate_story_node(self, node_id, player):
        """Generate a dynamic story node based on the current game state"""
        # Check if we should use Ollama
        from config import USE_OLLAMA
        
        if not USE_OLLAMA:
            # Skip Ollama integration if disabled
            return self._generate_fallback_node(node_id)
            
        # Check if Ollama is available
        if not self._check_availability():
            self.console.print("[bold red]Ollama is not available. Using fallback content.[/bold red]")
            return self._generate_fallback_node(node_id)
        
        # Create a prompt with the current game state
        prompt = self._create_story_prompt(node_id, player)
        
        # Make the request to Ollama
        response = self._make_request(prompt)
        
        if not response:
            self.console.print("[bold red]Failed to generate story content. Using fallback.[/bold red]")
            return self._generate_fallback_node(node_id)
```

### Configuration and Data

#### `config.py`
Global settings and constants.
```python
# Game information
GAME_TITLE = "NEON SHADOWS"
VERSION = "1.0.0"

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_DIR = os.path.join(BASE_DIR, "saves")

# Colors
COLORS = {
    "primary": "#FF00FF",  # neon pink
    "secondary": "#00FFFF",  # cyan
    "background": "#0A0A0A",  # near black
    "text": "#00FF00",  # matrix green
    "accent": "#FF0000"  # red
}

# Game mechanics
LEVEL_UP_BASE_XP = 100  # Base XP needed for level up
MAX_INVENTORY_ITEMS = 20  # Maximum number of unique items in inventory

# Ollama integration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
USE_OLLAMA = False  # Set to True to use Ollama, False to use fallback content
```

#### Data Files
- `story_nodes.json`: Contains story nodes, text, and choices
- `items.json`: Defines all game items and their properties
- `enemies.json`: Defines enemy types and attributes
- `ascii_art.py`: Contains ASCII art for visual display

## Technical Details

### Story Node Structure
Story nodes are structured as JSON objects:

```json
{
  "intro": {
    "title": "The Awakening",
    "ascii_art": "intro",
    "text": "Your consciousness flickers to life in a dimly-lit room...",
    "choices": [
      {
        "text": "Try to remember how you got here",
        "next_node": "intro_memory"
      },
      {
        "text": "Check your surroundings",
        "next_node": "intro_surroundings"
      }
    ]
  }
}
```

Different node types include:
- Narrative nodes (standard text and choices)
- Combat nodes (enemy encounters)
- Shop nodes (buying/selling items)
- Skill check nodes (stat-based challenges)

### Item System
Items have various properties:
```json
"Stimpack": {
  "description": "Emergency medical stimulant. Restores 5 health immediately.",
  "type": "consumable",
  "usable": true,
  "usable_in_combat": true,
  "effects": {
    "health": 5
  }
}
```

### Character Stats and Progression
Characters gain experience and level up, increasing their stats and abilities. Status effects can temporarily or permanently modify character stats.

## Ollama Integration

The game integrates with Ollama, a local large language model, to dynamically generate story content based on the player's character, choices, and game state.

### How it Works
1. The game checks if Ollama integration is enabled and available
2. If available, it sends a carefully crafted prompt that includes:
   - Current game state
   - Player character information
   - Context about the current story node
3. Ollama generates a structured response in JSON format that includes:
   - Story text
   - Choices for the player
   - Consequences of choices
   - Enemy information (for combat)
4. The game processes this response and presents it to the player

### Fallback Mechanism
If Ollama is unavailable or disabled, the game falls back to predefined story content from the JSON files.

## Developer Mode

The game includes a hidden developer mode that allows for quick testing and game state manipulation. This is useful for testing different parts of the game without having to play through the entire game.

### Accessing Developer Mode

To access the developer mode:
1. Start the game and wait for the main menu to appear
2. Type `dev` at the menu prompt (instead of selecting a menu option by number)
3. This will open the Developer Tools menu

### Developer Tools Features

The Developer Tools menu provides the following options:

1. **Quick Character Creator**
   - Create test characters quickly with predefined templates
   - Options include:
     - NetRunner (High Intelligence)
     - Solo (High Strength)
     - Fixer (High Charisma)
     - Custom Character (set your own stats)

2. **Test Map Navigation**
   - Jump directly to the map screen to test district travel
   - Explore different districts without progressing through the story

3. **Test Combat**
   - Start combat encounters with enemies of varying difficulty
   - Test combat mechanics, item usage, and rewards

4. **Test Inventory**
   - Access the inventory management screen
   - Test item usage and management

5. **Add Credits**
   - Add currency to your character for testing shop interactions

6. **Add Items**
   - Add specific items to your inventory
   - Choose from a predefined list of common items

7. **Level Up**
   - Add experience points to level up your character
   - Test stat point allocation and level-up mechanics

8. **Set Reputation**
   - Modify your character's reputation in different districts
   - Test how reputation affects interactions and prices

### Developer Mode Usage Notes

- Developer mode is intended for testing only and may affect game balance
- Saves created while using developer mode are compatible with normal gameplay
- Changes made in developer mode are persistent
- To exit developer mode, select "Return to Main Menu"

## Future Enhancements

Potential future enhancements to the game:
1. Expanded story content and branching narratives
2. More character classes and customization options
3. Enhanced combat system with special abilities
4. Reputation system with different factions
5. More sophisticated dynamic content generation
6. Options menu with gameplay customization
7. Visual enhancements and sound effects
8. Expanded developer tools with more testing options

## License

This project is open source and available under the MIT License.