#!/usr/bin/env python3
"""
🤖 ПРОСТОЙ TELEGRAM БОТ
Версия 1.0
"""

import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import config
from database import db

# ==================== НАСТРОЙКА ====================

# Проверяем конфигурацию
try:
    config.validate()
except ValueError as e:
    print(e)
    exit(1)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем бота
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ==================== КЛАВИАТУРА ====================

def main_keyboard():
    """Создаем клавиатуру"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🎮 Игры"),
        KeyboardButton(text="ℹ️ Помощь")
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

# ==================== КОМАНДЫ ====================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Команда /start"""
    user = message.from_user
    
    # Сохраняем в БД
    await db.add_user(user.id, user.username, user.first_name)
    await db.add_message(user.id, "/start")
    
    # Отправляем приветствие
    welcome = f"""
👋 Привет, {user.first_name}!

🤖 Я - ваш Telegram бот!

📱 **Используйте кнопки или команды:**
/start - Начать
/help - Помощь
/profile - Профиль
/games - Игры

🎮 **Игры доступные:**
• Угадай число (1-100)
• Камень-Ножницы-Бумага
"""
    await message.answer(welcome, reply_markup=main_keyboard())
    await db.add_message(user.id, welcome, is_bot=True)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Команда /help"""
    help_text = """
📚 **ПОМОЩЬ**

**Команды:**
/start - Начало работы
/help - Эта справка
/profile - Ваш профиль
/games - Игры

**Игры:**
1. **Угадай число** - напишите число от 1 до 100
2. **КНБ** - напишите: камень, ножницы или бумага

**Кнопки:**
👤 Профиль - информация о вас
🎮 Игры - выбор игры
ℹ️ Помощь - эта справка
"""
    await message.answer(help_text)
    await db.add_message(message.from_user.id, help_text, is_bot=True)

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Команда /profile"""
    user = message.from_user
    profile = f"""
👤 **ВАШ ПРОФИЛЬ**

🆔 ID: {user.id}
👤 Имя: {user.first_name}
📛 Фамилия: {user.last_name or 'не указана'}
🔗 Юзернейм: @{user.username or 'не указан'}
🤖 Бот: {'✅ Да' if user.is_bot else '❌ Нет'}
"""
    await message.answer(profile)
    await db.add_message(user.id, profile, is_bot=True)

@dp.message(Command("games"))
async def cmd_games(message: types.Message):
    """Команда /games"""
    games_text = """
🎮 **ДОСТУПНЫЕ ИГРЫ**

1. **🎲 Угадай число**
   Напишите число от 1 до 100
   Я загадаю число и скажу больше или меньше

2. **✂️ Камень-Ножницы-Бумага**
   Напишите: камень, ножницы или бумага
   Сыграем в классическую игру

**Как играть:**
Просто отправьте сообщение с:
- Числом от 1 до 100
- Или словом: камень, ножницы, бумага
"""
    await message.answer(games_text)
    await db.add_message(message.from_user.id, games_text, is_bot=True)

# ==================== ОБРАБОТКА КНОПОК ====================

@dp.message(F.text == "👤 Профиль")
async def button_profile(message: types.Message):
    """Кнопка Профиль"""
    await cmd_profile(message)

@dp.message(F.text == "🎮 Игры")
async def button_games(message: types.Message):
    """Кнопка Игры"""
    await cmd_games(message)

@dp.message(F.text == "ℹ️ Помощь")
async def button_help(message: types.Message):
    """Кнопка Помощь"""
    await cmd_help(message)

# ==================== ИГРЫ ====================

@dp.message(F.text.regexp(r'^\d+$'))
async def guess_number_game(message: types.Message):
    """Игра: Угадай число"""
    try:
        guess = int(message.text)
        if 1 <= guess <= 100:
            secret = random.randint(1, 100)
            
            if guess == secret:
                response = f"🎉 УРА! Вы угадали! Число было {secret}"
            elif guess < secret:
                response = f"📈 Больше! Мое число больше чем {guess}"
            else:
                response = f"📉 Меньше! Мое число меньше чем {guess}"
        else:
            response = "🔢 Введите число от 1 до 100 для игры"
    except ValueError:
        response = "❌ Введите число для игры"
    
    await message.answer(response)
    await db.add_message(message.from_user.id, response, is_bot=True)

@dp.message(F.text.lower().in_(["камень", "ножницы", "бумага"]))
async def rock_paper_scissors_game(message: types.Message):
    """Игра: Камень-ножницы-бумага"""
    user_choice = message.text.lower()
    bot_choice = random.choice(["камень", "ножницы", "бумага"])
    
    # Определяем победителя
    if user_choice == bot_choice:
        result = "🤝 Ничья!"
    elif (user_choice == "камень" and bot_choice == "ножницы") or \
         (user_choice == "ножницы" and bot_choice == "бумага") or \
         (user_choice == "бумага" and bot_choice == "камень"):
        result = "🎉 Вы победили!"
    else:
        result = "😢 Вы проиграли!"
    
    response = f"""
✂️ **КАМЕНЬ-НОЖНИЦЫ-БУМАГА**

👤 Ваш выбор: {user_choice}
🤖 Мой выбор: {bot_choice}

{result}
"""
    await message.answer(response)
    await db.add_message(message.from_user.id, response, is_bot=True)

# ==================== ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ====================

@dp.message()
async def handle_all_messages(message: types.Message):
    """Обработка всех остальных сообщений"""
    user_text = message.text
    
    # Сохраняем сообщение пользователя
    await db.add_message(message.from_user.id, user_text)
    
    # Простой ответ
    response = f"💬 Вы написали: {user_text}\n\nИспользуйте кнопки или команды!"
    
    await message.answer(response)
    await db.add_message(message.from_user.id, response, is_bot=True)

# ==================== ЗАПУСК БОТА ====================

async def main():
    """Главная функция"""
    print("=" * 40)
    print("🤖 TELEGRAM BOT ЗАПУСКАЕТСЯ")
    print("=" * 40)
    print(f"🔑 Токен: {config.BOT_TOKEN[:20]}...")
    print("📁 База данных: bot.db")
    print("=" * 40)
    
    try:
        print("✅ Бот запущен!")
        print("📱 Откройте Telegram и найдите своего бота")
        print("🔄 Для остановки нажмите Ctrl+C")
        print("=" * 40)
        
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
