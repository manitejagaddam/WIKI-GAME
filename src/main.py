from scapper import Scrapper



def main():
    url = "https://en.wikipedia.org/wiki/Narendra_Modi"
    sc = Scrapper(url)
    links = sc.get_links()
    print(links)


if __name__ == "__main__":
    main()