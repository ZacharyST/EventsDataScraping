#!usr/bin/env python
import sys
import json
import re
import traceback
import sentencer
from unidecode import unidecode
from operator import itemgetter
    
### function to open a file in append mode if no mode is specified
filters = (
            (re.compile("^.*? TYPE: O?CN\s*\)\)", re.IGNORECASE), ""), 
            (re.compile("^.*?new lede,\s+\d+\)\)", re.IGNORECASE), ""), 
            (re.compile("_Some information for this report(.|\r|\n)*",re.IGNORECASE),""),
            (re.compile("(\n|\r)+"), "\n"),
            (re.compile("_NEW:(.|\n|\r)+"), ""),
            (re.compile("_WikiLeaks_"), "WikiLeaks"),
            (re.compile(re.escape("Please turn on JavaScript. Media requires JavaScript to play."),re.IGNORECASE), "")
           )

def filterUnwatedText(text):
    
    #assigning original text to filetered text
    filteredText = text
    
    # filters is a tuple which contain tuples. For traversing each tuple inside filters for loop works.
    for unwantedFilter in filters:
        
        #unwantedFilters[0] select each regular expression string tuple and unwantedFilters[1] select "" for each tuple.
        
        ### This is an example
        # unwantedFilter[0].sub(unwantedFilter[1], filteredText) = re.compile("^.*? TYPE: O?CN\s*\)\)", re.IGNORECASE).sub("", filteredText)
        
        filteredText = unwantedFilter[0].sub(unwantedFilter[1], filteredText)
    return filteredText

def openFile(filename,mode = 'w'):
    handle = open(filename,mode) 
    return handle


### jsonFile accept the command line argument File name 
if (len(sys.argv) != 2 and len(sys.argv) !=3 ):
    print "Syntax: python tabari.py <jsonfile>\n./tabari <jsonfile>  or python tabari.py <jsonfile> <Path>"
    sys.exit(1)
    pass
filePath=""
jsonFile = sys.argv[1]

# Path to save Tabari File
if len(sys.argv)>2:
    filePath = sys.argv[2]
try:
    jsonData = openFile(jsonFile,'r')
except Exception:
    print "Failed to open JSON file"
    sys.exit(1)
    
### Opening three file to write information in Tabari format

tabariFile1 = jsonFile.replace(".json",'1.txt')
tabariFile2 = jsonFile.replace(".json",'2.txt')
tabariFile3 = jsonFile.replace(".json",'3.txt')

#added path with file name to store Tabari Data
if filePath != "":
    tabariFile1 = filePath+tabariFile1
    tabariFile2 = filePath+tabariFile2
    tabariFile3 = filePath+tabariFile3
try:
    articles = json.load(jsonData)
except Exception, e:
    print "Failed to load JSON file. Error: " + str(e)
    sys.exit(1)

### Sorting the JSON file according to date
articles = sorted(articles, key=itemgetter('date')) 

### Opening three files for writing in TABARI format
### File #1 (handle1) will only contain first sentences from each article
### File #2 (handle2) will only contain all sentences from each article
### File #3 (handle3) will only contain title and url of each article
handle1 = openFile(tabariFile1)
handle2 = openFile(tabariFile2)
handle3 = openFile(tabariFile3)

handleErr = openFile("error.txt","a+")


articleSeqNo = 0

import re

def findWholeWord(word,strs):
    exactMatch = False
    exactMatch = re.search(r'\b' + word + r'\b',strs)
    if exactMatch:
        return True
    return False



def check_process_article(source, url, title, content):
    if source == 'Reuters':
        ignoreURL = ['MW','BW']
        ignoreCONTENT = ['PRNewswire','(Reuters Life!)']
        ignoreTITLE = ['UPDATE','REFILE']
        for key in ignoreURL:
            if findWholeWord(key, url):
                return False
            
        for key in ignoreCONTENT:
            if findWholeWord(key, content):
                return False
            
        for key in ignoreTITLE:
            if findWholeWord(key, title):
                return False
        
        if title.startswith("REG ") or title.startswith("RCS ") or title.startswith("DIARY"):
            return False
        
    #[Manoj] If title contain these keywords. Then it is Escaped. 
    elif source == 'UPI':
        ignoreCONTENT = ['COL','NBA ','NHL','MLB','NFL','Nadal','UPI NewsTrack']
        
        for key in ignoreCONTENT:
            if findWholeWord(key, title):
                return False

        for key in ignoreCONTENT:
            if findWholeWord(key,content):
                return False
    #[04/06/2014]manoj
    elif source == 'XNA':
        if title.upper().startswith("FLASH:"):
            return False
    elif source == 'BBC':
        if 'World News for Schools' in title or 'magazine' in url:
            return False
    return True
    pass


for article in articles:
    title = article['title']
    url = article['url']
    source = article['source']
    content = article['content']
    
    if (check_process_article(source, url, title, content) == False):
        continue
    
    article['content'] = unidecode(article['content']).replace('*','').replace('#','')
    article['content'] = filterUnwatedText(article['content'])
    
    article['title'] = unidecode(article['title']).replace('*','').replace('#','')
    preProcessedSentences = sentencer.sentence_segmenter(article['content'])
    
    sentences = []
    
    #Remove quote sentences from sentences
    for sentence in preProcessedSentences:
        sentence = sentence.strip()
        sentenceFirstChar = sentence[0]
        if sentenceFirstChar == "'":
            if "'" in sentence[1:]:
                continue
        elif sentenceFirstChar == "\"":
            if '"' in sentence[1:]:
                continue
        
        if 'View the slide show' in sentence:
            continue
        sentences.append(sentence)
    
    if len(sentences) == 0:
        continue
    #sentences = preProcessedSentences
    
    if 'NEW YORK (Hollywood Reporter)' in sentences[0]:
        continue
    
    if re.match('.*?Reuters -', sentences[0]):
        sentences[0] = re.sub('.*?Reuters -', '', sentences[0])
    
    articleSeqNo += 1
    
    # writing File 1 in tabari Format
    try:
        firstSentence = sentences[0].replace("\n","").replace("\r",'').strip()
        handle1.write(article['date'])
        handle1.write(" ")
        handle1.write(article['source'])
        handle1.write("-%07d-1\n"%articleSeqNo)
        handle1.write(firstSentence)
        handle1.write("\n\n")
        
        
    # If some error occurs in formating the error details will be written in error.txt
    
    except Exception, e:
        tb = traceback.format_exc()
        print (sentences)
        print (article['content'])
        handleErr.write(str(e) + "\t")
        handleErr.write(str(tb) + "\t")
        handleErr.write(article['source'] + "\t")
        handleErr.write(article['title'] + "\t")
        handleErr.write(article['url'] + "\t")
        handleErr.write("-%07d-1-\n"%articleSeqNo)
        
        # Decrement SeqNo by 1 as the article failed to be written
        articleSeqNo -= 1
        continue
        
    # writing file 2 in tabari format
    try:
        sentenceSeqNo = 0
        for sentence in sentences:
            sentenceSeqNo += 1
            handle2.write(article['date'])
            handle2.write(" ")
            handle2.write(article['source'])
            handle2.write("-%07d-%d\n"%(articleSeqNo,sentenceSeqNo))
            handle2.write(sentence.replace("\n",""))
            handle2.write("\n\n")
    except:
        handle2.close()
        
    # writing file 3 in Tabari format
    try:  
        
        handle3.write(article['date'])
        handle3.write(" ")
        handle3.write(article['source'])
        handle3.write("-%07d-1 "%articleSeqNo)
        handle3.write("'"+article['title'].replace("'","\\'").replace('- Xinhua ','').replace("\n",'')+"' ")
        handle3.write(article['url'])
        handle3.write("\n")
    except:
        handle3.close()


###closing all files after finishing formating
handleErr.close()
handle1.close()
handle2.close()
handle3.close()
jsonData.close

print "Conversion Completed Successfully\n"