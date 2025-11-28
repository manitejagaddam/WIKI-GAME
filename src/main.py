from scapper import Scrapper
from get_similar_word import GetSimilarWord



def main():
    start_url = "https://en.wikipedia.org/wiki/Narendra_Modi"
    target = "New Delhi"

    visited = set()
    current_url = start_url
    scraper = Scrapper()
    similar = GetSimilarWord()

    while True:
        if current_url in visited:
            break
        
        visited.add(current_url)
        
        links = scraper.get_links(current_url)
        clean_links = convert_links_to_text_url(links)
        
        best_text, best_url, score = similar.getSimilarWord(target, clean_links)
        
        print("Moving to:", best_text, best_url)
        
        current_url = best_url

        if best_text.lower() == target.lower() or score > 0.85:
            print("Reached target!")
            break



if __name__ == "__main__":
    main()