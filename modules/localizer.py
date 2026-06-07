"""The module responsible for project localization (i18n)"""
import json
import os
import sys


def get_resource_path(relative_path):
    """Gets the correct path to resources in the compiled application"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Localizer:
    """
    The localizer class. Remembers the current language and returns
    the necessary strings in the desired language i18n
    """
    def __init__(self, language="en"):
        """Sets the starting parameters for a class that changes languages"""
        self.language = language
        self.text = {}
        self._load(language)

    def _load(self, language):
        """Uploads the localization file"""
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
        """
        The function returns a localized text fragment. The function requests
        the key as in .a json file and returns the text in the desired
        language .
        """
        text = self.text.get(key, key)
        if args:
            return text.format(*args)
        return text

    def refresh_language(self, language):
        """A function that updates the language of the application"""
        self._load(language)
