import requests

from bs4 import BeautifulSoup

def main():
    #url = input("Enter Tagesschau-URL: ")
    url = "https://www.tagesschau.de/klima"
    #search_string = input("What word are you looking for? :")
    search_string = "klima"
    print(url)
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')

    # Integration von Class
    category = ScrapeCategory(soup, search_string)
    #print(category.get_links(soup))
    print(category)
    #print(len(category.raw_articles))
    #for article in category.raw_articles:
    #    print(article.prettify())
    #print(category.raw_articles)
    #print(category.links)
    #for _ in category.links:
    #    print(_)

    """
    # Links
    links = soup.find_all("a", class_="teaser__link")
    print(len(links))
    #print(links[0].prettify())
    authors = []
    teasers = []
    for link in links:
        p = link.find('p')
        sub_p = p.find_all()
        for _ in sub_p:
            #tag = _.name
            if _.name == "em":
                authors.append(_.text.strip("Von "))
            _.decompose()
            #print(_.name)
        teasers.append(p.text.strip())
    counter = []
    string = "hsv"
    for teaser in teasers:
        if string in teaser.lower():
            counter.append(1)
            print(teaser)
        else:
            counter.append(0)
    #for count in counter:
    #    print(count)
    #for author in authors:
    #    print(author)
    #for teaser in teasers:
    #    print(teaser)
    print(counter.count(1)/len(links))


    p = links[0].find('p')
    #print(p.prettify())
    sub_p = p.find_all()
    for _ in sub_p:
        print(_.name)
    #print(sub_p)

    #for _ in links:
    #    print(_.get('href'))

    # Teaser


    # das funktioniert!
    for _ in links:
        p = _.find('p')
        span = p.span
        em = p.em
        try:
            span.decompose()
            em.decompose()
        except:
            continue
        #print(p.text.strip())


    #p = p.span.text
    #print(p)
    #print(links.find("p", recursive=False)
    #for _ in links:
    #    print(_.get('p'))
    """


class ScrapeCategory():
    def __init__(self, soup, search_string) -> None:
        self.soup = soup
        self.search_string = search_string
        self.raw_articles = self.get_articles()
        self.n_articles = len(self.raw_articles)
        self.teasers = []
        for article in self.raw_articles:
            d_article = {
                "topline": self.get_topline(article),
                "headline": self.get_headline(article),
                "shorttext": self.get_shorttext(article),
                "link": self.get_link(article),
                "search_string_found": self.analyze_teaser(self.get_shorttext(article)),
            }
            self.teasers.append(d_article)
        #for teaser in self.teasers:
            #for k in teaser:
            #    print(f"{k}: {teaser[k]}")
            #print("+++++++++++++++++")
        self.counter = 0
        for teaser in self.teasers:
            if teaser["search_string_found"] == True:
                self.counter += 1
        #print(self.raw_articles[0].prettify())




        # für jeden Artikel willst du ein Dict!
        """
        self.links = self.get_links()
        self.teasers = self.get_teaser()
        # for _ in self.authors:
        #    print(_)
        print(self.raw_articles[0].prettify())
        """


    def __str__(self):
        return f"The category has {self.n_articles} articles in which the search string was found {self.counter} times."

    def get_articles(self):
        return self.soup.find_all("a", class_="teaser__link")


    def get_topline(self, article):
        topline = article.find('span', {'class': 'teaser__topline'})
        return topline.text


    def get_headline(self, article):
        headline = article.find('span', {'class': 'teaser__headline'})
        return headline.text

    def get_link(self, article):
        link = article.get('href')
        if link.startswith('https:') == False:
            link = "https://www.tagesschau.de" + link
        return link

    # old
    """
    def get_links(self):
        self.links = []
        for _ in self.raw_articles:
            link = _.get('href')
            # complete links
            if link.startswith('https:') == False:
                link = "https://www.tagesschau.de" + link
            self.links.append(link)
        return self.links
    """

    def get_shorttext(self, article):
        shorttext = article.find('p')
        sub_p = shorttext.find_all()
        for _ in sub_p:
            _.decompose()
        return shorttext.text.strip()

    # old
    """
    def get_teaser(self):
        self.teasers = []
        for _ in self.raw_articles:
            p = _.find('p')
            sub_p = p.find_all()
            for _ in sub_p:
                _.decompose()
            self.teasers.append(p.text.strip())
        return self.teasers
    """

    def analyze_teaser(self, shorttext):
        if self.search_string in shorttext.lower():
            return True
        else:
            return False


if __name__ == "__main__":
    main()