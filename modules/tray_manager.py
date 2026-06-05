import os
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction


def get_resource_path(relative_path):
    """Получает правильный путь к ресурсам в собранном приложении"""
    if getattr(sys, 'frozen', False):
        # Приложение собрано PyInstaller
        base_path = sys._MEIPASS
    else:
        # Приложение запущено из исходников
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class TrayManager:
    def __init__(self, callbacks):
        self.callbacks = callbacks
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
        """Создает меню трея"""
        menu = QMenu()
        
        act_settings = QAction("Натройки", menu)
        act_settings.triggered.connect(self.callbacks['show_settings'])
        menu.addAction(act_settings)
        menu.addSeparator()
        
        act_next = QAction("Следующие обои", menu)
        act_next.triggered.connect(self.callbacks['next_wallpaper'])
        menu.addAction(act_next)

        act_next_group = QAction("Следующая группа", menu)
        act_next_group.triggered.connect(self.callbacks['next_group'])
        menu.addAction(act_next_group)
        menu.addSeparator()
        
        self.groups_menu = QMenu("Выбрать группу", menu)
        menu.addMenu(self.groups_menu)
        menu.addSeparator()
        
        act_exit = QAction("Выйти", menu)
        act_exit.triggered.connect(self.callbacks['exit_app'])
        menu.addAction(act_exit)
        
        self.tray_icon.setContextMenu(menu)
    
    def update_groups_menu(self, groups, current_group, callback):
        """Обновляет подменю групп"""
        self.groups_menu.clear()
        for group_name in groups:
            action = QAction(group_name, self.groups_menu)
            action.setCheckable(True)
            action.setChecked(group_name == current_group)
            action.triggered.connect(lambda checked, g=group_name: callback(g))
            self.groups_menu.addAction(action)
