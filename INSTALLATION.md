# Neon Shadows: Installation & Running Guide

This document provides detailed instructions for installing and running Neon Shadows, a text-based cyberpunk adventure game.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/neon-shadows.git
cd neon-shadows

# Install required packages
pip install -r requirements.txt

# Run the setup utility to verify your system is ready
python setup.py

# Or run the game directly
python main.py
```

## System Requirements

- **Python**: 3.8 or higher
- **Operating Systems**: Windows, macOS, Linux
- **Terminal**: Any terminal with color support
- **Disk Space**: Approximately 10MB
- **RAM**: Minimal (< 100MB)
- **Display**: Terminal with at least 80×24 characters for best experience

## Detailed Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/neon-shadows.git
cd neon-shadows
```

### Step 2: Python Environment

Neon Shadows requires Python 3.8 or higher. Verify your Python version:

```bash
python --version
```

If you need to install Python, download it from [python.org](https://www.python.org/downloads/).

### Step 3: Install Dependencies

The game requires several Python packages to run properly. You can install them using one of the following methods:

#### Using the Setup Utility (Recommended)

```bash
python setup.py
```

This will automatically check your system, install missing dependencies, and test key components.

#### Using pip

```bash
pip install rich pygame requests numpy scipy
```

#### Using requirements.txt

```bash
pip install -r requirements.txt
```

#### For Virtual Environment Users

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Game

### Standard Launch

To start the game normally:

```bash
python main.py
```

### With Setup Check

To perform system checks before launching:

```bash
python setup.py
```

### Component Tests

The game includes test modules for specific components:

```bash
# Test ASCII art display
python test_ascii_art.py

# Test animation system
python test_animations.py

# Test new animations
python test_new_animations.py

# Test tactical combat system
python test_tactical_combat.py

# Test tactical abilities
python test_tactical_abilities.py

# Test dynamic codex
python test_dynamic_codex.py
```

## Optional Features

### Ollama Integration for AI-Generated Content

Neon Shadows can use Ollama, a local LLM, to generate dynamic story content.

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a compatible model:
   ```bash
   ollama pull llama2
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```
4. Enable Ollama in the game by editing `config.py`:
   ```python
   USE_OLLAMA = True
   ```

## Troubleshooting

### Common Issues

#### Terminal Display Issues

- **Problem**: Text formatting appears incorrect or colors don't display
- **Solution**: Make sure the rich library is installed and your terminal supports ANSI color codes

#### Missing Module Errors

- **Problem**: "ModuleNotFoundError" when starting the game
- **Solution**: Run `python setup.py` to automatically install missing dependencies

#### Audio Not Working

- **Problem**: No sound effects or music
- **Solution**: Verify pygame is installed with `pip show pygame`

#### Game Crashes During Combat

- **Problem**: Game crashes with an error during combat
- **Solution**: Make sure all dependencies are installed, especially numpy and scipy

### Running the Diagnostic Tool

```bash
python setup.py
```

This will:
1. Check Python version
2. Verify all dependencies
3. Test critical game components
4. Provide detailed error reports if issues are found

## Advanced Configuration

### Game Settings

You can customize various game settings by editing `game_settings.json`:

```json
{
  "audio": {
    "music_volume": 0.5,
    "effects_volume": 0.7,
    "music_enabled": true,
    "effects_enabled": true
  },
  "ui": {
    "animation_speed": "normal",
    "animations_enabled": true,
    "color_theme": "default"
  },
  "gameplay": {
    "difficulty": "normal",
    "auto_save": true
  }
}
```

### Developer Mode

For developers and testers, the game includes a hidden developer mode:

1. Start the game
2. At the main menu, type `dev` instead of selecting a menu option
3. Access developer tools like quick character creation, combat testing, etc.

## Support and Community

For help with installation or gameplay:

- Open an issue on GitHub
- Join our Discord server: [link to discord]
- Visit our community forum: [link to forum]

## Updating the Game

To update to the latest version:

```bash
# Navigate to game directory
cd neon-shadows

# Pull latest changes
git pull

# Re-run setup to check for new dependencies
python setup.py
```

## Uninstallation

To uninstall the game:

1. Delete the game directory
2. Optionally, uninstall dependencies that were installed specifically for this game