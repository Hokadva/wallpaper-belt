import json
import os
import sys
import winreg

CONFIG_FILE = "wallpaper_config.json"

DEFAULT_CONFIG = {
    "current_group": "Default",
    "timer_interval_min": 5,
    "use_timer": True,
    "hotkey": "ctrl+alt+w",
    "group_hotkey": "ctrl+alt+g",
    "autorun": False,
    "volume": 50,
    "mute": False,
    "groups": {
        "Default": []
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    set_autorun(config.get("autorun", False))

def set_autorun(enable=True):
    package_name = "CustomWallpaperEngine"
    exe_path = os.path.abspath(sys.argv[0])
    
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        with reg_key:
            if enable:
                winreg.SetValueEx(reg_key, package_name, 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(reg_key, package_name)
                except FileNotFoundError:
                    pass
    except Exception as e:
        print(f"Ошибка изменения реестра: {e}")
