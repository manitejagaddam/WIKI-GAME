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
        max_steps: int = 15,
        similarity_threshold: float = 0.80
    ):
        self.scraper = scraper
        self.selector = selector
        self.max_steps = max_steps
        self.similarity_threshold = similarity_threshold

    def _canonical_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    def _title_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        if not parsed.path.startswith("/wiki/"):
            return url
        return parsed.path.split("/wiki/")[-1].replace("_", " ")

    # ================================================================
    # 🔥 Greedy Step-by-Step Wikipedia Navigation (NO DFS)
    # ================================================================
    def _get_best_next_link(self, current_url: str, target: str):
        links = self.scraper.get_links(current_url)
        if not links:
            return None, None

        best_link = None
        best_score = -1

        # Evaluate each link individually (fast)
        for link in links:
            if not link.text.strip():
                continue

            _, score = self.selector.get_similar_link(target, [link])

            if score > best_score:
                best_link = link
                best_score = score

        return best_link, best_score

    # ================================================================
    # 🔥 Main "Play" Loop (Greedy)
    # ================================================================
    def play(self, start_url: str, target: str):
        current_url = self._canonical_url(start_url)
        path = []

        logger.info(f"Starting greedy wiki navigation from {start_url} -> Target: {target}")

        for step in range(self.max_steps):
            title = self._title_from_url(current_url)
            path.append((title, current_url))

            logger.info(f"[STEP {step}] At page: {title}")

            # Check if reached target
            if title.lower() == target.lower():
                logger.info("🎯 Reached target page!")
                return path

            # Compute best next link
            best_link, score = self._get_best_next_link(current_url, target)

            if not best_link:
                logger.info("❌ No further links. Stopping.")
                return path

            if score < self.similarity_threshold:
                logger.info(f"⚠ Best similarity {score:.4f} < threshold {self.similarity_threshold}")
                logger.info("Stopping because no good next hop found.")
                return path

            logger.info(f"➡ Best match: '{best_link.text}' ({score:.4f}) → {best_link.url}")
            current_url = self._canonical_url(best_link.url)

        logger.info("⚠ Max steps reached.")
        return path
