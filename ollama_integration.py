"""
Ollama Integration Module - Handles dynamic content generation with local LLM
"""
import os
import json
import requests
from rich.console import Console

from config import OLLAMA_API_URL, OLLAMA_MODEL

class OllamaIntegration:
    """Integration with Ollama for dynamic story generation"""
    
    def __init__(self):
        """Initialize Ollama integration"""
        # Load settings from GAME_SETTINGS if available, fall back to config defaults
        try:
            from config import GAME_SETTINGS
            self.api_url = GAME_SETTINGS.get("ollama_api_url", OLLAMA_API_URL)
            self.model = GAME_SETTINGS.get("ollama_model", OLLAMA_MODEL)
            
            # Store token in instance for easy access (it's also in env var)
            self.token = GAME_SETTINGS.get("ollama_token", "")
        except:
            self.api_url = OLLAMA_API_URL
            self.model = OLLAMA_MODEL
            self.token = os.getenv("OLLAMA_TOKEN", "")
            
        self.console = Console()
    
    def _make_request(self, prompt, max_retries=3):
        """Make a request to the Ollama API"""
        # If the URL already contains "/api/generate", use it directly,
        # otherwise construct the full endpoint
        if self.api_url.endswith("/api/generate"):
            endpoint = self.api_url
        elif self.api_url.endswith("/api"):
            endpoint = f"{self.api_url}/generate"
        elif self.api_url.endswith("/api/"):
            # Handle trailing slash properly
            endpoint = f"{self.api_url}generate"
        else:
            # Ensure we have the /api path
            base_url = self.api_url
            if not base_url.endswith("/api"):
                if base_url.endswith("/"):
                    base_url += "api"
                else:
                    base_url += "/api"
            endpoint = f"{base_url}/generate"
            
        # Print the endpoint for debugging
        print(f"Making request to: {endpoint}")
        
        # Prepare the data payload
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        
        # Add API token if available (use the instance token)
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Try to make the request with retries
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, json=data, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Request failed with status code {response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"Retrying... (Attempt {attempt+1}/{max_retries})")
            except Exception as e:
                print(f"Error making request: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying... (Attempt {attempt+1}/{max_retries})")
        
        # If all retries fail
        return None
    
    def generate_story_node(self, node_id, player, choice_history=None):
        """Generate a dynamic story node based on the current game state and previous choices
        
        Args:
            node_id (str): The ID of the story node to generate
            player (Character): The player character object
            choice_history (ChoiceHistory, optional): The player's choice history
        """
        # Check if we should use Ollama
        from config import USE_OLLAMA
        
        if not USE_OLLAMA:
            # Skip Ollama integration if disabled
            return self._generate_fallback_node(node_id)
            
        # Check if Ollama is available
        if not self._check_availability():
            self.console.print("[bold red]Ollama is not available. Using fallback content.[/bold red]")
            return self._generate_fallback_node(node_id)
        
        # Create a prompt with the current game state and choice history
        prompt = self._create_story_prompt(node_id, player, choice_history)
        
        # Make the request to Ollama
        response = self._make_request(prompt)
        
        if not response:
            self.console.print("[bold red]Failed to generate story content. Using fallback.[/bold red]")
            return self._generate_fallback_node(node_id)
        
        # Extract the response text
        response_text = response.get("response", "")
        
        # Parse the response to extract the story node
        try:
            # Find json within the response text
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                node_json = response_text[start_idx:end_idx]
                node = json.loads(node_json)
                
                # Validate that the node has the minimal required fields
                if "text" in node and ("choices" in node or "type" in node):
                    return node
        except Exception as e:
            self.console.print(f"[bold red]Error parsing generated content: {str(e)}[/bold red]")
        
        # If parsing fails, use fallback
        return self._generate_fallback_node(node_id)
    
    def _check_availability(self):
        """Check if Ollama is available"""
        try:
            # If the URL ends with "/api" or "/api/", remove it for the tags endpoint
            base_url = self.api_url
            if base_url.endswith("/api"):
                base_url = base_url[:-4]
            elif base_url.endswith("/api/"):
                base_url = base_url[:-5]
                
            # Check availability
            
            # Get API token if available (use the instance token)
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                
            response = requests.get(f"{base_url}/api/tags", headers=headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama availability check failed: {str(e)}")
            return False
    
    def _create_story_prompt(self, node_id, player, choice_history=None):
        """Create a prompt for story generation based on current game state and choice history
        
        Args:
            node_id (str): The ID of the story node to generate
            player (Character): The player character object
            choice_history (ChoiceHistory, optional): The player's choice history
        """
        # Build the prompt piece by piece
        header = f"You are the storyteller for a cyberpunk text adventure game. The player has reached a story node with ID \"{node_id}\".\n\n"
        
        player_info = f"Player information:\n"
        player_info += f"- Name: {player.name}\n"
        player_info += f"- Class: {player.char_class}\n"
        player_info += f"- Level: {player.level}\n"
        player_info += f"- Stats: {json.dumps(player.stats)}\n"
        player_info += f"- Health: {player.health}/{player.max_health}\n"
        player_info += f"- Inventory: {json.dumps(player.inventory.get_all_items())}\n\n"
        
        # Add choice history if available
        history_section = ""
        if choice_history:
            # Get a narrative summary of recent choices
            narrative = choice_history.get_narrative_summary(limit=10)
            history_section = f"Recent Player History:\n{narrative}\n\n"
        
        # Instructions for response format
        instructions = "Based on this information, generate a story node in JSON format with the following structure:\n\n"
        instructions += "For a standard narrative node:\n"
        instructions += '{\n'
        instructions += '    "text": "Detailed and atmospheric description of the situation.",\n'
        instructions += '    "choices": [\n'
        instructions += '        {\n'
        instructions += '            "text": "Description of the first choice",\n'
        instructions += '            "next_node": "unique_id_for_next_node",\n'
        instructions += '            "requirements": {\n'
        instructions += '                "stats": {"stat_name": minimum_value},\n'
        instructions += '                "item": "required_item_name"\n'
        instructions += '            },\n'
        instructions += '            "consequences": {\n'
        instructions += '                "items_gained": {"item_name": quantity},\n'
        instructions += '                "items_lost": {"item_name": quantity},\n'
        instructions += '                "stats_change": {"stat_name": change_amount},\n'
        instructions += '                "health_change": change_amount,\n'
        instructions += '                "credits_change": change_amount\n'
        instructions += '            }\n'
        instructions += '        },\n'
        instructions += '        {\n'
        instructions += '            "text": "Description of the second choice",\n'
        instructions += '            "next_node": "another_unique_id"\n'
        instructions += '        }\n'
        instructions += '    ]\n'
        instructions += '}\n\n'
        
        instructions += 'OR for a combat node:\n'
        instructions += '{\n'
        instructions += '    "type": "combat",\n'
        instructions += '    "text": "Description of the combat situation",\n'
        instructions += '    "enemy": {\n'
        instructions += '        "name": "Enemy Name",\n'
        instructions += '        "health": health_value,\n'
        instructions += '        "damage": damage_value,\n'
        instructions += '        "defense": defense_value\n'
        instructions += '    },\n'
        instructions += '    "victory_node": "node_after_winning",\n'
        instructions += '    "escape_node": "node_after_escaping",\n'
        instructions += '    "rewards": {\n'
        instructions += '        "experience": amount,\n'
        instructions += '        "credits": amount,\n'
        instructions += '        "items": {\n'
        instructions += '            "item_name": quantity\n'
        instructions += '        }\n'
        instructions += '    }\n'
        instructions += '}\n\n'
        
        instructions += 'OR for a skill check node:\n'
        instructions += '{\n'
        instructions += '    "type": "skill_check",\n'
        instructions += '    "text": "Description of the situation requiring a skill check",\n'
        instructions += '    "skill": "skill_name",\n'
        instructions += '    "difficulty": difficulty_value,\n'
        instructions += '    "success_node": "node_after_success",\n'
        instructions += '    "failure_node": "node_after_failure",\n'
        instructions += '    "success_rewards": {\n'
        instructions += '        "experience": amount,\n'
        instructions += '        "items": {\n'
        instructions += '            "item_name": quantity\n'
        instructions += '        }\n'
        instructions += '    },\n'
        instructions += '    "failure_consequences": {\n'
        instructions += '        "health_loss": amount\n'
        instructions += '    }\n'
        instructions += '}\n\n'
        
        # Style and content guidance
        guidance = "Create a compelling and atmospheric cyberpunk scene that fits with a world where corporations control everything, "
        guidance += "technology and humanity have merged, and the divide between rich and poor is extreme. "
        guidance += "Include appropriate cyberpunk themes, terminology, and atmosphere.\n\n"
        guidance += "The response should be ONLY the JSON object, nothing else."
        
        # Combine all parts
        prompt = header + player_info + history_section + instructions + guidance
        
        return prompt
    
    def _generate_fallback_node(self, node_id):
        """Generate a fallback story node when Ollama is unavailable"""
        return {
            "title": "System Malfunction",
            "text": "Your neural interface flickers, displaying error messages across your vision. The data feed seems corrupted or jammed. As you try to make sense of your surroundings, the static clears briefly, giving you a few options to proceed.",
            "choices": [
                {
                    "text": "Try to reboot your neural systems",
                    "next_node": "street_entrance"
                },
                {
                    "text": "Look for a tech vendor who might help",
                    "next_node": "marketplace"
                },
                {
                    "text": "Push through despite the system errors",
                    "next_node": "neon_dragon_exterior",
                    "consequences": {
                        "health_change": -1
                    }
                }
            ]
        }
    
    def generate_codex_entry(self, entry_id, category, title, existing_entries=None):
        """Generate a dynamic codex entry based on entry ID, category, and title
        
        Args:
            entry_id (str): The ID of the entry to generate
            category (str): The category of the entry
            title (str): The title of the entry
            existing_entries (dict, optional): Dictionary of existing entries to provide context
            
        Returns:
            dict: A dictionary containing the generated codex entry
        """
        # Check if we should use Ollama
        from config import USE_OLLAMA
        
        if not USE_OLLAMA:
            # Skip Ollama integration if disabled
            return self._generate_fallback_codex_entry(entry_id, category, title)
            
        # Check if Ollama is available
        if not self._check_availability():
            self.console.print("[bold red]Ollama is not available. Using fallback content for codex entry.[/bold red]")
            return self._generate_fallback_codex_entry(entry_id, category, title)
        
        # Create a prompt for the codex entry
        prompt = self._create_codex_prompt(entry_id, category, title, existing_entries)
        
        # Make the request to Ollama
        response = self._make_request(prompt)
        
        if not response:
            self.console.print("[bold red]Failed to generate codex content. Using fallback.[/bold red]")
            return self._generate_fallback_codex_entry(entry_id, category, title)
        
        # Extract the response text
        response_text = response.get("response", "")
        
        # Parse the response to extract the codex entry
        try:
            # Find json within the response text
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                entry_json = response_text[start_idx:end_idx]
                entry = json.loads(entry_json)
                
                # Validate that the entry has the required fields
                if "content" in entry:
                    # Add any missing fields
                    entry.setdefault("category", category)
                    entry.setdefault("title", title)
                    entry.setdefault("related_entries", [])
                    entry.setdefault("image", None)
                    return entry
        except Exception as e:
            self.console.print(f"[bold red]Error parsing generated codex content: {str(e)}[/bold red]")
        
        # If parsing fails, use fallback
        return self._generate_fallback_codex_entry(entry_id, category, title)
    
    def _create_codex_prompt(self, entry_id, category, title, existing_entries=None):
        """Create a prompt for codex entry generation
        
        Args:
            entry_id (str): The ID of the entry to generate
            category (str): The category of the entry
            title (str): The title of the entry
            existing_entries (dict, optional): Dictionary of existing entries to provide context
        """
        # Dictionary mapping categories to descriptions and guidance
        category_info = {
            "world": {
                "description": "Information about the world of Neo Shanghai and its history",
                "guidance": "Focus on how climate change, corporate takeovers, and technological advancement shaped the city. Include geographical features, societal structure, governance, and key historical turning points. Describe the stratified urban architecture with ultra-wealthy living in sky-scraping arcologies while the underclass struggles in the perpetually dark, neon-lit streets below."
            },
            "factions": {
                "description": "Details about the major corporations, gangs, and other groups",
                "guidance": "Detail the faction's power structure, territory, specialization, notable members, rivals, and unique technologies or resources. Explain their origin story, current motives, and how they interact with other power players in Neo Shanghai. Include their reputation among different segments of society and any signature visual identifiers."
            },
            "technology": {
                "description": "Information about cybernetic implants, weapons, and other tech",
                "guidance": "Describe technical specifications, manufacturer, legality status, street price, and cultural impact. Detail any side effects, risks, or addiction potential. Explain how this technology altered society or created new subcultures. Include technical jargon that would appear in marketing or black market descriptions."
            },
            "locations": {
                "description": "Details about districts, landmarks, and important places",
                "guidance": "Paint a vivid picture of the atmosphere, architectural style, controlling factions, and social dynamics. Describe distinctive sights, sounds, smells, and the types of people found there. Detail security measures, unique features, hidden areas, and historical significance. Explain how this location connects to the broader city ecosystem."
            },
            "characters": {
                "description": "Background on key figures in the world",
                "guidance": "Develop a complex profile including appearance, cybernetic modifications, psychological traits, motivations, and connections to factions. Detail their rise to their current position, notable achievements, enemies, and allies. Include rumors about them that circulate in Neo Shanghai's streets."
            },
            "events": {
                "description": "Historical events that shaped the current world",
                "guidance": "Chronicle the causes, key players, timeline, immediate aftermath, and long-term consequences. Explain how various factions interpret or exploit this event today. Detail how this event changed power dynamics in Neo Shanghai or globally. Include primary sources like news excerpts or survivor accounts."
            }
        }
        
        # Build the prompt with category-specific guidance
        category_data = category_info.get(category, {"description": "General information", "guidance": "Provide detailed information"})
        
        # Core world context
        world_context = "Neo Shanghai is a sprawling cyberpunk megalopolis built after climate catastrophes and economic collapse in the mid-21st century. It features massive corporate arcologies, neon-lit streets shrouded in perpetual rain, ubiquitous technology alongside crushing poverty, and a society where human augmentation blurs the line between person and machine. The city operates on multiple physical and social levels, from the corporate elite in the heights to the struggling masses in the depths."
        
        header = f"You are writing content for a codex entry in a cyberpunk text adventure game set in Neo Shanghai. The entry has ID \"{entry_id}\", category \"{category}\" ({category_data['description']}), and title \"{title}\".\n\n"
        header += f"WORLD CONTEXT: {world_context}\n\n"
        header += f"SPECIFIC GUIDANCE FOR THIS ENTRY: {category_data['guidance']}\n\n"
        
        # Add context from existing entries if available
        context = ""
        if existing_entries and len(existing_entries) > 0:
            context = "EXISTING CODEX ENTRIES FOR CONTEXT:\n\n"
            # Include up to 3 related entries for context, prioritizing entries in the same category
            same_category_entries = {eid: entry for eid, entry in existing_entries.items() if entry.get('category') == category}
            other_entries = {eid: entry for eid, entry in existing_entries.items() if entry.get('category') != category}
            
            entries_to_use = list(same_category_entries.items())[:2] + list(other_entries.items())[:1]
            
            for eid, entry in entries_to_use:
                context += f"Entry: {entry.get('title', 'Unknown')}\n"
                context += f"Category: {entry.get('category', 'Unknown')}\n"
                context += f"Content: {entry.get('content', '')}\n\n"
        
        # Provide example for related entry naming conventions
        related_entries_examples = {
            "world": ["neo_shanghai", "corporate_takeover", "climate_crisis"],
            "factions": ["arasaka_corp", "street_samurai_guild", "netrunner_collective"],
            "technology": ["neural_interface", "combat_implants", "hacking_deck"],
            "locations": ["neon_district", "corporate_district", "underground_markets"],
            "characters": ["shadow_broker", "corporate_ceo", "street_doc"],
            "events": ["net_crash", "corporate_war", "water_riots"]
        }
        
        # Instructions for response format with better examples
        instructions = "CREATE A DETAILED CODEX ENTRY IN THIS JSON FORMAT:\n\n"
        instructions += "{\n"
        instructions += f'    "title": "{title}",\n'
        instructions += f'    "category": "{category}",\n'
        instructions += '    "content": "## Main Heading\\n\\nDetailed markdown content with **bold text** for emphasis and *italics* for technical terms or slang.\\n\\n### Subheading One\\n\\nMore detailed information with rich cyberpunk atmosphere.\\n\\n### Subheading Two\\n\\nAdditional details with historical context and connections to other elements of Neo Shanghai.",\n'
        instructions += f'    "related_entries": {str(related_entries_examples.get(category, ["example_entry_1", "example_entry_2"]))},\n'
        instructions += '    "image": null\n'
        instructions += "}\n\n"
        
        # Style and content guidance with better formatting examples
        guidance = "IMPORTANT STYLISTIC REQUIREMENTS:\n"
        guidance += "1. Use markdown formatting effectively with ## for main heading (title), ### for subheadings, **bold** for emphasis, and *italics* for technical terms or slang.\n"
        guidance += "2. Write in a technical yet atmospheric style that blends factual information with the gritty cyberpunk aesthetic.\n"
        guidance += "3. Include appropriate cyberpunk terminology and cultural references that fit Neo Shanghai's world.\n"
        guidance += "4. Content should be 300-500 words with 2-3 distinct sections under subheadings.\n"
        guidance += "5. For related_entries, use snake_case IDs that logically connect to this entry's topic.\n"
        guidance += "6. Do not use placeholders or meta-references to game mechanics.\n\n"
        guidance += "YOUR RESPONSE MUST BE ONLY THE VALID JSON OBJECT, NOTHING ELSE."
        
        # Combine all parts
        prompt = header + context + instructions + guidance
        
        return prompt
    
    def _generate_fallback_codex_entry(self, entry_id, category, title):
        """Generate a fallback codex entry when Ollama is unavailable
        
        Args:
            entry_id (str): The ID of the entry to generate
            category (str): The category of the entry
            title (str): The title of the entry
        """
        # Dictionary of category-specific fallback messages
        category_fallbacks = {
            "world": f"## {title}\n\n**NEURAL LINK ERROR: ARCHIVE CORRUPTED**\n\n*Your implant flickers with static as it attempts to access historical data on this subject.*\n\n### Connection Lost\n\nThe citywide data archives on this topic appear to have been corrupted or intentionally wiped. Multiple connection attempts have failed.\n\n### Recommended Actions\n* Visit a licensed data broker in the Neon District\n* Check black market data dealers in Neural Alley\n* Attempt connecting through a different uplink node\n\n**SYSTEM MESSAGE**: *Possible corporate data restriction detected. Caution advised when pursuing this information.*",
            
            "factions": f"## {title}\n\n**SECURITY ALERT: ACCESS DENIED**\n\n*Your neural interface displays a pulsing red warning as you attempt to access this restricted file.*\n\n### Security Protocol Active\n\nInformation on this faction has been classified under Neo Shanghai Security Directive 377-D. Unauthorized access attempts have been logged.\n\n### Intelligence Status\n* Known surveillance: **HIGH**\n* Encryption level: **MILITARY GRADE**\n* Last data update: **UNAVAILABLE**\n\n**SYSTEM WARNING**: *Multiple retrieval attempts may trigger autonomous security countermeasures. Corporate enforcers have been dispatched to similar intrusion attempts.*",
            
            "technology": f"## {title}\n\n**TECHNICAL DOCUMENTATION UNAVAILABLE**\n\n*Your interface displays scrolling error codes as it attempts to access technical specifications.*\n\n### Retrieval Failure\n\nSchematic data for this technology appears to be protected by proprietary encryption. Standard NetLink access has been denied.\n\n### Technical Analysis\n* Encryption: **Quantum-resistant**\n* Access level required: **Corporate Executive**\n* Known workarounds: **REDACTED**\n\n**HINT**: *Street vendors in the Lower Markets sometimes sell bootleg technical documentation. Reliability not guaranteed.*",
            
            "locations": f"## {title}\n\n**GEOSPATIAL DATA CORRUPTED**\n\n*Your mapping interface glitches, displaying fragmented location data and scattered coordinates.*\n\n### Area Access Status: UNKNOWN\n\nDetailed information about this location cannot be retrieved through standard channels. Map overlay functionality limited.\n\n### Navigation Advisory\n* Danger assessment: **CALCULATING...**\n* Faction control: **DATA UNAVAILABLE**\n* Public access: **UNDETERMINED**\n\n**LOCAL NETWORK MESSAGE**: *This area has been reported as contested territory. Physical reconnaissance recommended before visiting.*",
            
            "characters": f"## {title}\n\n**IDENTITY SCAN BLOCKED**\n\n*Your facial recognition software returns multiple contradictory matches as it attempts to analyze this individual.*\n\n### Biometric Analysis Failure\n\nThis person appears to be using advanced identity masking technology or has paid to have their records expunged from public databases.\n\n### Known Associates\n* **DATA PURGED**\n* **ACCESS DENIED**\n* **FILE CORRUPTED**\n\n**FIXER ADVISORY**: *Information on this individual might be available through black market channels, but expect to pay premium rates.*",
            
            "events": f"## {title}\n\n**HISTORICAL DATA QUARANTINED**\n\n*Your search for information triggers an automated censorship response.*\n\n### Media Control Notice\n\nReferences to this event have been restricted under the Corporate Truth in Information Act. Authorized narrative access requires special clearance.\n\n### Available Data\n* Official records: **SANITIZED**\n* Witness accounts: **SUPPRESSED**\n* Video evidence: **UNAVAILABLE**\n\n**UNDERGROUND NOTICE**: *Alternative accounts of this event circulate on physical media in the undercity markets. Corporate enforcement teams actively confiscate these materials.*"
        }
        
        # Get the appropriate fallback message or use a generic one if category not found
        fallback_content = category_fallbacks.get(category, f"## {title}\n\n**NEURAL INTERFACE ERROR**\n\nYour implant has failed to retrieve information about this subject. Connection to central database interrupted or data has been restricted.\n\n### Troubleshooting\n\nTry reconnecting to a data terminal or visiting an information broker to update your knowledge database.")
        
        # Create a thematic fallback entry
        return {
            "category": category,
            "title": title,
            "content": fallback_content,
            "related_entries": [],
            "image": None
        }
