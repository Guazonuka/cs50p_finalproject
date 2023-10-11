import requests

from bs4 import BeautifulSoup

def main():
    #url = input("Enter Tagesschau-URL: ")
    archiv_url = "https://www.tagesschau.de/archiv?datum="
    datum = "2023-10-09"
    #url = "https://www.tagesschau.de/wissen/klima"
    url = archiv_url+datum
    print(url)
    #search_string = input("What word are you looking for? :")
    search_string = "klima"
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')

    # Integration von Class
    archive = ScrapeArchive(soup, datum, search_string)
    print(archive.n_articles)
    #for article in archive.html_articles:
    #    print(article.get('href'))

    #category = ScrapeCategory(soup, datum, search_string)
    #print(category.n_articles)
    #print(category.raw_articles[0].prettify())
    #for _ in category.teasers:
    #    print(_['link'])
        #print(_['label'])
        #print(_['topline'])
    #    pass

    #article = ScrapeArticle(category.teasers[0], search_string)
    #print(category.teasers)
    #for link in category.teasers[:3]:
    #    x = ScrapeArticle(link, search_string)
    #    print(x)
        #print(link["link"])

    #print(article)
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
    """

### ich brauche ein dict auf article ebene (weile alle artikel können anderes html layout haben)
#### in dem dict sind alle keys einerseits
#### und alle gefundenen values aus dem article andererseits
#### default ist ""

class ScrapeArchive():
    def __init__(self, soup, datum, search_string):
        self.soup = soup
        self.date = datum
        self.search_string = search_string
        self.html_articles = self.get_articles()
        self.n_articles = len(self.html_articles)


    def get_articles(self):
        links = self.soup.main.find_all('a')
        for link in links:
            if "teaser" and "link" in link['class'][0]:
                print(link['class'][0])
        return [0,1]



class ScrapeCategory():
    def __init__(self, soup, search_string) -> None:
        self.soup = soup
        self.search_string = search_string
        self.raw_articles = self.get_articles()
        self.n_articles = len(self.raw_articles)
        self.teasers = []
        for article in self.raw_articles:
            d_article = {
                #"topline": self.get_topline(article),
                #"headline": self.get_headline(article),
                #"label": self.get_label(article),
                #"shorttext": self.get_shorttext(article),
                "link": self.get_link(article),
                #"search_string_found": self.analyze_teaser(self.get_shorttext(article)),
            }
            self.teasers.append(d_article)
            #if d_article["label"] == "Video":
            #    print("Video found!")
            #    continue
            #else:
            #    self.teasers.append(d_article)

        # counter logic is not state of the art...
        """
        self.counter = 0
        for teaser in self.teasers:
            if teaser["search_string_found"] == True:
                self.counter += 1
        """

    def __str__(self):
        return "nothing"
        return f"The category has {self.n_articles} teasers in which the search string was found {self.counter} times => {round((self.counter / self.n_articles * 100), 1)}% occurence"



    def get_articles(self):
        teaser_links = []
        for link in self.soup.main.find_all("a"):
            keyword = "teaser"
            if keyword in link['class'][0]:
                teaser_links.append(link['class'][0])
        d_teaser_links = {}
        for link in teaser_links:
            if link not in d_teaser_links.keys():
                d_teaser_links["class"]  = link
        return self.soup.main.find_all("a", d_teaser_links)


    """
    def get_articles(self):
        # teaser-xs is a link without a teaser text
        classes = {"teaser__link", "teaser-xs__link"}
        # find all links in main
        teaser_links = []
        for _link in self.soup.main.find_all("a"):
            #print(_link.get('href'))
            # shows class names for all links in main
            keyword = "teaser"
            #print(_link['class'][0])
            if keyword in _link['class'][0]:
                teaser_links.append(_link['class'][0])
        d_teaser_links = {}
        for link in teaser_links:
            if link not in d_teaser_links.keys():
                d_teaser_links["class"]  = link
        print(d_teaser_links)
        # shows no of links defined in classes
        #print(len(self.soup.main.find_all("a", class_=classes)))
        # working version for links with teaser-text
        return self.soup.find_all("a", d_teaser_links)
        #return self.soup.find_all("a", class_="teaser__link")
        # returns both type of links
        #return self.soup.find_all("a", class_={"teaser__link", "teaser-xs__link"})
    """

    def get_topline(self, article):
        teaser_toplines = []
        for topline in article.span['class']:
            keyword = "topline"
            if keyword in topline['class'][0]:
                teaser_toplines.append(topline['class'][0])
        return article.find('span', {'class': 'teaser__topline'}).text

    def get_headline(self, article):
        return article.find('span', {'class': 'teaser__headline'}).text

    def get_label(self, article):
        label = article.find('span', {'class': 'label label--small'})
        if label is not None:
            return label.text.strip()

    def get_link(self, article):
        link = article.get('href')
        if link.startswith('https:') == False:
            link = "https://www.tagesschau.de" + link
        return link

    def get_shorttext(self, article):
        shorttext = article.find('p')
        sub_p = shorttext.find_all()
        for _ in sub_p:
            _.decompose()
        return shorttext.text.strip()

    def analyze_teaser(self, shorttext):
        if self.search_string in shorttext.lower():
            return True
        else:
            return False


class ScrapeArticle():
    def __init__(self, teaser, search_string):
        self.teaser = teaser
        self.search_string = search_string
        self.raw_article = self.get_website(teaser["link"])
        self.teaser["metadata"] = self.raw_article.find("p", {"class": "metatextline"}).get_text().strip("Stand: ")
        self.paragraphs = []
        self.get_paragraphs()
        self.teaser["paragraphs"] = self.paragraphs
        self.teaser["search_string_paragraph"] = self.analyze_paragraphs()
        #for k in self.teaser:
        #    print(f"{k}: {teaser[k]}")

    def __str__(self):
        return f"Was the search string found in the article '{self.teaser['headline']}'? => {self.teaser['search_string_paragraph']}"

    def get_website(self, url):
        article = requests.get(url)
        return BeautifulSoup(article.text, 'html.parser')

    def get_paragraphs(self):
        for _ in self.raw_article.article.find_all("p", {"class": "textabsatz"}):
            self.paragraphs.append(_.get_text())

    def analyze_paragraphs(self):
        for _ in self.teaser["paragraphs"]:
            if self.search_string in _.lower():
                return True
        return False

if __name__ == "__main__":
    main()