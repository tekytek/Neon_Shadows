#!/usr/bin/env python3
"""
Test script for the dynamic codex content generation with Ollama
"""
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import time
import random

import codex
from config import USE_OLLAMA, COLORS

def main():
    """Test the dynamic codex content generation with Ollama"""
    console = Console()
    console.print(Panel("[bold cyan]TESTING ENHANCED DYNAMIC CODEX CONTENT GENERATION[/bold cyan]", 
                       border_style="cyan"))
    
    # Initialize codex
    test_codex = codex.Codex()
    
    # Check if Ollama is enabled
    console.print(f"[bold]Ollama integration:[/bold] {'[green]Enabled[/green]' if USE_OLLAMA else '[red]Disabled[/red]'}")
    console.print("[yellow]Note: When running in Replit, Ollama may not be available even if enabled in config.[/yellow]")
    console.print("[yellow]Fallback content will be used if Ollama is unavailable.[/yellow]")
    console.print("[yellow]On a local machine with Ollama installed, dynamic generation would work.[/yellow]\n")
    
    # Test entries for different categories
    test_entries = [
        {
            "id": "quantum_crypto",
            "title": "Quantum Cryptography",
            "category": "technology"
        },
        {
            "id": "chrome_dragons",
            "title": "Chrome Dragons",
            "category": "factions"
        },
        {
            "id": "neural_alley",
            "title": "Neural Alley",
            "category": "locations"
        }
    ]
    
    # Choose a random test entry to avoid duplicate entries in multiple test runs
    test_entry = random.choice(test_entries)
    entry_id = test_entry["id"]
    entry_title = test_entry["title"]
    entry_category = test_entry["category"]
    
    # Show processing animation
    console.print(f"\n[bold cyan]Generating new codex entry:[/bold cyan] [bold]{entry_title}[/bold] ({entry_category})")
    
    # Simple animation to show processing
    for i in range(10):
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        console.print(f"\r[cyan]{chars[i % len(chars)]} Processing...[/cyan]", end="")
        time.sleep(0.2)
    console.print("\r[green]✓ Processing complete![/green]" + " " * 20)
    
    # Create the entry with dynamic generation enabled
    default_content = f"## {entry_title}\n\nInitializing data retrieval from NetLink..."
    creation_success = test_codex.add_entry(
        entry_id=entry_id,
        category=entry_category,
        title=entry_title,
        content=default_content,
        dynamic_generation=True  # This will trigger enhanced Ollama content generation
    )
    
    # Mark as discovered
    was_discovered = test_codex.discover_entry(entry_id)
    
    if creation_success:
        console.print(f"\n[green]Successfully created entry:[/green] {entry_id}")
        
        # Get the generated entry
        entry = test_codex.get_entry(entry_id)
        if entry:
            # Display formatted entry details
            console.print(f"\n[bold cyan]═════ CODEX ENTRY DETAILS ═════[/bold cyan]")
            console.print(f"[bold]Title:[/bold] {entry['title']}")
            console.print(f"[bold]Category:[/bold] {entry['category']}")
            console.print(f"[bold]Content Length:[/bold] {len(entry['content'])} characters")
            
            # Show a preview of the content
            console.print(f"\n[bold magenta]═════ CONTENT PREVIEW ═════[/bold magenta]")
            
            # For a nicer display, use Markdown if content is not a fallback
            if len(entry['content']) > 200:
                preview_length = min(500, len(entry['content']))
                content_preview = entry['content'][:preview_length]
                if preview_length < len(entry['content']):
                    content_preview += "...\n\n[Content truncated for preview]"
                
                try:
                    console.print(Markdown(content_preview))
                except Exception:
                    # Fallback to plain text if markdown parsing fails
                    console.print(content_preview)
            else:
                console.print(entry['content'])
            
            # Show related entries and image if available
            if entry.get('related_entries') and len(entry['related_entries']) > 0:
                console.print(f"\n[bold]Related entries:[/bold] {', '.join(entry['related_entries'])}")
            if entry.get('image'):
                console.print(f"[bold]Associated image:[/bold] {entry['image']}")
        else:
            console.print("[bold red]Error: Could not retrieve the generated entry[/bold red]")
    else:
        console.print(f"[bold red]Failed to create entry: {entry_id}[/bold red]")
    
    # Check codex statistics
    discovered, total = test_codex.get_discovery_count()
    console.print(f"\n[bold]Codex Statistics:[/bold]")
    console.print(f"• Discovered entries: [cyan]{discovered}[/cyan] out of [cyan]{total}[/cyan] total entries")
    
    # Calculate and display discovery percentage
    percentage = (discovered/total*100) if total > 0 else 0
    
    # Create a visual progress bar
    bar_width = 30
    filled = int((bar_width * discovered) / total) if total > 0 else 0
    progress_bar = "[" + "█" * filled + "░" * (bar_width - filled) + "]"
    console.print(f"• Discovery progress: [cyan]{percentage:.1f}%[/cyan] {progress_bar}")
    
    # Display categories with discovered entries
    categories = test_codex.get_categories_with_discovered_entries()
    console.print(f"• Active categories: [cyan]{', '.join(categories)}[/cyan]")
    
    console.print(f"\n[bold green]Dynamic codex content generation testing complete![/bold green]")
    console.print(Panel("[cyan]The enhanced Ollama prompt generation is active and will produce more detailed, atmosphere-rich codex entries when Ollama is available.[/cyan]", 
                       border_style="green", 
                       title="System Status", 
                       subtitle="Neural Codex v2.1"))

if __name__ == "__main__":
    main()