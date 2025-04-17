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
from districts import DistrictManager, District
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
        
        name = Prompt.ask("[bold cyan]Enter your character's name[/bold cyan]")
        
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
        
        class_choice = IntPrompt.ask("[bold cyan]Select your class[/bold cyan]", choices=[str(i) for i in range(1, len(classes)+1)])
        selected_class = classes[class_choice-1]
        
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
            else:
                # Regular narrative node
                self.handle_narrative(console, node)
            
            # Check for game over conditions
            if self.player.health <= 0:
                self.handle_death(console)
                self.game_over = True
    
    def handle_narrative(self, console, node):
        """Process a narrative story node"""
        # Display node text with proper formatting
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
        console.print(Panel(f"[green]{node['text']}[/green]", title=node.get('title', '')))
        
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
            console.print("[yellow]M. Map (Travel)[/yellow]")
            console.print("[yellow]S. Save Game[/yellow]")
            console.print("[yellow]Q. Quit to Main Menu[/yellow]")
            
            # Get player choice
            valid_choices = [str(i) for i in range(1, len(choices)+1)]
            valid_choices.extend(['i', 'I', 'm', 'M', 's', 'S', 'q', 'Q'])
            
            choice = Prompt.ask("[bold green]Enter your choice[/bold green]", choices=valid_choices)
            
            # Process the choice
            if choice.upper() == 'I':
                self.handle_inventory(console)
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
            input()
            self.current_node = node.get('next_node', self.current_node)
    
    def handle_combat(self, console, node):
        """Process a combat encounter"""
        from config import GAME_SETTINGS, DIFFICULTY_SETTINGS
        
        enemy_data = node.get('enemy', {})
        
        # Get difficulty settings
        difficulty = GAME_SETTINGS.get("difficulty", "normal")
        difficulty_mods = DIFFICULTY_SETTINGS.get(difficulty, {})
        
        # Apply difficulty modifiers to enemy stats
        enemy_damage_mult = difficulty_mods.get("enemy_damage_multiplier", 1.0)
        
        # Initialize the enemy with difficulty modifications
        enemy = combat.Enemy(
            name=enemy_data.get('name', 'Unknown Enemy'),
            health=enemy_data.get('health', 10),
            damage=int(enemy_data.get('damage', 2) * enemy_damage_mult),
            defense=enemy_data.get('defense', 1)
        )
        
        # Display combat intro
        ui.clear_screen()
        ui.display_status_bar(console, self.player)
        
        if node.get('ascii_art'):
            ui.display_ascii_art(console, node['ascii_art'])
        
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
            input()
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
            input()
    
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
            input()
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
            input()
    
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
            
        # Display current district information
        console.print(f"[bold green]Current Location: {current_district.name}[/bold green]")
        console.print(f"[cyan]{current_district.description}[/cyan]")
        console.print(f"[yellow]Danger Level: {current_district.danger_level}/5[/yellow]")
        
        # Display current reputation in this district if available
        district_rep = self.player.reputation.get_district_reputation(current_district.district_id)
        rep_title = self.player.reputation.get_reputation_title(district_rep)
        console.print(f"[magenta]Your Reputation: {rep_title} ({district_rep})[/magenta]")
        
        # Display district ASCII art if available
        if current_district.ascii_art:
            ui.display_ascii_art(console, current_district.ascii_art)
        
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
                
            console.print("\n[yellow]Enter a number to travel to that district, or 0 to return[/yellow]")
            
            choices = ["0"] + [str(i) for i in range(1, len(connected_districts)+1)]
            choice = Prompt.ask("[bold green]Where would you like to go?[/bold green]", choices=choices)
            
            if choice != "0":
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
                        
                    time.sleep(1)
                else:
                    console.print("[red]Failed to travel to the selected district.[/red]")
                    time.sleep(1)
        else:
            console.print("\n[bold red]No connected districts available![/bold red]")
            console.print("\n[cyan]Press Enter to return...[/cyan]")
            input()
    
    def handle_travel_encounter(self, console, danger_level):
        """Handle random encounters that can occur during district travel"""
        encounter_types = ["combat", "skill_check", "find"]
        weights = [0.6, 0.3, 0.1]  # 60% combat, 30% skill check, 10% find something
        
        encounter_type = random.choices(encounter_types, weights=weights, k=1)[0]
        
        if encounter_type == "combat":
            # Create an appropriate enemy based on danger level
            enemy_types = [
                {"name": "Street Thug", "health": 8, "damage": 2, "defense": 1},  # Level 1
                {"name": "Gang Member", "health": 12, "damage": 3, "defense": 2},  # Level 2
                {"name": "Cyborg Enforcer", "health": 18, "damage": 4, "defense": 3},  # Level 3
                {"name": "Rogue Security Bot", "health": 25, "damage": 5, "defense": 4},  # Level 4
                {"name": "Corporate Assassin", "health": 35, "damage": 7, "defense": 5}   # Level 5
            ]
            
            # Adjust index to valid range (0-4)
            enemy_idx = min(max(danger_level - 1, 0), 4)
            enemy_data = enemy_types[enemy_idx]
            
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
