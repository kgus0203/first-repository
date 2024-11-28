import json
import streamlit as st

class Localization:
    def __init__(self, lang='ko'):
        self.lang = lang
        self.translations = self.load_translations()

    def load_translations(self):
        with open('translations.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_text(self, key):
        return self.translations.get(self.lang, {}).get(key, key)

    def switch_language(self):
        if self.lang == 'ko':
            self.lang = 'en'
        elif self.lang == 'en':
            self.lang = 'jp'
        else:
            self.lang = 'ko'

    def get_text(self, key):
        try:
            return self.translations[self.lang][key]
        except KeyError:
            st.warning(f"'{key}'가 '{self.lang}' 언어에 없습니다.")
            return key
        
