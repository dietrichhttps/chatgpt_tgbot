import os
import logging
from typing import Dict, List
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get API keys from environment
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configure OpenAI
openai.api_key = OPENAI_API_KEY


class DialogueManager:
    """Manages conversation history for each user"""
    
    def __init__(self):
        self.conversations: Dict[int, List[Dict]] = {}
    
    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to the conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })
    
    def get_history(self, user_id: int) -> List[Dict]:
        """Get the full conversation history for a user"""
        return self.conversations.get(user_id, [])
    
    def clear_history(self, user_id: int):
        """Clear the conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]
    
    def has_history(self, user_id: int) -> bool:
        """Check if user has any conversation history"""
        return user_id in self.conversations and len(self.conversations[user_id]) > 0


# Initialize dialogue manager
dialogue_manager = DialogueManager()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    
    # Clear conversation history
    dialogue_manager.clear_history(user_id)
    
    welcome_text = (
        "Привет! 👋\n\n"
        "Я бот, который использует ChatGPT для ответов на ваши вопросы.\n\n"
        "Команды:\n"
        "/start - начать новый диалог\n"
        "/help - получить помощь\n\n"
        "Просто напишите мне вопрос, и я помогу вам! 🚀"
    )
    
    keyboard = [
        ["Новый запрос"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 Справка по использованию бота:\n\n"
        "1️⃣ Просто напишите ваш вопрос или сообщение\n"
        "2️⃣ Бот обратится к ChatGPT и предоставит ответ\n"
        "3️⃣ Ваша история диалога сохраняется для лучшего контекста\n"
        "4️⃣ Нажмите 'Новый запрос' чтобы начать новый диалог\n"
        "5️⃣ Используйте /start для перезагрузки бота\n\n"
        "💡 Советы:\n"
        "• Чем более подробный вопрос, тем лучше ответ\n"
        "• Бот помнит контекст предыдущих сообщений\n"
        "• Используйте 'Новый запрос' для смены темы"
    )
    
    await update.message.reply_text(help_text)


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Новый запрос' button click"""
    user_id = update.effective_user.id
    dialogue_manager.clear_history(user_id)
    
    await update.message.reply_text(
        "✅ Контекст диалога очищен! Теперь я слушаю ваш новый запрос. 👂"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages and get response from ChatGPT"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Check if this is the reset button
    if user_message == "Новый запрос":
        await reset_context(update, context)
        return
    
    try:
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Add user message to history
        dialogue_manager.add_message(user_id, "user", user_message)
        
        # Get conversation history
        messages = dialogue_manager.get_history(user_id)
        
        # Call OpenAI API
        logger.info(f"Sending request to OpenAI for user {user_id}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract assistant response
        assistant_message = response.choices[0].message.content
        
        # Add assistant response to history
        dialogue_manager.add_message(user_id, "assistant", assistant_message)
        
        # Send response to user
        await update.message.reply_text(assistant_message)
        
        logger.info(f"Response sent to user {user_id}")
        
    except openai.error.AuthenticationError:
        error_msg = "❌ Ошибка аутентификации. Проверьте API ключ OpenAI."
        logger.error(error_msg)
        await update.message.reply_text(error_msg)
    
    except openai.error.RateLimitError:
        error_msg = "⏳ Превышено ограничение на количество запросов. Попробуйте позже."
        logger.error("Rate limit exceeded")
        await update.message.reply_text(error_msg)
    
    except Exception as e:
        error_msg = f"❌ Произошла ошибка: {str(e)}"
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text(error_msg)


async def main() -> None:
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    logger.info("Starting bot...")
    await application.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
