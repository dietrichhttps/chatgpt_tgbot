#!/usr/bin/env python3
"""
Telegram бот с использованием Groq Llama 3.1

Простой запуск на локальной машине или ноутбуке
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Загрузка переменных окружения
load_dotenv()

# Получение токенов
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Проверка обязательных переменных
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    logging.error("Ошибка: Проверьте файл .env и наличие токенов")
    logging.error("Требуются: TELEGRAM_BOT_TOKEN и GROQ_API_KEY")
    exit(1)

# Инициализация Groq клиента
try:
    client = Groq(api_key=GROQ_API_KEY)
    logging.info("✅ Groq клиент успешно инициализирован")
except Exception as e:
    logging.error(f"❌ Ошибка инициализации Groq клиента: {e}")
    exit(1)

# Хранение истории диалогов
dialog_history = {}

def reset_context(user_id):
    """Сброс контекста для пользователя"""
    dialog_history[user_id] = []
    logging.info(f"🔄 Контекст сброшен для пользователя {user_id}")

def get_history(user_id):
    """Получение истории диалога для пользователя"""
    return dialog_history.get(user_id, [])

def add_to_history(user_id, role, content):
    """Добавление сообщения в историю"""
    if user_id not in dialog_history:
        dialog_history[user_id] = []
    
    # Ограничим историю 10 сообщениями для экономии памяти
    if len(dialog_history[user_id]) >= 10:
        dialog_history[user_id] = dialog_history[user_id][-9:]
    
    dialog_history[user_id].append({"role": role, "content": content})

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
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
        logging.info(f"👤 Пользователь {user_id} запустил бота")
        
    except Exception as e:
        logging.error(f"❌ Ошибка в start_command: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    try:
        help_text = """📋 Справка по командам:

/start - Запустить бота
/help - Показать справку
/reset - Сбросить контекст диалога

💡 Особенности:
• Бесплатный AI на базе Groq Llama 3.1
• Быстрые ответы
• Контекст диалога сохраняется (последние 10 сообщений)
• Поддерживает любые вопросы на русском

❗️ Если бот не отвечает, попробуйте написать еще раз или используйте /reset"""
        
        await update.message.reply_text(help_text)
        logging.info(f"❓ Пользователь {update.effective_user.id} запросил помощь")
        
    except Exception as e:
        logging.error(f"❌ Ошибка в help_command: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset"""
    try:
        user_id = update.effective_user.id
        reset_context(user_id)
        
        await update.message.reply_text("🔄 Контекст диалога сброшен. Напишите новый вопрос!")
        logging.info(f"🔄 Пользователь {user_id} сбросил контекст")
        
    except Exception as e:
        logging.error(f"❌ Ошибка в reset_command: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

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
        
        logging.info(f"📨 Пользователь {user_id}: {message_text[:50]}...")
        
        # Отправляем запрос к Groq с таймаутом
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.1-8b-instant",
                messages=history,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            ),
            timeout=30.0  # 30 секунд таймаут
        )
        
        # Получаем ответ от Groq
        assistant_message = response.choices[0].message.content
        
        if not assistant_message:
            assistant_message = "Извините, не удалось сформировать ответ. Попробуйте еще раз."
        
        # Добавляем ответ ассистента в историю
        add_to_history(user_id, "assistant", assistant_message)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(assistant_message)
        logging.info(f"📩 Ответ отправлен пользователю {user_id}")
        
    except asyncio.TimeoutError:
        logging.error(f"⏰ Таймаут при запросе к Groq для пользователя {user_id}")
        await update.message.reply_text("⏰ Время ожидания истекло. Попробуйте еще раз.")
        
    except Exception as e:
        logging.error(f"❌ Ошибка при обработке сообщения от пользователя {user_id}: {e}")
        
        error_messages = {
            "rate_limit": "🚫 Превышен лимит запросов к Groq. Попробуйте позже.",
            "authentication": "🔑 Ошибка аутентификации Groq. Проверьте API ключ.",
            "timeout": "⏰ Время ожидания истекло. Попробуйте еще раз.",
            "connection": "🔌 Проблемы с соединением. Попробуйте еще раз."
        }
        
        # Определяем тип ошибки по ключевым словам
        error_msg = "Произошла ошибка. Попробуйте еще раз."
        error_str = str(e).lower()
        
        if "rate" in error_str:
            error_msg = error_messages["rate_limit"]
        elif "auth" in error_str or "unauthorized" in error_str:
            error_msg = error_messages["authentication"]
        elif "timeout" in error_str:
            error_msg = error_messages["timeout"]
        elif "connection" in error_str:
            error_msg = error_messages["connection"]
        
        try:
            await update.message.reply_text(error_msg)
        except:
            logging.error("Не удалось отправить сообщение об ошибке")

def main():
    """Основная функция запуска бота"""
    
    async def run_bot():
        try:
            # Создание приложения
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Добавление обработчиков
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("reset", reset_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Запуск бота
            logging.info("🚀 Запуск бота с Groq Llama 3.1...")
            logging.info("📋 Модель: llama-3.1-8b-instant")
            logging.info("💡 API: Groq (бесплатный)")
            logging.info("💻 Платформа: Локальный запуск")
            
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
            logging.info("✅ Бот успешно запущен и готов к работе!")
            logging.info("💬 Нажмите Ctrl+C для остановки")
            
            # Бесконечный цикл с обработкой прерываний
            while True:
                try:
                    await asyncio.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    logging.info("🛑 Получен сигнал остановки...")
                    break
                except Exception as e:
                    logging.error(f"❌ Ошибка в главном цикле: {e}")
                    
        except Exception as e:
            logging.error(f"❌ Критическая ошибка при запуске бота: {e}")
            raise
    
    # Запуск с обработкой исключений
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("🛑 Остановка бота по запросу пользователя...")
    except Exception as e:
        logging.error(f"❌ Неожиданная ошибка: {e}")
    finally:
        logging.info("👋 Бот остановлен")

if __name__ == '__main__':
    logging.info("🔧 Запуск Groq Telegram Bot...")
    main()