import xtriui
import uiconst
import uix
import uiutil
import cPickle
import form
import blue
import service
import urlparse
import listentry
import browserutil
import corebrowserutil
import util
import os
import uicls
import uiconst

class BrowserGeneralSettings(uicls.Window):
    __guid__ = 'form.BrowserGeneralSettings'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.showNavigationBar = settings.user.ui.Get('browserShowNavBar', True)
        self.showStatusBar = settings.user.ui.Get('browserShowStatusBar', True)
        self.SetWndIcon('ui_9_64_4')
        uicls.WndCaptionLabel(text=mls.UI_BROWSER_BROWSERSETTINGS, parent=self.sr.topParent)
        self.SetCaption(mls.UI_BROWSER_BROWSERSETTINGS)
        self.DefineButtons(uiconst.OKCLOSE, okLabel=mls.UI_CMD_SAVECHANGES, okFunc=self.Save, okModalResult=uiconst.ID_NONE)
        main = self.sr.main
        main.clipChildren = 0
        main.left = main.width = 6
        c = uicls.Container(name='homeCont', parent=main, align=uiconst.TOTOP, height=32)
        l = uicls.Container(name='left', parent=c, align=uiconst.TOLEFT, width=100, state=uiconst.UI_PICKCHILDREN)
        r = uicls.Container(name='right', parent=c, align=uiconst.TORIGHT, width=80, state=uiconst.UI_PICKCHILDREN)
        text = uicls.Label(text='%s:' % mls.UI_SHARED_HOMEPAGE, align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=l, left=0, top=4, width=2, autowidth=False, autoheight=False)
        top = (text.rectHeight - 16) / 2 + 2 if text.rectHeight > 16 else 0
        totalTop = top
        btn = uicls.Button(parent=r, label=mls.UI_CMD_RESET, func=self.ResetHomePage, pos=(0,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        if btn.width > 80:
            r.width = btn.width
        self.sr.homeEdit = uicls.SinglelineEdit(name='homeEdit', setvalue=settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage()), align=uiconst.TOTOP, pos=(0,
         top,
         0,
         0), parent=c)
        uicls.Line(parent=main, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        self.sr.showHideContainer = uicls.Container(name='showHideContainer', parent=main, align=uiconst.TOTOP, height=35, top=0, state=uiconst.UI_PICKCHILDREN)
        self.sr.showStatusBarCbx = uicls.Checkbox(text=mls.UI_BROWSER_SHOWSTATUSBAR, parent=self.sr.showHideContainer, configName='', retval=0, checked=self.showStatusBar)
        self.sr.showNavBarCbx = uicls.Checkbox(text=mls.UI_BROWSER_SHOWNAVIGATIONBAR, parent=self.sr.showHideContainer, configName='', retval=0, checked=self.showNavigationBar)
        uicls.Line(parent=main, align=uiconst.TOTOP, color=(0.5, 0.5, 0.5, 0.75))
        self.sr.cacheContainer = uicls.Container(name='cacheContainer', parent=main, align=uiconst.TOTOP, height=26, top=8, state=uiconst.UI_PICKCHILDREN)
        l = uicls.Container(name='cacheLeft', parent=self.sr.cacheContainer, align=uiconst.TOLEFT, width=100, state=uiconst.UI_PICKCHILDREN)
        r = uicls.Container(name='cacheRight', parent=self.sr.cacheContainer, align=uiconst.TORIGHT, width=80, state=uiconst.UI_PICKCHILDREN)
        if not blue.win32.IsTransgaming():
            text = uicls.Label(text=mls.UI_BROWSER_CACHELOCATION, align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=l, padding=(2, 4, 2, 4))
            top = (text.rectHeight - 16) / 2 + 2 if text.rectHeight > 16 else 0
            totalTop += top
            btn = uicls.Button(parent=r, label=mls.UI_CMD_RESET, func=self.ResetCacheLocation, pos=(0,
             top,
             0,
             0), align=uiconst.TOPRIGHT)
            if btn.width > 80:
                r.width = btn.width
            self.sr.cacheEdit = uicls.SinglelineEdit(name='cacheEdit', setvalue=settings.public.generic.Get('BrowserCache', corebrowserutil.DefaultCachePath()), align=uiconst.TOTOP, pos=(0,
             top,
             0,
             0), parent=self.sr.cacheContainer)
            explainContainer = uicls.Container(name='cacheExplainContainer', parent=main, align=uiconst.TOTOP, height=26)
            uicls.Label(text=mls.UI_BROWSER_CACHECAPTION, align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=explainContainer, autowidth=False, left=4, fontsize=10, uppercase=1, letterspace=1)
            totalTop += 26
            clearCacheContainer = uicls.Container(name='clearCacheContainer', parent=main, align=uiconst.TOTOP, height=14)
            btn = uicls.Button(parent=clearCacheContainer, label=mls.UI_BROWSER_CLEARBROWSERCACHE, func=self.ClearCache)
            btn.hint = mls.UI_BROWSER_CLEARBROWSERCACHE_HINT
            totalTop += 16
        else:
            totalTop -= 32
        self.SetMinSize((500, 204 + totalTop))
        sm.StartService('sites')



    def ResetHomePage(self, *args):
        settings.user.ui.Set('HomePage2', browserutil.DefaultHomepage())
        self.sr.homeEdit.SetValue(settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage()))



    def ResetCacheLocation(self, *args):
        settings.public.generic.Set('BrowserCache', corebrowserutil.DefaultCachePath())
        self.sr.cacheEdit.SetValue(corebrowserutil.DefaultCachePath())



    def Save(self, *args):
        url = self.sr.homeEdit.GetValue().strip()
        if url and url.find('://') < 0:
            url = 'http://' + url
            self.sr.homeEdit.SetValue(url)
        settings.user.ui.Set('HomePage2', url)
        cachePath = self.sr.cacheEdit.GetValue().strip()
        if cachePath:
            self.sr.cacheEdit.SetValue(cachePath)
        settings.public.generic.Set('BrowserCache', cachePath)
        show = bool(self.sr.showStatusBarCbx.GetValue())
        if bool(self.showStatusBar) != show:
            self.showStatusBar = show
            settings.user.ui.Set('browserShowStatusBar', show)
            sm.ScatterEvent('OnBrowserShowStatusBarChange')
        show = bool(self.sr.showNavBarCbx.GetValue())
        if bool(self.showNavigationBar) != show:
            self.showNavigationBar = show
            settings.user.ui.Set('browserShowNavBar', show)
            sm.ScatterEvent('OnBrowserShowNavigationBarChange')



    def ClearCache(self, *args):
        if uicore.Message('BrowserClearCache', {}, uiconst.YESNO) == uiconst.ID_YES:
            b = sm.GetService('window').GetWindow('virtualbrowser')
            if b:
                b.Close()
            sm.GetService('browserHostManager').RestartBrowserHost(clearCache=True)
            self.CloseX()




