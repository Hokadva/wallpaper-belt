"""A menu with settings is created in this module."""
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFileDialog, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QListWidget, QMainWindow, QMessageBox,
                             QPushButton, QRadioButton, QScrollArea, QSpinBox,
                             QVBoxLayout, QWidget)

import modules.config_manager as config_manager


class SettingsWindow(QMainWindow):
    def __init__(self, app_core, localizer):
        """This function sets the buttons for the main settings menu."""
        super().__init__()
        self.core = app_core
        self.loc = localizer

        self.setMinimumSize(800, 600)

        self.recording_target = None
        self.current_recorded_keys = []
        self.temp_wall_hk = ""
        self.temp_group_hk = ""

        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main content
        h_base_layout = QHBoxLayout()
        main_layout.addLayout(h_base_layout, 1)

        # left panel
        left_widget = QWidget()
        left_widget.setMinimumWidth(350)
        left_widget.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)

        # Select group
        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.currentTextChanged.connect(self.change_active_group)
        btn_add_group = QPushButton("+")
        btn_add_group.setFixedWidth(40)
        btn_add_group.clicked.connect(self.add_new_group)
        btn_add_group.setToolTip(self.loc.get_string("add_group"))
        btn_remove_group = QPushButton("-")
        btn_remove_group.setFixedWidth(40)
        btn_remove_group.clicked.connect(self.remove_group)
        btn_remove_group.setToolTip(self.loc.get_string("remove_group"))
        group_layout.addWidget(QLabel())
        group_layout.addWidget(self.group_combo, 1)
        group_layout.addWidget(btn_add_group)
        group_layout.addWidget(btn_remove_group)
        left_layout.addLayout(group_layout)

        # File list Drag & Drop
        self.left_layout_label = QLabel()
        left_layout.addWidget(self.left_layout_label)
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        left_layout.addWidget(self.file_list, 1)

        # Buttons manage file
        file_btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton()
        self.btn_add_file.clicked.connect(self.add_files_to_group)
        self.btn_remove_file = QPushButton()
        self.btn_remove_file.clicked.connect(self.remove_file_from_group)
        file_btn_layout.addWidget(self.btn_add_file)
        file_btn_layout.addWidget(self.btn_remove_file)
        left_layout.addLayout(file_btn_layout)

        # Move buttons
        move_group = QGroupBox()
        move_layout = QVBoxLayout()

        # Up buttons
        top_row = QHBoxLayout()
        self.btn_move_top = QPushButton()
        self.btn_move_top.clicked.connect(lambda: self.move_item(-999))
        self.btn_move_up5 = QPushButton("+5")
        self.btn_move_up5.clicked.connect(lambda: self.move_item(-5))
        self.btn_move_up1 = QPushButton("+1")
        self.btn_move_up1.clicked.connect(lambda: self.move_item(-1))
        top_row.addWidget(self.btn_move_top)
        top_row.addWidget(self.btn_move_up5)
        top_row.addWidget(self.btn_move_up1)
        move_layout.addLayout(top_row)

        # Low buttons
        bottom_row = QHBoxLayout()
        self.btn_move_bottom = QPushButton()
        self.btn_move_bottom.clicked.connect(lambda: self.move_item(999))
        self.btn_move_down5 = QPushButton("-5")
        self.btn_move_down5.clicked.connect(lambda: self.move_item(5))
        self.btn_move_down1 = QPushButton("-1")
        self.btn_move_down1.clicked.connect(lambda: self.move_item(1))
        bottom_row.addWidget(self.btn_move_bottom)
        bottom_row.addWidget(self.btn_move_down5)
        bottom_row.addWidget(self.btn_move_down1)
        move_layout.addLayout(bottom_row)

        move_group.setLayout(move_layout)
        left_layout.addWidget(move_group)

        # Right panel - settings
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; }")

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Preview with a focus grid
        self.preview_group = QGroupBox()
        preview_layout = QVBoxLayout()

        # Preview container with overlay
        self.preview_container = QWidget()
        self.preview_container.setFixedSize(320, 240)
        self.preview_container.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;")

        # Label with image
        self.preview_label = QLabel(self.preview_container)
        self.preview_label.setGeometry(0, 0, 320, 240)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3x3 Focus Button Grid
        self.focus_buttons = {}
        focus_positions = [
            ('top_left', 5, 5),
            ('top_center', 145, 5),
            ('top_right', 285, 5),
            ('center_left', 5, 105),
            ('center_center', 145, 105),
            ('center_right', 285, 105),
            ('bottom_left', 5, 205),
            ('bottom_center', 145, 205),
            ('bottom_right', 285, 205),
        ]

        for name, x, y in focus_positions:
            btn = QPushButton("", self.preview_container)
            btn.setFixedSize(25, 25)
            btn.move(x, y)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 150);
                    border: 2px solid #888;
                    border-radius: 12px;
                    color: #333;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: rgba(42, 130, 218, 200);
                    border: 2px solid #1a5fa0;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(200, 200, 200, 200);
                }
            """)
            btn.clicked.connect(
                lambda checked, n=name: self._on_focus_button_clicked(n))
            btn.setToolTip({
                'top_left': self.loc.get_string("focus_top_left"),
                'top_center': self.loc.get_string("focus_top"),
                'top_right': self.loc.get_string("focus_top_right"),
                'center_left': self.loc.get_string("focus_left"),
                'center_center': self.loc.get_string("focus_center"),
                'center_right': self.loc.get_string("focus_right"),
                'bottom_left': self.loc.get_string("focus_bottom_left"),
                'bottom_center': self.loc.get_string("focus_bottom"),
                'bottom_right': self.loc.get_string("focus_bottom_right"),
            }[name])
            btn.hide()
            self.focus_buttons[name] = btn

        preview_layout.addWidget(self.preview_container)

        # A preview hint
        self.focus_hint_label = QLabel()
        self.focus_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_hint_label.setStyleSheet(
            "color: #2a82da; font-weight: bold; padding: 4px;")
        self.focus_hint_label.hide()
        preview_layout.addWidget(self.focus_hint_label)

        self.preview_group.setLayout(preview_layout)
        right_layout.addWidget(self.preview_group)

        # Individual file settings
        self.file_settings_group = QGroupBox()
        self.file_settings_group.setEnabled(False)
        file_settings_layout = QVBoxLayout()

        # Scaling
        self.file_settings_layout_label = QLabel()
        file_settings_layout.addWidget(self.file_settings_layout_label)
        self.radio_fill = QRadioButton()
        self.radio_fit = QRadioButton()
        self.radio_fill.toggled.connect(self._on_scale_mode_changed)
        self.radio_fit.toggled.connect(self._on_scale_mode_changed)
        file_settings_layout.addWidget(self.radio_fill)
        file_settings_layout.addWidget(self.radio_fit)

        # The Focus grid display checkbox
        self.chk_show_focus_grid = QCheckBox()
        self.chk_show_focus_grid.toggled.connect(
            self._on_show_focus_grid_toggled)
        file_settings_layout.addWidget(self.chk_show_focus_grid)

        # Reset button
        self.btn_reset = QPushButton()
        self.btn_reset.clicked.connect(self.reset_file_settings)
        file_settings_layout.addWidget(self.btn_reset)

        self.file_settings_group.setLayout(file_settings_layout)
        right_layout.addWidget(self.file_settings_group)

        self.file_settings_group.setLayout(file_settings_layout)
        right_layout.addWidget(self.file_settings_group)

        # Main group settings
        self.group_settings_group = QGroupBox()
        group_settings_layout = QVBoxLayout()

        self.group_settings_layout_label = QLabel()
        group_settings_layout.addWidget(self.group_settings_layout_label)

        # Scaling for group
        group_scale_layout = QHBoxLayout()
        self.group_radio_fill = QRadioButton()
        self.group_radio_fit = QRadioButton()
        group_scale_layout.addWidget(self.group_radio_fill)
        group_scale_layout.addWidget(self.group_radio_fit)
        group_settings_layout.addLayout(group_scale_layout)

        # The checkbox for displaying the grid for group
        self.group_chk_show_focus = QCheckBox()
        self.group_chk_show_focus.toggled.connect(
            self._on_group_show_focus_toggled)
        group_settings_layout.addWidget(self.group_chk_show_focus)

        # A hint for focus
        self.group_focus_hint = QLabel()
        self.group_focus_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_focus_hint.setStyleSheet(
            "color: #2a82da; font-weight: bold;")
        self.group_focus_hint.hide()
        group_settings_layout.addWidget(self.group_focus_hint)

        self.group_settings_group.setLayout(group_settings_layout)
        right_layout.addWidget(self.group_settings_group)

        self.general_group = QGroupBox()
        self.general_layout = QVBoxLayout()

        # Timer
        self.general_layout_timer_label = QLabel()
        self.general_layout.addWidget(self.general_layout_timer_label)
        self.chk_timer = QCheckBox()
        self.chk_timer.stateChanged.connect(self.on_timer_check_changed)
        self.general_layout.addWidget(self.chk_timer)

        self.timer_input_layout = QHBoxLayout()

        hours_label = QVBoxLayout()
        self.hours_layout_label = QLabel()
        hours_label.addWidget(self.hours_layout_label)
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 23)
        self.spin_hours.setEnabled(False)
        hours_label.addWidget(self.spin_hours)
        self.timer_input_layout.addLayout(hours_label)

        minutes_layout = QVBoxLayout()
        self.minutes_layout_label = QLabel()
        minutes_layout.addWidget(self.minutes_layout_label)
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(0, 59)
        self.spin_minutes.setEnabled(False)
        minutes_layout.addWidget(self.spin_minutes)
        self.timer_input_layout.addLayout(minutes_layout)

        seconds_layout = QVBoxLayout()
        self.seconds_layout_label = QLabel()
        seconds_layout.addWidget(self.seconds_layout_label)
        self.spin_seconds = QSpinBox()
        self.spin_seconds.setRange(0, 59)
        self.spin_seconds.setEnabled(False)
        seconds_layout.addWidget(self.spin_seconds)
        self.timer_input_layout.addLayout(seconds_layout)

        self.general_layout.addLayout(self.timer_input_layout)

        # Random order
        self.chk_random_order = QCheckBox()
        self.general_layout.addWidget(self.chk_random_order)

        # Hotkeys
        self.general_layout_hk_label = QLabel()
        self.general_layout.addWidget(self.general_layout_hk_label)

        hk_wall_layout = QHBoxLayout()
        self.hk_wall_layout_label = QLabel()
        hk_wall_layout.addWidget(self.hk_wall_layout_label)
        self.btn_hk_wall = QPushButton("ctrl+alt+w")
        self.btn_hk_wall.clicked.connect(
            lambda: self.start_recording('wallpaper'))
        hk_wall_layout.addWidget(self.btn_hk_wall)
        hk_wall_layout.addStretch()
        self.general_layout.addLayout(hk_wall_layout)

        self.hotkey_msg = ""

        hk_group_layout = QHBoxLayout()
        self.hk_group_layout_label = QLabel()
        hk_group_layout.addWidget(self.hk_group_layout_label)
        self.btn_hk_group = QPushButton("ctrl+alt+g")
        self.btn_hk_group.clicked.connect(
            lambda: self.start_recording('group'))
        hk_group_layout.addWidget(self.btn_hk_group)
        hk_group_layout.addStretch()
        self.general_layout.addLayout(hk_group_layout)

        # Auto-start with Windows
        self.chk_autorun = QCheckBox()
        self.general_layout.addWidget(self.chk_autorun)

        self.general_group.setLayout(self.general_layout)
        right_layout.addWidget(self.general_group)

        self.group_radio_fill.toggled.connect(
            lambda: self._save_group_settings())
        self.group_radio_fit.toggled.connect(
            lambda: self._save_group_settings())

        # Save settings
        self.btn_save = QPushButton()
        self.btn_save.setMinimumHeight(36)
        self.btn_save.setStyleSheet(
            "background-color: #2a82da;"
            "color: white; font-weight: bold; padding: 8px;")
        self.btn_save.clicked.connect(self.save_all_settings)
        right_layout.addWidget(self.btn_save)

        right_layout.addStretch()

        right_scroll.setWidget(right_widget)

        h_base_layout.addWidget(left_widget, 1)
        h_base_layout.addWidget(right_scroll, 2)

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.btn_language = QPushButton(self.loc.get_string("select_language"))
        self.btn_language.setFixedWidth(120)
        self.btn_language.clicked.connect(self._show_language_dialog)
        top_bar.addWidget(self.btn_language)

        # Adding top_bar to the main layout
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_bar)
        main_layout.addLayout(h_base_layout, 1)

        # Connecting the signals after creating the entire UI
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        self.file_list.model().rowsMoved.connect(self.on_list_reordered)

        self.setCentralWidget(main_widget)
        self.load_settings_into_ui()
        self.preview_movie = None

    def on_scale_mode_changed(self):
        """Handler for changing the zoom mode for a file"""
        self.focus_group.setVisible(self.radio_fit.isChecked())
        self.on_file_setting_changed()

    def _show_language_dialog(self):
        """Shows the language selection dialog"""

        dialog = QDialog(self)
        dialog.setWindowTitle(self.loc.get_string("select_language"))
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(self.loc.get_string("language") + ":"))

        languages = {
            "en": "English",
            "de": "Deutsch",
            "eo": "Esperanto",
            "es": "Español",
            "fr": "Français",
            "ru": "Русский",
            "zh": "中文"
        }

        combo = QComboBox()
        for code, name in languages.items():
            combo.addItem(name, code)

        current_lang = self.core.config.get("language", "en")
        for i in range(combo.count()):
            if combo.itemData(i) == current_lang:
                combo.setCurrentIndex(i)
                break

        layout.addWidget(combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_lang = combo.currentData()
            if new_lang != current_lang:
                self.core.config["language"] = new_lang
                config_manager.save_config(self.core.config)
                self.loc.refresh_language(new_lang)
                self._apply_language()
                self.core.refresh_config()

    def _apply_language(self):
        """
        Applies the language to the interface, this function allows you
        not to pre-describe the labels of buttons, texts, etc. in __init__"""
        self.setWindowTitle(self.loc.get_string("title"))
        self.btn_language.setText(self.loc.get_string("language"))

        # All buttons are text, etc. in the application, set by a key:
        # value pair, where the key is a text element, and the value
        # is the text from the translation to .a json file
        translations = {
            self.preview_group: "preview",
            self.file_settings_group: "file_settings",
            self.group_settings_group: "group_settings",
            self.btn_save: "save",
            self.btn_add_file: "add_files",
            self.btn_remove_file: "remove_files",
            self.btn_reset: "reset_file",
            self.btn_move_top: "move_top",
            self.btn_move_up5: "move_up5",
            self.btn_move_up1: "move_up",
            self.btn_move_down1: "move_down",
            self.btn_move_down5: "move_down5",
            self.btn_move_bottom: "move_bottom",
            self.radio_fill: "fill",
            self.radio_fit: "crop",
            self.group_radio_fill: "fill",
            self.group_radio_fit: "crop",
            self.chk_show_focus_grid: "show_focus_grid",
            self.group_chk_show_focus: "show_focus_grid",
            self.chk_timer: "enable_timer",
            self.chk_random_order: "random_order",
            self.chk_autorun: "autostart",
            self.general_group: "general",
            self.hours_layout_label: "hours",
            self.minutes_layout_label: "minutes",
            self.seconds_layout_label: "seconds",
            self.group_settings_layout_label: "scaling",
            self.file_settings_layout_label: "scaling",
            self.left_layout_label: "media_filter",
            self.hk_group_layout_label: "next_group",
            self.hk_wall_layout_label: "tray_next",
            self.general_layout_hk_label: "hotkeys",
            self.general_layout_timer_label: "timer"
        }

        for widget, key in translations.items():
            text = self.loc.get_string(key)
            if hasattr(widget, 'setTitle'):
                widget.setTitle(text)
            elif hasattr(widget, 'setText'):
                widget.setText(text)

        self.hotkey_msg = self.loc.get_string("press_enter")

        self.setWindowTitle(self.loc.get_string("title"))

    def remove_group(self):
        """Deletes the current group"""
        current_group = self.group_combo.currentText()
        if not current_group:
            return

        groups = list(self.core.config["groups"].keys())
        if len(groups) <= 1:
            QMessageBox.warning(
                self, "Warning", self.loc.get_string("last_group"))
            return

        reply = QMessageBox.question(
            self, "Удалить группу",
            self.loc.get_string("delete_group", current_group),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.core.config["groups"][current_group]
            if current_group in self.core.config["group_settings"]:
                del self.core.config["group_settings"][current_group]

            remaining = list(self.core.config["groups"].keys())
            self.core.config["current_group"] = remaining[0]
            config_manager.save_config(self.core.config)

            self.group_combo.blockSignals(True)
            self.group_combo.clear()
            self.group_combo.addItems(remaining)
            self.group_combo.setCurrentText(remaining[0])
            self.group_combo.blockSignals(False)

            self.refresh_file_list()
            self._load_group_settings()

    def on_list_reordered(self, parent, start, end):
        """Called when dragging elements"""
        self.save_current_order()

    def save_current_order(self):
        """Saves the current file order in the config"""
        current_g = self.group_combo.currentText()
        if not current_g:
            return

        new_order = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                new_order.append(item.text())

        self.core.config["groups"][current_g] = new_order
        config_manager.save_config(self.core.config)

    def move_item(self, steps):
        """Moves the selected item by the specified number of positions"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        current_row = self.file_list.currentRow()
        total_rows = self.file_list.count()

        if total_rows <= 1:
            return

        if steps == -999:
            new_row = 0
        elif steps == 999:
            new_row = total_rows - 1
        else:
            new_row = current_row + steps

        new_row = max(0, min(new_row, total_rows - 1))

        if new_row == current_row:
            return

        self.file_list.currentItemChanged.disconnect(self.on_file_selected)
        item = self.file_list.takeItem(current_row)
        self.file_list.insertItem(new_row, item)
        self.file_list.setCurrentRow(new_row)
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        self.save_current_order()

    def refresh_file_list(self):
        """Updates the list of files in the group"""
        self.file_list.blockSignals(True)
        self.file_list.clear()
        current_g = self.group_combo.currentText()
        if current_g in self.core.config["groups"]:
            self.file_list.addItems(self.core.config["groups"][current_g])
        self.file_list.blockSignals(False)

    def _on_scale_mode_changed(self):
        """Handler for changing the zoom mode"""
        is_fit = self.radio_fit.isChecked()
        self.chk_show_focus_grid.setEnabled(is_fit)

        if not is_fit:
            self.chk_show_focus_grid.setChecked(False)
            self._hide_focus_grid()

        self.on_file_setting_changed()

    def _on_show_focus_grid_toggled(self, checked):
        """Shows/hides the focus grid"""
        if checked:
            self._show_focus_grid()
        else:
            self._hide_focus_grid()

    def _show_focus_grid(self):
        """Shows the focus grid buttons"""
        for btn in self.focus_buttons.values():
            btn.show()
        self._update_focus_hint()

    def _hide_focus_grid(self):
        """Hides the focus grid buttons"""
        for btn in self.focus_buttons.values():
            btn.hide()
        self.focus_hint_label.hide()

    def _on_focus_button_clicked(self, focus_name):
        """Handler for clicking on the focus button"""
        for name, btn in self.focus_buttons.items():
            btn.setChecked(name == focus_name)

        if self.chk_show_focus_grid.isChecked():
            self._update_focus_hint(focus_name)

        if self.group_chk_show_focus.isChecked():
            self._update_group_focus_hint(focus_name)

        self._save_group_settings()
        self.on_file_setting_changed()

    def _update_focus_hint(self, focus_name=None):
        """Update help text"""
        if not focus_name:
            return

        hints = {
            'top_left': self.loc.get_string("focus_top_left"),
            'top_center': self.loc.get_string("focus_top"),
            'top_right': self.loc.get_string("focus_top_right"),
            'center_left': self.loc.get_string("focus_left"),
            'center_center': self.loc.get_string("focus_center"),
            'center_right': self.loc.get_string("focus_right"),
            'bottom_left': self.loc.get_string("focus_bottom_left"),
            'bottom_center': self.loc.get_string("focus_bottom"),
            'bottom_right': self.loc.get_string("focus_bottom_right")
        }

        self.focus_hint_label.setText(hints.get(focus_name, ""))
        self.focus_hint_label.show()

    def get_selected_focus(self):
        """Returns the selected focus point"""
        for name, btn in self.focus_buttons.items():
            if btn.isChecked():
                return name
        return "center_center"

    def on_file_selected(self, current, previous):
        """Handler for selecting a file in the list"""
        self.update_preview(current, previous)

        self.chk_show_focus_grid.setChecked(False)
        self._hide_focus_grid()

        if current:
            path = current.text()
            if os.path.exists(path):
                settings = config_manager.get_file_settings(
                    self.core.config, path)
                self.file_settings_group.setEnabled(True)

                self.radio_fill.blockSignals(True)
                self.radio_fit.blockSignals(True)
                self.radio_fill.setChecked(settings["scale_mode"] == "fill")
                self.radio_fit.setChecked(settings["scale_mode"] == "fit")
                self.radio_fill.blockSignals(False)
                self.radio_fit.blockSignals(False)

                focus = settings.get("focus_point", "center_center")
                for name, btn in self.focus_buttons.items():
                    btn.setChecked(name == focus)

                self.chk_show_focus_grid.setEnabled(self.radio_fit.isChecked())
            else:
                self.file_settings_group.setEnabled(False)
        else:
            self.file_settings_group.setEnabled(False)

    def on_file_setting_changed(self):
        """Saves the file settings when changed"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        path = current_item.text()
        if not os.path.exists(path):
            return

        settings = {
            "customized": True,
            "scale_mode": "fill" if self.radio_fill.isChecked() else "fit",
            "focus_point": self.get_selected_focus()
        }

        config_manager.set_file_settings(self.core.config, path, settings)

    def reset_file_settings(self):
        """Resets the settings of the selected file"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        path = current_item.text()
        config_manager.reset_file_settings(self.core.config, path)
        self.on_file_selected(current_item, None)

    def update_preview(self, current, previous):
        """Updates the file list"""
        if self.preview_movie:
            self.preview_movie.stop()
            self.preview_movie = None
        self.preview_label.clear()

        if not current:
            self.preview_label.setText("Нет выбора")
            return

        path = current.text()
        if not os.path.exists(path):
            self.preview_label.setText("Файл отсутствует")
            return

        ext = path.lower()
        if ext.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            pix = QPixmap(path)
            self.preview_label.setPixmap(pix.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        elif ext.endswith('.gif'):
            self.preview_movie = QMovie(path)
            self.preview_movie.setScaledSize(self.preview_label.size())
            self.preview_label.setMovie(self.preview_movie)
            self.preview_movie.start()
        elif ext.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
            self.preview_label.setText(
                f"Видеофайл\n{os.path.basename(path)}\n"
                "(превью на рабочем столе)")

    def start_recording(self, target):
        """preview"""
        self.recording_target = target
        self.current_recorded_keys = []

        if target == 'wallpaper':
            self.btn_hk_wall.setText(self.hotkey_msg)
            self.btn_hk_wall.setStyleSheet("background-color: #d1a100;")
        else:
            self.btn_hk_group.setText(self.hotkey_msg)
            self.btn_hk_group.setStyleSheet("background-color: #d1a100;")
        self.grabKeyboard()

    def keyPressEvent(self, event):
        """We use it to enter hotkeys."""
        if self.recording_target:
            key = event.key()

            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.releaseKeyboard()

                if self.current_recorded_keys:
                    result_hk = "+".join(self.current_recorded_keys)
                else:
                    result_hk = (
                        self.temp_wall_hk
                        if self.recording_target == 'wallpaper'
                        else self.temp_group_hk)

                if self.recording_target == 'wallpaper':
                    self.temp_wall_hk = result_hk
                    self.btn_hk_wall.setText(result_hk.upper())
                    self.btn_hk_wall.setStyleSheet("")
                else:
                    self.temp_group_hk = result_hk
                    self.btn_hk_group.setText(result_hk.upper())
                    self.btn_hk_group.setStyleSheet("")

                self.recording_target = None
                event.accept()
                return

            key_str = ""
            if key == Qt.Key.Key_Control:
                key_str = "ctrl"
            elif key == Qt.Key.Key_Alt:
                key_str = "alt"
            elif key == Qt.Key.Key_Shift:
                key_str = "shift"
            elif key == Qt.Key.Key_Meta:
                key_str = "windows"
            elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
                key_str = chr(key).lower()
            elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                key_str = chr(key)
            elif Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
                key_str = f"f{key - Qt.Key.Key_F1 + 1}"
            else:
                special = {
                    Qt.Key.Key_Space: "space",
                    Qt.Key.Key_Escape: "esc",
                    Qt.Key.Key_Tab: "tab"}
                key_str = special.get(key, "")

            if key_str and key_str not in self.current_recorded_keys:
                self.current_recorded_keys.append(key_str)
                display_str = "+".join(self.current_recorded_keys).upper()
                if self.recording_target == 'wallpaper':
                    self.btn_hk_wall.setText(display_str)
                else:
                    self.btn_hk_group.setText(display_str)
            event.accept()
            return
        super().keyPressEvent(event)

    def on_timer_check_changed(self, state):
        """A function that changes the wallpaper by timer"""
        enabled = state == Qt.CheckState.Checked.value
        self.spin_hours.setEnabled(enabled)
        self.spin_minutes.setEnabled(enabled)
        self.spin_seconds.setEnabled(enabled)

    def change_active_group(self, text):
        """Changing the current group"""
        if text:
            self.core.config["current_group"] = text
            self.refresh_file_list()

    def add_new_group(self):
        """Added new group"""
        name, ok = QInputDialog.getText(
            self, self.loc.get_string("new_group"),
            self.loc.get_string("group_name"))
        if ok and name.strip():
            name = name.strip()
            if name not in self.core.config["groups"]:
                self.core.config["groups"][name] = []
                self.group_combo.addItem(name)
                self.group_combo.setCurrentText(name)

    def add_files_to_group(self):
        """Added file to group"""
        current_g = self.group_combo.currentText()
        if not current_g:
            return

        files, _ = QFileDialog.getOpenFileNames(
            self, "Выбрать медиа", "",
            ("Media files"
             "(*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mkv *.mov *.webm)")
        )

        if not files:
            return

        existing_files = set(self.core.config["groups"][current_g])
        new_files = []
        duplicates = []

        for f in files:
            normalized = os.path.normpath(f)
            if normalized not in existing_files:
                new_files.append(normalized)
                existing_files.add(normalized)
            else:
                duplicates.append(os.path.basename(f))

        if new_files:
            self.core.config["groups"][current_g].extend(new_files)
            self.refresh_file_list()

        if duplicates:
            if len(duplicates) <= 3:
                QMessageBox.information(
                    self, "Дупликаты пропущены",
                    self.loc.get_string("success")
                )
            else:
                QMessageBox.information(
                    self, "Дупликаты пропущены",
                    self.loc.get_string("duplicates_skipped",
                                        len(duplicates))
                )

        if new_files:
            config_manager.save_config(self.core.config)

    def remove_file_from_group(self):
        """Remove file from group"""
        current_g = self.group_combo.currentText()
        selected_item = self.file_list.currentItem()
        if selected_item and current_g:
            path = selected_item.text()
            self.core.config["groups"][current_g].remove(path)
            if path in self.core.config["file_settings"]:
                del self.core.config["file_settings"][path]
            self.refresh_file_list()

    def _on_group_show_focus_toggled(self, checked):
        """Shows/hides the focus grid for group settings"""
        if checked:
            self._show_focus_grid()
            focus = self.get_selected_focus()
            hints = {
                'top_left': self.loc.get_string("focus_top_left"),
                'top_center': self.loc.get_string("focus_top"),
                'top_right': self.loc.get_string("focus_top_right"),
                'center_left': self.loc.get_string("focus_left"),
                'center_center': self.loc.get_string("focus_center"),
                'center_right': self.loc.get_string("focus_right"),
                'bottom_left': self.loc.get_string("focus_bottom_left"),
                'bottom_center': self.loc.get_string("focus_bottom"),
                'bottom_right': self.loc.get_string("focus_bottom_right"),
            }
            self.group_focus_hint.setText(hints.get(focus, ""))
            self.group_focus_hint.show()
        else:
            self._hide_focus_grid()
            self.group_focus_hint.hide()

    def _update_group_focus_hint(self, focus_name=None):
        """Updates the group focus hint"""
        hints = {
            'top_left': self.loc.get_string("focus_top_left"),
            'top_center': self.loc.get_string("focus_top"),
            'top_right': self.loc.get_string("focus_top_right"),
            'center_left': self.loc.get_string("focus_left"),
            'center_center': self.loc.get_string("focus_center"),
            'center_right': self.loc.get_string("focus_right"),
            'bottom_left': self.loc.get_string("focus_bottom_left"),
            'bottom_center': self.loc.get_string("focus_bottom"),
            'bottom_right': self.loc.get_string("focus_bottom_right"),
        }
        self.group_focus_hint.setText(hints.get(focus_name, ""))
        self.group_focus_hint.show()

    def _save_group_settings(self):
        """Saves the settings of the current group"""
        group_name = self.group_combo.currentText()
        if not group_name:
            return

        settings = {
            "scale_mode": (
                "fill" if self.group_radio_fill.isChecked() else "fit"),
            "focus_point": self.get_selected_focus(),
        }

        config_manager.set_group_settings(
            self.core.config, group_name, settings)

    def _load_group_settings(self):
        """Loads the settings of the current group"""
        group_name = self.group_combo.currentText()
        if not group_name:
            return

        settings = config_manager.get_group_settings(
            self.core.config, group_name)

        self.group_radio_fill.blockSignals(True)
        self.group_radio_fit.blockSignals(True)
        self.group_radio_fill.setChecked(settings["scale_mode"] == "fill")
        self.group_radio_fit.setChecked(settings["scale_mode"] == "fit")
        self.group_radio_fill.blockSignals(False)
        self.group_radio_fit.blockSignals(False)

        focus = settings.get("focus_point", "center_center")
        for name, btn in self.focus_buttons.items():
            btn.setChecked(name == focus)

        self.group_chk_show_focus.setEnabled(self.group_radio_fit.isChecked())
        if not self.group_radio_fit.isChecked():
            self.group_chk_show_focus.setChecked(False)

    def load_settings_into_ui(self):
        """Uploads the settings to a file"""
        cfg = self.core.config
        self.group_combo.clear()
        self.group_combo.addItems(cfg["groups"].keys())
        self.group_combo.setCurrentText(cfg["current_group"])
        self._apply_language()

        self._load_group_settings()

        use_timer = cfg.get("use_timer", False)
        self.chk_timer.setChecked(use_timer)

        if "timer_interval_seconds" in cfg:
            total_seconds = cfg["timer_interval_seconds"]
        else:
            total_seconds = cfg.get("timer_interval_min", 5) * 60

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        self.spin_hours.setValue(hours)
        self.spin_minutes.setValue(minutes)
        self.spin_seconds.setValue(seconds)

        self.spin_hours.setEnabled(use_timer)
        self.spin_minutes.setEnabled(use_timer)
        self.spin_seconds.setEnabled(use_timer)

        self.chk_random_order.setChecked(cfg.get("random_order", False))
        self.chk_autorun.setChecked(cfg.get("autorun", False))

        self.temp_wall_hk = cfg.get("hotkey", "ctrl+alt+w")
        self.temp_group_hk = cfg.get("group_hotkey", "ctrl+alt+g")
        self.btn_hk_wall.setText(self.temp_wall_hk.upper())
        self.btn_hk_group.setText(self.temp_group_hk.upper())

        self.refresh_file_list()

    def save_all_settings(self):
        """Save all settings"""
        if self.preview_movie:
            self.preview_movie.stop()

        self._save_group_settings()

        self.core.config["random_order"] = self.chk_random_order.isChecked()
        self.core.config["use_timer"] = self.chk_timer.isChecked()

        total_seconds = (self.spin_hours.value() * 3600 +
                         self.spin_minutes.value() * 60 +
                         self.spin_seconds.value())
        total_seconds = max(1, total_seconds)
        self.core.config["timer_interval_seconds"] = total_seconds

        self.core.config["autorun"] = self.chk_autorun.isChecked()
        self.core.config["hotkey"] = self.temp_wall_hk
        self.core.config["group_hotkey"] = self.temp_group_hk

        config_manager.save_config(self.core.config)
        self.core.refresh_config()

        if self.core.config.get("random_order", False):
            self.core.random_wallpaper()
        else:
            self.core.wallpaper_index = 0
            self.core.next_wallpaper()

        QMessageBox.information(
            self, self.loc.get_string("success"),
            self.loc.get_string("success"))
        self.hide()

    def closeEvent(self, event):
        """The function of closing the application"""
        if self.recording_target:
            self.releaseKeyboard()
            self.recording_target = None
            self.btn_hk_wall.setStyleSheet("")
            self.btn_hk_group.setStyleSheet("")
        event.ignore()
        self.hide()
