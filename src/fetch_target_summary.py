import requests
from bs4 import BeautifulSoup
from clean_summary import clean_text

def fetch_wikipedia_summary(title: str, word_limit: int = 100) -> str:
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36"
        )
    })
    
    resp = session.get(url)

    if resp.status_code != 200:
        print("Error fetching page")
        return title

    soup = BeautifulSoup(resp.text, "html.parser")

    # Select all intro paragraphs inside the correct wiki container
    paragraphs = soup.select("#mw-content-text .mw-parser-output > p")

    for p in paragraphs:
        text = p.get_text().strip()

        # skip empty / metadata paragraphs

        cleaned = clean_text(text)

        if not cleaned or len(cleaned) < 30:
            continue
        
        # take first meaningful paragraph
        words = cleaned.split()
        summary = " ".join(words[:word_limit])
        print(summary)
        return summary

    # fallback
    return title
