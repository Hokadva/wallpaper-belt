import json
import os
import sys
import winreg

APP_NAME = "WallpaperEngine"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "current_group": "Default",
    "timer_interval_seconds": 300,
    "use_timer": True,
    "hotkey": "ctrl+alt+w",
    "group_hotkey": "ctrl+alt+g",
    "autorun": False,
    "volume": 50,
    "mute": False,
    "random_order": False,
    "groups": {
        "Default": []
    },
    "group_settings": {},  # Настройки для каждой группы
    "file_settings": {}
}

DEFAULT_GROUP_SETTINGS = {
    "scale_mode": "fill",
    "focus_point": "center_center",
    "gif_fps": 10
}


def _ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load_config():
    _ensure_config_dir()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config = {**DEFAULT_CONFIG, **loaded}
                
                if "file_settings" not in config:
                    config["file_settings"] = {}
                if "group_settings" not in config:
                    config["group_settings"] = {}
                
                # Нормализуем пути
                normalized_file_settings = {}
                for path, settings in config["file_settings"].items():
                    normalized_file_settings[os.path.normpath(path)] = settings
                config["file_settings"] = normalized_file_settings
                
                # Добавляем дефолтные настройки для групп без настроек
                for group_name in config["groups"]:
                    if group_name not in config["group_settings"]:
                        config["group_settings"][group_name] = DEFAULT_GROUP_SETTINGS.copy()
                
                return config
        except:
            return DEFAULT_CONFIG.copy()
    
    config = DEFAULT_CONFIG.copy()
    config["group_settings"]["Default"] = DEFAULT_GROUP_SETTINGS.copy()
    return config


def save_config(config):
    _ensure_config_dir()
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    set_autorun(config.get("autorun", False))


def set_autorun(enable=True):
    package_name = "WallpaperBelt"
    
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
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
        print(f"Registry error: {e}")


def get_group_settings(config, group_name):
    """Получает настройки для группы"""
    if group_name not in config["group_settings"]:
        config["group_settings"][group_name] = DEFAULT_GROUP_SETTINGS.copy()
    return config["group_settings"][group_name]


def set_group_settings(config, group_name, settings):
    """Устанавливает настройки для группы"""
    config["group_settings"][group_name] = settings
    save_config(config)


def get_file_settings(config, file_path):
    """Получает настройки для файла с учетом настроек группы"""
    file_path = os.path.normpath(file_path)
    
    if file_path in config["file_settings"]:
        return config["file_settings"][file_path]
    
    for saved_path, settings in config["file_settings"].items():
        if os.path.normpath(saved_path) == file_path:
            return settings
    
    # Возвращаем настройки группы как значения по умолчанию
    group_name = config.get("current_group", "Default")
    group_settings = get_group_settings(config, group_name)
    
    return {
        "customized": False,
        "scale_mode": group_settings.get("scale_mode", "fill"),
        "focus_point": group_settings.get("focus_point", "center_center"),
        "gif_fps": group_settings.get("gif_fps", 10)
    }


def set_file_settings(config, file_path, settings):
    file_path = os.path.normpath(file_path)
    config["file_settings"][file_path] = settings
    save_config(config)


def reset_file_settings(config, file_path):
    file_path = os.path.normpath(file_path)
    
    if file_path in config["file_settings"]:
        del config["file_settings"][file_path]
        save_config(config)
        return
    
    for saved_path in list(config["file_settings"].keys()):
        if os.path.normpath(saved_path) == file_path:
            del config["file_settings"][saved_path]
            save_config(config)
            return
