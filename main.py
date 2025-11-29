import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

import numpy as np
from sentence_transformers import SentenceTransformer


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
        try:
            res = self.session.get(url, timeout=10)
            res.raise_for_status()
            return res.text
        except requests.exceptions.RequestException as e:
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
            return []

        soup = BeautifulSoup(html, "html.parser")
        links: List[Link] = []


        for tag in soup.find_all("a"):
            href = tag.get("href")
            if not self._is_useful_href(href):
                continue

            text = tag.get_text(strip=True) or ""
            # Build absolute URL
            abs_url = urljoin(self.base_url, href)

            links.append(Link(text=text, url=abs_url))

        return links


# -----------------------
# Similarity Engine
# -----------------------
class GetSimilarWord:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_similar_link(self, query: str, links: List[Link]) -> Tuple[Optional[Link], Optional[float]]:
        if not links:
            return None, None

        # Filter out completely empty texts
        clean_links = [link for link in links if link.text and link.text.strip()]
        if not clean_links:
            return None, None

        texts = [link.text for link in clean_links]

        query_emb = self.model.encode([query])          # shape: (1, D)
        link_embs = self.model.encode(texts)            # shape: (N, D)

        # Cosine similarity via dot product (embeddings are normalized by default for this model)
        similarities = np.dot(link_embs, query_emb.T).flatten()

        best_idx = int(np.argmax(similarities))
        best_link = clean_links[best_idx]
        best_score = float(similarities[best_idx])

        return best_link, best_score


# -----------------------
# Wikipedia Game Engine
# -----------------------
class WikipediaGame:
    def __init__(
        self,
        scraper: Scrapper,
        selector: GetSimilarWord,
        max_steps: int = 20,
        similarity_threshold: float = 0.85,
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
        title = parsed.path.split("/wiki/")[-1]
        return title.replace("_", " ")

    # -----------------------------
    # SEMANTIC GREEDY NAVIGATION
    # -----------------------------
    def play(self, start_url: str, target: str):
        current_url = self._canonical_url(start_url)
        path = []

        for step in range(self.max_steps):
            title = self._title_from_url(current_url)
            path.append((title, current_url))

            print(f"\nSTEP {step+1}: {title} -> {current_url}")

            # Stop if title equals target
            if title.lower() == target.lower():
                print("Reached exact target page.")
                return path

            # 1. SCRAPE CURRENT PAGE — fresh on every loop
            links = self.scraper.get_links(current_url)
            if not links:
                print("No links -> Dead end. Stopping.")
                return path

            # 2. PREPARE TEXTS
            valid_links = [l for l in links if l.text.strip()]
            if not valid_links:
                print("No valid links -> Dead end.")
                return path

            texts = [l.text for l in valid_links]

            # 3. FRESH SIMILARITY CALCULATION ON THIS PAGE
            query_emb = self.selector.model.encode([target])
            link_embs = self.selector.model.encode(texts)

            sims = np.dot(link_embs, query_emb.T).flatten()

            best_idx = int(np.argmax(sims))
            best_link = valid_links[best_idx]
            best_score = float(sims[best_idx])

            print(f"Best match on page: {best_link.text} ({best_score:.4f})")

            # Stop if similarity strong
            if best_score >= self.similarity_threshold:
                print("High semantic match reached — stopping.")
                path.append((best_link.text, best_link.url))
                return path

            # 4. MOVE TO NEXT PAGE
            current_url = self._canonical_url(best_link.url)

        print("Max steps reached.")
        return path


# -----------------------
# Main entry
# -----------------------
def main():
    # Example: from Narendra Modi page to something like "New Delhi"
    start_url = "https://en.wikipedia.org/wiki/India"
    target_text = "Sundar Pichai"

    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(scraper, selector, max_steps=10, similarity_threshold=0.85)

    path = game.play(start_url, target_text)

    print("\nFinal Path:")
    for i, (title, url) in enumerate(path, start=1):
        print(f"{i}. {title} -> {url}")


if __name__ == "__main__":
    main()
