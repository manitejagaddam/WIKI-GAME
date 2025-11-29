import streamlit as st
from scapper import Scrapper
from get_similar_word import GetSimilarWord
from engine import WikipediaGame

st.set_page_config(
    page_title="Wikipedia Navigator",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Wikipedia Greedy Navigator")
st.write("Navigate from one Wikipedia page to another using similarity search (no DFS).")

# ------------------------------
# USER INPUTS
# ------------------------------
start_url = st.text_input(
    "Start Wikipedia URL:",
    "https://en.wikipedia.org/wiki/Parul_University"
)

target_text = st.text_input(
    "Target Word / Page Title:",
    "Nick Vujicic"
)

max_steps = st.slider("Max Steps:", 1, 200, 50)
threshold = st.slider("Similarity Threshold:", 0.0, 1.0, 0.20)

start_button = st.button("🚀 Start Navigation")

# ------------------------------
# RUN
# ------------------------------
if start_button:
    if not start_url.strip() or not target_text.strip():
        st.error("Please enter both Start URL and Target Target Word.")
        st.stop()

    st.info("Loading models & scraper... please wait...")

    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(scraper, selector, max_steps=max_steps, similarity_threshold=threshold)

    st.success("Navigation Started...")

    # RUN GAME
    path = game.play(start_url, target_text)

    # DISPLAY PATH
    st.subheader("🧭 Navigation Path")

    for i, (title, url) in enumerate(path, start=1):
        st.markdown(f"**{i}. [{title}]({url})**")

    # LAST STATUS
    if path and path[-1][0].lower() == target_text.lower():
        st.success("🎯 Successfully reached the target page!")
    else:
        st.warning("⚠ Could not reach the target page. Showing partial path.")
