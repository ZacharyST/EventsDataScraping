### importing Scrapy Library

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request

### importing local project support files

from newsScraper.items import NewsscraperItem
from newsScraper.config import Config,html2texthandler

### importing other helpful Python Library

from time import gmtime,strftime 
import re
import requests
import lxml.html
import time

### Spider Class starts From here

class ScrapeCrawler_UPI(Spider):
    
    ### This is Spider Name. Run this Spider as : scrapy crawl UPI -o output.json -t json
    
    name = 'UPI'
    URL = []
 
    def start_requests(self):
        ### This is a loop for keywords you have inserted into your Config.py File.
        
        for Config['keywords'] in Config['keywordsList']:
            
            ### This is a method to extract a single home page using Request Library
            ### The home page does'nt provide any symmetrical method to move on next page.
            ### We are extracting total results found and create next page urls using likely urls patterns  
            #print "http://www.upi.com/search/?ss="+Config['keywords']+"&s_l=articles&&s_term=ea"
        
            res = requests.get("http://www.upi.com/search/?ss=" + Config['keywords'] + "&s_l=articles&&s_term=ea")
            print "\n http://www.upi.com/search/?ss=" + Config['keywords'] + "&s_l=articles&s_term=ea"
            
            ### Converting html into lxml.html format to extract info from the page
            
            webDoc = lxml.html.fromstring(res.text)
            
            ### We find how many pages are available for scraping.
            
            try:
                totalPages = webDoc.xpath("//div[@class='of fll tac']/text()")
                p = re.compile('\d+')
                m = p.findall(totalPages[0])
                Pages = m[1]
                
            ### if TotalPages not found then we assume it has single page only
            
            except:
                Pages = 1
            i=1
            
            ### Creating a custom URL for scraping with the help of Config.py File keywords
            
            while (i<= int(Pages)):
                url = "http://www.upi.com/search/?ss=" + Config['keywords'] + "&s_l=articles&s_term=ea&offset=" + str(i)
                i += 1                                                                        
                
                ###Creating a List of URL to Scrape          
                
                yield Request(url, callback= self.parse)
            ### start_urls contain the list  of url's which are ready for scraping
            #self.start_urls = url
    allowed_domains = ["www.upi.com"]    
    
    
    ### function parse extract all the URL which are available on the current page and store them in a list name as LinkPage
    
    def parse(self,response):
        
        sel = Selector(response)
        Links = sel.xpath("//p[@class='hl']/a/@href").extract()
        
        ### startDate and endDate are the dates defined in config file for filtering the results
        
        startDate =  Config['start_year'] + "/" + Config['start_month'] + "/" + Config['start_day']
        endDate = Config['end_year'] + "/" + Config['end_month'] + "/" + Config['end_day']
        
        ### string to datetime format conversion
        
        startDateObject = time.strptime(startDate,'%Y/%m/%d')
        endDateObject = time.strptime(endDate,'%Y/%m/%d')
        
        for link in Links:
            
            ### extracting the date of article from link to create a filtered search
            
            date = re.search('\d{4}\/\d{2}\/\d{2}',link)
            articleDate = date.group()
            articleDateObject = time.strptime(articleDate,'%Y/%m/%d')
            
            ### iterating loop and requests every URl inside the list linkPage and call the function parseitem to extract the info from that page
            
            if ((startDateObject <= articleDateObject) and (articleDateObject <= endDateObject)):
                
                ### if search is qualified then it allows to request for article
                
                yield Request(link,self.parseitem)

    ### parseitem extract the info from the response requested in parse function
    
    def parseitem(self,response):
        sel = Selector(response)
        item = NewsscraperItem()
        
        ### storing the name of URL in item dictionary
        
        item['url']= response.url
        item['source']= self.name
        
        ### extracting title from the page and checking different xpath for searching the title
        
        item['title']= sel.xpath("//div[@id='c_story']/h1/text()").extract()[0]
        
        ### extracting date from the page using xpath
        
        date = sel.xpath("//div[@class='meta grey']/text()").extract()
        length = len(date)
        
        d = date[length-2].strip().replace(u'|',u'').strip().replace( ' at ',' ')
        
        ### filtering the date from the text 
        
        d = re.sub('.*\s{2,3}?|.* Updated|Updated?',"",d).strip()
        try:
            
            ###string to datetime conversion for formating
            
            f = time.strptime(d,'%B %d, %Y %I:%M %p')
        except:
            
            ### if sept. is inside date then replace it with sep.
            
            d = d.replace('Sept.','Sep.')
            
            ### removing unwanted unicode characters
            
            d = d.decode("ascii", "ignore")
            f = time.strptime(d,'%b. %d, %Y %I:%M %p')
        item['date']=time.strftime(Config['dateformat'],f)
        
        ### extracting the time of scraping of data inside the item
        
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        ### extracting content from the page
        
        x = (sel.xpath("//div[@class='st_text_c']").extract())
        
        ###converting html content to text.
        
        textContent = html2texthandler(x[0])
        
        try:
            splitedContent = textContent.split("(UPI) --")
            content = ''.join(splitedContent[1:]).strip()
        
            ### using regular expression to remove continuous white spaces from the content and replace by single space
        
            item['content']= re.sub(r"[ \t\n\"]", " ",content)
        except:
            item['content'] = textContent
            
        if not item['content']:
            return
        if (item['title'] and item['date'] and item['content']):
            return item
        else:
            
            ### if content not available or it's video or image then it extract nothing
            
            return