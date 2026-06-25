import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from downloader import download_video

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.reply("Send me a reel/video link")


@dp.message()
async def handle_url(message: types.Message):
    url = message.text.strip()

    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        await message.reply("Please send a valid URL")
        return

    status_msg = await message.reply("Downloading...")

    try:
        file_path = download_video(url)
        if file_path is None:
            await status_msg.edit_text("Failed to download the video")
            return

        await status_msg.edit_text("Uploading...")

        with open(file_path, "rb") as f:
            await message.reply_video(
                video=types.BufferedInputFile(f.read(), filename=os.path.basename(file_path))
            )

        os.remove(file_path)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"Error: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())