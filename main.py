import sys
import random
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QSharedMemory

import modules.config_manager as config_manager
from modules.wallpaper_window import WallpaperBelt
from modules.hotkey_manager import HotkeyManager
from modules.tray_manager import TrayManager
from modules.settings_ui import SettingsWindow


class WallpaperApp:
    """Главный класс приложения"""
    
    def __init__(self):
        self.config = config_manager.load_config()
        self.wallpaper_index = 0
        
        # Инициализация компонентов
        self.engine = WallpaperBelt()
        self.hotkeys = HotkeyManager()
        self.settings_ui = SettingsWindow(self)
        
        # Трей
        self.tray = TrayManager({
            'show_settings': self.show_settings,
            'next_wallpaper': self.next_wallpaper,
            'next_group': self.next_group,
            'select_group': self.select_group,
            'exit_app': self.exit_app
        })
        
        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)
        
        # Подключаем хоткеи
        self.hotkeys.wallpaper_trigger.connect(self.next_wallpaper)
        self.hotkeys.group_trigger.connect(self.next_group)
        
        # Применяем настройки
        self._apply_settings()
        
        # Загружаем первые обои
        QTimer.singleShot(1000, self.next_wallpaper)
    
    def _apply_settings(self):
        """Применяет все настройки"""
        # Таймер
        if self.config.get("use_timer", False):
            if "timer_interval_seconds" in self.config:
                interval_ms = self.config["timer_interval_seconds"] * 1000
            else:
                interval_ms = self.config.get("timer_interval_min", 5) * 60 * 1000
            self.timer.start(interval_ms)
        else:
            self.timer.stop()
        
        # Хоткеи
        self.hotkeys.register_hotkeys(
            self.config.get("hotkey", ""),
            self.config.get("group_hotkey", "")
        )
        
        # Аудио
        self.engine.update_audio(
            self.config.get("volume", 50),
            self.config.get("mute", False)
        )
        
        # Меню групп
        self.tray.update_groups_menu(
            list(self.config["groups"].keys()),
            self.config.get("current_group", "Default"),
            self.select_group
        )
    
    def _timer_tick(self):
        """Обработчик таймера"""
        if self.config.get("random_order", False):
            self.random_wallpaper()
        else:
            self.next_wallpaper()
    
    def next_wallpaper(self):
        """Следующие обои по порядку"""
        group = self.config.get("current_group", "Default")
        wallpapers = self.config["groups"].get(group, [])
        is_random_order = self.config["group_hotkey"]
        
        if not wallpapers:
            return

        if is_random_order:
            self.random_wallpaper()
            return

        if self.wallpaper_index >= len(wallpapers):
            self.wallpaper_index = 0
        
        path = wallpapers[self.wallpaper_index]
        self.engine.set_wallpaper(path)
        self.wallpaper_index = (self.wallpaper_index + 1) % len(wallpapers)
    
    def random_wallpaper(self):
        """Случайные обои"""
        group = self.config.get("current_group", "Default")
        wallpapers = self.config["groups"].get(group, [])
        
        if not wallpapers:
            return
        
        if len(wallpapers) == 1:
            path = wallpapers[0]
        else:
            # Исключаем текущее
            if self.wallpaper_index > 0 and self.wallpaper_index <= len(wallpapers):
                current = wallpapers[self.wallpaper_index - 1]
            else:
                current = wallpapers[-1]
            
            available = [w for w in wallpapers if w != current] or wallpapers
            path = random.choice(available)
            self.wallpaper_index = wallpapers.index(path)
        
        self.engine.set_wallpaper(path)
        self.wallpaper_index = (self.wallpaper_index + 1) % len(wallpapers)
    
    def next_group(self):
        """Следующая группа"""
        groups = list(self.config["groups"].keys())
        if not groups:
            return
        
        current = self.config.get("current_group", "Default")
        try:
            idx = groups.index(current)
        except ValueError:
            idx = -1
        
        next_name = groups[(idx + 1) % len(groups)]
        self.select_group(next_name)
    
    def select_group(self, group_name):
        """Выбор группы"""
        self.config["current_group"] = group_name
        config_manager.save_config(self.config)
        
        self.tray.update_groups_menu(
            list(self.config["groups"].keys()),
            group_name,
            self.select_group
        )
        
        self.settings_ui.group_combo.setCurrentText(group_name)
        self.wallpaper_index = 0
        self.next_wallpaper()
    
    def show_settings(self):
        """Показывает окно настроек"""
        self.settings_ui.show()
        self.settings_ui.raise_()
        self.settings_ui.activateWindow()
    
    def refresh_config(self):
        """Перезагружает конфиг и применяет настройки"""
        self.config = config_manager.load_config()
        self._apply_settings()
    
    def exit_app(self):
        """Выход из приложения"""
        self.engine.stop()
        self.hotkeys.unregister_all()
        QApplication.quit()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)
        
        # Проверка на второй экземпляр
        guard = QSharedMemory("WallpaperBelt_SingleInstance")
        if not guard.create(1):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Приложение уже запущено в системном трее.")
            msg.exec()
            sys.exit(0)
        
        wallpaper_app = WallpaperApp()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"FATAL: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
