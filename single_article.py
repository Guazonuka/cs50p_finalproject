import calendar
import datetime as dt
import requests
import sqlite3
import time
import re

from bs4 import BeautifulSoup
from helpers import ScrapeArchive, ScrapeArticle


def main():
    # Search string
    search_string = "klima"

    # Url
    url = "https://www.tagesschau.de/ausland/europa/egmr-klimaklagen-100.html"
    url = "https://www.tagesschau.de/inland/innenpolitik/kindergrundsicherung-paus-102.html"

    if re.search("^https?://", url):
        print("secure")
    else:
        print("insecure or invalid")


    # Request url and get bs4soup
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    soup = BeautifulSoup(r.text, 'html.parser')   

    # Solved
    shorttext_raw = soup.find('p', class_=re.compile('^textabsatz'))
    try:
        print(shorttext_raw.strong.text.strip())
    except AttributeError:
        try:
            print(shorttext_raw.text.strip())
        except:
            print("No Shorttext")


    # Solved
    taglist_raw = soup.find('ul', class_='taglist')
    tags_list = []
    try:
        tag_link_list_raw = taglist_raw.find_all('a')
    except AttributeError:
        print(tags_list)
    else:
        for tag in tag_link_list_raw:
            tags_list.append(tag.text.strip())


    seitenkopf = soup.find('div', class_=re.compile('seitenkopf'))
    print(seitenkopf)
    topline_label_raw = seitenkopf.find('span', class_=re.compile('label--small'))
    print(type(topline_label_raw))
    if topline_label_raw == None:
        print("no label found")
    else:
        print(topline_label_raw.strong.text.strip())


    if soup.find('article') == None:
        print("no article tag")
    #tag_article = soup.find('article')
    #print(tag_article)


if __name__ == "__main__":
    main()