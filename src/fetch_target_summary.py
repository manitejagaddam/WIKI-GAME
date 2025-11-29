import requests
from bs4 import BeautifulSoup
from clean_summary import clean_text

LANGS = ["en", "simple", "es", "fr", "de", "hi", "ru", "ja"]

def fetch_wikipedia_summary(title: str, word_limit: int = 100) -> str:
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36"
        )
    })

    normalized_title = title.replace(" ", "_")
    
    for lang in LANGS:
        url = f"https://{lang}.wikipedia.org/wiki/{normalized_title}"
        print(f"Trying {lang.upper()} → {url}")

        resp = session.get(url)

        if resp.status_code != 200:
            continue  # try next language

        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.select("#mw-content-text .mw-parser-output > p")

        for p in paragraphs:
            text = p.get_text().strip()
            cleaned = clean_text(text)

            if not cleaned or len(cleaned) < 30:
                continue

            # take first meaningful paragraph
            words = cleaned.split()
            summary = " ".join(words[:word_limit])

            print(f"Found summary in {lang.upper()}!")
            return summary

    # fallback to title if nothing found
    print("No valid summary found in any language.")
    return title
