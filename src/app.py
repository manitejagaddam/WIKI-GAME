import streamlit as st
import threading

from scapper import Scrapper
from get_similar_word import GetSimilarWord
from engine import WikipediaGame
from fetch_target_summary import fetch_wikipedia_summary
from run_thread import run_game_thread1, run_game_thread2


st.set_page_config(page_title="Wikipedia Race Navigator", page_icon="🌐", layout="wide")

st.title("🌐 Wikipedia Greedy Navigator — Multithreaded Race Mode")
st.write("Two threads race: one using Title-Based similarity & one using Context-Based similarity.")

# --------------------------------------------------------------------
# USER INPUTS
# --------------------------------------------------------------------
start_url = st.text_input(
    "Start Wikipedia URL:",
    "https://en.wikipedia.org/wiki/India"
)

target_title = st.text_input(
    "Target Page Title:",
    "London"
)

word_limit = st.slider("Word Limit for Context Extraction:", 20, 200, 80)
max_steps = st.slider("Max Steps for Navigation:", 1, 200, 50)
threshold = st.slider("Similarity Threshold:", 0.0, 1.0, 0.2)

start_button = st.button("🚀 Start Multithreaded Race")


# --------------------------------------------------------------------
# THREAD RUNNER
# --------------------------------------------------------------------
def run_navigation_race():
    st.info("Fetching target context...")
    target_context = fetch_wikipedia_summary(target_title, word_limit)

    results = []
    stop_event = threading.Event()

    # THREAD 1 — Title-based
    t1 = threading.Thread(
        target=run_game_thread1,
        args=("Title-Based", start_url, target_title, results, stop_event)
    )

    # THREAD 2 — Context-based
    t2 = threading.Thread(
        target=run_game_thread2,
        args=("Context-Based", start_url, target_context, results, stop_event)
    )

    st.write("Starting threads...")

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    st.success("Race Completed!")

    return results


# --------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------
if start_button:

    if not start_url.strip() or not target_title.strip():
        st.error("Please provide both Start URL and Target Title.")
        st.stop()

    st.warning("⏳ Running two navigation threads in parallel...")

    results = run_navigation_race()

    # --------------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------------
    st.subheader("🏁 Race Result")

    if not results:
        st.error("⚠ No thread finished. Probably got stuck.")
        st.stop()

    winner = results[0]

    st.success(f"🏆 **Winner: {winner.name} Navigation**")

    # Show winning path
    st.markdown("### 🧭 Winning Path")
    for i, (title, url) in enumerate(winner.path, start=1):
        st.markdown(f"**{i}. [{title}]({url})**")

    # Comparison info
    if len(results) > 1:
        st.markdown("### 🥈 Second Thread Result")
        loser = results[1]
        for i, (title, url) in enumerate(loser.path, start=1):
            st.markdown(f"{i}. [{title}]({url})")
