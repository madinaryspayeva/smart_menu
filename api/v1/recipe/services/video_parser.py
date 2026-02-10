import yt_dlp
import os
import tempfile
import whisper
from faster_whisper import WhisperModel


class VideoParserService:
    """
    Сервис для парсинга видео
    """

    _model = None

    def __init__(self):
        self.tmp_dir = tempfile.gettempdir()
        self.ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.tmp_dir, "%(id)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = WhisperModel(
                "small", 
                device="cpu",   #TODO for production need to change?
                compute_type="int8",
            )
        return cls._model

    def parse_video(self, url:str) -> str:
        """
        Основной метод - парсит видео по URL
        """

        audio_path, description, thumbnail = self._extract_audio_and_description(url)
        transcript =  self._transcribe_audio(audio_path)

        full_data = {
            "description":description,
            "transcript":transcript,
            "thumbnail": thumbnail,
        }
        return  full_data
    
    def _extract_audio_and_description(self, url:str) -> str:
        """
        Извлекает аудио и описание из видео
        """

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            description = info.get("description", "") or ""
            thumbnail = info.get("thumbnail", "")

            downloaded_file = ydl.prepare_filename(info)
            audio_path = os.path.splitext(downloaded_file)[0] + ".mp3" 
            # read documentation to optimize 
        return audio_path, description, thumbnail
    
    def _transcribe_audio(self, audio_path:str) -> str:
        """
        Транскрибирует аудио
        """

        model = self.get_model()
        result, _ = model.transcribe(
            audio_path,
            beam_size=1,
            vad_filter=True,
        )
        return " ".join(seg.text for seg in result)
