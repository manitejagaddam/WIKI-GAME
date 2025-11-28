import requests
from bs4 import BeautifulSoup

class Scrapper:
    def __init__(self, _url):
        self.url = _url
        self.html_text = ""

    def get_html(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/120.0.0.0 Safari/537.36"
            )
        }

        try:
            res = requests.get(self.url, timeout=10, headers=headers)
            res.raise_for_status()
            self.html_text = res.text
        except Exception as e:
            print("Error fetching HTML:", e)
            self.html_text = ""

    def get_links(self):
        self.get_html()
        if not self.html_text:
            return []

        soup = BeautifulSoup(self.html_text, 'html.parser')
        links = []

        for tag in soup.find_all('a'):
            text = tag.get_text()
            href = tag.get('href')
            if href:
                links.append({"text": text, "url": href})

        return links
