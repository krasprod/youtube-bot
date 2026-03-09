# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем ffmpeg, который нужен yt-dlp для обработки видео/аудио
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Создаем папку для загрузок
RUN mkdir -p downloads

# Команда для запуска бота
CMD ["python", "bot.py"]
