import json
import os
import sys


def get_resource_path(relative_path):
    """Получает правильный путь к ресурсам в собранном приложении"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class Localizer:
    def __init__(self, language="en"):
        self.language = language
        self.text = {}
        self._load(language)
    
    def _load(self, language):
        """Загружает файл локализации"""
        path = get_resource_path(os.path.join('locales', f'{language}.json'))

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                self.text = json.load(file)
                self.language = language
                return

        path = get_resource_path(os.path.join('locales', 'en.json'))
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                self.text = json.load(file)
                self.language = "en"

    def get_string(self, key: str, *args):
        text = self.text.get(key, key)
        if args:
            return text.format(*args)
        return text

    def refresh_language(self, language):
        self._load(language)
