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




def run_game_thread_title(name, start_url, target, results_list, stop_event):
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



def run_game_thread_context(name, start_url, target, context, results_list, stop_event):
    """Thread worker with early stop support."""
    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(scraper, selector, max_steps=70, similarity_threshold=0.20)

    logger.info(f"[{name}] Starting game...")

    # GAME RUNS STEP BY STEP
    path = []

    for title, url in game.play_stepwise(start_url, target, context):
        if stop_event.is_set():
            logger.info(f"[{name}] Stop signal received. Exiting thread.")
            return
        
        path.append((title, url))

    # If this thread finishes first → announce winner
    if not stop_event.is_set():
        stop_event.set()        # Tell the other thread to stop
        results_list.append(PathResult(name=name, path=path))
        logger.info(f"[{name}] Completed FIRST — winner!")
