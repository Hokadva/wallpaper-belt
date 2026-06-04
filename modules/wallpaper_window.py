import ctypes
import os
import tempfile
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QMovie, QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink

class WallpaperWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("[DEBUG] WallpaperManager initialized")
        
        self.setWindowTitle("WallpaperManager")
        self.setGeometry(0, 0, 1, 1)
        
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        
        self.video_sink = QVideoSink(self)
        self.media_player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self.process_video_frame)
        
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
        
        self.current_wallpaper_path = None
        self.current_frame_path = None
        
        print("[DEBUG] WallpaperManager initialized successfully")

    def process_video_frame(self, frame):
        """Обрабатывает кадры видео для установки как обои"""
        if frame.isValid():
            image = frame.toImage()
            if not image.isNull():
                temp_path = os.path.join(tempfile.gettempdir(), "wallpaper_frame.png")
                pixmap = QPixmap.fromImage(image)
                
                screen = QGuiApplication.primaryScreen()
                screen_size = screen.size()
                scaled = pixmap.scaled(
                    screen_size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                if scaled.save(temp_path, "PNG"):
                    self.current_frame_path = temp_path
                    self.set_windows_wallpaper(temp_path)

    def set_windows_wallpaper(self, image_path):
        """Быстрая установка обоев через Windows API"""
        try:
            abs_path = os.path.abspath(image_path)

            SPI_SETDESKWALLPAPER = 20
            SPIF_SENDCHANGE = 0x02
            
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                SPIF_SENDCHANGE
            )
            print(f"[DEBUG] Wallpaper set: {abs_path}")
                
        except Exception as e:
            print(f"[ERROR] Exception setting wallpaper: {e}")

    def update_audio_settings(self, volume_int, is_muted):
        self.audio_output.setMuted(is_muted)
        self.audio_output.setVolume(volume_int / 100.0)

    def display_wallpaper(self, path):
        """Отображает обои (изображение или видео)"""
        print(f"[DEBUG] display_wallpaper: {path}")
        
        if not path or not os.path.exists(path):
            print(f"[ERROR] File not found: {path}")
            return
            
        path = os.path.normpath(path)
        
        self.media_player.stop()
        
        if self.current_frame_path and os.path.exists(self.current_frame_path):
            try:
                os.remove(self.current_frame_path)
            except:
                pass
            self.current_frame_path = None
        
        ext = path.lower()
        
        try:
            if ext.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm')):
                print("[DEBUG] Playing video wallpaper...")
                self.media_player.setSource(QUrl.fromLocalFile(path))
                self.media_player.play()
            else:
                print("[DEBUG] Setting image wallpaper...")
                
                if ext.endswith('.gif'):
                    movie = QMovie(path)
                    movie.jumpToFrame(0)
                    pixmap = QPixmap(movie.currentImage())
                    movie.stop()
                else:
                    pixmap = QPixmap(path)
                
                if not pixmap.isNull():
                    screen = QGuiApplication.primaryScreen()
                    screen_size = screen.size()
                    
                    scaled = pixmap.scaled(
                        screen_size,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
                    temp_path = os.path.join(temp_dir, "wallpaper_current.bmp")
                    
                    if scaled.save(temp_path, "BMP"):
                        self.set_windows_wallpaper(temp_path)
                        self.current_wallpaper_path = temp_path
                    else:
                        print("[ERROR] Failed to save image")
                else:
                    print("[ERROR] Failed to load image")
                    
        except Exception as e:
            print(f"[ERROR] Error setting wallpaper: {e}")

    def stop(self):
        """Останавливает все процессы"""
        print("[DEBUG] Stopping wallpaper manager...")
        self.media_player.stop()
        
        for temp_file in [self.current_frame_path, self.current_wallpaper_path]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
