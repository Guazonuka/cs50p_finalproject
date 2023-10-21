import calendar
import pandas as pd
import requests
import re
import sqlite3
import time

from bs4 import BeautifulSoup
import datetime as dt

def main():
    # Search string
    search_string = "klima"

    # Select year and month
    year = 2023
    month = 9

    num_days = calendar.monthrange(year, month)[1]
    days = [dt.date(year, month, day) for day in range(1, num_days+1)]

    # Implementing Sqlite3
    con = sqlite3.connect("tagesschau.db")
    db = con.cursor()

    # Create tables if not exist
    db.execute("CREATE TABLE IF NOT EXISTS articles (url VARCHAR PRIMARY KEY NOT NULL, topline_label TEXT, topline TEXT, headline TEXT, shorttext TEXT, datetime NUMERIC, author TEXT, tags TEXT, word_count INTEGER, matches INTEGER, scraped_dt NUMERIC, department TEXT, categories TEXT);")
    db.execute("CREATE TABLE IF NOT EXISTS articles_content (url VARCHAR PRIMARY KEY NOT NULL, subheadlines TEXT, paragraphs TEXT, scraped_dt NUMERIC);")

    for day in days:
        # Create day string
        date = dt.datetime.strftime(day, '%Y-%m-%d')
        # Create URL
        archive_url = "https://www.tagesschau.de/archiv"
        url_extention = "?datum="
        url = archive_url+url_extention+date

        # Request url and get bs4soup
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError
        soup = BeautifulSoup(r.text, 'html.parser')   

        # Running archiveScraper
        archive = ScrapeArchive(soup, date, search_string)
        
        # List for links not used in analysis
        unused_links = []

        # Using articleScraper
        for teaser in archive.teaser_list:
            if not teaser["link"].startswith("https://www.tagesschau.de"):
                unused_links.append(teaser["link"])
                continue
            article_url = teaser["link"]
            a = requests.get(article_url)
            soup = BeautifulSoup(a.text, 'html.parser')
            article = ScrapeArticle(article_url, soup, search_string)
            db_row = [
                article.article_dict["link"],
                article.article_dict["topline_label"],
                article.article_dict["topline"],
                article.article_dict["headline"],
                article.article_dict["shorttext"],
                article.article_dict["datetime"],
                article.article_dict["author"],
                ', '.join(article.article_dict["tags"]),
                article.article_analysis["word_count"],
                article.article_analysis["match_search_string_counter"],
                article.article_dict["scraped_dt"],
                article.article_dict["department"],
                ', '.join(article.article_dict["categories"]),
            ]

            article_content_row = [
                article.article_dict["link"],
                ' | '.join(article.article_dict["subheadlines"]),
                ' '.join(article.article_dict["paragraphs"]),
                article.article_dict["scraped_dt"],
            ]

            try:
                db.execute("INSERT INTO articles (url, topline_label, topline, headline, shorttext, datetime, author, tags, word_count, matches, scraped_dt, department, categories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (db_row))
                print(f"{article.article_dict['topline']} published on {article.article_dict['datetime']} added to database")
            except sqlite3.IntegrityError:
                print(f"The following URL from {article.article_dict['datetime']} is already in the database and will be skipped: {article.article_dict['link']}")
                pass

            try:
                db.execute("INSERT INTO articles_content (url, subheadlines, paragraphs, scraped_dt) VALUES (?, ?, ?, ?);", (article_content_row))
            except sqlite3.IntegrityError:
                pass

            # commit changes to db
            con.commit()

            # sleep counter of 1 second
            time.sleep(1)
        print(f"On {date} a total of {len(archive.teaser_list)} articles were analysed")

    # Close DB
    con.close()

    # Print list of links that were not analysed
    for link in unused_links:
        print(link)


class ScrapeArticle():
    def __init__(self, url, soup, search_string):
        # Input
        self.url = url
        self.soup = soup
        self.search_string = search_string
        # Raw HTML
        self.raw_article = self.soup.find('article')
        self.article_dict = {
            "link": self.url,
            "topline_label": self.get_topline_label(),
            "topline": self.raw_article.find('span', class_='seitenkopf__topline').text.strip(),
            "headline": self.raw_article.find('span', class_='seitenkopf__headline--text').text.strip(),
            "shorttext": self.get_shorttext(),
            "datetime": self.get_datetime(),
            "author": "", #self.get_author(),
            "subheadlines": self.get_subheadlines(),
            "paragraphs": self.get_paragraphs(),
            "tags": self.get_tags(),
            "hash": "",
            "scraped_dt": self.get_scraped_dt(),
            "department": self.url.replace("https://www.tagesschau.de/", "").split("/")[0],
            "categories": self.url.replace("https://www.tagesschau.de/", "").split("/")[1:-1],
        }
        # Analysis of article
        self.article_analysis = {
            "word_count": self.word_count(),
            "match_search_string_counter": self.match_search_string_counter(),
        }


    def __str__(self):
        return f"The article consists of {self.article_analysis['word_count']} words and {self.article_analysis['match_search_string_counter']} search_string matches"


    def word_count(self):
        counter = 0
        for _ in self.article_dict["topline"]:
            counter += len(_.split())
        for _ in self.article_dict["headline"]:
            counter += len(_.split())
        for _ in self.article_dict["subheadlines"]:
            counter += len(_.split())
        # Shorttext is included in paragraphs and therefore not counted
        for _ in self.article_dict["paragraphs"]:
            counter += len(_.split())
        return counter


    def match_search_string_counter(self):
        counter = 0
        if self.search_string in self.article_dict["topline"].lower():
            counter += self.article_dict["topline"].lower().count(self.search_string)
        if self.search_string in self.article_dict["headline"].lower():
            counter += self.article_dict["headline"].lower().count(self.search_string)
        for _ in self.article_dict["subheadlines"]:
            if self.search_string in _.lower():
                counter += _.lower().count(self.search_string)
        for _ in self.article_dict["paragraphs"]:
            if self.search_string in _.lower():
                counter += _.lower().count(self.search_string)
        return counter


    def get_topline_label(self):
        # find span-tag in which class entails 'label--small'
        topline_label_raw = self.raw_article.find('span', class_=re.compile('label--small'))
        if topline_label_raw == None:
            return None
        else:
            return topline_label_raw.strong.text.strip()


    def get_shorttext(self):
        shorttext_raw = self.raw_article.find('p', class_=re.compile('^textabsatz'))
        if shorttext_raw == None:
            return None
        else:
            return shorttext_raw.strong.text.strip()


    def get_datetime(self):
        datetime_raw = self.raw_article.find('p', class_='metatextline')
        if datetime_raw == None:
            return None
        else:
            datetime_str = datetime_raw.text.strip("Stand: ").strip(" Uhr")
            datetime = dt.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
            return datetime


    def get_author(self):
        author_raw = self.raw_article.find('div', class_='authorline__author')
        if author_raw == None:
            return None
        else:
            return author_raw.find('a').text.strip()
        

    def get_subheadlines(self):
        subheadlines_raw = self.raw_article.find_all('h2')
        subheadlines_list = []
        if subheadlines_raw == None:
            return None
        else:
            for subheadline in subheadlines_raw:
                subheadlines_list.append(subheadline.text.strip())
            return subheadlines_list


    def get_paragraphs(self):
        paragraphs_raw = self.raw_article.find_all('p', class_=re.compile('^textabsatz'))
        paragraphs_list = []
        if paragraphs_raw == None:
            return None
        else:
            for paragraph in paragraphs_raw:
                # strip method removes blank lines after shorttext but also all paragraph indications
                paragraphs_list.append(paragraph.text.strip())
            return paragraphs_list


    def get_tags(self):
        taglist_raw = self.raw_article.find('ul', class_='taglist')
        tag_link_list_raw = taglist_raw.find_all('a')
        tags_list = []
        if tag_link_list_raw == None:
            return None
        else:
            for tag in tag_link_list_raw:
                tags_list.append(tag.text.strip())
            return tags_list
        
    
    def get_scraped_dt(self):
        return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')



class ScrapeArchive():
    def __init__(self, soup, date, search_string):
        # Input
        self.soup = soup
        self.date = date
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
        if link.startswith("https://"):
            return link
        else:
            return "https://www.tagesschau.de"+link


    def get_topline_label(self, teaser):
        # find span-tag in which class entails 'label--small'
        topline_label_raw = teaser.find('span', class_=re.compile('label--small'))
        if topline_label_raw == None:
            return None
        else:
            return topline_label_raw.strong.text.strip()


    def get_topline(self, teaser):
        topline_raw = teaser.find('span', class_='teaser-right__labeltopline')
        if topline_raw == None:
            return None
        else:
            return topline_raw.text.strip()


    def get_headline(self, teaser):
        headline_raw = teaser.find('span', class_='teaser-right__headline')
        if headline_raw == None:
            return None
        else:
            return headline_raw.text.strip()


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
            datetime_str = datetime_raw.text.strip(" Uhr")
            datetime = dt.datetime.strptime(datetime_str, "%d.%m.%Y • %H:%M")
            return datetime  


if __name__ == "__main__":
    main()