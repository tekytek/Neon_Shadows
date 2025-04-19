"""
Sound Design Module - Provides dynamic audio cues and atmospheric sound design
"""
import os
import random
import threading
import time
from typing import Dict, List, Optional, Tuple

# Dictionary mapping district types to their sound profiles
DISTRICT_SOUND_PROFILES = {
    "downtown": {
        "ambient": "downtown_ambient",
        "music": "downtown_theme",
        "procedural_sounds": [
            "city_traffic", "crowd_voices", "police_siren", "corporate_announcement",
            "hovercars_passing", "advertisement_jingle"
        ],
        "situational_sounds": {
            "day": ["busy_street", "construction_work", "traffic_jam"],
            "night": ["nighttime_traffic", "distant_music", "drone_patrol"],
            "danger": ["police_alarm", "corporate_alert", "security_drone"]
        },
        "probability_weights": {
            "ambient": 1.0,        # Always play ambient
            "procedural": 0.7,     # 70% chance of procedural sounds
            "situational": 0.5     # 50% chance of situational sounds
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.5
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.2,
                "frequency_modifier": 1.5
            }
        }
    },
    "industrial": {
        "ambient": "industrial_ambient",
        "music": "industrial_theme",
        "procedural_sounds": [
            "machinery_hum", "factory_alarm", "metal_impact", "steam_release",
            "robotic_movement", "forge_sounds", "electric_spark"
        ],
        "situational_sounds": {
            "day": ["heavy_machinery", "worker_voices", "loading_dock"],
            "night": ["night_shift", "distant_alarm", "patrol_drones"],
            "danger": ["warning_siren", "gang_presence", "security_alert"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.8,
            "situational": 0.6
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.5
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.3,
                "frequency_modifier": 1.8
            }
        }
    },
    "residential": {
        "ambient": "residential_ambient",
        "music": "residential_theme",
        "procedural_sounds": [
            "apartment_noises", "domestic_argument", "door_closing", "dog_barking",
            "tv_static", "children_playing", "elevator_ding"
        ],
        "situational_sounds": {
            "day": ["community_chatter", "delivery_drone", "street_vendor"],
            "night": ["distant_music", "apartment_party", "insomnia_noise"],
            "danger": ["police_raid", "gang_activity", "domestic_dispute"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.5,
            "situational": 0.4
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.6,
                "frequency_modifier": 0.3
            },
            "medium": {
                "volume_modifier": 0.8,
                "frequency_modifier": 0.8
            },
            "high": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.2
            }
        }
    },
    "outskirts": {
        "ambient": "outskirts_ambient",
        "music": "outskirts_theme",
        "procedural_sounds": [
            "wind_through_ruins", "distant_gunshot", "scavenger_sounds", "metal_creaking",
            "broken_machinery", "wild_dog", "motorcycle_gang"
        ],
        "situational_sounds": {
            "day": ["scavengers_working", "makeshift_market", "vehicle_scrapyard"],
            "night": ["gang_patrol", "illegal_races", "distant_explosion"],
            "danger": ["gang_warfare", "security_drone", "automated_defense"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.6,
            "situational": 0.7
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.5
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.4,
                "frequency_modifier": 1.7
            }
        }
    },
    "corporate": {
        "ambient": "corporate_ambient",
        "music": "corporate_theme",
        "procedural_sounds": [
            "air_conditioning", "elevator_movement", "typing_sounds", "clean_footsteps",
            "corporate_announcement", "security_scanner", "automated_door"
        ],
        "situational_sounds": {
            "day": ["business_meeting", "corporate_lobby", "secretary_desk"],
            "night": ["security_patrol", "cleaning_robots", "system_maintenance"],
            "danger": ["security_alert", "lockdown_alarm", "breach_protocol"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.4,
            "situational": 0.3
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.5,
                "frequency_modifier": 0.4
            },
            "medium": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.7
            },
            "high": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            }
        }
    },
    "nightmarket": {
        "ambient": "nightmarket_ambient",
        "music": "nightmarket_theme",
        "procedural_sounds": [
            "crowd_chatter", "vendor_calls", "street_music", "food_sizzling",
            "haggling_voices", "trinket_sounds", "drone_delivery"
        ],
        "situational_sounds": {
            "day": ["market_setup", "delivery_trucks", "vendor_arrangement"],
            "night": ["night_crowd", "music_performance", "exotic_goods"],
            "danger": ["pickpocket_chase", "vendor_argument", "gang_shakedown"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.9,
            "situational": 0.8
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.8,
                "frequency_modifier": 0.7
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.2,
                "frequency_modifier": 1.4
            }
        }
    },
    "entertainment": {
        "ambient": "entertainment_ambient",
        "music": "entertainment_theme",
        "procedural_sounds": [
            "club_music", "laughter", "virtual_reality_hum", "slot_machines",
            "cheering_crowd", "gambling_chips", "drink_pouring"
        ],
        "situational_sounds": {
            "day": ["cleaning_crew", "deliveries", "system_check"],
            "night": ["nightclub_beat", "casino_activity", "vr_tournament"],
            "danger": ["club_fight", "security_intervention", "rigged_game"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.9,
            "situational": 0.7
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.8,
                "frequency_modifier": 0.6
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.3,
                "frequency_modifier": 1.5
            }
        }
    },
    "upscale": {
        "ambient": "upscale_ambient",
        "music": "upscale_theme",
        "procedural_sounds": [
            "fountain_water", "soft_music", "high_heels", "expensive_cars",
            "gallery_chatter", "champagne_pouring", "digital_art_installation"
        ],
        "situational_sounds": {
            "day": ["gallery_opening", "business_lunch", "shopping_district"],
            "night": ["exclusive_party", "security_patrol", "rooftop_lounge"],
            "danger": ["security_alert", "art_theft_alarm", "police_response"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.5,
            "situational": 0.4
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.5,
                "frequency_modifier": 0.4
            },
            "medium": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.7
            },
            "high": {
                "volume_modifier": 0.9,
                "frequency_modifier": 1.0
            }
        }
    },
    "wasteland": {
        "ambient": "wasteland_ambient",
        "music": "wasteland_theme",
        "procedural_sounds": [
            "toxic_wind", "distant_thunder", "metal_creaking", "wildlife_calls",
            "acid_rain", "radiation_detector", "scavenger_vehicle"
        ],
        "situational_sounds": {
            "day": ["scavenging_party", "mutant_call", "dust_storm"],
            "night": ["predator_howl", "distant_campfire", "night_scavengers"],
            "danger": ["mutant_attack", "raider_vehicles", "toxic_storm"]
        },
        "probability_weights": {
            "ambient": 1.0,
            "procedural": 0.8,
            "situational": 0.9
        },
        "intensity_levels": {
            "low": {
                "volume_modifier": 0.7,
                "frequency_modifier": 0.6
            },
            "medium": {
                "volume_modifier": 1.0,
                "frequency_modifier": 1.0
            },
            "high": {
                "volume_modifier": 1.5,
                "frequency_modifier": 2.0
            }
        }
    }
}

# Dictionary mapping gameplay contexts to their sound profiles
CONTEXT_SOUND_PROFILES = {
    "combat": {
        "ambient": "combat_tension",
        "music": "combat_theme",
        "procedural_sounds": [
            "gunshot_echo", "bullet_impact", "combat_movement", "reload_sound",
            "cybernetic_activation", "health_warning", "tactical_alert"
        ],
        "intensity_curve": [
            (0, "low"),      # First 0% of combat - low intensity
            (0.3, "medium"),  # After 30% of combat - medium intensity
            (0.7, "high"),    # After 70% of combat - high intensity
            (0.9, "peak")     # Final 10% of combat - peak intensity
        ]
    },
    "hacking": {
        "ambient": "digital_ambient",
        "music": "hacking_theme",
        "procedural_sounds": [
            "data_transfer", "firewall_alert", "system_access", "encryption_breaking",
            "digital_glitch", "connection_established", "system_warning"
        ],
        "intensity_curve": [
            (0, "low"),
            (0.4, "medium"),
            (0.75, "high"),
            (0.9, "peak")
        ]
    },
    "stealth": {
        "ambient": "stealth_tension",
        "music": "stealth_theme",
        "procedural_sounds": [
            "quiet_footstep", "camera_movement", "guard_patrol", "door_unlocking",
            "alarm_sensor", "security_radio", "distant_guard"
        ],
        "intensity_curve": [
            (0, "low"),
            (0.5, "medium"),
            (0.8, "high"),
            (0.9, "peak")
        ]
    },
    "conversation": {
        "ambient": "social_ambient",
        "music": "dialogue_theme",
        "procedural_sounds": [
            "ambient_chatter", "drink_pouring", "chair_movement", "distant_laughter",
            "phone_notification", "cigarette_lighting", "glass_clinking"
        ],
        "intensity_curve": [
            (0, "low"),
            (0.6, "medium"),
            (0.9, "high")
        ]
    },
    "shopping": {
        "ambient": "marketplace_ambient",
        "music": "shopping_theme",
        "procedural_sounds": [
            "transaction_beep", "packaging_sound", "item_examination", "haggling_voices",
            "counter_tap", "digital_catalog", "credit_transfer"
        ],
        "intensity_curve": [
            (0, "low"),
            (0.5, "medium"),
            (0.8, "high")
        ]
    }
}

# Dictionary of event-triggered sounds
EVENT_SOUNDS = {
    # Character status events
    "level_up": "level_up",
    "skill_unlock": "skill_unlock",
    "health_low": "health_warning",
    "health_critical": "critical_warning",
    "reputation_increase": "reputation_up",
    "reputation_decrease": "reputation_down",
    
    # Inventory and item events
    "item_acquired": "item_pickup",
    "weapon_equipped": "weapon_equip",
    "armor_equipped": "armor_equip",
    "cybernetic_installed": "cyber_install",
    "credits_received": "credit_transfer",
    "credits_spent": "credit_payment",
    
    # Environmental events
    "door_open": "door_open",
    "door_locked": "door_locked",
    "terminal_access": "terminal_access",
    "terminal_denied": "access_denied",
    "alarm_triggered": "alarm_triggered",
    "security_alert": "security_alert",
    
    # Travel and movement events
    "district_enter": "district_transition",
    "fast_travel": "fast_travel",
    "vehicle_mount": "vehicle_start",
    "vehicle_dismount": "vehicle_stop",
    
    # UI events
    "menu_open": "menu_open",
    "menu_close": "menu_close",
    "option_hover": "option_hover",
    "option_select": "option_select",
    "codex_update": "codex_update",
    "message_received": "message_notification",
    
    # Narrative events
    "story_milestone": "milestone_achieved",
    "major_choice": "important_decision",
    "quest_start": "quest_accepted",
    "quest_complete": "quest_complete",
    "quest_failed": "quest_failed"
}

# Emotional response triggers for narrative moments
EMOTIONAL_CUES = {
    "tension": "tension_rise",
    "relief": "tension_release",
    "revelation": "revelation",
    "loss": "somber_moment",
    "victory": "triumph",
    "betrayal": "betrayal",
    "mystery": "mystery",
    "horror": "horror",
    "wonder": "wonder"
}

class SoundDesignSystem:
    """Manages dynamic audio cues and atmospheric sound design"""
    
    def __init__(self, audio_system=None):
        """Initialize the sound design system
        
        Args:
            audio_system: Reference to the game's audio system
        """
        self.audio_system = audio_system
        self.active_threads = []
        self.current_district = None
        self.current_context = None
        self.time_of_day = "day"  # Could be "day" or "night"
        self.danger_level = "low"  # Could be "low", "medium", or "high"
        self.ambient_thread = None
        self.procedural_thread = None
        
        # Create sounds directories
        os.makedirs('sounds/ambient', exist_ok=True)
        os.makedirs('sounds/procedural', exist_ok=True)
        os.makedirs('sounds/events', exist_ok=True)
        os.makedirs('sounds/emotional', exist_ok=True)
        
    def set_district(self, district_id):
        """Set the current district and update audio atmosphere
        
        Args:
            district_id (str): ID of the district to set as current
        """
        if not self.audio_system:
            return
            
        self.current_district = district_id
        self._stop_ambient_threads()
        
        # Start new district-specific ambience
        sound_profile = DISTRICT_SOUND_PROFILES.get(district_id)
        if sound_profile:
            # Play the district ambient music
            self.audio_system.play_music(sound_profile.get("music", "cyberpunk_ambient"))
            
            # Start ambient sound thread
            self._start_ambient_thread(district_id)
    
    def set_context(self, context_type, intensity=0.0):
        """Set the current gameplay context and update audio atmosphere
        
        Args:
            context_type (str): Type of gameplay context (combat, hacking, etc.)
            intensity (float): Initial intensity level (0.0 to 1.0)
        """
        if not self.audio_system:
            return
            
        self.current_context = context_type
        self._stop_ambient_threads()
        
        # Start new context-specific ambience
        sound_profile = CONTEXT_SOUND_PROFILES.get(context_type)
        if sound_profile:
            # Play the context-specific music
            self.audio_system.play_music(sound_profile.get("music", "cyberpunk_ambient"))
            
            # Determine intensity level based on the intensity curve
            intensity_level = self._get_intensity_level(context_type, intensity)
            
            # Start context sound thread
            self._start_context_thread(context_type, intensity_level)
    
    def update_intensity(self, intensity):
        """Update the current context intensity
        
        Args:
            intensity (float): New intensity level (0.0 to 1.0)
        """
        if not self.audio_system or not self.current_context:
            return
            
        # Determine intensity level based on the intensity curve
        intensity_level = self._get_intensity_level(self.current_context, intensity)
        
        # Update the context thread with new intensity
        self._update_context_intensity(intensity_level)
    
    def set_time_of_day(self, time_of_day):
        """Set the current time of day for appropriate ambient sounds
        
        Args:
            time_of_day (str): Time of day ("day" or "night")
        """
        self.time_of_day = time_of_day
        
        # If we're in a district, update the ambient sounds
        if self.current_district and not self.current_context:
            self._stop_ambient_threads()
            self._start_ambient_thread(self.current_district)
    
    def set_danger_level(self, danger_level):
        """Set the current danger level for appropriate ambient sounds
        
        Args:
            danger_level (str): Danger level ("low", "medium", or "high")
        """
        self.danger_level = danger_level
        
        # If we're in a district, update the ambient sounds
        if self.current_district and not self.current_context:
            self._stop_ambient_threads()
            self._start_ambient_thread(self.current_district)
    
    def play_event_sound(self, event_type):
        """Play a sound effect for a specific game event
        
        Args:
            event_type (str): Type of event from EVENT_SOUNDS dictionary
        """
        if not self.audio_system:
            return
            
        sound_name = EVENT_SOUNDS.get(event_type)
        if sound_name:
            self.audio_system.play_sound(sound_name)
    
    def play_emotional_cue(self, emotion_type):
        """Play an emotional sound cue for narrative moments
        
        Args:
            emotion_type (str): Type of emotion from EMOTIONAL_CUES dictionary
        """
        if not self.audio_system:
            return
            
        sound_name = EMOTIONAL_CUES.get(emotion_type)
        if sound_name:
            self.audio_system.play_sound(sound_name)
    
    def return_to_district_ambience(self):
        """Return to the current district's ambient sound profile"""
        if not self.audio_system or not self.current_district:
            return
            
        self.current_context = None
        self.set_district(self.current_district)
    
    def _start_ambient_thread(self, district_id):
        """Start a thread to play ambient and procedural sounds for a district
        
        Args:
            district_id (str): ID of the district for which to play sounds
        """
        if not self.audio_system:
            return
            
        sound_profile = DISTRICT_SOUND_PROFILES.get(district_id)
        if not sound_profile:
            return
            
        # Start the ambient thread
        def ambient_thread_func():
            while True:
                # Check if procedural sounds should play
                if random.random() < sound_profile["probability_weights"]["procedural"]:
                    # Select a random procedural sound
                    if sound_profile["procedural_sounds"]:
                        sound_name = random.choice(sound_profile["procedural_sounds"])
                        try:
                            self.audio_system.play_sound(sound_name)
                        except Exception:
                            pass  # Ignore if sound doesn't exist
                
                # Check if situational sounds should play
                if random.random() < sound_profile["probability_weights"]["situational"]:
                    # Get situation based on time of day or danger level
                    situation = self.time_of_day
                    if self.danger_level == "high":
                        situation = "danger"
                        
                    # Select a random situational sound
                    situational_sounds = sound_profile["situational_sounds"].get(situation, [])
                    if situational_sounds:
                        sound_name = random.choice(situational_sounds)
                        try:
                            self.audio_system.play_sound(sound_name)
                        except Exception:
                            pass  # Ignore if sound doesn't exist
                
                # Wait a random amount of time before next sound
                intensity_modifier = sound_profile["intensity_levels"].get(
                    self.danger_level, {"frequency_modifier": 1.0}
                )["frequency_modifier"]
                
                wait_time = random.uniform(3.0, 15.0) / intensity_modifier
                time.sleep(wait_time)
        
        # Start the thread
        self.ambient_thread = threading.Thread(target=ambient_thread_func, daemon=True)
        self.ambient_thread.start()
        self.active_threads.append(self.ambient_thread)
    
    def _start_context_thread(self, context_type, intensity_level):
        """Start a thread to play ambient and procedural sounds for a gameplay context
        
        Args:
            context_type (str): Type of gameplay context
            intensity_level (str): Intensity level ("low", "medium", "high", "peak")
        """
        if not self.audio_system:
            return
            
        context_profile = CONTEXT_SOUND_PROFILES.get(context_type)
        if not context_profile:
            return
            
        # Start the procedural thread
        def procedural_thread_func():
            while True:
                # Select a random procedural sound
                if context_profile["procedural_sounds"]:
                    sound_name = random.choice(context_profile["procedural_sounds"])
                    try:
                        self.audio_system.play_sound(sound_name)
                    except Exception:
                        pass  # Ignore if sound doesn't exist
                
                # Wait time based on intensity level
                if intensity_level == "low":
                    wait_time = random.uniform(5.0, 15.0)
                elif intensity_level == "medium":
                    wait_time = random.uniform(3.0, 8.0)
                elif intensity_level == "high":
                    wait_time = random.uniform(1.5, 5.0)
                else:  # "peak"
                    wait_time = random.uniform(0.8, 2.0)
                    
                time.sleep(wait_time)
        
        # Start the thread
        self.procedural_thread = threading.Thread(target=procedural_thread_func, daemon=True)
        self.procedural_thread.start()
        self.active_threads.append(self.procedural_thread)
    
    def _update_context_intensity(self, intensity_level):
        """Update the context sounds based on new intensity level
        
        Args:
            intensity_level (str): New intensity level
        """
        # For now, just restart the thread with the new intensity
        # In a more complex implementation, we could smoothly transition
        if self.procedural_thread and self.procedural_thread.is_alive():
            self._stop_ambient_threads()
            self._start_context_thread(self.current_context, intensity_level)
    
    def _get_intensity_level(self, context_type, intensity):
        """Determine the intensity level based on the context's intensity curve
        
        Args:
            context_type (str): Type of gameplay context
            intensity (float): Intensity value (0.0 to 1.0)
            
        Returns:
            str: Intensity level ("low", "medium", "high", or "peak")
        """
        context_profile = CONTEXT_SOUND_PROFILES.get(context_type)
        if not context_profile or "intensity_curve" not in context_profile:
            return "medium"
            
        # Find the appropriate intensity level based on the curve
        curve = context_profile["intensity_curve"]
        for threshold, level in reversed(curve):
            if intensity >= threshold:
                return level
                
        return "low"  # Default to low if no threshold is met
    
    def _stop_ambient_threads(self):
        """Stop all running ambient sound threads"""
        # Mark threads for cleanup
        self.active_threads = [t for t in self.active_threads if t.is_alive()]
        self.ambient_thread = None
        self.procedural_thread = None

# Add function to generate example sound effects for testing
def generate_example_sounds():
    """Generate example sound effects for testing the sound design system"""
    try:
        from scipy.io import wavfile
        import numpy as np
        
        sample_rate = 44100
        
        # Generate district ambient sounds (short samples for testing)
        for district in DISTRICT_SOUND_PROFILES:
            # Create a simple ambient sound
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Generate different sounds for different districts
            if district == "downtown":
                signal = np.sin(2 * np.pi * 100 * t) * 0.1 + (np.random.rand(len(t)) - 0.5) * 0.2
            elif district == "industrial":
                signal = np.sin(2 * np.pi * 80 * t) * 0.15 + np.sin(2 * np.pi * 120 * t) * 0.05
            elif district == "residential":
                signal = np.sin(2 * np.pi * 200 * t) * 0.05 + (np.random.rand(len(t)) - 0.5) * 0.1
            elif district == "outskirts":
                signal = np.sin(2 * np.pi * 50 * t) * 0.1 + (np.random.rand(len(t)) - 0.5) * 0.3
            elif district == "corporate":
                signal = np.sin(2 * np.pi * 300 * t) * 0.03 + (np.random.rand(len(t)) - 0.5) * 0.05
            elif district == "nightmarket":
                signal = np.sin(2 * np.pi * 150 * t) * 0.1 + (np.random.rand(len(t)) - 0.5) * 0.3
            elif district == "entertainment":
                signal = np.sin(2 * np.pi * 220 * t) * 0.1 + np.sin(2 * np.pi * 440 * t) * 0.05
            elif district == "upscale":
                signal = np.sin(2 * np.pi * 350 * t) * 0.07 + (np.random.rand(len(t)) - 0.5) * 0.05
            elif district == "wasteland":
                signal = np.sin(2 * np.pi * 30 * t) * 0.2 + (np.random.rand(len(t)) - 0.5) * 0.4
            else:
                signal = np.sin(2 * np.pi * 220 * t) * 0.1
                
            # Save the ambient sound
            os.makedirs('sounds/music', exist_ok=True)
            filename = os.path.join('sounds', 'music', f"{district}_theme.wav")
            wavfile.write(filename, sample_rate, signal.astype(np.float32))
            
            # Save a few procedural sounds for each district
            os.makedirs('sounds/effects', exist_ok=True)
            procedural_sounds = DISTRICT_SOUND_PROFILES[district]["procedural_sounds"][:3]  # Just first 3 for demo
            for sound_name in procedural_sounds:
                duration = 0.5
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                
                # Create a unique sound based on the name's hash
                hash_val = sum(ord(c) for c in sound_name)
                freq = 200 + (hash_val % 500)
                
                signal = np.sin(2 * np.pi * freq * t) * 0.2 * np.exp(-3 * t)
                
                filename = os.path.join('sounds', 'effects', f"{sound_name}.wav")
                wavfile.write(filename, sample_rate, signal.astype(np.float32))
        
        # Generate context sounds
        for context in CONTEXT_SOUND_PROFILES:
            # Create a context theme
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            if context == "combat":
                signal = np.sin(2 * np.pi * 150 * t) * 0.2 + np.sin(2 * np.pi * 180 * t) * 0.1
            elif context == "hacking":
                signal = np.sin(2 * np.pi * 300 * t) * 0.15 + np.sin(2 * np.pi * 303 * t) * 0.15
            elif context == "stealth":
                signal = np.sin(2 * np.pi * 100 * t) * 0.1 + (np.random.rand(len(t)) - 0.5) * 0.05
            elif context == "conversation":
                signal = np.sin(2 * np.pi * 250 * t) * 0.08 + np.sin(2 * np.pi * 253 * t) * 0.08
            elif context == "shopping":
                signal = np.sin(2 * np.pi * 350 * t) * 0.07 + np.sin(2 * np.pi * 175 * t) * 0.05
            else:
                signal = np.sin(2 * np.pi * 220 * t) * 0.1
                
            # Save the context theme
            filename = os.path.join('sounds', 'music', f"{context}_theme.wav")
            wavfile.write(filename, sample_rate, signal.astype(np.float32))
            
            # Save a few procedural sounds for each context
            procedural_sounds = CONTEXT_SOUND_PROFILES[context]["procedural_sounds"][:3]  # Just first 3 for demo
            for sound_name in procedural_sounds:
                duration = 0.5
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                
                # Create a unique sound based on the name's hash
                hash_val = sum(ord(c) for c in sound_name)
                freq = 300 + (hash_val % 700)
                
                signal = np.sin(2 * np.pi * freq * t) * 0.2 * np.exp(-5 * t)
                
                filename = os.path.join('sounds', 'effects', f"{sound_name}.wav")
                wavfile.write(filename, sample_rate, signal.astype(np.float32))
        
        # Generate event sounds
        for event, sound_name in EVENT_SOUNDS.items():
            duration = 0.4
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Create a unique sound based on the event name's hash
            hash_val = sum(ord(c) for c in event)
            freq1 = 400 + (hash_val % 800)
            freq2 = 200 + (hash_val % 400)
            
            signal = np.sin(2 * np.pi * freq1 * t) * 0.15 + np.sin(2 * np.pi * freq2 * t) * 0.1
            signal = signal * np.exp(-4 * t)
            
            filename = os.path.join('sounds', 'effects', f"{sound_name}.wav")
            wavfile.write(filename, sample_rate, signal.astype(np.float32))
        
        # Generate emotional cues
        for emotion, sound_name in EMOTIONAL_CUES.items():
            duration = 1.5
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Create a unique sound based on the emotion name's hash
            hash_val = sum(ord(c) for c in emotion)
            freq1 = 200 + (hash_val % 300)
            freq2 = 400 + (hash_val % 500)
            
            # Different emotions have different patterns
            if emotion in ["tension", "horror"]:
                signal = np.sin(2 * np.pi * freq1 * t) * 0.2 * (1 + t/duration)
            elif emotion in ["relief", "victory"]:
                signal = np.sin(2 * np.pi * np.linspace(freq1, freq2, len(t)) * t) * 0.2
            elif emotion in ["revelation", "wonder"]:
                signal = np.sin(2 * np.pi * freq2 * t) * 0.15 * (1 - np.exp(-2 * t))
            elif emotion in ["loss", "betrayal"]:
                signal = np.sin(2 * np.pi * freq1 * t) * 0.15 * np.exp(-1 * t)
            else:
                signal = np.sin(2 * np.pi * freq1 * t) * 0.15
                
            filename = os.path.join('sounds', 'effects', f"{sound_name}.wav")
            wavfile.write(filename, sample_rate, signal.astype(np.float32))
            
        print("Created example sound effects for dynamic audio system.")
    except ImportError:
        print("Could not create example sounds: scipy not installed")
        
        # Create empty files as placeholders
        os.makedirs('sounds/music', exist_ok=True)
        os.makedirs('sounds/effects', exist_ok=True)
        
        # Create empty files for district themes
        for district in DISTRICT_SOUND_PROFILES:
            open(os.path.join('sounds', 'music', f"{district}_theme.wav"), 'w').close()
        
        # Create empty files for context themes
        for context in CONTEXT_SOUND_PROFILES:
            open(os.path.join('sounds', 'music', f"{context}_theme.wav"), 'w').close()