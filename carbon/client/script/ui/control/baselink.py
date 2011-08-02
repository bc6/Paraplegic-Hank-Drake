import blue
import uicls
import uiutil
import htmlwriter
import log
import types
import service

class BaseLinkCore(uicls.Container):
    __guid__ = 'uicls.BaseLinkCore'

    def OnClick(self, *args):
        if self.url:
            self.ClickLink(self, self.url.replace('&amp;', '&'))



    def ClickLink(self, parent, URL):
        if URL.startswith('shellexec:http://') or URL.startswith('shellexec:https://'):
            blue.os.ShellExecute(URL[10:])
            return 
        if URL.startswith('localsvc:'):
            self.LocalSvcCall(URL[9:])
            return 
        linkUsed = self.ClickGameLinks(parent, URL)
        if linkUsed:
            return 
        if self.CanOpenBrowser():
            browser = uicore.cmd.OpenBrowser(URL)
        else:
            browser = uiutil.GetBrowser(parent)
            if browser:
                if hasattr(browser.sr, 'window') and hasattr(browser.sr.window, 'ShowHint'):
                    browser.sr.window.ShowHint('')
                browser.GoTo(URL)
            else:
                self.UrlHandlerDelegate(parent, 'GoTo', URL)



    def ClickGameLinks(self, parent, URL):
        return False



    def CanOpenBrowser(self, *args):
        return False



    def GetMenu(self):
        if getattr(self, 'url', None) is None:
            return []
        return self.GetLinkMenu(self, self.url)



    def GetLinkMenu(self, parent, url):
        m = []
        if self.ValidateURL(url):
            url = url.replace('&amp;', '&')
            m += [('mls.UI_CMD_OPENINNEWVIEW', self.UrlHandlerDelegate, (parent, 'NewView', url))]
            m += [('mls.UI_CMD_OPEN', self.UrlHandlerDelegate, (parent, 'GoTo', url))]
        if url.lower().startswith('http'):
            m += [('mls.UI_CMD_COPYURL', self.CopyUrl, (url,))]
        return m



    def ValidateURL(self, URL):
        badURLs = self.GetBadUrls()
        for badURL in badURLs:
            if URL.startswith(badURL):
                return False

        return True



    def GetBadUrls(self, *args):
        return ['shellexec:', 'localsvc:/', 'cmd:/']



    def CopyUrl(self, url):
        blue.pyos.SetClipboardData(url)



    def UrlHandlerDelegate(self, parent, funcName, args):
        handler = getattr(self, 'URLHandler', None)
        if not handler and getattr(parent, 'sr', None) and getattr(parent.sr, 'node', None):
            handler = getattr(parent.sr.node, 'URLHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                apply(func, (args,))
                return 
        sm.GetService('cmd').OpenBrowser(args)



    def LocalSvcCall(self, args):
        kw = htmlwriter.PythonizeArgs(args)
        if 'service' not in kw:
            log.LogError('Invalid LocalSvc args:', args, ' (missing service)')
            return 
        sv = kw['service']
        del kw['service']
        if 'method' not in kw:
            log.LogError('Invalid LocalSvc args:', args, ' (missing method)')
            return 
        method = kw['method']
        del kw['method']
        svc = sm.GetService(sv)
        access = svc.__exportedcalls__.get(method, [])
        if access and type(access) in (types.ListType, types.TupleType):
            access = access[0]
        elif type(access) == types.DictType:
            access = access.get('role', 0)
        else:
            access = 0
        if access & service.ROLE_IGB:
            apply(getattr(svc, method), (), kw)
        else:
            log.LogError('Invalid LocalSvc args:', args, ' (method not allowed)')




