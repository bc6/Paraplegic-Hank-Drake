import blue
import browserutil
import form
import listentry
import service
import types
import uix
import uiutil
import uthread
import util
import xtriui
import uiconst
import uicls

class VirtualBrowser(uicls.Window):
    __guid__ = 'form.VirtualBrowser'
    __notifyevents__ = ['OnSessionChanged']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.loadupdates = 0
        self.statustext = ''
        self.views = []
        self.activeView = 0
        self.SetCaption('%s 2.0' % mls.UI_SHARED_EVEBROWSER)
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        bottom = uicls.Container(name='__bottom', parent=self.sr.main, align=uiconst.TOBOTTOM, height=12)
        self.sr.progress = uicls.Container(parent=bottom, align=uiconst.TOPLEFT, height=10, width=68, left=const.defaultPadding, top=-2, state=uiconst.UI_HIDDEN)
        uicls.Fill(parent=self.sr.progress, align=uiconst.RELATIVE, height=6, width=0, left=2, top=2, color=(1.0, 1.0, 1.0, 0.7))
        uicls.Label(text='', parent=self.sr.progress, width=100, autowidth=False, left=72, top=-1, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.sr.progress, color=(1.0, 1.0, 1.0, 0.5))
        cbox = uicls.Checkbox(text=mls.UI_GENERIC_TRUSTEDSITE, callback=self.OnTrustedSitesClick, align=uiconst.TOPRIGHT, pos=(6, -4, 0, 0))
        cbox.data = {}
        bottom.children.append(cbox)
        cbox.SetLabelText(mls.UI_GENERIC_TRUSTEDSITE)
        self.sr.trustedSiteCb = cbox
        self.sr.bottomParent = bottom
        self.sr.hint = uicls.Label(text='', parent=bottom, fontsize=10, left=8, top=-2, align=uiconst.TOALL, state=uiconst.UI_DISABLED, uppercase=1, autowidth=False, autoheight=False)
        topparent = uicls.Container(name='topparent', parent=self.sr.main, align=uiconst.TOTOP, height=16, top=const.defaultPadding, idx=0)
        standardButtonsParent = uicls.Container(name='standardButtonsParent', parent=topparent, align=uiconst.TORIGHT, padRight=4, idx=0)
        self.sr.stdTopParent = topparent
        for each in ['back',
         'forward',
         'home',
         'reload']:
            button = uicls.ImageButton(parent=standardButtonsParent, name=each, width=20, height=20, align=uiconst.RELATIVE, top=-2, left=standardButtonsParent.width, idleIcon='res:/UI/Texture/classes/Browser/%sIdle.png' % each, mouseoverIcon='res:/UI/Texture/classes/Browser/%sMouseOver.png' % each, mousedownIcon='res:/UI/Texture/classes/Browser/%sIdle.png' % each, onclick=getattr(self, each.capitalize(), None), hint=getattr(mls, 'UI_SHARED_BROWSER' + each.upper(), ''))
            button.flag = each
            setattr(self.sr, '%sBtn' % each, button)
            standardButtonsParent.width += 20

        self.sr.standardButtonsParent = standardButtonsParent
        urlinput = uicls.SinglelineEdit(name='urlinput', parent=topparent, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        urlinput.OnReturn = self.OnUrlInputReturn
        self.sr.urlinput = urlinput
        visited = settings.public.ui.Get('VisitedURLs', ['http://bughunters.addix.net/igbtest/index.html'])
        visited = [ url for url in visited if url if url.find('?') == -1 if url.find('&') == -1 ]
        ops = [ (url, url) for url in visited ]
        urlinput.LoadCombo('urlcombo', ops, self.OnComboChange)
        self.sr.tabsParent = uicls.Container(name='tabsparent', parent=self.sr.main, align=uiconst.TOTOP, height=20, idx=1, state=uiconst.UI_HIDDEN)
        self.sr.browser = None
        self.NewView(None)
        mp = uicls.Container(name='menu', align=uiconst.TOTOP, width=0, height=16, parent=self.sr.main, idx=0, top=0)
        uicls.Line(parent=mp, align=uiconst.TOBOTTOM)
        push = uicls.Container(name='push', parent=mp, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=const.defaultPadding)
        uicls.Line(parent=push, align=uiconst.TORIGHT)
        for (name, GetMenu,) in [(mls.UI_SHARED_BROWSERVIEW, lambda : [(mls.UI_CMD_NEWVIEW, self.NewView, (None,)),
           (mls.UI_CMD_CLOSEVIEW, self.CloseView, ()),
           None,
           (mls.UI_SHARED_BROWSERRELOAD, self.Reload, ()),
           (mls.UI_CMD_VIEWSOURCE, self.DocumentSource, ())]), (mls.UI_CMD_BROWSERBOOKMARKS, self.GetBookmarkMenu), (mls.UI_CMD_OPTIONS, lambda : [(mls.UI_CMD_GENERALSETTINGS, self.EditGeneralSettings, ()), None, (mls.UI_CMD_TRUSTEDSITES, self.EditSites, ('trusted',))])]:
            opt = xtriui.StandardMenu(name='menuoption', parent=mp, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
            opt.Setup(name, GetMenu)

        self.sr.menuParent = mp
        lp = uicls.Container(name='languageParent', align=uiconst.TORIGHT, width=4, height=0, parent=mp)
        i = 0
        for (name, hint, iconNo, callback,) in [('de',
          mls.UI_GENERIC_LANGGERMAN,
          'ui_22_32_35',
          self.ChangeLang),
         ('fr',
          mls.UI_GENERIC_LANGFRENCH,
          'ui_22_32_34',
          self.ChangeLang),
         ('en',
          mls.UI_GENERIC_LANGENGLISH,
          'ui_22_32_37',
          self.ChangeLang),
         ('es',
          mls.UI_GENERIC_LANGSPANISH,
          'ui_22_32_38',
          self.ChangeLang)]:
            btn = uicls.Icon(parent=lp, icon=iconNo, name=name, hint=hint, width=16, height=16, left=i * 17, top=-1, align=uiconst.RELATIVE, ignoreSize=True)
            btn.OnClick = (callback, btn)
            lp.width += btn.width + 1
            i += 1

        self.LanguageBtnsOnOff(0)
        self.reloadedScaleSize = (self.width, self.height)
        self.RefreshViewTabs()
        self.HistoryChange()



    def LoadHTML(self, html, hideBackground = 0, newThread = 1):
        self.ShowLoad()
        self.sr.browser.sr.hideBackground = hideBackground
        self.sr.browser.LoadHTML(html, newThread=newThread)



    def LoadEnd(self):
        if self and not self.destroyed:
            self.HideLoad()
            if not self.GetCaption() and self.sr.browser.sr.currentURL:
                self.SetCaption(self.sr.browser.sr.currentURL)



    def OptionsOn(self):
        self.sr.menuParent.state = uiconst.UI_PICKCHILDREN



    def OptionsOff(self):
        self.sr.menuParent.state = uiconst.UI_HIDDEN



    def ButtonBarOn(self):
        self.sr.standardButtonsParent.state = uiconst.UI_PICKCHILDREN



    def ButtonBarOff(self):
        self.sr.standardButtonsParent.state = uiconst.UI_HIDDEN



    def AddressBarOn(self):
        self.sr.stdTopParent.state = uiconst.UI_PICKCHILDREN



    def AddressBarOff(self):
        self.sr.stdTopParent.state = uiconst.UI_HIDDEN
        uicore.registry.SetFocus(self.sr.browser)



    def StatusBarOn(self):
        self.sr.bottomParent.state = uiconst.UI_PICKCHILDREN



    def StatusBarOff(self):
        self.sr.bottomParent.state = uiconst.UI_HIDDEN



    def LanguageBtnsOnOff(self, onoff, url = None):
        i = 0
        for lang in ['en',
         'fr',
         'de',
         'es',
         'se']:
            btn = uiutil.FindChild(self, 'languageParent', lang)
            if btn:
                if url and url.find('Tutorial') > 0:
                    btn.color.a = [0.33, 1.0][(i == settings.user.ui.Get('language', 0))]
                else:
                    btn.color.a = [0.33, 1.0][(i == min(1, settings.user.ui.Get('language', 0)))]
                btn.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][onoff]
            i += 1

        if url and url.find('Tutorial') < 0:
            uiutil.FindChild(self, 'languageParent', 'de').state = uiconst.UI_HIDDEN



    def ChangeLang(self, btn, *args):
        settings.user.ui.Set('language', ['en',
         'fr',
         'de',
         'es',
         'se'].index(btn.name))
        self.Reload(forced=1)



    def GetBookmarkMenu(self):
        m = [(mls.UI_CMD_ADDREMOVE, self.EditBookmarks), None]
        for (name, url,) in sm.GetService('sites').GetBookmarks():
            if url.find(':/') == -1:
                url = 'http://' + url
            m.append((name, self.GoTo, (url,)))

        return m



    def EditGeneralSettings(self):
        if not self.destroyed:
            wnd = sm.GetService('window').GetWindow('BrowserGeneralSettings', create=1, decoClass=form.BrowserGeneralSettings)
            wnd.ShowModal()



    def EditBookmarks(self):
        if not self.destroyed:
            wnd = sm.GetService('window').GetWindow('EditBookmarks', create=1, name=self.sr.wndCaption.text, url=self.sr.urlinput.GetValue())
            wnd.ShowModal()



    def EditSites(self, initialUrl):
        sm.GetService('window').GetWindow('WebsiteTrustManagementWindow', decoClass=form.WebsiteTrustManagementWindow, create=1, initialUrl=initialUrl)



    def RefreshViewTabs(self, selectIdx = None):
        self.sr.tabsParent.Flush()
        if len(self.views) > 1:
            tabs = []
            i = 0
            for (tabName, historyIdx, history, b,) in self.views:
                tabs.append([tabName,
                 None,
                 self,
                 i])
                i += 1

            tabgroup = uicls.TabGroup(name='viewtabs', parent=self.sr.tabsParent, align=uiconst.TOBOTTOM, tabs=tabs, groupID='browserviewtabs', autoselecttab=selectIdx is None)
            if selectIdx is not None:
                tabgroup.SelectByIdx(selectIdx)
            self.sr.tabsParent.state = uiconst.UI_NORMAL
        else:
            self.sr.tabsParent.state = uiconst.UI_HIDDEN



    def GetTabMenu(self, tab):
        return [(mls.UI_CMD_CLOSEVIEW, self.CloseView, (tab.sr.args,))]



    def CloseView(self, _viewIdx = None):
        viewIdx = _viewIdx or self.activeView
        if len(self.views) > viewIdx:
            b = self.views[viewIdx][3]
            self.sr.main.children.remove(b)
            b.Close()
            del self.views[viewIdx]
        if not len(self.views):
            self.Close()
            return 
        if viewIdx == self.activeView:
            self.activeView = max(0, viewIdx - 1)
        self.RefreshViewTabs()
        (tabName, historyIdx, history, self.sr.browser,) = self.views[self.activeView]
        self.sr.browser.state = uiconst.UI_PICKCHILDREN
        self.SetCaption(self.sr.browser.title or '')
        self.sr.urlinput.SetValue(self.sr.browser.sr.currentURL or '')



    def NewView(self, url):
        if self.sr.browser:
            self.sr.browser.state = uiconst.UI_HIDDEN
            currentURL = self.sr.browser.sr.currentURL or ''
        self.sr.browser = uicls.Edit(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), readonly=1)
        self.sr.browser.AllowResizeUpdates(0)
        self.sr.browser.sr.window = self
        self.sr.browser.GetMenu = self.GetMenu
        c = len(self.views)
        self.views.append(['%s %s' % (mls.UI_SHARED_BROWSERVIEW, c + 1),
         None,
         [],
         self.sr.browser])
        self.RefreshViewTabs(c)
        uicore.registry.SetFocus(self.sr.urlinput)
        if url:
            self.sr.browser.sr.currentURL = currentURL
            uthread.new(self.GoTo, url)



    def Load(self, *args):
        (viewIdx,) = args
        self.activeView = viewIdx
        if self.sr.browser:
            self.sr.browser.state = uiconst.UI_HIDDEN
        (tabName, historyIdx, history, self.sr.browser,) = self.views[self.activeView]
        self.sr.browser.state = uiconst.UI_PICKCHILDREN
        self.SetCaption(self.sr.browser.title or '')
        self.sr.urlinput.SetValue(self.sr.browser.sr.currentURL or '')
        self.HistoryChange()



    def Back(self, *args):
        if self.views:
            (tabName, historyIdx, history, b,) = self.views[self.activeView]
            if history:
                self.GoToIndex(historyIdx - 1)



    def Forward(self, *args):
        if self.views:
            (tabName, historyIdx, history, b,) = self.views[self.activeView]
            if history:
                self.GoToIndex(historyIdx + 1)



    def Reload(self, forced = 1, *args):
        if not self or self.destroyed:
            return 
        if not self.sr.browser:
            return 
        url = self.sr.browser.sr.currentURL or self.sr.urlinput.GetValue()
        if url and forced:
            uthread.new(self.GoTo, url, self.sr.browser.sr.currentData, scrollTo=self.sr.browser.GetScrollProportion())
        else:
            uthread.new(self.sr.browser.LoadHTML, None, scrollTo=self.sr.browser.GetScrollProportion())



    def Home(self, *args):
        home = settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage())
        if home:
            uthread.new(self.GoTo, home)



    def Stop(self, *args):
        print "Can't stop now... cause I'm having a good time... I don't want to stop at all... du du du"



    def GetMenu(self):
        m = []
        if self.sr.urlinput.GetValue():
            m.append((mls.UI_CMD_SETASHOMEPAGE, self.SetHomePage))
            m.append((mls.UI_CMD_BOOKMARK, self.EditBookmarks))
            m.append((mls.UI_CMD_VIEWSOURCE, self.DocumentSource))
        return m



    def SetHomePage(self, url = None):
        url = url or self.sr.urlinput.GetValue()
        settings.user.ui.Set('HomePage2', url)
        self.HistoryChange()



    def DocumentSource(self):
        if self.sr.urlinput.GetValue():
            txt = self.sr.browser._GoTo(self.sr.urlinput.GetValue(), getSource=1)
            if txt:
                if type(txt) != types.UnicodeType:
                    txt = unicode(txt, 'utf-8', 'replace')
                txt = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                (response, supress,) = sm.GetService('gameui').MessageBox(txt, title=mls.UI_SHARED_BROWSERHTMLSOURCEOF % self.sr.urlinput.GetValue(), buttons=uiconst.OK, icon=uiconst.INFO)



    def GoToIndex(self, i):
        (tabName, historyIdx, history, b,) = self.views[self.activeView]
        i = max(0, min(len(history) - 1, i))
        h = history[i]
        scrollTo = self.sr.browser.sr.positions.get(h[1], None)
        self.sr.browser._GoTo(h[0], h[1], h[2], scrollTo)
        self.views[self.activeView][0] = self.sr.browser.title or '%s %s' % (mls.UI_SHARED_BROWSERVIEW, self.activeView + 1)
        if len(self.sr.tabsParent.children):
            tab = self.sr.tabsParent.children[0].GetVisible(1)
            if tab:
                tab.SetLabel(self.views[self.activeView][0], self.sr.browser.sr.currentURL)
        self.sr.urlinput.SetValue(h[0])
        if self.views:
            self.views[self.activeView][1] = i
        self.HistoryChange()



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        if not URL:
            return 
        browser = self.sr.browser
        if not browser.sr.currentURL:
            browser.sr.currentURL = URL
        browser._GoTo(URL, data, args, scrollTo)
        if not self or self.destroyed:
            return 
        if browser.sr.currentURL is not None:
            URL = browser.sr.currentURL
        if URL.find(':/') == -1:
            URL = 'http://' + URL
        if self.views:
            for activeView in xrange(len(self.views)):
                (tabName, historyIdx, history, b,) = self.views[activeView]
                if b == browser:
                    if historyIdx is not None:
                        history = history[:(historyIdx + 1)]
                    if not history or history[-1][0] != URL:
                        history.append((URL,
                         data,
                         args,
                         scrollTo))
                        self.views[activeView][2] = history
                        self.views[activeView][1] = len(self.views[self.activeView][2]) - 1
                    self.views[activeView][0] = browser.title or '%s %s' % (mls.UI_SHARED_BROWSERVIEW, activeView + 1)
                    if len(self.sr.tabsParent.children):
                        tab = self.sr.tabsParent.children[0].sr.tabs[activeView]
                        if tab:
                            tab.SetLabel(self.views[activeView][0], URL)
                    break

        if browser == self.sr.browser:
            self.sr.urlinput.SetValue(URL)
        self.HistoryChange()
        known = settings.public.ui.Get('VisitedURLs', [])
        if URL not in known:
            known.append(URL)
            settings.public.ui.Set('VisitedURLs', known)
        known = [ URL for URL in known if URL if URL.find('?') == -1 if URL.find('&') == -1 ]
        known.sort()
        ops = [ (_url, _url) for _url in known ]
        self.sr.urlinput.LoadCombo('urlcombo', ops, self.OnComboChange, URL)



    def ShowHint(self, hint):
        if util.GetAttrs(self, 'sr', 'hint') and not self.sr.hint.destroyed:
            self.sr.hint.text = hint



    def ShowStatus(self, *args):
        (status,) = args
        self.statustext = status



    def ShowLoadBar(self, *args):
        if args:
            (part, total, string,) = args
            portion = part / float(total)
            self.sr.progress.children[0].width = int(64 * portion)
            self.sr.progress.children[1].text = '%d%% - %s' % (portion * 100, self.statustext)
            self.sr.progress.state = uiconst.UI_DISABLED
            self.sr.hint.state = uiconst.UI_HIDDEN
            self.loadupdates += 1
            if self.loadupdates == 32:
                blue.pyos.synchro.BeNice(150)
                self.loadupdates = 0
            if portion == 1:
                blue.pyos.synchro.BeNice(150)
                self.sr.progress.state = uiconst.UI_HIDDEN
                self.sr.hint.state = uiconst.UI_DISABLED



    def HistoryChange(self, *args):
        scrollList = []
        if self.views:
            (tabName, historyIdx, history, b,) = self.views[self.activeView]
            lenHistory = len(history)
            historyIdx = historyIdx or 0
            if historyIdx and lenHistory > 1:
                self.sr.backBtn.Enable()
                self.sr.backBtn.hint = '%s %s' % (mls.UI_SHARED_BROWSERBACKTO, history[(historyIdx - 1)][0])
            else:
                self.sr.backBtn.Disable()
                self.sr.backBtn.hint = ''
            if historyIdx < lenHistory - 1:
                self.sr.forwardBtn.Enable()
                self.sr.forwardBtn.hint = '%s %s' % (mls.UI_SHARED_BROWSERFORWARDTO, history[(historyIdx + 1)][0])
            else:
                self.sr.forwardBtn.Disable()
                self.sr.forwardBtn.hint = ''
            i = 0
            for h in history:
                scrollList.append(listentry.Get('Text', {'text': ['  ', '> '][(historyIdx == i)] + h[0],
                 'height': 12}))
                i += 1

        else:
            self.sr.backBtn.Disable()
            self.sr.backBtn.hint = ''
            self.sr.forwardBtn.Disable()
            self.sr.forwardBtn.hint = ''
        home = settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage())
        if home:
            self.sr.homeBtn.hint = '%s: %s' % (mls.UI_SHARED_BROWSERFORWARDTO, home)
            self.sr.homeBtn.Enable()
        else:
            self.sr.homeBtn.hint = mls.UI_SHARED_BROWSERNOHOMEPAGE
            self.sr.homeBtn.Disable()
        if self.sr.urlinput.GetValue():
            self.sr.reloadBtn.hint = mls.UI_GENERIC_RELOAD
            self.sr.reloadBtn.Enable()
        else:
            self.sr.reloadBtn.hint = ''
            self.sr.reloadBtn.Disable()



    def OnEndScale_(self, *args):
        self.reloadedScaleSize = (self.width, self.height)
        uthread.new(self.Reload, 0)



    def OnComboChange(self, combo, header, value, *args):
        self.sr.urlinput.SetValue(value)
        uthread.new(self.GoTo, value)



    def OnUrlInputReturn(self, *args):
        url = self.sr.urlinput.GetValue()
        if url:
            if url.find(':/') == -1:
                url = 'http://' + url
            uthread.new(self.GoTo, url)



    def Confirm(self, *args):
        pass



    def OnTrustedSitesClick(self, cb):
        if cb.GetValue():
            eve.Message('TrustedSitesHelpOn')
        else:
            eve.Message('TrustedSitesHelpOff')



    def OnSessionChanged(self, isRemote, sess, change):
        if not self.destroyed:
            self.sr.browser.SessionChanged()




class StandardMenu(uicls.Container):
    __guid__ = 'xtriui.StandardMenu'

    def Setup(self, name, GetMenu):
        self.name = name
        self.GetMenu = GetMenu
        uicls.Line(parent=self, align=uiconst.TORIGHT)
        self.sr.label = uicls.Label(text=name, parent=self, left=5, top=2, fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, uppercase=1)
        self.expandOnLeft = 1
        self.height = 10
        self.sr.hilite = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN, padding=(1, 1, 1, 1))
        self.width = self.sr.label.width + 10
        self.cursor = 1



    def OnMouseEnter(self):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def OnMouseExit(self):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def GetMenuPosition(self, *args):
        return (self.absoluteLeft, self.absoluteBottom + 2)




