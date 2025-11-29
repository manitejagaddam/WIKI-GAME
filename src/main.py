import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import threading
from get_similar_word import GetSimilarWord
from scapper import Scrapper
from fetch_target_summary import fetch_wikipedia_summary
from engine import WikipediaGame

import logging
from dataclasses import dataclass
from run_thread import run_game_thread_context, run_game_thread_title




def main():

    # target_title = "England"
    target_title = "Bhupalpally"

    target_context, target_lang = fetch_wikipedia_summary(target_title, 200)
    start_url = f"https://{target_lang}.wikipedia.org/wiki/India"
    print("target_lang =", target_lang)
    print(f"target_context: {target_context}")

    results = []
    stop_event = threading.Event()

    thread_title = threading.Thread(
        target=run_game_thread_title,
        args=("Title-Based", start_url, target_title, target_lang, results, stop_event)
    )

    thread_context = threading.Thread(
        target=run_game_thread_context,
        args=("Context-Based", start_url, target_title, target_context, target_lang, results, stop_event)
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
