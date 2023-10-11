import requests
import re

from bs4 import BeautifulSoup

def main():
    # Url
    archiv_url = "https://www.tagesschau.de/archiv"
    url_extention = "?datum="
    datum = "2023-10-06"
    url = archiv_url+url_extention+datum

    # Search string
    search_string = "klima"

    # Request url and get soup
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')

    # Running archiveScraper
    archive = ScrapeArchive(soup, datum, search_string)

    # Print archiveScraper results

    for teaser in archive.teaser_list:
        if teaser["string_found"] == True:
            print("+++")
            print(teaser["topline"])
            print(teaser["link"])
            print(teaser["datetime"])

    print(archive)


    # Using articleScraper
    for teaser in archive.teaser_list[:1]:
        article_url = teaser["link"]
        a = requests.get(article_url)
        soup = BeautifulSoup(a.text, 'html.parser')
        article = ScrapeArticle(article_url, soup, search_string)
        #print(article.raw_article.prettify())

        

class ScrapeArticle():
    def __init__(self, url, soup, search_string):
        # Input
        self.url = url
        self.soup = soup
        self.search_string = search_string
        # Raw HTML
        self.raw_article = self.soup.find('article')
        
        #self.content
        # Analysis of article
        #self.word_count
        #self.match_search_string_counter

    
    def __str__(self):
        return f"This is link {self.url} and search_string {self.search_string}"


class ScrapeArchive():
    def __init__(self, soup, datum, search_string):
        # Input
        self.soup = soup
        self.date = datum
        self.search_string = search_string
        # Raw HTML
        self.main_content = self.get_main_content()
        self.raw_teasers = self.get_raw_teasers()
        # Create and analyse list of teasers
        self.teaser_list = []
        for teaser in self.raw_teasers:
            self.teaser_list.append(self.scrape_teaser(teaser))
        self.teaser_counter = len(self.teaser_list)
        self.match_search_string_counter = 0
        self.match_search_string()


    def __str__(self):
        return f"Found teasers in archive page for {self.date}: {self.teaser_counter}\nFound string matches in archive page: {self.match_search_string_counter}"


    def get_main_content(self):
        return self.soup.find('div', class_='columns twelve')


    def get_raw_teasers(self):
        return self.main_content.find_all('a')


    def scrape_teaser(self, teaser):
        teaser_dict = {
            "link": self.get_link(teaser),
            "topline_label": self.get_topline_label(teaser),
            "topline": self.get_topline(teaser),
            "headline": self.get_headline(teaser),
            "shorttext": self.get_shorttext(teaser),
            "datetime": self.get_datetime(teaser),
            "date": self.date,
        }
        return teaser_dict


    def match_search_string(self):
        dict_categories = [
            "topline",
            "headline",
            "shorttext",
        ]
        for teaser in self.teaser_list:
            for category in dict_categories:
                if self.search_string in teaser[category].lower():
                    teaser["string_found"] = True
                    self.match_search_string_counter += 1
                    break
                teaser["string_found"] = False


    def get_link(self, teaser):
        link = teaser.get('href')
        if not link.startswith("https://www.tagesschau.de"):
            return "https://www.tagesschau.de"+link
        else:
            return link


    def get_topline_label(self, teaser):
        # find span-tag in which class entails 'label--small'
        topline_label_raw = teaser.find('span', class_=re.compile('label--small'))
        if topline_label_raw == None:
            return None
        else:
            return topline_label_raw.strong.text


    def get_topline(self, teaser):
        topline_raw = teaser.find('span', class_='teaser-right__labeltopline')
        if topline_raw == None:
            return None
        else:
            return topline_raw.text


    def get_headline(self, teaser):
        headline_raw = teaser.find('span', class_='teaser-right__headline')
        if headline_raw == None:
            return None
        else:
            return headline_raw.text


    def get_shorttext(self, teaser):
        shorttext_raw = teaser.find('p', class_='teaser-right__shorttext')
        # typical tags: 'span' => 'link-extend' and 'em' => 'author'
        dismiss_elements = shorttext_raw.find_all()
        for dismiss_element in dismiss_elements:
            dismiss_element.decompose()
        if shorttext_raw == None:
            return None
        else:
            return shorttext_raw.text.strip()


    def get_datetime(self, teaser):
        datetime_raw = teaser.find('div', class_='teaser-right__date')
        if datetime_raw == None:
            return None
        else:
            return datetime_raw.text


if __name__ == "__main__":
    main()