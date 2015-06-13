# Scrapy settings for newsScraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'newsScraper'

SPIDER_MODULES = ['newsScraper.spiders']
NEWSPIDER_MODULE = 'newsScraper.spiders' 

###parallel Number of connections
#CONCURRENT_REQUESTS = 16

###Downlaod Delay to delay items
#DOWNLOAD_DELAY= 10

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 Googlebot/2.1 (http://www.nogoogle.com)'
