import fontConst
import log
import uicls
import uiutil
import uiconst
import util
import trinity
import localization

class Label(uicls.LabelCore):
    __guid__ = 'uicls.Label'
    default_name = 'text'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_fontsize = fontConst.EVE_MEDIUM_FONTSIZE
    default_letterspace = 0
    default_color = (1.0, 1.0, 1.0, 0.75)
    default_align = uiconst.TOPLEFT
    default_allowpartialtext = 1
    default_shadowOffset = (0, 1)

    def DoFontChange(self, *args):
        self.OnCreate(trinity.device)




class EveStyleLabel(Label):
    __guid__ = 'uicls.EveStyleLabel'
    default_name = 'EveStyleLabel'

    def ApplyAttributes(self, attributes):
        fontsize = attributes.get('fontsize', None)
        if fontsize is not None:
            attributes.fontsize = self.default_fontsize
            log.LogTraceback('You are not allowed to change fontsize of a font style - find another style to use or use uicls.Label for custom labels')
        uppercase = attributes.get('uppercase', None)
        if uppercase is not None:
            attributes.uppercase = self.default_uppercase
            log.LogTraceback('You are not allowed to change uppercase of a font style - find another style to use or use uicls.Label for custom labels')
        letterspace = attributes.get('letterspace', None)
        if letterspace is not None:
            attributes.letterspace = self.default_letterspace
            log.LogTraceback('You are not allowed to change letterspace of a font style - find another style to use or use uicls.Label for custom labels')
        Label.ApplyAttributes(self, attributes)




class EveLabelSmall(EveStyleLabel):
    '\n    This is a small eve font, fontsize=%s\n    ' % fontConst.EVE_SMALL_FONTSIZE
    __guid__ = 'uicls.EveLabelSmall'
    default_name = 'EveLabelSmall'
    default_fontsize = fontConst.EVE_SMALL_FONTSIZE
    default_fontStyle = fontConst.STYLE_SMALLTEXT
    default_shadowOffset = (0, 1)


class EveHeaderSmall(EveStyleLabel):
    __guid__ = 'uicls.EveHeaderSmall'
    default_name = 'EveHeaderSmall'
    default_fontStyle = fontConst.STYLE_SMALLTEXT
    default_fontsize = fontConst.EVE_SMALL_FONTSIZE
    default_uppercase = 1
    default_shadowOffset = (0, 1)


class EveLabelSmallBold(EveStyleLabel):
    __guid__ = 'uicls.EveLabelSmallBold'
    default_name = 'EveLabelSmallBold'
    default_fontStyle = fontConst.STYLE_SMALLTEXT
    default_fontsize = fontConst.EVE_SMALL_FONTSIZE
    default_bold = True
    default_shadowOffset = (0, 1)


class EveLabelMedium(EveStyleLabel):
    '\n    This is a medium eve font, fontsize=%s\n    ' % fontConst.EVE_MEDIUM_FONTSIZE
    __guid__ = 'uicls.EveLabelMedium'
    default_name = 'EveLabelMedium'
    default_fontsize = fontConst.EVE_MEDIUM_FONTSIZE
    default_shadowOffset = (0, 1)


class EveHeaderMedium(EveStyleLabel):
    __guid__ = 'uicls.EveHeaderMedium'
    default_name = 'EveHeaderMedium'
    default_fontsize = fontConst.EVE_MEDIUM_FONTSIZE
    default_uppercase = 1
    default_shadowOffset = (0, 1)


class EveLabelMediumBold(EveStyleLabel):
    '\n    This is a bold medium eve font, fontsize=%s\n    ' % fontConst.EVE_MEDIUM_FONTSIZE
    __guid__ = 'uicls.EveLabelMediumBold'
    default_name = 'EveLabelMediumBold'
    default_fontsize = fontConst.EVE_MEDIUM_FONTSIZE
    default_bold = True
    default_shadowOffset = (0, 1)


class EveLabelLarge(EveStyleLabel):
    '\n    This is a large eve font, fontsize=%s\n    ' % fontConst.EVE_LARGE_FONTSIZE
    __guid__ = 'uicls.EveLabelLarge'
    default_name = 'EveLabelLarge'
    default_fontsize = fontConst.EVE_LARGE_FONTSIZE
    default_shadowOffset = (0, 1)


class EveHeaderLarge(EveStyleLabel):
    __guid__ = 'uicls.EveHeaderLarge'
    default_name = 'EveHeaderLarge'
    default_fontsize = fontConst.EVE_LARGE_FONTSIZE
    default_uppercase = 1
    default_fontStyle = fontConst.STYLE_HEADER
    default_shadowOffset = (0, 1)


class EveLabelLargeBold(EveStyleLabel):
    '\n    This is a bold large eve font, fontsize=%s\n    ' % fontConst.EVE_LARGE_FONTSIZE
    __guid__ = 'uicls.EveLabelLargeBold'
    default_name = 'EveLabelLargeBold'
    default_fontsize = fontConst.EVE_LARGE_FONTSIZE
    default_bold = True
    default_shadowOffset = (0, 1)


class EveLabelLargeUpper(EveLabelLarge):
    __guid__ = 'uicls.EveLabelLargeUpper'
    default_name = 'EveLabelLargeUpper'
    default_shadowOffset = (0, 1)


class EveCaptionMedium(EveStyleLabel):
    __guid__ = 'uicls.EveCaptionMedium'
    default_name = 'EveCaptionMedium'
    default_fontsize = 20
    default_bold = True
    default_fontStyle = fontConst.STYLE_HEADER
    default_lineSpacing = -0.18
    default_shadowOffset = (0, 1)


class EveCaptionLarge(EveStyleLabel):
    __guid__ = 'uicls.EveCaptionLarge'
    default_name = 'EveCaptionLarge'
    default_fontsize = 24
    default_bold = True
    default_fontStyle = fontConst.STYLE_HEADER
    default_lineSpacing = -0.18
    default_shadowOffset = (0, 1)


class CaptionLabel(Label):
    __guid__ = 'uicls.CaptionLabel'
    default_name = 'caption'
    default_fontsize = 20
    default_letterspace = 1
    default_align = uiconst.TOALL
    default_idx = -1
    default_state = uiconst.UI_DISABLED
    default_uppercase = True
    default_bold = True
    default_shadowOffset = (0, 1)


class WndCaptionLabel(EveCaptionMedium):
    __guid__ = 'uicls.WndCaptionLabel'
    default_left = 70
    default_top = 8
    default_subcaption = None

    def ApplyAttributes(self, attributes):
        uicls.LabelCore.ApplyAttributes(self, attributes)
        subcaption = attributes.get('subcaption', self.default_subcaption)
        self.subcapt = uicls.EveLabelSmall(text='', parent=self.parent, align=uiconst.TOPLEFT, left=self.left + 1, top=self.top + self.textheight - 2, state=uiconst.UI_HIDDEN, name='subcaption')
        if subcaption:
            self.SetSubcaption(subcaption)



    def SetSubcaption(self, text):
        self.subcapt.text = text
        self.subcapt.state = uiconst.UI_DISABLED




