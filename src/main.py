from scapper import Scrapper
from get_similar_word import GetSimilarWord



def main():
    url = "https://en.wikipedia.org/wiki/Narendra_Modi"
    sc = Scrapper(url)
    similar = GetSimilarWord()
    links = sc.get_links()
    print(links[:10])
    best_name, best_link, best_score = similar.getSimilarWord("new Delhi", links=links)
    print(best_name, best_link, best_score)


if __name__ == "__main__":
    main()