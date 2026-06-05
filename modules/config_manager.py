import json
import os
import sys
import winreg

CONFIG_FILE = "wallpaper_config.json"

DEFAULT_CONFIG = {
    "current_group": "Default",
    "timer_interval_min": 1,
    "use_timer": True,
    "hotkey": "ctrl+alt+w",
    "group_hotkey": "ctrl+alt+g",
    "autorun": False,
    "volume": 50,
    "mute": False,
    "default_scale_mode": "fill",
    "default_focus_point": "center",
    "default_gif_fps": 10,
    "random_order": False,
    "groups": {
        "Default": []
    },
    "file_settings": {}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config = {**DEFAULT_CONFIG, **loaded}
                if "file_settings" not in config:
                    config["file_settings"] = {}
                
                # Нормализуем все пути в file_settings
                normalized_settings = {}
                for path, settings in config["file_settings"].items():
                    normalized_path = os.path.normpath(path)
                    normalized_settings[normalized_path] = settings
                config["file_settings"] = normalized_settings
                
                return config
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

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

def get_file_settings(config, file_path):
    """Получает настройки для конкретного файла с учетом общих настроек по умолчанию"""
    file_path = os.path.normpath(file_path)
    
    # Проверяем точное совпадение
    if file_path in config["file_settings"]:
        return config["file_settings"][file_path]
    
    # Проверяем все пути
    for saved_path, settings in config["file_settings"].items():
        if os.path.normpath(saved_path) == file_path:
            return settings
    
    # Возвращаем общие настройки по умолчанию
    return {
        "customized": False,
        "scale_mode": config.get("default_scale_mode", "fill"),
        "focus_point": config.get("default_focus_point", "center"),
        "gif_fps": config.get("default_gif_fps", 10)
    }

def set_file_settings(config, file_path, settings):
    """Устанавливает настройки для конкретного файла"""
    file_path = os.path.normpath(file_path)
    config["file_settings"][file_path] = settings
    save_config(config)

def reset_file_settings(config, file_path):
    """Сбрасывает настройки файла"""
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