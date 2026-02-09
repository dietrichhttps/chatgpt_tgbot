"""
Tests for the ChatGPT Telegram Bot

To run tests, use:
    python -m pytest test_bot.py -v
"""

import unittest
from unittest.mock import MagicMock, patch
from dialogue_manager import DialogueManager
from utils import MessageFormatter, ValidationUtils


class TestDialogueManager(unittest.TestCase):
    """Test cases for DialogueManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = DialogueManager()
        self.user_id = 12345
    
    def test_add_message(self):
        """Test adding messages to conversation history"""
        self.manager.add_message(self.user_id, "user", "Hello")
        self.manager.add_message(self.user_id, "assistant", "Hi there!")
        
        history = self.manager.get_history(self.user_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there!")
    
    def test_get_history_empty(self):
        """Test getting history for user with no messages"""
        history = self.manager.get_history(self.user_id)
        self.assertEqual(len(history), 0)
        self.assertEqual(history, [])
    
    def test_clear_history(self):
        """Test clearing conversation history"""
        # Add some messages
        self.manager.add_message(self.user_id, "user", "Hello")
        self.manager.add_message(self.user_id, "assistant", "Hi!")
        
        # Verify messages exist
        self.assertTrue(self.manager.has_history(self.user_id))
        self.assertEqual(self.manager.get_history_length(self.user_id), 2)
        
        # Clear history
        self.manager.clear_history(self.user_id)
        
        # Verify history is cleared
        self.assertFalse(self.manager.has_history(self.user_id))
        self.assertEqual(self.manager.get_history_length(self.user_id), 0)
    
    def test_has_history(self):
        """Test checking if user has conversation history"""
        self.assertFalse(self.manager.has_history(self.user_id))
        
        self.manager.add_message(self.user_id, "user", "Hello")
        self.assertTrue(self.manager.has_history(self.user_id))
        
        self.manager.clear_history(self.user_id)
        self.assertFalse(self.manager.has_history(self.user_id))
    
    def test_multiple_users(self):
        """Test managing conversations for multiple users"""
        user1 = 11111
        user2 = 22222
        
        self.manager.add_message(user1, "user", "Hello from user1")
        self.manager.add_message(user2, "user", "Hello from user2")
        
        history1 = self.manager.get_history(user1)
        history2 = self.manager.get_history(user2)
        
        self.assertEqual(len(history1), 1)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history1[0]["content"], "Hello from user1")
        self.assertEqual(history2[0]["content"], "Hello from user2")


class TestMessageFormatter(unittest.TestCase):
    """Test cases for MessageFormatter class"""
    
    def test_format_history_empty(self):
        """Test formatting empty history"""
        result = MessageFormatter.format_history([])
        self.assertEqual(result, "История диалога пуста.")
    
    def test_format_history_with_messages(self):
        """Test formatting history with messages"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = MessageFormatter.format_history(messages)
        
        self.assertIn("История диалога", result)
        self.assertIn("Вы", result)
        self.assertIn("Hello", result)
        self.assertIn("Бот", result)
        self.assertIn("Hi there!", result)
    
    def test_format_history_truncate_long_message(self):
        """Test that long messages are truncated in history"""
        long_message = "A" * 150
        messages = [
            {"role": "user", "content": long_message},
        ]
        result = MessageFormatter.format_history(messages)
        
        self.assertIn("...", result)
        self.assertNotIn(long_message, result)
    
    def test_format_error_auth(self):
        """Test formatting authentication error"""
        result = MessageFormatter.format_error("auth_error")
        self.assertIn("Ошибка аутентификации", result)
    
    def test_format_error_rate_limit(self):
        """Test formatting rate limit error"""
        result = MessageFormatter.format_error("rate_limit")
        self.assertIn("Превышено ограничение", result)
    
    def test_format_welcome(self):
        """Test formatting welcome message"""
        result = MessageFormatter.format_welcome()
        self.assertIn("Привет", result)
        self.assertIn("/start", result)
        self.assertIn("/help", result)
    
    def test_format_help(self):
        """Test formatting help message"""
        result = MessageFormatter.format_help()
        self.assertIn("Справка", result)
        self.assertIn("/start", result)
        self.assertIn("/help", result)


class TestValidationUtils(unittest.TestCase):
    """Test cases for ValidationUtils class"""
    
    def test_is_valid_message_empty(self):
        """Test validation of empty message"""
        self.assertFalse(ValidationUtils.is_valid_message(""))
        self.assertFalse(ValidationUtils.is_valid_message("   "))
    
    def test_is_valid_message_valid(self):
        """Test validation of valid message"""
        self.assertTrue(ValidationUtils.is_valid_message("Hello"))
        self.assertTrue(ValidationUtils.is_valid_message("How are you?"))
    
    def test_is_valid_message_too_long(self):
        """Test validation of too long message"""
        long_message = "A" * 2001
        self.assertFalse(ValidationUtils.is_valid_message(long_message, max_length=2000))
    
    def test_get_validation_error_empty(self):
        """Test validation error for empty message"""
        error = ValidationUtils.get_validation_error("")
        self.assertIn("пустым", error)
    
    def test_get_validation_error_too_long(self):
        """Test validation error for too long message"""
        long_message = "A" * 101
        error = ValidationUtils.get_validation_error(long_message, max_length=100)
        self.assertIn("слишком длинное", error)
        self.assertIn("100", error)
    
    def test_get_validation_error_valid(self):
        """Test validation error for valid message"""
        error = ValidationUtils.get_validation_error("Hello")
        self.assertEqual(error, "")


if __name__ == '__main__':
    unittest.main()
