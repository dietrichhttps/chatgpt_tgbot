# Groq Telegram Bot

Telegram бот с использованием Groq Llama 3.1 для генерации ответов.

## Возможности

- Команды `/start` и `/help`
- Ответы на текстовые сообщения через Groq API
- Сохранение истории диалогов
- Использование контекста предыдущих сообщений
- Кнопка "Новый запрос" для сброса контекста

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository_url>
cd chatgpt_tgbot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env`:
```bash
cp .env.example .env
```

4. Получите Groq API ключ на https://console.groq.com/keys

5. Отредактируйте `.env` и добавьте свои API ключи:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

## Запуск

```bash
python bot.py
```

## Команды бота

- `/start` - Начать новый диалог (очищает историю)
- `/help` - Показать справку
- `Новый запрос` - Кнопка для сброса контекста

## Требования

- Python 3.8+
- Telegram Bot Token (получить от @BotFather)
- Groq API Key (бесплатно на https://console.groq.com/keys)