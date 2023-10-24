import calendar
import datetime as dt
import requests
import sqlite3
import time
import re
import sys

from bs4 import BeautifulSoup
from helpers import ScrapeArchive, ScrapeArticle


def main():
    # Search string
    search_string = "klima"
    """
    # Select year and month
    year = 2023
    month = 1

    num_days = calendar.monthrange(year, month)[1]
    dt_list = [dt.date(year, month, day) for day in range(1, num_days+1)]
    """
    start_dt = check_start_date()
    end_dt = check_end_date(start_dt)
    print(f"Start date: {start_dt}")
    print(f"End date: {end_dt}")
    dt_list = create_date_list(start_dt, end_dt)
    while True:
        x = input(f"Would you like to scrape {len(dt_list)} days between {start_dt} and {end_dt}? [y|n] ").strip()
        if re.fullmatch("^(y|n)$", x, flags=re.IGNORECASE):    
            if x.lower() == "n":
                sys.exit()
            else:
                break
        else:
            continue

    # Implementing Sqlite3
    #con = sqlite3.connect("tagesschau.db")
    con = sqlite3.connect("test.db")
    db = con.cursor()

    # Create tables if not exist
    db.execute("CREATE TABLE IF NOT EXISTS articles (url VARCHAR PRIMARY KEY NOT NULL, topline_label TEXT, topline TEXT, headline TEXT, shorttext TEXT, datetime NUMERIC, author TEXT, tags TEXT, word_count INTEGER, matches INTEGER, scraped_dt NUMERIC, department TEXT, categories TEXT);")
    db.execute("CREATE TABLE IF NOT EXISTS articles_content (url VARCHAR PRIMARY KEY NOT NULL, subheadlines TEXT, paragraphs TEXT, scraped_dt NUMERIC);")

    for date in dt_list:
        # Create day string
        #date = dt.datetime.strftime(day, '%Y-%m-%d')
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
            # Check if article is a Tagesschau original
            if not teaser["link"].startswith("https://www.tagesschau.de"):
                unused_links.append(teaser["link"])
                continue
            # Skip if article is already in DB
            db.execute("SELECT COUNT(*) FROM articles WHERE url = ?;", [teaser['link']])
            result = db.fetchone()
            if result[0] == 1:
                continue
            article_url = teaser["link"]
            a = requests.get(article_url)
            soup = BeautifulSoup(a.text, 'html.parser')
            if soup.find('article') == None:
                continue
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
                print(f"Article published on {article.article_dict['datetime']} added to DB. Headline: {article.article_dict['headline']}")
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
    if len(unused_links) > 1:
        print(f"The following {len(unused_links)} links are not Tagesschau originals and were not analyzed")
        for link in unused_links:
            print(link)
    elif len(unused_links) == 1:
        print(f"The following link is not a Tagesschau original and was not analyzed")
        for link in unused_links:
            print(link)


def check_start_date():
    while True:
        s = input("Enter first date for analysis (YYYY-MM-DD): ").strip()
        #x = re.fullmatch("(19|20)[0-9]{2}\-(0[1-9]|1[012])\-(0[1-9]|[1-2][0-9]|3[01])", s)
        match = re.fullmatch("20[23][0-9]\-(0[1-9]|1[012])\-(0[1-9]|[1-2][0-9]|3[01])", s)
        if match:
            try:
                dt.date.fromisoformat(s)
            except ValueError:
                print("day is out of range for month")
                continue
            if dt.date.fromisoformat(s) < dt.date.today():
                return s
            else:
                print("Start date needs to be before today's date")
            continue
        else:
            print("Start date not in the correct format or year before 2020")
            continue


def check_end_date(start_dt):   
    while True:
        s = input("Enter last date for analysis (YYYY-MM-DD): ").strip()
        match = re.fullmatch("20[23][0-9]\-(0[1-9]|1[012])\-(0[1-9]|[1-2][0-9]|3[01])", s)
        if match:
            try:
                dt.date.fromisoformat(s)
            except ValueError:
                print("day is out of range for month")
                continue            
            if dt.date.fromisoformat(start_dt) <= dt.date.fromisoformat(s) < dt.date.today():
                return s
            else:
                print(f"End date needs to be before today's date and after {start_dt}")
                continue
        else:
            print("Start date not in the correct format or year before 2020")
            continue


def create_date_list(start_dt, end_dt):
    start_dt = dt.date.fromisoformat(start_dt)
    end_dt = dt.date.fromisoformat(end_dt)
    dt_list = []
    delta = dt.timedelta(days=1)
    while start_dt <= end_dt:
        dt_list.append(start_dt.isoformat())
        start_dt += delta
    return dt_list


if __name__ == "__main__":
    main()