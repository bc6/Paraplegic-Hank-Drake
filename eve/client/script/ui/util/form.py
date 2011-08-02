import service
import uix
import uiutil
import blue
import uthread
import xtriui
import log
import util
import types
import form
import uiconst
import uicls

class Form(service.Service):
    __guid__ = 'svc.form'
    __exportedcalls__ = {'GetForm': [],
     'ProcessForm': []}
    __servicename__ = 'form'
    __displayname__ = 'Form Service'
    __dependencies__ = []

    def __init__(self):
        service.Service.__init__(self)



    def GetForm(self, format, parent):
        (_form, retfields, reqresult, panels, errorcheck, refresh,) = self._GetForm(format, parent)
        if _form.align == uiconst.TOALL:
            _form.SetSize(0, 0)
            _form.SetPosition(0, 0)
            _form.SetPadding(const.defaultPadding, const.defaultPadding, const.defaultPadding, const.defaultPadding)
        elif _form.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
            _form.SetPosition(0, 0)
            _form.width = 0
            _form.SetPadding(const.defaultPadding, const.defaultPadding, const.defaultPadding, const.defaultPadding)
        elif _form.align in (uiconst.TOLEFT, uiconst.TORIGHT):
            _form.SetPosition(0, 0)
            _form.height = 0
            _form.SetPadding(const.defaultPadding, const.defaultPadding, const.defaultPadding, const.defaultPadding)
        else:
            _form.left = _form.top = const.defaultPadding
        return (_form,
         retfields,
         reqresult,
         panels,
         errorcheck,
         refresh)



    def _GetForm(self, format, parent, retfields = [], reqresult = [], errorcheck = None, tabpanels = [], tabgroup = [], refresh = [], wipe = 1):
        if not uiutil.IsUnder(parent, uicore.desktop):
            log.LogTraceback('Form parent MUST be hooked on the desktop; it is impossible to know the real dimensions of stuff within otherwise.')
        self.retfields = retfields
        self.reqresult = reqresult
        self.errorcheck = errorcheck
        self.tabpanels = tabpanels
        self.tabgroup = tabgroup
        self.refresh = refresh
        if not isinstance(parent, xtriui.FormWnd):
            log.LogTraceback('Incompatible formparent, please change it to xtriui.FormWnd')
        self.parent = parent
        self.parent.sr.panels = {}
        self.parent.sr.focus = None
        if wipe:
            self.retfields = []
            self.reqresult = []
            self.tabpanels = []
            self.tabgroup = []
            self.refresh = []
        for each in format:
            self.type = each
            typeName = self.type['type']
            self.leftPush = self.type.get('labelwidth', 0) or 80
            self.code = None
            if typeName == 'errorcheck':
                self.AddErrorcheck()
                continue
            elif typeName == 'data':
                self.AddData()
                continue
            elif typeName == 'tab':
                self.AddTab()
                continue
            elif typeName in ('btline', 'bbline'):
                self.AddLine()
                continue
            elif typeName == 'push':
                self.AddPush()
            elif typeName == 'header':
                self.AddHeader()
            elif typeName == 'labeltext':
                self.AddLabeltext()
            elif typeName == 'text':
                self.AddText()
            elif typeName == 'edit':
                self.AddEdit()
            elif typeName == 'textedit':
                self.AddTextedit()
            elif typeName == 'checkbox':
                self.AddCheckbox()
            elif typeName == 'combo':
                self.AddCombo()
            elif typeName == 'btnonly':
                self.AddBtnonly()
            else:
                log.LogWarn('Unknown fieldtype in form generator')
                continue
            if self.type.has_key('key'):
                if self.code:
                    self.retfields.append([self.code, self.type])
                    self.parent.sr.Set(self.type['key'], self.code)
                else:
                    self.parent.sr.Set(self.type['key'], self.new)
            if self.type.get('required', 0) == 1:
                self.reqresult.append([self.code, self.type])
            if self.type.get('selectall', 0) == 1 and getattr(self.code, 'SelectAll', None):
                self.code.SelectAll()
            if self.type.get('setfocus', 0) == 1:
                self.parent.sr.focus = self.code
            if self.type.has_key('stopconfirm') and hasattr(self.code, 'stopconfirm'):
                self.code.stopconfirm = self.type['stopconfirm']
            if self.type.get('frame', 0) == 1:
                idx = 0
                for child in self.new.children:
                    if child.name.startswith('Line'):
                        idx += 1

                uicls.Container(name='leftpush', parent=self.new, align=uiconst.TOLEFT, width=6, idx=idx)
                uicls.Container(name='rightpush', parent=self.new, align=uiconst.TORIGHT, width=6, idx=idx)
                uicls.Line(parent=self.new, align=uiconst.TOLEFT, idx=idx)
                uicls.Line(parent=self.new, align=uiconst.TORIGHT, idx=idx)

        if wipe and len(self.tabgroup):
            tabs = uicls.TabGroup(name='tabparent', parent=self.parent, idx=0)
            tabs.Startup(self.tabgroup, 'hybrid')
            maxheight = 0
            for panel in self.tabpanels:
                maxheight = max(maxheight, panel.height)

            self.parent.height = maxheight + tabs.height
        elif len(self.tabpanels):
            for each in self.tabpanels:
                each.state = uiconst.UI_HIDDEN

            self.tabpanels[0].state = uiconst.UI_PICKCHILDREN
        uix.RefreshHeight(self.parent)
        uicore.registry.SetFocus(self)
        return (self.parent,
         self.retfields,
         self.reqresult,
         self.tabpanels,
         self.errorcheck,
         self.refresh)



    def AddErrorcheck(self):
        self.errorcheck = self.type['errorcheck']



    def AddData(self):
        self.retfields.append(self.type['data'])



    def AddTab(self):
        (_form, _retfield, _required, _tabpanels, _errorcheck, _refresh,) = self._GetForm(self.type['format'], xtriui.FormWnd(name='form', align=uiconst.TOTOP, parent=self.parent), self.retfields, self.reqresult, self.errorcheck, self.tabpanels, self.tabgroup, self.refresh, 0)
        if self.type.has_key('key'):
            self.parent.sr.panels[self.type['key']] = _form
        if self.type.get('panelvisible', 0):
            _form.state = uiconst.UI_PICKCHILDREN
        else:
            _form.state = uiconst.UI_HIDDEN
        if self.type.has_key('tabvisible'):
            if self.type['tabvisible'] == 1:
                self.tabgroup.append([self.type['tabtext'],
                 _form,
                 self,
                 None])
        else:
            self.tabgroup.append([self.type['tabtext'],
             _form,
             self,
             None])



    def AddPush(self):
        self.new = uicls.Container(name='push', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 6))



    def AddLine(self):
        uicls.Line(parent=self.parent, align=uiconst.TOTOP)



    def AddHeader(self):
        self.new = uicls.Container(name='headerField', parent=self.parent, align=uiconst.TOTOP)
        header = uicls.Label(text=self.type.get('text', ''), parent=self.new, name='header', padding=(7, 3, 7, 3), fontsize=9, letterspace=2, uppercase=1, linespace=9, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.new.height = max(self.type.get('height', 17), header.textheight + header.padTop * 2)
        self.refresh.append((self.new, header))
        if not self.type.get('hideLine', False):
            uicls.Line(parent=self.new, align=uiconst.TOTOP, padLeft=-6, padRight=-6, idx=0)
            uicls.Line(parent=self.new, align=uiconst.TOBOTTOM, padLeft=-6, padRight=-6, idx=0)



    def AddLabeltext(self):
        self.new = uicls.Container(name='labeltextField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20))
        text = uicls.Label(text=self.type.get('text', ''), parent=self.new, align=uiconst.TOTOP, name='text', padding=(self.leftPush,
         3,
         0,
         0), state=uiconst.UI_NORMAL)
        label = self.type.get('label', '')
        if label and label != '_hide':
            label = uicls.Label(text=label, parent=self.new, name='label', left=7, width=self.leftPush - 6, top=5, fontsize=9, letterspace=2, uppercase=1, linespace=9)
            self.refresh.append((self.new, text, label))
        else:
            self.refresh.append((self.new, text))



    def AddText(self):
        left = self.type.get('left', 0)
        self.new = uicls.Container(name='textField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20), padding=(left,
         0,
         0,
         0))
        fontsize = self.type.get('fontsize', 12)
        text = uicls.Label(text=self.type.get('text', ''), parent=self.new, align=uiconst.TOTOP, name='text', padding=(0, 3, 0, 3), fontsize=fontsize, singleline=bool(self.type.get('tabstops', [])), state=uiconst.UI_NORMAL, tabs=self.type.get('tabstops', []))
        self.new.height = max(self.new.height, int(text.textheight + 6))
        self.refresh.append((self.new, text))



    def AddEdit(self):
        self.new = uicls.Container(name='editField', parent=self.parent, align=uiconst.TOTOP)
        config = 'edit_%s' % self.type['key']
        self.code = uicls.SinglelineEdit(name=config, parent=self.new, setvalue=self.type.get('setvalue', ''), padding=(self.leftPush,
         2,
         0,
         2), ints=self.type.get('intonly', None), floats=self.type.get('floatonly', None), align=uiconst.TOTOP, maxLength=self.type.get('maxlength', None) or self.type.get('maxLength', None), passwordCharacter=self.type.get('passwordChar', None), readonly=self.type.get('readonly', 0), autoselect=self.type.get('autoselect', 0))
        self.new.height = self.code.height + self.code.padTop * 2
        width = self.type.get('width', None)
        if width:
            self.code.SetAlign(uiconst.TOLEFT)
            self.code.width = width
        if self.type.has_key('OnReturn'):
            self.code.data = {'key': self.type['key']}
            self.code.OnReturn = self.type['OnReturn']
        if self.type.has_key('unusedkeydowncallback'):
            self.code.OnUnusedKeyDown = self.type['unusedkeydowncallback']
        if self.type.has_key('onanychar'):
            self.code.OnAnyChar = self.type['onanychar']
        label = self.type.get('label', '')
        text = self.type.get('text', None)
        caption = text or label
        if label == '_hide':
            self.code.padLeft = 0
        elif caption:
            l = uicls.Label(text=caption, align=uiconst.CENTERLEFT, parent=self.new, name='label', left=7, width=self.leftPush - 6, fontsize=9, letterspace=2, uppercase=1, linespace=9)



    def AddTextedit(self):
        self.new = uicls.Container(name='texteditField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 68))
        self.code = uicls.EditPlainText(setvalue=self.type.get('setvalue', '') or self.type.get('text', ''), parent=self.new, padding=(self.leftPush,
         2,
         0,
         2), readonly=self.type.get('readonly', 0), showattributepanel=self.type.get('showAttribPanel', 0), maxLength=self.type.get('maxlength', None) or self.type.get('maxLength', None))
        label = self.type.get('label', '')
        if label == '_hide':
            self.code.padLeft = 0
        elif label:
            uicls.Label(text=label, parent=self.new, name='label', left=7, width=self.leftPush - 6, top=5, fontsize=9, letterspace=2, uppercase=1, linespace=9)



    def AddCheckbox(self):
        self.new = uicls.Container(name='checkboxCont', parent=self.parent, align=uiconst.TOTOP, pos=(0, 0, 0, 18))
        self.code = uicls.Checkbox(text=self.type.get('text', ''), parent=self.new, configName='none', retval=self.type['key'], checked=self.type.get('setvalue', 0), groupname=self.type.get('group', None), callback=self.parent.OnCheckboxChange)
        self.code.data = {}
        onchange = self.type.get('OnChange', None) or self.type.get('onchange', None)
        if onchange:
            self.code.data = {'key': self.type['key'],
             'callback': onchange}
        if self.type.has_key('showpanel'):
            self.code.data['showpanel'] = self.type['showpanel']
        if self.code.sr.label:
            self.refresh.append((self.code, self.code.sr.label))
        if self.type.get('hidden', 0):
            self.code.state = uiconst.UI_HIDDEN



    def AddCombo(self):
        self.new = uicls.Container(name='comboField', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20))
        options = self.type.get('options', [(mls.UI_GENERIC_NONE, None)])
        self.code = uicls.Combo(label='', parent=self.new, options=options, name=self.type.get('key', 'combo'), select=self.type.get('setvalue', ''), padding=(self.leftPush,
         2,
         0,
         2), align=uiconst.TOTOP, callback=self.type.get('callback', None), labelleft=self.leftPush)
        self.new.height = self.code.height + self.code.padTop * 2
        width = self.type.get('width', None)
        if width:
            self.code.SetAlign(uiconst.TOLEFT)
            self.code.width = width
        label = self.type.get('label', '')
        if label == '_hide':
            self.code.padLeft = 0
        else:
            uicls.Label(text=label, parent=self.new, name='label', left=7, width=self.leftPush - 6, fontsize=9, letterspace=2, uppercase=1, linespace=9, align=uiconst.CENTERLEFT)



    def AddBtnonly(self):
        self.new = uicls.Container(name='btnonly', parent=self.parent, align=uiconst.TOTOP, height=self.type.get('height', 20))
        btns = []
        align = uiconst.TORIGHT
        for wantedbtn in self.type['buttons']:
            if wantedbtn.has_key('align'):
                al = {'left': uiconst.CENTERLEFT,
                 'right': uiconst.CENTERRIGHT}
                align = al.get(wantedbtn['align'], uiconst.CENTERRIGHT)
            btns.append([wantedbtn['caption'],
             wantedbtn['function'],
             wantedbtn.get('args', 'self'),
             None,
             wantedbtn.get('btn_modalresult', 0),
             wantedbtn.get('btn_default', 0),
             wantedbtn.get('btn_cancel', 0)])

        btns = uicls.ButtonGroup(btns=btns, subalign=align, line=0, parent=self.new, padTop=4, align=uiconst.TOTOP, unisize=self.type.get('uniSize', 1))



    def ProcessForm(self, retfields, required, errorcheck = None):
        result = {}
        for each in retfields:
            if type(each) == dict:
                result.update(each)
                continue
            value = each[0].GetValue()
            if each[1]['type'] == 'checkbox' and each[1].has_key('group') and value == 1:
                result[each[1]['group']] = each[1]['key']
            else:
                result[each[1]['key']] = value

        if errorcheck:
            hint = errorcheck(result)
            if hint == 'silenterror':
                return 
            if hint:
                eve.Message('CustomInfo', {'info': hint})
                return 
        if len(required):
            for each in required:
                retval = each[0].GetValue()
                if retval is None or retval == '' or type(retval) in types.StringTypes and retval.strip() == '':
                    fieldname = ''
                    if each[1].has_key('label'):
                        fieldname = each[1]['label']
                        if fieldname == '_hide':
                            fieldname = each[1]['key']
                    else:
                        fieldname = each[1]['key']
                    eve.Message('MissingRequiredField', {'fieldname': fieldname})
                    return 
                if each[1]['type'] == 'checkbox' and each[1].has_key('group'):
                    if each[1]['group'] not in result:
                        eve.Message('MissingRequiredField', {'fieldname': each[1]['group']})
                        return 

        return result




class FormWnd(uicls.Container):
    __guid__ = 'xtriui.FormWnd'

    def _OnClose(self):
        uicls.Container._OnClose(self)
        windowKeys = self.sr.panels.keys()
        for key in windowKeys:
            if not self.sr.panels.has_key(key):
                continue
            wnd = self.sr.panels[key]
            del self.sr.panels[key]
            if wnd is not None and not wnd.destroyed:
                wnd.Close()

        self.sr.panels = None



    def ShowPanel(self, panelkey):
        for key in self.sr.panels:
            self.sr.panels[key].state = uiconst.UI_HIDDEN

        self.sr.panels[panelkey].state = uiconst.UI_NORMAL



    def OnCheckboxChange(self, sender, *args):
        if sender.data.has_key('callback'):
            sender.data['callback'](sender)
        if sender.data.has_key('showpanel') and self.sr.panels.has_key(sender.data['showpanel']):
            self.ShowPanel(sender.data['showpanel'])



    def OnChange(self, *args):
        pass




