### importing Scrapy Library

from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.spider import Spider

### importing local project support files

from newsScraper.items import NewsscraperItem
from newsScraper.config import Config,html2texthandler

### importing other helpful Python Library

from time import gmtime,strftime 
import requests
import lxml.html
import re
import time
### Spider Class starts From here

class ScrapeCrawler_VOA(Spider):

    ### This is Spider Name. Run this Spider as : scrapy crawl VOA -o output.json -t json  
     
    name = 'VOA'
    URL = []
    ### This is a loop for keywords you have inserted into your Config.py File.
    def   start_requests(self):
        for Config['keywords'] in Config['keywordsList']:
            
            ### This is a method to extract a single home page using Request Library
            ### The home page does'nt provide any symmetrical method to move on next page.
            ### We are extracting total results found and create next page urls using likely urls patterns  
            
      
            res = requests.get("http://www.voanews.com/search/search.aspx?st=article&k="+Config['keywords']+"&df="+Config['start_month']+"/"+Config['start_day']+"/"+Config['start_year']+"&dt="+Config['end_month']+"/"+Config['end_day']+"/"+Config['end_year']+"&ob=dt#article")
            
            ### Converting html into lxml.html format to extract info from the page
            
            webDoc = lxml.html.fromstring(res.text)
        
            ### We find how many pages are available for scraping.
            try:
                pages = webDoc.xpath("//div[@id='search-results']/p/a[last()-1]/text()")[0]
            except:
                pages = 1
            i=1
            #URL = []
            
            ### Loop to generate start_urls list for scraping
            ### Creating a custom URL for scraping with the help of Config.py File keywords 
            
            while(i <= int(pages)):
                url = "http://www.voanews.com/search/search.aspx?st=article&k=" + Config['keywords'] \
                        + "&df=" + Config['start_month'] + "/" + Config['start_day'] + "/" + Config['start_year'] \
                        + "&dt=" + Config['end_month'] + "/" + Config['end_day'] + "/" + Config['end_year'] \
                        + "&ob==dt&p="+str(i)
                i += 1
                
                ###Creating a List of URL to Scrape          
                
                yield Request(url, callback= self.parse)
    allowed_domains = ["www.voanews.com"]  
    
    ### start_urls contain the list  of url's which are ready for scraping
    
    start_urls = URL
    
    ### function parse extract all the URL which are available on the current page and store them in a list name as LinkPage
    
    def parse(self, response):
        sel = Selector(response)
        linkPage= sel.xpath("//div[@id='search-results']/div/h3/a/@href").extract()
        for link in linkPage:
            
            ### iterating loop and requests every URl inside the list linkPage and call the function parseitem to extract the info from that page
            
            yield Request("http://www.voanews.com"+link,self.parsemyitem)
            
    ### parseitem extract the info from the response requested in parse function
         
    def parsemyitem(self,response):
        sel = Selector(response)
        item = NewsscraperItem() 
        
        ### storing the name of URL in item dictionary
        
        item['url']= response.url
        item['source']= "Voice of America"
        
        ### extracting title from the page and checking different xpath for searching the title
        
        item['title']= sel.xpath("//div[@id='article']/h1/text()").extract()[0].strip()
        
        ### extracting date from the page using xpath
         
        d = sel.xpath("//p[@class='article_date']/text()").extract()[0].strip()
        d = re.sub('.*\s{2,3}?|.* updated on:|Updated?',"",d).strip()
        f = time.strptime(d,'%B %d, %Y %H:%M %p')
        item['date']=time.strftime(Config['dateformat'],f)
        
        ### extracting the time of scraping of data inside the item
        
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        ### extracting content from the page
        
        try:
            x = (sel.xpath("//div[@class='zoomMe']").extract())
            if x:
                p = html2texthandler(x[0])
                item['content']= re.sub(r"[\*\t\n]+", " ",p)
                if(item['date']!="" and item['title']!="" and item['content']!=""):
                    return item
            else:
                x = (sel.xpath("//div[@class='zoomMe']/p[1]").extract())
                
                if x:
                ###converting html content to text.
                
                    p = html2texthandler(x[0])
                
                    ### using regular expression to remove continuous white spaces from the content and replace by single space
                
                    item['content']= re.sub(r"[ \t\n]", " ",p)
                    if(item['date']!="" and item['title']!="" and item['content']!=""):
                        return item
                else:
                        ### if content not available or it's video or image then extract nothing
                    return
        except:
            pass
