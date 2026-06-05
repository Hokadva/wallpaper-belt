# Wallpaper Engine

A Windows desktop wallpaper changer with support for static images, GIF animations, and video wallpapers.

## Features

- Support for images (PNG, JPG, JPEG, BMP)
- Support for videos (MP4, AVI, MKV, MOV, WMV, WebM)
- Support for GIF animations with customizable FPS
- Groups for organizing wallpapers
- Timer-based automatic wallpaper change (1 second to 24 hours)
- Random or sequential wallpaper order
- Hotkeys for changing wallpapers and groups
- Two scaling modes: Fill and Crop
- 9 focus points for crop mode (interactive grid)
- Volume control for video wallpapers
- Drag and drop sorting
- Quick move buttons for list items
- System tray integration
- Auto-start with Windows
- Fast wallpaper switching without delays
- Pause animations when desktop is hidden

## Installation

### Download executable

Download the latest `WallpaperEngine.exe` from the [Releases page](https://github.com/yourusername/wallpaper-belt/releases)

### Run from source

```bash
# Clone the repository
git clone https://github.com/yourusername/wallpaper-belt.git
cd wallpaper-belt
```
# Create virtual environment
```
python -m venv venv
```

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements

# Run the application
python main.py

# Usage
Basic functions
Add wallpapers: Click "Add" and select files

Groups: Create groups for different wallpaper sets

Change wallpaper:

Automatically by timer

Via hotkey (default Ctrl+Alt+W)

Through tray menu

Change group: Ctrl+Alt+G or through tray menu

# Scaling settings
For each file you can choose:

Fill - stretches image to fill screen

Crop - crops image while preserving aspect ratio

In crop mode, a 3x3 grid is available for selecting the focus point:

```
+-----------+-----------+-----------+
|           |           |           |
| Top-Left  | Top-Center| Top-Right |
|           |           |           |
+-----------+-----------+-----------+
|           |           |           |
| Mid-Left  |  Center   | Mid-Right |
|           |           |           |
+-----------+-----------+-----------+
|           |           |           |
| Bot-Left  | Bot-Center| Bot-Right |
|           |           |           |
+-----------+-----------+-----------+
```
# Timer
Set wallpaper change interval with second precision:

Hours (0-23)

Minutes (0-59)

Seconds (0-59)

# Hotkeys
Configure custom key combinations:

Click the record button

Press desired key combination

Press Enter to save

#Drag and Drop
Reorder wallpapers by dragging or using buttons:

Up/Down by 1 position

Up/Down by 5 positions

Move to top/bottom

# Project structure
```
wallpaper-belt/
├── main.py                    # Entry point
├── build.spec                 # PyInstaller spec
├── icon.png                   # Application icon
├── wallpaper_config.json      # Configuration file
└── modules/
    ├── wallpaper_engine.py    # Wallpaper engine
    ├── settings_ui.py         # Settings interface
    ├── config_manager.py      # Configuration manager
    ├── hotkey_manager.py      # Hotkey manager
    └── tray_manager.py        # Tray manager
```
# Requirements
Windows 10/11

Python 3.9+ (for running from source)

PyQt6

# License
MIT License

# Links
Download latest release