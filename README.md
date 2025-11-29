# Wikipedia Navigator Game

A fun, challenge-inspired project that tries to move from one **Wikipedia page** to another **target page** by following only internal links.

You give it:

- a **starting Wikipedia URL**
- a **target page title**

The app then searches for a valid path using **linear traversal**, **multithreading**, **title-based matching**, and **context similarity** with **BERT**, plus **multi-language checks** when the English page isn’t available.

---

## ✨ Features

- 🔗 Navigate from a start page to a target Wikipedia page
- 🧵 **Multithreading**: runs multiple search strategies in parallel
- 🔤 **Title-based search** for direct matches
- 🧠 **Context-based search using BERT** for smarter matching when titles differ
- 🌍 **Multi-language support** when the English version of a page is missing
- 🖥️ **Streamlit UI** for an easy, interactive experience
- 🧹 Utilities for cleaning summaries, managing HTTP sessions, and handling edge cases

---

## 🧩 How It Works (High Level)

1. **Input**
   - Starting Wikipedia URL  
   - Target page title

2. **Target Context**  
   The app fetches and cleans the **target page summary** to build a contextual representation (via BERT embeddings).

3. **Traversal Engine**  
   - Scrapes outgoing links from each page  
   - Evaluates each link by:
     - **Title match**
     - **Context similarity**  
   - Follows links **linearly** (no BFS)

4. **Multithreaded Search**  
   Title-based and context-based strategies run in parallel.  
   The one that finds the target first returns the path.

5. **Multi-Language Handling**
   - Detects if English pages are missing  
   - Switches to the correct language automatically  
   - Continues navigation seamlessly  

6. **Output**  
   The app returns a full list of Wikipedia URLs from start → target.

---

## 🗂 Project Structure

```
.
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
└── src
    ├── __pycache__/
    ├── app.py
    ├── app2.py
    ├── clean_summary.py
    ├── engine.py
    ├── fetch_target_summary.py
    ├── get_similar_word.py
    ├── http_session.py
    ├── main.py
    ├── run_thread.py
    └── scapper.py
```

---

## 🧱 Tech Stack

- Python  
- Streamlit  
- Requests + BeautifulSoup  
- Sentence-BERT  
- Multithreading  

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/manitejagaddam/WIKI-GAME.git
cd WIKI-GAME
```

### Install dependencies

```bash
uv sync
```

---

## ▶️ Running the App

### Streamlit UI

```bash
streamlit run src/app.py
```

Alternate:

```bash
streamlit run src/app2.py
```

Alternate 2:

```bash
uv run main.py
```

Alternate 3:

```bash
uv run src/main.py
```

### Direct script

```bash
python src/main.py
```

---

## 🧪 Example

Start: `https://en.wikipedia.org/wiki/India`  
Target: `Bhupalpally`

What happens:

- Fetch target summary  
- Create context embedding  
- Evaluate link titles and context  
- Switch language if needed  
- Follow the best linear path  
- Return final navigation sequence  

---

## 🛠 Future Ideas

- Graph visualization  
- Difficulty levels  
- Leaderboard  
- Multiplayer race mode  
- Cached traversal for speed  

---

## 🤝 Contributing

Issues, improvements, and PRs are welcome.

---

## ⭐ Support

If you liked this project, please **star the repo**!

Made By Maniteja Gaddam 🩵
---