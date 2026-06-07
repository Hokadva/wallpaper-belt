"""the tray management module"""
import os
import sys

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


def get_resource_path(relative_path):
    """Gets the correct path to resources in the compiled application"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TrayManager:
    """Tray management class"""
    def __init__(self, callbacks, localizer):
        """Setting the tray settings"""
        self.callbacks = callbacks
        self.loc = localizer
        self.tray_icon = QSystemTrayIcon()

        icon_path = get_resource_path("icon.png")

        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_DesktopIcon
            ))

        self.groups_menu = None
        self._setup_menu()
        self.tray_icon.show()

    def _setup_menu(self):
        """Create menu in tray"""
        menu = QMenu()

        self.act_settings = QAction(menu)
        self.act_settings.triggered.connect(self.callbacks['show_settings'])
        menu.addAction(self.act_settings)
        menu.addSeparator()

        self.act_next = QAction(menu)
        self.act_next.triggered.connect(self.callbacks['next_wallpaper'])
        menu.addAction(self.act_next)

        self.act_next_group = QAction(menu)
        self.act_next_group.triggered.connect(self.callbacks['next_group'])
        menu.addAction(self.act_next_group)
        menu.addSeparator()

        self.groups_menu = QMenu(menu)
        menu.addMenu(self.groups_menu)
        menu.addSeparator()

        self.act_exit = QAction(menu)
        self.act_exit.triggered.connect(self.callbacks['exit_app'])
        menu.addAction(self.act_exit)

        self.tray_icon.setContextMenu(menu)

        self.apply_language_to_tray()

    def apply_language_to_tray(self):
        """Update language in tray"""
        translations = {
            self.act_settings: "tray_settings",
            self.act_next: "tray_next",
            self.act_next_group: "tray_next_group",
            self.groups_menu: "tray_select_group",
            self.act_exit: "tray_exit"
        }

        for tray_element, key in translations.items():
            text = self.loc.get_string(key)
            if hasattr(tray_element, "setText"):
                tray_element.setText(text)
            elif hasattr(tray_element, "setTitle"):
                tray_element.setTitle(text)

    def update_groups_menu(self, groups, current_group, callback):
        """Updates the groups submenu"""
        self.groups_menu.clear()
        for group_name in groups:
            action = QAction(group_name, self.groups_menu)
            action.setCheckable(True)
            action.setChecked(group_name == current_group)
            action.triggered.connect(lambda checked, g=group_name: callback(g))
            self.groups_menu.addAction(action)
