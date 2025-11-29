from bs4 import BeautifulSoup
from clean_summary import clean_text
from http_session import create_session

LANGS = ["en", "simple", "es", "fr", "de", "hi", "ru", "ja"]


def safe_get(session, url, timeout=5):
    try:
        return session.get(url, timeout=timeout)
    except Exception as e:
        print(f"[ERROR] GET failed for {url} → {e}")
        return None


def fetch_wikipedia_summary(title: str, word_limit: int = 100):
    session = create_session()
    normalized_title = title.replace(" ", "_")

    for lang in LANGS:
        url = f"https://{lang}.wikipedia.org/wiki/{normalized_title}"
        print(f"Trying {lang.upper()} → {url}")

        resp = safe_get(session, url)
        if not resp or resp.status_code != 200:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.select("#mw-content-text .mw-parser-output > p")

        for p in paragraphs:
            text = p.get_text().strip()
            cleaned = clean_text(text)

            if not cleaned or len(cleaned) < 30:
                continue

            words = cleaned.split()
            summary = " ".join(words[:word_limit])

            print(f"Found summary in {lang.upper()}!")
            return summary, lang  # <--- RETURN LANGUAGE ALSO

    print("No valid summary found in any language.")
    return title, "en"   # default fallback
