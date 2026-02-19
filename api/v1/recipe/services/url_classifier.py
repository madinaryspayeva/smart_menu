from dataclasses import dataclass
from urllib.parse import urlparse

import requests

from recipe.choices import ContentType, Domain, Source


@dataclass(frozen=True)
class UrlInfo:
    source: Source
    content_type: ContentType
    final_url: str
    domain: str


class UrlClassifier:
    """
    Сервис для определения источника URL
    """

    REQUEST_TIMEOUT = 5
    REDIRECT_DOMAINS = {
        "vm.tiktok.com",
        "vt.tiktok.com",
        "l.instagram.com",
    }

    def classify(self, url: str) -> UrlInfo:
        if not url or not isinstance(url, str):
            return self._unknown(url)
        
        final_url = self._resolve_redirects(url)
        parsed = urlparse(final_url)

        domain = self._normalize_domain(parsed.netloc)
        path = parsed.path or ""

        if domain.endswith(Domain.INSTAGRAM.value):
            return self._instagram(final_url, domain, path)
        
        if domain.endswith(Domain.TIKTOK.value):
            return UrlInfo(
                source=Source.TIKTOK,
                content_type=ContentType.TIKTOK_VIDEO,
                final_url=final_url,
                domain=domain,
            )
        
        if domain.endswith(("youtube.com", "youtu.be")):
            return self._youtube(final_url, domain, path)
        
        return UrlInfo(
            source=Source.WEBSITE,
            content_type=ContentType.ARTICLE_OR_RECIPE,
            final_url=final_url,
            domain=domain,
        )

    def _resolve_redirects(self, url: str) -> str:
        domain = self._normalize_domain(urlparse(url).netloc)

        if domain not in self.REDIRECT_DOMAINS:
            return url
        
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=self.REQUEST_TIMEOUT,
            )
            return response.url
        except requests.RequestException:
            return url

    @staticmethod
    def _normalize_domain(domain: str):
        domain = domain.lower()
        if domain.startswith("www."):
            domain = domain[4:]  
        return domain

    @staticmethod
    def _unknown(url: str) -> UrlInfo:
        return UrlInfo(
            source=Source.UNKNOWN,
            content_type=ContentType.UNKNOWN,
            final_url=url or "",
            domain="",
        )

    def _instagram(self, url: str, domain: str, path: str) -> UrlInfo:
        if path.startswith("/reel/"):
            ctype = ContentType.INSTAGRAM_REEL
        elif path.startswith("/p/"):
            ctype = ContentType.INSTAGRAM_POST
        else:
            ctype = ContentType.UNKNOWN
        
        return UrlInfo(
            source=Source.INSTAGRAM,
            content_type=ctype,
            final_url=url,
            domain=domain,
        )
    
    def _youtube(self, url: str, domain:str, path: str) -> UrlInfo:
        if path.startswith("/shorts/"):
            ctype = ContentType.YOUTUBE_SHORTS
        else:
            ctype = ContentType.YOUTUBE_VIDEO
        return UrlInfo(
            source=Source.YOUTUBE,
            content_type=ctype,
            final_url=url,
            domain=domain,
        )