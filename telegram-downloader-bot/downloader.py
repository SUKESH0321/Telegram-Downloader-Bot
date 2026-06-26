import yt_dlp
import os


def download_video(url: str) -> str | None:
    """
    Download a video from the given URL using yt-dlp.

    Args:
        url: The video/reel URL to download.

    Returns:
        The file path of the downloaded video, or None on failure.
    """
    opts = {
        "format": "best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            # yt-dlp may change extension; find the actual file
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for f in os.listdir("downloads"):
                    if f.startswith(os.path.basename(base)):
                        file_path = os.path.join("downloads", f)
                        break
            return file_path
    except Exception as e:
        print(f"Download error: {e}")
        return None


def download_audio(url: str) -> str | None:
    """
    Download audio from a video URL using yt-dlp and convert to MP3.

    Args:
        url: The video/reel URL to extract audio from.

    Returns:
        The file path of the downloaded MP3, or None on failure.
    """
    opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # After post-processing, the file will be .mp3
            file_path = os.path.join("downloads", f"{info['id']}.mp3")
            return file_path
    except Exception as e:
        print(f"Audio download error: {e}")
        return None