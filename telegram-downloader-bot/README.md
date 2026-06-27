# Telegram Video & Audio Downloader Bot

A simple Telegram bot that downloads videos/reels **and audio** from Instagram, TikTok, YouTube Shorts, and other platforms — built with **Python**, **Aiogram 3**, **yt-dlp**, and **Docker**.

## What We've Built

This project is a working MVP (Minimum Viable Product) that:

1. **Receives a video/reel URL** from a user on Telegram
2. **Shows inline buttons** — the user chooses between Video or Audio
3. **Downloads the media** using yt-dlp (MP4 video or MP3 audio)
4. **Sends the media file** back to the user
5. **Cleans up** — deletes the file from the server after sending

No database, no Redis, no rate limiting — just a simple, modular downloader bot.

---

## User Flow

```
User: /start
Bot:  "Send me a reel/video link"

User: https://instagram.com/reel/xyz
Bot:  "Choose format:"
      [🎬 Video]  [🎵 Audio]

User clicks [🎵 Audio]
Bot:  "Downloading..." → "Uploading..." → sends MP3 file

User clicks [🎬 Video]  
Bot:  "Downloading..." → "Uploading..." → sends MP4 file
```

---

## Project Structure

```
telegram-downloader-bot/
│── bot.py              # Telegram bot logic (Aiogram 3.x)
│── downloader.py       # Video + Audio download logic (yt-dlp)
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

- Uses **Aiogram 3.x** (`Bot`, `Dispatcher`, `Command` filter, `CallbackQuery`)
- **`/start` command** → replies with "Send me a reel/video link"
- **Message handler** for any URL:
  - Validates the URL (must start with `http://` or `https://`)
  - Stores the URL temporarily in an in-memory dictionary (`user_urls`)
  - Shows **inline buttons** with two options: **🎬 Video** and **🎵 Audio**
- **Callback query handler** for button clicks:
  - Parses callback data: `dl:{chat_id}:{video|audio}`
  - **[Security]** Verifies the button clicker matches the original requester
  - Calls the appropriate download function (`download_video` or `download_audio`)
  - Sends the file back using `reply_video()` or `reply_audio()` with `BufferedInputFile`
  - Deletes the local file and status message after sending
  - Cleans up the stored URL in a `finally` block
- Simple long-polling setup — no webhooks

### `downloader.py` — Download Engine

Two functions for downloading media:

#### `download_video(url: str) -> str | None`
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
- Returns the MP4/WebM file path on success, `None` on failure

#### `download_audio(url: str) -> str | None`
- Uses **yt-dlp** with these options:
  ```python
  opts = {
      "format": "bestaudio/best",
      "outtmpl": "downloads/%(id)s.%(ext)s",
      "quiet": True,
      "no_warnings": True,
      "postprocessors": [{
          "key": "FFmpegExtractAudio",
          "preferredcodec": "mp3",
          "preferredquality": "192",
      }],
  }
  ```
- Downloads the best available audio stream
- Uses **FFmpeg** to convert it to MP3 (192 kbps)
- Returns the MP3 file path on success, `None` on failure

### `requirements.txt`

```
aiogram>=3.0.0
yt-dlp>=2024.0.0
python-dotenv>=1.0.0
```

### `Dockerfile`

- Base image: `python:3.11-slim`
- Installs **ffmpeg** (required by yt-dlp for audio extraction and some video conversions)
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

5. **Send a video/reel URL** — choose **🎬 Video** or **🎵 Audio** from the inline buttons!

---

## Supported Platforms

- **Instagram Reels**
- **TikTok videos**
- **YouTube Shorts**
- **YouTube videos** (including audio-only extraction for music)
- Any other platform supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

## Design Principles

- **Simple** — no unnecessary complexity
- **Modular** — bot logic and download logic are separated into their own files
- **Stateless** — no database, no Redis, no persistent state; URLs stored in-memory only
- **Secure** — callback data includes the user's chat ID; prevents cross-user download hijacking
- **Clean** — files are deleted after sending; stored URLs are cleaned up
- **Containerized** — runs anywhere Docker is available

---

## Future Ideas (Not Implemented)

- Playlist / carousel support (multiple videos)
- Custom quality selection (720p, 1080p, etc.)
- Rate limiting
- Advanced logging
- User stats / download history
- Web dashboard