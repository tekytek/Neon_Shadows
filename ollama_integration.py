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
    
    def _create_story_prompt(self, node_id, player):
        """Create a prompt for story generation based on current game state"""
        prompt = f"""
        You are the storyteller for a cyberpunk text adventure game. The player has reached a story node with ID "{node_id}".
        
        Player information:
        - Name: {player.name}
        - Class: {player.char_class}
        - Level: {player.level}
        - Stats: {json.dumps(player.stats)}
        - Health: {player.health}/{player.max_health}
        - Inventory: {json.dumps(player.inventory.get_all_items())}
        
        Based on this information, generate a story node in JSON format with the following structure:
        
        For a standard narrative node:
        {{
            "text": "Detailed and atmospheric description of the situation.",
            "choices": [
                {{
                    "text": "Description of the first choice",
                    "next_node": "unique_id_for_next_node",
                    "requirements": {{
                        "stats": {{"stat_name": minimum_value}},
                        "item": "required_item_name"
                    }},
                    "consequences": {{
                        "items_gained": {{"item_name": quantity}},
                        "items_lost": {{"item_name": quantity}},
                        "stats_change": {{"stat_name": change_amount}},
                        "health_change": change_amount,
                        "credits_change": change_amount
                    }}
                }},
                {{
                    "text": "Description of the second choice",
                    "next_node": "another_unique_id"
                }}
            ]
        }}
        
        OR for a combat node:
        {{
            "type": "combat",
            "text": "Description of the combat situation",
            "enemy": {{
                "name": "Enemy Name",
                "health": health_value,
                "damage": damage_value,
                "defense": defense_value
            }},
            "victory_node": "node_after_winning",
            "escape_node": "node_after_escaping",
            "rewards": {{
                "experience": amount,
                "credits": amount,
                "items": {{
                    "item_name": quantity
                }}
            }}
        }}
        
        OR for a skill check node:
        {{
            "type": "skill_check",
            "text": "Description of the situation requiring a skill check",
            "skill": "skill_name",
            "difficulty": difficulty_value,
            "success_node": "node_after_success",
            "failure_node": "node_after_failure",
            "success_rewards": {{
                "experience": amount,
                "items": {{
                    "item_name": quantity
                }}
            }},
            "failure_consequences": {{
                "health_loss": amount
            }}
        }}
        
        Create a compelling and atmospheric cyberpunk scene that fits with a world where corporations control everything, technology and humanity have merged, and the divide between rich and poor is extreme. Include appropriate cyberpunk themes, terminology, and atmosphere.
        
        The response should be ONLY the JSON object, nothing else.
        """
        
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
