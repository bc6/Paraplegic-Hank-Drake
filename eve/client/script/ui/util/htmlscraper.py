import re
import blue
namefind = re.compile('(\\S+)\\s*(.*)', re.DOTALL)
attrfind = re.compile('\\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\\s*=\\s*(\\\'[^\\\']*\\\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~\\\'"@]*))?')

class HtmlScraper:
    __guid__ = 'hparser.HtmlScraper'

    def __init__(self):
        self.buffer = ''
        self.outfile = ''



    def reset(self):
        self.buffer = ''
        self.outfile = ''



    def push(self):
        data = self.outfile
        self.outfile = ''
        return data



    def close(self):
        data = self.push() + self.buffer
        self.buffer = ''
        return data



    def feed(self, data):
        self.tempindex = 0
        self.buffer = self.buffer + data
        if self.buffer.find('<!--') != -1:
            tempbuffer = []
            for cs in self.buffer.split('<!--'):
                commentline = cs.split('-->')
                if len(commentline) == 1:
                    tempbuffer.append(commentline[0])
                else:
                    commentline[0] = commentline[0].replace('<', '&lt;').replace('>', '&gt;')
                    tempbuffer.append('<!--' + '-->'.join(commentline))

            self.buffer = ''.join(tempbuffer)
        outlist = []
        thischunk = []
        self.index = 0
        bufferList = self.buffer.split('>')
        for thischunk in bufferList[:-1]:
            blue.pyos.BeNice(100)
            s = thischunk.split('<')
            if len(s[0]):
                outlist.append(self.pdata(s[0]))
            if len(s) > 1:
                self.tagstart(s[-1])

        self.buffer = bufferList[-1]



    def tagstart(self, thetag):
        if thetag.startswith('!'):
            return self.pdecl(thetag)
        if thetag.startswith('?'):
            return self.ppi()
        if thetag.startswith('/'):
            return self.endtag(thetag)
        nt = namefind.match(thetag)
        if not nt:
            return self.emptytag(thetag)
        (name, attributes,) = nt.group(1, 2)
        matchlist = attrfind.findall(attributes)
        attrs = []
        for entry in matchlist:
            (attrname, rest, attrvalue,) = entry
            if not rest:
                attrvalue = attrname
            elif attrvalue[:1] == "'" == attrvalue[-1:] or attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
            attrs.append((attrname.lower(), attrvalue))

        return self.handletag(name.lower(), attrs, thetag)



    def pdata(self, inchunk):
        return inchunk



    def pdecl(self, thetag):
        return '<'



    def ppi(self):
        return '<'



    def endtag(self, thetag):
        return '<' + thetag + '>'



    def emptytag(self, thetag):
        return '<' + thetag + '>'



    def handletag(self, name, attrs, thetag):
        return '<' + thetag + '>'



__doc__ = "\nScraper is a class to parse HTML files.\nIt contains methods to process the 'data portions' of an HTML and the tags.\nThese can be overridden to implement your own HTML processing methods in a subclass.\nThis class does most of what HTMLParser.HTMLParser does - except without choking on bad HTML.\nIt uses the regular expression and a chunk of logic from sgmllib.py (standard python distribution)\n\nThe only badly formed HTML that will cause errors is where a tag is missing the closing '>'. (Unfortunately common)\nIn this case the tag will be automatically closed at the next '<' - so some data could be incorrectly put inside the tag.\n\nThe useful methods of a Scraper instance are :\n\nfeed(data)  -   Pass more data into the parser.\n                As much as possible is processed - but nothing is returned from this method.\npush()      -   This returns all currently processed data and empties the output buffer.\nclose()     -   Returns any unprocessed data (without processing it) and resets the parser.\n                Should be used after all the data has been handled using feed and then collected with push.\n                This returns any trailing data that can't be processed.\nreset()     -   This method clears the input buffer and the output buffer.\n\nThe following methods are the methods called to handle various parts of an HTML document.\nIn a normal Scraper instance they do nothing and are intended to be overridden.\nSome of them rely on the self.index attribute property of the instance which tells it where in self.buffer we have got to.\nSome of them are explicitly passed the tag they are working on - in which case, self.index will be set to the end of the tag.\nAfter all these methods have returned self.index will be incremented to the next character.\nIf your methods do any future processing they can manually modify self.index\nAll these methods should return anything to include in the processed document.\n\npdata(inchunk)\n    Called when we encounter a new tag. All the unprocessed data since the last tag is passed to this method.\n    Dummy method to override. Just returns the data unchanged.\n\npdecl()\n    Called when we encounter the *start* of a declaration or comment. <!.....\n    It uses self.index and isn't passed anything.\n    Dummy method to override. Just returns '<'.\n\nppi()\n    Called when we encounter the *start* of a processing instruction. <?.....\n    It uses self.index and isn't passed anything.\n    Dummy method to override. Just returns '<'.\n\nendtag(thetag)\n    Called when we encounter a close tag.   </...\n    It is passed the tag contents (including leading '/') and just returns it.\n\nemptytag(thetag)\n    Called when we encounter a tag that we can't extract any valid name or attributes from.\n    It is passed the tag contents and just returns it.\n\nhandletag(name, attrs, thetag)\n    Called when we encounter a tag.\n    Is passed the tag name and attrs (a list of (attrname, attrvalue) tuples) - and the original tag contents as a string.\n\n\nTypical usage :\n\nfilehandle = open('file.html', 'r')\nparser = Scraper()\nwhile True:\n    data = filehandle.read(10000)               # read in the data in chunks\n    if not data: break                      # we've reached the end of the file - python could do with a do:...while syntax...\n    parser.feed(data)\n##    print parser.push()                     # you can output data whilst processing using the push method\nprocessedfile = parser.close()              # or all in one go using close\n## print parser.close()                       # Even if using push you will still need a final close\nfilehandle.close()\n\n\n\nTODO/ISSUES\nCould be sped up by jumping from '<' to '<' rather than a character by character search (which is still pretty quick).\nNeed to check I have all the right tags and attributes in the tagdict in approxScraper.\nThe only other modification this makes to HTML is to close tags that don't have a closing '>'.. theoretically it could close them in the wrog place I suppose....\n(This is very bad HTML anyway - but I need to watch for missing content that gets caught like this.)\nCould check for character entities and named entities in HTML like HTMLParser.\nDoesn't do anything special for self clsoing tags (e.g. <br />)\n\n\nCHANGELOG\n06-09-04        Version 1.3.0\nA couple of patches by Paul Perkins - mainly prevents the namefind regular expression grabbing a characters when it has no attributes.\n\n28-07-04        Version 1.2.1\nWas losing a bit of data with each new feed. Have sorted it now.\n\n24-07-04        Version 1.2.0\nRefactored into Scraper and approxScraper classes.\nIs now a general purpose, basic, HTML parser.\n\n19-07-04        Version 1.1.0\nModified to output URLs using the PATH_INFO method - see approx.py\nCleaned up tag handling - it now works properly when there is a missing closing tag (common - but see TODO - has to guess where to close it).\n\n11-07-04        Version 1.0.1\nAdded the close method.\n\n09-07-04        Version 1.0.0\nFirst version designed to work with approx.py the CGI proxy.\n\n"

