# ChatGPT Telegram Bot

Простой Telegram бот, который интегрируется с ChatGPT для генерации ответов с поддержкой прокси для обхода блокировок.

## Возможности

- Команды `/start` и `/help`
- Ответы на текстовые сообщения через ChatGPT API
- Сохранение истории диалогов
- Использование контекста предыдущих сообщений
- Кнопка "Новый запрос" для сброса контекста
- Поддержка прокси для обхода блокировок OpenAI

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

4. Отредактируйте `.env` и добавьте свои API ключи:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_PROXY=http://your-proxy:port  # Необязательно, для обхода блокировок
```

### Настройка прокси (если нужно)

Если вы находитесь в РФ или другой стране с блокировками OpenAI:

**Для HTTP прокси:**
```
OPENAI_PROXY=http://127.0.0.1:7890
```

**Для SOCKS5 прокси (рекомендуется):**
```
OPENAI_PROXY=socks5://127.0.0.1:1080
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
- OpenAI API Key (получить на https://platform.openai.com/api-keys)
- Прокси (опционально) для обхода блокировок OpenAI

## Поиск прокси

Рекомендуемые прокси-сервисы:
- VLESS/V2Ray (уже используется в вашем VPN)
- SOCKS5 прокси от провайдеров VPN
- Платные HTTP/SOCKS5 прокси сервисы