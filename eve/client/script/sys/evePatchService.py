import util
import uiconst
import svc
appName = 'EVE'
patchInfoURLs = {'optic': 'http://www.eve-online.com.cn/patches/',
 'ccp': 'http://www.eveonline.com/patches/'}
optionalPatchInfoURLs = {'optic': 'http://www.eve-online.com.cn/patches/optional/',
 'ccp': 'http://www.eveonline.com/patches/optional/'}

class EvePatchService(svc.patch):
    __guid__ = 'svc.evePatch'
    __displayname__ = 'Patch service'
    __replaceservice__ = 'patch'

    def OptionalUpgradeMessage(self, description, url):
        msg = cfg.GetMessage('CompiledCodeUpgradeAvailable', {'description': description,
         'url': url})
        (ret, suppress,) = sm.GetService('gameui').MessageBox(text=msg.text, title=msg.title, buttons=uiconst.YESNO, icon=uiconst.QUESTION, suppText=mls.UI_SHARED_SUPPRESS2)
        install = ret == uiconst.ID_YES
        if not install and suppress:
            suppress = eve.Message('CompiledCodeUpgradeSuppressConfirm', {}, uiconst.YESNO) == uiconst.ID_YES
        return (install, suppress)



exports = util.AutoExports('appPatch', locals())

