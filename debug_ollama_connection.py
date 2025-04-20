"""
Debug script for Ollama API connection
"""
import requests
import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Import settings
try:
    from config import GAME_SETTINGS, OLLAMA_API_URL, OLLAMA_TOKEN, OLLAMA_MODEL, USE_OLLAMA
    from ollama_integration import OllamaIntegration
except ImportError as e:
    console.print(f"[bold red]Error importing modules: {e}[/bold red]")
    exit(1)

def debug_ollama_connection():
    """Test the Ollama API connection and print diagnostic information"""
    console.print(Panel("Ollama Connection Diagnostic Tool", style="bold cyan"))
    
    # Display current settings
    console.print("[yellow]Current Settings:[/yellow]")
    console.print(f"Ollama Integration Enabled: {USE_OLLAMA}")
    console.print(f"Ollama API URL: {GAME_SETTINGS['ollama_api_url']}")
    console.print(f"Ollama Model: {OLLAMA_MODEL if 'OLLAMA_MODEL' in globals() else 'Not found'}")
    
    # Check for API token in settings and environment variables
    settings_token = GAME_SETTINGS.get("ollama_token", "")
    env_token = os.getenv("OLLAMA_TOKEN", "")
    
    if settings_token:
        console.print(f"Ollama API Token: [green]Set in game settings[/green]")
    elif env_token:
        console.print(f"Ollama API Token: [green]Found in environment variables[/green]")
    else:
        console.print(f"Ollama API Token: [yellow]Not set in settings or environment variables[/yellow]")
    
    # Create an OllamaIntegration instance
    ollama = OllamaIntegration()
    console.print(f"\nOllamaIntegration API URL: {ollama.api_url}")
    
    # Test URL format and construct the test endpoint
    if ollama.api_url.endswith("/api/generate"):
        endpoint = ollama.api_url
    elif ollama.api_url.endswith("/api"):
        endpoint = f"{ollama.api_url}/generate"
    elif ollama.api_url.endswith("/api/"):
        endpoint = f"{ollama.api_url}generate"
    else:
        base_url = ollama.api_url
        if not base_url.endswith("/api"):
            if base_url.endswith("/"):
                base_url += "api"
            else:
                base_url += "/api"
        endpoint = f"{base_url}/generate"
    
    console.print(f"Test endpoint: {endpoint}")
    
    # Prepare headers with token if available
    headers = {}
    if ollama_token:
        headers["Authorization"] = f"Bearer {ollama_token}"
    
    # Test 1: Check if the server is reachable
    console.print("\n[bold cyan]Test 1: Testing if the server is reachable...[/bold cyan]")
    try:
        base_url = endpoint.split("/api")[0]
        base_response = requests.get(base_url, headers=headers, timeout=5)
        console.print(f"Base URL response status: [green]{base_response.status_code}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error connecting to base URL: {str(e)}[/bold red]")
    
    # Test 2: Check if the API endpoint can be reached
    console.print("\n[bold cyan]Test 2: Testing if the API endpoint is available...[/bold cyan]")
    try:
        # If the URL has /api/generate, try /api/tags instead
        if "/api/generate" in endpoint:
            tags_endpoint = endpoint.replace("/api/generate", "/api/tags")
        else:
            # Construct the tags endpoint
            base_url = endpoint.split("/api")[0]
            tags_endpoint = f"{base_url}/api/tags"
        
        console.print(f"Tags endpoint: {tags_endpoint}")
        tags_response = requests.get(tags_endpoint, headers=headers, timeout=5)
        
        if tags_response.status_code == 200:
            console.print("[green]API endpoint is available![/green]")
            # Display available models
            models = tags_response.json()
            console.print("Available models:")
            for model in models.get("models", []):
                console.print(f"- {model['name']}")
        else:
            console.print(f"[bold red]API endpoint returned status code: {tags_response.status_code}[/bold red]")
            console.print(f"Response: {tags_response.text}")
            
            # Check if authentication might be required
            if tags_response.status_code in [401, 403]:
                console.print("[yellow]Authentication may be required. Try setting an OLLAMA_TOKEN environment variable.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error checking API endpoint: {str(e)}[/bold red]")
    
    # Test 3: Make a simple query to the API
    console.print("\n[bold cyan]Test 3: Testing API with a simple query...[/bold cyan]")
    try:
        data = {
            "model": ollama.model,
            "prompt": "Say hello in a short sentence.",
            "stream": False
        }
        
        console.print(f"Using model: {ollama.model}")
        console.print(f"Sending request to: {endpoint}")
        
        response = requests.post(endpoint, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            console.print("[green]API query successful![/green]")
            console.print(f"Response: {result.get('response', 'No response text found')}")
        else:
            console.print(f"[bold red]API query failed with status code: {response.status_code}[/bold red]")
            console.print(f"Response: {response.text}")
            
            # Check if authentication might be required
            if response.status_code in [401, 403]:
                console.print("[yellow]Authentication may be required. Try setting an OLLAMA_TOKEN environment variable.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error making API query: {str(e)}[/bold red]")
    
    # Options menu
    console.print("\n[bold cyan]Options:[/bold cyan]")
    console.print("1. Update Ollama API URL")
    console.print("2. Set Ollama API Token")
    console.print("3. Exit")
    
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3"], default="3")
    
    if choice == "1":
        new_url = Prompt.ask("Enter new Ollama API URL", default=GAME_SETTINGS['ollama_api_url'])
        
        # Update settings
        try:
            import settings
            settings.update_setting("ollama_api_url", new_url)
            console.print(f"[green]API URL updated to: {new_url}[/green]")
            console.print("[yellow]Please restart the application for changes to take effect.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error updating settings: {str(e)}[/bold red]")
    
    elif choice == "2":
        # We can't permanently set environment variables from Python,
        # but we can instruct the user on how to do it
        console.print("[yellow]To set the Ollama API Token, you need to set the OLLAMA_TOKEN environment variable.[/yellow]")
        console.print("For this session, you can enter the token and we'll test with it.")
        
        token = Prompt.ask("Enter your Ollama API Token", password=True)
        os.environ["OLLAMA_TOKEN"] = token
        
        console.print("[green]Token set for this session only.[/green]")
        console.print("To make this permanent, set the OLLAMA_TOKEN environment variable in your system.")
        console.print("Would you like to test the connection with this token?")
        
        test_again = Prompt.ask("Test connection? (y/n)", choices=["y", "n"], default="y")
        if test_again.lower() == "y":
            console.print("\n[yellow]Testing connection with the provided token...[/yellow]")
            # Run the tests again by calling the function recursively
            debug_ollama_connection()

def update_ollama_integration():
    """Add API token support to ollama_integration.py"""
    try:
        # Read the current file content
        file_path = "ollama_integration.py"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check if we need to update the file
        if "os.getenv(\"OLLAMA_TOKEN\")" not in content:
            console.print("[yellow]Updating ollama_integration.py to support API tokens...[/yellow]")
            
            # Add os import if not already present
            import_line = "import os"
            if import_line not in content:
                content = content.replace("import json", "import os\nimport json")
            
            # Add token support to _make_request method
            headers_code = """
        # Add API token if available
        headers = {}
        ollama_token = os.getenv("OLLAMA_TOKEN")
        if ollama_token:
            headers["Authorization"] = f"Bearer {ollama_token}"
        
        # Try to make the request with retries"""
            
            # Replace the existing code
            old_code = "# Try to make the request with retries"
            content = content.replace(old_code, headers_code)
            
            # Update the requests.post call to include headers
            old_post = "response = requests.post(endpoint, json=data, timeout=30)"
            new_post = "response = requests.post(endpoint, json=data, headers=headers, timeout=30)"
            content = content.replace(old_post, new_post)
            
            # Update the requests.get call in _check_availability
            old_get = "response = requests.get(f\"{base_url}/api/tags\", timeout=5)"
            new_get = """
            # Get API token if available
            headers = {}
            ollama_token = os.getenv("OLLAMA_TOKEN")
            if ollama_token:
                headers["Authorization"] = f"Bearer {ollama_token}"
                
            response = requests.get(f"{base_url}/api/tags", headers=headers, timeout=5)"""
            content = content.replace(old_get, new_get)
            
            # Write the updated content back to the file
            with open(file_path, "w") as f:
                f.write(content)
            
            console.print("[green]Successfully updated ollama_integration.py with API token support![/green]")
            return True
        else:
            console.print("[green]ollama_integration.py already supports API tokens.[/green]")
            return False
    except Exception as e:
        console.print(f"[bold red]Error updating ollama_integration.py: {str(e)}[/bold red]")
        return False

if __name__ == "__main__":
    try:
        # Import OLLAMA_MODEL which might not be imported in the global scope
        from config import OLLAMA_MODEL
        
        # First update the integration file with token support
        update_ollama_integration()
        
        # Then run the debug
        debug_ollama_connection()
    except Exception as e:
        console.print(f"[bold red]Error running diagnostics: {str(e)}[/bold red]")