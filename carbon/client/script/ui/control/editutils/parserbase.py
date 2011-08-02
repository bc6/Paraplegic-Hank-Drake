import util
import _weakref
import blue
import log
import types
import sys
import corebrowserutil
import parser
import urllib2
import html
import trinity
import fontConst
import fontflags
import uiutil
import uicls
import uiconst
import stackless
import service
globals().update(service.consts)

class ParserBaseCore(object):
    __guid__ = 'parser.ParserBaseCore'
    __update_on_reload__ = 1

    def Prepare(self):
        self.getWidths = 0
        self.minWidth = 0
        self.totalWidth = 0
        self.xmargin = 8
        self.tagdepth = 0
        self.readonly = 1
        self.htmldebug = 0
        self.wordMeasurer = uicore.font.GetMeasurer()
        self.glyphString = None
        self.plainload = 0
        self.title = None
        self.charset = 'cp1252'
        self.textbuffers = []
        self.css = html.Css()
        self.sr.parser = parser.Html(self)
        self.sr.parser.notify_load = self.Loading
        self.sr.window = None
        if self.sr.Get('content', None):
            parent = self.sr.content.parent
        else:
            parent = self
        self.sr.overlays_content = uicls.Container(parent=parent, name='overlays_content', align=uiconst.TOPLEFT)
        self.sr.underlays_content = uicls.Container(parent=parent, name='underlays_content', align=uiconst.TOPLEFT)
        self.sr.background = uicls.Container(parent=parent, name='background')
        self.sr.cacheContainer = uicls.Container(name='cacheContainer', parent=self, state=uiconst.UI_HIDDEN)



    def Loading(self, *args):
        if self.sr.window and hasattr(self.sr.window, 'ShowLoadBar'):
            self.sr.window.ShowLoadBar(*args)



    def SetStatus(self, *args):
        if self.sr.window and hasattr(self.sr.window, 'ShowStatus'):
            self.sr.window.ShowStatus(*args)



    def ShowHint(self, hint = None):
        if self.sr.window and hasattr(self.sr.window, 'ShowHint'):
            self.sr.window.ShowHint(hint)



    def OnStartTag(self, tag, attrs):
        if not self or not getattr(self, 'sr', None):
            return 
        if self.htmldebug:
            print '>>>>',
            print 'OnStartTag',
            print tag,
            print self.name
        closeTags = parser.HtmlOptionalClose.get(tag, ())
        if self.attrStack[-1]['tag'] in closeTags:
            self.OnEndTag(self.attrStack[-1]['tag'])
        if tag == 'table' and self.sr.table:
            self.blockBufferClose += 1
        elif tag == 'div' and self.divs:
            self.divs += 1
        if self.attrStack[-1]['bufferStack'] is not None:
            attrs.form = self.sr.form
            self.attrStack[-1]['bufferStack'].append(('OnStartTag', (tag, attrs)))
            return 
        f = getattr(self, 'OnStart_%s' % tag, None)
        if f:
            f(attrs)
        else:
            self.OnStart_default(tag, attrs)



    def OnEndTag(self, tag):
        if not self or not getattr(self, 'sr', None):
            return 
        if self.htmldebug:
            print '<<<<',
            print 'OnEndTag',
            print tag,
            print self.name,
            print self.attrStack[-1]['bufferStack'] is None,
            print self.blockBufferClose,
            print self.divs,
            print self.sr.table
        if self.attrStack[-1]['bufferStack'] is not None:
            if tag == 'table' and self.sr.table:
                self.blockBufferClose = max(0, self.blockBufferClose - 1)
            if tag == 'div' and self.divs:
                self.divs = max(0, self.divs - 1)
            if tag in 'div' and self.sr.table is None or tag in ('td', 'th', 'tr') and self.sr.table and not self.blockBufferClose and not self.divs:
                self.attrStack[-1]['bufferStack'].append(('FlushBuffer', (None,)))
            else:
                if self.htmldebug:
                    print '<<<<< adding to openbuffer, closing',
                    print tag,
                    print self.name,
                    print self.blockBufferClose
                self.attrStack[-1]['bufferStack'].append(('OnEndTag', (tag,)))
                return 
        closeTags = parser.HtmlAutoClose.get(tag, ())
        if self.attrStack[-1]['tag'] != tag and self.attrStack[-1]['tag'] in closeTags:
            self.OnEndTag(self.attrStack[-1]['tag'])
        f = getattr(self, 'OnEnd_%s' % tag, None)
        if f:
            f()
        else:
            self.OnEnd_default(tag)



    def OnData(self, data, *args):
        if not self or not getattr(self, 'sr', None):
            return 
        if self.attrStack[-1]['bufferStack'] is not None:
            if self.htmldebug:
                print '>>>>> adding to openbuffer OnData',
                print data,
                print self.blockBufferClose
            self.attrStack[-1]['bufferStack'].append(('OnData', (data,)))
            return 
        (tag, attrs,) = (self.attrStack[-1]['tag'], self.attrStack[-1]['attr'])
        data = self.sr.buffer + data
        self.sr.buffer = u''
        if not data:
            return 
        if self.htmldebug:
            print '----',
            print 'OnData',
            print self.name,
            print '-',
            print tag,
            print '-',
            print data,
            try:
                print attrs.__dict__
            except:
                sys.exc_clear()
                print '--'
        f = getattr(self, 'OnData_%s' % (tag or ''), None)
        if f:
            f(data, attrs)
        elif type(data) in types.StringTypes:
            data = self.StripText(data)
            if data:
                self.AddTextToBuffer(data, fromW='Ondata')
        elif self.htmldebug:
            print 'NonString data outside any tag',
            print self.name,
            print repr(data)
        log.LogWarn('NonString data outside any tag', repr(data))



    def StripText(self, text):
        text = text.replace('\n', u' ').replace('\r', u' ').replace('\t', u' ')
        if self.plainload:
            return text
        while text.find(u'  ') != -1:
            text = text.replace(u'  ', u' ')

        if not self.textbuffer:
            text = text.lstrip()
        return text



    def OnStart_default(self, tag, attrs, defaultStyles = None):
        self.attrStack.append(self.attrStack[-1].copy())
        self.attrStack[-1]['tag'] = tag
        self.attrStack[-1]['attr'] = attrs
        self.SetStyles(defaultStyles)
        self.ApplyCSS(tag, attrs)
        self.ParseStdStyles(attrs)



    def OnEnd_default(self, tag):
        idx = -1
        while self.attrStack[idx]['tag'] != tag:
            log.LogWarn('Incorrect order of tags in html string, trying to close', tag, 'but lasttag is', self.attrStack[idx]['tag'])
            idx -= 1
            if len(self.attrStack) <= abs(idx):
                log.LogWarn('Reached begining of attrStack while trying to close tag:', tag)
                return 

        self.attrStack.pop(idx)
        if len(self.attrStack) > abs(idx):
            self.attrStack[(idx - 1)]['lasttag'] = tag



    def FlushBuffer(self, fakeLines = None):
        data = self.StripText(self.sr.buffer)
        self.sr.buffer = u''
        if data:
            self.AddTextToBuffer(data)
        if self.textbuffer:
            obj = self.textbuffer[-1]
            if obj.type == '<text>' and obj.letters == u' ':
                self.textbuffer.pop(-1)
        if self.getWidths:
            self.BreakLines(self.textbuffer)
            self.textbuffer = []
            return 
        if fakeLines is not None:
            _lines = self.BuildEntries(fakeLines, self.textbuffer, self.attrStack[-1])
            self.textbuffers.append(([self.GetTextObject('')], self.attrStack[-1]))
            self.AddLines(_lines)
            return 
        if len(self.textbuffer):
            self.textbuffers.append((self.textbuffer, self.attrStack[-1]))
            lines = self.BreakLines(self.textbuffer)
            scrollNodes = self.BuildEntries(lines, self.textbuffer, self.attrStack[-1])
            self.AddLines(scrollNodes)
        self.textbuffer = []



    def LoadFont(self, force = 0):
        fontFlag = self.attrStack[-1]['fontflags']
        fontFlag &= ~(fontflags.b | fontflags.i | fontflags.o | fontflags.u | fontflags.strike)
        if self.attrStack[-1]['font-style'] == 'i':
            fontFlag |= fontflags.i
        if self.attrStack[-1]['font-weight'] == 'b':
            fontFlag |= fontflags.b
        if 'u' in self.attrStack[-1]['text-decoration']:
            fontFlag |= fontflags.u
        if 's' in self.attrStack[-1]['text-decoration']:
            fontFlag |= fontflags.strike
        if 'o' in self.attrStack[-1]['text-decoration']:
            fontFlag |= fontflags.o
        self.attrStack[-1]['fontflags'] = fontFlag



    def _LoadHTML(self, htmlstr):
        if self.destroyed:
            return 
        self.title = None
        self.sr.htmlstr = htmlstr
        self._Reset()
        if self.destroyed:
            return 
        self.sr.parser.reset()
        self.sr.parser.feed(self.sr.htmlstr)
        if self.destroyed:
            return 
        self.sr.parser.close()



    def LoadBuffer(self, buff, getWidths = 0, setWidth = None, singleWordMax = None):
        self._Reset()
        self.getWidths = getWidths
        self.minWidth = 0
        self.totalWidth = 0
        self.singleWordMax = singleWordMax or self.sr.browser and self.sr.browser.GetContentWidth() - self.sr.browser.xmargin * 2
        if setWidth is not None:
            self.sr.width = setWidth
        self.attrStack[-1]['background-color'] = None
        for (func, args,) in buff:
            if hasattr(self, func):
                apply(getattr(self, func, None), args)

        if self.getWidths:
            return 



    def GetDefaultFont(self):
        return getattr(self, 'font', None) or fontConst.DEFAULT_FONT



    def _Reset(self):
        for form in self.sr.get('forms', []):
            if form is not None:
                for (attrs, wnd,) in form.fields:
                    wnd.Close()


        self.textbuffers = []
        self.textbuffer = []
        self.attrStack = []
        self.areamap = []
        self.a = None
        self.blockquote = 0
        self.list = 0
        self.contentHeight = 0
        self.contentWidth = 0
        self.blockBufferClose = 0
        self.divs = 0
        self.sr.table = None
        self.sr.buffer = ''
        self.sr.listIndex = []
        self.sr.overlays = []
        self.sr.underlays = []
        self.sr.lines = []
        self.sr.forms = []
        self.sr.anchor = None
        self.sr.form = None
        self.sr.select = None
        attrEntry = {}
        attrEntry['font'] = getattr(self, 'defaultFont', None) or fontConst.DEFAULT_FONT
        attrEntry['font-family'] = None
        attrEntry['font-size'] = getattr(self, 'defaultFontSize', 12)
        attrEntry['font-style'] = ''
        attrEntry['font-weight'] = ''
        attrEntry['fontflags'] = 0
        attrEntry['basefontsize'] = 3
        attrEntry['text-decoration'] = ''
        attrEntry['color'] = getattr(self, 'defaultFontColor', (1.0, 1.0, 1.0, 0.75))
        attrEntry['background-color'] = None
        attrEntry['background-image'] = None
        attrEntry['background-image-color'] = (1.0, 1.0, 1.0, 1.0)
        attrEntry['background-image-width'] = 0
        attrEntry['background-image-height'] = 0
        attrEntry['background-image-left'] = 0
        attrEntry['background-image-top'] = 0
        attrEntry['background-repeat'] = 'repeat'
        attrEntry['background-attachment'] = 'scroll'
        attrEntry['line-height'] = 12
        attrEntry['align'] = None
        attrEntry['text-align'] = None
        attrEntry['text-indent'] = 0
        attrEntry['vertical-align'] = 3
        attrEntry['letter-spacing'] = 0
        attrEntry['word-spacing'] = 0
        attrEntry['line-height'] = None
        attrEntry['margin-left'] = 0
        attrEntry['margin-right'] = 0
        attrEntry['margin-top'] = 0
        attrEntry['margin-bottom'] = 0
        attrEntry['padding-left'] = 0
        attrEntry['padding-right'] = 0
        attrEntry['padding-top'] = 0
        attrEntry['padding-bottom'] = 0
        attrEntry['border-left-width'] = 0
        attrEntry['border-right-width'] = 0
        attrEntry['border-top-width'] = 0
        attrEntry['border-bottom-width'] = 0
        attrEntry['border-left-color'] = (1.0, 1.0, 1.0, 1.0)
        attrEntry['border-right-color'] = (1.0, 1.0, 1.0, 1.0)
        attrEntry['border-top-color'] = (1.0, 1.0, 1.0, 1.0)
        attrEntry['border-bottom-color'] = (1.0, 1.0, 1.0, 1.0)
        attrEntry['border-left-style'] = None
        attrEntry['border-right-style'] = None
        attrEntry['border-top-style'] = None
        attrEntry['border-bottom-style'] = None
        attrEntry['border-collapse'] = 0
        attrEntry['link-color'] = (1.0, 0.65, 0.0, 1.0)
        attrEntry['alink-color'] = None
        attrEntry['vlink-color'] = (1.0, 0.8, 0.0, 1.0)
        attrEntry['class'] = 'default'
        attrEntry['tag'] = 'default'
        attrEntry['lasttag'] = ''
        attrEntry['attr'] = None
        attrEntry['position'] = None
        attrEntry['float'] = None
        attrEntry['id'] = None
        attrEntry['bufferStack'] = None
        attrEntry['pstart'] = 0
        attrEntry['background-position'] = []
        self.attrStack.append(attrEntry)
        self.css.Reset()
        self.LoadFont(force=1)
        self.Reset()



    def GetLinespace(self):
        return int(self.attrStack[-1]['line-height'] or self.attrStack[-1]['font-size'])



    def Reset(self, *args):
        pass



    def LoadBodyAttrs(self, *args):
        pass



    def BuildEntries(self, lines, stack, attrs):
        if stack and stack[0].type == '<hr>':
            data = {'decoClass': uicls.SE_hr,
             'leftmargin': stack[0].lpush,
             'rightmargin': stack[0].rpush,
             'attrs': stack[0].attrs,
             'bgcolor': None}
            se = uicls.ScrollEntryNode(**data)
            return [se]
        _lines = []
        for each in lines:
            entry = self.GetTextEntry(attrs, stack, *each)
            _lines.append(entry)

        return _lines



    def GetFirstLine(self):
        (lpush, rpush,) = self.GetMargins(0, self.GetLinespace())
        textObj = self.GetTextObject('')
        self.AddObjectToBuffer(textObj)
        self.textbuffers.append(([textObj], self.attrStack[-1]))
        return self.GetTextEntry(self.attrStack[-1], [textObj], lpush=lpush, rpush=rpush)



    def GetTextEntry(self, attrs, stack, glyphString = None, inlines = None, links = None, lpush = 0, rpush = 0, bBox = None, baseHeight = 12, baseLine = 10, abspos = 0):
        lineWidth = 0
        if bBox is not None:
            lineWidth = bBox.Width()
        data = {'decoClass': uicls.SE_Textline,
         'glyphString': glyphString or [],
         'inlines': inlines or [],
         'pos': abspos,
         'stack': stack,
         'lpush': lpush,
         'rpush': rpush,
         'maxBaseHeight': baseHeight,
         'maxBaseLine': baseLine,
         'bBox': bBox,
         'lineWidth': lineWidth,
         'align': attrs['text-align'],
         'links': links or [],
         'SelectionHandler': self,
         'URLHandler': self.sr.window}
        entry = uicls.ScrollEntryNode(**data)
        self.contentHeight = max(self.contentHeight, self.contentHeight + baseHeight)
        self.contentWidth = max(lineWidth + lpush + rpush, self.contentWidth)
        return entry



    def InsertLines(self, stack, abspos, idx, attrs):
        lines = self.BreakLines(stack, abspos=abspos)
        nodes = self.BuildEntries(lines, stack, attrs)
        self.AddNodes(idx, nodes)
        return nodes



    def Simplify(self, quiet = 0):
        rem = []
        for (idx, (stack, attrs,),) in enumerate(self.textbuffers):
            oldFont = None
            oldSize = None
            oldColor = None
            oldFlags = None
            oldA = None
            oldFontFamily = None
            i = 0
            while i < len(stack):
                obj = stack[i]
                if obj.type == '<text>':
                    if len(obj.letters) == 0 and len(stack) > 1:
                        stack.pop(i)
                        continue
                    if obj.a:
                        obj.color = (1.0, 0.65, 0.0, 1.0)
                        obj.lcolor = (1.0, 0.65, 0.0, 1.0)
                        obj.fontFlags |= fontflags.b | fontflags.u
                    if obj.fontFamily == oldFontFamily and obj.fontSize == oldSize and obj.fontFlags == oldFlags and obj.color == oldColor and obj.a == oldA and stack[(i - 1)].type == '<text>':
                        stack[(i - 1)].letters += obj.letters
                        stack.pop(i)
                        continue
                    oldFontFamily = obj.fontFamily
                    oldSize = obj.fontSize
                    oldColor = obj.color
                    oldFlags = obj.fontFlags
                    oldA = obj.a
                i += 1

            if not len(stack):
                rem.append(idx)

        for idx in rem:
            self.textbuffers.pop(idx)




    def AddLines(self, lines):
        self.sr.lines += lines



    def AddTextToBuffer(self, text, width = None, fromW = None):
        self.LoadFont()
        self.AddObjectToBuffer(self.GetTextObject(text, width))



    def GetTextObject(self, text, width = None):
        obj = uiutil.Bunch()
        obj.spacing = self.attrStack[-1]['letter-spacing']
        obj.a = self.a
        if obj.a:
            visited = settings.public.ui.VisitedURLs or []
            obj.color = [self.attrStack[-1]['link-color'], self.attrStack[-1]['vlink-color'] or self.attrStack[-1]['link-color']][(obj.a.href in visited)]
            obj.lcolor = self.attrStack[-1]['alink-color'] or obj.color
        else:
            obj.color = self.attrStack[-1]['color']
        obj.fontFlags = self.attrStack[-1]['fontflags']
        obj.valign = self.attrStack[-1]['vertical-align']
        obj.type = '<text>'
        obj.width = width
        if type(text) != types.UnicodeType:
            text = unicode(text, 'utf-8', 'replace')
        obj.letters = text
        obj.wordSpacing = self.attrStack[-1]['word-spacing']
        obj.letterSpacing = self.attrStack[-1]['letter-spacing']
        obj.fontSize = obj.fontsize = self.attrStack[-1]['font-size']
        obj.fontFamily = self.attrStack[-1]['font-family']
        obj.font = self.attrStack[-1]['font']
        return obj



    def AddObjectToBuffer(self, obj):
        obj.depth = len(self.attrStack) - 1
        obj.tags = []
        obj.tagattrs = []
        while obj.depth > self.tagdepth:
            self.tagdepth += 1
            obj.tags.append(self.attrStack[self.tagdepth]['tag'])
            obj.tagattrs.append(self.attrStack[self.tagdepth]['attr'])

        self.textbuffer.append(obj)



    def GetWidthInBuffer(self):
        self.wordMeasurer.Reset(None)
        for obj in self.textbuffer:
            if obj.type == '<overlay>':
                continue
            elif obj.type == '<text>':
                fParams = obj
                fParams.font = obj.font
                fParams.fontsize = obj.fontSize
                fParams.letterspace = obj.letterSpacing
                fParams.wordspace = obj.wordSpacing
                fParams.bold = bool(obj.fontFlags & fontflags.b)
                fParams.italic = bool(obj.fontFlags & fontflags.i)
                fParams.underline = bool(obj.fontFlags & fontflags.u)
                self.wordMeasurer.AddText(obj.letters.replace(u'\xa0', u' '), fParams)
            elif obj.type in '<table><img><input>':
                self.wordMeasurer.AddSpace(obj.width)

        return self.wordMeasurer.cursor



    def NewLine(self):
        self.FlushBuffer()
        if type(self.attrStack[-1]['line-height']) == str and self.attrStack[-1]['line-height'].endswith('%'):
            self.attrStack[-1]['line-height'] = int(float(self.attrStack[-1]['line-height'][:-1]) * self.attrStack[-1]['font-size'] / 100.0)
        linespace = self.attrStack[-1]['line-height'] or self.attrStack[-1]['font-size']
        (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + linespace)
        self.FlushBuffer([([],
          [],
          [],
          lpush,
          rpush,
          None,
          linespace,
          0,
          0)])



    def GetMargins(self, fromY, toY):
        blockquote = self.blockquote * 32
        list = self.list * 32
        if self.destroyed:
            return (0, 0)
        contentWidth = self.GetContentWidth()
        self.attrStack[-1]['margin-left'] = self.GetPercent(self.attrStack[-1]['margin-left'], contentWidth)
        self.attrStack[-1]['margin-right'] = self.GetPercent(self.attrStack[-1]['margin-right'], contentWidth)
        lpush = self.attrStack[-1]['margin-left'] + self.attrStack[-1]['padding-left'] + self.attrStack[-1]['border-left-width'] + blockquote + list + self.xmargin
        rpush = self.attrStack[-1]['margin-right'] + self.attrStack[-1]['padding-right'] + self.attrStack[-1]['border-right-width'] + blockquote + self.xmargin
        for (overlay, attrs, x, y,) in self.sr.overlays:
            if overlay.state == uiconst.UI_HIDDEN:
                continue
            w = overlay.width
            h = overlay.height
            y = attrs.top
            if toY > y and fromY < y + h:
                if attrs.align == 'left':
                    lpush = max(lpush, getattr(attrs, 'left', 0) + w)
                elif attrs.align == 'right':
                    rpush = max(rpush, getattr(attrs, 'left', 0) + w)

        return (lpush, rpush)



    def StackPosToObjPos(self, stack, abspos, allobj = 0):
        objpos = 0
        pos = abspos
        for obj in stack:
            if not obj.letters:
                if allobj == 1 and pos < 1:
                    objpos = stack.index(obj)
                    break
                pos -= 1
                continue
            if pos < len(obj.letters):
                objpos = stack.index(obj)
                break
            pos -= len(obj.letters)
        else:
            return (0, abspos)

        return (objpos, pos)



    def GetWidths(self, textbuffer):
        s = uicore.font.GetGlyphString()
        s.shadow = None
        for obj in textbuffer:
            fParams = obj
            fParams.fontsize = obj.fontSize
            if obj.type == '<overlay>':
                continue
            elif obj.type == '<text>':
                if not obj.letters:
                    continue
                fParams = obj
                fParams.fontsize = obj.fontSize
                fParams.letterspace = obj.letterSpacing
                fParams.wordspace = obj.wordSpacing
                fParams.bold = bool(obj.fontFlags & fontflags.b)
                fParams.italic = bool(obj.fontFlags & fontflags.i)
                fParams.underline = bool(obj.fontFlags & fontflags.u)
                s.Append(fParams, obj.letters)
            elif obj.type in ('<table>', '<img>'):
                s.AddSpace(fParams, obj.control.width)
            else:
                s.AddSpace(fParams, obj.width)

        w = 0
        wordWidth = 0
        for t in s:
            if t[4] == u' ':
                maxWidth = max(wordWidth, w)
                w = 0
            else:
                w += t[0]
            if w > self.singleWordMax:
                w = 0
                continue
            wordWidth = max(wordWidth, w)

        self.minWidth = max(self.minWidth, wordWidth)
        self.totalWidth = max(self.totalWidth, s.width)



    def GetLine(self, textbuffer, startpos, recurse):
        s = self.glyphString
        if s:
            s.Reset()
        else:
            s = uicore.font.GetGlyphString()
            s.shadow = None
            self.glyphString = s
        (bufnum, pos,) = self.StackPosToObjPos(textbuffer, startpos, allobj=1)
        inlines = []
        links = []
        ustart = astart = None
        wordlen = 0
        aa = None
        acolor = None
        curr = stackless.getcurrent()
        onMainThread = curr.is_main
        contentWidth = self.GetContentWidth()
        startTime = blue.os.GetTime()
        while contentWidth <= 0 and not onMainThread and not self.destroyed:
            blue.synchro.Yield()
            contentWidth = self.GetContentWidth()
            if blue.os.TimeDiffInMs(startTime) > 500:
                contentWidth = 256
                warning = 'Someone is trying to load text into uicls.Edit which has 0 or less width. This controls visible state under desktop is: ' + str(uiutil.IsVisible(self)) + '. Edit location: ' + uiutil.GetTrace(self, trace='', div='/')
                log.LogWarn(warning)
                break

        for i in xrange(bufnum, len(textbuffer)):
            obj = textbuffer[i]
            fParams = obj
            fParams.fontsize = self.attrStack[-1]['font-size']
            if obj.type == '<overlay>':
                obj.attrs.top = self.contentHeight
                obj.overlay.top = self.contentHeight
                obj.overlay.state = uiconst.UI_NORMAL
                if obj.attrs.Get('align', None) == 'right':
                    obj.overlay.left = contentWidth - obj.overlay.width - obj.attrs.left
                if not obj.overlay.loaded:
                    obj.overlay.Load()
            elif obj.type == '<text>':
                fParams.fontsize = fontsize = obj.fontSize
                fParams.letterspace = obj.letterSpacing
                fParams.wordspace = obj.wordSpacing
                fParams.underline = bool(obj.fontFlags & fontflags.u)
                fParams.bold = bool(obj.fontFlags & fontflags.b)
                fParams.italic = bool(obj.fontFlags & fontflags.i)
                if astart is not None and aa != obj.a:
                    links.append((astart,
                     s.width,
                     aa,
                     acolor))
                    astart = None
                if obj.a and astart is None:
                    astart = s.width
                    aa = obj.a
                    acolor = obj.lcolor
                if pos:
                    s.Append(fParams, obj.letters[pos:])
                    pos = 0
                else:
                    s.Append(fParams, obj.letters)
            elif obj.type in '<table><img><input>':
                objectWidth = obj.width
                obj.inlineWidth = obj.control.width
                obj.inlineHeight = obj.control.height
                inlines.append((obj, s.GetWidth()))
                s.AddSpace(fParams, objectWidth)
            else:
                s.AddSpace(fParams, obj.width)

        if astart is not None:
            links.append((astart,
             s.width,
             aa,
             acolor))
        i = linewidth = lastlinepos = lastspace = lastlinewidth = lslinewidth = xpos = 0
        (rpush, lpush,) = self.GetMargins(self.contentHeight + self.batchHeight, self.contentHeight + self.batchHeight + self.GetLinespace())
        contentWidth = self.GetContentWidth()
        maxwidth = contentWidth - (lpush + rpush)
        for t in s:
            if t[4] == u' ':
                lastspace = i + 1
                lslinewidth = linewidth + t[0]
            linewidth += t[0]
            xpos += t[0]
            if linewidth > maxwidth:
                if lastspace == lastlinepos:
                    lastspace = i
                    lslinewidth = linewidth - t[0]
                line = uicore.font.GetGlyphString()
                line.shadow = None
                line += s[lastlinepos:lastspace]
                yield (rpush,
                 lpush,
                 startpos + lastlinepos,
                 line,
                 self.GetOthers(inlines, links, xpos - linewidth, lslinewidth, fParams))
                if not recurse:
                    return 
                lastlinepos = lastspace
                lastlinewidth = lslinewidth
                (rpush, lpush,) = self.GetMargins(self.contentHeight + self.batchHeight, self.contentHeight + self.batchHeight + self.GetLinespace())
                maxwidth = contentWidth - (lpush + rpush)
                linewidth -= lslinewidth
            i += 1

        if i > lastlinepos or xpos == 0:
            line = uicore.font.GetGlyphString()
            line.shadow = None
            line += s[lastlinepos:i]
            yield (rpush,
             lpush,
             startpos + lastlinepos,
             line,
             self.GetOthers(inlines, links, xpos - linewidth, linewidth, fParams))



    def GetOthers(self, inlines, links, x, width, fParam):
        endpos = x + width
        newinlines = []
        for (obj, pos,) in inlines:
            if x <= pos < endpos:
                newinlines.append((obj, pos - x))

        newlinks = []
        for (s, e, aa, color,) in links:
            e = min(e - x, width + s)
            s = max(s - x, 0)
            if s < e:
                link = uiutil.Bunch()
                link.left = s
                link.hint = aa.alt or ''
                link.url = aa.href
                link.width = e - s
                link.alink_color = color
                newlinks.append(link)

        return (newinlines, newlinks)



    def BreakLines(self, textbuffer, batchHeight = 0, abspos = 0, recurse = 1):
        if self.getWidths:
            self.GetWidths(textbuffer)
            return 
        if not len(textbuffer):
            return []
        self.batchHeight = batchHeight
        lines = []
        for (rpush, lpush, startpos, s, others,) in self.GetLine(textbuffer, abspos, recurse):
            (inlines, links,) = others
            bBox = s.GetBBox()
            baseHeight = max(s.baseHeight, self.attrStack[-1]['line-height']) or self.attrStack[-1]['font-size']
            baseLine = s.baseLine
            for (obj, pos,) in inlines:
                objectWidth = obj.width
                objectHeight = obj.height
                obj.inlineWidth = obj.control.width
                obj.inlineHeight = obj.control.height
                valign = getattr(obj, 'valign', html.ALIGNBASELINE)
                if valign in (html.ALIGNTOP, html.ALIGNSUB, html.ALIGNSUPER):
                    baseHeight = max(baseHeight, objectHeight)
                elif valign == html.ALIGNMIDDLE:
                    baseLine = max(baseLine, max(baseHeight, objectHeight) / 2 - (baseHeight - baseLine) / 2)
                    baseHeight = max(baseHeight, objectHeight)
                elif valign == html.ALIGNBOTTOM:
                    diffBefore = baseHeight - baseLine
                    baseHeight = max(baseHeight, objectHeight)
                    baseLine = baseHeight - diffBefore
                elif valign == html.ALIGNBASELINE:
                    if objectHeight > baseLine:
                        diffBefore = baseHeight - baseLine
                        baseHeight = objectHeight + diffBefore
                        baseLine = objectHeight

            lines.append((s,
             inlines,
             links,
             rpush,
             lpush,
             bBox,
             baseHeight,
             baseLine,
             startpos))
            self.batchHeight += baseHeight

        return lines



    def AddOverlay(self, attrs, x, y, lpush = None, rpush = None):
        attrs.height = getattr(attrs, 'height', 1) or 1
        if lpush is None or rpush is None:
            (lpush, rpush,) = self.GetMargins(y, y + attrs.height)
        if attrs.align == 'right':
            attrs.left = rpush + getattr(attrs, 'rightmargin', 0)
        elif attrs.align == 'left':
            attrs.left = lpush + getattr(attrs, 'leftmargin', 0)
        else:
            attrs.left = x + lpush
        attrs.top = y
        overlay = self.GetOverlay_Underlay(self.GetScrollEntry(attrs), self.sr.overlays_content)
        self.sr.overlays.append((overlay,
         attrs,
         x,
         y))
        return overlay



    def GetScrollEntry(self, attrs):
        decoClass = uicls.Get('SE_' + attrs.type)
        return uicls.ScrollEntryNode(decoClass=decoClass, attrs=attrs)



    def AddUnderlay(self, attrs, x, y):
        attrs.left = x
        attrs.top = y
        underlay = self.GetOverlay_Underlay(self.GetScrollEntry(attrs), self.sr.underlays_content)
        self.sr.underlays.append((underlay,
         attrs,
         x,
         y))



    def AddFloater(self):
        attrs = self.attrStack[-1]['attr']
        attrs.type = 'div'
        attrs.content = self.attrStack[-1]['bufferStack'][:]
        self.attrStack[-1]['bufferStack'] = None
        attrs.top = getattr(attrs, 'top', self.contentHeight)
        attrs.stack = self.attrStack[-1].copy()
        floater = self.GetOverlay_Underlay(self.GetScrollEntry(attrs), self.sr.overlays_content)
        floater.state = uiconst.UI_NORMAL
        uiutil.SetOrder(floater, 0)
        contentWidth = self.GetContentWidth()
        if self.attrStack[-1]['float'] and not getattr(attrs, 'left', 0):
            attrs.align = self.attrStack[-1]['float']
            y = attrs.top
            (lpush, rpush,) = self.GetMargins(-1, -1)
            if lpush + floater.width + rpush <= contentWidth:
                while True:
                    (lpush, rpush,) = self.GetMargins(y, y + floater.height)
                    if lpush + floater.width + rpush < contentWidth:
                        break
                    y += floater.height
                    if y > 100000:
                        raise RuntimeError("OK, at this point it seems obviousI don't know how to render this one.I give up so I won't loop forever.")

            floater.left = attrs.left = lpush
            floater.top = attrs.top = y
        self.contentHeight = max(self.contentHeight, floater.height)
        self.contentWidth = max(self.contentWidth, floater.width)
        self.sr.overlays.append((floater,
         attrs,
         getattr(attrs, 'left', 0),
         attrs.top))
        self.blockBufferClose = 0



    def GetOverlay_Underlay(self, data, container):
        if getattr(data, 'attrs', None) and getattr(data.attrs, 'uiwindow', None):
            overlay = data.attrs.uiwindow
            uiutil.Transplant(overlay, container)
        else:
            overlay = data.decoClass(parent=container)
            overlay.state = uiconst.UI_HIDDEN
            overlay.data = data
            overlay.Startup(self)
            overlay.loaded = 0
        return overlay



    def AddBorder(self, y, height):
        if self.getWidths:
            return 
        s = self.attrStack[-1]
        if s['background-color'] or s['border-left-width'] != 0 or s['border-right-width'] != 0 or s['border-top-width'] != 0 or s['border-bottom-width'] != 0:
            (lpush, rpush,) = self.GetMargins(y, y + 1)
            contentWidth = self.GetContentWidth()
            attrs = uiutil.Bunch()
            attrs.bgcolor = s['background-color']
            attrs.lbstyle = s['border-left-style']
            attrs.rbstyle = s['border-right-style']
            attrs.tbstyle = s['border-top-style']
            attrs.bbstyle = s['border-bottom-style']
            attrs.lbcolor = s['border-left-color']
            attrs.rbcolor = s['border-right-color']
            attrs.tbcolor = s['border-top-color']
            attrs.bbcolor = s['border-bottom-color']
            attrs.lbwidth = s['border-left-width']
            attrs.rbwidth = s['border-right-width']
            attrs.tbwidth = s['border-top-width']
            attrs.bbwidth = s['border-bottom-width']
            attrs.type = 'border'
            attrs.height = height - s['margin-top'] - s['margin-bottom']
            attrs.width = contentWidth - (lpush + rpush - s['padding-left'] - s['padding-right'] - s['border-left-width'] - s['border-right-width'])
            attrs.border = 10
            self.AddUnderlay(attrs, lpush - s['padding-left'] - s['border-left-width'], y + s['margin-top'])



    def AddTopBorders(self):
        if self.getWidths:
            return 
        self.attrStack[-1]['margin-top'] = self.GetPercent(self.attrStack[-1]['margin-top'], self.contentHeight)
        height = self.attrStack[-1]['margin-top'] + self.attrStack[-1]['padding-top'] + self.attrStack[-1]['border-top-width']
        if height:
            (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + height)
            data = {'decoClass': uicls.SE_Textline,
             'align': 'left',
             'lpush': lpush,
             'rpush': rpush,
             'maxBaseHeight': height,
             'stack': [],
             'pos': 0}
            _lines = [uicls.ScrollEntryNode(**data)]
            self.contentHeight = max(self.contentHeight, self.contentHeight + height)
            self.AddLines(_lines)



    def AddBottomBorders(self):
        if self.getWidths:
            return 
        self.attrStack[-1]['margin-bottom'] = self.GetPercent(self.attrStack[-1]['margin-bottom'], self.contentHeight)
        height = self.attrStack[-1]['margin-bottom'] + self.attrStack[-1]['padding-bottom'] + self.attrStack[-1]['border-bottom-width']
        if height:
            (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + height)
            data = {'decoClass': uicls.SE_Textline,
             'align': 'left',
             'lpush': lpush,
             'rpush': rpush,
             'maxBaseHeight': height,
             'stack': [],
             'pos': 0}
            _lines = [uicls.ScrollEntryNode(**data)]
            self.contentHeight = max(self.contentHeight, self.contentHeight + height)
            self.AddLines(_lines)



    def ApplyCSS(self, tag, attrs):
        s = self.css.ApplyCSS(tag, attrs, self.attrStack)
        self.SetStyles(s)
        self.attrStack[-1]['tag'] = tag
        self.attrStack[-1]['attr'] = attrs



    def SetStyles(self, s):
        if s is not None:
            self.attrStack[-1].update(s)



    def ParseStdStyles(self, attrs):
        if getattr(attrs, 'style', None):
            s = self.css.ParseCSS(attrs)
            self.attrStack[-1].update(s)
        if getattr(attrs, 'id', None):
            c = self.css.GetClass(attrs.id)
            if c:
                for (key, value,) in c.iteritems():
                    if key in ('tag', 'attr'):
                        continue
                    self.attrStack[-1][key] = value

        elif getattr(attrs, 'class', None):
            c = self.css.GetClass(getattr(attrs, 'class', None))
            if c:
                for (key, value,) in c.iteritems():
                    if key in ('tag', 'attr'):
                        continue
                    self.attrStack[-1][key] = value




    def AddStyles(self, stack, css):
        self.attrStack.append(stack)
        self.css = css.copy()



    def CheckURL(self, URL, getAnchor = 0):
        browser = uiutil.GetBrowser(self)
        currentURL = None
        if browser:
            currentURL = browser.sr.currentURL
        (URL, anchor,) = corebrowserutil.ParseURL(URL, currentURL)
        if URL.startswith('./'):
            if currentURL.endswith('/'):
                base = currentURL
            else:
                base = corebrowserutil.DirUp(currentURL)
            URL = base + URL[2:]
        elif URL.startswith('../'):
            base = corebrowserutil.DirUp(corebrowserutil.DirUp(currentURL))
            URL = base + URL[3:]
        if getAnchor:
            return (URL, anchor)
        return URL



    def LocalizeURL(self, url):
        if prefs.languageID != 'EN' and url and (url[:4] == 'res:' or url.find('res') > 0):
            current = None
            if '/en/' not in url:
                return url
            newUrl = url.replace('/en/', '/%s/' % prefs.languageID.lower())
            rf = blue.ResFile()
            if rf.FileExists(newUrl):
                return newUrl
            log.LogWarn('No localized image found for', url, 'with languageID', prefs.languageID)
        return url



    def OnStart_body(self, attrs):
        self.OnStart_default('body', attrs)
        self.bodyAttrs = attrs
        self.LoadBodyAttrs(attrs)



    def OnEnd_body(self):
        self.FlushBuffer()
        self.OnEnd_default('body')



    def OnStart_meta(self, attrs):
        content = attrs.content
        if content:
            options = content.split(';')
            for option in options:
                option = option.strip()
                if option.startswith('charset='):
                    charset = option[8:].strip().lower()
                    try:
                        import codecs
                        codecs.lookup(str(charset))
                        self.charset = charset
                    except:
                        sys.exc_clear()




    def IsIconOrSimilarType(self, attrs):
        if attrs.src.startswith('icon:'):
            return True
        return False



    def OnStart_img_Game(self, attrs):
        pass



    def OnStart_img(self, attrs):
        attrs.a = self.a
        attrs.loadlater = 0
        gameHandling = self.OnStart_img_Game(attrs)
        if gameHandling:
            (texture, tWidth, tHeight,) = gameHandling
            attrs.width = getattr(attrs, 'width', None) or tWidth
            attrs.height = getattr(attrs, 'height', None) or tHeight
        elif attrs.src.startswith('res:'):
            if getattr(attrs, 'localize', False):
                attrs.src = self.LocalizeURL(attrs.src)
            (texture, tWidth, tHeight,) = sm.GetService('browserImage').GetTextureFromURL(attrs.src, fromWhere='OnStart_img')
            attrs.width = getattr(attrs, 'width', None) or tWidth
            attrs.height = getattr(attrs, 'height', None) or tHeight
        else:
            browser = uiutil.GetBrowser(self)
            currentURL = None
            if browser:
                currentURL = browser.sr.currentURL
            attrs.src = self.CheckURL(attrs.src)
            (tWidth, tHeight,) = (32, 32)
            if attrs.width is None or attrs.height is None:
                cache = sm.GetService('browserImage').GetTextureInfoFromURL(attrs.src, currentURL, fromWhere='OnStart_img')
                if cache is not None:
                    (path, tWidth, tHeight, bw, bh,) = cache
            texture = None
            attrs.loadlater = 1
            attrs.currentURL = currentURL
        if attrs.width:
            if unicode(attrs.width).endswith('%'):
                attrs.width = int(float(unicode(attrs.width)[:-1]) / 100.0 * self.sr.content.width)
            else:
                attrs.width = int(attrs.width)
        if attrs.height:
            if unicode(attrs.height).endswith('%'):
                attrs.height = int(float(unicode(attrs.height)[:-1]) / 100.0 * self.sr.content.height)
            else:
                attrs.height = int(attrs.height)
        if not attrs.width:
            if attrs.height:
                attrs.width = int(attrs.height * (tWidth / float(tHeight)))
            else:
                attrs.width = tWidth
        if not attrs.height:
            if attrs.width:
                attrs.height = int(attrs.width * (tHeight / float(tWidth)))
            else:
                attrs.height = tHeight
        s = {'border-left-width': 0,
         'border-right-width': 0,
         'border-top-width': 0,
         'border-bottom-width': 0,
         'margin-left': 0,
         'margin-right': 0,
         'margin-top': 0,
         'margin-bottom': 0,
         'float': None}
        for side in ['left',
         'top',
         'right',
         'bottom']:
            if attrs.border is not None:
                s['border-%s-width' % side] = self.GetInt(attrs.border)
            if attrs.bordercolor:
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor, 1)

        if attrs.hspace is not None:
            s['margin-left'] = int(attrs.hspace)
            s['margin-right'] = int(attrs.hspace)
        if attrs.vspace is not None:
            s['margin-top'] = s['margin-bottom'] = int(attrs.vspace)
        if attrs.usemap:
            if attrs.usemap.startswith('#'):
                umap = attrs.usemap[1:]
                for each in self.areamap:
                    if each['name'] == umap:
                        attrs.areamap = each['coords']
                        break

        attrs.texture = texture
        attrs.type = 'img'
        if getattr(attrs, 'bgcolor', None):
            attrs.bgcolor = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + attrs.height)
        self.OnStart_default('img', attrs, s)
        for side in ['left',
         'top',
         'right',
         'bottom']:
            setattr(attrs, '%sborder' % side, self.attrStack[-1][('border-%s-width' % side)])
            setattr(attrs, '%scolor' % side, self.attrStack[-1][('border-%s-color' % side)])
            setattr(attrs, '%smargin' % side, self.attrStack[-1][('margin-%s' % side)])

        if self.attrStack[-1]['float']:
            attrs.align = self.attrStack[-1]['float']
        if (getattr(attrs, 'align', None) or 'None').lower() not in ('left', 'right'):
            img = self.GetInline(self.GetScrollEntry(attrs))
            obj = uiutil.Bunch()
            obj.type = '<img>'
            obj.width = attrs.width
            obj.height = attrs.height
            obj.attrs = attrs
            obj.valign = [None, 1][(attrs.align == 'center')] or self.attrStack[-1]['vertical-align']
            obj.control = img
            self.AddObjectToBuffer(obj)
        else:
            overlay = self.AddOverlay(attrs, 0, self.contentHeight, lpush=lpush, rpush=rpush)
            obj = uiutil.Bunch()
            obj.type = '<overlay>'
            obj.attrs = attrs
            obj.overlay = overlay
            obj.lpush = lpush
            obj.rpush = rpush
            self.AddObjectToBuffer(obj)
        self.attrStack.pop()



    def OnStart_script(self, attrs):
        self.OnStart_default('script', attrs)



    def OnData_script(self, data, attrs):
        pass



    def OnEnd_script(self):
        self.OnEnd_default('script')



    def OnStart_b(self, attrs):
        self.OnStart_default('b', attrs)
        self.FontFlag('b')



    def OnStart_i(self, attrs):
        self.OnStart_default('i', attrs)
        self.FontFlag('i')



    def OnStart_shadow(self, attrs):
        self.OnStart_default('shadow', attrs)
        self.FontFlag('shadow')



    def OnStart_u(self, attrs):
        self.OnStart_default('u', attrs)
        self.FontFlag('u')



    def OnStart_strong(self, attrs):
        self.OnStart_default('strong', attrs)
        self.FontFlag('strong')



    def OnStart_s(self, attrs):
        self.OnStart_default('s', attrs)
        self.FontFlag('s')



    def OnStart_em(self, attrs):
        self.OnStart_default('em', attrs)
        self.FontFlag('em')



    def OnStart_tt(self, attrs):
        self.OnStart_default('tt', attrs)
        self.FontFlag('tt')



    def OnStart_strike(self, attrs):
        self.OnStart_default('strike', attrs)
        self.FontFlag('strike')



    def OnStart_samp(self, attrs):
        self.OnStart_default('samp', attrs)
        self.FontFlag('samp')



    def OnStart_kbd(self, attrs):
        self.OnStart_default('kbd', attrs)
        self.FontFlag('kbd')



    def OnData_pre(self, data, attrs):
        for line in data.replace('\r', '').split('\n'):
            self.AddTextToBuffer(line, fromW='pre')
            if not self.textbuffer:
                self.NewLine()
            else:
                self.FlushBuffer()




    def FontFlag(self, tag):
        f = getattr(fontflags, tag, 0)
        if f:
            self.attrStack[-1]['fontflags'] |= f
            if fontflags.i & f:
                self.attrStack[-1]['font-style'] = 'i'
            if fontflags.b & f:
                self.attrStack[-1]['font-weight'] = 'b'
            if fontflags.u & f:
                self.attrStack[-1]['text-decoration'] += 'u'
            if fontflags.strike & f:
                self.attrStack[-1]['text-decoration'] += 's'
            if fontflags.o & f:
                self.attrStack[-1]['text-decoration'] += 'o'



    def OnStart_li(self, attrs):
        if self.attrStack[-1]['tag'] == 'li':
            self.OnEnd_li()
        self.FlushBuffer()
        tag = self.attrStack and self.attrStack[-1]['tag']
        if not self.sr.listIndex:
            self.sr.listIndex = [0]
        self.sr.listIndex[-1] += 1
        if tag == 'ul':
            bullType = attrs.__dict__.get('type', None) or self.attrStack[-1]['attr'].__dict__.get('type', 'disc')
            text = {'disc': unichr(8226),
             'square': unichr(9632),
             'circle': unichr(9675)}.get(bullType.lower(), unichr(8226))
        elif tag == 'ol':
            idx = self.sr.listIndex[-1]
            orderType = attrs.__dict__.get('type', None) or self.attrStack[-1]['attr'].__dict__.get('type', '1')
            if orderType in 'aA':
                text = '%s.' % unichr(96 + idx)
            elif orderType in 'iI':
                text = '%s' % uiutil.IntToRoman(idx).lower()
            else:
                text = '%s.' % self.sr.listIndex[-1]
            if orderType in 'AI':
                text = text.upper()
        else:
            text = unichr(8226)
        obj = uiutil.Bunch()
        obj.width = -24
        obj.type = '<nbsp>'
        self.AddObjectToBuffer(obj)
        self.AddTextToBuffer(text, fromW='OnStart_li')
        obj = uiutil.Bunch()
        obj.width = 24 - self.GetWidthInBuffer()
        obj.type = '<nbsp>'
        self.AddObjectToBuffer(obj)
        self.OnStart_default('li', attrs)
        self.list += 1



    def OnEnd_li(self):
        self.FlushBuffer()
        self.OnEnd_default('li')
        self.list = max(0, self.list - 1)



    def OnStartList(self):
        if self.attrStack and self.attrStack[-1]['tag'] not in ('ul', 'ol'):
            self.FlushBuffer()
        self.sr.listIndex.append(0)



    def OnDataList(self, data, attrs):
        if data.strip():
            log.LogError('Character data directly in UL?')



    def OnEndList(self):
        if len(self.attrStack) > 1 and self.attrStack[-2]['tag'] not in ('ul', 'ol'):
            self.FlushBuffer()
        if len(self.sr.listIndex):
            self.sr.listIndex.pop()



    def OnStart_ol(self, attrs):
        self.OnStart_default('ol', attrs)
        self.OnStartList()


    OnData_ol = OnDataList

    def OnEnd_ol(self):
        self.OnEndList()
        self.OnEnd_default('ol')



    def OnStart_ul(self, attrs):
        self.OnStart_default('ul', attrs)
        self.OnStartList()


    OnData_ul = OnDataList

    def OnEnd_ul(self):
        self.OnEndList()
        self.OnEnd_default('ul')



    def OnStart_sub(self, attrs):
        s = {'vertical-align': 4}
        self.OnStart_default('sub', attrs, s)



    def OnEnd_sub(self):
        self.OnEnd_default('sub')



    def OnStart_sup(self, attrs):
        s = {'vertical-align': 5}
        self.OnStart_default('sup', attrs, s)



    def OnEnd_sup(self):
        self.OnEnd_default('sup')



    def OnStart_h1(self, attrs):
        s = {'font-size': 28,
         'font-weight': 'b'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h1', attrs, s)
        self.FlushBuffer()



    def OnEnd_h1(self):
        self.FlushBuffer()
        self.OnEnd_default('h1')



    def OnStart_h2(self, attrs):
        s = {'font-size': 24,
         'font-weight': 'b'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h2', attrs, s)
        self.FlushBuffer()



    def OnEnd_h2(self):
        self.FlushBuffer()
        self.OnEnd_default('h2')



    def OnStart_h3(self, attrs):
        s = {'font-size': 20,
         'font-weight': 'b'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h3', attrs, s)
        self.FlushBuffer()



    def OnEnd_h3(self):
        self.FlushBuffer()
        self.OnEnd_default('h3')



    def OnStart_h4(self, attrs):
        s = {'font-size': 18,
         'font-weight': 'b'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h4', attrs, s)
        self.FlushBuffer()



    def OnEnd_h4(self):
        self.FlushBuffer()
        self.OnEnd_default('h4')



    def OnStart_h5(self, attrs):
        s = {'font-size': 16,
         'font-weight': 'b'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h5', attrs, s)
        self.FlushBuffer()



    def OnEnd_h5(self):
        self.FlushBuffer()
        self.OnEnd_default('h5')



    def OnStart_h6(self, attrs):
        s = {'font-size': 14,
         'font-weight': 'bold'}
        if attrs.align:
            s['text-align'] = attrs.align
        self.OnStart_default('h6', attrs, s)
        self.FlushBuffer()



    def OnEnd_h6(self):
        self.FlushBuffer()
        self.OnEnd_default('h6')



    def OnStart_style(self, attrs):
        self.OnStart_default('style', attrs)



    def OnData_style(self, data, attrs):
        self.css.ParseCSSData(data)



    def OnEnd_style(self):
        self.OnEnd_default('style')



    def OnStart_link(self, attrs):
        rel = attrs.rel
        t = attrs.type
        href = attrs.href
        if not rel or not href:
            return 
        if rel.lower() == 'stylesheet':
            url = self.CheckURL(href)
            browser = uiutil.GetBrowser(self)
            currentURL = None
            if browser:
                currentURL = browser.sr.currentURL
            if href.startswith('res:') or href.startswith('script:'):
                try:
                    f = blue.ResFile()
                    f.OpenAlways(href)
                    self.css.ParseCSSData(str(f.Read()))
                    del f
                except Exception:
                    log.LogException()
                return 
            fullPath = corebrowserutil.ParseURL(url, currentURL)[0]
            try:
                buff = corebrowserutil.GetStringFromURL(*(corebrowserutil.ParseURL(fullPath)[:1] + (None,))).read()
                self.css.ParseCSSData(buff)
            except urllib2.URLError as what:
                sys.exc_clear()
            except Exception:
                log.LogException()



    def OnStart_title(self, attrs):
        self.OnStart_default('title', attrs)



    def OnData_title(self, data, attrs):
        data = data.strip()
        self.title = data
        if self.sr.window and getattr(self.sr.window, 'SetCaption', None):
            self.sr.window.SetCaption(data)



    def OnEnd_title(self):
        self.OnEnd_default('title')



    def OnStart_form(self, attrs):
        if not self or getattr(self, 'sr', None) is None:
            return 
        if self.sr.form:
            self.OnEnd_form()
        if self.sr.Get('browser', None):
            self.sr.form = corebrowserutil.NewBrowserForm(attrs, _weakref.proxy(self.sr.browser))
        else:
            self.sr.form = corebrowserutil.NewBrowserForm(attrs, _weakref.proxy(self))



    def OnEnd_form(self):
        self.sr.forms.append(self.sr.form)
        self.sr.form = None



    def OnStart_input(self, attrs):
        form = self.sr.form or getattr(attrs, 'form', None)
        if form is None:
            form = self.sr.form = corebrowserutil.NewBrowserForm(attrs, _weakref.proxy(self))
        s = {'width': None,
         'height': None}
        self.OnStart_default('input', attrs, s)
        if not hasattr(attrs, 'valign'):
            attrs.valign = 1
        attrs.fontcolor = self.attrStack[-1]['color']
        attrs.bordercolor = self.attrStack[-1]['color']
        attrs.form = form
        attrs.width = self.attrStack[-1]['width']
        attrs.height = self.attrStack[-1]['height']
        if getattr(attrs, 'value', None):
            attrs.value = self.sr.parser.decode_string(attrs.value)
        obj = form.AddInput(attrs, not self.getWidths)
        if obj:
            self.AddObjectToBuffer(obj)
        self.attrStack.pop()



    def OnEnd_input(self):
        pass



    def OnStart_select(self, attrs):
        form = self.sr.form or getattr(attrs, 'form', None)
        if form is None:
            form = self.sr.form = corebrowserutil.NewBrowserForm(attrs, _weakref.proxy(self))
        self.sr.select = uiutil.Bunch()
        self.sr.select.attrs = attrs
        self.sr.select.attrs.form = form
        self.sr.select.options = []
        s = {'width': None,
         'height': None}
        self.OnStart_default('select', attrs, s)
        attrs.fontcolor = self.attrStack[-1]['color']
        attrs.width = self.attrStack[-1]['width']
        attrs.height = self.attrStack[-1]['height']



    def OnEnd_select(self):
        if self.sr.select is None:
            raise RuntimeError('ParsingError', {'what': 'Unmatched select end'})
        obj = self.sr.select.attrs.form.AddSelect(self.sr.select.attrs, self.sr.select.options, not self.getWidths)
        if obj:
            self.AddObjectToBuffer(obj)
        self.sr.select = None
        self.OnEnd_default('select')



    def OnData_select(self, data, attrs):
        pass



    def OnStart_option(self, attrs):
        self.OnStart_default('option', attrs)



    def OnData_option(self, data, attrs):
        self.sr.buffer += data



    def OnEnd_option(self):
        if self.sr.select is not None:
            self.sr.buffer = self.sr.buffer.replace('\n', '').replace('\r', '')
            value = self.attrStack[-1]['attr'].value
            if value is None:
                value = self.sr.buffer
            self.sr.select.options.append((self.sr.buffer, value, self.attrStack[-1]['attr'].selected))
            self.sr.buffer = ''
        else:
            log.LogWarn('Bogus HTML syntax, Option outside any select')
        self.OnEnd_default('option')



    def OnStart_textarea(self, attrs):
        s = {'width': None,
         'height': None}
        self.OnStart_default('textarea', attrs, s)
        form = self.sr.form or getattr(attrs, 'form', None)
        if form is None:
            form = self.sr.form = corebrowserutil.NewBrowserForm(attrs, _weakref.proxy(self))
        attrs.fontcolor = self.attrStack[-1]['color']
        attrs.width = self.attrStack[-1]['width']
        attrs.height = self.attrStack[-1]['height']
        attrs.form = form



    def OnData_textarea(self, data, attrs):
        data = data.replace('\n', '<br>').replace('\r', '')
        self.sr.buffer += data



    def OnEnd_textarea(self):
        attrs = self.attrStack[-1]['attr']
        attrs.value = self.sr.buffer
        obj = attrs.form.AddTextArea(attrs, not self.getWidths)
        if obj:
            self.AddObjectToBuffer(obj)
        self.sr.buffer = ''
        self.OnEnd_default('textarea')



    def OnStart_center(self, attrs):
        self.FlushBuffer()
        self.OnStart_default('center', attrs)
        self.attrStack[-1]['text-align'] = 'center'



    def OnEnd_center(self):
        self.FlushBuffer()
        self.OnEnd_default('center')



    def OnStart_p(self, attrs):
        if self.attrStack[-1]['tag'] == 'p':
            self.OnEnd_p()
        s = {}
        s['text-align'] = getattr(attrs, 'align', None)
        self.OnStart_default('p', attrs, s)
        self.NewLine()
        if int(self.attrStack[-1]['text-indent']) > 0:
            obj = uiutil.Bunch()
            obj.width = int(self.attrStack[-1]['text-indent'])
            obj.type = '<list>'
            self.AddObjectToBuffer(obj)
        self.attrStack[-1]['pstart'] = self.contentHeight
        self.AddTopBorders()



    def OnEnd_p(self):
        if self.attrStack[-1]['margin-bottom'] == 0:
            self.NewLine()
        else:
            self.FlushBuffer()
        self.AddBottomBorders()
        self.AddBorder(self.attrStack[-1]['pstart'], self.contentHeight - self.attrStack[-1]['pstart'])
        self.OnEnd_default('p')



    def OnStart_font(self, attrs):
        s = {}
        fontfamily = getattr(attrs, 'style', None) or self.attrStack[-1]['font-family']
        s['font-family'] = fontfamily
        fontsize = getattr(attrs, 'size', None)
        basefontsize = None
        if unicode(fontsize).startswith('+') or unicode(fontsize).startswith('-'):
            try:
                m = int(fontsize[1:])
            except:
                m = 0
                sys.exc_clear()
            basefontsize = max(0, min(7, self.attrStack[-1]['basefontsize'] + [-1, 1][unicode(fontsize).startswith('+')] * m))
        elif len(unicode(fontsize)) == 1 and unicode(fontsize) in '1234567':
            try:
                basefontsize = int(fontsize)
            except:
                sys.exc_clear()
        if basefontsize is not None:
            fontsize = {1: 6,
             2: 8,
             3: 10,
             4: 12,
             5: 14,
             6: 17,
             7: 20}.get(basefontsize, fontsize)
            s['basefontsize'] = basefontsize
        spacing = getattr(attrs, 'letter-spacing', None) or getattr(attrs, 'space', None)
        if fontsize is not None and unicode(fontsize).isdigit():
            s['font-size'] = int(fontsize)
        if spacing is not None:
            s['letter-spacing'] = int(spacing)
        if getattr(attrs, 'color', None):
            s['color'] = uiutil.ParseHTMLColor(getattr(attrs, 'color', None), 1)
        self.OnStart_default('font', attrs, s)



    def OnEnd_font(self):
        self.OnEnd_default('font')



    def OnStart_br(self, attrs):
        if not self.textbuffer:
            self.NewLine()
        else:
            self.FlushBuffer()



    def OnStart_hr(self, attrs):
        self.FlushBuffer()
        s = {'margin-top': 2,
         'margin-bottom': 2,
         'padding-top': 0,
         'padding-bottom': 0,
         'border-top-width': 0,
         'border-bottom-width': 0}
        self.OnStart_default('hr', attrs, s)
        self.AddTopBorders()
        self.FlushBuffer()
        lineHeight = int(getattr(attrs, 'size', 0) or 1)
        (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + lineHeight)
        obj = uiutil.Bunch()
        obj.type = '<hr>'
        obj.width = 0
        obj.height = lineHeight
        obj.lpush = lpush
        obj.rpush = rpush
        obj.attrs = attrs
        self.AddObjectToBuffer(obj)
        self.contentHeight += lineHeight
        self.FlushBuffer()
        self.AddBottomBorders()
        self.attrStack.pop()



    def ClearAttrs(self, s):
        for side in ['left',
         'top',
         'right',
         'bottom']:
            s['border-%s-width' % side] = 0
            s['border-%s-color' % side] = None
            s['margin-%s' % side] = 0

        s['background-color'] = None



    def OnStart_blockquote(self, attrs):
        self.NewLine()
        self.OnStart_default('blockquote', attrs)
        self.blockquote += 1



    def OnEnd_blockquote(self):
        self.NewLine()
        self.OnEnd_default('blockquote')
        self.blockquote = max(0, self.blockquote - 1)



    def OnStart_var(self, attrs):
        s = {'font-style': 'i'}
        self.OnStart_default('var', attrs, s)



    def OnEnd_var(self):
        self.OnEnd_default('var')



    def OnStart_cite(self, attrs):
        s = {'font-style': 'i'}
        self.OnStart_default('cite', attrs, s)



    def OnEnd_cite(self):
        self.OnEnd_default('cite')



    def OnStart_address(self, attrs):
        s = {'font-style': 'i'}
        self.OnStart_default('address', attrs, s)



    def OnEnd_address(self):
        self.OnEnd_default('address')



    def OnStart_dfn(self, attrs):
        s = {'font-style': 'i'}
        self.OnStart_default('dfn', attrs, s)



    def OnEnd_dfn(self):
        self.OnEnd_default('dfn')



    def OnStart_code(self, attrs):
        s = {'font-family': fontConst.DEFAULT_FONT}
        self.OnStart_default('code', attrs, s)
        self.plainload = 1



    def OnEnd_code(self):
        self.plainload = 0
        self.OnEnd_default('code')



    def OnStart_frame(self, attrs):
        pass



    def OnStart_div(self, attrs):
        self.FlushBuffer()
        contentWidth = self.GetContentWidth()
        if hasattr(attrs, 'width') and type(attrs.width) == str and attrs.width.endswith('%'):
            attrs.width = self.GetInt(attrs.width) * contentWidth / 100.0
        else:
            attrs.width = int(getattr(attrs, 'width', None) or contentWidth)
        attrs.height = int(getattr(attrs, 'height', None) or 0)
        attrs.left = int(getattr(attrs, 'left', None) or 0)
        attrs.top = int(getattr(attrs, 'top', self.contentHeight) or 0)
        s = {'position': 'unset',
         'text-align': 'left',
         'float': None,
         'width': attrs.width,
         'height': attrs.height,
         'left': attrs.left,
         'top': attrs.top}
        for side in ['left',
         'top',
         'right',
         'bottom']:
            s['border-%s-width' % side] = int(attrs.border or 0)
            if attrs.bordercolor:
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor, 1)

        if attrs.align:
            s['text-align'] = attrs.align
            s['align'] = attrs.align
        if attrs.bgcolor is not None:
            s['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        self.OnStart_default('div', attrs, s)
        if self.attrStack[-1]['width'] is not None:
            attrs.width = self.attrStack[-1]['width']
        if self.attrStack[-1]['height'] is not None:
            attrs.width = self.attrStack[-1]['height']
        if self.attrStack[-1]['position'] in ('absolute', 'relative') or self.attrStack[-1]['float'] in ('left', 'right'):
            self.attrStack[-1]['bufferStack'] = [('AddStyles', (self.attrStack[-1].copy(), self.css.copy()))]
            self.divs += 1
        else:
            self.attrStack[-1]['pstart'] = self.contentHeight
            self.AddTopBorders()



    def OnEnd_div(self):
        if self.attrStack[-1]['bufferStack'] and self.attrStack[-1]['tag'] == 'div':
            self.divs = max(0, self.divs - 1)
            self.AddFloater()
        else:
            self.FlushBuffer()
            self.AddBottomBorders()
            self.AddBorder(self.attrStack[-1]['pstart'], self.contentHeight - self.attrStack[-1]['pstart'])
        self.OnEnd_default('div')



    def OnStart_table(self, attrs):
        if self.sr.table is not None:
            self.OnEnd_table()
        self.FlushBuffer()
        self.sr.table = attrs
        self.sr.table.rows = []
        self.sr.table.colgroups = []
        s = self.GetTableAttrs(attrs)
        self.OnStart_default('table', attrs, s)
        if self.attrStack[-1]['border-collapse']:
            for side in ['left',
             'top',
             'right',
             'bottom']:
                self.attrStack[-1]['spacing-%s' % side] = 0

        self.attrStack[-1]['table-width'] = attrs.width
        self.attrStack[-1]['table-height'] = attrs.height



    def OnEnd_table(self):
        if self.sr.table is None:
            self.OnEnd_default('table')
            self.FlushBuffer()
            return 
        attrs = self.attrStack[-1]['attr']
        attrs.type = 'table'
        attrs.charset = self.charset
        se = self.GetScrollEntry(attrs)
        se.attrs = self.sr.table
        table = self.GetInline(se)
        if getattr(attrs, 'align', None) is None:
            obj = uiutil.Bunch()
            obj.type = '<table>'
            obj.width = table.width
            obj.height = table.height
            obj.attrs = attrs
            obj.valign = self.attrStack[-1]['vertical-align']
            obj.control = table
            self.AddObjectToBuffer(obj)
        else:
            attrs.height = table.height
            attrs.width = table.width
            table.Close()
            self.AddOverlay(attrs, 0, self.contentHeight)
        if self.destroyed:
            return 
        self.sr.table = None
        self.OnEnd_default('table')
        self.FlushBuffer()



    def OnData_table(self, data, attrs):
        pass



    def GetTableAttrs(self, attrs):
        s = {}
        for side in ['left',
         'top',
         'right',
         'bottom']:
            s['border-%s-width' % side] = 0
            s['border-%s-color' % side] = self.attrStack[-1]['color']
            s['spacing-%s' % side] = 1
            s['padding-%s' % side] = 2

        s['background-color'] = None
        s['background-image'] = None
        for side in ['left',
         'top',
         'right',
         'bottom']:
            if hasattr(attrs, 'border') and attrs.border and unicode(attrs.border).isdigit():
                s['border-%s-width' % side] = int(attrs.border)
                s['border-%s-style' % side] = 1
            if getattr(attrs, 'bordercolor', None):
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor, 1, error=1) or s[('border-%s-color' % side)]
            if getattr(attrs, 'cellspacing', None) is not None:
                s['spacing-%s' % side] = max(0, int((int(attrs.cellspacing) + [0, 1][(side in ('right', 'bottom'))]) / 2))
            if getattr(attrs, 'cellpadding', None) is not None:
                s['padding-%s' % side] = max(0, int(attrs.cellpadding))

        if getattr(attrs, 'bgcolor', None) is not None:
            s['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        return s



    def OnStart_colgroup(self, attrs):
        if self.sr.table is None:
            print 'parsing error, no open table to add colgroup into'
            return 
        s = {}
        s['colgroup-width'] = attrs.width
        s['colgroup-span'] = attrs.span
        s['cols'] = []
        self.OnStart_default('colgroup', attrs, s)



    def OnData_colgroup(self, data, attrs):
        pass



    def OnEnd_colgroup(self):
        s = self.attrStack[-1]
        for i in xrange(s['colgroup-span'] or len(s['cols']) or 1):
            if len(s['cols']):
                self.sr.table.colgroups.append(s['cols'].pop(0) or s['colgroup-width'])
            else:
                self.sr.table.colgroups.append(s['colgroup-width'])

        self.OnEnd_default('colgroup')



    def OnStart_col(self, attrs):
        if self.sr.table is None:
            print 'parsing error, no open table to add col into'
            return 
        if not self.attrStack[-1].has_key('cols'):
            print 'parsing error, no open colgroup to add col into'
            return 
        for i in xrange(attrs.span or 1):
            self.attrStack[-1]['cols'].append(attrs.width)




    def OnStart_tr(self, attrs):
        if self.sr.table is None:
            print 'parsing error, no open table to add tr into'
            return 
        attrs.cols = []
        if unicode(attrs.height).isdigit():
            attrs.height = int(attrs.height or 0)
        else:
            attrs.height = 0
        s = {}
        for side in ['left',
         'top',
         'right',
         'bottom']:
            if getattr(attrs, 'border', 0):
                s['border-%s-width' % side] = int(attrs.border or 0)
            if getattr(attrs, 'bordercolor', None):
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor or '#000000', 1)
            if hasattr(attrs, 'cellspacing') and attrs.cellspacing is not None:
                s['spacing-%s' % side] = max(0, int((int(attrs.cellspacing) + [0, 1][(side in ('right', 'bottom'))]) / 2))
            if hasattr(attrs, 'cellpadding') and attrs.cellpadding is not None:
                s['padding-%s' % side] = max(0, int(attrs.cellpadding))

        if attrs.valign is not None:
            s['vertical-align'] = getattr(html, 'ALIGN%s' % unicode(attrs.valign).upper(), 1)
        else:
            s['vertical-align'] = html.ALIGNTOP
        s['background-image'] = None
        s['background-color'] = None
        if attrs.bgcolor is not None:
            s['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        self.OnStart_default('tr', attrs, s)
        attrs.styles = self.attrStack[-1].copy()
        self.sr.table.rows.append(attrs)



    def OnEnd_tr(self):
        self.OnEnd_default('tr')



    def OnData_tr(self, data, attrs):
        pass



    def GetInt(self, stringVal):
        if stringVal is None:
            return stringVal
        stringVal = filter(lambda x: x in '0123456789', unicode(stringVal))
        return int(stringVal)



    def GetPercent(self, value, reference):
        if type(value) == str and value.endswith('%'):
            value = self.GetInt(value)
            return int(value * reference / 100.0)
        return int(value)



    def GetInline(self, data):
        inline = data.decoClass(parent=self.sr.cacheContainer)
        inline.data = data
        inline.Startup(self)
        inline.loaded = 0
        return inline



    def OnStart_td(self, attrs):
        if self.sr.table is None:
            print 'parsing error, no open table to add td into'
            return 
        if not getattr(self.sr.table, 'rows', None):
            attrs.height = getattr(attrs, 'height', None)
            self.OnStart_tr(attrs)
        h = unicode(getattr(attrs, 'height', None))
        if h and h[-1] == '%':
            attrs.height = None
        attrs.content = []
        s = {}
        s['text-align'] = 'left'
        for side in ['left',
         'top',
         'right',
         'bottom']:
            s['border-%s-width' % side] = int(getattr(attrs, 'border', 0))
            if getattr(attrs, 'bordercolor', None):
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor or '#000000', 1)

        if getattr(attrs, 'valign', None):
            s['vertical-align'] = getattr(html, 'ALIGN%s' % unicode(attrs.valign).upper(), 1)
        s['text-align'] = getattr(attrs, 'align', None) or s['text-align']
        if attrs.bgcolor is not None:
            s['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        self.OnStart_default('td', attrs, s)
        attrs.styles = self.attrStack[-1].copy()
        attrs.css = self.css.copy()
        self.attrStack[-1]['bufferStack'] = []
        self.sr.table.rows[-1].cols.append(attrs)



    def OnEnd_td(self):
        if self.attrStack[-1]['bufferStack'] is not None and self.attrStack[-1]['tag'] == 'td':
            if self.sr.table and len(self.sr.table.rows[-1].cols):
                self.sr.table.rows[-1].cols[-1].content = self.attrStack[-1]['bufferStack'][:]
        else:
            log.LogWarn('Ending unknown td')
        self.OnEnd_default('td')



    def OnStart_th(self, attrs):
        if self.sr.table is None:
            print 'parsing error, no open table to add th into'
            return 
        if not getattr(self.sr.table, 'rows', None):
            attrs.height = getattr(attrs, 'height', None)
            self.OnStart_tr(attrs)
        h = unicode(getattr(attrs, 'height', None))
        if h and h[-1] == '%':
            attrs.height = None
        attrs.content = []
        s = {}
        s['text-align'] = 'center'
        s['font-weight'] = 'b'
        for side in ['left',
         'top',
         'right',
         'bottom']:
            s['border-%s-width' % side] = int(getattr(attrs, 'border', 0))
            if getattr(attrs, 'bordercolor', None):
                s['border-%s-color' % side] = uiutil.ParseHTMLColor(attrs.bordercolor or '#000000', 1)

        if getattr(attrs, 'valign', None):
            s['vertical-align'] = getattr(html, 'ALIGN%s' % unicode(attrs.valign).upper(), 1)
        s['text-align'] = getattr(attrs, 'align', None) or s['text-align']
        if attrs.bgcolor is not None:
            s['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        self.OnStart_default('th', attrs, s)
        attrs.styles = self.attrStack[-1].copy()
        attrs.css = self.css.copy()
        self.attrStack[-1]['bufferStack'] = []
        self.sr.table.rows[-1].cols.append(attrs)



    def OnEnd_th(self):
        if self.attrStack[-1]['bufferStack'] is not None and self.attrStack[-1]['tag'] == 'th':
            if self.sr.table and len(self.sr.table.rows[-1].cols):
                self.sr.table.rows[-1].cols[-1].content = self.attrStack[-1]['bufferStack'][:]
        else:
            log.LogWarn('Ending unknown th')
        self.OnEnd_default('th')



    def OnStart_a(self, attrs):
        s = {'font-weight': 'b',
         'text-decoration': 'u',
         'color': self.attrStack[-1]['link-color'],
         'link-color': None}
        visited = settings.public.ui.VisitedURLs or []
        self.OnStart_default('a', attrs, s)
        self.CheckForMailAddress(attrs)
        self.attrStack[-1]['link-color'] = self.attrStack[-1]['link-color'] or self.attrStack[-1]['color']
        if attrs.href:
            attrs.href = attrs.href
        attrs.color = [self.attrStack[-1]['link-color'], self.attrStack[-1]['vlink-color'] or self.attrStack[-1]['link-color']][(attrs.href in visited)]
        self.a = attrs



    def CheckForMailAddress(self, attrs):
        pass



    def OnEnd_a(self):
        self.a = None
        self.OnEnd_default('a')



    def OnStart_span(self, attrs):
        self.OnStart_default('span', attrs)
        self.ParseStdStyles(attrs)



    def OnEnd_span(self):
        self.OnEnd_default('span')



    def OnStart_map(self, attrs):
        self.OnStart_default('map', attrs)
        if attrs.name:
            amap = {}
            amap['name'] = attrs.name
            amap['coords'] = []
            self.areamap.append(amap)
        else:
            print 'no name attribute set in tag map',
            print self.name
            return 



    def OnData_map(self, data, attrs):
        pass



    def OnEnd_map(self):
        self.OnEnd_default('map')



    def OnStart_area(self, attrs):
        if self.attrStack[-1]['tag'] != 'map':
            print 'unexpected area tag',
            print self.name
        if attrs.shape and attrs.coords and attrs.href:
            if attrs.shape != 'rect':
                return 
            if attrs.coords.count(',') != 3:
                return 
            self.CheckForMailAddress(attrs)
            (x0, y0, x1, y1,) = attrs.coords.split(',')
            area = {}
            area['x0'] = int(x0)
            area['y0'] = int(y0)
            area['x1'] = int(x1)
            area['y1'] = int(y1)
            area['url'] = attrs.href
            self.areamap[-1]['coords'].append(area)




