"""
Choice History Module - Tracks and manages player choices for story generation
"""
import time
import json

class ChoiceHistory:
    """Manages a history of player choices for enhanced story generation"""
    
    def __init__(self):
        """Initialize the choice history tracker"""
        self.choices = []
        self.max_choices = 20  # Maximum number of choices to remember
    
    def add_choice(self, node_id, choice_text, next_node, consequences=None):
        """Add a choice to the history
        
        Args:
            node_id (str): The ID of the story node where the choice was made
            choice_text (str): The text of the choice that was selected
            next_node (str): The ID of the next node after the choice
            consequences (dict, optional): Any consequences of the choice
        """
        # Create a record of the choice
        choice_record = {
            'timestamp': time.time(),
            'node_id': node_id,
            'choice_text': choice_text,
            'next_node': next_node,
            'consequences': consequences or {}
        }
        
        # Add to the history
        self.choices.append(choice_record)
        
        # Trim if we have too many choices
        if len(self.choices) > self.max_choices:
            self.choices = self.choices[-self.max_choices:]
    
    def get_recent_choices(self, count=5):
        """Get the most recent choices
        
        Args:
            count (int): Number of recent choices to return
            
        Returns:
            list: The most recent choices, newest first
        """
        return self.choices[-count:]
    
    def get_choices_for_node(self, node_id):
        """Get all choices made at a specific node
        
        Args:
            node_id (str): The ID of the node to get choices for
            
        Returns:
            list: All choices made at the specified node
        """
        return [choice for choice in self.choices if choice['node_id'] == node_id]
    
    def get_choices_with_consequence(self, consequence_key):
        """Get all choices that had a specific consequence
        
        Args:
            consequence_key (str): The key of the consequence to search for
            
        Returns:
            list: All choices with the specified consequence
        """
        return [
            choice for choice in self.choices 
            if consequence_key in choice.get('consequences', {})
        ]
    
    def get_narrative_summary(self, limit=10):
        """Get a narrative summary of recent choices for prompts
        
        Args:
            limit (int): Maximum number of choices to include
            
        Returns:
            str: A narrative summary of choices
        """
        if not self.choices:
            return "No previous choices have been made."
        
        recent_choices = self.choices[-limit:]
        narrative = []
        
        for choice in recent_choices:
            node_id = choice['node_id']
            choice_text = choice['choice_text']
            
            # Format consequences if any
            consequences = []
            for key, value in choice.get('consequences', {}).items():
                if key == 'items_gained' and value:
                    for item, count in value.items():
                        consequences.append(f"gained {count} {item}")
                elif key == 'items_lost' and value:
                    for item, count in value.items():
                        consequences.append(f"lost {count} {item}")
                elif key == 'health_change':
                    if value > 0:
                        consequences.append(f"healed {value} health")
                    elif value < 0:
                        consequences.append(f"took {abs(value)} damage")
                elif key == 'credits_change':
                    if value > 0:
                        consequences.append(f"gained {value} credits")
                    elif value < 0:
                        consequences.append(f"lost {abs(value)} credits")
            
            # Create narrative line
            line = f"At location '{node_id}', the player chose to '{choice_text}'"
            if consequences:
                line += f" and {', '.join(consequences)}"
            narrative.append(line)
        
        return "\n".join(narrative)
    
    def to_dict(self):
        """Convert the choice history to a dictionary for saving
        
        Returns:
            dict: The choice history as a dictionary
        """
        return {
            'choices': self.choices,
            'max_choices': self.max_choices
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a choice history from a dictionary (for loading saves)
        
        Args:
            data (dict): The choice history data to load
            
        Returns:
            ChoiceHistory: A new choice history object
        """
        history = cls()
        history.choices = data.get('choices', [])
        history.max_choices = data.get('max_choices', 20)
        return history