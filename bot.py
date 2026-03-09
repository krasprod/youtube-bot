import asyncio
import logging
import os
import re
import glob
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

from config import (
    BOT_TOKEN, MAX_FILE_SIZE, DOWNLOAD_DIR,
    YTDLP_VIDEO_OPTIONS, YTDLP_AUDIO_OPTIONS,
    YOUTUBE_COOKIES
)

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регулярное выражение для YouTube ссылок
YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/|embed/|v/)|youtu\.be/)"
    r"[\w\-]{11}"
)


def is_youtube_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой на YouTube."""
    return bool(YOUTUBE_REGEX.search(text))


def extract_youtube_url(text: str) -> Optional[str]:
    """Извлекает YouTube URL из текста."""
    match = YOUTUBE_REGEX.search(text)
    return match.group(0) if match else None


def cleanup_files(video_id: str) -> None:
    """Удаляет все скачанные файлы по ID видео."""
    pattern = os.path.join(DOWNLOAD_DIR, f"{video_id}.*")
    for filepath in glob.glob(pattern):
        try:
            os.remove(filepath)
            logger.info(f"Удалён файл: {filepath}")
        except OSError as e:
            logger.warning(f"Не удалось удалить {filepath}: {e}")


def _prepare_cookies() -> Optional[str]:
    """Если есть переменная YOUTUBE_COOKIES, сохраняет её в файл и возвращает путь."""
    if not YOUTUBE_COOKIES:
        return None
    
    cookies_path = os.path.join(DOWNLOAD_DIR, "yt_cookies.txt")
    with open(cookies_path, "w", encoding="utf-8") as f:
        f.write(YOUTUBE_COOKIES)
    return cookies_path


def download_video(url: str) -> dict:
    """Скачивает видео с YouTube."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    info_opts = {**YTDLP_VIDEO_OPTIONS, "skip_download": True}
    dl_opts = {**YTDLP_VIDEO_OPTIONS}
    
    cookies_path = _prepare_cookies()
    if cookies_path:
        info_opts["cookiefile"] = cookies_path
        dl_opts["cookiefile"] = cookies_path

    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    video_id = info.get("id", "unknown")
    title = info.get("title", "Видео")
    duration = info.get("duration", 0)

    with yt_dlp.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])

    # Очищаем временный файл куков
    if cookies_path and os.path.exists(cookies_path):
        os.remove(cookies_path)

    pattern = os.path.join(DOWNLOAD_DIR, f"{video_id}.*")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError("Файл не найден после скачивания")

    filepath = files[0]
    file_size = os.path.getsize(filepath)

    return {
        "filepath": filepath,
        "title": title,
        "duration": duration,
        "file_size": file_size,
        "video_id": video_id,
    }


def download_audio(url: str) -> dict:
    """Скачивает аудио с YouTube."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    info_opts = {**YTDLP_AUDIO_OPTIONS, "skip_download": True}
    # Убираем postprocessors для info-запроса
    info_opts.pop("postprocessors", None)
    
    dl_opts = {**YTDLP_AUDIO_OPTIONS}
    
    cookies_path = _prepare_cookies()
    if cookies_path:
        info_opts["cookiefile"] = cookies_path
        dl_opts["cookiefile"] = cookies_path

    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    video_id = info.get("id", "unknown")
    title = info.get("title", "Аудио")
    duration = info.get("duration", 0)

    with yt_dlp.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])

    # Очищаем временный файл куков
    if cookies_path and os.path.exists(cookies_path):
        os.remove(cookies_path)

    # Ищем mp3 файл
    pattern = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError("Файл не найден после скачивания")

    filepath = files[0]
    file_size = os.path.getsize(filepath)

    return {
        "filepath": filepath,
        "title": title,
        "duration": duration,
        "file_size": file_size,
        "video_id": video_id,
    }


def format_duration(seconds: int) -> str:
    """Форматирует длительность в читаемый вид."""
    if seconds < 60:
        return f"{seconds} сек"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes} мин {secs} сек"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours} ч {mins} мин"


def format_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид."""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} КБ"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} МБ"


def make_choice_keyboard(url: str) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с выбором: видео или аудио."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Видео", callback_data=f"video|{url}"),
            InlineKeyboardButton(text="🎵 Аудио (MP3)", callback_data=f"audio|{url}"),
        ]
    ])


# ─── Обработчики ────────────────────────────────────────────


@dp.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    """Обработчик команды /start."""
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Я бот для скачивания видео и аудио с YouTube.\n\n"
        "📎 Отправь мне ссылку на видео, и выбери:\n"
        "• 🎬 <b>Видео</b> — скачать видеоролик\n"
        "• 🎵 <b>Аудио</b> — скачать только звук (MP3)\n\n"
        "⚠️ <i>Ограничение: файлы до 50 МБ</i>",
        parse_mode="HTML",
    )


@dp.message(F.text)
async def handle_message(message: types.Message) -> None:
    """Обработчик текстовых сообщений — показывает кнопки выбора."""
    url = extract_youtube_url(message.text)

    if not url:
        await message.answer(
            "🤔 Не вижу ссылку на YouTube.\n\n"
            "Отправь мне ссылку вида:\n"
            "• <code>https://youtube.com/watch?v=...</code>\n"
            "• <code>https://youtu.be/...</code>\n"
            "• <code>https://youtube.com/shorts/...</code>",
            parse_mode="HTML",
        )
        return

    if not url.startswith("http"):
        url = "https://" + url

    await message.answer(
        "🔗 Ссылка получена! Что скачать?",
        reply_markup=make_choice_keyboard(url),
    )


@dp.callback_query(F.data.startswith("video|"))
async def handle_video_download(callback: types.CallbackQuery) -> None:
    """Скачивание видео по нажатию кнопки."""
    await callback.answer()
    url = callback.data.split("|", 1)[1]

    status_msg = await callback.message.edit_text("⬇️ Скачиваю видео... ⏳")

    video_id = None
    try:
        result = await asyncio.to_thread(download_video, url)
        video_id = result["video_id"]

        if result["file_size"] > MAX_FILE_SIZE:
            size_str = format_size(result["file_size"])
            await status_msg.edit_text(
                f"❌ Видео слишком большое ({size_str}).\n"
                f"Telegram позволяет файлы до 50 МБ."
            )
            return

        await status_msg.edit_text("📤 Отправляю видео...")

        video_file = FSInputFile(result["filepath"])
        caption = (
            f"🎬 <b>{result['title']}</b>\n"
            f"⏱ {format_duration(result['duration'])} • 💾 {format_size(result['file_size'])}"
        )

        await callback.message.answer_video(
            video=video_file,
            caption=caption,
            parse_mode="HTML",
        )
        await status_msg.delete()
        logger.info(f"Видео отправлено: {result['title']} ({format_size(result['file_size'])})")

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Ошибка скачивания видео: {e}")
        await status_msg.edit_text("❌ Не удалось скачать видео. Попробуй другую ссылку.")
    except FileNotFoundError:
        await status_msg.edit_text("❌ Файл не найден после скачивания.")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await status_msg.edit_text("❌ Произошла ошибка. Попробуй позже.")
    finally:
        if video_id:
            cleanup_files(video_id)


@dp.callback_query(F.data.startswith("audio|"))
async def handle_audio_download(callback: types.CallbackQuery) -> None:
    """Скачивание аудио по нажатию кнопки."""
    await callback.answer()
    url = callback.data.split("|", 1)[1]

    status_msg = await callback.message.edit_text("🎵 Скачиваю аудио... ⏳")

    video_id = None
    try:
        result = await asyncio.to_thread(download_audio, url)
        video_id = result["video_id"]

        if result["file_size"] > MAX_FILE_SIZE:
            size_str = format_size(result["file_size"])
            await status_msg.edit_text(
                f"❌ Аудио слишком большое ({size_str}).\n"
                f"Telegram позволяет файлы до 50 МБ."
            )
            return

        await status_msg.edit_text("📤 Отправляю аудио...")

        audio_file = FSInputFile(result["filepath"])
        caption = (
            f"🎵 <b>{result['title']}</b>\n"
            f"⏱ {format_duration(result['duration'])} • 💾 {format_size(result['file_size'])}"
        )

        await callback.message.answer_audio(
            audio=audio_file,
            caption=caption,
            title=result["title"],
            duration=result["duration"],
            parse_mode="HTML",
        )
        await status_msg.delete()
        logger.info(f"Аудио отправлено: {result['title']} ({format_size(result['file_size'])})")

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Ошибка скачивания аудио: {e}")
        await status_msg.edit_text("❌ Не удалось скачать аудио. Попробуй другую ссылку.")
    except FileNotFoundError:
        await status_msg.edit_text("❌ Файл не найден после скачивания.")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await status_msg.edit_text("❌ Произошла ошибка. Попробуй позже.")
    finally:
        if video_id:
            cleanup_files(video_id)


# ─── Запуск ─────────────────────────────────────────────────


from aiohttp import web

async def handle_ping(request):
    """Простой обработчик для Fake Web Server."""
    return web.Response(text="Bot is running!")

async def main() -> None:
    """Запуск бота."""
    if not BOT_TOKEN:
        logger.error(
            "BOT_TOKEN не найден! "
            "Создай файл .env и добавь туда BOT_TOKEN=твой_токен"
        )
        return

    logger.info("🤖 Бот запускается...")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    await bot.delete_webhook(drop_pending_updates=True)
    
    # Настраиваем фейковый веб-сервер для Render.com
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    logger.info(f"🌐 Запуск веб-сервера на порту {port} (для Render)")
    await site.start()

    # Запускаем поллинг Telegram параллельно
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
