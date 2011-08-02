import uix
import uiutil
import xtriui
import urllib
import blue
import trinity
import util
import re
import uicls
import uiconst

class NewBrowserForm:
    __guid__ = 'browserutil.NewBrowserForm'

    def __init__(self, attrs, browser):
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
            eve.Message('Busy')
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
        if getattr(self.attrs, 'action', None) is None:
            setattr(self.attrs, 'action', browser.sr.currentURL.split('?')[0])
        if getattr(self.attrs, 'method', 'get').lower() == 'get':
            if 'localsvc:' in self.attrs.action:
                import parser
                import uthread
                uicls.BaseLink().LocalSvcCall(self.attrs.action[9:] + ''.join([ name for (name, value,) in d ]))
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
        if hasattr(wnd, 'sr') and hasattr(wnd.sr, 'label') and hasattr(wnd.sr.label, 'text'):
            wnd.name = 'htmlButton%s' % wnd.sr.label.text.capitalize()
        browser = uiutil.GetBrowser(self.browser)
        if not browser:
            return 
        if add:
            self.fields.append((attrs, wnd))
        attrs.control = wnd
        attrs.align = getattr(attrs, 'align', None)
        obj = util.KeyVal()
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
        if getattr(attrs, 'readonly', False):
            wnd = uicls.Edit(align=uiconst.RELATIVE)
        else:
            wnd = uicls.EditPlainText(align=uiconst.RELATIVE)
        wnd.width = getattr(attrs, 'width', None) or 8 * int(attrs.cols) or 350
        wnd.height = getattr(attrs, 'height', None) or 18 * int(attrs.rows) or 45
        return wnd



    def Startup_textarea(self, wnd, attrs):
        wnd.Startup(showattributepanel=0)
        if getattr(attrs, 'maxlength', None):
            wnd.SetMaxLength(attrs.maxlength)
        if hasattr(attrs, 'readonly'):
            wnd.ReadOnly()
        if attrs.value:
            wnd.SetValue(attrs.value)
        color = self.browser.attrStack[-1]['color']
        uicls.Line(parent=wnd, align=uiconst.TOTOP, color=color)
        uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=color)
        uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=color)
        uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=color)



    def GetValue_textarea(self, wnd, attrs):
        return wnd.GetValue().replace('<br>', '\r\n')


    SetValue_textarea = StdSetValue

    def Create_text(self, attrs):
        wnd = uicls.SinglelineEdit(name='textedit', width=getattr(attrs, 'width', None) or min(200, 7 * (attrs.size or 30)), height=16, align=uiconst.RELATIVE)
        return wnd



    def Startup_text(self, wnd, attrs, password = 0):
        wnd.Startup()
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
            uicls.Line(parent=wnd, align=uiconst.TOTOP, color=color)
            uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=color)
            uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=color)
            uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=color)


    GetValue_text = StdGetValue
    SetValue_text = StdSetValue
    Create_password = Create_text

    def Startup_password(self, wnd, attrs):
        self.Startup_text(wnd, attrs, password=1)
        wnd.SetPasswordChar('\x95')


    GetValue_password = StdGetValue
    SetValue_password = StdSetValue

    def Create_checkbox(self, attrs):
        cbox = uicls.Checkbox(align=uiconst.TOPLEFT)
        cbox.width = cbox.height = 14
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
            return xtriui.Select(name='select', align=uiconst.TOPLEFT, height=getattr(attrs, 'height', None) or int(attrs.size) * 18 - 1 + attrs.vspace * 2, width=getattr(attrs, 'width', None) or 128)
        c = xtriui.Combo(align=uiconst.TOPLEFT, name='selection_%s' % attrs.name)
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
                    uix.Flush(each)
                    uicls.Frame(parent=each, color=self.browser.attrStack[-1]['color'], padding=(-1, -1, -1, -1))

            uicls.Line(parent=wnd, align=uiconst.TOLEFT, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TORIGHT, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOBOTTOM, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Line(parent=wnd, align=uiconst.TOTOP, color=getattr(attrs, 'fontcolor', None), weight=1)
            uicls.Container(name='push', parent=wnd, align=uiconst.TOTOP, height=attrs.vspace, idx=0)
            uicls.Container(name='push', parent=wnd, align=uiconst.TOBOTTOM, height=attrs.vspace, idx=0)
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
                    uicls.Container(name='push', parent=each, align=uiconst.TOTOP, height=attrs.vspace, idx=0)
                    uicls.Container(name='push', parent=each, align=uiconst.TOBOTTOM, height=attrs.vspace, idx=0)
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
        wnd = uicls.Button()
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
            rgba = getattr(attrs, 'fontcolor', (1.0, 1.0, 1.0, 1.0))
            wnd.sr.activeframe.color.SetRGB(*rgba)
        return wnd




