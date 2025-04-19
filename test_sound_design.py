"""
Test module for the sound design system
"""
import time
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

# Initialize the console
console = Console()

def main():
    """Main test function"""
    console.print(Panel("[cyan]CYBERPUNK SOUND DESIGN TEST[/cyan]", 
                       title="NEON SHADOWS", subtitle="Dynamic Audio Test"))
    
    # Import necessary modules
    console.print("[yellow]Initializing audio system...[/yellow]")
    try:
        import audio
        audio.initialize()
        import sound_design
    except ImportError as e:
        console.print(f"[bold red]Error importing modules: {e}[/bold red]")
        return
    
    # Generate example sounds if they don't exist
    console.print("[yellow]Checking for example sound effects...[/yellow]")
    if not os.path.exists("sounds/effects") or len(os.listdir("sounds/effects")) < 10:
        console.print("[yellow]Generating example sound effects for testing...[/yellow]")
        sound_design.generate_example_sounds()
    
    # Create the sound design system
    console.print("[yellow]Initializing sound design system...[/yellow]")
    sds = sound_design.SoundDesignSystem(audio)
    
    # Menu loop
    while True:
        show_test_menu(console)
        choice = Prompt.ask("[bold cyan]Choose a test option[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "8", "0"])
        
        if choice == "0":
            console.print("[yellow]Exiting test...[/yellow]")
            break
        elif choice == "1":
            test_district_ambience(console, sds)
        elif choice == "2":
            test_context_ambience(console, sds)
        elif choice == "3":
            test_event_sounds(console, sds)
        elif choice == "4":
            test_emotional_cues(console, sds)
        elif choice == "5":
            test_intensity_levels(console, sds)
        elif choice == "6":
            test_time_of_day(console, sds)
        elif choice == "7":
            test_danger_levels(console, sds)
        elif choice == "8":
            test_sound_sequence(console, sds)

def show_test_menu(console):
    """Display the test menu"""
    console.print("\n[bold cyan]SOUND DESIGN TEST MENU[/bold cyan]")
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan")
    table.add_column("Description", style="white")
    
    table.add_row("1", "Test District Ambience")
    table.add_row("2", "Test Gameplay Context Sounds")
    table.add_row("3", "Test Event Sounds")
    table.add_row("4", "Test Emotional Cues")
    table.add_row("5", "Test Intensity Levels")
    table.add_row("6", "Test Time of Day Effects")
    table.add_row("7", "Test Danger Level Effects")
    table.add_row("8", "Test Sound Sequence")
    table.add_row("0", "Exit Test")
    
    console.print(table)

def test_district_ambience(console, sds):
    """Test the district ambient sounds"""
    console.print("\n[bold cyan]DISTRICT AMBIENCE TEST[/bold cyan]")
    
    districts = list(sound_design.DISTRICT_SOUND_PROFILES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("District", style="white")
    
    for i, district in enumerate(districts, 1):
        # Capitalize and replace underscores with spaces
        district_name = district.replace('_', ' ').title()
        table.add_row(str(i), district_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice
    choices = [str(i) for i in range(len(districts) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a district[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    district_id = districts[int(choice) - 1]
    district_name = district_id.replace('_', ' ').title()
    
    console.print(f"[bold green]Playing ambience for {district_name}...[/bold green]")
    console.print("[yellow]Listen to the sounds for 15 seconds. Press Enter to stop.[/yellow]")
    
    # Play the district ambience
    sds.set_district(district_id)
    
    # Wait for Enter or timeout
    try:
        # Wait for 15 seconds or until Enter is pressed
        from threading import Event
        event = Event()
        
        def input_thread():
            input()
            event.set()
        
        import threading
        t = threading.Thread(target=input_thread, daemon=True)
        t.start()
        
        event.wait(timeout=15)
        
    except (KeyboardInterrupt, EOFError):
        pass  # Ignore keyboard interrupts
    
    console.print("[yellow]Returning to menu...[/yellow]")
    
    # Return to neutral
    sds.current_district = None
    sds._stop_ambient_threads()

def test_context_ambience(console, sds):
    """Test the gameplay context sounds"""
    console.print("\n[bold cyan]GAMEPLAY CONTEXT TEST[/bold cyan]")
    
    contexts = list(sound_design.CONTEXT_SOUND_PROFILES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Context", style="white")
    
    for i, context in enumerate(contexts, 1):
        # Capitalize and replace underscores with spaces
        context_name = context.replace('_', ' ').title()
        table.add_row(str(i), context_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice
    choices = [str(i) for i in range(len(contexts) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a gameplay context[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    context_id = contexts[int(choice) - 1]
    context_name = context_id.replace('_', ' ').title()
    
    console.print(f"[bold green]Playing sounds for {context_name} context...[/bold green]")
    console.print("[yellow]Listen to the sounds for 15 seconds. Press Enter to stop.[/yellow]")
    
    # Play the context ambience
    sds.set_context(context_id, intensity=0.5)  # Start at medium intensity
    
    # Wait for Enter or timeout
    try:
        # Wait for 15 seconds or until Enter is pressed
        from threading import Event
        event = Event()
        
        def input_thread():
            input()
            event.set()
        
        import threading
        t = threading.Thread(target=input_thread, daemon=True)
        t.start()
        
        event.wait(timeout=15)
        
    except (KeyboardInterrupt, EOFError):
        pass  # Ignore keyboard interrupts
    
    console.print("[yellow]Returning to menu...[/yellow]")
    
    # Return to neutral
    sds.current_context = None
    sds._stop_ambient_threads()

def test_event_sounds(console, sds):
    """Test the event sounds"""
    console.print("\n[bold cyan]EVENT SOUNDS TEST[/bold cyan]")
    
    # Group the events into categories
    event_categories = {
        "Character": ["level_up", "skill_unlock", "health_low", "health_critical", 
                    "reputation_increase", "reputation_decrease"],
        "Inventory": ["item_acquired", "weapon_equipped", "armor_equipped", 
                     "cybernetic_installed", "credits_received", "credits_spent"],
        "Environment": ["door_open", "door_locked", "terminal_access", 
                       "terminal_denied", "alarm_triggered", "security_alert"],
        "Travel": ["district_enter", "fast_travel", "vehicle_mount", "vehicle_dismount"],
        "UI": ["menu_open", "menu_close", "option_hover", "option_select", 
              "codex_update", "message_received"],
        "Narrative": ["story_milestone", "major_choice", "quest_start", 
                     "quest_complete", "quest_failed"]
    }
    
    # Let the user choose a category first
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Category", style="white")
    
    categories = list(event_categories.keys())
    for i, category in enumerate(categories, 1):
        table.add_row(str(i), category)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice for category
    choices = [str(i) for i in range(len(categories) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a category[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    category = categories[int(choice) - 1]
    events = event_categories[category]
    
    # Now let the user choose an event from the category
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Event", style="white")
    
    for i, event in enumerate(events, 1):
        # Format the event name for display
        event_name = event.replace('_', ' ').title()
        table.add_row(str(i), event_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice for event
    choices = [str(i) for i in range(len(events) + 1)]
    choice = Prompt.ask("[bold cyan]Choose an event[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    event = events[int(choice) - 1]
    event_name = event.replace('_', ' ').title()
    
    console.print(f"[bold green]Playing sound for {event_name} event...[/bold green]")
    
    # Play the event sound
    sds.play_event_sound(event)
    
    # Wait a moment to hear the sound
    time.sleep(2)

def test_emotional_cues(console, sds):
    """Test the emotional sound cues"""
    console.print("\n[bold cyan]EMOTIONAL CUES TEST[/bold cyan]")
    
    emotions = list(sound_design.EMOTIONAL_CUES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Emotion", style="white")
    
    for i, emotion in enumerate(emotions, 1):
        # Capitalize for display
        emotion_name = emotion.replace('_', ' ').title()
        table.add_row(str(i), emotion_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice
    choices = [str(i) for i in range(len(emotions) + 1)]
    choice = Prompt.ask("[bold cyan]Choose an emotional cue[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    emotion = emotions[int(choice) - 1]
    emotion_name = emotion.replace('_', ' ').title()
    
    console.print(f"[bold green]Playing emotional cue for {emotion_name}...[/bold green]")
    
    # Play the emotional cue
    sds.play_emotional_cue(emotion)
    
    # Wait a moment to hear the sound
    time.sleep(2)

def test_intensity_levels(console, sds):
    """Test different intensity levels for a context"""
    console.print("\n[bold cyan]INTENSITY LEVELS TEST[/bold cyan]")
    
    # Choose a context first
    contexts = list(sound_design.CONTEXT_SOUND_PROFILES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Context", style="white")
    
    for i, context in enumerate(contexts, 1):
        context_name = context.replace('_', ' ').title()
        table.add_row(str(i), context_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice for context
    choices = [str(i) for i in range(len(contexts) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a context[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    context_id = contexts[int(choice) - 1]
    context_name = context_id.replace('_', ' ').title()
    
    # Now test different intensity levels
    intensity_levels = [
        ("Low (beginning)", 0.1),
        ("Medium", 0.5),
        ("High", 0.8),
        ("Peak (climax)", 0.95)
    ]
    
    for level_name, intensity in intensity_levels:
        console.print(f"[bold green]Setting {context_name} intensity to {level_name}...[/bold green]")
        console.print("[yellow]Listen to the sounds for 10 seconds...[/yellow]")
        
        # Set the context with the specified intensity
        sds.set_context(context_id, intensity=intensity)
        
        # Wait for the sound to play
        time.sleep(10)
    
    console.print("[yellow]Intensity test complete.[/yellow]")
    
    # Return to neutral
    sds.current_context = None
    sds._stop_ambient_threads()

def test_time_of_day(console, sds):
    """Test the effect of time of day on district sounds"""
    console.print("\n[bold cyan]TIME OF DAY TEST[/bold cyan]")
    
    # Choose a district first
    districts = list(sound_design.DISTRICT_SOUND_PROFILES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("District", style="white")
    
    for i, district in enumerate(districts, 1):
        district_name = district.replace('_', ' ').title()
        table.add_row(str(i), district_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice for district
    choices = [str(i) for i in range(len(districts) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a district[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    district_id = districts[int(choice) - 1]
    district_name = district_id.replace('_', ' ').title()
    
    # Test both day and night
    for time_of_day in ["day", "night"]:
        console.print(f"[bold green]Setting {district_name} time to {time_of_day}...[/bold green]")
        console.print("[yellow]Listen to the sounds for 10 seconds...[/yellow]")
        
        # Set the district and time of day
        sds.set_time_of_day(time_of_day)
        sds.set_district(district_id)
        
        # Wait for the sound to play
        time.sleep(10)
    
    console.print("[yellow]Time of day test complete.[/yellow]")
    
    # Return to neutral
    sds.current_district = None
    sds._stop_ambient_threads()

def test_danger_levels(console, sds):
    """Test the effect of danger levels on district sounds"""
    console.print("\n[bold cyan]DANGER LEVEL TEST[/bold cyan]")
    
    # Choose a district first
    districts = list(sound_design.DISTRICT_SOUND_PROFILES.keys())
    
    table = Table(show_header=False, border_style="cyan")
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("District", style="white")
    
    for i, district in enumerate(districts, 1):
        district_name = district.replace('_', ' ').title()
        table.add_row(str(i), district_name)
    
    table.add_row("0", "Back to main menu")
    console.print(table)
    
    # Get user choice for district
    choices = [str(i) for i in range(len(districts) + 1)]
    choice = Prompt.ask("[bold cyan]Choose a district[/bold cyan]", choices=choices)
    
    if choice == "0":
        return
    
    district_id = districts[int(choice) - 1]
    district_name = district_id.replace('_', ' ').title()
    
    # Test different danger levels
    for danger_level in ["low", "medium", "high"]:
        console.print(f"[bold green]Setting {district_name} danger level to {danger_level}...[/bold green]")
        console.print("[yellow]Listen to the sounds for 10 seconds...[/yellow]")
        
        # Set the district and danger level
        sds.set_danger_level(danger_level)
        sds.set_district(district_id)
        
        # Wait for the sound to play
        time.sleep(10)
    
    console.print("[yellow]Danger level test complete.[/yellow]")
    
    # Return to neutral
    sds.current_district = None
    sds._stop_ambient_threads()

def test_sound_sequence(console, sds):
    """Test a sequence of sound cues that might occur during gameplay"""
    console.print("\n[bold cyan]SOUND SEQUENCE TEST[/bold cyan]")
    console.print("[yellow]This test will simulate a sequence of events that might occur during gameplay.[/yellow]")
    console.print("[yellow]Press Enter to begin...[/yellow]")
    input()
    
    # Start in the residential district (peaceful)
    console.print("[bold green]Starting in Residential District (peaceful)...[/bold green]")
    sds.set_district("residential")
    sds.set_time_of_day("day")
    sds.set_danger_level("low")
    time.sleep(5)
    
    # Receive a message
    console.print("[bold cyan]> You receive a message on your neural link.[/bold cyan]")
    sds.play_event_sound("message_received")
    time.sleep(3)
    
    # Transition to downtown
    console.print("[bold cyan]> You head downtown for a job.[/bold cyan]")
    sds.play_event_sound("district_enter")
    sds.set_district("downtown")
    time.sleep(5)
    
    # Enter a corporate building
    console.print("[bold cyan]> You enter a corporate building.[/bold cyan]")
    sds.play_event_sound("door_open")
    sds.set_district("corporate")
    time.sleep(5)
    
    # Hack a terminal
    console.print("[bold cyan]> You attempt to hack into a secure terminal.[/bold cyan]")
    sds.set_context("hacking", intensity=0.3)
    time.sleep(3)
    
    # Tension increases during hack
    console.print("[bold cyan]> The system detects your intrusion attempts.[/bold cyan]")
    sds.update_intensity(0.7)
    time.sleep(3)
    
    # Security alert
    console.print("[bold cyan]> Security systems are alerted![/bold cyan]")
    sds.play_event_sound("security_alert")
    sds.play_emotional_cue("tension")
    time.sleep(2)
    
    # Combat begins
    console.print("[bold cyan]> Security guards appear! Combat initiated.[/bold cyan]")
    sds.set_context("combat", intensity=0.4)
    time.sleep(5)
    
    # Combat intensifies
    console.print("[bold cyan]> The fight escalates![/bold cyan]")
    sds.update_intensity(0.8)
    time.sleep(5)
    
    # Take damage
    console.print("[bold cyan]> You take a serious hit![/bold cyan]")
    sds.play_event_sound("health_low")
    time.sleep(1)
    
    # Victory
    console.print("[bold cyan]> You defeat the guards![/bold cyan]")
    sds.play_emotional_cue("victory")
    time.sleep(3)
    
    # Escape to outskirts
    console.print("[bold cyan]> You escape to the city outskirts.[/bold cyan]")
    sds.play_event_sound("district_enter")
    sds.set_district("outskirts")
    sds.set_time_of_day("night")
    sds.set_danger_level("medium")
    time.sleep(5)
    
    # Quest complete
    console.print("[bold cyan]> Mission accomplished! Quest complete.[/bold cyan]")
    sds.play_event_sound("quest_complete")
    sds.play_emotional_cue("relief")
    time.sleep(3)
    
    # Return to residential
    console.print("[bold cyan]> You return to your apartment.[/bold cyan]")
    sds.play_event_sound("district_enter")
    sds.set_district("residential")
    sds.set_time_of_day("night")
    sds.set_danger_level("low")
    time.sleep(5)
    
    console.print("[bold green]Sound sequence complete![/bold green]")
    
    # Return to neutral
    sds.current_district = None
    sds.current_context = None
    sds._stop_ambient_threads()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Test interrupted. Exiting...[/bold yellow]")
        sys.exit(0)