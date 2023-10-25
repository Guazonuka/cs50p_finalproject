# Tagesschau Scraper
#### Video Demo:  <URL HERE>
#### Description:

## Introduction
This is an application that scrapes news articles from the German media outlet tagesschau.de and analyzes the reference to the copic of the climate crisis.

### Background
The unfolding climate crisis is not a news event but rather a process that will concern us for all our lifetime. What we know about it - much like what we know about anything on society or nature - we gather from media. How has the media coverage on climate crisis changed over the course of the years? This project allows to analyze the treatment of this topic in news articles published by the German media outlet Tagesschau which is part of the German public broadcasting system.

### Scope of project
The goal of this project was to develop an app that would request all articles published on tagesschau.de within a given period, check them for their connection to the climate crisis, and then write the results to a database.

## Methodology
The vast majority of key words in the German language related to the topic of climate crisis entail the letter sequence "klima" ("climate"). These include words such as "Klimakrise" (climate crisis), "Klimawandel" (climate change), "Weltklimarat" (international panel on climate change), "klimaschädlich" (climate-damaging) etc. It is assumend that articles which relate to the topic of climate crisis will include the string "klima".

## Implementation
The project consists of an application that can be launched and controlled from the terminal as well as a database to which article content and analysis results are written.

### Files in base directory
The project consists of two .py files. In addition it will require a sqlite3 database.

#### project.py
Handles the entire scraping process and includes all functions and classes.
Required modules are listed in requirements.txt.
In essence the program executes the following steps:
* Upon launching the app the user is requested to enter a start and an end date to specify the analysis period. The related functions will only accept dates after the year 2019.
* Inproper formats or illogical dates will be rejected and the user is prompted to enter dates again.
* The programm connects to the database and creates two tables:
 * "article"
 * "article_content"
* Next a list of dates will be created will encompass the starting and end date as well as all dates in between.
* The dates in this list will be used to create a url for each day of analysis in a for loop.
* Each url will be requested
* For each url the ScrapeArchive class is called which will receive the HTML-content as well as the search_string ("klima") and date
* ScrapeArchive will essentially scrape all urls for articles published on that date and return a list with a dict for each url
* The dict includes some teaser information for each article such as
 * url to full article
 * topline
 * headline
 * teaser text
 * date and time of publication
* Next the class ScrapeArticle will be called for each article url found on each date
* ScrapeArticle analyzes the actual article and looks for matches of the search string in
 * topline
 * headline
 * teaser text
 * subheadlines
 * paragraphs
* each word will be counted
* each search_string match will be counted
* additonal meta information such as news department, labels and tags will be scraped
* the scraped data will be inserted into the two database tables - one row for each article

#### test_project.py


#### database
The default sqlite3 database to connect to is called "test.db" in the project directory.


## Challenges

## Possible improvements for future versions

* use a GUI
* updating analysis