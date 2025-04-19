#!/usr/bin/env python3
"""
Test script for the enhanced reputation system
"""
from districts import ReputationSystem, Faction, District, DistrictManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

def test_reputation_milestones():
    """Test the reputation milestone tracking system"""
    console.print(Panel.fit("Testing Reputation Milestone System", style="bold cyan"))
    
    # Create a reputation system
    rep_system = ReputationSystem()
    
    # Test district reputation changes and milestone tracking
    console.print("\n[bold green]Testing District Reputation Milestones[/]")
    changes = [
        {"district": "downtown", "amount": 25, "reason": "Helped local businesses"},
        {"district": "downtown", "amount": 20, "reason": "Completed district quest"},
        {"district": "undercity", "amount": -30, "reason": "Angered local gang"},
        {"district": "undercity", "amount": -15, "reason": "Failed to deliver promised goods"},
        {"district": "tech_row", "amount": 45, "reason": "Provided valuable tech info"},
        {"district": "corporate", "amount": -70, "reason": "Sabotaged corporate interests"}
    ]
    
    for change in changes:
        result = rep_system.modify_district_reputation(
            change["district"], 
            change["amount"], 
            change["reason"]
        )
        
        console.print(f"Changed {change['district']} reputation by {change['amount']} ({change['reason']})")
        console.print(f"  New value: {result['new_value']}")
        
        if result["milestone"]:
            console.print(f"  [bold yellow]MILESTONE REACHED:[/] {result['milestone']['description']} " +
                         f"({result['milestone']['threshold_type']})")
    
    # Test faction reputation changes and milestone tracking
    console.print("\n[bold green]Testing Faction Reputation Milestones[/]")
    changes = [
        {"faction": "arasaka", "amount": -45, "reason": "Leaked corporate data"},
        {"faction": "voodoo_boys", "amount": 35, "reason": "Helped with netrunning operation"},
        {"faction": "voodoo_boys", "amount": 30, "reason": "Retrieved valuable data"},
        {"faction": "police", "amount": -25, "reason": "Resisted arrest"},
        {"faction": "smugglers_guild", "amount": 60, "reason": "Completed several smuggling jobs"},
        {"faction": "jade_fist", "amount": 55, "reason": "Helped defend territory"}
    ]
    
    for change in changes:
        result = rep_system.modify_faction_reputation(
            change["faction"], 
            change["amount"], 
            None,  # No district manager for this test
            change["reason"]
        )
        
        console.print(f"Changed {change['faction']} reputation by {change['amount']} ({change['reason']})")
        console.print(f"  New value: {result['primary_change']['new_value']}")
        
        if result["primary_change"]["milestone"]:
            console.print(f"  [bold yellow]MILESTONE REACHED:[/] {result['primary_change']['milestone']['description']} " +
                         f"({result['primary_change']['milestone']['threshold_type']})")
        
        # Check for ripple effects on other factions
        if result["ripple_effects"]:
            console.print("  [bold cyan]Ripple effects on other factions:[/]")
            for faction, effect in result["ripple_effects"].items():
                console.print(f"    {faction}: {effect['change']} (new value: {effect['new_value']})")
                
                if "milestone" in effect and effect["milestone"]:
                    console.print(f"    [bold yellow]MILESTONE REACHED for {faction}:[/] " +
                                 f"{effect['milestone']['description']} ({effect['milestone']['threshold_type']})")


def test_faction_relationships():
    """Test the faction relationship system"""
    console.print(Panel.fit("Testing Faction Relationship System", style="bold cyan"))
    
    # Create a reputation system and district manager
    rep_system = ReputationSystem()
    district_manager = DistrictManager()
    
    # Make a significant change to one faction and observe ripple effects
    console.print("\n[bold green]Testing Major Faction Reputation Change[/]")
    
    # Test with a significant positive change to Arasaka
    result = rep_system.modify_faction_reputation(
        "arasaka",
        50,
        district_manager,
        "Completed major corporate contract"
    )
    
    # Create a table to display the results
    table = Table(title="Reputation Change Results")
    table.add_column("Target", style="cyan")
    table.add_column("Old Value", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("New Value", justify="right")
    table.add_column("Milestone", style="yellow")
    
    # Add primary change to table
    primary = result["primary_change"]
    milestone_text = (primary["milestone"]["description"] 
                     if "milestone" in primary and primary["milestone"] else "None")
    table.add_row("arasaka (primary)", 
                 str(primary["old_value"]), 
                 f"+{primary['change']}", 
                 str(primary["new_value"]),
                 milestone_text)
    
    # Add ripple effects to table
    for faction, effect in result["ripple_effects"].items():
        milestone_text = (effect["milestone"]["description"] 
                         if "milestone" in effect and effect["milestone"] else "None")
        table.add_row(faction, 
                     str(effect["old_value"]), 
                     str(effect["change"]), 
                     str(effect["new_value"]),
                     milestone_text)
    
    console.print(table)
    
    # Test district effects
    if "district_effects" in result and result["district_effects"]:
        console.print("\n[bold green]District Effects:[/]")
        for district, effect in result["district_effects"].items():
            console.print(f"District {district}: {effect['old_value']} → {effect['new_value']} " +
                         f"(change: {effect['change']})")
            if effect["milestone"]:
                console.print(f"  [bold yellow]MILESTONE REACHED:[/] {effect['milestone']['description']}")
    
    # Test with a significant negative change to a faction
    console.print("\n[bold green]Testing Negative Faction Reputation Change[/]")
    
    result = rep_system.modify_faction_reputation(
        "deep_collective",
        -60,
        district_manager,
        "Betrayed trust and sold out members"
    )
    
    # Create a table to display the results
    table = Table(title="Reputation Change Results")
    table.add_column("Target", style="cyan")
    table.add_column("Old Value", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("New Value", justify="right")
    table.add_column("Milestone", style="yellow")
    
    # Add primary change to table
    primary = result["primary_change"]
    milestone_text = (primary["milestone"]["description"] 
                     if "milestone" in primary and primary["milestone"] else "None")
    table.add_row("deep_collective (primary)", 
                 str(primary["old_value"]), 
                 str(primary["change"]), 
                 str(primary["new_value"]),
                 milestone_text)
    
    # Add ripple effects to table
    for faction, effect in result["ripple_effects"].items():
        milestone_text = (effect["milestone"]["description"] 
                         if "milestone" in effect and effect["milestone"] else "None")
        table.add_row(faction, 
                     str(effect["old_value"]), 
                     str(effect["change"]), 
                     str(effect["new_value"]),
                     milestone_text)
    
    console.print(table)


def test_faction_events():
    """Test faction-specific events based on reputation"""
    console.print(Panel.fit("Testing Faction-Specific Events", style="bold cyan"))
    
    # Create a reputation system
    rep_system = ReputationSystem()
    
    # Set up some test reputation values
    rep_system.faction_reputation["arasaka"] = 75
    rep_system.faction_reputation["voodoo_boys"] = 80
    rep_system.faction_reputation["police"] = -65
    rep_system.faction_reputation["smugglers_guild"] = 30
    
    # Get events for each faction
    for faction in ["arasaka", "voodoo_boys", "police", "smugglers_guild"]:
        console.print(f"\n[bold green]Events for {faction} (Reputation: {rep_system.faction_reputation[faction]})[/]")
        events = rep_system.get_faction_specific_events(faction)
        
        if events:
            for event in events:
                console.print(f"[bold cyan]{event['name']}[/] - {event['description']}")
                console.print(f"  Type: {event['type']}, ID: {event['id']}")
        else:
            console.print("No special events available.")


def test_district_events():
    """Test district-specific events based on reputation"""
    console.print(Panel.fit("Testing District-Specific Events", style="bold cyan"))
    
    # Create a reputation system
    rep_system = ReputationSystem()
    
    # Set up some test reputation values
    rep_system.district_reputation["downtown"] = 60
    rep_system.district_reputation["undercity"] = -70
    rep_system.district_reputation["tech_row"] = 50
    rep_system.district_reputation["digital_depths"] = 85
    
    # Get events for each district
    for district in ["downtown", "undercity", "tech_row", "digital_depths"]:
        console.print(f"\n[bold green]Events for {district} (Reputation: {rep_system.district_reputation[district]})[/]")
        events = rep_system.get_district_specific_events(district)
        
        if events:
            for event in events:
                console.print(f"[bold cyan]{event['name']}[/] - {event['description']}")
                console.print(f"  Type: {event['type']}, ID: {event['id']}")
        else:
            console.print("No special events available.")


if __name__ == "__main__":
    console.print("\n" + "="*80)
    console.print("REPUTATION SYSTEM TEST SUITE", style="bold green", justify="center")
    console.print("="*80 + "\n")
    
    # Run the tests
    test_reputation_milestones()
    print("\n")
    test_faction_relationships()
    print("\n")
    test_faction_events()
    print("\n")
    test_district_events()