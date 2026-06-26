import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

from downloader import download_video, download_audio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Simple in-memory store: chat_id -> URL
user_urls: dict[int, str] = {}


def format_choice_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Build inline keyboard with Video and Audio buttons."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🎬 Video", callback_data=f"dl:{chat_id}:video"
        ),
        InlineKeyboardButton(
            text="🎵 Audio", callback_data=f"dl:{chat_id}:audio"
        ),
    )
    return builder.as_markup()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.reply("Send me a reel/video link")


@dp.message()
async def handle_url(message: types.Message):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        await message.reply("Please send a valid URL")
        return

    chat_id = message.chat.id
    user_urls[chat_id] = url

    await message.reply(
        "Choose format:",
        reply_markup=format_choice_keyboard(chat_id),
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("dl:"))
async def handle_format_choice(callback: CallbackQuery):
    """Handle inline button clicks for Video or Audio download."""
    if not callback.data:
        return

    parts = callback.data.split(":")
    if len(parts) != 3:
        return

    _, chat_id_str, fmt = parts
    callback_chat_id = int(chat_id_str)

    if callback.from_user.id != callback_chat_id:
        await callback.answer("This is not your download request!", show_alert=True)
        return

    url = user_urls.get(callback_chat_id)
    if not url:
        await callback.message.edit_text("URL expired. Please send a new link.")
        return

    await callback.answer()
    await callback.message.edit_text("Downloading...")

    try:
        if fmt == "video":
            file_path = download_video(url)
        else:
            file_path = download_audio(url)

        if file_path is None:
            await callback.message.edit_text("Failed to download the media")
            return

        await callback.message.edit_text("Uploading...")

        with open(file_path, "rb") as f:
            data = f.read()

        if fmt == "video":
            await callback.message.reply_video(
                video=types.BufferedInputFile(data, filename=os.path.basename(file_path))
            )
        else:
            await callback.message.reply_audio(
                audio=types.BufferedInputFile(data, filename=os.path.basename(file_path))
            )

        os.remove(file_path)
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text(f"Error: {e}")

    finally:
        # Clean up stored URL
        user_urls.pop(callback_chat_id, None)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())