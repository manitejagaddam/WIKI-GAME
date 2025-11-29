import logging
import re
import numpy as np
from dataclasses import dataclass
from typing import List
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


class GetSimilarWord:
    _model = None

    def __init__(self):
        if GetSimilarWord._model is None:
            logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
            GetSimilarWord._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Model loaded.")
        else:
            logger.info("Reusing already-loaded model.")

        self.model = GetSimilarWord._model

    # ----------------------------------------------------------
    # 🔥 Remove useless / navigation / junk links
    # ----------------------------------------------------------
    def filter_links(self, links: List[Link]) -> List[Link]:
        blacklist = {
            "home", "back", "previous", "next", "login", "logout",
            "about", "contact", "terms", "privacy", "copyright",
            "<<", ">>", "»", "«"
        }

        cleaned = []
        seen = set()

        for link in links:
            if not link.text:
                continue

            text = link.text.strip().lower()

            # ❌ skip empty or extremely short text
            if len(text) <= 2:
                continue

            # ❌ skip pure symbols or non-alphabetic junk
            if not re.search(r"[a-zA-Z]", text):
                continue

            # ❌ skip blacklist matches
            if text in blacklist:
                continue

            # ❌ skip if contains navigation keywords
            if any(b in text for b in ["back", "home", "login", "previous", "next"]):
                continue

            # ❌ remove duplicates by normalized text
            if text in seen:
                continue

            seen.add(text)
            cleaned.append(link)

        return cleaned

    # ----------------------------------------------------------
    # 🔥 Compute similarity after cleaning
    # ----------------------------------------------------------
    def get_similar_link(self, query: str, links: List[Link]):
        if not links:
            logger.warning("Link list is empty.")
            return None, None

        clean_links = self.filter_links(links)

        if not clean_links:
            logger.warning("All links removed after filtering.")
            return None, None

        texts = [link.text for link in clean_links]

        logger.info(f"Encoding query and {len(texts)} cleaned links...")
        query_emb = self.model.encode([query])
        link_embs = self.model.encode(texts)

        similarities = np.dot(link_embs, query_emb.T).flatten()

        best_idx = int(np.argmax(similarities))
        best_link = clean_links[best_idx]
        best_score = float(similarities[best_idx])

        logger.info(f"Best match: '{best_link.text}' ({best_score:.4f}) -> {best_link.url}")

        return best_link, best_score
