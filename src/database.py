import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                credits INTEGER DEFAULT 0,
                search_count INTEGER DEFAULT 0,
                generation_count INTEGER DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                default_inventory TEXT,
                default_format TEXT DEFAULT 'WITH_URL',
                default_quantity INTEGER DEFAULT 1,
                search_notifications BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                record_count INTEGER DEFAULT 0,
                domain_count INTEGER DEFAULT 0,
                file_size INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                domain TEXT NOT NULL,
                results_found INTEGER DEFAULT 0,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Generation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_history (
                generation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                domain TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                output_format TEXT NOT NULL,
                inventory_source TEXT,
                results_generated INTEGER DEFAULT 0,
                generation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Credit transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Domain index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domain_index (
                domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                inventory_id INTEGER NOT NULL,
                record_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(inventory_id) REFERENCES inventory(inventory_id)
            )
        ''')

        # Admin logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(admin_id) REFERENCES users(user_id)
            )
        ''')

        # Daily limits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_limits (
                limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                search_count INTEGER DEFAULT 0,
                generation_count INTEGER DEFAULT 0,
                date DATE DEFAULT CURRENT_DATE,
                UNIQUE(user_id, date),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        # Cooldown table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cooldown (
                cooldown_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                cooldown_until TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def create_user(self, user_id: int, username: str = None, is_admin: bool = False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, is_admin, credits)
                VALUES (?, ?, ?, 0)
            ''', (user_id, username, is_admin))
            
            cursor.execute('''
                INSERT OR IGNORE INTO user_settings (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    def get_user(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def add_credits(self, user_id: int, amount: int, reason: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users SET credits = credits + ? WHERE user_id = ?
            ''', (amount, user_id))
            
            cursor.execute('''
                INSERT INTO credit_transactions (user_id, amount, transaction_type, reason)
                VALUES (?, ?, 'ADD', ?)
            ''', (user_id, amount, reason))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return False
        finally:
            conn.close()

    def remove_credits(self, user_id: int, amount: int, reason: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            user = self.get_user(user_id)
            if user and user['credits'] >= amount:
                cursor.execute('''
                    UPDATE users SET credits = credits - ? WHERE user_id = ?
                ''', (amount, user_id))
                
                cursor.execute('''
                    INSERT INTO credit_transactions (user_id, amount, transaction_type, reason)
                    VALUES (?, ?, 'REMOVE', ?)
                ''', (user_id, amount, reason))
                
                conn.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing credits: {e}")
            return False
        finally:
            conn.close()

    def get_user_credits(self, user_id: int):
        user = self.get_user(user_id)
        return user['credits'] if user else 0

    def add_search_history(self, user_id: int, domain: str, results_found: int = 0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO search_history (user_id, domain, results_found)
                VALUES (?, ?, ?)
            ''', (user_id, domain, results_found))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding search history: {e}")
            return False
        finally:
            conn.close()

    def add_generation_history(self, user_id: int, domain: str, quantity: int, 
                              output_format: str, inventory_source: str = None, results_generated: int = 0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO generation_history (user_id, domain, quantity, output_format, inventory_source, results_generated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, domain, quantity, output_format, inventory_source, results_generated))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding generation history: {e}")
            return False
        finally:
            conn.close()

    def get_user_search_history(self, user_id: int, limit: int = 10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM search_history WHERE user_id = ? ORDER BY search_time DESC LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_user_generation_history(self, user_id: int, limit: int = 10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM generation_history WHERE user_id = ? ORDER BY generation_time DESC LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def add_inventory(self, filename: str, file_path: str, record_count: int = 0, domain_count: int = 0, file_size: int = 0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO inventory (filename, file_path, record_count, domain_count, file_size, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (filename, file_path, record_count, domain_count, file_size))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding inventory: {e}")
            return False
        finally:
            conn.close()

    def get_all_inventory(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory ORDER BY last_updated DESC')
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def remove_inventory(self, filename: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM inventory WHERE filename = ?', (filename,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing inventory: {e}")
            return False
        finally:
            conn.close()

    def log_admin_action(self, admin_id: int, action: str, details: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, details)
                VALUES (?, ?, ?)
            ''', (admin_id, action, details))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging admin action: {e}")
            return False
        finally:
            conn.close()

    def ban_user(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False
        finally:
            conn.close()

    def unban_user(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False
        finally:
            conn.close()

    def is_user_banned(self, user_id: int):
        user = self.get_user(user_id)
        return user['is_banned'] if user else False

    def is_admin(self, user_id: int):
        user = self.get_user(user_id)
        return user['is_admin'] if user else False
