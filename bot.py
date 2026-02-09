#!/usr/bin/env python3
"""
Telegram бот с использованием Groq Llama 3

Быстрый AI бот на бесплатном API
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Загрузка переменных окружения
load_dotenv()

# Получение токенов
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.getenv('PORT', 8080))

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    print("Ошибка: Проверьте файл .env и наличие токенов")
    exit(1)

# Инициализация Groq клиента
client = Groq(api_key=GROQ_API_KEY)
app = FastAPI()

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
    
    welcome_text = """🤖 Привет! Я AI-бот с использованием Groq Llama 3.1

Доступные команды:
/start - Показать это сообщение
/help - Помощь
/reset - Сбросить контекст диалога

Просто напиши мне любой вопрос, и я постараюсь помочь!"""

    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """📋 Справка по командам:

/start - Запустить бота
/help - Показать справку
/reset - Сбросить контекст диалога

💡 Особенности:
• Бесплатный AI на базе Groq Llama 3.1
• Быстрые ответы
• Контекст диалога сохраняется
• Поддерживает любые вопросы на русском

❗️ Если бот не отвечает, попробуйте написать еще раз или используйте /reset"""
    
    await update.message.reply_text(help_text)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset"""
    user_id = update.effective_user.id
    reset_context(user_id)
    
    await update.message.reply_text("🔄 Контекст диалога сброшен. Напишите новый вопрос!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if not message_text or not message_text.strip():
            return
        
        # Добавляем сообщение пользователя в историю
        add_to_history(user_id, "user", message_text.strip())
        
        # Получаем историю для отправки в Groq
        history = get_history(user_id)
        
        # Отправляем запрос к Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history,
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )
        
        # Получаем ответ от Groq
        assistant_message = response.choices[0].message.content
        
        # Добавляем ответ ассистента в историю
        add_to_history(user_id, "assistant", assistant_message)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(assistant_message)
        
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        error_messages = {
            "rate_limit": "Превышен лимит запросов к Groq. Попробуйте позже.",
            "authentication": "Ошибка аутентификации Groq. Проверьте API ключ.",
            "timeout": "Время ожидания истекло. Попробуйте еще раз.",
        }
        
        # Определяем тип ошибки по ключевым словам
        error_msg = "Произошла ошибка. Попробуйте еще раз."
        if "rate" in str(e).lower():
            error_msg = error_messages["rate_limit"]
        elif "auth" in str(e).lower() or "unauthorized" in str(e).lower():
            error_msg = error_messages["authentication"]
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            error_msg = error_messages["timeout"]
        
        await update.message.reply_text(error_msg)

@app.get("/health")
async def health_check():
    """Health check endpoint для Scalingo"""
    return JSONResponse({
        "status": "healthy",
        "bot": "Groq Telegram Bot",
        "model": "llama-3.1-8b-instant",
        "api": "Groq"
    })

def main():
    """Основная функция запуска бота"""
    
    async def run_bot():
        # Создание приложения
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавление обработчиков
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("reset", reset_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Запуск бота с Groq Llama 3.1...")
        print("Модель: llama-3.1-8b-instant")
        print("API: Бесплатный Groq")
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
    # Если запущено на Scalingo, использовать FastAPI
    if os.getenv('SCALINGO_APP_NAME'):
        import uvicorn
        print("Запуск FastAPI сервера на Scalingo...")
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    else:
        main()