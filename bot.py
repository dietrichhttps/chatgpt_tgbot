#!/usr/bin/env python3
"""
ChatGPT Telegram Bot

Простой бот для общения с ChatGPT через Telegram с поддержкой прокси
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Загрузка переменных окружения
load_dotenv()

# Получение токенов
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_PROXY = os.getenv('OPENAI_PROXY')

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    print("Ошибка: Проверьте файл .env и наличие токенов")
    exit(1)

# Настройка HTTP клиента с прокси (если указан)
http_client = None
if OPENAI_PROXY:
    print(f"Используем прокси: {OPENAI_PROXY}")
    http_client = httpx.Client(
        proxy=OPENAI_PROXY,
        timeout=30.0
    )
else:
    print("Прокси не настроен, используем прямое соединение")

# Инициализация OpenAI клиента с прокси
if http_client:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        http_client=http_client
    )
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Хранение истории диалогов
dialog_history = {}

def reset_context(user_id):
    """Сброс контекста для пользователя"""
    dialog_history[user_id] = []

def get_history(user_id):
    """Получение истории диалога для пользователя"""
    return dialog_history.get(user_id, [])

def add_to_history(user_id, role, content):
    """Добавление сообщения в историю"""
    if user_id not in dialog_history:
        dialog_history[user_id] = []
    dialog_history[user_id].append({"role": role, "content": content})

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Сброс контекста
    reset_context(user_id)
    
    # Создание клавиатуры
    keyboard = [["Новый запрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Привет! Я ChatGPT бот. Отправь мне сообщение, и я отвечу с помощью ChatGPT.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "📋 Доступные команды:\n"
        "/start - Начать новый диалог (сбросить историю)\n"
        "/help - Показать эту справку\n"
        "\n💬 Просто отправь мне любое текстовое сообщение, и я отвечу с помощью ChatGPT!"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Проверка на кнопку "Новый запрос"
    if user_message == "Новый запрос":
        reset_context(user_id)
        await update.message.reply_text("✅ Контекст диалога очищен! Теперь я слушаю ваш новый запрос.")
        return
    
    try:
        # Показываем индикатор набора
        await update.message.chat.send_action("typing")
        
        # Добавляем сообщение пользователя в историю
        add_to_history(user_id, "user", user_message)
        
        # Получаем историю для отправки в OpenAI
        history = get_history(user_id)
        
        # Отправляем запрос в OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Получаем ответ от ChatGPT
        assistant_message = response.choices[0].message.content
        
        # Добавляем ответ ассистента в историю
        add_to_history(user_id, "assistant", assistant_message)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(assistant_message)
        
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция запуска бота"""
    
    async def run_bot():
        # Создание приложения
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавление обработчиков
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запуск бота
        print("Запуск бота...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(1)
    
    # Запуск
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Остановка бота...")

if __name__ == '__main__':
    main()