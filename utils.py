"""
Advanced utilities for ChatGPT Telegram Bot
"""

from typing import List, Dict
from datetime import datetime


class MessageFormatter:
    """Formats messages for display"""
    
    @staticmethod
    def format_history(messages: List[Dict[str, str]]) -> str:
        """
        Format conversation history for display
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted string representation of history
        """
        if not messages:
            return "История диалога пуста."
        
        formatted_lines = ["📋 История диалога:\n"]
        for i, msg in enumerate(messages, 1):
            role = "👤 Вы" if msg["role"] == "user" else "🤖 Бот"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            formatted_lines.append(f"{i}. {role}: {content}")
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def format_error(error_type: str, message: str = "") -> str:
        """
        Format error message for display
        
        Args:
            error_type: Type of error
            message: Additional message
            
        Returns:
            Formatted error message
        """
        error_messages = {
            "auth_error": "❌ Ошибка аутентификации. Проверьте API ключ OpenAI.",
            "rate_limit": "⏳ Превышено ограничение на количество запросов. Попробуйте позже.",
            "connection_error": "🌐 Ошибка подключения. Проверьте интернет-соединение.",
            "general_error": f"❌ Произошла ошибка: {message}",
        }
        return error_messages.get(error_type, "❌ Неизвестная ошибка.")
    
    @staticmethod
    def format_welcome() -> str:
        """Format welcome message"""
        return (
            "Привет! 👋\n\n"
            "Я бот, который использует ChatGPT для ответов на ваши вопросы.\n\n"
            "Команды:\n"
            "/start - начать новый диалог\n"
            "/help - получить помощь\n"
            "/history - показать историю диалога\n\n"
            "Просто напишите мне вопрос, и я помогу вам! 🚀"
        )
    
    @staticmethod
    def format_help() -> str:
        """Format help message"""
        return (
            "📚 Справка по использованию бота:\n\n"
            "1️⃣ Просто напишите ваш вопрос или сообщение\n"
            "2️⃣ Бот обратится к ChatGPT и предоставит ответ\n"
            "3️⃣ Ваша история диалога сохраняется для лучшего контекста\n"
            "4️⃣ Нажмите 'Новый запрос' чтобы начать новый диалог\n"
            "5️⃣ Используйте /start для перезагрузки бота\n"
            "6️⃣ Используйте /history для просмотра истории\n\n"
            "💡 Советы:\n"
            "• Чем более подробный вопрос, тем лучше ответ\n"
            "• Бот помнит контекст предыдущих сообщений\n"
            "• Используйте 'Новый запрос' для смены темы"
        )


class ValidationUtils:
    """Utilities for input validation"""
    
    @staticmethod
    def is_valid_message(text: str, max_length: int = 2000) -> bool:
        """
        Validate user message
        
        Args:
            text: Message text
            max_length: Maximum message length
            
        Returns:
            True if message is valid
        """
        if not text or not text.strip():
            return False
        
        if len(text) > max_length:
            return False
        
        return True
    
    @staticmethod
    def get_validation_error(text: str, max_length: int = 2000) -> str:
        """
        Get validation error message
        
        Args:
            text: Message text
            max_length: Maximum message length
            
        Returns:
            Error message if validation fails
        """
        if not text or not text.strip():
            return "❌ Сообщение не может быть пустым."
        
        if len(text) > max_length:
            return f"❌ Сообщение слишком длинное. Максимум {max_length} символов."
        
        return ""


class UserSession:
    """Manages user session information"""
    
    def __init__(self, user_id: int, username: str = ""):
        self.user_id = user_id
        self.username = username
        self.created_at = datetime.now()
        self.last_message_at = None
        self.message_count = 0
    
    def update_activity(self):
        """Update last message timestamp and increment counter"""
        self.last_message_at = datetime.now()
        self.message_count += 1
    
    def get_session_info(self) -> Dict:
        """Get session information"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at,
            "last_message_at": self.last_message_at,
            "message_count": self.message_count,
        }
