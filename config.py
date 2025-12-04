import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота берется из .env файла
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Telegram ID администратора
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # Проверяем токен
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не установлен! Создайте файл .env")
        return True

config = Config()
