from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from PLIN053_utils import show_popup, get_current_user, get_database

# Instance databáze
db = get_database()

class ConversationsScreen(Screen):
    """Obrazovka se seznamem konverzací"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Nadpis a zpět tlačítko
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        back_btn = Button(text='← Zpět', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        title = Label(text='Moje konverzace', font_size=20)

        header.add_widget(back_btn)
        header.add_widget(title)

        # Seznam konverzací
        scroll = ScrollView(size_hint_y=0.9)
        self.conversations_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.conversations_layout.bind(minimum_height=self.conversations_layout.setter('height'))

        scroll.add_widget(self.conversations_layout)

        layout.add_widget(header)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def on_enter(self):
        """Načtení konverzací při vstup na obrazovku"""
        self.load_conversations()

    def load_conversations(self):
        """Načtení všech konverzací uživatele"""
        current_user = get_current_user()
        if not current_user:
            return

        self.conversations_layout.clear_widgets()
        conversations = db.get_user_conversations(current_user['id'])

        if not conversations:
            no_conversations = Label(text='Zatím žádné konverzace', size_hint_y=None, height=60)
            self.conversations_layout.add_widget(no_conversations)
            return

        for conversation in conversations:
            conv_id, book_title, book_author, other_user, user_role, created_at = conversation

            role_text = "Kupujete" if user_role == "buyer" else "Prodáváte"
            conv_text = f"{book_title} - {book_author}\n{role_text} | {other_user}"

            conv_btn = Button(text=conv_text, size_hint_y=None, height=80, text_size=(None, None))
            conv_btn.bind(on_press=lambda x, c_id=conv_id: self.open_conversation(c_id))
            self.conversations_layout.add_widget(conv_btn)

    def open_conversation(self, conversation_id):
        """Otevření konkrétní konverzace"""
        chat_screen = self.manager.get_screen('chat')
        chat_screen.set_conversation(conversation_id)
        self.manager.current = 'chat'


class ChatScreen(Screen):
    """Obrazovka chatu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_id = None
        self.conversation_info = None

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Horní lišta s informacemi o konverzaci
        header = BoxLayout(size_hint_y=0.1, spacing=10)

        back_btn = Button(text='← Zpět', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)

        self.header_info = Label(text='Chat', font_size=16)

        header.add_widget(back_btn)
        header.add_widget(self.header_info)

        # Oblast pro zprávy
        scroll = ScrollView(size_hint_y=0.7)
        self.messages_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        scroll.add_widget(self.messages_layout)

        # Vstupní pole pro novou zprávu
        input_layout = BoxLayout(size_hint_y=0.2, spacing=10)

        self.message_input = TextInput(multiline=True, size_hint_x=0.8)
        send_btn = Button(text='Odeslat', size_hint_x=0.2)
        send_btn.bind(on_press=self.send_message)

        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)

        layout.add_widget(header)
        layout.add_widget(scroll)
        layout.add_widget(input_layout)

        self.add_widget(layout)

        # Pravidelná aktualizace zpráv
        Clock.schedule_interval(self.refresh_messages, 2)

    def set_conversation(self, conversation_id):
        """Nastavení konverzace pro zobrazení"""
        self.conversation_id = conversation_id

        # Načtení informací o konverzaci
        self.conversation_info = db.get_conversation_info(conversation_id)

        if self.conversation_info:
            conv_id, book_title, book_author, book_price, seller_name, buyer_name, book_id = self.conversation_info
            self.header_info.text = f"{book_title} - {book_author}"

        # Načtení zpráv
        self.load_messages()

    def load_messages(self):
        """Načtení všech zpráv v konverzaci"""
        if not self.conversation_id:
            return

        self.messages_layout.clear_widgets()
        messages = db.get_messages(self.conversation_id)

        for message in messages:
            msg_id, msg_text, created_at, sender_id, sender_name = message

            current_user = get_current_user()
            # Určení, jestli je zpráva od aktuálního uživatele
            is_my_message = current_user and sender_id == current_user['id']

            # Vytvoření zprávy s informací o odesílateli
            if is_my_message:
                message_text = f"Já: {msg_text}"
                # Můžete přidat jiné styling pro vlastní zprávy
            else:
                message_text = f"{sender_name}: {msg_text}"

            message_label = Label(
                text=message_text,
                size_hint_y=None,
                height=40,
                text_size=(None, None),
                halign='left' if not is_my_message else 'right'
            )

            self.messages_layout.add_widget(message_label)

    def send_message(self, instance):
        """Odeslání nové zprávy"""
        current_user = get_current_user()
        if not current_user or not self.conversation_id:
            show_popup("Chyba", "Nejste přihlášeni nebo není vybrana konverzace!")
            return

        message_text = self.message_input.text.strip()
        if not message_text:
            return

        # Odeslání zprávy do databáze
        success = db.send_message(self.conversation_id, current_user['id'], message_text)

        if success:
            self.message_input.text = ""  # Vymazání inputu
            self.load_messages()  # Znovu načtení zpráv
        else:
            show_popup("Chyba", "Nepodařilo se odeslat zprávu!")

    def refresh_messages(self, dt):
        """Pravidelná aktualizace zpráv (pro real-time chat)"""
        if self.conversation_id and self.manager.current == 'chat':
            self.load_messages()

    def go_back(self, instance):
        """Návrat na seznam konverzací"""
        self.manager.current = 'conversations'