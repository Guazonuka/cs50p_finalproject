import calendar
import datetime as dt
import requests
import sqlite3
import time

from bs4 import BeautifulSoup
from helpers import ScrapeArchive, ScrapeArticle


def main():
    # Search string
    search_string = "klima"

    # Implementing Sqlite3
    con = sqlite3.connect("tagesschau.db")
    db = con.cursor()

    # Create tables if not exist
    db.execute("CREATE TABLE IF NOT EXISTS articles (url VARCHAR PRIMARY KEY NOT NULL, topline_label TEXT, topline TEXT, headline TEXT, shorttext TEXT, datetime NUMERIC, author TEXT, tags TEXT, word_count INTEGER, matches INTEGER, scraped_dt NUMERIC, department TEXT, categories TEXT);")
    db.execute("CREATE TABLE IF NOT EXISTS articles_content (url VARCHAR PRIMARY KEY NOT NULL, subheadlines TEXT, paragraphs TEXT, scraped_dt NUMERIC);")

    # Create day string (format "YYYY-MM-DD")
    date = "2023-09-11"
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
        db.execute("SELECT COUNT(*) FROM articles WHERE url = ?;", [teaser['link']])
        result = db.fetchone()
        if result:
            continue
        #con.commit()
        #print(num)
        #if db.execute("SELECT COUNT(1) FROM articles WHERE url = ?;", (teaser["link"])) == 1:
            #continue
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
            continue

        try:
            db.execute("INSERT INTO articles_content (url, subheadlines, paragraphs, scraped_dt) VALUES (?, ?, ?, ?);", (article_content_row))
        except sqlite3.IntegrityError:
            continue

        # commit changes to db
        con.commit()

        # sleep counter of 1 second
        #time.sleep(1)
    print(f"On {date} a total of {len(archive.teaser_list)} articles were analysed")

    # Close DB
    con.close()

    # Print list of links that were not analysed
    for link in unused_links:
        print(link)


if __name__ == "__main__":
    main()