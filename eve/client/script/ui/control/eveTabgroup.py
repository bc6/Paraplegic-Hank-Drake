import blue
import uix
import uiutil
import xtriui
import uthread
import sys
import log
import uiconst
import uicls
import trinity
import form
import util

class TabGroup(uicls.TabGroupCore):
    __guid__ = 'uicls.TabGroup'
    default_name = 'tabgroup'
    default_align = uiconst.TOTOP
    default_height = 32
    default_clipChildren = 1
    default_state = uiconst.UI_PICKCHILDREN
    default_leftMargin = 8
    default_rightMargin = 20
    default_minTabsize = 32

    def ApplyAttributes(self, attributes):
        uicls.TabGroupCore.ApplyAttributes(self, attributes)
        tabs = attributes.tabs
        groupID = attributes.groupID
        autoselecttab = attributes.get('autoselecttab', True)
        UIIDPrefix = attributes.UIIDPrefix
        silently = attributes.get('silently', False)
        if tabs:
            self.Startup(tabs, groupID=groupID, autoselecttab=autoselecttab, UIIDPrefix=UIIDPrefix, silently=silently)



    def Startup(self, tabs, groupID = None, _notUsed_callback = None, _notUsed_isSub = 0, _notUsed_detachable = 0, autoselecttab = 1, UIIDPrefix = None, silently = False):
        loadtabs = []
        for each in tabs:
            panelparent = None
            hint = None
            uiID = 'tab'
            if len(each) == 4:
                (label, panel, code, args,) = each
            elif len(each) == 5:
                (label, panel, code, args, panelparent,) = each
            elif len(each) == 6:
                (label, panel, code, args, panelparent, hint,) = each
            if UIIDPrefix is not None:
                secondPart = label.replace(' ', '')
                secondPart = secondPart.capitalize()
                uiID = '%s%s' % (UIIDPrefix, secondPart)
            tabData = uiutil.Bunch()
            tabData.label = label
            tabData.code = code
            tabData.args = args
            tabData.panel = panel
            tabData.panelparent = panelparent
            tabData.hint = hint
            tabData.name = uiID
            loadtabs.append(tabData)

        self.LoadTabs(loadtabs, autoselecttab, settingsID=groupID, silently=silently)




class Tab(uicls.TabCore):
    __guid__ = 'uicls.Tab'
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(uicls.Tab, self).ApplyAttributes(attributes)
        self.isTabStop = False



    def OnMouseEnter(self, *args):
        self.sr.label.color = (1.0, 1.0, 1.0, 1.0)



    def OnMouseExit(self, *args):
        self.sr.label.color = (1.0, 1.0, 1.0, 0.9)




