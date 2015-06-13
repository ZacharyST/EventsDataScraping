# EventsDataScraping

These files constitute a basic events coded I made in May and June
2014.  The first part is a web crawler.  It visits the Associated
Press, BBC, Reuters, UPI, VOA, and XNA and downloads articles based on
user-defined dates and search terms.  It creates one JSON file per
source per query.  The second part is a formatter that takes each
article, a dictionary in each JSON file, and creates a text file
formatted to be read by TABARI, Phil Schrodt’s program that creates
events data from news articles.  The user must install TABARI on their
own.
