import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import openai

from config import Config, setup_logging
from dialogue_manager import DialogueManager
from chatgpt_client import ChatGPTClient
from utils import MessageFormatter, ValidationUtils

# Setup logging
logger = setup_logging()

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise

# Initialize dialogue manager and ChatGPT client
dialogue_manager = DialogueManager()
chatgpt_client = ChatGPTClient()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    
    # Clear conversation history
    dialogue_manager.clear_history(user_id)
    
    keyboard = [
        ["Новый запрос"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        MessageFormatter.format_welcome(),
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(MessageFormatter.format_help())


async def help_command_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command"""
    user_id = update.effective_user.id
    messages = dialogue_manager.get_history(user_id)
    
    history_text = MessageFormatter.format_history(messages)
    await update.message.reply_text(history_text)


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Новый запрос' button click"""
    user_id = update.effective_user.id
    dialogue_manager.clear_history(user_id)
    
    await update.message.reply_text(
        "Контекст диалога очищен! Теперь я слушаю ваш новый запрос."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages and get response from ChatGPT"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Check if this is the reset button
    if user_message == "Новый запрос":
        await reset_context(update, context)
        return
    
    # Validate message
    if not ValidationUtils.is_valid_message(user_message):
        error = ValidationUtils.get_validation_error(user_message)
        await update.message.reply_text(error)
        return
    
    try:
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Add user message to history
        dialogue_manager.add_message(user_id, "user", user_message)
        
        # Get conversation history
        messages = dialogue_manager.get_history(user_id)
        
        # Call ChatGPT
        logger.info(f"Sending request to ChatGPT for user {user_id}")
        assistant_message = await chatgpt_client.get_response(messages)
        
        # Add assistant response to history
        dialogue_manager.add_message(user_id, "assistant", assistant_message)
        
        # Send response to user
        await update.message.reply_text(assistant_message)
        
        logger.info(f"Response sent to user {user_id}")
        
    except openai.AuthenticationError:
        error_msg = MessageFormatter.format_error("auth_error")
        logger.error(error_msg)
        await update.message.reply_text(error_msg)
    
    except openai.RateLimitError:
        error_msg = MessageFormatter.format_error("rate_limit")
        logger.error("Rate limit exceeded")
        await update.message.reply_text(error_msg)
    
    except Exception as e:
        error_msg = MessageFormatter.format_error("general_error", str(e))
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text(error_msg)


def main() -> None:
    """Start bot"""
    # Create the Application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", help_command_history))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    logger.info("Starting bot...")
    logger.info(f"Using model: {Config.OPENAI_MODEL}")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
