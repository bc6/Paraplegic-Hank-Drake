import uicls
import blue
import uiconst
import uthread
import uiutil
import uix
import mathUtil
import form
import types
import base

class Window(uicls.WindowCore):
    __guid__ = 'uicls.Window'
    default_state = uiconst.UI_HIDDEN
    default_pinned = False
    default_iconNum = 'ui_9_64_9'
    default_topParentHeight = 52

    def ApplyAttributes(self, attributes):
        self.default_parent = uicore.layer.main
        self.default_windowID = attributes.get('name', None)
        self._pinned = False
        self._pinable = True
        self.showhelp = False
        self.showforward = False
        self.showback = False
        self.defaultPrefsID = 'generic'
        self.isBlinking = False
        self.iconNum = attributes.get('iconNum', self.default_iconNum)
        uicls.WindowCore.ApplyAttributes(self, attributes)



    def Prepare_(self):
        self.Prepare_Layout()
        self.Prepare_Header_()
        self.Prepare_LoadingIndicator_()
        self.Prepare_Background_()
        self.Prepare_ScaleAreas_()



    def Prepare_Layout(self):
        self.sr.headerParent = uicls.Container(parent=self.sr.maincontainer, name='headerParent', align=uiconst.TOTOP, pos=(0, 0, 0, 16))
        self.sr.topParent = uicls.Container(parent=self.sr.maincontainer, name='topParent', align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.default_topParentHeight), clipChildren=True)
        self.sr.mainIcon = uicls.Icon(parent=self.sr.topParent, name='mainicon', pos=(0, 0, 64, 64), state=uiconst.UI_HIDDEN)
        self.sr.main = uicls.Container(parent=self.sr.maincontainer, name='main', align=uiconst.TOALL)
        self.sr.iconClipper = uicls.Container(parent=self.sr.maincontainer, name='iconclipper', align=uiconst.TOALL, state=uiconst.UI_DISABLED, top=-53, clipChildren=True)
        self.sr.clippedIcon = uicls.Icon(parent=self.sr.iconClipper, name='clippedicon', pos=(-22, -36, 128, 128), state=uiconst.UI_HIDDEN)
        self.sr.clippedIcon.color.a = 0.1



    def Prepare_Header_(self):
        top = uicls.Container(parent=self.sr.headerParent, name='top', align=uiconst.TOALL)
        self.sr.captionParent = uicls.Container(parent=top, name='captionParent', align=uiconst.TOALL, clipChildren=True)
        self.sr.caption = uicls.Label(text='', parent=self.sr.captionParent, left=8, top=2, state=uiconst.UI_DISABLED, fontsize=10, letterspace=1, uppercase=1)
        self.sr.headerLine = uicls.Line(parent=self.sr.headerParent, align=uiconst.TOBOTTOM, idx=0)



    def Prepare_LoadingIndicator_(self):
        uicls.WindowCore.Prepare_LoadingIndicator_(self)
        self.sr.loadingIndicator.icons = [ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ]



    def Prepare_HeaderButtons_(self):
        self.sr.headerButtons = uicls.Container(name='headerButtons', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPRIGHT, parent=self.sr.maincontainer, pos=(5, 0, 0, 30), idx=0)
        if self.sr.stack:
            closeHint = mls.UI_GENERIC_CLOSEWINDOWSTACK
            minimizeHint = mls.UI_CMD_MINIMIZEWINDOWSTACK
        else:
            closeHint = mls.UI_GENERIC_CLOSE
            minimizeHint = mls.UI_CMD_MINIMIZE
        if self._pinned:
            pinFunc = self.Unpin
            pinhint = mls.UI_GENERIC_UNPINWINDOW
        else:
            pinFunc = self.Pin
            pinhint = mls.UI_GENERIC_PINWINDOW
        w = 0
        for (icon, name, hint, showflag, clickfunc, menufunc,) in [('ui_38_16_220',
          'close',
          closeHint,
          self._killable,
          self._CloseClick,
          None),
         ('ui_38_16_221',
          'minimize',
          minimizeHint,
          self._minimizable,
          self.Minimize,
          None),
         ('ui_38_16_222',
          'pin',
          pinhint,
          self._pinable,
          pinFunc,
          None),
         ('ui_38_16_219',
          'contextHelp',
          mls.UI_SHARED_HELP,
          self.showhelp,
          None,
          self.Help)]:
            if not showflag:
                continue
            btn = uicls.ImageButton(name=name, parent=self.sr.headerButtons, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, pos=(w,
             0,
             16,
             16), idleIcon=icon, mouseoverIcon=icon, mousedownIcon=icon, onclick=clickfunc, getmenu=menufunc, expandonleft=True, hint=hint)
            w += 15

        self.sr.headerButtons.width = w
        if self.sr.captionParent:
            self.sr.captionParent.padRight = w + 6
        self.sr.GoBackBtn = uicls.Icon(parent=self.sr.headerButtons, align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN, icon='ui_38_16_223', pos=(12, 15, 16, 16), hint=self.GetGoBackHint())
        self.sr.GoBackBtn.OnClick = self.GoBack
        self.sr.GoForwardBtn = uicls.Icon(parent=self.sr.headerButtons, align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN, icon='ui_38_16_224', pos=(-2, 15, 16, 16), hint=self.GetGoForwardHint())
        self.sr.GoForwardBtn.OnClick = self.GoForward



    def Prepare_Background_(self):
        self.sr.underlay = uicls.WindowUnderlay(parent=self)
        self.sr.underlay.SetState(uiconst.UI_DISABLED)



    def SetWndIcon(self, iconNum = None, headerIcon = 0, size = 64, fullPath = None, mainTop = -3, hidden = False, **kw):
        self.iconNum = iconNum
        if hidden:
            iconNum = None
        retmain = None
        retclipped = None
        for each in ['mainicon', 'clippedicon', 'clippedicon2']:
            icon = uiutil.FindChild(self, each)
            if not icon:
                continue
            elif iconNum is None:
                icon.state = uiconst.UI_HIDDEN
                continue
            icon.state = uiconst.UI_DISABLED
            icon.LoadIcon(iconNum or fullPath, ignoreSize=True)
            if each in ('clippedicon', 'clippedicon2'):
                if self.sr.topParent:
                    icon.parent.top = -self.sr.topParent.height
                if headerIcon:
                    retclipped = None
                    icon.Close()
                else:
                    retclipped = icon
            elif each == 'mainicon':
                retmain = icon
                icon.top = mainTop
            if headerIcon and each == 'mainicon':
                icon.width = icon.height = 16
                icon.left = 4
                icon.top = 0
                uiutil.Transplant(icon, uiutil.GetChild(self, 'captionParent'))
                if self.sr.caption:
                    self.sr.caption.left = 24
                self.sr.headerIcon = icon

        return (retmain, retclipped)



    def SetTopparentHeight(self, height):
        self.sr.topParent.height = height
        self.sr.iconClipper.top = -height



    def Help(self, *args):
        m = []
        (kbContent, msg, suppressed,) = self.CheckForContextHelp()
        if kbContent is not None:
            sub = []
            for each in kbContent:
                sub.append((each.description.strip(), self.ClickHelp, (each.url.strip(),)))

            if sub:
                m.append((mls.UI_SHARED_KNOWLEDGEBASEARTICLES, sub))
                m.append(None)
        if msg:
            m.append(None)
            m.append((mls.UI_CMD_SHOWWELCOMEPAGE, self.ShowWelcomePage, (None,)))
        return m



    def CheckForContextHelp(self, *args):
        disallowedWnds = ('form.HybridWindow', 'form.ListWindow', 'form.LSCChannel', 'uicls.WindowStack', 'form.VirtualBrowser')
        caption = self.GetCaption(0)
        if not caption or getattr(self, '__guid__', None) in disallowedWnds:
            return (None, None, None)
        ret = sm.GetService('tutorial').GetMappedContextHelp([caption])
        (msg, suppressed,) = self.GetWelcomePageMessage()
        if self and not self.destroyed and (ret or msg):
            self.ShowHelp()
        return (ret, msg, suppressed)



    def GetWelcomePageMessage(self):
        msgkey = 'Welcome_%s' % self.windowID.capitalize()
        return (cfg.GetMessage(msgkey, onNotFound='pass'), settings.user.suppress.Get('suppress.' + msgkey, None))



    def ClickHelp(self, url, *args):
        uthread.new(self.ClickURL, url)



    def ClickURL(self, url, *args):
        uicore.cmd.OpenBrowser(url=url)



    def ClickTutorial(self, tutorialID, *args):
        uthread.new(sm.StartService('tutorial').OpenTutorialSequence_Check, tutorialID, force=1, click=1)



    def ShowHelp(self):
        self.showhelp = True



    def HideHelp(self):
        self.showhelp = False



    def HideMainIcon(self):
        self.sr.mainIcon.state = uiconst.UI_HIDDEN



    def SetHeaderIcon(self, iconNo = 'ui_73_16_50', shiftLabel = 12, hint = None, size = 16):
        par = self.sr.captionParent
        if self.sr.headerIcon:
            self.sr.headerIcon.Close()
            self.sr.headerIcon = None
        if iconNo is None:
            if self.sr.caption:
                self.sr.caption.left = 8
        else:
            self.sr.headerIcon = uicls.Icon(icon=iconNo, parent=par, pos=(4,
             0,
             size,
             size), align=uiconst.RELATIVE, ignoreSize=True)
            self.sr.headerIcon.SetAlpha(0.8)
            self.sr.headerIcon.OnMouseEnter = self.HeaderIconMouseEnter
            self.sr.headerIcon.OnMouseExit = self.HeaderIconMouseExit
            self.sr.headerIcon.expandOnLeft = 1
            if self.sr.caption:
                self.sr.caption.left = 8 + shiftLabel
        self.headerIconNo = iconNo
        self.headerIconHint = hint
        if self.sr.btn:
            self.sr.btn.SetIcon(iconNo, 12, hint)
        if self.sr.tab:
            self.sr.tab.SetIcon(iconNo, 14, hint)



    def HeaderIconMouseEnter(self, *args):
        self.sr.headerIcon.SetAlpha(1.0)



    def HeaderIconMouseExit(self, *args):
        self.sr.headerIcon.SetAlpha(0.8)



    def ShowWelcomePage(self, *args):
        self.LoadWelcomePage(1)



    def LoadWelcomePage(self, force = 0):
        mainpar = uiutil.FindChild(self, 'startpage_mainpar')
        if mainpar and not mainpar.destroyed:
            return 
        if not self or self.destroyed:
            return 
        (kbContent, msg, suppressed,) = self.CheckForContextHelp()
        if msg is None or suppressed and not force:
            return 
        if getattr(self, 'isToggling', 0):
            return 
        if self.sr.stack:
            top = 0
        else:
            headerHeight = self.GetCollapsedHeight()
            top = headerHeight
        if not force:
            tutorialWnd = sm.GetService('window').GetWindow('aura9', decoClass=form.VirtualBrowser, create=0)
            if tutorialWnd:
                return 
        m = 2
        mainpar = uicls.Container(name='startpage', parent=self.sr.maincontainer, left=m, width=m, height=m, idx=0, top=top, clipChildren=True, state=uiconst.UI_NORMAL)
        par = uicls.Container(name='startpage_mainpar', parent=mainpar, state=uiconst.UI_HIDDEN)
        uicls.Line(parent=par, align=uiconst.TOLEFT)
        uicls.Line(parent=par, align=uiconst.TORIGHT)
        uicls.Line(parent=par, align=uiconst.TOBOTTOM)
        uicls.Fill(parent=par, color=(0.0, 0.0, 0.0, 0.8))
        contentpar = uicls.Container(name='contentpar', parent=par, idx=0)
        topPar = uicls.Container(name='topPar', parent=contentpar, align=uiconst.TOTOP, height=64)
        icon = uicls.Icon(icon='ui_74_64_13', parent=contentpar)
        caption = uicls.CaptionLabel(text=msg.title, parent=topPar, align=uiconst.CENTERLEFT, left=70)
        topPar.height = max(topPar.height, caption.textheight)
        bottomPar = uicls.Container(name='bottomPar', parent=contentpar, align=uiconst.TOBOTTOM)
        uicls.Line(parent=bottomPar, align=uiconst.TOTOP)
        btn = uicls.Button(parent=bottomPar, label=mls.UI_CMD_CLOSEWELCOMEPAGE, func=self.CloseWelcomePage, idx=0, left=6, align=uiconst.CENTERRIGHT, alwaysLite=True)
        self.sr.wpCloseBtn = btn
        self.sr.wpSuppress = uicls.Checkbox(text=mls.UI_SHARED_SHOWTHISWELCOMEPAGE, parent=bottomPar, configName='suppress', retval=0, checked=suppressed, groupname=None, align=uiconst.TOPLEFT, pos=(6, 0, 200, 0), callback=self.DoSupress)
        allSuppressed = not settings.char.ui.Get('showWelcomPages', 0)
        self.sr.wpSuppressAll = uicls.Checkbox(text=mls.UI_SHARED_DISABLEWELCOMEPAGES, parent=bottomPar, configName='suppressAll', retval=0, checked=allSuppressed, groupname=None, align=uiconst.TOPLEFT, pos=(6, 0, 200, 0), callback=self.DoSuppressAll)
        self.sr.wpSuppress.top = self.sr.wpSuppressAll.height
        bottomPar.height = max(self.sr.wpSuppress.height + 2 + self.sr.wpSuppressAll.height, btn.height + 6)
        if kbContent:
            uicls.Container(name='push', parent=contentpar, align=uiconst.TOBOTTOM, height=16)
            mainBottomPar = uicls.Container(name='mainBottomPar', parent=contentpar, align=uiconst.TOBOTTOM, height=32)
            kbPar = uicls.Container(name='kbPar', parent=mainBottomPar, align=uiconst.TOLEFT, width=128, left=16)
            uicls.Line(parent=kbPar, align=uiconst.TORIGHT)
            t = uicls.Label(text='<b>%s</b>' % mls.UI_GENERIC_KNOWLEDGEBASE, parent=kbPar, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
            maxWidth = t.textwidth
            for each in kbContent:
                if not each.url:
                    continue
                entryPar = uicls.Container(name='entryPar', parent=kbPar, align=uiconst.TOTOP)
                l = uicls.Label(text='<url=%s>%s</url>' % (each.url, each.description or each.url), parent=entryPar, uppercase=1, fontsize=9, letterspace=1, top=1, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                entryPar.height = max(14, l.textheight)
                maxWidth = max(maxWidth, l.textwidth + 18)
                icon = uicls.Icon(icon='ui_38_16_125', parent=entryPar, align=uiconst.CENTERRIGHT, idx=0, state=uiconst.UI_NORMAL)
                icon.OnClick = (self.ClickHelp, each.url)

            kbPar.width = maxWidth
            kbHeight = sum([ each.height for each in kbPar.children ])
            tutorials = sm.GetService('tutorial').GetTutorials()
            validTutorials = sm.GetService('tutorial').GetValidTutorials()
            tutorialsPar = uicls.Container(name='tutorialsPar', parent=mainBottomPar, align=uiconst.TOLEFT, width=128, left=16)
            uicls.Line(parent=tutorialsPar, align=uiconst.TORIGHT)
            t = uicls.Label(text='<b>%s</b>' % mls.UI_CMD_TUTORIALS, parent=tutorialsPar, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
            maxWidth = t.textwidth
            for each in kbContent:
                if each.tutorialID is None:
                    continue
                tutorialData = tutorials.get(each.tutorialID, None)
                if tutorialData and each.tutorialID in validTutorials:
                    entryPar = uicls.Container(name='entryPar', parent=tutorialsPar, align=uiconst.TOTOP)
                    l = uicls.Label(text='<url=localsvc:service=tutorial&method=OpenTutorialSequence_Check&tutorialID=%s&force=1&click=1>%s</url>' % (each.tutorialID, tutorialData.tutorialName), parent=entryPar, align=uiconst.CENTERLEFT, uppercase=1, fontsize=9, letterspace=1, top=1, state=uiconst.UI_NORMAL)
                    entryPar.height = max(14, l.textheight)
                    maxWidth = max(maxWidth, l.textwidth + 18)
                    icon = uicls.Icon(icon='ui_38_16_125', parent=entryPar, align=uiconst.CENTERRIGHT, idx=0, state=uiconst.UI_NORMAL)
                    icon.OnClick = (self.ClickTutorial, each.tutorialID)

            if len(tutorialsPar.children) <= 2:
                tutorialsPar.Flush()
            tutorialsPar.width = maxWidth
            tutorialsHeight = sum([ each.height for each in tutorialsPar.children ])
            mainBottomPar.height = max(64, kbHeight, tutorialsHeight)
        browser = uicls.Edit(parent=uicls.Container(name='scroll', parent=contentpar, left=const.defaultPadding, width=const.defaultPadding), readonly=1, hideBackground=1)
        message = '\n            <html>\n            < head >\n            <link rel="stylesheet" type="text/css"HREF="res:/ui/css/dungeontm.css">\n            </head>\n            <body>\n            %s\n            </body>\n            </html>\n        ' % msg.text
        if not self or self.destroyed:
            return 
        browser.LoadHTML(message)
        uthread.new(self.ToggleWelcomePage, 1)



    def CloseWelcomePage(self, *args):
        startpage = uiutil.FindChild(self, 'startpage')
        if startpage:
            self.ToggleWelcomePage(0)
            startpage.Close()



    def ToggleWelcomePage(self, show):
        if getattr(self, 'isToggling', 0):
            return 
        prestate = self.state
        if not self or self.destroyed:
            return 
        if prestate != uiconst.UI_HIDDEN:
            self.state = uiconst.UI_DISABLED
        setattr(self, 'isToggling', 1)
        try:
            mainpar = uiutil.FindChild(self, 'startpage_mainpar')
            if not mainpar or mainpar.destroyed:
                return 
            mainpar.state = uiconst.UI_PICKCHILDREN
            (l, t, w, h,) = mainpar.parent.GetAbsolute()
            (start, ndt,) = (blue.os.GetTime(), 0.0)
            time = 750.0
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                if show:
                    mainpar.top = int(mathUtil.Lerp(-h, 0, ndt))
                    mainpar.opacity = ndt
                else:
                    mainpar.top = int(mathUtil.Lerp(0, -h, ndt))
                    mainpar.opacity = 1.0 - ndt
                mainpar.height = -mainpar.top
                blue.pyos.synchro.Yield()


        finally:
            if not self.destroyed:
                self.state = prestate

        mainpar = uiutil.FindChild(self, 'startpage_mainpar')
        if mainpar and not mainpar.destroyed:
            uicore.registry.SetFocus(self.sr.wpCloseBtn)
        if not self or self.destroyed:
            return 
        setattr(self, 'isToggling', 0)



    def DoSupress(self, *args):
        suppress = self.sr.wpSuppress.GetValue()
        key = 'suppress.' + 'Welcome_%s' % self.name.capitalize()
        if suppress:
            settings.user.suppress.Set(key, suppress)
        else:
            try:
                settings.user.suppress.Delete(key)
            except:
                sys.exc_clear()



    def DoSuppressAll(self, *args):
        suppress = not self.sr.wpSuppressAll.GetValue()
        settings.char.ui.Set('showWelcomPages', suppress)



    def Pin(self, delegate = 1, *args):
        if settings.user.windows.Get('lockwhenpinned', 0):
            self.Lock()
        self._SetPinned(True)
        if delegate:
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            if shift or ctrl:
                if shift:
                    alignedWindows = self.FindConnectingWindows(self)
                else:
                    alignedWindows = self.FindConnectingWindows(self, 'bottom')
                for each in alignedWindows:
                    if each == self:
                        continue
                    each.Pin(0)

        self.ShowHeaderButtons(refresh=True)
        sm.GetService('window').ToggleLiteWindowAppearance(self)
        self.OnPin_(self)



    def Unpin(self, delegate = 1, *args):
        if self.IsLocked():
            self.Unlock()
        self._SetPinned(False)
        if delegate:
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            if shift or ctrl:
                if shift:
                    alignedWindows = self.FindConnectingWindows(self)
                else:
                    alignedWindows = self.FindConnectingWindows(self, 'bottom')
                for each in alignedWindows:
                    if each == self:
                        continue
                    each.Unpin(0)

        self.ShowHeaderButtons(refresh=True)
        sm.GetService('window').ToggleLiteWindowAppearance(self)
        self.OnUnpin_(self)



    def MakePinable(self):
        self._pinable = True
        self.ShowHeaderButtons(refresh=True)



    def MakeUnpinable(self):
        self._pinable = False
        self.ShowHeaderButtons(refresh=True)



    def OnPin_(self, wnd):
        pass



    def OnUnpin_(self, wnd):
        pass



    def SetActive(self, *args):
        self.SetNotBlinking()
        self.OnSetActive_(self)



    def SetBlinking(self):
        if uicore.registry.GetActive() == self:
            return 
        self.isBlinking = True
        sm.ScatterEvent('OnWindowStartBlinking', self)



    def SetNotBlinking(self):
        self.isBlinking = False
        sm.ScatterEvent('OnWindowStopBlinking', self)



    def IsPinned(self):
        return self._pinned



    def _SetPinned(self, isPinned):
        self._pinned = isPinned
        self.RegisterState('_pinned')



    def IsBlinking(self):
        return self.isBlinking



    def DefineButtons(self, buttons, okLabel = None, okFunc = 'default', args = 'self', cancelLabel = None, cancelFunc = 'default', okModalResult = 'default', default = None):
        if okLabel is None:
            okLabel = mls.UI_CMD_OK
        if cancelLabel is None:
            cancelLabel = mls.UI_CMD_CANCEL
        if getattr(self.sr, 'bottom', None) is None:
            self.sr.bottom = uiutil.FindChild(self, 'bottom')
            if not self.sr.bottom:
                self.sr.bottom = uicls.Container(name='bottom', parent=self.sr.maincontainer, align=uiconst.TOBOTTOM, height=24, idx=0)
        if self.sr.bottom is None:
            return 
        self.sr.bottom.Flush()
        if buttons is None:
            self.sr.bottom.state = uiconst.UI_HIDDEN
            return 
        self.sr.bottom.height = 24
        if okModalResult == 'default':
            okModalResult = uiconst.ID_OK
        if okFunc == 'default':
            okFunc = self.ConfirmFunction
        if cancelFunc == 'default':
            cancelFunc = self.ButtonResult
        if buttons == uiconst.OK:
            btns = [[okLabel,
              okFunc,
              args,
              None,
              okModalResult,
              1,
              0]]
        elif buttons == uiconst.OKCANCEL:
            btns = [[okLabel,
              okFunc,
              args,
              None,
              okModalResult,
              1,
              0], [cancelLabel,
              cancelFunc,
              args,
              None,
              uiconst.ID_CANCEL,
              0,
              1]]
        elif buttons == uiconst.OKCLOSE:
            btns = [[okLabel,
              okFunc,
              args,
              None,
              okModalResult,
              1,
              0], [mls.UI_CMD_CLOSE,
              self.CloseX,
              args,
              None,
              uiconst.ID_CLOSE,
              0,
              1]]
        elif buttons == uiconst.YESNO:
            btns = [[mls.UI_CMD_YES,
              self.ButtonResult,
              args,
              None,
              uiconst.ID_YES,
              1,
              0], [mls.UI_CMD_NO,
              self.ButtonResult,
              args,
              None,
              uiconst.ID_NO,
              0,
              0]]
        elif buttons == uiconst.YESNOCANCEL:
            btns = [[mls.UI_CMD_YES,
              self.ButtonResult,
              args,
              None,
              uiconst.ID_YES,
              1,
              0], [mls.UI_CMD_NO,
              self.ButtonResult,
              args,
              None,
              uiconst.ID_NO,
              0,
              0], [cancelLabel,
              cancelFunc,
              args,
              None,
              uiconst.ID_CANCEL,
              0,
              1]]
        elif buttons == uiconst.CLOSE:
            btns = [[mls.UI_CMD_CLOSE,
              self.CloseX,
              args,
              None,
              uiconst.ID_CANCEL,
              0,
              1]]
        elif type(okLabel) == types.ListType or type(okLabel) == types.TupleType:
            btns = []
            for index in xrange(len(okLabel)):
                label = okLabel[index]
                additionalArguments = {'Function': okFunc,
                 'Arguments': args,
                 'Cancel Label': cancelLabel,
                 'Cancel Function': cancelFunc,
                 'Modal Result': okModalResult,
                 'Default': default}
                for argName in additionalArguments:
                    if type(additionalArguments[argName]) in (types.ListType, types.TupleType) and len(additionalArguments[argName]) > index:
                        additionalArguments[argName] = additionalArguments[argName][index]

                cancel = additionalArguments['Modal Result'] == uiconst.ID_CANCEL
                btns.append([label,
                 additionalArguments['Function'],
                 additionalArguments['Arguments'],
                 None,
                 additionalArguments['Modal Result'],
                 additionalArguments['Default'],
                 cancel])

        else:
            btns = [[okLabel,
              okFunc,
              args,
              None,
              okModalResult,
              1,
              0]]
        if default is not None:
            for each in btns:
                each[5] = each[4] == default

        uicls.ButtonGroup(btns=btns, parent=self.sr.bottom, unisize=1)
        self.sr.bottom.state = uiconst.UI_PICKCHILDREN



    def NoSeeThrough(self):
        solidBackground = uicls.Fill(name='solidBackground', color=(0.0, 0.0, 0.0, 1.0), padding=(2, 2, 2, 2))
        self.sr.underlay.background.append(solidBackground)
        self._pinable = False



    def SetScope(self, scope):
        self.scope = scope



    def HideClippedIcon(self):
        self.sr.iconClipper.state = uiconst.UI_HIDDEN



    def CloseX(self, *args):
        if not self._killable:
            return 
        uicls.WindowCore._CloseClick(self)



    def _CloseClick(self, *args):
        self.CloseX()



    def SelfDestruct(self, checkStack = 1, checkOthers = 0, checkOutmost = 0, *args):
        uicls.WindowCore.SelfDestruct(self, checkStack, checkOthers, checkOutmost, *args)



    def SetMainIconSize(self, size = 64):
        self.sr.mainIcon.width = self.sr.mainIcon.height = size



    def Collapse(self, forceCollapse = False, checkchain = 1, *args):
        if not self._collapseable or not forceCollapse and self.IsCollapsed():
            return 
        if self.sr.iconClipper:
            self.sr.iconClipper.state = uiconst.UI_HIDDEN
        if self.sr.topParent:
            self.sr.topParent.state = uiconst.UI_HIDDEN
        if self.sr.bottom:
            self.sr.bottom.state = uiconst.UI_HIDDEN
        if self.sr.main:
            self.sr.main.state = uiconst.UI_HIDDEN
        uicls.WindowCore.Collapse(self, forceCollapse, checkchain, args)



    def Expand(self, checkchain = 1, *args):
        uicls.WindowCore.Expand(self, checkchain, args)
        if self.sr.iconClipper:
            self.sr.iconClipper.state = uiconst.UI_PICKCHILDREN
        if self.sr.topParent:
            self.sr.topParent.state = uiconst.UI_PICKCHILDREN
        if self.sr.bottom:
            self.sr.bottom.state = uiconst.UI_PICKCHILDREN
        if self.sr.main:
            self.sr.main.state = uiconst.UI_PICKCHILDREN



    def OnResize_(self, *args):
        self.OnResizeUpdate(self)



    def OnResizeUpdate(self, *args):
        pass



    def GetStackClass(self):
        return uicls.WindowStack



    def HideHeaderButtons(self):
        self._hideHeaderButtons = True



    def UnhideHeaderButtons(self):
        self._hideHeaderButtons = False



    def ShowHeaderButtons(self, refresh = False, *args):
        if getattr(self, '_hideHeaderButtons', False):
            return 
        if refresh:
            if self.sr.headerButtons:
                self.sr.headerButtons.Close()
                self.sr.headerButtons = None
            else:
                return 
        if self.sr.stack or self.GetAlign() != uiconst.RELATIVE or uicore.uilib.leftbtn or getattr(self, 'isImplanted', False):
            return 
        if not self.sr.headerButtons:
            self.Prepare_HeaderButtons_()
        if self.sr.headerButtons:
            w = self.sr.headerButtons.width
            if self.sr.captionParent:
                self.sr.captionParent.padRight = w + 6
            if self.sr.loadingIndicator:
                self.sr.loadingIndicator.left = w + self.sr.headerButtons.left
        if not self.IsCollapsed():
            if self.showforward or self.showback:
                if not self.showforward:
                    self.sr.GoForwardBtn.state = uiconst.UI_DISABLED
                    self.sr.GoForwardBtn.color.a = 0.25
                else:
                    self.sr.GoForwardBtn.state = uiconst.UI_NORMAL
                    self.sr.GoForwardBtn.color.a = 1.0
                if not self.showback:
                    self.sr.GoBackBtn.state = uiconst.UI_DISABLED
                    self.sr.GoBackBtn.color.a = 0.25
                else:
                    self.sr.GoBackBtn.state = uiconst.UI_NORMAL
                self.sr.GoBackBtn.color.a = 1.0
        self.sr.headerButtonsTimer = base.AutoTimer(1000, self.CloseHeaderButtons)



    def IndicateStackable(self, wnd = None):
        if wnd is None:
            if self.sr.Get('snapIndicator', None):
                self.sr.snapIndicator.Close()
                self.sr.snapIndicator = None
            return 
        if not wnd._stackable or not self._stackable:
            return 
        if self.sr.Get('snapIndicator', None) is None:
            self.sr.snapIndicator = uicls.Fill(parent=None, align=uiconst.RELATIVE)
        si = self.sr.snapIndicator
        idx = wnd.parent.children.index(wnd)
        (wl, wt, ww, wh,) = wnd.GetAbsolute()
        si.left = wl
        si.top = wt
        si.width = ww
        si.height = wh
        si.state = uiconst.UI_DISABLED
        if si.parent != wnd.parent:
            uiutil.Transplant(si, wnd.parent, idx=idx)
        sidx = si.parent.children.index(si)
        if sidx != idx - 1:
            uiutil.SetOrder(si, idx)



    def _Minimize(self, wnd):
        if not wnd or wnd.destroyed or wnd.IsMinimized() or wnd.sr.minimizedBtn:
            return 
        wnd.OnStartMinimize_(wnd)
        wnd._changing = True
        sm.GetService('window').MinimizeWindow(wnd)
        if wnd.destroyed:
            return 
        wnd._SetMinimized(True)
        wnd.state = uiconst.UI_HIDDEN
        wnd.OnEndMinimize_(wnd)
        wnd._changing = False



    def Maximize(self, silent = 0, expandIfCollapsed = True):
        sm.GetService('window').MaximizeWindow(self, silent, expandIfCollapsed=expandIfCollapsed)



    def GetMenu(self, *args):
        menu = uicls.WindowCore.GetMenu(self)
        helpMenu = self.Help()
        if helpMenu:
            menu.append((mls.UI_SHARED_HELP, helpMenu))
        return menu



    def InitializeStatesAndPosition(self, expandIfCollapsed = False, skipCornerAligmentCheck = False, skipWelcomePage = False, skipState = False):
        self.startingup = 1
        wndSvc = sm.GetService('window')
        if not self.sr.stack:
            collapsed = self.GetRegisteredState('collapsed')
            if not expandIfCollapsed and collapsed:
                uthread.new(self.Collapse, True)
            elif expandIfCollapsed:
                uthread.new(self.Expand, True)
                focus = uicore.registry.GetFocus()
                if not (focus and getattr(focus, '__guid__', None) in ('uicls.Edit', 'uicls.SingleLineEdit', 'uicls.EditPlainText')):
                    uthread.new(uicore.registry.SetFocus, self)
            if settings.user.ui.Get('skipWindowGrouping', 0) or skipCornerAligmentCheck or not wndSvc.TryAlignToCornerGroup(self):
                d = uicore.desktop
                (left, top, width, height, dw, dh,) = self.GetRegisteredPositionAndSize()
                self.left = max(0, min(d.width - self.width, left))
                self.top = max(0, min(d.height - self.height, top))
                (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
                if self.left in (0, 16):
                    self.left += leftpush
                elif self.left + self.width in (d.width, d.width - 16):
                    self.left -= rightpush
                self.CheckWndPos()
            if not skipState:
                self.state = uiconst.UI_NORMAL
            locked = self.GetRegisteredState('locked')
            if locked:
                self.Lock()
            else:
                self.Unlock()
        pinned = self.GetRegisteredState('pinned')
        if pinned:
            self.Pin(0)
        else:
            self.Unpin(0)
        if self.sr.stack:
            self.sr.stack.Check()
        if settings.char.ui.Get('showWelcomPages', 0) and not skipWelcomePage:
            uthread.new(self.LoadWelcomePage)
        self.startingup = 0
        self._SetOpen(True)



    def CreateSnapGrid(self, shiftGroup = None, ctrlGroup = None):
        (neoleft, neoright,) = sm.GetService('neocom').GetSideOffset()
        allWnds = self.GetOtherWindows()
        desk = uicore.desktop
        hAxes = [0,
         desk.height,
         16,
         desk.height - 16]
        vAxes = [0,
         neoleft,
         neoleft + 16,
         desk.width - neoright,
         desk.width - 16 - neoright]
        hAxesWithOutMe = hAxes[:]
        vAxesWithOutMe = vAxes[:]
        hAxesWithOutShiftGroup = hAxes[:]
        vAxesWithOutShiftGroup = vAxes[:]
        hAxesWithOutCtrlGroup = hAxes[:]
        vAxesWithOutCtrlGroup = vAxes[:]
        hLists = [hAxes,
         hAxesWithOutMe,
         hAxesWithOutShiftGroup,
         hAxesWithOutCtrlGroup]
        vLists = [vAxes,
         vAxesWithOutMe,
         vAxesWithOutShiftGroup,
         vAxesWithOutCtrlGroup]
        for wnd in allWnds:
            (l, t, w, h,) = wnd.GetAbsolute()
            self.AddtoAxeList(wnd, vLists, l, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, vLists, l + w, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t + h, shiftGroup, ctrlGroup)

        self.snapGrid = [(hAxes, vAxes),
         (hAxesWithOutMe, vAxesWithOutMe),
         (hAxesWithOutShiftGroup, vAxesWithOutShiftGroup),
         (hAxesWithOutCtrlGroup, vAxesWithOutCtrlGroup)]
        return self.snapGrid



    def LockHeight(self, height):
        self._fixedHeight = height
        if self.sr.stack is None:
            self.height = height
        for each in self.sr.resizers.children[:]:
            if each.name in ('sTop', 'sBottom', 'sRightTop', 'sLeftTop', 'sRightBottom', 'sLeftBottom'):
                each.state = uiconst.UI_HIDDEN
            elif each.name in ('sLeft', 'sRight'):
                each.top = 0




    def UnlockHeight(self):
        self._fixedHeight = None
        for each in self.sr.resizers.children[:]:
            each.state = uiconst.UI_NORMAL
            if each.name in ('sLeft', 'sRight'):
                each.top = 8

        if self._fixedWidth:
            self.LockWidth(self._fixedWidth)



    def LockWidth(self, width):
        self._fixedWidth = width
        if self.sr.stack is None:
            self.width = width
        for each in self.sr.resizers.children[:]:
            if each.name in ('sLeft', 'sRight', 'sRightTop', 'sLeftTop', 'sRightBottom', 'sLeftBottom'):
                each.state = uiconst.UI_HIDDEN
            elif each.name in ('sTop', 'sBottom'):
                each.left = 0




    def UnlockWidth(self):
        self._fixedWidth = None
        for each in self.sr.resizers.children[:]:
            each.state = uiconst.UI_NORMAL
            if each.name in ('sTop', 'sBottom'):
                each.left = 8

        if self._fixedHeight:
            self.LockHeight()



    def DefineIcons(self, icon, customicon = None, mainTop = -3):
        import types
        if customicon is not None:
            iconNo = customicon
        else:
            mapping = {uiconst.INFO: 'ui_9_64_9',
             uiconst.WARNING: 'ui_9_64_11',
             uiconst.QUESTION: 'ui_9_64_10',
             uiconst.ERROR: 'ui_9_64_8',
             uiconst.FATAL: 'ui_9_64_12'}
            if type(icon) == types.StringType:
                iconNo = icon
            else:
                iconNo = mapping.get(icon, 'ui_9_64_11')
        self.SetWndIcon(iconNo, mainTop=mainTop)



    def ConfirmFunction(self, button, *args):
        uicore.registry.Confirm(button)



    def ShowGoBack(self):
        self.showback = True



    def ShowGoForward(self):
        self.showforward = True



    def HideGoBack(self):
        self.showback = False



    def HideGoForward(self):
        self.showforward = False



    def GetGoBackHint(self, *args):
        return mls.UI_CMD_PREVIOUS



    def GetGoForwardHint(self, *args):
        return mls.UI_CMD_NEXT



    def GoBack(self, *args):
        pass



    def GoForward(self, *args):
        pass



    def HideBackground(self):
        self.HideUnderlay()
        for each in self.children[:]:
            if each.name.startswith('_lite'):
                each.Close()




    def ShowBackground(self):
        self.ShowUnderlay()
        liteState = self.IsPinned()
        sm.GetService('window').ToggleLiteWindowAppearance(self, liteState)



    def SetCaption(self, caption, delete = 1):
        uicls.WindowCore.SetCaption(self, caption, delete)
        self.CheckForContextHelp()



    def ShowDialog(self, modal = False, state = uiconst.UI_NORMAL):
        if modal:
            self.NoSeeThrough()
        return uicls.WindowCore.ShowDialog(self, modal, state)



    def GetDefaultLeftOffset(self, width, align = None, left = 0):
        return sm.GetService('window').GetCameraLeftOffset(width, align, left)



    def AttachWindow(self, wnd, side, *args):
        if side not in ('top', 'bottom') or wnd == self:
            return 
        alignedWindows = self.FindConnectingWindows(self, side)
        removeFrom = None
        if wnd in alignedWindows:
            removeFrom = alignedWindows
        else:
            removeFrom = self.FindConnectingWindows(self, 'top') + self.FindConnectingWindows(self, 'bottom')

            def FilterWnds(wnds, side):
                valid = []
                done = []
                for w in wnds:
                    if w not in done:
                        valid.append((w.top, w))
                        done.append(w)

                return uiutil.SortListOfTuples(valid)


            removeFrom = FilterWnds(removeFrom, side)
        (pgl, pgt, pgw, pgh,) = self.GetGroupAbsolute(removeFrom)
        if removeFrom and wnd in removeFrom:
            idx = removeFrom.index(wnd)
            for awnd in removeFrom[(idx + 1):]:
                awnd.top -= wnd.height

            wnd.state = uiconst.UI_HIDDEN
            alignedWindows = self.FindConnectingWindows(self, side)
        wnd.state = uiconst.UI_NORMAL
        if alignedWindows[0] != self:
            return 
        desk = uicore.desktop
        myCurrentGroup = self.FindConnectingWindows(self, 'top') + self.FindConnectingWindows(self, 'bottom')
        (cgl, cgt, cgw, cgh,) = self.GetGroupAbsolute(myCurrentGroup)
        wasOnTop = bool(cgt == 0)
        wasOnTop16 = bool(cgt == 16)
        wasOnBottom = bool(cgt + cgh == desk.height)
        wasOnBottom16 = bool(cgt + cgh == desk.height - 16)
        wnd.left = self.left
        wnd.width = self.width
        if side == 'bottom':
            wnd.top = self.top + self.height
        elif side == 'top':
            wnd.top = self.top - wnd.height
        for awnd in alignedWindows[1:]:
            if awnd == wnd:
                continue
            if side == 'bottom':
                awnd.top += wnd.height
            elif side == 'top':
                awnd.top -= wnd.height

        myNewGroup = self.FindConnectingWindows(self, 'top')[1:] + self.FindConnectingWindows(self, 'bottom')
        (ngl, ngt, ngw, ngh,) = self.GetGroupAbsolute(myNewGroup)
        if wasOnTop or wasOnTop16:
            margin = wasOnTop16 * 16
            if ngt != margin:
                diff = -ngt + margin
                for each in myNewGroup:
                    each.top += diff

        elif wasOnBottom or wasOnBottom16:
            margin = wasOnBottom16 * 16
            if desk.height - (ngt + ngh) != margin:
                diff = desk.height - (ngt + ngh) - margin
                for each in myNewGroup:
                    each.top += diff

        (gl, gt, gw, gh,) = self.GetGroupAbsolute(myNewGroup)
        if max(0, gt) + gh > desk.height:
            self.FitWndGroup(myNewGroup, (gl,
             gt,
             gw,
             gh))



    def FitWndGroup(self, wnds, groupAbs):
        wnds = uiutil.SortListOfTuples([ (wnd.top, wnd) for wnd in wnds ])
        (gl, gt, gw, gh,) = groupAbs
        d = uicore.desktop
        totalHeight = max(0, gt) + gh
        overShot = d.height - totalHeight
        while overShot < 0:
            scaleAble = [ each for each in wnds if each.GetMinHeight() < each.height ]
            if not scaleAble:
                break
            totalHeightScaleAble = sum([ each.height for each in scaleAble ])
            scaleValue = 1.0 - float(abs(overShot)) / totalHeightScaleAble
            for wnd in scaleAble:
                h = int(wnd.height * scaleValue)
                minH = wnd.GetMinHeight()
                wnd.height = max(h, minH)

            totalHeight = sum([ each.height for each in wnds ])
            overShot = d.height - (gt + totalHeight)

        t = max(0, gt)
        for each in wnds:
            if uiutil.GetAttrs(each, 'sr', 'stack') is not None:
                continue
            each.top = t
            t += each.height





