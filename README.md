# Wallpaper Belt

A Windows desktop wallpaper manager with support for static images, GIF animations, and video wallpapers. Features automatic rotation, customizable hotkeys, and per-file scaling options.

## Features

- **Multiple formats**: PNG, JPG, JPEG, BMP, GIF, MP4, AVI, MKV, MOV, WMV, WebM
- **Groups**: Organize wallpapers into separate groups
- **Timer**: Automatic wallpaper rotation (1 second to 24 hours)
- **Random mode**: Shuffle wallpapers randomly
- **Hotkeys**: Customizable keyboard shortcuts for next wallpaper and next group
- **Scaling modes**: Fill (stretch) or Crop with 9 focus points
- **Interactive focus grid**: Click on a 3x3 grid to choose what part of the image to keep when cropping
- **Per-file settings**: Override default scaling for individual files
- **Drag and drop**: Reorder wallpapers by dragging or using quick move buttons
- **GIF support**: Animated wallpapers with configurable pause when desktop is hidden
- **Video support**: Video wallpapers with volume control
- **System tray**: Minimizes to tray with quick access menu
- **Autorun**: Option to start with Windows
- **Multilingual**: Available in 7 languages (English, German, Esperanto, Spanish, French, Russian, Chinese)
- **Duplicate detection**: Automatically skips files already in the group
- **No desktop clutter**: Configuration stored in `%APPDATA%`, temporary files in `%TEMP%`

## Installation

### Download

Download the latest `WallpaperBelt.exe` from the [Releases](https://github.com/yourusername/wallpaper-belt/releases) page.

No installation required — the executable is portable.

### Run from source

```bash
git clone https://github.com/yourusername/wallpaper-belt.git
cd wallpaper-belt
python -m venv venv
venv\Scripts\activate
pip install PyQt6 keyboard
python main.py
```

# Build from source

```bash
pip install pyinstaller Pillow
pyinstaller build.spec
```

Output: dist/WallpaperBelt.exe

# Usage
# Getting started
1) Launch the application — it appears in the system tray
2) Right-click the tray icon and select Settings
3) Add wallpaper files to the default group or create new groups
4) Configure timer, hotkeys, and scaling preferences
5) Click Save & Apply

| Default hotkeys | |
| --------------------- | -------------------------- |
| Action | Shortcut |
| Next wallpaper | Ctrl + Alt + W |
| Next group | Ctrl + Alt + G |

# Scaling modes
 - Fill: Stretches the image to fill the entire screen (may distort aspect ratio)
 - Crop: Crops the image to fit the screen while preserving aspect ratio


When using Crop mode, a 3x3 grid appears on the preview:
```
| --------- | --------- | --------- |
| Top-Left  | Top-Center| Top-Right |
| --------- | --------- | --------- |
| Mid-Left  |  Center   | Mid-Right |
| --------- | --------- | --------- |
| Bot-Left  | Bot-Center| Bot-Right |
| --------- | --------- | --------- |
```

Click any point to choose which part of the image is kept when cropping.

# Timer
Set any interval from 1 second to 23 hours, 59 minutes, 59 seconds.

# Language
Click the language button in the top-right corner of the settings window to switch between available languages.

# Configuration
Settings are stored in:

```
%APPDATA%\WallpaperBelt\config.json
```

Temporary wallpaper files are stored in:

```
%TEMP%\wallpaper_static.bmp
%TEMP%\wallpaper_frame.bmp
```

# Requirements
 - Windows 10 or Windows 11
 - No additional software required for the executable

For running from source:
 - Python 3.9+
 - PyQt6
 - keyboard

Project structure

```
wallpaper-belt/
├── main.py                    # Application entry point
├── build.spec                 # PyInstaller build specification
├── icon.png                   # Application icon
├── locales/                   # Translation files
│   ├── en.json
│   ├── ru.json
│   ├── de.json
│   ├── eo.json
│   ├── es.json
│   ├── fr.json
│   └── zh.json
└── modules/
    ├── wallpaper_engine.py    # Wallpaper rendering engine
    ├── settings_ui.py         # Settings window interface
    ├── config_manager.py      # Configuration file management
    ├── hotkey_manager.py      # Global hotkey registration
    ├── tray_manager.py        # System tray icon and menu
    └── localizer.py           # Localization support
```

# License

MIT License

# Links

 - [Download](https://github.com/Hokadva/wallpaper-belt/releases)
 - [Report a bug](https://github.com/Hokadva/wallpaper-belt/issues)
