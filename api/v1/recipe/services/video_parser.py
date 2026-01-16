import yt_dlp
import os
import tempfile
import whisper



class VideoParserService:
    """
    Сервис для парсинга видео
    """

    def __init__(self):
        self.tmp_dir = tempfile.gettempdir()
        self.ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.tmp_dir, "%(id)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }

    def parse_video(self, url:str) -> str:
        """
        Основной метод - парсит видео по URL
        """
        
        audio_path = self._extract_audio(url)
        return self._transcribe_audio(audio_path)
    
    def _extract_audio(self, url:str) -> str:
        """
        Извлекает аудио из видео
        """

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            downloaded_file = ydl.prepare_filename(info)
            audio_path = os.path.splitext(downloaded_file)[0] + ".mp3" 
            # read documentation to optimize 
        return audio_path
    
    def _transcribe_audio(self, audio_path:str) -> str:
        """
        Транскрибирует аудио
        """

        model = whisper.load_model("small")
        result = model.transcribe(audio_path)
        return result["text"]


