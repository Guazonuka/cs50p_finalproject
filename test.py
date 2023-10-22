import calendar
import datetime as dt
import requests
import sqlite3
import time
import re

from bs4 import BeautifulSoup
from helpers import ScrapeArchive, ScrapeArticle


def main():
    search_string = "klima"
    
    year = 2023

    # Implementing Sqlite3
    con = sqlite3.connect("tagesschau.db")
    db = con.cursor()
    """
    l = range(1, 10)    # last value exclusive!
    for i in l:
        month = i

        num_days = calendar.monthrange(year, month)[1]
        days = [dt.date(year, month, day) for day in range(1, num_days+1)]

        for day in days:
            # Create day string
            date = dt.datetime.strftime(day, '%Y-%m-%d')
            # Create URL
            archive_url = "https://www.tagesschau.de/archiv"
            url_extention = "?datum="
            url = archive_url+url_extention+date
    """
    url = "https://www.tagesschau.de/archiv?datum=2023-09-27"
    date = "2023-09-27"

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
        article_url = teaser["link"]
        a = requests.get(article_url)
        soup = BeautifulSoup(a.text, 'html.parser')
        if soup.find('article') == None:
            continue
        raw_article = soup.find('article')
        seitenkopf = raw_article.find('div', class_=('seitenkopf'))
        topline_label_raw = seitenkopf.find('span', class_=re.compile('label--small'))
        try:
            db.execute("UPDATE articles SET topline_label = ? WHERE url = ?;", [topline_label_raw.strong.text.strip()], [teaser['link']])
        except:
            try:
                db.execute("UPDATE articles SET topline_label = ? WHERE url = ?;", [topline_label_raw.text.strip()], [teaser['link']])
            except:
                db.execute("UPDATE articles SET topline_label = ? WHERE url = ?;", [None, teaser['link']])
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
    

if __name__ == "__main__":
    main()