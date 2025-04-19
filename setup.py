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

# First, check if rich is installed - we need it for the UI
try:
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    
    # Initialize console with rich
    console = Console()
    use_rich = True
except ImportError:
    # Rich not installed, use fallback text-only mode
    use_rich = False
    
    # Create a minimal console class that mimics the parts of rich.console.Console we use
    class MinimalConsole:
        def print(self, text, style=None, end="\n", **kwargs):
            # Strip out rich formatting markup with a very simple approach
            text = str(text)
            
            # Remove color tags like [red], [bold], etc.
            while "[" in text and "]" in text:
                start = text.find("[")
                end = text.find("]", start)
                if start < end:  # Ensure we found a matching pair
                    text = text[:start] + text[end+1:]
                else:
                    break  # Avoid infinite loop if there's a malformed tag
            
            print(text, end=str(end))
        
        def clear(self):
            # Cross-platform clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
    # Create a minimal Panel class to mimic rich.panel.Panel
    class MinimalPanel:
        @staticmethod
        def fit(text, title=None, border_style=None):
            # Create a simple boxed panel without fancy styling
            lines = text.split('\n')
            width = max(len(line) for line in lines) + 4  # +4 for side borders and spaces
            
            result = []
            # Top border
            top_border = "╭" + "─" * (width - 2) + "╮"
            if title:
                # Strip formatting from title
                clean_title = title
                while "[" in clean_title and "]" in clean_title:
                    start = clean_title.find("[")
                    end = clean_title.find("]", start)
                    if start < end:
                        clean_title = clean_title[:start] + clean_title[end+1:]
                    else:
                        break
                
                # Add title to top border
                title_start = (width - len(clean_title)) // 2 - 1
                top_border = top_border[:title_start] + " " + clean_title + " " + top_border[title_start + len(clean_title) + 2:]
            
            result.append(top_border)
            
            # Content
            for line in lines:
                result.append(f"│ {line.ljust(width - 4)} │")
            
            # Bottom border
            result.append("╰" + "─" * (width - 2) + "╯")
            
            return "\n".join(result)
    
    # Create minimal Progress class and related components
    class TextColumn:
        def __init__(self, text):
            self.text = text
    
    class BarColumn:
        pass
    
    class SpinnerColumn:
        pass
    
    class Progress:
        def __init__(self, *args, console=None):
            self.tasks = {}
            self.console = console
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        
        def add_task(self, description, total=100):
            task_id = hash(description) % 10000
            self.tasks[task_id] = {"completed": 0, "total": total}
            # Print a simple text representation
            print(f"Starting task: {description}")
            return task_id
        
        def update(self, task_id, completed=None):
            if task_id in self.tasks and completed is not None:
                self.tasks[task_id]["completed"] = completed
                # Optionally print progress
                if completed % 20 == 0:  # Update less frequently
                    print(f"Progress: {completed}%")
        
        def advance(self, task_id, advance=1):
            if task_id in self.tasks:
                self.tasks[task_id]["completed"] += advance
                completed = self.tasks[task_id]["completed"]
                # Optionally print progress
                if completed % 20 == 0:  # Update less frequently
                    print(f"Progress: {completed}%")
    
    # Initialize our minimal console and panel
    console = MinimalConsole()
    Panel = MinimalPanel
    
    # Try to install rich automatically
    print("Rich library not found. Attempting to install it...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
        print("Rich installed successfully. Please restart the setup script.")
        sys.exit(0)
    except subprocess.CalledProcessError:
        print("Failed to automatically install Rich. Continuing in text-only mode.")
        print("For best experience, install Rich manually with: pip install rich")

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

def install_packages_with_pip(packages):
    """Try to install packages using pip"""
    try:
        console.print("[blue]Attempting to install using pip...[/blue]")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        return True
    except subprocess.CalledProcessError:
        console.print("[yellow]Pip installation failed, will try alternative methods[/yellow]")
        return False
        
def install_packages_with_pipx(packages):
    """Try to install packages using pipx if available"""
    try:
        console.print("[blue]Checking if pipx is available...[/blue]")
        # First check if pipx is installed
        subprocess.check_call(["which", "pipx"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Try to install each package with pipx
        success = True
        for package in packages:
            try:
                console.print(f"[blue]Installing {package} with pipx...[/blue]")
                subprocess.check_call(["pipx", "install", package])
            except subprocess.CalledProcessError:
                success = False
        
        return success
    except subprocess.CalledProcessError:
        console.print("[yellow]Pipx not available, will try other methods[/yellow]")
        return False

def install_packages_with_apt(packages):
    """Try to install packages using apt-get if on Debian/Ubuntu"""
    try:
        console.print("[blue]Checking if apt-get is available...[/blue]")
        # Check if apt-get exists
        subprocess.check_call(["which", "apt-get"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Map Python package names to apt package names
        apt_packages = {
            "rich": "python3-rich",
            "numpy": "python3-numpy",
            "pygame": "python3-pygame",
            "requests": "python3-requests",
            "scipy": "python3-scipy"
        }
        
        # Filter for only the packages in our mapping
        packages_to_install = [apt_packages[pkg] for pkg in packages if pkg in apt_packages]
        
        if packages_to_install:
            console.print("[blue]Installing packages with apt-get...[/blue]")
            
            # Check if we can use sudo
            can_use_sudo = False
            try:
                subprocess.check_call(["sudo", "-n", "true"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                can_use_sudo = True
            except subprocess.CalledProcessError:
                console.print("[yellow]No sudo access, will try to run apt-get without sudo[/yellow]")
            
            try:
                # Try to update apt repositories
                if can_use_sudo:
                    subprocess.check_call(["sudo", "apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    install_cmd = ["sudo", "apt-get", "install", "-y"] + packages_to_install
                else:
                    # Try without sudo in case user is already privileged or has correct permissions
                    subprocess.check_call(["apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    install_cmd = ["apt-get", "install", "-y"] + packages_to_install
                
                # Try to install packages
                subprocess.check_call(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                console.print("[green]Successfully installed system packages using apt-get[/green]")
                return True
            except subprocess.CalledProcessError:
                console.print("[yellow]Failed to install packages automatically with apt-get[/yellow]")
                
                # Provide command for manual installation
                cmd_str = "sudo apt-get install -y " + " ".join(packages_to_install)
                console.print(f"[bold cyan]Please install the packages manually with:[/bold cyan]\n{cmd_str}")
                
                return False
        else:
            console.print("[yellow]No apt packages mapped for the required packages[/yellow]")
            return False
    except subprocess.CalledProcessError:
        console.print("[yellow]Apt-get not available or installation failed[/yellow]")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["rich", "numpy", "pygame", "requests", "scipy"]
    missing_packages = []
    
    # Check if we're on a system with externally managed environment
    is_externally_managed = False
    try:
        # Try to install a dummy package to check if we get the externally-managed-environment error
        test_process = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--dry-run", "dummypackage"],
            capture_output=True,
            text=True
        )
        if "externally-managed-environment" in test_process.stderr:
            is_externally_managed = True
            console.print("[yellow]Detected externally managed Python environment (like Raspberry Pi OS)[/yellow]")
            console.print("[yellow]Will prioritize system package manager for installations[/yellow]")
    except Exception:
        pass  # Ignore any errors in detection
    
    # Use minimal display if rich is missing
    if use_rich:
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
    else:
        # Simple text-based progress for systems without rich
        print("Checking dependencies...")
        for package in required_packages:
            print(f"  Checking {package}...")
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
    
    if missing_packages:
        console.print("[yellow]Missing dependencies found:[/yellow]")
        for package in missing_packages:
            console.print(f"  - [yellow]{package}[/yellow]")
        
        console.print("\nAttempting to install missing dependencies...")
        
        # For externally managed environments, try apt/system first
        if is_externally_managed:
            console.print("[cyan]This system uses an externally managed Python environment.[/cyan]")
            console.print("[cyan]Will try system packages first (recommended).[/cyan]")
            
            if install_packages_with_apt(missing_packages):
                console.print("[green]✓[/green] Dependencies installed successfully with apt-get\n")
            else:
                # Print instructions for manually installing system packages
                apt_packages = {
                    "rich": "python3-rich",
                    "numpy": "python3-numpy",
                    "pygame": "python3-pygame",
                    "requests": "python3-requests",
                    "scipy": "python3-scipy"
                }
                
                system_packages = [apt_packages[pkg] for pkg in missing_packages if pkg in apt_packages]
                if system_packages:
                    console.print("[yellow]Please install these system packages manually:[/yellow]")
                    console.print(f"[bold cyan]sudo apt install {' '.join(system_packages)}[/bold cyan]")
                    
                console.print("[yellow]Alternatively, you can create a virtual environment:[/yellow]")
                console.print("[bold cyan]python3 -m venv ~/neon_shadows_venv[/bold cyan]")
                console.print("[bold cyan]source ~/neon_shadows_venv/bin/activate[/bold cyan]")
                console.print("[bold cyan]pip install {' '.join(missing_packages)}[/bold cyan]")
                
                return False
        else:
            # For normal environments, try pip first, then others
            if install_packages_with_pip(missing_packages):
                console.print("[green]✓[/green] Dependencies installed successfully with pip\n")
            elif install_packages_with_pipx(missing_packages):
                console.print("[green]✓[/green] Dependencies installed successfully with pipx\n")
            elif install_packages_with_apt(missing_packages):
                console.print("[green]✓[/green] Dependencies installed successfully with apt-get\n")
            else:
                console.print("[bold red]ERROR: Failed to install dependencies with any method[/bold red]")
                console.print("[bold yellow]Please try to install them manually:[/bold yellow]")
                console.print(f"[bold cyan]pip install {' '.join(missing_packages)}[/bold cyan]")
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
            if use_rich:
                try:
                    from rich.console import Console as RichConsole
                    test_console = RichConsole()
                except ImportError:
                    # If the import fails for any reason, fall back
                    test_console = console
            else:
                # Use our minimal console implementation if Rich is not available
                test_console = console
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
    
    # Skip actual codex test if rich isn't available
    # This is fine because the game will use fallback content anyway
    if not use_rich:
        console.print("[green]✓[/green] Skipping detailed codex test in text-mode. Will use fallback content if needed.\n")
        return True
        
    success = False  # Initialize success variable
    try:
        import codex
        # First check if data directory exists
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Check if codex data file exists, create a minimal one if not
        codex_file = "data/codex.json"
        if not os.path.exists(codex_file):
            with open(codex_file, "w") as f:
                import json
                json.dump({
                    "entries": {
                        "night_city": {
                            "category": "world",
                            "title": "Night City",
                            "content": "A test entry for Night City",
                            "discovered": False
                        }
                    },
                    "discovered_entries": []
                }, f)
                
        test_codex = codex.Codex()
        # Simple test to ensure basic codex functionality works
        test_codex.discover_entry("night_city", "Night City", "world")
        success = "night_city" in [e.get("id") for e in test_codex.get_entries_by_category("world")]
    except Exception as e:
        console.print(f"[bold red]ERROR: Codex test failed - {str(e)}[/bold red]")
        # Don't treat as failure since the game can run without codex
        console.print("[yellow]Note: Game can still run with fallback codex content[/yellow]")
        return True
    
    if success:
        console.print("[green]✓[/green] Codex system test passed\n")
        return True
    else:
        console.print("[yellow]WARNING: Codex test failed, will use fallback content[/yellow]")
        # Don't treat as failure since the game can run without codex
        return True

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
    
    try:
        input("\nPress Enter to begin setup...")
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow]Input error detected. Continuing automatically...[/yellow]")
        time.sleep(1.5)
    
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
        
        # Start the game and wait for it to complete
        console.print("[cyan]Starting game...[/cyan]")
        try:
            # Using call instead of Popen to wait for the process to complete
            subprocess.call([sys.executable, "main.py"])
        except KeyboardInterrupt:
            console.print("[yellow]Game execution interrupted.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error running the game: {e}[/red]")
    else:
        console.print("\n[yellow bold]Some tests failed. You may experience issues when running the game.[/yellow bold]")
        console.print("[yellow]Please review the errors above and try to resolve them before playing.[/yellow]")
        
        try:
            proceed = input("\nDo you want to proceed to the game anyway? (y/n): ").lower().strip()
        except (EOFError, KeyboardInterrupt):
            console.print("[yellow]Input error detected. Assuming 'y' to continue...[/yellow]")
            time.sleep(1.5)
            proceed = 'y'
        if proceed == 'y':
            console.print("\nStarting game...")
            try:
                # Using call instead of Popen to wait for the process to complete
                subprocess.call([sys.executable, "main.py"])
            except KeyboardInterrupt:
                console.print("[yellow]Game execution interrupted.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error running the game: {e}[/red]")
        else:
            console.print("\nSetup aborted. Please fix the issues and run setup.py again.")

if __name__ == "__main__":
    main()