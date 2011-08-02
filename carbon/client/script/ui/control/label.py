import blue
import bluepy
import trinity
import log
import mathUtil
import uicls
import uiutil
import uiconst
import fontConst
import sys
import log
import re
layoutCountStat = blue.statistics.Find('CarbonUI/labelLayout')
if not layoutCountStat:
    print "Registering new 'CarbonUI/labelLayout' stat"
    layoutCountStat = blue.CcpStatisticsEntry()
    layoutCountStat.name = 'CarbonUI/labelLayout'
    layoutCountStat.type = 1
    layoutCountStat.resetPerFrame = True
    layoutCountStat.description = 'The number of calls to LabelCore.Layout per frame'
    blue.statistics.Register(layoutCountStat)

class LabelCore(uicls.Sprite):
    __guid__ = 'uicls.LabelCore'
    ALLEFT = 0
    ALRIGHT = 1
    ALCENTER = 2
    default_name = 'label'
    default_state = uiconst.UI_DISABLED
    default_font = fontConst.DEFAULT_FONT
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_color = None
    default_text = ''
    default_tabs = []
    default_shadow = [(1, -1, -1090519040)]
    default_uppercase = False
    default_maxlines = None
    default_singleline = 0
    default_linespace = None
    default_letterspace = uiconst.LABELLETTERSPACE
    default_underline = 0
    default_bold = 0
    default_italic = 0
    default_mousehilite = 0
    default_allowpartialtext = 0
    default_width = 0
    default_height = 0
    default_textalign = ALLEFT
    default_boldlinks = 1
    default_filter = False
    default_specialIndent = 0

    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        align = self.GetAlign()
        if align != uiconst.TOALL:
            self._setWidth = self.width
            self._setheight = self.height
        else:
            self._setWidth = 0
            self._setheight = 0
        self.busy = 1
        self.textwidth = 0
        self.textheight = 0
        self._resolvingAutoSizing = False
        self._defaultcolor = mathUtil.LtoI(4294967295L)
        self._colorstack = []
        self._boundingBoxes = []
        self._links = []
        self._renderlines = []
        self._parsingBuff = []
        self._paramsBackup = None
        self._tabMargin = uiconst.LABELTABMARGIN
        self._hilite = 0
        self._currentLink = None
        self._activeLink = None
        self._numLines = None
        self._lastAbs = None
        self._inited = 1
        self.tabs = attributes.get('tabs', self.default_tabs)
        self.shadow = attributes.get('shadow', self.default_shadow)
        self.font = attributes.get('font', self.default_font)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.uppercase = attributes.get('uppercase', self.default_uppercase)
        self.maxlines = attributes.get('maxlines', self.default_maxlines)
        self.singleline = attributes.get('singleline', self.default_singleline)
        self.linespace = attributes.get('linespace', self.default_linespace)
        self.letterspace = attributes.get('letterspace', self.default_letterspace)
        self.underline = attributes.get('underline', self.default_underline)
        self.bold = attributes.get('bold', self.default_bold)
        self.italic = attributes.get('italic', self.default_italic)
        self.mousehilite = attributes.get('mousehilite', self.default_mousehilite)
        self.allowpartialtext = attributes.get('allowpartialtext', self.default_allowpartialtext)
        self.boldLinks = attributes.get('boldlinks', self.default_boldlinks)
        self.specialIndent = attributes.get('specialIndent', self.default_specialIndent)
        self._measuringText = attributes.get('measuringText', False)
        self.SetRGB(1.0, 1.0, 1.0, 1.0)
        textcolor = attributes.get('color', self.default_color) or self.default_color
        if textcolor is not None:
            self.SetTextColor(textcolor)
        self.__dict__['labelIsReady'] = True
        self.busy = 0
        self.text = attributes.get('text', self.default_text)
        trinity.device.RegisterResource(self)



    def Close(self):
        uicls.Sprite.Close(self)
        self._boundingBoxes = []
        self._links = []
        self._renderlines = []
        self._parsingBuff = []
        self._paramsBackup = None
        self._renderer = None
        self.measurer = None
        self.params = None



    def ResolveAutoSizing(self, absoluteSize):
        self._resolvingAutoSizing = True
        setWidth = self._setWidth
        setHeight = self._setHeight
        (absWidth, absHeight,) = absoluteSize
        align = self.GetAlign()
        if align in (uiconst.RELATIVE,
         uiconst.TOPLEFT,
         uiconst.TOPRIGHT,
         uiconst.BOTTOMRIGHT,
         uiconst.BOTTOMLEFT,
         uiconst.CENTER,
         uiconst.CENTERLEFT,
         uiconst.CENTERTOP,
         uiconst.CENTERRIGHT,
         uiconst.CENTERBOTTOM):
            self.width = setWidth or self.textwidth
            self.rectWidth = self.width
            absWidth = self.width
            self.height = setHeight or self.textheight
            self.rectHeight = self.height
            absHeight = self.height
        elif align in (uiconst.TOLEFT, uiconst.TORIGHT):
            self.width = setWidth or self.textwidth
            self.rectWidth = self.width
            self.rectHeight = absHeight
            absWidth = self.width
        elif align in (uiconst.TOBOTTOM, uiconst.TOTOP):
            self.height = setHeight or self.textheight
            self.rectHeight = self.height
            self.rectWidth = absWidth
            absHeight = self.height
        else:
            self.rectWidth = absWidth
            self.rectHeight = absHeight
        self._resolvingAutoSizing = False
        return (absWidth, absHeight)



    def OnInvalidate(self, level):
        self.texture = None



    def OnCreate(self, dev):
        if not self.destroyed:
            self.Layout('OnCreate')



    @apply
    def width():
        doc = 'Width of UI element'
        fget = uicls.Sprite.width.fget

        def fset(self, value):
            uicls.Sprite.width.fset(self, value)
            if not getattr(self, '_resolvingAutoSizing', False) and self.GetAlign() != uiconst.TOALL:
                self._setWidth = value


        return property(**locals())



    @apply
    def height():
        doc = 'Height of UI element'
        fget = uicls.Sprite.height.fget

        def fset(self, value):
            uicls.Sprite.height.fset(self, value)
            if not getattr(self, '_resolvingAutoSizing', False) and self.GetAlign() != uiconst.TOALL:
                self._setHeight = value


        return property(**locals())



    @apply
    def text():
        doc = 'Text of this label'

        def fget(self):
            return self._text



        def fset(self, value):
            if value is None:
                value = ''
            self._text = unicode(value)
            if 'labelIsReady' in self.__dict__:
                self._activeLink = None
                self.Layout('text')


        return property(**locals())



    @apply
    def font():
        doc = 'Font'

        def fget(self):
            return self._font



        def fset(self, value):
            self._font = value
            self.Layout('font')


        return property(**locals())



    @apply
    def fontsize():
        doc = 'Font size'

        def fget(self):
            return self._fontsize



        def fset(self, value):
            self._fontsize = value
            self.Layout('fontsize')


        return property(**locals())



    @apply
    def letterspace():
        doc = ''

        def fget(self):
            return self._letterspace



        def fset(self, value):
            self._letterspace = value
            self.Layout('letterspace')


        return property(**locals())



    @apply
    def uppercase():
        doc = ''

        def fget(self):
            return self._uppercase



        def fset(self, value):
            self._uppercase = value
            self.Layout('uppercase')


        return property(**locals())



    @apply
    def linespace():
        doc = ''

        def fget(self):
            return self._linespace



        def fset(self, value):
            self._linespace = value
            self.Layout('linespace')


        return property(**locals())



    @apply
    def wordspace():
        doc = ''

        def fget(self):
            return self._wordspace



        def fset(self, value):
            self._wordspace = value
            self.Layout('wordspace')


        return property(**locals())



    @apply
    def underline():
        doc = ''

        def fget(self):
            return self._underline



        def fset(self, value):
            self._underline = value
            self.Layout('underline')


        return property(**locals())



    @apply
    def bold():
        doc = ''

        def fget(self):
            return self._bold



        def fset(self, value):
            self._bold = value
            self.Layout('bold')


        return property(**locals())



    @apply
    def italic():
        doc = ''

        def fget(self):
            return self._italic



        def fset(self, value):
            self._italic = value
            self.Layout('italic')


        return property(**locals())



    def SetTextColor(self, color):
        tricolor = trinity.TriColor()
        tricolor.SetRGB(*color)
        if len(color) != 4:
            tricolor.a = 1.0
        self._defaultcolor = tricolor.AsInt()


    SetDefaultColor = SetTextColor

    def SetTabMargin(self, margin, refresh = 1):
        self._tabMargin = margin
        if refresh:
            self.Layout('SetTabMargin')



    def GetRenderer(self):
        if not getattr(self, '_renderer', None):
            self._renderer = uicore.font.GetRenderer()
        return self._renderer



    def GetMeasurer(self):
        if not getattr(self, 'measurer', None):
            self.measurer = uicore.font.GetMeasurer()
        return self.measurer



    def GetParams(self, new = 0):
        if not getattr(self, 'params', None) or new:
            params = uicore.font.GetParams()
            params.font = self.font
            params.fontsize = self.fontsize
            params.underline = self.underline
            params.bold = self.bold
            params.italic = self.italic
            params.letterspace = self.letterspace
            params.linespace = self.linespace or self.fontsize
            params.color = self._defaultcolor
            self.params = params
        return self.params



    def SetText(self, text):
        self.text = text



    def GetText(self):
        return self.text



    def GetTab(self, idx, right = None):
        if len(self.tabs) > idx:
            return self.tabs[idx]
        if right is not None:
            return right



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLeftOverText(self):
        text = self.text.replace(u'<BR>', u'<br>').replace(u'\r\n', u'<br>').replace(u'<T>', u'<t>')
        if self.singleline:
            text = text.replace(u'<br>', u' ')
        rettext = ''
        characterCount = 0
        currentCharacterAmount = len(self._boundingBoxes)
        startedToAdd = False
        for line in text.split(u'<br>'):
            if startedToAdd:
                rettext += line + '<br>'
                continue
            for each in line.split(u'>'):
                texttag = each.split(u'<', 1)
                if len(texttag) == 1:
                    (text, tag,) = (self.Encode(texttag[0]), None)
                else:
                    (text, tag,) = (self.Encode(texttag[0]), texttag[1])
                for word in text.split(u' '):
                    if characterCount >= currentCharacterAmount:
                        rettext += word + ' '
                        startedToAdd = True
                    characterCount += len(word) + 1

                characterCount -= 1
                if tag:
                    rettext += '<' + tag + '>'

            if startedToAdd:
                rettext += '<br>'

        if startedToAdd:
            rettext = rettext[:-4]
        return rettext



    @bluepy.CCP_STATS_ZONE_METHOD
    def Layout(self, hint = 'None', params = None, absSize = None):
        layoutCountStat.Inc()
        if getattr(self, 'busy', 0):
            return 
        self.busy = True
        self._boundingBoxes = []
        self.textwidth = 0
        self.textheight = 0
        text = self.text or u''
        if not text:
            self.texture = None
            self.spriteEffect = trinity.TR2_SFX_NONE
            self.busy = False
            return 
        self.spriteEffect = trinity.TR2_SFX_COPY
        align = self.GetAlign()
        if align in (uiconst.RELATIVE,
         uiconst.TOPLEFT,
         uiconst.TOPRIGHT,
         uiconst.BOTTOMRIGHT,
         uiconst.BOTTOMLEFT,
         uiconst.CENTER,
         uiconst.CENTERLEFT,
         uiconst.CENTERTOP,
         uiconst.CENTERRIGHT,
         uiconst.CENTERBOTTOM):
            if self._setWidth:
                width = self._setWidth
            else:
                width = self.GetMaxWidth()
        elif absSize:
            (width, height,) = absSize
        else:
            (width, height,) = self.GetAbsoluteSize()
        self.textalign = self.ALLEFT
        self._currentLink = None
        self._colorstack = []
        self._links = []
        self._renderlines = []
        self._parsingBuff = []
        self._numLines = 0
        p = params or self.GetParams(1)
        margin = self._tabMargin
        text = text.replace(u'<BR>', u'<br>').replace(u'\r\n', u'<br>').replace(u'\n', u'<br>').replace(u'<T>', u'<t>')
        if self.singleline:
            text = text.replace(u'<br>', u' ')
        for line in text.split(u'<br>'):
            tabtext = line.split(u'<t>')
            if len(tabtext) > 1:
                vScrollshiftX = getattr(self, 'xShift', 0)
                left = max(0, margin + vScrollshiftX)
                for i in xrange(len(tabtext)):
                    self.textalign = self.default_textalign
                    right = self.GetTab(i, width) - margin
                    self.Parse(tabtext[i], left, right + vScrollshiftX - left)
                    self.FlushBuff()
                    left = right + margin * 2 + vScrollshiftX

            else:
                self.Parse(tabtext[0], 0, width)
            self.Linebreak()

        if self.shadow:
            extendLeft = 0
            extendTop = 0
            extendRight = 0
            extendBottom = 0
            for (sx, sy, scol,) in self.shadow:
                extendLeft = min(extendLeft, sx)
                extendRight = max(extendRight, sx)
                extendTop = max(extendTop, sy)
                extendBottom = min(extendBottom, sy)

            self.textwidth += -extendLeft + extendRight
            self.textheight += -extendBottom + extendTop
        if not self._measuringText:
            absoluteSize = self.GetAbsoluteSize()
            absoluteSize = self.ResolveAutoSizing(absoluteSize=absoluteSize)
            self.Render(absoluteSize)
            self._lastRenderData = (text, absoluteSize)
        self.busy = False



    def GetMaxWidth(self, *args):
        return uicore.deviceCaps['MaxTextureWidth']



    @bluepy.CCP_STATS_ZONE_METHOD
    def Render(self, absoluteSize = None):
        if not hasattr(self, '_renderlines'):
            return 
        if absoluteSize:
            (absW, absH,) = absoluteSize
        else:
            (absW, absH,) = self.GetAbsoluteSize()
        needW = max(2, absW, self.textwidth)
        needH = max(2, absH, self.textheight)
        if needW > self.GetMaxWidth():
            needW = self.GetMaxWidth()
        if needW < 1 or needH < 4:
            self.texture = None
            self.spriteEffect = trinity.TR2_SFX_NONE
            return 
        needNewTexture = True
        if self.texture and self.texture.atlasTexture:
            at = self.texture.atlasTexture
            if at.width == needW and at.height == needH:
                needNewTexture = False
        if needNewTexture:
            self.texture = None
            texturePrimary = trinity.Tr2Sprite2dTexture()
            texturePrimary.atlasTexture = uicore.uilib.CreateTexture(int(needW), int(needH))
            texturePrimary.srcX = 0.0
            texturePrimary.srcY = 0.0
            self.texture = texturePrimary
        else:
            texturePrimary = self.texture
        texturePrimary.srcWidth = int(absW)
        texturePrimary.srcHeight = int(absH)
        try:
            bufferData = texturePrimary.atlasTexture.LockBuffer()
        except AttributeError:
            if texturePrimary.atlasTexture:
                texturePrimary.atlasTexture.UnlockBuffer()
                bufferData = texturePrimary.atlasTexture.LockBuffer()
            else:
                self.display = False
                return 
        (bufferDataData, bufferDataWidth, bufferDataHeight, bufferDataPitch,) = bufferData
        uicore.font.Clear_Buffer(*bufferData)
        renderer = self.GetRenderer()
        shadowOffsetX = shadowOffsetY = 0
        if self.shadow:
            (sx, sy, scol,) = self.shadow[-1]
            if sx < 0:
                shadowOffsetX = abs(sx)
            if sy > 0:
                shadowOffsetY = sy
            extendLeft = 0
            extendTop = 0
            for (sx, sy, scol,) in self.shadow:
                extendLeft = min(extendLeft, sx)
                extendTop = max(extendTop, sy)

            shadowOffsetX = -extendLeft
            shadowOffsetY = extendTop
        for (text, params, shiftX, shiftY, strong, sBits,) in self._renderlines:
            renderer.Reset(bufferData, (shiftX + shadowOffsetX, bufferDataHeight - shiftY - shadowOffsetY), self._hilite, self.shadow)
            renderer.AddTextFast(text, params, sBits)

        texturePrimary.atlasTexture.UnlockBuffer()



    @bluepy.CCP_STATS_ZONE_METHOD
    def Parse(self, line, xoffset, width):
        self.tabwidth = width
        self.tabpos = xoffset
        self.GetMeasurer().Reset(self.tabwidth, self.GetParams())
        for each in line.split(u'>'):
            texttag = each.split(u'<', 1)
            if len(texttag) == 1:
                (text, tag,) = (self.Encode(texttag[0]), None)
            else:
                (text, tag,) = (self.Encode(texttag[0]), texttag[1])
            if text:
                if self.uppercase:
                    text = text.upper()
                for word in uiutil.FindTextBoundaries(text, regexObject=uiconst.LINE_BREAK_BOUNDARY_REGEX):
                    if not self.PushWord(word):
                        if tag:
                            self.ParseTag(tag)
                        return 

            if tag:
                self.ParseTag(tag)

        if not self._parsingBuff:
            self.PushWord(u' ')



    @bluepy.CCP_STATS_ZONE_METHOD
    def PushWord(self, word, params = None):
        toReturn = True
        if word:
            params = params or self.GetParams()
            (n, last, bbox, renderData,) = self.GetMeasurer().AddTextGetRenderData(word, params)
            if not n:
                if not self.singleline and self._parsingBuff:
                    if len(self._parsingBuff) > 1:
                        lastWord = self._parsingBuff[-1][0]
                        lastParams = self._parsingBuff[-1][3]
                    self.Linebreak()
                    if self.maxlines and self._numLines >= self.maxlines:
                        return False
                    return self.PushWord(word)
                return False
            if self._setHeight:
                measurer = self.GetMeasurer()
                actualHeight = measurer.asc - measurer.des
                linespace = params.linespace
                lineheight = linespace or actualHeight
                if self.textheight + lineheight >= self._setHeight:
                    if self.allowpartialtext:
                        toReturn = False
                    else:
                        return False
            if n < len(word):
                if self.singleline:
                    self._parsingBuff += renderData[:n]
                    for each in renderData[:n]:
                        self._boundingBoxes += each[-1]

                    return False
                if not self._parsingBuff:
                    self._parsingBuff += renderData[:n]
                    for each in renderData[:n]:
                        self._boundingBoxes += each[-1]

                    return self.PushWord(word[n:])
                if self._parsingBuff:
                    if len(self._parsingBuff) > 1:
                        lastWord = self._parsingBuff[-1][0]
                        lastParams = self._parsingBuff[-1][3]
                        if not lastWord[-1] == ' ':
                            self._parsingBuff = self._parsingBuff[:-1]
                            self.Linebreak()
                            if self.maxlines and self._numLines >= self.maxlines:
                                return False
                            self.PushWord(lastWord, lastParams)
                        else:
                            self.Linebreak()
                            if self.maxlines and self._numLines >= self.maxlines:
                                return False
                    else:
                        self.Linebreak()
                        if self.maxlines and self._numLines >= self.maxlines:
                            return False
                return self.PushWord(word)
            self._parsingBuff += renderData[:n]
            for each in renderData[:n]:
                self._boundingBoxes += each[-1]

        return toReturn



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetIndexUnderPos(self, pos):
        retIndex = 0
        totalWidth = 0
        if pos < 0:
            return (retIndex, totalWidth)
        for sBit in self._boundingBoxes:
            glyphWidth = sBit.xadvance
            if totalWidth - glyphWidth / 2.0 < pos <= totalWidth + glyphWidth / 2.0 or totalWidth >= pos:
                break
            totalWidth += glyphWidth
            retIndex += 1

        return (retIndex, totalWidth)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetWidthToIndex(self, index):
        if index == -1:
            index = len(self._boundingBoxes)
        index = min(len(self._boundingBoxes), max(0, index))
        return (index, sum([ each.xadvance for each in self._boundingBoxes[:index] ]))



    @bluepy.CCP_STATS_ZONE_METHOD
    def Linebreak(self):
        self.FlushBuff()
        measurer = self.GetMeasurer()
        actualHeight = measurer.asc - measurer.des
        linespace = self.GetParams().linespace
        lineheight = max(linespace, actualHeight)
        self.textheight += lineheight
        if self._currentLink:
            self._links[-1][3] = measurer.cursor
            self._links[-1][4] = self.textheight
        measurer.Reset(self.tabwidth)
        measurer.cursor = self.specialIndent
        self._numLines += 1
        if self._currentLink:
            self._links.append([self._currentLink,
             measurer.cursor,
             self.textheight,
             0,
             0])



    @bluepy.CCP_STATS_ZONE_METHOD
    def FlushBuff(self):
        if not self._parsingBuff:
            return 
        buffWidth = self._parsingBuff[-1][2]
        pos = self.tabpos
        if self.textalign == self.ALRIGHT:
            pos += self.tabwidth - buffWidth
        elif self.textalign == self.ALCENTER:
            pos += int((self.tabwidth - buffWidth) / 2)
        shiftY = self.textheight + self.GetMeasurer().asc
        for (text, textStart, textEnd, params, sBits,) in self._parsingBuff:
            self._renderlines.append((text,
             params,
             pos + textStart,
             shiftY,
             0,
             sBits))
            self.textwidth = max(self.textwidth, pos + textStart + (textEnd - textStart))

        self._parsingBuff = []



    @bluepy.CCP_STATS_ZONE_METHOD
    def ParseTag(self, _tag):
        orgTag = _tag
        tag = _tag.lower()
        params = self.GetParams()
        if tag == u'u':
            if self.params.underline != 1:
                self.params = params.Copy()
            self.params.underline = 1
        elif tag == u'/u':
            if self.params.underline != 0:
                self.params = params.Copy()
            self.params.underline = 0
        elif tag.startswith(u'url'):
            self.StartLink(orgTag[4:], params)
        elif tag == u'/url':
            self.EndLink(params)
        elif tag == u'b':
            if self.params.bold != 1:
                self.params = params.Copy()
            self.params.bold = 1
        elif tag == u'/b':
            if self.params.bold != 0:
                self.params = params.Copy()
            self.params.bold = 0
        elif tag == u'i':
            if self.params.italic != 1:
                self.params = params.Copy()
            self.params.italic = 1
        elif tag == u'/i':
            if self.params.italic != 0:
                self.params = params.Copy()
            self.params.italic = 0
        elif tag == u'left':
            self.textalign = self.ALLEFT
        elif tag == u'right':
            self.textalign = self.ALRIGHT
        elif tag == u'center':
            self.textalign = self.ALCENTER
        elif tag.startswith(u'fontsize='):
            fs = int(_tag[9:])
            if self.params.fontsize != fs:
                self.params = params.Copy()
            self.params.fontsize = fs
        elif tag.startswith(u'font='):
            fn = _tag[5:]
            if self.params.font != fn:
                self.params = params.Copy()
            self.params.font = fn
        elif tag.startswith(u'letterspace='):
            ls = int(_tag[12:])
            if self.params.letterspace != ls:
                self.params = params.Copy()
            self.params.letterspace = fs
        elif tag.startswith(u'icon='):
            measurer = self.GetMeasurer()
            measurer.AddSpace(16)
            fakeSbit = uiutil.Bunch()
            fakeSbit.xadvance = 16
            self._boundingBoxes.append(fakeSbit)
        elif tag.startswith(u'color='):
            color = uiutil.StringColorToHex(_tag[6:])
            if color is None:
                color = _tag[6:16]
            col = mathUtil.LtoI(long(color, 0))
            if self._currentLink and self._currentLink == self._activeLink:
                col = -9472
            if self.params.color != col:
                self.params = params.Copy()
            self.params.color = col
            self._colorstack.append(col)
        elif tag.startswith(u'/color'):
            if self.params.color != self._defaultcolor:
                self.params = params.Copy()
            if self._colorstack:
                self._colorstack.pop()
            if self._colorstack:
                self.params.color = self._colorstack[-1]
            else:
                self.params.color = self._defaultcolor



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartLink(self, url, params):
        url = url.replace('&amp;', '&')
        self._currentLink = url
        self._paramsBackup = params.Copy()
        self.params = params.Copy()
        if url == self._activeLink:
            self.params.color = -9472
        else:
            self.params.color = getattr(self, 'linkColor', None) or -23040
        self.params.bold = self.boldLinks
        measurer = self.GetMeasurer()
        self._links.append([url,
         self.tabpos + measurer.cursor,
         self.textheight,
         0,
         0])



    @bluepy.CCP_STATS_ZONE_METHOD
    def EndLink(self, params):
        if not self._links:
            return 
        measurer = self.GetMeasurer()
        actualHeight = measurer.asc - measurer.des
        lineheight = self.GetParams().linespace or actualHeight
        self._links[-1][3] = self.tabpos + measurer.cursor
        self._links[-1][4] = self.textheight + lineheight
        if self._paramsBackup:
            self.params = self._paramsBackup.Copy()
            self._paramsBackup = None
        else:
            self.params = None
        self._currentLink = None



    def GetMenu(self):
        m = []
        if self._activeLink:
            m = uicls.BaseLink().GetLinkMenu(self, self._activeLink.replace('&amp;', '&'))
        m += [(mls.UI_CMD_COPY, self.CopyText)]
        return m



    def CopyText(self):
        blue.pyos.SetClipboardData(self.text)



    def OnMouseEnter(self, *args):
        if self.mousehilite:
            self._hilite = 1
            self.Render((self._displayWidth, self._displayHeight))



    def OnMouseMove(self, *args):
        if not self._hilite:
            self.CheckLinks()



    def OnMouseExit(self, *args):
        if self.mousehilite:
            self._hilite = 0
            self.Render((self._displayWidth, self._displayHeight))
        else:
            self.CheckLinks()



    @bluepy.CCP_STATS_ZONE_METHOD
    def CheckLinks(self):
        aLink = None
        if self._links and uicore.uilib.mouseOver == self:
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            (left, top, width, height,) = self.GetAbsolute()
            for (url, startX, startY, endX, endY,) in self._links:
                if left + startX < mouseX < left + endX and top + startY < mouseY < top + endY:
                    hint = url
                    aLink = url
                    break

            if not aLink:
                self.sr.hint = None
                self.cursor = uiconst.UICURSOR_DEFAULT
            else:
                self.cursor = uiconst.UICURSOR_SELECT
        if aLink != self._activeLink:
            self._activeLink = aLink
            self.Layout()



    def OnClick(self, *args):
        if self._activeLink:
            uicls.BaseLink().ClickLink(self, self._activeLink.replace('&amp;', '&'))



    def Encode(self, text):
        return text.replace(u'&gt;', u'>').replace(u'&lt;', u'<').replace(u'&amp;', u'&').replace(u'&GT;', u'>').replace(u'&LT;', u'<')



    def Decode(self, text):
        return text.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')



    @bluepy.CCP_STATS_ZONE_METHOD
    def _OnSizeChange_NoBlock(self, newWidth, newHeight, *args):
        uicls.Sprite._OnSizeChange_NoBlock(self, newWidth, newHeight, *args)
        if not self._resolvingAutoSizing:
            newAbs = (newWidth, newHeight)
            lastRenderData = getattr(self, '_lastRenderData', (None, None))
            (lastText, absSize,) = lastRenderData
            if absSize != newAbs:
                self.Layout('_OnSizeChange_NoBlock', absSize=newAbs)
        if getattr(self, 'OnSizeChanged', None):
            self.OnSizeChanged()




