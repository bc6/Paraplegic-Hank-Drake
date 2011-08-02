import blue
import os
import svc
import util
import fontConst
import _PyFreeTypeP as ft
from _PyFreeTypeP import FTC_Manager, FTC_Scaler, FTC_CMapCache, FTC_SBitCache, FTC_ImageType, FTC_SBit, IBBox
from _PyFreeTypeP import Clear_Buffer
globals().update(ft.constants)

class EveFont(svc.font):
    default_unicodeRange = 1
    __guid__ = 'svc.eveFont'
    __displayname__ = 'Font service'
    __replaceservice__ = 'font'

    def Run(self, memStream = None):
        svc.font.Run(self)
        self.ruFonts = None
        self.useEveNeue = False
        self.asianFont = None
        self.zhflags = FT_LOAD_TARGET_LIGHT
        if eve.session.languageID == 'ZH':
            self.asianFont = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS) + '\\simsun.ttc'
            default_unicodeRange = 2
            self.asianFontsize = {10: 12,
             11: 13,
             12: 14,
             13: 14}
        elif not self.useEveNeue and eve.session.languageID == 'RU':
            tryFonts = [('ARIALN.ttf', 'ARIALNI.ttf', 'ARIALNB.ttf', 'ARIALNBI.ttf'),
             ('FRABK.ttf', 'FRABKIT.ttf', 'FRAHV.ttf', 'FRAHVIT.ttf'),
             ('TREBUC.ttf', 'TREBUCIT.ttf', 'TREBUCBD.ttf', 'TREBUCBI.ttf'),
             ('ARIAL.ttf', 'ARIALI.ttf', 'ARIALBD.ttf', 'ARIALBI.ttf'),
             ('TAHOMA.ttf', 'TAHOMA.ttf', 'TAHOMABD.ttf', 'TAHOMABD.ttf'),
             ('MICROSS.ttf', 'MICROSS.ttf', 'MICROSS.ttf', 'MICROSS.ttf'),
             ('L_10646.ttf', 'L_10646.ttf', 'L_10646.ttf', 'L_10646.ttf'),
             ('VERDANA.ttf', 'VERDANAI.ttf', 'VERDANAB.ttf', 'VERDANAZ.ttf')]
            ft = util.FreeType()
            fontDir = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS)
            for family in tryFonts:
                failed = False
                ruFonts = []
                for style in family:
                    fullname = fontDir + '/' + style
                    try:
                        f = ft.New_Res_Face(fullname)
                        ruFonts.append(fullname)
                    except:
                        failed = True
                        break

                if not failed:
                    self.ruFonts = ruFonts
                    break

        else:
            for fontName in ('msgothic.ttc', 'msmincho.ttf'):
                asianFontPath = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS) + '\\' + fontName
                if os.path.exists(asianFontPath):
                    self.asianFont = asianFontPath
                    break

            self.asianFontsize = {}



    def AlterParams(self, params, unicodeRange = None, formatLinks = False):
        if unicodeRange is None:
            unicodeRange = self.default_unicodeRange
        defaultFallback = self.GetFallbackFonts()
        renderLetterSpace = params.letterspace or fontConst.DEFAULT_LETTERSPACE
        renderFontSize = params.fontsize or fontConst.DEFAULT_FONTSIZE
        bold = bool(params.bold)
        italic = bool(params.italic)
        if formatLinks and params.url:
            bold = True
        if self.useEveNeue and eve.session.languageID == 'RU':
            loadflag = FT_LOAD_FORCE_AUTOHINT
            renderFontSize = max(9, renderFontSize - 2)
            renderLetterSpace = max(0, renderLetterSpace - 1)
            defaultFace = self.GetEveFont(params)
            loadflag = FT_LOAD_FORCE_AUTOHINT
        elif self.ruFonts and eve.session.languageID == 'RU':
            idx = bold * 2 + italic * 1
            path = self.ruFonts[idx]
            defaultFace = self.GetFace(path)
            if not defaultFace:
                defaultFace = defaultFallback[0]
            face = defaultFace
            loadflag = FT_LOAD_FORCE_AUTOHINT
        elif unicodeRange == 1:
            defaultFace = self.GetEveFont(params, formatLinks)
            if self.useEveNeue:
                loadflag = FT_LOAD_FORCE_AUTOHINT
                renderFontSize = max(9, renderFontSize - 2)
                renderLetterSpace = max(0, renderLetterSpace - 1)
            else:
                loadflag = FT_LOAD_TARGET_LIGHT
        elif unicodeRange == 2:
            defaultFace = self.GetFace(self.asianFont)
            if not defaultFace:
                defaultFace = defaultFallback[0]
            face = defaultFace
            renderFontSize = max(11, self.asianFontsize.get(renderFontSize, renderFontSize))
            renderLetterSpace = max(0, renderLetterSpace - 1)
            loadflag = self.zhflags
        else:
            idx = bold * 2 + italic * 1
            face = ['arial',
             'ariali',
             'arialbd',
             'arialbi'][idx]
            defaultFace = self.GetFace(blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS) + '\\%s.ttf' % face)
            if not defaultFace:
                defaultFace = self.GetFace(blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS) + '\\msgothic.ttc')
            if not defaultFace:
                defaultFace = defaultFallback[0]
            face = defaultFace
            loadflag = FT_LOAD_TARGET_LIGHT
        if renderFontSize <= 9:
            renderLetterSpace = max(1, renderLetterSpace)
        params = params.Copy()
        params.fontsize = renderFontSize
        params.letterspace = renderLetterSpace
        params.flags = loadflag
        params.face = defaultFace
        params.fallback = defaultFallback
        return params



    def GetEveFont(self, params, formatLinks = False):
        fontsize = params.fontsize or fontConst.DEFAULT_FONTSIZE
        bold = bool(params.bold)
        if formatLinks and params.url:
            bold = True
        italic = bool(params.italic)
        mmwidth = getattr(params, 'mmwidth', None)
        mmbold = getattr(params, 'mmbold', None)
        if self.useEveNeue:
            bold = bold or bool(mmbold)
            idx = bold * 2 + italic * 1
            faceName = ['EveSansNeue.otf',
             'EveSansNeueItalic.otf',
             'EveSansNeueBold.otf',
             'EveSansNeueBoldItalic.otf'][idx]
            face = self.GetFace(blue.os.respath + faceName)
            return face
        if mmwidth is None:
            us = settings.user.ui.Get('fontWFactor', 'normal')
            mmwidth = {'condensed': 0.15,
             'normal': 0.5,
             'expanded': 0.9}.get(us, 0.5)
            if fontsize > 12:
                diff = fontsize - 12
                factor = diff * 0.05
                mmwidth = min(1.0, max(0.15, mmwidth - factor))
        if mmbold is None:
            mmbold = [0.0, min(1.5, max(0.5, 1.5 - (fontsize - 12) * 0.75 / 12))][bold]
        mmitalic = [0.0, 1.5][italic]
        fontid = (mmwidth, mmbold, mmitalic)
        if fontid in self.cmapIdx:
            return self.cmapIdx[fontid]
        self.cmapIdx[fontid] = self.fontcache.AddCMapIdx([('res:/evesansmm.pfb', 0, {'Width': mmwidth,
           'Weight': mmbold,
           'Italic': mmitalic})])[0]
        return self.cmapIdx[fontid]




