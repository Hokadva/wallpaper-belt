"""The main application file"""
import random
import sys
import traceback

from PyQt6.QtCore import QSharedMemory, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

import modules.config_manager as config_manager
from modules.hotkey_manager import HotkeyManager
from modules.localizer import Localizer
from modules.settings_ui import SettingsWindow
from modules.tray_manager import TrayManager
from modules.wallpaper_window import WallpaperBelt


class WallpaperApp:
    """The main class of the application"""
    def __init__(self):
        """Application initialization"""
        self.config = config_manager.load_config()
        self.localizer = Localizer(self.config.get("language", "en"))

        self.wallpaper_index = 0

        self.engine = WallpaperBelt()
        self.hotkeys = HotkeyManager()
        self.settings_ui = SettingsWindow(self, self.localizer)

        self.tray = TrayManager({
            'show_settings': self.show_settings,
            'next_wallpaper': self.next_wallpaper,
            'random_wallpaper': self.random_wallpaper,
            'next_group': self.next_group,
            'select_group': self.select_group,
            'exit_app': self.exit_app
        }, self.localizer)

        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)

        self.hotkeys.wallpaper_trigger.connect(self.next_wallpaper)
        self.hotkeys.group_trigger.connect(self.next_group)

        self._apply_settings()
        QTimer.singleShot(1000, self.next_wallpaper)

    def refresh_config(self):
        """A function that updates the application configuration"""
        self.config = config_manager.load_config()
        self._apply_settings()
        self.tray._setup_menu()

    def _apply_settings(self):
        """A function that applies settings"""
        if self.config.get("use_timer", False):
            if "timer_interval_seconds" in self.config:
                interval_ms = self.config["timer_interval_seconds"] * 1000
            else:
                interval_ms = (
                    self.config.get("timer_interval_min", 5) * 60 * 1000)
            self.timer.start(interval_ms)
        else:
            self.timer.stop()

        self.hotkeys.register_hotkeys(
            self.config.get("hotkey", ""),
            self.config.get("group_hotkey", "")
        )

        self.tray.update_groups_menu(
            list(self.config["groups"].keys()),
            self.config.get("current_group", "Default"),
            self.select_group
        )

        self.tray.apply_language_to_tray()

    def _timer_tick(self):
        """Timer Handler"""
        if self.config.get("random_order", False):
            self.random_wallpaper()
        else:
            self.next_wallpaper()

    def next_wallpaper(self):
        """The following wallpapers are in order"""
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
        """
        A function for selecting random wallpapers from a
        list and then installing them.
        """
        group = self.config.get("current_group", "Default")
        wallpapers = self.config["groups"].get(group, [])

        if not wallpapers:
            return

        if len(wallpapers) == 1:
            path = wallpapers[0]
        else:
            if (self.wallpaper_index > 0 and
               self.wallpaper_index <= len(wallpapers)):
                current = wallpapers[self.wallpaper_index - 1]
            else:
                current = wallpapers[-1]

            available = [w for w in wallpapers if w != current] or wallpapers
            path = random.choice(available)
            self.wallpaper_index = wallpapers.index(path)

        self.engine.set_wallpaper(path)
        self.wallpaper_index = (self.wallpaper_index + 1) % len(wallpapers)

    def next_group(self):
        """A function for switching groups"""
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
        """Group Selection"""
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
        """A function that opens the settings window"""
        self.settings_ui.show()
        self.settings_ui.raise_()
        self.settings_ui.activateWindow()

    def exit_app(self):
        """Exiting the app"""
        self.engine.stop()
        self.hotkeys.unregister_all()
        QApplication.quit()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)

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
