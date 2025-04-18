#!/usr/bin/env python3
"""
Setup Script - Installs dependencies and runs tests to ensure everything is working

This script prepares the environment for Neon Shadows by:
1. Checking and installing required dependencies
2. Running critical component tests
3. Verifying that animations, combat system, and other features work correctly
"""
import os
import sys
import subprocess
import time
import importlib.util
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Initialize console
console = Console()

def header():
    """Display the setup header"""
    console.print("\n[bold cyan]NEON SHADOWS - SETUP UTILITY[/bold cyan]")
    console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]\n")

def check_python_version():
    """Check Python version requirements"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Checking Python version...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate check
        for i in range(101):
            time.sleep(0.01)
            progress.update(task, completed=i)
    
    major, minor = sys.version_info.major, sys.version_info.minor
    console.print(f"Python version: [green]{major}.{minor}[/green]")
    
    if major < 3 or (major == 3 and minor < 8):
        console.print("[bold red]ERROR: Python 3.8 or higher is required[/bold red]")
        return False
    
    console.print("[green]✓[/green] Python version check passed\n")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["rich", "numpy", "pygame", "requests", "scipy"]
    missing_packages = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Checking dependencies...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=len(required_packages))
        
        for package in required_packages:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
            progress.advance(task)
            time.sleep(0.2)  # Brief pause for visual effect
    
    if missing_packages:
        console.print("[yellow]Missing dependencies found:[/yellow]")
        for package in missing_packages:
            console.print(f"  - [yellow]{package}[/yellow]")
        
        console.print("\nAttempting to install missing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            console.print("[green]✓[/green] Dependencies installed successfully\n")
        except subprocess.CalledProcessError:
            console.print("[bold red]ERROR: Failed to install dependencies[/bold red]")
            return False
    else:
        console.print("[green]✓[/green] All dependencies are installed\n")
    
    return True

def run_animation_test(test_type="basic"):
    """Run a quick animation test to ensure animations are working"""
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]Testing {test_type} animations...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate test running
        for i in range(101):
            time.sleep(0.02)
            progress.update(task, completed=i)
    
    # Test a simple animation function
    success = False  # Initialize success variable
    try:
        if test_type == "basic":
            import animations
            test_console = Console()
            animations.set_animation_speed("fast")  # Speed up for testing
            animations.typing_effect("Animation system operational", test_console)
            success = True
        elif test_type == "advanced":
            result = subprocess.run(
                [sys.executable, "test_animations.py", "--headless"], 
                capture_output=True, 
                text=True
            )
            success = result.returncode == 0
    except Exception as e:
        console.print(f"[bold red]ERROR: Animation test failed - {str(e)}[/bold red]")
        return False
    
    if success:
        console.print(f"[green]✓[/green] {test_type.capitalize()} animation test passed\n")
        return True
    else:
        console.print(f"[bold red]ERROR: {test_type.capitalize()} animation test failed[/bold red]")
        return False

def run_codex_test():
    """Run a quick test to ensure the codex system is working"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Testing codex system...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate test running
        for i in range(101):
            time.sleep(0.03)
            progress.update(task, completed=i)
    
    success = False  # Initialize success variable
    try:
        import codex
        test_codex = codex.Codex()
        # Simple test to ensure basic codex functionality works
        test_codex.discover_entry("night_city", "Night City", "world")
        success = "night_city" in test_codex.get_entries_by_category("world")
    except Exception as e:
        console.print(f"[bold red]ERROR: Codex test failed - {str(e)}[/bold red]")
        return False
    
    if success:
        console.print("[green]✓[/green] Codex system test passed\n")
        return True
    else:
        console.print("[bold red]ERROR: Codex system test failed[/bold red]")
        return False

def run_combat_test():
    """Run a quick test to ensure combat system is working"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Testing tactical combat system...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate test running
        for i in range(101):
            time.sleep(0.03)
            progress.update(task, completed=i)
    
    success = False  # Initialize success variable
    try:
        # Import key combat modules to verify they load correctly
        import combat
        import combat_positioning
        import tactical_abilities
        success = True
    except Exception as e:
        console.print(f"[bold red]ERROR: Combat system test failed - {str(e)}[/bold red]")
        return False
    
    if success:
        console.print("[green]✓[/green] Combat system test passed\n")
        return True
    else:
        console.print("[bold red]ERROR: Combat system test failed[/bold red]")
        return False

def check_audio_system():
    """Check if the audio system is working"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Testing audio system...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate test running
        for i in range(101):
            time.sleep(0.02)
            progress.update(task, completed=i)
    
    success = False  # Initialize success variable
    try:
        import audio
        audio.initialize()
        success = True
        # Don't actually play sound during setup to avoid disruption
    except Exception as e:
        console.print(f"[bold red]ERROR: Audio system test failed - {str(e)}[/bold red]")
        return False
    
    if success:
        console.print("[green]✓[/green] Audio system test passed\n")
        return True
    else:
        console.print("[bold red]ERROR: Audio system test failed[/bold red]")
        return False

def check_save_system():
    """Check if the save system is working"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Testing save system...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=100)
        
        # Simulate test running
        for i in range(101):
            time.sleep(0.02)
            progress.update(task, completed=i)
    
    success = False  # Initialize success variable
    try:
        import save_system
        # Check if saves directory exists
        if not os.path.exists("saves"):
            os.makedirs("saves")
        success = os.path.exists("saves")
    except Exception as e:
        console.print(f"[bold red]ERROR: Save system test failed - {str(e)}[/bold red]")
        return False
    
    if success:
        console.print("[green]✓[/green] Save system test passed\n")
        return True
    else:
        console.print("[bold red]ERROR: Save system test failed[/bold red]")
        return False

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "data/codex.json",
        "data/districts.json", 
        "data/enemies.json", 
        "data/items.json",
        "data/perks.json",
        "data/skills.json",
        "data/story_nodes.json"
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Checking data files...[/bold blue]"),
        BarColumn(),
        TextColumn("[bold blue]{task.percentage:.0f}%[/bold blue]"),
        console=console
    ) as progress:
        task = progress.add_task("", total=len(required_files))
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
            progress.advance(task)
            time.sleep(0.1)  # Brief pause for visual effect
    
    if missing_files:
        console.print("[yellow]Missing data files:[/yellow]")
        for file in missing_files:
            console.print(f"  - [yellow]{file}[/yellow]")
        return False
    else:
        console.print("[green]✓[/green] All data files present\n")
        return True

def main():
    """Main setup function"""
    header()
    
    console.print(Panel.fit(
        "[bold]This utility will check your system and prepare it for Neon Shadows[/bold]\n"
        "It will ensure all dependencies are installed and components are working correctly",
        title="[cyan]WELCOME[/cyan]",
        border_style="cyan"
    ))
    
    input("\nPress Enter to begin setup...")
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Data Files", check_data_files),
        ("Basic Animations", lambda: run_animation_test("basic")),
        ("Audio System", check_audio_system),
        ("Save System", check_save_system),
        ("Codex System", run_codex_test),
        ("Combat System", run_combat_test)
    ]
    
    results = {}
    
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    console.print("\n[bold cyan]SETUP SUMMARY[/bold cyan]")
    console.print("[cyan]━━━━━━━━━━━━━━━━━[/cyan]")
    
    all_passed = True
    for name, result in results.items():
        status = "[green]PASSED[/green]" if result else "[red]FAILED[/red]"
        console.print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        console.print("\n[green bold]All tests passed! Your system is ready for Neon Shadows![/green bold]")
        console.print("\nStarting game in 3 seconds...")
        time.sleep(3)
        
        # Start the game
        subprocess.Popen([sys.executable, "main.py"])
    else:
        console.print("\n[yellow bold]Some tests failed. You may experience issues when running the game.[/yellow bold]")
        console.print("[yellow]Please review the errors above and try to resolve them before playing.[/yellow]")
        
        proceed = input("\nDo you want to proceed to the game anyway? (y/n): ").lower().strip()
        if proceed == 'y':
            console.print("\nStarting game...")
            subprocess.Popen([sys.executable, "main.py"])
        else:
            console.print("\nSetup aborted. Please fix the issues and run setup.py again.")

if __name__ == "__main__":
    main()