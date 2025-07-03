from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from PLIN053_utils import show_popup, get_current_user, get_database

# Instance databáze
db = get_database()

class HomeScreen(Screen):
    """Hlavní obrazovka s nabídkou knih"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Horní lišta
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        self.welcome_label = Label(text='Knihomat', font_size=20)
        header.add_widget(self.welcome_label)

        nav_layout = BoxLayout(size_hint_x=0.6, spacing=5)

        messages_btn = Button(text='Zprávy', size_hint_x=0.5)
        messages_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'conversations'))

        profile_btn = Button(text='Profil', size_hint_x=0.5)
        profile_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'profile'))

        nav_layout.add_widget(messages_btn)
        nav_layout.add_widget(profile_btn)
        header.add_widget(nav_layout)

        # Vyhledávání
        search_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        self.search_input = TextInput(hint_text='Vyhledat knihu...', size_hint_x=0.8)
        search_btn = Button(text='Hledat', size_hint_x=0.2)
        search_btn.bind(on_press=self.search_books)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)

        # Seznam knih (scroll view)
        scroll = ScrollView(size_hint_y=0.8)
        self.books_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.books_layout.bind(minimum_height=self.books_layout.setter('height'))

        scroll.add_widget(self.books_layout)

        layout.add_widget(header)
        layout.add_widget(search_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def on_enter(self):
        """Zavolá se při vstupu na obrazovku"""
        current_user = get_current_user()
        if current_user:
            self.welcome_label.text = f"Vítejte, {current_user['name']}!"
        self.load_books()

    def load_books(self):
        """Načtení knih z databáze"""
        self.books_layout.clear_widgets()
        books = db.get_all_books()

        if not books:
            no_books = Label(text='Zatím žádné knihy k prodeji', size_hint_y=None, height=60)
            self.books_layout.add_widget(no_books)
            return

        for book in books:
            book_id, title, author, price, condition, description, seller_name = book

            book_text = f"{title} - {author}\n{price} Kč | {condition} | Prodává: {seller_name}"
            book_btn = Button(text=book_text, size_hint_y=None, height=80, text_size=(None, None))
            book_btn.bind(on_press=lambda x, book_data=book: self.view_book_detail(book_data))
            self.books_layout.add_widget(book_btn)

    def search_books(self, instance):
        """Vyhledání knih"""
        query = self.search_input.text.strip()
        if not query:
            self.load_books()
            return

        self.books_layout.clear_widgets()
        books = db.search_books(query)

        if not books:
            no_books = Label(text=f'Žádné knihy nenalezeny pro "{query}"', size_hint_y=None, height=60)
            self.books_layout.add_widget(no_books)
            return

        for book in books:
            book_id, title, author, price, condition, description, seller_name = book

            book_text = f"{title} - {author}\n{price} Kč | {condition} | Prodává: {seller_name}"
            book_btn = Button(text=book_text, size_hint_y=None, height=80, text_size=(None, None))
            book_btn.bind(on_press=lambda x, book_data=book: self.view_book_detail(book_data))
            self.books_layout.add_widget(book_btn)

    def view_book_detail(self, book_data):
        """Zobrazení detailu knihy"""
        # Předání dat do detail obrazovky
        detail_screen = self.manager.get_screen('book_detail')
        detail_screen.set_book_data(book_data)
        self.manager.current = 'book_detail'


class BookDetailScreen(Screen):
    """Obrazovka s detailem knihy"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.book_data = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Zpět tlačítko
        back_btn = Button(text='← Zpět', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        # Detail knihy
        self.book_info = BoxLayout(orientation='vertical', size_hint_y=0.7, spacing=10)

        # Tlačítka
        buttons_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        buy_btn = Button(text='Koupit')
        buy_btn.bind(on_press=self.buy_book)

        message_btn = Button(text='Napsat prodávajícímu')
        message_btn.bind(on_press=self.message_seller)

        buttons_layout.add_widget(buy_btn)
        buttons_layout.add_widget(message_btn)

        layout.add_widget(back_btn)
        layout.add_widget(self.book_info)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def set_book_data(self, book_data):
        """Nastavení dat knihy"""
        self.book_data = book_data
        self.update_book_info()

    def update_book_info(self):
        """Aktualizace zobrazení detailu knihy"""
        if not self.book_data:
            return

        book_id, title, author, price, condition, description, seller_name = self.book_data

        self.book_info.clear_widgets()

        self.book_info.add_widget(Label(text=title, font_size=20))
        self.book_info.add_widget(Label(text=f'Autor: {author}'))
        self.book_info.add_widget(Label(text=f'Stav: {condition}'))
        self.book_info.add_widget(Label(text=f'Cena: {price} Kč', font_size=18))
        self.book_info.add_widget(Label(text=f'Prodává: {seller_name}'))
        if description:
            self.book_info.add_widget(Label(text=f'Popis: {description}'))

    def buy_book(self, instance):
        """Zahájení procesu nákupu knihy"""
        current_user = get_current_user()
        
        if not current_user:
            show_popup("Chyba", "Pro nákup knihy se musíte přihlásit!")
            return

        if not self.book_data:
            show_popup("Chyba", "Chyba při načítání dat knihy!")
            return

        book_id = self.book_data[0]
        seller_id = db.get_seller_id_by_book(book_id)

        # Kontrola, zda uživatel nekupuje vlastní knihu
        if seller_id == current_user['id']:
            show_popup("Info", "Nemůžete koupit vlastní knihu!")
            return

        # Kontrola, zda kniha ještě není prodaná
        book_details = db.get_book_details(book_id)
        if book_details and book_details[9]:  # is_sold je na indexu 9
            show_popup("Info", "Tato kniha již byla prodána!")
            return

        # Přechod na obrazovku nákupu
        purchase_screen = self.manager.get_screen('purchase')
        purchase_screen.set_book_for_purchase(book_id)
        self.manager.current = 'purchase'

    def message_seller(self, instance):
        """Kontaktování prodávajícího - vytvoření konverzace"""
        current_user = get_current_user()
        if not current_user:
            show_popup("Chyba", "Pro kontaktování prodávajícího se musíte přihlásit!")
            return

        if not self.book_data:
            show_popup("Chyba", "Chyba při načítání dat knihy!")
            return

        book_id = self.book_data[0]
        seller_id = db.get_seller_id_by_book(book_id)

        if not seller_id:
            show_popup("Chyba", "Nepodařilo se najít prodávajícího!")
            return

        # Kontrola, zda uživatel nekontaktuje sám sebe
        if seller_id == current_user['id']:
            show_popup("Info", "Nemůžete kontaktovat sami sebe!")
            return

        # Vytvoření nebo získání konverzace
        conversation_id = db.create_or_get_conversation(book_id, current_user['id'], seller_id)

        if conversation_id:
            # Přechod na chat
            chat_screen = self.manager.get_screen('chat')
            chat_screen.set_conversation(conversation_id)
            self.manager.current = 'chat'
        else:
            show_popup("Chyba", "Nepodařilo se vytvořit konverzaci!")

class AddBookScreen(Screen):
    """Obrazovka pro přidání nové knihy"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Nadpis
        title = Label(text='Přidat knihu k prodeji', size_hint_y=0.1, font_size=20)

        # Formulář
        form_layout = GridLayout(cols=2, size_hint_y=0.7, spacing=10)

        form_layout.add_widget(Label(text='Název knihy:'))
        self.title_input = TextInput(multiline=False)
        form_layout.add_widget(self.title_input)

        form_layout.add_widget(Label(text='Autor:'))
        self.author_input = TextInput(multiline=False)
        form_layout.add_widget(self.author_input)

        form_layout.add_widget(Label(text='Cena (Kč):'))
        self.price_input = TextInput(multiline=False, input_filter='float')
        form_layout.add_widget(self.price_input)

        form_layout.add_widget(Label(text='Stav:'))
        self.condition_input = TextInput(multiline=False, text='Velmi dobrý')
        form_layout.add_widget(self.condition_input)

        form_layout.add_widget(Label(text='Popis:'))
        self.description_input = TextInput(multiline=True)
        form_layout.add_widget(self.description_input)

        # Tlačítka
        buttons_layout = BoxLayout(size_hint_y=0.2, spacing=10)

        save_btn = Button(text='Přidat knihu')
        save_btn.bind(on_press=self.save_book)

        cancel_btn = Button(text='Zrušit')
        cancel_btn.bind(on_press=self.cancel)

        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)

        layout.add_widget(title)
        layout.add_widget(form_layout)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def save_book(self, instance):
        """Uložení knihy do databáze"""
        current_user = get_current_user()
        if not current_user:
            show_popup("Chyba", "Nejste přihlášeni!")
            return

        title = self.title_input.text.strip()
        author = self.author_input.text.strip()
        price_text = self.price_input.text.strip()
        condition = self.condition_input.text.strip()
        description = self.description_input.text.strip()

        # Validace
        if not title or not author or not price_text:
            show_popup("Chyba", "Vyplňte všechna povinná pole!")
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError()
        except ValueError:
            show_popup("Chyba", "Zadejte platnou cenu!")
            return

        # Uložení do databáze
        success, message = db.add_book(title, author, price, condition, description, current_user['id'])

        if success:
            show_popup("Úspěch", message)
            self.clear_form()
            self.manager.current = 'home'
        else:
            show_popup("Chyba", message)

    def clear_form(self):
        """Vymazání formuláře"""
        self.title_input.text = ""
        self.author_input.text = ""
        self.price_input.text = ""
        self.condition_input.text = "Velmi dobrý"
        self.description_input.text = ""

    def cancel(self, instance):
        self.clear_form()
        self.manager.current = 'profile'

    def add_book(self, instance):
        print("Otevírám formulář pro přidání knihy")

    def view_my_books(self, instance):
        print("Zobrazuji moje knihy")

    def logout(self, instance):
        self.manager.current = 'login'