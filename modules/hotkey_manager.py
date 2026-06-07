import keyboard
from PyQt6.QtCore import QObject, pyqtSignal


class HotkeyManager(QObject):
    """Управление горячими клавишами"""
    
    wallpaper_trigger = pyqtSignal()
    group_trigger = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._wallpaper_hk = None
        self._group_hk = None
    
    def register_hotkeys(self, wallpaper_hk, group_hk):
        """Регистрирует горячие клавиши"""
        keyboard.unhook_all()
        
        if wallpaper_hk:
            try:
                keyboard.add_hotkey(wallpaper_hk, lambda: self.wallpaper_trigger.emit())
                self._wallpaper_hk = wallpaper_hk
            except Exception as e:
                print(f"Hotkey error: {e}")
        
        if group_hk:
            try:
                keyboard.add_hotkey(group_hk, lambda: self.group_trigger.emit())
                self._group_hk = group_hk
            except Exception as e:
                print(f"Group hotkey error: {e}")
    
    def unregister_all(self):
        """Отключает все горячие клавиши"""
        keyboard.unhook_all()
