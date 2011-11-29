import blue
import bluepy
import trinity
import mathUtil
import uicls
import uiutil
import uiconst
import fontConst
import sys
import log
import re
import localization
import localizationUtil
import localizationInternalUtil
import types
import service
import uthread
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
    linespace = 0
    ALLEFT = 0
    ALRIGHT = 1
    ALCENTER = 2
    default_name = 'label'
    default_state = uiconst.UI_DISABLED
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_linkStyle = uiconst.LINKSTYLE_SUBTLE
    default_color = None
    default_text = ''
    default_tabs = []
    default_uppercase = False
    default_maxlines = None
    default_singleline = 0
    default_lineSpacing = 0.0
    default_wordspace = 0
    default_letterspace = 0
    default_underline = 0
    default_bold = 0
    default_italic = 0
    default_mousehilite = 0
    default_allowpartialtext = 0
    default_width = 0
    default_height = 0
    default_textalign = ALLEFT
    default_specialIndent = 0
    default_autoDetectCharset = False

    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        self.useSizeFromTexture = True
        self._lineSpacing = self.default_lineSpacing
        align = self.GetAlign()
        if align != uiconst.TOALL:
            self._setWidth = self.width
            self._setHeight = self.height
        else:
            self._setWidth = 0
            self._setHeight = 0
        self.busy = 1
        self._layoutOnSizeChangeThread = None
        self.textwidth = 0
        self.textheight = 0
        self.actualTextWidth = 0
        self.actualTextHeight = 0
        self._resolvingAutoSizing = False
        self._defaultcolor = mathUtil.LtoI(4294967295L)
        self.localizationErrorCheckEnabled = localizationUtil.IsHardcodedStringDetectionEnabled() and session.role & service.ROLE_QA == service.ROLE_QA
        self.localizationPseudolocalizationEnabled = localizationUtil.IsPseudolocalizationEnabled() and localizationUtil.GetLanguageID() == localization.LOCALE_SHORT_ENGLISH
        self._numCharactersAdded = 0
        self._links = []
        self._inlineObjects = []
        self._inlineObjectsBuff = []
        self._tabMargin = uiconst.LABELTABMARGIN
        self._hilite = 0
        self._mouseOverUrl = None
        self._numLines = None
        self._lastAbs = None
        self._inited = 1
        self.tabs = attributes.get('tabs', self.default_tabs)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.linkStyle = attributes.get('linkStyle', self.default_linkStyle)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.underline = attributes.get('underline', self.default_underline)
        self.bold = attributes.get('bold', self.default_bold)
        self.italic = attributes.get('italic', self.default_italic)
        self.uppercase = attributes.get('uppercase', self.default_uppercase)
        self.autoDetectCharset = attributes.get('autoDetectCharset', self.default_autoDetectCharset)
        self.maxlines = attributes.get('maxlines', self.default_maxlines)
        self.singleline = attributes.get('singleline', self.default_singleline)
        self.lineSpacing = attributes.get('lineSpacing', self.default_lineSpacing)
        self.wordspace = attributes.get('wordspace', self.default_wordspace)
        self.letterspace = attributes.get('letterspace', self.default_letterspace)
        self.mousehilite = attributes.get('mousehilite', self.default_mousehilite)
        self.allowpartialtext = attributes.get('allowpartialtext', self.default_allowpartialtext)
        self.specialIndent = attributes.get('specialIndent', self.default_specialIndent)
        self._measuringText = attributes.get('measuringText', False)
        self.SetRGB(1.0, 1.0, 1.0, 1.0)
        textcolor = attributes.color or self.default_color
        if textcolor is not None:
            self.SetTextColor(textcolor)
        self.__dict__['labelIsReady'] = True
        self.busy = 0
        self._cachedLines = None
        self.text = attributes.get('text', self.default_text)
        trinity.device.RegisterResource(self)
        uicore.textObjects.add(self)



    def Close(self):
        uicls.Sprite.Close(self)
        self._links = []
        self._inlineObjects = []
        self._inlineObjectsBuff = []
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
        elif align in (uiconst.TOLEFT,
         uiconst.TORIGHT,
         uiconst.TOLEFT_NOPUSH,
         uiconst.TORIGHT_NOPUSH):
            self.width = setWidth or self.textwidth
            self.rectWidth = self.width
            self.rectHeight = absHeight
            absWidth = self.width
        elif align in (uiconst.TOBOTTOM,
         uiconst.TOTOP,
         uiconst.TOBOTTOM_NOPUSH,
         uiconst.TOTOP_NOPUSH):
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
    def hint():

        def fget(self):
            return getattr(self, '_hint', None)



        def fset(self, value):
            if not getattr(self, '_resolvingInlineHint', False):
                self._objectHint = value
            else:
                self._hint = value


        return property(**locals())



    @apply
    def text():
        doc = 'Text of this label, this can be pure string or list of [formattags, str, ...]'

        def fget(self):
            return self._text



        @bluepy.CCP_STATS_ZONE_METHOD
        def fset(self, value):
            value = uiutil.GetAsUnicode(value)
            if self.localizationErrorCheckEnabled:
                (self._renderText, self._localizationError,) = localizationUtil.CheckForLocalizationErrors(value)
                self._text = uiutil.StripTags(self._renderText, stripOnly=['localized'])
                self._renderText = localizationInternalUtil.WrapStringForDisplay(self._renderText)
            else:
                self._text = value
                self._renderText = value
                self._localizationError = False
            self._renderText = self._renderText.replace(u'<BR>', u'<br>').replace(u'\r\n', u'<br>').replace(u'\n', u'<br>').replace(u'<T>', u'<t>').replace('<br />', '<br>').replace('<br/>', '<br>').replace('\t', ' ').replace('&nbsp;', ' ')
            self._cachedLines = None
            if 'labelIsReady' in self.__dict__:
                self._mouseOverUrl = None
                self.Layout('text')


        return property(**locals())



    @apply
    def fontStyle():
        doc = ''

        def fget(self):
            return self._fontStyle



        def fset(self, value):
            self._fontStyle = value
            self.Layout('fontStyle')


        return property(**locals())



    @apply
    def fontFamily():
        doc = 'Font Family, list of 4 font resPaths representing regular, italic, bold, boldItalic'

        def fget(self):
            return self._fontFamily



        def fset(self, value):
            self._fontFamily = value
            self.Layout('fontFamily')


        return property(**locals())



    @apply
    def fontPath():
        doc = 'Font Family, list of 4 font resPaths representing regular, italic, bold, boldItalic'

        def fget(self):
            return self._fontPath



        def fset(self, value):
            self._fontPath = value
            self.Layout('fontPath')


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
            return bool(self._uppercase)



        def fset(self, value):
            self._uppercase = value
            self.Layout('uppercase')


        return property(**locals())



    @apply
    def lineSpacing():
        doc = ''

        def fget(self):
            return self._lineSpacing



        def fset(self, value):
            value = max(-1.0, value)
            if self._lineSpacing != value:
                self._lineSpacing = value
                self.Layout('lineSpacing')


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
        self.Layout('SetTextColor')


    SetDefaultColor = SetTextColor

    def SetTabMargin(self, margin, refresh = 1):
        self._tabMargin = margin
        if refresh:
            self.Layout('SetTabMargin')



    def GetMeasurer(self):
        if not getattr(self, 'measurer', None):
            self.measurer = trinity.Tr2FontMeasurer()
        return self.measurer



    def GetParams(self, new = 0):
        if not getattr(self, 'params', None) or new:
            params = uiutil.Bunch()
            params.fontStyle = self.fontStyle
            params.fontFamily = self.fontFamily
            params.fontPath = self.fontPath
            self.params = params
            return params
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
        currentCharacterAmount = self._numCharactersAdded
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
    def Layout(self, hint = 'None', absSize = None):
        layoutCountStat.Inc()
        if getattr(self, 'busy', 0):
            return 
        self.busy = True
        self.GetMeasurer().Reset()
        self._numCharactersAdded = 0
        self.textwidth = 0
        self.actualTextWidth = 0
        self.textheight = 0
        self.actualTextHeight = 0
        text = self._renderText
        if not text:
            self.texture = None
            self.spriteEffect = trinity.TR2_SFX_NONE
            self.busy = False
            return 
        if self.localizationPseudolocalizationEnabled and localizationInternalUtil.IsLocalizationSafeString(text):
            text = localization.Pseudolocalize(text)
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
        self.ResetTagStack()
        self._links = []
        self._inlineObjects = []
        self._inlineObjectsBuff = []
        self._numLines = 0
        margin = self._tabMargin
        if self.singleline:
            lines = [text.replace(u'<br>', u' ')]
        else:
            lines = self._cachedLines
            if lines is None:
                self._cachedLines = self.SplitIntoLines(text)
                lines = self._cachedLines
        for line in lines:
            tabtext = line.split(u'<t>')
            if len(tabtext) > 1:
                vScrollshiftX = getattr(self, 'xShift', 0)
                left = max(0, margin + vScrollshiftX)
                for i in xrange(len(tabtext)):
                    if i == 0:
                        left = 0
                    self.textalign = self.default_textalign
                    right = self.GetTab(i, width) - margin
                    self.Parse(tabtext[i], left, right + vScrollshiftX - left)
                    self.FlushBuff()
                    left = right + margin * 2 + vScrollshiftX

            else:
                self.Parse(tabtext[0], 0, width)
            self.Linebreak()

        if uicore.desktop.dpiScaling != 1.0:
            self.textwidth = self.ReverseScaleDpi(self.actualTextWidth + 0.5)
            self.textheight = self.ReverseScaleDpi(self.actualTextHeight + 0.5)
        else:
            self.textwidth = self.actualTextWidth
            self.textheight = self.actualTextHeight
        if not self._measuringText:
            absoluteSize = self.GetAbsoluteSize()
            absoluteSize = self.ResolveAutoSizing(absoluteSize=absoluteSize)
            self.Render(absoluteSize)
            self._lastRenderData = (text, absoluteSize)
        self.busy = False



    def ResetTagStack(self):
        self._tagStack = {'font': [],
         'fontsize': [self.fontsize],
         'color': [self._defaultcolor],
         'letterspace': [self.letterspace],
         'hint': [],
         'link': [],
         'localized': [],
         'u': self.underline,
         'b': self.bold,
         'i': self.italic,
         'uppercase': self.uppercase}



    def GetMaxWidth(self, *args):
        return uicore.deviceCaps['MaxTextureWidth']



    @bluepy.CCP_STATS_ZONE_METHOD
    def Render(self, absoluteSize = None):
        if absoluteSize:
            (absW, absH,) = absoluteSize
        else:
            (absW, absH,) = self.GetAbsoluteSize()
        needW = max(2, self.ScaleDpi(absW), self.actualTextWidth)
        needH = max(2, self.ScaleDpi(absH), self.actualTextHeight)
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
            texturePrimary.atlasTexture = uicore.uilib.CreateTexture(needW, needH)
            texturePrimary.srcX = 0.0
            texturePrimary.srcY = 0.0
            self.texture = texturePrimary
        else:
            texturePrimary = self.texture
        texturePrimary.srcWidth = self.ScaleDpi(absW)
        texturePrimary.srcHeight = self.ScaleDpi(absH)
        self.measurer.DrawToAtlasTexture(texturePrimary.atlasTexture)



    @bluepy.CCP_STATS_ZONE_METHOD
    def Parse(self, line, xoffset, width):
        self.tabwidth = width
        self.tabpos = xoffset
        self.measurer.limit = int(self.ScaleDpi(self.tabwidth))
        self.measurer.cursorX = 0
        self.measurer.cursorY = 0
        texts_tags = self.GetTextAndTags(line)
        paramsDirty = True
        for (isTag, text_or_tag,) in texts_tags:
            if isTag:
                self.ParseTag(text_or_tag[1:-1])
                paramsDirty = True
            else:
                if paramsDirty:
                    params = self.GetParams()
                    tagStack = self._tagStack
                    if self.autoDetectCharset and not params.fontPath:
                        windowsLanguageID = uicore.font.GetWindowsLanguageIDForText(text_or_tag)
                        if windowsLanguageID:
                            fontFamily = uicore.font.GetFontFamilyBasedOnWindowsLanguageID(windowsLanguageID)
                            params.fontFamily = fontFamily
                    params.fontsize = self.ScaleDpi(tagStack['fontsize'][-1])
                    params.color = tagStack['color'][-1]
                    params.letterspace = tagStack['letterspace'][-1]
                    params.underline = bool(tagStack['u'])
                    params.italic = bool(tagStack['i'])
                    params.bold = bool(tagStack['b'])
                    if self.localizationErrorCheckEnabled:
                        if not self._tagStack['localized']:
                            params.color = localizationUtil.COLOR_HARDCODED
                        if self._localizationError:
                            params.color = localizationUtil.COLOR_HARDCODED
                    uicore.font.ResolveFontFamily(params)
                    paramsDirty = False
                couldAdd = self.PushWord(text_or_tag)
                if not couldAdd:
                    return 




    def GetTrailingWhiteSpaces(self, text):
        trail = u''
        while text and text[-1] == ' ':
            trail += u' '
            text = text[:-1]

        return (text, trail)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PushWord(self, word):
        toReturn = True
        if word:
            params = self.params
            measurer = self.measurer
            tagStack = self._tagStack
            if tagStack['uppercase']:
                word = uiutil.UpperCase(word)
            if not self.singleline:
                (word, trailingSpaces,) = self.GetTrailingWhiteSpaces(word)
            else:
                trailingSpaces = u''
            hasUncommittedText = measurer.HasUncommittedText()
            n = measurer.AddText(word, params)
            t = measurer.AddText(trailingSpaces, params)
            if self._setHeight:
                actualHeight = measurer.asc - measurer.des
                if self.actualTextHeight:
                    current = self.actualTextHeight + int(self.lineSpacing * actualHeight)
                else:
                    current = 0
                if current + actualHeight >= self._setHeight:
                    if self.allowpartialtext:
                        toReturn = False
                    else:
                        measurer.CancelLastText()
                        measurer.CancelLastText()
                        return False
            if n < len(word):
                if self.singleline:
                    return False
                else:
                    if hasUncommittedText:
                        measurer.CancelLastText()
                        measurer.CancelLastText()
                        self.Linebreak()
                        if self.maxlines and self._numLines >= self.maxlines:
                            return False
                        return self.PushWord(word + trailingSpaces)
                    if n == 0:
                        return False
                    measurer.CancelLastText()
                    measurer.CancelLastText()
                    n = measurer.AddText(word[:n], params)
                    self._numCharactersAdded += n
                    measurer.AddText(u'', params)
                    self.Linebreak()
                    if self.maxlines and self._numLines >= self.maxlines:
                        return False
                    return self.PushWord(word[n:] + trailingSpaces)
            else:
                self._numCharactersAdded += n + t
        return toReturn



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetIndexUnderPos(self, layoutPosition):
        index = self.measurer.GetIndexAtPos(self.ScaleDpi(layoutPosition))
        width = self.ReverseScaleDpi(self.measurer.GetWidthAtIndex(index))
        return (index, width)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetWidthToIndex(self, index):
        if index == -1:
            index = len(self._renderText)
        width = self.ReverseScaleDpi(self.GetMeasurer().GetWidthAtIndex(index))
        return (index, width)



    @bluepy.CCP_STATS_ZONE_METHOD
    def Linebreak(self):
        self.FlushBuff()
        measurer = self.GetMeasurer()
        actualHeight = measurer.asc - measurer.des
        if self.actualTextHeight:
            self.actualTextHeight += int(self.lineSpacing * actualHeight) + actualHeight
        else:
            self.actualTextHeight = actualHeight
        if uicore.desktop.dpiScaling != 1.0:
            self.textwidth = self.ReverseScaleDpi(self.actualTextWidth + 0.5)
            self.textheight = self.ReverseScaleDpi(self.actualTextHeight + 0.5)
        else:
            self.textwidth = self.actualTextWidth
            self.textheight = self.actualTextHeight
        measurer.limit = self.ScaleDpi(self.tabwidth)
        measurer.cursorX = self.specialIndent
        self._numLines += 1



    @bluepy.CCP_STATS_ZONE_METHOD
    def FlushBuff(self):
        measurer = self.GetMeasurer()
        buffWidth = measurer.cursorX
        pos = self.ScaleDpi(self.tabpos)
        scaledTabWidth = self.ScaleDpi(self.tabwidth)
        if self.textalign == self.ALRIGHT:
            pos += scaledTabWidth - buffWidth
        elif self.textalign == self.ALCENTER:
            pos += int((scaledTabWidth - buffWidth) / 2)
        lineHeight = measurer.asc - measurer.des
        lineSpacing = int(self.lineSpacing * lineHeight)
        if self.actualTextHeight:
            shiftY = self.actualTextHeight + lineSpacing + self.measurer.asc
        else:
            shiftY = self.measurer.asc
        moveToNextLine = []
        for object in self._inlineObjectsBuff:
            registerObject = object.Copy()
            if object.inlineXEnd is None:
                object.inlineX = self.tabpos
                moveToNextLine.append(object)
                registerObject.inlineXEnd = measurer.cursorX
            registerObject.inlineX += self.ReverseScaleDpi(pos)
            registerObject.inlineXEnd += self.ReverseScaleDpi(pos)
            registerObject.inlineY = self.textheight
            registerObject.inlineHeight = self.ReverseScaleDpi(lineHeight + lineSpacing)
            self._inlineObjects.append(registerObject)

        commited = self.measurer.CommitText(pos, shiftY)
        self.actualTextWidth = max(self.actualTextWidth, pos + buffWidth)
        self._inlineObjectsBuff = moveToNextLine



    def StripQuotes(self, tag):
        tag = tag.replace('"', '')
        tag = tag.replace("'", '')
        return tag



    @bluepy.CCP_STATS_ZONE_METHOD
    def ParseTag(self, _tag):
        orgTag = _tag
        tag = _tag.lower()
        if tag.startswith('font '):
            fontcolor = self.GetTagValue(' color=', tag)
            if fontcolor:
                self.ParseTag('color=' + self.StripQuotes(fontcolor))
            fontsize = self.GetTagValue(' size=', tag)
            if fontsize:
                self.ParseTag('fontsize=' + self.StripQuotes(fontsize))
            self._tagStack['font'].append(tag)
            return 
        if tag == '/font':
            tagStack = self._tagStack['font']
            if tagStack:
                closeFontTag = tagStack.pop()
                fontcolor = self.GetTagValue(' color=', closeFontTag)
                if fontcolor:
                    self.ParseTag('/color')
                fontsize = self.GetTagValue(' size=', closeFontTag)
                if fontsize:
                    self.ParseTag('/fontsize')
            return 
        if tag in ('u', 'i', 'b', 'uppercase'):
            self._tagStack[tag] += 1
        elif tag in ('/u', '/i', '/b', '/uppercase'):
            stackTag = tag[1:]
            self._tagStack[stackTag] = max(0, self._tagStack[stackTag] - 1)
        elif tag.startswith(u'url') or tag.startswith(u'a href'):
            fulltag = orgTag.replace('a href', 'url').replace('url:', 'url=')
            url = self.GetTagStringValue('url=', fulltag)
            if not url:
                url = self.GetTagValue('url=', fulltag)
            alt = self.GetTagStringValue(' alt=', fulltag)
            url = url.replace('&amp;', '&')
            inlineObject = self.StartInline('link', orgTag)
            inlineObject.url = url
            inlineObject.alt = alt
            self._tagStack['link'].append(inlineObject)
            linkState = uiconst.LINK_IDLE
            if self._mouseOverUrl and url == self._mouseOverUrl:
                if uicore.uilib.leftbtn:
                    linkState = uiconst.LINK_ACTIVE
                else:
                    linkState = uiconst.LINK_HOVER
            linkFmt = uicls.BaseLink().GetLinkFormat(url, linkState, self.linkStyle)
            linkColor = None
            if linkState == uiconst.LINK_IDLE:
                colorSyntax = self.GetTagValue(' color=', fulltag)
                if colorSyntax:
                    colorSyntax = colorSyntax.replace('#', '0x')
                    hexColor = uiutil.StringColorToHex(colorSyntax) or colorSyntax
                    if hexColor:
                        linkColor = mathUtil.LtoI(long(hexColor, 0))
            inlineObject.bold = linkFmt.bold
            inlineObject.italic = linkFmt.italic
            inlineObject.underline = linkFmt.underline
            if linkFmt.bold:
                self.ParseTag('b')
            if linkFmt.italic:
                self.ParseTag('i')
            if linkFmt.underline:
                self.ParseTag('u')
            self._tagStack['color'].append(linkColor or linkFmt.color or self._defaultcolor)
        elif tag == u'/url' or tag == u'/a':
            self.EndInline('link')
            if self._tagStack['link']:
                closingLink = self._tagStack['link'].pop()
                if closingLink.bold:
                    self.ParseTag('/b')
                if closingLink.italic:
                    self.ParseTag('/i')
                if closingLink.underline:
                    self.ParseTag('/u')
                self.ParseTag('/color')
        elif tag == u'left':
            self.textalign = self.ALLEFT
        elif tag == u'right':
            self.textalign = self.ALRIGHT
        elif tag == u'center':
            self.textalign = self.ALCENTER
        elif tag.startswith(u'fontsize='):
            fs = int(_tag[9:])
            if 'fontsize' not in self._tagStack:
                self._tagStack['fontsize'] = []
            self._tagStack['fontsize'].append(fs)
        elif tag.startswith(u'letterspace='):
            ls = int(_tag[12:])
            if 'letterspace' not in self._tagStack:
                self._tagStack['letterspace'] = []
            self._tagStack['letterspace'].append(fs)
        elif tag.startswith(u'color='):
            color = uiutil.StringColorToHex(_tag[6:])
            if color is None:
                color = _tag[6:16]
                color = color.replace('#', '0x')
            col = mathUtil.LtoI(long(color, 0))
            self._tagStack['color'].append(col)
        elif tag.startswith(u'hint='):
            hint = self.GetTagStringValue('hint=', orgTag)
            inlineObject = self.StartInline('hint', hint)
            self._tagStack['hint'].append(inlineObject)
        elif tag == '/hint':
            self.EndInline('hint')
            if self._tagStack['hint']:
                self._tagStack['hint'].pop()
        elif tag in ('/color', '/fontsize', '/letterspace'):
            stackTag = tag[1:]
            if stackTag in self._tagStack and len(self._tagStack[stackTag]) > 1:
                self._tagStack[stackTag].pop()
        elif self.localizationErrorCheckEnabled:
            if tag.startswith('localized'):
                self._tagStack['localized'].append(tag)
            elif tag == '/localized':
                if self._tagStack['localized']:
                    self._tagStack['localized'].pop()



    def GetMouseOverUrl(self):
        return self._mouseOverUrl



    def StartInline(self, inlineType, data):
        inlineObject = uiutil.Bunch()
        inlineObject.inlineType = inlineType
        inlineObject.data = data
        measurer = self.GetMeasurer()
        inlineObject.inlineX = self.ReverseScaleDpi(measurer.cursorX)
        inlineObject.inlineXEnd = None
        self._inlineObjectsBuff.append(inlineObject)
        return inlineObject



    def EndInline(self, inlineType):
        if inlineType in self._tagStack and self._tagStack[inlineType]:
            inlineObject = self._tagStack[inlineType][-1]
            if inlineObject:
                measurer = self.GetMeasurer()
                inlineObject.inlineXEnd = self.ReverseScaleDpi(measurer.cursorX)



    def GetMenu(self):
        m = []
        if self._mouseOverUrl:
            m = uicls.BaseLink().GetLinkMenu(self, self._mouseOverUrl)
        m += [(localization.GetByLabel('/Carbon/UI/Controls/Common/Copy'), self.CopyText)]
        return m



    def CopyText(self):
        blue.pyos.SetClipboardData(self.text)



    def OnMouseEnter(self, *args):
        if self.mousehilite:
            self._hilite = 1
            self.Render((self._displayWidth, self._displayHeight))



    def OnMouseMove(self, *args):
        if not self._hilite:
            self.CheckInlines()



    def OnMouseExit(self, *args):
        if self.mousehilite:
            self._hilite = 0
            self.Render((self._displayWidth, self._displayHeight))
        else:
            self.CheckInlines()



    @bluepy.CCP_STATS_ZONE_METHOD
    def CheckInlines(self):
        inlineLinkObj = None
        inlineHintObj = None
        if self._inlineObjects and uicore.uilib.mouseOver == self:
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            (left, top, width, height,) = self.GetAbsolute()
            for inline in self._inlineObjects:
                startX = inline.inlineX
                endX = inline.inlineXEnd
                startY = inline.inlineY
                endY = startY + inline.inlineHeight
                if left + startX < mouseX < left + endX and top + startY < mouseY < top + endY:
                    if inline.inlineType == 'link':
                        inlineLinkObj = inline
                    elif inline.inlineType == 'hint':
                        inlineHintObj = inline

        self._resolvingInlineHint = True
        mouseOverUrl = None
        inlineHint = None
        if inlineLinkObj:
            mouseOverUrl = inlineLinkObj.url
            if inlineLinkObj.alt:
                inlineHint = inlineLinkObj.alt
            else:
                standardHint = uicls.BaseLink().GetStandardLinkHint(mouseOverUrl)
                if standardHint:
                    inlineHint = standardHint
        if not inlineHint and inlineHintObj:
            inlineHint = inlineHintObj.data
        hint = inlineHint or getattr(self, '_objectHint', None)
        if hint != self.hint:
            self.hint = hint
            uicore.CheckHint()
        self._resolvingInlineHint = False
        if mouseOverUrl != self._mouseOverUrl:
            self._mouseOverUrl = mouseOverUrl
            self.Layout()



    def GetStandardLinkHint(self, url):
        return None



    def OnClick(self, *args):
        if self._mouseOverUrl:
            uicls.BaseLink().ClickLink(self, self._mouseOverUrl.replace('&amp;', '&'))



    def Encode(self, text):
        return text.replace(u'&gt;', u'>').replace(u'&lt;', u'<').replace(u'&amp;', u'&').replace(u'&AMP;', u'&').replace(u'&GT;', u'>').replace(u'&LT;', u'<')



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



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetTagStringValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            tagBegin = tagstring[(start + len(tagtofind)):]
            for checkQuote in ['"', "'"]:
                if tagBegin.startswith(checkQuote):
                    end = tagBegin.find(checkQuote, 1)
                    if end != -1:
                        return tagBegin[1:end]




    @bluepy.CCP_STATS_ZONE_METHOD
    def GetTagValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            end = tagstring.find(' ', start)
            if end == start:
                end = tagstring.find(' ', start + 1)
            if end == -1:
                end = tagstring.find('>', start)
            if end == -1:
                end = len(tagstring)
            return tagstring[(start + len(tagtofind)):end]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetTextAndTags(self, text):
        if not text:
            return []
        tagStart = None
        tagSkip = 0
        charBuff = ''
        textOutsideTags = ''
        texts_or_tags = []
        if text.find('<') != -1:
            for (i, char,) in enumerate(text):
                if char == '<':
                    if tagStart is None:
                        if charBuff:
                            textOutsideTags += charBuff
                            texts_or_tags.append((False, self.Encode(charBuff)))
                            charBuff = ''
                        tagStart = i
                    else:
                        tagSkip += 1
                elif char == '>':
                    if not tagSkip:
                        texts_or_tags.append((True, text[tagStart:(i + 1)]))
                        tagStart = None
                    else:
                        tagSkip -= 1
                elif tagStart is None:
                    charBuff += char

        else:
            charBuff = text
        if charBuff:
            textOutsideTags += charBuff
            texts_or_tags.append((False, self.Encode(charBuff)))
        if self.singleline:
            return texts_or_tags
        wrapPoints = []
        boundaries = uiutil.FindTextBoundaries(self.Encode(textOutsideTags), regexObject=uiconst.LINE_BREAK_BOUNDARY_REGEX)
        for boundary in boundaries:
            if wrapPoints:
                wrapPoints.append(wrapPoints[-1] + len(boundary))
            else:
                wrapPoints.append(len(boundary))

        charBuff = ''
        charCounter = 0
        wraptexts_or_tags = []
        for (isTag, each,) in texts_or_tags:
            if isTag:
                if charBuff:
                    wraptexts_or_tags.append((False, charBuff))
                    charBuff = ''
                wraptexts_or_tags.append((True, each))
            else:
                for char in each:
                    charBuff += char
                    charCounter += 1
                    if charCounter in wrapPoints:
                        wraptexts_or_tags.append((False, charBuff))
                        charBuff = ''


        return wraptexts_or_tags



    @bluepy.CCP_STATS_ZONE_METHOD
    def SplitIntoLines(self, text):
        if not text:
            return []
        tagStart = None
        tagSkip = 0
        charBuff = ''
        texts_or_tags = []
        if text.find('<') != -1:
            for (i, char,) in enumerate(text):
                if char == '<':
                    if tagStart is None:
                        if charBuff:
                            texts_or_tags.append(charBuff)
                            charBuff = ''
                        tagStart = i
                    else:
                        tagSkip += 1
                elif char == '>':
                    if not tagSkip:
                        texts_or_tags.append(text[tagStart:(i + 1)])
                        tagStart = None
                    else:
                        tagSkip -= 1
                elif tagStart is None:
                    charBuff += char

        else:
            return [text]
        if charBuff:
            texts_or_tags.append(charBuff)
        ret = []
        buff = u''
        for each in texts_or_tags:
            if each == '<br>':
                if buff:
                    ret.append(buff)
                buff = u''
            else:
                buff += each

        if buff:
            ret.append(buff)
        return ret



    @classmethod
    def MeasureTextSize(cls, text, **customAttributes):
        if 'width' in customAttributes and customAttributes.get('singleline', False):
            raise RuntimeError('You cannot set both width and singleline when measuring textsize', '(MeasureTextSize)')
        customAttributes['text'] = text
        customAttributes['parent'] = None
        customAttributes['measuringText'] = True
        customAttributes['align'] = uiconst.TOPLEFT
        label = cls(**customAttributes)
        return (label.textwidth, label.textheight)




