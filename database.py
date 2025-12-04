import aiosqlite
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создаем таблицы в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица сообщений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    async def add_user(self, user_id: int, username: str, first_name: str):
        """Добавить пользователя в БД"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, datetime.now()))
            await db.commit()
    
    async def add_message(self, user_id: int, text: str, is_bot: bool = False):
        """Добавить сообщение в историю"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO messages (user_id, text, is_bot, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, text, is_bot, datetime.now()))
            await db.commit()

db = Database()
