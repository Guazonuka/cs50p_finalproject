import calendar
import pandas as pd
import requests
import re
import sqlite3
import time

from bs4 import BeautifulSoup
#from datetime import datetime as dt
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

        # Using articleScraper
        for teaser in archive.teaser_list[0:20]:
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
                db.execute("INSERT INTO test_3 (url, topline_label, topline, headline, shorttext, datetime, author, tags, word_count, matches, scraped_dt, department, categories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (db_row))
            except sqlite3.IntegrityError:
                print(f"The following URL is already in the database and will be skipped: {article.article_dict['link']}")
                pass

            try:
                db.execute("INSERT INTO test_4 (url, subheadlines, paragraphs, scraped_dt) VALUES (?, ?, ?, ?);", (article_content_row))
            except sqlite3.IntegrityError:
                pass

            # commit changes to db
            con.commit()

            # sleep counter of 1 second
            time.sleep(1)

    con.close()




    archive_url = "https://www.tagesschau.de/archiv"
    url_extention = "?datum="
    date = "2023-08-06"
    url = archive_url+url_extention+date

    # Search string
    search_string = "klima"

    # Request url and get bs4soup
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')

    # Running archiveScraper
    archive = ScrapeArchive(soup, date, search_string)

    # Implementing Sqlite3
    con = sqlite3.connect("tagesschau.db")
    db = con.cursor()

    # Print archiveScraper results
    """
    for teaser in archive.teaser_list:
        if teaser["string_found"] == True:
            print("+++")
            print(teaser["topline"])
            print(teaser["link"])
            print(teaser["datetime"])
            print(type(teaser["datetime"]))
    #print(archive)
    """
    """
    # Using articleScraper
    for teaser in archive.teaser_list[0:20]:
        article_url = teaser["link"]
        a = requests.get(article_url)
        soup = BeautifulSoup(a.text, 'html.parser')
        article = ScrapeArticle(article_url, soup, search_string)
        #print(article.article_dict["scraped_dt"])
        #print(article.article_dict["author"])
        #db.execute("INSERT INTO articles_short(word_count) VALUES (?);", [article.article_analysis["word_count"]])
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
        #print(article_content_row[0])
        #print(article_content_row[2])

        #
        self.article_dict = {
            "link": self.url,
            "topline_label": self.get_topline_label(),
            "topline": self.raw_article.find('span', class_='seitenkopf__topline').text,
            "headline": self.raw_article.find('span', class_='seitenkopf__headline--text').text,
            "shorttext": self.get_shorttext(),
            "datetime": self.get_datetime(),
            "author": "",
            "subheadlines": self.get_subheadlines(),
            "paragraphs": self.get_paragraphs(),
            "tags": self.get_tags(),
            "hash": "",
        }
        #
        
        # Creation of archive table
        #CREATE TABLE IF NOT EXISTS articles_short (url VARCHAR, topline_label TEXT, topline TEXT, headline TEXT, shorttext TEXT, datetime NUMERIC, tags TEXT, word_count INTEGER, matches INTEGER);

        # Insertion into archive table
        #db.execute("INSERT INTO articles_short (url, topline_label, topline, headline, shorttext, datetime, tags, word_count, matches) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (article.article_dict["link"], article.article_dict["topline_label"], article.article_dict["topline"], article.article_dict["headline"], article.article_dict["shorttext"], article.article_dict["datetime"], ', '.join(article.article_dict["tags"]), article.article_analysis["word_count"], article.article_analysis["match_search_string_counter"]))


        # create table test_1
        #CREATE TABLE test_1 (url VARCHAR, word_count INTEGER, matches INTEGER);
        
        # insertion in test table
        #db.execute("INSERT INTO test_1 (url, word_count, matches) VALUES (?, ?, ?);", (article.article_dict["link"], article.article_analysis["word_count"], article.article_analysis["match_search_string_counter"]))


        # create table test_3
        #CREATE TABLE IF NOT EXISTS test_3 (url VARCHAR PRIMARY KEY NOT NULL, topline_label TEXT, topline TEXT, headline TEXT, shorttext TEXT, datetime NUMERIC, author TEXT, tags TEXT, word_count INTEGER, matches INTEGER, scraped_dt NUMERIC, department TEXT, categories TEXT);

        # create table test_4
        #CREATE TABLE IF NOT EXISTS test_4 (url VARCHAR PRIMARY KEY NOT NULL, subheadlines TEXT, paragraphs TEXT, scraped_dt NUMERIC);

        # insertion in test table_3
        
        
        try:
            # Old version
            #db.execute("INSERT INTO test_2 (url, topline_label, topline, headline, shorttext, datetime, tags, word_count, matches) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (article.article_dict["link"], article.article_dict["topline_label"], article.article_dict["topline"], article.article_dict["headline"], article.article_dict["shorttext"], article.article_dict["datetime"], ', '.join(article.article_dict["tags"]), article.article_analysis["word_count"], article.article_analysis["match_search_string_counter"]))
            # this works!
            db.execute("INSERT INTO test_3 (url, topline_label, topline, headline, shorttext, datetime, author, tags, word_count, matches, scraped_dt, department, categories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (db_row))
        except sqlite3.IntegrityError:
            print(f"The following URL is already in the database and will be skipped: {article.article_dict['link']}")
            pass

        try:
            db.execute("INSERT INTO test_4 (url, subheadlines, paragraphs, scraped_dt) VALUES (?, ?, ?, ?);", (article_content_row))
        except sqlite3.IntegrityError:
            pass

        # commit changes to db
        con.commit()

        # sleep counter of 1 second
        time.sleep(1)

        #
        for s in article.article_dict:
            print(s, type(article.article_dict[s]))
        for s in article.article_analysis:
            print(s, type(article.article_analysis[s]))
        #
    
        #print(article.article_dict["subheadlines"])
        if article.article_analysis["match_search_string_counter"] > 0:
            print("+++")
            print(article.article_dict["topline"])
            print(article.article_dict["headline"])
            print(article.article_dict["datetime"])
            print(article.article_dict["link"])
            print(article.article_dict["tags"])
            print(type(article.article_dict["datetime"]))
            print(article.article_analysis["word_count"])
            print(type(article.article_analysis["word_count"]))
            print(article)
        # insert delay for article scraping
    """    


    pandas_db = pd.read_sql_query("SELECT * FROM test_3", con)
    #print(pandas_db[["word_count", "matches", "datetime", "scraped_dt"]].head(20))
    # closure of db
    con.close()
    #print("+++")


    
    # Using pandas to create dataframe
    #pd.set_option('display.max_columns', 1000)
    df = pd.DataFrame(archive.teaser_list)
    filt = df["string_found"] == False
    #print(df.loc[filt][["topline", "headline", "string_found"]])
    #print(df.shape)
    #print(df.head())
    #print(df.columns)
    #print(df[["topline_label", "headline", "datetime"]].head(20))
    #print(df.loc[0, "shorttext"])
    




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
            "topline": self.raw_article.find('span', class_='seitenkopf__topline').text,
            "headline": self.raw_article.find('span', class_='seitenkopf__headline--text').text,
            "shorttext": self.get_shorttext(),
            "datetime": self.get_datetime(),
            "author": self.get_author(),
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
            return topline_label_raw.strong.text


    def get_shorttext(self):
        shorttext_raw = self.raw_article.find('p', class_=re.compile('^textabsatz'))
        if shorttext_raw == None:
            return None
        else:
            return shorttext_raw.strong.text


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
            return author_raw.find('a').text
        

    def get_subheadlines(self):
        subheadlines_raw = self.raw_article.find_all('h2')
        subheadlines_list = []
        if subheadlines_raw == None:
            return None
        else:
            for subheadline in subheadlines_raw:
                subheadlines_list.append(subheadline.text)
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
        return dt.now().strftime('%Y-%m-%d %H:%M:%S')



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
            datetime_str = datetime_raw.text.strip(" Uhr")
            datetime = dt.datetime.strptime(datetime_str, "%d.%m.%Y • %H:%M")
            return datetime  


if __name__ == "__main__":
    main()