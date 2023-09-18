import requests
from bs4 import BeautifulSoup


def main():
    soup = get_website("https://www.tagesschau.de/inland/gesellschaft/corona-pandemie-drosten-101.html")
    article = chop_soup(soup)
    results = analyze_article(article)
    for _ in results:
        print(_, results[_])


def get_website(s):
    article = requests.get(s)
    return BeautifulSoup(article.text, 'html.parser')


def chop_soup(soup):
    subtitles = []
    for _ in soup.article.find_all("h2"):
        subtitles.append(_.get_text())
    
    paragraphs = []
    for _ in soup.article.find_all("p", {"class": "textabsatz"}):
        paragraphs.append(_.get_text())
    
    article = {
        "metadata":soup.article.find("p", {"class": "metatextline"}).get_text(),
        "title":soup.title.string,
        "subtitles":subtitles,
        "paragraphs":paragraphs,
    }
    return article


def analyze_article(article):
    string = "drosten"
    results = {}
    for k in article:
        results[f"{k}_counted"] = count_string(string, article[k])
    results["count_total"] = sum(results.values())
    return results


def count_string(string, k):
    obj_counter = 0
    if isinstance(k, list):
        for v in k:
            obj_counter += v.lower().count(string)
    else:
        obj_counter += k.lower().count(string)
    return obj_counter


if __name__ == "__main__":
    main()