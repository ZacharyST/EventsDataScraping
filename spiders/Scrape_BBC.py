### importing Scrapy Library

from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.http.response import Response

from scrapy.spider import Spider

### importing local project support files


from newsScraper.items import NewsscraperItem
from newsScraper.config import Config,html2texthandler

### importing other helpful Python Library

from time import strftime,strptime,gmtime
import re
import urlparse

###these are library not in active mode
                                                
from readability import Document
import logging

### Spider Class starts From here

class ScrapeCrawler_BBC(Spider):
    
    ### This is Spider Name. Run this Spider as : scrapy crawl BBC -o output.json -t json
    
    name = "BBC"
    
    ### start_urls is a empty list.
    
    start_urls = []
    allowed_domains = ['www.bbc.co.uk', 'news.bbc.co.uk']
    
    ###this is a loop for keyword which generate the custom URL for scraping 
    
    for Config['keywords'] in Config['keywordsList']:
        
        ### start_urls is appended by custom urls for scraping. 
        
        start_urls.append("http://www.bbc.co.uk/search/news/?q=" + Config['keywords'] \
                          + "&text=on&sort=date&start_day=" + Config['start_day'] \
                          + "&start_month=" + Config['start_month'] \
                          + "&start_year=" + Config['start_year'] \
                          + "&end_day=" + Config['end_day'] \
                          + "&end_month=" + Config['end_month'] \
                          + "&end_year=" + Config['end_year'])
    

    ### function parse extract all the URL which are available on the current page and store them in a list name as LinkPage
        
    def parse(self,response):
        ':type response: Response'
        sel = Selector(response)
        
    ### extracting the links of article pages and next page
    
        pageLink = sel.xpath(".//*[@id='news-content']//a[starts-with(@class,'title')]/@href").extract()
        nextLink = sel.xpath("//a[@id='next']/@href").extract()
        for page in pageLink:
            
            if not('/school_report/' in page or 'magazine' in page):
                
            ### requesting the article pages
             
                yield Request(page,self.parseitem)
            
        ### requesting the next page after scraping all articles.
        
        if nextLink:
            yield Request(urlparse.urljoin(response.url,nextLink[0]),self.parse)
    
    ### parseitem extract the info from the response requested in parse function
    
    def parseitem(self,response):
        ':type response: Response'

        if 'Please turn on JavaScript' in response.body:
            body = response.body
            body = re.sub('<p class="caption"[^<]+', '', body)
            body = re.sub('<noscript>(.|\r|\n)*?</noscript>','',body)

            response = response.replace(body=body)

        sel =  Selector(response)
        item = NewsscraperItem()

        
        ### storing the name of URL and source in item dictionary
         
        item['url']= response.url
        item['source']= self.name
        
        ### extracting the time of scraping of data inside the item
        
        item['dateScraped']= strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        ### checking for url category defined in allowed domain. If response.url contain the string then move in otherwise in else condition
        try:  
            if 'www.bbc.co.uk' in response.url:
                
                ### extracting title
                title = sel.xpath("//h1[starts-with(@class,'story')]/text()").extract()
                if(title):
                    
                    ### extracting title from the page and checking different xpath for searching the title
                    
                    item['title']=title[0].strip()
                    
                    ### extracting date from the page using xpath
                    
                    d = sel.xpath("//span[@class='date']/text()").extract()[0].strip()
                    
                    ###string to datetime conversion
                    
                    f = strptime(d,'%d %B %Y')
                    
                    ###formating date in a particular format defined in config file  
                    
                    item['date']= strftime(Config['dateformat'],f)
                
                    ### extracting content from the page
                    
                    x = sel.xpath("(//div[@class='story-body']//*[self::p or self::strong]/text()) |(//span[@class='cross-head']/text())|(//div[@class='story-body']/p/a/text())").extract()
                    if len(x) > 1:
                        st="\n"
                        p = st.join(x)
                        
                        ### using regular expression to remove continuous white spaces from the content and replace by single space
                        
                        item['content']= re.sub(r"[ \t\n]+", " ",p)
                    else:
                        # Not able to extract article content using xpath. Move to backup approach and use readability
                        try:
                            html = sel.xpath("//div[@class = 'story-body']").extract() 
                            doc = Document(html)
                            doc.options['debug'] = False
                            
                            try:
                                logging.basicConfig(level=logging.CRITICAL)

                                htmlContent = doc.summary()                    
                                content = html2texthandler(htmlContent)
                            except Exception, e:
                                pass
                            finally:
                                logging.basicConfig(level=logging.INFO)

                            item['content']= re.sub(r"[ \t\n\"]", " ",content)
                        except:
                            return 
                        
                    if (item['content']!="" and item['title']!="" and item['date']):
                        return item
                    else:
                        return
                
                ### if format of page different then move to new syntax to extract data
                
                else:
                    
                    ### extracting title from the page and checking different xpath for searching the title
                    
                    item['title'] = sel.xpath("//div[@class='story-inner']/h1/text()").extract()[0].strip()
                    
                    ### extracting date from the page using xpath
                    
                    d = sel.xpath("//p[starts-with(@class,'date')]/strong/text()").extract()[0].strip()
                    f = strptime(d,'%d %B %Y')
                    item['date']= strftime(Config['dateformat'],f)
                
                    ### extracting content from the page
                    try:
                        x = (sel.xpath("(//div[@class='story-inner']/p/text()) |(//h2[@class='heading']/text())").extract())
                        joiner = "\n"
                        p = joiner.join(x)
                    
                        ### using regular expression to remove continuous white spaces from the content and replace by single space
                    
                        item['content']= re.sub(r"[ \t\n]+", " ",p)
                    except:
                        try:
                            html = sel.xpath("//div[@class = 'story-body']").extract() 
                            logging.basicConfig(level=logging.CRITICAL)
                            doc = Document(html)
                            htmlContent = doc.summary()                    
                            content = html2texthandler(htmlContent)
                            item['content']= re.sub(r"[ \t\n\"]", " ",content)
                        except:
                            print"image coontent"
                            return 
                        finally:
                            logging.basicConfig(level=logging.INFO)

                    if (item['content']!="" and item['title']!="" and item['date']!="" ):
                        return item
                    else:
                        return
            ### if url is of second category then else condition take care of that
               
            else:
                
                title = sel.xpath("//div[@class='mxb']/h1/text()").extract()
                if(title):
                    
                    ### extracting title from the page and checking different xpath for searching the title
                    
                    item['title']=title[0].strip()
                    
                    ### extracting date from the page using xpath
                    try:
                        d = sel.xpath("//div[@class='ds']/text()").extract()[0].strip()
                    except:
                        return
                    try:
                        f = strptime(d,'%H:%M GMT, %A, %d %B %Y')
                    except:
                        d = d.split(" ")
                        d = ' '.join(d[0:6])
                        f = strptime(d,'%H:%M GMT, %A, %d %B %Y')
    
                    item['date']= strftime(Config['dateformat'],f)
                
                    ### extracting content from the page
                    try:
                        x = sel.xpath("(//td[@class='storybody']/p/b/text())|(//td[@class='storybody']/p/text())").extract()
                        st="\n"
                        p = st.join(x)
                        
                        ### using regular expression to remove continuous white spaces from the content and replace by single space
                        
                        item['content']= re.sub(r"[ \t\n]+", " ",p)
                    except:
                        try:
                            html = sel.xpath("//div[@class = 'story-body']").extract() 
                            logging.basicConfig(level=logging.CRITICAL)
                            doc = Document(html)
                            htmlContent = doc.summary()                    
                            content = html2texthandler(htmlContent)
                            item['content']= re.sub(r"[ \t\n\"]", " ",content)
                        except:
                            return
                        finally:
                            logging.basicConfig(level=logging.INFO)
                            
                    if (item['content']!="" and item['title']!="" and item['date']!=""):
                        return item
                    else:
                        return
        except:
            return