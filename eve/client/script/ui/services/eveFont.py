import bluepy
import svc
import fontConst
import uiconst

class EveFont(svc.font):
    __guid__ = 'svc.eveFont'
    __displayname__ = 'Font service'
    __replaceservice__ = 'font'

    def Run(self, memStream = None):
        svc.font.Run(self)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetFontFamilyBasedOnWindowsLanguageID(self, windowsLanguageID):
        if windowsLanguageID in fontConst.EVEFONTGROUP:
            return fontConst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[uiconst.LANG_ENGLISH]
        return fontConst.FONTFAMILY_PER_WINDOWS_LANGUAGEID.get(windowsLanguageID, None)




