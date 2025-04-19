"""
Test script for the Ollama API URL functionality
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

# Import necessary modules
try:
    from config import GAME_SETTINGS, OLLAMA_API_URL
    import settings
    from ollama_integration import OllamaIntegration
except ImportError as e:
    console.print(f"[bold red]Error importing modules: {e}[/bold red]")
    sys.exit(1)

def test_ollama_api_url():
    """Test the Ollama API URL functionality"""
    console.print(Panel("Testing Ollama API URL Configuration", style="bold cyan"))
    
    # Current settings
    console.print("\n[yellow]Current Settings:[/yellow]")
    console.print(f"Default API URL from config: {OLLAMA_API_URL}")
    console.print(f"Current API URL from GAME_SETTINGS: {GAME_SETTINGS['ollama_api_url']}")
    
    # Test updating the setting
    new_url = "http://test-api.example.com:11434"
    console.print(f"\n[yellow]Updating API URL to:[/yellow] {new_url}")
    settings.update_setting("ollama_api_url", new_url)
    console.print(f"Updated API URL in GAME_SETTINGS: {GAME_SETTINGS['ollama_api_url']}")
    
    # Test Ollama integration using the new URL
    console.print("\n[yellow]Creating OllamaIntegration instance with new URL:[/yellow]")
    ollama = OllamaIntegration()
    console.print(f"OllamaIntegration API URL: {ollama.api_url}")
    
    # Test endpoint generation
    console.print("\n[yellow]Testing endpoint generation for different URL formats:[/yellow]")
    
    # Test URLs
    test_urls = [
        "http://localhost:11434",
        "http://localhost:11434/api",
        "http://localhost:11434/api/",
        "https://example.org:9999",
        "https://example.org:9999/api",
        "https://example.org:9999/api/generate"
    ]
    
    for url in test_urls:
        # Update the API URL
        ollama.api_url = url
        
        # Create a simple prompt
        prompt = "Test prompt"
        
        # Get the endpoint through our helper method
        endpoint = _get_test_endpoint(ollama, prompt)
        
        console.print(f"API URL: [cyan]{url}[/cyan]")
        console.print(f"Generated endpoint: [green]{endpoint}[/green]")
        console.print("")
    
    # Test resetting to defaults
    console.print("\n[yellow]Testing reset to defaults:[/yellow]")
    settings.reset_to_defaults()
    console.print(f"API URL after reset: {GAME_SETTINGS['ollama_api_url']}")
    
    console.print("\n[bold green]Test completed successfully![/bold green]")

def _get_test_endpoint(ollama, prompt):
    """Extract the endpoint from OllamaIntegration._make_request method logic"""
    if ollama.api_url.endswith("/api/generate"):
        endpoint = ollama.api_url
    elif ollama.api_url.endswith("/api"):
        endpoint = f"{ollama.api_url}/generate"
    elif ollama.api_url.endswith("/api/"):
        # Handle trailing slash properly
        endpoint = f"{ollama.api_url}generate"
    else:
        # Ensure we have the /api path
        base_url = ollama.api_url
        if not base_url.endswith("/api"):
            if base_url.endswith("/"):
                base_url += "api"
            else:
                base_url += "/api"
        endpoint = f"{base_url}/generate"
    
    return endpoint

if __name__ == "__main__":
    test_ollama_api_url()