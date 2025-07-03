
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from PLIN053_utils import show_popup, get_current_user, logout_user

class ProfileScreen(Screen):
    """Obrazovka profilu uživatele"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Zpět tlačítko
        back_btn = Button(text='← Zpět na hlavní', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        # Profil info
        self.profile_info = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=10)

        # Menu tlačítka
        menu_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=10)

        add_book_btn = Button(text='Přidat knihu k prodeji')
        add_book_btn.bind(on_press=self.add_book)

        my_books_btn = Button(text='Moje knihy')
        my_books_btn.bind(on_press=self.view_my_books)

        orders_btn = Button(text='Moje objednávky')
        orders_btn.bind(on_press=self.view_orders)

        logout_btn = Button(text='Odhlásit se')
        logout_btn.bind(on_press=self.logout)

        menu_layout.add_widget(add_book_btn)
        menu_layout.add_widget(my_books_btn)
        menu_layout.add_widget(orders_btn)
        menu_layout.add_widget(logout_btn)

        layout.add_widget(back_btn)
        layout.add_widget(self.profile_info)
        layout.add_widget(menu_layout)

        self.add_widget(layout)

    def on_enter(self):
        """Aktualizace profilu při vstupu"""
        self.update_profile_info()

    def update_profile_info(self):
        """Aktualizace informací o profilu"""
        self.profile_info.clear_widgets()

        current_user = get_current_user()
        if current_user:
            self.profile_info.add_widget(Label(text='Můj profil', font_size=24))
            self.profile_info.add_widget(Label(text=f"Jméno: {current_user['name']}"))
            self.profile_info.add_widget(Label(text=f"Email: {current_user['email']}"))
            
        else:
            self.profile_info.add_widget(Label(text='Nejste přihlášeni'))

    def add_book(self, instance):
        current_user = get_current_user()
        if not current_user:
            show_popup("Chyba", "Nejste přihlášeni!")
            return
        self.manager.current = 'add_book'

    def view_my_books(self, instance):
        current_user = get_current_user()
        if not current_user:
            show_popup("Chyba", "Nejste přihlášeni!")
            return
        self.manager.current = 'my_books'

    def logout(self, instance):
        logout_user()
        global current_user
        current_user = None
        show_popup("Info", "Byli jste odhlášeni")
        self.manager.current = 'login'

    def view_orders(self, instance):
        """Zobrazení objednávek"""
        current_user = get_current_user()
        if not current_user:
            show_popup("Chyba", "Nejste přihlášeni!")
            return
        self.manager.current = 'orders'