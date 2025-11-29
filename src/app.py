import streamlit as st
import threading
import time
from queue import Queue

from scapper import Scrapper
from get_similar_word import GetSimilarWord
from engine import WikipediaGame
from fetch_target_summary import fetch_wikipedia_summary


# ==============================================================
# PAGE CONFIG & GLOBAL CSS
# ==============================================================
st.set_page_config(page_title="Wiki Navigator PRO+", page_icon="🌐", layout="wide")

st.markdown(
    """
    <style>
    /* MAIN BACKGROUND */
    .main {
        background: radial-gradient(circle at top left, #232b3a 0, #0b0d14 45%, #050609 100%);
        color: #ffffff;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }

    /* BIG TITLE WITH ANIMATION */
    .big-title {
        font-size: 60px;
        font-weight: 850;
        text-align: center;
        margin-top:15px;
        margin-bottom: 15px;
        background: linear-gradient(90deg, #33bbff, #ff33ee, #ffd633);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGlow 6s ease infinite;
        text-shadow: 0 0 25px rgba(51, 187, 255, 0.7);
    }

    @keyframes titleGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .subtitle {
        text-align:center;
        color:#9aa2ba;
        margin-bottom: 25px;
        font-size: 14px;
    }

    /* GLASS CARD */
    .glass-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 18px;
        padding: 20px 22px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        margin-bottom: 22px;
    }

    /* LOG BOX */
    .log-box {
        height: 260px;
        overflow-y: auto;
        padding: 12px;
        background: rgba(3,6,15,0.9);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.13);
        font-size: 13px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
    }

    .log-line {
        margin-bottom: 4px;
        color: #d5ddff;
    }

    .log-line span.tag {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 999px;
        margin-right: 6px;
    }

    .log-line span.title-tag {
        background: rgba(51,187,255,0.15);
        color: #33bbff;
    }

    .log-line span.context-tag {
        background: rgba(124,252,0,0.15);
        color: #7CFC00;
    }

    /* WIKI CARD */
    .wiki-card {
        padding: 14px 14px;
        margin: 8px 0;
        border-radius: 12px;
        background: rgba(15,18,30,0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.09);
        transition: 0.25s ease;
        position: relative;
        overflow: hidden;
    }

    .wiki-card::before {
        content: "";
        position: absolute;
        inset: -40%;
        background: conic-gradient(
            from 180deg,
            rgba(51,187,255,0.15),
            rgba(255,51,238,0.15),
            rgba(255,214,51,0.15),
            transparent,
            transparent
        );
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: 0;
    }

    .wiki-card:hover::before {
        opacity: 1;
    }

    .wiki-card-inner {
        position: relative;
        z-index: 1;
    }

    .wiki-card:hover {
        transform: translateY(-3px);
        border-color: #33bbff;
        box-shadow: 0 0 20px rgba(51,187,255,0.35);
    }

    .wiki-highlight {
        border-color: #ff33ee !important;
        box-shadow: 0 0 20px rgba(255,51,238,0.65) !important;
    }

    .wiki-title {
        font-size: 15px;
        font-weight: 600;
        color: #e4ecff;
        margin-bottom: 4px;
    }

    .wiki-url a {
        color: #8fd3ff;
        font-size: 12px;
        text-decoration: none;
    }

    .wiki-url a:hover {
        text-decoration: underline;
    }

    /* WINNER STRIP */
    .winner-strip {
        border-left: 5px solid #33bbff;
        padding-left: 12px;
        margin: 10px 0 18px 0;
    }

    .winner-strip h2 {
        margin: 0;
        color: #e9f5ff;
    }

    /* PROGRESS BAR GRADIENT */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #33bbff, #ff33ee);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='big-title'>Wikipedia Multithreaded Navigator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Two strategies race from a start page to a target using title vs context similarity.</div>", unsafe_allow_html=True)


# ==============================================================
# User Inputs (inside glass card)
# ==============================================================
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)
    with col_input1:
        start_url = st.text_input("🌍 Start Wikipedia URL:", "https://en.wikipedia.org/wiki/India")
        word_limit = st.slider("🧠 Context Word Limit:", 20, 200, 80)

    with col_input2:
        target_title = st.text_input("🎯 Target Page Title:", "London")
        max_steps = st.slider("🔁 Max Steps:", 5, 200, 50)

    threshold = st.slider("📏 Similarity Threshold:", 0.0, 1.0, 0.2)

    start_btn = st.button("🚀 Start Navigation Race", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================
# UI HELPERS
# ==============================================================
def wiki_card(title, url, highlight=False):
    extra_class = "wiki-highlight" if highlight else ""
    st.markdown(
        f"""
        <div class="wiki-card {extra_class}">
            <div class="wiki-card-inner">
                <div class="wiki-title">{title}</div>
                <div class="wiki-url"><a href="{url}" target="_blank">{url}</a></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================
# THREAD WORKER
# ==============================================================
def thread_worker(
    mode_name,
    game_method,
    start_url,
    target_title,
    context,
    results_dict,
    stop_event,
    log_queue,
    prog_queue,
):
    scraper = Scrapper()
    selector = GetSimilarWord()
    game = WikipediaGame(
        scraper,
        selector,
        max_steps=max_steps,
        similarity_threshold=threshold,
    )

    path = []

    try:
        if game_method == "title":
            gen = game.play_stepwise_title(start_url, target_title)
        else:
            gen = game.play_stepwise_context(start_url, target_title, context)

        for step_idx, (title, url) in enumerate(gen):
            if stop_event.is_set():
                return

            path.append((title, url))

            log_queue.put((mode_name, step_idx, title))
            prog_queue.put(step_idx)

            time.sleep(0.05)

        if not stop_event.is_set() and path:
            stop_event.set()
            results_dict[mode_name] = path

    except Exception as e:
        log_queue.put((mode_name, -1, f"❌ ERROR: {e}"))


# ==============================================================
# MAIN UI EXECUTION
# ==============================================================
if start_btn:

    if not start_url.strip() or not target_title.strip():
        st.error("Please fill both Start URL and Target Title.")
        st.stop()

    st.info("Fetching target context & detecting language...")
    target_context, lang = fetch_wikipedia_summary(target_title, word_limit)

    # Force start URL into correct language domain
    slug = start_url.split("/wiki/")[-1]
    start_url = f"https://{lang}.wikipedia.org/wiki/{slug}"

    st.markdown(
        f"**🌐 Detected Language:** `{lang}` &nbsp;&nbsp; | &nbsp;&nbsp; "
        f"**Context Extracted (first 200 chars):** `{target_context[:200]}...`"
    )

    # Queues
    title_log_q = Queue()
    ctx_log_q = Queue()
    title_prog_q = Queue()
    ctx_prog_q = Queue()

    results = {}
    stop_event = threading.Event()

    # UI containers
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    log_cols = st.columns(2)

    with log_cols[0]:
        st.markdown("##### 🟦 Title-Based Logs")
        log_title_box = st.empty()

    with log_cols[1]:
        st.markdown("##### 🟩 Context-Based Logs")
        log_ctx_box = st.empty()

    prog_cols = st.columns(2)
    with prog_cols[0]:
        prog_title = st.progress(0, text="Title-based Progress")
    with prog_cols[1]:
        prog_ctx = st.progress(0, text="Context-based Progress")

    st.markdown("</div>", unsafe_allow_html=True)

    # Start threads
    t1 = threading.Thread(
        target=thread_worker,
        args=(
            "Title-Based",
            "title",
            start_url,
            target_title,
            target_context,
            results,
            stop_event,
            title_log_q,
            title_prog_q,
        ),
        daemon=True,
    )

    t2 = threading.Thread(
        target=thread_worker,
        args=(
            "Context-Based",
            "context",
            start_url,
            target_title,
            target_context,
            results,
            stop_event,
            ctx_log_q,
            ctx_prog_q,
        ),
        daemon=True,
    )

    t1.start()
    t2.start()

    # log buffers so we show history, not only last line
    title_log_html = ""
    ctx_log_html = ""

    # Poll UI queues while threads run
    while t1.is_alive() or t2.is_alive():
        # Title logs
        while not title_log_q.empty():
            mode, step_idx, text = title_log_q.get()
            tag_html = "<span class='tag title-tag'>Title</span>"
            step_label = f"[step {step_idx}]" if step_idx >= 0 else ""
            title_log_html += f"<div class='log-line'>{tag_html}{step_label} {text}</div>"
            log_title_box.markdown(
                f"<div class='log-box'>{title_log_html}</div>", unsafe_allow_html=True
            )

        # Context logs
        while not ctx_log_q.empty():
            mode, step_idx, text = ctx_log_q.get()
            tag_html = "<span class='tag context-tag'>Context</span>"
            step_label = f"[step {step_idx}]" if step_idx >= 0 else ""
            ctx_log_html += f"<div class='log-line'>{tag_html}{step_label} {text}</div>"
            log_ctx_box.markdown(
                f"<div class='log-box'>{ctx_log_html}</div>", unsafe_allow_html=True
            )

        # Progress bars
        if not title_prog_q.empty():
            step = title_prog_q.get()
            prog_title.progress(min((step + 1) / max_steps, 1.0))

        if not ctx_prog_q.empty():
            step = ctx_prog_q.get()
            prog_ctx.progress(min((step + 1) / max_steps, 1.0))

        time.sleep(0.05)

    st.success("🏁 Race finished!")

    if not results:
        st.error("No thread completed a path. Try increasing max steps or lowering threshold.")
        st.stop()

    # Winner selection
    # The first key in results corresponds to the thread that finished first
    winner_name = list(results.keys())[0]
    winner_path = results[winner_name]

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='winner-strip'>
            <h2>🏆 Winner: {winner_name}</h2>
            <p style="color:#9aa2ba;font-size:13px;">
                Final landing page: <b>{winner_path[-1][0]}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 🧭 Winning Path")
    for i, (t, u) in enumerate(winner_path, 1):
        wiki_card(t, u, highlight=(i == len(winner_path)))

    st.markdown("</div>", unsafe_allow_html=True)
