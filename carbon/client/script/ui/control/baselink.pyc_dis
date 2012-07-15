#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/baselink.py
import blue
import uicls
import uiutil
import htmlwriter
import localization
import log
import types
import service
import uiconst

class BaseLinkCore(uicls.Container):
    __guid__ = 'uicls.BaseLinkCore'
    isDragObject = True

    def GetDragData(self, *args):
        if getattr(self, 'url', None) and getattr(self, 'linkText', None):
            entry = uiutil.Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = self.url
            entry.displayText = self.linkText
            return [entry]

    @classmethod
    def PrepareDrag(cls, dragContainer, dragSource, *args):
        dragData = dragContainer.dragData[0]
        displayText = uiutil.TruncateStringTo(dragData.displayText, 24, '...')
        label = uicls.Label(parent=dragContainer, text=uiutil.StripTags(displayText), align=uiconst.TOPLEFT, bold=True)
        uicls.Fill(parent=dragContainer, color=(0, 0, 0, 0.3), padding=(-10, -2, -10, -2))
        dragContainer.width = label.textwidth
        dragContainer.height = label.textheight
        return (2, label.textheight)

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

    def GetStandardLinkHint(self, *args, **kwds):
        return None

    def GetLinkFormat(self, url, linkState = None, linkStyle = None):
        linkState = linkState or uiconst.LINK_IDLE
        fmt = uiutil.Bunch()
        if linkState in (uiconst.LINK_IDLE, uiconst.LINK_DISABLED):
            fmt.color = -23040
        elif linkState in (uiconst.LINK_ACTIVE, uiconst.LINK_HOVER):
            fmt.color = -256
        fmt.bold = True
        return fmt

    def FormatLinkParams(self, params, linkState = None, linkStyle = None):
        if 'priorUrlColor' not in params:
            params.priorUrlColor = params.color
        if 'priorUrlBold' not in params:
            params.priorUrlBold = params.bold
        if 'priorUrlItalic' not in params:
            params.priorUrlItalic = params.italic
        if 'priorUrlUnderline' not in params:
            params.priorUrlUnderline = params.underline
        linkFmt = self.GetLinkFormat(params.url, linkState, linkStyle)
        if linkFmt.color is not None:
            params.color = linkFmt.color
        if linkFmt.underline is not None:
            params.underline = linkFmt.underline
        if linkFmt.bold is not None:
            params.bold = linkFmt.bold
        if linkFmt.italic is not None:
            params.italic = linkFmt.italic

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
            m += [(uiutil.MenuLabel('/Carbon/UI/Commands/OpenInNewView'), self.UrlHandlerDelegate, (parent, 'NewView', url))]
            m += [(uiutil.MenuLabel('/Carbon/UI/Commands/Open'), self.UrlHandlerDelegate, (parent, 'GoTo', url))]
        if url.lower().startswith('http'):
            m += [(uiutil.MenuLabel('/Carbon/UI/Commands/CopyURL'), self.CopyUrl, (url,))]
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