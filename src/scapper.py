import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Link:
    text: str
    url: str


class Scrapper:
    def __init__(self, target_lang: str = "en"):
        """
        target_lang: Wikipedia language code (en, es, hi, fr, ...)
        """
        self.target_lang = target_lang

        # Base URL switches depending on language
        self.base_url = f"https://{self.target_lang}.wikipedia.org"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def get_html(self, url: str) -> str:
        logger.info(f"Fetching URL: {url}")
        try:
            res = self.session.get(url, timeout=10)
            res.raise_for_status()
            logger.info(f"Fetched successfully ({len(res.text)} chars).")
            return res.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return ""

    def _is_useful_href(self, href: str) -> bool:
        if not href:
            return False

        # Reject bad schemes
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            return False

        # Accept ONLY links inside the target language domain
        if href.startswith("/wiki/"):
            return True

        if href.startswith(f"https://{self.target_lang}.wikipedia.org/wiki/"):
            return True

        # Reject cross-language links
        return False

    def get_links(self, url: str) -> List[Link]:
        html = self.get_html(url)
        if not html:
            logger.warning("Empty HTML. No links extracted.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        links: List[Link] = []

        logger.info("Extracting links...")

        for tag in soup.find_all("a"):
            href = tag.get("href")
            if not self._is_useful_href(href):
                continue

            text = tag.get_text(strip=True) or ""

            # Normalize to correct base_url
            abs_url = href
            if href.startswith("/wiki/"):
                abs_url = f"{self.base_url}{href}"

            links.append(Link(text=text, url=abs_url))

        logger.info(f"Total useful links extracted: {len(links)}")
        return links
