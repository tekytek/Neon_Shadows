"""
Demo script to showcase the sound design system capabilities
"""
import time
import os
from rich.console import Console
from rich.panel import Panel

# Initialize the console
console = Console()

def main():
    """Main function to run the sound design demo"""
    console.print(Panel("[cyan]CYBERPUNK SOUND DESIGN DEMO[/cyan]", 
                       title="NEON SHADOWS", subtitle="Dynamic Audio Showcase"))
    
    # Import necessary modules
    console.print("[yellow]Initializing audio system...[/yellow]")
    import audio
    audio.initialize()
    import sound_design
    
    # Generate example sounds if they don't exist
    console.print("[yellow]Checking for example sound effects...[/yellow]")
    if not os.path.exists("sounds/effects") or len(os.listdir("sounds/effects")) < 10:
        console.print("[yellow]Generating example sound effects for testing...[/yellow]")
        sound_design.generate_example_sounds()
    
    # Create the sound design system
    console.print("[yellow]Initializing sound design system...[/yellow]")
    sds = sound_design.SoundDesignSystem(audio)

    # Begin the interactive demo
    console.print("\n[bold cyan]SOUND DESIGN DEMO[/bold cyan]")
    console.print("[cyan]This script will run through a sequence of sound design events to showcase the system.[/cyan]")
    console.print("[cyan]Starting demo in 3 seconds...[/cyan]")
    time.sleep(3)
    
    # PART 1: District Ambience
    console.print("\n[bold green]PART 1: DISTRICT AMBIENCE[/bold green]")
    console.print("[yellow]Traveling to Downtown district...[/yellow]")
    
    # Set district ambience for downtown
    sds.play_event_sound("district_enter")
    sds.set_time_of_day("day")
    sds.set_danger_level("low")
    sds.set_district("downtown")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the ambient sounds of Downtown during daytime (low danger)...[/cyan]")
    time.sleep(8)
    
    # Change to night time in downtown
    console.print("\n[yellow]Time passes, night falls over Downtown...[/yellow]")
    sds.set_time_of_day("night")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the ambient sounds of Downtown at night...[/cyan]")
    time.sleep(8)
    
    # Increase danger level
    console.print("\n[red]Danger level increasing in Downtown![/red]")
    sds.set_danger_level("high")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the ambient sounds of Downtown at night with high danger...[/cyan]")
    time.sleep(8)
    
    # PART 2: Context Transitions
    console.print("\n[bold green]PART 2: GAMEPLAY CONTEXT TRANSITIONS[/bold green]")
    
    # Transition to combat
    console.print("\n[red]Enemies spotted! Combat initiated.[/red]")
    sds.play_emotional_cue("tension")
    sds.set_context("combat", intensity=0.3)
    
    # Give user some time to listen
    console.print("[cyan]Listen to initial combat sounds (low intensity)...[/cyan]")
    time.sleep(8)
    
    # Increase combat intensity
    console.print("\n[red]Combat intensifies![/red]")
    sds.update_intensity(0.8)
    
    # Give user some time to listen
    console.print("[cyan]Listen to intense combat sounds (high intensity)...[/cyan]")
    time.sleep(8)
    
    # Victory in combat
    console.print("\n[green]Combat victory![/green]")
    sds.play_emotional_cue("victory")
    time.sleep(3)
    
    # Return to district
    console.print("\n[yellow]Returning to district ambience...[/yellow]")
    sds.return_to_district_ambience()
    time.sleep(5)
    
    # PART 3: District Transitions
    console.print("\n[bold green]PART 3: DISTRICT TRANSITIONS[/bold green]")
    
    # Travel to industrial zone
    console.print("\n[yellow]Traveling to Industrial Zone...[/yellow]")
    sds.play_event_sound("district_enter")
    sds.set_district("industrial")
    sds.set_time_of_day("day")
    sds.set_danger_level("medium")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the Industrial Zone ambience...[/cyan]")
    time.sleep(8)
    
    # Travel to nightmarket
    console.print("\n[yellow]Traveling to Night Market...[/yellow]")
    sds.play_event_sound("district_enter")
    sds.set_district("nightmarket")
    sds.set_time_of_day("night")
    sds.set_danger_level("medium")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the Night Market ambience...[/cyan]")
    time.sleep(8)
    
    # PART 4: Event Sounds
    console.print("\n[bold green]PART 4: EVENT SOUNDS & EMOTIONAL CUES[/bold green]")
    
    # Level up event
    console.print("\n[green]You've gained enough experience to level up![/green]")
    sds.play_event_sound("level_up")
    time.sleep(3)
    
    # Item acquisition
    console.print("\n[green]You found a rare item![/green]")
    sds.play_event_sound("item_acquired")
    time.sleep(3)
    
    # Reputation increase
    console.print("\n[green]Your reputation in the Night Market has increased![/green]")
    sds.play_event_sound("reputation_increase")
    time.sleep(3)
    
    # Quest completion
    console.print("\n[green]Quest completed: 'The Market Heist'[/green]")
    sds.play_event_sound("quest_complete")
    sds.play_emotional_cue("triumph")
    time.sleep(3)
    
    # PART 5: Stealth Context
    console.print("\n[bold green]PART 5: STEALTH CONTEXT[/bold green]")
    
    # Transition to corporate sector with stealth
    console.print("\n[yellow]Infiltrating the Corporate Sector...[/yellow]")
    sds.play_event_sound("district_enter")
    sds.set_district("corporate")
    time.sleep(2)
    
    console.print("\n[yellow]Initiating stealth operation...[/yellow]")
    sds.set_context("stealth", intensity=0.4)
    
    # Give user some time to listen
    console.print("[cyan]Listen to the stealth context sounds...[/cyan]")
    time.sleep(8)
    
    # Increase stealth tension
    console.print("\n[red]Guard patrol approaching! Tension increases...[/red]")
    sds.update_intensity(0.9)
    
    # Give user some time to listen
    console.print("[cyan]Listen to the high-tension stealth sounds...[/cyan]")
    time.sleep(8)
    
    # Alert triggered
    console.print("\n[red]Alert triggered! Security system detects intruder![/red]")
    sds.play_event_sound("alarm_triggered")
    sds.play_emotional_cue("tension")
    time.sleep(3)
    
    # PART 6: End Sequence
    console.print("\n[bold green]PART 6: ENDING SEQUENCE[/bold green]")
    
    # Escape to residential
    console.print("\n[yellow]Escaping to Residential Sector...[/yellow]")
    sds.play_event_sound("district_enter")
    sds.set_district("residential")
    sds.set_time_of_day("night")
    sds.set_danger_level("low")
    
    # Give user some time to listen
    console.print("[cyan]Listen to the peaceful residential district sounds at night...[/cyan]")
    time.sleep(8)
    
    # Final emotional cue - relief
    console.print("\n[green]Mission accomplished. You're safe at your apartment.[/green]")
    sds.play_emotional_cue("relief")
    time.sleep(4)
    
    # Demo complete
    console.print("\n[bold magenta]Sound Design Demo Complete![/bold magenta]")
    console.print("[cyan]Press Enter to exit...[/cyan]")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Demo interrupted. Exiting...[/bold yellow]")