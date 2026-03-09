# 🎬 YouTube Telegram Bot

Telegram-бот для скачивания видео с YouTube.

## Установка

### 1. Установи зависимости

```bash
pip install -r requirements.txt
```

### 2. Получи токен бота

1. Открой Telegram и найди [@BotFather](https://t.me/BotFather)
2. Отправь `/newbot`
3. Следуй инструкциям — задай имя и username бота
4. Скопируй полученный токен

### 3. Настрой переменные окружения

```bash
cp .env.example .env
```

Открой `.env` и вставь свой токен:

```
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

### 4. Запусти бота

```bash
python bot.py
```

## Использование

1. Открой своего бота в Telegram
2. Отправь `/start` для приветствия
3. Отправь ссылку на YouTube-видео
4. Бот скачает и отправит видео в чат

### Поддерживаемые ссылки

- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `https://youtu.be/dQw4w9WgXcQ`
- `https://www.youtube.com/shorts/dQw4w9WgXcQ`

## Ограничения

- ⚠️ Максимальный размер видео — **50 МБ** (ограничение Telegram)
- 🔒 Приватные и возрастные видео не поддерживаются
