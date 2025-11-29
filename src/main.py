# from get_similar_word import GetSimilarWord
# from fetch_target_summary import fetch_wikipedia_summary

# from scapper import Scrapper
# import logging
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from dataclasses import dataclass
# from typing import List, Optional, Tuple, Set

# import numpy as np
# from sentence_transformers import SentenceTransformer
# from engine import WikipediaGame

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# @dataclass
# class Link:
#     text: str
#     url: str



# def main():

#     # Example: from Narendra Modi page to something like "New Delhi"
#     start_url = "https://en.wikipedia.org/wiki/Parul_University"
#     target_text = "Samantha Ruth Prabhu"
#     target_context = fetch_wikipedia_summary(target_text, word_limit=100)
#     print(f"target_context : {target_context}")

#     scraper = Scrapper()
#     selector = GetSimilarWord()
#     game = WikipediaGame(scraper, selector, max_steps=100, similarity_threshold=0.20)

#     path = game.play(start_url, target_context)

#     print("\nFinal Path:")
#     for i, (title, url) in enumerate(path, start=1):
#         print(f"{i}. {title} -> {url}")


# if __name__ == "__main__":
#     main()


import threading
from get_similar_word import GetSimilarWord
from scapper import Scrapper
from fetch_target_summary import fetch_wikipedia_summary
from engine import WikipediaGame

import logging
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PathResult:
    name: str
    path: list

def run_game_thread(name, start_url, target, results_list, stop_event):
    """Thread worker with early stop support."""
    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(scraper, selector, max_steps=100, similarity_threshold=0.20)

    logger.info(f"[{name}] Starting game...")

    # GAME RUNS STEP BY STEP
    path = []

    for title, url in game.play_stepwise(start_url, target):
        if stop_event.is_set():
            logger.info(f"[{name}] Stop signal received. Exiting thread.")
            return
        
        path.append((title, url))

    # If this thread finishes first → announce winner
    if not stop_event.is_set():
        stop_event.set()        # Tell the other thread to stop
        results_list.append(PathResult(name=name, path=path))
        logger.info(f"[{name}] Completed FIRST — winner!")


def main():

    start_url = "https://en.wikipedia.org/wiki/India"
    # target_title = "England"
    target_title = "Bhupalpally"

    target_context = fetch_wikipedia_summary(target_title, 100)
    print(f"target_context: {target_context}")

    results = []
    stop_event = threading.Event()

    thread_title = threading.Thread(
        target=run_game_thread,
        args=("Title-Based", start_url, target_title, results, stop_event)
    )

    thread_context = threading.Thread(
        target=run_game_thread,
        args=("Context-Based", start_url, target_context, results, stop_event)
    )

    thread_title.start()
    thread_context.start()

    thread_title.join()
    thread_context.join()

    print("\n======================")
    print(" WINNER RESULT")
    print("======================\n")

    if results:
        winner = results[0]
        print(f"\n---- {winner.name} Path (Winner) ----")
        for i, (title, url) in enumerate(winner.path, start=1):
            print(f"{i}. {title} -> {url}")
    else:
        print("No thread completed successfully.")


if __name__ == "__main__":
    main()
