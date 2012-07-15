#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/combatLogWindow.py
import base
import uicls
import uiconst

class CombatLogWindow(uicls.Window):
    __guid__ = 'uicls.CombatLogWindow'
    default_width = 540
    default_height = 430
    default_windowID = 'CombatLogWindow'
    DEFAULT_COMBO_OPTION = 'All'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.zactionLoggerSvc = attributes['service']
        self.entityClient = sm.GetService('entityClient')
        self.playerEntID = self.entityClient.GetPlayerEntity().entityID
        self.entityList = []
        self.categoryList = []
        self.selectedCategory = self.DEFAULT_COMBO_OPTION
        self.selectedEntity = self.DEFAULT_COMBO_OPTION
        self.lineNumber = 0
        self.comboElementVersion = 0
        self.minsize = (540, 200)
        self.maincontainer = uicls.Container(parent=self.sr.content, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(5, 5, 5, 5), padTop=20)
        self.combatLogLines = uicls.Scroll(parent=self.maincontainer, name='logScroll', align=uiconst.TOALL, pos=(0, 0, 0, 0), padTop=20)
        self.entityCombo = uicls.Combo(parent=self.maincontainer, callback=self._ForceEntityUpdate, name='entityCombo', align=uiconst.TOPLEFT, width=350)
        self.categoryCombo = uicls.Combo(parent=self.maincontainer, callback=self._ForceCategoryUpdate, name='categoryCombo', align=uiconst.TOPRIGHT, width=150)
        self._GetCombatLogLines(bForceUpdate=True)
        self.sr.updateTimer = base.AutoTimer(100, self._GetCombatLogLines)

    def _OnClose(self, *args):
        uicls.Window._OnClose(self, *args)
        self.sr.updateTimer = None

    def _UpdateComboBoxes(self):
        self.entityList = self.zactionLoggerSvc.GetEntityList()
        self.categoryList = self.zactionLoggerSvc.GetCategoryList()
        self.entityList.sort()
        self.categoryList.sort()
        self.entityCombo.LoadOptions(self.entityList, self.selectedEntity)
        self.categoryCombo.LoadOptions(self.categoryList, self.selectedCategory)

    def _ForceCategoryUpdate(self, uiclsname, header, value, *args):
        self.selectedCategory = value
        self._GetCombatLogLines(bForceUpdate=True)

    def _ForceEntityUpdate(self, uiclsname, header, value, *args):
        self.selectedEntity = value
        self._GetCombatLogLines(bForceUpdate=True)

    def _FilterSelectedEntity(self, scrollEntry):
        self.selectedEntity = scrollEntry.sr.node.entID
        self._GetCombatLogLines(bForceUpdate=True)

    def _GetCombatLogLines(self, bForceUpdate = False):
        serverLineNumber = self.zactionLoggerSvc.GetLineNumber()
        serverComboElementVersion = self.zactionLoggerSvc.GetComboElementVersion()
        if bForceUpdate or serverLineNumber != self.lineNumber:
            self.lineNumber = serverLineNumber
            contentList = []
            logLines = self.zactionLoggerSvc.GetCombatLog(self.selectedEntity, self.selectedCategory)
            for entry in logLines:
                subbedChat, entID, logCategory = entry
                data = {'label': subbedChat,
                 'hideNoItem': True,
                 'OnDblClick': self._FilterSelectedEntity,
                 'entID': entID,
                 'logCategory': logCategory}
                contentList.append(uicls.ScrollEntryNode(**data))

            contentList.reverse()
            self.combatLogLines.LoadContent(contentList=contentList, keepPosition=True)
        if bForceUpdate or serverComboElementVersion != self.comboElementVersion:
            self.comboElementVersion = serverComboElementVersion
            self._UpdateComboBoxes()