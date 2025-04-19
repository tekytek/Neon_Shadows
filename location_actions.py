"""
Location Actions Module - Handles district-specific actions and events
"""
import random
import time
from typing import Dict, List, Optional, Tuple, Any

class LocationActionHandler:
    """Handles location-specific actions that players can take in different districts"""
    
    def __init__(self, game_engine):
        """Initialize with reference to the game engine"""
        self.game_engine = game_engine
        
        # Initialize faction_reputation_change in result dictionary if not present
        self.default_results = {
            'success': True,  # Default to success
            'messages': [],  # Messages to display to player
            'credits_change': 0,  # Credits gained or lost (negative for loss)
            'items_gained': {},  # Dict of item_name: count
            'items_lost': {},  # Dict of item_name: count
            'health_change': 0,  # Health gained or lost
            'experience_gain': 0,  # XP gained
            'reputation_change': {},  # Dict of district_id: change_amount
            'faction_reputation_change': {},  # Dict of faction_id: change_amount
            'combat_encounter': None  # Combat details if an encounter was triggered
        }
    
    def handle_location_action(self, console, choice_id: str, district_id: str) -> Dict[str, Any]:
        """
        Process a location-specific action and return its results
        
        Args:
            console: The rich console for output
            choice_id: The ID of the chosen action
            district_id: The ID of the current district
            
        Returns:
            Dict containing result information
        """
        # Get action type based on choice ID
        action_type = self._get_action_type(choice_id)
        
        # Base results dictionary - use default values from init
        results = self.default_results.copy()
        # Set district ID for reputation changes
        results["reputation_change"] = {district_id: 0}
        
        # Process action based on its type
        if action_type == "combat":
            self._handle_combat_action(console, choice_id, district_id, results)
        elif action_type == "resource":
            self._handle_resource_action(console, choice_id, district_id, results)
        elif action_type == "social":
            self._handle_social_action(console, choice_id, district_id, results)
        elif action_type == "tech":
            self._handle_tech_action(console, choice_id, district_id, results)
        elif action_type == "criminal":
            self._handle_criminal_action(console, choice_id, district_id, results)
        elif action_type == "rest":
            self._handle_rest_action(console, choice_id, district_id, results)
        else:
            self._handle_generic_action(console, choice_id, district_id, results)
        
        return results
    
    def _get_action_type(self, choice_id: str) -> str:
        """
        Determine action type based on choice ID
        
        Args:
            choice_id: The ID of the chosen action
            
        Returns:
            String indicating the action type
        """
        # Map common keywords in choice_id to action types
        combat_keywords = ["fight", "battle", "confront", "attack", "defend"]
        resource_keywords = ["gather", "collect", "scavenge", "hunt", "find"]
        social_keywords = ["talk", "meet", "negotiate", "discuss", "gossip", "network"]
        tech_keywords = ["hack", "program", "decrypt", "code", "bypass"]
        criminal_keywords = ["steal", "pickpocket", "smuggle", "illegal", "theft"]
        rest_keywords = ["rest", "sleep", "recover", "apartment"]
        
        # Check for keywords in the choice_id
        choice_lower = choice_id.lower()
        
        for keyword in combat_keywords:
            if keyword in choice_lower:
                return "combat"
        
        for keyword in resource_keywords:
            if keyword in choice_lower:
                return "resource"
        
        for keyword in social_keywords:
            if keyword in choice_lower:
                return "social"
        
        for keyword in tech_keywords:
            if keyword in choice_lower:
                return "tech"
        
        for keyword in criminal_keywords:
            if keyword in choice_lower:
                return "criminal"
        
        for keyword in rest_keywords:
            if keyword in choice_lower:
                return "rest"
        
        # Default to generic type
        return "generic"
    
    def _handle_combat_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle combat-oriented location actions"""
        console.print("[cyan]You prepare for potential conflict...[/cyan]")
        time.sleep(1)
        
        # Determine difficulty based on district danger level
        district = self.game_engine.district_manager.get_district(district_id)
        danger_level = district.danger_level if district else 3
        
        # Chance of actual combat versus just a tense situation
        if random.random() < 0.7:  # 70% chance of combat
            # Combat occurs - the game engine's combat system will handle details
            results["combat_encounter"] = {
                "enemy_type": self._get_district_enemy(district_id),
                "danger_level": danger_level,
                "rewards": {
                    "experience": 30 * danger_level,
                    "credits": 15 * danger_level,
                    "items": {"Stimpack": 1} if random.random() < 0.3 else {}
                }
            }
            results["messages"].append("You encounter a hostile target and prepare for combat.")
        else:
            # Tense situation but no combat
            results["messages"].append("The situation is tense, but you manage to avoid direct conflict.")
            results["experience_gain"] = 10 * danger_level
            
            # Small chance of finding something valuable
            if random.random() < 0.4:
                credits_found = random.randint(5, 15) * danger_level
                results["credits_change"] = credits_found
                results["messages"].append(f"You find {credits_found} credits in the process.")
    
    def _handle_resource_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle resource-gathering location actions"""
        console.print("[cyan]You search the area for useful resources...[/cyan]")
        time.sleep(1)
        
        # Determine district-specific resources
        district_resources = self._get_district_resources(district_id)
        
        # Determine success chance based on district danger
        district = self.game_engine.district_manager.get_district(district_id)
        danger_level = district.danger_level if district else 3
        success_chance = max(0.3, 0.9 - (danger_level * 0.1))
        
        # Check for success
        if random.random() < success_chance:
            # Success - find resources
            found_something = False
            
            # Try to find each available resource
            for resource in district_resources:
                if random.random() < resource["chance"]:
                    count = random.randint(resource["min"], resource["max"])
                    results["items_gained"][resource["name"]] = count
                    results["messages"].append(f"You found {count} {resource['name']}!")
                    found_something = True
            
            # Maybe find some credits
            if random.random() < 0.5:  # 50% chance
                credits_found = random.randint(5, 10) * danger_level
                results["credits_change"] = credits_found
                results["messages"].append(f"You find {credits_found} credits!")
                found_something = True
            
            if not found_something:
                results["messages"].append("You search thoroughly but find nothing of value.")
                
            # Small experience gain for the effort
            results["experience_gain"] = 5 * danger_level
        else:
            # Failure - potential problems
            results["success"] = False
            results["messages"].append("Your search is interrupted!")
            
            # Determine consequence
            if random.random() < 0.6:  # 60% chance of minor issue
                # Minor health loss from environmental hazard
                health_loss = random.randint(1, 3)
                results["health_change"] = -health_loss
                results["messages"].append(f"You hurt yourself while scavenging and lose {health_loss} health.")
            else:
                # More serious problem - encounter someone hostile
                results["messages"].append("You accidentally intrude on someone else's territory.")
                results["combat_encounter"] = {
                    "enemy_type": "Scavenger",
                    "danger_level": max(1, danger_level - 1),
                    "rewards": {
                        "experience": 20 * danger_level,
                        "credits": 10 * danger_level
                    }
                }
    
    def _handle_social_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle social interaction location actions"""
        console.print("[cyan]You engage in social interaction...[/cyan]")
        time.sleep(1)
        
        # Get player charisma to influence outcome
        player_charisma = self.game_engine.player.stats.get("charisma", 0)
        
        # Charisma check
        difficulty = 5  # Base difficulty
        success_chance = min(0.9, 0.5 + ((player_charisma - difficulty) * 0.1))
        success = random.random() < success_chance
        
        if success:
            # Successful social interaction
            results["messages"].append("Your social interaction goes well.")
            
            # Determine specific outcome
            outcome_type = random.choices(
                ["reputation", "faction", "information", "item", "credits"],
                weights=[0.3, 0.2, 0.2, 0.2, 0.1],
                k=1
            )[0]
            
            if outcome_type == "reputation":
                # Gain reputation in this district
                rep_gain = random.randint(1, 3)
                results["reputation_change"][district_id] = rep_gain
                results["messages"].append(f"Your reputation in this district increases by {rep_gain}.")
            
            elif outcome_type == "faction":
                # Gain reputation with a faction present in this district
                district_factions = self.game_engine.district_manager.get_factions_in_district(district_id)
                
                if district_factions:
                    # Choose a random faction
                    faction = random.choice(district_factions)
                    
                    # Determine if this is a positive or negative interaction
                    if random.random() < 0.8:  # 80% chance of positive outcome
                        # Positive interaction
                        rep_gain = random.randint(1, 3)
                        results["faction_reputation_change"][faction.faction_id] = rep_gain
                        results["messages"].append(f"You make a connection with {faction.name}.")
                        results["messages"].append(f"Your reputation with {faction.name} increases by {rep_gain}.")
                    else:
                        # Negative interaction but not hostile
                        rep_loss = -1
                        results["faction_reputation_change"][faction.faction_id] = rep_loss
                        results["messages"].append(f"Your interaction with {faction.name} doesn't go as planned.")
                        results["messages"].append(f"Your reputation with {faction.name} decreases slightly.")
                else:
                    # No factions here, default to district reputation
                    rep_gain = random.randint(1, 2)
                    results["reputation_change"][district_id] = rep_gain
                    results["messages"].append(f"You make some local connections, increasing district reputation by {rep_gain}.")
            
            elif outcome_type == "information":
                # Gain useful information (translate to XP)
                xp_gain = 20 + (5 * player_charisma)
                results["experience_gain"] = xp_gain
                results["messages"].append("You learn valuable information about the district.")
            
            elif outcome_type == "item":
                # Receive a useful item
                item_options = ["Access Card", "Encrypted Data Chip", "Stimpack", "Local Map"]
                item = random.choice(item_options)
                results["items_gained"][item] = 1
                results["messages"].append(f"Your new contact gives you a {item}.")
            
            elif outcome_type == "credits":
                # Receive some credits
                credits_gained = 10 + (player_charisma * 5)
                results["credits_change"] = credits_gained
                results["messages"].append(f"Your social connection pays off with {credits_gained} credits.")
        else:
            # Failed social interaction
            results["success"] = False
            results["messages"].append("Your social attempt doesn't go as planned.")
            
            # Determine consequence
            consequence = random.choices(
                ["minor", "reputation", "scam"],
                weights=[0.6, 0.3, 0.1],
                k=1
            )[0]
            
            if consequence == "minor":
                # Minor embarrassment, no real effect
                results["messages"].append("It's a bit embarrassing, but nothing serious.")
            
            elif consequence == "reputation":
                # Lose some reputation
                rep_loss = random.randint(1, 2)
                results["reputation_change"][district_id] = -rep_loss
                results["messages"].append(f"Your reputation in this district decreases by {rep_loss}.")
            
            elif consequence == "scam":
                # Get scammed out of some credits
                max_loss = min(self.game_engine.player.credits, 50)
                if max_loss > 0:
                    credit_loss = random.randint(10, max_loss)
                    results["credits_change"] = -credit_loss
                    results["messages"].append(f"You get scammed and lose {credit_loss} credits.")
    
    def _handle_tech_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle technology and hacking location actions"""
        console.print("[cyan]You attempt to work with the technology...[/cyan]")
        time.sleep(1)
        
        # Get player intelligence for skill check
        player_intelligence = self.game_engine.player.stats.get("intelligence", 0)
        
        # Get district for difficulty
        district = self.game_engine.district_manager.get_district(district_id)
        danger_level = district.danger_level if district else 3
        
        # Intelligence check
        difficulty = 3 + danger_level
        success_chance = min(0.9, 0.5 + ((player_intelligence - difficulty) * 0.1))
        success = random.random() < success_chance
        
        if success:
            # Successful tech action
            results["messages"].append("Your technical skills pay off.")
            
            # Determine specific outcome
            outcome_type = random.choices(
                ["data", "credits", "access", "item"],
                weights=[0.4, 0.3, 0.2, 0.1],
                k=1
            )[0]
            
            if outcome_type == "data":
                # Find valuable data (translate to XP)
                xp_gain = 25 + (5 * player_intelligence)
                results["experience_gain"] = xp_gain
                results["messages"].append("You extract valuable data worth " + str(xp_gain) + " experience points.")
            
            elif outcome_type == "credits":
                # Hack credits
                credits_gained = 15 + (player_intelligence * danger_level)
                results["credits_change"] = credits_gained
                results["messages"].append(f"You manage to transfer {credits_gained} credits to your account.")
            
            elif outcome_type == "access":
                # Gain system access (reputation)
                rep_gain = random.randint(1, 2)
                results["reputation_change"][district_id] = rep_gain
                results["messages"].append(f"Your technical prowess impresses locals, increasing reputation by {rep_gain}.")
            
            elif outcome_type == "item":
                # Find/create a tech item
                item_options = ["Tech Component", "Decryption Key", "Security Bypass", "Neural Booster"]
                item = random.choice(item_options)
                results["items_gained"][item] = 1
                results["messages"].append(f"You manage to obtain a {item}.")
        else:
            # Failed tech action
            results["success"] = False
            results["messages"].append("Your technical attempt fails.")
            
            # Determine consequence severity based on district danger
            consequence_chance = 0.2 + (danger_level * 0.1)  # 20-70% chance based on danger
            
            if random.random() < consequence_chance:
                # Significant consequence
                consequence_type = random.choices(
                    ["alarm", "trace", "damage"],
                    weights=[0.5, 0.3, 0.2],
                    k=1
                )[0]
                
                if consequence_type == "alarm":
                    # Trigger security response
                    results["messages"].append("You trigger security protocols!")
                    results["combat_encounter"] = {
                        "enemy_type": "Security Drone",
                        "danger_level": danger_level,
                        "rewards": {
                            "experience": 15 * danger_level,
                            "credits": 5 * danger_level
                        }
                    }
                
                elif consequence_type == "trace":
                    # Tracked back to you (reputation loss)
                    rep_loss = random.randint(1, 3)
                    results["reputation_change"][district_id] = -rep_loss
                    results["messages"].append(f"Your hack is traced back to you, decreasing reputation by {rep_loss}.")
                
                elif consequence_type == "damage":
                    # Electrical feedback
                    health_loss = random.randint(2, 5)
                    results["health_change"] = -health_loss
                    results["messages"].append(f"System feedback causes {health_loss} points of damage to you.")
            else:
                # Minor consequence
                results["messages"].append("The attempt fails, but you avoid any serious consequences.")
    
    def _handle_criminal_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle criminal and illicit location actions"""
        console.print("[cyan]You prepare to engage in some questionable activities...[/cyan]")
        time.sleep(1)
        
        # Get player reflexes for skill check
        player_reflex = self.game_engine.player.stats.get("reflex", 0)
        
        # Get district for difficulty and consequences
        district = self.game_engine.district_manager.get_district(district_id)
        danger_level = district.danger_level if district else 3
        
        # Reflexes check - harder in more secure districts
        difficulty = 3 + danger_level
        success_chance = min(0.8, 0.4 + ((player_reflex - difficulty) * 0.1))
        success = random.random() < success_chance
        
        if success:
            # Successful criminal action
            results["messages"].append("Your criminal activity succeeds.")
            
            # Higher danger districts have better payouts
            payout_multiplier = 0.8 + (danger_level * 0.2)
            
            # Calculate credits gained
            credits_gained = int((20 + (player_reflex * 5)) * payout_multiplier)
            results["credits_change"] = credits_gained
            results["messages"].append(f"You pocket {credits_gained} credits from your illicit actions.")
            
            # Experience gain
            results["experience_gain"] = 20 * danger_level
            
            # Chance for additional item
            if random.random() < 0.3:  # 30% chance
                item_options = ["Encrypted Keycard", "Security Passkey", "Contraband", "Valuable Trinket"]
                item = random.choice(item_options)
                results["items_gained"][item] = 1
                results["messages"].append(f"You also manage to grab a {item}.")
            
            # Check for factions present in this district
            district_factions = self.game_engine.district_manager.get_factions_in_district(district_id)
            
            # Try to find a criminal faction that might appreciate your actions
            criminal_faction = None
            for faction in district_factions:
                if faction.faction_type == "gang":
                    criminal_faction = faction
                    break
            
            # Chance for faction reputation impact
            if random.random() < 0.6:  # 60% chance
                if criminal_faction:
                    # Criminal activity might impress local gangs
                    rep_gain = random.randint(1, 2)
                    results["faction_reputation_change"][criminal_faction.faction_id] = rep_gain
                    results["messages"].append(f"Your criminal prowess has impressed the {criminal_faction.name}.")
                    
                    # But might upset law-abiding factions
                    law_factions = [f for f in district_factions if f.faction_type in ["government", "corp"]]
                    if law_factions and random.random() < 0.4:  # 40% chance
                        law_faction = random.choice(law_factions)
                        results["faction_reputation_change"][law_faction.faction_id] = -1
                        results["messages"].append(f"However, the {law_faction.name} would disapprove if they knew.")
            
            # Small district reputation loss even with success - someone might have seen you
            if random.random() < 0.3:  # 30% chance
                results["reputation_change"][district_id] = -1
                results["messages"].append("Despite your success, someone may have witnessed your actions.")
        else:
            # Failed criminal action
            results["success"] = False
            results["messages"].append("Your criminal attempt fails and you're spotted.")
            
            # Identify if any law enforcement or corporate factions are present
            district_factions = self.game_engine.district_manager.get_factions_in_district(district_id)
            faction_present = None
            
            # Look for law enforcement or corporate factions first
            for faction in district_factions:
                if faction.faction_type in ["government", "corp"]:
                    faction_present = faction
                    break
            
            # If no government/corp factions, check if there's a local gang
            if not faction_present and district_factions:
                for faction in district_factions:
                    if faction.faction_type == "gang":
                        faction_present = faction
                        break
            
            # Determine how bad the consequence is
            consequence_severity = random.choices(
                ["minor", "moderate", "severe"],
                weights=[0.4, 0.4, 0.2],
                k=1
            )[0]
            
            if consequence_severity == "minor":
                # Minor consequence - small reputation loss
                results["reputation_change"][district_id] = -1
                results["messages"].append("You narrowly escape, but rumors about your actions spread.")
                
                # If a faction was present, lose reputation with them
                if faction_present:
                    rep_loss = -1
                    results["faction_reputation_change"][faction_present.faction_id] = rep_loss
                    results["messages"].append(f"Your actions have not gone unnoticed by the {faction_present.name}.")
                
                # Maybe lose a few credits
                if self.game_engine.player.credits > 20:
                    credit_loss = random.randint(10, 20)
                    results["credits_change"] = -credit_loss
                    results["messages"].append(f"In your hasty escape, you lose {credit_loss} credits.")
            
            elif consequence_severity == "moderate":
                # Moderate consequence - security response
                
                # Determine appropriate enemy type based on present faction
                enemy_type = "Security Officer"  # Default
                if faction_present:
                    if faction_present.faction_type == "corp":
                        enemy_type = "Corporate Security"
                    elif faction_present.faction_type == "government":
                        enemy_type = "Law Enforcement"
                    elif faction_present.faction_type == "gang":
                        enemy_type = f"{faction_present.name} Enforcer"
                
                results["messages"].append(f"You're spotted by {enemy_type}s who move to intervene!")
                
                # Set faction reputation change for the moderate encounter
                if faction_present:
                    rep_loss = -2
                    results["faction_reputation_change"][faction_present.faction_id] = rep_loss
                    results["messages"].append(f"Your actions have angered the {faction_present.name}.")
                
                results["combat_encounter"] = {
                    "enemy_type": enemy_type,
                    "danger_level": danger_level,
                    "rewards": {
                        "experience": 15 * danger_level,
                        "credits": 0  # No credits from this combat - you're escaping
                    }
                }
            
            elif consequence_severity == "severe":
                # Severe consequence - big reputation hit, lose credits and health
                rep_loss = random.randint(2, 5)
                results["reputation_change"][district_id] = -rep_loss
                results["messages"].append(f"Your botched criminal activity severely damages your reputation (-{rep_loss}).")
                
                # If a faction was present, lose significant reputation with them
                if faction_present:
                    faction_rep_loss = random.randint(-3, -5)
                    results["faction_reputation_change"][faction_present.faction_id] = faction_rep_loss
                    results["messages"].append(f"The {faction_present.name} has put you on their watch list.")
                    
                    # If it's a gang, maybe give a small reputation boost to a rival gang
                    if faction_present.faction_type == "gang" and faction_present.rival_factions:
                        rival_faction_id = random.choice(faction_present.rival_factions)
                        rival_faction = self.game_engine.district_manager.get_faction(rival_faction_id)
                        if rival_faction:
                            results["faction_reputation_change"][rival_faction_id] = 1
                            results["messages"].append(f"Word of your conflict with {faction_present.name} reaches the {rival_faction.name}, who appreciate your actions.")
                
                # Health loss from escape
                health_loss = random.randint(3, 8)
                results["health_change"] = -health_loss
                results["messages"].append(f"You sustain {health_loss} damage while desperately escaping.")
                
                # Credit loss
                if self.game_engine.player.credits > 50:
                    credit_loss = int(self.game_engine.player.credits * 0.2)  # Lose 20%
                    results["credits_change"] = -credit_loss
                    results["messages"].append(f"You drop {credit_loss} credits during your escape.")
    
    def _handle_rest_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle rest and recovery location actions"""
        console.print("[cyan]You take some time to rest and recover...[/cyan]")
        time.sleep(1)
        
        # Calculate health recovery based on max health
        max_health = self.game_engine.player.max_health
        recovery_amount = max(5, int(max_health * 0.3))  # Recover 30% of max health, minimum 5
        
        # Apply recovery
        results["health_change"] = recovery_amount
        results["messages"].append(f"You rest and recover {recovery_amount} health points.")
        
        # Chance for a random event during rest
        if random.random() < 0.3:  # 30% chance
            event_type = random.choices(
                ["dream", "visitor", "message", "item"],
                weights=[0.3, 0.3, 0.2, 0.2],
                k=1
            )[0]
            
            if event_type == "dream":
                # Prophetic dream (small XP gain)
                results["experience_gain"] = 10
                results["messages"].append("You have a strange, vivid dream that feels prophetic.")
            
            elif event_type == "visitor":
                # Someone visits
                results["messages"].append("While resting, you receive an unexpected visitor.")
                
                # Small reputation gain
                results["reputation_change"][district_id] = 1
                results["messages"].append("The interaction improves your local standing slightly.")
            
            elif event_type == "message":
                # Receive a message
                results["messages"].append("You receive an encrypted message with useful information.")
                results["experience_gain"] = 15
            
            elif event_type == "item":
                # Find a forgotten item
                item_options = ["Forgotten Credit Chip", "Old Key", "Nutritional Bar", "Med Patch"]
                item = random.choice(item_options)
                results["items_gained"][item] = 1
                results["messages"].append(f"You find a {item} you had forgotten about.")
    
    def _handle_generic_action(self, console, choice_id: str, district_id: str, results: Dict) -> None:
        """Handle generic location actions that don't fit other categories"""
        console.print("[cyan]You explore the area...[/cyan]")
        time.sleep(1)
        
        # Random outcomes for generic actions
        outcome = random.choices(
            ["nothing", "minor_find", "encounter", "information"],
            weights=[0.3, 0.3, 0.2, 0.2],
            k=1
        )[0]
        
        if outcome == "nothing":
            # Nothing particularly interesting
            results["messages"].append("You spend some time exploring, but find nothing noteworthy.")
            
            # Minimal XP for the effort
            results["experience_gain"] = 5
        
        elif outcome == "minor_find":
            # Find something minor
            if random.random() < 0.7:  # 70% chance of credits
                credits_found = random.randint(5, 20)
                results["credits_change"] = credits_found
                results["messages"].append(f"While exploring, you find {credits_found} credits.")
            else:
                # Find a common item
                item_options = ["Scrap Parts", "Synth-Food Pack", "Micro-Battery", "Pocket Tool"]
                item = random.choice(item_options)
                results["items_gained"][item] = 1
                results["messages"].append(f"You find a {item} during your exploration.")
            
            # Small XP
            results["experience_gain"] = 10
        
        elif outcome == "encounter":
            # Random encounter with someone
            if random.random() < 0.7:  # 70% chance of friendly encounter
                results["messages"].append("You encounter someone who shares useful information.")
                results["experience_gain"] = 15
                
                # Small reputation gain
                results["reputation_change"][district_id] = 1
                results["messages"].append("The interaction improves your local reputation slightly.")
            else:
                # Unfriendly encounter
                results["messages"].append("You encounter someone with hostile intentions.")
                
                # Get district for difficulty
                district = self.game_engine.district_manager.get_district(district_id)
                danger_level = district.danger_level if district else 3
                
                results["combat_encounter"] = {
                    "enemy_type": "Street Thug",
                    "danger_level": max(1, danger_level - 1),
                    "rewards": {
                        "experience": 20 * danger_level,
                        "credits": 10 * danger_level
                    }
                }
        
        elif outcome == "information":
            # Discover useful information
            results["messages"].append("You discover some interesting information about the area.")
            results["experience_gain"] = 20
            
            # Chance to also gain a bit of reputation
            if random.random() < 0.5:  # 50% chance
                results["reputation_change"][district_id] = 1
                results["messages"].append("Locals appreciate your interest in their district.")
    
    def _get_district_enemy(self, district_id: str) -> str:
        """Get an appropriate enemy type for a district"""
        district_enemies = {
            # Core districts
            "downtown": ["Corporate Guard", "Street Thug", "Corrupt Cop"],
            "industrial": ["Security Robot", "Gang Member", "Factory Worker"],
            "residential": ["Local Tough", "Home Defender", "Gang Recruit"],
            "outskirts": ["Wasteland Scavenger", "Mutant", "Gang Enforcer"],
            
            # Corporate areas
            "corporate": ["Corporate Security", "Combat Droid", "Executive Bodyguard"],
            "corporate_sector": ["Elite Security", "Corporate Enforcer", "Security Drone"],
            
            # Commerce areas
            "nightmarket": ["Market Guard", "Smuggler", "Thief"],
            "entertainment": ["Club Bouncer", "Drug Dealer", "Rich Thug"],
            "upscale": ["Private Security", "Armed Civilian", "Corporate Agent"],
            
            # Outer areas
            "wasteland": ["Mutant Beast", "Rad-Scavenger", "Tribal Warrior"],
            
            # Tech areas
            "tech_district": ["Rogue AI Bot", "Tech Gang Member", "Cyber-Enhanced Guard"],
            
            # Add any other districts that might be present in your game
        }
        
        # Normalize district ID to handle variations in naming
        normalized_id = district_id.lower().replace(' ', '_').replace('-', '_')
        
        # Try exact match first
        if normalized_id in district_enemies:
            enemies = district_enemies[normalized_id]
        else:
            # Try partial matching for similar district names
            matched = False
            for key in district_enemies:
                if key in normalized_id or normalized_id in key:
                    enemies = district_enemies[key]
                    matched = True
                    break
            
            # Fall back to default enemies if no match found
            if not matched:
                enemies = ["Hostile Stranger", "Armed Civilian", "Street Fighter"]
            
            # Log the fallback for debugging
            print(f"Warning: No exact enemy match for district '{district_id}', using best match or default.")
        
        # Return a random enemy from the list
        return random.choice(enemies)
    
    def _get_district_resources(self, district_id: str) -> List[Dict]:
        """Get resources that can be found in a specific district"""
        district_resources = {
            # Core districts
            "downtown": [
                {"name": "Credit Chip", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Tech Component", "chance": 0.4, "min": 1, "max": 2},
                {"name": "Data Shard", "chance": 0.5, "min": 1, "max": 3}
            ],
            "industrial": [
                {"name": "Scrap Metal", "chance": 0.7, "min": 2, "max": 5},
                {"name": "Circuit Board", "chance": 0.5, "min": 1, "max": 3},
                {"name": "Industrial Cleaner", "chance": 0.3, "min": 1, "max": 1}
            ],
            "residential": [
                {"name": "Synth-Food Pack", "chance": 0.6, "min": 1, "max": 3},
                {"name": "Household Tool", "chance": 0.5, "min": 1, "max": 1},
                {"name": "Med Patch", "chance": 0.3, "min": 1, "max": 2}
            ],
            "outskirts": [
                {"name": "Scrap Electronics", "chance": 0.6, "min": 1, "max": 3},
                {"name": "Stimpack", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Makeshift Weapon", "chance": 0.4, "min": 1, "max": 1}
            ],
            
            # Corporate areas
            "corporate": [
                {"name": "Corporate ID Card", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Premium Tech Component", "chance": 0.4, "min": 1, "max": 1},
                {"name": "Encrypted Data Chip", "chance": 0.5, "min": 1, "max": 2}
            ],
            "corporate_sector": [
                {"name": "High-End Datachip", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Corporate Access Card", "chance": 0.2, "min": 1, "max": 1},
                {"name": "Premium Stimpack", "chance": 0.4, "min": 1, "max": 1}
            ],
            
            # Commerce areas
            "nightmarket": [
                {"name": "Street Food", "chance": 0.7, "min": 1, "max": 3},
                {"name": "Black Market Item", "chance": 0.4, "min": 1, "max": 1},
                {"name": "Counterfeit Goods", "chance": 0.5, "min": 1, "max": 2}
            ],
            "entertainment": [
                {"name": "Synthetic Drug", "chance": 0.5, "min": 1, "max": 2},
                {"name": "Club Pass", "chance": 0.4, "min": 1, "max": 1},
                {"name": "Audio Recording", "chance": 0.3, "min": 1, "max": 1}
            ],
            "upscale": [
                {"name": "Luxury Item", "chance": 0.4, "min": 1, "max": 1},
                {"name": "Designer Clothes", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Gourmet Food", "chance": 0.5, "min": 1, "max": 2}
            ],
            
            # Outer areas
            "wasteland": [
                {"name": "Rare Metal", "chance": 0.4, "min": 1, "max": 2},
                {"name": "Mutant Tissue", "chance": 0.5, "min": 1, "max": 3},
                {"name": "Radiation Pills", "chance": 0.6, "min": 1, "max": 2}
            ],
            
            # Tech areas
            "tech_district": [
                {"name": "Experimental Chip", "chance": 0.4, "min": 1, "max": 1},
                {"name": "AI Core Fragment", "chance": 0.3, "min": 1, "max": 1},
                {"name": "Neural Interface", "chance": 0.2, "min": 1, "max": 1}
            ]
        }
        
        # Normalize district ID to handle variations in naming
        normalized_id = district_id.lower().replace(' ', '_').replace('-', '_')
        
        # Try exact match first
        if normalized_id in district_resources:
            resources = district_resources[normalized_id]
        else:
            # Try partial matching for similar district names
            matched = False
            for key in district_resources:
                if key in normalized_id or normalized_id in key:
                    resources = district_resources[key]
                    matched = True
                    break
            
            # Fall back to default resources if no match found
            if not matched:
                resources = [
                    {"name": "Scrap Parts", "chance": 0.6, "min": 1, "max": 3},
                    {"name": "Stimpack", "chance": 0.3, "min": 1, "max": 1}
                ]
            
            # Log the fallback for debugging
            print(f"Warning: No exact resource match for district '{district_id}', using best match or default.")
        
        return resources