#!/usr/bin/env python3
"""
Test script for the codex module and UI integration
"""
from rich.console import Console

import codex

def main():
    """Test the codex functionality non-interactively"""
    console = Console()
    print("Testing the codex functionality...")
    
    # Initialize codex
    test_codex = codex.Codex()
    
    # Check discovered entries
    discovered, total = test_codex.get_discovery_count()
    print(f"Codex has {discovered} discovered entries out of {total} total entries.")
    
    # Get categories with discovered entries
    available_categories = test_codex.get_categories_with_discovered_entries()
    print(f"Categories with discovered entries: {available_categories}")
    
    # Check entries in the 'world' category
    world_entries = test_codex.get_entries_by_category('world')
    print(f"Discovered 'world' entries: {[entry['title'] for entry in world_entries]}")
    
    # Check entries in the 'locations' category
    location_entries = test_codex.get_entries_by_category('locations')
    print(f"Discovered 'locations' entries: {[entry['title'] for entry in location_entries]}")
    
    # Get a specific entry
    neo_shanghai = test_codex.get_entry('neo_shanghai')
    if neo_shanghai:
        print(f"Neo Shanghai entry exists with title: {neo_shanghai['title']}")
    
    print("Testing complete!")

if __name__ == "__main__":
    main()