# Telegram Video Downloader Bot

A simple Telegram bot that downloads videos/reels from Instagram, TikTok, YouTube Shorts, and other platforms — built with **Python**, **Aiogram 3**, **yt-dlp**, and **Docker**.

## What We've Built

This project is a working MVP (Minimum Viable Product) that:

1. **Receives a video/reel URL** from a user on Telegram
2. **Downloads the video** using yt-dlp
3. **Sends the video file** back to the user
4. **Cleans up** — deletes the file from the server after sending

No database, no Redis, no rate limiting — just a simple, modular downloader bot.

---

## Project Structure

```
telegram-downloader-bot/
│── bot.py              # Telegram bot logic (Aiogram 3.x)
│── downloader.py       # Video download logic (yt-dlp)
│── requirements.txt    # Python dependencies
│── Dockerfile          # Docker build instructions
│── docker-compose.yml  # Docker Compose configuration
│── .env                # Environment variables (BOT_TOKEN)
│── downloads/          # Temporary download directory
│── README.md           # This file
```

---

## File-by-File Breakdown

### `bot.py` — Telegram Bot

- Uses **Aiogram 3.x** (`Bot`, `Dispatcher`, `Command` filter)
- **`/start` command** → replies with "Send me a reel/video link"
- **Message handler** for any text:
  - Validates the URL (must start with `http://` or `https://`)
  - Calls `downloader.download_video(url)` to download
  - Sends the video back using `reply_video()` with `BufferedInputFile`
  - Deletes the local file after sending
  - Sends error messages on failure
- Simple long-polling setup — no webhooks

### `downloader.py` — Download Engine

- Single function: `download_video(url: str) -> str | None`
- Uses **yt-dlp** with these options:
  ```python
  opts = {
      "format": "best",
      "outtmpl": "downloads/%(id)s.%(ext)s",
      "quiet": True,
      "no_warnings": True,
  }
  ```
- Downloads the best quality video to the `downloads/` folder
- Handles cases where yt-dlp changes the file extension
- Returns the file path on success, `None` on failure

### `requirements.txt`

```
aiogram>=3.0.0
yt-dlp>=2024.0.0
python-dotenv>=1.0.0
```

### `Dockerfile`

- Base image: `python:3.11-slim`
- Installs **ffmpeg** (required by yt-dlp for some format conversions)
- Installs Python dependencies from `requirements.txt`
- Copies `bot.py` and `downloader.py` into the container
- Creates the `downloads/` directory
- Runs `python bot.py` on container start

### `docker-compose.yml`

- Single service: `bot`
- Builds from the current directory
- Mounts `./downloads:/app/downloads` as a volume (so downloaded files persist on the host)
- Loads environment variables from `.env`

### `.env`

```
BOT_TOKEN=your_telegram_bot_token
```

Replace `your_telegram_bot_token` with your actual bot token from [@BotFather](https://t.me/BotFather).

---

## How to Run

### Prerequisites

- **Docker** and **Docker Compose** installed on your system

### Steps

1. **Clone or navigate** to the project directory:
   ```bash
   cd telegram-downloader-bot
   ```

2. **Set your bot token** in `.env`:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrstUVwxyz
   ```
   (Get a token from [@BotFather](https://t.me/BotFather) on Telegram)

3. **Build and start** the container:
   ```bash
   docker compose up --build
   ```

4. **Open Telegram**, find your bot, and send `/start`

5. **Send a video/reel URL** — the bot will download it and send it back!

---

## Supported Platforms

- **Instagram Reels**
- **TikTok videos**
- **YouTube Shorts**
- Any other platform supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

## Design Principles

- **Simple** — no unnecessary complexity
- **Modular** — bot logic and download logic are separated
- **Stateless** — no database, no Redis, no persistent state
- **Clean** — files are deleted after sending
- **Containerized** — runs anywhere Docker is available

---

## Future Ideas (Not Implemented)

- Support for playlists / multiple videos
- Audio-only extraction
- Custom quality selection
- Rate limiting
- Advanced logging
- User analytics