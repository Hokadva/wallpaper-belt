import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QListWidget, QFileDialog, 
                             QLabel, QSpinBox, QCheckBox, QMessageBox, QSlider, 
                             QInputDialog, QRadioButton, QGroupBox,
                             QScrollArea)
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QListWidget, QFileDialog, 
                             QLabel, QSpinBox, QCheckBox, QMessageBox, QSlider, 
                             QInputDialog, QRadioButton, QGroupBox, QScrollArea,
                             QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QMovie
import modules.config_manager as config_manager


class SettingsWindow(QMainWindow):
    def __init__(self, app_core):
        super().__init__()
        self.core = app_core
        self.setWindowTitle("Панель управления обоями")
        self.setMinimumSize(800, 600)
        
        self.recording_target = None 
        self.current_recorded_keys = []
        self.temp_wall_hk = ""
        self.temp_group_hk = ""
        
        main_widget = QWidget()
        h_base_layout = QHBoxLayout(main_widget)
        h_base_layout.setContentsMargins(10, 10, 10, 10)
        
        # ЛЕВАЯ ПАНЕЛЬ
        left_widget = QWidget()
        left_widget.setMinimumWidth(350)
        left_widget.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Выбор группы
        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.currentTextChanged.connect(self.change_active_group)
        btn_add_group = QPushButton("➕")
        btn_add_group.setFixedWidth(40)
        btn_add_group.clicked.connect(self.add_new_group)
        btn_add_group.setToolTip("Добавить группу")
        group_layout.addWidget(QLabel("Группа:"))
        group_layout.addWidget(self.group_combo, 1)
        group_layout.addWidget(btn_add_group)
        left_layout.addLayout(group_layout)
        
        # Список файлов с Drag & Drop
        left_layout.addWidget(QLabel("Медиафайлы (перетаскивайте для сортировки):"))
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        left_layout.addWidget(self.file_list, 1)
        
        # Кнопки управления файлами
        file_btn_layout = QHBoxLayout()
        btn_add_file = QPushButton("📁 Добавить")
        btn_add_file.clicked.connect(self.add_files_to_group)
        btn_remove_file = QPushButton("🗑 Удалить")
        btn_remove_file.clicked.connect(self.remove_file_from_group)
        file_btn_layout.addWidget(btn_add_file)
        file_btn_layout.addWidget(btn_remove_file)
        left_layout.addLayout(file_btn_layout)
        
        # Кнопки перемещения
        move_group = QGroupBox("Перемещение")
        move_layout = QVBoxLayout()
        
        # Верхний ряд
        top_row = QHBoxLayout()
        self.btn_move_top = QPushButton("⏫ Вверх")
        self.btn_move_top.clicked.connect(lambda: self.move_item(-999))
        self.btn_move_up5 = QPushButton("⬆ +5")
        self.btn_move_up5.clicked.connect(lambda: self.move_item(-5))
        self.btn_move_up1 = QPushButton("🔼 +1")
        self.btn_move_up1.clicked.connect(lambda: self.move_item(-1))
        top_row.addWidget(self.btn_move_top)
        top_row.addWidget(self.btn_move_up5)
        top_row.addWidget(self.btn_move_up1)
        move_layout.addLayout(top_row)
        
        # Нижний ряд
        bottom_row = QHBoxLayout()
        self.btn_move_bottom = QPushButton("⏬ Вниз")
        self.btn_move_bottom.clicked.connect(lambda: self.move_item(999))
        self.btn_move_down5 = QPushButton("⬇ +5")
        self.btn_move_down5.clicked.connect(lambda: self.move_item(5))
        self.btn_move_down1 = QPushButton("🔽 +1")
        self.btn_move_down1.clicked.connect(lambda: self.move_item(1))
        bottom_row.addWidget(self.btn_move_bottom)
        bottom_row.addWidget(self.btn_move_down5)
        bottom_row.addWidget(self.btn_move_down1)
        move_layout.addLayout(bottom_row)
        
        move_group.setLayout(move_layout)
        left_layout.addWidget(move_group)
        
        # ПРАВАЯ ПАНЕЛЬ - настройки
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Предпросмотр с сеткой фокуса
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()

        # Контейнер для предпросмотра с оверлеем
        self.preview_container = QWidget()
        self.preview_container.setFixedSize(320, 240)
        self.preview_container.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        # Label с изображением
        self.preview_label = QLabel("Выберите файл из списка", self.preview_container)
        self.preview_label.setGeometry(0, 0, 320, 240)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Сетка кнопок фокуса 3x3
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
            btn = QPushButton("◉", self.preview_container)
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
            btn.clicked.connect(lambda checked, n=name: self._on_focus_button_clicked(n))
            btn.setToolTip({
                'top_left': 'Левый верх',
                'top_center': 'Центр верх',
                'top_right': 'Правый верх',
                'center_left': 'Левый центр',
                'center_center': 'Центр',
                'center_right': 'Правый центр',
                'bottom_left': 'Левый низ',
                'bottom_center': 'Центр низ',
                'bottom_right': 'Правый низ',
            }[name])
            btn.hide()  # Скрыты по умолчанию
            self.focus_buttons[name] = btn

        preview_layout.addWidget(self.preview_container)

        # Подсказка под предпросмотром
        self.focus_hint_label = QLabel("")
        self.focus_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_hint_label.setStyleSheet("color: #2a82da; font-weight: bold; padding: 4px;")
        self.focus_hint_label.hide()
        preview_layout.addWidget(self.focus_hint_label)

        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)

        # Индивидуальные настройки файла
        self.file_settings_group = QGroupBox("Настройки файла")
        self.file_settings_group.setEnabled(False)
        file_settings_layout = QVBoxLayout()

        # Масштабирование
        file_settings_layout.addWidget(QLabel("Масштабирование:"))
        self.radio_fill = QRadioButton("Заполнить (растянуть)")
        self.radio_fit = QRadioButton("Обрезать")
        self.radio_fill.toggled.connect(self._on_scale_mode_changed)
        self.radio_fit.toggled.connect(self._on_scale_mode_changed)
        file_settings_layout.addWidget(self.radio_fill)
        file_settings_layout.addWidget(self.radio_fit)

        # Чекбокс показа сетки фокуса
        self.chk_show_focus_grid = QCheckBox("Показать сетку фокуса на предпросмотре")
        self.chk_show_focus_grid.toggled.connect(self._on_show_focus_grid_toggled)
        file_settings_layout.addWidget(self.chk_show_focus_grid)

        # Частота кадров GIF
        self.gif_widget = QWidget()
        gif_layout = QHBoxLayout(self.gif_widget)
        gif_layout.setContentsMargins(0, 0, 0, 0)
        gif_layout.addWidget(QLabel("FPS для GIF:"))
        self.spin_gif_fps = QSpinBox()
        self.spin_gif_fps.setRange(1, 30)
        self.spin_gif_fps.setValue(10)
        self.spin_gif_fps.valueChanged.connect(self.on_file_setting_changed)
        gif_layout.addWidget(self.spin_gif_fps)
        gif_layout.addStretch()
        file_settings_layout.addWidget(self.gif_widget)

        # Кнопка сброса
        btn_reset = QPushButton("Сбросить настройки")
        btn_reset.clicked.connect(self.reset_file_settings)
        file_settings_layout.addWidget(btn_reset)

        self.file_settings_group.setLayout(file_settings_layout)
        right_layout.addWidget(self.file_settings_group)
        
        self.file_settings_group.setLayout(file_settings_layout)
        right_layout.addWidget(self.file_settings_group)
        
        # Общие настройки
        general_group = QGroupBox("Общие настройки")
        general_layout = QVBoxLayout()
        
        # Общие настройки отображения
        general_layout.addWidget(QLabel("Отображение по умолчанию:"))
        
        scale_default_layout = QHBoxLayout()
        self.radio_default_fill = QRadioButton("Заполнить")
        self.radio_default_fit = QRadioButton("Обрезать")
        scale_default_layout.addWidget(self.radio_default_fill)
        scale_default_layout.addWidget(self.radio_default_fit)
        general_layout.addLayout(scale_default_layout)

        # FPS для GIF по умолчанию
        gif_default_layout = QHBoxLayout()
        gif_default_layout.addWidget(QLabel("FPS для GIF по умолчанию:"))
        self.spin_default_gif_fps = QSpinBox()
        self.spin_default_gif_fps.setRange(1, 30)
        self.spin_default_gif_fps.setValue(10)
        gif_default_layout.addWidget(self.spin_default_gif_fps)
        gif_default_layout.addStretch()
        general_layout.addLayout(gif_default_layout)
        
        # Разделитель
        separator = QLabel("─" * 30)
        separator.setStyleSheet("color: #aaa;")
        general_layout.addWidget(separator)
        
        # Звук
        general_layout.addWidget(QLabel("Звук:"))
        audio_layout = QHBoxLayout()
        self.chk_mute = QCheckBox("Без звука")
        self.chk_mute.stateChanged.connect(self.on_audio_ui_changed)
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(50)
        self.slider_volume.valueChanged.connect(self.on_audio_ui_changed)
        self.lbl_volume_val = QLabel("50%")
        self.lbl_volume_val.setFixedWidth(35)
        audio_layout.addWidget(self.chk_mute)
        audio_layout.addWidget(self.slider_volume)
        audio_layout.addWidget(self.lbl_volume_val)
        general_layout.addLayout(audio_layout)
        
        # Таймер
        general_layout.addWidget(QLabel("Таймер смены:"))
        self.chk_timer = QCheckBox("Включить смену по таймеру")
        self.chk_timer.stateChanged.connect(self.on_timer_check_changed)
        general_layout.addWidget(self.chk_timer)
        
        timer_input_layout = QHBoxLayout()
        
        hours_layout = QVBoxLayout()
        hours_layout.addWidget(QLabel("Часы"))
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 23)
        self.spin_hours.setEnabled(False)
        hours_layout.addWidget(self.spin_hours)
        timer_input_layout.addLayout(hours_layout)
        
        minutes_layout = QVBoxLayout()
        minutes_layout.addWidget(QLabel("Минуты"))
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(0, 59)
        self.spin_minutes.setEnabled(False)
        minutes_layout.addWidget(self.spin_minutes)
        timer_input_layout.addLayout(minutes_layout)
        
        seconds_layout = QVBoxLayout()
        seconds_layout.addWidget(QLabel("Секунды"))
        self.spin_seconds = QSpinBox()
        self.spin_seconds.setRange(0, 59)
        self.spin_seconds.setEnabled(False)
        seconds_layout.addWidget(self.spin_seconds)
        timer_input_layout.addLayout(seconds_layout)
        
        general_layout.addLayout(timer_input_layout)
        
        # Случайный порядок
        self.chk_random_order = QCheckBox("🎲 Случайный порядок смены обоев")
        general_layout.addWidget(self.chk_random_order)
        
        # Горячие клавиши
        general_layout.addWidget(QLabel("Горячие клавиши:"))
        
        hk_wall_layout = QHBoxLayout()
        hk_wall_layout.addWidget(QLabel("Смена обоев:"))
        self.btn_hk_wall = QPushButton("ctrl+alt+w")
        self.btn_hk_wall.clicked.connect(lambda: self.start_recording('wallpaper'))
        hk_wall_layout.addWidget(self.btn_hk_wall)
        hk_wall_layout.addStretch()
        general_layout.addLayout(hk_wall_layout)
        
        hk_group_layout = QHBoxLayout()
        hk_group_layout.addWidget(QLabel("Смена группы:"))
        self.btn_hk_group = QPushButton("ctrl+alt+g")
        self.btn_hk_group.clicked.connect(lambda: self.start_recording('group'))
        hk_group_layout.addWidget(self.btn_hk_group)
        hk_group_layout.addStretch()
        general_layout.addLayout(hk_group_layout)
        
        # Автозапуск
        self.chk_autorun = QCheckBox("Автозапуск при старте Windows")
        general_layout.addWidget(self.chk_autorun)
        
        general_group.setLayout(general_layout)
        right_layout.addWidget(general_group)
        
        # Кнопка сохранения
        btn_save = QPushButton("💾 Сохранить и применить")
        btn_save.setMinimumHeight(36)
        btn_save.setStyleSheet("background-color: #2a82da; color: white; font-weight: bold; padding: 8px;")
        btn_save.clicked.connect(self.save_all_settings)
        right_layout.addWidget(btn_save)
        
        right_layout.addStretch()
        
        right_scroll.setWidget(right_widget)
        
        h_base_layout.addWidget(left_widget, 1)
        h_base_layout.addWidget(right_scroll, 2)
        
        self.setCentralWidget(main_widget)
        
        # Подключаем сигналы после создания всего UI
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        self.file_list.model().rowsMoved.connect(self.on_list_reordered)
        
        self.load_settings_into_ui()
        
        self.preview_movie = None

    def on_scale_mode_changed(self):
        """Обработчик изменения режима масштабирования для файла"""
        self.focus_group.setVisible(self.radio_fit.isChecked())
        self.on_file_setting_changed()

    def on_list_reordered(self, parent, start, end):
        """Вызывается при перетаскивании элементов"""
        self.save_current_order()

    def save_current_order(self):
        """Сохраняет текущий порядок файлов в конфиг"""
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
        """Перемещает выбранный элемент на указанное количество позиций"""
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
        
        # Блокируем сигналы
        self.file_list.currentItemChanged.disconnect(self.on_file_selected)
        
        # Извлекаем элемент
        item = self.file_list.takeItem(current_row)
        
        # Вставляем на новую позицию
        self.file_list.insertItem(new_row, item)
        
        # Выделяем перемещенный элемент
        self.file_list.setCurrentRow(new_row)
        
        # Восстанавливаем сигналы
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        
        # Сохраняем изменения
        self.save_current_order()

    def update_move_buttons_state(self, current, previous):
        """Обновляет состояние кнопок перемещения"""
        pass  # Можно добавить логику для отключения кнопок на краях

    def refresh_file_list(self):
        # Блокируем сигналы
        self.file_list.currentItemChanged.disconnect(self.on_file_selected)
        
        self.file_list.clear()
        current_g = self.group_combo.currentText()
        if current_g in self.core.config["groups"]:
            self.file_list.addItems(self.core.config["groups"][current_g])
        
        # Восстанавливаем сигналы
        self.file_list.currentItemChanged.connect(self.on_file_selected)

    def _on_scale_mode_changed(self):
        """Обработчик изменения режима масштабирования"""
        is_fit = self.radio_fit.isChecked()
        self.chk_show_focus_grid.setEnabled(is_fit)
        
        if not is_fit:
            self.chk_show_focus_grid.setChecked(False)
            self._hide_focus_grid()
        
        self.on_file_setting_changed()

    def _on_show_focus_grid_toggled(self, checked):
        """Показывает/скрывает сетку фокуса"""
        if checked:
            self._show_focus_grid()
        else:
            self._hide_focus_grid()

    def _show_focus_grid(self):
        """Показывает кнопки сетки фокуса"""
        for btn in self.focus_buttons.values():
            btn.show()
        self._update_focus_hint()

    def _hide_focus_grid(self):
        """Скрывает кнопки сетки фокуса"""
        for btn in self.focus_buttons.values():
            btn.hide()
        self.focus_hint_label.hide()

    def _on_focus_button_clicked(self, focus_name):
        """Обработчик клика по кнопке фокуса"""
        # Снимаем выделение со всех кнопок
        for name, btn in self.focus_buttons.items():
            btn.setChecked(name == focus_name)
        
        # Обновляем подсказку
        self._update_focus_hint(focus_name)
        
        # Сохраняем настройки
        self.on_file_setting_changed()

    def _update_focus_hint(self, focus_name=None):
        """Обновляет текст подсказки"""
        if not focus_name:
            return
        
        hints = {
            'top_left': 'Фокус: левый верхний угол',
            'top_center': 'Фокус: верхний край',
            'top_right': 'Фокус: правый верхний угол',
            'center_left': 'Фокус: левый край',
            'center_center': 'Фокус: центр изображения',
            'center_right': 'Фокус: правый край',
            'bottom_left': 'Фокус: левый нижний угол',
            'bottom_center': 'Фокус: нижний край',
            'bottom_right': 'Фокус: правый нижний угол',
        }
        
        self.focus_hint_label.setText(hints.get(focus_name, ""))
        self.focus_hint_label.show()

    def get_selected_focus(self):
        """Возвращает выбранную точку фокуса"""
        for name, btn in self.focus_buttons.items():
            if btn.isChecked():
                return name
        return "center_center"  # По умолчанию

    def on_file_selected(self, current, previous):
        """Обработчик выбора файла в списке"""
        self.update_preview(current, previous)
        
        # Скрываем сетку при смене файла
        self.chk_show_focus_grid.setChecked(False)
        self._hide_focus_grid()
        
        if current:
            path = current.text()
            if os.path.exists(path):
                settings = config_manager.get_file_settings(self.core.config, path)
                self.file_settings_group.setEnabled(True)
                
                # Блокируем сигналы при загрузке
                self.radio_fill.blockSignals(True)
                self.radio_fit.blockSignals(True)
                self.radio_fill.setChecked(settings["scale_mode"] == "fill")
                self.radio_fit.setChecked(settings["scale_mode"] == "fit")
                self.radio_fill.blockSignals(False)
                self.radio_fit.blockSignals(False)
                
                # Сетка фокуса
                focus = settings.get("focus_point", "center_center")
                for name, btn in self.focus_buttons.items():
                    btn.setChecked(name == focus)
                
                # Активируем чекбокс только в режиме обрезки
                self.chk_show_focus_grid.setEnabled(self.radio_fit.isChecked())
                
                # GIF настройки
                self.spin_gif_fps.blockSignals(True)
                self.spin_gif_fps.setValue(settings.get("gif_fps", 10))
                self.spin_gif_fps.blockSignals(False)
                
                ext = path.lower()
                self.gif_widget.setVisible(ext.endswith('.gif'))
            else:
                self.file_settings_group.setEnabled(False)
        else:
            self.file_settings_group.setEnabled(False)

    def on_file_setting_changed(self):
        """Сохраняет настройки файла при изменении"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return
            
        path = current_item.text()
        if not os.path.exists(path):
            return
            
        settings = {
            "customized": True,
            "scale_mode": "fill" if self.radio_fill.isChecked() else "fit",
            "focus_point": self.get_selected_focus(),
            "gif_fps": self.spin_gif_fps.value()
        }
        
        config_manager.set_file_settings(self.core.config, path, settings)

    def reset_file_settings(self):
        """Сбрасывает настройки выбранного файла"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return
            
        path = current_item.text()
        config_manager.reset_file_settings(self.core.config, path)
        self.on_file_selected(current_item, None)

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
            self.preview_label.setText(f"Видеофайл\n{os.path.basename(path)}\n(превью на рабочем столе)")

    def start_recording(self, target):
        self.recording_target = target
        self.current_recorded_keys = []
        
        msg = "Ввод... ENTER"
        if target == 'wallpaper':
            self.btn_hk_wall.setText(msg)
            self.btn_hk_wall.setStyleSheet("background-color: #d1a100;")
        else:
            self.btn_hk_group.setText(msg)
            self.btn_hk_group.setStyleSheet("background-color: #d1a100;")
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
                display_str = "+".join(self.current_recorded_keys).upper()
                if self.recording_target == 'wallpaper':
                    self.btn_hk_wall.setText(display_str)
                else:
                    self.btn_hk_group.setText(display_str)
            event.accept()
            return
        super().keyPressEvent(event)

    def on_timer_check_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.spin_hours.setEnabled(enabled)
        self.spin_minutes.setEnabled(enabled)
        self.spin_seconds.setEnabled(enabled)

    def on_audio_ui_changed(self):
        vol = self.slider_volume.value()
        mute = self.chk_mute.isChecked()
        self.lbl_volume_val.setText(f"{vol}%")
        self.core.wall_window.update_audio_settings(vol, mute)

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
            path = selected_item.text()
            self.core.config["groups"][current_g].remove(path)
            if path in self.core.config["file_settings"]:
                del self.core.config["file_settings"][path]
            self.refresh_file_list()

    def load_settings_into_ui(self):
        cfg = self.core.config
        self.group_combo.clear()
        self.group_combo.addItems(cfg["groups"].keys())
        self.group_combo.setCurrentText(cfg["current_group"])
        
        # Загружаем общие настройки отображения
        default_scale = cfg.get("default_scale_mode", "fill")
        self.radio_default_fill.setChecked(default_scale == "fill")
        self.radio_default_fit.setChecked(default_scale == "fit")
        
        use_timer = cfg.get("use_timer", False)
        self.chk_timer.setChecked(use_timer)

        # Получаем секунды
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

        self.chk_autorun.setChecked(cfg["autorun"])
        
        self.temp_wall_hk = cfg.get("hotkey", "ctrl+alt+w")
        self.temp_group_hk = cfg.get("group_hotkey", "ctrl+alt+g")
        self.btn_hk_wall.setText(self.temp_wall_hk.upper())
        self.btn_hk_group.setText(self.temp_group_hk.upper())
        
        self.slider_volume.setValue(cfg.get("volume", 50))
        self.chk_mute.setChecked(cfg.get("mute", False))
        self.lbl_volume_val.setText(f"{self.slider_volume.value()}%")
        self.refresh_file_list()

    def save_all_settings(self):
        if self.preview_movie:
            self.preview_movie.stop()
        
        # Сохраняем общие настройки отображения
        self.core.config["default_scale_mode"] = "fill" if self.radio_default_fill.isChecked() else "fit"
        self.core.config["default_gif_fps"] = self.spin_default_gif_fps.value()
        
        self.core.config["random_order"] = self.chk_random_order.isChecked()
        self.core.config["use_timer"] = self.chk_timer.isChecked()
        
        # Сохраняем в СЕКУНДАХ
        total_seconds = (self.spin_hours.value() * 3600 + 
                        self.spin_minutes.value() * 60 + 
                        self.spin_seconds.value())
        # Минимум 1 секунда
        total_seconds = max(1, total_seconds)
        self.core.config["timer_interval_seconds"] = total_seconds
        
        # Для обратной совместимости сохраняем и минуты
        self.core.config["timer_interval_min"] = max(1, total_seconds // 60)
        
        self.core.config["autorun"] = self.chk_autorun.isChecked()
        self.core.config["volume"] = self.slider_volume.value()
        self.core.config["mute"] = self.chk_mute.isChecked()
        self.core.config["hotkey"] = self.temp_wall_hk
        self.core.config["group_hotkey"] = self.temp_group_hk
        
        config_manager.save_config(self.core.config)
        self.core.refresh_config()

        is_random_wallpaper = self.core.config["random_order"]

        if is_random_wallpaper:
            self.core.random_wallpaper()

        else:
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
