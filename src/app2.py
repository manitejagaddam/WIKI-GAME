import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import streamlit as st
import threading
from urllib.parse import urlparse

from scapper import Scrapper
from get_similar_word import GetSimilarWord
from engine import WikipediaGame
from fetch_target_summary import fetch_wikipedia_summary
from run_thread import run_game_thread_title, run_game_thread_context




# --------------------------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Wikipedia Race Navigator",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Wikipedia Greedy Navigator — Multithreaded Race Mode")
st.write("Two threads race: **Title-Based** vs **Context-Based** similarity.")


# --------------------------------------------------------------------
# USER INPUTS
# --------------------------------------------------------------------
start_url = st.text_input(
    "Start Wikipedia URL:",
    "https://en.wikipedia.org/wiki/India"
)

target_title = st.text_input(
    "Target Page Title:",
    "Bhupalpally"
)

word_limit = st.slider("Word Limit for Context Extraction:", 20, 200, 80)
max_steps = st.slider("Max Steps for Navigation:", 1, 200, 50)
threshold = st.slider("Similarity Threshold:", 0.0, 1.0, 0.2)

start_button = st.button("🚀 Start Multithreaded Race")


# --------------------------------------------------------------------
# CORE RACE RUNNER
# --------------------------------------------------------------------
def run_navigation_race():

    st.info("Fetching target summary and detecting language...")
    target_context, target_lang = fetch_wikipedia_summary(target_title, word_limit)

    st.write(f"**Detected Language:** `{target_lang}`")
    st.write(f"**Extracted Context:** {target_context[:300]}...")


    # Force start URL to match discovered language domain
    page_slug = start_url.split("/wiki/")[-1]
    lang_start_url = f"https://{target_lang}.wikipedia.org/wiki/{page_slug}"

    st.write(f"Using language-adapted start URL: {lang_start_url}")

    # THREAD RESULTS AND STOP FLAG
    results = []
    stop_event = threading.Event()

    # Thread 1 - Title based
    t1 = threading.Thread(
        target=run_game_thread_title,
        args=("Title-Based", lang_start_url, target_title, results, stop_event, target_lang, max_steps, threshold)
    )

    # Thread 2 - Context based
    t2 = threading.Thread(
        target=run_game_thread_context,
        args=("Context-Based", lang_start_url, target_title, target_context, results, stop_event, target_lang, max_steps, threshold)
    )

    st.write("Starting threads...")

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    st.success("Race Completed!")

    return results, target_lang, target_context



# --------------------------------------------------------------------
# UI EXECUTION
# --------------------------------------------------------------------
if start_button:

    if not start_url.strip() or not target_title.strip():
        st.error("Please provide both Start URL and Target Title.")
        st.stop()

    st.warning("⏳ Running two navigation threads in parallel...")

    results, target_lang, target_context = run_navigation_race()

    # ----------------------------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------------------------
    st.subheader("🏁 Race Result")

    if not results:
        st.error("⚠ No thread finished. Probably got stuck or both were stopped early.")
        st.stop()

    # Winner is always first appended
    winner = results[0]

    st.success(f"🏆 **Winner:** {winner.name}")

    st.markdown("### 🧭 Winning Path")
    for i, (title, url) in enumerate(winner.path, start=1):
        st.markdown(f"**{i}. [{title}]({url})**")

    # If loser exists, show it too
    if len(results) > 1:
        st.markdown("---")
        st.markdown("### 🥈 Second Thread Path")
        loser = results[1]
        for i, (title, url) in enumerate(loser.path, start=1):
            st.markdown(f"{i}. [{title}]({url})")

    st.markdown("---")
    st.markdown("### 🔍 Debug Information")
    st.write(f"**Detected language:** {target_lang}")
    st.write(f"**Target context (first 300 chars):** {target_context[:300]}...")
