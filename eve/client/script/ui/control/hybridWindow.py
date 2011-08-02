import uix
import uiutil
import xtriui
import form
import uthread
import blue
import util
import types
import sys
import draw
import uicls
import uiconst

class HybridWindow(uicls.Window):
    __guid__ = 'form.HybridWindow'
    __nonpersistvars__ = ['isModal',
     'scrolllist',
     'listentry',
     'result',
     'listtype',
     'fields',
     'reqresult',
     'retfields',
     'tabpanels',
     'tabs',
     'tabparents',
     'minh',
     'minw',
     'refreshHeight',
     'checkingtabs',
     'activetab',
     'settingheight',
     'wndID',
     'panels',
     'errorcheck',
     'OnConfirm']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.ResetSelf()
        format = attributes.format
        caption = attributes.caption
        modal = attributes.modal
        wndID = attributes.wndID
        buttons = attributes.buttons
        location = attributes.location
        minw = attributes.get('minW', 320)
        minh = attributes.get('minH', 240)
        icon = attributes.icon
        blockconfirm = attributes.get('blockconfirm', False)
        self.name = caption
        self.result = {}
        self.isModal = modal
        self.wndID = wndID
        self.blockconfirmonreturn = blockconfirm
        self.sr.topParent.align = uiconst.TOALL
        self.sr.topParent.height = 0
        iconClipper = uiutil.FindChild(self, 'iconclipper')
        if iconClipper:
            iconClipper.top = -1
        uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TORIGHT, width=const.defaultPadding)
        uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TOTOP, height=const.defaultPadding)
        main = uiutil.GetChild(self, 'main')
        if icon:
            uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TOLEFT, width=60)
            self.DefineIcons(icon)
        else:
            uicls.Container(name='push', parent=self.sr.topParent, align=uiconst.TOLEFT, width=const.defaultPadding)
            self.HideMainIcon()
            self.HideClippedIcon()
        self.state = uiconst.UI_HIDDEN
        self.DefineButtons(buttons)
        self.MakeUnMinimizable()
        self.MakeUncollapseable()
        self.MakeUnpinable()
        self.SetCaption(caption)
        self.SetMinSize([minw, minh], 1)
        (self.form, self.retfields, self.reqresult, self.panels, self.errorcheck, refresh,) = sm.GetService('form').GetForm(format, xtriui.FormWnd(name='form', align=uiconst.TOTOP, parent=self.sr.topParent))
        self.form.OnChange = self.OnChange
        for each in self.form.sr.panels.itervalues():
            each.OnChange = self.OnChange

        self.refresh = refresh
        for each in refresh:
            for textControl in each[1:]:
                textControl.OnSizeChanged = self.UpdateTextControlSize


        self.state = self.form.state = uiconst.UI_NORMAL
        self.width = self.minsize[0]
        if self.form.sr.focus:
            uicore.registry.SetFocus(self.form.sr.focus)
        else:
            uicore.registry.SetFocus(self)
        uthread.new(self.RefreshSize_, 1)



    def UpdateTextControlSize(self, *args):
        self.RefreshSize_()



    def ResetSelf(self):
        self.scrolllist = None
        self.listentry = None
        self.reqresult = []
        self.retfields = []
        self.tabpanels = []
        self.tabparents = []
        self.result = {}
        self.tabs = []
        self.minh = 0
        self.minw = 240
        self.refreshHeight = []
        self.onconfirmargs = ()
        self.checkingtabs = 0
        self.settingheight = 0
        self.activetab = None
        self.refresh = None
        self.form = None
        self.sr.queue = None
        self.locked = 0



    def OnClose_(self, *args):
        if self.sr.queue is not None:
            self.sr.queue.send(None)
        self.form.OnChange = None
        self.form.sr.focus = None
        for each in self.form.sr.panels.itervalues():
            each.OnChange = None

        self.form.Close()
        self.form = None
        self.retfields = None
        self.reqresult = None
        self.panels = None
        self.errorcheck = None
        main = uiutil.GetChild(self, 'main')
        uix.Flush(main)
        self.ResetSelf()



    def OnChange(self, *args):
        self.OnScale_(*args)



    def OnScale_(self, *args):
        self.RefreshSize_()



    def OnEndScale_(self, *args):
        self.RefreshSize_()



    def RefreshSize_(self, update = 0, *args):
        self.RefreshTextControls(self.refresh)
        if self.locked:
            return 
        minformheight = 0
        notformheight = 0
        hasTab = 0
        minw = 0
        for each in self.form.children:
            if each.name == 'form':
                for each2 in each.children:
                    if each2.name == 'form':
                        uix.RefreshHeight(each2)

                uix.RefreshHeight(each)
                minformheight = max(minformheight, each.height)
            elif each.name == 'tabparent':
                hasTab = 1
                if each.width > minw:
                    minw = each.width
            else:
                notformheight += each.height

        if self.form.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
            self.form.height = minformheight + notformheight
        totHeight = minformheight + sum([ each.height + each.padTop + each.padBottom for each in self.form.parent.children if each.align in (uiconst.TOTOP, uiconst.TOBOTTOM) ])
        if hasTab == 1:
            if self.minsize[0] < minw:
                self.minsize[0] = minw
        preheight = self.height
        minHeight = totHeight + (self.sr.stack is not None) * 6 + 51
        if minHeight > self.minsize[1]:
            self.SetMinSize([self.minsize[0], minHeight], 1)



    def RefreshTextControls(self, rlist):
        for each in rlist:
            itemToUpdate = each[0]
            m = 0
            for textcontrol in each[1:]:
                if textcontrol.GetAlign() in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
                    m = max(m, textcontrol.textheight + textcontrol.padTop + textcontrol.padBottom)
                else:
                    m = max(m, textcontrol.textheight + textcontrol.top * 2)

            itemToUpdate.height = m




    def Execute(self):
        if self.sr.queue is not None:
            raise RuntimeError('already executing?')
        self.sr.queue = uthread.Channel()
        ret = self.sr.queue.receive()
        self.sr.queue = None
        return ret



    def Confirm(self, sender = None, *args):
        uicore.registry.SetFocus(uicore.desktop)
        if sender is None:
            if getattr(uicore.registry.GetFocus(), 'stopconfirm', 0):
                return 
        self.result = sm.GetService('form').ProcessForm(self.retfields, self.reqresult, self.errorcheck)
        if self.result is None:
            return 
        if uicore.registry.GetModalWindow() == self:
            import triui
            self.SetModalResult(triui.ID_OK)
        else:
            if self.sr.queue is not None:
                self.sr.queue.send(self.result)
            ret = self.result
            self.SelfDestruct()
            return ret


    ConfirmFunction = Confirm


