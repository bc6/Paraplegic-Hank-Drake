import sys
import util
import uiutil
import fontConst

class css:
    __guid__ = 'html.Css'

    def __init__(self):
        self.Reset()



    def Reset(self):
        self.classes = []
        self.s = {}



    def copy(self):
        new = css()
        new.classes = self.classes[:]
        return new



    def ApplyCSS(self, tag, attrs, attrStack):
        classlist = []
        for c in self.classes:
            if self.CompareSelector(attrStack[-1], c) == 1:
                b = 0
                if c['deptag']:
                    i = len(attrStack) - 2
                    if i < 0:
                        continue
                    for t in c['deptag']:
                        if b == 1 or i < 0:
                            break
                        if t['op'] == ' ':
                            while not self.CompareSelector(attrStack[i], t):
                                i -= 1
                                if i < 0:
                                    b = 1
                                    break

                            if i < 0:
                                b = 1
                                break
                            i -= 1
                        elif t['op'] == '>':
                            if self.CompareSelector(attrStack[i], t):
                                i -= 1
                                continue
                            else:
                                b = 1
                                break
                        elif t['op'] == '*':
                            i -= 1
                            if i < 0:
                                break
                            while not self.CompareSelector(attrStack[i], t):
                                i -= 1
                                if i < 0:
                                    b = 1
                                    break

                            if i < 0:
                                b = 1
                                break
                            i -= 1
                        elif t['op'] == '+':
                            if attrStack[i]['lasttag'] == t['tag']:
                                i -= 1
                        else:
                            b = 1
                            break
                            continue

                if b == 0:
                    classlist.append(c)

        classlist.sort(lambda x, y: cmp(x['prio'], y['prio']))
        c = {}
        for each in classlist:
            c.update(each)

        return c



    def CompareSelector(self, astack, csel):
        tag = astack['tag']
        tid = getattr(astack['attr'], 'id', None)
        cl = getattr(astack['attr'], 'class', '').lower()
        if csel['tag'] not in (tag, '*') and csel['tag']:
            return 
        if csel['class']:
            if csel['class'] not in cl.split(' '):
                return 
        if csel['id'] and tid != csel['id']:
            return 
        return 1



    def SplitSelector(self, sel):
        s = {}
        s['tag'] = None
        s['id'] = None
        s['class'] = None
        s['attr'] = None
        s['pclass'] = None
        sel = sel.strip().lower()
        if sel.count(':'):
            (sel, pclass,) = sel.split(':', 1)
            s['pclass'] = pclass
            if sel == '':
                sel = '*'
        ccount = sel.count('.')
        acount = sel.count('[')
        icount = sel.count('#')
        if ccount + acount + icount > 1:
            return 
        if ccount == 1:
            h = sel.split('.')
            if len(h) == 1:
                s['class'] = h[0]
            else:
                s['tag'] = h[0]
                s['class'] = h[1]
            return s
        if acount == 1:
            h = sel.split('[')
            if sel[-1] == ']':
                if len(h) == 1:
                    s['attr'] = h[0]
                else:
                    s['tag'] = h[0]
                    s['attr'] = h[1]
            else:
                return 
            return s
        if icount == 1:
            h = sel.split('#')
            if len(h) == 1:
                s['id'] = h[0]
            else:
                s['tag'] = h[0]
                s['id'] = h[1]
            return s
        s['tag'] = sel
        return s



    def GetClass(self, classID):
        classID = classID.lower()
        for c in self.classes:
            if c['id'] == classID:
                return c
            if c['class'] == classID:
                return c




    def HandlePseudoClass(self, pclass):
        links = [('link', 'link-color'),
         ('visited', 'vlink-color'),
         ('active', 'alink-color'),
         ('hover', 'alink-color')]
        d = {}
        for (dclass, attr,) in links:
            if pclass == dclass and 'color' in self.s:
                d[attr] = self.s['color']

        self.s = d.copy()



    def ParseCSSData(self, cssdata):
        lines = ''
        for dataAndComment in cssdata.split('*/'):
            data = dataAndComment.split('/*', 1)[0]
            lines += data

        for styleClass in lines.split('}'):
            if not styleClass:
                continue
            if styleClass.count('{') != 1:
                continue
            (attr, styles,) = styleClass.strip().split('{')
            self.s = {}
            prio = 0
            if not styles:
                continue
            (data, imp,) = self.ParseStyleData(styles.strip())
            self.ParseStyle(data)
            selector = depsel = depop = None
            prio += attr.count('.') * 100 + attr.count('#') * 1000 + attr.count('[') * 10 + attr.count(' ') + 1 - (attr.count('.') + attr.count('#') + attr.count('['))
            selectors = attr.replace('\t', ' ').replace('  ', ' ').strip().split(' ')
            selector = selectors[-1]
            selectors = selectors[:-1]
            selectors.reverse()
            deptags = []
            op = ' '
            for t in selectors:
                if t in ('>', '*', '+'):
                    op = t
                else:
                    d = self.SplitSelector(t)
                    if d:
                        d['op'] = op
                        deptags.append(d)
                        op = ' '

            for sel in selector.split(','):
                attrs = self.SplitSelector(sel)
                if attrs:
                    if attrs['pclass']:
                        self.HandlePseudoClass(attrs['pclass'])
                    s = self.s.copy()
                    s['tag'] = attrs['tag']
                    s['class'] = attrs['class']
                    s['id'] = attrs['id']
                    s['attr'] = attrs['attr']
                    s['deptag'] = deptags
                    s['prio'] = prio
                    self.classes.append(s)

            if len(imp):
                self.s = {}
                self.ParseStyle(imp)
                for sel in selector.split(','):
                    attrs = self.SplitSelector(sel)
                    if attrs:
                        if attrs['pclass']:
                            self.HandlePseudoClass(attrs['pclass'])
                        s = self.s.copy()
                        s['tag'] = attrs['tag']
                        s['class'] = attrs['class']
                        s['id'] = attrs['id']
                        s['attr'] = attrs['attr']
                        s['deptag'] = deptags
                        s['prio'] = 10000
                    self.classes.append(s)





    def ParseStyleData(self, cssdata):
        data = {}
        imp = {}
        for attrAndValue in cssdata.split(';'):
            if not attrAndValue:
                continue
            if ':' in attrAndValue:
                (attr, value,) = attrAndValue.strip().split(':', 1)
            else:
                continue
            if attr and value:
                attr = attr.strip().lower()
                if '!' in value:
                    (value, important,) = value.split('!', -1)
                    if important.strip().lower() == 'important':
                        imp[attr] = value.strip()
                        continue
                data[attr] = value.strip()

        return (data, imp)



    def ParseCSS(self, attrs = None):
        self.s = {}
        sattr = getattr(attrs, 'style', None)
        if sattr:
            (data, imp,) = self.ParseStyleData(sattr)
            data.update(imp)
            return self.ParseStyle(data)



    def ParseStyle(self, style = None):
        if style:
            for (k, v,) in style.iteritems():
                if k in self.styleDict:
                    eval('self.%s' % self.styleDict[k])(k, v)

        return self.s



    def ParseStyleNum(self, value):
        value = str(value).lower().strip()
        if value.isdigit():
            return int(value)
        if value.endswith('%'):
            return value
        if value[-2:] in self.absStyleUnits and value[:-2].isdigit():
            return int(self.absStyleUnits[value[-2:]] * float(value[:-2].strip()))
        try:
            return int(value)
        except:
            sys.exc_clear()
            return None


    absStyleUnits = {'px': 1.0,
     'in': 100.0,
     'cm': 100.0 / 2.54,
     'mm': 100.0 / 25.4,
     'pt': 100.0 / 72.0,
     'pc': 100.0 / 6.0}

    def ParseFontSize(self, k, v):
        if v:
            if not v.isdigit():
                if v in self.fontSize:
                    v = self.fontSize[v]
            v = self.ParseStyleNum(v)
            if v is None or not type(v) == int and not v.isdigit():
                return 
            if v in self.fontFamilies:
                self.s['font-size'] = int(v)
                self.s['font-family'] = self.fontFamilies[int(v)]
            else:
                self.s['font-size'] = int(v or 10)
            self.s['font-family'] = fontConst.DEFAULT_FONT



    def ParseFontStyle(self, k, v):
        if v:
            if v == 'normal':
                self.s['font-style'] = 'n'
            if v in ('italic', 'oblique'):
                self.s['font-style'] = 'i'



    def ParseFontWeight(self, k, v):
        if v:
            if v == 'normal':
                self.s['font-weight'] = 'n'
            elif v in ('bold', 'bolder'):
                self.s['font-weight'] = 'b'



    def ParseTextDecoration(self, k, v):
        if v:
            if v == 'none':
                self.s['text-decoration'] = ''
                return 
            s = str(v)
            s = s.replace('underline', 'u').replace('line-through', 's').replace('overline', 'o')
            for t in s:
                if t.strip() not in ('u', 's', 'o'):
                    return 

            self.s['text-decoration'] = s



    def ParseTextAlign(self, k, v):
        if v in ('left', 'right', 'center'):
            self.s['text-align'] = v



    def ParseFont(self, k, v):
        if v:
            for param in v.split(' '):
                self.ParseFontSize('', param)
                self.ParseFontStyle('', param)
                self.ParseFontWeight('', param)
                self.ParseTextDecoration('', param)




    def ParseMargin(self, k, v):
        if v:
            a = []
            for p in v.replace('  ', ' ').split(' '):
                p = self.ParseStyleNum(p)
                if p:
                    a.append(p)

            if len(a) > 0:
                self.s['margin-left'] = a[[0,
                 1,
                 1,
                 3][(len(a) - 1)]]
                self.s['margin-right'] = a[[0,
                 1,
                 1,
                 1][(len(a) - 1)]]
                self.s['margin-top'] = a[[0,
                 0,
                 0,
                 0][(len(a) - 1)]]
                self.s['margin-bottom'] = a[[0,
                 0,
                 2,
                 2][(len(a) - 1)]]



    def ParsePadding(self, k, v):
        if v:
            v = self.ParseStyleNum(v)
            if v:
                self.s['padding-left'] = self.s['padding-right'] = v
                self.s['padding-top'] = self.s['padding-bottom'] = v



    def ParseBorderWidth(self, k, v):
        if v:
            if v in self.borderWidths:
                v = self.borderWidths[v]
            else:
                v = self.ParseStyleNum(v)
            if v:
                if k == 'border-width':
                    for i in ('left', 'right', 'top', 'bottom'):
                        self.s['border-' + i + '-width'] = v

                else:
                    self.s[k] = v



    def ParseBorderColor(self, k, v):
        if v:
            v = uiutil.ParseHTMLColor(v, 1, error=1)
            if v:
                self.s['border-left-color'] = self.s['border-right-color'] = v
                self.s['border-top-color'] = self.s['border-bottom-color'] = v



    def ParseBorderStyles(self, k, v):
        if v:
            if v in self.borderStyles:
                self.s[k] = self.borderStyles[v]



    def ParseBorderStyle(self, k, v):
        if v in self.borderStyles:
            self.s['border-left-style'] = self.borderStyles[v]
            self.s['border-right-style'] = self.borderStyles[v]
            self.s['border-top-style'] = self.borderStyles[v]
            self.s['border-bottom-style'] = self.borderStyles[v]



    def ParseBorder(self, k, v):
        for each in v.split(' '):
            if each in self.borderStyles:
                self.ParseBorderStyle(k, each)
                continue
            self.ParseBorderColor(k, each)
            self.ParseBorderWidth('border-width', each)




    def ParseBorders(self, k, v):
        for each in v.split(' '):
            if each in self.borderStyles:
                self.ParseBorderStyles(k, each)
                continue
            self.ParseColor(k + '-color', each)
            self.ParseBorder(k + '-width', each)




    def ParseBorderCollapse(self, k, v):
        if v in self.borderCollapse:
            self.s['border-collapse'] = self.borderCollapse[v]
        else:
            self.s['border-collapse'] = 0



    def ParseColor(self, k, v):
        if v:
            v = uiutil.ParseHTMLColor(v, 1, error=1)
            if v:
                self.s[k] = v



    def ParseBackground(self, k, v):
        for each in v.split(' '):
            each = each.replace(' ', '').lower()
            if each.find('url(') != -1:
                self.ParseBackgroundImage(None, each)
            elif each.find('repeat') != -1:
                self.ParseBackgroundRepeat(None, each)
            elif v:
                color = uiutil.ParseHTMLColor(each, 1, error=1)
                if color:
                    self.s['background-color'] = color




    def ParseBackgroundRepeat(self, k, v):
        if v in ('repeat', 'repeat-x', 'repeat-y', 'no-repeat'):
            self.s['background-repeat'] = v



    def ParseBackgroundImage(self, k, v):
        if v and v.startswith('url(') and v.endswith(')'):
            self.s['background-image'] = v[4:-1]



    def ParseBackgroundAttachment(self, k, v):
        if v in ('fixed', 'scroll'):
            self.s['background-attachment'] = v



    def ParseBackgroundPosition(self, k, v):
        if v:
            v = v.split(' ')
            if len(v) in (2, 4):
                self.ParseAbsSize('background-image-left', v[0])
                self.ParseAbsSize('background-image-top', v[1])
            if len(v) == 4:
                self.ParseAbsSize('background-image-width', v[2])
                self.ParseAbsSize('background-image-height', v[3])
            self.s['background-position'] = []
            for i in v:
                if i in ('top', 'center', 'middle', 'bottom', 'left', 'right'):
                    self.s['background-position'].append(i)




    def ParseAbsSize(self, k, v):
        if v:
            v = self.ParseStyleNum(v)
            if v:
                self.s[k] = int(v)



    def ParsePosAbsSize(self, k, v):
        if v:
            v = self.ParseStyleNum(v)
            if v:
                if type(v) == int:
                    self.s[k] = max(v, 0)
                else:
                    self.s[k] = v



    def ParseVerticalAlign(self, k, v):
        if v in self.vertStyles:
            self.s['vertical-align'] = self.vertStyles[v]



    def ParseHorizontalAlign(self, k, v):
        if v in ('left', 'right', 'center'):
            self.s['horizontal-align'] = v



    def ParsePosition(self, k, v):
        if v in ('absolute', 'fixed', 'relative', 'static'):
            self.s['position'] = v



    def ParseFloat(self, k, v):
        if v in ('left', 'right'):
            self.s['float'] = v
        elif v == 'none':
            self.s['float'] = None
        elif v == 'inherit' and self.s.has_key('float'):
            del self.s['float']


    fontSize = {'small': 8,
     'x-small': 7,
     'xx-small': 6,
     'smaller': 8,
     'medium': 10,
     'large': 12,
     'larger': 14,
     'x-large': 20}
    fontFamilies = {8: fontConst.DEFAULT_FONT,
     10: fontConst.DEFAULT_FONT,
     12: fontConst.DEFAULT_FONT,
     14: fontConst.DEFAULT_FONT,
     20: fontConst.DEFAULT_FONT}
    vertStyles = {'top': 0,
     'middle': 1,
     'bottom': 2,
     'baseline': 3,
     'sub': 4,
     'super': 5}
    borderStyles = {'none': None,
     'hidden': 0,
     'solid': 1,
     'groove': 2,
     'ridge': 2,
     'inset': 2,
     'outset': 2}
    borderWidths = {'thin': 1,
     'medium': 2,
     'thick': 3}
    borderCollapse = {'seperate': 0,
     'collapse': 1}
    absStyles = ('text-indent', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom', 'padding-left', 'padding-right', 'padding-top', 'padding-bottom', 'border-left-width', 'border-right-width', 'border-top-width', 'border-bottom-width', 'letter-spacing', 'word-spacing', 'line-height')
    styleDict = {'text-indent': 'ParseAbsSize',
     'margin-left': 'ParsePosAbsSize',
     'margin-right': 'ParsePosAbsSize',
     'margin-top': 'ParsePosAbsSize',
     'margin-bottom': 'ParsePosAbsSize',
     'padding-left': 'ParsePosAbsSize',
     'padding-right': 'ParsePosAbsSize',
     'padding-top': 'ParsePosAbsSize',
     'padding-bottom': 'ParsePosAbsSize',
     'border-left-width': 'ParseBorderWidth',
     'border-right-width': 'ParseBorderWidth',
     'border-top-width': 'ParseBorderWidth',
     'border-bottom-width': 'ParseBorderWidth',
     'border-left-style': 'ParseBorderStyles',
     'border-right-style': 'ParseBorderStyles',
     'border-top-style': 'ParseBorderStyles',
     'border-bottom-style': 'ParseBorderStyles',
     'letter-spacing': 'ParseAbsSize',
     'word-spacing': 'ParseAbsSize',
     'line-height': 'ParsePosAbsSize',
     'font-size': 'ParseFontSize',
     'font-weight': 'ParseFontWeight',
     'font-style': 'ParseFontStyle',
     'text-decoration': 'ParseTextDecoration',
     'text-align': 'ParseTextAlign',
     'font': 'ParseFont',
     'margin': 'ParseMargin',
     'padding': 'ParsePadding',
     'border-width': 'ParseBorderWidth',
     'border-color': 'ParseBorderColor',
     'border-style': 'ParseBorderStyle',
     'border': 'ParseBorder',
     'border-left': 'ParseBorders',
     'border-right': 'ParseBorders',
     'border-top': 'ParseBorders',
     'border-bottom': 'ParseBorders',
     'color': 'ParseColor',
     'link-color': 'ParseColor',
     'alink-color': 'ParseColor',
     'vlink-color': 'ParseColor',
     'background': 'ParseBackground',
     'background-color': 'ParseColor',
     'border-left-color': 'ParseColor',
     'border-right-color': 'ParseColor',
     'border-top-color': 'ParseColor',
     'border-bottom-color': 'ParseColor',
     'vertical-align': 'ParseVerticalAlign',
     'align': 'ParseHorizontalAlign',
     'background-repeat': 'ParseBackgroundRepeat',
     'background-image': 'ParseBackgroundImage',
     'background-image-color': 'ParseColor',
     'background-image-width': 'ParseAbsSize',
     'background-image-height': 'ParseAbsSize',
     'background-image-left': 'ParseAbsSize',
     'background-image-top': 'ParseAbsSize',
     'background-attachment': 'ParseBackgroundAttachment',
     'background-position': 'ParseBackgroundPosition',
     'border-collapse': 'ParseBorderCollapse',
     'position': 'ParsePosition',
     'float': 'ParseFloat',
     'left': 'ParseAbsSize',
     'right': 'ParseAbsSize',
     'top': 'ParseAbsSize',
     'bottom': 'ParseAbsSize',
     'width': 'ParsePosAbsSize',
     'min-width': 'ParsePosAbsSize',
     'max-width': 'ParsePosAbsSize',
     'height': 'ParsePosAbsSize',
     'min-height': 'ParsePosAbsSize',
     'max-height': 'ParsePosAbsSize'}


