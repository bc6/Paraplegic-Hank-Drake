import util
import blue
import base
import uthread
import sys
import menu
import errno
import log
import corebrowserutil
import parser
import urllib2
import urlparse
import html
import trinity
import _weakref
import fontflags
import gps
import fontConst
import localization
import localizationUtil
from util import ResFile
WORD_BOUNDARIES = [' ',
 '.',
 ',',
 ':',
 ';']
import uiconst
import uiutil
import uicls
import service
globals().update(service.consts)

class EditCore(parser.ParserBase, uicls.Scroll):
    __guid__ = 'uicls.EditCore'
    default_name = 'edit_multiline'
    default_align = uiconst.TOTOP
    default_width = 0
    default_height = 100
    default_maxLength = None
    default_readonly = False
    default_showattributepanel = 0
    default_hideBackground = False
    default_setvalue = ''
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontcolor = (1.0, 1.0, 1.0, 1.0)
    default_letterspace = fontConst.DEFAULT_LETTERSPACE

    def ApplyAttributes(self, attributes):
        uicls.Scroll.ApplyAttributes(self, attributes)
        self._initingEdit = True
        parser.ParserBase.Prepare(self)
        self.sr.currentURL = None
        self.sr.currentData = None
        self.sr.currentTXT = None
        self.sr.window = None
        self.sr.sessionreload = False
        self._knownWidth = None
        self.xmargin = 8
        self.ymargin = 6
        self.sr.resizeTimer = None
        self.sr.window = None
        self.sr.positions = {}
        self._selecting = 0
        self._showCursor = True
        self._maxGlobalCursorIndex = 0
        self.sr.startSelectionPos = (0, 0)
        self.sr.scrollTimer = None
        self.sr.attribPanel = None
        self.maxletters = None
        self.globalSelectionRange = (None, None)
        self.globalSelectionInitpos = None
        self.globalCursorPos = 0
        self.debug = 0
        self.htmldebug = 0
        self.IsBrowser = 1
        self.AttribStateChange = None
        self.updating = 0
        self.readonly = 0
        self.autoScrollToBottom = 0
        self.fontFlag = 0
        self.href = None
        self.fontSize = self.defaultFontSize = attributes.get('fontsize', self.default_fontsize)
        self.fontColor = self.defaultFontColor = attributes.get('fontcolor', self.default_fontcolor)
        self.sr.cookieMgr = corebrowserutil.CookieManager()
        self.resizing = 0
        self.preCompText = None
        self.allowPrivateDrops = 0
        self.sr.content.GetMenu = self.GetMenuDelegate
        self.sr.content.OnKeyDown = self.OnKeyDown
        self.sr.content.OnDropData = self.OnContentDropData
        self.sr.content.OnMouseDown = self.OnMouseDown
        self.sr.content.OnMouseUp = self.OnMouseUp
        self.sr.content.OnMouseMove = self.OnMouseMove
        self.sr.content.cursor = uiconst.UICURSOR_IBEAM
        self._AttribStateChange()
        self.hideBackground = attributes.get('hideBackground', self.default_hideBackground)
        maxLength = attributes.get('maxLength', self.default_maxLength)
        self.SetMaxLength(maxLength)
        readonly = attributes.get('readonly', self.default_readonly)
        if readonly:
            self.ReadOnly()
        else:
            showattributepanel = attributes.get('showattributepanel', self.default_showattributepanel)
            if showattributepanel:
                self.ShowAttributePanel()
            self.Editable(showpanel=showattributepanel)
        setvalue = attributes.get('setvalue', self.default_setvalue)
        self.SetValue(setvalue)
        if not self.destroyed:
            self._initingEdit = False



    def Prepare_Underlay_(self):
        self.sr.backgroundColorContainer = uicls.Container(name='backgroundColorContainer', parent=self)
        uicls.Scroll.Prepare_Underlay_(self)



    def ShowAttributePanel(self):
        if not self.readonly:
            self.sr.attribPanel = uicls.FontAttribPanel(align=uiconst.TOTOP, pos=(0, 0, 0, 20), parent=self, idx=0, state=uiconst.UI_HIDDEN)



    def GetLinespace(self):
        if not self or not getattr(self, 'sr', None):
            return 0
        if self.sr.nodes:
            if self.sr.nodes[-1].maxBaseHeight is not None:
                return self.sr.nodes[-1].maxBaseHeight
            if self.sr.nodes[-1].size is not None:
                return int(self.sr.nodes[-1].size)
        return 18



    def Reset(self, *args, **kw):
        (cw, ch,) = self.sr.content.GetAbsoluteSize()
        if cw <= 0:
            uicore.uilib.RecalcWindows()
        self._knownWidth = max(100, cw)
        uiutil.Flush(self.sr.overlays_content)
        uiutil.Flush(self.sr.underlays_content)



    def LoadHTML(self, htmlstr, reload = 0, scrollTo = None, newThread = 1, breakOnly = 0):
        if not self or self.destroyed:
            return 
        if self._loading:
            return 
        self._loading = 1
        self.sr.resizeTimer = None
        self.tagdepth = 0
        self.keybuffer = []
        self.textbuffers = []
        formdatalist = []
        if htmlstr is None:
            if self.sr.currentTXT is not None:
                for form in self.sr.forms:
                    formdatalist.append(form.GetFields())

        else:
            self.sr.currentTXT = htmlstr
        htmlstr = htmlstr or self.sr.currentTXT or ''
        self._LoadHTML(htmlstr)
        if self.destroyed:
            return 
        if breakOnly:
            self._loading = 0
            return 
        self.SetSelectionRange(None, None)
        self.RenderLines(scrollTo, formdatalist)
        if hasattr(self, 'CheckOverlaysAndUnderlays'):
            self.CheckOverlaysAndUnderlays()
        self.UpdateNodesCursorIndexes()
        if not self.readonly:
            self.DoContentResize()
            self.SetCursorPos(0)
        else:
            self.RefreshCursorAndSelection()
        self._loading = 0



    def RenderLines(self, scrollTo = None, formdatalist = []):
        self.sr.lines.insert(0, uicls.ScrollEntryNode(decoClass=uicls.SE_Space, height=self.ymargin))
        if len(self.sr.lines) == 1 and not self.readonly:
            self.sr.lines.append(self.GetFirstLine())
        self.LoadContent(contentList=self.sr.lines, scrollTo=scrollTo)
        if len(formdatalist) == len(self.sr.forms):
            for i in xrange(len(formdatalist)):
                self.sr.forms[i].SetFields(formdatalist[i])

        if self.sr.window and hasattr(self.sr.window, 'LoadEnd'):
            self.sr.window.LoadEnd()



    def DoFontChange(self, *args):
        self.DoContentResize()



    def IsLoading(self):
        return self._loading



    def LoadBodyAttrs(self, attrs):
        uiutil.Flush(self.sr.background)
        if self.hideBackground:
            self.RemoveActiveFrame()
            uiutil.Flush(self.sr.backgroundColorContainer)
            self.HideBackground(alwaysHidden=self.hideBackground)
        if not attrs:
            return 
        self.bgscrolltype = html.BG_TILED
        for each in ('link', 'alink', 'vlink'):
            if getattr(attrs, each, None):
                self.attrStack[-1]['%s-color' % each] = uiutil.ParseHTMLColor(getattr(attrs, each, None), 1)

        if attrs.text:
            self.attrStack[-1]['color'] = uiutil.ParseHTMLColor(attrs.text, 1)
        if attrs.bgcolor:
            self.attrStack[-1]['background-color'] = uiutil.ParseHTMLColor(attrs.bgcolor, 1)
        if attrs.background:
            self.attrStack[-1]['background-image'] = attrs.background
        self.ParseStdStyles(attrs)
        if not self.hideBackground:
            if self.attrStack[-1]['background-color']:
                col = self.attrStack[-1]['background-color']
                uicls.Fill(parent=self.sr.backgroundColorContainer, color=col)
                self.attrStack[-1]['background-color'] = None
            if self.attrStack[-1]['background-image']:
                (aL, aT, aW, aH,) = self.parent.GetAbsolute()
                windowWidth = aW
                windowHeight = aH
                pic = uicls.Sprite()
                pic.left = self.attrStack[-1]['background-image-left']
                pic.top = self.attrStack[-1]['background-image-top']
                pic.width = self.attrStack[-1]['background-image-width']
                pic.height = self.attrStack[-1]['background-image-height']
                if self.attrStack[-1]['background-image'].startswith('icon:'):
                    log.LogError('Icon:* is not legal background path')
                path = self.CheckURL(self.attrStack[-1]['background-image'])
                (texture, tWidth, tHeight,) = sm.GetService('browserImage').GetTextureFromURL(path, fromWhere='Bastard::LoadBodyAttrs')
                if self.destroyed:
                    return 
                pic.width = self.attrStack[-1]['background-image-width'] or tWidth
                pic.height = self.attrStack[-1]['background-image-height'] or tHeight
                pic.texture = texture
                for pos in self.attrStack[-1]['background-position']:
                    if pos == 'top':
                        pic.top = 0
                    elif pos == 'bottom':
                        pic.left = windowHeight - pic.height
                    elif pos == 'middle':
                        pic.left = (windowHeight - pic.height) / 2
                    elif pos == 'left':
                        pic.left = 0
                    elif pos == 'right':
                        pic.left = windowWidth - pic.width
                    elif pos == 'center':
                        pic.left = (windowWidth - pic.width) / 2

                if self.attrStack[-1]['background-image-color']:
                    pic.SetRGB(*self.attrStack[-1]['background-image-color'])
                row = uicls.Container(name='row', align=uiconst.TOTOP, pos=(0,
                 0,
                 0,
                 pic.height))
                if self.attrStack[-1]['background-repeat'] in ('repeat', 'repeat-x'):
                    for x in xrange(max(windowWidth / pic.width, 2)):
                        row.children.append(pic.CopyTo())
                        pic.left += pic.width

                else:
                    row.children.append(pic.CopyTo())
                if self.attrStack[-1]['background-repeat'] in ('repeat', 'repeat-y'):
                    if self.attrStack[-1]['background-attachment'] == 'scroll':
                        self.bgscrolltype = html.BG_TILED
                    for y in xrange(max(windowHeight / tHeight, 2) + 1):
                        self.sr.background.children.append(row.CopyTo())

                elif self.attrStack[-1]['background-attachment'] == 'scroll':
                    self.bgscrolltype = html.BG_SCROLL
                self.sr.background.children.append(row.CopyTo())
                if self.attrStack[-1]['background-attachment'] == 'fixed':
                    self.bgscrolltype = html.BG_FIXED
                    self.sr.background.top = 0
                self.attrStack[-1]['background-image'] = None
        if self.attrStack[-1]['margin-top'] != 0:
            margin = self.attrStack[-1]['margin-top']
            (lpush, rpush,) = self.GetMargins(self.contentHeight, self.contentHeight + margin)
            self.FlushBuffer([([],
              [],
              [],
              lpush,
              rpush,
              None,
              margin,
              0,
              0)])



    def GoTo(self, URL, data = None, args = {}, scrollTo = None, newThread = 1):
        if self.sr.window and hasattr(self.sr.window, 'GoTo'):
            self.sr.window.GoTo(URL, data, args, scrollTo)
        else:
            return self._GoTo(URL, data, args, newThread=newThread)



    def _GoTo(self, url, data = None, args = {}, scrollTo = None, recursive = 0, newThread = 1, getSource = 0):
        if not url:
            return 
        if getSource:
            return self.sr.currentTXT
        if self.sr.window and hasattr(self.sr.window, 'ShowLoad'):
            self.sr.window.ShowLoad()
        self.startTime = blue.os.GetWallclockTimeNow()
        self.SetStatus(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/OpeningURL', url=url))
        url = url.encode('ascii')
        try:
            if self.sr.window and getattr(self.sr.window, 'SetCaption', None):
                self.sr.window.SetCaption('')
            node = data
            self.sr.currentData = data
            try:
                if url.startswith('./'):
                    url = url[2:]
                if self.sr.currentURL is not None and self.sr.currentURL.lower().startswith('res:') and ':' not in url[:6]:
                    lastslash = self.sr.currentURL.rfind('/')
                    url = self.sr.currentURL[:(lastslash + 1)] + url
                url = self.LocalizeURL(url)
                if url.lower().startswith('res:'):
                    response = ResFile(url)
                    self.sr.currentURL = url
                else:
                    (url, anchor,) = self.CheckURL(url, getAnchor=1)
                    (scheme, netloc, path, query, fragment,) = urlparse.urlsplit(url)
                    self.sr.currentURL = urlparse.urlunsplit((scheme,
                     netloc,
                     path or '/',
                     query,
                     '')).rstrip()
                    cookie = self.sr.cookieMgr.GetCookie(url)
                    response = corebrowserutil.GetStringFromURL(url, data, cookie)
                    if self.destroyed:
                        return 
                    (scheme, netloc, path, query, fragment,) = urlparse.urlsplit(url)
                    if path and path[-1] != '/' and '.' not in path[-5:] and url.find('local://') == -1:
                        path += '/'
                    if getattr(response, 'url', None):
                        self.sr.currentURL = response.url
                    else:
                        self.sr.currentURL = urlparse.urlunsplit((scheme,
                         netloc,
                         path or '/',
                         query,
                         '')).rstrip()
                    self.sr.anchor = fragment
                    self.sr.sessionreload = False
                    self.sr.reloadtimer = None
                    for each in response.info().headers:
                        tmp = each.strip()
                        if tmp.lower().startswith('refresh:'):
                            args = tmp[8:].strip().split(';')
                            interval = None
                            if len(args) == 2:
                                (interval, url,) = args
                                self.sr.reloadURL = url.replace('URL=', '').strip()
                            elif len(args) == 1:
                                interval = args[0]
                                self.sr.reloadURL = self.sr.currentURL
                            if interval is not None:
                                if str(interval).strip().lower() == 'sessionchange':
                                    self.sr.sessionreload = True
                                else:
                                    if int(interval) == 0:
                                        self._GoTo(self.sr.reloadURL)
                                        return 
                                    self.sr.reloadtimer = base.AutoTimer(1000 * int(interval), self.TimedReload)

                    self.sr.cookieMgr.ProcessCookies(response)
                    self.charset = 'cp1252'
                    if 'content-type' in response.headers.keys():
                        if response.headers['content-type'].startswith('image/'):
                            self.LoadHTML('<HTML><BODY><IMG SRC="' + url + '"></BODY></HTML>')
                            return 
                        for each in response.headers['content-type'].split(';'):
                            tmp = each.strip().lower()
                            if tmp.startswith('charset='):
                                charset = tmp[8:].strip()
                                try:
                                    import codecs
                                    codecs.lookup(str(charset))
                                    self.charset = charset
                                except:
                                    sys.exc_clear()

                pieces = []
                while True:
                    next4kb = response.read(4096)
                    if next4kb:
                        pieces.append(next4kb)
                        blue.pyos.BeNice(10)
                    else:
                        break

                txt = ''.join(pieces)
                if txt[:2] == '\xff\xfe':
                    txt = txt.decode('utf-16')
                self.LoadHTML(txt, scrollTo=scrollTo, newThread=newThread)
            except OSError as what:
                if what.errno == errno.ENOENT:
                    self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorFileNotFound', filename=what.filename))
                else:
                    self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorOSError', filename=what.filename, errorNumber=what.errno, errorString=what.strerror))
                sys.exc_clear()
            except gps.ClientConnectFailed as what:
                s = gps.ClientConnectFailedString(what)
                if s.lower() in ('host not found', 'valid name, no data record of requested type'):
                    self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorHostNotFound'))
                elif s.lower() in ('connection timed out', 'valid name, no data record of requested type'):
                    self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorConnectionTimeOut', title=what.args[0], hostAddress=url))
                else:
                    self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorGeneric', title=what.args[0]))
                sys.exc_clear()
            except urllib2.URLError as what:
                self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorURLError', error=what))
                sys.exc_clear()
            except ValueError as what:
                self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorURLError', error=what))
                log.LogException()
            except AttributeError:
                if self is None or self.destroyed:
                    sys.exc_clear()
                else:
                    self.HandleException()
            except Exception as e:
                self.HandleException()

        finally:
            if self.destroyed:
                return 
            self.SetStatus('Done')




    def HandleException(self):
        log.LogException()
        self.LoadHTML(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/HTMLErrorException'))



    def TimedReload(self):
        self.sr.reloadtimer = None
        self._GoTo(self.sr.reloadURL)



    def SessionChanged(self):
        if self.sr.sessionreload:
            self._GoTo(self.sr.reloadURL)



    def CloseTags(self, tag):
        s = ''
        closetags = {'u': '</u>',
         'b': '</b>',
         'i': '</i>',
         'a': '</a>',
         'color': '</font>',
         'size': '</font>',
         'url': '</url>'}
        t = ''
        flags = size = color = link = None
        while t != tag and len(self.tagstack):
            (t, flags, size, color, link,) = self.tagstack.pop()
            s += closetags[t]

        return (s,
         flags,
         size,
         color,
         link)



    def SetValue(self, text, scrolltotop = 0, cursorPos = None, preformatted = 0, html = 1, fontColor = None):
        self.fontSize = self.defaultFontSize
        self.fontColor = fontColor or self.defaultFontColor
        self.fontFlag = 0
        self.href = None
        self._AttribStateChange()
        if scrolltotop:
            scrollTo = 0.0
        else:
            scrollTo = self.GetScrollProportion()
            if self.autoScrollToBottom and scrollTo == 0.0:
                scrollTo = 1.0
        text = text or ''
        if not html:
            text = text.replace('<url=', '<a href=').replace('</url>', '</a>').replace('<fontsize', '<font size').replace('<color=0x', '<font color=#')
        if preformatted:
            self.SetPlainLoad()
            text = text.replace('\t', '    ')
        if not uiutil.StripTags(text):
            text = ''
        self.LoadHTML('<html><body>%s</body></html>' % text, breakOnly=0, scrollTo=scrollTo)
        if cursorPos is not None and not self.readonly:
            self.SetCursorPos(cursorPos)


    SetText = SetValue

    def GetValue(self, html = 1):
        if html:
            ret = self.SaveHTML()
        else:
            ret = self.SaveTextMarkup()
        return ret



    def SaveHTML(self):
        self.Simplify()
        str = ''
        oldFontSize = self.defaultFontSize
        defaultColor = oldColor = (1.0, 1.0, 1.0, 0.75)
        oldFlags = 0
        oldLink = None
        self.tagstack = []
        for (stack, attrs,) in self.textbuffers:
            for obj in stack:
                if obj.type == '<text>':
                    if obj.a != oldLink and oldLink is not None:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('a')
                        str += t
                    if oldFlags & fontflags.u and not obj.fontFlags & fontflags.u:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('u')
                        str += t
                    if obj.color != oldColor and oldColor != defaultColor:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('color')
                        str += t
                    if obj.fontSize != oldFontSize and oldFontSize != self.defaultFontSize:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('size')
                        str += t
                    if oldFlags & fontflags.b and not obj.fontFlags & fontflags.b:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('b')
                        str += t
                    if oldFlags & fontflags.i and not obj.fontFlags & fontflags.i:
                        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('i')
                        str += t
                    if not oldFlags & fontflags.i and obj.fontFlags & fontflags.i:
                        str += '<i>'
                        self.tagstack += [('i',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    if not oldFlags & fontflags.b and obj.fontFlags & fontflags.b and not obj.a:
                        str += '<b>'
                        self.tagstack += [('b',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    if obj.fontSize != oldFontSize and self.defaultFontSize != obj.fontSize:
                        str += '<font size="%d">' % obj.fontSize
                        self.tagstack += [('size',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    if obj.color != oldColor and obj.color != defaultColor and not obj.a:
                        str += '<font color="#%02x%02x%02x%02x">' % (obj.color[3] * 255,
                         obj.color[0] * 255,
                         obj.color[1] * 255,
                         obj.color[2] * 255)
                        self.tagstack += [('color',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    if not oldFlags & fontflags.u and obj.fontFlags & fontflags.u and not obj.a:
                        str += '<u>'
                        self.tagstack += [('u',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    if obj.a != oldLink and obj.a is not None:
                        str += '<a href="%s">' % obj.a.href
                        self.tagstack += [('a',
                          oldFlags,
                          oldFontSize,
                          oldColor,
                          oldLink)]
                    oldFontSize = obj.fontSize
                    oldFlags = obj.fontFlags
                    oldColor = obj.color
                    oldLink = obj.a
                    str += obj.letters.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            str += '<br>'

        str = str[:-4]
        (t, oldFlags, oldFontSize, oldColor, oldLink,) = self.CloseTags('all')
        str += t
        if not uiutil.StripTags(str):
            return ''
        return str



    def SaveTextMarkup(self):
        self.Simplify()
        retString = ''
        for (stack, attrs,) in self.textbuffers:
            for obj in stack:
                if obj.type == '<text>':
                    if not obj.letters:
                        continue
                    if self.defaultFontSize != obj.fontSize:
                        retString += '<fontsize=%s>' % obj.fontSize
                    if self.defaultFontColor != obj.color:
                        retString += '<color=0x%02x%02x%02x%02x>' % (obj.color[3] * 255,
                         obj.color[0] * 255,
                         obj.color[1] * 255,
                         obj.color[2] * 255)
                    if obj.a is not None:
                        retString += '<url=%s>' % obj.a.href
                    if obj.fontFlags & fontflags.u:
                        retString += '<u>'
                    if obj.fontFlags & fontflags.b:
                        retString += '<b>'
                    if obj.fontFlags & fontflags.i:
                        retString += '<i>'
                    retString += obj.letters.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    if obj.fontFlags & fontflags.i:
                        retString += '</i>'
                    if obj.fontFlags & fontflags.b:
                        retString += '</b>'
                    if obj.fontFlags & fontflags.u:
                        retString += '</u>'
                    if obj.a is not None:
                        retString += '</url>'
                    if self.defaultFontColor != obj.color:
                        retString += '</color>'
                    if self.defaultFontSize != obj.fontSize:
                        retString += '</fontsize>'

            retString += '<br>'

        retString = retString[:-4]
        if not uiutil.StripTags(retString):
            return ''
        return retString



    def SetDefaultFontSize(self, size):
        for (stack, attrs,) in self.textbuffers:
            for obj in stack:
                if obj.type == '<text>' and obj.fontSize == self.defaultFontSize:
                    obj.fontSize = size


        self.defaultFontSize = self.fontSize = size
        self.DoContentResize()



    def PrintBuffer(self):
        print '++++++++++++++++++++'
        for (stack, attrs,) in self.textbuffers:
            print 'Stack',
            print id(stack)
            for obj in stack:
                if obj.type == '<text>':
                    print '    Object',
                    print id(obj),
                    print obj.fontSize,
                    print repr(obj.letters)
                else:
                    print '    Object.type',
                    print rept(obj.type)





    def ReadOnly(self, *args):
        self.readonly = 1
        if self.sr.attribPanel is not None:
            self.sr.attribPanel.state = uiconst.UI_HIDDEN
        self.HideCursor()



    def Editable(self, showpanel = 1, plainload = 0, *args):
        self.readonly = 0
        if self.sr.attribPanel is not None:
            if showpanel:
                self.sr.attribPanel.state = uiconst.UI_NORMAL
            else:
                self.sr.attribPanel.state = uiconst.UI_HIDDEN
        if plainload:
            self.SetPlainLoad()
        self.ShowCursor()



    def SetPlainLoad(self):
        self.plainload = 1
        self.GetTextObject = self.GetTextObject_Overwrite



    def AllowResizeUpdates(self, resize):
        self.noresize = not resize



    def SetMaxLength(self, value):
        self.maxletters = value



    def ShowObject(self, obj):
        if self.scrollingRange:
            absPos = obj.GetAbsolute()
            if absPos is not None:
                (left, top, width, height,) = absPos
                (cleft, ctop, cwidth, cheight,) = self.sr.clipper.GetAbsolute()
                top = top - ctop + self._position
                portion = max(top + height - cheight + 5, min(top - 5, self._position)) / float(self.scrollingRange)
                self.ScrollToProportion(portion)



    def GetTextObject_Overwrite(self, text, width = None):
        obj = parser.ParserBase.GetTextObject(self, text, width)
        fontFlag = obj.fontFlags
        fontSize = obj.fontSize
        fontColor = obj.color
        if fontFlag != self.fontFlag or fontSize != self.fontSize or fontColor != self.fontColor:
            if not obj.a:
                obj.color = self.fontColor
            obj.fontFlags = self.fontFlag
            obj.fontSize = self.fontSize
        return obj



    def OnSetFocus(self, *args, **kw):
        uicls.Scroll.OnSetFocus(self, *args, **kw)
        if not self.readonly:
            sm.GetService('ime').SetFocus(self)
        self.UpdateNodesCursorIndexes()
        self.RefreshCursorAndSelection()
        if getattr(self, 'RegisterFocus', None):
            self.RegisterFocus(self)



    def OnKillFocus(self, *args, **kw):
        uicls.Scroll.OnKillFocus(self, *args, **kw)
        if not self.readonly:
            sm.GetService('ime').KillFocus(self)
        uthread.new(self.RefreshCursorAndSelection)
        if getattr(self, 'OnFocusLost', None):
            uthread.new(self.OnFocusLost, self)



    def HideCursor(self):
        self._showCursor = False
        self.RefreshCursorAndSelection()



    def ShowCursor(self):
        self._showCursor = False
        self.RefreshCursorAndSelection()



    def EvalAttributeState(self):
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        if obj is not None:
            if obj.fontFlags != self.fontFlag or obj.fontSize != self.fontSize or obj.color != self.fontColor or obj.a and obj.a.href != self.href:
                self.fontFlag = obj.fontFlags
                self.fontSize = obj.fontSize
                self.fontColor = obj.color
                self.href = obj.a and obj.a.href
                self._AttribStateChange()



    def GetMenuDelegate(self, node = None):
        m = []
        if self.sr.window and getattr(self.sr.window, 'GetMenu', None):
            m = self.sr.window.GetMenu()
        m.append((localization.GetByLabel('/Carbon/UI/Controls/Common/CopyAll'), self.CopyAll))
        if self.HasSelection():
            m.append((localization.GetByLabel('/Carbon/UI/Controls/Common/CopySelected'), self.Copy))
            if not self.readonly:
                m.append((localization.GetByLabel('/Carbon/UI/Controls/Common/CutSelected'), self.Cut))
        clipboard = uiutil.GetClipboardData()
        if clipboard and not self.readonly:
            m.append((localization.GetByLabel('/Carbon/UI/Controls/Common/Paste'), self.Paste, (clipboard,)))
        if not self.readonly:
            m.append(None)
            linkmenu = [(localization.GetByLabel('/EVE/UI/Common/Character'), self.LinkCharacter),
             (localization.GetByLabel('/EVE/UI/Common/Corporation'), self.LinkCorp),
             (localization.GetByLabel('/EVE/UI/Common/LocationTypes/SolarSystem'), self.LinkSolarSystem),
             (localization.GetByLabel('/EVE/UI/Common/LocationTypes/Station'), self.LinkStation),
             (localization.GetByLabel('/Carbon/UI/Controls/Common/ItemType'), self.LinkItemType)]
            m.append((localization.GetByLabel('/Carbon/UI/Controls/Common/AutoLink'), linkmenu))
            sm.GetService('ime').GetMenuDelegate(self, node, m)
        return m



    def SelectLineUnderCursor(self):
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        if node.startCursorIndex is None:
            self.UpdateNodesCursorIndexes()
        (fromIdx, toIdx,) = (node.startCursorIndex, node.endCursorIndex)
        self.SetSelectionRange(fromIdx, toIdx)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)



    def FindWordBoundariesFromGlobalCursor(self):
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        if node.startCursorIndex is None:
            self.UpdateNodesCursorIndexes()
        pos = self.globalCursorPos - node.startCursorIndex
        glyphString = uicore.font.GetLineGlyphString(node)
        text = ''.join([ each[4] for each in glyphString if each[4] ])
        boundaries = uiutil.FindTextBoundaries(text, regexObject=uiconst.WORD_BOUNDARY_REGEX)
        wordLength = 0
        totalWordLength = 0
        for wordLength in [ len(word) for word in boundaries ]:
            totalWordLength += wordLength
            if pos < totalWordLength:
                break

        leftOffset = totalWordLength - wordLength - pos
        rightOffset = totalWordLength - pos
        return (leftOffset, rightOffset)



    def SelectWordUnderCursor(self):
        (leftBound, rightBound,) = self.FindWordBoundariesFromGlobalCursor()
        (fromIdx, toIdx,) = (self.globalCursorPos + leftBound, self.globalCursorPos + rightBound)
        self.SetSelectionRange(fromIdx, toIdx)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)



    def SetSelectionInitPos(self, globalIndex):
        self.globalSelectionInitpos = globalIndex



    def CheckCursorAndSelectionUpdate(self):
        (fromCharIndex, toCharIndex,) = self.globalSelectionRange
        cursorPos = self.globalCursorPos
        (last_cursorPos, last_fromCharIndex, last_toCharIndex,) = getattr(self, 'lastCursorUpdateProps', (None, None, None))
        if cursorPos != last_cursorPos or fromCharIndex != last_fromCharIndex or toCharIndex != last_toCharIndex:
            self.RefreshCursorAndSelection()



    def SetSelectionRange(self, fromCharIndex, toCharIndex):
        if fromCharIndex == toCharIndex:
            (fromCharIndex, toCharIndex,) = (None, None)
        elif toCharIndex < fromCharIndex:
            copy_fromCharIndex = fromCharIndex
            fromCharIndex = toCharIndex
            toCharIndex = copy_fromCharIndex
        self.globalSelectionRange = (fromCharIndex, toCharIndex)
        self.CheckCursorAndSelectionUpdate()



    def SetCursorPos(self, globalIndex, forceUpdate = False):
        if globalIndex == -1:
            globalIndex = self._maxGlobalCursorIndex
        self.globalCursorPos = max(0, min(self._maxGlobalCursorIndex, globalIndex))
        if forceUpdate:
            self.RefreshCursorAndSelection()
        else:
            self.CheckCursorAndSelectionUpdate()



    def RefreshCursorAndSelection(self):
        if self.dead:
            return 
        self.UpdateNodesCursorIndexes()
        (fromIdx, toIdx,) = self.globalSelectionRange
        for node in self.GetNodes():
            if not issubclass(node.decoClass, uicls.SE_TextlineCore):
                continue
            if node.startCursorIndex is None:
                self.UpdateNodesCursorIndexes()
            if node.startCursorIndex <= self.globalCursorPos <= node.endCursorIndex:
                indexInLine = self.globalCursorPos - node.startCursorIndex
                startCheck = node.startCursorIndex - node.pos
                for obj in node.stack:
                    lenLetters = len(obj.letters or '')
                    if startCheck <= self.globalCursorPos <= startCheck + lenLetters:
                        self._activeNodeObjPos = (node, obj, node.startCursorIndex - startCheck + indexInLine)
                        break
                    startCheck += lenLetters

            if not self.readonly:
                if node.cursorPos is not None:
                    node.cursorPos = None
                    if node.panel:
                        node.panel.UpdateCursor()
            if fromIdx is None or not (fromIdx <= node.startCursorIndex <= toIdx or node.startCursorIndex <= fromIdx <= node.endCursorIndex):
                node.selectionStartIndex = None
                node.selectionEndIndex = None
            else:
                node.selectionStartIndex = max(0, fromIdx - node.startCursorIndex)
                node.selectionEndIndex = max(0, min(node.letterCountInLine, toIdx - node.startCursorIndex))
            if node.panel and hasattr(node.panel, 'UpdateSelectionHilite'):
                node.panel.UpdateSelectionHilite()

        if not self.readonly:
            (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
            if node:
                node.cursorPos = self.globalCursorPos - node.startCursorIndex
                if node.panel:
                    node.panel.UpdateCursor()
        self.lastCursorUpdateProps = (self.globalCursorPos, fromIdx, toIdx)



    def GetNodeAndTextObjectFromGlobalCursor(self):
        return getattr(self, '_activeNodeObjPos', (None, None, 0))



    def GetSelectedText(self, getAll = False):
        if getAll:
            ret = ''
            for (stackIndex, (stack, attrs,),) in enumerate(self.textbuffers):
                for obj in stack:
                    if obj.type == '<text>':
                        ret += obj.letters
                    elif obj.type == '<table>' and obj.control:
                        tableValue = obj.control.GetValue()
                        if tableValue:
                            ret += tableValue + '\r\n'

                ret += '\r\n'

            return ret
        (fromIdx, toIdx,) = self.globalSelectionRange
        if fromIdx == toIdx:
            return ''
        newret = ''
        for node in self.GetNodes():
            if not issubclass(node.decoClass, uicls.SE_TextlineCore):
                continue
            if node.selectionStartIndex is None:
                continue
            if node.inlines:
                for (inline, x,) in node.inlines:
                    if inline.type == '<table>' and inline.control:
                        tableText = inline.control.GetValue()
                        if tableText:
                            newret += tableText + '\r\n'

            if node.glyphString is None:
                continue
            if newret and node.pos == 0:
                newret += '\r\n'
            text = ''.join([ glyphData[4] for glyphData in node.glyphString if glyphData[4] is not None ])
            if node.startCursorIndex <= fromIdx <= node.startCursorIndex + len(text):
                newret += text[(fromIdx - node.startCursorIndex):(toIdx - node.startCursorIndex)]
            elif node.startCursorIndex <= toIdx <= node.startCursorIndex + len(text):
                newret += text[:(toIdx - node.startCursorIndex)]
            else:
                newret += text

        return newret



    def LinkCharacter(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'char'})



    def LinkCorp(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'corp'})



    def LinkSolarSystem(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'solarsystem'})



    def LinkStation(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'station'})



    def LinkItemType(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'type'})



    def OnMouseUpDelegate(self, _node, *args):
        self._selecting = 0
        self.sr.scrollTimer = None



    def OnMouseDownDelegate(self, _node, *args):
        self.UpdateNodesCursorIndexes()
        self._selecting = 1
        self.sr.scrollTimer = base.AutoTimer(100, self.ScrollTimer)
        if _node and _node.panel and _node.panel.children:
            self.SetCursorFromNodeAndMousePos(_node)
            if uicore.uilib.Key(uiconst.VK_SHIFT) and self.globalSelectionInitpos is not None:
                (fromIdx, toIdx,) = self.globalSelectionRange
                newIndex = self.globalCursorPos
                toIndex = self.globalSelectionInitpos
                if newIndex > toIndex:
                    self.SetSelectionRange(toIndex, newIndex)
                else:
                    self.SetSelectionRange(newIndex, toIndex)
            else:
                self.SetSelectionRange(None, None)
                self.SetSelectionInitPos(self.globalCursorPos)
            self.EvalAttributeState()



    def OnMouseMoveDelegate(self, *args):
        if not self._selecting or self.globalSelectionInitpos is None:
            return 
        if not uicore.uilib.leftbtn:
            self._selecting = 0
            return 
        toAffect = self.CrawlForTextline(uicore.uilib.mouseOver)
        if toAffect is None:
            toAffect = self.GetLastTextline()
            if toAffect is None:
                return 
        node = toAffect.sr.node
        if node is None:
            return 
        self.SetCursorFromNodeAndMousePos(node)
        if self.globalCursorPos > self.globalSelectionInitpos:
            self.SetSelectionRange(self.globalSelectionInitpos, self.globalCursorPos)
        else:
            self.SetSelectionRange(self.globalCursorPos, self.globalSelectionInitpos)
        self.EvalAttributeState()



    def SetCursorFromNodeAndMousePos(self, node):
        if node.startCursorIndex is None:
            self.UpdateNodesCursorIndexes()
        if node.panel is not None:
            toCursorPos = uicore.uilib.x - node.panel.sr.inlines.GetAbsolute()[0]
            internalPos = uicore.font.GetLetterIdx(node, toCursorPos)[0]
            startCursorIndex = node.startCursorIndex or 0
            self.SetCursorPos(startCursorIndex + internalPos)
        else:
            self.SetCursorPos(-1)



    def SetCursorPosAtObjectEnd(self, toEnd):
        for node in self.GetNodes():
            if not issubclass(node.decoClass, uicls.SE_TextlineCore):
                continue
            if node.startCursorIndex is None:
                self.UpdateNodesCursorIndexes()
            counter = 0
            for obj in node.stack:
                if obj.letters:
                    counter += len(obj.letters)
                if obj is toEnd:
                    self.SetCursorPos(node.startCursorIndex + counter)
                    return 





    def GetLastTextline(self):
        totalLines = len(self.sr.content.children)
        for i in xrange(totalLines):
            nodePanel = self.sr.content.children[(totalLines - i - 1)]
            if isinstance(nodePanel, uicls.SE_TextlineCore):
                return nodePanel




    def CrawlForTextline(self, mo):
        if isinstance(mo, uicls.SE_TextlineCore):
            return mo
        if mo.parent:
            if mo.parent is uicore.desktop:
                return None
            return self.CrawlForTextline(mo.parent)



    def ScrollTimer(self):
        if uicore.uilib.leftbtn and self._selecting:
            (aL, aT, aW, aH,) = self.GetAbsolute()
            if uicore.uilib.y < aT:
                uthread.new(self.Scroll, 1)
            elif uicore.uilib.y > aT + aH:
                uthread.new(self.Scroll, -1)
        else:
            self.sr.scrollTimer = None



    def OnDragEnterDelegate(self, node, nodes):
        if self.readonly:
            return 
        self.SetCursorFromNodeAndMousePos(node)



    def OnDragMoveDelegate(self, node, nodes):
        if self.readonly:
            return 
        self.SetCursorFromNodeAndMousePos(node)



    def OnDropDataDelegate(self, node, nodes):
        if self.readonly:
            return 
        self.SetCursorFromNodeAndMousePos(node)



    def OnContentDropData(self, dragObj, nodes):
        self.SetCursorPos(self._maxGlobalCursorIndex)
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        self.OnDropDataDelegate(node, nodes)



    def OnDropData(self, dragObj, nodes):
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        self.OnDropDataDelegate(node, nodes)



    def OnMouseUp(self, *args):
        self._selecting = 0
        self.sr.scrollTimer = None



    def OnMouseDown(self, button, *args):
        if button != uiconst.MOUSELEFT:
            return 
        if len(self.sr.content.children):
            self.UpdateNodesCursorIndexes()
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            lastEntry = self.sr.content.children[-1]
            (l, t, w, h,) = lastEntry.GetAbsolute()
            if uicore.uilib.y > t + h:
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    self.SetSelectionRange(selectionStartIndex or self.globalCursorPos, self._maxGlobalCursorIndex)
                else:
                    self.SetSelectionRange(None, None)
                    self.SetSelectionInitPos(self._maxGlobalCursorIndex)
                self.SetCursorPos(self._maxGlobalCursorIndex)
        self._selecting = 1



    def OnMouseMove(self, *args):
        self.OnMouseMoveDelegate()



    def OnKeyDown(self, vkey, flag, *args, **kw):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if vkey in (uiconst.VK_LEFT,
         uiconst.VK_RIGHT,
         uiconst.VK_UP,
         uiconst.VK_DOWN,
         uiconst.VK_HOME,
         uiconst.VK_END):
            if self.globalCursorPos is None:
                return 
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if not shift:
                self.SetSelectionRange(None, None)
            (leftBound, rightBound,) = self.FindWordBoundariesFromGlobalCursor()
            newCursorPos = self.globalCursorPos
            (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
            if node.startCursorIndex is None:
                self.UpdateNodesCursorIndexes()
            if vkey == uiconst.VK_LEFT:
                if ctrl:
                    newCursorPos = self.globalCursorPos + leftBound
                else:
                    newCursorPos = max(0, self.globalCursorPos - 1)
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos)
            elif vkey == uiconst.VK_RIGHT:
                if ctrl:
                    newCursorPos = self.globalCursorPos + rightBound
                else:
                    newCursorPos = self.globalCursorPos + 1
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos)
            elif vkey == uiconst.VK_UP:
                if not ctrl:
                    self.OnUp()
                    if self.globalSelectionRange == (None, None):
                        self.Scroll(1 + 10 * shift)
                    else:
                        posInLine = self.globalCursorPos - node.startCursorIndex
                        if node.idx > 0:
                            aboveIdx = node.idx - 1
                            nodeAbove = None
                            while aboveIdx:
                                nodeAbove = self.GetNode(aboveIdx)
                                if nodeAbove and nodeAbove.startCursorIndex != nodeAbove.endCursorIndex:
                                    break
                                aboveIdx -= 1

                            if nodeAbove and nodeAbove.endCursorIndex is not None:
                                newCursorPos = min(nodeAbove.endCursorIndex, nodeAbove.startCursorIndex + posInLine)
                            else:
                                newCursorPos = 0
                            if shift:
                                (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                                if selectionStartIndex is None:
                                    self.SetSelectionRange(newCursorPos, self.globalCursorPos)
                                elif self.globalCursorPos == selectionStartIndex:
                                    self.SetSelectionRange(newCursorPos, selectionEndIndex)
                                else:
                                    self.SetSelectionRange(selectionStartIndex, newCursorPos)
            elif vkey == uiconst.VK_DOWN:
                if not ctrl:
                    self.OnDown()
                    if self.globalSelectionRange == (None, None):
                        self.Scroll(-1 - 10 * shift)
                    else:
                        posInLine = self.globalCursorPos - node.startCursorIndex
                        nodeBelow = self.GetNode(node.idx + 1)
                        if nodeBelow and nodeBelow.startCursorIndex is not None:
                            newCursorPos = nodeBelow.startCursorIndex + min(posInLine, nodeBelow.letterCountInLine)
                        else:
                            newCursorPos = self._maxGlobalCursorIndex
                    if shift:
                        (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                        if selectionStartIndex is None:
                            self.SetSelectionRange(self.globalCursorPos, newCursorPos)
                        elif self.globalCursorPos == selectionStartIndex:
                            self.SetSelectionRange(newCursorPos, selectionEndIndex)
                        else:
                            self.SetSelectionRange(selectionStartIndex, newCursorPos)
            elif vkey == uiconst.VK_HOME:
                self.OnHome()
                if ctrl:
                    newCursorPos = 0
                else:
                    newCursorPos = node.startCursorIndex
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex)
                    else:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex)
            elif vkey == uiconst.VK_END:
                self.OnEnd()
                if ctrl:
                    newCursorPos = self._maxGlobalCursorIndex
                else:
                    newCursorPos = node.endCursorIndex
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos)
            self.SetCursorPos(newCursorPos)
            self.EvalAttributeState()
            if self.globalSelectionRange != (None, None):
                (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
                if node:
                    self.ShowNodeIdx(node.idx)
        if self.readonly:
            return 
        if ctrl:
            if vkey == uiconst.VK_B:
                self.ToggleBold()
            if vkey == uiconst.VK_U:
                self.ToggleUnderline()
            if vkey == uiconst.VK_I:
                self.ToggleItalic()
            if vkey == uiconst.VK_ADD:
                self.EnlargeSize()
            if vkey == uiconst.VK_SUBTRACT:
                self.ReduceSize()
            if vkey == uiconst.VK_UP:
                self.CtrlUp(self)
            if vkey == uiconst.VK_DOWN:
                self.CtrlDown(self)
            return 
        if vkey == uiconst.VK_DELETE:
            self.OnChar(127, flag)



    def OnChar(self, char, flag):
        if self.readonly:
            return False
        if char < 32 and char not in (uiconst.VK_RETURN, uiconst.VK_BACK):
            return False
        if self.globalCursorPos is None:
            return False
        self.keybuffer.append(char)
        if not self.updating:
            if char == uiconst.VK_RETURN and not uicore.uilib.Key(uiconst.VK_SHIFT) and self.OnReturn:
                self.Simplify()
                return uthread.new(self.OnReturn)
            try:
                self.updating = 1
                while len(self.keybuffer):
                    char = self.keybuffer.pop(0)
                    if self.DeleteSelected() and char in [127, uiconst.VK_BACK]:
                        continue
                    self.Insert(char)


            finally:
                self.updating = 0

        return True



    def SelectAll(self, *args):
        self.SetSelectionRange(0, self._maxGlobalCursorIndex)



    def Copy(self):
        selstring = self.GetSelectedText()
        if selstring:
            blue.pyos.SetClipboardData(selstring)



    def CopyAll(self):
        all = self.GetSelectedText(getAll=True)
        if all:
            blue.pyos.SetClipboardData(all)



    def Cut(self):
        self.Copy()
        if not self.readonly:
            self.DeleteSelected()



    def EnoughRoomFor(self, textLen):
        if not self.maxletters:
            return True
        currentLen = len(uiutil.StripTags(self.GetSelectedText(getAll=True)))
        if currentLen + textLen <= self.maxletters:
            return True
        return textLen <= self.RoomLeft()



    def RoomLeft(self):
        if not self.maxletters:
            return None
        currentLen = len(self.GetValue(0))
        return self.maxletters + len(self.GetSelectedText()) - currentLen



    def Paste(self, text):
        roomLeft = self.RoomLeft()
        if roomLeft is not None and roomLeft < len(text):
            uicore.Message('uiwarning03')
            text = text[:roomLeft]
        if self.readonly or not text:
            return 
        self.DeleteSelected(reloadAll=False)
        currentCursor = self.globalCursorPos
        text = text.replace('\t', '    ').replace('\r', '')
        lines = text.split('\n')
        line = lines.pop(0)
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        endObj = obj.Copy()
        endObj.letters = obj.letters[npos:]
        lastStack = node.stack
        obj.letters = obj.letters[:npos] + line
        if lines:
            stackIndex = 0
            attrStack = None
            for (s, a,) in self.textbuffers:
                if s is node.stack:
                    attrStack = a
                    break
                stackIndex += 1
            else:
                attrStack = self.attrStack[-1]

            for (lineIdx, line,) in enumerate(lines):
                betweenObj = obj.Copy()
                betweenObj.letters = line
                newStack = [betweenObj]
                self.textbuffers.insert(stackIndex + lineIdx + 1, (newStack, attrStack))
                lastStack = newStack

        if endObj.letters:
            lastStack.append(endObj)
        self.UpdateNodesCursorIndexes()
        self.DoContentResize()
        self.SetCursorPos(currentCursor + len(text))
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        if node:
            self.ShowNodeIdx(node.idx)



    def Insert(self, char):
        if char not in (uiconst.VK_BACK, uiconst.VK_RETURN, 127) and not self.EnoughRoomFor(1):
            uicore.Message('uiwarning03')
            return 
        self.Simplify()
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        stackIdx = 0
        prevStack = None
        for (s, a,) in self.textbuffers:
            if s is node.stack:
                attrs = a
                break
            prevStack = s
            stackIdx += 1
        else:
            attrs = self.attrStack[-1]

        cursorAdvance = 0
        if char == uiconst.VK_RETURN:
            if obj.a and npos == len(obj.letters):
                newobj = obj.Copy()
                newobj.letters = ''
                newobj.a = None
                node.stack.insert(node.stack.index(obj) + 1, newobj)
                self.href = None
                self.fontFlag &= ~(fontflags.b | fontflags.u)
                self.fontColor = (1.0, 1.0, 1.0, 0.75)
                newobj.fontFlags = self.fontFlag
                newobj.color = self.fontColor
                obj = newobj
                npos = 0
            cursorAdvance = 1
            newobj = obj.Copy()
            newobj.letters = obj.letters[npos:]
            obj.letters = obj.letters[:npos]
            newstack = [newobj]
            startMove = False
            for textobject in node.stack[:]:
                if startMove:
                    newstack.append(textobject)
                    node.stack.remove(textobject)
                    continue
                if textobject is obj:
                    startMove = True

            sIdx = 0
            for (sIdx, (thisStack, thisAttrs,),) in enumerate(self.textbuffers):
                if thisStack is node.stack:
                    break

            self.textbuffers.insert(sIdx + 1, (newstack, attrs))
            self.RefreshLine(node, attrs, fullRefresh=True)
            self.InsertLines(newstack, 0, node.idx + 1, attrs)
        elif char == 127:
            if npos == len(obj.letters):
                if obj is node.stack[-1]:
                    if stackIdx + 1 < len(self.textbuffers):
                        (nextStack, nextAttrs,) = self.textbuffers[(stackIdx + 1)]
                        del self.textbuffers[stackIdx + 1]
                        node.stack += nextStack
                        self.RemoveStack(nextStack)
                        self.UpdateNodes(nextStack, node.stack)
                        if len(obj.letters) == 0:
                            node.stack.remove(obj)
                    else:
                        return 
                else:
                    obj = node.stack[(node.stack.index(obj) + 1)]
                    obj.letters = obj.letters[1:]
            else:
                obj.letters = obj.letters[:npos] + obj.letters[(npos + 1):]
            self.RefreshLine(node, attrs)
        elif char == uiconst.VK_BACK:
            if npos == 0:
                if self.globalCursorPos != 0 and prevStack:
                    prevStack += node.stack
                    oldStack = node.stack
                    self.RemoveStack(oldStack)
                    self.UpdateNodes(node.stack, prevStack)
                    if len(obj.letters) == 0:
                        node.stack.remove(obj)
                    self.RefreshLine(node, attrs)
                    self.Simplify()
                    cursorAdvance = -1
            else:
                obj.letters = obj.letters[:(npos - 1)] + obj.letters[npos:]
                self.RefreshLine(node, attrs)
                cursorAdvance = -1
        elif char == uiconst.VK_SPACE and obj.a and npos == len(obj.letters):
            newobj = obj.Copy()
            newobj.letters = ' '
            newobj.a = None
            node.stack.insert(node.stack.index(obj) + 1, newobj)
            self.href = None
            self.fontFlag &= ~(fontflags.b | fontflags.u)
            self.fontColor = (1.0, 1.0, 1.0, 0.75)
            newobj.fontFlags = self.fontFlag
            newobj.color = self.fontColor
        else:
            char = unichr(char)
            (newobj, npos,) = self.CheckAttribs(node.stack, obj, npos)
            if newobj is not obj:
                newobj.letters = char
            else:
                obj.letters = obj.letters[:npos] + char + obj.letters[npos:]
        cursorAdvance = 1
        self.RefreshLine(node, attrs)
        if hasattr(self, 'OnChange'):
            self.OnChange()
        self.UpdateNodesCursorIndexes()
        self.SetCursorPos(self.globalCursorPos + cursorAdvance, forceUpdate=True)
        self.EvalAttributeState()
        (node, obj, npos,) = self.GetNodeAndTextObjectFromGlobalCursor()
        if node:
            self.ShowNodeIdx(node.idx)



    def RemoveStack(self, stack):
        idx = 0
        delIdx = None
        for (s, a,) in self.textbuffers:
            if stack is s:
                delIdx = idx
                break
            idx += 1

        if delIdx is not None:
            del self.textbuffers[delIdx]



    def UpdateNodesCursorIndexes(self):
        i = 0
        stackShift = 0
        lastStack = None
        globalCursorIndex = 0
        for node in self.GetNodes():
            if not issubclass(node.decoClass, uicls.SE_TextlineCore):
                continue
            if node.glyphString:
                letterCountInLine = len(node.glyphString)
            else:
                letterCountInLine = 0
            node.letterCountInLine = letterCountInLine
            if lastStack and lastStack is not node.stack:
                stackShift += 1
            node.startCursorIndex = globalCursorIndex + stackShift
            node.endCursorIndex = node.startCursorIndex + letterCountInLine
            globalCursorIndex += letterCountInLine
            lastStack = node.stack
            i += 1

        self._maxGlobalCursorIndex = max(0, globalCursorIndex + stackShift)



    def CheckAttribs(self, stack, obj, npos):
        fontFlag = obj.fontFlags
        fontSize = obj.fontSize
        fontColor = obj.color
        if fontFlag != self.fontFlag or fontSize != self.fontSize or fontColor != self.fontColor:
            (obj, npos,) = self.SplitObj(stack, obj, npos)
            obj.color = self.fontColor
            obj.fontFlags = self.fontFlag
            obj.fontSize = self.fontSize
            if not self.href:
                obj.a = None
        return (obj, npos)



    def SplitObj(self, stack, obj, npos):
        if not len(obj.letters):
            return (obj, 0)
        newobj = obj.Copy()
        newobj.letters = ''
        if npos == 0:
            stack.insert(stack.index(obj), newobj)
        elif npos == len(obj.letters):
            stack.insert(stack.index(obj) + 1, newobj)
        else:
            stack.insert(stack.index(obj), newobj)
            newobj2 = obj.Copy()
            newobj2.letters = obj.letters[:npos]
            stack.insert(stack.index(obj) - 1, newobj2)
            obj.letters = obj.letters[npos:]
        return (newobj, 0)



    def BreakObject(self, obj, npos):
        stack = None
        stackIndex = 0
        for (s, a,) in self.textbuffers:
            for _obj in s:
                if _obj is obj:
                    stack = s
                    attrs = a
                    break

            stackIndex += 1

        newobj = obj.Copy()
        newobj.letters = newobj.letters[npos:]
        obj.letters = obj.letters[:npos]
        newStack = [newobj]
        rm = []
        found = False
        for other in stack:
            if found:
                newStack.append(other)
                rm.append(other)
            if other is obj:
                found = True

        for each in rm:
            stack.remove(each)

        self.textbuffers.insert(stackIndex + 1, (newStack, attrs))
        return newobj



    def GetSelection(self):
        return self.HasSelection()



    def HasSelection(self):
        (fromIdx, toIdx,) = self.globalSelectionRange
        return fromIdx != toIdx



    def DeleteSelected(self, reloadAll = True):
        (fromIdx, toIdx,) = self.globalSelectionRange
        if fromIdx == toIdx:
            return 
        self.Simplify()
        delRange = abs(fromIdx - toIdx)
        counter = 0
        doneDeleting = False
        startObj = None
        endObj = None
        clearStacks = []
        for (stackIndex, (stack, attrs,),) in enumerate(self.textbuffers):
            for obj in stack:
                if obj.type == '<text>':
                    lettersAmount = len(obj.letters)
                    if counter <= fromIdx <= counter + lettersAmount:
                        obj.letters = obj.letters[:(fromIdx - counter)] + obj.letters[(fromIdx - counter + delRange):]
                        startObj = (stack, obj)
                    elif counter <= toIdx <= counter + lettersAmount:
                        obj.letters = obj.letters[(toIdx - counter):]
                        endObj = (stack, obj)
                    elif fromIdx <= counter <= toIdx and fromIdx <= counter + lettersAmount <= toIdx:
                        obj.letters = ''
                        clearStacks.append(stackIndex)
                    counter += lettersAmount
                    if counter > toIdx:
                        doneDeleting = True
                        break

            counter += 1
            if doneDeleting:
                break

        clearStacks.reverse()
        for stackIndex in clearStacks:
            if len(self.textbuffers) > stackIndex:
                del self.textbuffers[stackIndex]

        if startObj and endObj and startObj[0] is not endObj[0]:
            startObj[0].append(endObj[1])
            endObj[0].remove(endObj[1])
        self.Simplify()
        if reloadAll:
            self.DoContentResize()
        self.UpdateNodesCursorIndexes()
        self.SetCursorPos(fromIdx)
        self.SetSelectionRange(None, None)
        return 1



    def ApplySelection(self, what, data = None):
        (fromIdx, toIdx,) = self.globalSelectionRange
        if fromIdx == toIdx:
            return 
        self.Simplify()
        selectionRange = abs(fromIdx - toIdx)
        counter = 0
        startObjData = None
        endObjData = None
        startAndEndObjData = None
        changeObjs = []
        for (stackIndex, (stack, attrs,),) in enumerate(self.textbuffers):
            for obj in stack:
                if obj.type == '<text>':
                    lettersAmount = len(obj.letters)
                    if counter <= fromIdx <= counter + lettersAmount:
                        if counter <= toIdx <= counter + lettersAmount:
                            startAndEndObjData = (stack, obj, fromIdx - counter)
                            break
                        else:
                            startObjData = (stack, obj, fromIdx - counter)
                    elif counter <= toIdx <= counter + lettersAmount:
                        if not endObjData:
                            endObjData = (stack, obj, toIdx - counter)
                    elif fromIdx <= counter and counter + lettersAmount <= toIdx:
                        changeObjs.append(obj)
                    counter += lettersAmount

            counter += 1
            if endObjData or startAndEndObjData:
                break

        if startAndEndObjData:
            (stack, obj, npos,) = startAndEndObjData
            newObj = obj.Copy()
            newObj.letters = obj.letters[npos:(npos + selectionRange)]
            stack.insert(stack.index(obj) + 1, newObj)
            changeObjs.insert(0, newObj)
            newObj2 = obj.Copy()
            newObj2.letters = obj.letters[(npos + selectionRange):]
            stack.insert(stack.index(newObj) + 1, newObj2)
            obj.letters = obj.letters[:npos]
        if startObjData:
            (stack, obj, npos,) = startObjData
            newObj = obj.Copy()
            newObj.letters = obj.letters[npos:]
            obj.letters = obj.letters[:npos]
            stack.insert(stack.index(obj) + 1, newObj)
            changeObjs.insert(0, newObj)
        if endObjData:
            (stack, obj, npos,) = endObjData
            newObj = obj.Copy()
            newObj.letters = obj.letters[npos:]
            obj.letters = obj.letters[:npos]
            stack.insert(stack.index(obj) + 1, newObj)
            changeObjs.append(obj)
        anchor = self.ApplyGameSelection(what, data, changeObjs)
        if anchor is None:
            return 
        if anchor == -1:
            anchor = None
        bBalance = 0
        uBalance = 0
        iBalance = 0
        for obj in changeObjs:
            letterAmt = len(obj.letters)
            bBalance += letterAmt if obj.fontFlags & fontflags.b else -letterAmt
            uBalance += letterAmt if obj.fontFlags & fontflags.u else -letterAmt
            iBalance += letterAmt if obj.fontFlags & fontflags.i else -letterAmt

        for obj in changeObjs:
            prevFlag = obj.fontFlags
            if what == 1:
                obj.fontFlags = (fontflags.b if bBalance <= 0 else 0) | prevFlag & fontflags.i | prevFlag & fontflags.u
            elif what == 2:
                obj.fontFlags = prevFlag & fontflags.b | (fontflags.i if iBalance <= 0 else 0) | prevFlag & fontflags.u
            elif what == 3:
                obj.fontFlags = prevFlag & fontflags.b | prevFlag & fontflags.i | (fontflags.u if uBalance <= 0 else 0)
            elif what == 4:
                obj.color = self.fontColor
            elif what == 5:
                obj.fontSize = self.fontSize
            elif what == 6:
                if anchor is not None:
                    attr = uiutil.Bunch()
                    attr.href = anchor
                    attr.alt = anchor
                    obj.a = attr
                else:
                    obj.color = (1.0, 1.0, 1.0, 0.75)
                    obj.lcolor = None
                    if obj.a:
                        obj.fontFlags ^= fontflags.b | fontflags.u
                    obj.a = None

        self.DoContentResize()
        if what == 6:
            self.SetSelectionRange(None, None)
            self.RemoveAnchor()
        uthread.new(uicore.registry.SetFocus, self)



    def ApplyGameSelection(self, *args):
        pass



    def OnUp(self):
        pass



    def OnDown(self):
        pass



    def OnHome(self):
        pass



    def OnEnd(self):
        pass



    def CtrlUp(self, *args):
        pass



    def CtrlDown(self, *args):
        pass



    def OnClipperResize(self, clipperWidth, clipperHeight, *args, **kw):
        if getattr(self, '_loading', False):
            return 
        if getattr(self, 'noresize', 0):
            return 
        if getattr(self, '_initingEdit', False):
            return 
        if not self.sr.resizeTimer:
            self.sr.resizeTimer = base.AutoTimer(100, self.DoContentResize)


    DoSizeUpdate = OnClipperResize

    def DoContentResize(self):
        if getattr(self, 'resizing', 0) or self.destroyed or not hasattr(self, 'autoScrollToBottom'):
            return 
        if self.readonly and self.sr.htmlstr:
            self.resizing = 1
            scrollTo = self.GetScrollProportion()
            (fromCharIndex, toCharIndex,) = self.globalSelectionRange
            self.LoadHTML(None, scrollTo=scrollTo, newThread=False)
            self.SetSelectionRange(fromCharIndex, toCharIndex)
            self.resizing = 0
            self.sr.resizeTimer = None
        else:
            try:
                self.resizing = 1
                self.contentHeight = 0
                self.contentWidth = 0
                if hasattr(self, 'textbuffers'):
                    self.Simplify()
                    for (overlay, attrs, x, y,) in self.sr.overlays:
                        overlay.state = uiconst.UI_HIDDEN

                    _lines = [uicls.ScrollEntryNode(decoClass=uicls.SE_Space, height=self.ymargin)]
                    for (stack, attrs,) in self.textbuffers:
                        lines = self.BreakLines(stack)
                        entries = self.BuildEntries(lines, stack, attrs)
                        _lines += entries

                    if len(_lines) == 1 and not self.readonly:
                        _lines.append(self.GetFirstLine())
                    pos = self.GetScrollProportion()
                    if self.autoScrollToBottom and pos == 0.0:
                        pos = 1.0
                    self.LoadContent(contentList=_lines, scrollTo=pos)
                    if hasattr(self, 'CheckOverlaysAndUnderlays'):
                        self.CheckOverlaysAndUnderlays()
                self.RefreshCursorAndSelection()

            finally:
                self.resizing = 0

            self.sr.resizeTimer = None



    def RefreshLine(self, node, attrs, fullRefresh = False):
        idx = node.idx
        stack = node.stack
        nodesInStack = []
        for _node in self.GetNodes():
            if _node.stack is stack:
                nodesInStack.append(_node)
            elif nodesInStack:
                break

        if fullRefresh:
            rmNodes = nodesInStack
            inStackCursorPos = 0
        else:
            rmNodes = []
            inStackCursorPos = 0
            for _node in nodesInStack:
                if _node is node:
                    rmNodes.append(_node)
                elif rmNodes:
                    rmNodes.append(_node)
                else:
                    inStackCursorPos += _node.letterCountInLine

        self.RemoveNodes(rmNodes)
        self.InsertLines(stack, inStackCursorPos, idx, attrs)



    def UpdateNodes(self, oldStack, newStack):
        for node in self.GetNodes():
            if node.stack is oldStack:
                node.stack = newStack




    def EnlargeSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(1, 1)



    def ReduceSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(-1, 1)



    def ToggleBold(self):
        self.fontFlag ^= fontflags.b
        self.ApplySelection(1)
        self._AttribStateChange()



    def ToggleUnderline(self):
        self.fontFlag ^= fontflags.u
        self.ApplySelection(3)
        self._AttribStateChange()



    def ToggleItalic(self):
        self.fontFlag ^= fontflags.i
        self.ApplySelection(2)
        self._AttribStateChange()



    def ChangeFontSize(self, newSize):
        self.fontSize = newSize
        self._AttribStateChange()
        self.ApplySelection(5)
        uicore.registry.SetFocus(self)



    def ChangeFontColor(self, newColor):
        self.fontColor = newColor
        self._AttribStateChange()
        self.ApplySelection(4)
        uicore.registry.SetFocus(self)



    def AddAnchor(self):
        if self.GetSelectedText().strip() == '':
            return 
        self.RemoveAnchor()
        self.ApplySelection(6)



    def RemoveAnchor(self):
        if self.href:
            self.href = None
            self.fontFlag &= ~(fontflags.b | fontflags.u)
            self.fontColor = (1.0, 1.0, 1.0, 0.75)
            self._AttribStateChange()



    def _AttribStateChange(self):
        if self.sr.attribPanel is not None:
            self.sr.attribPanel.AttribStateChange(bool(self.fontFlag & fontflags.b), bool(self.fontFlag & fontflags.i), bool(self.fontFlag & fontflags.u), self.fontSize, self.fontColor, self.href)



    def SetLangIndicator(self, lang):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.langIndicator.text = lang




class FontAttribPanelCore(uicls.Container):
    __guid__ = 'uicls.FontAttribPanelCore'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.sr.bold = uicls.Label(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/BoldSymbol'), parent=self, pos=(6, 0, 12, 0), align=uiconst.TOPLEFT, fontsize=14, color=(1.0, 1.0, 1.0, 0.6), mousehilite=1, state=uiconst.UI_NORMAL)
        self.sr.italic = uicls.Label(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ItalicSymbol'), parent=self, pos=(18, 0, 12, 0), align=uiconst.TOPLEFT, fontsize=14, color=(1.0, 1.0, 1.0, 0.6), mousehilite=1, state=uiconst.UI_NORMAL)
        self.sr.underline = uicls.Label(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/UnderlineSymbol'), parent=self, pos=(30, 0, 12, 0), align=uiconst.TOPLEFT, fontsize=14, color=(1.0, 1.0, 1.0, 0.6), mousehilite=1, state=uiconst.UI_NORMAL)
        self.sr.bold.OnClick = self.ToggleBold
        self.sr.italic.OnClick = self.ToggleItalic
        self.sr.underline.OnClick = self.ToggleUnderline
        self.sr.bold.hint = localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Bold')
        self.sr.italic.hint = localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Italic')
        self.sr.underline.hint = localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Underline')
        self.sr.color = uicls.Container(parent=self, align=uiconst.RELATIVE, pos=(45, 2, 12, 12), state=uiconst.UI_NORMAL)
        uicls.Fill(parent=self.sr.color, pos=(1, 1, 1, 1))
        self.sr.colorborder = uicls.Frame(parent=self.sr.color, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.color.OnClick = self.OnColorChange
        self.sr.color.sr.hint = localization.GetByLabel('/Carbon/UI/Controls/EditRichText/TextColor')
        options = [[localizationUtil.FormatNumeric(8), 8],
         [localizationUtil.FormatNumeric(9), 9],
         [localizationUtil.FormatNumeric(10), 10],
         [localizationUtil.FormatNumeric(11), 11],
         [localizationUtil.FormatNumeric(12), 12],
         [localizationUtil.FormatNumeric(14), 14],
         [localizationUtil.FormatNumeric(18), 18],
         [localizationUtil.FormatNumeric(24), 24],
         [localizationUtil.FormatNumeric(30), 30],
         [localizationUtil.FormatNumeric(36), 36]]
        combo = uicls.Combo(parent=self, options=options, name='fontsize', select='12', callback=self.OnFontSizeChange, align=uiconst.TOPLEFT, pos=(67, 0, 0, 0), width=38)
        self.sr.comboFontSize = combo
        self.sr.comboFontSize.SetHint(localization.GetByLabel('/Carbon/UI/Controls/EditRichText/FontSize'))
        self.sr.anchor = uicls.Label(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/LinkSymbol'), parent=self, pos=(110, 3, 18, 16), color=(1.0, 1.0, 1.0, 0.6), align=uiconst.TOPLEFT, mousehilite=1, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/AddLink'), fontsize=9, hspace=1, state=uiconst.UI_NORMAL)
        self.sr.anchor.OnClick = self.AddAnchor
        self.sr.clearnote = uicls.Label(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ClearTextSymbol'), parent=self, pos=(130, 0, 12, 16), color=(1.0, 1.0, 1.0, 0.6), align=uiconst.TOPLEFT, mousehilite=1, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ClearText'), fontsize=14, state=uiconst.UI_NORMAL)
        self.sr.clearnote.OnClick = self.ClearNote
        languageIndicator = sm.GetService('ime').GetLanguageIndicator()
        self.sr.langIndicator = uicls.Label(text=languageIndicator, parent=self, color=(1.0, 1.0, 1.0, 0.6), fontsize=12, width=14, height=16, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.expanding = 0
        self.expanded = 0



    def ClearNote(self, *args):
        response = uicore.Message('ConfirmClearText', {}, uiconst.YESNO, uiconst.ID_YES)
        if response == uiconst.ID_YES:
            self.parent.SetValue('')
        uicore.registry.SetFocus(self.parent)



    def ToggleBold(self, *args):
        self.parent.ToggleBold()



    def ToggleUnderline(self, *args):
        self.parent.ToggleUnderline()



    def ToggleItalic(self, *args):
        self.parent.ToggleItalic()



    def AddAnchor(self, *args):
        self.parent.AddAnchor()



    def OnFontSizeChange(self, entry, header, value, *args):
        self.parent.ChangeFontSize(value)



    def OnColorChange(self, *args):
        if not self.expanding and not self.expanded:
            self.Expand()



    def Expand(self):
        uicore.layer.main.state = uiconst.UI_DISABLED
        self.expanding = 1
        uicore.Message('ComboExpand')
        colorpar = uicls.Container(name='colors', align=uiconst.RELATIVE, pos=(0, 0, 130, 133), parent=uicore.layer.menu, idx=0)
        colors = [((1.0, 1.0, 1.0, 1.0), 'white'),
         ((0.7, 0.7, 0.7, 1.0), 'grey 70%'),
         ((0.3, 0.3, 0.3, 1.0), 'grey 30%'),
         ((0.0, 0.0, 0.0, 1.0), 'black'),
         ((1.0, 1.0, 0.0, 1.0), 'yellow'),
         ((0.0, 1.0, 0.0, 1.0), 'green'),
         ((1.0, 0.0, 0.0, 1.0), 'red'),
         ((0.0, 0.0, 1.0, 1.0), 'blue'),
         ((0.5, 0.5, 0.0, 1.0), 'dark yellow'),
         ((0.0, 0.5, 0.0, 1.0), 'dark green'),
         ((0.5, 0.0, 0.0, 1.0), 'dark red'),
         ((0.0, 0.0, 0.5, 1.0), 'dark blue'),
         ((0.5, 0.0, 0.5, 1.0), 'dark mangenta'),
         ((0.0, 1.0, 1.0, 1.0), 'cyan'),
         ((1.0, 0.0, 1.0, 1.0), 'mangenta'),
         ((0.0, 0.5, 1.0, 1.0), 'dark blue')]
        x = y = 0
        scrolllist = []
        icons = []
        size = 32
        for each in colors:
            (color, labelstr,) = each
            x += 1
            if x == 4:
                colorsprite = uicls.Sprite(parent=colorpar, align=uiconst.RELATIVE, pos=(size * x,
                 size * y,
                 size,
                 size), color=color)
                colorsprite.OnClick = (self.PickCol, colorsprite)
                colorsprite.sr.color = color
                y += 1
                x = 0

        (cl, ct, cw, ch,) = self.sr.color.GetAbsolute()
        colorpar.left = min(cl, uicore.desktop.width - colorpar.width)
        colorpar.top = min(ct + ch, uicore.desktop.height - colorpar.height)
        self.sr.colorpar = _weakref.ref(colorpar)
        sm.GetService('event').RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self.expanding = 0
        self.expanded = 1



    def OnGlobalClick(self, fromwhere, *etc):
        if self.sr.colorpar and self.sr.colorpar() and uiutil.IsUnder(fromwhere, self.sr.colorpar()):
            return 1
        if self.sr.colorpar and self.sr.colorpar():
            if uicore.uilib.mouseOver is self.sr.colorpar().sr.scrolltop or fromwhere is self.sr.colorpar().sr.scrolltop:
                log.LogInfo('Combo.OnGlobalClick Ignoring click on scrolltop')
                return 1
            if self.sr.colorpar and self.sr.colorpar():
                if self.sr.colorpar().parent and not self.sr.colorpar().parent.destroyed:
                    self.sr.colorpar().parent.Close()
            self.sr.colorpar = None
        self.Cleanup()
        return 0



    def PickCol(self, sender, *args):
        self.parent.ChangeFontColor(sender.sr.identifier)
        self.Cleanup()



    def Cleanup(self):
        menu.KillAllMenus()
        self.expanded = 0



    def AttribStateChange(self, bold, italic, underline, size, color, url, *args):
        self.sr.bold.SetAlpha([0.6, 1.0][bold])
        self.sr.italic.SetAlpha([0.6, 1.0][italic])
        self.sr.underline.SetAlpha([0.6, 1.0][underline])
        self.sr.color.children[0].SetRGB(*color)
        self.sr.comboFontSize.SelectItemByValue(size)
        self.sr.anchor.SetAlpha([0.6, 1.0][bool(url)])




