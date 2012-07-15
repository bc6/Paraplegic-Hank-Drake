#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/fontconst.py
import blue
import uiconst
import os
DEFAULT_FONTSIZE = 10
DEFAULT_LINESPACE = 12
DEFAULT_LETTERSPACE = 0
DEFAULT_UPPERCASE = False
STYLE_DEFAULT = 'STYLE_DEFAULT'
try:
    import fontConst
    FONTFAMILY_PER_WINDOWS_LANGUAGEID = fontConst.FONTFAMILY_PER_WINDOWS_LANGUAGEID
except:
    FONTFAMILY_PER_WINDOWS_LANGUAGEID = {}

SYSTEMFONTROOT = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS)
prioritizedFontPaths = ((uiconst.LANG_JAPANESE, STYLE_DEFAULT, ((SYSTEMFONTROOT + '\\msgothic.ttc',
    SYSTEMFONTROOT + '\\msgothic.ttc',
    SYSTEMFONTROOT + '\\msgothic.ttc',
    SYSTEMFONTROOT + '\\msgothic.ttc'),)), (uiconst.LANG_CHINESE, STYLE_DEFAULT, ((SYSTEMFONTROOT + '\\msyh.ttf',
    SYSTEMFONTROOT + '\\msyh.ttf',
    SYSTEMFONTROOT + '\\msyhbd.ttf',
    SYSTEMFONTROOT + '\\msyhbd.ttf'), (SYSTEMFONTROOT + '\\simsun.ttc',
    SYSTEMFONTROOT + '\\simsun.ttc',
    SYSTEMFONTROOT + '\\simsun.ttc',
    SYSTEMFONTROOT + '\\simsun.ttc'))))

def ResolvePriorityList(priorityListPerLanguage):
    for languageID, fontStyle, priorityList in priorityListPerLanguage:
        for each in priorityList:
            if type(each) == tuple:
                for variantPath in each:
                    isThere = os.path.exists(variantPath)
                    if not isThere:
                        break

                if isThere:
                    FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageID] = {fontStyle: each}
                    break
            else:
                isThere = os.path.exists(each)
                if isThere:
                    FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageID] = {fontStyle: each}
                    break


ResolvePriorityList(prioritizedFontPaths)
del ResolvePriorityList
del prioritizedFontPaths
import uiutil
exports = uiutil.AutoExports('fontConst', locals())