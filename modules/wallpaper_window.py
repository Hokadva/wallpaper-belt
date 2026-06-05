import ctypes
import os
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QMovie, QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
import modules.config_manager as config_manager
import winreg

class WallpaperEngine:
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
        self.current_frame_path = None
        self.current_wallpaper_path = None
        
        # GIF анимация
        self.gif_movie = None
        self.gif_timer = QTimer()
        self.gif_timer.timeout.connect(self._update_gif_frame)
        
        # Видимость рабочего стола
        self.desktop_visible = True
        self.visibility_timer = QTimer()
        self.visibility_timer.timeout.connect(self._check_desktop_visibility)
        self.visibility_timer.start(500)
    
    def set_wallpaper(self, path):
        """Устанавливает обои (изображение, GIF или видео)"""
        if not path or not os.path.exists(path):
            return
            
        path = os.path.normpath(path)
        self.current_file_path = path
        
        # Останавливаем всё
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
                fps = settings.get("gif_fps", 10)
                interval = max(33, 1000 // fps)
                self.gif_timer.start(interval)
        else:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self._set_pixmap(pixmap, path)
    
    def update_audio(self, volume, muted):
        """Обновляет настройки аудио"""
        self.audio_output.setMuted(muted)
        self.audio_output.setVolume(volume / 100.0)
    
    def stop(self):
        """Останавливает все процессы"""
        self.visibility_timer.stop()
        self._stop_all()
        
        for temp_file in [self.current_frame_path, self.current_wallpaper_path]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def _stop_all(self):
        """Останавливает все анимации и видео"""
        self.media_player.stop()
        self.gif_timer.stop()
        
        if self.gif_movie:
            self.gif_movie.stop()
            self.gif_movie = None
        
        if self.current_frame_path and os.path.exists(self.current_frame_path):
            try:
                os.remove(self.current_frame_path)
            except:
                pass
            self.current_frame_path = None
    
    def _set_pixmap(self, pixmap, file_path=None):
        """Устанавливает QPixmap как обои с учетом настроек"""
        if pixmap.isNull() or not self.desktop_visible:
            return
        
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()
        
        config = config_manager.load_config()
        settings = config_manager.get_file_settings(config, file_path) if file_path else {}
        
        scale_mode = settings.get("scale_mode", "fill")
        focus_point = settings.get("focus_point", "center")
        
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
        
        temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
        temp_path = os.path.join(temp_dir, "wallpaper_current.png")
        
        if final.save(temp_path, "PNG"):
            self._apply_wallpaper(temp_path)
            self.current_wallpaper_path = temp_path
    
    def _crop_with_focus(self, pixmap, target_size, focus_point):
        """Обрезает изображение с учетом точки фокуса"""
        src_w, src_h = pixmap.width(), pixmap.height()
        tgt_w, tgt_h = target_size.width(), target_size.height()
        
        x = 0
        y = 0
        
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
        """Применяет обои через Windows API"""
        try:
            abs_path = os.path.abspath(image_path)
            
            # Устанавливаем стиль
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)
            
            SPI_SETDESKWALLPAPER = 20
            SPIF_SENDCHANGE = 0x02
            
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 0, abs_path, SPIF_SENDCHANGE
            )
        except Exception as e:
            print(f"[ERROR] Failed to set wallpaper: {e}")
    
    def _process_video_frame(self, frame):
        if not self.desktop_visible or not frame.isValid():
            return
        image = frame.toImage()
        if not image.isNull():
            self._set_pixmap(QPixmap.fromImage(image), self.current_file_path)
    
    def _update_gif_frame(self):
        if not self.desktop_visible:
            return
        if self.gif_movie and self.gif_movie.state() == QMovie.MovieState.Running:
            pixmap = self.gif_movie.currentPixmap()
            if not pixmap.isNull():
                self._set_pixmap(pixmap, self.current_file_path)
    
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
                
                self.desktop_visible = not is_fullscreen or is_desktop
                
                if not self.desktop_visible:
                    if self.gif_movie:
                        self.gif_movie.setPaused(True)
                        self.gif_timer.stop()
                    if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                        self.media_player.pause()
                else:
                    if self.gif_movie and self.gif_movie.state() == QMovie.MovieState.Paused:
                        self.gif_movie.setPaused(False)
                        config = config_manager.load_config()
                        settings = config_manager.get_file_settings(config, self.current_file_path)
                        fps = settings.get("gif_fps", 10)
                        self.gif_timer.start(max(33, 1000 // fps))
                    if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                        self.media_player.play()
        except:
            pass
