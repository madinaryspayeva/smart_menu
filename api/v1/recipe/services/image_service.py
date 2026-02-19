import os
import uuid
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile


class ImageService:
    """
    Сервис для скачивания и подготовки изображений
    """

    @staticmethod
    def download_image(url: str):
        """
        Скачивает изображение по URL, возвращает bytes и имя файла
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
            filename = f"{uuid.uuid4().hex}{ext}"

            return resp.content, filename
        
        except requests.RequestException as e:
            print(f"Error downloading image: {e}")
        
        except Exception as e:
            print(f"Unknown error downloading image: {e}")
    
        return None, None
    
    @staticmethod
    def save_image_to_model(model_instance, field_name, image_bytes, filename):
        """
        Сохраняет изображение в ImageField модели
        """

        if image_bytes:
            getattr(model_instance, field_name).save(
                filename, 
                ContentFile(image_bytes), 
                save=True
        )
