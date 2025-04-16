"""
Story Management Module - Handles story nodes and progression
"""
import os
import json

from config import DATA_DIR

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
    
    def create_default_story(self):
        """Create a default story structure"""
        self.nodes = {
            # Introduction sequence
            "intro": {
                "title": "The Awakening",
                "ascii_art": "intro",
                "text": "Your consciousness flickers to life in a dimly-lit room. Your neural implant boots up, feeding you status notifications that scroll across your vision in glowing green text. Welcome to Neo-Shanghai, 2077, where corporations rule and the line between human and machine blurs with each passing day.",
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
            },
            "intro_memory": {
                "title": "Fragmented Memories",
                "text": "You strain to recall your recent past, but your memories are fragmented. Flashes of a job gone wrong, a double-cross, the sensation of falling. Your head throbs as you push against the mental block. Something - or someone - has tampered with your neural implant.",
                "choices": [
                    {
                        "text": "Force through the memory block",
                        "next_node": "intro_force_memory",
                        "requirements": {
                            "stats": {"intelligence": 5}
                        }
                    },
                    {
                        "text": "Let it go for now and check your surroundings",
                        "next_node": "intro_surroundings"
                    }
                ]
            },
            "intro_force_memory": {
                "title": "Breaking Through",
                "text": "You push against the mental barrier, using techniques you've learned to bypass neural blocks. A searing pain shoots through your skull, but fragments come back to you: a high-rise office, security alarms, a familiar face betraying you, then darkness. Someone wanted whatever you found - or what you know - and they were willing to erase your memory to keep it hidden.",
                "choices": [
                    {
                        "text": "Check your surroundings",
                        "next_node": "intro_surroundings"
                    }
                ],
                "consequences": {
                    "stats_change": {"intelligence": 1},
                    "health_change": -2
                }
            },
            "intro_surroundings": {
                "title": "Unfamiliar Territory",
                "text": "You're in a cheap motel room, the kind that charges by the hour and doesn't ask questions. Neon light bleeds through thin curtains, casting the room in a sickly pink glow. Your gear is scattered across a small table - some of it missing. Your crypto-wallet shows a balance of 100 credits - barely enough to survive a couple of days in the city.",
                "choices": [
                    {
                        "text": "Check what gear you still have",
                        "next_node": "intro_gear"
                    },
                    {
                        "text": "Leave the motel room",
                        "next_node": "street_entrance"
                    }
                ]
            },
            "intro_gear": {
                "title": "Remaining Assets",
                "text": "Your essential gear remains: communication device, basic weapons, and your neural link hardware. The most valuable items are missing - particularly the data shard you remember securing before everything went dark. Someone has been thorough in taking what they wanted, but left you with enough to survive. Maybe they thought you were dead - or wished you were.",
                "choices": [
                    {
                        "text": "Leave the motel room",
                        "next_node": "street_entrance"
                    }
                ]
            },
            
            # First street scene
            "street_entrance": {
                "title": "Neon Streets",
                "ascii_art": "street",
                "text": "You step out into the busy street. Towering skyscrapers pierce the smog-filled sky, their surfaces alive with massive holographic advertisements. Rain falls in an unending drizzle, reflecting the kaleidoscope of neon lights that define Neo-Shanghai's perpetual night. The air is thick with the smell of synthetic food, exhaust, and too many people packed together.",
                "choices": [
                    {
                        "text": "Head toward the marketplace",
                        "next_node": "marketplace"
                    },
                    {
                        "text": "Look for information at the local bar",
                        "next_node": "neon_dragon_exterior"
                    },
                    {
                        "text": "Try to contact an old connection",
                        "requirements": {
                            "item": "Encrypted Phone"
                        },
                        "next_node": "contact_fixer"
                    }
                ]
            },
            
            # Marketplace branch
            "marketplace": {
                "title": "The Night Market",
                "ascii_art": "market",
                "text": "The Night Market bustles with activity despite the late hour. Vendors hawk everything from street food to black market tech under makeshift tents glowing with string lights. The market is a good place to stock up or gather information - if you know who to talk to and have the credits to spend.",
                "choices": [
                    {
                        "text": "Visit the tech vendor",
                        "next_node": "tech_vendor"
                    },
                    {
                        "text": "Approach the street doctor's stall",
                        "next_node": "street_doctor"
                    },
                    {
                        "text": "Return to the main street",
                        "next_node": "street_entrance"
                    }
                ]
            },
            "tech_vendor": {
                "title": "Wei's Tech Emporium",
                "type": "shop",
                "shop_name": "Wei's Tech Emporium",
                "ascii_art": "tech_shop",
                "text": "A wizened man with more mechanical parts than organic sits behind a counter covered in circuit boards and neural implants. 'Wei's the name. What you lookin' for, runner?' His cybernetic eye whirs as it scans you, likely assessing how much you can afford.",
                "inventory": {
                    "Basic Cyberdeck": {
                        "price": 150,
                        "description": "Entry-level hacking device. Necessary for breaching low-level security systems."
                    },
                    "Neural Booster": {
                        "price": 75,
                        "description": "Temporary intelligence enhancement. +2 Intelligence for 3 encounters."
                    },
                    "EMP Grenade": {
                        "price": 120,
                        "description": "Disables electronic devices and cyberware in a small radius."
                    },
                    "Memory Shard": {
                        "price": 50,
                        "description": "Storage device for neural data and programs."
                    }
                },
                "exit_node": "marketplace"
            },
            "street_doctor": {
                "title": "Doc Mei's Stall",
                "type": "shop",
                "shop_name": "Doc Mei's Medical Stall",
                "ascii_art": "doctor",
                "text": "The 'clinic' is barely more than a reinforced shipping container with surgical equipment. Doc Mei, a woman with steady hands and eyes that have seen too much, nods as you approach. 'Patching up or enhancing today?' she asks, already prepping a sterilization field.",
                "inventory": {
                    "Stimpack": {
                        "price": 40,
                        "description": "Emergency healing injection. Restores 5 health immediately."
                    },
                    "Med Nanites": {
                        "price": 120,
                        "description": "Advanced healing. Restores 10 health and removes one negative status effect."
                    },
                    "Reflex Booster": {
                        "price": 100,
                        "description": "Temporary enhancement. +2 Reflex for 3 encounters."
                    },
                    "Immunity Chip": {
                        "price": 80,
                        "description": "Protects against common toxins and pathogens for 24 hours."
                    }
                },
                "exit_node": "marketplace"
            },
            
            # Bar branch
            "neon_dragon_exterior": {
                "title": "The Neon Dragon",
                "ascii_art": "bar_exterior",
                "text": "The Neon Dragon looms before you, a dive bar housed in a repurposed industrial building. A holographic dragon coils around the entrance, its animated scales shifting from crimson to electric blue. The bouncer, a mountain of muscle and metal, gives you a once-over as you approach.",
                "choices": [
                    {
                        "text": "Enter the bar",
                        "next_node": "neon_dragon_interior"
                    },
                    {
                        "text": "Return to the street",
                        "next_node": "street_entrance"
                    }
                ]
            },
            "neon_dragon_interior": {
                "title": "Inside the Dragon",
                "ascii_art": "bar_interior",
                "text": "Synthetic bass thumps through speakers as you enter the crowded bar. The air is thick with vaporized alcohol and designer pheromones. Patrons from all walks of life drink, deal, and disappear into private booths. The bartender, sporting chrome arms with built-in dispensers, raises an eyebrow as you approach the counter.",
                "choices": [
                    {
                        "text": "Order a drink and listen to nearby conversations",
                        "next_node": "bar_eavesdrop"
                    },
                    {
                        "text": "Approach the suspicious figure in the corner booth",
                        "next_node": "bar_contact"
                    },
                    {
                        "text": "Leave the bar",
                        "next_node": "neon_dragon_exterior"
                    }
                ]
            },
            "bar_eavesdrop": {
                "title": "Liquid Intelligence",
                "text": "You order a 'Neuro-Toxin' - a fluorescent green cocktail that's more chemical than alcohol. As you sip the electric-tasting drink, you focus your enhanced hearing on conversations around you. There's talk of a major corporate feud between MegaTech and Orison Industries. Someone mentions a high-profile data theft that has the corps on edge. Another group discusses a job with a big payout for those willing to take risks.",
                "choices": [
                    {
                        "text": "Ask the bartender about the corporate feud",
                        "next_node": "bartender_info"
                    },
                    {
                        "text": "Try to join the conversation about the job",
                        "next_node": "job_conversation"
                    },
                    {
                        "text": "Return to watching the bar",
                        "next_node": "neon_dragon_interior"
                    }
                ],
                "consequences": {
                    "credits_change": -10
                }
            },
            "bartender_info": {
                "title": "Insider Knowledge",
                "text": "The bartender leans in, chrome arms gleaming under the bar lights. 'The feud? Started when a top MegaTech scientist disappeared with breakthrough research. Now both corps are tearing the city apart looking for them.' He wipes the counter with a cloth that's seen better days. 'Word is, whoever finds the scientist first gets a game-changing edge in the market. People associated with the case have been going missing - or turning up dead.'",
                "choices": [
                    {
                        "text": "Ask if he knows anything about memory tampering",
                        "next_node": "memory_tampering_info"
                    },
                    {
                        "text": "Return to watching the bar",
                        "next_node": "neon_dragon_interior"
                    }
                ],
                "consequences": {
                    "credits_change": -15
                }
            },
            "memory_tampering_info": {
                "title": "Memory Lanes",
                "text": "'Memory tampering?' The bartender's eyes narrow with interest. 'That's specialized work. Not many can do it clean. There's a tech named Zhi who operates out of the old industrial zone. If someone messed with your head and you're still walking around, it was probably her work. She's the best.' He slides you a data chip. 'Her location. Don't say where you got it.'",
                "choices": [
                    {
                        "text": "Thank the bartender and return to watching the bar",
                        "next_node": "neon_dragon_interior"
                    }
                ],
                "consequences": {
                    "items_gained": {"Zhi's Location Data": 1},
                    "credits_change": -20
                }
            },
            "job_conversation": {
                "title": "Business Opportunity",
                "text": "You slide into the conversation smoothly. The group consists of three individuals: a woman with military-grade cyberarms, a thin man whose eyes never stop scanning the room, and a corporate-looking type trying hard not to look corporate. They're discussing a retrieval job - breaking into an Orison Industries research facility to extract data. The pay is substantial, but they're clearly nervous about the details.",
                "choices": [
                    {
                        "text": "Offer your services for the job",
                        "next_node": "accept_job"
                    },
                    {
                        "text": "Ask more questions about what exactly they're retrieving",
                        "next_node": "job_details"
                    },
                    {
                        "text": "Politely excuse yourself",
                        "next_node": "neon_dragon_interior"
                    }
                ]
            },
            "job_details": {
                "title": "Due Diligence",
                "text": "The corporate type hesitates, but the woman cuts in. 'We need someone to infiltrate a secure lab and extract research data on neural interface technology. The security is top-tier - both digital and physical.' The thin man adds with a smirk, 'We've lost two runners already trying to get in. But third time's the charm, right?' Something in their story doesn't add up, but the job could connect to your missing memories.",
                "choices": [
                    {
                        "text": "Accept the job",
                        "next_node": "accept_job"
                    },
                    {
                        "text": "Decline and return to watching the bar",
                        "next_node": "neon_dragon_interior"
                    }
                ]
            },
            "accept_job": {
                "title": "Contract Sealed",
                "text": "The corporate type slides a credchip across the table with a down payment. 'Half now, half when you deliver. The facility is in the eastern corporate sector. Our intel suggests there's a maintenance entrance with lighter security. You'll need to find the main research server and extract the neural mapping data.' The woman hands you a specialized data shard. 'Use this for the extraction. Don't try to access the data yourself if you value your sanity.'",
                "choices": [
                    {
                        "text": "Head to the eastern corporate sector",
                        "next_node": "corporate_sector_entrance"
                    },
                    {
                        "text": "Prepare first and visit the marketplace",
                        "next_node": "marketplace"
                    }
                ],
                "consequences": {
                    "items_gained": {"Specialized Data Shard": 1, "Facility Access Codes": 1},
                    "credits_change": 200
                }
            },
            
            # First combat encounter
            "corporate_sector_entrance": {
                "title": "Corporate Territory",
                "ascii_art": "corporate_sector",
                "text": "The eastern corporate sector is a stark contrast to the chaotic streets you left behind. Here, everything is ordered, pristine, and heavily surveilled. Massive corporate towers reach toward the sky, their facades displaying stock tickers and company propaganda. As you approach the Orison Industries complex, you spot two security guards patrolling the maintenance entrance mentioned in your briefing.",
                "choices": [
                    {
                        "text": "Try to sneak past the guards",
                        "next_node": "sneak_attempt",
                        "requirements": {
                            "stats": {"reflex": 5}
                        }
                    },
                    {
                        "text": "Try to hack the security system",
                        "next_node": "hack_attempt",
                        "requirements": {
                            "stats": {"intelligence": 5},
                            "item": "Cyberdeck"
                        }
                    },
                    {
                        "text": "Confront the guards directly",
                        "next_node": "guard_combat"
                    }
                ]
            },
            "sneak_attempt": {
                "title": "Shadow Walk",
                "type": "skill_check",
                "skill": "reflex",
                "difficulty": 7,
                "text": "You time your approach carefully, using the shadows and blind spots in the security system. Your augmented reflexes help you move in perfect silence as you approach the maintenance entrance. A security camera sweeps across your path as you make your final approach...",
                "success_node": "maintenance_entrance",
                "failure_node": "guard_combat",
                "success_rewards": {
                    "experience": 50
                },
                "failure_consequences": {
                    "health_loss": 0
                }
            },
            "hack_attempt": {
                "title": "Digital Infiltration",
                "type": "skill_check",
                "skill": "intelligence",
                "difficulty": 7,
                "text": "You find a hidden junction box and connect your cyberdeck. Your fingers dance across the interface as you attempt to bypass the security protocols. The system is sophisticated, but you've seen worse. Layers of ICE (Intrusion Countermeasures Electronics) stand between you and control of the external security systems...",
                "success_node": "maintenance_entrance",
                "failure_node": "guard_combat",
                "success_rewards": {
                    "experience": 50
                },
                "failure_consequences": {
                    "health_loss": 0
                }
            },
            "guard_combat": {
                "title": "Security Response",
                "type": "combat",
                "ascii_art": "security_guard",
                "text": "The security guards spot you and immediately draw their weapons - standard corporate issue stun batons and pistols. 'Halt! This is a restricted area!' one shouts as they advance toward you. You'll need to deal with them quickly before reinforcements arrive.",
                "enemy": {
                    "name": "Corporate Security Guard",
                    "health": 15,
                    "damage": 3,
                    "defense": 2
                },
                "victory_node": "maintenance_entrance",
                "escape_node": "street_entrance",
                "escape_consequences": {
                    "health_loss": 3,
                    "items_lost": {"credits": 20}
                },
                "rewards": {
                    "experience": 75,
                    "credits": 30,
                    "items": {
                        "Security Keycard": 1,
                        "Stimpack": 1
                    }
                }
            },
            "maintenance_entrance": {
                "title": "Breach Point",
                "text": "With the guards neutralized, you access the maintenance entrance. The utilitarian corridor beyond is dimly lit with emergency lighting, and the distant hum of machinery fills the air. According to your intel, the research lab should be three levels up, in the secure R&D wing. You need to find an elevator or service ladder without alerting more security.",
                "choices": [
                    {
                        "text": "Search for a service ladder",
                        "next_node": "service_ladder"
                    },
                    {
                        "text": "Look for a staff elevator",
                        "next_node": "staff_elevator"
                    }
                ]
            }
            
            # Additional story nodes would continue here...
        }
    
    def get_node(self, node_id):
        """Get a story node by ID"""
        return self.nodes.get(node_id, None)
    
    def add_node(self, node_id, node_data):
        """Add a new story node"""
        self.nodes[node_id] = node_data
        return True
    
    def save_story(self):
        """Save the current story nodes to file"""
        story_file = os.path.join(DATA_DIR, 'story_nodes.json')
        
        try:
            with open(story_file, 'w') as f:
                json.dump(self.nodes, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving story nodes: {str(e)}")
            return False
