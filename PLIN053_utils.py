from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from PLIN053_database import Database

db = Database()
current_user = None


def show_popup(title, message):
    """Zobrazení popup zprávy"""
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=message))

    close_btn = Button(text='OK', size_hint_y=None, height=40)
    content.add_widget(close_btn)

    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    close_btn.bind(on_press=popup.dismiss)
    popup.open()

def set_current_user(user):
    """Nastavení aktuálního uživatele"""
    global current_user
    current_user = user


def get_current_user():
    """Získání aktuálního uživatele"""
    return current_user


def get_database():
    """Získání instance databáze"""
    return db


def logout_user():
    """Odhlášení uživatele"""
    global current_user
    current_user = None