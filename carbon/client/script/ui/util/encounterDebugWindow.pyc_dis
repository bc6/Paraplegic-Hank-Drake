#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/util/encounterDebugWindow.py
import uicls
import uiconst

class EncounterDebugWindow(uicls.Window):
    __guid__ = 'uicls.EncounterDebugWindow'
    default_windowID = 'EncounterDebugWindow'
    default_width = 325
    default_height = 325

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetMinSize([self.default_width, self.default_height])
        self.SetCaption('Encounter Debug Window')
        self.sr.content.padding = 5
        self.encounterSpawnServer = sm.RemoteSvc('encounterSpawnServer')
        debugContainer = uicls.Container(parent=self.sr.content)
        uicls.Button(parent=debugContainer, align=uiconst.TOBOTTOM, label='Start Encounter', func=self._StartSelectedEncounter, padding=(0, 3, 0, 0))
        uicls.Button(parent=debugContainer, align=uiconst.TOBOTTOM, label='Stop Encounter', func=self._StopSelectedEncounter, padding=(0, 5, 0, 0))
        uicls.Button(parent=debugContainer, align=uiconst.TOBOTTOM, label='Clear Results', func=self._ClearResults, padding=(0, 5, 0, 0))
        self.results = uicls.EditCore(parent=debugContainer, align=uiconst.TOBOTTOM, padding=(0, 5, 0, 0), readonly=True, name='results')
        self.encounterScroll = uicls.Scroll(parent=debugContainer, name='encounterScroll', align=uiconst.TOALL)
        self.encounterScroll.LoadContent(contentList=self._GetAvailableEncounters())

    def _ClearResults(self, *args):
        self.results.SetValue('', html=0)

    def AppendResult(self, newText):
        currentText = self.results.GetValue()
        if currentText:
            currentText += '<br>------------------<br>'
        currentText += newText
        self.results.SetValue(currentText, html=0)

    def _StartSelectedEncounter(self, *args):
        encounterList = [ node.encounterID for node in self.encounterScroll.GetSelected() ]
        logResults = self.encounterSpawnServer.RequestActivateEncounters(encounterList, logResults=True)
        self.AppendResult(logResults)

    def _StopSelectedEncounter(self, *args):
        encounterList = [ node.encounterID for node in self.encounterScroll.GetSelected() ]
        logResults = self.encounterSpawnServer.RequestDeactivateEncounters(encounterList, logResults=True)
        self.AppendResult(logResults)

    def _GetAvailableEncounters(self):
        encounters = self.encounterSpawnServer.GetMyEncounters()
        contentList = []
        for encounter in encounters:
            data = {'text': encounter['encounterName'],
             'label': encounter['encounterName'],
             'id': encounter['encounterID'],
             'encounterID': encounter['encounterID'],
             'disableToggle': True,
             'hint': encounter['encounterName']}
            contentList.append(uicls.ScrollEntryNode(**data))

        return contentList