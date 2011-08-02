import trinity
import blue
import urllib2
import urllib
import urlparse
import nturl2path
import log
import re
import uiutil
import uiconst
import uicls

class NewBrowserForm():
    __guid__ = 'corebrowserutil.NewBrowserForm'

    def __init__(self, attrs, browser):
        if getattr(attrs, 'action', None) is None:
            setattr(attrs, 'action', uiutil.GetBrowser(browser).sr.currentURL.split('?')[0])
        if str(getattr(attrs, 'method', 'get')).lower() not in ('get', 'post'):
            setattr(attrs, 'method', 'get')
        self.submitting = 0
        self.attrs = attrs
        self.browser = browser
        self.fields = []



    def fixup(self, m):
        return '&#' + hex(int(m.group(1)))[1:] + ';'



    def decode(self, u):
        return re.sub('&#(\\d+);', self.fixup, u.encode('cp1252', 'xmlcharrefreplace'))



    def OnSubmit(self, *etc):
        if self.submitting:
            uicore.Message('Busy')
            return 
        self.submitting = 1
        e = []
        for (attrs, wnd,) in self.fields:
            if not attrs.name:
                continue
            if getattr(attrs, 'type', None).lower() == 'submit' and wnd not in etc:
                continue
            getval = getattr(self, 'GetValue_%s' % attrs.type.lower(), lambda *args: None)
            val = getval(wnd, attrs)
            if val is not None:
                e.append((attrs.name, val))

        d = []
        for (key, val,) in e:
            if type(val) == list:
                for v in val:
                    if isinstance(v, unicode):
                        v = self.decode(v)
                    d.append((key, v))

            else:
                if isinstance(val, unicode):
                    val = self.decode(val)
                d.append((key, val))

        s = urllib.urlencode(d)
        if isinstance(s, unicode):
            s = self.decode(val)
        browser = uiutil.GetBrowser(self.browser)
        if not browser:
            return 
        if getattr(self.attrs, 'method', 'get').lower() == 'get':
            if 'localsvc:' in self.attrs.action:
                uicls.BaseLinkCore().LocalSvcCall(self.attrs.action[9:] + ''.join([ name for (name, value,) in d ]))
                self.submitting = 0
            else:
                browser.GoTo('?'.join((self.attrs.action, s)))
        elif self.attrs.method.lower() == 'post':
            browser.GoTo(self.attrs.action, s)



    def GetField(self, name = None):
        if name is None:
            return self.fields[-1][1]
        for (attrs, wnd,) in self.fields:
            if attrs.name == name:
                return wnd
        else:
            return 




    def GetFields(self):
        d = {}
        for (attrs, wnd,) in self.fields:
            if not attrs.name:
                continue
            if getattr(attrs, 'type', None) in ('submit', 'hidden'):
                continue
            getval = getattr(self, 'GetValue_%s' % attrs.type.lower(), lambda *args: None)
            val = getval(wnd, attrs)
            if val is not None:
                d[attrs.name] = val

        return d



    def SetFields(self, d):
        for (attrs, wnd,) in self.fields:
            if not attrs.name:
                continue
            setval = getattr(self, 'SetValue_%s' % attrs.type.lower(), lambda *args: None)
            if not d.has_key(attrs.name):
                if getattr(attrs, 'type', None) == 'checkbox':
                    setval(wnd, attrs, 0)
                continue
            setval(wnd, attrs, d[attrs.name])




    def AddInput(self, attrs, add = 1):
        attrs.vspace = getattr(attrs, 'vspace', 1)
        if attrs.type is None:
            attrs.type = 'text'
        create = getattr(self, 'Create_%s' % attrs.type.lower(), None)
        if create:
            wnd = create(attrs)
        else:
            wnd = uicls.Container()
        browser = uiutil.GetBrowser(self.browser)
        if not browser:
            return 
        if add:
            self.fields.append((attrs, wnd))
        attrs.control = wnd
        attrs.align = getattr(attrs, 'align', None)
        obj = uiutil.Bunch()
        obj.font = None
        obj.key = 'input_%s' % attrs.type.lower()
        obj.type = '<input>'
        obj.attrs = attrs
        wnd.state = uiconst.UI_HIDDEN
        if hasattr(self.browser, 'sr'):
            uiutil.Transplant(wnd, self.browser.sr.cacheContainer)
        startup = getattr(self, 'Startup_%s' % attrs.type.lower(), None)
        if startup:
            startup(wnd, attrs)
        obj.width = wnd.width + 5
        obj.height = wnd.height + 5
        obj.valign = 1
        if add:
            obj.control = wnd
            wnd.loaded = 1
        else:
            wnd.Close()
        return obj



    def AddTextArea(self, attrs, add = 1):
        attrs.type = 'textarea'
        return self.AddInput(attrs, add)



    def AddSelect(self, attrs, options, add = 1):
        attrs.type = 'select'
        attrs.options = options
        return self.AddInput(attrs, add)



    def StdGetValue(self, wnd, attrs):
        return wnd.GetValue()



    def StdSetValue(self, wnd, attrs, val):
        wnd.SetValue(val)



    def GetValue_submit(self, wnd, attrs):
        return getattr(attrs, 'value', None) or 'Submit'



    def GetValue_hidden(self, wnd, attrs):
        return attrs.value



    def Create_textarea(self, attrs):
        wnd = uicls.Edit(name='textarea', align=uiconst.RELATIVE)
        wnd.width = getattr(attrs, 'width', None) or 8 * int(attrs.cols) or 350
        wnd.height = getattr(attrs, 'height', None) or 18 * int(attrs.rows) or 45
        return wnd



    def Startup_textarea(self, wnd, attrs):
        if getattr(attrs, 'maxlength', None):
            wnd.SetMaxLength(attrs.maxlength)
        if hasattr(attrs, 'readonly'):
            wnd.ReadOnly()
        if attrs.value:
            wnd.SetValue(attrs.value)
        color = self.browser.attrStack[-1]['color']
        uicls.Line(parent=wnd, align=uiconst.TOTOP, color=color, weight=1)
        uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=color, weight=1)
        uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=color, weight=1)
        uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=color, weight=1)



    def GetValue_textarea(self, wnd, attrs):
        return wnd.GetValue().replace('<br>', '\r\n')


    SetValue_textarea = StdSetValue

    def Create_text(self, attrs):
        wnd = uicls.SinglelineEdit(name='textedit', align=uiconst.RELATIVE, pos=(0,
         0,
         getattr(attrs, 'width', None) or min(200, 7 * (attrs.size or 30)),
         16))
        return wnd



    def Startup_text(self, wnd, attrs, password = 0):
        wnd.OnReturn = self.OnSubmit
        if password:
            wnd.SetPasswordChar('*')
        maxlength = getattr(attrs, 'maxlength', None)
        if maxlength is not None:
            wnd.SetMaxLength(int(maxlength))
        if attrs.value:
            wnd.SetValue(attrs.value, updateIndex=0)
        if hasattr(self.browser, 'attrStack'):
            color = self.browser.attrStack[-1]['color']
            uicls.Line(parent=wnd, align=uiconst.TOTOP, color=color, weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=color, weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=color, weight=1)
            uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=color, weight=1)


    GetValue_text = StdGetValue
    SetValue_text = StdSetValue
    Create_password = Create_text

    def Startup_password(self, wnd, attrs):
        self.Startup_text(wnd, attrs, password=1)
        wnd.SetPasswordChar('\x95')


    GetValue_password = StdGetValue
    SetValue_password = StdSetValue

    def Create_checkbox(self, attrs):
        cbox = uicls.Checkbox(pos=(0, 0, 0, 0), align=uiconst.RELATIVE)
        cbox.data = {}
        attrs.vspace = 3
        return cbox



    def Startup_checkbox(self, wnd, attrs):
        checked = getattr(attrs, 'checked', '').lower() == 'checked'
        if not checked and attrs.__dict__.has_key('checked') and getattr(attrs, 'checked', None) is None:
            checked = 1
        wnd.SetChecked(checked, 0)



    def SetValue_checkbox(self, wnd, attrs, val):
        if val == attrs.value:
            wnd.SetValue(1)
        else:
            wnd.SetValue(0)



    def GetValue_checkbox(self, wnd, attrs):
        checked = wnd.GetValue()
        if checked:
            return attrs.value or 'on'
        else:
            return None



    def Create_radio(self, attrs):
        ret = self.Create_checkbox(attrs)
        ret.SetGroup(attrs.name)
        ret.width = ret.height = 14
        return ret


    Startup_radio = Startup_checkbox
    GetValue_radio = GetValue_checkbox
    SetValue_radio = SetValue_checkbox

    def Create_select(self, attrs):
        if getattr(attrs, 'size', None) is not None or getattr(attrs, 'height', 0):
            return uicls.Select(name='select', align=uiconst.RELATIVE, pos=(0,
             0,
             getattr(attrs, 'width', None) or 128,
             getattr(attrs, 'height', None) or int(attrs.size) * 18 - 1 + attrs.vspace * 2))
        c = uicls.Combo(name='selection_%s' % attrs.name, align=uiconst.RELATIVE)
        if getattr(attrs, 'width', None) is not None:
            c.width = getattr(attrs, 'width', None)
        return c



    def Startup_select(self, wnd, attrs):
        if getattr(attrs, 'size', None) is not None or getattr(attrs, 'height', 0):
            wnd.Startup([ (k, v, s) for (k, v, s,) in attrs.options ])
            if not hasattr(attrs, 'multiple'):
                wnd.multiSelect = 0
            for each in wnd.children:
                if each.name in ('_underlay',):
                    each.Close()
                if each.name == 'activeframe':
                    uiutil.Flush(each)
                    uicls.Frame(parent=each, color=self.browser.attrStack[-1]['color'], padding=(-1, -1, -1, -1))

            uicls.Line(parent=wnd, align=uiconst.TOTOP, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Container(name='push', parent=wnd, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             attrs.vspace), idx=0)
            uicls.Container(name='push', parent=wnd, align=uiconst.TOBOTTOM, pos=(0,
             0,
             0,
             attrs.vspace), idx=0)
        else:
            default = None
            for (key, value, selected,) in attrs.options:
                if selected:
                    default = key
                    break

            if getattr(attrs, 'width', None) is not None:
                wnd.Startup([ (k, v) for (k, v, s,) in attrs.options ], default=default)
            else:
                wnd.Startup([ (k, v) for (k, v, s,) in attrs.options ], default=default, adjustWidth=1)
            clipper = uiutil.GetChild(wnd, 'clipper')
            clipper.clipChildren = 1
            for each in wnd.children:
                if each.name == 'selected':
                    wnd.sr.activeframe = uicls.Frame(parent=each, color=getattr(attrs, 'fontcolor', None), padding=(-1, -1, -1, -1))
                    wnd.sr.activeframe.state = uiconst.UI_HIDDEN
                    uicls.Frame(parent=each, color=getattr(attrs, 'fontcolor', None))
                    uicls.Container(name='push', parent=each, align=uiconst.TOTOP, pos=(0,
                     0,
                     0,
                     attrs.vspace), idx=0)
                    uicls.Container(name='push', parent=each, align=uiconst.TOBOTTOM, pos=(0,
                     0,
                     0,
                     attrs.vspace), idx=0)
                    for child in each.children:
                        if child.name in ('_underlay',):
                            child.Close()

                    break




    def GetValue_select(self, wnd, attrs):
        v = wnd.GetValue()
        if getattr(wnd, 'multiSelect', 1) == 0 and type(v) == list:
            return v[0]
        return v



    def SetValue_select(self, wnd, attrs, val):
        wnd.SetValue(val)



    def Create_submit(self, attrs):
        wnd = uicls.Button(parent=None)
        if getattr(attrs, 'value', None) and mls.HasLabel('UI_CMD_' + getattr(attrs, 'value', None).upper()):
            label = getattr(mls, 'UI_CMD_' + getattr(attrs, 'value', None).upper())
        else:
            label = (getattr(attrs, 'value', None) or mls.UI_CMD_SUBMIT).replace('>', '&gt;').replace('<', '&lt;')
        wnd.SetLabel(label)
        if getattr(attrs, 'width', None) is not None:
            wnd.width = int(attrs.width)
        wnd.OnClick = self.OnSubmit
        attrs.vspace = 0
        if getattr(attrs, 'fontcolor', None):
            (r, g, b, a,) = getattr(attrs, 'fontcolor', (1.0, 1.0, 1.0, 1.0))
        return wnd




class Css():
    __guid__ = 'corebrowserutil.Css'

    def __init__(self):
        self.Reset()



    def Reset(self):
        self.classes = []
        self.s = {}



    def copy(self):
        new = Css()
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
            self.s['font-family'] = 'sans'



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
    fontFamilies = {8: 'sans',
     10: 'sans',
     12: 'sans',
     14: 'sans',
     20: 'sans'}
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


def GetStringFromURL(url, data = None, cookie = None):
    if cookie:
        header = {'Cookie': cookie}
    else:
        header = {}
    header['User-Agent'] = 'CCP-minibrowser/3.0'
    for (k, v,) in header.iteritems():
        if isinstance(v, unicode):
            header[k] = v.encode('ascii', 'xmlcharrefreplace')
        else:
            header[k] = str(v)

    try:
        url = url.encode('ascii')
    except:
        if not url.startswith('file:'):
            raise urllib2.URLError('URL contained non-ascii characters')
    try:
        r = urllib2.Request(url, data, header)
        if url.lower().find('local://') == 0:
            return OpenLocalURL(url, r, data, cookie)
        else:
            return urllib2.urlopen(r)
    except ValueError as what:
        if what.args[0].startswith('invalid literal for int():'):
            raise urllib2.URLError('malformed URL')
        raise 



def OpenLocalURL(url, r, data, cookie):
    path = url[(url.find(':') + 2):]

    class FakeSocket:

        def __init__(self, req, data):
            self.request = req
            self.header = ['HTTP']
            self.buff = ''
            self.isFake = True
            method = 'GET'
            contentLength = ''
            contentType = ''
            post = ''
            if data:
                method = 'POST'
                contentLength = 'Content-Length: %s\r\n' % len(data)
                contentType = 'Content-Type: application/x-www-form-urlencoded\r\n'
                post = data + '\r\n'
            self.buff = '%(method)s %(path)s HTTP/1.0\r\nHost: dummy:0\r\nUser-agent: EVE\r\nEve.trusted: no\r\n%(contenttype)s%(contentlength)s\r\n%(data)s\r\n' % {'method': method,
             'path': path,
             'contenttype': contentType,
             'contentlength': contentLength,
             'data': post}



        def Read(self):
            return self.buff



        def Write(self, what):
            self.buff = what




    class FakeInfo:

        def __init__(self):
            self.headers = {}




    class FakeResponse:

        def __init__(self, buf):
            self.buf = buf
            self.inf = FakeInfo()
            self.url = ''
            self.headers = {}



        def read(self):
            return self.buf



        def info(self):
            return self.inf



    fakeSocket = FakeSocket(r, data)
    import gps
    ep = gps.RawTransport(fakeSocket, '')
    conn = sm.GetService('http')
    conn.Handle(ep)
    buf = ep.Read()
    code = int(buf[9:12])
    if code == 302:
        lines = buf.split('\r\n')
        loc = ''
        lkey = 'location: '
        for l in lines:
            if l.lower().find(lkey) >= 0:
                loc = l[len(lkey):]
                break

        (loc, a,) = ParseURL(loc, 'local://')
        return GetStringFromURL(loc, data, cookie)
    content = buf[(buf.find('\r\n\r\n') + 4):]
    return FakeResponse(content)



def ParseURL(url, current = None):
    url = url.encode('ascii')
    if current:
        current = current.encode('ascii')
        if current.find('local://') == 0 and url.find('://') == -1:
            url = 'local://' + url
        else:
            url = urlparse.urljoin(current, url)
    elif url.find(':/') == -1:
        url = 'http://' + url
    repl = None
    if 'res:/' in url:
        repl = ('res:/', blue.os.respath)
    elif 'script:/' in url:
        repl = ('script:/', blue.os.scriptpath)
    elif 'cache:/' in url:
        repl = ('cache:/', blue.os.cachepath)
    if repl:
        url = url.replace(repl[0], 'file:' + nturl2path.pathname2url(repl[1]))
    (scheme, netloc, path, query, fragment,) = urlparse.urlsplit(url)
    return (urlparse.urlunsplit((scheme,
      netloc,
      path,
      query,
      '')), fragment)



def DirUp(url, force = 1):
    i = url[:-1].rfind('/')
    if i == -1:
        if force:
            raise ValueError, 'Bad URL (no parent dir): %s' % url
        return url
    return url[:i] + '/'



def DefaultHomepage():
    import browserutil
    if hasattr(browserutil, 'DefaultHomepage'):
        home = browserutil.DefaultHomepage()
    if home is not None:
        return home
    return 'http://www.google.com'



def DefaultCachePath():
    return blue.os.cachepath + 'Browser/'



class CrashedBrowserViewHost(object):
    alive = False

    def __getattr__(self, attr):
        return CrashedBrowserViewHostAttribute(attr)



    def __setattr__(self, attr, value):
        pass




class CrashedBrowserViewHostAttribute():

    def __init__(self, attr):
        self.attr = attr



    def __call__(self, *args, **kwargs):
        print 'Calling %s%s%s on a crashed BrowserView' % (self.attr, args, kwargs)



    def __repr__(self):
        return '<CrashedBrowserViewHostAttribute %s>' % self.attr




def NextPowerOfTwo(n):
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1



class LoadErrors():
    BLACKLIST = 100
    WHITELIST = 101
    FAILED = -2
    ABORTED = -3
    FILE_NOT_FOUND = -4
    OPERATION_TIMED_OUT = -7
    ACCESS_DENIED = -10
    CONNECTION_CLOSED = -100
    CONNECTION_RESET = -101
    CONNECTION_REFUSED = -102
    CONNECTION_ABORTED = -103
    CONNECTION_FAILED = -104
    NAME_NOT_RESOLVED = -105
    INTERNET_DISCONNECTED = -106
    SSL_PROTOCOL_ERROR = -107
    ADDRESS_INVALID = -108
    ADDRESS_UNREACHABLE = -109
    CERT_ERRORS_BEGIN = -200
    CERT_COMMON_NAME_INVALID = -200
    CERT_DATE_INVALID = -201
    CERT_AUTHORITY_INVALID = -202
    CERT_CONTAINS_ERRORS = -203
    CERT_NO_REVOCATION_MECHANISM = -204
    CERT_UNABLE_TO_CHECK_REVOCATION = -205
    CERT_REVOKED = -206
    CERT_INVALID = -207
    CERT_ERRORS_END = -208
    INVALID_URL = -300
    DISALLOWED_URL_SCHEME = -301
    UNKNOWN_URL_SCHEME = -302
    TOO_MANY_REDIRECTS = -311
    UNSAFE_PORT = -312
    INVALID_RESPONSE = -320
    INVALID_CHUNKED_ENCODING = -321
    METHOD_NOT_SUPPORTED = -322
    UNEXPECTED_PROXY_AUTH = -323
    EMPTY_RESPONSE = -324
    RESPONSE_HEADERS_TOO_BIG = -325


def GetErrorString(errorCode):
    errorString = ''
    if errorCode == LoadErrors.FILE_NOT_FOUND:
        errorString += mls.UI_SHARED_HTMLERROR1
    elif errorCode == LoadErrors.OPERATION_TIMED_OUT:
        errorString += mls.UI_BROWSER_LOAD_ERROR_TIMED_OUT
    elif errorCode == LoadErrors.ACCESS_DENIED:
        errorString += mls.UI_GENERIC_ACCESSDENIED
    elif errorCode == LoadErrors.CONNECTION_CLOSED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_CLOSED
    elif errorCode == LoadErrors.CONNECTION_RESET:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_RESET
    elif errorCode == LoadErrors.CONNECTION_REFUSED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_REFUSED
    elif errorCode == LoadErrors.CONNECTION_ABORTED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_ABORTED
    elif errorCode == LoadErrors.CONNECTION_FAILED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_FAILED
    elif errorCode == LoadErrors.NAME_NOT_RESOLVED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_NAME_NOT_RESOLVED
    elif errorCode == LoadErrors.INTERNET_DISCONNECTED:
        errorString += mls.UI_BROWSER_LOAD_ERROR_CONNECTION_LOST
    elif errorCode == LoadErrors.ADDRESS_INVALID:
        errorString += mls.UI_BROWSER_LOAD_ERROR_ADDRESS_INVALID
    elif errorCode == LoadErrors.ADDRESS_UNREACHABLE:
        errorString += mls.UI_BROWSER_LOAD_ERROR_ADDRESS_UNREACHABLE
    elif errorCode <= LoadErrors.CERT_ERRORS_BEGIN and errorCode >= LoadErrors.CERT_ERRORS_END or errorCode == LoadErrors.SSL_PROTOCOL_ERROR:
        if errorCode == LoadErrors.CERT_COMMON_NAME_INVALID:
            errorString += mls.UI_BROWSER_LOAD_ERROR_CERT_NAME_MISMATCH
        elif errorCode == LoadErrors.CERT_DATE_INVALID:
            errorString += mls.UI_BROWSER_LOAD_ERROR_CERT_EXPIRED
        else:
            errorString += mls.UI_BROWSER_LOAD_ERROR_CERT_ERRORS
    elif errorCode == LoadErrors.INVALID_URL or errorCode == LoadErrors.DISALLOWED_URL_SCHEME or errorCode == LoadErrors.UNKNOWN_URL_SCHEME:
        errorString += mls.UI_BROWSER_LOAD_ERROR_INVALID_URL
    elif errorCode == LoadErrors.INVALID_RESPONSE or errorCode == LoadErrors.EMPTY_RESPONSE or errorCode == LoadErrors.RESPONSE_HEADERS_TOO_BIG:
        errorString += mls.UI_BROWSER_LOAD_ERROR_RESPONSE_INVALID
    return errorString


exports = {'corebrowserutil.ParseURL': ParseURL,
 'corebrowserutil.DirUp': DirUp,
 'corebrowserutil.GetStringFromURL': GetStringFromURL,
 'corebrowserutil.DefaultHomepage': DefaultHomepage,
 'corebrowserutil.DefaultCachePath': DefaultCachePath,
 'corebrowserutil.CrashedBrowserViewHost': CrashedBrowserViewHost,
 'corebrowserutil.LoadErrors': LoadErrors,
 'corebrowserutil.GetErrorString': GetErrorString,
 'corebrowserutil.NextPowerOfTwo': NextPowerOfTwo}

