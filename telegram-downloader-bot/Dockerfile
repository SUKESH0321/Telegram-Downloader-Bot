FROM python:3.11-slim

# Install ffmpeg (required by yt-dlp for some formats)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py downloader.py ./

# Create downloads directory
RUN mkdir -p downloads

CMD ["python", "bot.py"]