"""
Codex Module - In-game encyclopedia of lore and world-building details
"""
import json
import os
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.columns import Columns
from rich.box import SIMPLE_HEAVY, DOUBLE_EDGE

from config import COLORS
import assets
import animations

# Codex categories
CATEGORIES = {
    "world": {
        "name": "World",
        "description": "Information about the world of Neo Shanghai and its history",
        "icon": "🌆"
    },
    "factions": {
        "name": "Factions",
        "description": "Details about the major corporations, gangs, and other groups",
        "icon": "👥"
    },
    "technology": {
        "name": "Technology",
        "description": "Information about cybernetic implants, weapons, and other tech",
        "icon": "🔧"
    },
    "locations": {
        "name": "Locations",
        "description": "Details about districts, landmarks, and important places",
        "icon": "📍"
    },
    "characters": {
        "name": "Characters",
        "description": "Background on key figures in the world",
        "icon": "👤"
    },
    "events": {
        "name": "Events",
        "description": "Historical events that shaped the current world",
        "icon": "📅"
    }
}

class Codex:
    """Manages the in-game encyclopedia of lore and world-building details"""
    
    def __init__(self, data_path="data/codex.json"):
        """
        Initialize the codex
        
        Args:
            data_path (str): Path to the codex data file
        """
        self.data_path = data_path
        self.entries = {}
        self.discovered_entries = set()  # Track which entries the player has found
        self.load_data()
    
    def load_data(self):
        """Load codex data from file"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = data.get("entries", {})
                    
                    # Convert discovered entries to a set if it exists in the data
                    if "discovered" in data:
                        self.discovered_entries = set(data["discovered"])
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading codex data: {e}")
                # Initialize with empty data if there's an error
                self.entries = {}
                self.discovered_entries = set()
    
    def save_data(self):
        """Save codex data to file"""
        data = {
            "entries": self.entries,
            "discovered": list(self.discovered_entries)
        }
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving codex data: {e}")
    
    def add_entry(self, entry_id, category, title, content, related_entries=None, image=None, dynamic_generation=False):
        """
        Add a new entry to the codex
        
        Args:
            entry_id (str): Unique ID for the entry
            category (str): Category of the entry (must be in CATEGORIES)
            title (str): Title of the entry
            content (str): Markdown-formatted content
            related_entries (list, optional): List of related entry IDs
            image (str, optional): ASCII art reference for the entry
            dynamic_generation (bool, optional): Whether to dynamically generate content with Ollama
        
        Returns:
            bool: Whether the entry was added successfully
        """
        if category not in CATEGORIES:
            return False
            
        if entry_id in self.entries and not dynamic_generation:
            # Entry already exists, could update it here if needed
            return False
        
        # If dynamic generation is enabled and Ollama is configured, generate content
        if dynamic_generation:
            try:
                # Import here to avoid circular imports
                from config import USE_OLLAMA
                
                if USE_OLLAMA:
                    from ollama_integration import OllamaIntegration
                    
                    ollama = OllamaIntegration()
                    generated_entry = ollama.generate_codex_entry(
                        entry_id, 
                        category, 
                        title,
                        self.entries
                    )
                    
                    # Use generated content if available
                    if generated_entry and "content" in generated_entry:
                        # Override content with generated content
                        content = generated_entry.get("content", content)
                        # Use generated related entries if provided
                        if "related_entries" in generated_entry and generated_entry["related_entries"]:
                            related_entries = generated_entry.get("related_entries", related_entries)
                        # Use suggested image if provided
                        if "image" in generated_entry and generated_entry["image"]:
                            image = generated_entry.get("image", image)
            except Exception as e:
                print(f"Error generating dynamic content: {str(e)}")
                # Continue with provided content if generation fails
        
        self.entries[entry_id] = {
            "category": category,
            "title": title,
            "content": content,
            "related_entries": related_entries or [],
            "image": image
        }
        
        self.save_data()
        return True
    
    def discover_entry(self, entry_id, title=None, category=None):
        """
        Mark an entry as discovered by the player
        
        Args:
            entry_id (str): ID of the entry to mark as discovered
            title (str, optional): Title of the entry if it doesn't exist yet
            category (str, optional): Category of the entry if it doesn't exist yet
            
        Returns:
            bool: Whether the entry was newly discovered
        """
        # If the entry doesn't exist yet but title and category are provided,
        # create it dynamically with Ollama
        if entry_id not in self.entries and title and category:
            if category in CATEGORIES:
                # Create default placeholder content
                default_content = f"## {title}\n\nInformation on this subject is being retrieved..."
                
                # Attempt to add the entry with dynamic generation
                self.add_entry(
                    entry_id=entry_id,
                    category=category,
                    title=title,
                    content=default_content,
                    dynamic_generation=True  # This will trigger Ollama content generation
                )
        
        # Check if the entry exists now
        if entry_id not in self.entries:
            return False
            
        # Check if it's already discovered
        if entry_id in self.discovered_entries:
            return False
            
        # Mark as discovered
        self.discovered_entries.add(entry_id)
        self.save_data()
        return True
    
    def is_discovered(self, entry_id):
        """
        Check if an entry has been discovered
        
        Args:
            entry_id (str): ID of the entry to check
            
        Returns:
            bool: Whether the entry has been discovered
        """
        return entry_id in self.discovered_entries
    
    def get_entry(self, entry_id):
        """
        Get a codex entry by ID
        
        Args:
            entry_id (str): ID of the entry to retrieve
            
        Returns:
            dict: The entry data, or None if not found or not discovered
        """
        if entry_id not in self.entries:
            return None
            
        return self.entries[entry_id]
    
    def get_entries_by_category(self, category):
        """
        Get all discovered entries in a category
        
        Args:
            category (str): Category to filter by
            
        Returns:
            list: List of entry dictionaries with their IDs included
        """
        result = []
        
        for entry_id, entry in self.entries.items():
            if entry["category"] == category and entry_id in self.discovered_entries:
                # Include the ID in the entry data for convenience
                entry_data = entry.copy()
                entry_data["id"] = entry_id
                result.append(entry_data)
        
        return result
    
    def get_categories_with_discovered_entries(self):
        """
        Get list of categories that have at least one discovered entry
        
        Returns:
            list: List of category IDs
        """
        categories = set()
        
        for entry_id in self.discovered_entries:
            if entry_id in self.entries:
                categories.add(self.entries[entry_id]["category"])
        
        return list(categories)
    
    def get_discovery_count(self):
        """
        Get the number of discovered entries and total entries
        
        Returns:
            tuple: (discovered_count, total_count)
        """
        return len(self.discovered_entries), len(self.entries)
    
    def get_random_undiscovered_entry(self):
        """
        Get a random entry that hasn't been discovered yet
        
        Returns:
            str: Entry ID, or None if all entries are discovered
        """
        undiscovered = [entry_id for entry_id in self.entries if entry_id not in self.discovered_entries]
        
        if not undiscovered:
            return None
            
        return random.choice(undiscovered)
    
    def discover_random_entries(self, count=1, category=None):
        """
        Discover a random selection of entries
        
        Args:
            count (int): Number of entries to discover
            category (str, optional): Only discover entries from this category
            
        Returns:
            list: List of newly discovered entry IDs
        """
        undiscovered = []
        
        for entry_id in self.entries:
            if entry_id not in self.discovered_entries:
                if category is None or self.entries[entry_id]["category"] == category:
                    undiscovered.append(entry_id)
        
        if not undiscovered:
            return []
            
        to_discover = min(count, len(undiscovered))
        discovered = random.sample(undiscovered, to_discover)
        
        for entry_id in discovered:
            self.discover_entry(entry_id)
            
        self.save_data()
        return discovered
        
    def to_dict(self):
        """
        Convert the codex to a dictionary for saving
        
        Returns:
            dict: Dictionary representation of the codex
        """
        return {
            "entries": self.entries,
            "discovered": list(self.discovered_entries)
        }
        
    def from_dict(self, data):
        """
        Load codex from a dictionary (for loading saves)
        
        Args:
            data (dict): Dictionary with codex data
            
        Returns:
            Codex: Self for method chaining
        """
        if "entries" in data:
            self.entries = data["entries"]
            
        if "discovered" in data:
            self.discovered_entries = set(data["discovered"])
            
        return self

def display_codex_menu(console, codex, player=None):
    """
    Display the codex main menu and handle navigation
    
    Args:
        console: Console for output
        codex: Codex instance
        player: Player character (optional)
    """
    # Play a subtle animation when opening the codex
    animations.circuit_pattern(console, duration=1.0)
    
    while True:
        console.clear()
        
        # Display codex header with more cyberpunk style
        title_panel = Panel(
            "[bold cyan]NEURAL CODEX v2.1: Neo Shanghai Encyclopedia[/bold cyan]\n"
            "[dim cyan]// Neural-link interface active //[/dim cyan]",
            border_style="cyan",
            subtitle="[dim]Accessing data archives...[/dim]"
        )
        console.print(title_panel)
        
        # Display discovery statistics with a progress bar
        discovered, total = codex.get_discovery_count()
        percentage = (discovered/total*100) if total > 0 else 0
        
        # Create a visual progress bar
        bar_width = 40
        filled = int((bar_width * discovered) / total) if total > 0 else 0
        progress_bar = "[" + "█" * filled + "░" * (bar_width - filled) + "]"
        
        console.print(f"\n[bold]DATABANK STATUS:[/bold]")
        console.print(f"[dim cyan]Memory blocks discovered:[/dim cyan] [cyan]{discovered}[/cyan]/[cyan]{total}[/cyan]")
        console.print(f"[{COLORS['neon_pink']}]{progress_bar}[/{COLORS['neon_pink']}] {percentage:.1f}%")
        
        # Get categories with discovered entries
        available_categories = codex.get_categories_with_discovered_entries()
        
        if not available_categories:
            # Use an animation for the "no entries" message
            console.print("\n[bold yellow]< NO CODEX ENTRIES DETECTED >[/bold yellow]")
            animations.data_corruption("Neural interface has not recorded any data entries yet.\nExplore Neo Shanghai to expand your knowledge database.", console)
            console.print("\n[blink]> Press Enter to disconnect neural interface[/blink]")
            Prompt.ask("", default="")
            return
        
        # Display categories in a more cyberpunk way
        console.print("\n[bold]AVAILABLE DATA CLUSTERS:[/bold]")
        
        # Create a table for better formatting
        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        table.add_column("Index", style="dim cyan", width=4)
        table.add_column("Icon", width=2)
        table.add_column("Name", style=f"{COLORS['neon_pink']}")
        table.add_column("Count", style="cyan", width=10)
        table.add_column("Description", style="dim white")
        
        for i, category_id in enumerate(available_categories, 1):
            category_data = CATEGORIES[category_id]
            entry_count = len(codex.get_entries_by_category(category_id))
            
            table.add_row(
                f"[{i}]", 
                category_data['icon'], 
                category_data['name'], 
                f"({entry_count})", 
                category_data['description']
            )
        
        console.print(table)
        
        # Add a decorative divider
        console.print("\n[dim cyan]" + "═" * 50 + "[/dim cyan]")
        console.print("[0] [dim cyan]Disconnect neural interface[/dim cyan]")
        
        # Add a glitchy effect occasionally for immersion
        if random.random() < 0.2:  # 20% chance of glitch effect
            console.print("\n[bold red]< INTERFERENCE DETECTED - SIGNAL DEGRADING >[/bold red]")
        
        # Get user choice with enhanced prompt
        choice = Prompt.ask(
            "\n[bold cyan]> Select data cluster[/bold cyan]", 
            choices=[str(i) for i in range(len(available_categories) + 1)]
        )
        
        if choice == "0":
            # Animation for disconnecting from the codex
            animations.glitch_text("Neural interface disconnecting...", console)
            return
        
        # Display loading animation when selecting a category
        animations.loading_bar(console, length=30, message=f"Loading data cluster {choice}")
        
        # Display category
        category_id = available_categories[int(choice) - 1]
        display_category(console, codex, category_id)

def display_category(console, codex, category_id):
    """
    Display entries in a category
    
    Args:
        console: Console for output
        codex: Codex instance
        category_id: ID of the category to display
    """
    entries = codex.get_entries_by_category(category_id)
    
    # Show transition animation when entering a category
    if category_id == "technology":
        animations.digital_rain(console, duration=0.8, density=0.1)
    elif category_id == "factions":
        animations.hacker_transition(console, lines=3)
    else:
        animations.cyber_flicker(f"Loading {CATEGORIES[category_id]['name']} Database...", console)
    
    while True:
        console.clear()
        
        category_data = CATEGORIES[category_id]
        
        # Create a more cyberpunk styled header with category specific color
        category_colors = {
            "world": f"{COLORS['neon_blue']}",
            "factions": f"{COLORS['neon_pink']}",
            "technology": f"{COLORS['matrix_green']}",
            "locations": f"{COLORS['neon_cyan']}",
            "characters": f"{COLORS['neon_purple']}",
            "events": f"{COLORS['neon_orange']}"
        }
        color = category_colors.get(category_id, "cyan")
        
        header_panel = Panel(
            f"[bold {color}]NEURAL CODEX: {category_data['icon']} {category_data['name']}[/bold {color}]",
            border_style=color,
            subtitle=f"[dim]// {len(entries)} data fragments discovered //[/dim]"
        )
        console.print(header_panel)
        console.print(f"[dim]{category_data['description']}[/dim]\n")
        
        if not entries:
            # Show animated message for empty categories
            console.print("\n[bold yellow]< NO DATA FRAGMENTS AVAILABLE >[/bold yellow]")
            animations.data_corruption(
                "No entries have been discovered for this data cluster yet.\nContinue exploring to expand your knowledge base.", 
                console, 
                corruption_level=0.15
            )
        else:
            # Create a cyberpunk-styled table of entries
            table = Table(show_header=True, expand=True, box=SIMPLE_HEAVY)
            table.add_column("[dim]ID[/dim]", justify="center", style="dim cyan", width=3)
            table.add_column(f"[{color}]ENTRY TITLE[/{color}]", style="white")
            table.add_column("[dim]TYPE[/dim]", justify="right", style="dim", width=12)
            
            # Add some visual variety to the entries
            for i, entry in enumerate(entries, 1):
                # Add some cyberpunk flavor to the display
                entry_type = ""
                if "secret" in entry["id"] or "shadow" in entry["id"]:
                    entry_type = "[red]RESTRICTED[/red]"
                elif "neural" in entry["id"] or "cyber" in entry["id"]:
                    entry_type = "[green]TECHNICAL[/green]"
                elif "corp" in entry["id"]:
                    entry_type = "[blue]CORPORATE[/blue]"
                
                table.add_row(
                    f"[{i}]", 
                    entry["title"], 
                    entry_type
                )
            
            console.print(table)
        
        # Add decorative divider
        console.print(f"\n[dim {color}]" + "═" * 50 + f"[/dim {color}]")
        console.print(f"[0] [dim {color}]Return to main menu[/dim {color}]")
        
        # Occasionally show a "connection unstable" message for immersion
        if random.random() < 0.15:  # 15% chance
            console.print("\n[dim red]< WARNING: Connection stability at 78% >[/dim red]")
        
        # Get user choice with enhanced styling
        choice = Prompt.ask(
            f"\n[bold {color}]> Select data fragment[/bold {color}]", 
            choices=[str(i) for i in range(len(entries) + 1)]
        )
        
        if choice == "0":
            # Animation when exiting
            animations.glitch_text("Returning to main index...", console, glitch_chars="⌐░▒▓")
            return
        
        # Show loading animation when selecting an entry
        animations.loading_bar(
            console, 
            length=25, 
            message=f"Accessing data fragment {choice}", 
            style=f"bold {color}"
        )
        
        # Display entry
        entry_id = entries[int(choice) - 1]["id"]
        display_entry(console, codex, entry_id)

def display_entry(console, codex, entry_id):
    """
    Display a single codex entry
    
    Args:
        console: Console for output
        codex: Codex instance
        entry_id: ID of the entry to display
    """
    entry = codex.get_entry(entry_id)
    
    if not entry:
        return
    
    # Import necessary components for styling
    from rich.style import Style
    from rich.box import DOUBLE_EDGE
    
    # Display a load animation
    if entry["category"] == "technology":
        animations.code_decryption("DECODING TECHNICAL SPECIFICATIONS...", console)
    elif entry["category"] == "factions":
        animations.neural_interface(console, message="FACTION DATABASE ACCESSED", duration=1.0)
    elif entry["category"] == "events":
        animations.heartbeat_monitor(console, heartbeats=3, bpm=120)
    else:
        animations.digital_rain(console, duration=0.7, density=0.1)
    
    while True:
        console.clear()
        
        # Get category-specific color for consistent theming
        category_data = CATEGORIES[entry["category"]]
        category_colors = {
            "world": f"{COLORS['neon_blue']}",
            "factions": f"{COLORS['neon_pink']}",
            "technology": f"{COLORS['matrix_green']}",
            "locations": f"{COLORS['neon_cyan']}",
            "characters": f"{COLORS['neon_purple']}",
            "events": f"{COLORS['neon_orange']}"
        }
        color = category_colors.get(entry["category"], "cyan")
        
        # Create cyberpunk styled header
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        header_panel = Panel(
            f"[bold {color}]DATA ENTRY: {entry['title']}[/bold {color}]\n"
            f"[dim {color}]Source: {category_data['icon']} {category_data['name']} Archives • Entry #{hash(entry_id) % 10000:04d}[/dim {color}]",
            border_style=color,
            subtitle=f"[dim]Neural Link Active • {timestamp} • Connection Stable[/dim]",
            box=DOUBLE_EDGE
        )
        console.print(header_panel)
        
        # Display entry image if available with enhanced styling
        if entry.get("image"):
            art = assets.get_ascii_art(entry["image"])
            if art:
                art_panel = Panel(
                    art, 
                    border_style=color,
                    title=f"[dim {color}]Visual Reference[/dim {color}]",
                    subtitle=f"[dim {color}]Data Visualization #{random.randint(1000, 9999)}[/dim {color}]",
                    box=DOUBLE_EDGE
                )
                console.print(art_panel)
        
        # Add cyberpunk flair before content
        console.print(f"[dim {color}]{'═' * 50}[/dim {color}]")
        console.print(f"[{color}]DATA STREAM BEGINS[/{color}]\n")
        
        # Display entry content with appropriate animation effects
        if animations.get_animation_delay() > 0:
            # Choose animation effect based on entry category and content - more varied now
            
            # Technology entries
            if entry["category"] == "technology":
                if "neural" in entry_id or "brain" in entry_id:
                    animations.hologram_effect(entry["content"], console, style=Style(color="#00FFFF"))
                elif "weapon" in entry_id or "combat" in entry_id:
                    animations.data_corruption(entry["content"], console, corruption_level=0.1)
                else:
                    animations.code_decryption(entry["content"], console)
            
            # Faction entries
            elif entry["category"] == "factions":
                if any(term in entry_id.lower() for term in ["secret", "shadow", "criminal", "unknown"]):
                    animations.data_corruption(entry["content"], console, corruption_level=0.2)
                elif "corp" in entry_id:
                    animations.typing_effect(entry["content"], console, style=Style(color="#0088FF"))
                else:
                    animations.data_stream(entry["content"], console)
            
            # Location entries
            elif entry["category"] == "locations":
                if any(term in entry_id.lower() for term in ["cyber", "net", "virtual", "digital"]):
                    animations.digital_rain(console, duration=0.8, density=0.2, chars="01")
                    animations.typing_effect(entry["content"], console)
                elif "district" in entry_id:
                    animations.cyber_scan(entry["content"], console, style=Style(color="#00FFAA"))
                else:
                    animations.typing_effect(entry["content"], console)
            
            # Event entries
            elif entry["category"] == "events":
                if any(term in entry_id.lower() for term in ["war", "massacre", "disaster", "conflict"]):
                    animations.glitch_text(entry["content"], console, glitch_chars="!@#$%^*<>?_-+=~")
                else:
                    animations.typing_effect(entry["content"], console)
            
            # Character entries
            elif entry["category"] == "characters":
                animations.code_decryption(entry["content"], console)
            
            # Default to typing effect for standard entries
            else:
                animations.typing_effect(entry["content"], console)
        else:
            # Use markdown rendering for non-animated text
            console.print(Markdown(entry["content"]))
        
        # Add closing flair
        console.print(f"\n[{color}]DATA STREAM ENDS[/{color}]")
        console.print(f"[dim {color}]{'═' * 50}[/dim {color}]")
        
        # Display related entries if any are discovered
        related = entry.get("related_entries", [])
        discovered_related = [rel for rel in related if codex.is_discovered(rel) and rel in codex.entries]
        
        if discovered_related:
            console.print(f"\n[bold {color}]LINKED DATA NODES:[/bold {color}]")
            
            # Create a stylish table for related entries
            related_table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
            related_table.add_column("Index", style="dim cyan", width=3)
            related_table.add_column("Title", style="white")
            related_table.add_column("Category", style="dim", width=10)
            
            for i, rel_id in enumerate(discovered_related, 1):
                rel_entry = codex.entries[rel_id]
                rel_category = CATEGORIES[rel_entry["category"]]["icon"]
                related_table.add_row(
                    f"[{i}]", 
                    rel_entry["title"],
                    rel_category
                )
            
            console.print(related_table)
        
        # Occasionally display a system message for atmosphere
        if random.random() < 0.2:  # 20% chance
            status_messages = [
                "[dim]System integrity nominal[/dim]",
                "[dim yellow]Minor data corruption detected[/dim yellow]",
                "[dim green]Neural connection optimal[/dim green]",
                "[dim]Memory cache utilization: 64%[/dim]",
                "[dim blue]Link stability: 96.7%[/dim blue]"
            ]
            console.print(f"\n{random.choice(status_messages)}")
        
        # Navigation options with better styling
        console.print(f"\n[dim {color}]{'─' * 50}[/dim {color}]")
        console.print(f"[0] [dim {color}]Return to data index[/dim {color}]")
        
        if discovered_related:
            console.print(f"[r] [dim {color}]Access linked data node[/dim {color}]")
        
        # Get user choice with enhanced styling
        choices = ["0"]
        if discovered_related:
            choices.append("r")
            
        choice = Prompt.ask(f"\n[bold {color}]> Select action[/bold {color}]", choices=choices)
        
        if choice == "0":
            # Exit animation
            animations.glitch_text("Disconnecting from data node...", console, glitch_chars="░▒▓█")
            return
        elif choice == "r":
            # Create a more visually styled submenu for related entries
            console.print(f"\n[bold {color}]SELECT LINKED DATA NODE:[/bold {color}]")
            for i, rel_id in enumerate(discovered_related, 1):
                rel_entry = codex.entries[rel_id]
                console.print(f"[{i}] {rel_entry['title']}")
            console.print(f"[0] [dim]Cancel[/dim]")
            
            # Display loading animation when making selection
            rel_choice = Prompt.ask(
                f"[bold {color}]> Enter selection[/bold {color}]", 
                choices=[str(i) for i in range(len(discovered_related) + 1)]
            )
            
            if rel_choice == "0":
                continue
            
            # Show transition effect when navigating to a related entry
            animations.loading_bar(console, length=20, message="Accessing linked data node", style=f"bold {color}")
                
            rel_id = discovered_related[int(rel_choice) - 1]
            display_entry(console, codex, rel_id)

def initialize_codex_data():
    """Initialize the codex with default entries if the file doesn't exist"""
    codex = Codex()
    
    # Only initialize if the codex is empty
    if len(codex.entries) > 0:
        return codex
    
    # World entries
    codex.add_entry(
        "neo_shanghai",
        "world",
        "Neo Shanghai",
        """
## Neo Shanghai

The sprawling megalopolis of Neo Shanghai arose from the ashes of climate catastrophe and economic collapse in the mid-21st century. As coastal flooding ravaged the original Shanghai, corporations funded the rapid construction of a new city built atop massive stilts and floating platforms.

Today, Neo Shanghai stands as a testament to humanity's resilience and corporate greed. The city stretches across what was once the East China Sea, a glittering expanse of neon and steel that never sleeps. Its iconic profile is dominated by the massive arcology towers of the Corporate District, which rise like monoliths above the sprawling urban landscape below.

The city operates on multiple levels - from the luxurious upper sectors where the corporate elite reside, to the mid-levels of commerce and entertainment, down to the perpetually dark and rain-soaked streets of the lower districts where most citizens struggle to survive.

Despite its technological wonders, Neo Shanghai is a city of stark contrasts and brutal inequality. Corporate security forces maintain order in the upper and mid-levels, while the lower reaches are largely controlled by various criminal organizations and gangs.
        """,
        related_entries=["corporate_district", "neon_district", "blackout_zone", "the_float"],
        image="CITY_SKYLINE"
    )
    
    codex.add_entry(
        "corporate_takeover",
        "world",
        "The Corporate Takeover",
        """
## The Corporate Takeover

In the aftermath of the Collapse of 2042, traditional governments found themselves overwhelmed by cascading crises: climate disasters, mass migrations, resource shortages, and economic free-fall. It was in this vacuum of power that the megacorporations made their move.

Led by Zheng Dynamics, Arasaka, and MiliTech, corporations began offering privatized solutions to desperate populations. They promised security, stability, and technological solutions to humanity's most pressing problems. In exchange, they demanded unprecedented freedom from regulation and oversight.

By 2055, the transition was complete in most urban centers. Former government buildings stood vacant or repurposed as corporate headquarters. Police departments were replaced by private security firms. Public services were fully privatized, available only to those who could afford them.

Neo Shanghai became the model for this new world order - the first major city to formally transition to corporate rule under the so-called "Shanghai Compact." This agreement, signed by the 12 largest corporations operating in the region, established the Corporate Council as the city's governing body.

Today, citizenship in Neo Shanghai is tied directly to corporate affiliation. Those without corporate sponsorship exist in a legal gray area, forced to survive in the margins of society.
        """,
        related_entries=["corporate_council", "zheng_dynamics", "arasaka"]
    )
    
    codex.add_entry(
        "digital_pandemic",
        "world",
        "Digital Pandemic of 2064",
        """
## Digital Pandemic of 2064

One of the most devastating global events of the mid-21st century, the Digital Pandemic began as a seemingly minor glitch in neural interface systems across major corporate networks. What at first appeared to be isolated incidents of data corruption rapidly spread through interconnected networks, proving resistant to standard quarantine protocols.

Within 72 hours, an estimated 15% of all neural implant users worldwide reported symptoms ranging from sensory hallucinations to complete cognitive dysfunction. The pandemic's unusual vectors—spreading through both network connections and direct neural interface contact—left cybersecurity experts baffled.

Official casualty counts remain disputed, but conservative estimates suggest over 200,000 people suffered permanent neural damage, with at least 30,000 deaths from various causes including suicide, brain hemorrhage, and "autopilot accidents" where afflicted individuals continued functioning without higher cognitive awareness.

In Neo Shanghai, the outbreak hit particularly hard due to the city's high concentration of neural interface users. The Blackout Zone remains a lasting testament to the pandemic's impact—an entire district abandoned when its inhabitants either perished or fled during the three-week crisis.

Though the pandemic was officially declared contained after corporate forces deployed an aggressive countermeasure that severed all network connections to affected regions, conspiracy theories persist regarding its origin, ranging from terrorist cyberattacks to corporate warfare gone wrong.

Certain strains of the code pattern responsible for the pandemic reportedly remain dormant in isolated systems, with black market netrunners occasionally claiming to possess "weaponized samples" of what they call "the Mindkiller virus."
        """,
        related_entries=["blackout_zone", "neural_interfaces", "cyber_psychosis", "netrunning"],
        image="VIRUS_PATTERN"
    )
    
    # Factions entries
    codex.add_entry(
        "zheng_dynamics",
        "factions",
        "Zheng Dynamics",
        """
## Zheng Dynamics

Founded in 2031 by Dr. Elizabeth Zheng, Zheng Dynamics began as a pioneering medical cybernetics company before expanding into neural interfaces, AI research, and military applications. Now headquartered in the imposing Diamond Tower of Neo Shanghai's Corporate District, it stands as one of the most powerful corporations in the world.

Zheng Dynamics is known for its cutting-edge neural implant technology, particularly the "NeoLink" series that revolutionized human-computer interfaces. The corporation maintains a sleek, clean public image focused on "enhancing human potential," though rumors persist about dangerous experimental programs and unethical testing practices.

The corporation is currently led by CEO Victor Zheng, grandson of the founder, who has pushed aggressive expansion into new markets and technologies. Under his leadership, Zheng Dynamics has developed a particularly strong presence in the fields of consciousness digitization and synthetic intelligence.

Employees of Zheng Dynamics are easily identified by their distinctive blue and silver corporate uniforms and implants. Most feature the company's logo - a stylized "ZD" surrounded by a hexagonal pattern - embedded somewhere on their person, either as a dermal implant or incorporated into their cybernetics.

The corporation maintains its own private security force, the "Zheng Guardians," who operate with near-impunity throughout Neo Shanghai.
        """,
        related_entries=["corporate_council", "neo_shanghai", "corporate_district"],
        image="CORPORATE_LOGO"
    )
    
    codex.add_entry(
        "steel_dragons",
        "factions",
        "Steel Dragons",
        """
## Steel Dragons

Among Neo Shanghai's most feared street gangs, the Steel Dragons control significant territory in the Neon District and parts of the Blackout Zone. Founded by former military cybernetic specialist Jin "Steelclaw" Lau, the gang is known for its members' extensive cybernetic modifications and ruthless enforcement of territory.

Steel Dragons members undergo mandatory cybernetic enhancement upon joining, with status within the organization often tied to the extent and quality of one's implants. The gang's inner circle, known as the "Titanium Core," have replaced upwards of 80% of their original biological components.

The gang generates revenue through protection rackets, black market cybernetics, and the sale of the designer combat drug "ChromeRage" - a stimulant specifically designed to enhance the performance of cybernetic implants at the cost of severe long-term neural damage.

Steel Dragons territory is marked by graffiti tags showing a stylized dragon with metallic scales, often painted in reflective materials that shimmer under neon lights. Members typically display the gang's symbol as a holographic tattoo visible through transparent cybernetic components.

Despite their fearsome reputation, the Steel Dragons maintain a complex relationship with residents of their territory, sometimes providing protection and services that the Corporate Council fails to offer to lower-income areas.
        """,
        related_entries=["neon_district", "blackout_zone", "street_samurai"],
        image="GANG_SYMBOL"
    )
    
    # Technology entries
    codex.add_entry(
        "neural_interfaces",
        "technology",
        "Neural Interfaces",
        """
## Neural Interfaces

Neural interface technology represents one of the most significant technological leaps of the 21st century. These devices establish direct communication pathways between the human nervous system and external technology, effectively allowing the mind to control machines and perceive digital information directly.

The most common consumer-grade neural interfaces are:

- **Neural Ports**: Physical connection points typically installed at the base of the skull or behind the ear. These provide high-bandwidth, secure connections but require physical cables for data transfer.

- **Wireless Neural Links**: Subcutaneous implants that transmit data wirelessly. More convenient but more vulnerable to hacking and interference.

- **Full Neural Integration Systems**: Comprehensive implants that interface with multiple regions of the brain, allowing more complex interactions and enhanced processing. Primarily used by netrunners and specialized professionals.

Premium neural interfaces from companies like Zheng Dynamics include features such as:

- Emotion filtering
- Memory enhancement
- Dream recording
- Subconscious processing for problem-solving during sleep
- Augmented sensory perception

While neural interfaces offer unprecedented capabilities, they come with significant risks, including potential neural damage, hacking vulnerabilities, and the poorly understood condition known as "Dissociative Neural Syndrome" that can occur when users spend too much time connected to digital environments.
        """,
        related_entries=["cybernetic_implants", "netrunning", "brain_dance"],
        image="NEURAL_IMPLANT"
    )
    
    codex.add_entry(
        "cybernetic_implants",
        "technology",
        "Cybernetic Implants",
        """
## Cybernetic Implants

Cybernetic enhancement technology has progressed dramatically since its military origins in the 2030s. Modern implants range from subtle performance enhancers to radical body modifications that blur the line between human and machine.

Common categories of cybernetic implants include:

### Sensory Systems
- **Optical Implants**: Enhanced vision, including zoom capabilities, different visual spectrums, recording functions, and augmented reality overlays.
- **Auditory Enhancers**: Improved hearing range, audio filtering, recording capabilities, and translation software.
- **Neural Sensory Package**: Direct sensory feeds to the brain, sometimes including senses beyond the standard human range.

### Physical Enhancements
- **Subdermal Armor**: Reinforced skin providing protection against physical trauma.
- **Muscle Grafts**: Synthetic muscle tissue offering enhanced strength and reflexes.
- **Skeletal Reinforcement**: Carbon-fiber bone lacing or full skeletal replacement for durability and strength.
- **Internal Air Filters**: Protection against toxins and pollutants.

### Limb Prosthetics
- **Basic Replacements**: Functional prosthetics with limited enhancement.
- **Military-Grade**: Combat-optimized limbs with integrated weapons systems.
- **Specialized Models**: Task-specific designs for industrial work, athletics, or artistic pursuits.

The quality of cybernetics varies dramatically based on price point, from budget "chrome" that requires regular maintenance and can cause chronic pain, to premium implants that often perform better than their biological counterparts and include self-diagnostic and repair systems.

Most cybernetic systems require immunosuppressive drugs to prevent rejection, creating a dependency that manufacturers exploit through subscription-based medication plans.
        """,
        related_entries=["neural_interfaces", "street_samurai", "cyber_psychosis"],
        image="CYBORG_ARM"
    )
    
    # Locations entries
    codex.add_entry(
        "corporate_district",
        "locations",
        "Corporate District",
        """
## Corporate District

The gleaming heart of Neo Shanghai, the Corporate District rises above the rest of the city both literally and figuratively. Built primarily on the highest elevation platforms, the district remains above the frequent floods and perpetual smog that plague the lower levels.

Dominated by massive arcology towers that serve as self-contained corporate ecosystems, the district features:

- **The Diamond Tower**: Headquarters of Zheng Dynamics, a 200-story structure of crystalline design that reflects and refracts light in mesmerizing patterns.

- **Arasaka Compound**: A heavily fortified complex surrounding the black monolith of Arasaka Tower, featuring traditional Japanese architectural elements contrasted with cutting-edge technology.

- **Emerald Boulevard**: The main thoroughfare lined with luxury boutiques, exclusive restaurants, and high-end service providers catering to executives and the corporate elite.

- **Sky Gardens**: Carefully maintained green spaces on elevated platforms connecting the major towers, providing rare access to plants and open air, strictly reserved for higher-tier corporate employees.

- **Corporate Council Chambers**: The central meeting facility where representatives of the twelve ruling corporations gather to deliberate on city governance.

Access to the Corporate District is strictly controlled through layered security checkpoints, with different zones requiring progressively higher clearance levels. Most citizens of Neo Shanghai will never set foot in this district, viewing it only from a distance as a glittering symbol of wealth and power high above their everyday struggles.

The district employs its own private security forces, supplemented by advanced automated defense systems, making it virtually impenetrable without proper authorization.
        """,
        related_entries=["zheng_dynamics", "arasaka", "corporate_council", "neo_shanghai"],
        image="CORPORATE_DISTRICT"
    )
    
    codex.add_entry(
        "neon_district",
        "locations",
        "Neon District",
        """
## Neon District

The pulsing entertainment heart of Neo Shanghai, the Neon District never truly sleeps. Located primarily on the mid-level platforms, it's a riot of holographic advertisements, vibrant street markets, and endless entertainment venues.

Key features of the district include:

- **Luminous Strip**: The main thoroughfare, stretching five kilometers through the district's center, lined with clubs, bars, restaurants, and shopping arcades. Famous for its overhead canopy of intersecting holographic advertisements creating a perpetual artificial daylight.

- **Memory Palace**: The largest Brain Dance entertainment complex in Asia, offering experiences ranging from legal adventure simulations to black-market sensory recordings of questionable origin.

- **Fortune Market**: A sprawling open-air market where anything can be bought for the right price, from street food to bootleg cybernetics. Known for the distinctive red lanterns that illuminate its maze-like passages.

- **The Circuit**: A cluster of underground clubs centered around the electronic music scene, where DJs with neural-link instruments create immersive sound experiences.

- **Little Tokyo**: A sub-district featuring Japanese-inspired architecture, specializing in imported entertainment and technology from the Japanese Corporate Zone.

The Neon District serves as a mixing ground where corporate employees, mid-level workers, and even those from the lower districts come to seek entertainment and escape. Security is present but less oppressive than in the Corporate District, with different establishments maintaining their own protection forces.

Beneath the glittering surface of entertainment, the district hosts a thriving black market economy. Many establishments serve as fronts for less legal operations, from cybernetic chop shops to data smuggling operations.
        """,
        related_entries=["brain_dance", "steel_dragons", "neo_shanghai"],
        image="NEON_DISTRICT"
    )
    
    codex.add_entry(
        "blackout_zone",
        "locations",
        "Blackout Zone",
        """
## Blackout Zone

The most notorious district in Neo Shanghai, the Blackout Zone stands as a haunting memorial to the Digital Pandemic of 2064. Once a thriving middle-class residential sector called New Pudong, it was abandoned during the crisis when nearly 70% of its neural interface-equipped residents were affected by the spreading digital contagion.

Corporate emergency protocols implemented a complete network and power isolation of the district, cutting it off from the rest of the city. When the quarantine was finally lifted three weeks later, thousands were dead, and thousands more had fled, leaving behind a ghost town of shuttered apartments and businesses.

Today, the Blackout Zone exists in a perpetual twilight state. Official electricity and data networks were never fully restored, leading to its name. Electricity comes from a patchwork of makeshift generators and illegally tapped power lines, creating an unreliable grid that frequently plunges entire blocks into darkness.

Despite—or perhaps because of—its isolation, the Blackout Zone has become home to those seeking to escape corporate surveillance or authority. Various factions control different territories within the district:

- **The Forgotten**: Original residents who refused to leave, many suffering from lingering neural damage from the pandemic. They've formed tight-knit communities and are generally hostile to outsiders.

- **The Disconnected**: A quasi-religious community that rejects neural interfaces and most modern technology, seeing the Blackout Zone as a punishment for humanity's over-reliance on digital systems.

- **Ghost Market**: The largest black market in Neo Shanghai, operating from the ruins of what was once the New Pudong Commercial Center. Specializes in selling illegal technology, weapons, and stolen corporate data.

The district remains officially abandoned on corporate records, with no law enforcement presence. Rumors persist that the original pandemic code still lurks in isolated networks throughout the zone, with some claiming that certain areas experience "echo events" where equipment spontaneously manifests pandemic-like symptoms.
        """,
        related_entries=["digital_pandemic", "neo_shanghai", "steel_dragons"],
        image="DARK_RUINS"
    )

    # Events entries
    codex.add_entry(
        "neo_shanghai_founding",
        "events",
        "Founding of Neo Shanghai",
        """
## Founding of Neo Shanghai (2047-2053)

After the Great Coastal Flooding of 2045 devastated the original Shanghai and displaced over 20 million people, a consortium of Asian and Western corporations proposed an ambitious solution: a new city built on massive oceanic platforms and stilts over the submerged ruins.

Construction began in 2047 under the "Phoenix Rising" initiative, with Zheng Dynamics, Arasaka, and five other corporations providing the majority of funding and technological expertise. Using automated construction drones, prefabricated materials, and an army of desperate workers from the refugee camps, the first platforms were completed in record time.

The Corporate District was established first, housing the headquarters of the founding corporations and their elite employees. As construction continued outward in concentric rings, social stratification became physically manifest in the city's architecture - the wealthy at the elevated center, the middle class in the mid-level rings, and the working poor in the outer platforms closer to the water level.

By 2051, as governments worldwide continued to collapse under the weight of climate catastrophes and economic crises, the corporate consortium formalized their control by establishing the Shanghai Compact, effectively declaring Neo Shanghai an independent corporate city-state.

The city was officially inaugurated on April 10, 2053, when the original Shanghai was formally abandoned and all remaining government functions were transferred to the corporate-run Neo Shanghai Administrative Council. This date is now celebrated as "Ascension Day" in official corporate calendars.

What began as an emergency response to disaster quickly became the template for a new world order, as other coastal megacities followed Neo Shanghai's model of corporate-led reconstruction and governance in the following decades.
        """,
        related_entries=["neo_shanghai", "corporate_takeover", "zheng_dynamics"],
        image="CITY_CONSTRUCTION"
    )
    
    codex.add_entry(
        "liberty_day_massacre",
        "events",
        "Liberty Day Massacre",
        """
## Liberty Day Massacre (November 12, 2062)

What began as the largest anti-corporate demonstration in Neo Shanghai's history ended in bloodshed and controversy that continues to haunt the city. On November 12, 2062, approximately 50,000 protesters gathered in Unity Plaza in the Commerce District to demand democratic representation, basic income guarantees, and regulation of corporate power.

The protest—organized by the "Free Citizens Movement"—coincided with the old American holiday of Veterans Day, which the organizers rebranded as "Liberty Day" to symbolize their struggle for freedom from corporate control. For six hours, the demonstration remained peaceful, with speeches, music, and organized marches.

The situation deteriorated when a small group of protesters breached the security perimeter around the Corporate Council's Commerce District offices. Within minutes, private security forces from multiple corporations responded with what they termed "crowd control measures" but what witnesses described as "indiscriminate violence."

Official reports acknowledge 76 casualties, though independent investigations suggest the true death toll may exceed 200. Thousands more were injured or arrested, with many disappearing into corporate detention facilities.

The aftermath saw sweeping new security measures implemented throughout the city and the official banning of the Free Citizens Movement as a "terrorist organization." Corporate media portrayed the incident as a necessary response to a violent insurrection, releasing heavily edited footage showing protesters attacking security personnel.

Alternative accounts and unedited footage continue to circulate on the darknet, showing security forces firing into crowds of unarmed protesters. A memorial known as the "Liberty Wall"—an unofficial collection of names and photos of the dead—is maintained in the Blackout Zone, regularly removed by corporate security and just as regularly restored by local residents.

Today, November 12 remains a tense date in Neo Shanghai, with increased security presence and occasional underground memorial gatherings.
        """,
        related_entries=["corporate_takeover", "neo_shanghai", "blackout_zone"],
        image="PROTEST_SCENE"
    )
    
    # Characters entries
    codex.add_entry(
        "shade",
        "characters",
        "Shade",
        """
## Shade (Born 2044)

Known only by the handle "Shade," this infamous netrunner has been a ghost in Neo Shanghai's systems for nearly two decades. Neither corporate security nor street gangs claim to know Shade's true identity, gender, or appearance—each encounter with Shade is mediated through different proxies, avatars, or hired intermediaries.

What is known about Shade is their seemingly supernatural ability to bypass any security system in the city. According to underground legend, Shade was one of the early victims of the Digital Pandemic, but instead of dying or suffering neural damage like most victims, they somehow integrated the evolving code into their neural interface, fundamentally changing their relationship with cyberspace.

Shade is credited with several high-profile security breaches, including:

- The 2065 "Truth Bomb" that revealed corruption in Zheng Dynamics' neural interface safety testing
- The 2067 Arasaka Defense Systems hack that exposed illegal weapons sales to banned conflict zones
- The 2069 "Liberation Day" when every debt record in the Corporate District's central banking network was scrambled beyond recovery

Corporate authorities classify Shade as a terrorist with a 2 million credit bounty. To those in the Blackout Zone and lower levels, they are a mythic hero. Rumors persist that Shade maintains a physical hideout somewhere deep in the Blackout Zone, surrounded by improvised security systems and an army of reprogrammed combat drones.

Behavioral analysis suggests Shade isn't motivated by financial gain, but rather by an ideological opposition to corporate power—or perhaps more disturbingly, by the sheer challenge of defeating increasingly sophisticated security systems.
        """,
        related_entries=["digital_pandemic", "blackout_zone", "zheng_dynamics"],
        image="CYBERSPACE"
    )
    
    codex.add_entry(
        "dr_elizabeth_zheng",
        "characters",
        "Dr. Elizabeth Zheng",
        """
## Dr. Elizabeth Zheng (2001-2076)

The founder of Zheng Dynamics and pioneer of modern neural interface technology, Dr. Elizabeth Zheng transformed human-machine interaction and laid the groundwork for today's cybernetic society.

Born to Chinese-American parents in San Francisco, Zheng displayed extraordinary talent in neuroscience and computer engineering from an early age. After earning dual PhDs from MIT by age 24, she worked briefly for the DARPA neural interface program before striking out on her own.

In 2031, she founded Zheng Dynamics, initially focusing on medical neural interfaces to help patients with neurological injuries. The company's breakthrough came in 2036 with the first-generation NeoLink system, which allowed direct neural control of prosthetics with unprecedented precision.

As her company grew, Zheng expanded research into increasingly controversial areas, including consciousness digitization and synthetic intelligence. Critics accused her of ethical violations, particularly regarding test subjects, but corporate protection and legal maneuvering kept her work progressing.

Known for her brilliant mind and uncompromising vision, Zheng was also notorious for her demanding management style and willingness to push ethical boundaries in the name of progress. Her personal motto, "Evolution by Design," captures her belief that humanity should take active control of its development through technology.

Though officially listed as deceased from natural causes in 2076, persistent rumors suggest her consciousness may have been successfully digitized as part of Project Immortality, her final and most secretive research initiative. Zheng Dynamics has neither confirmed nor denied these speculations.
        """,
        related_entries=["zheng_dynamics", "neural_interfaces", "victor_zheng"],
        image="SCIENTIST"
    )
    
    codex.add_entry(
        "raven",
        "characters",
        "Raven",
        """
## Raven

One of Neo Shanghai's most notorious and enigmatic netrunners, Raven has achieved an almost mythical status in the digital underground. Their true identity remains unknown despite considerable efforts by corporate security forces to unmask them.

Raven first appeared on the scene approximately seven years ago, when they breached Arasaka's supposedly impenetrable financial servers and redistributed over 300 million credits to random citizens in the lower districts. Since then, they have been responsible for numerous high-profile data leaks, security breaches, and digital sabotage operations targeting primarily corporate entities.

What makes Raven unique among netrunners is their distinctive digital signature - a swirling pattern of dark code that resembles wings unfurling. This signature, always left at the scene of their intrusions, has become a symbol of resistance against corporate control.

Tech analysts who have studied Raven's code work suggest they must possess extremely advanced, possibly experimental neural interface technology, allowing them to navigate the Net with unprecedented speed and adaptability. Some speculate they may be using technologies stolen from Zheng Dynamics' classified research divisions.

Sightings of Raven in the physical world are rare and unconfirmed, though most reports describe a figure in a black coat with glowing blue neural interface lines visible at the temples. Whether Raven is an individual or a collective operating under a single identity remains a matter of speculation.

For many in the lower districts, Raven represents hope against corporate oppression. For the corporations, they represent a dangerous terrorist and data thief with a 5 million credit bounty on their head.
        """,
        related_entries=["netrunning", "neural_interfaces", "blackout_zone"],
        image="NETRUNNER"
    )
    
    # Events entries
    codex.add_entry(
        "the_collapse",
        "events",
        "The Collapse",
        """
## The Collapse (2042-2046)

The defining catastrophe of the 21st century, the period known simply as "The Collapse" represented the convergence of multiple crises that fundamentally reshaped global society and power structures.

The cascading disasters began with the Financial Crash of 2042, triggered by the destabilization of critical AI-driven market systems. Within weeks, global markets lost over 70% of their value, wiping out savings, pensions, and government funds worldwide.

As economic systems failed, they exacerbated existing climate crises:

- Rising sea levels accelerated dramatically with the Antarctic Shelf Collapse in 2043
- Crop failures led to widespread famine across previously fertile regions
- Water wars erupted in areas already experiencing scarcity
- Mass migration from uninhabitable regions overwhelmed remaining stable nations

Traditional governments, already weakened by decades of declining public trust and growing corporate influence, proved incapable of mounting effective responses. Over 60% of world governments either collapsed entirely or devolved into authoritarian regimes desperately trying to maintain control.

Into this power vacuum stepped the megacorporations, which had insulated themselves from the worst effects of the crash through private currencies, resources, and security forces. They offered stability and solutions at the price of unprecedented control over society.

By 2046, when the immediate crises began to stabilize, the world had been fundamentally transformed. Nation-states remained as geographic concepts, but real power had shifted decisively to corporate entities whose wealth and technological advantages gave them effective control over what remained of civilization.
        """,
        related_entries=["corporate_takeover", "neo_shanghai", "climate_crisis"],
        image="CITY_RUINS"
    )
    
    # Discover a few initial entries for new games
    initial_discoveries = ["neo_shanghai", "corporate_district", "neon_district"]
    for entry_id in initial_discoveries:
        codex.discover_entry(entry_id)
    
    codex.save_data()
    return codex