### importing Scrapy Library

from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.exceptions import CloseSpider

### importing local project support files

from newsScraper.items import NewsscraperItem
from newsScraper.config import Config,html2texthandler

### importing other helpful Python Library

from time import gmtime,strftime,strptime
import re
### Spider Class starts From here

class spider(CrawlSpider):
    
    ### This is Spider Name. Run this Spider as : scrapy crawl Reuters -o output.json -t json
     
    name = 'Reuters'
    urls = []

    ### This is a loop for keywords you have inserted into your Config.py File.
    

    
    ### start contain the starting and last contain the end year for example start = '2010' and last = '2014'
     
    start = int(Config['start_year'])
    last = int(Config['end_year']) + 1

    
    ### Creating custom URLs for scraping with the help of Config.py File keywords
    
    while(start !=  last):
        yearURL = "http://www.reuters.com/resources/archive/us/"+ str(start) + ".html"
        start+=1
        
        ###Creating a List of URL to Scrape          
        urls.append(yearURL)
    
   
    ### Only those url will be allowed for scraping which are defined in the allowed domain list
    
    allowed_domains = ["www.reuters.com"]
    
    ### start_urls contain the list  of url's which are ready for scraping
      
    start_urls = urls
    
    ### rule is a standard way to follow the link which have some unique syntax

    rules =(
        Rule(
            SgmlLinkExtractor(allow=('\d+\.html$',)
            ,restrict_xpaths=(".//div[@class='moduleBody']//p",))
            ,callback = 'parselink', follow=True)
        ,)

    ### function parselink extract all the URL of article whcih are available on the current page and store them in a list name as LinkPage
    
    def parselink(self,response):
        sel = Selector(response)
        mainLinks = sel.xpath("//div[@class='headlineMed']/a/@href").extract()
        
        ### startDate and endDate are the dates you have entered in config file
        
        startDate =  Config['start_year'] + "/" + Config['start_month'] + "/" + Config['start_day']
        endDate = Config['end_year'] + "/" + Config['end_month'] + "/" + Config['end_day']
        
        ###Dates are in string format converting them into time date format for comparison
        
        startDateObject = strptime(startDate,'%Y/%m/%d')
        endDateObject = strptime(endDate,'%Y/%m/%d')
        
        for link in mainLinks:
            testforVideoLink = link.find("video")
            
            ### discarding the urls which contains videos
            
            if (testforVideoLink == -1):
                ### iterating loop and requests every URl inside the list mainLinks and call the function parsemyitem to extract the info from that page
                ### extracting the date from urls
                
                date = re.search('\d{4}\/\d{2}\/\d{2}',link)
                articleDate = date.group()
                articleDateObject = strptime(articleDate,'%Y/%m/%d')
            
            ### request to the article page if the current article url qualify the search criteria  
            
                if ((startDateObject <= articleDateObject) and (articleDateObject <= endDateObject)):
        
                    yield Request(link,self.parsemyitem)
               
                
    
    ### parseitem extract the info from the response requested in parse function            
            
    def parsemyitem(self,response):
        sel = Selector(response)
        item = NewsscraperItem() 
        
        ### storing the name of URL in item dictionary
        
        item['url']= response.url
        item['source']= self.name
        
        ### extracting title from the page and checking different xpath for searching the title
        
        item['title']= sel.xpath("//div[@class='column1 gridPanel grid8']/h1/text()").extract()[0]
        
        ### extracting date from the page using xpath
        
        d = sel.xpath("(//span[@class='timestamp']/text())[1]").extract()[0]
        try:
            f = strptime(d,'%a %b %d, %Y %I:%M%p EDT')
        except:
            f = strptime(d,'%a %b %d, %Y %I:%M%p EST')
        item['date']=strftime(Config['dateformat'],f)
        
        ### extracting the time of scraping of data inside the item
        
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        ### extracting content from the page
        
        x = (sel.xpath("//span[@id='articleText']").extract())
        
        ###converting html content to text.
        
                
        p = html2texthandler(x[0])
        
        ### using regular expression to remove continuous white spaces from the content and replace by single space
        item['content']= None
        contentText = re.sub(r"[ \t\n]+", " ",p)
        for key in Config['keywordsList']:
            if key in contentText:
                if '(Reuters) -' in contentText:
                    print "\n"+key
                    content = contentText.split("(Reuters) -")
                    if (len(content)>2):
                        i=1
                        while(i < len(content)):
                            contentText += content[i]
                            i += 1
                    else:
                        
                        contentText = content[1]
            
                item['content']= contentText
                
                #this article has the keyword
                break
        
          
        if (item['title'] and item['date'] and item['content']!= None):
            return item
        else:
            
            ### if content not available or it's video or image then it extract nothing
            
            return