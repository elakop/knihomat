from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout

from PLIN053_utils import show_popup, set_current_user, get_database

# Instance databáze
db = get_database()

class LoginScreen(Screen):
    """Obrazovka pro přihlášení"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Nadpis
        title = Label(text='Knihomat - Přihlášení', size_hint_y=0.2, font_size=24)

        # Formulář
        form_layout = GridLayout(cols=2, size_hint_y=0.6, spacing=10)

        form_layout.add_widget(Label(text='Email:'))
        self.email_input = TextInput(multiline=False)
        form_layout.add_widget(self.email_input)

        form_layout.add_widget(Label(text='Heslo:'))
        self.password_input = TextInput(password=True, multiline=False)
        form_layout.add_widget(self.password_input)

        # Tlačítka
        buttons_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        login_btn = Button(text='Přihlásit se')
        login_btn.bind(on_press=self.login)

        register_btn = Button(text='Registrovat se')
        register_btn.bind(on_press=self.go_to_register)

        buttons_layout.add_widget(login_btn)
        buttons_layout.add_widget(register_btn)

        layout.add_widget(title)
        layout.add_widget(form_layout)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def login(self, instance):
        # Skutečné přihlášení přes databázi
        email = self.email_input.text.strip()
        password = self.password_input.text

        if not email or not password:
            show_popup("Chyba", "Vyplňte všechna pole!")
            return

        success, result = db.login_user(email, password)

        if success:
            set_current_user(result)
            show_popup("Úspěch", f"Vítejte, {result['name']}!")
            self.manager.current = 'home'
            # Vymazání formuláře
            self.email_input.text = ""
            self.password_input.text = ""
        else:
            show_popup("Chyba", result)

    def go_to_register(self, instance):
        self.manager.current = 'register'


class RegisterScreen(Screen):
    """Obrazovka pro registraci"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        title = Label(text='Registrace', size_hint_y=0.15, font_size=24)

        # Formulář
        form_layout = GridLayout(cols=2, size_hint_y=0.6, spacing=10)

        form_layout.add_widget(Label(text='Jméno:'))
        self.name_input = TextInput(multiline=False)
        form_layout.add_widget(self.name_input)

        form_layout.add_widget(Label(text='Email:'))
        self.email_input = TextInput(multiline=False)
        form_layout.add_widget(self.email_input)

        form_layout.add_widget(Label(text='Heslo:'))
        self.password_input = TextInput(password=True, multiline=False)
        form_layout.add_widget(self.password_input)

        # Tlačítka
        buttons_layout = BoxLayout(size_hint_y=0.25, spacing=10)
        register_btn = Button(text='Registrovat')
        register_btn.bind(on_press=self.register)

        back_btn = Button(text='Zpět')
        back_btn.bind(on_press=self.go_back)

        buttons_layout.add_widget(register_btn)
        buttons_layout.add_widget(back_btn)

        layout.add_widget(title)
        layout.add_widget(form_layout)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def register(self, instance):
        # Skutečná registrace do databáze
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text

        if not name or not email or not password:
            show_popup("Chyba", "Vyplňte všechna pole!")
            return

        if len(password) < 6:
            show_popup("Chyba", "Heslo musí mít alespoň 6 znaků!")
            return

        success, message = db.register_user(name, email, password)

        if success:
            show_popup("Úspěch", message)
            self.manager.current = 'login'
            # Vymazání formuláře
            self.name_input.text = ""
            self.email_input.text = ""
            self.password_input.text = ""
        else:
            show_popup("Chyba", message)

    def go_back(self, instance):
        self.manager.current = 'login'