"""
Game Engine - Core logic for the cyberpunk adventure game
"""
import os
import time
import json
import random
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

import character
import story
import ui
import combat
import inventory
import save_system
import ollama_integration
import districts
import location_actions
from districts import DistrictManager, District
from location_actions import LocationActionHandler
from config import GAME_TITLE, SAVE_DIR

class GameEngine:
    """Main game engine that orchestrates all game components"""
    
    def __init__(self):
        """Initialize the game engine"""
        self.player = None
        self.current_node = None
        self.story_manager = story.StoryManager()
        self.game_over = False
        self.ollama = ollama_integration.OllamaIntegration()
        
        # Initialize choice history tracker
        import choice_history
        self.choice_history = choice_history.ChoiceHistory()
        
        # Initialize district manager
        self.district_manager = DistrictManager()
        
        # Initialize location action handler
        self.location_handler = LocationActionHandler(self)
        
        # Initialize codex system
        import codex
        self.codex = codex.Codex()
        
        # Initialize audio system if available
        try:
            import audio
            audio.initialize()
            self.audio_system = audio
            self.audio_enabled = True
        except ImportError:
            self.audio_system = None
            self.audio_enabled = False
        
        # Ensure save directory exists
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
    
    def new_game(self, console):
        """Start a new game with character creation"""
        from config import GAME_SETTINGS, DIFFICULTY_SETTINGS
        
        ui.clear_screen()
        ui.display_header(console, "CHARACTER CREATION")
        
        console.print(Panel("[cyan]In the neon-washed streets of Neo-Shanghai, your story begins...[/cyan]"))
        console.print("[green]Create your character:[/green]")
        
        try:
            name = Prompt.ask("[bold cyan]Enter your character's name[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            # Fallback to a default name if we can't get input
            console.print("[yellow]Input error detected. Using default name 'Runner'.[/yellow]")
            name = "Runner"
            # Add a short delay to show the message
            time.sleep(1.5)
        
        # Display character class options
        console.print("\n[bold green]Choose your character class:[/bold green]")
        
        classes = [
            {"name": "NetRunner", "description": "Elite hackers who navigate the digital realm", 
             "stats": {"strength": 3, "intelligence": 8, "charisma": 4, "reflex": 5}},
            {"name": "Enforcer", "description": "Muscle for hire with augmented combat abilities", 
             "stats": {"strength": 8, "intelligence": 3, "charisma": 3, "reflex": 6}},
            {"name": "Fixer", "description": "Connected operators who know everyone worth knowing", 
             "stats": {"strength": 4, "intelligence": 5, "charisma": 8, "reflex": 3}},
            {"name": "Tech", "description": "Augmentation specialists and gadget gurus", 
             "stats": {"strength": 3, "intelligence": 7, "charisma": 4, "reflex": 6}}
        ]
        
        for i, char_class in enumerate(classes, 1):
            console.print(f"[cyan]{i}. {char_class['name']}[/cyan]: {char_class['description']}")
            stats = char_class['stats']
            console.print(f"   STR: {stats['strength']} | INT: {stats['intelligence']} | CHA: {stats['charisma']} | REF: {stats['reflex']}")
        
        try:
            class_choice = IntPrompt.ask("[bold cyan]Select your class[/bold cyan]", choices=[str(i) for i in range(1, len(classes)+1)])
            selected_class = classes[class_choice-1]
        except (EOFError, KeyboardInterrupt, ValueError, IndexError):
            # Fall back to a default class if we can't get input
            console.print("[yellow]Input error detected. Using default class 'NetRunner'.[/yellow]")
            selected_class = classes[0]  # NetRunner is the first class
            time.sleep(1.5)
        
        # Create the player character
        self.player = character.Character(
            name=name,
            char_class=selected_class['name'],
            stats=selected_class['stats']
        )
        
        # Apply difficulty settings to starting stats if needed
        difficulty = GAME_SETTINGS.get("difficulty", "normal")
        difficulty_mods = DIFFICULTY_SETTINGS.get(difficulty, {})
        
        # Apply health bonus from difficulty
        health_bonus = difficulty_mods.get("starting_health_bonus", 0)
        if health_bonus != 0:
            self.player.max_health += health_bonus
            self.player.health = self.player.max_health
            
            # Show message about difficulty adjustment
            if health_bonus > 0:
                console.print(f"[green]Difficulty bonus: +{health_bonus} starting health[/green]")
            else:
                console.print(f"[red]Difficulty penalty: {health_bonus} starting health[/red]")
        
        # Apply credits bonus from difficulty
        credits_bonus = difficulty_mods.get("starting_credits_bonus", 0)
        if credits_bonus != 0:
            self.player.credits += credits_bonus
            
            # Show message about difficulty adjustment
            if credits_bonus > 0:
                console.print(f"[green]Difficulty bonus: +{credits_bonus} starting credits[/green]")
            else:
                console.print(f"[red]Difficulty penalty: {credits_bonus} starting credits[/red]")
        
        # Add starting items based on class
        if selected_class['name'] == "NetRunner":
            self.player.inventory.add_item("Cyberdeck", 1)
            self.player.inventory.add_item("ICEbreaker", 1)
        elif selected_class['name'] == "Enforcer":
            self.player.inventory.add_item("Heavy Pistol", 1)
            self.player.inventory.add_item("Armored Vest", 1)
        elif selected_class['name'] == "Fixer":
            self.player.inventory.add_item("Encrypted Phone", 1)
            self.player.inventory.add_item("Concealed Pistol", 1)
        elif selected_class['name'] == "Tech":
            self.player.inventory.add_item("Multi-tool", 1)
            self.player.inventory.add_item("Diagnostic Scanner", 1)
        
        # Common starting items
        self.player.inventory.add_item("Credchip", 1)
        self.player.inventory.add_item("Stimpack", 2)
        
        # Extra items on easy difficulty
        if difficulty == "easy":
            self.player.inventory.add_item("Stimpack", 1)  # One extra stimpack
            console.print(f"[green]Difficulty bonus: Extra Stimpack[/green]")
        
        # Start the intro sequence
        self.current_node = "intro"
        console.print("\n[bold green]Character created! Your cyberpunk adventure begins...[/bold green]")
        time.sleep(2)
    
    def load_game(self, console):
        """Load a saved game"""
        ui.clear_screen()
        ui.display_header(console, "LOAD GAME")
        
        save_files = save_system.get_save_files()
        
        if not save_files:
            console.print(Panel("[red]No save files found![/red]", title="Error"))
            time.sleep(2)
            return False
        
        console.print("[green]Available save files:[/green]")
        for i, save_file in enumerate(save_files, 1):
            # Extract save metadata to show details
            save_meta = save_system.get_save_metadata(save_file)
            if save_meta:
                console.print(f"[cyan]{i}. {save_meta['character_name']} - {save_meta['character_class']} - Level {save_meta['level']}[/cyan]")
                console.print(f"   Last saved: {save_meta['save_date']}")
            else:
                console.print(f"[cyan]{i}. {os.path.basename(save_file)}[/cyan] (No metadata available)")
        
        console.print("[cyan]0. Back to main menu[/cyan]")
        
        choice = IntPrompt.ask("[bold cyan]Select a save file to load[/bold cyan]", 
                              choices=[str(i) for i in range(0, len(save_files)+1)])
        
        if choice == 0:
            return False
        
        save_file = save_files[choice-1]
        
        try:
            # Load the save file
            save_data = save_system.load_game(save_file)
            
            # Recreate game state from save data
            self.player = character.Character.from_dict(save_data['player'])
            self.current_node = save_data['current_node']
            
            # Load choice history if it exists
            if 'choice_history' in save_data:
                import choice_history
                self.choice_history = choice_history.ChoiceHistory.from_dict(save_data['choice_history'])
                
            # Load district manager if it exists
            if 'district_manager' in save_data:
                self.district_manager = DistrictManager.from_dict(save_data['district_manager'])
            
            # Load codex data if it exists
            if 'codex' in save_data:
                import codex as codex_module
                self.codex = codex_module.Codex()
                self.codex.from_dict(save_data['codex'])
            
            console.print("[bold green]Game loaded successfully![/bold green]")
            time.sleep(1)
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error loading save file: {str(e)}[/bold red]")
            time.sleep(2)
            return False
    
    def save_game(self, console):
        """Save the current game state"""
        if not self.player:
            console.print("[bold red]No active game to save![/bold red]")
            return False
        
        ui.clear_screen()
        ui.display_header(console, "SAVE GAME")
        
        save_name = Prompt.ask("[bold cyan]Enter a name for your save[/bold cyan]", 
                              default=f"{self.player.name.lower().replace(' ', '_')}_save")
        
        # Create save data dictionary
        save_data = {
            'player': self.player.to_dict(),
            'current_node': self.current_node,
            'choice_history': self.choice_history.to_dict(),
            'district_manager': self.district_manager.to_dict(),
            'codex': self.codex.to_dict(),
            'metadata': {
                'character_name': self.player.name,
                'character_class': self.player.char_class,
                'level': self.player.level,
                'save_date': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        success = save_system.save_game(save_name, save_data)
        
        if success:
            console.print("[bold green]Game saved successfully![/bold green]")
        else:
            console.print("[bold red]Failed to save game![/bold red]")
        
        time.sleep(1)
        return success
    
    def game_loop(self, console):
        """Main game loop"""
        self.game_over = False
        
        while not self.game_over:
            ui.clear_screen()
            
            # Display character status
            ui.display_status_bar(console, self.player)
            
            # Get the current story node
            node = self.story_manager.get_node(self.current_node)
            
            if not node:
                # If node doesn't exist in predefined story, generate it with Ollama
                # Pass the choice history to enhance the generation
                node = self.ollama.generate_story_node(
                    self.current_node, 
                    self.player,
                    self.choice_history
                )
                
                if not node:
                    # Fallback if Ollama fails
                    console.print("[bold red]Error: Could not load or generate story node![/bold red]")
                    time.sleep(2)
                    self.game_over = True
                    continue
            
            # Process node type
            if node.get('type') == 'combat':
                self.handle_combat(console, node)
            elif node.get('type') == 'inventory':
                self.handle_inventory(console)
            elif node.get('type') == 'shop':
                self.handle_shop(console, node)
            elif node.get('type') == 'skill_check':
                self.handle_skill_check(console, node)
            elif node.get('type') == 'map':
                self.handle_map_travel(console)
            elif node.get('type') == 'location_action':
                self.handle_location_action(console, node)
            else:
                # Regular narrative node
                self.handle_narrative(console, node)
            
            # Check for game over conditions
            if self.player.health <= 0:
                self.handle_death(console)
                self.game_over = True
    
    def _process_codex_discoveries(self, console, codex_entries):
        """Process codex discoveries from a story node
        
        Args:
            console: Console for output
            codex_entries: List of codex entries to discover
        """
        newly_discovered = []
        import codex as codex_module  # Import locally to avoid circular imports
        
        for entry in codex_entries:
            entry_id = entry.get("id")
            
            # Skip if no ID provided
            if not entry_id:
                continue
                
            # Check if the entry should be dynamically generated
            dynamic = entry.get("dynamic", False)
            title = entry.get("title")
            category = entry.get("category")
            
            # First try to discover an existing entry
            was_discovered = self.codex.discover_entry(
                entry_id=entry_id,
                title=title,
                category=category
            )
            
            # If the entry doesn't exist yet and we have enough info, create it
            if not was_discovered and title and category:
                # Create a default entry that will be dynamically generated if needed
                default_content = f"## {title}\n\nInformation on this subject is being retrieved..."
                self.codex.add_entry(
                    entry_id=entry_id,
                    category=category,
                    title=title,
                    content=default_content,
                    dynamic_generation=dynamic
                )
                
                # Mark it as discovered
                was_discovered = self.codex.discover_entry(entry_id)
            
            if was_discovered:
                newly_discovered.append(entry_id)
        
        # Notify player of new codex entries if any were discovered
        if newly_discovered:
            # Play discovery sound if available
            if self.audio_enabled and self.audio_system:
                self.audio_system.play_sound("level_up")  # Reuse level up sound for now
                
            console.print("\n[bold cyan]New Codex Entry Discovered![/bold cyan]")
            for entry_id in newly_discovered:
                entry = self.codex.get_entry(entry_id)
                if entry:
                    console.print(f"[cyan]• {entry['title']} (in {codex_module.CATEGORIES[entry['category']]['name']})[/cyan]")
            
            console.print(f"[italic cyan]Access the Codex from the Main Menu to view these entries.[/italic cyan]")
            time.sleep(2)
    
    def handle_narrative(self, console, node):
        """Process a narrative story node"""
        # Display node text with proper formatting
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
        # Prepare the text panel once
        from rich.panel import Panel
        text_panel = Panel(f"[green]{node['text']}[/green]", title=node.get('title', ''))
        
        # Try to use animation for narrative text if available
        try:
            import animations
            from config import GAME_SETTINGS
            from rich.style import Style
            
            # Only use animations if enabled in settings
            if GAME_SETTINGS.get("ui_animations_enabled", True):
                # For cyberspace or hacking nodes, use digital rain animation as a prelude
                if node.get('environment') == 'cyberspace' or 'hacking' in node.get('tags', []):
                    animations.digital_rain(console, duration=1.5, density=0.2, chars="01")
                
                # Apply different effects based on node tags
                if 'corrupted' in node.get('tags', []) or 'glitching' in node.get('tags', []):
                    # For corrupted or glitching nodes, use data corruption effect
                    animations.data_corruption(
                        text_panel, 
                        console,
                        corruption_level=0.4
                    )
                elif 'holographic' in node.get('tags', []) or 'high_tech' in node.get('tags', []):
                    # For high-tech or holographic interfaces, use hologram effect
                    animations.hologram_effect(
                        text_panel,
                        console,
                        style=Style(color="#00FFFF")
                    )
                else:
                    # Default to typing effect for standard narrative
                    # Use a custom delay to avoid duplication issues
                    console.print(text_panel)
            else:
                # Animations disabled, just print the panel
                console.print(text_panel)
        except (ImportError, AttributeError) as e:
            # Fall back to standard display if animations not available
            console.print(text_panel)
        
        # Process codex discoveries if present in the node
        if node.get('codex_entries'):
            self._process_codex_discoveries(console, node['codex_entries'])
        
        # Check if this is an ending
        if node.get('is_ending', False):
            console.print("\n[bold magenta]THE END[/bold magenta]")
            console.print("[cyan]Press any key to return to the main menu...[/cyan]")
            input()
            self.game_over = True
            return
        
        # Display choices
        choices = node.get('choices', [])
        
        # If we have valid choices, display them
        if choices:
            console.print("\n[bold cyan]What will you do?[/bold cyan]")
            
            for i, choice in enumerate(choices, 1):
                # Check if choice has requirements
                requirements = choice.get('requirements', {})
                can_choose = True
                req_text = ""
                
                # Check item requirements
                if 'item' in requirements and not self.player.inventory.has_item(requirements['item']):
                    can_choose = False
                    req_text = f" [red](Requires: {requirements['item']})[/red]"
                
                # Check stat requirements
                for stat, value in requirements.get('stats', {}).items():
                    if self.player.stats.get(stat, 0) < value:
                        can_choose = False
                        req_text = f" [red](Requires: {stat.capitalize()} {value}+)[/red]"
                
                # Display the choice with appropriate color
                color = "cyan" if can_choose else "gray"
                console.print(f"[{color}]{i}. {choice['text']}{req_text}[/{color}]")
            
            # Add game options
            console.print("[yellow]I. Inventory[/yellow]")
            console.print("[yellow]C. Character (Skills & Perks)[/yellow]")
            console.print("[yellow]M. Map (Travel)[/yellow]")
            console.print("[yellow]S. Save Game[/yellow]")
            console.print("[yellow]Q. Quit to Main Menu[/yellow]")
            
            # Get player choice
            valid_choices = [str(i) for i in range(1, len(choices)+1)]
            valid_choices.extend(['i', 'I', 'c', 'C', 'm', 'M', 's', 'S', 'q', 'Q'])
            
            try:
                choice = Prompt.ask("[bold green]Enter your choice[/bold green]", choices=valid_choices)
            except (EOFError, KeyboardInterrupt):
                # Default to first choice if input fails
                console.print("[yellow]Input error detected. Defaulting to first choice.[/yellow]")
                choice = "1" if valid_choices else "q"
                time.sleep(1.5)
            
            # Process the choice
            if choice.upper() == 'I':
                self.handle_inventory(console)
            elif choice.upper() == 'C':
                self.handle_character_progression(console)
            elif choice.upper() == 'M':
                self.handle_map_travel(console)
            elif choice.upper() == 'S':
                self.save_game(console)
            elif choice.upper() == 'Q':
                if Prompt.ask("[bold red]Are you sure you want to quit? Unsaved progress will be lost.[/bold red]", 
                             choices=["y", "n"]) == "y":
                    self.game_over = True
            else:
                # Process narrative choice
                choice_idx = int(choice) - 1
                selected_choice = choices[choice_idx]
                
                # Check requirements again
                requirements = selected_choice.get('requirements', {})
                can_choose = True
                
                # Check item requirements
                if 'item' in requirements and not self.player.inventory.has_item(requirements['item']):
                    can_choose = False
                
                # Check stat requirements
                for stat, value in requirements.get('stats', {}).items():
                    if self.player.stats.get(stat, 0) < value:
                        can_choose = False
                
                if not can_choose:
                    console.print("[bold red]You don't meet the requirements for this choice![/bold red]")
                    time.sleep(2)
                    return
                
                # Process consequences
                consequences = selected_choice.get('consequences', {})
                
                # Item consequences
                for item, count in consequences.get('items_gained', {}).items():
                    self.player.inventory.add_item(item, count)
                    console.print(f"[green]Gained {count} {item}[/green]")
                
                for item, count in consequences.get('items_lost', {}).items():
                    self.player.inventory.remove_item(item, count)
                    console.print(f"[red]Lost {count} {item}[/red]")
                
                # Stat consequences
                for stat, value in consequences.get('stats_change', {}).items():
                    old_value = self.player.stats.get(stat, 0)
                    self.player.stats[stat] = max(0, old_value + value)
                    
                    if value > 0:
                        console.print(f"[green]{stat.capitalize()} increased by {value}[/green]")
                    elif value < 0:
                        console.print(f"[red]{stat.capitalize()} decreased by {abs(value)}[/red]")
                
                # Health/credits consequences
                if 'health_change' in consequences:
                    old_health = self.player.health
                    self.player.health = max(0, min(self.player.max_health, old_health + consequences['health_change']))
                    
                    if consequences['health_change'] > 0:
                        console.print(f"[green]Restored {consequences['health_change']} health[/green]")
                    elif consequences['health_change'] < 0:
                        console.print(f"[red]Lost {abs(consequences['health_change'])} health[/red]")
                
                if 'credits_change' in consequences:
                    old_credits = self.player.credits
                    self.player.credits = max(0, old_credits + consequences['credits_change'])
                    
                    if consequences['credits_change'] > 0:
                        console.print(f"[green]Gained {consequences['credits_change']} credits[/green]")
                    elif consequences['credits_change'] < 0:
                        console.print(f"[red]Lost {abs(consequences['credits_change'])} credits[/red]")
                
                # Apply any consequence delays
                if 'delay' in consequences:
                    time.sleep(consequences['delay'])
                
                # Record the choice in the history
                next_node = selected_choice.get('next_node', self.current_node)
                self.choice_history.add_choice(
                    node_id=self.current_node,
                    choice_text=selected_choice['text'],
                    next_node=next_node,
                    consequences=consequences
                )
                
                # Move to the next node
                self.current_node = next_node
        else:
            # No choices available, just continue to the next node
            console.print("\n[cyan]Press Enter to continue...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
            self.current_node = node.get('next_node', self.current_node)
    
    def handle_combat(self, console, node):
        """Process a combat encounter"""
        from config import GAME_SETTINGS, DIFFICULTY_SETTINGS
        import json
        
        enemy_data = node.get('enemy', {})
        enemy_name = enemy_data.get('name', 'Unknown Enemy')
        
        # Get difficulty settings
        difficulty = GAME_SETTINGS.get("difficulty", "normal")
        difficulty_mods = DIFFICULTY_SETTINGS.get(difficulty, {})
        enemy_damage_mult = difficulty_mods.get("enemy_damage_multiplier", 1.0)
        
        # Load enemies data from JSON file
        enemies_data = {}
        try:
            with open("data/enemies.json", "r") as f:
                enemies_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            console.print(f"[red]Warning: Could not load enemies data: {e}[/red]")
        
        # Check if enemy exists in the JSON data
        if enemy_name in enemies_data:
            # Create enemy from JSON data
            enemy_json_data = enemies_data[enemy_name]
            
            # Apply difficulty modifiers to stats from JSON
            modified_data = enemy_json_data.copy()
            modified_data["damage"] = int(modified_data.get("damage", 2) * enemy_damage_mult)
            
            # Create the enemy instance using the from_enemy_data method
            enemy = combat.Enemy.from_enemy_data(enemy_name, modified_data)
            console.print(f"[green]Loaded enemy data for {enemy_name} from enemies.json[/green]")
        else:
            # Fallback to node data if enemy not found in JSON
            console.print(f"[yellow]Warning: Enemy {enemy_name} not found in enemies.json, using node data[/yellow]")
            enemy = combat.Enemy(
                name=enemy_name,
                health=enemy_data.get('health', 10),
                damage=int(enemy_data.get('damage', 2) * enemy_damage_mult),
                defense=enemy_data.get('defense', 1),
                enemy_type=enemy_data.get('type', 'standard')
            )
        
        # Display combat intro
        ui.clear_screen()
        ui.display_status_bar(console, self.player)
        
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
        # Try to use animation for combat text if available
        try:
            import animations
            from config import GAME_SETTINGS
            
            # Only use animations if enabled in settings
            if GAME_SETTINGS.get("ui_animations_enabled", True):
                animations.glitch_text(
                    Panel(f"[red]{node['text']}[/red]", title=f"COMBAT: {enemy.name}"),
                    console
                )
            else:
                console.print(Panel(f"[red]{node['text']}[/red]", title=f"COMBAT: {enemy.name}"))
        except (ImportError, AttributeError):
            # Fall back to standard display if animations not available
            console.print(Panel(f"[red]{node['text']}[/red]", title=f"COMBAT: {enemy.name}"))
        
        # Display difficulty information if not normal
        if difficulty == "easy":
            console.print(f"[green]Easy difficulty: Your attacks deal more damage, enemy attacks deal less damage.[/green]")
        elif difficulty == "hard":
            console.print(f"[red]Hard difficulty: Your attacks deal less damage, enemy attacks deal more damage.[/red]")
        
        # Pass difficulty modifiers to combat system
        player_damage_mult = difficulty_mods.get("player_damage_multiplier", 1.0)
        combat_animations = GAME_SETTINGS.get("combat_animations", True)
        
        # Start the combat loop with difficulty settings
        combat_result = combat.run_combat(
            console, 
            self.player, 
            enemy, 
            player_damage_multiplier=player_damage_mult,
            use_animations=combat_animations,
            audio_system=self.audio_system if self.audio_enabled else None
        )
        
        # Process combat outcome
        if combat_result == 'victory':
            # Player won
            rewards = node.get('rewards', {})
            
            # Process rewards
            if 'experience' in rewards:
                self.player.add_experience(rewards['experience'], audio_system=self.audio_system if self.audio_enabled else None)
                console.print(f"[green]Gained {rewards['experience']} experience[/green]")
            
            if 'credits' in rewards:
                self.player.credits += rewards['credits']
                console.print(f"[green]Gained {rewards['credits']} credits[/green]")
                
                # Play credits pickup sound if audio system is available
                if self.audio_enabled and self.audio_system:
                    self.audio_system.play_sound("credits_pickup")
            
            if 'items' in rewards:
                for item, count in rewards['items'].items():
                    self.player.inventory.add_item(item, count)
                    console.print(f"[green]Gained {count} {item}[/green]")
            
            # Move to the victory node
            self.current_node = node.get('victory_node', self.current_node)
            
            console.print("\n[cyan]Press Enter to continue...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
        elif combat_result == 'defeat':
            # Player lost
            self.handle_death(console)
            self.game_over = True
        elif combat_result == 'escape':
            # Player escaped
            escape_consequences = node.get('escape_consequences', {})
            
            # Process escape consequences
            if 'health_loss' in escape_consequences:
                self.player.health = max(1, self.player.health - escape_consequences['health_loss'])
                console.print(f"[red]Lost {escape_consequences['health_loss']} health while escaping[/red]")
            
            if 'items_lost' in escape_consequences:
                for item, count in escape_consequences['items_lost'].items():
                    if self.player.inventory.has_item(item):
                        self.player.inventory.remove_item(item, count)
                        console.print(f"[red]Lost {count} {item} while escaping[/red]")
            
            # Move to the escape node
            self.current_node = node.get('escape_node', self.current_node)
            
            console.print("\n[cyan]Press Enter to continue...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
    
    def handle_inventory(self, console):
        """Handle inventory management"""
        ui.clear_screen()
        ui.display_header(console, "INVENTORY")
        
        # Display inventory contents
        items = self.player.inventory.get_all_items()
        
        if not items:
            console.print("[bold]Your inventory is empty.[/bold]")
        else:
            console.print("[bold cyan]Your inventory contains:[/bold cyan]")
            
            for i, (item_name, count) in enumerate(items.items(), 1):
                console.print(f"[cyan]{i}. {item_name} (x{count})[/cyan]")
        
        console.print("\n[yellow]1. Use an item[/yellow]")
        console.print("[yellow]2. Examine an item[/yellow]")
        console.print("[yellow]3. Drop an item[/yellow]")
        console.print("[yellow]4. Return to game[/yellow]")
        
        action = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=["1", "2", "3", "4"])
        
        if action == "1" and items:
            # Use an item
            item_idx = IntPrompt.ask("[bold cyan]Enter the number of the item to use[/bold cyan]", 
                                    choices=[str(i) for i in range(1, len(items)+1)])
            
            item_name = list(items.keys())[item_idx-1]
            self.player.use_item(item_name, console, audio_system=self.audio_system if self.audio_enabled else None)
        elif action == "2" and items:
            # Examine an item
            item_idx = IntPrompt.ask("[bold cyan]Enter the number of the item to examine[/bold cyan]", 
                                    choices=[str(i) for i in range(1, len(items)+1)])
            
            item_name = list(items.keys())[item_idx-1]
            item_info = inventory.get_item_info(item_name)
            
            if item_info:
                console.print(Panel(f"[green]{item_info['description']}[/green]", title=item_name))
            else:
                console.print(f"[green]This appears to be {item_name}. No detailed information available.[/green]")
            
            console.print("\n[cyan]Press Enter to continue...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
        elif action == "3" and items:
            # Drop an item
            item_idx = IntPrompt.ask("[bold cyan]Enter the number of the item to drop[/bold cyan]", 
                                    choices=[str(i) for i in range(1, len(items)+1)])
            
            item_name = list(items.keys())[item_idx-1]
            count = IntPrompt.ask(f"[bold cyan]How many {item_name} do you want to drop?[/bold cyan]", 
                                 default=1)
            
            if self.player.inventory.remove_item(item_name, count):
                console.print(f"[green]Dropped {count} {item_name}[/green]")
            else:
                console.print(f"[red]Failed to drop {item_name}[/red]")
            
            console.print("\n[cyan]Press Enter to continue...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
    
    def handle_map_travel(self, console):
        """Handle district map view and travel"""
        ui.clear_screen()
        ui.display_header(console, "DISTRICT MAP")
        ui.display_status_bar(console, self.player)
        
        # Get current district information
        current_district = self.district_manager.get_current_district()
        if not current_district:
            # Set the starting district if not already set
            self.district_manager.set_current_district("downtown")
            current_district = self.district_manager.get_current_district()
        
        # Generate and display the city map
        console.print("[bold cyan]Neo-Shanghai City Map:[/bold cyan]")
        map_lines = self.district_manager.generate_map_display()
        
        # Display the map with formatting
        for line in map_lines:
            if line.strip():  # Only print non-empty lines
                formatted_line = line
                # Highlight the current district
                if current_district:
                    formatted_line = formatted_line.replace(
                        current_district.name[:8].center(8),
                        f"[bold green]{current_district.name[:8].center(8)}[/bold green]"
                    )
                console.print(formatted_line)
            
        console.print("\n[bold blue]Map Legend:[/bold blue]")
        console.print("■ [cyan]District boxes show: Name, Danger level (█=danger), and [Connection count][/cyan]")
        console.print("■ [cyan]· lines represent available travel routes between districts[/cyan]")
        
        # Display current district information
        console.print(f"\n[bold green]Current Location: {current_district.name}[/bold green]")
        console.print(f"[cyan]{current_district.description}[/cyan]")
        console.print(f"[yellow]Danger Level: {current_district.danger_level}/5[/yellow]")
        
        # Display current reputation in this district if available
        district_rep = self.player.reputation.get_district_reputation(current_district.district_id)
        rep_title = self.player.reputation.get_reputation_title(district_rep)
        console.print(f"[magenta]Your Reputation: {rep_title} ({district_rep})[/magenta]")
        
        # Display district ASCII art if available
        if current_district.ascii_art:
            ui.display_ascii_art(console, current_district.ascii_art)
        
        # Display location-specific choices in this district
        location_choices = self.district_manager.get_district_location_choices()
        if location_choices:
            console.print("\n[bold purple]District-Specific Activities:[/bold purple]")
            for choice in location_choices:
                choice_type = choice.get("type", "general")
                icon = "🔧" if choice_type == "tech" else "👥" if choice_type == "social" else "⚔️" if choice_type == "combat" else "💼"
                console.print(f"{icon} [cyan]{choice['text']}[/cyan] ({choice_type})")
        
        # Get connected districts
        connected_districts = self.district_manager.get_connected_districts()
        
        if connected_districts:
            console.print("\n[bold cyan]Connected Districts:[/bold cyan]")
            
            for i, district in enumerate(connected_districts, 1):
                # Check if player has access to this district based on reputation
                has_access = self.player.reputation.has_access(district.district_id)
                color = "green" if has_access else "red"
                access_text = "" if has_access else " [red](Access Denied)[/red]"
                
                console.print(f"[{color}]{i}. {district.name} - Danger Level: {district.danger_level}/5{access_text}[/{color}]")
                console.print(f"   {district.description}")
                
            console.print("\n[yellow]Travel Options:[/yellow]")
            console.print("[yellow]* Enter a number to travel to that district[/yellow]")
            console.print("[yellow]* Enter 'E' to explore district actions[/yellow]")
            console.print("[yellow]* Enter '0' to return[/yellow]")
            
            choices = ["0", "e", "E"] + [str(i) for i in range(1, len(connected_districts)+1)]
            choice = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=choices)
            
            if choice.upper() == "E":
                # Player wants to explore local district actions
                self.handle_location_action(console)
                return
            elif choice != "0":
                district_idx = int(choice) - 1
                target_district = connected_districts[district_idx]
                
                # Check if player has access to this district
                if not self.player.reputation.has_access(target_district.district_id):
                    console.print(f"[bold red]You don't have access to {target_district.name}![/bold red]")
                    console.print("[red]You need to improve your reputation in this area first.[/red]")
                    time.sleep(2)
                    return
                
                # Handle travel cost/consequences based on danger level
                travel_risk = target_district.danger_level - current_district.danger_level
                if travel_risk > 0:
                    console.print(f"[yellow]Warning: You're traveling to a more dangerous area (risk +{travel_risk}).[/yellow]")
                    
                    # Random chance of an encounter based on risk level
                    if random.random() < (travel_risk * 0.15):  # 15% chance per risk level
                        console.print("[bold red]You've encountered trouble while traveling![/bold red]")
                        time.sleep(1)
                        
                        # Create an appropriate encounter based on district danger level
                        self.handle_travel_encounter(console, target_district.danger_level)
                
                # Complete the travel
                success = self.district_manager.set_current_district(target_district.district_id)
                
                if success:
                    console.print(f"[green]Successfully traveled to {target_district.name}.[/green]")
                    
                    # Play sound effect if available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("door_open")
                    
                    # Check for district-specific actions and offer them to the player
                    location_choices = self.district_manager.get_district_location_choices()
                    if location_choices:
                        console.print(f"\n[cyan]This district has {len(location_choices)} unique actions available.[/cyan]")
                        if Prompt.ask("[bold cyan]Would you like to explore district actions now?[/bold cyan]", choices=["y", "n"]) == "y":
                            self.handle_location_action(console)
                            return
                            
                    time.sleep(1)
                else:
                    console.print("[red]Failed to travel to the selected district.[/red]")
                    time.sleep(1)
        else:
            console.print("\n[bold red]No connected districts available![/bold red]")
            console.print("\n[cyan]Press Enter to return...[/cyan]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                # Just continue if input fails
                console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
                time.sleep(1.5)
    
    def handle_travel_encounter(self, console, danger_level):
        """Handle random encounters that can occur during district travel"""
        import json
        
        encounter_types = ["combat", "skill_check", "find"]
        weights = [0.6, 0.3, 0.1]  # 60% combat, 30% skill check, 10% find something
        
        encounter_type = random.choices(encounter_types, weights=weights, k=1)[0]
        
        if encounter_type == "combat":
            # Load enemies from JSON file
            enemies_data = {}
            try:
                with open("data/enemies.json", "r") as f:
                    enemies_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                console.print(f"[red]Warning: Could not load enemies data: {e}[/red]")
                # Fallback enemy types if JSON fails
                enemy_types = [
                    {"name": "Street Thug", "health": 8, "damage": 2, "defense": 1},  # Level 1
                    {"name": "Gang Member", "health": 12, "damage": 3, "defense": 2},  # Level 2
                    {"name": "Cyborg Enforcer", "health": 18, "damage": 4, "defense": 3},  # Level 3
                    {"name": "Rogue Security Bot", "health": 25, "damage": 5, "defense": 4},  # Level 4
                    {"name": "Corporate Assassin", "health": 35, "damage": 7, "defense": 5}   # Level 5
                ]
                enemy_idx = min(max(danger_level - 1, 0), 4)
                enemy_data = enemy_types[enemy_idx]
            else:
                # Group enemies by danger level (approximated by health and damage)
                danger_level_enemies = {
                    1: [],  # Low danger
                    2: [],  # Medium-low danger
                    3: [],  # Medium danger
                    4: [],  # Medium-high danger
                    5: []   # High danger
                }
                
                # Categorize enemies by their stats
                for enemy_name, enemy_info in enemies_data.items():
                    # Calculate approximate danger level
                    health = enemy_info.get("health", 10)
                    damage = enemy_info.get("damage", 3)
                    defense = enemy_info.get("defense", 1)
                    
                    # Simple formula to determine danger level (1-5)
                    estimated_danger = min(5, max(1, int((health / 10) + (damage / 2) + (defense / 2))))
                    
                    # Add to appropriate category
                    danger_level_enemies[estimated_danger].append(enemy_name)
                
                # Select enemy from appropriate danger level or fall back to lower levels if needed
                for level in range(danger_level, 0, -1):
                    if danger_level_enemies[level]:
                        # Randomly select an enemy from this danger level
                        enemy_name = random.choice(danger_level_enemies[level])
                        enemy_data = {"name": enemy_name}
                        console.print(f"[green]Using enemy '{enemy_name}' from enemies.json.[/green]")
                        break
                else:
                    # Fallback if no enemies found
                    enemy_fallback_types = ["Street Thug", "Mercenary", "Corporate Security Guard", "Cyber-Dog"]
                    enemy_name = random.choice(enemy_fallback_types)
                    enemy_data = {"name": enemy_name}
                    console.print(f"[yellow]No suitable enemies found for danger level {danger_level}, using fallback.[/yellow]")
            
            # Create a combat node
            combat_node = {
                "type": "combat",
                "text": f"As you travel through the district, a {enemy_data['name']} ambushes you from the shadows!",
                "enemy": enemy_data,
                "rewards": {
                    "experience": 50 * danger_level,
                    "credits": 20 * danger_level,
                    "items": {"Stimpack": 1} if random.random() < 0.3 else {}
                },
                "victory_node": self.current_node,
                "escape_node": self.current_node,
                "escape_consequences": {
                    "health_loss": danger_level * 2,
                    "items_lost": {"Credits": danger_level * 5} if self.player.credits > danger_level * 5 else {}
                }
            }
            
            # Run the combat encounter
            self.handle_combat(console, combat_node)
        
        elif encounter_type == "skill_check":
            # Create a skill check based on danger level
            skills = ["strength", "intelligence", "charisma", "reflex"]
            skill = random.choice(skills)
            difficulty = 3 + danger_level  # Base difficulty (3) plus danger level
            
            # Create skill check node
            skill_node = {
                "type": "skill_check",
                "text": f"You encounter an obstacle that requires {skill}. You need to test your abilities to proceed safely.",
                "skill": skill,
                "difficulty": difficulty,
                "success_text": "You successfully navigate the situation and continue your journey.",
                "failure_text": "You fail to handle the situation properly, and suffer the consequences.",
                "success_consequences": {
                    "experience": 30 * danger_level
                },
                "failure_consequences": {
                    "health_change": -danger_level * 2
                }
            }
            
            # Run the skill check
            self.handle_skill_check(console, skill_node)
        
        elif encounter_type == "find":
            # Find something valuable
            item_options = [
                {"name": "Credits", "count": danger_level * 10},
                {"name": "Stimpack", "count": 1},
                {"name": "Scrap Electronics", "count": danger_level}
            ]
            
            found_item = random.choice(item_options)
            
            console.print(f"[green]While traveling, you found {found_item['count']} {found_item['name']}![/green]")
            
            if found_item['name'] == "Credits":
                self.player.credits += found_item['count']
            else:
                self.player.inventory.add_item(found_item['name'], found_item['count'])
            
            # Play appropriate sound if available
            if self.audio_enabled and self.audio_system:
                if found_item['name'] == "Credits":
                    self.audio_system.play_sound("credits_pickup")
                else:
                    self.audio_system.play_sound("item_pickup")
            
            time.sleep(2)
    
    def handle_shop(self, console, node):
        """Handle shop interaction"""
        ui.clear_screen()
        ui.display_status_bar(console, self.player)
        
        shop_name = node.get('shop_name', 'Shop')
        ui.display_header(console, shop_name)
        
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
        # Try to use animation for shop text if available
        try:
            import animations
            from config import GAME_SETTINGS
            
            # Only use animations if enabled in settings
            if GAME_SETTINGS.get("ui_animations_enabled", True):
                animations.cyber_scan(
                    Panel(f"[green]{node['text']}[/green]"),
                    console
                )
            else:
                console.print(Panel(f"[green]{node['text']}[/green]"))
        except (ImportError, AttributeError):
            # Fall back to standard display if animations not available
            console.print(Panel(f"[green]{node['text']}[/green]"))
        
        # Display shop inventory
        shop_inventory = node.get('inventory', {})
        
        if not shop_inventory:
            console.print("[bold red]The shop has nothing for sale.[/bold red]")
        else:
            console.print(f"[bold cyan]Credits: {self.player.credits}[/bold cyan]")
            console.print("\n[bold cyan]Items for sale:[/bold cyan]")
            
            for i, (item_name, details) in enumerate(shop_inventory.items(), 1):
                price = details.get('price', 0)
                description = details.get('description', '')
                console.print(f"[cyan]{i}. {item_name} - {price} credits[/cyan]")
                console.print(f"   {description}")
        
        console.print("\n[yellow]1. Buy an item[/yellow]")
        console.print("[yellow]2. Sell an item[/yellow]")
        console.print("[yellow]3. Leave shop[/yellow]")
        
        action = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=["1", "2", "3"])
        
        if action == "1" and shop_inventory:
            # Buy an item
            item_idx = IntPrompt.ask("[bold cyan]Enter the number of the item to buy[/bold cyan]", 
                                    choices=[str(i) for i in range(1, len(shop_inventory)+1)])
            
            item_name = list(shop_inventory.keys())[item_idx-1]
            price = shop_inventory[item_name]['price']
            
            if self.player.credits >= price:
                count = IntPrompt.ask(f"[bold cyan]How many {item_name} do you want to buy?[/bold cyan]", 
                                     default=1)
                
                total_price = price * count
                
                if self.player.credits >= total_price:
                    self.player.credits -= total_price
                    self.player.inventory.add_item(item_name, count)
                    console.print(f"[green]Bought {count} {item_name} for {total_price} credits[/green]")
                    
                    # Play transaction sound if audio system is available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("shop_transaction")
                else:
                    console.print(f"[red]You can't afford {count} {item_name}[/red]")
            else:
                console.print(f"[red]You can't afford {item_name}[/red]")
            
            time.sleep(1)
        elif action == "2":
            # Sell an item
            player_items = self.player.inventory.get_all_items()
            
            if not player_items:
                console.print("[bold red]You have nothing to sell.[/bold red]")
                time.sleep(1)
            else:
                console.print("\n[bold cyan]Your inventory:[/bold cyan]")
                
                for i, (item_name, count) in enumerate(player_items.items(), 1):
                    # Calculate sell price (usually 50% of buy price)
                    sell_price = 0
                    if item_name in shop_inventory:
                        sell_price = max(1, shop_inventory[item_name]['price'] // 2)
                    else:
                        # Default price for items not in shop
                        sell_price = 5
                    
                    console.print(f"[cyan]{i}. {item_name} (x{count}) - {sell_price} credits each[/cyan]")
                
                item_idx = IntPrompt.ask("[bold cyan]Enter the number of the item to sell[/bold cyan]", 
                                       choices=[str(i) for i in range(1, len(player_items)+1)])
                
                item_name = list(player_items.keys())[item_idx-1]
                max_count = player_items[item_name]
                
                count = IntPrompt.ask(f"[bold cyan]How many {item_name} do you want to sell?[/bold cyan]", 
                                    default=1)
                
                count = min(count, max_count)
                
                # Calculate sell price
                sell_price = 0
                if item_name in shop_inventory:
                    sell_price = max(1, shop_inventory[item_name]['price'] // 2)
                else:
                    # Default price for items not in shop
                    sell_price = 5
                
                total_price = sell_price * count
                
                if self.player.inventory.remove_item(item_name, count):
                    self.player.credits += total_price
                    console.print(f"[green]Sold {count} {item_name} for {total_price} credits[/green]")
                    
                    # Play transaction sound if audio system is available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("shop_transaction")
                else:
                    console.print(f"[red]Failed to sell {item_name}[/red]")
                    
                    # Play error sound if audio system is available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("skill_failure")
                
                time.sleep(1)
        
        # If not leaving the shop, stay in the shop
        if action != "3":
            self.handle_shop(console, node)
        else:
            # Return to the previous node or specified exit node
            self.current_node = node.get('exit_node', self.current_node)
    
    def handle_skill_check(self, console, node):
        """Handle a skill check scenario"""
        ui.clear_screen()
        ui.display_status_bar(console, self.player)
        
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
        # Try to use animation for skill check text if available
        try:
            import animations
            from config import GAME_SETTINGS
            
            # Only use animations if enabled in settings
            if GAME_SETTINGS.get("ui_animations_enabled", True):
                animations.matrix_effect(
                    Panel(f"[green]{node['text']}[/green]", title=node.get('title', 'Skill Check')),
                    console
                )
            else:
                console.print(Panel(f"[green]{node['text']}[/green]", title=node.get('title', 'Skill Check')))
        except (ImportError, AttributeError):
            # Fall back to standard display if animations not available
            console.print(Panel(f"[green]{node['text']}[/green]", title=node.get('title', 'Skill Check')))
        
        # Get skill check details
        skill = node.get('skill', 'intelligence')
        difficulty = node.get('difficulty', 5)
        
        player_skill = self.player.stats.get(skill, 0)
        
        console.print(f"\n[bold cyan]Skill Check: {skill.capitalize()}[/bold cyan]")
        console.print(f"[cyan]Your {skill.capitalize()}: {player_skill}[/cyan]")
        console.print(f"[cyan]Difficulty: {difficulty}[/cyan]")
        
        # Roll for skill check
        roll = random.randint(1, 10)
        total = player_skill + roll
        
        console.print(f"\n[bold]You rolled: {roll}[/bold]")
        console.print(f"[bold]Total: {total} vs. Difficulty: {difficulty}[/bold]")
        
        # Determine result
        success = total >= difficulty
        
        if success:
            console.print(f"\n[bold green]SUCCESS![/bold green]")
            
            # Play success sound if audio system is available
            if self.audio_enabled and self.audio_system:
                self.audio_system.play_sound("skill_success")
            
            # Process success rewards
            rewards = node.get('success_rewards', {})
            
            # Process rewards
            if 'experience' in rewards:
                self.player.add_experience(rewards['experience'], 
                                           audio_system=self.audio_system if self.audio_enabled else None)
                console.print(f"[green]Gained {rewards['experience']} experience[/green]")
            
            if 'credits' in rewards:
                self.player.credits += rewards['credits']
                console.print(f"[green]Gained {rewards['credits']} credits[/green]")
                
                # Play credits pickup sound if audio system is available
                if self.audio_enabled and self.audio_system:
                    self.audio_system.play_sound("credits_pickup")
            
            if 'items' in rewards:
                for item, count in rewards['items'].items():
                    self.player.inventory.add_item(item, count)
                    console.print(f"[green]Gained {count} {item}[/green]")
                    
                    # Play item pickup sound if audio system is available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("item_pickup")
            
            # Move to success node
            self.current_node = node.get('success_node', self.current_node)
        else:
            console.print(f"\n[bold red]FAILURE![/bold red]")
            
            # Play failure sound if audio system is available
            if self.audio_enabled and self.audio_system:
                self.audio_system.play_sound("skill_failure")
            
            # Process failure consequences
            consequences = node.get('failure_consequences', {})
            
            if 'health_loss' in consequences:
                self.player.health = max(0, self.player.health - consequences['health_loss'])
                console.print(f"[red]Lost {consequences['health_loss']} health[/red]")
            
            if 'credits_loss' in consequences:
                loss = min(self.player.credits, consequences['credits_loss'])
                self.player.credits -= loss
                console.print(f"[red]Lost {loss} credits[/red]")
            
            if 'items_lost' in consequences:
                for item, count in consequences['items_lost'].items():
                    if self.player.inventory.has_item(item):
                        self.player.inventory.remove_item(item, count)
                        console.print(f"[red]Lost {count} {item}[/red]")
            
            # Move to failure node
            self.current_node = node.get('failure_node', self.current_node)
        
        console.print("\n[cyan]Press Enter to continue...[/cyan]")
        input()
    
    def handle_character_progression(self, console):
        """Handle character progression, skills, and perks"""
        ui.clear_screen()
        ui.display_header(console, "CHARACTER PROGRESSION")
        
        # Display basic character info
        console.print(f"[cyan]Name:[/cyan] {self.player.name}")
        console.print(f"[cyan]Class:[/cyan] {self.player.char_class}")
        console.print(f"[cyan]Level:[/cyan] {self.player.level}")
        console.print(f"[cyan]Experience:[/cyan] {self.player.experience}")
        
        # Get skill and perk points
        skill_points = self.player.progression.skill_points
        perk_points = self.player.progression.perk_points
        
        console.print(f"\n[green]Available Skill Points: {skill_points}[/green]")
        console.print(f"[green]Available Perk Points: {perk_points}[/green]")
        
        # Display menu options
        console.print("\n[yellow]1. View/Upgrade Skills[/yellow]")
        console.print("[yellow]2. View/Acquire Perks[/yellow]")
        console.print("[yellow]3. View Active Abilities[/yellow]")
        console.print("[yellow]4. Return to Game[/yellow]")
        
        action = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=["1", "2", "3", "4"])
        
        if action == "1":
            self._handle_skills_menu(console)
        elif action == "2":
            self._handle_perks_menu(console)
        elif action == "3":
            self._handle_abilities_menu(console)
        # action 4 returns to game
        
    def _handle_skills_menu(self, console):
        """Handle the skills submenu for upgrading character skills"""
        while True:
            ui.clear_screen()
            ui.display_header(console, "SKILLS")
            
            # Get available skills from progression system
            available_skills = self.player.progression.get_available_skills()
            skill_categories = {}
            
            # Organize skills by category
            for skill_tuple in available_skills:
                skill, can_learn, message = skill_tuple
                category = skill.category
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append((skill, can_learn, message))
            
            # Display skill points
            skill_points = self.player.progression.skill_points
            console.print(f"[green]Available Skill Points: {skill_points}[/green]\n")
            
            # Display skills by category
            for category, skills in skill_categories.items():
                console.print(f"[bold cyan]{category.upper()}[/bold cyan]")
                
                for i, (skill, can_learn, message) in enumerate(skills, 1):
                    current_level = self.player.progression.get_skill_level(skill.skill_id)
                    max_level = skill.max_level
                    
                    # Determine display color based on availability
                    if can_learn:
                        color = "green"
                    else:
                        color = "gray"
                    
                    # Display skill with level indicator
                    console.print(f"[{color}]{i}. {skill.name} ({current_level}/{max_level}) - {skill.description}[/{color}]")
                    
                    # If there's a reason why skill can't be learned, show it
                    if not can_learn and message:
                        console.print(f"   [red]{message}[/red]")
                    
                    # Show skill level effects if they have any levels
                    if current_level > 0:
                        effects = skill.get_effects_at_level(current_level)
                        if effects:
                            effect_text = ", ".join([f"{k}: {v}" for k, v in effects.items()])
                            console.print(f"   [cyan]Current Effects: {effect_text}[/cyan]")
                    
                    # Show next level effects if not at max
                    if current_level < max_level:
                        next_effects = skill.get_effects_at_level(current_level + 1)
                        if next_effects:
                            effect_text = ", ".join([f"{k}: {v}" for k, v in next_effects.items()])
                            console.print(f"   [yellow]Next Level: {effect_text}[/yellow]")
                
                console.print("")  # Add spacing between categories
            
            # User options
            console.print("[yellow]U. Upgrade a skill[/yellow]")
            console.print("[yellow]B. Back to character menu[/yellow]")
            
            choice = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=["u", "U", "b", "B"])
            
            if choice.upper() == "U" and skill_points > 0:
                # Upgrade a skill
                flat_skills = []
                for skills in skill_categories.values():
                    flat_skills.extend(skills)
                
                # Check if there are any skills available to upgrade
                upgradable_skills = [s for s, can_learn, _ in flat_skills if can_learn]
                
                if not upgradable_skills:
                    console.print("[red]No skills available to upgrade at this time.[/red]")
                    console.print("[cyan]Press Enter to continue...[/cyan]")
                    input()
                    continue
                
                # Choose skill to upgrade
                console.print("[bold cyan]Choose a skill to upgrade:[/bold cyan]")
                for i, (skill, _, _) in enumerate(flat_skills, 1):
                    console.print(f"{i}. {skill.name}")
                
                skill_idx = IntPrompt.ask("[bold cyan]Enter skill number[/bold cyan]", 
                                         choices=[str(i) for i in range(1, len(flat_skills)+1)])
                
                selected_skill, can_learn, message = flat_skills[int(skill_idx)-1]
                
                if can_learn:
                    # Attempt to learn/upgrade the skill
                    success, result_message = self.player.progression.learn_skill(selected_skill.skill_id)
                    
                    if success:
                        console.print(f"[green]{result_message}[/green]")
                        
                        # Play sound if audio system available
                        if self.audio_enabled and self.audio_system:
                            self.audio_system.play_sound("skill_success")
                    else:
                        console.print(f"[red]{result_message}[/red]")
                        
                        # Play sound if audio system available
                        if self.audio_enabled and self.audio_system:
                            self.audio_system.play_sound("skill_failure")
                else:
                    console.print(f"[red]Cannot upgrade this skill: {message}[/red]")
                    
                    # Play sound if audio system available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("skill_failure")
                
                console.print("[cyan]Press Enter to continue...[/cyan]")
                input()
            elif choice.upper() == "B":
                # Return to character progression menu
                break
            
    def _handle_perks_menu(self, console):
        """Handle the perks submenu for acquiring character perks"""
        while True:
            ui.clear_screen()
            ui.display_header(console, "PERKS")
            
            # Get available perks from progression system
            available_perks = self.player.progression.get_available_perks()
            perk_categories = {}
            
            # Organize perks by category
            for perk_tuple in available_perks:
                perk, can_learn, message = perk_tuple
                category = perk.category
                if category not in perk_categories:
                    perk_categories[category] = []
                perk_categories[category].append((perk, can_learn, message))
            
            # Display perk points
            perk_points = self.player.progression.perk_points
            console.print(f"[green]Available Perk Points: {perk_points}[/green]\n")
            
            # Display perks by category
            for category, perks in perk_categories.items():
                console.print(f"[bold cyan]{category.upper()}[/bold cyan]")
                
                for i, (perk, can_learn, message) in enumerate(perks, 1):
                    has_perk = self.player.progression.has_perk(perk.perk_id)
                    
                    # Determine display color based on availability
                    if has_perk:
                        color = "green"
                        status = "[ACQUIRED]"
                    elif can_learn:
                        color = "yellow"
                        status = "[AVAILABLE]"
                    else:
                        color = "gray"
                        status = "[LOCKED]"
                    
                    # Display perk information
                    console.print(f"[{color}]{i}. {perk.name} {status} - {perk.description}[/{color}]")
                    
                    # If there's a reason why perk can't be learned, show it
                    if not can_learn and not has_perk and message:
                        console.print(f"   [red]{message}[/red]")
                    
                    # Show perk effects
                    if perk.effects:
                        effect_text = ", ".join([f"{k}: {v}" for k, v in perk.effects.items()])
                        console.print(f"   [cyan]Effects: {effect_text}[/cyan]")
                
                console.print("")  # Add spacing between categories
            
            # User options
            console.print("[yellow]A. Acquire a perk[/yellow]")
            console.print("[yellow]B. Back to character menu[/yellow]")
            
            choice = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=["a", "A", "b", "B"])
            
            if choice.upper() == "A" and perk_points > 0:
                # Acquire a perk
                flat_perks = []
                for perks in perk_categories.values():
                    flat_perks.extend(perks)
                
                # Check if there are any perks available to acquire
                acquirable_perks = [p for p, can_learn, _ in flat_perks if can_learn]
                
                if not acquirable_perks:
                    console.print("[red]No perks available to acquire at this time.[/red]")
                    console.print("[cyan]Press Enter to continue...[/cyan]")
                    input()
                    continue
                
                # Choose perk to acquire
                console.print("[bold cyan]Choose a perk to acquire:[/bold cyan]")
                for i, (perk, _, _) in enumerate(flat_perks, 1):
                    console.print(f"{i}. {perk.name}")
                
                perk_idx = IntPrompt.ask("[bold cyan]Enter perk number[/bold cyan]", 
                                        choices=[str(i) for i in range(1, len(flat_perks)+1)])
                
                selected_perk, can_learn, message = flat_perks[int(perk_idx)-1]
                
                if can_learn:
                    # Attempt to learn the perk
                    success, result_message = self.player.progression.learn_perk(selected_perk.perk_id)
                    
                    if success:
                        console.print(f"[green]{result_message}[/green]")
                        
                        # Play sound if audio system available
                        if self.audio_enabled and self.audio_system:
                            self.audio_system.play_sound("skill_success")
                    else:
                        console.print(f"[red]{result_message}[/red]")
                        
                        # Play sound if audio system available
                        if self.audio_enabled and self.audio_system:
                            self.audio_system.play_sound("skill_failure")
                else:
                    console.print(f"[red]Cannot acquire this perk: {message}[/red]")
                    
                    # Play sound if audio system available
                    if self.audio_enabled and self.audio_system:
                        self.audio_system.play_sound("skill_failure")
                
                console.print("[cyan]Press Enter to continue...[/cyan]")
                input()
            elif choice.upper() == "B":
                # Return to character progression menu
                break
                
    def _handle_abilities_menu(self, console):
        """Handle the active abilities menu for viewing character abilities"""
        ui.clear_screen()
        ui.display_header(console, "ACTIVE ABILITIES")
        
        # Get character abilities
        abilities = self.player.get_available_abilities()
        
        if not abilities:
            console.print("[yellow]You don't have any active abilities.[/yellow]")
        else:
            console.print("[green]Your active abilities:[/green]\n")
            
            for ability_id, ability_data in abilities.items():
                name = ability_data.get('name', ability_id)
                description = ability_data.get('description', 'No description available')
                cooldown = ability_data.get('cooldown', 0)
                
                console.print(f"[cyan]{name}[/cyan]")
                console.print(f"[green]{description}[/green]")
                console.print(f"[yellow]Cooldown: {cooldown} turns[/yellow]\n")
        
        # Display abilities from skills and perks
        all_effects = self.player.progression.calculate_all_effects()
        if all_effects:
            console.print("\n[bold cyan]Combat Effects from Skills & Perks:[/bold cyan]")
            
            # Show combat-related numerical bonuses
            bonus_effects = {
                "damage_bonus": "Damage Bonus",
                "defense_bonus": "Defense Bonus",
                "critical_chance": "Critical Chance",
                "dodge_chance": "Dodge Chance",
                "stealth_bonus": "Stealth Bonus",
                "hacking_bonus": "Hacking Bonus",
                "healing_bonus": "Healing Bonus"
            }
            
            for effect_key, display_name in bonus_effects.items():
                if effect_key in all_effects and all_effects[effect_key] > 0:
                    console.print(f"[green]{display_name}: +{all_effects[effect_key]}[/green]")
            
            # Show stat bonuses
            if "stat_bonuses" in all_effects:
                for stat, bonus in all_effects["stat_bonuses"].items():
                    if bonus > 0:
                        console.print(f"[green]{stat.capitalize()}: +{bonus}[/green]")
            
            # Show abilities granted by skills/perks
            if "abilities" in all_effects and all_effects["abilities"]:
                console.print("\n[bold cyan]Abilities Granted by Skills & Perks:[/bold cyan]")
                for ability_name in all_effects["abilities"]:
                    # Check if this ability is in the character's available abilities
                    ability_found = False
                    for ability_id, ability_data in abilities.items():
                        if ability_data.get('name') == ability_name:
                            ability_found = True
                            break
                    
                    if not ability_found:
                        console.print(f"[cyan]{ability_name}[/cyan]")
                        console.print(f"[green]Special ability unlocked through character progression[/green]")
        
        console.print("\n[cyan]Press Enter to return to the character menu...[/cyan]")
        input()
        
    def handle_death(self, console):
        """Handle player death"""
        ui.clear_screen()
        
        # Play death sound if audio system is available
        if self.audio_enabled and self.audio_system:
            # Stop any current music
            self.audio_system.stop_music()
            # Play player damage sound
            self.audio_system.play_sound("player_damage")
        
        # Display death screen
        ui.display_ascii_art(console, "death")
        
        console.print(Panel("[bold red]YOU ARE DEAD[/bold red]", title="Game Over"))
        console.print("\n[red]Your journey ends here, in the cold neon shadows of the city...[/red]")
        console.print("\n[cyan]Press Enter to return to the main menu...[/cyan]")
        
        input()
        
    def handle_location_action(self, console, node=None):
        """Handle location-specific actions in the current district"""
        ui.clear_screen()
        ui.display_header(console, "DISTRICT ACTIONS")
        ui.display_status_bar(console, self.player)
        
        # Get current district
        current_district = self.district_manager.get_current_district()
        if not current_district:
            console.print("[bold red]Error: No current district found![/bold red]")
            time.sleep(2)
            return
        
        # Get location-specific choices
        location_choices = self.district_manager.get_district_location_choices()
        
        if not location_choices:
            console.print(f"[bold yellow]There are no special actions available in {current_district.name}.[/bold yellow]")
            console.print("\n[cyan]Press Enter to return...[/cyan]")
            input()
            return
        
        # Display district info and ASCII art
        console.print(f"[bold green]Location: {current_district.name}[/bold green]")
        console.print(f"[cyan]{current_district.description}[/cyan]")
        
        if current_district.ascii_art:
            ui.display_ascii_art(console, current_district.ascii_art)
            
        # Display factions present in this district
        district_factions = self.district_manager.get_factions_in_district(current_district.district_id)
        if district_factions:
            console.print("\n[bold purple]Factions with presence in this district:[/bold purple]")
            for faction in district_factions:
                # Check player's reputation with this faction
                faction_rep = self.player.reputation.get_faction_reputation(faction.faction_id)
                rep_title = self.player.reputation.get_reputation_title(faction_rep)
                
                # Determine color based on relationship
                if faction_rep >= 40:
                    color = "green"
                elif faction_rep >= 0:
                    color = "blue"
                elif faction_rep > -40:
                    color = "yellow"
                else:
                    color = "red"
                
                # Display influence level (home district vs regular presence)
                if faction.home_district == current_district.district_id:
                    influence = "[bold]HEADQUARTERS[/bold]"
                else:
                    influence = "Presence"
                
                console.print(f"[{color}]► {faction.name} ({faction.faction_type}) - {influence}[/{color}]")
                console.print(f"   [dim]{faction.description}[/dim]")
                console.print(f"   Your standing: {rep_title} ({faction_rep})")
                
            # Display hint about faction reputation
            console.print("\n[dim italic]Note: Your reputation with these factions will affect available jobs, prices, and interactions.[/dim italic]")
        
        # Display available actions
        console.print("\n[bold purple]Available Actions in this District:[/bold purple]")
        for i, choice in enumerate(location_choices, 1):
            choice_type = choice.get("type", "general")
            icon = "🔧" if choice_type == "tech" else "👥" if choice_type == "social" else "⚔️" if choice_type == "combat" else "💼"
            console.print(f"[cyan]{i}. {icon} {choice['text']} ({choice_type})[/cyan]")
        
        console.print("\n[yellow]0. Return[/yellow]")
        
        # Get player choice
        valid_choices = ["0"] + [str(i) for i in range(1, len(location_choices)+1)]
        choice = Prompt.ask("[bold green]What would you like to do?[/bold green]", choices=valid_choices)
        
        if choice == "0":
            return
        
        # Process the selected location action
        choice_idx = int(choice) - 1
        selected_action = location_choices[choice_idx]
        
        console.print(f"\n[bold cyan]You decide to {selected_action['text'].lower()}...[/bold cyan]")
        time.sleep(1)
        
        # Process the action using our location handler
        action_id = selected_action['id']
        district_id = current_district.district_id
        
        # Get results from location handler
        results = self.location_handler.handle_location_action(
            console, 
            action_id, 
            district_id
        )
        
        # Process action results
        if 'messages' in results:
            for message in results['messages']:
                console.print(message)
                time.sleep(0.5)  # Small delay between messages
        
        # Handle credits change
        if 'credits_change' in results and results['credits_change'] != 0:
            credits_change = results['credits_change']
            if credits_change > 0:
                self.player.credits += credits_change
                console.print(f"[green]You gained {credits_change} credits.[/green]")
                
                # Play credits pickup sound if available
                if self.audio_enabled and self.audio_system and credits_change > 0:
                    self.audio_system.play_sound("credits_pickup")
            else:
                self.player.credits = max(0, self.player.credits + credits_change)
                console.print(f"[red]You lost {abs(credits_change)} credits.[/red]")
        
        # Handle items gained
        for item_name, count in results.get('items_gained', {}).items():
            self.player.inventory.add_item(item_name, count)
            console.print(f"[green]You acquired {count} {item_name}.[/green]")
            
            # Play item pickup sound if available
            if self.audio_enabled and self.audio_system:
                self.audio_system.play_sound("item_pickup")
        
        # Handle items lost
        for item_name, count in results.get('items_lost', {}).items():
            if self.player.inventory.has_item(item_name):
                self.player.inventory.remove_item(item_name, count)
                console.print(f"[red]You lost {count} {item_name}.[/red]")
        
        # Handle health change
        if 'health_change' in results and results['health_change'] != 0:
            health_change = results['health_change']
            if health_change > 0:
                old_health = self.player.health
                self.player.health = min(self.player.max_health, old_health + health_change)
                actual_change = self.player.health - old_health
                console.print(f"[green]You recovered {actual_change} health points.[/green]")
                
                # Play heal sound if available
                if self.audio_enabled and self.audio_system and actual_change > 0:
                    self.audio_system.play_sound("item_pickup")  # Using as heal sound
            else:
                old_health = self.player.health
                self.player.health = max(0, old_health + health_change)
                actual_change = self.player.health - old_health
                console.print(f"[red]You lost {abs(actual_change)} health points.[/red]")
                
                # Play damage sound if available
                if self.audio_enabled and self.audio_system and actual_change < 0:
                    self.audio_system.play_sound("player_damage")
        
        # Handle experience gain
        if 'experience_gain' in results and results['experience_gain'] > 0:
            xp_gain = results['experience_gain']
            self.player.add_experience(xp_gain, audio_system=self.audio_system if self.audio_enabled else None)
            console.print(f"[green]You gained {xp_gain} experience points.[/green]")
        
        # Handle district reputation changes
        for district_id, rep_change in results.get('reputation_change', {}).items():
            if rep_change != 0:
                if rep_change > 0:
                    self.player.reputation.modify_district_reputation(district_id, rep_change)
                    district_name = self.district_manager.get_district(district_id).name
                    console.print(f"[green]Your reputation in {district_name} increased by {rep_change}.[/green]")
                else:
                    self.player.reputation.modify_district_reputation(district_id, rep_change)
                    district_name = self.district_manager.get_district(district_id).name
                    console.print(f"[red]Your reputation in {district_name} decreased by {abs(rep_change)}.[/red]")
        
        # Handle faction reputation changes
        for faction_id, rep_change in results.get('faction_reputation_change', {}).items():
            if rep_change != 0:
                # Use the enhanced modify_faction_reputation method which handles ripple effects
                faction_results = self.player.reputation.modify_faction_reputation(
                    faction_id, 
                    rep_change, 
                    district_manager=self.district_manager
                )
                
                # Get faction name
                faction = self.district_manager.get_faction(faction_id)
                if not faction:
                    continue
                    
                # Display primary change
                if rep_change > 0:
                    console.print(f"[green]Your reputation with {faction.name} increased by {rep_change}.[/green]")
                else:
                    console.print(f"[red]Your reputation with {faction.name} decreased by {abs(rep_change)}.[/red]")
                
                # Display ripple effects (secondary reputation changes)
                for ripple_id, ripple_amount in faction_results.get('ripple_effects', {}).items():
                    # Skip small ripple effects to avoid overwhelming the player
                    if abs(ripple_amount) < 3:
                        continue
                        
                    # Check if this is a district or faction effect
                    if ripple_id.startswith('district_'):
                        # This is a district reputation change
                        district_id = ripple_id.replace('district_', '')
                        district = self.district_manager.get_district(district_id)
                        if district:
                            if ripple_amount > 0:
                                console.print(f"[dim green]► This also improved your standing in {district.name} slightly.[/dim green]")
                            else:
                                console.print(f"[dim red]► This also harmed your standing in {district.name} slightly.[/dim red]")
                    else:
                        # This is a faction reputation change
                        affected_faction = self.district_manager.get_faction(ripple_id)
                        if affected_faction:
                            if ripple_amount > 0:
                                console.print(f"[dim green]► Your standing with {affected_faction.name} also improved slightly.[/dim green]")
                            else:
                                console.print(f"[dim red]► Your standing with {affected_faction.name} also decreased slightly.[/dim red]")
        
        # Handle combat encounter if one was triggered
        if 'combat_encounter' in results:
            combat_data = results['combat_encounter']
            
            # Create a combat node from the encounter data
            combat_node = {
                "type": "combat",
                "text": f"You're confronted by a {combat_data['enemy_type']}!",
                "enemy": {"name": combat_data['enemy_type']},
                "rewards": combat_data.get('rewards', {
                    "experience": 20 * combat_data.get('danger_level', 3),
                    "credits": 10 * combat_data.get('danger_level', 3)
                }),
                "victory_node": self.current_node,
                "escape_node": self.current_node
            }
            
            # Wait for user to acknowledge the encounter
            console.print("\n[cyan]Press Enter to continue to combat...[/cyan]")
            input()
            
            # Run the combat encounter
            self.handle_combat(console, combat_node)
            return
        
        console.print("\n[cyan]Press Enter to continue...[/cyan]")
        input()
