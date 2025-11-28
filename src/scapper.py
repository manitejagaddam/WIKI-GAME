import requests
import logging
from bs4 import BeautifulSoup

# -----------------------
# Configure Global Logger
# -----------------------
logging.basicConfig(
    level=logging.INFO,                      # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

        logging.info(f"Fetching URL: {self.url}")

        try:
            res = requests.get(self.url, timeout=10, headers=headers)
            res.raise_for_status()

            logging.info(f"Fetched successfully: {len(res.text)} characters")
            self.html_text = res.text

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error fetching URL {self.url}: {e}")
            self.html_text = ""

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching URL {self.url}: {e}")
            self.html_text = ""

    def get_links(self, url=""):
        if url != "":
            logging.info(f"URL overridden. New URL: {url}")
            self.url = url

        self.get_html()
        if not self.html_text:
            logging.warning("HTML content is empty. No links extracted.")
            return []

        soup = BeautifulSoup(self.html_text, 'html.parser')
        links = []

        logging.info("Extracting links...")

        for tag in soup.find_all('a'):
            text = tag.get_text().strip()
            href = tag.get('href')

            if not href:
                logging.debug("Skipping <a> tag without href.")
                continue

            links.append({"text": text, "url": href})

        logging.info(f"Total links extracted: {len(links)}")

        return links
