from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from PLIN053_login_screen import LoginScreen, RegisterScreen
from PLIN053_book_screen import HomeScreen, BookDetailScreen, AddBookScreen
from PLIN053_profile_screen import ProfileScreen
from PLIN053_chat_screen import ConversationsScreen, ChatScreen
from PLIN053_purchase_screen import PurchaseScreen, OrdersScreen
from PLIN053_my_books import MyBooksScreen

class BookSellingApp(App):

    def build(self):

        sm = ScreenManager()

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(BookDetailScreen(name='book_detail'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(AddBookScreen(name='add_book'))
        sm.add_widget(ConversationsScreen(name='conversations'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(PurchaseScreen(name='purchase'))
        sm.add_widget(OrdersScreen(name='orders'))
        sm.add_widget(MyBooksScreen(name='my_books'))

        sm.current = 'login' #počáteční obrazovka je přihlášení

        return sm

if __name__ == '__main__':
    BookSellingApp().run()