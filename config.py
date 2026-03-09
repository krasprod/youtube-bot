import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# YouTube Cookies (текст из cookies.txt)
YOUTUBE_COOKIES = os.getenv("YOUTUBE_COOKIES")

# Максимальный размер файла для Telegram (50 МБ)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB в байтах

# Директория для временных файлов
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

# Путь к FFmpeg
# Пытаемся использовать локальный ffmpeg (для Windows), если его нет - надеемся на системный (для Docker/Linux)
_local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
FFMPEG_PATH = _local_ffmpeg if os.path.exists(_local_ffmpeg) else "ffmpeg"

# Настройки для скачивания видео
YTDLP_VIDEO_OPTIONS = {
    **_BASE_OPTIONS,
    "format": "18/best[filesize<50M]/best",
    "merge_output_format": "mp4",
}

# Настройки для скачивания аудио (конвертация в MP3 через FFmpeg)
YTDLP_AUDIO_OPTIONS = {
    **_BASE_OPTIONS,
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}
