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


class PurchaseScreen(Screen):
    """Obrazovka pro potvrzení nákupu knihy"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.book_id = None
        self.book_info = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Zpět tlačítko
        back_btn = Button(text='← Zpět', size_hint_y=0.08)
        back_btn.bind(on_press=self.go_back)

        # Nadpis
        title = Label(text='Potvrzení nákupu', size_hint_y=0.08, font_size=20)

        # Informace o knize
        self.book_info_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=5)

        # Formulář pro dodací údaje
        form_label = Label(text='Dodací údaje:', size_hint_y=0.05, font_size=16)
        
        form_layout = GridLayout(cols=2, size_hint_y=0.3, spacing=10)

        form_layout.add_widget(Label(text='Dodací adresa:'))
        self.address_input = TextInput(multiline=True, hint_text='Ulice, město, PSČ')
        form_layout.add_widget(self.address_input)

        form_layout.add_widget(Label(text='Telefon:'))
        self.phone_input = TextInput(multiline=False, hint_text='+420 xxx xxx xxx')
        form_layout.add_widget(self.phone_input)

        # Celková cena
        self.price_layout = BoxLayout(orientation='vertical', size_hint_y=0.1, spacing=5)

        # Tlačítka
        buttons_layout = BoxLayout(size_hint_y=0.14, spacing=10)
        
        confirm_btn = Button(text='Potvrdit objednávku', background_color=(0.2, 0.8, 0.2, 1))
        confirm_btn.bind(on_press=self.confirm_purchase)

        cancel_btn = Button(text='Zrušit', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn.bind(on_press=self.go_back)

        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)

        layout.add_widget(back_btn)
        layout.add_widget(title)
        layout.add_widget(self.book_info_layout)
        layout.add_widget(form_label)
        layout.add_widget(form_layout)
        layout.add_widget(self.price_layout)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def set_book_for_purchase(self, book_id):
        """Nastavení knihy pro nákup"""
        self.book_id = book_id
        self.book_info = db.get_book_details(book_id)
        self.update_book_display()

    def update_book_display(self):
        """Aktualizace zobrazení informací o knize"""
        self.book_info_layout.clear_widgets()
        self.price_layout.clear_widgets()

        if not self.book_info:
            self.book_info_layout.add_widget(Label(text='Chyba při načítání knihy'))
            return

        book_id, title, author, price, condition, description, seller_name, seller_email, seller_id, is_sold = self.book_info

        if is_sold:
            self.book_info_layout.add_widget(Label(text='Tato kniha již byla prodána!', color=(1, 0, 0, 1)))
            return

        # Informace o knize
        self.book_info_layout.add_widget(Label(text=f'Kniha: {title}', font_size=18))
        self.book_info_layout.add_widget(Label(text=f'Autor: {author}'))
        self.book_info_layout.add_widget(Label(text=f'Stav: {condition}'))
        self.book_info_layout.add_widget(Label(text=f'Prodává: {seller_name}'))

        # Celková cena
        self.price_layout.add_widget(Label(text=f'Celková cena: {price} Kč', font_size=18, bold=True))

    def confirm_purchase(self, instance):
        """Potvrzení nákupu"""
        current_user = get_current_user()
        
        if not current_user:
            show_popup("Chyba", "Nejste přihlášeni!")
            return

        if not self.book_id:
            show_popup("Chyba", "Není vybrána žádná kniha!")
            return

        # Validace formuláře
        address = self.address_input.text.strip()
        phone = self.phone_input.text.strip()

        if not address:
            show_popup("Chyba", "Vyplňte dodací adresu!")
            return

        if not phone:
            show_popup("Chyba", "Vyplňte telefonní číslo!")
            return

        # Vytvoření objednávky
        success, message = db.create_order(
            self.book_id,
            current_user['id'],
            address,
            phone
        )

        if success:
            show_popup("Úspěch", message)
            self.clear_form()
            self.manager.current = 'orders'  # Přechod na seznam objednávek
        else:
            show_popup("Chyba", message)

    def clear_form(self):
        """Vymazání formuláře"""
        self.address_input.text = ""
        self.phone_input.text = ""

    def go_back(self, instance):
        """Návrat zpět"""
        self.clear_form()
        self.manager.current = 'book_detail'


class OrdersScreen(Screen):
    """Obrazovka se seznamem objednávek"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Horní lišta
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        
        back_btn = Button(text='← Zpět', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        title = Label(text='Moje objednávky', font_size=20)

        header.add_widget(back_btn)
        header.add_widget(title)

        # Přepínač mezi nákupy a prodeji
        toggle_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        
        self.purchases_btn = Button(text='Mé nákupy', background_color=(0.2, 0.6, 1, 1))
        self.purchases_btn.bind(on_press=self.show_purchases)
        
        self.sales_btn = Button(text='Mé prodeje')
        self.sales_btn.bind(on_press=self.show_sales)

        toggle_layout.add_widget(self.purchases_btn)
        toggle_layout.add_widget(self.sales_btn)

        # Seznam objednávek
        scroll = ScrollView(size_hint_y=0.82)
        self.orders_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.orders_layout.bind(minimum_height=self.orders_layout.setter('height'))

        scroll.add_widget(self.orders_layout)

        layout.add_widget(header)
        layout.add_widget(toggle_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

        self.current_view = 'purchases'  # Výchozí zobrazení

    def on_enter(self):
        """Načtení objednávek při vstupu na obrazovku"""
        self.show_purchases(None)

    def show_purchases(self, instance):
        """Zobrazení nákupů"""
        self.current_view = 'purchases'
        self.purchases_btn.background_color = (0.2, 0.6, 1, 1)
        self.sales_btn.background_color = (1, 1, 1, 1)
        self.load_orders(as_buyer=True)

    def show_sales(self, instance):
        """Zobrazení prodejů"""
        self.current_view = 'sales'
        self.sales_btn.background_color = (0.2, 0.6, 1, 1)
        self.purchases_btn.background_color = (1, 1, 1, 1)
        self.load_orders(as_buyer=False)

    def load_orders(self, as_buyer=True):
        """Načtení objednávek"""
        current_user = get_current_user()
        if not current_user:
            return

        self.orders_layout.clear_widgets()
        orders = db.get_user_orders(current_user['id'], as_buyer)

        if not orders:
            no_orders_text = 'Zatím žádné nákupy' if as_buyer else 'Zatím žádné prodeje'
            no_orders = Label(text=no_orders_text, size_hint_y=None, height=60)
            self.orders_layout.add_widget(no_orders)
            return

        for order in orders:
            order_widget = self.create_order_widget(order, as_buyer)
            self.orders_layout.add_widget(order_widget)

    def create_order_widget(self, order, as_buyer):
        """Vytvoření widgetu pro objednávku"""
        if as_buyer:
            order_id, title, author, price, status, created_at, other_user = order
            contact_info = ""
        else:
            order_id, title, author, price, status, created_at, other_user, address, phone = order
            contact_info = f"\nAdresa: {address}\nTelefon: {phone}"

        # Převod stavu do češtiny
        status_cz = {
            'pending': 'Čeká na vyřízení',
            'confirmed': 'Potvrzeno',
            'shipped': 'Odesláno',
            'completed': 'Dokončeno',
            'cancelled': 'Zrušeno'
        }.get(status, status)

        role_text = 'Prodáno uživateli:' if not as_buyer else 'Koupeno od:'
        
        order_text = f"#{order_id} - {title} ({author})\n{price} Kč | {status_cz}\n{role_text} {other_user}{contact_info}"

        order_btn = Button(
            text=order_text,
            size_hint_y=None,
            height=120,
            text_size=(None, None),
            halign='left',
            valign='middle'
        )

        # Pokud je prodávající, může měnit stav objednávky
        if not as_buyer and status == 'pending':
            order_btn.bind(on_press=lambda x, oid=order_id: self.confirm_order(oid))

        return order_btn

    def confirm_order(self, order_id):
        """Potvrzení objednávky prodávajícím"""
        success = db.update_order_status(order_id, 'confirmed')
        if success:
            show_popup("Úspěch", "Objednávka byla potvrzena!")
            self.load_orders(as_buyer=False)
        else:
            show_popup("Chyba", "Nepodařilo se potvrdit objednávku!")