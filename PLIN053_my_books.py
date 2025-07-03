from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

from PLIN053_utils import show_popup, get_current_user, get_database

# Instance databáze
db = get_database()


class MyBooksScreen(Screen):
    """Obrazovka se seznamem mých knih"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Horní lišta
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        
        back_btn = Button(text='← Zpět', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'profile'))

        title = Label(text='Moje knihy', font_size=20)

        add_book_btn = Button(text='+ Přidat knihu', size_hint_x=0.4)
        add_book_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'add_book'))

        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_book_btn)

        # Filtry
        filter_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        
        self.all_btn = Button(text='Všechny', background_color=(0.2, 0.6, 1, 1))
        self.all_btn.bind(on_press=self.show_all_books)
        
        self.available_btn = Button(text='K prodeji')
        self.available_btn.bind(on_press=self.show_available_books)
        
        self.sold_btn = Button(text='Prodané')
        self.sold_btn.bind(on_press=self.show_sold_books)

        filter_layout.add_widget(self.all_btn)
        filter_layout.add_widget(self.available_btn)
        filter_layout.add_widget(self.sold_btn)

        # Seznam knih
        scroll = ScrollView(size_hint_y=0.82)
        self.books_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.books_layout.bind(minimum_height=self.books_layout.setter('height'))

        scroll.add_widget(self.books_layout)

        layout.add_widget(header)
        layout.add_widget(filter_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

        self.current_filter = 'all'  # Výchozí filtr

    def on_enter(self):
        """Načtení knih při vstupu na obrazovku"""
        self.load_books()

    def show_all_books(self, instance):
        """Zobrazení všech knih"""
        self.current_filter = 'all'
        self.all_btn.background_color = (0.2, 0.6, 1, 1)
        self.available_btn.background_color = (1, 1, 1, 1)
        self.sold_btn.background_color = (1, 1, 1, 1)
        self.load_books()

    def show_available_books(self, instance):
        """Zobrazení knih k prodeji"""
        self.current_filter = 'available'
        self.available_btn.background_color = (0.2, 0.6, 1, 1)
        self.all_btn.background_color = (1, 1, 1, 1)
        self.sold_btn.background_color = (1, 1, 1, 1)
        self.load_books()

    def show_sold_books(self, instance):
        """Zobrazení prodaných knih"""
        self.current_filter = 'sold'
        self.sold_btn.background_color = (0.2, 0.6, 1, 1)
        self.all_btn.background_color = (1, 1, 1, 1)
        self.available_btn.background_color = (1, 1, 1, 1)
        self.load_books()

    def load_books(self):
        """Načtení knih podle filtru"""
        current_user = get_current_user()
        if not current_user:
            return

        self.books_layout.clear_widgets()
        all_books = db.get_user_books(current_user['id'])

        # Filtrování knih
        if self.current_filter == 'available':
            books = [book for book in all_books if not book[6]]  # is_sold je na indexu 6
        elif self.current_filter == 'sold':
            books = [book for book in all_books if book[6]]
        else:  
            books = all_books

        if not books:
            filter_text = {
                'all': 'žádné knihy',
                'available': 'žádné knihy k prodeji',
                'sold': 'žádné prodané knihy'
            }
            no_books = Label(text=f'Zatím {filter_text[self.current_filter]}', size_hint_y=None, height=60)
            self.books_layout.add_widget(no_books)
            return

        for book in books:
            book_widget = self.create_book_widget(book)
            self.books_layout.add_widget(book_widget)

    def create_book_widget(self, book):
        """Vytvoření widgetu pro knihu"""
        book_id, title, author, price, condition, description, is_sold, created_at = book

        # Hlavní layout pro knihu
        book_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=10)

        # Informace o knize
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        status_text = "PRODÁNO" if is_sold else "K PRODEJI"
        status_color = (1, 0.3, 0.3, 1) if is_sold else (0.3, 1, 0.3, 1)
        
        title_label = Label(text=f"{title} - {author}", font_size=16, bold=True, halign='left')
        title_label.bind(size=title_label.setter('text_size'))
        
        details_label = Label(text=f"{price} Kč | {condition}", halign='left')
        details_label.bind(size=details_label.setter('text_size'))
        
        status_label = Label(text=status_text, color=status_color, halign='left')
        status_label.bind(size=status_label.setter('text_size'))

        info_layout.add_widget(title_label)
        info_layout.add_widget(details_label)
        info_layout.add_widget(status_label)

        # Tlačítka pro akce
        actions_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=5)

        if not is_sold:
            # Tlačítko pro označení jako prodané
            mark_sold_btn = Button(text='Označit\njako prodané', font_size=12)
            mark_sold_btn.bind(on_press=lambda x, bid=book_id: self.mark_as_sold(bid))
            actions_layout.add_widget(mark_sold_btn)
        else:
            # Tlačítko pro vrácení do prodeje
            mark_available_btn = Button(text='Vrátit\ndo prodeje', font_size=12)
            mark_available_btn.bind(on_press=lambda x, bid=book_id: self.mark_as_available(bid))
            actions_layout.add_widget(mark_available_btn)

        # Tlačítko pro smazání
        delete_btn = Button(text='Smazat', font_size=12, background_color=(1, 0.3, 0.3, 1))
        delete_btn.bind(on_press=lambda x, bid=book_id, title=title: self.confirm_delete(bid, title))
        actions_layout.add_widget(delete_btn)

        book_layout.add_widget(info_layout)
        book_layout.add_widget(actions_layout)

        return book_layout

    def mark_as_sold(self, book_id):
        """Označení knihy jako prodané"""
        current_user = get_current_user()
        if not current_user:
            return

        success, message = db.update_book_status(book_id, current_user['id'], True)
        if success:
            show_popup("Úspěch", message)
            self.load_books()
        else:
            show_popup("Chyba", message)

    def mark_as_available(self, book_id):
        """Vrácení knihy do prodeje"""
        current_user = get_current_user()
        if not current_user:
            return

        success, message = db.update_book_status(book_id, current_user['id'], False)
        if success:
            show_popup("Úspěch", message)
            self.load_books()
        else:
            show_popup("Chyba", message)

    def confirm_delete(self, book_id, title):
        """Potvrzení smazání knihy"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f'Opravdu chcete smazat knihu\n"{title}"?'))

        buttons_layout = BoxLayout(spacing=10)
        
        confirm_btn = Button(text='Ano, smazat', background_color=(1, 0.3, 0.3, 1))
        cancel_btn = Button(text='Zrušit')

        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)

        popup = Popup(title='Potvrzení smazání', content=content, size_hint=(0.8, 0.4))
        
        confirm_btn.bind(on_press=lambda x: self.delete_book(book_id, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def delete_book(self, book_id, popup):
        """Smazání knihy"""
        current_user = get_current_user()
        if not current_user:
            return

        success, message = db.delete_book(book_id, current_user['id'])
        popup.dismiss()
        
        if success:
            show_popup("Úspěch", message)
            self.load_books()
        else:
            show_popup("Chyba", message)