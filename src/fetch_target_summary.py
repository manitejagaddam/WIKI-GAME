import requests
from bs4 import BeautifulSoup

def fetch_wikipedia_summary(title: str, word_limit: int = 100) -> str:
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    resp = requests.get(url)

    if resp.status_code != 200:
        return title  # fallback to simple text

    soup = BeautifulSoup(resp.text, "html.parser")

    # Get the first paragraph
    p = soup.select_one("p")
    if not p:
        return title

    text = p.get_text().strip()
    words = text.split()

    # Limit number of words
    summary = " ".join(words[:word_limit])

    return summary
