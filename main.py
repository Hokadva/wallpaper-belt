import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QSharedMemory
from PyQt6.QtGui import QIcon, QAction
import keyboard

import modules.config_manager as config_manager
from modules.wallpaper_window import WallpaperWindow
from modules.settings_gui import SettingsWindow

class HotkeySignaler(QObject):
    trigger = pyqtSignal()

class WallpaperEngineApp:
    def __init__(self):
        print("WallpaperEngineApp.__init__ started", flush=True)
        self.config = config_manager.load_config()
        print(f"Config: {self.config}", flush=True)
        
        self.wallpaper_index = 0
        
        print("Creating WallpaperWindow...", flush=True)
        self.wall_window = WallpaperWindow()
        print("WallpaperWindow created", flush=True)
        
        print("Creating SettingsWindow...", flush=True)
        self.settings_window = SettingsWindow(self)
        print("SettingsWindow created", flush=True)
        
        self.wall_hotkey_signaler = HotkeySignaler()
        self.wall_hotkey_signaler.trigger.connect(self.next_wallpaper)
        
        self.group_hotkey_signaler = HotkeySignaler()
        self.group_hotkey_signaler.trigger.connect(self.next_group)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_wallpaper)
        
        print("Setting up tray...", flush=True)
        self.setup_tray()
        print("Tray set up", flush=True)
        
        print("Applying settings...", flush=True)
        self.apply_new_settings()
        print("Settings applied", flush=True)
        
        self.wall_window.update_audio_settings(
            self.config.get("volume", 50),
            self.config.get("mute", False)
        )
        
        print("Loading first wallpaper...", flush=True)
        QTimer.singleShot(1000, self.next_wallpaper)
        
        print("WallpaperEngineApp initialized", flush=True)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        if os.path.exists("icon.png"):
            self.tray_icon.setIcon(QIcon("icon.png"))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
            
        tray_menu = QMenu()
        
        act_settings = QAction("⚙️ Настройки", tray_menu)
        act_settings.triggered.connect(self.show_settings)
        tray_menu.addAction(act_settings)
        
        tray_menu.addSeparator()
        
        act_next = QAction("➡️ Следующие обои", tray_menu)
        act_next.triggered.connect(self.next_wallpaper)
        tray_menu.addAction(act_next)
        
        act_next_group = QAction("🔄 Следующая группа", tray_menu)
        act_next_group.triggered.connect(self.next_group)
        tray_menu.addAction(act_next_group)
        
        tray_menu.addSeparator()
        
        self.groups_menu = QMenu("📁 Выбрать группу", tray_menu)
        tray_menu.addMenu(self.groups_menu)
        
        tray_menu.addSeparator()
        
        act_exit = QAction("❌ Выход", tray_menu)
        act_exit.triggered.connect(self.exit_app)
        tray_menu.addAction(act_exit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.update_groups_menu()
        
        print("Tray icon shown", flush=True)

    def update_groups_menu(self):
        self.groups_menu.clear()
        
        current_group = self.config.get("current_group", "Default")
        groups = list(self.config["groups"].keys())
        
        for group_name in groups:
            action = QAction(group_name, self.groups_menu)
            action.setCheckable(True)
            action.setChecked(group_name == current_group)
            action.triggered.connect(lambda checked, g=group_name: self.select_group(g))
            self.groups_menu.addAction(action)

    def select_group(self, group_name):
        print(f"Selecting group: {group_name}", flush=True)
        self.config["current_group"] = group_name
        config_manager.save_config(self.config)
        
        self.update_groups_menu()
        self.settings_window.group_combo.setCurrentText(group_name)
        
        self.wallpaper_index = 0
        self.next_wallpaper()

    def show_settings(self):
        try:
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
        except Exception as e:
            print(f"Error showing settings: {e}", flush=True)

    def apply_new_settings(self):
        if self.config.get("use_timer", False):
            interval_ms = self.config.get("timer_interval_min", 5) * 60 * 1000
            self.timer.start(interval_ms)
        else:
            self.timer.stop()
            
        keyboard.unhook_all()
        
        hk_wall = self.config.get("hotkey", "")
        if hk_wall:
            try:
                keyboard.add_hotkey(hk_wall, lambda: self.wall_hotkey_signaler.trigger.emit())
                print(f"Hotkey {hk_wall} registered", flush=True)
            except Exception as e: 
                print(f"Hotkey error: {e}", flush=True)
            
        hk_group = self.config.get("group_hotkey", "")
        if hk_group:
            try:
                keyboard.add_hotkey(hk_group, lambda: self.group_hotkey_signaler.trigger.emit())
                print(f"Group hotkey {hk_group} registered", flush=True)
            except Exception as e: 
                print(f"Group hotkey error: {e}", flush=True)
        
        self.update_groups_menu()

    def next_wallpaper(self):
        print("next_wallpaper called", flush=True)
        current_group = self.config.get("current_group", "Default")
        wallpapers = self.config["groups"].get(current_group, [])
        
        print(f"Group: {current_group}, Wallpapers count: {len(wallpapers)}", flush=True)
        
        if not wallpapers:
            print("No wallpapers in group", flush=True)
            return
            
        if self.wallpaper_index >= len(wallpapers):
            self.wallpaper_index = 0
            
        target_wallpaper = wallpapers[self.wallpaper_index]
        print(f"Setting wallpaper {self.wallpaper_index + 1}/{len(wallpapers)}: {target_wallpaper}", flush=True)
        
        self.wall_window.display_wallpaper(target_wallpaper)
        
        self.wallpaper_index = (self.wallpaper_index + 1) % len(wallpapers)

    def next_group(self):
        print("next_group called", flush=True)
        groups = list(self.config["groups"].keys())
        
        if not groups:
            print("No groups available", flush=True)
            return
            
        current = self.config.get("current_group", "Default")
        print(f"Current group: {current}, All groups: {groups}", flush=True)
        
        try:
            current_idx = groups.index(current)
        except ValueError:
            current_idx = 0
            
        next_idx = (current_idx + 1) % len(groups)
        next_group_name = groups[next_idx]
        
        print(f"Switching to group: {next_group_name}", flush=True)
        
        self.config["current_group"] = next_group_name
        config_manager.save_config(self.config)
        
        self.settings_window.group_combo.setCurrentText(next_group_name)
        self.update_groups_menu()
        
        self.wallpaper_index = 0
        self.next_wallpaper()

    def exit_app(self):
        print("Exiting...", flush=True)
        self.wall_window.stop()
        keyboard.unhook_all()
        QApplication.quit()

if __name__ == "__main__":
    print("Starting application...", flush=True)
    
    try:
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)
        
        instance_guard = QSharedMemory("CustomWallpaperEngine_SingleInstance_Key_2026")
        if not instance_guard.create(1):
            print("Another instance running", flush=True)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Приложение Живые обои уже запущено и работает в системном трее (возле часов).")
            msg.exec()
            sys.exit(0)
            
        print("Creating engine...", flush=True)
        engine = WallpaperEngineApp()
        print("Entering event loop...", flush=True)
        sys.exit(app.exec())
    except Exception as e:
        print(f"FATAL: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
