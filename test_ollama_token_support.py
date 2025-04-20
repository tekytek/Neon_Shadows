"""
Test script for Ollama API token support
"""
import os
import json
from rich.console import Console
from rich.panel import Panel

# Import ollama integration
from ollama_integration import OllamaIntegration
import settings
from config import GAME_SETTINGS

console = Console()

def test_token_support():
    """Test Ollama API token support"""
    console.print(Panel("Testing Ollama API Token Support", style="bold cyan"))
    
    # Display current settings
    console.print("[yellow]Current Settings:[/yellow]")
    console.print(f"Ollama API URL: {GAME_SETTINGS.get('ollama_api_url', 'Not set')}")
    console.print(f"Ollama Model: {GAME_SETTINGS.get('ollama_model', 'Not set')}")
    
    # Check for token in settings and environment
    settings_token = GAME_SETTINGS.get("ollama_token", "")
    env_token = os.getenv("OLLAMA_TOKEN", "")
    
    if settings_token:
        token_display = settings_token[:3] + "*" * (len(settings_token) - 6) + settings_token[-3:] if len(settings_token) > 6 else "***"
        console.print(f"Ollama API Token in settings: [green]{token_display}[/green]")
    else:
        console.print("Ollama API Token in settings: [yellow]Not set[/yellow]")
        
    if env_token:
        token_display = env_token[:3] + "*" * (len(env_token) - 6) + env_token[-3:] if len(env_token) > 6 else "***"
        console.print(f"Ollama API Token in environment: [green]{token_display}[/green]")
    else:
        console.print("Ollama API Token in environment: [yellow]Not set[/yellow]")
    
    # Create Ollama integration instance
    console.print("\n[bold cyan]Creating OllamaIntegration instance...[/bold cyan]")
    ollama = OllamaIntegration()
    
    # Display instance settings
    console.print(f"Integration API URL: {ollama.api_url}")
    console.print(f"Integration Model: {ollama.model}")
    if ollama.token:
        token_display = ollama.token[:3] + "*" * (len(ollama.token) - 6) + ollama.token[-3:] if len(ollama.token) > 6 else "***"
        console.print(f"Integration Token: [green]{token_display}[/green]")
    else:
        console.print("Integration Token: [yellow]Not set[/yellow]")
    
    # Test availability
    console.print("\n[bold cyan]Testing Ollama availability...[/bold cyan]")
    available = ollama._check_availability()
    if available:
        console.print("[green]Ollama is available![/green]")
    else:
        console.print("[yellow]Ollama is not available.[/yellow]")
        console.print("This is normal when testing in environments where Ollama isn't installed.")
        console.print("When running on a system with Ollama, make sure the API endpoint and token are correct.")
    
    # Test a simple request
    console.print("\n[bold cyan]Testing simple request...[/bold cyan]")
    test_prompt = "Say hello in a short sentence."
    console.print(f"Sending test prompt: '{test_prompt}'")
    
    try:
        response = ollama._make_request(test_prompt)
        if response:
            response_text = response.get("response", "No response text found")
            console.print(f"[green]Response received:[/green] {response_text}")
        else:
            console.print("[yellow]No response received from Ollama.[/yellow]")
            console.print("This is normal when testing in environments where Ollama isn't installed.")
    except Exception as e:
        console.print(f"[red]Error making request: {str(e)}[/red]")
    
    # Test token-based authentication handling
    console.print("\n[bold cyan]Testing token-based authentication handling...[/bold cyan]")
    
    # Check headers in _make_request method
    test_headers = {}
    if ollama.token:
        test_headers["Authorization"] = f"Bearer {ollama.token}"
        console.print("[green]Authorization header would be set with token[/green]")
    else:
        console.print("[yellow]No token available, no Authorization header would be set[/yellow]")
    
    # Provide guidance for local testing
    console.print("\n[bold cyan]Testing Guidance:[/bold cyan]")
    console.print("""
To test token authentication with Ollama locally:
1. Set the Ollama API URL in settings to your Ollama server address (e.g., http://localhost:11434)
2. Set the Ollama token in game settings or as an environment variable
3. Run this test again on a system where Ollama is installed
    """)
    
    return ollama

if __name__ == "__main__":
    try:
        ollama = test_token_support()
        
        # Offer to update settings
        console.print("\n[bold cyan]Options:[/bold cyan]")
        choice = input("Would you like to update the Ollama API settings? (y/n): ").lower()
        
        if choice == 'y':
            # Get new values
            new_url = input(f"Enter new Ollama API URL (press Enter to keep '{GAME_SETTINGS['ollama_api_url']}'): ")
            new_model = input(f"Enter new Ollama model (press Enter to keep '{GAME_SETTINGS['ollama_model']}'): ")
            new_token = input("Enter new Ollama API token (press Enter to keep current, type 'clear' to remove): ")
            
            # Update settings
            if new_url and new_url != GAME_SETTINGS['ollama_api_url']:
                settings.update_setting("ollama_api_url", new_url)
                console.print(f"[green]Updated API URL to: {new_url}[/green]")
                
            if new_model and new_model != GAME_SETTINGS['ollama_model']:
                settings.update_setting("ollama_model", new_model)
                console.print(f"[green]Updated model to: {new_model}[/green]")
                
            if new_token:
                if new_token.lower() == 'clear':
                    settings.update_setting("ollama_token", "")
                    console.print("[green]Cleared API token[/green]")
                else:
                    settings.update_setting("ollama_token", new_token)
                    console.print("[green]Updated API token[/green]")
            
            console.print("[yellow]Settings updated. Restart the application for changes to take effect.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error running test: {str(e)}[/bold red]")