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
        max_steps: int = 100,
        similarity_threshold: float = 0.40
    ):
        self.scraper = scraper
        self.selector = selector
        self.max_steps = max_steps
        self.similarity_threshold = similarity_threshold
        self.seen = set()

    def _canonical_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    def _title_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        if not parsed.path.startswith("/wiki/"):
            return url
        return parsed.path.split("/wiki/")[-1].replace("_", " ")
    
    def play_stepwise(self, start_url: str, target: str):
        current_url = self._canonical_url(start_url)

        for step in range(self.max_steps):
            title = self._title_from_url(current_url)
            yield (title, current_url)

            if title.lower() == target.lower():
                return

            best_link, score = self._get_best_next_link(current_url, target)
            if not best_link:
                return

            current_url = self._canonical_url(best_link.url)

    def play_stepwise(self, start_url: str, target_title: str, target_context: str):
        current_url = self._canonical_url(start_url)

        for step in range(self.max_steps):
            title = self._title_from_url(current_url)

            # Yield step so thread can stop early
            yield (title, current_url)

            # STOP CONDITION (title match, not context match)
            if title.lower() == target_title.lower():
                return

            # Find best next link using CONTEXT for similarity
            best_link, score = self._get_best_next_link(current_url, target_context)

            if not best_link:
                return

            current_url = self._canonical_url(best_link.url)



    # ================================================================
    # 🔥 Greedy Step-by-Step Wikipedia Navigation (NO DFS)
    # ================================================================
    def _get_best_next_link(self, current_url: str, target: str):
        links = self.scraper.get_links(current_url)
        if not links:
            return None, None

        # Filter valid links
        clean_links = [link for link in links if link.text and link.text.strip()]
        if not clean_links:
            return None, None

        texts = [link.text for link in clean_links]
        # print(texts)

        # Encode target once
        query_emb = self.selector.model.encode([target])

        # Encode all link texts at once
        link_embs = self.selector.model.encode(texts)

        similarities = np.dot(link_embs, query_emb.T).flatten()

        # Mask visited URLs
        for i, link in enumerate(clean_links):
            if link.url in self.seen:
                similarities[i] = -9999  # effectively remove it from competition

        # Get best remaining link
        best_idx = int(np.argmax(similarities))
        best_link = clean_links[best_idx]
        best_score = float(similarities[best_idx])

        # Mark visited
        self.seen.add(best_link.url)

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
