"""
Codex Module - In-game encyclopedia of lore and world-building details
"""
import json
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.columns import Columns

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
    while True:
        console.clear()
        
        # Display codex header
        console.print(Panel("[bold cyan]CODEX: Neo Shanghai Encyclopedia[/bold cyan]"))
        
        # Display discovery statistics
        discovered, total = codex.get_discovery_count()
        console.print(f"Entries discovered: [cyan]{discovered}[/cyan]/[cyan]{total}[/cyan] ({(discovered/total*100) if total > 0 else 0:.1f}%)")
        
        # Get categories with discovered entries
        available_categories = codex.get_categories_with_discovered_entries()
        
        if not available_categories:
            console.print("[yellow]You haven't discovered any codex entries yet.[/yellow]")
            console.print("[yellow]Explore the world to unlock more knowledge.[/yellow]")
            console.print("\nPress Enter to return...")
            Prompt.ask("", default="")
            return
        
        # Display categories
        console.print("\n[bold]Available Categories:[/bold]")
        
        for i, category_id in enumerate(available_categories, 1):
            category_data = CATEGORIES[category_id]
            entry_count = len(codex.get_entries_by_category(category_id))
            
            console.print(f"{i}. {category_data['icon']} {category_data['name']} ({entry_count} entries)")
            console.print(f"   [dim]{category_data['description']}[/dim]")
        
        console.print("\n0. Return to Game")
        
        # Get user choice
        choice = Prompt.ask(
            "Select a category", 
            choices=[str(i) for i in range(len(available_categories) + 1)]
        )
        
        if choice == "0":
            return
        
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
    
    while True:
        console.clear()
        
        category_data = CATEGORIES[category_id]
        console.print(Panel(f"[bold cyan]CODEX: {category_data['icon']} {category_data['name']}[/bold cyan]"))
        console.print(f"[dim]{category_data['description']}[/dim]")
        
        if not entries:
            console.print("[yellow]No entries discovered in this category yet.[/yellow]")
        else:
            # Create a table of entries
            table = Table(show_header=False, expand=True)
            table.add_column("Index", style="cyan", width=3)
            table.add_column("Title", style="white")
            
            for i, entry in enumerate(entries, 1):
                table.add_row(str(i), entry["title"])
            
            console.print(table)
        
        console.print("\n0. Back to Categories")
        
        # Get user choice
        choices = [str(i) for i in range(len(entries) + 1)]
        choice = Prompt.ask("Select an entry", choices=choices)
        
        if choice == "0":
            return
        
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
    
    while True:
        console.clear()
        
        # Display entry title
        category_data = CATEGORIES[entry["category"]]
        console.print(Panel(f"[bold cyan]CODEX: {entry['title']}[/bold cyan]"))
        console.print(f"[dim]Category: {category_data['icon']} {category_data['name']}[/dim]\n")
        
        # Display entry image if available
        if entry.get("image"):
            art = assets.get_ascii_art(entry["image"])
            if art:
                console.print(Panel(art, border_style="cyan"))
        
        # Display entry content as markdown
        if animations.get_animation_delay() > 0:
            # Use typing effect for animated text
            animations.typing_effect(entry["content"], console)
        else:
            # Use markdown rendering for non-animated text
            console.print(Markdown(entry["content"]))
        
        # Display related entries if any are discovered
        related = entry.get("related_entries", [])
        discovered_related = [rel for rel in related if codex.is_discovered(rel) and rel in codex.entries]
        
        if discovered_related:
            console.print("\n[bold]Related Entries:[/bold]")
            
            for i, rel_id in enumerate(discovered_related, 1):
                rel_entry = codex.entries[rel_id]
                console.print(f"{i}. {rel_entry['title']}")
        
        # Navigation options
        console.print("\n0. Back to Entry List")
        
        if discovered_related:
            console.print("r. View a Related Entry")
        
        # Get user choice
        choices = ["0"]
        if discovered_related:
            choices.append("r")
            
        choice = Prompt.ask("Select an option", choices=choices)
        
        if choice == "0":
            return
        elif choice == "r":
            # Display submenu for related entries
            rel_choice = Prompt.ask(
                "Select a related entry", 
                choices=[str(i) for i in range(len(discovered_related) + 1)]
            )
            
            if rel_choice == "0":
                continue
                
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
    
    # Characters entries
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