### importing Scrapy Library

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request

### importing local project support files

from newsScraper.items import NewsscraperItem
from newsScraper.config import Config,html2texthandler

### importing other helpful Python Library

from time import gmtime,strftime 
import html2text
import requests
import lxml.html
import re
import time
import readability

### Spider Class starts From here

class ScrapeCrawler_XNA(Spider):

    ### This is Spider Name. Run this Spider as : scrapy crawl XNA -o output.json -t json       
    
    name = 'XNA'
    
    ### This is a loop for keywords you have inserted into your Config.py File.

    def start_requests(self):
        for Config['keywords'] in Config['keywordsList']:
    
            ### This is a method to extract a single home page using Request Library    
            
            res = requests.get("http://search.news.cn/language/search.jspa?page=1&id=en&t2s="+Config['start_year']+"-"+Config['start_month']+"-"+Config['start_day']+"&t2e="+Config['end_year']+"-"+Config['end_month']+"-"+Config['end_day']+"&rp=50&n1="+Config['keywords']+"&n2=&n3=&ct=&np=content&ss=-PubTime&t1=0&t=2")
            print "\nhttp://search.news.cn/language/search.jspa?page=1&id=en&t2s="+Config['start_year']+"-"+Config['start_month']+"-"+Config['start_day']+"&t2e="+Config['end_year']+"-"+Config['end_month']+"-"+Config['end_day']+"&rp=50&n1="+Config['keywords']+"&n2=&n3=&ct=&np=content&ss=-PubTime&t1=0&t=2"
            ### Converting html into lxml.html format to extract info from the page
    
            webDoc = lxml.html.fromstring(res.text)
            try:
                totalPages = webDoc.xpath("//td[text()[contains(.,'results found')]]/text()")[0]
                if totalPages:
                    list = totalPages.split()
                    totalResults = list[0].replace(',','')
    
                ### We find how many pages are available for scraping. It's divide by 50 because the site shows 50 results per pages.
                
                    Remainder = int(totalResults)%50
                    Pages = int(totalResults)/50
                    if (Remainder != 0):
                        Pages += 1 
                
                    else:
                
                        break
            except:
                Pages =1
            
            ### i is counter reference variable
            i=1
            
            ### Looping the Spiders for Total Pages Available
            
            while (i <= Pages):
                
                ### Creating a custom URL for scraping with the help of Config.py File keywords
                
                url= "http://search.news.cn/language/search.jspa?page="+str(i)+"&id=en&t2s="+Config['start_year']+"-"+Config['start_month']+"-"+Config['start_day']+"&t2e="+Config['end_year']+"-"+Config['end_month']+"-"+Config['end_day']+"&rp=50&n1="+Config['keywords']+"&n2=&n3=&ct=&np=content&ss=-PubTime&t1=0&t=2"
                i+=1
                
                ###Creating a List of URL to Scrape            
    
                yield Request(url,self.parse)
    
    allowed_domains = ["search.news.cn","news.xinhuanet.com"]
        
        ### start_urls contain the list  of url's which are ready for scraping
        
   
            
    ### function parse extract all the URL which are available on the current page and store them in a list name as pageLink
        
    def parse(self,response):
        sel = Selector(response)
        pageLink = sel.xpath("//span[@class='style1a']/a/@href").extract()
        
        ### iterating loop and requests every URl inside the list pageLInk and call the function parseitem to extract the info from that page         
  
        for page in pageLink:
            if '/video/' not in page:
                yield Request(page,self.parseitem)
                    
    ### parseitem extract the info from the response requested in parse function                       
                    
    def parseitem(self,response):
        sel = Selector(response)
        item = NewsscraperItem()
        
        ### storing the name of URL in item dictionary            
        
        item['url']= response.url
        item['source']= self.name
                  
        
        ### extracting date from the page using xpath            

        date= sel.xpath("//*[contains(text(), ':' )and contains(text(), '-' ) and text()[string-length() < 30]]/text()").extract()
        if date:
            d = date[0].strip()
            f = time.strptime(d,'%Y-%m-%d %H:%M:%S')
            item['date']=time.strftime(Config['dateformat'],f)
            
        ### extracting the time of scraping of data inside the item
            
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())

        ### extracting content from the page
        
        x = (sel.xpath("//html").extract())
    
        ### reading html response of the page    
            
        html = readability.Document(x[0])
        htmlContent = html.summary()
        
        ###converting html content to text.

        textContent = html2texthandler(htmlContent)
        
        try:
            splitedContent = textContent.split("--")
            content = splitedContent[1].strip()
        
            ### using regular expression to remove continuous white spaces from the content and replace by single space
        
            item['content']= re.sub(r"[ \t\n\"]", " ",content)
        except:
            item['content'] = textContent
            
        if not item['content']:
            return
        ### extracting title from the page and checking different xpath for searching the title
        try:
            title = sel.xpath("//div[@id='Title']/text()").extract()
            
        ### 04/06/14 manoj(',' issue)
        
            title=''.join(title)
            item['title'] = title.strip()
        except:
            
            htmlTitle = html.short_title()
            rawTitle = html2text.html2text(htmlTitle).strip()
            splitedTitle = rawTitle.split("_")
            title = splitedTitle[0]
            item['title'] = title.strip()
        if(item['date']!="" and item['title']!="" and item['content']!=""):
            return item
        
    