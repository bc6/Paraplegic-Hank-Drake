import xtriui
import uix
import uiutil
import blue
import util
import log
import listentry
import sys
import uicls
import uiconst

class AuditLogSecureContainerLogViewer(uicls.Window):
    __guid__ = 'form.AuditLogSecureContainerLogViewer'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        itemID = attributes.itemID
        self.scope = 'all'
        self.sr.container = eve.GetInventoryFromId(itemID)
        self.sr.itemID = itemID
        self.sr.logIDmax = None
        self.sr.logIDmin = None
        self.SetMinSize([400, 400])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_SHARED_AUDITLOGSECCONTAINER)
        self.sr.logOptions = uicls.Container(name='logOptions', parent=self.sr.main, align=uiconst.TOTOP, height=36, idx=1)
        sidepar = uicls.Container(name='sidepar', parent=self.sr.logOptions, align=uiconst.TORIGHT, width=54)
        btn = uix.GetBigButton(24, sidepar, 0, 12)
        btn.OnClick = (self.BrowseLog, 0)
        btn.hint = mls.UI_GENERIC_PREVIOUS
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.sr.wndBackBtn = btn
        btn = uix.GetBigButton(24, sidepar, 24, 12)
        btn.OnClick = (self.BrowseLog, 1)
        btn.hint = mls.UI_GENERIC_VIEWMORE
        btn.state = uiconst.UI_HIDDEN
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.wndFwdBtn = btn
        self.sr.fromDate = self.GetNow()
        inpt = uicls.SinglelineEdit(name='fromdate', parent=self.sr.logOptions, setvalue=self.sr.fromDate, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         16,
         72,
         0), maxLength=16)
        uicls.Label(text=mls.UI_GENERIC_DATE, parent=inpt, width=200, autowidth=False, left=0, top=-12, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        self.sr.wndFromDate = inpt
        self.sr.wndFromDate.OnReturn = self.GetDate
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ViewLogForContainer()



    def GetDate(self):
        self.ViewLogForContainer(util.ParseDate(self.sr.wndFromDate.GetValue()))



    def GetNow(self):
        return util.FmtDate(blue.os.GetTime(), 'sn')



    def BrowseLog(self, direction, *args):
        fromDate = None
        if self.sr.fromDate != self.sr.wndFromDate.GetValue():
            fromDate = util.ParseDate(self.sr.wndFromDate.GetValue())
        if direction == 1:
            fromLogID = self.sr.logIDmax
        else:
            fromLogID = self.sr.logIDmin
        self.ViewLogForContainer(fromDate=fromDate, fromLogID=fromLogID, forward=direction)



    def ViewLogForContainer(self, fromDate = None, fromLogID = None, forward = 1):
        log.LogInfo('ViewLogForContainer fromDate:', fromDate, 'fromLogID:', fromLogID, 'forward:', forward)
        if self is None or self.destroyed:
            return 
        try:
            try:
                if fromDate is None and fromLogID is None:
                    if forward == 1:
                        fromLogID = self.sr.logIDmax
                    else:
                        fromLogID = self.sr.logIDmin
                    if fromLogID is None:
                        fromLogID = 1
                scrolllist = []
                self.ShowLoad()
                headers = [mls.UI_GENERIC_DATE,
                 mls.UI_GENERIC_LOCATION,
                 mls.UI_GENERIC_SUBLOCATION,
                 mls.UI_GENERIC_WHO,
                 mls.UI_GENERIC_ACTION,
                 mls.UI_GENERIC_STATUS,
                 mls.UI_GENERIC_TYPE,
                 '%s/%s' % (mls.UI_GENERIC_QTY, mls.UI_GENERIC_OWNER)]
                logs = self.sr.container.ALSCLogGet(fromDate, fromLogID, forward)
                log.LogInfo('result count:', len(logs))
                if len(logs):
                    self.sr.logIDmax = None
                    self.sr.logIDmin = None
                for contLog in logs:
                    log.LogInfo('log:', contLog)
                    subLocation = None
                    if self.sr.logIDmax is None or self.sr.logIDmax < contLog.logID:
                        self.sr.logIDmax = contLog.logID
                    if self.sr.logIDmin is None or self.sr.logIDmin > contLog.logID:
                        self.sr.logIDmin = contLog.logID
                    if contLog.inventoryMgrLocationID == contLog.locationID:
                        if contLog.flagID == const.flagHangar:
                            subLocation = mls.UI_GENERIC_PERSONALHANGAR
                    else:
                        divisionByFlag = {const.flagHangar: 1,
                         const.flagCorpSAG2: 2,
                         const.flagCorpSAG3: 3,
                         const.flagCorpSAG4: 4,
                         const.flagCorpSAG5: 5,
                         const.flagCorpSAG6: 6,
                         const.flagCorpSAG7: 7}
                        if divisionByFlag.has_key(contLog.flagID):
                            divisions = sm.GetService('corp').GetDivisionNames()
                            subLocation = divisions[divisionByFlag[contLog.flagID]]
                    if subLocation is None:
                        location = cfg.evelocations.GetIfExists(contLog.locationID)
                        if location is not None:
                            subLocation = location.locationName
                        else:
                            subLocation = '%s' % contLog.flagID
                    action = '%s' % contLog.actionID
                    arg1 = '%s' % contLog.arg1
                    arg2 = '%s' % contLog.arg2
                    if contLog.actionID == const.ALSCActionAssemble:
                        action = mls.UI_GENERIC_ASSEMBLED
                        arg1 = cfg.invtypes.Get(contLog.arg2).typeName
                        arg2 = cfg.eveowners.Get(contLog.arg1).ownerName
                    elif contLog.actionID == const.ALSCActionRepackage:
                        action = mls.UI_GENERIC_REPACKAGED
                        arg1 = arg2 = mls.UI_GENERIC_NOTAVAILABLESHORT
                    elif contLog.actionID == const.ALSCActionSetName:
                        action = mls.UI_GENERIC_SETNAME
                        arg1 = arg2 = mls.UI_GENERIC_NOTAVAILABLESHORT
                    elif contLog.actionID == const.ALSCActionSetPassword:
                        action = mls.UI_GENERIC_SETPASSWORD
                        if contLog.arg1 == const.SCCPasswordTypeGeneral:
                            arg1 = mls.UI_GENERIC_GENERAL
                        elif contLog.arg1 == const.SCCPasswordTypeConfig:
                            arg1 = mls.UI_GENERIC_CONFIGURATION
                        arg2 = mls.UI_GENERIC_NOTAVAILABLESHORT
                    elif contLog.actionID == const.ALSCActionLock:
                        action = mls.UI_GENERIC_LOCK
                        arg1 = cfg.invtypes.Get(contLog.arg1).typeName
                        arg2 = '%s' % contLog.arg2
                    elif contLog.actionID == const.ALSCActionUnlock:
                        action = mls.UI_GENERIC_UNLOCK
                        arg1 = cfg.invtypes.Get(contLog.arg1).typeName
                        arg2 = '%s' % contLog.arg2
                    elif contLog.actionID == const.ALSCActionEnterPassword:
                        action = mls.UI_GENERIC_ENTERPASSWORD
                        if contLog.arg1 == const.SCCPasswordTypeGeneral:
                            arg1 = mls.UI_GENERIC_GENERAL
                        elif contLog.arg1 == const.SCCPasswordTypeConfig:
                            arg1 = mls.UI_GENERIC_CONFIGURATION
                        arg2 = mls.UI_GENERIC_NOTAVAILABLESHORT
                    elif contLog.actionID == const.ALSCActionConfigure:
                        action = mls.UI_GENERIC_CONFIGURE
                        arg1 = arg2 = mls.UI_GENERIC_NOTAVAILABLESHORT
                    failSucceed = [(mls.UI_GENERIC_FAIL, '0xffff0000'), (mls.UI_GENERIC_SUCCESS, '0xff00ff00')][contLog.status]
                    label = '%s' % util.FmtDate(contLog.logDate)
                    label += '<t>%s' % cfg.evelocations.Get(contLog.inventoryMgrLocationID).locationName
                    label += '<t>%s' % subLocation
                    label += '<t>%s' % cfg.eveowners.Get(contLog.actorID).ownerName
                    label += '<t>%s' % action
                    label += '<t><color=%s>%s</color>' % (failSucceed[1], failSucceed[0])
                    label += '<t>%s' % arg1
                    label += '<t>%s' % arg2
                    data = util.KeyVal()
                    data.label = label
                    data.entryData = contLog
                    data.GetMenu = self.GetDataMenu
                    scrolllist.append(listentry.Get('Generic', data=data))

                self.sr.scroll.Load(None, scrolllist, headers=headers)
                if len(logs) == 50:
                    self.sr.wndBackBtn.state = uiconst.UI_NORMAL
                    self.sr.wndFwdBtn.state = uiconst.UI_NORMAL
                if forward == 1 and len(logs) < 50:
                    self.sr.wndBackBtn.state = uiconst.UI_NORMAL
                    self.sr.wndFwdBtn.state = uiconst.UI_HIDDEN
                if forward == 0 and len(logs) < 50:
                    self.sr.wndBackBtn.state = uiconst.UI_HIDDEN
                    self.sr.wndFwdBtn.state = uiconst.UI_NORMAL
            except UserError as e:
                eve.Message(e.msg, e.dict)
                sys.exc_clear()
                self.Close()

        finally:
            if not self.destroyed:
                self.HideLoad()




    def GetDataMenu(self, entry):
        m = []
        if entry.sr.node.entryData:
            contLog = entry.sr.node.entryData
            if util.IsSolarSystem(contLog.locationID):
                (itemID, typeID,) = (contLog.inventoryMgrLocationID, const.typeSolarSystem)
            else:
                (itemID, typeID,) = (contLog.inventoryMgrLocationID, const.groupStation)
            m += [(mls.UI_CMD_LOCATION, sm.GetService('menu').CelestialMenu(itemID=itemID, mapItem=None, typeID=typeID))]
            m += [None]
            m += [('%s (%s)' % (cfg.eveowners.Get(contLog.actorID).ownerName, mls.UI_SHARED_OPERATOR), sm.GetService('menu').CharacterMenu(contLog.actorID))]
            m += [None]
        return m




