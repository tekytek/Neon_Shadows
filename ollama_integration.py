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
        self.api_url = OLLAMA_API_URL
        self.model = OLLAMA_MODEL
        self.console = Console()
    
    def _make_request(self, prompt, max_retries=3):
        """Make a request to the Ollama API"""
        # Define the API endpoint
        endpoint = f"{self.api_url}/api/generate"
        
        # Prepare the data payload
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        # Try to make the request with retries
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, json=data, timeout=30)
                
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
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
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
