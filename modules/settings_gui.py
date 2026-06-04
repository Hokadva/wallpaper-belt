import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QListWidget, QFileDialog, 
                             QLabel, QSpinBox, QCheckBox, QMessageBox, QSlider, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QMovie
import modules.config_manager as config_manager

class SettingsWindow(QMainWindow):
    def __init__(self, app_core):
        super().__init__()
        self.core = app_core
        self.setWindowTitle("Панель управления обоями")
        self.setMinimumSize(800, 500)

        self.recording_target = None 
        self.current_recorded_keys = []
        self.temp_wall_hk = ""
        self.temp_group_hk = ""

        main_widget = QWidget()
        h_base_layout = QHBoxLayout(main_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.currentTextChanged.connect(self.change_active_group)
        btn_add_group = QPushButton("➕ Группа")
        btn_add_group.clicked.connect(self.add_new_group)
        group_layout.addWidget(QLabel("Группа:"))
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(btn_add_group)
        left_layout.addLayout(group_layout)

        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.update_preview)
        left_layout.addWidget(QLabel("Медиафайлы в группе:"))
        left_layout.addWidget(self.file_list)

        file_btn_layout = QHBoxLayout()
        btn_add_file = QPushButton("Добавить файлы")
        btn_add_file.clicked.connect(self.add_files_to_group)
        btn_remove_file = QPushButton("Удалить")
        btn_remove_file.clicked.connect(self.remove_file_from_group)
        file_btn_layout.addWidget(btn_add_file)
        file_btn_layout.addWidget(btn_remove_file)
        left_layout.addLayout(file_btn_layout)

        audio_layout = QHBoxLayout()
        self.chk_mute = QCheckBox("Без звука")
        self.chk_mute.stateChanged.connect(self.on_audio_ui_changed)
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.valueChanged.connect(self.on_audio_ui_changed)
        self.lbl_volume_val = QLabel("50%")
        audio_layout.addWidget(self.chk_mute)
        audio_layout.addWidget(self.slider_volume)
        audio_layout.addWidget(self.lbl_volume_val)
        left_layout.addLayout(audio_layout)

        timer_layout = QHBoxLayout()
        self.chk_timer = QCheckBox("Смена по таймеру")
        self.spin_timer = QSpinBox()
        self.spin_timer.setRange(1, 1440)
        self.spin_timer.setSuffix(" мин.")
        timer_layout.addWidget(self.chk_timer)
        timer_layout.addWidget(self.spin_timer)
        left_layout.addLayout(timer_layout)

        hk_layout = QVBoxLayout()
        self.btn_hk_wall = QPushButton("Нажмите для записи")
        self.btn_hk_wall.clicked.connect(lambda: self.start_recording('wallpaper'))
        hk_layout.addWidget(QLabel("Клавиша смены обоев:"))
        hk_layout.addWidget(self.btn_hk_wall)

        self.btn_hk_group = QPushButton("Нажмите для записи")
        self.btn_hk_group.clicked.connect(lambda: self.start_recording('group'))
        hk_layout.addWidget(QLabel("Клавиша смены группы:"))
        hk_layout.addWidget(self.btn_hk_group)
        left_layout.addLayout(hk_layout)

        self.chk_autorun = QCheckBox("Автозапуск при старте Windows")
        left_layout.addWidget(self.chk_autorun)

        btn_save = QPushButton("💾 Сохранить и применить")
        btn_save.setStyleSheet("background-color: #2a82da; color: white; font-weight: bold; padding: 6px;")
        btn_save.clicked.connect(self.save_all_settings)
        left_layout.addWidget(btn_save)
        
        # Правая панель с предпросмотром
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("👀 Предпросмотр выбранного файла:"))
        self.preview_label = QLabel("Выберите файл из списка")
        self.preview_label.setFixedSize(320, 240)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #555; background-color: #111; color: #888;")
        right_layout.addWidget(self.preview_label)
        right_layout.addStretch()
        
        self.preview_movie = None
        
        h_base_layout.addWidget(left_widget, stretch=2)
        h_base_layout.addWidget(right_widget, stretch=1)
        
        self.setCentralWidget(main_widget)
        self.load_settings_into_ui()

    def load_settings_into_ui(self):
        cfg = self.core.config
        self.group_combo.clear()
        self.group_combo.addItems(cfg["groups"].keys())
        self.group_combo.setCurrentText(cfg["current_group"])
        
        self.chk_timer.setChecked(cfg["use_timer"])
        self.spin_timer.setValue(cfg["timer_interval_min"])
        self.chk_autorun.setChecked(cfg["autorun"])
        
        self.temp_wall_hk = cfg.get("hotkey", "ctrl+alt+w")
        self.temp_group_hk = cfg.get("group_hotkey", "ctrl+alt+g")
        self.btn_hk_wall.setText(self.temp_wall_hk.upper())
        self.btn_hk_group.setText(self.temp_group_hk.upper())
        
        self.slider_volume.setValue(cfg.get("volume", 50))
        self.chk_mute.setChecked(cfg.get("mute", False))
        self.lbl_volume_val.setText(f"{self.slider_volume.value()}%")
        self.refresh_file_list()

    def update_preview(self, current, previous):
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
            self.preview_label.setText(f"📹 Видеофайл\n{os.path.basename(path)}\n(Превью доступно на рабочем столе)")

    def start_recording(self, target):
        self.recording_target = target
        self.current_recorded_keys = []
        
        msg = "⏳ Ввод клавиш... Нажмите ENTER"
        if target == 'wallpaper':
            self.btn_hk_wall.setText(msg)
            self.btn_hk_wall.setStyleSheet("background-color: #d1a100; color: white;")
        else:
            self.btn_hk_group.setText(msg)
            self.btn_hk_group.setStyleSheet("background-color: #d1a100; color: white;")
        self.grabKeyboard()

    def keyPressEvent(self, event):
        if self.recording_target:
            key = event.key()
            
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.releaseKeyboard()
                
                if self.current_recorded_keys:
                    result_hk = "+".join(self.current_recorded_keys)
                else:
                    result_hk = self.temp_wall_hk if self.recording_target == 'wallpaper' else self.temp_group_hk
                    
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
            if key == Qt.Key.Key_Control: key_str = "ctrl"
            elif key == Qt.Key.Key_Alt: key_str = "alt"
            elif key == Qt.Key.Key_Shift: key_str = "shift"
            elif key == Qt.Key.Key_Meta: key_str = "windows"
            elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z: key_str = chr(key).lower()
            elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9: key_str = chr(key)
            elif Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12: key_str = f"f{key - Qt.Key.Key_F1 + 1}"
            else:
                special = {Qt.Key.Key_Space: "space", Qt.Key.Key_Escape: "esc", Qt.Key.Key_Tab: "tab"}
                key_str = special.get(key, "")
                
            if key_str and key_str not in self.current_recorded_keys:
                self.current_recorded_keys.append(key_str)
                display_str = "+".join(self.current_recorded_keys).upper() + " ... (ENTER)"
                if self.recording_target == 'wallpaper':
                    self.btn_hk_wall.setText(display_str)
                else:
                    self.btn_hk_group.setText(display_str)
            event.accept()
            return
        super().keyPressEvent(event)

    def on_audio_ui_changed(self):
        vol = self.slider_volume.value()
        mute = self.chk_mute.isChecked()
        self.lbl_volume_val.setText(f"{vol}%")
        self.core.wall_window.update_audio_settings(vol, mute)

    def refresh_file_list(self):
        self.file_list.clear()
        current_g = self.group_combo.currentText()
        if current_g in self.core.config["groups"]:
            self.file_list.addItems(self.core.config["groups"][current_g])

    def change_active_group(self, text):
        if text:
            self.core.config["current_group"] = text
            self.refresh_file_list()

    def add_new_group(self):
        name, ok = QInputDialog.getText(self, "Новая группа", "Название:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.core.config["groups"]:
                self.core.config["groups"][name] = []
                self.group_combo.addItem(name)
                self.group_combo.setCurrentText(name)

    def add_files_to_group(self):
        current_g = self.group_combo.currentText()
        if not current_g: return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выбор медиа", "", "Медиа (*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mkv *.mov)"
        )
        if files:
            self.core.config["groups"][current_g].extend(files)
            self.refresh_file_list()

    def remove_file_from_group(self):
        current_g = self.group_combo.currentText()
        selected_item = self.file_list.currentItem()
        if selected_item and current_g:
            self.core.config["groups"][current_g].remove(selected_item.text())
            self.refresh_file_list()

    def save_all_settings(self):
        if self.preview_movie:
            self.preview_movie.stop()
        
        self.core.config["use_timer"] = self.chk_timer.isChecked()
        self.core.config["timer_interval_min"] = self.spin_timer.value()
        self.core.config["autorun"] = self.chk_autorun.isChecked()
        self.core.config["volume"] = self.slider_volume.value()
        self.core.config["mute"] = self.chk_mute.isChecked()
        self.core.config["hotkey"] = self.temp_wall_hk
        self.core.config["group_hotkey"] = self.temp_group_hk
        
        config_manager.save_config(self.core.config)
        self.core.apply_new_settings()
        
        self.core.wallpaper_index = 0
        self.core.next_wallpaper()
        
        QMessageBox.information(self, "Успех", "Конфигурация обновлена!")
        self.hide()

    def closeEvent(self, event):
        if self.recording_target:
            self.releaseKeyboard()
            self.recording_target = None
            self.btn_hk_wall.setStyleSheet("")
            self.btn_hk_group.setStyleSheet("")
        event.ignore()
        self.hide()
