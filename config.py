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
_local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
FFMPEG_PATH = _local_ffmpeg if os.path.exists(_local_ffmpeg) else "ffmpeg"

# Общие настройки yt-dlp для обхода блокировок
_BASE_OPTIONS = {
    'ffmpeg_location': FFMPEG_PATH,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'player_skip': ['webpage', 'configs'],
        }
    },
}

# Настройки для скачивания видео
YTDLP_VIDEO_OPTIONS = {
    **_BASE_OPTIONS,
    'format': 'bestvideo[ext=mp4][filesize<50M]+bestaudio[ext=m4a]/best[ext=mp4][filesize<50M]/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
}

# Настройки для скачивания аудио
YTDLP_AUDIO_OPTIONS = {
    **_BASE_OPTIONS,
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
