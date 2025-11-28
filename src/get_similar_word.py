import logging
import requests
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------
# Logging Setup
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------
# Data Model
# -----------------------
@dataclass
class Link:
    text: str
    url: str

class GetSimilarWord:
    _model = None  # class-level model

    def __init__(self):
        if GetSimilarWord._model is None:
            logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
            GetSimilarWord._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Model loaded.")
        else:
            logger.info("Reusing already-loaded model.")

        self.model = GetSimilarWord._model

    def get_similar_link(self, query: str, links: List[Link]):
        if not links:
            logger.warning("Link list is empty. Cannot compute similarity.")
            return None, None

        clean_links = [link for link in links if link.text and link.text.strip()]
        if not clean_links:
            logger.warning("All link texts are empty after filtering.")
            return None, None

        texts = [link.text for link in clean_links]

        logger.info(f"Encoding query and {len(texts)} link texts...")
        query_emb = self.model.encode([query])
        link_embs = self.model.encode(texts)

        similarities = np.dot(link_embs, query_emb.T).flatten()

        best_idx = int(np.argmax(similarities))
        best_link = clean_links[best_idx]
        best_score = float(similarities[best_idx])

        logger.info(f"Best match: '{best_link.text}' ({best_score:.4f}) -> {best_link.url}")
        return best_link, best_score
