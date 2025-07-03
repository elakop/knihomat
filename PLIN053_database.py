import sqlite3
import hashlib
import os
from datetime import datetime
from kivy.utils import platform

class Database:

    def __init__(self):
        # cesta k databázi pro různé platformy
        if platform == 'android':
            # Pro Android -> použití app storage
            from kivy.app import App
            app = App.get_running_app()
            if app:
                self.db_name = os.path.join(app.user_data_dir, 'knihomat.db')
            else:
                # Fallback (záchrana, pokud appka ještě neběží)
                self.db_name = '/data/data/org.example.knihomat/files/knihomat.db'
        else:
            # Pro počítač
            self.db_name = 'knihomat.db'
            
        # Vytvoření adresáře (pokud ještě nexistuje)
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        self.init_database()

    def init_database(self):
        """Vytvoření tabulek v databázi"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Tabulka uživatelů
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabulka knih
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                price REAL NOT NULL,
                condition TEXT NOT NULL,
                description TEXT,
                seller_id INTEGER NOT NULL,
                is_sold BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES users (id)
            )
        ''')

        # Tabulka konverzací
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        buyer_id INTEGER NOT NULL,
                        seller_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (book_id) REFERENCES books (id),
                        FOREIGN KEY (buyer_id) REFERENCES users (id),
                        FOREIGN KEY (seller_id) REFERENCES users (id),
                        UNIQUE(book_id, buyer_id, seller_id)
                    )
                ''')

        # Tabulka zpráv
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                        FOREIGN KEY (sender_id) REFERENCES users (id)
                    )
                ''')
        
        #tabulka objednávek
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        buyer_id INTEGER NOT NULL,
                        seller_id INTEGER NOT NULL,
                        order_status TEXT DEFAULT 'pending',
                        total_price REAL NOT NULL,
                        buyer_address TEXT,
                        buyer_phone TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (book_id) REFERENCES books (id),
                        FOREIGN KEY (buyer_id) REFERENCES users (id),
                        FOREIGN KEY (seller_id) REFERENCES users (id)
                    )
                ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Zahashování hesla"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, name, email, password):
        """Registrace nového uživatele"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )

            conn.commit()
            conn.close()
            return True, "Registrace úspěšná!"
        except sqlite3.IntegrityError:
            return False, "Email už je zaregistrovaný!"
        except Exception as e:
            return False, f"Chyba: {str(e)}"

    def login_user(self, email, password):
        """Přihlášení uživatele"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute(
                "SELECT id, name, email FROM users WHERE email = ? AND password_hash = ?",
                (email, password_hash)
            )

            user = cursor.fetchone()
            conn.close()

            if user:
                return True, {"id": user[0], "name": user[1], "email": user[2]}
            else:
                return False, "Špatný email nebo heslo!"
        except Exception as e:
            return False, f"Chyba: {str(e)}"

    def add_book(self, title, author, price, condition, description, seller_id):
        """Přidání knihy do databáze"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO books (title, author, price, condition, description, seller_id) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, price, condition, description, seller_id)
            )

            conn.commit()
            conn.close()
            return True, "Kniha byla přidána!"
        except Exception as e:
            return False, f"Chyba: {str(e)}"

    def get_all_books(self):
        """Získání všech knih z databáze"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.title, b.author, b.price, b.condition, b.description, u.name
                FROM books b
                JOIN users u ON b.seller_id = u.id
                WHERE b.is_sold = FALSE
                ORDER BY b.created_at DESC
            ''')

            books = cursor.fetchall()
            conn.close()
            return books
        except Exception as e:
            print(f"Chyba při načítání knih: {str(e)}")
            return []

    def search_books(self, query):
        """Vyhledání knih podle názvu nebo autora"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.title, b.author, b.price, b.condition, b.description, u.name
                FROM books b
                JOIN users u ON b.seller_id = u.id
                WHERE (b.title LIKE ? OR b.author LIKE ?) AND b.is_sold = FALSE
                ORDER BY b.created_at DESC
            ''', (f'%{query}%', f'%{query}%'))

            books = cursor.fetchall()
            conn.close()
            return books
        except Exception as e:
            print(f"Chyba při vyhledávání: {str(e)}")
            return []

    def create_or_get_conversation(self, book_id, buyer_id, seller_id):
        """Vytvoření nebo získání konverzace"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # najít existující konverzaci
            cursor.execute(
                "SELECT id FROM conversations WHERE book_id = ? AND buyer_id = ? AND seller_id = ?",
                (book_id, buyer_id, seller_id)
            )

            conversation = cursor.fetchone()

            if conversation:
                conversation_id = conversation[0]
            else:
                # Vytvořit novou konverzaci
                cursor.execute(
                    "INSERT INTO conversations (book_id, buyer_id, seller_id) VALUES (?, ?, ?)",
                    (book_id, buyer_id, seller_id)
                )
                conversation_id = cursor.lastrowid
                conn.commit()

            conn.close()
            return conversation_id
        except Exception as e:
            print(f"Chyba při vytváření konverzace: {str(e)}")
            return None

    def send_message(self, conversation_id, sender_id, message):
        """Odeslání zprávy"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO messages (conversation_id, sender_id, message) VALUES (?, ?, ?)",
                (conversation_id, sender_id, message)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Chyba při odesílání zprávy: {str(e)}")
            return False

    def get_messages(self, conversation_id):
        """Získání zpráv z konverzace"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT m.id, m.message, m.created_at, m.sender_id, u.name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.conversation_id = ?
                ORDER BY m.created_at ASC
            ''', (conversation_id,))

            messages = cursor.fetchall()
            conn.close()
            return messages
        except Exception as e:
            print(f"Chyba při načítání zpráv: {str(e)}")
            return []

    def get_user_conversations(self, user_id):
        """Získání všech konverzací uživatele"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT DISTINCT c.id, b.title, b.author, 
                       CASE WHEN c.buyer_id = ? THEN seller_u.name ELSE buyer_u.name END as other_user_name,
                       CASE WHEN c.buyer_id = ? THEN 'buyer' ELSE 'seller' END as user_role,
                       c.created_at
                FROM conversations c
                JOIN books b ON c.book_id = b.id
                JOIN users seller_u ON c.seller_id = seller_u.id
                JOIN users buyer_u ON c.buyer_id = buyer_u.id
                WHERE c.buyer_id = ? OR c.seller_id = ?
                ORDER BY c.created_at DESC
            ''', (user_id, user_id, user_id, user_id))

            conversations = cursor.fetchall()
            conn.close()
            return conversations
        except Exception as e:
            print(f"Chyba při načítání konverzací: {str(e)}")
            return []

    def get_conversation_info(self, conversation_id):
        """Získání informací o konverzaci"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT c.id, b.title, b.author, b.price, seller_u.name, buyer_u.name, c.book_id
                FROM conversations c
                JOIN books b ON c.book_id = b.id
                JOIN users seller_u ON c.seller_id = seller_u.id
                JOIN users buyer_u ON c.buyer_id = buyer_u.id
                WHERE c.id = ?
            ''', (conversation_id,))

            info = cursor.fetchone()
            conn.close()
            return info
        except Exception as e:
            print(f"Chyba při načítání informací o konverzaci: {str(e)}")
            return None

    def get_seller_id_by_book(self, book_id):
        """Získání ID prodávajícího podle ID knihy"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("SELECT seller_id FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else None
        except Exception as e:
            print(f"Chyba při získávání seller_id: {str(e)}")
            return None
    
    def create_order(self, book_id, buyer_id, buyer_address, buyer_phone):
        """Vytvoření objednávky"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Získání informací o knize
            cursor.execute("SELECT seller_id, price, is_sold FROM books WHERE id = ?", (book_id,))
            book_info = cursor.fetchone()
            
            if not book_info:
                return False, "Kniha nebyla nalezena!"
            
            seller_id, price, is_sold = book_info
            
            if is_sold:
                return False, "Kniha již byla prodána!"
            
            if seller_id == buyer_id:
                return False, "Nemůžete koupit vlastní knihu!"

            # Vytvoření objednávky
            cursor.execute('''
                INSERT INTO orders (book_id, buyer_id, seller_id, total_price, buyer_address, buyer_phone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book_id, buyer_id, seller_id, price, buyer_address, buyer_phone))

            order_id = cursor.lastrowid

            # Označení knihy jako prodané
            cursor.execute("UPDATE books SET is_sold = TRUE WHERE id = ?", (book_id,))

            conn.commit()
            conn.close()
            
            return True, f"Objednávka #{order_id} byla úspěšně vytvořena!"
            
        except Exception as e:
            return False, f"Chyba při vytváření objednávky: {str(e)}"

    def get_user_orders(self, user_id, as_buyer=True):
        """Získání objednávek uživatele"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            if as_buyer:
                # Objednávky jako kupující
                cursor.execute('''
                    SELECT o.id, b.title, b.author, o.total_price, o.order_status, 
                        o.created_at, u.name as seller_name
                    FROM orders o
                    JOIN books b ON o.book_id = b.id
                    JOIN users u ON o.seller_id = u.id
                    WHERE o.buyer_id = ?
                    ORDER BY o.created_at DESC
                ''', (user_id,))
            else:
                # Objednávky jako prodávající
                cursor.execute('''
                    SELECT o.id, b.title, b.author, o.total_price, o.order_status, 
                        o.created_at, u.name as buyer_name, o.buyer_address, o.buyer_phone
                    FROM orders o
                    JOIN books b ON o.book_id = b.id
                    JOIN users u ON o.buyer_id = u.id
                    WHERE o.seller_id = ?
                    ORDER BY o.created_at DESC
                ''', (user_id,))

            orders = cursor.fetchall()
            conn.close()
            return orders
            
        except Exception as e:
            print(f"Chyba při načítání objednávek: {str(e)}")
            return []

    def update_order_status(self, order_id, new_status):
        """Aktualizace stavu objednávky"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", (new_status, order_id))
            
            if new_status == 'completed':
                cursor.execute("UPDATE orders SET completed_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))

            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Chyba při aktualizaci objednávky: {str(e)}")
            return False

    def get_book_details(self, book_id):
        """Získání detailů knihy pro nákup"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.title, b.author, b.price, b.condition, b.description, 
                    u.name, u.email, b.seller_id, b.is_sold
                FROM books b
                JOIN users u ON b.seller_id = u.id
                WHERE b.id = ?
            ''', (book_id,))

            book = cursor.fetchone()
            conn.close()
            return book
            
        except Exception as e:
            print(f"Chyba při načítání detailů knihy: {str(e)}")
            return None
        
    def get_user_books(self, user_id):
        """Získání všech knih uživatele"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.title, b.author, b.price, b.condition, b.description, 
                    b.is_sold, b.created_at
                FROM books b
                WHERE b.seller_id = ?
                ORDER BY b.created_at DESC
            ''', (user_id,))

            books = cursor.fetchall()
            conn.close()
            return books
            
        except Exception as e:
            print(f"Chyba při načítání uživatelových knih: {str(e)}")
            return []

    def delete_book(self, book_id, user_id):
        """Smazání knihy (pouze vlastník může smazat)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Kontrola, jestli je uživatel vlastníkem knihy
            cursor.execute("SELECT seller_id, is_sold FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Kniha nebyla nalezena!"
            
            seller_id, is_sold = result
            
            if seller_id != user_id:
                return False, "Nemůžete smazat cizí knihu!"
            
            if is_sold:
                return False, "Nelze smazat prodanou knihu!"

            # Smazání knihy
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            
            conn.commit()
            conn.close()
            return True, "Kniha byla smazána!"
            
        except Exception as e:
            return False, f"Chyba při mazání knihy: {str(e)}"

    def update_book_status(self, book_id, user_id, is_sold):
        """Změna stavu knihy (prodáno/k prodeji)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Kontrola vlastnictví
            cursor.execute("SELECT seller_id FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != user_id:
                return False, "Nemůžete upravit cizí knihu!"

            cursor.execute("UPDATE books SET is_sold = ? WHERE id = ?", (is_sold, book_id))
            
            conn.commit()
            conn.close()
            
            status_text = "prodáno" if is_sold else "k prodeji"
            return True, f"Stav knihy změněn na: {status_text}"
            
        except Exception as e:
            return False, f"Chyba při změně stavu: {str(e)}"