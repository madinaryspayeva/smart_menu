import os
import tempfile

import yt_dlp
from faster_whisper import WhisperModel

from api.v1.recipe.dto.recipe_dto import RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeParserService


class VideoParserService(IRecipeParserService):
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

    def parse(self, url:str) -> RecipeDTO:
        """
        Основной метод - парсит видео по URL
        """

        audio_path, description, thumbnail = self._extract_audio_and_description(url)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            transcript =  self._transcribe_audio(audio_path)
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        return RecipeDTO(
            title="Без названия",
            description=f"{description} {transcript}",
            meal_type=None,
            ingredients=[],
            steps=[],
            tips=None,
            thumbnail=thumbnail
        )
    
    def _extract_audio_and_description(self, url:str) -> str:
        """
        Извлекает аудио и описание из видео
        """

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            description = info.get("description", "") or ""
            thumbnail = info.get("thumbnail", "")

            if "requested_downloads" in info:
                audio_path = info["requested_downloads"][0]["filepath"]
            else:
                downloaded_file = ydl.prepare_filename(info)
                audio_path = os.path.splitext(downloaded_file)[0] + ".mp3" 
           
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
