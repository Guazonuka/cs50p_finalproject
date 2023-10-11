import requests
import re

from bs4 import BeautifulSoup

def main():
    # Url
    archiv_url = "https://www.tagesschau.de/archiv?datum="
    datum = "2023-10-09"
    url = archiv_url+datum

    # Search string
    search_string = "klima"

    # Request url and get soup
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')

    # Running Scraper
    archive = ScrapeArchive(soup, datum, search_string)

    #print(archive.raw_teasers[4].prettify())


    for teaser in archive.teaser_list:
        print("++++++++++")
        print(teaser["topline"])
        print(teaser["datetime"])
        #for line in teaser:
        #    print(f"{line}: {teaser[line]}")



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
            self.teaser_list.append(self.analyze_teaser(teaser))


    def get_main_content(self):
        return self.soup.find('div', class_='columns twelve')


    def get_raw_teasers(self):
        return self.main_content.find_all('a')


    def analyze_teaser(self, teaser):
        teaser_dict = {
            "link": teaser.get('href'),
            "topline_label": self.get_topline_label(teaser),
            "topline": self.get_topline(teaser),
            "headline": self.get_headline(teaser),
            "shorttext": self.get_shorttext(teaser),
            "datetime": self.get_datetime(teaser),
        }
        return teaser_dict


    def get_topline_label(self, teaser):
        #topline_label_raw = teaser.find('span', class_='label label--small')
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