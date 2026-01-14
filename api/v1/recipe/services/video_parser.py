import yt_dlp
import os
import tempfile



class VideoParserService:
    """
    Сервис для парсинга видео
    """

    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join()
        }