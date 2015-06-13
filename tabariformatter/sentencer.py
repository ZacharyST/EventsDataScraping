import re

headerflags = ['LENGTH', 'SECTION', 'BYLINE', 'DATELINE']  # various indicators we are past the headline

datepat = re.compile(',? \w+day[^.]')    # used to isolate '%B %d, %Y' across various date line formats
terpat = re.compile('[\.\?!]\s+[A-Z\"\d+(]')    # sentence termination pattern used in sentence_segmenter(paragr)

MIN_SENTLENGTH = 20   # this is relatively high because we are only looking for sentences that will have subject and object
MAX_SENTLENGTH = 512
STORY_LINE_SIZE = 64  # first line following a header greater than this length is start of story

#source: LbjNerTagger1.11.release/Data/KnownLists/known_title.lst from University of Illinois with editing
ABBREV_LIST = ['mrs.', 'ms.', 'mr.', 'dr.', 'gov.', 'sr.', 'rev.',  'r.n.', 'pres.', 
    'treas.', 'sect.', 'maj.', 'ph.d.', 'ed. psy.', 'proc.', 'fr.', 'asst.', 'p.f.c.', 'prof.', 
    'admr.', 'engr.', 'mgr.', 'supt.', 'admin.', 'assoc.', 'voc.', 'hon.', 'm.d.', 'dpty.', 
    'sec.', 'capt.', 'c.e.o.', 'c.f.o.', 'c.i.o.', 'c.o.o.', 'c.p.a.', 'c.n.a.', 'acct.', 
    'llc.', 'inc.', 'dir.', 'esq.', 'lt.', 'd.d.', 'ed.', 'revd.', 'psy.d.', 'v.p.', 
    'senr.', 'gen.', 'prov.', 'cmdr.', 'sgt.', 'sen.', 'col.', 'lieut.', 'cpl.', 'pfc.', 
    'k.p.h.', 'cent.', 'deg.', 'doz.', 'Fahr.', 'Cel.', 'F.', 'C.', 'K.', 'ft.', 'fur.', 
    'gal.', 'gr.', 'in.', 'kg.', 'km.', 'kw.', 'l.', 'lat.', 'lb.', 'lb per sq in.', 
    'long.', 'mg.', 'mm.,, m.p.g.', 'm.p.h.', 'cc.', 'qr.', 'qt.', 'sq.', 't.', 'vol.', 
    'w.', 'wt.', 'u.s.','u.n.', 'p.j.','st.','d.c.', 'jan.' ,'feb.', 'mar.','apr.', 'may.', 'jun.', 'jul.', 'aug.', 'sep.', 'oct.','nov.','dec.']
    
### function to break the paragraph into sentences 
           
def sentence_segmenter(paragr):
    """ Breaks the string 'paragraph' into a list of sentences based on the following rules
    1. Look for terminal [.,?,!] followed by a space and [A-Z\d+]
    2. If ., check against abbreviation list ABBREV_LIST: Get the string between the . and the
       previous blank, lower-case it, and see if it is in the list. Also check for single-
       letter initials. If true, continue search for terminal punctuation
    3. Extend selection to balance (...) and "...". Reapply termination rules
    4. Add to sentlist if the length of the string is between MIN_SENTLENGTH and MAX_SENTLENGTH 
    5. Returns sentlist """

#    ka = 0
#    print '\nSentSeg-Mk1'
    sentlist = []
    searchstart = 0  # controls skipping over non-terminal conditions
    terloc = terpat.search(paragr)
    while terloc:
#        print 'Mk2-0:', paragr[:terloc.start()+2]
        isok = True
        if paragr[terloc.start()] == '.':
            if (paragr[terloc.start()-1].isupper() and 
                paragr[terloc.start()-2] == ' '):  isok = False   # single initials
            else:
                loc = paragr.rfind(' ',0,terloc.start()-1)   # check abbreviations
                if loc > 0:
#                    print 'SentSeg-Mk1: checking',paragr[loc+1:terloc.start()+1]
                    if paragr[loc+1:terloc.start()+1].lower() in ABBREV_LIST: 
#                        print 'SentSeg-Mk2: found',paragr[loc+1:terloc.start()+1]
                        isok = False
        if paragr[:terloc.start()].count('(') != paragr[:terloc.start()].count(')') :  
#            print 'SentSeg-Mk2: unbalanced ()'
            isok = False
        if paragr[:terloc.start()].count('"') % 2 != 0  :
#            print 'SentSeg-Mk2: unbalanced ""'
            isok = False
        if isok:
            if (len(paragr[:terloc.start()]) > MIN_SENTLENGTH and   
                len(paragr[:terloc.start()]) < MAX_SENTLENGTH) :
                sentlist.append(paragr[:terloc.start()+2])
#                print 'SentSeg-Mk3: added',paragr[:terloc.start()+2]
            paragr = paragr[terloc.end()-1:]
            searchstart = 0
        else: searchstart = terloc.start()+2 
 
#        print 'SentSeg-Mk4:',paragr[:64]
#        print '            ',paragr[searchstart:searchstart+64]
        terloc = terpat.search(paragr,searchstart)
#        ka += 1
#        if ka > 16: sys.exit()

    if (len(paragr) > MIN_SENTLENGTH and len(paragr) < MAX_SENTLENGTH) :  # add final sentence 
        sentlist.append(paragr) 
        
    if len(sentlist) == 0:
        sentlist = [paragr]
    return sentlist
