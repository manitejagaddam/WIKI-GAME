from get_similar_word import GetSimilarWord

from scapper import Scrapper
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

import numpy as np
from sentence_transformers import SentenceTransformer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class Link:
    text: str
    url: str



class WikipediaGame:
    def __init__(
        self,
        scraper: Scrapper,
        selector: GetSimilarWord,
        max_depth: int = 5,
        similarity_threshold: float = 0.85,
    ):
        self.scraper = scraper
        self.selector = selector
        self.max_depth = max_depth
        self.similarity_threshold = similarity_threshold
        self.visited = set()

    def _canonical_url(self, url: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    def _title_from_url(self, url: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if not parsed.path.startswith("/wiki/"):
            return url
        title = parsed.path.split("/wiki/")[-1]
        return title.replace("_", " ")

    # ===========================
    # MAIN DFS WITH BACKTRACKING
    # ===========================
    def dfs(self, current_url: str, target: str, depth: int, path: List[Tuple[str, str]]):
        current_url = self._canonical_url(current_url)
        current_title = self._title_from_url(current_url)

        logger.info(f"{'  '*depth}Exploring: {current_title} ({current_url}) Depth={depth}")

        # Stop looping on revisits
        if current_url in self.visited:
            logger.info(f"{'  '*depth}Already visited. Backtracking...")
            return False
        
        self.visited.add(current_url)
        path.append((current_title, current_url))

        # Check if we reached the target
        if current_title.lower() == target.lower():
            logger.info(f"{'  '*depth}Reached target page: {current_title}")
            return True

        if depth >= self.max_depth:
            logger.info(f"{'  '*depth}Max depth reached. Backtracking...")
            path.pop()
            return False

        # Get links from this page
        links = self.scraper.get_links(current_url)
        if not links:
            logger.info(f"{'  '*depth}No links found. Backtracking...")
            path.pop()
            return False

        # Rank the links by similarity
        ranked: List[Tuple[float, Link]] = []
        for link in links:
            if not link.text.strip():
                continue
            _, score = self.selector.get_similar_link(target, [link])
            ranked.append((score, link))

        ranked.sort(reverse=True, key=lambda x: x[0])  # Best first

        # Try each link in descending similarity
        for score, link in ranked:
            if score >= self.similarity_threshold:
                logger.info(f"{'  '*depth}High similarity: {score:.4f} -> Trying {link.text}")

            if self.dfs(link.url, target, depth + 1, path):
                return True

        # If none worked → backtrack
        logger.info(f"{'  '*depth}All links exhausted for {current_title}. Backtracking...")
        path.pop()
        return False

    # PUBLIC METHOD
    def play(self, start_url: str, target: str):
        path = []
        found = self.dfs(start_url, target, 0, path)

        if not found:
            logger.info("Did not reach the target. Partial path shown:")
        else:
            logger.info("Successfully reached target!")

        return path
