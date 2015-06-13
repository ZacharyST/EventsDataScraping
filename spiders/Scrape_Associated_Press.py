### importing Scrapy Library

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request

### importing local project support files

from newsScraper.items import NewsscraperItem
from newsScraper.config import Config, html2texthandler

### importing other helpful Python Library

from time import gmtime,strftime,strptime 
import html2text
import re

### Spider Class starts From here

class ScrapeCrawler_AP(Spider):
    
    ### This is Spider Name. Run this Spider as : scrapy crawl AP -o output.json -t json
    
    name = 'AP'
    
    ### This is a loop for keywords you have inserted into your Config.py File.
    
    for Config['keywords'] in Config['keywordsList']:
        i=0
        URL=[]
        
        ### Creating a custom URL for scraping with the help of Config.py File keywords.
        ### As the uncertainty of the page how many result it will display i chose it will show max 40 pages. 
        ### You can change it as your need. 
        
        while(i<15):
            url = "http://www.apnewsarchive.com/NewsArchive/MainPage.aspx#?SearchText="+Config['keywords']+"&Display=&start="+str(i)+"&num=10"
            i +=10
            
            ###Creating a List of URL to Scrape          
            
            URL.append(url)
        
    allowed_domains = ["www.apnewsarchive.com"]
        
        ### start_urls contain the list  of url's which are ready for scraping
        
    start_urls = URL
        
        ### function parse extract all the URL which are available inside frame on the current page and store them in a list name as LinkPage
        
    def parse(self,response):
           
        i=0
        URL=[]
        while(i<400):
            url = "http://www.apnewsarchive.com/NewsArchive/SearchResults.aspx?SearchText="+Config['keywords']+"&Display=&start="+str(i)+"&num=10"
            print url
            i +=10
            URL.append(url)
            for framelink in URL:
                yield Request(framelink,self.parselink)
                    
        ### function parselink extract all the URL which are available on the current frame page and store them in a list name as pageLink
            
    def parselink(self,response):
        sel= Selector(response)
        nextPageMark = sel.xpath("//a[@class='pgLnk']").extract()
        if (nextPageMark):
            pageLink = sel.xpath("//span[@class='refTxt']/text()").extract()
            for link in pageLink:
                year = re.search('\d{4}',link)
                articleYear = year.group()
                if(int(Config['start_year']) <= int(articleYear)<= int(Config['end_year'])):  
        ### iterating loop and requests every URl inside the list linkPage and call the function parseitem to extract the info from that page
                    
                    yield Request(link,self.parseitem)
        
        ### parseitem extract the info from the response requested in parselink function
            
    def parseitem(self,response):
        sel = Selector(response)
        item = NewsscraperItem()
            
        ### storing the name of URL in item dictionary
                    
        item['url']= response.url
        item['source']= self.name
            
        ### extracting title from the page and checking different xpath for searching the title
            
        item['title']= sel.xpath("//h1[@class='ap_headTitle']//span/text()").extract()[0]
            
        ### extracting date from the page using xpath
            
        d = sel.xpath("//strong[@class='ap_dt_stmp']/span/text()").extract()[0].strip()
        f = strptime(d,'%b. %d, %Y')
        item['date'] = strftime(Config['dateformat'],f)
            
            ### extracting the time of scraping of data inside the item
            
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())
            
        ### extracting content from the page
            
        x = (sel.xpath("//span[@id='dateLine']/ancestor::div[1]").extract())
            
            ###converting html content to text.
            
        p = html2texthandler(x[0])
            
            ### using regular expression to remove continuous white spaces from the content and replace by single space
            
        item['content']= re.sub(r"[ \t\n]+", " ",p)
        if (item['title'] and item['date'] and item['content']):
            return item
        else:
                
            ### if content not available or it's video or image then it extract nothing
                
            return