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
        similarity_threshold: float = 0.85,
    ):
        self.scraper = scraper
        self.selector = selector
        self.max_steps = max_steps
        self.similarity_threshold = similarity_threshold

    def _canonical_url(self, url: str) -> str:
        # Drop fragment and query to avoid duplicates
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    def _title_from_url(self, url: str) -> str:
        """
        Convert .../wiki/New_Delhi -> 'New Delhi'
        """
        parsed = urlparse(url)
        if not parsed.path.startswith("/wiki/"):
            return url
        title = parsed.path.split("/wiki/")[-1]
        return title.replace("_", " ")

    def play(self, start_url: str, target_text: str):
        """
        Runs the game:
        - start_url: starting Wikipedia page
        - target_text: user-provided target concept/text
        """
        logger.info(f"Starting Wikipedia Game")
        logger.info(f"Start URL: {start_url}")
        logger.info(f"Target text: '{target_text}'")

        visited: Set[str] = set()
        path = []

        current_url = self._canonical_url(start_url)

        for step in range(1, self.max_steps + 1):
            if current_url in visited:
                logger.warning(f"Already visited {current_url}. Breaking to avoid loop.")
                break

            visited.add(current_url)
            current_title = self._title_from_url(current_url)
            logger.info(f"\n--- Step {step} ---")
            logger.info(f"Current page: {current_title} ({current_url})")

            path.append((current_title, current_url))

            # Check if current page itself is already the target title
            if current_title.lower() == target_text.lower():
                logger.info("Current page title matches target text. Game finished.")
                break

            links = self.scraper.get_links(current_url)
            if not links:
                logger.warning("No links on this page. Stopping.")
                break

            best_link, score = self.selector.get_similar_link(target_text, links)
            if best_link is None:
                logger.warning("Could not find a suitable next link. Stopping.")
                break

            logger.info(f"Chose next: '{best_link.text}' ({score:.4f}) -> {best_link.url}")

            # Stop if similarity is high enough or link text matches target
            if best_link.text.lower() == target_text.lower():
                logger.info("Best link text exactly matches target. Game finished.")
                path.append((best_link.text, best_link.url))
                break

            if score >= self.similarity_threshold:
                logger.info(
                    f"Similarity {score:.4f} >= threshold {self.similarity_threshold:.2f}. "
                    f"Assuming target reached."
                )
                path.append((best_link.text, best_link.url))
                break

            # Move to next page
            current_url = self._canonical_url(best_link.url)

        logger.info("\n=== PATH TAKEN ===")
        for idx, (title, url) in enumerate(path, start=1):
            logger.info(f"{idx}. {title} -> {url}")

        return path