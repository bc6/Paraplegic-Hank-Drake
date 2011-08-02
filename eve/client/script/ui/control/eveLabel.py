import uicls
import uiutil
import uiconst
import util
import xtriui
import trinity
HINTLABELS = {'showinfo': mls.UI_CMD_SHOWINFO,
 'contract': mls.UI_CMD_SHOWCONTRACT,
 'note': mls.UI_CMD_SHOWNOTE,
 'fleet': mls.UI_CMD_JOINFLEET,
 'localsvc': None,
 'showrouteto': mls.UI_CMD_SHOWROUTE,
 'fitting': mls.UI_CMD_SHOWFITTING,
 'preview': mls.UI_CMD_PREVIEW,
 'CertSlot': mls.UI_CMD_OPENCERTIFICATEPLANNER,
 'fleet': mls.UI_CMD_JOINFLEET}

class Label(uicls.LabelCore):
    __guid__ = 'uicls.Label'
    default_name = 'text'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_fontsize = 12
    default_linespace = 0
    default_letterspace = 0
    default_color = (1.0, 1.0, 1.0, 0.75)
    default_align = uiconst.TOPLEFT
    default_allowpartialtext = 1

    def DoFontChange(self, *args):
        self.OnCreate(trinity.device)



    def ApplyAttributes(self, attributes):
        if eve.session.languageID == 'RU':
            attributes.uppercase = 0
        uicls.LabelCore.ApplyAttributes(self, attributes)



    def CheckLinks(self):
        aLink = None
        if self._links and uicore.uilib.mouseOver == self:
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            (left, top, width, height,) = self.GetAbsolute()
            for (url, startX, startY, endX, endY,) in self._links:
                if left + startX < mouseX < left + endX and top + startY < mouseY < top + endY:
                    hint = url
                    for (k, v,) in HINTLABELS.iteritems():
                        if url.startswith('%s:' % k):
                            hint = v

                    self.sr.hint = hint
                    aLink = url
                    break

            if not aLink:
                self.sr.hint = None
                self.cursor = uiconst.UICURSOR_DEFAULT
            else:
                self.cursor = uiconst.UICURSOR_SELECT
        if aLink != self._activeLink:
            self._activeLink = aLink
            self.Layout()



    def GetParams(self, new = 0):
        if not getattr(self, 'params', None) or new:
            params = uicls.LabelCore.GetParams(self, new)
            params.linespace = self.linespace
            self.params = params
        return self.params




class CaptionLabel(Label):
    __guid__ = 'uicls.CaptionLabel'
    default_name = 'caption'
    default_fontsize = 20
    default_letterspace = 1
    default_align = uiconst.TOALL
    default_autowidth = True
    default_autoheight = True
    default_idx = -1
    default_state = uiconst.UI_DISABLED
    default_uppercase = True


class WndCaptionLabel(CaptionLabel):
    __guid__ = 'uicls.WndCaptionLabel'
    default_left = 70
    default_top = 8
    default_subcaption = None

    def ApplyAttributes(self, attributes):
        uicls.LabelCore.ApplyAttributes(self, attributes)
        subcaption = attributes.get('subcaption', self.default_subcaption)
        self.subcapt = uicls.Label(text='', parent=self.parent, align=uiconst.TOPLEFT, left=self.left + 1, top=self.top + self.textheight - 2, fontsize=9, linespace=9, letterspace=2, state=uiconst.UI_HIDDEN, uppercase=1, name='subcaption')
        if subcaption:
            self.SetSubcaption(subcaption)



    def SetSubcaption(self, text):
        self.subcapt.text = text
        self.subcapt.state = uiconst.UI_DISABLED




