import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

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
    def __init__(self, base_url: str = "https://en.wikipedia.org"):
        self.base_url = base_url
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
        # Skip fragments, mailto, javascript, etc.
        if not href:
            return False
        if href.startswith("#"):
            return False
        if href.startswith("mailto:") or href.startswith("javascript:"):
            return False

        # Wikipedia-specific filters
        # Only internal wiki links
        if href.startswith("/wiki/") or href.startswith("https://en.wikipedia.org/wiki/"):
            # Skip special namespaces like Help:, File:, Talk:, etc.
            if any(ns in href for ns in [":", "Main_Page"]):
                return False
            return True

        return False

    def get_links(self, url: str) -> List[Link]:
        html = self.get_html(url)
        if not html:
            logger.warning("Empty HTML. No links extracted.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        links: List[Link] = []

        logger.info("Extracting links from page...")

        for tag in soup.find_all("a"):
            href = tag.get("href")
            if not self._is_useful_href(href):
                continue

            text = tag.get_text(strip=True) or ""
            # Build absolute URL
            abs_url = urljoin(self.base_url, href)

            links.append(Link(text=text, url=abs_url))

        logger.info(f"Total useful links extracted: {len(links)}")
        return links
