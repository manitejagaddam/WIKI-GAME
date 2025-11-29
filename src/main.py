from get_similar_word import GetSimilarWord
from fetch_target_summary import fetch_wikipedia_summary

from scapper import Scrapper
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

import numpy as np
from sentence_transformers import SentenceTransformer
from engine import WikipediaGame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class Link:
    text: str
    url: str



def main():

    # Example: from Narendra Modi page to something like "New Delhi"
    start_url = "https://en.wikipedia.org/wiki/Parul_University"
    target_text = "London"
    target_context = fetch_wikipedia_summary(target_text, word_limit=100)
    print(target_context)

    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(scraper, selector, max_steps=100, similarity_threshold=0.20)

    path = game.play(start_url, target_context)

    print("\nFinal Path:")
    for i, (title, url) in enumerate(path, start=1):
        print(f"{i}. {title} -> {url}")


if __name__ == "__main__":
    main()