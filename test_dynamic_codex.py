#!/usr/bin/env python3
"""
Test script for the dynamic codex content generation with Ollama
"""
from rich.console import Console

import codex
from config import USE_OLLAMA

def main():
    """Test the dynamic codex content generation with Ollama"""
    console = Console()
    print("Testing the dynamic codex content generation with Ollama...")
    
    # Initialize codex
    test_codex = codex.Codex()
    
    # Check if Ollama is enabled
    print(f"Ollama integration is {'enabled' if USE_OLLAMA else 'disabled'}")
    print("Note: When running in Replit, Ollama may not be available even if enabled in config.")
    print("You will see fallback content in this case, which is the expected behavior.")
    print("On a local machine with Ollama installed, dynamic generation would work.")
    
    # Create a technology entry directly to test functionality
    entry_id = "quantum_tech"
    entry_title = "Quantum Hacking"
    entry_category = "technology"
    
    print(f"\nCreating and discovering a new codex entry: {entry_title}...")
    
    # First create the entry
    default_content = f"## {entry_title}\n\nInformation on this subject is being retrieved..."
    creation_success = test_codex.add_entry(
        entry_id=entry_id,
        category=entry_category,
        title=entry_title,
        content=default_content,
        dynamic_generation=True  # This will trigger Ollama content generation
    )
    
    # Then mark it as discovered
    was_discovered = test_codex.discover_entry(
        entry_id=entry_id
    )
    
    if creation_success:
        print(f"Successfully created entry: {entry_id}")
        
        # Get the generated entry
        entry = test_codex.get_entry(entry_id)
        if entry:
            print("\n--- Generated Entry ---")
            print(f"Title: {entry['title']}")
            print(f"Category: {entry['category']}")
            print(f"Content length: {len(entry['content'])} characters")
            print("Content preview:")
            content_preview = entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content']
            print(content_preview)
            
            if entry.get('related_entries'):
                print(f"Related entries: {entry['related_entries']}")
            if entry.get('image'):
                print(f"Image: {entry['image']}")
        else:
            print("Error: Could not retrieve the generated entry")
    else:
        print(f"Failed to create entry: {entry_id}")
    
    # Create an entry for a different category
    entry_id2 = "synth_corp"
    entry_title2 = "SynthWave Corporation" 
    entry_category2 = "factions"
    
    print(f"\nCreating and discovering another codex entry: {entry_title2}...")
    
    # Create and discover in one step
    default_content2 = f"## {entry_title2}\n\nInformation on this subject is being retrieved..."
    creation_success2 = test_codex.add_entry(
        entry_id=entry_id2,
        category=entry_category2,
        title=entry_title2,
        content=default_content2,
        dynamic_generation=True
    )
    
    # Mark as discovered
    was_discovered2 = test_codex.discover_entry(
        entry_id=entry_id2
    )
    
    if creation_success2:
        print(f"Successfully created entry: {entry_id2}")
        
        # Get the generated entry
        entry2 = test_codex.get_entry(entry_id2)
        if entry2:
            print("\n--- Generated Entry ---")
            print(f"Title: {entry2['title']}")
            print(f"Category: {entry2['category']}")
            print(f"Content length: {len(entry2['content'])} characters")
            print("Content preview:")
            content_preview = entry2['content'][:200] + "..." if len(entry2['content']) > 200 else entry2['content']
            print(content_preview)
            
            if entry2.get('related_entries'):
                print(f"Related entries: {entry2['related_entries']}")
            if entry2.get('image'):
                print(f"Image: {entry2['image']}")
        else:
            print("Error: Could not retrieve the generated entry")
    else:
        print(f"Failed to create entry: {entry_id2}")
    
    # Check updated discovery count
    discovered, total = test_codex.get_discovery_count()
    print(f"\nAfter dynamic generation, codex has {discovered} discovered entries out of {total} total entries.")
    
    # Test get_categories_with_discovered_entries
    categories = test_codex.get_categories_with_discovered_entries()
    print(f"Categories with discovered entries: {categories}")
    
    print("\nDynamic codex content generation testing complete!")

if __name__ == "__main__":
    main()