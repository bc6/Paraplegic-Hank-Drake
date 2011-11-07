import util
import blue
import bluepy
import base
import uthread
import log
import fontConst
import uiconst
import uiutil
import uicls
import types
import trinity
import mathUtil
WORD_BOUNDARIES = [' ',
 '.',
 ',',
 ':',
 ';']
BOOLTAGS = [('b', 'bold'), ('i', 'italic'), ('u', 'underline')]
VALUETAGS = [('fontsize', 'defaultFontSize'),
 ('color', 'defaultFontColor'),
 ('font', 'defaultFont'),
 ('url', None)]
HTMLCONVERSION = {'fontsize': 'font size',
 '/fontsize': '/font',
 'color': 'font color',
 '/color': '/font',
 'url': 'a href',
 '/url': '/a'}
HTMLFONTTAG = {('fontsize', 'size'), ('color', 'color')}
ENDLINKCHARS = u' ,'
TEXTSIDEMARGIN = 6
TEXTLINEMARGIN = 1

class EditPlainTextCore(uicls.Scroll):
    __guid__ = 'uicls.EditPlainTextCore'
    default_name = 'edit_plaintext'
    default_align = uiconst.TOTOP
    default_height = 100
    default_maxLength = None
    default_readonly = False
    default_showattributepanel = 0
    default_setvalue = ''
    default_font = fontConst.DEFAULT_FONT
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontcolor = (1.0, 1.0, 1.0, 1.0)

    def ApplyAttributes(self, attributes):
        uicls.Scroll.ApplyAttributes(self, attributes)
        self.sr.scrollTimer = None
        self.keybuffer = []
        self._activeParams = None
        self._activeNode = None
        self._selecting = 0
        self._showCursor = True
        self._maxGlobalCursorIndex = 0
        self.sr.paragraphs = []
        self.globalSelectionRange = (None, None)
        self.globalSelectionInitpos = None
        self.globalCursorPos = 0
        self.OnReturn = None
        self.resizeTasklet = None
        self.updating = 0
        self.readonly = 0
        self.autoScrollToBottom = 0
        self.defaultFont = attributes.get('font', self.default_font)
        self.defaultFontSize = attributes.get('fontsize', self.default_fontsize)
        self.defaultFontColor = attributes.get('fontcolor', self.default_fontcolor)
        self.sr.content.GetMenu = self.GetMenuDelegate
        self.sr.content.OnKeyDown = self.OnKeyDown
        self.sr.content.OnDropData = self.OnContentDropData
        self.sr.content.OnMouseDown = self.OnMouseDown
        self.sr.content.OnMouseUp = self.OnMouseUp
        self.sr.content.cursor = uiconst.UICURSOR_IBEAM
        maxLength = attributes.get('maxLength', self.default_maxLength)
        self.SetMaxLength(maxLength)
        showattributepanel = attributes.get('showattributepanel', self.default_showattributepanel)
        if showattributepanel:
            self.ShowAttributePanel()
        setvalue = attributes.get('setvalue', self.default_setvalue)
        self.SetValue(setvalue)



    def CreateNode(self):
        entry = uicls.ScrollEntryNode(decoClass=uicls.SE_EditTextline, SelectionHandler=self, pos=0)
        return entry



    def Close(self, *args, **kwds):
        self.resizeTasklet = None
        uicls.Scroll.Close(self, *args, **kwds)



    def Prepare_Underlay_(self):
        self.sr.backgroundColorContainer = uicls.Container(name='backgroundColorContainer', parent=self)
        uicls.Scroll.Prepare_Underlay_(self)



    def ShowAttributePanel(self):
        if not self.readonly:
            self.sr.attribPanel = uicls.FontAttribPanel(align=uiconst.TOTOP, pos=(0, 0, 0, 22), parent=self, idx=0, state=uiconst.UI_PICKCHILDREN)



    def DoFontChange(self, *args):
        self.DoSizeUpdateDelayed()



    def IsLoading(self):
        return self._loading



    def SetValue(self, text, scrolltotop = 0, cursorPos = None, preformatted = 0, html = 1, fontColor = None):
        text = text or ''
        if not self.EnoughRoomFor(len(uiutil.StripTags(text))):
            return 
        self._activeParams = None
        newGS = uicore.font.GetGlyphString()
        self.sr.paragraphs = [newGS]
        self.LoadContent(contentList=[])
        self.UpdateGlyphString(newGS)
        self.SetSelectionRange(None, None, updateCursor=False)
        self.SetCursorPos(0)
        self.SetSelectionInitPos(self.globalCursorPos)
        for (tag, paramName,) in BOOLTAGS:
            setattr(self, 'tagStack_%s' % tag, [])

        for (paramName, defaultAttrName,) in VALUETAGS:
            setattr(self, 'tagStack_%s' % paramName, [])

        scrollTo = None
        if scrolltotop:
            scrollTo = 0.0
        elif self.autoScrollToBottom and self.GetScrollProportion() == 0.0:
            scrollTo = 1.0
        self.InsertText(text)
        if not self.readonly:
            self.SetCursorPos(cursorPos or 0)
        if scrollTo is not None:
            self.ScrollToProportion(scrollTo)



    @bluepy.CCP_STATS_ZONE_METHOD
    def InsertText(self, text):
        text = text or ''
        if not uiutil.StripTags(text):
            text = ''
        text = text.replace('\t', '    ').replace('\n', '').replace('\r', '<br>')
        lines = text.split('<br>')
        node = self.GetActiveNode()
        if node is None:
            return 
        self._fontTagStack = []
        initCursor = self.globalCursorPos
        advance = 0
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        for (lineIdx, line,) in enumerate(lines):
            text = line
            if line.find('<') > -1 and line.find('>') > -1:
                for each in line.split(u'>'):
                    texttag = each.split(u'<', 1)
                    if len(texttag) == 1:
                        (text, tag,) = (self.Encode(texttag[0]), None)
                    else:
                        (text, tag,) = (self.Encode(texttag[0]), texttag[1])
                    self.InsertToGlyphString(glyphString, self.GetFontParams(), text, stackCursorIndex)
                    stackCursorIndex += len(text)
                    advance += len(text)
                    if tag:
                        self.ParseTag(tag)

            else:
                text = self.Encode(text)
                self.InsertToGlyphString(glyphString, self.GetFontParams(), text, stackCursorIndex)
                stackCursorIndex += len(text)
                advance += len(text)
            self.UpdateGlyphString(glyphString, 0, 0)
            if lineIdx != len(lines) - 1:
                newGS = uicore.font.GetGlyphString()
                newGS += glyphString[stackCursorIndex:]
                glyphString.FlushFromIndex(stackCursorIndex)
                self.UpdateGlyphString(glyphString)
                self.InsertNewGlyphString(newGS, glyphString)
                self.SetCursorPos(self.globalCursorPos + 1, updateActiveParams=False)
                glyphString = newGS
                stackCursorIndex = len(newGS)
                advance += 1

        self.UpdatePosition()
        self.SetCursorPos(initCursor + advance)


    SetText = SetValue

    def Encode(self, text):
        return text.replace(u'&gt;', u'>').replace(u'&lt;', u'<').replace(u'&amp;', u'&').replace(u'&GT;', u'>').replace(u'&LT;', u'<')



    def Decode(self, text):
        return text.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')



    def ParseTag(self, tag):
        orgtag = tag
        tag = tag.replace('"', '')
        tag = tag.replace("'", '')
        tag = tag.lower()
        if tag.startswith('font '):
            fontcolor = self.GetTagValue('color=', tag)
            if fontcolor:
                self.ParseTag('color=' + fontcolor)
            fontsize = self.GetTagValue('size=', tag)
            if fontsize:
                self.ParseTag('fontsize=' + fontsize)
            tagStack = getattr(self, 'tagStack_font', [])
            tagStack.append(tag)
            setattr(self, 'tagStack_font', tagStack)
            return 
        if tag.startswith('/font'):
            tagStack = getattr(self, 'tagStack_font', [])
            if tagStack:
                closeFontTag = tagStack.pop()
                fontcolor = self.GetTagValue('color=', closeFontTag)
                if fontcolor:
                    self.ParseTag('/color')
                fontsize = self.GetTagValue('size=', closeFontTag)
                if fontsize:
                    self.ParseTag('/fontsize')
            return 
        tag = tag.replace('a href=', 'url=').replace('/a', '/url')
        if tag[0] == '/':
            stackName = tag[1:]
        elif '=' in tag:
            stackName = tag.split('=')[0]
        else:
            stackName = tag
        tagStack = getattr(self, 'tagStack_%s' % stackName, [])
        if tag[0] == '/':
            if len(tagStack):
                tagStack.pop()
        elif tag.startswith(u'color='):
            colorSyntax = tag[6:]
            color = uiutil.StringColorToHex(colorSyntax)
            if color is None:
                hexColor = colorSyntax.replace('#', '0x')
                try:
                    col = mathUtil.LtoI(long(hexColor, 0))
                    tagStack.append(col)
                except ValueError:
                    try:
                        (r, g, b, a,) = self.defaultFontColor
                        defaultHex = '0x%02x%02x%02x%02x' % (a * 255,
                         r * 255,
                         g * 255,
                         b * 255)
                        col = mathUtil.LtoI(long(defaultHex, 0))
                        tagStack.append(col)
                    except ValueError:
                        tagStack.append(-1)
        elif '=' in tag:
            value = orgtag.split('=')
            value = '='.join(value[1:])
            if value[0] == '"':
                value = value[1:]
            if value[-1] == '"':
                value = value[:-1]
            try:
                addVal = int(value)
            except:
                addVal = value
            tagStack.append(addVal)
        else:
            tagStack.append(1)
        setattr(self, 'tagStack_%s' % stackName, tagStack)



    def GetTagValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            end = tagstring.find(' ', start)
            if end == -1:
                end = tagstring.find('>', start)
            if end == -1:
                end = len(tagstring)
            return tagstring[(start + len(tagtofind)):end]



    def GetColorSyntax(self, color, html):
        if type(color) is types.IntType:
            c = trinity.TriColor()
            c.FromInt(color)
            color = (c.r,
             c.g,
             c.b,
             c.a)
        else:
            color = color
        if html:
            colorString = '"#%02x%02x%02x%02x"' % (color[3] * 255,
             color[0] * 255,
             color[1] * 255,
             color[2] * 255)
        else:
            colorString = '0x%02x%02x%02x%02x' % (color[3] * 255,
             color[0] * 255,
             color[1] * 255,
             color[2] * 255)
        return colorString



    def GetValue(self, html = 1):

        def FormatValue(value, html):
            if html:
                return '"%s"' % value
            return value



        def FormatTag(fmttag, html):
            if html and fmttag in HTMLCONVERSION:
                return HTMLCONVERSION[fmttag]
            return fmttag


        defaultColorValue = self.GetColorSyntax(self.defaultFontColor, html)
        defaultFontSizeValue = FormatValue(self.defaultFontSize, html)
        defaultHtmlFontTagCombined = '<font size=%s color=%s>' % (defaultFontSizeValue, defaultColorValue)
        defaultAdded = False
        tagStacks = {}
        for (tag, defaultAttrName,) in VALUETAGS:
            if defaultAttrName:
                tagStacks[tag] = [getattr(self, defaultAttrName, None)]
            else:
                tagStacks[tag] = [None]

        tagStacks['fontCombined'] = [defaultHtmlFontTagCombined]
        for (tag, paramName,) in BOOLTAGS:
            tagStacks[tag] = [False]

        lastParams = None
        retString = ''
        for glyphString in self.sr.paragraphs:
            for charData in glyphString:
                (advance, align, color, sbit, char, asc, des, params,) = charData
                if lastParams is not params:
                    lastParams = params
                    for (tag, paramName,) in BOOLTAGS:
                        tagStack = tagStacks[tag]
                        paramValue = params.get(paramName, False)
                        if paramValue != tagStack[-1]:
                            if len(tagStack) > 1:
                                retString += '<%s>' % FormatTag('/%s' % tag, html)
                                tagStack.pop()

                    if html:
                        htmlFontTagCombined = ''
                        for (fmtTag, htmlTag,) in HTMLFONTTAG:
                            paramValue = params.Get(fmtTag, None)
                            if paramValue:
                                if fmtTag == 'color':
                                    paramValue = self.GetColorSyntax(paramValue, html)
                                else:
                                    paramValue = FormatValue(paramValue, html)
                                if htmlFontTagCombined:
                                    htmlFontTagCombined += ' '
                                htmlFontTagCombined += '%s=%s' % (htmlTag, paramValue)

                        if htmlFontTagCombined:
                            htmlFontTagCombined = '<font %s>' % htmlFontTagCombined
                            currentStack = tagStacks['fontCombined']
                            if currentStack[-1] != htmlFontTagCombined:
                                if not defaultAdded:
                                    retString = defaultHtmlFontTagCombined + retString + '</font>'
                                    defaultAdded = True
                                if len(currentStack) > 1:
                                    retString += '</font>'
                                    currentStack.pop()
                                currentStack.append(htmlFontTagCombined)
                                retString += htmlFontTagCombined
                    for (paramName, defaultAttrName,) in VALUETAGS:
                        if html and paramName in ('font', 'color', 'fontsize'):
                            continue
                        currentStack = tagStacks[paramName]
                        currentStackValue = currentStack[-1]
                        currentParamValue = params.get(paramName, None)
                        if currentParamValue != currentStackValue:
                            if len(currentStack) > 1:
                                retString += '<%s>' % FormatTag('/%s' % paramName, html)
                                currentStack.pop()
                            if currentParamValue:
                                if paramName == 'color':
                                    formattedValue = self.GetColorSyntax(currentParamValue, html)
                                else:
                                    formattedValue = FormatValue(currentParamValue, html)
                                retString += '<%s=%s>' % (FormatTag(paramName, html), formattedValue)
                                currentStack.append(currentParamValue)

                    for (tag, paramName,) in BOOLTAGS:
                        tagStack = tagStacks[tag]
                        paramValue = params.get(paramName, False)
                        if paramValue != tagStack[-1] and paramValue:
                            retString += '<%s>' % FormatTag('%s' % tag, html)
                            tagStack.append(True)

                retString += self.Decode(char)

            if glyphString is not self.sr.paragraphs[-1]:
                retString += '<br>'

        for (tag, paramName,) in BOOLTAGS:
            tagStack = tagStacks[tag]
            while len(tagStack) > 1:
                retString += '<%s>' % FormatTag('/%s' % tag, html)
                tagStack.pop()


        for (paramName, defaultAttrName,) in VALUETAGS:
            tagStack = tagStacks[paramName]
            while len(tagStack) > 1:
                retString += '<%s>' % FormatTag('/%s' % paramName, html)
                tagStack.pop()


        if html:
            currentStack = tagStacks['fontCombined']
            while len(currentStack) > 1:
                currentStack.pop()
                retString += '</font>'

        if not uiutil.StripTags(retString):
            return ''
        return retString



    def SetDefaultFontSize(self, size):
        for glyphString in self.sr.paragraphs:
            for charData in glyphString:
                (advance, align, color, sbit, char, asc, des, params,) = charData
                if params.fontsize == self.defaultFontSize:
                    params.fontsize = size

            self.ReloadGlyphString(glyphString)
            self.UpdateGlyphString(glyphString)

        self.SetCursorPos(self.globalCursorPos)
        if self._activeParams:
            self._activeParams.fontsize = size
        self.defaultFontSize = size



    def SetMaxLength(self, value):
        self.maxletters = value



    def SetFocus(self, *args, **kw):
        uicls.Scroll.SetFocus(self, *args, **kw)
        if uicore.registry.GetFocus() is self:
            return 
        if not self.readonly:
            sm.GetService('ime').SetFocus(self)
        self.RefreshCursorAndSelection()
        if hasattr(self, 'RegisterFocus'):
            self.RegisterFocus(self)



    def OnKillFocus(self, *args, **kw):
        uicls.Scroll.OnKillFocus(self, *args, **kw)
        if not self.readonly:
            sm.GetService('ime').KillFocus(self)
        uthread.new(self.RefreshCursorAndSelection)
        uthread.new(self.OnFocusLost, self)



    def OnFocusLost(self, *args):
        pass



    def UpdateAttributePanel(self):
        params = self._activeParams
        if self.sr.attribPanel is not None:
            if type(params.color) is types.IntType:
                c = trinity.TriColor()
                c.FromInt(params.color)
                color = (c.r, c.g, c.b)
            else:
                color = params.color
            self.sr.attribPanel.AttribStateChange(params.bold, params.italic, params.underline, params.fontsize, color, params.url)



    def GetMenuDelegate(self, node = None):
        m = [(mls.UI_CMD_COPYALL, self.CopyAll)]
        if self.HasSelection():
            m.append((mls.UI_CMD_COPYSELECTED, self.Copy))
            if not self.readonly:
                m.append((mls.UI_CMD_CUTSELECTED, self.Cut))
        clipboard = uiutil.GetClipboardData()
        if clipboard and not self.readonly:
            m.append((mls.UI_CMD_PASTE, self.Paste, (clipboard,)))
        return m



    def SelectLineUnderCursor(self):
        node = self.GetActiveNode()
        (fromIdx, toIdx,) = (node.startCursorIndex, node.endCursorIndex)
        self.SetSelectionRange(fromIdx, toIdx, updateCursor=False)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)



    def FindWordBoundariesFromGlobalCursor(self):
        text = ''.join(self.words)
        boundaries = uiutil.FindTextBoundaries(text, regexObject=uiconst.WORD_BOUNDARY_REGEX)
        totalWordLength = 0
        for (i, wordLength,) in enumerate([ len(word) for word in boundaries ]):
            totalWordLength += wordLength
            if self.globalCursorPos < totalWordLength:
                break

        leftOffset = totalWordLength - wordLength - self.globalCursorPos
        rightOffset = totalWordLength - self.globalCursorPos
        return (leftOffset, rightOffset, i)



    def SelectWordUnderCursor(self):
        (leftBound, rightBound, wordIndex,) = self.FindWordBoundariesFromGlobalCursor()
        (fromIdx, toIdx,) = (self.globalCursorPos + leftBound, self.globalCursorPos + rightBound)
        self.SetSelectionRange(fromIdx, toIdx, updateCursor=False)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)



    def SetSelectionInitPos(self, globalIndex):
        self.globalSelectionInitpos = globalIndex



    def SetSelectionRange(self, fromCharIndex, toCharIndex, updateCursor = True):
        if fromCharIndex == toCharIndex:
            (fromCharIndex, toCharIndex,) = (None, None)
        self.globalSelectionRange = (fromCharIndex, toCharIndex)
        if fromCharIndex is None or toCharIndex is None:
            self.SetSelectionInitPos(self.globalCursorPos)
        if updateCursor:
            self.RefreshCursorAndSelection()



    def SetCursorPos(self, globalIndex, updateActiveParams = True):
        if globalIndex == -1:
            globalIndex = self._maxGlobalCursorIndex
        maxIndex = 0
        for gs in self.sr.paragraphs:
            maxIndex += len(gs) + 1

        maxIndex -= 1
        self._maxGlobalCursorIndex = max(0, maxIndex)
        self.globalCursorPos = max(0, min(self._maxGlobalCursorIndex, globalIndex))
        self.RefreshCursorAndSelection(updateActiveParams=updateActiveParams)



    @bluepy.CCP_STATS_ZONE_METHOD
    def RefreshCursorAndSelection(self, updateActiveParams = True):
        if self.dead:
            return 
        i = 0
        stackShift = 0
        lastGlyphString = None
        globalCursorIndex = 0
        stackCursor = 0
        (fromIdx, toIdx,) = self.globalSelectionRange
        for node in self.GetNodes():
            if not issubclass(node.decoClass, uicls.SE_EditTextlineCore):
                continue
            if node._endIndex is None:
                letterCountInLine = 0
            else:
                letterCountInLine = node._endIndex - node._startIndex
            node.letterCountInLine = letterCountInLine
            if lastGlyphString is not None and lastGlyphString is not node.glyphString:
                stackShift += 1
                stackCursor = 0
            node.startCursorIndex = globalCursorIndex + stackShift
            node.endCursorIndex = node.startCursorIndex + letterCountInLine
            node.stackCursorIndex = stackCursor
            globalCursorIndex += letterCountInLine
            stackCursor += letterCountInLine
            lastGlyphString = node.glyphString
            if updateActiveParams and node.startCursorIndex <= self.globalCursorPos <= node.endCursorIndex:
                self._activeNode = node
                stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
                self._activeParams = self.GetPriorParams(node.glyphString, stackCursorIndex) or self.GetFontParams()
                self._activeParams = self._activeParams.Copy()
                self.UpdateAttributePanel()
            if not self.readonly:
                if node.globalCursorPos is not None:
                    node.globalCursorPos = None
                    if node.panel:
                        node.panel.UpdateCursor()
            if fromIdx is None or not (fromIdx <= node.startCursorIndex <= toIdx or node.startCursorIndex <= fromIdx <= node.endCursorIndex):
                node.selectionStartIndex = None
                node.selectionEndIndex = None
            else:
                node.selectionStartIndex = max(0, fromIdx)
                node.selectionEndIndex = max(0, toIdx)
            if node.panel and hasattr(node.panel, 'UpdateSelectionHilite'):
                node.panel.UpdateSelectionHilite()
            i += 1

        if not self.readonly:
            node = self.GetActiveNode()
            if node:
                node.globalCursorPos = self.globalCursorPos
                if node.panel:
                    node.panel.UpdateCursor()



    def GetActiveNode(self):
        ret = getattr(self, '_activeNode', None)
        if ret is None:
            ret = self.sr.nodes[0]
        return ret



    def GetSelectedText(self):
        ret = ''
        selectedData = self.GetSeletedCharData()
        if not selectedData:
            return ret
        for (glyphString, gsData,) in selectedData:
            for (charIdx, (advance, align, color, sbit, char, asc, des, params,),) in gsData:
                ret += char

            ret += '\r\n'

        return ret[:-2]



    def GetAllText(self, newLineStr = '\r\n'):
        ret = ''
        for glyphString in self.sr.paragraphs:
            for (advance, align, color, sbit, char, asc, des, params,) in glyphString:
                ret += char

            ret += newLineStr

        return ret[:(-len(newLineStr))]



    def PrintGS(self, gs):
        t = ''
        for (advance, align, color, sbit, char, asc, des, params,) in gs:
            t += ' %s %s' % (params.italic, char)

        print 'GS',
        print repr(t)



    def OnMouseUpDelegate(self, _node, *args):
        self._selecting = 0
        self.sr.scrollTimer = None
        self.SetCursorPos(self.globalCursorPos)



    def OnMouseDownDelegate(self, _node, *args):
        self._selecting = 1
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
        self.sr.scrollTimer = base.AutoTimer(100, self.ScrollTimer)



    def SetCursorFromNodeAndMousePos(self, node):
        if node.panel is not None:
            internalPos = node.panel.GetInternalCursorPos()
            self.SetCursorPos(node.startCursorIndex + internalPos)
        else:
            self.SetCursorPos(-1)



    def GetLastTextline(self):
        totalLines = len(self.sr.content.children)
        for i in xrange(totalLines):
            nodePanel = self.sr.content.children[(totalLines - i - 1)]
            if isinstance(nodePanel, uicls.SE_EditTextlineCore):
                return nodePanel




    def CrawlForTextline(self, mo):
        if isinstance(mo, uicls.SE_EditTextlineCore):
            return mo
        if mo.parent:
            if mo.parent is uicore.desktop:
                return None
            return self.CrawlForTextline(mo.parent)



    def ScrollTimer(self):
        if not self._selecting or self.globalSelectionInitpos is None:
            self.sr.scrollTimer = None
            return 
        if not uicore.uilib.leftbtn:
            self.sr.scrollTimer = None
            self._selecting = 0
            return 
        toAffect = None
        if uiutil.IsUnder(uicore.uilib.mouseOver, self):
            toAffect = self.CrawlForTextline(uicore.uilib.mouseOver)
        if toAffect is None:
            toAffect = self.GetLineAtCursorLevel()
        (aL, aT, aW, aH,) = self.GetAbsolute()
        if uicore.uilib.y < aT:
            self.Scroll(1)
        elif uicore.uilib.y > aT + aH:
            self.Scroll(-1)
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



    def GetLineAtCursorLevel(self):
        (aL, aT, aW, aH,) = self.GetAbsolute()
        if uicore.uilib.y < aT:
            return self.sr.content.children[0]
        if uicore.uilib.y > aT + aH:
            return self.sr.content.children[-1]
        each = None
        for each in self.sr.content.children:
            (l, t, w, h,) = each.GetAbsolute()
            if t < uicore.uilib.y <= t + h:
                return each

        return each



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
        node = self.GetActiveNode()
        self.OnDropDataDelegate(node, nodes)



    def OnDropData(self, dragObj, nodes):
        node = self.GetActiveNode()
        self.OnDropDataDelegate(node, nodes)



    def OnMouseUp(self, *args):
        self._selecting = 0
        self.sr.scrollTimer = None



    def OnMouseDown(self, button, *args):
        if button != uiconst.MOUSELEFT:
            return 
        if len(self.sr.content.children):
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            lastEntry = self.sr.content.children[-1]
            (l, t, w, h,) = lastEntry.GetAbsolute()
            if uicore.uilib.y > t + h:
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    self.SetSelectionRange(selectionStartIndex or self.globalCursorPos, self._maxGlobalCursorIndex, updateCursor=False)
                else:
                    self.SetSelectionRange(None, None, updateCursor=False)
                    self.SetSelectionInitPos(self._maxGlobalCursorIndex)
                self.SetCursorPos(self._maxGlobalCursorIndex)
        self._selecting = 1



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
            (preFromIdx, preToIdx,) = self.globalSelectionRange
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if not shift:
                self.SetSelectionRange(None, None)
            else:
                (preFromIdx, preToIdx,) = (None, None)
            node = self.GetActiveNode()
            newCursorPos = self.globalCursorPos
            if vkey == uiconst.VK_LEFT:
                if ctrl:
                    (leftBound, rightBound, wordIndex,) = self.FindWordBoundariesFromGlobalCursor()
                    jumpVal = leftBound
                    if not jumpVal and wordIndex:
                        jumpVal -= len(self.words[(wordIndex - 1)])
                    newCursorPos = self.globalCursorPos + jumpVal
                else:
                    (fromIdx, toIdx,) = self.globalSelectionRange
                    if preFromIdx is not None and preToIdx is not None:
                        newCursorPos = min(preFromIdx, preToIdx)
                    else:
                        newCursorPos = max(0, self.globalCursorPos - 1)
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_RIGHT:
                if ctrl:
                    (leftBound, rightBound, wordIndex,) = self.FindWordBoundariesFromGlobalCursor()
                    jumpVal = rightBound
                    if not jumpVal and wordIndex < len(self.words) - 1:
                        jumpVal += len(self.words[(wordIndex + 1)])
                    newCursorPos = self.globalCursorPos + jumpVal
                elif preFromIdx is not None and preToIdx is not None:
                    newCursorPos = max(preFromIdx, preToIdx)
                else:
                    newCursorPos = self.globalCursorPos + 1
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_UP:
                if not ctrl:
                    self.OnUp()
                    posInLine = self.globalCursorPos - node.startCursorIndex
                    if node.idx > 0:
                        nodeAbove = self.GetNode(node.idx - 1)
                        if nodeAbove and nodeAbove.endCursorIndex is not None:
                            newCursorPos = min(nodeAbove.endCursorIndex, nodeAbove.startCursorIndex + posInLine)
                        else:
                            newCursorPos = 0
                        if shift:
                            (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                            if selectionStartIndex is None:
                                self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                            elif self.globalCursorPos == selectionStartIndex:
                                self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                            else:
                                self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_DOWN:
                if not ctrl:
                    self.OnDown()
                    posInLine = self.globalCursorPos - node.startCursorIndex
                    nodeBelow = self.GetNode(node.idx + 1)
                    if nodeBelow and nodeBelow.startCursorIndex is not None:
                        newCursorPos = nodeBelow.startCursorIndex + min(posInLine, nodeBelow.letterCountInLine)
                    else:
                        newCursorPos = self._maxGlobalCursorIndex
                    if shift:
                        (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                        if selectionStartIndex is None:
                            self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                        elif self.globalCursorPos == selectionStartIndex:
                            self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                        else:
                            self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_HOME:
                self.OnHome()
                if ctrl:
                    newCursorPos = 0
                else:
                    newCursorPos = node.startCursorIndex
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
            elif vkey == uiconst.VK_END:
                self.OnEnd()
                if ctrl:
                    newCursorPos = self._maxGlobalCursorIndex
                else:
                    newCursorPos = node.endCursorIndex
                if shift:
                    (selectionStartIndex, selectionEndIndex,) = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            self.SetCursorPos(newCursorPos)
            node = self.GetActiveNode()
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



    def ReadOnly(self, *args):
        self.readonly = True



    def Editable(self, *args):
        self.readonly = False



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
                self.keybuffer.pop(-1)
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
        all = self.GetAllText()
        if all:
            blue.pyos.SetClipboardData(all)



    def Cut(self):
        self.Copy()
        if not self.readonly:
            self.DeleteSelected()



    def EnoughRoomFor(self, textLen):
        if not self.maxletters:
            return True
        currentLen = len(self.GetAllText())
        if currentLen + textLen <= self.maxletters:
            return True
        return textLen <= self.RoomLeft()



    def RoomLeft(self):
        if not self.maxletters:
            return None
        currentLen = len(self.GetAllText())
        return self.maxletters + len(self.GetSelectedText()) - currentLen



    def Paste(self, text):
        if self.ValidatePaste:
            text = self.ValidatePaste(text)
        roomLeft = self.RoomLeft()
        if roomLeft is not None and roomLeft < len(text):
            uicore.Message('uiwarning03')
            text = text[:roomLeft]
        if self.readonly or not text:
            return 
        self.DeleteSelected()
        self.InsertText(text)
        node = self.GetActiveNode()
        if node:
            self.ShowNodeIdx(node.idx)
        uicore.registry.SetFocus(self)



    def ValidatePaste(self, text):
        return text



    def GetFontParams(self):
        std = uicore.font.GetParams()
        if self._activeParams:
            std.color = self._activeParams.color
            std.fontsize = self._activeParams.fontsize
        else:
            std.color = self.defaultFontColor
            std.fontsize = self.defaultFontSize
        std.font = self.defaultFont
        for (tag, paramName,) in BOOLTAGS:
            tagStack = getattr(self, 'tagStack_%s' % tag, [])
            std.Set(paramName, bool(tagStack))

        for (paramName, defaultAttrName,) in VALUETAGS:
            tagStack = getattr(self, 'tagStack_%s' % paramName, [])
            if tagStack:
                std.Set(paramName, tagStack[-1])

        return std



    @bluepy.CCP_STATS_ZONE_METHOD
    def CheckLineWrap(self, glyphString):
        text = ''.join([ charData[4] for charData in glyphString ])
        if not text:
            return [(0, 0, 0, 12, 12)]
        self.words = uiutil.FindTextBoundaries(self.GetAllText(newLineStr='\n'), regexObject=uiconst.WORD_BOUNDARY_REGEX)
        words = uiutil.FindTextBoundaries(text, regexObject=uiconst.LINE_BREAK_BOUNDARY_REGEX)
        wordBoundaries = []
        wordWidths = []
        wordStartIndex = 0
        for wordLength in [ len(word) for word in words ]:
            wordBoundaries.append(wordStartIndex)
            wordWidths.append(sum([ glyphString[i][0] for i in xrange(wordStartIndex, wordStartIndex + wordLength) ]))
            wordStartIndex += wordLength

        maxWidth = self.GetContentWidth() - TEXTSIDEMARGIN * 2
        if maxWidth < 0:
            return [(0, 0, 0, 12, 12)]
        while max(wordWidths) > maxWidth:
            for (wordIndex, wordWidth,) in enumerate(wordWidths):
                if wordWidth > maxWidth:
                    splitWidth = 0
                    for letterIndex in xrange(len(words[wordIndex])):
                        wordStartIndex = wordBoundaries[wordIndex]
                        letterPixelWidth = glyphString[(wordStartIndex + letterIndex)][0]
                        splitWidth += letterPixelWidth
                        if splitWidth > maxWidth:
                            splitWord1 = words[wordIndex][:letterIndex]
                            splitWord2 = words[wordIndex][letterIndex:]
                            splitWordLength1 = splitWidth - letterPixelWidth
                            splitWordLength2 = wordWidth - splitWordLength1
                            wordBoundaries.insert(wordIndex + 1, wordStartIndex + len(splitWord1))
                            wordWidths[wordIndex] = splitWordLength1
                            wordWidths.insert(wordIndex + 1, splitWordLength2)
                            words[wordIndex] = splitWord1
                            words.insert(wordIndex + 1, splitWord2)
                            break



        ret = []
        lineWidth = lineStartIndex = lineEndIndex = 0
        for (wordIndex, word,) in enumerate(words):
            lineWidth += wordWidths[wordIndex]
            wordStartIndex = wordBoundaries[wordIndex]
            lineEndIndex = wordStartIndex + len(word)
            if wordIndex + 1 < len(words) and lineWidth + wordWidths[(wordIndex + 1)] > maxWidth:
                maxAsc = max([ glyphString[i][5] for i in xrange(lineStartIndex, lineEndIndex) ])
                maxDes = max([ glyphString[i][5] - glyphString[i][6] for i in xrange(lineStartIndex, lineEndIndex) ])
                ret.append((lineStartIndex,
                 lineEndIndex,
                 lineWidth,
                 maxAsc,
                 maxDes))
                lineWidth = 0
                lineStartIndex = lineEndIndex

        if lineStartIndex < lineEndIndex:
            maxAsc = max([ glyphString[i][5] for i in xrange(lineStartIndex, lineEndIndex) ])
            maxDes = max([ glyphString[i][5] - glyphString[i][6] for i in xrange(lineStartIndex, lineEndIndex) ])
            ret.append((lineStartIndex,
             lineEndIndex,
             lineWidth,
             maxAsc,
             maxDes))
        return ret



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateGlyphString(self, glyphString, advance = None, stackCursorIndex = None):
        allNodesInStack = []
        for _node in self.GetNodes():
            if _node.glyphString is glyphString:
                allNodesInStack.append(_node)

        lineIndexes = self.CheckLineWrap(glyphString)
        if stackCursorIndex is not None:
            r = max(len(allNodesInStack), len(lineIndexes))
            if allNodesInStack:
                insertAt = allNodesInStack[0].idx
            else:
                insertAt = 0
            lenNew = len(lineIndexes)
            lenOld = len(allNodesInStack)
            if lenNew < lenOld:
                rem = allNodesInStack[(-(lenOld - lenNew)):]
                self.RemoveNodesRaw(rem)
            elif lenNew > lenOld:
                newNodes = []
                if allNodesInStack:
                    startAt = allNodesInStack[-1].idx + 1
                else:
                    startAt = 0
                for x in xrange(lenNew - lenOld):
                    newNode = self.CreateNode()
                    newNode.glyphString = glyphString
                    newNode._startIndex = 0
                    newNode._endIndex = 0
                    newNode._width = 0
                    newNode._baseHeight = 12
                    newNode._baseLine = 12
                    newNodes.append(newNode)

                self.InsertNodesRaw(startAt, newNodes)
                allNodesInStack += newNodes
            updateCount = 0
            for (i, lineData,) in enumerate(lineIndexes):
                old = allNodesInStack[i]
                (startIdx, endIdx, width, baseLine, baseHeight,) = lineData
                addAdv = 0
                if stackCursorIndex <= endIdx:
                    addAdv = advance
                if old._startIndex + addAdv != startIdx or old._endIndex + addAdv != endIdx:
                    doUpdate = True
                else:
                    doUpdate = False
                old._startIndex = startIdx
                old._endIndex = endIdx
                old._width = width
                old._baseHeight = baseHeight
                old._baseLine = baseLine
                if doUpdate:
                    if old.panel:
                        old.panel.Load(old)
                    updateCount += 1

        elif allNodesInStack:
            insertAt = allNodesInStack[0].idx
            self.RemoveNodesRaw(allNodesInStack)
        else:
            insertAt = 0
        newNodes = []
        for (startIdx, endIdx, width, baseLine, baseHeight,) in lineIndexes:
            newNode = self.CreateNode()
            newNode.glyphString = glyphString
            newNode._startIndex = startIdx
            newNode._endIndex = endIdx
            newNode._width = width
            newNode._baseHeight = baseHeight
            newNode._baseLine = baseLine
            newNodes.append(newNode)

        self.InsertNodesRaw(insertAt, newNodes)



    def InsertNewGlyphString(self, glyphString, afterGS):
        afterIdx = self.GetGlyphStringIndex(afterGS)
        self.sr.paragraphs.insert(afterIdx + 1, glyphString)
        allNodesInStack = []
        for _node in self.GetNodes():
            if _node.glyphString is afterGS:
                allNodesInStack.append(_node)

        insertAt = allNodesInStack[-1].idx + 1
        lineIndexes = self.CheckLineWrap(glyphString)
        newNodes = []
        for (startIdx, endIdx, width, baseLine, baseHeight,) in lineIndexes:
            newNode = self.CreateNode()
            newNode.glyphString = glyphString
            newNode._startIndex = startIdx
            newNode._endIndex = endIdx
            newNode._width = width
            newNode._baseHeight = baseHeight
            newNode._baseLine = baseLine
            newNodes.append(newNode)

        self.InsertNodesRaw(insertAt, newNodes)



    def RemoveGlyphString(self, glyphString):
        allNodesInStack = []
        for _node in self.GetNodes():
            if _node.glyphString is glyphString:
                allNodesInStack.append(_node)

        if allNodesInStack:
            self.RemoveNodesRaw(allNodesInStack)
        gsIdx = self.GetGlyphStringIndex(glyphString)
        if gsIdx is not None:
            del self.sr.paragraphs[gsIdx]



    def GetGlyphStringIndex(self, glyphString):
        for (glyphStringIndex, _glyphString,) in enumerate(self.sr.paragraphs):
            if _glyphString is glyphString:
                return glyphStringIndex




    @bluepy.CCP_STATS_ZONE_METHOD
    def Insert(self, char):
        if char not in (uiconst.VK_BACK, uiconst.VK_RETURN, 127) and not self.EnoughRoomFor(1):
            uicore.Message('uiwarning03')
            return 
        node = self.GetActiveNode()
        if node is None:
            return 
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        cursorAdvance = 0
        setParams = None
        if char == uiconst.VK_RETURN:
            newGS = uicore.font.GetGlyphString()
            newGS += glyphString[stackCursorIndex:]
            glyphString.FlushFromIndex(stackCursorIndex)
            self.UpdateGlyphString(glyphString)
            self.InsertNewGlyphString(newGS, glyphString)
            cursorAdvance = 1
        elif char == 127:
            if stackCursorIndex == len(glyphString):
                if self.sr.paragraphs[-1] is not glyphString:
                    idx = self.GetGlyphStringIndex(glyphString)
                    glyphStringBelow = self.sr.paragraphs[(idx + 1)]
                    glyphString += glyphStringBelow
                    self.UpdateGlyphString(glyphString)
                    self.RemoveGlyphString(glyphStringBelow)
            else:
                glyphString.Remove(stackCursorIndex, stackCursorIndex + 1)
                self.UpdateGlyphString(glyphString, -1, stackCursorIndex + 1)
        elif char == uiconst.VK_BACK:
            setParams = self.GetPriorParams(node.glyphString, stackCursorIndex)
            if stackCursorIndex > 0:
                glyphString.Remove(stackCursorIndex - 1, stackCursorIndex)
                self.UpdateGlyphString(glyphString, -1, stackCursorIndex - 1)
                cursorAdvance = -1
            elif glyphStringIndex > 0:
                glyphStringAbove = self.sr.paragraphs[(glyphStringIndex - 1)]
                glyphStringAbove += glyphString
                self.RemoveGlyphString(glyphString)
                self.UpdateGlyphString(glyphStringAbove)
                cursorAdvance = -1
        else:
            currentParams = self._activeParams.Copy()
            unichar = unichr(char)
            if currentParams.url:
                if unichar in ENDLINKCHARS:
                    nextParams = self.GetNextParams(glyphString, stackCursorIndex)
                    if not nextParams or nextParams.url != currentParams.url:
                        currentParams.url = None
                elif stackCursorIndex == 0:
                    currentParams.url = None
            self.InsertToGlyphString(glyphString, currentParams, unichar, stackCursorIndex)
            self.UpdateGlyphString(glyphString, advance=1, stackCursorIndex=stackCursorIndex)
            cursorAdvance = 1
        self.OnChange()
        self.SetCursorPos(self.globalCursorPos + cursorAdvance)
        self.SetSelectionInitPos(self.globalCursorPos)
        node = self.GetActiveNode()
        if node:
            self.ShowNodeIdx(node.idx)
        if setParams:
            self._activeParams = setParams.Copy()
            self.UpdateAttributePanel()



    def GetPriorParams(self, glyphString, stackCursorIndex):
        if len(glyphString):
            paramsInFront = glyphString[max(0, min(len(glyphString) - 1, stackCursorIndex - 1))][-1]
            return paramsInFront
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        while glyphStringIndex > 0:
            glyphString = self.sr.paragraphs[(glyphStringIndex - 1)]
            if len(glyphString):
                return glyphString[-1][-1]
            glyphStringIndex = self.GetGlyphStringIndex(glyphString)




    def GetNextParams(self, glyphString, stackCursorIndex):
        if len(glyphString) > stackCursorIndex:
            paramsBehind = glyphString[stackCursorIndex][-1]
            return paramsBehind
        while glyphString is not self.sr.paragraphs[-1]:
            glyphStringIndex = self.GetGlyphStringIndex(glyphString)
            glyphString = self.sr.paragraphs[(glyphStringIndex + 1)]
            if len(glyphString):
                return glyphString[0][-1]




    def ReloadGlyphString(self, glyphString):
        data = [ (params, char) for (advance, align, color, sbit, char, asc, des, params,) in glyphString ]
        del glyphString[:]
        for (idx, (params, char,),) in enumerate(data):
            self.InsertToGlyphString(glyphString, params, char, idx)




    def RemoveFromGlyphString(self, glyphString, startIdx, endIdx):
        for i in xrange(startIdx, endIdx):
            glyphString.pop(startIdx)




    @bluepy.CCP_STATS_ZONE_METHOD
    def InsertToGlyphString(self, glyphString, params, text, idx):
        letterspace = params.letterspace or 0
        color = params.color or -1
        if type(color) != types.IntType:
            tricol = trinity.TriColor(*color)
            color = tricol.AsInt()
        last = (None, 0)
        lastURange = -1
        for char in text:
            unicodeRange = uicore.font.GetUnicodeRange(ord(char))
            params = uicore.font.AlterParams(params, unicodeRange, formatLinks=True)
            if char == u'\xa0':
                rchar = u' '
            else:
                rchar = char
            fgi = glyphString.cmc.LookupFB(params.face, ord(rchar), uicore.font.GetFallbackFonts())
            if fgi[0] != last[0] or glyphString.scaler.height != params.fontsize:
                glyphString.imageType.width = glyphString.imageType.height = glyphString.scaler.width = glyphString.scaler.height = params.fontsize
                glyphString.imageType.flags = params.flags
                glyphString.imageType.face_id = fgi[0]
                glyphString.GetMetrics(fgi[0])
                glyphString.baseLine = max(glyphString.baseLine, glyphString.asc)
                glyphString.baseHeight = max(glyphString.baseHeight, glyphString.asc - glyphString.des)
                kern = 0
            else:
                kern = glyphString.cm.LookupKerningXP(glyphString.scaler, last[1], fgi[1])
            last = fgi
            sbit = glyphString.sbc.Lookup(glyphString.imageType, fgi[1])
            advance = sbit.xadvance + (letterspace or 0) + kern
            glyphString.insert(idx, (advance,
             0,
             color,
             sbit,
             char,
             glyphString.asc,
             glyphString.des,
             params.Copy()))
            idx += 1




    def OnClipperResize(self, width, height):
        self.RefreshNodes()
        self.DoSizeUpdateDelayed()



    def OnChange(self, *args):
        pass



    def GetSelection(self):
        return self.HasSelection()



    def HasSelection(self):
        (fromIdx, toIdx,) = self.globalSelectionRange
        return fromIdx != toIdx



    def DeleteSelected(self):
        (fromIdx, toIdx,) = self.globalSelectionRange
        if fromIdx == toIdx:
            return 
        startGS = None
        endGS = None
        singleLineGS = None
        rmCompletely = []
        counter = 0
        for (gsIdx, glyphString,) in enumerate(self.sr.paragraphs):
            gsLength = len(glyphString)
            if fromIdx <= counter and counter + gsLength <= toIdx:
                rmCompletely.append(glyphString)
            elif counter <= fromIdx <= counter + gsLength and counter <= toIdx <= counter + gsLength:
                singleLineGS = glyphString
                self.RemoveFromGlyphString(glyphString, fromIdx - counter, toIdx - counter)
            elif counter <= fromIdx <= counter + gsLength:
                startGS = glyphString
                startGS.FlushFromIndex(fromIdx - counter)
            elif counter <= toIdx <= counter + gsLength:
                endGS = glyphString
                self.FlushToIndex(glyphString, toIdx - counter)
            counter += gsLength
            counter += 1
            if counter >= toIdx:
                break

        if singleLineGS is not None:
            self.UpdateGlyphString(singleLineGS)
        elif startGS and endGS:
            startGS += endGS
            rmCompletely.append(endGS)
            self.UpdateGlyphString(startGS)
        elif startGS:
            self.UpdateGlyphString(startGS)
        elif endGS:
            self.UpdateGlyphString(endGS)
        for glyphString in rmCompletely:
            self.RemoveGlyphString(glyphString)

        if not self.GetNodes():
            self.SetValue('')
        else:
            self.SetSelectionRange(None, None, updateCursor=False)
            self.SetCursorPos(fromIdx)
            self.SetSelectionInitPos(self.globalCursorPos)
        return 1



    def FlushToIndex(self, glyphString, idx):
        for i in xrange(idx):
            if len(glyphString):
                glyphString.pop(0)




    def GetSeletedCharData(self):
        (fromIdx, toIdx,) = self.globalSelectionRange
        if fromIdx == toIdx:
            return 
        startedCollection = False
        done = False
        ret = []
        counter = 0
        for (gsIdx, glyphString,) in enumerate(self.sr.paragraphs):
            gData = []
            for (cdIdx, charData,) in enumerate(glyphString):
                if counter == fromIdx:
                    startedCollection = True
                if startedCollection:
                    gData.append((cdIdx, charData))
                counter += 1
                if counter == toIdx:
                    done = True
                    break

            if counter == fromIdx:
                startedCollection = True
            if startedCollection:
                ret.append((glyphString, gData))
            if done:
                break
            counter += 1
            if counter == toIdx:
                done = True
                break

        return ret



    def ApplySelection(self, what, data = None, toggle = False):
        selectedData = self.GetSeletedCharData()
        if selectedData:
            node = self.GetActiveNode()
            stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
            prevParams = self.GetPriorParams(node.glyphString, stackCursorIndex)
            if prevParams:
                params = prevParams.Copy()
            else:
                params = self.GetFontParams()
            changeGS = []
            changeParams = []
            for (glyphString, gsData,) in selectedData:
                for (charIdx, (advance, align, color, sbit, char, asc, des, _params,),) in gsData:
                    changeParams.append(_params)

                changeGS.append(glyphString)

            anchor = self.ApplyGameSelection(what, data, changeParams)
            if anchor == -1:
                anchor = None
            bBalance = 0
            uBalance = 0
            iBalance = 0
            for obj in changeParams:
                bBalance += 1 if obj.bold else -1
                uBalance += 1 if obj.underline else -1
                iBalance += 1 if obj.italic else -1

            params.bold = 1 if bBalance > 0 else 0
            params.italic = 1 if iBalance > 0 else 0
            params.underline = 1 if uBalance > 0 else 0
            if toggle:
                params.bold = not params.bold
                params.italic = not params.italic
                params.underline = not params.underline
            for obj in changeParams:
                if what == 1:
                    obj.bold = params.bold
                elif what == 2:
                    obj.italic = params.italic
                elif what == 3:
                    obj.underline = params.underline
                elif what == 4:
                    obj.color = data
                elif what == 5:
                    obj.fontsize = data
                elif what == 6:
                    obj.url = anchor

            for glyphString in changeGS:
                self.ReloadGlyphString(glyphString)
                self.UpdateGlyphString(glyphString)

            self._activeParams = params.Copy()
            self.UpdateAttributePanel()
            self.UpdatePosition()
            (fromIdx, toIdx,) = self.globalSelectionRange
            self.SetCursorPos(max(fromIdx, toIdx))
            uicore.registry.SetFocus(self)
        else:
            self.UpdateAttributePanel()
        if what == 6:
            self.SetSelectionRange(None, None, updateCursor=False)
            self.SetSelectionInitPos(self.globalCursorPos)
            self.RemoveAnchor()
        self.RefreshCursorAndSelection(updateActiveParams=False)



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



    @bluepy.CCP_STATS_ZONE_METHOD
    def DoSizeUpdateDelayed(self):
        if not self.GetNodes():
            return 
        try:
            self._DoSizeUpdateDelayed()
        except TaskletExit:
            pass
        except Exception as e:
            raise 



    @bluepy.CCP_STATS_ZONE_METHOD
    def _DoSizeUpdateDelayed(self):
        if self.resizeTasklet:
            self.resizeTasklet.kill()
            self.resizeTasklet = None
        self.resizeTasklet = uthread.new(self.DoSizeUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def DoSizeUpdate(self):
        if self.destroyed:
            return 
        self.resizing = 1
        for glyphString in self.sr.paragraphs:
            self.UpdateGlyphString(glyphString, 0, 0)

        if self.autoScrollToBottom and self.GetScrollProportion() == 0.0:
            self.ScrollToProportion(1.0)
        else:
            self.UpdatePosition()
        self.RefreshCursorAndSelection()
        self.resizeTasklet = None
        self.resizing = 1



    def EnlargeSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(1, 1)



    def ReduceSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(-1, 1)



    def ToggleBold(self):
        self._activeParams.bold = not self._activeParams.bold
        self.ApplySelection(1, toggle=True)



    def ToggleUnderline(self):
        self._activeParams.underline = not self._activeParams.underline
        self.ApplySelection(3, toggle=True)



    def ToggleItalic(self):
        self._activeParams.italic = not self._activeParams.italic
        self.ApplySelection(2, toggle=True)



    def ChangeFontSize(self, newSize):
        uicore.registry.SetFocus(self)
        self._activeParams.fontsize = newSize
        self.ApplySelection(5, newSize)



    def ChangeFontColor(self, newColor):
        uicore.registry.SetFocus(self)
        self._activeParams.color = newColor
        self.ApplySelection(4, newColor)



    def AddAnchor(self):
        uicore.registry.SetFocus(self)
        self.RemoveAnchor()
        self.ApplySelection(6)



    def RemoveAnchor(self):
        self._activeParams.url = None




class SE_EditTextlineCore(uicls.SE_BaseClassCore, uicls.BaseLink):
    __guid__ = 'uicls.SE_EditTextlineCore'

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.selectingtext = 0
        self.advanceByIndex = []
        self._currentWidth = 0
        self.sr.textcursor = None
        self.sr.cursortimer = None
        self.sr.textselection = None
        self.sr.links = uicls.Container(name='links', parent=self)
        trinity.device.RegisterResource(self)



    def OnChar(self, *args):
        pass



    def Load(self, node):
        self.sr.links.Flush()
        self.RenderLine()
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        if self.height != node._baseHeight + xtraHeight:
            node.height = None
            node.scroll.UpdatePosition()
        self.UpdateSelectionHilite()
        self.UpdateCursor()



    def GetSprite(self):
        if self.sr.sprite is None:
            self.sr.sprite = uicls.Sprite(parent=self, state=uiconst.UI_PICKCHILDREN, idx=0)
        return self.sr.sprite



    def OnCreate(self, dev):
        if self.sr.sprite:
            self.sr.sprite.texture = None
        if self.sr and self.sr.node:
            self.Load(self.sr.node)



    def RenderLine(self):
        node = self.sr.node
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        self.advanceByIndex = []
        self._currentWidth = 0
        if node._startIndex is None or not node.glyphString or node._width == 0 or node._baseHeight == 0:
            if self.sr.sprite:
                self.sr.sprite.state = uiconst.UI_HIDDEN
            return 
        (sprite, surf,) = self.GetSurface(node._width, node._baseHeight)
        if not surf:
            return 
        sprite.left = TEXTSIDEMARGIN
        sprite.top = xtraHeight
        k = surf.LockBuffer(None, False)
        try:
            buf = uicls.SE_TextlineCore.TexResBuf(k)
            uicore.font.Clear_Buffer(buf.data, buf.width, buf.height, buf.pitch)
            self.DrawLine(node.glyphString, buf, 0, node._baseHeight - node._baseLine, startIdx=node._startIndex, endIdx=node._endIndex)

        finally:
            surf.UnlockBuffer()

        sprite.SetSize(node._width, node._baseHeight)
        sprite.state = uiconst.UI_DISABLED



    def DrawLine(self, glyphString, buf, bx0, by0, startIdx, endIdx):
        sprite = self.GetSprite()
        x = 0
        self.advanceByIndex.append(x)
        openLink = None
        lastParams = None
        activeUnderline = None
        for t in glyphString[startIdx:endIdx]:
            (advance, align, color, sbit, char, asc, des, params,) = t
            if lastParams and lastParams.url != params.url:
                openLink = None
            if params.url:
                underline = True
                color = -23040
                if not lastParams or lastParams.url != params.url:
                    openLink = self.CreateLink(params.url)
                    openLink.left = x + sprite.left
                    openLink.height = sprite.height
                    openLink.top = sprite.top
            else:
                underline = bool(params.underline)
                color = params.color or -1
            if type(color) != types.IntType:
                tricol = trinity.TriColor(*color)
                color = tricol.AsInt()
            sbit.ToBuffer(buf.data, buf.width, buf.height, buf.pitch, x + bx0, by0, color)
            if underline:
                if activeUnderline and activeUnderline[-1] != (params.face,
                 params.fontsize,
                 color,
                 params.flags):
                    glyphString.DrawUnderline(buf, activeUnderline)
                    activeUnderline = None
                if activeUnderline:
                    activeUnderline[1] = x + bx0 + advance
                else:
                    activeUnderline = [x + bx0,
                     x + bx0 + advance,
                     by0,
                     buf.pitch,
                     asc,
                     des,
                     (params.face,
                      params.fontsize,
                      color,
                      params.flags)]
            elif activeUnderline:
                glyphString.DrawUnderline(buf, activeUnderline)
                activeUnderline = None
            if openLink:
                openLink.width += advance
            lastParams = params
            x += advance
            self.advanceByIndex.append(x)

        self._currentWidth = x
        if activeUnderline:
            glyphString.DrawUnderline(buf, activeUnderline)



    def GetSurface(self, width, height):
        sprite = self.GetSprite()
        if sprite.texture:
            textureSize = (sprite.texture.srcWidth, sprite.texture.srcHeight)
        else:
            textureSize = (0, 0)
        surf = None
        try:
            if textureSize != (width, height):
                texturePrimary = trinity.Tr2Sprite2dTexture()
                texturePrimary.atlasTexture = trinity.textureAtlasMan.atlases[0].CreateTexture(width, height)
                texturePrimary.srcX = 0.0
                texturePrimary.srcY = 0.0
                texturePrimary.srcWidth = int(width)
                texturePrimary.srcHeight = int(height)
                sprite.texture = texturePrimary
                surf = texturePrimary.atlasTexture
            else:
                surf = sprite.texture.atlasTexture
            sprite.width = width
            sprite.height = height
            return (sprite, surf)
        except Exception as e:
            log.LogWarn('Failed to create surface', e)
            log.LogException()
            return (sprite, None)



    def CreateLink(self, url):
        link = uicls.BaseLink(parent=self.sr.links, align=uiconst.RELATIVE, state=uiconst.UI_NORMAL)
        link.OnDblClick = self.OnDblClick
        link.OnMouseEnter = (self.LinkEnter, link)
        link.OnMouseExit = (self.LinkExit, link)
        link.OnMouseDown = (self.LinkDown, link)
        link.OnMouseUp = (self.LinkUp, link)
        link.cursor = 21
        link.url = url
        link.name = 'textlink'
        link.URLHandler = self.sr.node.Get('URLHandler', None)
        return link



    def LinkDown(self, link, *args):
        self.ResetLinks()



    def LinkUp(self, link, *args):
        if uicore.uilib.mouseOver is link:
            self.LinkEnter(link)



    def LinkEnter(self, link, *args):
        browser = uiutil.GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint(link.hint or link.url)
        self.ResetLinks()
        for entry in self.sr.node.scroll.GetNodes():
            if not entry.panel:
                continue
            if entry.panel.sr.Get('links', None):
                for item in entry.panel.sr.links.children:
                    if item.name == 'textlink' and item.url == link.url:
                        self.HiliteLink(item)





    def ResetLinks(self):
        for entry in self.sr.node.scroll.GetNodes():
            if not entry.panel:
                continue
            if entry.panel.sr.Get('links', None):
                for item in entry.panel.sr.links.children:
                    item.Flush()





    def LinkExit(self, link, *args):
        browser = uiutil.GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint('')
        self.ResetLinks()



    def HiliteLink(self, link):
        if not len(link.children):
            uicls.Fill(parent=link, color=(1.0, 0.65, 0.0, 0.33), pos=(-2, 0, -2, 0))



    def SelectionHandlerDelegate(self, funcName, args):
        handler = self.sr.node.Get('SelectionHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                return apply(func, args)



    def GetMenu(self):
        self.sr.node.scroll.ShowHint('')
        return self.SelectionHandlerDelegate('GetMenuDelegate', (self.sr.node,))



    def OnMouseDown(self, button, *args):
        if button == 0:
            self.SelectionHandlerDelegate('OnMouseDownDelegate', (self.sr.node,))



    def OnMouseUp(self, button, *args):
        if button == 0:
            self.SelectionHandlerDelegate('OnMouseUpDelegate', (self.sr.node,))



    def OnDropData(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDropDataDelegate', (self.sr.node, nodes))



    def OnDragMove(self, nodes, *args):
        self.SelectionHandlerDelegate('OnDragMoveDelegate', (self.sr.node, nodes))



    def OnDragEnter(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragExitDelegate', (self.sr.node, nodes))



    def OnDragExit(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragExitDelegate', (self.sr.node, nodes))



    def OnClick(self, *args):
        pass



    def OnDblClick(self, *args):
        self.SelectionHandlerDelegate('SelectWordUnderCursor', ())



    def OnTripleClick(self, *args):
        self.SelectionHandlerDelegate('SelectLineUnderCursor', ())



    def GetScrollAbove(self):
        item = self.parent
        while item:
            if isinstance(item, uicls.ScrollCore):
                return item
            item = item.parent




    def UpdateSelectionHilite(self):
        if not self.sr.node:
            return 
        scrollAbove = self.GetScrollAbove()
        f = uicore.registry.GetFocus()
        if not scrollAbove or scrollAbove is not f or not blue.rot.GetInstance('app:/App').IsActive():
            selectionAlpha = 0.125
        else:
            selectionAlpha = 0.25
        if self.sr.node.selectionStartIndex is not None:
            if self.sr.textselection is None:
                self.sr.textselection = uicls.Fill(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
            self.sr.textselection.SetAlpha(selectionAlpha)
            if self.sr.node.startCursorIndex <= self.sr.node.selectionStartIndex <= self.sr.node.endCursorIndex:
                left = self.GetWidthToGlobalIndex(self.sr.node.selectionStartIndex)
            else:
                left = 0
            if self.sr.node.startCursorIndex <= self.sr.node.selectionEndIndex <= self.sr.node.endCursorIndex:
                width = self.GetWidthToGlobalIndex(self.sr.node.selectionEndIndex)
            elif len(self.sr.node.glyphString):
                width = getattr(self, '_currentWidth', 0) or self.GetSprite().width
            else:
                width = 0
            self.sr.textselection.left = left + TEXTSIDEMARGIN
            self.sr.textselection.width = max(2, width - left)
            self.sr.textselection.top = TEXTLINEMARGIN
            self.sr.textselection.height = self.height
            self.sr.textselection.state = uiconst.UI_DISABLED
        elif self.sr.textselection:
            self.sr.textselection.state = uiconst.UI_HIDDEN



    def GetInternalCursorPos(self):
        if not self.sr.sprite:
            return 0
        (l, t, w, h,) = self.sr.sprite.GetAbsolute()
        toCursorPos = uicore.uilib.x - l
        idx = 0
        w = 0
        for charData in self.sr.node.glyphString[self.sr.node.stackCursorIndex:(self.sr.node.stackCursorIndex + self.sr.node.letterCountInLine)]:
            adv = charData[0]
            if w + adv > toCursorPos:
                break
            w += adv
            idx += 1

        return idx



    def UpdateCursor(self):
        if self.sr.node.globalCursorPos is not None:
            sprite = self.GetSprite()
            if self.sr.textcursor is None:
                self.sr.textcursor = uicls.Fill(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 1.0))
                self.sr.textcursor.width = 1
            left = self.GetWidthToGlobalIndex(self.sr.node.globalCursorPos)
            if self.sr.node.idx == 0:
                margin = TEXTSIDEMARGIN
            else:
                margin = TEXTLINEMARGIN
            self.sr.textcursor.top = margin
            self.sr.textcursor.left = left + TEXTSIDEMARGIN
            self.sr.textcursor.height = self.height - margin
            if self.sr.cursortimer is None:
                self.CursorBlink()
        elif self.sr.textcursor:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN



    def GetWidthToGlobalIndex(self, globalCursorPos):
        localIndex = globalCursorPos - self.sr.node.startCursorIndex
        if len(self.advanceByIndex) > localIndex:
            return self.advanceByIndex[localIndex]
        return 0



    def GetCursorOffset(self):
        if self.sr.textcursor:
            return self.sr.textcursor.left



    def CursorBlink(self):
        f = uicore.registry.GetFocus()
        if f is uicore.desktop or not blue.rot.GetInstance('app:/App').IsActive():
            if self.sr.textcursor:
                self.sr.textcursor.state = uiconst.UI_HIDDEN
            self.sr.cursortimer = None
            return 
        if f and uiutil.IsUnder(self, f) and self.sr.node.globalCursorPos is not None and self.sr.textcursor is not None:
            self.sr.textcursor.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][(self.sr.textcursor.state == uiconst.UI_HIDDEN)]
            if self.sr.cursortimer is None:
                self.sr.cursortimer = base.AutoTimer(250, self.CursorBlink)
        else:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN



    def GetCopyData(self, fromIdx, toIdx):
        return uicore.font.GetNodeCopyData(self.sr.node, fromIdx, toIdx)



    def GetText(self, node):
        if node.rawText:
            return node.rawText
        text = ''.join([ glyphData[4] for glyphData in self.sr.node.glyphString[self.sr.node.stackCursorIndex:(self.sr.node.stackCursorIndex + self.sr.node.letterCountInLine)] if glyphData[4] != None ])
        node.rawText = text
        return text



    def GetDynamicHeight(node, width):
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        return node._baseHeight + xtraHeight




