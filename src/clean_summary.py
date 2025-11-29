import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

def clean_text(text: str):
    # lower
    text = text.lower()

    # remove punctuation, numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # remove stopwords + tiny words
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]

    return " ".join(words)

