import typing
import requests

from bs4 import BeautifulSoup

def main():
    url: int = input("Enter Tagesschau-URL: ")
    print(url)
    r: int = requests.get(url)
    print(r.status_code)


if __name__ == "__main__":
    main()