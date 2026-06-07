import ctypes
import os
import tempfile
import time
import winreg

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QGuiApplication, QMovie, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink

import modules.config_manager as config_manager


class WallpaperBelt:
    """Движок для установки обоев рабочего стола"""
    
    def __init__(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        
        self.video_sink = QVideoSink()
        self.media_player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self._process_video_frame)
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
        
        self.current_file_path = None
        self.current_wallpaper_path = None
        
        # GIF
        self.gif_movie = None
        self.gif_timer = QTimer()
        self.gif_timer.timeout.connect(self._update_gif_frame)
        self._last_gif_update = 0
        self._gif_min_interval = 0.1
        
        # Видимость
        self.desktop_visible = True
        self.visibility_timer = QTimer()
        self.visibility_timer.timeout.connect(self._check_desktop_visibility)
        self.visibility_timer.start(1000)
    
    def set_wallpaper(self, path):
        if not path or not os.path.exists(path):
            return
            
        path = os.path.normpath(path)
        self.current_file_path = path
        
        self._stop_all()
        
        ext = path.lower()
        
        if ext.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm')):
            self.media_player.setSource(QUrl.fromLocalFile(path))
            if self.desktop_visible:
                self.media_player.play()
                
        elif ext.endswith('.gif'):
            self.gif_movie = QMovie(path)
            self.gif_movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.gif_movie.start()
            
            if self.desktop_visible:
                config = config_manager.load_config()
                settings = config_manager.get_file_settings(config, path)
                target_fps = min(settings.get("gif_fps", 10), 15)
                interval = max(67, 1000 // target_fps)
                self._gif_min_interval = interval / 1000.0
                self.gif_timer.start(interval)
        else:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self._set_pixmap(pixmap, path)
    
    def update_audio(self, volume, muted):
        self.audio_output.setMuted(muted)
        self.audio_output.setVolume(volume / 100.0)
    
    def stop(self):
        self.visibility_timer.stop()
        self._stop_all()
        
        if self.current_wallpaper_path and os.path.exists(self.current_wallpaper_path):
            try:
                os.remove(self.current_wallpaper_path)
            except:
                pass
    
    def _stop_all(self):
        self.media_player.stop()
        self.gif_timer.stop()
        
        if self.gif_movie:
            self.gif_movie.stop()
            self.gif_movie = None
        
        self._last_gif_update = 0
    
    def _set_pixmap(self, pixmap, file_path=None):
        """Устанавливает статичное изображение"""
        if pixmap.isNull():
            return
        
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()
        
        config = config_manager.load_config()
        settings = config_manager.get_file_settings(config, file_path) if file_path else {}
        
        scale_mode = settings.get("scale_mode", "fill")
        focus_point = settings.get("focus_point", "center_center")
        
        if scale_mode == "fit":
            scaled = pixmap.scaled(
                screen_size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            final = self._crop_with_focus(scaled, screen_size, focus_point)
        else:
            final = pixmap.scaled(
                screen_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        temp_path = os.path.join(tempfile.gettempdir(), "wallpaper_static.bmp")
        
        if final.save(temp_path, "BMP"):
            self._apply_wallpaper(temp_path)
            self.current_wallpaper_path = temp_path
    
    def _update_gif_frame(self):
        """Обновляет кадр GIF с троттлингом"""
        if not self.desktop_visible:
            return

        now = time.time()
        if now - self._last_gif_update < self._gif_min_interval:
            return

        self._last_gif_update = now

        if self.gif_movie and self.gif_movie.state() == QMovie.MovieState.Running:
            pixmap = self.gif_movie.currentPixmap()
            if not pixmap.isNull():
                self._apply_frame_fast(pixmap)

    def _apply_frame_fast(self, pixmap):
        """Быстрое применение кадра без сложной обработки"""
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()

        config = config_manager.load_config()
        settings = config_manager.get_file_settings(config, self.current_file_path)

        scale_mode = settings.get("scale_mode", "fill")
        focus_point = settings.get("focus_point", "center_center")
        
        # Быстрое масштабирование
        if scale_mode == "fit":
            scaled = pixmap.scaled(
                screen_size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.FastTransformation  # Быстрее чем Smooth
            )
            final = self._crop_with_focus(scaled, screen_size, focus_point)
        else:
            final = pixmap.scaled(
                screen_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
        
        # Используем фиксированный временный файл
        temp_path = os.path.join(tempfile.gettempdir(), "wallpaper_frame.bmp")
        
        try:
            if final.save(temp_path, "BMP"):
                # Быстрое применение
                ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_path, 0x02)
        except:
            pass
    
    def _process_video_frame(self, frame):
        """Кадры видео тоже с троттлингом"""
        if not self.desktop_visible or not frame.isValid():
            return
        
        now = time.time()
        if now - self._last_gif_update < 0.1:  # Не чаще 10 FPS для видео
            return
        self._last_gif_update = now
        
        image = frame.toImage()
        if not image.isNull():
            self._apply_frame_fast(QPixmap.fromImage(image))
    
    def _crop_with_focus(self, pixmap, target_size, focus_point):
        src_w, src_h = pixmap.width(), pixmap.height()
        tgt_w, tgt_h = target_size.width(), target_size.height()
        
        x, y = 0, 0
        
        if src_w > tgt_w:
            if "right" in focus_point:
                x = src_w - tgt_w
            elif "center" in focus_point:
                x = (src_w - tgt_w) // 2
        
        if src_h > tgt_h:
            if "bottom" in focus_point:
                y = src_h - tgt_h
            elif "center" in focus_point:
                y = (src_h - tgt_h) // 2
        
        x = max(0, min(x, src_w - tgt_w))
        y = max(0, min(y, src_h - tgt_h))
        
        return pixmap.copy(int(x), int(y), int(tgt_w), int(tgt_h))
    
    def _apply_wallpaper(self, image_path):
        try:
            abs_path = os.path.abspath(image_path)
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, abs_path)
            winreg.CloseKey(key)
            
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0x02)
        except Exception as e:
            print(f"[ERROR] Failed to set wallpaper: {e}")
    
    def _check_desktop_visibility(self):
        try:
            fg = ctypes.windll.user32.GetForegroundWindow()
            if fg:
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(fg, ctypes.byref(rect))
                sw = ctypes.windll.user32.GetSystemMetrics(0)
                sh = ctypes.windll.user32.GetSystemMetrics(1)
                ww = rect.right - rect.left
                wh = rect.bottom - rect.top
                
                is_fullscreen = (ww >= sw * 0.95 and wh >= sh * 0.95)
                desk = ctypes.windll.user32.FindWindowW("Progman", None)
                is_desktop = fg == desk
                
                was_visible = self.desktop_visible
                self.desktop_visible = not is_fullscreen or is_desktop
                
                if was_visible and not self.desktop_visible:
                    # Скрыт - пауза
                    if self.gif_movie:
                        self.gif_movie.setPaused(True)
                        self.gif_timer.stop()
                    if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                        self.media_player.pause()
                        
                elif not was_visible and self.desktop_visible:
                    if self.gif_movie and self.gif_movie.state() == QMovie.MovieState.Paused:
                        self.gif_movie.setPaused(False)
                        config = config_manager.load_config()
                        settings = config_manager.get_file_settings(config, self.current_file_path)
                        target_fps = min(settings.get("gif_fps", 10), 15)
                        interval = max(67, 1000 // target_fps)
                        self._gif_min_interval = interval / 1000.0
                        self.gif_timer.start(interval)
                    if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                        self.media_player.play()
        except:
            pass
