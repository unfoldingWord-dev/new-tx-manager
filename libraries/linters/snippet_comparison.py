'''
   snippet_comparison.py
'''

import re
from libraries.door43_tools import bible_books
from libraries.general_tools import url_utils

class snippet_comparison(object):
    def __init__(self,book,chap,chnk):
        self.book = book
        self.chap = chap
        self.chnk = chnk

        self.DCSwebaddressmap = {
            'en_tn'  : 'https://git.door43.org/Door43/en_tn/raw/master/',
            'en_ulb' : 'https://git.door43.org/Door43/en_ulb/raw/master/',
            'en_ugl' : 'https://git.door43.org/Door43/en_ugl/raw/master/'
        }
        thiscompare = parse_tn_file(self)
        
    def getFill(bk):
        if 'psa' in bk.lower():
            return 3
        return 2

    def getulb(self):
        lowerbook = self.book.lower()
        upperbook = self.book.upper()
        ulbDCS = "https://git.door43.org/Door43/en_ulb/raw/master/"
        ulbsrc = ulbDCS + bible_books.BOOK_NUMBERS[lowerbook] + '-' + upperbook + '.usfm' 
        content = url_utils.get_url(ulbsrc) # resp,content = self.httplib2_instance.request(ulbsrc)
        content = re.sub(r'\n','~',content)
        ulbbook = content
        ulbchapters = re.split(r'\\c\s+',ulbbook)
        thischapter = ulbchapters[int(chapter)]
        ulbchunks = re.split(r'\\s5',thischapter)
        versenum = 1
        usechunk = False
        savechunk = ''
        for ulbchunk in ulbchunks:
            lines = ulbchunk.split('~')
            for line in lines:
                versefound = re.search(r'\\v\s+(\d+)\s+(.+)',line)
                if versefound:
                    versenum = int(versefound.group(1))
                    if versenum >= int(chunk):
                        usechunk = True
                if usechunk:
                    savechunk = savechunk + line + " "
            if usechunk:
                savechunk = savechunk.replace('  ',' ')
                return savechunk
        return ''

    def print_error (self,msg):
        self.log.warning(msg+self.book+' '+self.chap+":"+self.chnk)
        return 

    def removepunct (instr) :
        ans = instr
        ans = re.sub(r'[!"\#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]','',ans)
        return ans

    def tighter_search (self,sinput,uinput):
        compare = True
        srch = sinput
        u = uinput
        srch = re.sub(r'\x2d','\x20',srch)
        srch = re.sub(r'{\d+}','',srch)
        u = re.sub(r'\x2d','\x20', u)
        srch = srch.replace('?','')
        #print "srch",srch
        swrds = re.split(r'\s+',srch)
        srchinustr = "("+srch+")(.+)"
        #print "srchinustr,u",srchinustr,'\n',u
        srchinu = re.search(r''+srchinustr+'',u)
        if  srchinu:
            remainder = srchinu.group(2)
            #print "T_S remainder",remainder
            ustr = srchinu.group(1) + remainder
            uwrds = re.split(r'\s+',ustr)
            uindex = 0
            for swrd in swrds:
                if not re.search(r'\'s',swrd):
                    uwrds[uindex] = re.sub(r'\'s','',uwrds[uindex])
                stest = removepunct(swrd)
                #print "swrd,stext",swrd,stest
                stest = re.sub(r'ZZZZ','',stest)
                utest = removepunct(uwrds[uindex])
                utest = re.sub(r'ZZZZ','',utest)
                #print "undx,swrd,stest,utest",uindex,swrd,stest,utest
                if stest != utest:
                  # check if possible follow-on compare
                    if re.search(r''+srch+'',remainder):
                        #print "call tighter_search 2nd time"
                        compare = tighter_search(self,sinput,remainder)
                    else :
                        #print "Last word-pair miscompared"
                        compare = False # no follow-on match, so miscompare
                uindex = uindex + 1    
        return compare

    def compare_snippet (self,tn, ulb):
        global book,chap,chnk,author,comdate
        compare = True
        eitherelippsis = 0
        snippet = tn
        savesnippet = snippet
        snippet = re.sub(r'\(','XXXX',snippet)
        snippet = re.sub(r'\)','ZZZZ',snippet)
        snippet = snippet.replace("?",' QM')
        snippet = re.sub(r'\x97',' EMB ',snippet) # em-dash
        snippet = re.sub(r'\xe2\x80\x94',' EMB ',snippet) # em-dash
        ulb = ulb.replace("?",' QM')
        ulb = re.sub(r'\(','XXXX',ulb)
        ulb = re.sub(r'\)','ZZZZ',ulb)
        ulb = re.sub(r'~',' ',ulb)
        ulb = re.sub(r'\\v\s+\d+\s+',' ',ulb)
        ulb = re.sub(r'\\q\d+','',ulb)
        ulb = re.sub(r'\\q\s+',' ',ulb)
        ulb = re.sub(r'\\m','',ulb)
        ulb = re.sub(r'\s*\x97\s*',' EMB ',ulb) # em-dash
        ulb = re.sub(r'\s*\xe2\x80\x94\s*',' EMB ',ulb) # em-dash
        ulb = re.sub(r'\s{2,}',' ',ulb)
        if re.search(r'\.\.\.',ulb):
            srchulb = ulb
            eitherelippsis = 1
            srchulb = re.sub(r'\s+\.\.\.\s+',' ',srchulb)
            srchulb = re.sub(r'\s+\.\.\.',' ',srchulb)
            srchulb = re.sub(r'\.\.\.\s+',' ',srchulb)
            srchulb = re.sub(r'\.\.\.',' ',ulb)
        else :
            srchulb = ulb
        if re.search(r'\.\.\.',snippet):
            eitherelippsis = 1
            srchstr = snippet
            srchstr = re.sub(r'\s+\.\.\.\s+','^',srchstr)
            srchstr = re.sub(r'\s+\.\.\.','^',srchstr)
            srchstr = re.sub(r'\.\.\.\s+','^',srchstr)
            srchstr = re.sub(r'\.\.\.','^',srchstr)
            srchstr = srchstr.replace('^','.+')
        else:
            srchstr = snippet        
        #print "SRCHSTR\n",srchstr    ,"\nSNIPPET\n",snippet,"\nSRCHULB\n",srchulb
        if eitherelippsis == 1:
            strinulb = re.search(r''+srchstr+'',srchulb)
             if not strinulb :
                compare = False
    #            print "Miscomp with elippsis"
    #            print "tn,ulb===> ",srchstr,"\n",srchulb
                print_error(self,"Snippet miscompare for")
        else:
                #snippet = snippet  + "\x3f"
                #print "snippet,ULB",snippet,'\n',srchulb
                strinulb = re.search(r''+snippet+'',srchulb)
                 if strinulb :
                     #print "call tighter_search"
                     #print "IN ULB  snippet,ULB",snippet,'\n',srchulb
                    compare = tighter_search (snippet, ulb)
                else:
                    #print "DON'T call tighter_search"
                    #print 'Not IN ULB snippet,ULB:"'+snippet+'"\n',srchulb
                    compare = False
                if not compare:
    #                print "Miscomp without elippsis"
    #                print '\n\n',book,chap,chnk,'\nsavesnippet',savesnippet,"\nsrchULB",srchulb
                    print_error(self,"Snippet miscompare for")
        return compare

    def parse_tn_file(self):
        any_error_found = False
        bookname = self.book.lower()
        zerofillwidth = getFill(book)
        chapname = self.chap.zfill(zerofillwidth)
        chunkname = self.chnk.zfill(zerofillwidth)
        tnDCS = "https://git.door43.org/Door43/en_tn/raw/master/" 
        tnsrc = tnDCS + bookname + '/' + chapname + '/' + chunkname + '.md' 
        tncontent = url_utils.get_url(tnsrc) # resp,tncontent = self.httplib2_instance.request(tnsrc)
        ulb_chunkdata = getulb(self)
        linenumber = 0
        compare = False
        tnlines = tncontent.split('\n')
        snippet = ''
        for iline in tnlines:
            linenumber = linenumber + 1
            markerfound = re.search(r'^\#{1}\s+(.+)',iline)
            if markerfound:
                remainder = markerfound.group(1)
                if (not re.search(r'translationWords',remainder)) and (not re.search(r'General Information',remainder))  and (not re.search(r'Connecting Statement',remainder)):
                    snippet = remainder
                    compare = compare_snippet(self,snippet, ulb_chunkdata)
        if (snippet == ''):
            compare = True # Since there were none to compare
        return compare

