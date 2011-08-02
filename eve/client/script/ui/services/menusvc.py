import sys
import uix
import uiutil
import uthread
import util
import log
import blue
import menu
import form
import xtriui
import moniker
import service
import destiny
import chat
import types
import state
import trinity
import base
import fleetcommon
import math
import inventoryFlagsCommon
import uiconst
import copy
import pos
import uicls
from collections import defaultdict

class MenuSvc(service.Service):
    __guid__ = 'svc.menu'
    __update_on_reload__ = 0
    __dependencies__ = ['account',
     'addressbook',
     'pvptrade',
     'LSC',
     'fleet',
     'pwn',
     'godma',
     'michelle',
     'faction',
     'manufacturing']
    __notifyevents__ = ['DoBallRemove', 'OnSessionChanged']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.primedMoons = {}
        self.bypassCommonFilter = [mls.UI_CMD_REPACKAGE]
        self.multiFunctions = [mls.UI_CMD_REPACKAGE,
         mls.UI_CMD_BREAK,
         mls.UI_CMD_REFINE,
         mls.UI_CMD_REPROCESS,
         mls.UI_CMD_LAUNCHDRONES,
         mls.UI_CMD_TRASHIT,
         mls.UI_CMD_SPLITSTACK,
         mls.UI_CMD_TOHANGARANDREFINE,
         mls.UI_SHARED_SQ_TRAINNOW % {'num': 1},
         mls.UI_SHARED_SKILLS_INJECT,
         mls.UI_CMD_PLUGIN,
         mls.UI_CMD_SETNAME,
         mls.UI_CMD_ASSEMBLECONTAINER,
         mls.UI_CMD_ASSEMBLEPLATFORM,
         mls.UI_CMD_OPENCONTAINER,
         mls.UI_CMD_ASSEMBLESHIP,
         mls.UI_CMD_FITTOACTIVESHIP,
         mls.UI_CMD_OPENDRONEBAY,
         mls.UI_CMD_OPENCARGOHOLD,
         mls.UI_CMD_LAUNCHFORSELF,
         mls.UI_CMD_LAUNCHFORCORP,
         mls.UI_CMD_JETTISON,
         mls.UI_CMD_LAUNCHSHIP,
         mls.UI_CMD_TAKEOUTTRASH,
         mls.UI_CMD_ENGAGETARGET,
         mls.UI_CMD_MINE,
         mls.UI_CMD_MINEREPEATEDLY,
         mls.UI_CMD_RETURNANDORBIT,
         mls.UI_CMD_RETURNTODRONEBAY,
         mls.UI_CMD_DELEGATECONTROL,
         mls.UI_CMD_ASSIST,
         mls.UI_CMD_GUARD,
         mls.UI_CMD_RETURNCONTROL,
         mls.UI_CMD_ABANDONDRONE,
         mls.UI_CMD_SCOOPTODRONEBAY,
         mls.UI_CMD_LOCKITEM,
         mls.UI_CMD_UNLOCKITEM,
         mls.UI_CMD_REPROCESS,
         mls.UI_CMD_MOVETODRONEBAY,
         mls.UI_GENERIC_MEMBER,
         mls.UI_CMD_CONTRACTTHISITEM,
         mls.UI_CMD_AWARDDECORATION,
         mls.UI_CMD_SENDMESSAGE,
         mls.UI_CMD_REMOVEFROMADDRESSBOOK,
         mls.UI_CMD_ADDTOADDRESSBOOK,
         mls.UI_CMD_FORMFLEETWITH,
         mls.UI_CMD_CAPTUREPORTRAIT,
         mls.UI_CMD_LAUNCHSHIP,
         mls.UI_CMD_LAUNCHSHIPFROMBAY,
         mls.UI_CMD_GETREPAIRQUOTE,
         mls.UI_PI_ACCESSCARGOLINK]
        self.allReasonsDict = self.GetReasonsDict()
        self.multiFunctionFunctions = [self.DeliverToCorpHangarFolder]
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self.OnGlobalMouseDown)



    def GetReasonsDict(self):
        dict = {'notInSpace': mls.UI_MENUHINT_CHECKIFINSPACENOT,
         'notInSystem': mls.UI_MENUHINT_CHECKINSYSTEMNOT,
         'notInApporachRange': mls.UI_MENUHINT_CHECKAPPROACHDISTNOT,
         'cantKeepInRange': mls.UI_MENU_KEEPINRANGEFALSE,
         'notStation': mls.UI_MENUHINT_CHECKSTATIONNOT,
         'notStargate': mls.UI_MENUHINT_CHECKSTARGATENOT,
         'notWithinMaxJumpDist': mls.UI_MENUHINT_CHECKJUMPDISTNOT,
         'severalJumpDest': mls.UI_MENUHINT_CHECKSINGLEJUMPDESTNOT,
         'cantUseGate': mls.UI_MENUHINT_CHECKCANUSEGATENOT,
         'notWarpGate': mls.UI_MENUHINT_CHECKWARPGATENOT,
         'notCloseEnoughToWH': mls.UI_MENUHINT_CHECKWORMHOLEDISTNOT,
         'notInLookingRange': mls.UI_MENUHINT_CHECKLOOKATDISTNOT,
         'notWithinMaxTransferRange': mls.UI_MENUHINT_CHECKTRANSFERDISTNOT,
         'notInTargetingRange': mls.UI_MENUHINT_CHECKTARGETINGRANGENOT,
         'notSpacePig': mls.UI_MENUHINT_CHECKSPACEPIGNOT,
         'cantScoopDrone': mls.UI_MENUHINT_CHECKSCOOPABLENOT,
         'droneNotInScooopRange': mls.UI_MENUHINT_CHECKSCOOPDISTNOT,
         'notWithinMaxConfigRange': mls.UI_MENUHINT_CHECKCONFIGDISTNOT,
         'notOwnedByYouOrCorpOrAlliance': mls.UI_MENUHINT_CHECKISMINEORCORPSORALLIANCESNOT,
         'dontControlDrone': mls.UI_MENUHINT_DONTCONTROLDRONE,
         'droneIncapacitated': mls.UI_MENUHINT_CHECKDRONENOT,
         'dontOwnDrone': mls.UI_MENUHINT_DONTOWNDRONE,
         'notInWarpRange': mls.UI_MENUHINT_CHECKWARPDISTNOT,
         'inCapsule': mls.UI_MENUHINT_CHECKINCAPSULE,
         'inWarp': mls.UI_MENUHINT_CHECKWARPACTIVE,
         'pilotInShip': mls.UI_MENUHINT_PILOTINSHIP,
         'inWarpRange': mls.UI_MENUHINT_CHECKWARPDIST,
         'beingTargeted': mls.UI_MENUHINT_CHECKBEINGTARGETED,
         'isMyShip': mls.UI_MENUHINT_CHECKMYSHIP,
         'isNotMyShip': mls.UI_MENUHINT_CHECKMYSHIPNOT,
         'autopilotActive': mls.UI_MENUHINT_CHECKAUTOPILOT,
         'autopilotNotActive': mls.UI_MENUHINT_CHECKAUTOPILOTNOT,
         'isLookingAtItem': mls.UI_MENUHINT_CHECKLOOKINGATITEM,
         'notLookingAtItem': mls.UI_MENUHINT_CHECKLOOKINGATITEMNOT,
         'alreadyTargeted': mls.UI_MENUHINT_CHECKINTARGETS,
         'notInTargets': mls.UI_MENUHINT_CHECKINTARGETSNOT,
         'badGroup': mls.UI_MENUHINT_BADTYPEWITHNAME,
         'thisIsNot': mls.UI_MENUHINT_THISISNOTWITHNAME}
        return dict



    def OnGlobalMouseDown(self, object, *args):
        if not uiutil.IsUnder(object, uicore.layer.menu):
            uiutil.Flush(uicore.layer.menu)
        return True



    def Stop(self, *args):
        self.expandTimer = None



    def OnSessionChanged(self, isremote, session, change):
        self.expandTimer = None
        menu.KillAllMenus()
        if 'solarsystemid' in change:
            self.PrimeMoons()



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        self.LogInfo('DoBallRemove::menusvc', ball.id)
        if sm.GetService('camera').LookingAt() == ball.id and ball.id != session.shipid:
            if terminal:
                uthread.new(self.ResetCameraDelayed, ball.id)
            else:
                sm.GetService('camera').LookAt(session.shipid)



    def ResetCameraDelayed(self, id):
        blue.pyos.synchro.Sleep(5000)
        if sm.GetService('camera').LookingAt() == id:
            sm.GetService('camera').LookAt(session.shipid)



    def TryExpandActionMenu(self, *args):
        if uicore.uilib.Key(uiconst.VK_MENU) or uicore.uilib.Key(uiconst.VK_CONTROL):
            return 0
        wantedBtn = settings.user.ui.Get('actionmenuBtn', 0)
        if not uicore.uilib.rightbtn and (uicore.uilib.leftbtn and wantedBtn == 0 or uicore.uilib.midbtn and wantedBtn == 2):
            self.expandTimer = base.AutoTimer(settings.user.ui.Get('actionMenuExpandTime', 150), self._TryExpandActionMenu, *args)
            return 1
        return 0



    def _TryExpandActionMenu(self, itemID, x, y, wnd):
        self.expandTimer = None
        if wnd.destroyed:
            return 
        v = trinity.TriVector(float(uicore.uilib.x - x), float(uicore.uilib.y - y), 0.0)
        if int(v.Length() > 12):
            return 
        slimItem = uix.GetBallparkRecord(itemID)
        if not slimItem:
            return 
        self.ExpandActionMenu(slimItem)



    def ExpandActionMenu(self, slimItem, centerItem = None):
        uix.Flush(uicore.layer.menu)
        menu = xtriui.ActionMenu(name='actionMenu', parent=uicore.layer.menu, state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
        uicore.uilib.SetMouseCapture(menu)
        menu.expandTime = blue.os.GetTime()
        menu.Load(slimItem, centerItem)
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            sm.StartService('state').SetState(slimItem.itemID, state.selected, 1)
            menu.Close()
            return 
        sm.StartService('state').SetState(slimItem.itemID, state.mouseOver, 0)
        menu.state = uiconst.UI_NORMAL
        uicls.Container(name='blocker', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        if slimItem.itemID == session.shipid:
            displayName = '%s %s' % (mls.UI_GENERIC_YOUR, cfg.invgroups.Get(slimItem.groupID).name)
        else:
            displayName = uix.GetSlimItemName(slimItem)
            bp = sm.StartService('michelle').GetBallpark()
            if bp:
                ball = bp.GetBall(slimItem.itemID)
                if ball:
                    displayName += ' ' + util.FmtDist(ball.surfaceDist)
        self.AddHint(displayName, menu)



    def AddHint(self, hint, where):
        hintobj = uicls.Container(parent=where, name='hint', align=uiconst.TOPLEFT, width=200, height=16, idx=0, state=uiconst.UI_DISABLED)
        hintobj.hinttext = uicls.Label(text=hint, parent=hintobj, top=4, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1)
        border = uicls.Frame(parent=hintobj, frameConst=uiconst.FRAME_BORDER1_CORNER5, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
        frame = uicls.Frame(parent=hintobj, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER4, state=uiconst.UI_DISABLED)
        if hintobj.hinttext.textwidth > 200:
            hintobj.hinttext.autowidth = 0
            hintobj.hinttext.width = 200
            hintobj.hinttext.text = '<center>' + hint + '</center>'
        hintobj.width = max(56, hintobj.hinttext.textwidth + 16)
        hintobj.height = max(16, hintobj.hinttext.textheight + hintobj.hinttext.top * 2)
        hintobj.left = (where.width - hintobj.width) / 2
        hintobj.top = -hintobj.height - 4
        hintobj.hinttext.left = (hintobj.width - hintobj.hinttext.textwidth) / 2



    def MapMenu(self, itemIDs, unparsed = 0):
        if type(itemIDs) == list:
            menus = []
            for itemID in itemIDs:
                menus.append(self._MapMenu(itemID, unparsed))

            return self.MergeMenus(menus)
        else:
            return self._MapMenu(itemIDs, unparsed)



    def _MapMenu(self, itemID, unparsed = 0):
        mapItem = sm.StartService('map').GetItem(itemID)
        if mapItem is None:
            return []
        checkSolarsystem = mapItem.typeID == const.typeSolarSystem
        menuEntries = []
        if checkSolarsystem is True:
            waypoints = sm.StartService('starmap').GetWaypoints()
            (uni, regionID, constellationID, _sol, _item,) = sm.StartService('map').GetParentLocationID(itemID, gethierarchy=1)
            checkInWaypoints = itemID in waypoints
            menuEntries += [None]
            if checkSolarsystem:
                menuEntries += [[mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (itemID, 1)]]
                if checkInWaypoints:
                    menuEntries += [[mls.UI_CMD_REMOVEWAYPOINT, sm.StartService('starmap').ClearWaypoints, (itemID,)]]
                else:
                    menuEntries += [[mls.UI_CMD_ADDWAYPOINT, sm.StartService('starmap').SetWaypoint, (itemID,)]]
                menuEntries += [[mls.UI_CMD_BOOKMARKLOCATION, self.Bookmark, (itemID, const.typeSolarSystem, constellationID)]]
        if unparsed:
            return menuEntries
        return self.ParseMenu(menuEntries)



    def InvItemMenu(self, invItems, viewOnly = 0, voucher = None, unparsed = 0, filterFunc = None):
        if type(invItems) == list:
            menus = []
            for (invItem, viewOnly, voucher,) in invItems:
                menus.append(self._InvItemMenu(invItem, viewOnly, voucher, unparsed, len(invItems) > 1, filterFunc, allInvItems=invItems))

            return self.MergeMenus(menus)
        else:
            return self.MergeMenus([self._InvItemMenu(invItems, viewOnly, voucher, unparsed, filterFunc=filterFunc, allInvItems=None)])



    def _InvItemMenu(self, invItem, viewOnly, voucher, unparsed = 0, multi = 0, filterFunc = None, allInvItems = None):
        if invItem.groupID == const.groupMoney:
            return []
        godmaSM = self.godma.GetStateManager()
        invType = cfg.invtypes.Get(invItem.typeID)
        groupID = invType.groupID
        invGroup = cfg.invgroups.Get(groupID)
        categoryID = invGroup.categoryID
        invCategory = cfg.invcategories.Get(categoryID)
        serviceMask = None
        if session.stationid:
            serviceMask = eve.stationItem.serviceMask
        checkIfInSpace = self.GetCheckInSpace()
        checkIfInStation = self.GetCheckInStation()
        checkIfDrone = categoryID == const.categoryDrone
        checkIfInDroneBay = invItem.flagID == const.flagDroneBay
        checkIfInHangar = invItem.flagID == const.flagHangar
        checkIfInCargo = invItem.flagID == const.flagCargo
        locationItem = checkIfInSpace and self.michelle.GetItem(invItem.locationID) or None
        checkIfDBLessAmmo = type(invItem.itemID) is tuple and locationItem is not None and locationItem.categoryID == const.categoryStructure
        checkIfInShipMA = locationItem is not None and locationItem.groupID in (const.groupShipMaintenanceArray, const.groupAssemblyArray)
        checkIfInShipMAShip = locationItem is not None and locationItem.categoryID == const.categoryShip and godmaSM.GetType(locationItem.typeID).hasShipMaintenanceBay and invItem.flagID == const.flagShipHangar
        checkIfInShipMAShip2 = locationItem is not None and locationItem.categoryID == const.categoryShip and godmaSM.GetType(locationItem.typeID).hasShipMaintenanceBay and invItem.flagID == const.flagShipHangar and invItem.locationID != session.shipid
        checkIfShipMAShip = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).hasShipMaintenanceBay)
        checkIfShipCHShip = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).hasCorporateHangars)
        checkMAInRange = self.CheckMAInRange(const.maxConfigureDistance)
        checkIfShipFuelBay = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialFuelBayCapacity)
        checkIfShipOreHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialOreHoldCapacity)
        checkIfShipGasHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialGasHoldCapacity)
        checkIfShipMineralHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialMineralHoldCapacity)
        checkIfShipSalvageHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialSalvageHoldCapacity)
        checkIfShipShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialShipHoldCapacity)
        checkIfShipSmallShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialSmallShipHoldCapacity)
        checkIfShipMediumShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialMediumShipHoldCapacity)
        checkIfShipLargeShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialLargeShipHoldCapacity)
        checkIfShipIndustrialShipHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialIndustrialShipHoldCapacity)
        checkIfShipAmmoHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialAmmoHoldCapacity)
        checkIfShipCommandCenterHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialCommandCenterHoldCapacity)
        checkIfShipPlanetaryCommoditiesHold = categoryID == const.categoryShip and bool(godmaSM.GetType(invItem.typeID).specialPlanetaryCommoditiesHoldCapacity)
        checkViewOnly = bool(viewOnly)
        checkIfAtStation = util.IsStation(invItem.locationID)
        checkIfActiveShip = invItem.itemID == session.shipid
        checkIfInHangarAtStation = not (bool(checkIfInHangar) and invItem.locationID != session.stationid)
        checkContainer = invItem.groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupMissionContainer)
        checkCanContain = cfg.IsContainer(invItem)
        checkSingleton = bool(invItem.singleton)
        checkBPSingleton = bool(invItem.singleton) and invItem.categoryID == const.categoryBlueprint
        checkPlasticWrap = invItem.typeID == const.typePlasticWrap
        checkIsStation = util.IsStation(invItem.itemID)
        checkIfMineOrCorps = invItem.ownerID in [session.corpid, session.charid]
        checkIfImInStation = bool(session.stationid)
        checkIfIsMine = invItem.ownerID == session.charid
        checkIfIsShip = invItem.categoryID == const.categoryShip
        checkIfIsCapsule = invItem.groupID == const.groupCapsule
        checkIfIsMyCorps = invItem.ownerID == session.corpid
        checkIfIsStructure = invItem.categoryID == const.categoryStructure
        checkIfIsSovStructure = categoryID == const.categorySovereigntyStructure
        checkIfIsHardware = invCategory.IsHardware()
        checkActiveShip = bool(session.shipid)
        checkIfRepackable = categoryID in const.repackableCategorys or groupID in const.repackableGroups
        checkIfNoneLocation = invItem.flagID == const.flagNone
        checkIfAnchorable = invGroup.anchorable
        checkConstructionPF = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
        checkMineable = categoryID == const.categoryAsteroid or groupID == const.groupHarvestableCloud
        checkRefining = bool(session.stationid) and bool(serviceMask & const.stationServiceRefinery or serviceMask & const.stationServiceReprocessingPlant)
        checkRefinable = bool(checkRefining) and sm.StartService('reprocessing').GetOptionsForItemTypes({invItem.typeID: 0})[invItem.typeID].isRefinable
        checkRecyclable = bool(checkRefining) and sm.StartService('reprocessing').GetOptionsForItemTypes({invItem.typeID: 0})[invItem.typeID].isRecyclable
        checkSkill = categoryID == const.categorySkill
        checkImplant = categoryID == const.categoryImplant and bool(godmaSM.GetType(invItem.typeID).implantness)
        checkPilotLicence = invItem.groupID == const.groupGameTime
        checkReverseRedeemable = invItem.groupID in const.reverseRedeemingLegalGroups
        checkBooster = groupID == const.groupBooster and bool(godmaSM.GetType(invItem.typeID).boosterness)
        checkSecContainer = groupID in (const.groupSecureCargoContainer, const.groupAuditLogSecureContainer)
        checkIfInQuickBar = invItem.typeID in settings.user.ui.Get('marketquickbar', [])
        checkMultiSelection = bool(multi)
        checkAuditLogSecureContainer = groupID == const.groupAuditLogSecureContainer
        checkIfLockedInALSC = invItem.flagID == const.flagLocked
        checkIfUnlockedInALSC = invItem.flagID == const.flagUnlocked
        checkSameLocation = self.CheckSameLocation(invItem)
        checkHasMarketGroup = cfg.invtypes.Get(invItem.typeID).marketGroupID is not None
        checkIsPublished = cfg.invtypes.Get(invItem.typeID).published
        checkRepairService = bool(session.stationid) and bool(serviceMask & const.stationServiceRepairFacilities)
        checkIfRepairable = util.IsItemOfRepairableType(invItem)
        checkLocationInSpace = locationItem is not None
        checkLocationCorpHangarArrayEquivalent = locationItem is not None and locationItem.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray)
        checkShipInStructure = locationItem is not None and locationItem.categoryID == const.categoryStructure and invItem.categoryID == const.categoryShip
        checkInControlTower = locationItem is not None and locationItem.groupID == const.groupControlTower
        checkIfInHangarOrCorpHangarAndCanTake = self.CheckIfInHangarOrCorpHangarAndCanTake(invItem)
        checkIfInDeliveries = invItem.flagID == const.flagCorpMarket
        checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake = checkIfInHangarOrCorpHangarAndCanTake or checkIfInDeliveries
        checkIsRamInstallable = sm.StartService('manufacturing').IsRamInstallable(invItem)
        checkIsReverseEngineering = sm.StartService('manufacturing').IsReverseEngineering(invItem)
        checkIfLockableBlueprint = self.CheckIfLockableBlueprint(invItem)
        checkIfUnlockableBlueprint = self.CheckIfUnlockableBlueprint(invItem)
        checkIfIAmDirector = session.corprole & const.corpRoleDirector > 0
        checkItemIsInSpace = bool(const.minSolarSystem <= invItem.locationID <= const.maxSolarSystem)
        checkStack = invItem.stacksize > 1
        checkIfQueueOpen = sm.StartService('skillqueue').IsQueueWndOpen()
        checkMultStations = False
        if allInvItems and len(allInvItems) > 0:
            checkIsMultipleStations = False
            locationIDCompare = allInvItems[0][0].locationID
            for item in allInvItems:
                item = item[0]
                if item.locationID != locationIDCompare:
                    checkIsMultipleStations = True
                    break

            checkMultStations = checkIsMultipleStations
        menuEntries = MenuList()
        if checkIfActiveShip:
            menuEntries += self.RigSlotMenu(invItem.itemID)
        if not checkMultiSelection:
            menuEntries += [[mls.UI_CMD_SHOWINFO, self.ShowInfo, (invItem.typeID,
               invItem.itemID,
               0,
               invItem,
               None)]]
        if checkIfInSpace and checkIfDrone and checkIfInDroneBay and not checkViewOnly:
            menuEntries += [[mls.UI_CMD_LAUNCHDRONES, self.LaunchDrones, [invItem]]]
        else:
            prereqs = [('notInSpace', checkIfInSpace, True), ('badGroup',
              checkIfDrone,
              True,
              {'groupName': invCategory.name})]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_LAUNCHDRONES] = reason
        if checkStack and not checkIfInDeliveries and checkIfIsMyCorps and checkIfInHangarOrCorpHangarAndCanTake:
            menuEntries += [[mls.UI_CMD_SPLITSTACK, self.SplitStack, [invItem]]]
        menuEntries += [None]
        if checkIfInStation and checkRefining and not checkViewOnly and not checkIfInDeliveries:
            if checkMineable and checkRefinable and checkIfAtStation and checkIfInHangarAtStation:
                menuEntries += [[mls.UI_CMD_REFINE, self.Refine, [invItem]]]
            if checkSameLocation and checkRecyclable and checkIfAtStation and not checkIfActiveShip:
                menuEntries += [[mls.UI_CMD_REPROCESS, self.Refine, [invItem]]]
            if checkMineable and not checkIfAtStation and checkRefinable:
                menuEntries += [[mls.UI_CMD_TOHANGARANDREFINE, self.RefineToHangar, [invItem]]]
        menuEntries += [None]
        if not checkViewOnly:
            if checkSameLocation:
                if checkSkill and not checkIfQueueOpen:
                    menuEntries += [[mls.UI_SHARED_SQ_TRAINNOW % {'num': 1}, self.TrainNow, [invItem]]]
                if checkSkill:
                    menuEntries += [[mls.UI_SHARED_SKILLS_INJECT, self.InjectSkillIntoBrain, [invItem]]]
                if checkImplant:
                    menuEntries += [[mls.UI_CMD_PLUGIN, self.PlugInImplant, [invItem]]]
                if checkBooster:
                    menuEntries += [[mls.UI_CMD_CONSUME, self.ConsumeBooster, [invItem]]]
            if checkPilotLicence and not checkMultiSelection:
                menuEntries += [[mls.UI_CMD_APPLYPILOTLICENCE, self.ApplyPilotLicence, (invItem.itemID,)]]
            if checkReverseRedeemable and not checkMultiSelection:
                menuEntries += [[mls.UI_CMD_REVERSEREDEEM, sm.GetService('redeem').ReverseRedeem, (invItem,)]]
        menuEntries += [None]
        if not checkViewOnly and checkSameLocation and not checkMultiSelection and checkSingleton:
            if checkSecContainer and checkIfInStation:
                menuEntries += [[mls.UI_CMD_SETNEWPASSWORD, self.AskNewContainerPwd, ([invItem], mls.UI_GENERIC_SETPASSWORDONSECURECONT, const.SCCPasswordTypeGeneral)]]
            if checkAuditLogSecureContainer and checkIfInStation:
                menuEntries += [[mls.UI_CMD_SETNEWCONFIGURATIONPASSWORD, self.AskNewContainerPwd, ([invItem], mls.UI_GENERIC_SETPASSWORDONSECURECONT, const.SCCPasswordTypeConfig)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[mls.UI_CMD_VIEWLOG, self.ViewAuditLogForALSC, (invItem.itemID,)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[mls.UI_CMD_CONFIGURECONTAINER, self.ConfigureALSC, (invItem.itemID,)]]
            if checkAuditLogSecureContainer and checkIfMineOrCorps:
                menuEntries += [[mls.UI_CMD_RETRIEVEPASSWORD, self.RetrievePasswordALSC, (invItem.itemID,)]]
            if checkContainer:
                menuEntries += [[mls.UI_CMD_SETNAME, self.SetName, [invItem]]]
        if checkContainer and checkIfInStation and not checkSingleton and not checkViewOnly and checkSameLocation:
            menuEntries += [[mls.UI_CMD_ASSEMBLECONTAINER, self.AssembleContainer, [invItem]]]
        menuEntries += [None]
        if checkConstructionPF and not checkViewOnly and checkSingleton and not checkMultiSelection:
            menuEntries += [[mls.UI_CMD_SETACCESSPASSWORD, self.AskNewContainerPwd, ([invItem], mls.UI_GENERIC_SETACCESSPASSWORDONCONSTRPLATFORM, const.SCCPasswordTypeGeneral)]]
            menuEntries += [[mls.UI_CMD_SETBUILDPASSWORD, self.AskNewContainerPwd, ([invItem], mls.UI_GENERIC_SETBUILDPASSWORDONCONSTRPLATFORM, const.SCCPasswordTypeConfig)]]
        if checkIfInSpace and checkIfDBLessAmmo and not checkMultiSelection:
            menuEntries += [[mls.UI_CMD_TRANSFERTOCARGO, self.TransferToCargo, (invItem.itemID,)]]
        menuEntries += [None]
        if checkIfUnlockedInALSC:
            menuEntries += [[mls.UI_CMD_LOCKITEM, self.ALSCLock, [invItem]]]
        if checkIfLockedInALSC:
            menuEntries += [[mls.UI_CMD_UNLOCKITEM, self.ALSCUnlock, [invItem]]]
        if checkIfLockableBlueprint:
            menuEntries += [[mls.UI_CMD_PROPOSE_LOCKDOWN_VOTE, self.LockDownBlueprint, (invItem,)]]
        if checkIfUnlockableBlueprint:
            menuEntries += [[mls.UI_CMD_PROPOSE_UNLOCK_VOTE, self.UnlockBlueprint, (invItem,)]]
        if checkIfInStation and checkRepairService and checkIfRepairable and checkIfAtStation and checkSameLocation and checkIfIsMine:
            menuEntries += [[mls.UI_CMD_GETREPAIRQUOTE, self.RepairItems, [invItem]]]
        if checkHasMarketGroup and not checkMultiSelection and not checkIsStation:
            menuEntries += [[mls.UI_CMD_VIEWMARKETDETAILS, self.ShowMarketDetails, (invItem,)]]
            if checkIfMineOrCorps and not checkIfActiveShip and checkIfInHangarOrCorpHangarAndCanTake and not checkBPSingleton:
                menuEntries += [[mls.UI_CMD_SELLTHISITEM, self.QuickSell, (invItem,)]]
            menuEntries += [[mls.UI_CMD_BUYTHISTYPE, self.QuickBuy, (invItem.typeID,)]]
        if not checkIsStation and checkIfMineOrCorps and not checkIfActiveShip and not checkMultStations and checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake:
            menuEntries += [[mls.UI_CMD_CONTRACTTHISITEM, self.QuickContract, [invItem]]]
        if checkIsPublished and not checkMultiSelection and not checkIsStation:
            menuEntries += [[mls.UI_CMD_FINDINCONTRACTS, sm.GetService('contracts').FindRelated, (invItem.typeID,
               None,
               None,
               None,
               None,
               None)]]
        if checkHasMarketGroup and not checkIfInQuickBar and not checkMultiSelection and not checkIsStation:
            menuEntries += [[mls.UI_CMD_ADDTOMARKETQUICKBAR, self.AddToQuickBar, (invItem.typeID,)]]
        if checkIfInQuickBar and not checkMultiSelection:
            menuEntries += [[mls.UI_CMD_REMOVEFROMMARKETQUICKBAR, self.RemoveFromQuickBar, (invItem,)]]
        if checkIfInHangar and checkIfAtStation and checkIfIsMine and checkCanContain:
            menuEntries += [[mls.UI_CMD_VIEWCONTENTS, self.GetContainerContents, [invItem]]]
        if not checkViewOnly and checkSingleton:
            if checkSameLocation and checkContainer:
                menuEntries += [[mls.UI_CMD_OPENCONTAINER, self.OpenContainer, [invItem]]]
                if checkIfAtStation and checkIfInHangar and checkPlasticWrap:
                    menuEntries += [[mls.UI_CMD_BREAK, self.Break, [invItem]]]
                    menuEntries += [[mls.UI_CMD_DELIVER, self.DeliverCourierContract, [invItem]]]
            if checkSameLocation and checkIfIsShip and checkIfImInStation and checkIfAtStation and checkIfInHangar and checkIfIsMine and not checkMultiSelection:
                if not checkIfActiveShip and checkIfMineOrCorps:
                    menuEntries += [[mls.UI_CMD_MAKEACTIVE, self.ItemLockFunction, (invItem,
                       mls.UI_GENERIC_ACTIVATED.lower(),
                       self.ActivateShip,
                       (invItem,))]]
                if checkIfActiveShip and checkIfMineOrCorps and not checkIfIsCapsule:
                    menuEntries += [[mls.UI_CMD_LEAVESHIP, self.ItemLockFunction, (invItem,
                       mls.UI_GENERIC_LEAVINGSHIP.lower(),
                       self.LeaveShip,
                       (invItem,))]]
                if not checkIfIsCapsule:
                    menuEntries += [[mls.UI_CMD_STRIPFITTING, self.StripFitting, [invItem]]]
        if checkContainer and checkPlasticWrap:
            menuEntries += [[mls.UI_CMD_FINDCONTRACT, self.FindCourierContract, [invItem]]]
        menuEntries += [None]
        if checkIsRamInstallable:
            for (actID, text,) in sm.GetService('manufacturing').GetActivities():
                if actID != const.activityNone:
                    menuEntries += [[(text, menu.BLUEPRINTGROUP), self.Manufacture, [invItem, actID]]]

        if checkIsReverseEngineering:
            for (actID, text,) in sm.GetService('manufacturing').GetActivities():
                if actID == const.activityReverseEngineering:
                    menuEntries += [[(text, menu.BLUEPRINTGROUP), self.Manufacture, [invItem, actID]]]

        menuEntries += [None]
        if not checkViewOnly:
            if checkIfIsShip and checkSameLocation and checkIfImInStation and checkIfAtStation and checkIfInHangar and checkIfIsMine and not checkSingleton:
                menuEntries += [[mls.UI_CMD_ASSEMBLESHIP, self.AssembleShip, [invItem]]]
            if checkIfIsShip and checkIfInSpace and checkIfInCargo and checkIfIsMine and not checkSingleton:
                menuEntries += [[mls.UI_CMD_ASSEMBLESHIP, self.AssembleShip, [invItem]]]
            if checkIfIsShip and checkIfInSpace and checkLocationCorpHangarArrayEquivalent and checkLocationInSpace and not checkSingleton:
                menuEntries += [[mls.UI_CMD_ASSEMBLESHIP, self.AssembleShip, [invItem]]]
            if checkIfImInStation and checkIfIsHardware and checkActiveShip and checkSameLocation and not checkImplant and not checkBooster:
                menuEntries += [[mls.UI_CMD_FITTOACTIVESHIP, self.TryFit, [invItem]]]
            if checkIfInSpace and not checkIfInDroneBay and checkIfDrone and checkMAInRange:
                menuEntries += [[mls.UI_CMD_MOVETODRONEBAY, self.FitDrone, [invItem]]]
        menuEntries += [None]
        if checkIfImInStation and checkIfInHangar and checkIfIsShip and checkSingleton and checkSameLocation:
            menuEntries += [[mls.UI_CMD_OPENCARGOHOLD, self.OpenCargohold, [invItem]]]
            if checkIfShipMAShip:
                menuEntries += [[mls.UI_CMD_OPENSHIPMAINTENANCEBAY, self.OpenShipMaintenanceBayShip, (invItem.itemID, mls.UI_SHIPMAINTENANCEBAY)]]
            if checkIfShipCHShip:
                menuEntries += [[mls.UI_CMD_OPENCORPHANGARS, self.OpenShipCorpHangars, (invItem.itemID, 'Corporate Hangars')]]
            menuEntries += [[mls.UI_CMD_OPENDRONEBAY, self.OpenDroneBay, [invItem]]]
        if checkIfImInStation and checkIfInHangar and checkIfIsShip and checkSingleton and checkSameLocation:
            if checkIfShipFuelBay:
                menuEntries += [[mls.UI_CMD_OPENFUELBAY, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedFuelBay)]]
            if checkIfShipOreHold:
                menuEntries += [[mls.UI_CMD_OPENOREHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedOreHold)]]
            if checkIfShipGasHold:
                menuEntries += [[mls.UI_CMD_OPENGASHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedGasHold)]]
            if checkIfShipMineralHold:
                menuEntries += [[mls.UI_CMD_OPENMINERALHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedMineralHold)]]
            if checkIfShipSalvageHold:
                menuEntries += [[mls.UI_CMD_OPENSALVAGEHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedSalvageHold)]]
            if checkIfShipShipHold:
                menuEntries += [[mls.UI_CMD_OPENSHIPHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedShipHold)]]
            if checkIfShipSmallShipHold:
                menuEntries += [[mls.UI_CMD_OPENSMALLSHIPHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedSmallShipHold)]]
            if checkIfShipMediumShipHold:
                menuEntries += [[mls.UI_CMD_OPENMEDIUMSHIPHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedMediumShipHold)]]
            if checkIfShipLargeShipHold:
                menuEntries += [[mls.UI_CMD_OPENLARGESHIPHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedLargeShipHold)]]
            if checkIfShipIndustrialShipHold:
                menuEntries += [[mls.UI_CMD_OPENINDUSTRIALSHIPHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedIndustrialShipHold)]]
            if checkIfShipAmmoHold:
                menuEntries += [[mls.UI_CMD_OPENAMMOHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedAmmoHold)]]
            if checkIfShipCommandCenterHold:
                menuEntries += [[mls.UI_CMD_OPENCOMMANDCENTERHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedCommandCenterHold)]]
            if checkIfShipPlanetaryCommoditiesHold:
                menuEntries += [[mls.UI_CMD_OPENPLANETARYCOMMODITIESHOLD, self.OpenSpecialCargoBay, (invItem.itemID, const.flagSpecializedPlanetaryCommoditiesHold)]]
        menuEntries += [None]
        if checkSameLocation and checkIfImInStation and checkIfInHangar and checkIfIsShip and checkIfIsMine and checkSingleton and not checkMultiSelection and not checkViewOnly:
            menuEntries += [[mls.UI_CMD_CHANGENAME, self.ItemLockFunction, (invItem,
               mls.UI_GENERIC_RENAMED.lower(),
               self.SetName,
               [[invItem]])]]
        if not checkIsStation and not checkLocationInSpace and checkSingleton and checkIfInHangarOrCorpHangarAndCanTake and checkIfMineOrCorps and not checkIfActiveShip and checkIfRepackable:
            menuEntries += [[mls.UI_CMD_REPACKAGE, self.Repackage, [invItem]]]
        menuEntries += [None]
        if checkIfInSpace and not checkViewOnly:
            if checkIfInCargo and checkIfAnchorable and not checkConstructionPF and not checkIfIsStructure and not checkIfIsSovStructure:
                menuEntries += [[mls.UI_CMD_LAUNCHFORSELF, self.LaunchForSelf, [invItem]]]
            if checkIfInCargo and checkIfAnchorable:
                menuEntries += [[mls.UI_CMD_LAUNCHFORCORP, self.LaunchForCorp, [invItem]]]
            if checkIfInCargo and not checkPlasticWrap:
                menuEntries += [[mls.UI_CMD_JETTISON, self.Jettison, [invItem]]]
            if checkIfIsShip:
                if checkIfInShipMA:
                    menuEntries += [[mls.UI_CMD_LAUNCHSHIP, self.LaunchSMAContents, [invItem]]]
                    menuEntries += [[mls.UI_CMD_BOARDSHIP, self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
                if checkIfInShipMAShip:
                    menuEntries += [[mls.UI_CMD_LAUNCHSHIPFROMBAY, self.LaunchSMAContents, [invItem]]]
                if checkIfInShipMAShip2:
                    menuEntries += [[mls.UI_CMD_BOARDSHIPFROMBAY, self.BoardSMAShip, (invItem.locationID, invItem.itemID)]]
        if checkIfImInStation and checkSameLocation and checkIfIsShip and checkIfActiveShip:
            menuEntries += [[mls.UI_CMD_UNDOCKFROMSTATION, self.ExitStation, (invItem,)]]
        if not util.IsNPC(session.corpid) and checkIfIsMyCorps:
            deliverToMenu = []
            divisions = sm.GetService('corp').GetDivisionNames()
            deliverToCorpHangarMenu = [(divisions[1], self.DeliverToCorpHangarFolder, [[invItem, const.flagHangar]]),
             (divisions[2], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG2]]),
             (divisions[3], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG3]]),
             (divisions[4], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG4]]),
             (divisions[5], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG5]]),
             (divisions[6], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG6]]),
             (divisions[7], self.DeliverToCorpHangarFolder, [[invItem, const.flagCorpSAG7]])]
            deliverToMenu.append([mls.UI_GENERIC_CORPHANGAR, deliverToCorpHangarMenu])
            deliverToMenu.append((mls.UI_GENERIC_MEMBER, self.DeliverToCorpMember, [invItem]))
            if not checkIfNoneLocation and not checkLocationCorpHangarArrayEquivalent and checkIfInHangarOrCorpHangarOrDeliveriesAndCanTake:
                menuEntries += [None]
                menuEntries += [[mls.UI_GENERIC_DELIVER_TO, deliverToMenu]]
        menuEntries += [None]
        if not checkIfActiveShip and not checkPilotLicence:
            if checkIfInHangar and checkIfAtStation and checkIfIsMine:
                menuEntries += [[mls.UI_CMD_TRASHIT, self.TrashInvItems, [invItem]]]
            if checkIfIsMyCorps and checkIfIAmDirector and not checkItemIsInSpace and not checkShipInStructure and not checkInControlTower and checkIfInHangarOrCorpHangarAndCanTake:
                menuEntries += [[mls.UI_CMD_TRASHIT, self.TrashInvItems, [invItem]]]
        if unparsed:
            return menuEntries
        m = []
        if not (filterFunc and mls.UI_CMD_GMEXTRAS in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            m = [(mls.UI_CMD_GMEXTRAS, ('isDynamic', self.GetGMMenu, (invItem.itemID,
                None,
                None,
                invItem,
                None)))]
        return m + self.ParseMenu(menuEntries, filterFunc)



    def CheckItemsInSamePlace(self, invItems):
        if len(invItems) == 0:
            return 
        locationID = invItems[0].locationID
        flag = invItems[0].flagID
        ownerID = invItems[0].ownerID
        for item in invItems:
            if item.locationID != locationID or item.flagID != flag or item.ownerID != ownerID:
                raise UserError('ItemsMustBeInSameHangar')
            locationID = item.locationID
            ownerID = item.ownerID
            flag = item.flagID
            locationID = item.locationID




    def InvalidateItemLocation(self, ownerID, stationID, flag):
        if ownerID == session.corpid:
            which = 'offices'
            if flag == const.flagCorpMarket:
                which = 'deliveries'
            sm.services['objectCaching'].InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, stationID, which)
        else:
            sm.services['objectCaching'].InvalidateCachedMethodCall('stationSvc', 'GetStation', stationID)
            eve.GetInventory(const.containerGlobal).InvalidateStationItemsCache(stationID)



    def DeliverToCorpHangarFolder(self, invItemAndFlagList):
        if len(invItemAndFlagList) == 0:
            return 
        invItems = []
        itemIDs = []
        for item in invItemAndFlagList:
            invItems.append(item[0])
            itemIDs.append(item[0].itemID)

        self.CheckItemsInSamePlace(invItems)
        fromID = invItems[0].locationID
        doSplit = bool(uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItemAndFlagList) == 1 and invItemAndFlagList[0][0].stacksize > 1)
        qty = None
        if doSplit:
            (invItem, flag,) = invItemAndFlagList[0]
            ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
            if ret is not None:
                qty = ret['qty']
        id = sm.StartService('invCache').GetStationIDOfItem(invItems[0])
        stationID = id
        if stationID is None:
            raise UserError('CanOnlyDoInStations')
        ownerID = invItems[0].ownerID
        flag = invItems[0].flagID
        deliverToFlag = invItemAndFlagList[0][1]
        qty = None
        if doSplit:
            invItem = invItems[0]
            ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
            if ret is not None:
                qty = ret['qty']
        eve.inventorymgr.DeliverToCorpHangar(fromID, stationID, itemIDs, qty, ownerID, deliverToFlag)
        self.InvalidateItemLocation(ownerID, stationID, flag)
        if ownerID == session.corpid:
            sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)



    def DeliverToCorpMember(self, invItems):
        if len(invItems) == 0:
            return 
        self.CheckItemsInSamePlace(invItems)
        corpMemberIDs = sm.GetService('corp').GetMemberIDs()
        cfg.eveowners.Prime(corpMemberIDs)
        memberslist = []
        for memberID in corpMemberIDs:
            who = cfg.eveowners.Get(memberID)
            memberslist.append([who.ownerName, memberID, who.typeID])

        doSplit = uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItems) == 1 and invItems[0].stacksize > 1
        stationID = sm.StartService('invCache').GetStationIDOfItem(invItems[0])
        if stationID is None:
            raise UserError('CanOnlyDoInStations')
        ownerID = invItems[0].ownerID
        flag = invItems[0].flagID
        itemIDs = [ item.itemID for item in invItems ]
        res = uix.ListWnd(memberslist, 'character', mls.UI_CORP_SELECTMEMBER, mls.UI_CORP_SELECT_MEMBER_TO_DELIVER_TO, 1)
        if res:
            corporationMemberID = res[1]
            qty = None
            if doSplit:
                invItem = invItems[0]
                ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
                if ret is not None:
                    qty = ret['qty']
            eve.inventorymgr.DeliverToCorpMember(corporationMemberID, stationID, itemIDs, qty, ownerID)
            self.InvalidateItemLocation(ownerID, stationID, flag)
            if ownerID == session.corpid:
                sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)



    def SplitStack(self, invItems):
        if len(invItems) != 1:
            raise UserError('CannotPerformOnMultipleItems')
        invItem = invItems[0]
        ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, mls.UI_GENERIC_DIVIDESTACK)
        if ret is not None:
            qty = ret['qty']
            stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
            if stationID is None:
                raise UserError('CanOnlyDoInStations')
            flag = invItem.flagID
            eve.inventorymgr.SplitStack(stationID, invItem.itemID, qty, invItem.ownerID)
            self.InvalidateItemLocation(invItem.ownerID, stationID, flag)
            if invItem.ownerID == session.corpid:
                invItem.quantity = invItem.quantity - qty
                sm.ScatterEvent('OnCorpAssetChange', [invItem], stationID)



    def GetDroneMenu(self, data):
        return self.DroneMenu(data, unmerged=0)



    def DroneMenu(self, data, unmerged = 0):
        menu = self.GetGroupSpecificDroneMenu(data, unmerged=unmerged)
        menu += self.GetCommonDroneMenu(data, unmerged=unmerged)
        return menu



    def GetGroupSpecificDroneMenu(self, data, unmerged = 0):
        menuEntries = MenuList()
        for (droneID, groupID, ownerID,) in data:
            droneState = sm.StartService('michelle').GetDroneState(droneID)
            if droneState:
                ownerID = droneState.ownerID
                controllerID = droneState.controllerID
                groupID = cfg.invtypes.Get(droneState.typeID).groupID
            else:
                controllerID = None
            groupName = cfg.invgroups.Get(groupID).name
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return []
            checkMiningDrone = groupID == const.groupMiningDrone
            checkFighterDrone = groupID == const.groupFighterDrone
            checkCombatDrone = groupID == const.groupCombatDrone
            checkUnanchoringDrone = groupID == const.groupUnanchoringDrone
            checkOtherDrone = not (checkMiningDrone or checkUnanchoringDrone)
            checkOwner = ownerID == session.charid
            checkController = controllerID == session.shipid
            checkDroneState = droneState is not None
            checkFleet = bool(session.fleetid)
            m = []
            if checkController and checkDroneState:
                if checkOtherDrone:
                    m += [[mls.UI_CMD_ENGAGETARGET, self.EngageTarget, [droneID]]]
                else:
                    reason = self.FindReasonNotAvailable([('thisIsNot',
                      checkOtherDrone,
                      True,
                      {'groupName': groupName})])
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ENGAGETARGET] = reason
                if checkMiningDrone:
                    m += [[mls.UI_CMD_MINE, self.Mine, [droneID]]]
                    m += [[mls.UI_CMD_MINEREPEATEDLY, self.MineRepeatedly, [droneID]]]
                else:
                    reason = self.FindReasonNotAvailable([('thisIsNot',
                      checkMiningDrone,
                      True,
                      {'groupName': groupName})])
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_MINE] = reason
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_MINEREPEATEDLY] = reason
            else:
                prereqs = [('dontControlDrone', checkController, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ENGAGETARGET] = reason
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_MINE] = reason
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_MINEREPEATEDLY] = reason
            if checkOwner and checkController and checkFleet and checkDroneState:
                if checkFighterDrone:
                    m += [[mls.UI_CMD_DELEGATECONTROL, ('isDynamic', self.GetFleetMemberMenu, (self.DelegateControl,)), [droneID]]]
                elif checkCombatDrone:
                    m += [[mls.UI_CMD_ASSIST, ('isDynamic', self.GetFleetMemberMenu, (self.Assist,)), [droneID]]]
                    m += [[mls.UI_CMD_GUARD, ('isDynamic', self.GetFleetMemberMenu, (self.Guard,)), [droneID]]]
            if not checkOwner and checkController and checkFighterDrone and checkDroneState:
                m += [[mls.UI_CMD_RETURNCONTROL, self.ReturnControl, [droneID]]]
            if checkController and checkUnanchoringDrone and checkDroneState:
                m += [[mls.UI_CMD_UNANCHOR, self.DroneUnanchor, [droneID]]]
            else:
                prereqs = [('dontControlDrone', checkController, True), ('thisIsNot',
                  checkUnanchoringDrone,
                  True,
                  {'groupName': groupName}), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_UNANCHOR] = reason
            if unmerged:
                menuEntries.append(m)
            else:
                menuEntries.append(self.ParseMenu(m))
                menuEntries.reasonsWhyNotAvailable = getattr(self, 'reasonsWhyNotAvailable', {})

        if unmerged:
            return menuEntries
        merged = self.MergeMenus(menuEntries)
        return merged



    def GetCommonDroneMenu(self, data, unmerged = 0):
        menuEntries = MenuList()
        for (droneID, groupID, ownerID,) in data:
            droneState = sm.StartService('michelle').GetDroneState(droneID)
            if droneState:
                ownerID = droneState.ownerID
                controllerID = droneState.controllerID
            else:
                controllerID = None
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return []
            droneBall = bp.GetBall(droneID)
            checkOwner = ownerID == session.charid
            checkController = controllerID == session.shipid
            checkDroneState = droneState is not None
            dist = droneBall and max(0, droneBall.surfaceDist)
            checkScoopable = droneState is None or ownerID == session.charid
            checkScoopDist = dist is not None and dist < const.maxCargoContainerTransferDistance
            checkOwnerOrController = checkOwner or checkController
            m = []
            if checkOwnerOrController and checkDroneState:
                m += [[mls.UI_CMD_RETURNANDORBIT, self.ReturnAndOrbit, [droneID]]]
            else:
                prereqs = [('dontControlDrone', checkOwnerOrController, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_RETURNANDORBIT] = reason
            if checkOwner and checkDroneState:
                m += [[mls.UI_CMD_RETURNTODRONEBAY, self.ReturnToDroneBay, [droneID]]]
            else:
                prereqs = [('dontOwnDrone', checkOwner, True), ('droneIncapacitated', checkDroneState, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_RETURNTODRONEBAY] = reason
            if checkScoopable and checkScoopDist:
                m += [[mls.UI_CMD_SCOOPTODRONEBAY, self.ScoopToDroneBay, [droneID]]]
            else:
                prereqs = [('cantScoopDrone', checkScoopable, True), ('droneNotInScooopRange', checkScoopDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_SCOOPTODRONEBAY] = reason
            m += [None]
            if checkOwner and checkDroneState:
                m += [[mls.UI_CMD_ABANDONDRONE, self.AbandonDrone, [droneID]]]
            if unmerged:
                menuEntries.append(m)
            else:
                menuEntries.append(self.ParseMenu(m))

        if unmerged:
            return menuEntries
        merged = self.MergeMenus(menuEntries)
        return merged



    def CharacterMenu(self, charid, charIDs = [], corpid = None, unparsed = 0, filterFunc = None):
        if type(charid) == list:
            menus = []
            for (chid, coid,) in charid:
                menus.append(self._CharacterMenu(chid, coid, unparsed, filterFunc, len(charid) > 1))

            return self.MergeMenus(menus)
        else:
            return self._CharacterMenu(charid, corpid, unparsed, filterFunc)



    def _CharacterMenu(self, charid, corpid, unparsed = 0, filterFunc = None, multi = 0):
        if not charid:
            return []
        addressBookSvc = sm.GetService('addressbook')
        checkIsNPC = util.IsNPC(charid)
        checkIsAgent = sm.GetService('agents').IsAgent(charid)
        checkInStation = bool(session.stationid)
        checkInAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'contact'))
        checkInCorpAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'corpcontact'))
        checkInAllianceAddressbook = bool(addressBookSvc.IsInAddressBook(charid, 'alliancecontact'))
        checkIfBlocked = addressBookSvc.IsBlocked(charid)
        checkIfGuest = session.stationid and sm.StartService('station').IsGuest(charid)
        checkIfMe = charid == session.charid
        checkHaveCloneBay = sm.StartService('clonejump').HasCloneReceivingBay()
        checkBountyOffice = self.CheckBountyOffice()
        checkIfExecCorp = session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid
        checkIAmDiplomat = (const.corpRoleDirector | const.corpRoleDiplomat) & session.corprole != 0
        checkMultiSelection = bool(multi)
        menuEntries = MenuList()
        if not checkMultiSelection and not checkIfMe and not checkIsNPC:
            menuEntries += [[mls.UI_CMD_STARTCONVERSATION, sm.StartService('LSC').Invite, (charid,)]]
        else:
            prereqs = [('checkMultiSelection', checkMultiSelection, False), ('checkIfMe', checkIfMe, False), ('checkIsNPC', checkIsNPC, False)]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_STARTCONVERSATION] = reason
        if not checkMultiSelection and not checkIfMe and checkIsNPC and checkIsAgent:
            menuEntries += [[(mls.UI_CMD_STARTCONVERSATION, menu.ACTIONSGROUP2), sm.StartService('agents').InteractWith, (charid,)]]
        else:
            prereqs = [('checkMultiSelection', checkMultiSelection, False),
             ('checkIfMe', checkIfMe, False),
             ('checkIsNPC', checkIsNPC, True),
             ('checkIsAgent', checkIsAgent, True)]
            reason = self.FindReasonNotAvailable(prereqs)
            if reason:
                menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_STARTCONVERSATION] = reason
        if not checkIfMe:
            if not checkInAddressbook and checkIsNPC and checkIsAgent:
                menuEntries += [[mls.UI_CMD_ADDTOADDRESSBOOK, addressBookSvc.AddToPersonalMulti, [charid]]]
            if not checkIsNPC:
                if not checkMultiSelection:
                    menuEntries += [[mls.UI_CMD_INVITETO, ('isDynamic', self._MenuSvc__GetInviteMenu, (charid,))]]
                menuEntries += [[mls.UI_CMD_SENDMESSAGE, sm.StartService('mailSvc').SendMsgDlg, ([charid], None, None)]]
                if not checkMultiSelection and not checkInAddressbook:
                    menuEntries += [[mls.UI_CONTACTS_ADDTOCONTACTS, addressBookSvc.AddToPersonalMulti, [charid, 'contact']]]
                if not checkMultiSelection and checkInAddressbook:
                    menuEntries += [[mls.UI_CONTACTS_EDITCONTACT, addressBookSvc.AddToPersonalMulti, [charid, 'contact', True]]]
                if not checkMultiSelection and checkInAddressbook:
                    menuEntries += [[mls.UI_CONTACTS_REMOVEFROMCONTACTS, addressBookSvc.DeleteEntryMulti, [[charid], 'contact']]]
            if checkInAddressbook and checkIsNPC and checkIsAgent:
                menuEntries += [[mls.UI_CMD_REMOVEFROMADDRESSBOOK, addressBookSvc.DeleteEntryMulti, [charid]]]
            if not checkMultiSelection and checkIfBlocked:
                menuEntries += [[mls.UI_CMD_UNBLOCK, addressBookSvc.UnblockOwner, ([charid],)]]
            if not checkMultiSelection and not checkIsNPC and not checkIfBlocked:
                menuEntries += [[mls.UI_CMD_BLOCK, addressBookSvc.BlockOwner, (charid,)]]
        if not checkIsNPC and checkIAmDiplomat:
            if not checkInCorpAddressbook:
                menuEntries += [[mls.UI_CONTACTS_ADDCORPCONTACT, addressBookSvc.AddToPersonalMulti, [charid, 'corpcontact']]]
            else:
                menuEntries += [[mls.UI_CONTACTS_EDITCORPCONTACT, addressBookSvc.AddToPersonalMulti, [charid, 'corpcontact', True]]]
                menuEntries += [[mls.UI_CONTACTS_REMOVECORPCONTACT, addressBookSvc.DeleteEntryMulti, [[charid], 'corpcontact']]]
            if checkIfExecCorp:
                if not checkInAllianceAddressbook:
                    menuEntries += [[mls.UI_CONTACTS_ADDALLIANCECONTACT, addressBookSvc.AddToPersonalMulti, [charid, 'alliancecontact']]]
                else:
                    menuEntries += [[mls.UI_CONTACTS_EDITALLIANCECONTACT, addressBookSvc.AddToPersonalMulti, [charid, 'alliancecontact', True]]]
                    menuEntries += [[mls.UI_CONTACTS_REMOVEALLIANCECONTACT, addressBookSvc.DeleteEntryMulti, [[charid], 'alliancecontact']]]
        if not checkMultiSelection and not checkIfMe and not checkIsNPC:
            menuEntries += [[mls.UI_CMD_GIVEMONEY, sm.StartService('wallet').TransferMoney, (session.charid,
               None,
               charid,
               None)]]
            if checkHaveCloneBay:
                menuEntries += [[mls.UI_CMD_OFFERCLONEINSTALLATION, sm.StartService('clonejump').OfferShipCloneInstallation, (charid,)]]
        if not multi:
            agentInfo = sm.StartService('agents').GetAgentByID(charid)
            if agentInfo:
                if agentInfo.solarsystemID and agentInfo.solarsystemID != session.solarsystemid2:
                    menuEntries += [None]
                    menuEntries += self.MapMenu(agentInfo.solarsystemID, unparsed=1)
        if not checkMultiSelection and not checkIfMe and checkInStation and not checkIsNPC and checkIfGuest:
            menuEntries += [[mls.UI_CMD_TRADE, sm.StartService('pvptrade').StartTradeSession, (charid,)]]
        if not checkIsNPC:
            menuEntries += [[mls.UI_CMD_CAPTUREPORTRAIT, sm.StartService('photo').SavePortraits, [charid]]]
        if not checkMultiSelection and not checkIfMe and checkInStation and not checkIsNPC and checkBountyOffice:
            menuEntries += [[mls.UI_CMD_ADDBOUNTY, uicore.cmd.OpenMissions, (charid,)]]
        if not checkIsNPC:
            if session.fleetid is not None:
                fleetSvc = sm.GetService('fleet')
                members = fleetSvc.GetMembers()
                checkIfImLeader = self.ImFleetLeaderOrCommander()
                member = members.get(charid, None)
                if member is None:
                    if not checkMultiSelection and checkIfImLeader:
                        menuEntries += [[mls.UI_FLEET_INVITETOFLEET, self.FleetInviteMenu(charid)]]
                elif not checkMultiSelection:
                    menuEntries += [[mls.UI_FLEET_FLEET, ('isDynamic', self.FleetMenu, (charid, False))]]
            else:
                menuEntries += [[mls.UI_CMD_FORMFLEETWITH, self.InviteToFleet, [charid]]]
            menuEntries += self.CorpMemberMenu(charid, multi)
        if unparsed:
            return menuEntries
        m = []
        if not (filterFunc and mls.UI_CMD_GMEXTRAS in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD | service.ROLE_LEGIONEER):
            m = [(mls.UI_CMD_GMEXTRAS, ('isDynamic', self.GetGMMenu, (None,
                None,
                charid,
                None,
                None)))]
        return m + self.ParseMenu(menuEntries, filterFunc)



    def CheckBountyOffice(self):
        isBountyOffice = False
        if session.stationid:
            services = sm.GetService('station').GetStationServiceInfo()
            serviceMask = eve.stationItem.serviceMask
            for (serviceID, cmdStr, displayName, iconpath, stationOnly, stationServiceIDs,) in services:
                if serviceID == 'missions':
                    for bit in stationServiceIDs:
                        if bit & serviceMask:
                            isBountyOffice = True
                            break


        return isBountyOffice



    def GetCheckInSpace(self):
        return bool(session.solarsystemid)



    def GetCheckInStation(self):
        return bool(session.stationid)



    def CheckIfLockableBlueprint(self, invItem):
        isLockable = False
        if invItem.categoryID == const.categoryBlueprint:
            if invItem.singleton:
                if invItem.ownerID == session.corpid:
                    if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                        if invItem.flagID in [const.flagHangar,
                         const.flagCorpSAG2,
                         const.flagCorpSAG3,
                         const.flagCorpSAG4,
                         const.flagCorpSAG5,
                         const.flagCorpSAG6,
                         const.flagCorpSAG7]:
                            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
                            if rows and len(rows) and rows[0].officeID == invItem.locationID:
                                if not sm.GetService('corp').IsItemLocked(invItem):
                                    isLockable = True
        return bool(isLockable)



    def CheckIfUnlockableBlueprint(self, invItem):
        isUnlockable = False
        if invItem.categoryID == const.categoryBlueprint:
            if invItem.singleton:
                if invItem.ownerID == session.corpid:
                    if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                        if invItem.flagID in [const.flagHangar,
                         const.flagCorpSAG2,
                         const.flagCorpSAG3,
                         const.flagCorpSAG4,
                         const.flagCorpSAG5,
                         const.flagCorpSAG6,
                         const.flagCorpSAG7]:
                            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
                            if rows and len(rows) and rows[0].officeID == invItem.locationID:
                                if sm.GetService('corp').IsItemLocked(invItem):
                                    isUnlockable = True
        return bool(isUnlockable)



    def CheckIfInHangarOrCorpHangarAndCanTake(self, invItem):
        canTake = False
        corpMember = False
        stationID = None
        bp = sm.StartService('michelle').GetBallpark()
        if invItem.ownerID == session.charid:
            if util.IsStation(invItem.locationID) and invItem.flagID == const.flagHangar:
                canTake = True
        elif session.solarsystemid and bp is not None and invItem.locationID in bp.slimItems and invItem.ownerID == bp.slimItems[invItem.locationID].ownerID:
            corpMember = True
        elif invItem.ownerID == session.corpid and not util.IsNPC(invItem.ownerID):
            stationID = None
            rows = sm.StartService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [invItem.locationID])
            if rows and len(rows):
                for row in rows:
                    if invItem.locationID == row.officeID:
                        stationID = row.stationID
                        break

        if stationID is not None or corpMember:
            flags = [const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7]
            if invItem.flagID in flags:
                roles = 0
                if stationID == session.hqID:
                    roles = session.rolesAtHQ
                elif stationID == session.baseID:
                    roles = session.rolesAtBase
                else:
                    roles = session.rolesAtOther
                if invItem.ownerID == session.corpid or corpMember:
                    rolesByFlag = {const.flagHangar: const.corpRoleHangarCanTake1,
                     const.flagCorpSAG2: const.corpRoleHangarCanTake2,
                     const.flagCorpSAG3: const.corpRoleHangarCanTake3,
                     const.flagCorpSAG4: const.corpRoleHangarCanTake4,
                     const.flagCorpSAG5: const.corpRoleHangarCanTake5,
                     const.flagCorpSAG6: const.corpRoleHangarCanTake6,
                     const.flagCorpSAG7: const.corpRoleHangarCanTake7}
                    roleRequired = rolesByFlag[invItem.flagID]
                    if roleRequired & roles == roleRequired:
                        canTake = True
        return bool(canTake)



    def CheckSameLocation(self, invItem):
        inSameLocation = 0
        if session.stationid:
            if invItem.locationID == session.stationid:
                inSameLocation = 1
            elif util.IsPlayerItem(invItem.locationID):
                inSameLocation = 1
            else:
                office = sm.StartService('corp').GetOffice_NoWireTrip()
                if office is not None:
                    if invItem.locationID == office.itemID:
                        inSameLocation = 1
        if invItem.locationID == session.shipid and invItem.flagID != const.flagShipHangar:
            inSameLocation = 1
        elif session.solarsystemid and invItem.locationID == session.solarsystemid:
            inSameLocation = 1
        return inSameLocation



    def CheckMAInRange(self, useRange):
        if not session.solarsystemid:
            return False
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return False
        godmaSM = self.godma.GetStateManager()
        for slimItem in bp.slimItems.itervalues():
            if slimItem.groupID == const.groupShipMaintenanceArray or slimItem.categoryID == const.categoryShip and godmaSM.GetType(slimItem.typeID).hasShipMaintenanceBay:
                otherBall = bp.GetBall(slimItem.itemID)
                if otherBall:
                    if otherBall.surfaceDist < useRange:
                        return True

        return False



    def ImFleetLeaderOrCommander(self):
        return sm.GetService('fleet').IsBoss() or session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr)



    def ImFleetCommander(self):
        return session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr)



    def CheckImFleetLeaderOrBoss(self):
        return sm.GetService('fleet').IsBoss() or session.fleetrole == const.fleetRoleLeader



    def CheckImFleetLeader(self):
        return session.fleetrole == const.fleetRoleLeader



    def CheckImWingCmdr(self):
        return session.fleetrole == const.fleetRoleWingCmdr



    def CheckImSquadCmdr(self):
        return session.fleetrole == const.fleetRoleSquadCmdr



    def FleetMenu(self, charID, unparsed = True):

        def ParsedMaybe(menuEntries):
            if unparsed:
                return menuEntries
            else:
                return self.ParseMenu(menuEntries, None)


        if session.fleetid is None:
            return []
        fleetSvc = sm.GetService('fleet')
        vivox = sm.GetService('vivox')
        members = fleetSvc.GetMembers()
        shipItem = util.SlimItemFromCharID(charID)
        bp = sm.StartService('michelle').GetBallpark()
        otherBall = bp and shipItem and bp.GetBall(shipItem.itemID) or None
        me = members[session.charid]
        checkIfImLeader = self.ImFleetLeaderOrCommander()
        checkIfImWingCommanderOrHigher = self.CheckImFleetLeaderOrBoss() or self.CheckImWingCmdr()
        member = members.get(charID)
        char = cfg.eveowners.Get(charID)
        if member is None:
            menuEntries = [[mls.UI_CMD_SHOWINFO, self.ShowInfo, (int(char.Type()),
               charID,
               0,
               None,
               None)]]
            return menuEntries
        isTitan = False
        isJumpDrive = False
        if session.solarsystemid and session.shipid:
            ship = sm.StartService('godma').GetItem(session.shipid)
            if ship.canJump:
                isJumpDrive = True
            if ship.groupID in [const.groupTitan, const.groupBlackOps]:
                isTitan = True
        checkImCreator = bool(me.job & const.fleetJobCreator)
        checkIfMe = charID == session.charid
        checkIfInSpace = self.GetCheckInSpace()
        checkIfActiveBeacon = fleetSvc.HasActiveBeacon(charID)
        checkIsTitan = isTitan
        checkIsJumpDrive = isJumpDrive
        checkBoosterFleet = bool(member.roleBooster == const.fleetBoosterFleet)
        checkBoosterWing = bool(member.roleBooster == const.fleetBoosterWing)
        checkBoosterSquad = bool(member.roleBooster == const.fleetBoosterSquad)
        checkBoosterAny = bool(checkBoosterFleet or checkBoosterWing or checkBoosterSquad)
        checkSubordinate = self.CheckImFleetLeaderOrBoss() or me.role == const.fleetRoleWingCmdr and member.wingID == me.wingID or me.role == const.fleetRoleSquadCmdr and member.squadID == me.squadID
        checkBoss = member.job & const.fleetJobCreator
        checkWingCommander = member.role == const.fleetRoleWingCmdr
        checkFleetCommander = member.role == const.fleetRoleLeader
        checkBoosterSubordinate = checkBoosterAny and (checkImCreator or me.role == const.fleetRoleLeader or (checkBoosterWing or checkBoosterSquad) and me.role == const.fleetRoleWingCmdr or checkBoosterSquad and me.role == const.fleetRoleSquadCmdr)
        checkBoosterSubordinateOrSelf = checkBoosterSubordinate or checkBoosterAny and checkIfMe
        checkIfFavorite = charID in fleetSvc.GetFavorites()
        checkIfIsBubble = shipItem is not None
        checkMultiSelection = False
        dist = sys.maxint
        if otherBall:
            dist = max(0, otherBall.surfaceDist)
        checkWarpDist = dist > const.minWarpDistance
        checkIsVoiceEnabled = sm.StartService('vivox').Enabled()
        checkCanMute = fleetSvc.CanIMuteOrUnmuteCharInMyChannel(charID) > 0
        checkCanUnmute = fleetSvc.CanIMuteOrUnmuteCharInMyChannel(charID) < 0
        checkIfPrivateMuted = charID in vivox.GetMutedParticipants()
        myChannelName = mls.UI_FLEET_FLEET
        if session.fleetrole == const.fleetRoleWingCmdr:
            myChannelName = mls.UI_FLEET_WING
        elif session.fleetrole == const.fleetRoleSquadCmdr:
            myChannelName = mls.UI_FLEET_SQUAD
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        menuEntries = []
        if not checkMultiSelection:
            menuEntries += [[mls.UI_CMD_SHOWINFO, self.ShowInfo, (int(char.Type()),
               charID,
               0,
               None,
               None)]]
        menuEntries += [None]
        if checkSubordinate and not checkIfMe and not checkBoss:
            menuEntries += [[mls.UI_FLEET_KICKMEMBER, self.ConfirmMenu(lambda *x: fleetSvc.KickMember(charID))]]
        if not checkIfMe and checkImCreator:
            menuEntries += [[mls.UI_FLEET_MAKELEADER, fleetSvc.MakeLeader, (charID,)]]
        if not checkIfFavorite and not checkIfMe:
            menuEntries += [[mls.UI_FLEET_ADDTOWATCHLIST, fleetSvc.AddFavorite, (charID,)]]
        if self.CheckImFleetLeaderOrBoss() and not checkBoosterAny and checkSubordinate:
            menuEntries += [[mls.UI_FLEET_SETFLEETBOOSTER, fleetSvc.SetBooster, (charID, const.fleetBoosterFleet)]]
        if checkIfImWingCommanderOrHigher and not checkBoosterAny and not checkFleetCommander and checkSubordinate:
            menuEntries += [[mls.UI_FLEET_SETWINGBOOSTER, fleetSvc.SetBooster, (charID, const.fleetBoosterWing)]]
        if not checkBoosterAny and not checkWingCommander and not checkFleetCommander and checkSubordinate:
            menuEntries += [[mls.UI_FLEET_SETSQUADBOOSTER, fleetSvc.SetBooster, (charID, const.fleetBoosterSquad)]]
        if checkBoosterSubordinateOrSelf:
            menuEntries += [[mls.UI_FLEET_REVOKEBOOSTER, fleetSvc.SetBooster, (charID, const.fleetBoosterNone)]]
        if checkIfImLeader and checkIfMe:
            menuEntries += [['%s: %s' % (mls.UI_FLEET_BROADCAST, mls.UI_FLEET_TRAVELTOME), sm.GetService('fleet').SendBroadcast_TravelTo, (session.solarsystemid2,)]]
        if checkWarpDist and checkIfInSpace and not checkIfMe:
            menuEntries += [[mls.UI_CMD_WARPTOMEMBER, self.WarpToMember, (charID, float(defaultWarpDist))]]
            menuEntries += [[(mls.UI_CMD_WARPTOMEMBERDIST % {'dist': ''}, menu.ACTIONSGROUP), self.WarpToMenu(self.WarpToMember, charID)]]
            if self.CheckImFleetLeader():
                menuEntries += [[mls.UI_CMD_WARPFLEETTOMEMBER, self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[(mls.UI_CMD_WARPFLEETTOMEMBERDIST % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToMember, charID)]]
            if self.CheckImWingCmdr():
                menuEntries += [[mls.UI_FLEET_WARPWINGTOMEMBER, self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[(mls.UI_FLEET_WARPWINGTOMEMBERDIST % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToMember, charID)]]
            if self.CheckImSquadCmdr():
                menuEntries += [[mls.UI_FLEET_WARPSQUADTOMEMBER, self.WarpFleetToMember, (charID, float(defaultWarpDist))]]
                menuEntries += [[(mls.UI_FLEET_WARPSQUADTOMEMBERDIST % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToMember, charID)]]
        if not checkIfIsBubble and checkIfInSpace and not checkIfMe and checkIfActiveBeacon:
            if checkIsJumpDrive:
                menuEntries += [[mls.UI_CMD_JUMPTOMEMBER, self.JumpToMember, (charID,)]]
            if checkIsTitan:
                menuEntries += [[mls.UI_CMD_BRIDGETOMEMBER, self.BridgeToMember, (charID,)]]
        if checkIfFavorite:
            menuEntries += [[mls.UI_FLEET_REMOVEFROMWATCHLIST, fleetSvc.RemoveFavorite, (charID,)]]
        if not checkIfMe and checkCanMute:
            menuEntries += [[mls.UI_CMD_MUTEINMYCHANNEL % {'name': myChannelName}, fleetSvc.AddToVoiceMute, (charID,)]]
        if checkCanUnmute:
            menuEntries += [[mls.UI_CMD_UNMUTEINMYCHANNEL % {'name': myChannelName}, fleetSvc.ExcludeFromVoiceMute, (charID,)]]
        if checkIsVoiceEnabled and not checkIfPrivateMuted and not checkIfMe:
            menuEntries += [[mls.UI_FLEET_MUTEVOICE, vivox.MuteParticipantForMe, (charID, 1)]]
        if checkIsVoiceEnabled and checkIfPrivateMuted and not checkIfMe:
            menuEntries += [[mls.UI_FLEET_UNMUTEVOICE, vivox.MuteParticipantForMe, (charID, 0)]]
        if checkIfMe:
            menuEntries += [[mls.UI_FLEET_LEAVE, self.ConfirmMenu(fleetSvc.LeaveFleet)]]
        menuEntries = ParsedMaybe(menuEntries)
        moveMenu = self.GetFleetMemberMenu2(charID, fleetSvc.MoveMember, True)
        if moveMenu:
            menuEntries.extend([[mls.UI_FLEET_MOVEMEMBER, moveMenu]])
        return menuEntries



    def FleetInviteMenu(self, charID):
        return self.GetFleetMemberMenu2(charID, lambda *args: self.DoInviteToFleet(*args))



    def GetFleetMemberMenu2(self, charID, callback, isMove = False):
        if session.fleetid is None:
            return []
        wings = sm.GetService('fleet').GetWings()
        members = sm.GetService('fleet').GetMembers()
        hasFleetCommander = bool([ 1 for guy in members.itervalues() if guy.role == const.fleetRoleLeader ])
        wingsWithCommanders = set([ guy.wingID for guy in members.itervalues() if guy.role == const.fleetRoleWingCmdr ])
        squadsWithCommanders = set([ guy.squadID for guy in members.itervalues() if guy.role == const.fleetRoleSquadCmdr ])
        squads = {}
        for guy in members.itervalues():
            if guy.squadID not in (None, -1):
                squads.setdefault(guy.squadID, []).append(guy)

        myself = members[session.charid]
        member = members.get(charID, None)
        canMoveSquad = myself.role == const.fleetRoleSquadCmdr
        canMoveWing = myself.role == const.fleetRoleWingCmdr
        canMoveAll = myself.role == const.fleetRoleLeader or myself.job & const.fleetJobCreator
        isFreeMove = False
        if sm.GetService('fleet').GetOptions().isFreeMove and charID == session.charid:
            isFreeMove = True
        wingMenu = []
        if canMoveAll or canMoveWing or canMoveSquad or isFreeMove:
            sortedWings = wings.items()
            sortedWings.sort()
            sortedSquads = []
            for w in wings.itervalues():
                sortedSquads.extend(w.squads.iterkeys())

            sortedSquads.sort()
            if canMoveAll or isFreeMove:
                if not hasFleetCommander and canMoveAll:
                    wingMenu.append([mls.UI_FLEET_FLEETCOMMANDER, callback, (charID,
                      None,
                      None,
                      const.fleetRoleLeader)])
                if member and member.role in [const.fleetRoleMember, const.fleetRoleSquadCmdr] and member.wingID not in wingsWithCommanders and canMoveAll:
                    wingMenu.append([mls.UI_FLEET_WINGCOMMANDER, callback, (charID,
                      member.wingID,
                      None,
                      const.fleetRoleWingCmdr)])
                if member and member.role == const.fleetRoleMember and member.squadID not in squadsWithCommanders:
                    wingMenu.append([mls.UI_FLEET_SQUADCOMMANDER, callback, (charID,
                      member.wingID,
                      member.squadID,
                      const.fleetRoleSquadCmdr)])
                if member and member.role == const.fleetRoleSquadCmdr:
                    wingMenu.append([mls.UI_FLEET_SQUADMEMBER, callback, (charID,
                      member.wingID,
                      member.squadID,
                      const.fleetRoleMember)])
            if not isMove:
                wingMenu.append([mls.UI_FLEET_FREEPOSITION, callback, (charID,
                  None,
                  None,
                  None)])
            for (wi, (wid, w,),) in enumerate(sortedWings):
                if not (canMoveAll or isFreeMove) and wid != myself.wingID:
                    continue
                if (canMoveWing or canMoveAll) and wid not in wingsWithCommanders:
                    subsquads = [[mls.UI_FLEET_WINGCOMMANDER, callback, (charID,
                       wid,
                       None,
                       const.fleetRoleWingCmdr)]]
                else:
                    subsquads = []
                for (sid, s,) in w.squads.iteritems():
                    if canMoveSquad and not canMoveAll and sid != myself.squadID:
                        continue
                    nMembers = len(squads.get(sid, ()))
                    if nMembers >= fleetcommon.MAX_MEMBERS_IN_SQUAD and (not member or member.squadID != sid):
                        continue
                    si = sortedSquads.index(sid) + 1
                    submembers = []
                    if sid not in squadsWithCommanders:
                        submembers.append([mls.UI_FLEET_SQUADCOMMANDER, callback, (charID,
                          wid,
                          sid,
                          const.fleetRoleSquadCmdr)])
                    if member is None or member.squadID != sid or member.role == const.fleetRoleSquadCmdr:
                        submembers.append([mls.UI_FLEET_SQUADMEMBER, callback, (charID,
                          wid,
                          sid,
                          const.fleetRoleMember)])
                    if submembers:
                        name = s.name
                        if name == '':
                            name = '%s %s' % (mls.UI_FLEET_SQUAD, si)
                        subsquads.append(['%s (%s)' % (name, nMembers), submembers])

                if subsquads:
                    name = w.name
                    if name == '':
                        name = '%s %s' % (mls.UI_FLEET_WING, wi + 1)
                    wingMenu.append([name, subsquads])

        return wingMenu



    def DoInviteToFleet(self, charID, wingID, squadID, role):
        sm.GetService('fleet').Invite(charID, wingID, squadID, role)



    def CorpMemberMenu(self, charID, multi = 0):
        checkInSameCorp = charID in sm.StartService('corp').GetMemberIDs()
        checkIAmDirector = const.corpRoleDirector & session.corprole == const.corpRoleDirector
        checkICanKickThem = session.charid == charID or const.corpRoleDirector & session.corprole == const.corpRoleDirector
        checkIAmCEO = sm.StartService('corp').UserIsCEO()
        checkIAmAccountant = const.corpRoleAccountant & session.corprole == const.corpRoleAccountant
        checkIBlockRoles = sm.StartService('corp').UserBlocksRoles()
        checkIsMe = session.charid == charID
        checkIAmPersonnelMgr = const.corpRolePersonnelManager & session.corprole == const.corpRolePersonnelManager
        checkIsNPC = util.IsNPC(charID)
        checkIAmInNPCCorp = util.IsNPC(session.corpid)
        checkMultiSelection = bool(multi)
        quitCorpMenu = [[mls.UI_CMD_REMOVEALLROLES, sm.StartService('corp').RemoveAllRoles, ()], [mls.UI_CMD_CONFIRMQUITCORP, sm.StartService('corp').KickOut, (charID,)]]
        allowRolesMenu = [[mls.UI_CMD_CONFIRMALLOWROLES, sm.StartService('corp').UpdateMember, (session.charid,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           None,
           0)]]
        expelMenu = [[mls.UI_CMD_CONFIRMEXPELMEMBER, sm.StartService('corp').KickOut, (charID,)]]
        resignMenu = [[mls.UI_CMD_CONFIRMREASIGNASCEO, sm.StartService('corp').ResignFromCEO, ()]]
        menuEntries = [None]
        if not checkMultiSelection and checkInSameCorp:
            if not checkIAmDirector:
                menuEntries += [[mls.UI_CMD_VIEWMEMBERDETAILS, self.ShowCorpMemberDetails, (charID,)]]
            else:
                menuEntries += [[mls.UI_CMD_EDITMEMBER, self.ShowCorpMemberDetails, (charID,)]]
            if checkIsMe and checkIBlockRoles:
                menuEntries += [[mls.UI_CMD_ALLOWROLES, allowRolesMenu]]
        if not checkMultiSelection and checkIAmAccountant and not checkIsNPC:
            menuEntries += [[mls.UI_CMD_TRANSFERCORPCASH, sm.StartService('wallet').TransferMoney, (session.corpid,
               None,
               charID,
               None)]]
        if checkInSameCorp:
            if checkICanKickThem and checkIsMe and not checkIAmInNPCCorp and not checkIAmCEO:
                menuEntries += [[mls.UI_CMD_QUITCORP, quitCorpMenu]]
            if checkICanKickThem and not checkIsMe:
                menuEntries += [[mls.UI_CMD_EXPELMEMBER, expelMenu]]
            if checkIsMe and checkIAmCEO:
                menuEntries += [[mls.UI_CMD_REASIGNASCEO, resignMenu]]
            if checkIAmPersonnelMgr and not checkIsNPC:
                menuEntries += [[mls.UI_CMD_AWARDDECORATION, self.AwardDecoration, [charID]]]
        return menuEntries



    def AwardDecoration(self, charIDs):
        if not charIDs:
            return 
        if not type(charIDs) == list:
            charIDs = [charIDs]
        (info, graphics,) = sm.GetService('medals').GetAllCorpMedals(session.corpid)
        options = [ (medal.title, medal.medalID) for medal in info ]
        if len(options) <= 0:
            raise UserError('MedalCreateToAward')
        cfg.eveowners.Prime(charIDs)
        hintLen = 5
        hint = ', '.join([ cfg.eveowners.Get(charID).name for charID in charIDs[:hintLen] ])
        if len(charIDs) > hintLen:
            hint += ', ...'
        ret = uix.ListWnd(options, 'generic', mls.UI_CMD_AWARDDECORATION, isModal=1, ordered=1, scrollHeaders=[mls.UI_GENERIC_NAME], hint=hint)
        if ret:
            medalID = ret[1]
            sm.StartService('medals').GiveMedalToCharacters(medalID, charIDs)



    def ShowCorpMemberDetails(self, charID):
        form.CorpMembers().MemberDetails(charID)



    def __GetInviteMenu(self, charID, submenu = None):

        def Invite(charID, channelID):
            sm.StartService('LSC').Invite(charID, channelID)


        inviteMenu = []
        submenus = {}
        for channel in sm.StartService('LSC').GetChannels():
            if sm.StartService('LSC').IsJoined(channel.channelID) and type(channel.channelID) == types.IntType:
                members = sm.StartService('LSC').GetMembers(channel.channelID)
                if members and charID not in members:
                    t = chat.GetDisplayName(channel.channelID).split('\\')
                    if submenu and len(t) == 2 and submenu == t[0] or not submenu and len(t) != 2:
                        inviteMenu += [[t[-1], Invite, (charID, channel.channelID)]]
                    elif not submenu and len(t) == 2:
                        submenus[t[0]] = 1

        for each in submenus.iterkeys():
            inviteMenu += [[each, ('isDynamic', self._MenuSvc__GetInviteMenu, (charID, each))]]

        inviteMenu.sort()
        inviteMenu = [[mls.UI_CMD_STARTCONVERSATION, Invite, (charID, None)]] + inviteMenu
        return inviteMenu



    def SlashCmd(self, cmd):
        try:
            sm.RemoteSvc('slash').SlashCmd(cmd)
        except RuntimeError:
            sm.GetService('gameui').MessageBox('This only works on items at your current location.', 'Oops!', buttons=uiconst.OK)



    def GetGMTypeMenu(self, typeID, itemID = None, divs = False, unload = False):
        if not session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            return []

        def _wrapMulti(command, what = None, maxValue = 2147483647):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                if not what:
                    what = command.split(' ', 1)[0]
                result = uix.QtyPopup(maxvalue=maxValue, minvalue=1, caption=what, label=mls.UI_GENERIC_QUANTITY, hint='')
                if result:
                    qty = result['qty']
                else:
                    return 
            else:
                qty = 1
            return sm.GetService('slash').SlashCmd(command % qty)


        item = cfg.invtypes.Get(typeID)
        cat = item.categoryID
        if unload:
            if type(itemID) is tuple:
                for row in eve.GetInventoryFromId(itemID[0]).ListHardwareModules():
                    if row.flagID == itemID[1]:
                        itemID = row.itemID
                        break
                else:
                    itemID = None

            else:
                charge = self.godma.GetItem(itemID)
                if charge.categoryID == const.categoryCharge:
                    for row in eve.GetInventoryFromId(charge.locationID).ListHardwareModules():
                        if row.flagID == charge.flagID and row.itemID != itemID:
                            itemID = row.itemID
                            break
                    else:
                        itemID = None

        gm = []
        if divs:
            gm.append(None)
        if session.role & (service.ROLE_WORLDMOD | service.ROLE_SPAWN):
            if not session.stationid:
                if cat == const.categoryShip:
                    gm.append(('WM: /Spawn this type', lambda *x: _wrapMulti('/spawnN %%d 4000 %d' % item.typeID, '/Spawn', 50)))
                    gm.append(('WM: /Unspawn this ship', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unspawn %d' % itemID)))
                if cat == const.categoryEntity:
                    gm.append(('WM: /Entity deploy this type', lambda *x: _wrapMulti('/entity deploy %%d %d' % item.typeID, '/Entity', 100)))
        if item.typeID != const.typeSolarSystem and cat not in [const.categoryStation, const.categoryOwner]:
            if session.role & service.ROLE_WORLDMOD:
                gm.append(('WM: /create this type', lambda *x: _wrapMulti('/create %d %%d' % item.typeID)))
            gm.append(('GM: /load me this type', lambda *x: _wrapMulti('/load me %d %%d' % item.typeID)))
        if cfg.IsFittableCategory(cat):
            gm.append(('GM: /fit me this type', lambda *x: _wrapMulti('/loop %%d /fit me %d' % item.typeID, '/Fit', 8)))
            if unload:
                if itemID:
                    gm.append(('GM: /unload me this item', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % itemID)))
                gm.append(('GM: /unload me this type', lambda *x: sm.RemoteSvc('slash').SlashCmd('/unload me %d' % item.typeID)))
                if itemID and self.godma.GetItem(itemID).damage:
                    gm.append(('GM: Repair this module', lambda *x: sm.RemoteSvc('slash').SlashCmd('/heal %d' % itemID)))
        if itemID:
            gm.append(('GM: Inspect Attributes', self.InspectAttributes, (itemID, typeID)))
        if session.role & service.ROLE_PROGRAMMER:
            gm.append(('PROG: Modify Attributes', ('isDynamic', self.AttributeMenu, (itemID, typeID))))
        if divs:
            gm.append(None)
        return gm



    def InspectAttributes(self, itemID, typeID):
        sm.GetService('window').GetWindow('AttributeInspector', create=1, ignoreCurrent=1, itemID=itemID, typeID=typeID)



    def NPCInfoMenu(self, item):
        lst = []
        action = 'gd/type.py?action=Type&typeID=' + str(item.typeID)
        lst.append((mls.GENERIC_MENU_OVERVIEW, self.GetFromESP, (action,)))
        action = 'gd/type.py?action=TypeDogma&typeID=' + str(item.typeID)
        lst.append(('Dogma Attributes', self.GetFromESP, (action,)))
        action = 'gd/npc.py?action=GetNPCInfo&shipID=' + str(item.itemID) + '&solarSystemID=' + str(session.solarsystemid)
        lst.append(('Info', self.GetFromESP, (action,)))
        return lst



    def AttributeMenu(self, itemID, typeID):
        d = sm.StartService('info').GetAttrDict(typeID)
        statemgr = sm.StartService('godma').GetStateManager()
        a = statemgr.attributesByID
        lst = []
        for (id, baseValue,) in d.iteritems():
            attrName = a[id].attributeName
            try:
                actualValue = statemgr.GetAttribute(itemID, attrName)
            except:
                sys.exc_clear()
                actualValue = baseValue
            lst.append(('%s - %s' % (attrName, actualValue), self.SetDogmaAttribute, (itemID, attrName, actualValue)))

        lst.sort(lambda x, y: cmp(x[0], y[0]))
        return lst



    def SetDogmaAttribute(self, itemID, attrName, actualValue):
        ret = uix.QtyPopup(None, None, actualValue, 'Set Dogma Attribute for <b>%s</b>' % attrName, 'Set Dogma Attribute', digits=5)
        if ret:
            cmd = '/dogma %s %s = %s' % (itemID, attrName, ret['qty'])
            self.SlashCmd(cmd)



    def GagPopup(self, charID, numMinutes):
        reason = 'Gagged for Spamming'
        ret = uix.NamePopup(mls.UI_GENERIC_GAGUSER, mls.UI_GENERIC_ENTERREASON, reason)
        if ret:
            self.SlashCmd('/gag %s "%s" %s' % (charID, ret['name'], numMinutes))



    def ReportISKSpammer(self, charID, channelID):
        if eve.Message('ConfirmReportISKSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        if charID == session.charid:
            raise UserError('ReportISKSpammerCannotReportYourself')
        lscSvc = sm.GetService('LSC')
        c = lscSvc.GetChannelWindow(channelID)
        entries = copy.copy(c.output.GetNodes())
        spamEntries = []
        for e in entries:
            if e.charid == charID:
                (who, txt, charid, time, colorkey,) = e.msg
                spamEntries.append('[%s] %s > %s' % (util.FmtDate(time, 'nl'), who, txt))

        if len(spamEntries) == 0:
            raise UserError('ReportISKSpammerNoEntries')
        spamEntries.reverse()
        spamEntries = spamEntries[:10]
        spammers = getattr(lscSvc, 'spammerList', set())
        if charID in spammers:
            return 
        spammers.add(charID)
        lscSvc.spammerList = spammers
        c.LoadMessages()
        channel = lscSvc.channels.get(channelID, None)
        if channel and channel.info:
            channelID = channel.info.displayName
        sm.RemoteSvc('userSvc').ReportISKSpammer(charID, channelID, spamEntries)



    def BanIskSpammer(self, charID):
        if eve.Message('ConfirmBanIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        self.SlashCmd('/baniskspammer %s' % charID)



    def GagIskSpammer(self, charID):
        if eve.Message('ConfirmGagIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        self.SlashCmd('/gagiskspammer %s' % charID)



    def GetFromESP(self, action):
        addy = sm.services['machoNet'].namedtransports['ip:packet:server'].transport.address.split(':')[0]
        espaddy = {'87.237.38.51': '87.237.38.15:50001',
         '87.237.38.50': '87.237.38.24:50001',
         '87.237.38.60': '87.237.38.61:50001',
         '87.237.32.22': '87.237.32.22:50001',
         '87.237.38.200': '87.237.38.201:50001'}.get(addy, None)
        if not espaddy:
            espaddy = addy + ':50001'
        blue.os.ShellExecute('http://%s/%s' % (espaddy, action))



    def GetGMMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        if not session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            if charID and session.role & service.ROLE_LEGIONEER:
                return [(mls.UI_CMD_GAGISKSPAMMER, self.GagIskSpammer, (charID,))]
            return []
        gm = [(str(itemID or charID), blue.pyos.SetClipboardData, (str(itemID or charID),))]
        if mapItem and not slimItem:
            gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(mapItem.itemID),)))
            gm.append(None)
        elif charID:
            gm.append(('TR me to %s' % cfg.eveowners.Get(charID).name, sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(charID),)))
            gm.append(None)
        elif slimItem:
            gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(itemID),)))
            gm.append(None)
        if invItem:
            gm += [(mls.UI_CMD_COPYIDQTY, self.CopyItemIDAndMaybeQuantityToClipboard, (invItem,))]
            typeText = 'copy typeID (%s)' % invItem.typeID
            gm += [(typeText, blue.pyos.SetClipboardData, (str(invItem.typeID),))]
            if invItem.flagID == const.flagHangar and invItem.locationID == session.stationid and invItem.itemID not in (session.shipid, session.charid):
                gm.append((mls.UI_CMD_TAKEOUTTRASH, self.TakeOutTrash, [[invItem]]))
            gm.append((mls.UI_CMD_EDIT, self.GetAdamEditType, [invItem.typeID]))
        if charID and not util.IsNPC(charID):
            action = 'gm/character.py?action=Character&characterID=' + str(charID)
            gm.append((mls.UI_GENERIC_SHOWINESP, self.GetFromESP, (action,)))
            gm.append(None)
            gm.append((mls.UI_CMD_GAGISKSPAMMER, self.GagIskSpammer, (charID,)))
            gm.append((mls.UI_CMD_BANISKSPAMMER, self.BanIskSpammer, (charID,)))
            action = 'gm/users.py?action=BanUserByCharacterID&characterID=' + str(charID)
            gm.append((mls.UI_GENERIC_BANUSERESP, self.GetFromESP, (action,)))
            gm += [('Gag User', [('30 ' + mls.UI_GENERIC_MINUTES, self.GagPopup, (charID, 30)),
               ('1 ' + mls.UI_GENERIC_HOUR, self.GagPopup, (charID, 60)),
               ('6 ' + mls.UI_GENERIC_HOURS, self.GagPopup, (charID, 360)),
               ('24 ' + mls.UI_GENERIC_HOURS, self.GagPopup, (charID, 1440)),
               None,
               (mls.UI_GENERIC_UNGAG, lambda *x: self.SlashCmd('/ungag %s' % charID))])]
        gm.append(None)
        item = slimItem or invItem
        if item:
            if item.categoryID == const.categoryShip and (item.singleton or not session.stationid):
                import dna
                if item.ownerID in [session.corpid, session.charid] or session.role & service.ROLE_WORLDMOD:
                    try:
                        menu = dna.Ship().ImportFromShip(shipID=item.itemID, ownerID=item.ownerID, deferred=True).GetMenuInline(spiffy=False, fit=item.itemID != session.shipid)
                        gm.append(('Copycat', menu))
                    except RuntimeError:
                        pass
                gm += [('/Online modules', lambda shipID = item.itemID: self.SlashCmd('/online %d' % shipID))]
            gm += self.GetGMTypeMenu(item.typeID, itemID=item.itemID)
            if getattr(slimItem, 'categoryID', None) == const.categoryEntity or getattr(slimItem, 'groupID', None) == const.groupWreck:
                gm.append(('NPC Info', ('isDynamic', self.NPCInfoMenu, (item,))))
            gm.append(None)
        if session.role & service.ROLE_CONTENT:
            if slimItem:
                if getattr(slimItem, 'dunObjectID', None) != None:
                    if not sm.StartService('scenario').IsSelected(itemID):
                        gm.append((mls.UI_CMD_ADDTOSELECTION, sm.StartService('scenario').AddSelected, (itemID,)))
                    else:
                        gm.append((mls.UI_CMD_REMOVEFROMSELECTION, sm.StartService('scenario').RemoveSelected, (itemID,)))
        if slimItem:
            itemID = slimItem.itemID
            graphicID = cfg.invtypes.Get(slimItem.typeID).graphicID
            graphicFile = util.GraphicFile(graphicID)
            if graphicFile is '':
                graphicFile = None
            subMenu = self.GetGMStructureStateMenu(itemID, slimItem, charID, invItem, mapItem)
            if len(subMenu) > 0:
                gm += [('Change State', subMenu)]
            gm += self.GetGMBallsAndBoxesMenu(itemID, slimItem, charID, invItem, mapItem)
            gm.append(None)
            gm.append(('charID: ' + self.GetOwnerLabel(slimItem.charID), blue.pyos.SetClipboardData, (str(slimItem.charID),)))
            gm.append(('ownerID: ' + self.GetOwnerLabel(slimItem.ownerID), blue.pyos.SetClipboardData, (str(slimItem.ownerID),)))
            gm.append(('corpID: ' + self.GetOwnerLabel(slimItem.corpID), blue.pyos.SetClipboardData, (str(slimItem.corpID),)))
            gm.append(('allianceID: ' + self.GetOwnerLabel(slimItem.allianceID), blue.pyos.SetClipboardData, (str(slimItem.allianceID),)))
            gm.append(None)
            gm.append(('typeID: ' + str(slimItem.typeID) + ' (%s)' % cfg.invtypes.Get(slimItem.typeID).name, blue.pyos.SetClipboardData, (str(slimItem.typeID),)))
            gm.append(('groupID: ' + str(slimItem.groupID) + ' (%s)' % cfg.invgroups.Get(slimItem.groupID).name, blue.pyos.SetClipboardData, (str(slimItem.groupID),)))
            gm.append(('categID: ' + str(slimItem.categoryID) + ' (%s)' % cfg.invcategories.Get(slimItem.categoryID).name, blue.pyos.SetClipboardData, (str(slimItem.categoryID),)))
            gm.append(('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)))
            gm.append(('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),)))
            gm.append(None)
            gm.append(('Copy Coordinates', self.CopyCoordinates, (itemID,)))
            gm.append(None)
        gm.append(None)
        dict = {'CHARID': charID,
         'ITEMID': itemID,
         'ID': charID or itemID}
        for i in range(20):
            item = prefs.GetValue('gmmenuslash%d' % i, None)
            if item:
                for (k, v,) in dict.iteritems():
                    if ' %s ' % k in item and v:
                        item = item.replace(k, str(v))
                        break
                else:
                    continue

                gm.append((item, sm.RemoteSvc('slash').SlashCmd, (item,)))

        return gm



    def GetGMStructureStateMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        subMenu = []
        if hasattr(slimItem, 'posState') and slimItem.posState is not None:
            currentState = slimItem.posState
            if currentState not in pos.ONLINE_STABLE_STATES:
                if currentState == pos.STRUCTURE_ANCHORED:
                    subMenu.append(('Online', sm.RemoteSvc('slash').SlashCmd, ('/pos online ' + str(itemID),)))
                    subMenu.append(('Unanchor', sm.RemoteSvc('slash').SlashCmd, ('/pos unanchor ' + str(itemID),)))
                elif currentState == pos.STRUCTURE_UNANCHORED:
                    subMenu.append(('Anchor', sm.RemoteSvc('slash').SlashCmd, ('/pos anchor ' + str(itemID),)))
            elif getattr(slimItem, 'posTimestamp', None) is not None:
                subMenu.append(('Complete State', sm.RemoteSvc('slash').SlashCmd, ('/sov complete ' + str(itemID),)))
            subMenu.append(('Offline', sm.RemoteSvc('slash').SlashCmd, ('/pos offline ' + str(itemID),)))
        if hasattr(slimItem, 'structureState') and slimItem.structureState != None and slimItem.structureState in [pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE]:
            subMenu.append(('Complete State', sm.RemoteSvc('slash').SlashCmd, ('/sov complete ' + str(itemID),)))
        return subMenu



    def GetGMBallsAndBoxesMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):
        spaceMgr = sm.StartService('space')
        partMenu = [('Stop partition box display ', spaceMgr.StopPartitionDisplayTimer, ()),
         None,
         ('Start partition box display limit = 0', spaceMgr.StartPartitionDisplayTimer, (0,)),
         ('Start partition box display limit = 1', spaceMgr.StartPartitionDisplayTimer, (1,)),
         ('Start partition box display limit = 2', spaceMgr.StartPartitionDisplayTimer, (2,)),
         ('Start partition box display limit = 3', spaceMgr.StartPartitionDisplayTimer, (3,)),
         ('Start partition box display limit = 4', spaceMgr.StartPartitionDisplayTimer, (4,)),
         ('Start partition box display limit = 5', spaceMgr.StartPartitionDisplayTimer, (5,)),
         ('Start partition box display limit = 6', spaceMgr.StartPartitionDisplayTimer, (6,)),
         ('Start partition box display limit = 7', spaceMgr.StartPartitionDisplayTimer, (7,)),
         None,
         ('Show single level', self.ChangePartitionLevel, (0,)),
         ('Show selected level and up', self.ChangePartitionLevel, (1,))]
        subMenu = [('Balls & Boxes', [('Show miniballs', self.ShowDestinyBalls, (itemID,)),
           None,
           ('Wireframe Destiny Ball', self.BallsUp, (itemID, True)),
           ('Wireframe Model Ball', self.BallsUp, (itemID, False)),
           ('Wireframe BoundingSphere', self.BallsUp, (itemID, -1)),
           None,
           ('Partition', partMenu)])]
        return subMenu



    def GetOwnerLabel(self, ownerID):
        name = ''
        if ownerID != None:
            try:
                name = ' (' + cfg.eveowners.Get(ownerID).name + ')    '
            except:
                sys.exc_clear()
        return str(ownerID) + name



    def GetAdamEditType(self, typeID):
        uthread.new(self.ClickURL, 'http://adam:50001/gd/type.py?action=EditTypeDogmaForm&typeID=%s' % typeID)



    def ClickURL(self, url, *args):
        blue.os.ShellExecute(url)



    def SolarsystemScanMenu(self, scanResultID):
        warptoLabel = self.DefaultWarpToLabel()
        defaultWarpDist = self.GetDefaultActionDistance('WarpTo')
        ret = [(warptoLabel, self.WarpToScanResult, (scanResultID, defaultWarpDist)), ((mls.UI_CMD_WARPTOWITHIN % {'dist': ''}, menu.ACTIONSGROUP), self.WarpToMenu(self.WarpToScanResult, scanResultID))]
        if self.CheckImFleetLeader():
            ret.extend([(mls.UI_CMD_WARPFLEET, self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), ((mls.UI_CMD_WARPFLEETTOWITHIN % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        elif self.CheckImWingCmdr():
            ret.extend([(mls.UI_CMD_WARPWING, self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), ((mls.UI_CMD_WARPWINGTOWITHIN % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        elif self.CheckImSquadCmdr():
            ret.extend([(mls.UI_CMD_WARPSQUAD, self.WarpFleetToScanResult, (scanResultID, float(defaultWarpDist))), ((mls.UI_CMD_WARPSQUADTOWITHIN % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(self.WarpFleetToScanResult, scanResultID))])
        return ret



    def WarpToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange)



    def WarpFleetToScanResult(self, scanResultID, minRange = None):
        self._WarpXToScanResult(scanResultID, minRange, fleet=True)



    def _WarpXToScanResult(self, scanResultID, minRange = None, fleet = False):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('scan', scanResultID, minRange=minRange, fleet=fleet)
            sm.StartService('space').WarpDestination(scanResultID, None, None)



    def CelestialMenu(self, itemID, mapItem = None, slimItem = None, noTrace = 0, typeID = None, parentID = None, bookmark = None, itemIDs = [], ignoreTypeCheck = 0, ignoreDroneMenu = 0, filterFunc = None, hint = None, ignoreMarketDetails = 1):
        if type(itemID) == list:
            menus = []
            for data in itemID:
                m = self._CelestialMenu(data, ignoreTypeCheck, ignoreDroneMenu, filterFunc, hint, ignoreMarketDetails, len(itemID) > 1)
                menus.append(m)

            return self.MergeMenus(menus)
        else:
            ret = self._CelestialMenu((itemID,
             mapItem,
             slimItem,
             noTrace,
             typeID,
             parentID,
             bookmark), ignoreTypeCheck, ignoreDroneMenu, filterFunc, hint, ignoreMarketDetails)
            return self.MergeMenus([ret])



    def _CelestialMenu(self, data, ignoreTypeCheck = 0, ignoreDroneMenu = 0, filterFunc = None, hint = None, ignoreMarketDetails = 1, multi = 0):
        (itemID, mapItem, slimItem, noTrace, typeID, parentID, bookmark,) = data
        categoryID = None
        bp = sm.StartService('michelle').GetBallpark()
        fleetSvc = sm.GetService('fleet')
        if bp:
            slimItem = slimItem or bp.GetInvItem(itemID)
        if slimItem:
            typeID = slimItem.typeID
            parentID = sm.StartService('map').GetParent(itemID) or session.solarsystemid
            categoryID = slimItem.categoryID
        mapItemID = None
        if bookmark:
            typeID = bookmark.typeID
            parentID = bookmark.locationID
            itemID = itemID or bookmark.locationID
        else:
            mapItem = mapItem or sm.StartService('map').GetItem(itemID)
            if mapItem:
                typeID = mapItem.typeID
                parentID = getattr(mapItem, 'locationID', None) or const.locationUniverse
                if typeID == const.groupSolarSystem:
                    mapItemID = mapItem.itemID
        if typeID is None or categoryID and categoryID == const.categoryCharge:
            return []
        invType = cfg.invtypes.Get(typeID)
        groupID = invType.groupID
        invGroup = cfg.invgroups.Get(groupID)
        groupName = invGroup.name
        categoryID = categoryID or invGroup.categoryID
        godmaSM = self.godma.GetStateManager()
        shipItem = self.godma.GetStateManager().GetItem(session.shipid)
        isMyShip = itemID == session.shipid
        otherBall = bp and bp.GetBall(itemID) or None
        ownBall = bp and bp.GetBall(session.shipid) or None
        dist = otherBall and max(0, otherBall.surfaceDist)
        otherCharID = slimItem and (slimItem.charID or slimItem.ownerID or None)
        if parentID is None and groupID == const.groupStation and itemID:
            tmp = sm.StartService('ui').GetStation(itemID)
            if tmp is not None:
                parentID = tmp.solarSystemID
        if bookmark and bookmark.locationID and bookmark.locationID == session.solarsystemid:
            myLoc = ownBall and trinity.TriVector(ownBall.x, ownBall.y, ownBall.z) or None
            if (bookmark.typeID == const.typeSolarSystem or bookmark.itemID == bookmark.locationID) and bookmark.x is not None:
                location = None
                if hasattr(bookmark, 'locationType') and bookmark.locationType in ('agenthomebase', 'objective'):
                    entryPoint = sm.StartService('agents').GetAgentMoniker(bookmark.agentID).GetEntryPoint()
                    if entryPoint is not None:
                        location = trinity.TriVector(*entryPoint) or None
                if location is None:
                    location = trinity.TriVector(bookmark.x, bookmark.y, bookmark.z) or None
                dist = myLoc and location and (myLoc - location).Length() or 0.0
            else:
                dist = 0.0
                if bookmark.itemID in bp.balls:
                    b = bp.balls[bookmark.itemID]
                    dist = b.surfaceDist
                    location = trinity.TriVector(b.x, b.y, b.z)
        checkMultiCategs1 = categoryID in (const.categoryEntity, const.categoryDrone, const.categoryShip)
        niceRange = dist and util.FmtDist(dist) or mls.UI_MENU_NODISTANCE
        checkIsMine = bool(slimItem) and slimItem.ownerID == session.charid
        checkIsMyCorps = bool(slimItem) and slimItem.ownerID == session.corpid
        checkIsMineOrCorps = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid)
        checkIsMineOrCorpsOrAlliances = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid or session.allianceid and slimItem.allianceID == session.allianceid)
        checkIsMineOrCorpsOrFleets = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid or slimItem.ownerID in sm.GetService('fleet').GetMembers().keys())
        checkIsFree = bool(otherBall) and otherBall.isFree
        checkBP = bool(bp)
        checkMyShip = isMyShip
        checkInCapsule = itemID == session.shipid and groupID == const.groupCapsule
        checkShipBusy = bool(otherBall) and otherBall.isInteractive
        checkInSpace = bool(session.solarsystemid)
        checkInSystem = dist is not None and (bp and itemID in bp.balls or parentID == session.solarsystemid)
        checkIsObserving = sm.GetService('target').IsObserving()
        checkStation = groupID == const.groupStation
        checkPlanetCargoLink = groupID == const.groupPlanetaryCustomsOffices
        checkPlanet = groupID == const.groupPlanet
        checkMoon = groupID == const.groupMoon
        checkThisPlanetOpen = sm.GetService('planetUI').IsOpen() and sm.GetService('planetUI').planetID == itemID
        checkStargate = bool(slimItem) and groupID == const.groupStargate
        checkWarpgate = groupID == const.groupWarpGate
        checkWormhole = groupID == const.groupWormhole
        checkControlTower = groupID == const.groupControlTower
        checkSentry = groupID in (const.groupMobileMissileSentry, const.groupMobileProjectileSentry, const.groupMobileHybridSentry)
        checkLaserSentry = groupID == const.groupMobileLaserSentry
        checkShipMaintainer = groupID == const.groupShipMaintenanceArray
        checkCorpHangarArray = groupID == const.groupCorporateHangarArray
        checkAssemblyArray = groupID == const.groupAssemblyArray
        checkMobileLaboratory = groupID == const.groupMobileLaboratory
        checkSilo = groupID == const.groupSilo
        checkReactor = groupID == const.groupMobileReactor
        checkRefinery = groupID == const.groupRefiningArray
        checkContainer = groupID in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSpawnContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupDeadspaceOverseersBelongings,
         const.groupMissionContainer)
        checkCynoField = typeID == const.typeCynosuralFieldI
        checkConstructionPf = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
        checkShip = categoryID == const.categoryShip
        checkSpacePig = (groupID == const.groupAgentsinSpace or groupID == const.groupDestructibleAgentsInSpace) and bool(sm.StartService('godma').GetType(typeID).agentID)
        checkIfShipMAShip = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).hasShipMaintenanceBay)
        checkIfShipCHShip = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).hasCorporateHangars)
        checkShipConfig = checkIfShipMAShip
        checkSolarSystem = groupID == const.groupSolarSystem
        checkWreck = groupID == const.groupWreck
        checkIfShipFuelBay = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialFuelBayCapacity)
        checkIfShipOreHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialOreHoldCapacity)
        checkIfShipGasHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialGasHoldCapacity)
        checkIfShipMineralHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialMineralHoldCapacity)
        checkIfShipSalvageHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialSalvageHoldCapacity)
        checkIfShipShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialShipHoldCapacity)
        checkIfShipSmallShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialSmallShipHoldCapacity)
        checkIfShipMediumShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialMediumShipHoldCapacity)
        checkIfShipLargeShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialLargeShipHoldCapacity)
        checkIfShipIndustrialShipHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialIndustrialShipHoldCapacity)
        checkIfShipAmmoHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialAmmoHoldCapacity)
        checkIfShipCommandCenterHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialCommandCenterHoldCapacity)
        checkIfShipPlanetaryCommoditiesHold = slimItem and categoryID == const.categoryShip and bool(godmaSM.GetType(typeID).specialPlanetaryCommoditiesHoldCapacity)
        maxTransferDistance = max(getattr(godmaSM.GetType(typeID), 'maxOperationalDistance', 0), const.maxCargoContainerTransferDistance)
        checkWarpDist = dist is not None and dist > const.minWarpDistance
        checkApproachDist = dist is not None and dist < const.minWarpDistance
        checkAlignTo = dist is not None and dist > const.minWarpDistance
        checkJumpDist = dist is not None and dist < const.maxStargateJumpingDistance
        checkWormholeDist = dist is not None and dist < const.maxWormholeEnterDistance
        checkTransferDist = dist is not None and dist < maxTransferDistance
        checkConfigDist = dist is not None and dist < const.maxConfigureDistance
        checkLookatDist = dist is not None and (dist < 100000.0 or checkIsObserving)
        checkTargetingRange = dist is not None and shipItem is not None and shipItem and dist < shipItem.maxTargetRange
        checkSpacePigDist = dist is not None and dist < sm.StartService('godma').GetType(typeID).agentCommRange
        checkDistNone = dist is None
        checkWarpActive = ownBall and ownBall.mode == destiny.DSTBALL_WARP
        checkCanUseGate = slimItem and shipItem is not None and not shipItem.canNotUseStargates
        checkJumpThrough = slimItem and sm.GetService('fleet').CanJumpThrough(slimItem)
        checkWreckViewed = checkWreck and sm.GetService('wreck').IsViewedWreck(itemID)
        checkFleet = bool(session.fleetid)
        checkIfImCommander = self.ImFleetCommander()
        checkEnemySpotted = sm.GetService('fleet').CurrentFleetBroadcastOnItem(itemID, state.gbEnemySpotted)
        checkHasMarketGroup = cfg.invtypes.Get(typeID).marketGroupID is not None and not ignoreMarketDetails
        checkIsPublished = cfg.invtypes.Get(typeID).published
        checkMultiSelection = bool(multi)
        checkIfLandmark = itemID and itemID < 0
        checkIfAgentBookmark = bookmark and getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber')
        checkIfReadonlyBookmark = bookmark and type(getattr(bookmark, 'bookmarkID', 0)) == types.TupleType
        menuEntries = MenuList()
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        m = MenuList()
        if bookmark:
            checkBookmarkWarpTo = dist is not None and (itemID == session.solarsystemid or parentID == session.solarsystemid)
            checkBookmarkDeadspace = bool(getattr(bookmark, 'deadspace', 0))
            if slimItem:
                if not checkMultiSelection:
                    menuEntries += [[mls.UI_CMD_SHOWINFO, self.ShowInfo, (slimItem.typeID,
                       slimItem.itemID,
                       0,
                       None,
                       None)]]
            if checkInSpace and not checkWarpActive:
                if checkInSystem and checkApproachDist:
                    menuEntries += [[(mls.UI_CMD_APPROACHLOCATION, menu.ACTIONSGROUP), self.ApproachLocation, (bookmark,)]]
                if checkBookmarkWarpTo and checkWarpDist:
                    if not checkBookmarkDeadspace:
                        menuEntries += [[(mls.UI_CMD_WARPTOLOCATIONWITHIN % {'dist': util.FmtDist(float(defaultWarpDist))}, menu.ACTIONSGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist))]]
                        menuEntries += [[(mls.UI_CMD_WARPTOLOCATION, menu.ACTIONSGROUP), self.WarpToMenu(self.WarpToBookmark, bookmark)]]
                        if checkFleet:
                            if self.CheckImFleetLeader():
                                menuEntries += [[(mls.UI_CMD_WARPFLEETTOLOCATIONWITHIN % {'dist': util.FmtDist(float(defaultWarpDist))}, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                            if self.CheckImWingCmdr():
                                menuEntries += [[(mls.UI_CMD_WARPWINGTOLOCATIONWITHIN % {'dist': util.FmtDist(float(defaultWarpDist))}, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                            if self.CheckImSquadCmdr():
                                menuEntries += [[(mls.UI_CMD_WARPSQUADTOLOCATIONWITHIN % {'dist': util.FmtDist(float(defaultWarpDist))}, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                    if checkBookmarkDeadspace:
                        menuEntries += [[(mls.UI_CMD_WARPTOLOCATION, menu.ACTIONSGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist))]]
                        if checkFleet:
                            if self.CheckImFleetLeader():
                                menuEntries += [[(mls.UI_CMD_WARPFLEETTOLOCATION, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                            if self.CheckImWingCmdr():
                                menuEntries += [[(mls.UI_CMD_WARPWINGTOLOCATION, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
                            if self.CheckImSquadCmdr():
                                menuEntries += [[(mls.UI_CMD_WARPSQUADTOLOCATION, menu.FLEETGROUP), self.WarpToBookmark, (bookmark, float(defaultWarpDist), True)]]
            if checkInSystem and not checkMyShip and checkAlignTo and not checkWarpActive and not checkIfAgentBookmark:
                menuEntries += [[(mls.UI_CMD_ALIGNTO, menu.ACTIONSGROUP), self.AlignToBookmark, (getattr(bookmark, 'bookmarkID', None),)]]
            if not checkIfAgentBookmark and not checkIfReadonlyBookmark:
                menuEntries += [[(mls.UI_CMD_REMOVELOCATION, menu.CHANGESGROUP), sm.GetService('addressbook').DeleteBookmarks, ([getattr(bookmark, 'bookmarkID', None)],)]]
            if ignoreTypeCheck or checkStation is True:
                menuEntries += [None]
                if checkBP and checkInSystem and checkStation and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_DOCK, self.Dock, (itemID,)]]
                else:
                    prereqs = [('checkBP', checkBP, True),
                     ('notInSystem', checkInSystem, True),
                     ('notStation', checkStation, True),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_DOCK] = reason
        elif bp and itemID is not None:
            checkBillboard = groupID == const.groupBillboard
            checkStructure = categoryID in (const.categoryStructure, const.categorySovereigntyStructure)
            checkSovStructure = categoryID == const.categorySovereigntyStructure
            checkControlTower = groupID == const.groupControlTower
            checkContainer = groupID in (const.groupWreck,
             const.groupCargoContainer,
             const.groupSpawnContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupFreightContainer,
             const.groupDeadspaceOverseersBelongings,
             const.groupMissionContainer)
            checkMyWreck = groupID == const.groupWreck and slimItem is not None and (slimItem.ownerID == session.charid or fleetSvc.IsMember(slimItem.ownerID) or bp.HaveLootRight(slimItem.itemID))
            checkMyCargo = groupID == const.groupCargoContainer and slimItem is not None and (slimItem.ownerID == session.charid or fleetSvc.IsMember(slimItem.ownerID) or bp.HaveLootRight(slimItem.itemID))
            checkNotAbandoned = hasattr(slimItem, 'lootRights') and (getattr(slimItem, 'lootRights', None) is None or None not in getattr(slimItem, 'lootRights', []))
            checkCorpHangarArray = groupID == const.groupCorporateHangarArray
            checkAssemblyArray = groupID == const.groupAssemblyArray
            checkMobileLaboratory = groupID == const.groupMobileLaboratory
            checkRefinery = groupID == const.groupRefiningArray
            checkSilo = groupID == const.groupSilo
            checkConstructionPf = groupID in (const.groupConstructionPlatform, const.groupStationUpgradePlatform, const.groupStationImprovementPlatform)
            checkJumpPortalArray = groupID == const.groupJumpPortalArray
            checkPMA = groupID in (const.groupPlanet, const.groupMoon, const.groupAsteroidBelt)
            checkMultiGroups1 = groupID in (const.groupSecureCargoContainer, const.groupAuditLogSecureContainer)
            checkMultiGroups2 = categoryID == const.categoryDrone or groupID == const.groupBiomass
            checkAnchorDrop = godmaSM.TypeHasEffect(typeID, const.effectAnchorDrop)
            checkAnchorLift = godmaSM.TypeHasEffect(typeID, const.effectAnchorLift)
            checkAutoPilot = bool(sm.StartService('autoPilot').GetState())
            checkCanRename = checkIsMine or bool(checkIsMyCorps and session.corprole & const.corpRoleEquipmentConfig and categoryID != const.categorySovereigntyStructure) or session.role & service.ROLE_WORLDMOD
            checkAnchorable = invGroup.anchorable
            checkRenameable = not (groupID == const.groupStation and godmaSM.GetType(typeID).isPlayerOwnable == 1)
            checkInTargets = itemID in sm.StartService('target').GetTargets()
            checkBeingTargeted = sm.StartService('target').BeingTargeted(itemID)
            checkStructureOnline = slimItem is not None and (slimItem.posState in pos.ONLINE_STABLE_STATES or slimItem.posState == pos.STRUCTURE_ONLINING and (slimItem.posTimestamp is None or blue.os.GetTime() - slimItem.posTimestamp > sm.StartService('godma').GetTypeAttribute(typeID, const.attributeOnliningDelay) * const.MSEC))
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            checkScoopable = invGroup.anchorable and otherBall and otherBall.isFree or shipItem is not None and shipItem.groupID not in (const.groupFreighter, const.groupJumpFreighter) and groupID == const.groupCargoContainer and typeID != const.typeCargoContainer and typeID != const.typePlanetaryLaunchContainer or shipItem is not None and shipItem.groupID in (const.groupFreighter, const.groupJumpFreighter) and groupID == const.groupFreightContainer or groupID in (const.groupBiomass, const.groupMine) or categoryID == const.categoryDrone
            checkScoopableSMA = categoryID == const.categoryShip and groupID != const.groupCapsule and not isMyShip and shipItem is not None and shipItem.hasShipMaintenanceBay
            checkKeepRangeGroups = categoryID != const.categoryAsteroid and groupID not in (const.groupHarvestableCloud,
             const.groupMiningDrone,
             const.groupCargoContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupStation,
             const.groupStargate,
             const.groupFreightContainer,
             const.groupWreck)
            checkLookingAtItem = bool(sm.GetService('camera').LookingAt() == itemID)
            checkInterest = bool(util.GetAttrs(camera, 'interest', 'translationCurve', 'id') == itemID)
            advancedCamera = bool(settings.user.ui.Get('advancedCamera', 0))
            checkHasConsumables = checkStructure and godmaSM.GetType(typeID).consumptionType != 0
            checkAuditLogSecureContainer = groupID == const.groupAuditLogSecureContainer
            checkShipJumpDrive = slimItem and shipItem is not None and shipItem.canJump
            checkShipJumpPortalGenerator = slimItem and shipItem is not None and shipItem.groupID in [const.groupTitan, const.groupBlackOps] and len([ each for each in godmaSM.GetItem(session.shipid).modules if each.groupID == const.groupJumpPortalGenerator ]) > 0
            structureShipBridge = sm.services['pwn'].GetActiveBridgeForShip(itemID)
            checkShipHasBridge = structureShipBridge is not None
            if structureShipBridge is not None:
                structureShipBridgeLabel = mls.UI_CMD_JUMPTHROUGHTOSYSTEM % {'system': cfg.evelocations.Get(structureShipBridge[0]).name}
            else:
                structureShipBridgeLabel = 'ERROR'
            keepRangeranges = [50, 200, 500]
            defMenuKeepRangeOptions = [ (util.FmtDist(rnge), self.SetDefaultKeepAtRangeDist, (rnge,)) for rnge in keepRangeranges ]
            keepRangeMenu = [ (util.FmtDist(rnge), self.KeepAtRange, (itemID, rnge)) for rnge in keepRangeranges ]
            keepRangeMenu += [(mls.UI_CMD_CURRENTRANGE % {'range': niceRange}, self.KeepAtRange, (itemID, dist)), None, (mls.UI_CMD_SETDEFAULTRANGE, defMenuKeepRangeOptions)]
            orbitranges = [500,
             1000,
             2500,
             5000,
             7500,
             10000,
             15000,
             20000,
             25000,
             30000]
            defMenuOrbitOptions = [ (util.FmtDist(rnge), self.SetDefaultOrbitDist, (rnge,)) for rnge in orbitranges ]
            orbitMenu = [ (util.FmtDist(rnge), self.Orbit, (itemID, rnge)) for rnge in orbitranges ]
            orbitMenu += [(mls.UI_CMD_CURRENTRANGE % {'range': niceRange}, self.Orbit, (itemID, dist)), None, (mls.UI_CMD_SETDEFAULTRANGE, defMenuOrbitOptions)]
            if checkEnemySpotted:
                (senderID,) = checkEnemySpotted
                menuEntries += [['%s: Enemy Spotted!' % cfg.eveowners.Get(senderID).name, ('isDynamic', self.CharacterMenu, (senderID,))]]
            if ignoreTypeCheck or checkShip is True:
                checkCanStoreVessel = shipItem is not None and slimItem is not None and shipItem.groupID != const.groupCapsule and slimItem.itemID != shipItem.itemID
                checkInSameCorp = bool(slimItem) and slimItem.ownerID in sm.StartService('corp').GetMemberIDs()
                canUseFittingService = checkInSameCorp or checkIsMineOrCorpsOrFleets
                if checkShip and checkMyShip:
                    menuEntries += [[[mls.UI_CMD_STOPMYSHIP, mls.UI_CMD_STOPMYCAPSULE][(groupID == const.groupCapsule)], self.StopMyShip]]
                    menuEntries += [[mls.UI_CMD_OPENMYCARGO, self.OpenCargo, (itemID, 'My')]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        string = [mls.UI_CMD_STOPMYSHIP, mls.UI_CMD_STOPMYCAPSULE][(groupID == const.groupCapsule)]
                        menuEntries.reasonsWhyNotAvailable[string] = reason
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_OPENMYCARGO] = reason
                if checkShip and checkIfShipMAShip:
                    menuEntries += [[mls.UI_CMD_OPENSHIPMAINTENANCEBAY, self.OpenShipMaintenanceBayShip, (itemID, mls.UI_SHIPMAINTENANCEBAY)]]
                if checkShip and checkIfShipCHShip and checkIsMineOrCorpsOrFleets:
                    menuEntries += [[mls.UI_CMD_OPENCORPHANGARS, self.OpenShipCorpHangars, (itemID, 'Corporate Hangars')]]
                if checkShip and checkMyShip and not checkInCapsule:
                    if checkIfShipFuelBay:
                        menuEntries += [[mls.UI_CMD_OPENFUELBAY, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedFuelBay)]]
                    if checkIfShipOreHold:
                        menuEntries += [[mls.UI_CMD_OPENOREHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedOreHold)]]
                    if checkIfShipGasHold:
                        menuEntries += [[mls.UI_CMD_OPENGASHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedGasHold)]]
                    if checkIfShipMineralHold:
                        menuEntries += [[mls.UI_CMD_OPENMINERALHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedMineralHold)]]
                    if checkIfShipSalvageHold:
                        menuEntries += [[mls.UI_CMD_OPENSALVAGEHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedSalvageHold)]]
                    if checkIfShipShipHold:
                        menuEntries += [[mls.UI_CMD_OPENSHIPHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedShipHold)]]
                    if checkIfShipSmallShipHold:
                        menuEntries += [[mls.UI_CMD_OPENSMALLSHIPHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedSmallShipHold)]]
                    if checkIfShipMediumShipHold:
                        menuEntries += [[mls.UI_CMD_OPENMEDIUMSHIPHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedMediumShipHold)]]
                    if checkIfShipLargeShipHold:
                        menuEntries += [[mls.UI_CMD_OPENLARGESHIPHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedLargeShipHold)]]
                    if checkIfShipIndustrialShipHold:
                        menuEntries += [[mls.UI_CMD_OPENINDUSTRIALSHIPHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedIndustrialShipHold)]]
                    if checkIfShipAmmoHold:
                        menuEntries += [[mls.UI_CMD_OPENAMMOHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedAmmoHold)]]
                    if checkIfShipCommandCenterHold:
                        menuEntries += [[mls.UI_CMD_OPENCOMMANDCENTERHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedCommandCenterHold)]]
                    if checkIfShipPlanetaryCommoditiesHold:
                        menuEntries += [[mls.UI_CMD_OPENPLANETARYCOMMODITIESHOLD, self.OpenSpecialCargoBay, (itemID, const.flagSpecializedPlanetaryCommoditiesHold)]]
                if checkConfigDist and checkIfShipMAShip and checkCanStoreVessel and checkIsMineOrCorpsOrFleets:
                    menuEntries += [[mls.UI_CMD_STOREVESSEL, self.StoreVessel, (itemID, session.shipid)]]
                if checkShipConfig and checkShip and checkMyShip and checkIsMineOrCorpsOrFleets:
                    menuEntries += [[mls.UI_CMD_CONFIGURESHIP, self.ShipConfig, (itemID,)]]
                if checkShip and checkMyShip and not checkInCapsule and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_EJECT, self.Eject]]
                else:
                    prereqs = [('checkShip', checkShip, True),
                     ('isNotMyShip', checkMyShip, True),
                     ('inCapsule', checkInCapsule, False),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_EJECT] = reason
                if checkMyShip and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_SELFDESTRUCT, self.SelfDestructShip, (itemID,)]]
                else:
                    prereqs = [('isNotMyShip', checkMyShip, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_SELFDESTRUCT] = reason
                if checkShip and not checkMyShip and not checkWarpActive and not checkShipBusy and not checkDistNone:
                    menuEntries += [[mls.UI_CMD_BOARDSHIP, self.Board, (itemID,)]]
                else:
                    prereqs = [('checkShip', checkShip, True),
                     ('isMyShip', checkMyShip, False),
                     ('inWarp', checkWarpActive, False),
                     ('pilotInShip', checkShipBusy, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_BOARDSHIP] = reason
                if checkShip and checkMyShip:
                    menuEntries += [[mls.UI_CMD_ENTERSTARBASEPASSWORD, self.EnterPOSPassword]]
                if checkShip and checkMyShip and checkAutoPilot:
                    menuEntries += [[mls.UI_CMD_DEACTIVATEAUTOPILOT, self.ToggleAutopilot, (0,)]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True), ('autopilotNotActive', checkAutoPilot, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_DEACTIVATEAUTOPILOT] = reason
                if checkShip and checkMyShip and not checkAutoPilot:
                    menuEntries += [[mls.UI_CMD_ACTIVATEAUTOPILOT, self.ToggleAutopilot, (1,)]]
                else:
                    prereqs = [('checkShip', checkShip, True), ('isNotMyShip', checkMyShip, True), ('autopilotActive', checkAutoPilot, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACTIVATEAUTOPILOT] = reason
                menuEntries += [None]
                if checkMyShip and not checkInCapsule and checkShipJumpDrive:
                    menuEntries += [[mls.UI_CMD_JUMPTO, ('isDynamic', self.GetHybridBeaconJumpMenu, [])]]
                    if checkShipJumpPortalGenerator:
                        menuEntries += [[mls.UI_CMD_BRIDGETO, ('isDynamic', self.GetHybridBridgeMenu, [])]]
                if not checkMyShip and checkShipHasBridge:
                    menuEntries += [[(structureShipBridgeLabel, menu.FLEETGROUP), self.JumpThroughAlliance, (itemID,)]]
                menuEntries += [None]
                if checkShip and checkIfShipMAShip and canUseFittingService:
                    menuEntries += [[mls.UI_CMD_OPENFITTING, uicore.cmd.OpenFitting, ()]]
            if ignoreTypeCheck or checkPMA is False:
                checkDrone = groupID == const.groupMiningDrone
                menuEntries += [None]
                if checkInSystem and not checkMyShip and not checkPMA:
                    if checkApproachDist:
                        menuEntries += [[mls.UI_CMD_APPROACH, self.Approach, (itemID, 50)]]
                    else:
                        reason = self.FindReasonNotAvailable([('notInApporachRange', checkApproachDist, True)])
                        if reason:
                            menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_APPROACH] = reason
                    if not checkWarpDist:
                        menuEntries += [[mls.UI_CMD_ORBIT, orbitMenu]]
                    else:
                        reason = self.FindReasonNotAvailable([('inWarpRange', checkWarpDist, False)])
                        if reason:
                            menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ORBIT] = reason
                    if not checkDrone and checkKeepRangeGroups and not checkWarpDist:
                        menuEntries += [[mls.UI_CMD_KEEPATRANGE, keepRangeMenu]]
                    else:
                        prereqs = [('cantKeepInRange',
                          checkKeepRangeGroups,
                          True,
                          {'groupName': groupName}), ('inWarpRange', checkWarpDist, False)]
                        reason = self.FindReasonNotAvailable(prereqs)
                        if reason:
                            menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_KEEPATRANGE] = reason
                else:
                    prereqs = [('notInSystem', checkInSystem, True), ('isMyShip', checkMyShip, False), ('badGroup',
                      checkPMA,
                      False,
                      {'groupName': groupName})]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_APPROACH] = reason
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ORBIT] = reason
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_KEEPATRANGE] = reason
            warpRange = None
            if checkShip and slimItem and slimItem.charID:
                warpFn = self.WarpToMember
                warpFleetFn = self.WarpFleetToMember
                warpID = slimItem.charID
                warpRange = float(defaultWarpDist)
            else:
                warpFn = self.WarpToItem
                warpFleetFn = self.WarpFleet
                warpID = itemID
            if checkInSystem and not checkWarpActive and not checkMyShip and checkWarpDist:
                menuEntries += [[self.DefaultWarpToLabel(), warpFn, (warpID, warpRange)]]
            else:
                prereqs = [('notInSystem', checkInSystem, True),
                 ('inWarp', checkWarpActive, False),
                 ('isMyShip', checkMyShip, False),
                 ('notInWarpRange', checkWarpDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[self.DefaultWarpToLabel()[0]] = reason
            if checkInSystem and not checkMyShip:
                if checkWarpDist and not checkWarpActive:
                    menuEntries += [[(mls.UI_CMD_WARPTOWITHIN % {'dist': ''}, menu.ACTIONSGROUP), self.WarpToMenu(warpFn, warpID)]]
                    if checkFleet:
                        if self.CheckImFleetLeader():
                            menuEntries += [[mls.UI_CMD_WARPFLEET, warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImFleetLeader():
                            menuEntries += [[(mls.UI_CMD_WARPFLEETTOWITHIN % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(warpFleetFn, warpID)]]
                        if self.CheckImWingCmdr():
                            menuEntries += [[mls.UI_CMD_WARPWING, warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImWingCmdr():
                            menuEntries += [[mls.UI_CMD_WARPWINGTOWITHIN % {'dist': ''}, self.WarpToMenu(warpFleetFn, warpID)]]
                        if self.CheckImSquadCmdr():
                            menuEntries += [[mls.UI_CMD_WARPSQUAD, warpFleetFn, (warpID, float(defaultWarpDist))]]
                        if self.CheckImSquadCmdr():
                            menuEntries += [[(mls.UI_CMD_WARPSQUADTOWITHIN % {'dist': ''}, menu.FLEETGROUP), self.WarpToMenu(warpFleetFn, warpID)]]
                if checkAlignTo and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_ALIGNTO, self.AlignTo, (itemID,)]]
                if checkFleet and checkApproachDist:
                    menuEntries += [[self.BroadcastCaption('TARGET'), sm.GetService('fleet').SendBroadcast_Target, (itemID,)]]
            if checkInSystem and checkFleet:
                if not checkMultiCategs1:
                    menuEntries += [[self.BroadcastCaption('WARPTO'), sm.GetService('fleet').SendBroadcast_WarpTo, (itemID,)]]
                    menuEntries += [[self.BroadcastCaption('ALIGNTO'), sm.GetService('fleet').SendBroadcast_AlignTo, (itemID,)]]
                if checkStargate:
                    menuEntries += [[self.BroadcastCaption('JUMPTO'), sm.GetService('fleet').SendBroadcast_JumpTo, (itemID,)]]
            if ignoreTypeCheck or checkJumpThrough:
                throughSystemID = sm.GetService('fleet').CanJumpThrough(slimItem)
                throughSystemName = cfg.evelocations.Get(throughSystemID).name
                menuEntries += [None]
                if checkInSystem and checkJumpDist and not checkWarpActive:
                    menuEntries += [[(mls.UI_CMD_JUMPTHROUGHTOSYSTEM % {'system': throughSystemName}, menu.FLEETGROUP), self.JumpThroughFleet, (otherCharID, itemID)]]
            if ignoreTypeCheck or checkStation is True:
                menuEntries += [None]
                if checkInSystem and checkStation and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_DOCK, self.Dock, (itemID,)]]
                else:
                    prereqs = [('notInSystem', checkInSystem, True), ('notStation', checkStation, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_DOCK] = reason
            if ignoreTypeCheck or checkStargate is True:
                dests = []
                locs = []
                for each in slimItem.jumps:
                    if each.locationID not in locs:
                        locs.append(each.locationID)
                    if each.toCelestialID not in locs:
                        locs.append(each.toCelestialID)

                if len(locs):
                    cfg.evelocations.Prime(locs)
                for each in slimItem.jumps:
                    solname = cfg.evelocations.Get(each.locationID).name
                    destname = cfg.evelocations.Get(each.toCelestialID).name
                    name = mls.UI_CMD_DESTNAMEINSYSTEMNAME % {'destination': destname,
                     'system': solname}
                    dests.append((name, self.StargateJump, (itemID, each.toCelestialID, each.locationID)))

                if not dests:
                    dests = [('None', None, None)]
                checkSingleJumpDest = len(dests) == 1
                if dests:
                    if checkStargate and checkJumpDist and checkSingleJumpDest and checkCanUseGate:
                        menuEntries += [[mls.UI_CMD_JUMP, dests[0][1], dests[0][2]]]
                    else:
                        prereqs = [('notStargate', checkStargate, True),
                         ('notWithinMaxJumpDist', checkJumpDist, True),
                         ('severalJumpDest', checkSingleJumpDest, True),
                         ('cantUseGate', checkCanUseGate, True)]
                        reason = self.FindReasonNotAvailable(prereqs)
                        if reason:
                            menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_JUMP] = reason
                    if checkStargate and checkJumpDist and not checkSingleJumpDest and checkCanUseGate:
                        menuEntries += [[mls.UI_CMD_JUMPTO, dests]]
                    if dests[0][2]:
                        waypoints = sm.StartService('starmap').GetWaypoints()
                        checkInWaypoints = dests[0][2][2] in waypoints
                        if checkSingleJumpDest and checkStargate and checkCanUseGate and not checkInWaypoints:
                            menuEntries += [[mls.UI_CMD_ADDFIRSTWAYPOINT, sm.StartService('starmap').SetWaypoint, (dests[0][2][2], 0, 1)]]
            if slimItem and (ignoreTypeCheck or checkWarpgate is True):
                checkOneTwo = 1
                if checkWarpgate and checkOneTwo and checkJumpDist and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_ACTIVATEGATE, self.ActivateAccelerationGate, (itemID,)]]
                else:
                    prereqs = [('notWarpGate', checkWarpgate, True),
                     ('severalJumpDest', checkOneTwo, True),
                     ('notWithinMaxJumpDist', checkJumpDist, True),
                     ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACTIVATEGATE] = reason
            if slimItem and (ignoreTypeCheck or checkWormhole is True):
                if checkWormhole and checkWormholeDist and not checkWarpActive:
                    menuEntries += [[mls.UI_CMD_ENTERWORMHOLE, self.EnterWormhole, (itemID,)]]
                else:
                    prereqs = [('notCloseEnoughToWH', checkWormholeDist, True), ('inWarp', checkWarpActive, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ENTERWORMHOLE] = reason
            menuEntries += [None]
            if not checkWarpActive and checkLookatDist:
                if not checkLookingAtItem and not checkPlanet and not checkMoon:
                    menuEntries += [[mls.UI_CMD_LOOKAT, sm.GetService('camera').LookAt, (itemID,)]]
                else:
                    prereqs = [('isLookingAtItem', checkLookingAtItem, False)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_LOOKAT] = reason
                if not checkLookingAtItem and advancedCamera:
                    menuEntries += [[mls.UI_CMD_SETASPARENT, self.SetParent, (itemID,)]]
                if not checkInterest and advancedCamera:
                    menuEntries += [[mls.UI_CMD_SETASINTEREST, self.SetInterest, (itemID,)]]
            else:
                prereqs = [('inWarp', checkWarpActive, False), ('notInLookingRange', checkLookatDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_LOOKAT] = reason
            if checkLookingAtItem:
                menuEntries += [[mls.UI_CMD_RESETCAMERA, sm.GetService('camera').ResetCamera]]
            else:
                reason = self.FindReasonNotAvailable([('notLookingAtItem', checkLookingAtItem, True)])
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_RESETCAMERA] = reason
            if ignoreTypeCheck or checkBillboard is True:
                newsURL = 'http://www.eveonline.com/mb2/news.asp'
                if boot.region == 'optic':
                    newsURL = 'http://eve.gtgame.com.cn/gamenews/index.htm'
                menuEntries += [None]
                if checkBillboard:
                    menuEntries += [[mls.UI_CMD_READNEWS, uicore.cmd.OpenBrowser, (newsURL, 'browser')]]
            if ignoreTypeCheck or checkContainer is True:
                menuEntries += [None]
                if checkTransferDist and checkContainer:
                    menuEntries += [[mls.UI_CMD_OPENCARGO, self.OpenCargo, [itemID]]]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_OPENCARGO] = reason
            if ignoreTypeCheck or checkPlanetCargoLink is True:
                menuEntries += [None]
                if checkPlanetCargoLink and checkTransferDist:
                    menuEntries += [[mls.UI_PI_ACCESSCARGOLINK, self.OpenPlanetCargoLinkInventory, [itemID]]]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_PI_ACCESSCARGOLINK] = reason
                if checkPlanetCargoLink:
                    menuEntries += [[mls.UI_PI_CMD_OPENIMEX, self.OpenPlanetCargoLinkImportWindow, [itemID]]]
            if ignoreTypeCheck or checkMyWreck is True or checkMyCargo is True:
                if checkNotAbandoned:
                    if checkMyWreck:
                        menuEntries += [[mls.UI_CMD_ABANDONWRECK, self.AbandonLoot, [itemID]]]
                        menuEntries += [[mls.UI_CMD_ABANDONALLWRECKS, self.AbandonAllLoot, [itemID]]]
                    if checkMyCargo:
                        menuEntries += [[mls.UI_CMD_ABANDONCARGO, self.AbandonLoot, [itemID]]]
                        menuEntries += [[mls.UI_CMD_ABANDONALLCARGO, self.AbandonAllLoot, [itemID]]]
            if checkScoopable and checkTransferDist:
                menuEntries += [[mls.UI_CMD_SCOOPTOCARGOHOLD, self.Scoop, (itemID, typeID)]]
            if checkScoopableSMA and checkTransferDist:
                menuEntries += [[mls.UI_CMD_SCOOPTOMAINTENANCEBAY, self.ScoopSMA, (itemID,)]]
            if checkConstructionPf is True:
                menuEntries += [None]
                if checkTransferDist:
                    menuEntries += [[mls.UI_CMD_ACCESSRSOURCES, self.OpenConstructionPlatform, (itemID, mls.UI_SHARED_CONSTRUCTIONPLATFORM)]]
                    menuEntries += [[mls.UI_CMD_BUILD, self.BuildConstructionPlatform, (itemID,)]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorps and checkAnchorDrop and checkIsFree:
                menuEntries += [[mls.UI_CMD_ANCHOR, self.AnchorObject, (itemID, 1)]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorps and checkAnchorLift and not checkIsFree:
                menuEntries += [[mls.UI_CMD_UNANCHOR, self.AnchorObject, (itemID, 0)]]
            else:
                prereqs = [('notWithinMaxConfigRange', checkConfigDist, True), ('checkIsMineOrCorps', checkIsMineOrCorps, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_UNANCHOR] = reason
            structureEntries = []
            if checkJumpPortalArray is True:
                structureBridge = sm.services['pwn'].GetActiveBridgeForStructure(itemID)
                checkStructureHasBridge = structureBridge is not None
                if structureBridge is not None:
                    bridgeJumpLabel = mls.UI_CMD_JUMPTHROUGHTOSYSTEM % {'system': cfg.evelocations.Get(structureBridge[1]).name}
                    bridgeUnlinkLabel = mls.UI_CMD_UNBRIDGEFROM % {'location': cfg.evelocations.Get(structureBridge[1]).name}
                else:
                    bridgeJumpLabel = 'ERROR'
                    bridgeUnlinkLabel = 'ERROR'
                checkStructureFullyOnline = sm.services['pwn'].IsStructureFullyOnline(itemID)
                checkStructureFullyAnchored = sm.services['pwn'].IsStructureFullyAnchored(itemID)
                if not checkInCapsule and checkIsMyCorps and checkStructureFullyAnchored and not checkStructureHasBridge:
                    structureEntries += [[mls.UI_CMD_BRIDGETO, self.JumpPortalBridgeMenu, (itemID,)]]
                if not checkInCapsule and checkIsMyCorps and checkStructureHasBridge and checkStructureFullyAnchored:
                    structureEntries += [[bridgeUnlinkLabel, self.UnbridgePortal, (itemID,)]]
                if not checkInCapsule and checkStructureHasBridge and checkStructureFullyOnline and checkJumpDist:
                    structureEntries += [[(bridgeJumpLabel, menu.FLEETGROUP), self.JumpThroughPortal, (itemID,)]]
                if checkAnchorable and checkConfigDist and checkIsMineOrCorpsOrAlliances and not checkIsFree and checkTransferDist:
                    structureEntries += [[mls.UI_CMD_ACCESSRSOURCES, self.OpenStructure, (itemID, mls.UI_SHARED_RESOURCESCONTAINER)]]
            if checkAnchorable and checkConfigDist and checkIsMineOrCorpsOrAlliances and not checkIsFree:
                if checkControlTower:
                    structureEntries += [[mls.UI_CMD_ACCESSFUELSTORAGE, self.OpenStructure, (itemID, mls.UI_SHARED_FUELCONTAINER)]]
                    structureEntries += [[mls.UI_CMD_ACCESSTRONTIUMSTORAGE, self.OpenStrontiumBay, (itemID, mls.UI_SHARED_STRONTIUM)]]
                if checkSentry:
                    structureEntries += [[mls.UI_CMD_ACCESSAMMUNITION, self.OpenStructureCharges, (itemID, mls.UI_SHARED_AMMUNITIONCONTAINER, True)]]
                if checkLaserSentry:
                    structureEntries += [[mls.UI_CMD_ACCESSACTIVECRYSTAL, self.OpenStructureCharges, (itemID, mls.UI_SHARED_ACTIVECRYSTALCONTAINER, False)]]
                    structureEntries += [[mls.UI_CMD_ACCESSCRYSTALSTORAGE, self.OpenStructure, (itemID, mls.UI_SHARED_CRYSTALSTORAGECONTAINER)]]
                if checkHasConsumables:
                    structureEntries += [[mls.UI_CMD_ACCESSRSOURCES, self.OpenStructure, (itemID, mls.UI_SHARED_RESOURCESCONTAINER)]]
                checkCanStoreVessel = shipItem is not None and shipItem.groupID != const.groupCapsule
                if checkCanStoreVessel and checkShipMaintainer:
                    structureEntries += [[mls.UI_CMD_STOREVESSEL, self.StoreVessel, (itemID, session.shipid)]]
                if checkShipMaintainer:
                    structureEntries += [[mls.UI_CMD_OPENFITTING, uicore.cmd.OpenFitting, ()]]
                if checkStructureOnline and checkAssemblyArray:
                    structureEntries += [[mls.UI_CMD_ACCESSSTORAGE, self.OpenCorpHangarArray, (itemID, mls.UI_SHARED_ASSAMBLYARRAYCONTAINER)]]
                if checkStructureOnline and checkMobileLaboratory:
                    structureEntries += [[mls.UI_CMD_ACCESSSTORAGE, self.OpenCorpHangarArray, (itemID, mls.UI_SHARED_INDUSTRIALCORPHANGAR)]]
            if checkAnchorable and not checkIsFree:
                if checkIsMineOrCorps and checkControlTower:
                    structureEntries += [[mls.UI_CMD_MANAGE, self.ManageControlTower, (slimItem,)]]
                    if checkConfigDist:
                        structureEntries += [[mls.UI_CMD_SETPASSWORD, self.EnterForceFieldPassword, (itemID,)]]
                if checkTransferDist and checkIsMineOrCorpsOrAlliances and checkShipMaintainer:
                    structureEntries += [[mls.UI_CMD_ACCESSVESSELS, self.OpenStructure, (itemID, mls.UI_SHARED_SHIPMAINTENANCECONTAINER)]]
                    structureEntries += [None]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True), ('notOwnedByYouOrCorpOrAlliance', checkIsMineOrCorpsOrAlliances, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACCESSVESSELS] = reason
                if checkTransferDist and checkIsMineOrCorpsOrAlliances:
                    if checkStructureOnline and checkCorpHangarArray:
                        structureEntries += [[mls.UI_CMD_ACCESSSTORAGE, self.OpenCorpHangarArray, (itemID, mls.UI_SHARED_CORPHANGARARRAYCONTAINER)]]
                    if checkRenameable and checkAssemblyArray:
                        structureEntries += [[mls.UI_CMD_SETNAME, self.SetName, [slimItem]]]
                    if checkRenameable and checkMobileLaboratory:
                        structureEntries += [[mls.UI_CMD_SETNAME, self.SetName, [slimItem]]]
                    if checkSilo:
                        structureEntries += [[mls.UI_CMD_ACCESSSTORAGE, self.OpenStructure, (itemID, mls.UI_SHARED_SILOCONTAINER)]]
                    if checkReactor:
                        structureEntries += [[mls.UI_CMD_ACCESSSTORAGE, self.OpenStructure, (itemID, mls.UI_SHARED_STRUCTURECONTAINER)]]
                else:
                    prereqs = [('notWithinMaxTransferRange', checkTransferDist, True), ('notOwnedByYouOrCorpOrAlliance', checkIsMineOrCorpsOrAlliances, True)]
                    reason = self.FindReasonNotAvailable(prereqs)
                    if reason:
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACCESSVESSELS] = reason
                        menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACCESSSTORAGE] = reason
            checkRefineryState = otherBall and not otherBall.isFree
            if checkRefinery and checkRefineryState and checkTransferDist:
                structureEntries += [[mls.UI_CMD_ACCESSREFINERY, self.OpenStructureCargo, (itemID, mls.UI_SHARED_PROCESSINGAREACONTAINER)]]
            else:
                prereqs = [('notWithinMaxTransferRange', checkTransferDist, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_ACCESSREFINERY] = reason
            if checkRefinery and checkTransferDist:
                structureEntries += [[mls.UI_CMD_RUNREFININGPROCESS, self.RunRefiningProcess, (itemID,)]]
            if checkStructure is True:
                checkIsSovereigntyClaimMarker = categoryID == const.categorySovereigntyStructure and groupID == const.groupSovereigntyClaimMarkers
                checkIsSovereigntyDisruptor = categoryID == const.categorySovereigntyStructure and groupID == const.groupSovereigntyDisruptionStructures
                checkCanAnchorStructure = bool(slimItem) and self.pwn.CanAnchorStructure(itemID)
                checkCanUnanchorStructure = bool(slimItem) and self.pwn.CanUnanchorStructure(itemID)
                checkCanOnlineStructure = bool(slimItem) and self.pwn.CanOnlineStructure(itemID)
                checkCanOfflineStructure = bool(slimItem) and self.pwn.CanOfflineStructure(itemID)
                checkCanAssumeControlStructure = bool(slimItem) and self.pwn.CanAssumeControlStructure(itemID)
                checkHasControlStructureTarget = bool(slimItem) and self.pwn.GetCurrentTarget(itemID) is not None
                checkHasControl = bool(slimItem) and slimItem.controllerID is not None
                checkHasMyControl = bool(slimItem) and slimItem.controllerID is not None and slimItem.controllerID == session.charid
                checkIsMineOrCorpsOrAlliancesOrOrphaned = bool(slimItem) and (self.pwn.StructureIsOrphan(itemID) or checkIsMineOrCorpsOrAlliances)
                checkIfIAmDirector = session.corprole & const.corpRoleDirector > 0
                checkInfrastructureHub = groupID == const.groupInfrastructureHub
                checkStructureFullyOnline = self.pwn.IsStructureFullyOnline(itemID)
                checkInPlanetMode = sm.GetService('planetUI').IsOpen()
                if checkAnchorable and checkConfigDist and checkStructure:
                    if checkIsMineOrCorpsOrAlliances and checkCanAnchorStructure:
                        structureEntries += [[mls.UI_CMD_ANCHORSTRUCTURE, sm.StartService('posAnchor').StartAnchorPosSelect, (itemID,)]]
                    if checkIsMineOrCorpsOrAlliancesOrOrphaned and checkCanUnanchorStructure:
                        structureEntries += [[mls.UI_CMD_UNANCHORSTRUCTURE, self.AnchorStructure, (itemID, 0)]]
                    if checkIsMineOrCorpsOrAlliances and checkCanOnlineStructure and not checkIsSovereigntyDisruptor:
                        structureEntries += [[mls.UI_CMD_PUTONLINE, self.ToggleObjectOnline, (itemID, 1)]]
                    if checkIsMineOrCorpsOrAlliances and checkCanOfflineStructure:
                        structureEntries += [[mls.UI_CMD_PUTOFFLINE, self.ToggleObjectOnline, (itemID, 0)]]
                    if checkIsSovereigntyDisruptor and checkCanOnlineStructure:
                        structureEntries += [[mls.UI_CMD_PUTONLINE, self.ToggleObjectOnline, (itemID, 1)]]
                if checkAnchorable and checkIsMineOrCorpsOrAlliances and checkCanAssumeControlStructure and checkCanOfflineStructure and checkStructure and not checkSovStructure and not checkInPlanetMode:
                    if checkHasMyControl:
                        structureEntries += [[mls.UI_INFLIGHT_RELINQUISHCONTROL, self.pwn.RelinquishStructureControl, (slimItem,)]]
                    if not checkHasControl:
                        structureEntries += [[mls.UI_INFLIGHT_ASSUMECONTROL, self.pwn.AssumeStructureControl, (slimItem,)]]
                if checkAnchorable and checkIsMineOrCorpsOrAlliances and checkCanAssumeControlStructure and checkStructure and checkHasMyControl and checkHasControlStructureTarget and not checkSovStructure:
                    structureEntries += [[mls.UI_CMD_UNLOCKSTRUCTURETARGET, self.pwn.UnlockStructureTarget, (itemID,)]]
                if checkAnchorable and checkConfigDist and checkIsMyCorps and checkCanOfflineStructure and checkStructure and checkSovStructure and checkIfIAmDirector and checkIsSovereigntyClaimMarker:
                    structureEntries += [[mls.UI_STATION_TRANSFER_OWNERSHIP, self.TransferOwnership, (itemID,)]]
                if checkConfigDist and checkIsMyCorps and checkInfrastructureHub and checkStructure and checkStructureFullyOnline:
                    structureEntries += [[mls.SOVEREIGNTY_OPEN_HUB_MANAGER, sm.GetService('sov').GetInfrastructureHubWnd, (itemID,)]]
            if len(structureEntries):
                menuEntries.append(None)
                menuEntries.extend(structureEntries)
            if checkWreck:
                if checkWreckViewed:
                    menuEntries += [[mls.UI_CMD_MARKWRECKNOTVIEWED, sm.GetService('wreck').MarkViewed, (itemID, False)]]
                else:
                    menuEntries += [[mls.UI_CMD_MARKWRECKVIEWED, sm.GetService('wreck').MarkViewed, (itemID, True)]]
            if slimItem and ignoreTypeCheck or checkMultiGroups2 is False:
                menuEntries += [None]
                if not checkMultiGroups2 and not checkCynoField and checkCanRename and checkRenameable:
                    menuEntries += [[mls.UI_CMD_SETNAME, self.SetName, [slimItem]]]
            tagItemMenu = [(mls.UI_CMD_TAGNUMBER, [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in xrange(10) ])]
            tagItemMenu += [(mls.UI_CMD_TAGLETTER, [ (' ' + str(i), self.TagItem, (itemID, str(i))) for i in 'ABCDEFGHIJXYZ' ])]
            menuEntries += [None]
            if checkInTargets and not checkBeingTargeted:
                menuEntries += [[mls.UI_CMD_UNLOCKTARGET, self.UnlockTarget, (itemID,)]]
            else:
                prereqs = [('notInTargets', checkInTargets, True), ('beingTargeted', checkBeingTargeted, False)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_UNLOCKTARGET] = reason
            if not checkMyShip and not checkInTargets and not checkBeingTargeted and not checkPMA and checkTargetingRange:
                menuEntries += [[mls.UI_CMD_LOCKTARGET, self.LockTarget, (itemID,)]]
            else:
                prereqs = [('isMyShip', checkMyShip, False),
                 ('alreadyTargeted', checkInTargets, False),
                 ('checkBeingTargeted', checkBeingTargeted, False),
                 ('badGroup',
                  checkPMA,
                  False,
                  {'groupName': groupName}),
                 ('notInTargetingRange', checkTargetingRange, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_LOCKTARGET] = reason
            if not checkMyShip and not checkPMA and checkFleet and checkIfImCommander:
                menuEntries += [[mls.UI_CMD_TAGITEM, tagItemMenu]]
            if checkSpacePig and checkSpacePigDist:
                menuEntries += [[mls.UI_CMD_STARTCONVERSATION, sm.StartService('agents').InteractWith, (sm.StartService('godma').GetType(typeID).agentID,)]]
            else:
                prereqs = [('notSpacePig', checkSpacePig, True)]
                reason = self.FindReasonNotAvailable(prereqs)
                if reason:
                    menuEntries.reasonsWhyNotAvailable[mls.UI_CMD_STARTCONVERSATION] = reason
            menuEntries += [None]
            if ignoreTypeCheck or checkMultiGroups1 is True:
                menuEntries += [None]
                if checkMultiGroups1:
                    menuEntries += [[mls.UI_CMD_SETNEWPASSWORD, self.AskNewContainerPassword, (itemID, mls.UI_GENERIC_SETPASSWORDONSECURECONT, const.SCCPasswordTypeGeneral)]]
                if checkAuditLogSecureContainer:
                    menuEntries += [[mls.UI_CMD_SETNEWCONFIGURATIONPASSWORD, self.AskNewContainerPassword, (itemID, mls.UI_GENERIC_SETCONFIGPASSWORDONSECURECONT, const.SCCPasswordTypeConfig)]]
                if checkIsMineOrCorps:
                    if checkAuditLogSecureContainer:
                        menuEntries += [[mls.UI_CMD_VIEWLOG, self.ViewAuditLogForALSC, (itemID,)]]
                    if checkAuditLogSecureContainer:
                        menuEntries += [[mls.UI_CMD_CONFIGURECONTAINER, self.ConfigureALSC, (itemID,)]]
                    if checkAuditLogSecureContainer:
                        menuEntries += [[mls.UI_CMD_RETRIEVEPASSWORD, self.RetrievePasswordALSC, (itemID,)]]
        checkInTactical = sm.StartService('tactical').CheckIfGroupIDActive(groupID)
        mapTypeID = typeID
        mapFunctionID = None
        if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion] and parentID != session.solarsystemid and not (bookmark and bookmark.itemID == bookmark.locationID and bookmark.x and bookmark.y and bookmark.z):
            mapFunctionID = mapItemID or itemID
        elif bookmark:
            mapFunctionID = bookmark.locationID
            parentBookmarkItem = sm.StartService('map').GetItem(mapFunctionID)
            if parentBookmarkItem and parentBookmarkItem.groupID == const.groupSolarSystem:
                mapTypeID = parentBookmarkItem.typeID
        elif parentID:
            parentMapItem = sm.StartService('map').GetItem(parentID)
            if parentMapItem and parentMapItem.groupID == const.groupSolarSystem:
                mapFunctionID = parentID
                mapTypeID = parentMapItem.typeID
        elif groupID == const.groupStation:
            if itemID:
                parentID = sm.StartService('ui').GetStation(itemID).solarSystemID
                if parentID != session.solarsystemid:
                    mapTypeID = const.typeSolarSystem
                    mapFunctionID = parentID
        checkSameSolarSystemID = mapFunctionID and mapFunctionID == session.solarsystemid2
        checkHaveSolarSystemID = mapTypeID == const.typeSolarSystem
        if checkHaveSolarSystemID is True:
            waypoints = sm.StartService('starmap').GetWaypoints()
            checkInWaypoints = mapFunctionID in waypoints
            menuEntries += [None]
            if checkHaveSolarSystemID:
                if not checkSameSolarSystemID:
                    menuEntries += [[mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (mapFunctionID, 1)]]
                if checkInWaypoints:
                    menuEntries += [[mls.UI_CMD_REMOVEWAYPOINT, sm.StartService('starmap').ClearWaypoints, (mapFunctionID,)]]
                else:
                    menuEntries += [[mls.UI_CMD_ADDWAYPOINT, sm.StartService('starmap').SetWaypoint, (mapFunctionID,)]]
                if checkFleet and checkSolarSystem:
                    menuEntries += [None]
                    menuEntries += [[self.BroadcastCaption('TRAVELTO'), sm.GetService('fleet').SendBroadcast_TravelTo, (mapFunctionID,)]]
        elif checkStation and parentID is not None and parentID != session.solarsystemid2:
            menuEntries += [None]
            menuEntries += [[mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (parentID, 1)]]
        if session.solarsystemid and not checkIfLandmark:
            if checkInTactical == True:
                menuEntries += [[(mls.UI_CMD_REMOVEFROMOVERVIEW % {'item': groupName}, menu.CHANGESGROUP), sm.StartService('tactical').ChangeSettings, ('groups', groupID, 0)]]
            elif checkInTactical == False:
                menuEntries += [[(mls.UI_CMD_ADDTOOVERVIEW % {'item': groupName}, menu.NAVIGATIONGROUP2), sm.StartService('tactical').ChangeSettings, ('groups', groupID, 1)]]
        if not bookmark and checkMultiCategs1 is False:
            if groupID == const.groupBeacon:
                beacon = sm.StartService('michelle').GetItem(itemID)
                if beacon and hasattr(beacon, 'dunDescription') and beacon.dunDescription:
                    hint = beacon.dunDescription
            if itemID and parentID:
                menuEntries += [None]
                if not checkMultiCategs1 and not checkIfLandmark:
                    menuEntries += [[mls.UI_CMD_BOOKMARKLOCATION, self.Bookmark, (itemID,
                       typeID,
                       parentID,
                       hint)]]
        if ignoreTypeCheck or mapFunctionID is not None:
            if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion]:
                checkMultiGroups3 = mapFunctionID is not None
                menuEntries += [None]
                if checkMultiGroups3:
                    menuEntries += [[mls.UI_CMD_SHOWONMAP, self.ShowInMap, (mapFunctionID,)]]
                    menuEntries += [[(mls.UI_CMD_SHOWITEMONMAPBROWSER % {'item': groupName}, menu.NAVIGATIONGROUP2), self.ShowInMapBrowser, (mapFunctionID,)]]
                    if mapFunctionID not in sm.StartService('pathfinder').GetAvoidanceItems():
                        menuEntries += [[(mls.UI_CMD_AVOIDITEM % {'item': groupName}, menu.NAVIGATIONGROUP2), sm.StartService('pathfinder').AddAvoidanceItem, (mapFunctionID,)]]
                    else:
                        menuEntries += [[(mls.UI_CMD_STOPAVOIDITEM % {'item': groupName}, menu.NAVIGATIONGROUP2), sm.StartService('pathfinder').RemoveAvoidanceItem, (mapFunctionID,)]]
        if checkPlanet and itemID is not None:
            if checkPlanet and not checkThisPlanetOpen:
                menuEntries += [[mls.UI_PI_VIEW_IN_PLANET_MODE, sm.GetService('planetUI').Open, (itemID,)]]
            if checkPlanet and checkThisPlanetOpen:
                menuEntries += [[mls.UI_PI_EXIT_PLANET_MODE, sm.GetService('planetUI').Close, ()]]
        if not ignoreDroneMenu and slimItem and categoryID == const.categoryDrone:
            newMenuEntries = MenuList([None])
            for me in self.DroneMenu([[itemID, groupID, slimItem.ownerID]], 1):
                newMenuEntries.extend(me)

            newMenuEntries.extend(menuEntries)
            menuEntries = newMenuEntries
        if not (filterFunc and mls.UI_CMD_SHOWINFO in filterFunc):
            if not checkMultiSelection:
                menuEntries += [[mls.UI_CMD_SHOWINFO, self.ShowInfo, (typeID,
                   itemID,
                   0,
                   None,
                   parentID)]]
        m += self.ParseMenu(menuEntries, filterFunc)
        m.reasonsWhyNotAvailable.update(getattr(menuEntries, 'reasonsWhyNotAvailable', None))
        if groupID == const.groupPlanet:
            moons = self.GetPrimedMoons(itemID)
            if moons:
                m.append((mls.UI_CMD_MOONS, ('isDynamic', self.GetMoons, (itemID, moons))))
            if checkBP and checkInSystem:
                cargoLinkIDs = bp.GetCargoLinksForPlanet(itemID)
                if cargoLinkIDs is not None and len(cargoLinkIDs) > 0:
                    cargoLinkID = cargoLinkIDs[0]
                    cargoLinkBall = bp.GetBall(cargoLinkID)
                    if cargoLinkBall:
                        m.append((mls.UI_PI_CMD_CUSTOMSOFFICE, ('isDynamic', self.GetCargoLinkMenu, (cargoLinkID,))))
        if checkShip is True and slimItem:
            m += [None] + [(mls.UI_CMD_PILOT, ('isDynamic', self.CharacterMenu, (slimItem.charID or slimItem.ownerID,
                [],
                slimItem.corpID,
                0,
                [mls.UI_CMD_GMEXTRAS])))]
        if not (filterFunc and mls.UI_CMD_VIEWMARKETDETAILS in filterFunc) and checkHasMarketGroup:
            m += [(mls.UI_CMD_VIEWMARKETDETAILS, self.ShowMarketDetails, (util.KeyVal(typeID=typeID),))]
        if not (filterFunc and mls.UI_CMD_FINDINCONTRACTS in filterFunc) and checkIsPublished and not ignoreMarketDetails:
            m += [(mls.UI_CMD_FINDINCONTRACTS, sm.GetService('contracts').FindRelated, (typeID,
               None,
               None,
               None,
               None,
               None))]
        if not (filterFunc and mls.UI_CMD_GMEXTRAS in filterFunc) and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            m.insert(0, (mls.UI_CMD_GMEXTRAS, ('isDynamic', self.GetGMMenu, (itemID,
               slimItem,
               None,
               None,
               mapItem))))
        return m



    def BroadcastCaption(self, which):
        return '%s: %s' % (mls.UI_FLEET_BROADCAST, getattr(mls, 'UI_FLEET_BROADCAST_%s' % which.upper()))



    def JumpPortalBridgeMenu(self, itemID):
        l = []
        fromSystem = cfg.evelocations.Get(session.solarsystemid)
        for (solarSystemID, structureID,) in sm.RemoteSvc('map').GetLinkableJumpArrays():
            if solarSystemID == session.solarsystemid:
                continue
            toSystem = cfg.evelocations.Get(solarSystemID)
            dist = uix.GetLightYearDistance(fromSystem, toSystem)
            l.append(('%s<t>%.1f ly' % (toSystem.name, dist), (solarSystemID, structureID)))

        pick = uix.ListWnd(l, 'generic', mls.UI_SHARED_PICKDESTINATION, isModal=1, scrollHeaders=[mls.UI_GENERIC_SOLARSYSTEM, mls.UI_GENERIC_DISTANCE])
        if pick:
            (remoteSolarSystemID, remoteItemID,) = pick[1]
            self.BridgePortals(itemID, remoteSolarSystemID, remoteItemID)



    def BridgePortals(self, localItemID, remoteSolarSystemID, remoteItemID):
        posLocation = util.Moniker('posMgr', session.solarsystemid)
        posLocation.InstallJumpBridgeLink(localItemID, remoteSolarSystemID, remoteItemID)



    def UnbridgePortal(self, itemID):
        posLocation = util.Moniker('posMgr', session.solarsystemid)
        posLocation.UninstallJumpBridgeLink(itemID)



    def JumpThroughPortal(self, itemID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        slim = sm.services['michelle'].GetItem(itemID)
        remoteStructureID = slim.remoteStructureID
        if not remoteStructureID:
            return 
        remoteSystemID = slim.remoteSystemID
        self.LogNotice('Jump Through Portal', itemID, remoteStructureID, remoteSystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.JumpThroughCorporationStructure, itemID, remoteStructureID, remoteSystemID)



    def GetFuelConsumptionOfJumpBridgeForMyShip(self, fromSystem, toSystem, toStructureType):
        if not session.shipid:
            return 
        myShip = sm.services['godma'].GetItem(session.shipid)
        if myShip is None:
            return 
        myDist = uix.GetLightYearDistance(fromSystem, toSystem, False)
        if myDist is None:
            return 
        attrDict = sm.GetService('info').GetAttrDict(toStructureType)
        attrs = [const.attributeJumpDriveConsumptionAmount, const.attributeJumpPortalConsumptionMassFactor]
        for each in attrs:
            if attrDict.has_key(each):
                myDist *= attrDict[each]

        shipMass = getattr(myShip, 'mass', None)
        if shipMass:
            myDist *= shipMass
        return (myDist, attrDict.get(const.attributeJumpDriveConsumptionType, None))



    def GetFuelConsumptionForMyShip(self, fromSystem, toSystem, attrDict):
        if not session.shipid:
            return 
        else:
            myDist = uix.GetLightYearDistance(fromSystem, toSystem, False)
            if myDist is None:
                return 
            if len(attrDict) > 0:
                for displayAttribute in attrDict:
                    if displayAttribute.attributeID == const.attributeJumpDriveConsumptionAmount:
                        consumptionAmount = myDist * displayAttribute.value
                    else:
                        comsumptionType = displayAttribute.value

                return (int(consumptionAmount), comsumptionType)
            return (None, None)



    def GetHybridBeaconJumpMenu(self):
        fleetMenu = []
        allianceMenu = []
        if session.fleetid:
            beacons = sm.GetService('fleet').GetActiveBeacons()
            for (charID, beaconArgs,) in beacons.iteritems():
                (solarSystemID, itemID,) = beaconArgs
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    character = cfg.eveowners.Get(charID)
                    charName = '%s (%s)' % (character.name, solarsystem.name)
                    fleetMenu.append((uiutil.UpperCase(character.name), (charID, beaconArgs, charName)))

            fleetMenu = uiutil.SortListOfTuples(fleetMenu)
        if session.allianceid:
            beacons = sm.RemoteSvc('map').GetAllianceBeacons()
            for (solarSystemID, structureID, structureTypeID,) in beacons:
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    invType = cfg.invtypes.Get(structureTypeID)
                    structureName = '%s (%s)' % (solarsystem.name, invType.Group().name)
                    allianceMenu.append((uiutil.UpperCase(solarsystem.name), (solarSystemID, structureID, structureName)))

            allianceMenu = uiutil.SortListOfTuples(allianceMenu)
        fullMenu = []
        if len(fleetMenu) > 0:
            for (charID, beaconArgs, charName,) in fleetMenu:
                fullMenu.append([charName, self.JumpToBeaconFleet, (charID, beaconArgs)])

        if len(allianceMenu) > 0:
            if len(fullMenu) > 0:
                fullMenu.append(None)
            for (solarSystemID, structureID, structureName,) in allianceMenu:
                fullMenu.append([structureName, self.JumpToBeaconAlliance, (solarSystemID, structureID)])

        if len(fullMenu) > 0:
            if len(fullMenu) > 40:
                return ([mls.UI_CMD_OPENCAPITALNAVIGATION, self.OpenCapitalNavigation],)
            else:
                return fullMenu
        else:
            return ([mls.UI_GENERIC_NODESTINATION, self.DoNothing],)



    def OpenCapitalNavigation(self, *args):
        if session.shipid:
            wnd = sm.GetService('window').GetWindow('capitalnav', decoClass=form.CapitalNav, create=1, maximize=1)



    def GetHybridBridgeMenu(self):
        fleetMenu = []
        allianceMenu = []
        menuSize = 20
        if session.fleetid:
            menu = []
            beacons = sm.GetService('fleet').GetActiveBeacons()
            for (charID, beaconArgs,) in beacons.iteritems():
                (solarSystemID, itemID,) = beaconArgs
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    character = cfg.eveowners.Get(charID)
                    charName = '%s (%s)' % (character.name, solarsystem.name)
                    menu.append((uiutil.UpperCase(character.name), (charID, beaconArgs, charName)))

            menu = uiutil.SortListOfTuples(menu)
            fleetMenu = [ (charName, self.BridgeToBeacon, (charID, beaconArgs)) for (charID, beaconArgs, charName,) in menu ]
        if session.allianceid:
            menu = []
            datas = sm.RemoteSvc('map').GetAllianceBeacons()
            for (solarSystemID, structureID, structureTypeID,) in datas:
                if solarSystemID != session.solarsystemid:
                    solarsystem = cfg.evelocations.Get(solarSystemID)
                    invtype = cfg.invtypes.Get(structureTypeID)
                    structureName = '%s (%s)' % (solarsystem.name, invtype.Group().name)
                    menu.append((uiutil.UpperCase(solarsystem.name), (solarSystemID, structureID, structureName)))

            menu = uiutil.SortListOfTuples(menu)
            all = []
            while len(menu) > menuSize:
                all.append(menu[:menuSize])
                menu = menu[menuSize:]

            if menu:
                all.append(menu)
            if not all:
                allianceMenu = all
            if len(all) == 1:
                allianceMenu = self.GetAllianceBeaconSubMenu(all[0], self.BridgeToBeaconAlliance)
            else:
                allianceMenu = [ ('%c ... %c' % (sub[0][2][0], sub[-1][2][0]), ('isDynamic', self.GetAllianceBeaconSubMenu, (sub, self.BridgeToBeaconAlliance))) for sub in all ]
        if len(fleetMenu) > 0 and len(allianceMenu) > 0:
            fleetMenu.append(None)
        fleetMenu.extend(allianceMenu)
        if len(fleetMenu) == 0:
            return ([mls.UI_GENERIC_NODESTINATION, self.DoNothing],)
        else:
            return fleetMenu



    def GetAllianceBeaconSubMenu(self, structureIDs, func):
        return [ [structureName, func, (solarSystemID, structureID)] for (solarSystemID, structureID, structureName,) in structureIDs ]



    def RigSlotMenu(self, itemID):
        menu = []
        if itemID == session.shipid:
            ship = sm.GetService('godma').GetItem(session.shipid)
            for module in ship.modules:
                rigslots = [ getattr(const, 'flagRigSlot%s' % i, None) for i in xrange(8) ]
                if module.flagID in rigslots:
                    menu.append([module.name + ' (Slot %s)' % rigslots.index(module.flagID),
                     [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (module.typeID, module.itemID))],
                     None,
                     ()])

        if not menu:
            return []
        return [(mls.UI_GENERIC_RIGS, menu)]



    def RemoveRig(self, moduleID, shipID):
        if session.stationid:
            eve.GetInventory(const.containerHangar).Add(moduleID, shipID)



    def RigFittingCheck(self, invItem):
        moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
        for mEff in moduleEffects:
            if mEff.effectID == const.effectRigSlot:
                if eve.Message('RigFittingInfo', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return 0

        return 1



    def ConfirmMenu(self, func):
        m = [(mls.UI_GENERIC_CONFIRM, func)]
        return m



    def WarpToMenu(self, func, ID):
        ranges = [const.minWarpEndDistance,
         (const.minWarpEndDistance / 10000 + 1) * 10000,
         (const.minWarpEndDistance / 10000 + 2) * 10000,
         (const.minWarpEndDistance / 10000 + 3) * 10000,
         (const.minWarpEndDistance / 10000 + 5) * 10000,
         (const.minWarpEndDistance / 10000 + 7) * 10000,
         const.maxWarpEndDistance]
        defMenuWarpOptions = [ (util.FmtDist(rnge), self.SetDefaultWarpToDist, (rnge,)) for rnge in ranges ]
        warpDistMenu = [(mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[0])}, func, (ID, float(ranges[0]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[1])}, func, (ID, float(ranges[1]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[2])}, func, (ID, float(ranges[2]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[3])}, func, (ID, float(ranges[3]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[4])}, func, (ID, float(ranges[4]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[5])}, func, (ID, float(ranges[5]))),
         (mls.UI_CMD_WARPTOSUBMENU % {'dist': util.FmtDist(ranges[6])}, func, (ID, float(ranges[6]))),
         None,
         (mls.UI_CMD_SETDEFAULTRANGE, defMenuWarpOptions)]
        return warpDistMenu



    def MergeMenus(self, menus):
        if not menus:
            return []
        typeDict = {}
        allCaptions = []
        allReasons = {}
        for menu in menus:
            i = 0
            if getattr(menu, 'reasonsWhyNotAvailable', {}):
                allReasons.update(menu.reasonsWhyNotAvailable)
            for each in menu:
                if each is None:
                    if len(allCaptions) <= i:
                        allCaptions.append(None)
                    else:
                        while allCaptions[i] != None:
                            i += 1
                            if i == len(allCaptions):
                                allCaptions.append(None)
                                break

                elif each[0] not in allCaptions:
                    allCaptions.insert(i, each[0])
                    typeDict[each[0]] = type(each[1])
                i += 1


        menus = filter(None, [ filter(None, each) for each in menus ])
        for caption in allCaptions:
            if caption is None:
                continue
            for menu in menus:
                ok = 0
                for menuEntry in menu:
                    if menuEntry[0] not in typeDict:
                        continue
                    if menuEntry[0] == caption:
                        if type(menuEntry[1]) == typeDict[caption]:
                            ok = 1
                            break
                else:
                    ok = 1

                if not ok and caption in typeDict:
                    del typeDict[caption]


        for caption in self.bypassCommonFilter:
            if caption not in allCaptions:
                allCaptions.append(caption)

        ret = MenuList()
        ret.reasonsWhyNotAvailable = allReasons
        for caption in allCaptions:
            if caption is None:
                ret.append(None)
                continue
            if caption not in typeDict and caption not in self.bypassCommonFilter:
                continue
            lst = []
            isList = None
            broken = 0
            for menu in menus:
                for entry in menu:
                    if entry[0] == caption:
                        if type(entry[1]) in (str, unicode):
                            if caption in self.bypassCommonFilter:
                                continue
                            ret.append((caption, entry[1]))
                            broken = 1
                            break
                        if type(entry[1]) == tuple and entry[1][0] == 'isDynamic' and len(entry) == 2:
                            ret.append((caption, entry[1]))
                            broken = 1
                            break
                        if isList is None:
                            isList = type(entry[1]) == list
                        if isList != type(entry[1]) == list:
                            broken = 1
                        elif isList:
                            lst.append(entry[1])
                        else:
                            lst.append(entry[1:])
                        break

                if broken:
                    break

            if not broken:
                if isList:
                    ret.append((caption, self.MergeMenus(lst)))
                else:
                    if caption in self.multiFunctions or len(lst) and len(lst[0]) and lst[0][0] in self.multiFunctionFunctions:
                        mergedArgs = []
                        for (_func, args,) in lst:
                            if type(args) == type([]):
                                mergedArgs += args
                            else:
                                log.LogWarn('unsupported format of arguments for MergeMenu, function label: ', caption)

                        if mergedArgs:
                            if type(lst[0][0]) == tuple and lst[0][0][0] == 'isDynamic':
                                ret.append((caption, (lst[0][0][0], lst[0][0][1], lst[0][0][2] + (mergedArgs,))))
                            else:
                                ret.append((caption, self.CheckLocked, (lst[0][0], mergedArgs)))
                    else:
                        ret.append((caption, self.ExecMulti, lst))

        return ret



    def ExecMulti(self, *actions):
        for each in actions:
            uthread.new(self.ExecAction, each)




    def ExecAction(self, action):
        apply(*action)



    def GetMenuFormItemIDTypeID(self, itemID, typeID, bookmark = None, filterFunc = None, invItem = None, ignoreMarketDetails = 1):
        if typeID is None:
            return []
        else:
            if invItem:
                return self.InvItemMenu(invItem, filterFunc=filterFunc)
            typeinfo = cfg.invtypes.Get(typeID)
            groupinfo = typeinfo.Group()
            if typeinfo.groupID in (const.groupCharacter,):
                return self.CharacterMenu(itemID, filterFunc=filterFunc)
            if groupinfo.categoryID in (const.categoryCelestial,
             const.categoryStructure,
             const.categoryStation,
             const.categoryShip,
             const.categoryEntity,
             const.categoryDrone,
             const.categoryAsteroid):
                return self.CelestialMenu(itemID, typeID=typeID, bookmark=bookmark, filterFunc=filterFunc, ignoreMarketDetails=ignoreMarketDetails)
            m = []
            if not (filterFunc and mls.UI_CMD_SHOWINFO in filterFunc):
                m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (typeID,
                   itemID,
                   0,
                   None,
                   None))]
            if typeinfo.groupID == const.groupCorporation and util.IsCorporation(itemID) and not util.IsNPC(itemID):
                m += [(mls.UI_CMD_GIVEMONEY, sm.StartService('wallet').TransferMoney, (session.charid,
                   None,
                   itemID,
                   None))]
            if typeinfo.groupID in [const.groupCorporation, const.groupAlliance, const.groupFaction]:
                addressBookSvc = sm.GetService('addressbook')
                inAddressbook = addressBookSvc.IsInAddressBook(itemID, 'contact')
                isBlocked = addressBookSvc.IsBlocked(itemID)
                isNPC = util.IsNPC(itemID)
                if inAddressbook:
                    m += ((mls.UI_CONTACTS_EDITCONTACT, addressBookSvc.AddToPersonalMulti, [itemID, 'contact', True]),)
                    m += ((mls.UI_CONTACTS_REMOVEFROMCONTACTS, addressBookSvc.DeleteEntryMulti, [[itemID], 'contact']),)
                else:
                    m += ((mls.UI_CONTACTS_ADDTOCONTACTS, addressBookSvc.AddToPersonalMulti, [itemID, 'contact']),)
                if not isNPC:
                    if isBlocked:
                        m += ((mls.UI_CMD_UNBLOCK, addressBookSvc.UnblockOwner, [[itemID]]),)
                    else:
                        m += ((mls.UI_CMD_BLOCK, addressBookSvc.BlockOwner, [itemID]),)
                iAmDiplomat = (const.corpRoleDirector | const.corpRoleDiplomat) & session.corprole != 0
                if iAmDiplomat:
                    inCorpAddressbook = addressBookSvc.IsInAddressBook(itemID, 'corpcontact')
                    if inCorpAddressbook:
                        m += ((mls.UI_CONTACTS_EDITCORPCONTACT, addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact', True]),)
                        m += ((mls.UI_CONTACTS_REMOVECORPCONTACT, addressBookSvc.DeleteEntryMulti, [[itemID], 'corpcontact']),)
                    else:
                        m += ((mls.UI_CONTACTS_ADDCORPCONTACT, addressBookSvc.AddToPersonalMulti, [itemID, 'corpcontact']),)
                    if session.allianceid:
                        execCorp = sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid
                        if execCorp:
                            inAllianceAddressbook = addressBookSvc.IsInAddressBook(itemID, 'alliancecontact')
                            if inAllianceAddressbook:
                                m += ((mls.UI_CONTACTS_EDITALLIANCECONTACT, addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact', True]),)
                                m += ((mls.UI_CONTACTS_REMOVEALLIANCECONTACT, addressBookSvc.DeleteEntryMulti, [[itemID], 'alliancecontact']),)
                            else:
                                m += ((mls.UI_CONTACTS_ADDALLIANCECONTACT, addressBookSvc.AddToPersonalMulti, [itemID, 'alliancecontact']),)
            if not (filterFunc and mls.UI_CMD_VIEWMARKETDETAILS in filterFunc) and not ignoreMarketDetails:
                if session.charid:
                    if cfg.invtypes.Get(typeID).marketGroupID is not None:
                        m += [(mls.UI_CMD_VIEWMARKETDETAILS, self.ShowMarketDetails, (util.KeyVal(typeID=typeID),))]
                    if cfg.invtypes.Get(typeID).published:
                        m += [(mls.UI_CMD_FINDINCONTRACTS, sm.GetService('contracts').FindRelated, (typeID,
                           None,
                           None,
                           None,
                           None,
                           None))]
            return m



    def ParseMenu(self, menuEntries, filterFunc = None):
        m = MenuList()
        for menuProps in menuEntries:
            if menuProps is None:
                m += [None]
                continue
            label = menuProps[0]
            if len(menuProps) == 3:
                (label, func, test,) = menuProps
                if test == None:
                    log.LogTraceback('Someone still using None as args')
            if filterFunc and label in filterFunc:
                continue
            m += [menuProps]

        m.reasonsWhyNotAvailable = getattr(menuEntries, 'reasonsWhyNotAvailable', {})
        return m



    def ChangePartitionLevel(self, level):
        settings.user.ui.Set('partition_box_showall', level)



    def GetPrimedMoons(self, planetID):
        if session.solarsystemid2 not in self.primedMoons:
            self.PrimeMoons()
        return self.primedMoons[session.solarsystemid2].get(planetID, [])



    def PrimeMoons(self):
        if session.solarsystemid2 not in self.primedMoons:
            solarsystemitems = sm.RemoteSvc('config').GetMapObjects(session.solarsystemid2, 0, 0, 0, 1, 0)
            moonsByPlanets = {}
            for item in solarsystemitems:
                if item.groupID != const.groupMoon:
                    continue
                moonsByPlanets.setdefault(item.orbitID, []).append(item)

            self.primedMoons[session.solarsystemid2] = moonsByPlanets



    def GetMoons(self, planetID, moons, *args):
        if len(moons):
            moons = uiutil.SortListOfTuples([ (moon.itemID, moon) for moon in moons ])
            moonmenu = []
            i = 1
            for moon in moons:
                moonmenu.append((mls.UI_CMD_MOONSUBMENU % {'num': i}, ('isDynamic', self.ExpandMoon, (moon.itemID, moon))))
                i += 1

            return moonmenu
        return [(mls.UI_CMD_NOMOONS, self.DoNothing)]



    def GetCargoLinkMenu(self, cargoLinkID, *args):
        return sm.StartService('menu').CelestialMenu(cargoLinkID)



    def TransferToCargo(self, itemKey):
        structure = eve.GetInventoryFromId(itemKey[0])
        structure.RemoveChargeToCargo(itemKey)



    def DoNothing(self, *args):
        pass



    def ExpandMoon(self, itemID, moon):
        return sm.StartService('menu').CelestialMenu(itemID, moon)



    def Activate(self, slimItem):
        if eve.rookieState and eve.rookieState < 22:
            return 
        (itemID, groupID, categoryID,) = (slimItem.itemID, slimItem.groupID, slimItem.categoryID)
        if itemID == session.shipid:
            myship = sm.StartService('godma').GetItem(session.shipid)
            if myship.groupID == const.groupCapsule:
                bp = sm.StartService('michelle').GetRemotePark()
                if bp is not None:
                    bp.Stop()
            else:
                self.OpenCargo(itemID, 'My')
            return 
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            ownBall = bp.GetBall(session.shipid)
            otherBall = bp.GetBall(itemID)
            dist = None
            if ownBall and otherBall:
                dist = bp.GetSurfaceDist(ownBall.id, otherBall.id)
            if dist < const.minWarpDistance:
                if groupID == const.groupStation and dist < const.maxDockingDistance:
                    self.Dock(itemID)
                elif groupID in (const.groupWreck,
                 const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer,
                 const.groupSpawnContainer,
                 const.groupDeadspaceOverseersBelongings) and dist < const.maxCargoContainerTransferDistance:
                    self.OpenCargo(itemID, 'SomeCargo')
                else:
                    self.Approach(itemID, 50)



    def SetDefaultWarpToDist(self, rnge):
        settings.user.ui.Set('defaultWarpToDist', rnge)
        sm.ScatterEvent('OnDistSettingsChange')



    def SetDefaultOrbitDist(self, rnge, *args):
        settings.user.ui.Set('defaultOrbitDist', rnge)
        sm.ScatterEvent('OnDistSettingsChange')



    def SetDefaultKeepAtRangeDist(self, rnge, *args):
        settings.user.ui.Set('defaultKeepAtRangeDist', rnge)
        sm.ScatterEvent('OnDistSettingsChange')



    def FindReasonNotAvailable(self, prereqs):
        for each in prereqs:
            d = None
            if len(each) == 4:
                (label, value, expected, d,) = each
            else:
                (label, value, expected,) = each
            if value == expected:
                continue
            if label not in self.allReasonsDict:
                continue
            reason = self.allReasonsDict[label]
            if d:
                reason = reason % d
            return reason




    def ShowDestinyBalls(self, itemID):
        toRemove = None
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        for each in scene.children:
            if each.name == 'miniballs_of_' + str(itemID):
                toRemove = each
                break

        if toRemove:
            scene.children.remove(toRemove)
            scene = None
            toRemove = None
            return 
        ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
        t = trinity.TriTransform()
        sphere = blue.os.LoadObject('res:/Model/Global/greenSphere.blue')
        del sphere.children[:]
        if len(ball.miniBalls) > 0:
            for miniball in ball.miniBalls:
                mball = sphere.CopyTo()
                mball.translation.SetXYZ(miniball.x, miniball.y, miniball.z)
                mball.scaling.SetXYZ(miniball.radius * 2, miniball.radius * 2, miniball.radius * 2)
                t.children.append(mball)

            t.useCurves = 1
            t.translationCurve = ball
        t.name = 'miniballs_of_' + str(itemID)
        scene.children.append(t)
        scene = None
        t = None
        toRemove = None



    def BallsUp(self, itemID, useDestinyRadius):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
        if useDestinyRadius == -1:
            prefix = 'bs'
        elif useDestinyRadius:
            prefix = 'd'
        else:
            prefix = 'm'
        toRemove = None
        for each in scene.children:
            if each.name == prefix + str(ball.id):
                toRemove = each
                break

        if toRemove:
            scene.children.remove(toRemove)
            return 
        if useDestinyRadius == -1:
            s = trinity.TriTransform()
            b = blue.os.LoadObject('res:/Model/Global/greensphere.blue')
            b.scaling.Scale(ball.model.GetBoundingSphereRadius() * 2.0)
            pos = ball.model.GetBoundingSphereCenter()
            b.translation = trinity.TriVector(pos[0], pos[1], pos[2])
            s.children.append(b)
            s.rotationCurve = ball
        else:
            s = blue.os.LoadObject('res:/model/global/sphere.blue')
            if useDestinyRadius:
                useRadius = ball.radius
            elif hasattr(ball, 'boundingSphereRadius'):
                useRadius = ball.boundingSphereRadius
            else:
                useRadius = ball.radius
            s.scaling.x = useRadius
            s.scaling.y = useRadius
            s.scaling.z = useRadius
            s.scaling.Scale(2.0)
            s.object.areas[0].shader.passes[0].fill = 2
        s.translationCurve = ball
        s.useCurves = 1
        s.name = prefix + str(ball.id)
        scene.children.append(s)
        scene = None
        s = None
        toRemove = None



    def ShowBallPartition(self, itemID):
        ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
        ball.showBoxes = 1



    def AnchorObject(self, itemID, anchorFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            typeID = sm.StartService('michelle').GetItem(itemID).typeID
            anchoringDelay = self.godma.GetType(typeID).anchoringDelay
            if anchorFlag:
                eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})
                dogmaLM.Activate(itemID, const.effectAnchorDrop)
            else:
                eve.Message('UnanchoringObject', {'delay': anchoringDelay / 1000.0})
                dogmaLM.Activate(itemID, const.effectAnchorLift)



    def AnchorStructure(self, itemID, anchorFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            item = sm.StartService('michelle').GetItem(itemID)
            typeID = item.typeID
            if anchorFlag:
                anchoringDelay = self.godma.GetType(typeID).anchoringDelay
                eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})
                ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
                sm.StartService('pwn').Anchor(itemID, (ball.x, ball.y, ball.z))
            else:
                orphaned = self.pwn.StructureIsOrphan(itemID)
                item = sm.StartService('michelle').GetItem(itemID)
                if orphaned:
                    msgName = 'ConfirmOrphanStructureUnanchor'
                elif item.groupID == const.groupInfrastructureHub:
                    msgName = 'ConfirmInfrastructureHubUnanchor'
                else:
                    msgName = 'ConfirmStructureUnanchor'
                if eve.Message(msgName, {'item': (TYPEID, item.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return 
                unanchoringDelay = self.godma.GetType(typeID).unanchoringDelay
                eve.Message('UnanchoringObject', {'delay': unanchoringDelay / 1000.0})
                dogmaLM.Activate(itemID, const.effectAnchorLiftForStructures)



    def ToggleObjectOnline(self, itemID, onlineFlag):
        dogmaLM = self.godma.GetDogmaLM()
        if dogmaLM:
            item = sm.StartService('michelle').GetItem(itemID)
            if onlineFlag:
                if item.groupID in (const.groupSovereigntyClaimMarkers,):
                    if eve.Message('ConfirmSovStructureOnline', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                        return 
                dogmaLM.Activate(itemID, const.effectOnlineForStructures)
            elif item.groupID == const.groupControlTower:
                msgName = 'ConfirmTowerOffline'
            elif item.groupID == const.groupSovereigntyClaimMarkers:
                msgName = 'ConfirmSovereigntyClaimMarkerOffline'
            else:
                msgName = 'ConfirmStructureOffline'
            if eve.Message(msgName, {'item': (TYPEID, item.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            dogmaLM.Deactivate(itemID, const.effectOnlineForStructures)



    def TransferOwnership(self, itemID):
        members = sm.GetService('alliance').GetMembers()
        twit = sm.GetService('michelle')
        remotePark = twit.GetRemotePark()
        localPark = twit.GetBallpark()
        if itemID not in localPark.slimItems:
            return 
        oldOwnerID = localPark.slimItems[itemID].ownerID
        owners = []
        for member in members.itervalues():
            if member.corporationID not in owners:
                owners.append(member.corporationID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        tmplist = []
        for member in members.itervalues():
            if oldOwnerID != member.corporationID:
                tmplist.append((cfg.eveowners.Get(member.corporationID).ownerName, member.corporationID))

        ret = uix.ListWnd(tmplist, 'generic', mls.UI_CORP_SELECT_CORPORATION, None, 1)
        if ret is not None and len(ret):
            newOwnerID = ret[1]
            if remotePark is not None:
                remotePark.ChangeSovStructOwner(itemID, oldOwnerID, newOwnerID)



    def ConfigureObject(self, itemID):
        self.pwn.ConfigureSentryGun(itemID)



    def AskNewContainerPassword(self, id_, desc, which = 1, setnew = '', setold = ''):
        format = [{'type': 'edit',
          'setvalue': setold or '',
          'labelwidth': 48,
          'label': mls.UI_GENERIC_OLD,
          'key': 'oldpassword',
          'maxlength': 16,
          'setfocus': 1,
          'passwordChar': '*'}, {'type': 'edit',
          'setvalue': setnew or '',
          'labelwidth': 48,
          'label': mls.UI_GENERIC_NEW,
          'key': 'newpassword',
          'maxlength': 16,
          'passwordChar': '*'}, {'type': 'edit',
          'setvalue': '',
          'labelwidth': 48,
          'label': mls.UI_GENERIC_CONFIRM,
          'key': 'conpassword',
          'maxlength': 16,
          'passwordChar': '*'}]
        retval = uix.HybridWnd(format, desc, icon=uiconst.QUESTION, minW=300, minH=75)
        if retval:
            old = retval['oldpassword'] or None
            new = retval['newpassword'] or None
            con = retval['conpassword'] or None
            if new is None or len(new) < 3:
                eve.Message('MinThreeLetters')
                return self.AskNewContainerPassword(id_, desc, which, new, old)
            if new != con:
                eve.Message('NewPasswordMismatch')
                return self.AskNewContainerPassword(id_, desc, which, new, old)
            container = eve.GetInventoryFromId(id_)
            container.SetPassword(which, old, new)



    def LockDownBlueprint(self, invItem):
        dlg = sm.GetService('window').GetWindow('VoteWizardDialog', create=1)
        stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
        blueprints = eve.GetInventory(const.containerGlobal).ListStationBlueprintItems(invItem.locationID, stationID, True)
        description = None
        for blueprint in blueprints:
            if blueprint.itemID != invItem.itemID:
                continue
            description = '%s: %s<br>' % (mls.UI_SHARED_LOCATEDAT, cfg.evelocations.Get(stationID).locationName)
            description += '%s: %s<br>' % (mls.UI_GENERIC_MATERIALEFF, blueprint.materialLevel)
            description += '%s: %s<br>' % (mls.UI_GENERIC_PRODUCTIVITY, blueprint.productivityLevel)
            break

        dlg.voteType = const.voteItemLockdown
        dlg.voteTitle = mls.UI_CORP_LOCKDOWNTHE2 % {'item': cfg.invtypes.Get(invItem.typeID).typeName}
        dlg.voteDescription = description or dlg.voteTitle
        dlg.voteDays = 1
        dlg.itemID = invItem.itemID
        dlg.typeID = invItem.typeID
        dlg.flagInput = invItem.flagID
        dlg.locationID = stationID
        dlg.GoToStep(len(dlg.steps))
        dlg.ShowModal()



    def UnlockBlueprint(self, invItem):
        voteCases = sm.GetService('corp').GetVoteCasesByCorporation(session.corpid, 2)
        voteCaseIDByItemToUnlockID = {}
        if voteCases and len(voteCases):
            for voteCase in voteCases.itervalues():
                if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetTime() - DAY:
                    options = sm.GetService('corp').GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID)
                    if len(options):
                        for option in options.itervalues():
                            if option.parameter:
                                voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID


        if voteCaseIDByItemToUnlockID.has_key(invItem.itemID):
            raise UserError('CustomInfo', {'info': mls.UI_CORP_UNLOCK_VOTE_ALREADY_EXISTS})
        sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(session.corpid, 1).itervalues()
        sanctionedActionsByLockedItemID = util.IndexRowset(sanctionedActionsInEffect.header, [], 'parameter')
        if sanctionedActionsInEffect and len(sanctionedActionsInEffect):
            for sanctionedActionInEffect in sanctionedActionsInEffect:
                if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                    sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect.line

        if not sanctionedActionsByLockedItemID.has_key(invItem.itemID):
            raise UserError('CustomInfo', {'info': mls.UI_CORP_CANNOT_UNLOCK_NO_LOCKDOWN_SANCTIONEDACTION})
        dlg = sm.GetService('window').GetWindow('VoteWizardDialog', create=1)
        stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
        blueprints = eve.GetInventory(const.containerGlobal).ListStationBlueprintItems(invItem.locationID, stationID, True)
        description = None
        for blueprint in blueprints:
            if blueprint.itemID != invItem.itemID:
                continue
            description = '%s: %s<br>' % (mls.UI_SHARED_LOCATEDAT, cfg.evelocations.Get(stationID).locationName)
            description += '%s: %s<br>' % (mls.UI_GENERIC_MATERIALEFF, blueprint.materialLevel)
            description += '%s: %s<br>' % (mls.UI_GENERIC_PRODUCTIVITY, blueprint.productivityLevel)
            break

        dlg.voteType = const.voteItemUnlock
        dlg.voteTitle = mls.UI_CORP_UNLOCKTHE2 % {'item': cfg.invtypes.Get(invItem.typeID).typeName}
        dlg.voteDescription = description or dlg.voteTitle
        dlg.voteDays = 1
        dlg.itemID = invItem.itemID
        dlg.typeID = invItem.typeID
        dlg.flagInput = invItem.flagID
        dlg.locationID = stationID
        dlg.GoToStep(len(dlg.steps))
        dlg.ShowModal()



    def ALSCLock(self, invItems):
        for item in invItems:
            container = eve.GetInventoryFromId(item.locationID)
            container.LockItem(item.itemID)




    def ALSCUnlock(self, invItems):
        for item in invItems:
            container = eve.GetInventoryFromId(item.locationID)
            container.UnlockItem(item.itemID)




    def ViewAuditLogForALSC(self, itemID):
        sm.GetService('window').GetWindow('alsclogviewer', create=1, decoClass=form.AuditLogSecureContainerLogViewer, itemID=itemID)



    def ConfigureALSC(self, itemID):
        container = eve.GetInventoryFromId(itemID)
        config = None
        if charsession.corprole & const.corpRoleEquipmentConfig > 0 or 1:
            try:
                config = container.ALSCConfigGet()
            except UserError as e:
                pass
        defaultLock = settings.user.ui.Get('defaultContainerLock_%s' % itemID, None)
        if defaultLock is None:
            defaultLock = const.flagLocked
        format = []
        format.append({'type': 'header',
         'text': mls.UI_INFLIGHT_DEFAULTLOCKED,
         'frame': 1})
        m = [(const.flagLocked, mls.UI_GENERIC_LOCKED), (const.flagUnlocked, mls.UI_GENERIC_UNLOCKED)]
        for (value, settingName,) in m:
            format.append({'type': 'checkbox',
             'setvalue': defaultLock == value,
             'key': value,
             'label': '',
             'text': settingName,
             'frame': 1,
             'group': 'defaultContainerLock'})

        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        if config is not None:
            format.append({'type': 'header',
             'text': mls.UI_INFLIGHT_REQUIREPASSWORDFOR,
             'frame': 1})
            configSettings = [[const.ALSCPasswordNeededToOpen, mls.UI_INFLIGHT_CONTAINERPASSWORDFOROPENING],
             [const.ALSCPasswordNeededToLock, mls.UI_INFLIGHT_CONTAINERPASSWORDFORLOCKING],
             [const.ALSCPasswordNeededToUnlock, mls.UI_INFLIGHT_CONTAINERPASSWORDFORUNLOCKING],
             [const.ALSCPasswordNeededToViewAuditLog, mls.UI_INFLIGHT_CONTAINERPASSWORDFORVIEWINGLOG]]
            for (value, settingName,) in configSettings:
                format.append({'type': 'checkbox',
                 'setvalue': value & config == value,
                 'key': value,
                 'label': '',
                 'text': settingName,
                 'frame': 1})

            format.append({'type': 'btline'})
            format.append({'type': 'push'})
        retval = uix.HybridWnd(format, mls.UI_INFLIGHT_CONTAINERCONFIGURATION, 1, None, uiconst.OKCANCEL, unresizeAble=1, minW=300)
        if retval is None:
            return 
        newconfig = 0
        for (k, v,) in retval.iteritems():
            if k in (const.flagLocked, const.flagUnlocked):
                continue
            elif k == 'defaultContainerLock':
                settings.user.ui.Set('defaultContainerLock_%s' % itemID, v)
            else:
                newconfig += k * v

        if config is not None:
            container.ALSCConfigSet(newconfig)



    def RetrievePasswordALSC(self, itemID):
        container = eve.GetInventoryFromId(itemID)
        format = []
        format.append({'type': 'header',
         'text': mls.UI_INFLIGHT_WHICHPASSWORD,
         'frame': 1})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        configSettings = [[const.SCCPasswordTypeGeneral, mls.UI_GENERIC_GENERAL], [const.SCCPasswordTypeConfig, mls.UI_GENERIC_CONFIGURATION]]
        for (value, settingName,) in configSettings:
            format.append({'type': 'checkbox',
             'setvalue': value & const.SCCPasswordTypeGeneral == value,
             'key': value,
             'label': '',
             'text': settingName,
             'frame': 1,
             'group': 'which_password'})

        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, mls.UI_CMD_RETRIEVEPASSWORD, 1, None, uiconst.OKCANCEL)
        if retval is None:
            return 
        container.RetrievePassword(retval['which_password'])



    def GetFleetMemberMenu(self, func, args):
        menuSize = 20
        fleet = []
        for member in sm.GetService('fleet').GetMembers().itervalues():
            if member.charID == session.charid:
                continue
            data = cfg.eveowners.Get(member.charID)
            fleet.append((uiutil.UpperCase(data.name), (member.charID, data.name)))

        fleet = uiutil.SortListOfTuples(fleet)
        all = []
        while len(fleet) > menuSize:
            all.append(fleet[:menuSize])
            fleet = fleet[menuSize:]

        if fleet:
            all.append(fleet)
        if not all:
            return []
        else:
            if len(all) == 1:
                return self.GetSubFleetMemberMenu(all[0], func, args)
            return [ ('%c ... %c' % (sub[0][1][0], sub[-1][1][0]), ('isDynamic', self.GetSubFleetMemberMenu, (sub, func, args))) for sub in all ]



    def GetSubFleetMemberMenu(self, memberIDs, func, args):
        return [ [name, func, (charID, args)] for (charID, name,) in memberIDs ]



    def BridgeToMember(self, charID):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charID)
        if beaconStuff is None:
            return 
        self.BridgeToBeacon(charID, beaconStuff)



    def BridgeToBeaconAlliance(self, solarSystemID, beaconID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        bp.BridgeToStructure(beaconID, solarSystemID)



    def BridgeToBeacon(self, charID, beacon):
        (solarsystemID, beaconID,) = beacon
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        bp.BridgeToMember(charID, beaconID, solarsystemID)



    def JumpThroughFleet(self, otherCharID, otherShipID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        bridge = sm.GetService('fleet').GetActiveBridgeForShip(otherShipID)
        if bridge is None:
            return 
        (solarsystemID, beaconID,) = bridge
        self.LogNotice('Jump Through Fleet', otherCharID, otherShipID, beaconID, solarsystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.JumpThroughFleet, otherCharID, otherShipID, beaconID, solarsystemID)



    def JumpThroughAlliance(self, otherShipID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        bridge = sm.StartService('pwn').GetActiveBridgeForShip(otherShipID)
        if bridge is None:
            return 
        (solarsystemID, beaconID,) = bridge
        self.LogNotice('Jump Through Alliance', otherShipID, beaconID, solarsystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.JumpThroughAlliance, otherShipID, beaconID, solarsystemID)



    def JumpToMember(self, charid):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return 
        self.JumpToBeaconFleet(charid, beaconStuff)



    def JumpToBeaconFleet(self, charid, beacon):
        (solarsystemID, beaconID,) = beacon
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        self.LogNotice('Jump To Beacon Fleet', charid, beaconID, solarsystemID)
        for wnd in sm.GetService('window').GetWindows()[:]:
            if getattr(wnd, '__guid__', None) == 'form.CorpHangarArray':
                wnd.CloseX()

        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.BeaconJumpFleet, charid, beaconID, solarsystemID)



    def JumpToBeaconAlliance(self, solarSystemID, beaconID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        self.LogNotice('Jump To Beacon Alliance', beaconID, solarSystemID)
        sm.StartService('sessionMgr').PerformSessionChange('jump', bp.BeaconJumpAlliance, beaconID, solarSystemID)



    def ActivateGridSmartBomb(self, charid, effect):
        beaconStuff = sm.GetService('fleet').GetActiveBeaconForChar(charid)
        if beaconStuff is None:
            return 
        (solarsystemID, beaconID,) = beaconStuff
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is None:
            return 
        effect.Activate(beaconID, False)



    def LeaveFleet(self):
        sm.GetService('fleet').LeaveFleet()



    def MakeLeader(self, charid):
        sm.GetService('fleet').MakeLeader(charid)



    def KickMember(self, charid):
        sm.GetService('fleet').KickMember(charid)



    def DisbandFleet(self):
        sm.GetService('fleet').DisbandFleet()



    def InviteToFleet(self, charIDs, ignoreWars = 0):
        if type(charIDs) != list:
            charIDs = [charIDs]
        charErrors = {}
        for charID in charIDs:
            try:
                sm.GetService('fleet').Invite(charID, None, None, None)
            except UserError as ue:
                charErrors[charID] = ue
                sys.exc_clear()

        if len(charErrors) == 1:
            raise charErrors.values()[0]
        elif len(charErrors) > 1:
            charNames = None
            for charID in charErrors.iterkeys():
                if charNames is not None:
                    charNames += ', %s' % cfg.eveowners.Get(charID).name
                else:
                    charNames = cfg.eveowners.Get(charID).name

            raise UserError('FleetInviteMultipleErrors', {'namelist': charNames})



    def Regroup(self, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.FleetRegroup()



    def WarpFleet(self, id, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('item', id, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(id, None, None)



    def WarpToMember(self, charID, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('char', charID, minRange=warpRange)
            sm.StartService('space').WarpDestination(None, None, charID)



    def WarpFleetToMember(self, charID, warpRange = None):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('char', charID, minRange=warpRange, fleet=True)
            sm.StartService('space').WarpDestination(None, None, charID)



    def TacticalItemClicked(self, itemID):
        isTargeted = sm.GetService('target').IsTarget(itemID)
        if isTargeted:
            sm.GetService('state').SetState(itemID, state.activeTarget, 1)
        uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)



    def KeepAtRange(self, id, range = None):
        if id == session.shipid:
            return 
        if range is None:
            range = self.GetDefaultDist('KeepAtRange', id, minDist=50)
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and range is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            eve.Message('Command', {'command': mls.UI_INFLIGHT_KEEPINGATRANGE % {'name': name,
                         'range': int(range)}})
            bp.FollowBall(id, range)



    def Approach(self, id, range = None):
        if id == session.shipid:
            return 
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            eve.Message('Command', {'command': mls.UI_INFLIGHT_APPROACHINGITEM % {'name': name}})
            bp.FollowBall(id, range or 50)



    def AlignTo(self, id):
        if id == session.shipid:
            return 
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            eve.Message('Command', {'command': mls.UI_INFLIGHT_ALIGNINGTO % {'name': name}})
            bp.AlignTo(id)



    def AlignToBookmark(self, id):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.AlignTo(bookmarkID=id)



    def Orbit(self, id, range = None):
        if id == session.shipid:
            return 
        if range is None:
            range = self.GetDefaultDist('Orbit')
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and range is not None:
            name = sm.GetService('space').GetWarpDestinationName(id)
            range = float(range) if range < 10.0 else int(range)
            eve.Message('Command', {'command': mls.UI_INFLIGHT_ORBITING % {'name': name,
                         'range': range}})
            bp.Orbit(id, range)



    def TagItem(self, itemID, tag):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            bp.FleetTagTarget(itemID, tag)



    def LockTarget(self, id):
        sm.StartService('target').LockTarget(id)



    def UnlockTarget(self, id):
        sm.StartService('target').UnlockTarget(id)



    def ShowInfo(self, typeID, itemID = None, new = 0, rec = None, parentID = None, *args):
        sm.StartService('info').ShowInfo(typeID, itemID, new, rec, parentID)



    def ShowInfoForItem(self, itemID):
        bp = sm.StartService('michelle').GetBallpark()
        if bp:
            itemTypeID = bp.GetInvItem(itemID).typeID
            sm.GetService('info').ShowInfo(itemTypeID, itemID)



    def DockOrJumpOrActivateGate(self, itemID):
        bp = sm.StartService('michelle').GetBallpark()
        menuSvc = sm.GetService('menu')
        if bp:
            groupID = bp.GetInvItem(itemID).groupID
            if groupID == const.groupStation:
                menuSvc.Dock(itemID)
            if groupID == const.groupStargate:
                bp = sm.StartService('michelle').GetBallpark()
                slimItem = bp.slimItems.get(itemID)
                if slimItem:
                    jump = slimItem.jumps[0]
                    if not jump:
                        return 
                    menuSvc.StargateJump(itemID, jump.toCelestialID, jump.locationID)
            elif groupID == const.groupWarpGate:
                menuSvc.ActivateAccelerationGate(itemID)



    def PreviewType(self, typeID):
        sm.GetService('preview').PreviewType(typeID)



    def GetDefaultDist(self, forWhat, itemID = None, minDist = 500, maxDist = 1000000):
        drange = sm.GetService('menu').GetDefaultActionDistance(forWhat)
        if drange is None:
            dist = ''
            if itemID:
                bp = sm.StartService('michelle').GetBallpark()
                if not bp:
                    return 
                ball = bp.GetBall(itemID)
                if not ball:
                    return 
                dist = long(max(minDist, min(maxDist, ball.surfaceDist)))
            hint = mls.UI_INFLIGHT_SETDEFAULTDISTHINT % {'typeName': getattr(mls, 'UI_CMD_' + forWhat.upper(), forWhat),
             'fromDist': util.FmtAmt(minDist),
             'toDist': util.FmtAmt(maxDist)}
            r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=dist, hint=hint, caption=mls.UI_INFLIGHT_SETDEFAULTDIST % {'typeName': getattr(mls, 'UI_CMD_' + forWhat.upper(), forWhat)}, label=None, digits=0)
            if r:
                drange = max(minDist, min(maxDist, r['qty']))
                settings.user.ui.Set('default%sDist' % forWhat, drange)
                sm.ScatterEvent('OnDistSettingsChange')
            else:
                return 
        return drange



    def ApproachLocation(self, bookmark):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
                referringAgentID = getattr(bookmark, 'referringAgentID', None)
                sm.StartService('agents').GetAgentMoniker(bookmark.agentID).GotoLocation(bookmark.locationType, bookmark.locationNumber, referringAgentID)
            else:
                bp.GotoBookmark(bookmark.bookmarkID)



    def WarpToBookmark(self, bookmark, warpRange = 20000.0, fleet = False):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp:
            if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
                referringAgentID = getattr(bookmark, 'referringAgentID', None)
                sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
            else:
                bp.WarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)
                sm.StartService('space').WarpDestination(None, bookmark.bookmarkID, None)



    def WarpToItem(self, id, warpRange = None):
        if id == session.shipid:
            return 
        if warpRange is None:
            warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        else:
            warprange = warpRange
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and sm.StartService('space').CanWarp(id):
            bp.WarpToStuff('item', id, minRange=warprange)
            sm.StartService('space').WarpDestination(id, None, None)



    def StoreVessel(self, destID, shipID):
        if shipID != session.shipid:
            return 
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return 
        destItem = uix.GetBallparkRecord(destID)
        if destItem.categoryID == const.categoryShip:
            msgName = 'ConfirmStoreVesselInShip'
        else:
            msgName = 'ConfirmStoreVesselInStructure'
        if eve.Message(msgName, {'dest': (TYPEID, destItem.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        if shipID != session.shipid:
            return 
        shipItem = self.godma.GetStateManager().GetItem(shipID)
        if shipItem.groupID == const.groupCapsule:
            return 
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            sm.StartService('sessionMgr').PerformSessionChange('storeVessel', ship.StoreVessel, destID)



    def OpenCorpHangarArray(self, id, name):
        if getattr(self, '_openingCorpHangarArray', 0):
            return 
        self._openingCorpHangarArray = 1
        uthread.new(self._OpenCorpHangarArray, id, name)



    def _OpenCorpHangarArray(self, id, name):
        try:
            sm.StartService('window').OpenCorpHangarArray(id, name, locationFlag=const.flagNone, hasCapacity=1, nameLabel='corpHangar')

        finally:
            self._openingCorpHangarArray = 0




    def OpenShipCorpHangars(self, id, name):
        if getattr(self, '_openingCorpHangarArray', 0):
            return 
        self._openingShipCorpHangars = 1
        uthread.new(self._OpenShipCorpHangars, id, name)



    def _OpenShipCorpHangars(self, id, name):
        try:
            sm.StartService('window').OpenShipCorpHangars(id, name, locationFlag=const.flagNone, hasCapacity=1, nameLabel='corpHangar')

        finally:
            self._openingShipCorpHangars = 0




    def OpenStructure(self, id, name):
        if getattr(self, '_openingStructure', 0):
            return 
        self._openingStructure = 1
        uthread.new(self._OpenStructure, id, name)



    def _OpenStructure(self, id, name):
        try:
            sm.StartService('window').OpenContainer(id, name, locationFlag=const.flagNone, hasCapacity=1, nameLabel='structure')

        finally:
            self._openingStructure = 0




    def OpenStructureCargo(self, id, name):
        if getattr(self, '_openingStructureCargo', 0):
            return 
        self._openingStructureCargo = 1
        uthread.new(self._OpenStructureCargo, id, name)



    def _OpenStructureCargo(self, id, name):
        try:
            sm.StartService('window').OpenContainer(id, name, locationFlag=const.flagCargo, hasCapacity=1, nameLabel='cargo')

        finally:
            self._openingStructureCargo = 0




    def OpenStructureCharges(self, id, name, showCapacity = 0):
        if getattr(self, '_openingStructureCharges', 0):
            return 
        self._openingStructureCharges = 1
        uthread.new(self._OpenStructureCharges, id, name, showCapacity)



    def _OpenStructureCharges(self, id, name, showCapacity):
        try:
            sm.StartService('window').OpenContainer(id, name, locationFlag=const.flagHiSlot0, hasCapacity=showCapacity, nameLabel=name)

        finally:
            self._openingStructureCharges = 0




    def OpenStrontiumBay(self, id, name):
        if getattr(self, '_openingStrontiumBay', 0):
            return 
        self._openingStrontiumBay = 1
        uthread.new(self._OpenStrontiumBay, id, name)



    def _OpenStrontiumBay(self, id, name):
        try:
            sm.StartService('window').OpenContainer(id, name, locationFlag=const.flagSecondaryStorage, hasCapacity=1, nameLabel=name)

        finally:
            self._openingStrontiumBay = 0




    def ManageControlTower(self, id):
        uthread.new(self._ManageControlTower, id)



    def _ManageControlTower(self, id):
        uicore.cmd.OpenMoonMining(id)



    def OpenConstructionPlatform(self, id, name):
        if getattr(self, '_openingPlatform', 0):
            return 
        self._openingPlatform = 1
        uthread.new(self._OpenConstructionPlatform, id, name)



    def _OpenConstructionPlatform(self, id, name):
        try:
            sm.StartService('window').OpenContainer(id, name)

        finally:
            self._openingPlatform = 0




    def BuildConstructionPlatform(self, id):
        if getattr(self, '_buildingPlatform', 0):
            return 
        self._buildingPlatform = 1
        uthread.new(self._BuildConstructionPlatform, id)



    def _BuildConstructionPlatform(self, id):
        try:
            securityCode = None
            shell = eve.GetInventoryFromId(id)
            while 1:
                try:
                    if securityCode is None:
                        shell.Build()
                    else:
                        shell.Build(securityCode=securityCode)
                    break
                except UserError as what:
                    if what.args[0] == 'PermissionDenied':
                        if securityCode:
                            caption = mls.UI_GENERIC_INCORRECTPASSWORD
                            label = mls.UI_GENERIC_PLEASETRYAGAIN
                        else:
                            caption = mls.UI_GENERIC_PASSWORDREQUIRED
                            label = mls.UI_GENERIC_PLEASEENTERPASSWORD
                        passw = uix.NamePopup(caption=caption, label=label, setvalue='', icon=-1, modal=1, btns=None, maxLength=50, passwordChar='*')
                        if passw is None:
                            raise UserError('IgnoreToTop')
                        else:
                            securityCode = passw['name']
                    else:
                        raise 
                    sys.exc_clear()


        finally:
            self._buildingPlatform = 0




    def Bookmark(self, itemID, typeID, parentID, note = None):
        sm.StartService('addressbook').BookmarkLocationPopup(itemID, typeID, parentID, note)



    def ShowInMapBrowser(self, itemID, *args):
        uicore.cmd.OpenMapBrowser(itemID)



    def ShowInMap(self, itemID, *args):
        if session.stationid:
            sm.GetService('station').CleanUp()
        sm.GetService('map').OpenStarMap()
        sm.GetService('starmap').SetInterest(itemID, forceframe=1)



    def Dock(self, id):
        bp = sm.StartService('michelle').GetBallpark()
        if not bp:
            return 
        station = bp.GetBall(id)
        if not station:
            return 
        station.GetVectorAt(blue.os.GetTime())
        if station.surfaceDist >= const.minWarpDistance:
            self.WarpDock(id)
        else:
            eve.Message('OnDockingRequest')
            eve.Message('Command', {'command': mls.UI_INFLIGHT_REQUESTTODOCKAT % {'station': cfg.evelocations.Get(id).name}})
            paymentRequired = 0
            try:
                bp = sm.GetService('michelle').GetRemotePark()
                if bp is not None:
                    self.LogNotice('Docking', id)
                    if uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_MENU) and session.role & service.ROLE_GML:
                        success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.TurboDock, id)
                    else:
                        success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.Dock, id, session.shipid)
            except UserError as e:
                if e.msg == 'DockingRequestDeniedPaymentRequired':
                    sys.exc_clear()
                    paymentRequired = e.args[1]['amount']
                else:
                    raise 
            except Exception as e:
                raise 
            if paymentRequired:
                try:
                    if eve.Message('AskPayDockingFee', {'cost': util.FmtAmt(paymentRequired)}, uiconst.YESNO) == uiconst.ID_YES:
                        bp = sm.GetService('michelle').GetRemotePark()
                        if bp is not None:
                            session.ResetSessionChangeTimer('Retrying with docking payment')
                            if uicore.uilib.Key(uiconst.VK_CONTROL) and session.role & service.ROLE_GML:
                                success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.TurboDock, id, paymentRequired)
                            else:
                                success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.Dock, id, session.shipid, paymentRequired)
                except Exception as e:
                    raise 



    def CancelWarpDock(self):
        self.warpDocking = False



    def DefaultWarpToLabel(self):
        defaultWarpDist = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
        return (mls.UI_CMD_WARPTOWITHIN % {'dist': util.FmtDist(float(defaultWarpDist))}, menu.ACTIONSGROUP)



    def WarpDock(self, id):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None and sm.StartService('space').CanWarp():
            eve.Message('Command', {'command': mls.UI_INFLIGHT_WARPTOPRIORLOCATION % {'location': cfg.evelocations.Get(id).name}})
            self.warpDocking = True
            try:
                bp.WarpToStuff('item', id)
                sm.StartService('space').WarpDestination(id, None, None)
                michelle = sm.StartService('michelle')
                ball = michelle.GetBall(session.shipid)
                if ball is None:
                    return 
                while self.warpDocking and ball.mode != destiny.DSTBALL_WARP:
                    blue.pyos.synchro.Sleep(500)

                while self.warpDocking and ball.mode == destiny.DSTBALL_WARP:
                    blue.pyos.synchro.Sleep(500)

                if self.warpDocking:
                    self.Dock(id)

            finally:
                self.warpDocking = False




    def GetIllegality(self, itemID, typeID = None, solarSystemID = None):
        if solarSystemID is None:
            solarSystemID = session.solarsystemid
        toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID)
        if typeID is not None and cfg.invtypes.Get(typeID).groupID not in (const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer):
            if cfg.invtypes.Get(typeID).Illegality(toFactionID):
                return cfg.invtypes.Get(typeID).name
            return ''
        stuff = ''
        invItem = sm.GetService('invCache').GetInventoryFromId(itemID)
        for item in invItem.List():
            try:
                illegality = cfg.invtypes.Get(item.typeID).Illegality(toFactionID)
                if illegality:
                    stuff += cfg.invtypes.Get(item.typeID).name + ', '
                if cfg.invtypes.Get(item.typeID).groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer):
                    sublegality = self.GetIllegality(item.itemID, solarSystemID=solarSystemID)
                    if sublegality:
                        stuff += sublegality + ', '
            except:
                log.LogTraceback('bork in illegality check 2')
                sys.exc_clear()

        return stuff[:-2]



    def StargateJump(self, id, beaconID = None, solarSystemID = None):
        if beaconID:
            bp = sm.StartService('michelle').GetRemotePark()
            if bp is not None:
                if solarSystemID is not None:
                    fromFactionID = sm.StartService('faction').GetFactionOfSolarSystem(session.solarsystemid)
                    toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(solarSystemID)
                    if toFactionID and fromFactionID != toFactionID:
                        stuff = self.GetIllegality(session.shipid, solarSystemID=solarSystemID)
                        if stuff and eve.Message('ConfirmJumpWithIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name,
                         'stuff': stuff}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return 
                    sec = sm.StartService('map').GetSecurityStatus(solarSystemID)
                    toSecClass = sm.StartService('map').GetSecurityClass(solarSystemID)
                    fromSecClass = sm.StartService('map').GetSecurityClass(session.solarsystemid)
                    if toSecClass <= const.securityClassLowSec:
                        if fromSecClass >= const.securityClassHighSec and eve.Message('ConfirmJumpToUnsafeSS', {'ss': sec}, uiconst.OKCANCEL) != uiconst.ID_OK:
                            return 
                    elif fromSecClass <= const.securityClassLowSec:
                        (charcrimes, corpcrimes,) = sm.GetService('michelle').GetCriminalFlagCountDown()
                        if charcrimes.has_key(None) and eve.Message('JumpCriminalConfirm', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return 
                self.LogNotice('Stargate Jump from', session.solarsystemid2, 'to', id)
                sm.StartService('sessionMgr').PerformSessionChange(mls.UI_CMD_JUMP, bp.StargateJump, id, beaconID, session.shipid)



    def ActivateAccelerationGate(self, id):
        if eve.rookieState and not sm.StartService('tutorial').CheckAccelerationGateActivation():
            return 
        sm.StartService('sessionMgr').PerformSessionChange(mls.UI_CMD_ACTIVATEGATE, sm.RemoteSvc('keeper').ActivateAccelerationGate, id, violateSafetyTimer=1)
        self.LogNotice('Acceleration Gate activated to ', id)



    def EnterWormhole(self, itemID):
        fromSecClass = sm.StartService('map').GetSecurityClass(session.solarsystemid)
        if fromSecClass == const.securityClassHighSec and eve.Message('WormholeJumpingFromHiSec', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        probes = sm.StartService('scanSvc').GetProbeData()
        if probes is not None and len(probes) > 0:
            if eve.Message('WormholeLeaveProbesConfirm', {'probes': len(probes)}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        self.LogNotice('Wormhole Jump from', session.solarsystemid2, 'to', itemID)
        sm.StartService('sessionMgr').PerformSessionChange(mls.UI_CMD_ENTERWORMHOLE, sm.RemoteSvc('wormholeMgr').WormholeJump, itemID)



    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))



    def StopMyShip(self):
        uicore.cmd.CmdStopShip()



    def AbortWarpDock(self):
        self.warpDocking = False



    def OpenCargo(self, id, *args):
        if getattr(self, '_openingCargo', 0):
            return 
        self._openingCargo = 1
        uthread.new(self._OpenCargo, id)



    def _OpenCargo(self, _id):
        if type(_id) != types.ListType:
            _id = [_id]
        for id in _id:
            try:
                if id == session.shipid:
                    uicore.cmd.OpenCargoHoldOfActiveShip()
                else:
                    slim = sm.GetService('michelle').GetItem(id)
                    if slim and slim.groupID == const.groupWreck:
                        sm.StartService('window').OpenContainer(id, mls.UI_INFLIGHT_WRECK, hasCapacity=0, isWreck=True, windowPrefsID='lootCargoContainer')
                    else:
                        sm.StartService('window').OpenContainer(id, mls.UI_INFLIGHT_FLOATINGCARGO, hasCapacity=1, windowPrefsID='lootCargoContainer')

            finally:
                self._openingCargo = 0





    def OpenPlanetCargoLinkInventory(self, invItems):
        for invItemID in invItems:
            sm.StartService('window').OpenPlanetCargoLink(invItemID, mls.UI_PI_GENERIC_SPACEPORT)




    def OpenPlanetCargoLinkImportWindow(self, cargoLinkID):
        sm.GetService('planetUI').OpenPlanetCargoLinkImportWindow(cargoLinkID)



    def AbandonLoot(self, wreckID, *args):
        twit = sm.GetService('michelle')
        localPark = twit.GetBallpark()
        allowedGroup = None
        if wreckID in localPark.slimItems:
            allowedGroup = localPark.slimItems[wreckID].groupID
        if eve.Message('ConfirmAbandonLoot', {'type': (GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        remotePark = sm.GetService('michelle').GetRemotePark()
        if remotePark is not None:
            remotePark.AbandonLoot([wreckID])



    def AbandonAllLoot(self, wreckID, *args):
        twit = sm.GetService('michelle')
        localPark = twit.GetBallpark()
        remotePark = twit.GetRemotePark()
        if remotePark is None:
            return 
        wrecks = []
        allowedGroup = None
        if wreckID in localPark.slimItems:
            allowedGroup = localPark.slimItems[wreckID].groupID
        if eve.Message('ConfirmAbandonLootAll', {'type': (GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        bp = sm.GetService('michelle').GetBallpark()
        fleetSvc = sm.GetService('fleet')
        for (itemID, slimItem,) in localPark.slimItems.iteritems():
            if slimItem.groupID == allowedGroup:
                lootRights = getattr(slimItem, 'lootRights', [])
                if lootRights is not None and None in lootRights:
                    continue
                canLoot = session.charid == slimItem.ownerID
                if not canLoot:
                    if lootRights is not None:
                        canLoot = session.charid in lootRights or session.corpid in lootRights
                if not canLoot:
                    if fleetSvc.IsMember(slimItem.ownerID) or bp.HaveLootRight(slimItem.itemID):
                        canLoot = True
                if not canLoot:
                    continue
                wrecks.append(itemID)

        if remotePark is not None:
            remotePark.AbandonLoot(wrecks)



    def OpenShipMaintenanceBayShip(self, id, name):
        if getattr(self, '_openingSMA', 0):
            return 
        self._openingSMA = 1
        uthread.new(self._OpenShipMaintenanceBayShip, id, name)



    def _OpenShipMaintenanceBayShip(self, id, name):
        try:
            sm.StartService('window').OpenContainer(id, name, locationFlag=const.flagShipHangar, hasCapacity=1, nameLabel='sma')

        finally:
            self._openingSMA = 0




    def ShipConfig(self, id = None):
        if id == session.shipid:
            uthread.new(self._ShipConfig)



    def _ShipConfig(self):
        uicore.cmd.OpenShipConfig()



    def RunRefiningProcess(self, refineryID):
        eve.GetInventoryFromId(refineryID).RunRefiningProcess()



    def OpenDrones(self):
        if getattr(self, '_openingDrones', 0):
            return 
        self._openingDrones = 1
        uthread.new(self._OpenDrones)



    def _OpenDrones(self):
        try:
            sm.StartService('window').OpenDrones(session.shipid, 'My')

        finally:
            self._openingDrones = 0




    def EnterPOSPassword(self):
        sm.StartService('pwn').EnterShipPassword()



    def EnterForceFieldPassword(self, towerID):
        sm.StartService('pwn').EnterTowerPassword(towerID)



    def Eject(self):
        if eve.Message('ConfirmEject', {}, uiconst.YESNO) == uiconst.ID_YES:
            ship = sm.StartService('gameui').GetShipAccess()
            if ship:
                if session.stationid:
                    eve.Message('NoEjectingToSpaceInStation')
                else:
                    self.LogNotice('Ejecting from ship', session.shipid)
                    sm.StartService('sessionMgr').PerformSessionChange('eject', ship.Eject)



    def Board(self, id):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            self.LogNotice('Boarding ship', id)
            sm.StartService('sessionMgr').PerformSessionChange('board', ship.Board, id, session.shipid or session.stationid)
            shipItem = sm.StartService('godma').GetItem(session.shipid)
            if shipItem and shipItem.groupID != const.groupRookieship:
                sm.StartService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)



    def BoardSMAShip(self, structureID, shipID):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            self.LogNotice('Boarding SMA ship', structureID, shipID)
            sm.StartService('sessionMgr').PerformSessionChange('board', ship.BoardStoredShip, structureID, shipID)
            shipItem = sm.StartService('godma').GetItem(session.shipid)
            if shipItem and shipItem.groupID != const.groupRookieship:
                sm.StartService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)



    def ToggleAutopilot(self, on):
        if on:
            sm.StartService('autoPilot').SetOn()
        else:
            sm.StartService('autoPilot').SetOff('toggled through menu')



    def SelfDestructShip(self, pickid):
        if eve.Message('ConfirmSelfDestruct', {}, uiconst.YESNO) == uiconst.ID_YES:
            ship = sm.StartService('gameui').GetShipAccess()
            if ship and not session.stationid:
                self.LogNotice('Self Destruct for', session.shipid)
                sm.StartService('sessionMgr').PerformSessionChange('selfdestruct', ship.SelfDestruct, pickid)



    def SetParent(self, pickid):
        sm.GetService('camera').SetCameraParent(pickid)



    def SetInterest(self, pickid):
        sm.GetService('camera').SetCameraInterest(pickid)



    def TryLookAt(self, itemID):
        slimItem = uix.GetBallparkRecord(itemID)
        if not slimItem:
            return 
        try:
            sm.GetService('camera').LookAt(itemID)
        except Exception as e:
            sys.exc_clear()



    def ToggleLookAt(self, itemID):
        if sm.GetService('camera').LookingAt() == itemID and itemID != session.shipid:
            self.TryLookAt(session.shipid)
        else:
            self.TryLookAt(itemID)



    def Scoop(self, objectID, typeID, password = None):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            toFactionID = sm.StartService('faction').GetFactionOfSolarSystem(session.solarsystemid)
            stuff = self.GetIllegality(objectID, typeID)
            if stuff and eve.Message('ConfirmScoopWithIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            try:
                if password is None:
                    ship.Scoop(objectID)
                else:
                    ship.Scoop(objectID, password)
            except UserError as what:
                if what.args[0] == 'ShpScoopSecureCC':
                    if password:
                        caption = mls.UI_GENERIC_INCORRECTPASSWORD
                        label = mls.UI_GENERIC_PLEASETRYAGAIN
                    else:
                        caption = mls.UI_GENERIC_PASSWORDREQUIRED
                        label = mls.UI_GENERIC_PLEASEENTERPASSWORD
                    passw = uix.NamePopup(caption=caption, label=label, setvalue='', icon=-1, modal=1, btns=None, maxLength=50, passwordChar='*')
                    if passw:
                        self.Scoop(objectID, password=passw['name'])
                else:
                    raise 
                sys.exc_clear()



    def ScoopSMA(self, objectID):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ship.ScoopToSMA(objectID)



    def InteractWithAgent(self, agentID, *args):
        sm.StartService('agents').InteractWith(agentID)



    def TakeOutTrash(self, invItems, *args):
        eve.GetInventory(const.containerHangar).TakeOutTrash([ invItem.itemID for invItem in invItems ])



    def QuickBuy(self, typeID):
        sm.StartService('marketutils').Buy(typeID)



    def QuickSell(self, invItem):
        sm.StartService('marketutils').Sell(invItem.typeID, invItem=invItem)



    def QuickContract(self, invItems, *args):
        sm.GetService('contracts').OpenCreateContract(items=invItems)



    def ShowMarketDetails(self, invItem):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, invItem.typeID, None)



    def GetContainerContents(self, invItem):
        hasFlag = invItem.categoryID == const.categoryShip
        name = cfg.invtypes.Get(invItem.typeID).name
        stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
        self.DoGetContainerContents(invItem.itemID, stationID, hasFlag, name)



    def DoGetContainerContents(self, itemID, stationID, hasFlag, name):
        contents = eve.inventorymgr.GetContainerContents(itemID, stationID)
        t = ''
        lst = []
        for c in contents:
            locationName = ''
            flag = c.flagID
            if flag == const.flagPilot:
                continue
            locationName = util.GetShipFlagLocationName(flag)
            t = cfg.invtypes.Get(c.typeID)
            if hasFlag:
                txt = '%s<t>%s<t>%s<t>%s' % (t.name,
                 cfg.invgroups.Get(t.groupID).name,
                 locationName,
                 c.stacksize)
            else:
                txt = '%s<t>%s<t>%s' % (t.name, cfg.invgroups.Get(t.groupID).name, c.stacksize)
            lst.append([txt, None, c.typeID])

        if hasFlag:
            hdr = [mls.UI_GENERIC_NAME,
             mls.UI_GENERIC_GROUP,
             mls.UI_GENERIC_LOCATION,
             mls.UI_GENERIC_QTY]
        else:
            hdr = [mls.UI_GENERIC_NAME, mls.UI_GENERIC_GROUP, mls.UI_GENERIC_QTY]
        uix.ListWnd(lst, 'item', mls.UI_GENERIC_ITEMSINCONTAINER, hint=mls.UI_GENERIC_ITEMSINCONTAINER_HINT % {'name': name}, isModal=0, minChoices=0, scrollHeaders=hdr, minw=500)



    def AddToQuickBar(self, typeID):
        current = settings.user.ui.Get('quickbar', {})
        lastid = settings.user.ui.Get('quickbar_lastid', 0)
        for (id, data,) in current.items():
            if data.parent == 0 and data.label == typeID:
                return None

        n = util.KeyVal()
        n.parent = 0
        n.id = lastid + 1
        n.label = typeID
        lastid += 1
        settings.user.ui.Set('quickbar_lastid', lastid)
        current[n.id] = n
        settings.user.ui.Set('quickbar', current)
        sm.ScatterEvent('OnMarketQuickbarChange', menu=1)



    def RemoveFromQuickBar(self, node):
        current = settings.user.ui.Get('quickbar', {})
        parent = node.parent
        typeID = node.typeID
        toDelete = None
        for (id, data,) in current.items():
            if parent == data.parent and type(data.label) == types.IntType:
                if data.label == typeID:
                    toDelete = id
                    break

        if toDelete:
            del current[id]
        settings.user.ui.Set('quickbar', current)
        sm.ScatterEvent('OnMarketQuickbarChange')



    def GetAndvancedMarket(self, typeID):
        pass



    def ActivateShip(self, invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryActivateShip(invItem)



    def LeaveShip(self, invItem):
        if invItem.singleton and not uicore.uilib.Key(uiconst.VK_CONTROL):
            sm.StartService('station').TryLeaveShip(invItem)



    def StripFitting(self, invItem):
        if eve.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            shipID = invItem.itemID
            sm.GetService('invCache').GetInventoryFromId(shipID).StripFitting()



    def ExitStation(self, invItem):
        uicore.cmd.CmdExitStation()



    def CheckLocked(self, func, invItemsOrIDs):
        if not len(invItemsOrIDs):
            return 
        if type(invItemsOrIDs[0]) == int or not hasattr(invItemsOrIDs[0], 'itemID'):
            ret = func(invItemsOrIDs)
        else:
            lockedItems = []
            try:
                for item in invItemsOrIDs:
                    if sm.StartService('invCache').IsItemLocked(item.itemID):
                        continue
                    if sm.StartService('invCache').TryLockItem(item.itemID):
                        lockedItems.append(item)

                if not len(lockedItems):
                    eve.Message('BusyItems')
                    return 
                ret = func(lockedItems)

            finally:
                for invItem in lockedItems:
                    sm.StartService('invCache').UnlockItem(invItem.itemID)


        return ret



    def Repackage(self, invItems):
        if eve.Message('ConfirmRepackageItem', {}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        validIDsByStationID = defaultdict(list)
        ok = 0
        for invItem in invItems:
            state = sm.StartService('godma').GetItem(invItem.itemID)
            if state:
                damage = 0
                if invItem.categoryID in (const.categoryShip, const.categoryDrone):
                    damage += state.armorDamage
                damage += state.damage
                if damage != 0:
                    eve.Message('CantRepackageDamagedItem')
                    continue
                contracts = sm.StartService('insurance').GetContracts()
                if contracts.has_key(invItem.itemID):
                    if ok or eve.Message('RepairUnassembleVoidsContract', {}, uiconst.YESNO) == uiconst.ID_YES:
                        stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
                        if stationID is not None:
                            validIDsByStationID[stationID].append((invItem.itemID, invItem.locationID))
                            ok = 1
                    else:
                        continue
                else:
                    stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
                    if stationID is not None:
                        validIDsByStationID[stationID].append((invItem.itemID, invItem.locationID))
            else:
                stationID = sm.StartService('invCache').GetStationIDOfItem(invItem)
                if stationID is not None:
                    validIDsByStationID[stationID].append((invItem.itemID, invItem.locationID))

        skipChecks = []
        while True:
            try:
                sm.RemoteSvc('repairSvc').UnasembleItems(dict(validIDsByStationID), skipChecks)
            except UserError as e:
                if cfg.messages[e.msg].messageType == 'question':
                    ret = eve.Message(e.msg, e.dict, uiconst.YESNO)
                    if ret == uiconst.ID_YES:
                        skipChecks.append(e.msg)
                        sys.exc_clear()
                        continue
                else:
                    raise 
            break




    def Break(self, invItems):
        ok = 0
        validIDs = []
        for invItem in invItems:
            if ok or eve.Message('ConfirmBreakCourierPackage', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                validIDs.append(invItem.itemID)
                ok = 1

        for itemID in validIDs:
            eve.GetInventoryFromId(itemID).BreakPlasticWrap()




    def DeliverCourierContract(self, invItem):
        sm.GetService('contracts').DeliverCourierContractFromItemID(invItem.itemID)



    def FindCourierContract(self, invItem):
        sm.GetService('contracts').FindCourierContractFromItemID(invItem.itemID)



    def LaunchDrones(self, invItems, *args):
        sm.GetService('godma').GetStateManager().SendDroneSettings()
        util.LaunchFromShip(invItems)



    def LaunchForSelf(self, invItems):
        util.LaunchFromShip(invItems, session.charid)



    def LaunchForCorp(self, invItems, ignoreWarning = False):
        util.LaunchFromShip(invItems, session.corpid, ignoreWarning)



    def LaunchSMAContents(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        structureID = None
        bp = sm.StartService('michelle').GetBallpark()
        myShipBall = bp.GetBall(session.shipid)
        if myShipBall and myShipBall.mode == destiny.DSTBALL_WARP:
            raise UserError('ShipInWarp')
        ids = []
        for invItem in invItems:
            structureID = invItem.locationID
            ids += [invItem.itemID] * invItem.stacksize

        sm.StartService('gameui').GetShipAccess().LaunchFromContainer(structureID, ids)



    def Jettison(self, invItems):
        if eve.Message('ConfirmJettison', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        ids = []
        for invItem in invItems:
            ids += [invItem.itemID]

        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ship.Jettison(ids)



    def TrashInvItems(self, invItems):
        if len(invItems) == 0:
            return 
        self.CheckItemsInSamePlace(invItems)
        if len(invItems) == 1:
            question = 'ConfirmTrashingSin'
            args = {'item': (TYPEIDANDQUANTITY, invItems[0].typeID, invItems[0].stacksize)}
        else:
            question = 'ConfirmTrashingPlu'
            report = ''
            for item in invItems:
                report += '<t>- %s<br>' % cfg.FormatConvert(TYPEIDANDQUANTITY, item.typeID, item.stacksize)

            args = {'items': report}
        if eve.Message(question, args, uiconst.YESNO) != uiconst.ID_YES:
            return 
        stationID = sm.StartService('invCache').GetStationIDOfItem(invItems[0])
        windows = ['sma',
         'corpHangar',
         'drones',
         'shipCargo']
        for item in invItems:
            isShip = False
            if hasattr(item, 'categoryID'):
                isShip = item.categoryID == const.categoryShip
            else:
                isShip = cfg.invtypes.Get(item.typeID).categoryID == const.categoryShip
            if isShip:
                for window in windows:
                    wnd = sm.GetService('window').GetWindow('%s_%s' % (window, item.itemID))
                    if wnd:
                        wnd.SelfDestruct()


        errors = eve.inventorymgr.TrashItems([ item.itemID for item in invItems ], stationID if stationID else invItems[0].locationID)
        if errors:
            for e in errors:
                eve.Message(e)

            return 
        isCorp = invItems[0].ownerID == session.corpid
        self.InvalidateItemLocation([session.charid, session.corpid][isCorp], stationID, invItems[0].flagID)
        if isCorp:
            sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)



    def Refine(self, invItems):
        if not session.stationid:
            return 
        if len(invItems) == 1:
            item = invItems[0]
            ty = cfg.invtypes.Get(item.typeID)
            if item.stacksize < ty.portionSize:
                eve.Message('QuantityLessThanMinimumPortion', {'typename': ty.name,
                 'portion': ty.portionSize})
                return 
        sm.StartService('reprocessing').ReprocessDlg(invItems)



    def RefineToHangar(self, invItems):
        if not session.stationid:
            return 
        (ownerID, flag,) = (invItems[0].ownerID, invItems[0].flagID)
        if flag not in (const.flagHangar,
         const.flagCorpSAG2,
         const.flagCorpSAG3,
         const.flagCorpSAG4,
         const.flagCorpSAG5,
         const.flagCorpSAG6,
         const.flagCorpSAG7):
            flag = const.flagHangar
        if flag != const.flagHangar and ownerID != session.corpid:
            ownerID = session.corpid
        if ownerID not in (session.charid, session.corpid):
            ownerID = session.charid
        sm.StartService('reprocessing').ReprocessDlg(invItems, ownerID, flag)



    def TrainNow(self, invItems):
        if len(invItems) > 1:
            eve.Message('TrainMoreTheOne')
            return 
        self.InjectSkillIntoBrain(invItems)
        blue.pyos.synchro.Sleep(500)
        sm.StartService('skillqueue').TrainSkillNow(invItems[0].typeID, 1)



    def InjectSkillIntoBrain(self, invItems):
        sm.StartService('skills').InjectSkillIntoBrain(invItems)



    def PlugInImplant(self, invItems):
        if eve.Message('ConfirmPlugInImplant', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        for invItem in invItems:
            sm.StartService('godma').GetSkillHandler().CharAddImplant(invItem.itemID, invItem.locationID)




    def ApplyPilotLicence(self, itemID):
        try:
            sm.RemoteSvc('userSvc').ApplyPilotLicence(itemID, justQuery=True)
        except UserError as e:
            if e.msg == '28DaysConfirmApplyServer':
                if eve.Message(e.msg, e.dict, uiconst.YESNO) != uiconst.ID_YES:
                    return 
                sm.RemoteSvc('userSvc').ApplyPilotLicence(itemID, justQuery=False)
            else:
                raise 



    def ConsumeBooster(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        for invItem in invItems:
            sm.StartService('godma').GetSkillHandler().CharUseBooster(invItem.itemID, invItem.locationID)




    def AssembleContainer(self, invItems):
        for invItem in invItems:
            eve.inventorymgr.AssembleCargoContainer(invItem.itemID, None, 0.0)




    def OpenContainer(self, invItems):
        for invItem in invItems:
            if invItem.ownerID not in (session.charid, session.corpid):
                eve.Message('CantDoThatWithSomeoneElsesStuff')
                return 
            name = cfg.evelocations.Get(invItem.itemID).name or cfg.invtypes.Get(invItem.typeID).name
            sm.StartService('window').OpenContainer(invItem.itemID, name, "%s's container" % name, invItem.typeID, hasCapacity=invItem.typeID != const.typePlasticWrap)




    def Manufacture(self, invItems, activityID):
        sm.StartService('manufacturing').CreateJob(invItems, None, activityID)



    def AssembleShip(self, invItems):
        itemIDs = []
        for item in invItems:
            techLevel = sm.StartService('godma').GetTypeAttribute(invItems[0].typeID, const.attributeTechLevel)
            if techLevel is None:
                techLevel = 1
            else:
                techLevel = int(techLevel)
            if techLevel == 3:
                if session.stationid is None:
                    eve.Message('CantAssembleModularShipInSpace')
                    return 
                windowSvc = sm.GetService('window')
                wndName = 'assembleWindow_%s' % item.itemID
                wnd = windowSvc.GetWindow(wndName)
                if wnd is None:
                    wnd = windowSvc.GetWindow(wndName, create=1, decoClass=form.AssembleShip, ship=invItems[0])
                else:
                    wnd.Maximize()
                return 
            itemIDs.append(item.itemID)

        sm.StartService('gameui').GetShipAccess().AssembleShip(itemIDs)



    def TryFit(self, invItems):
        if not session.shipid:
            return 
        godma = sm.services['godma']
        ship = godma.GetItem(session.shipid)
        if not ship:
            return 
        godmaSM = godma.GetStateManager()
        invCassi = sm.StartService('invCache')
        useRigs = None
        shipInv = eve.GetInventoryFromId(session.shipid)
        charges = set()
        for invItem in invItems[:]:
            if invItem.categoryID == const.categoryModule:
                moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
                for mEff in moduleEffects:
                    if mEff.effectID == const.effectRigSlot:
                        if useRigs is None:
                            useRigs = True if self.RigFittingCheck(invItem) else False
                        if not useRigs:
                            invItems.remove(invItem)
                            invCassi.UnlockItem(invItem.itemID)
                            break

            elif invItem.categoryID == const.categorySubSystem:
                if godmaSM.CheckFutileSubSystemSwitch(invItem.typeID, invItem.itemID):
                    invItems.remove(invItem)
                    invCassi.UnlockItem(invItem.itemID)
            elif invItem.categoryID == const.categoryCharge:
                charges.add(invItem)
                invItems.remove(invItem)

        if len(invItems) > 0:
            ship.inventory.moniker.MultiAdd([ invItem.itemID for invItem in invItems ], invItems[0].locationID, flag=const.flagAutoFit)
            for invItem in invItems:
                uthread.new(godma.GetStateManager().DelayedOnlineAttempt, session.shipid, invItem.itemID)

        if charges:
            if len(invItems):
                count = 0
                while count < 1000:
                    count += 1
                    blue.pyos.synchro.Sleep(100)
                    for item in invItems:
                        if not godmaSM.GetAttributeValueByID(item.itemID, const.attributeIsOnline):
                            if count % 20 == 0:
                                self.LogInfo('After', count / 10, "seconds, I'm still waiting for all modules to come online")
                            break
                    else:
                        break

                else:
                    self.LogWarn("I've waited for", count / 10, "seconds for all the added modules to come online, but they didn't. Continuing, but expect errors...")

            shipStuff = shipInv.List()
            shipStuff.sort(key=lambda r: (r.flagID, godmaSM.IsSubLocation(r.itemID)))
            loadedSlots = set()
        for invItem in charges:
            chargeDgmType = godmaSM.GetType(invItem.typeID)
            isCrystalOrScript = invItem.groupID in cfg.GetCrystalGroups()
            for row in shipStuff:
                if row in loadedSlots:
                    continue
                if not cfg.IsShipFittingFlag(row.flagID):
                    continue
                if godmaSM.IsInWeaponBank(row.itemID) and godmaSM.IsSlaveModule(row.itemID):
                    continue
                if row.categoryID == const.categoryCharge:
                    continue
                moduleDgmType = godmaSM.GetType(row.typeID)
                desiredSize = getattr(moduleDgmType, 'chargeSize', None)
                for x in xrange(1, 5):
                    chargeGroup = getattr(moduleDgmType, 'chargeGroup%d' % x, False)
                    if not chargeGroup:
                        continue
                    if chargeDgmType.groupID != chargeGroup:
                        continue
                    if desiredSize is not None and getattr(chargeDgmType, 'chargeSize', -1) != desiredSize:
                        continue
                    leftOvers = False
                    for (i, squatter,) in enumerate([ i for i in shipStuff if i.flagID == row.flagID ]):
                        if isCrystalOrScript and i > 0:
                            break
                        elif not isCrystalOrScript and godmaSM.IsSubLocation(squatter.itemID):
                            if godmaSM.GetType(row.typeID).capacity <= chargeDgmType.volume * squatter.stacksize:
                                break
                    else:
                        godmaSM.LoadAmmoToModules([row.itemID], invItem.typeID, invItem.itemID, invItem.locationID)
                        leftOvers = not isCrystalOrScript and invItem.stacksize > godmaSM.GetType(row.typeID).capacity / chargeDgmType.volume
                        loadedSlots.add(row)
                        blue.pyos.synchro.Sleep(100)
                        break

                else:
                    continue

                if not leftOvers:
                    break
            else:
                eve.Message('NoSuitableModules')





    def OpenCargohold(self, invItems):
        knowCantDoThatWithSomeoneElsesStuff = 0
        for invItem in invItems:
            if not invItem.ownerID == session.charid:
                if not knowCantDoThatWithSomeoneElsesStuff:
                    eve.Message('CantDoThatWithSomeoneElsesStuff')
                    knowCantDoThatWithSomeoneElsesStuff = 1
                continue
            name = cfg.evelocations.Get(invItem.itemID).name
            sm.StartService('window').OpenCargo(invItem.itemID, name, "%s's %s" % (name, mls.UI_GENERIC_CARGO), invItem.typeID)




    def OpenDroneBay(self, invItems):
        knowCantDoThatWithSomeoneElsesStuff = 0
        for invItem in invItems:
            if not invItem.ownerID == session.charid:
                if not knowCantDoThatWithSomeoneElsesStuff:
                    eve.Message('CantDoThatWithSomeoneElsesStuff')
                    knowCantDoThatWithSomeoneElsesStuff = 1
                return 
            name = cfg.evelocations.Get(invItem.itemID).name
            sm.StartService('window').OpenDrones(invItem.itemID, name, "%s's %s" % (name, mls.UI_GENERIC_DRONEBAY), invItem.typeID)




    def OpenSpecialCargoBay(self, id, invFlag):
        if getattr(self, '_openingSpecialCargo', 0):
            return 
        self._openingSpecialCargo = 1
        uthread.new(self._OpenSpecialCargoBay, id, invFlag)



    def _OpenSpecialCargoBay(self, id, invFlag):
        try:
            invFlagData = inventoryFlagsCommon.inventoryFlagData[invFlag]
            if id == session.shipid:
                holdName = mls.UI_GENERIC_MYSPECIALBAY % invFlagData['name']
            else:
                holdName = mls.UI_GENERIC_POSSESSIVESPECIALBAY % {'owner': uix.Possessive(cfg.evelocations.Get(id).name),
                 'item': invFlagData['name']}
            sm.StartService('window').OpenSpecialCargoBay(id, holdName, invFlag, nameLabel='specialCargo')

        finally:
            self._openingSpecialCargo = 0




    def HandleMultipleCallError(self, droneID, ret, messageName):
        if not len(ret):
            return 
        if len(droneID) == 1:
            pick = droneID[0]
            raise UserError(ret[pick][0], ret[pick][1])
        elif len(droneID) >= len(ret):
            lastError = ''
            for error in ret.itervalues():
                if error[0] != lastError and lastError != '':
                    raise UserError(messageName, {'succeeded': len(droneID) - len(ret),
                     'failed': len(ret),
                     'total': len(droneID)})
                lastError = error[0]
            else:
                pick = ret.items()[0][1]
                raise UserError(pick[0], pick[1])




    def EngageTarget(self, droneIDs):
        michelle = sm.StartService('michelle')
        requiresAttackConfirmation = False
        requiresAidConfirmation = False
        dronesRemoved = []
        for droneID in droneIDs:
            item = michelle.GetItem(droneID)
            if not item:
                dronesRemoved.append(droneID)
                continue
            for row in cfg.dgmtypeeffects.get(item.typeID, []):
                (effectID, isDefault,) = (row.effectID, row.isDefault)
                if isDefault:
                    effect = cfg.dgmeffects.Get(effectID)
                    if effect.isOffensive:
                        requiresAttackConfirmation = True
                        break
                    elif effect.isAssistance:
                        requiresAidConfirmation = True
                        break


        for droneID in dronesRemoved:
            droneIDs.remove(droneID)

        if requiresAttackConfirmation and requiresAidConfirmation:
            raise UserError('DroneCommandEngageRequiresNoAmbiguity')
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        if requiresAidConfirmation and not sm.StartService('consider').DoAidConfirmations(targetID):
            return 
        if requiresAttackConfirmation and not sm.StartService('consider').DoAttackConfirmations(targetID):
            return 
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdEngage(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs:
                name = sm.GetService('space').GetWarpDestinationName(targetID)
                eve.Message('Command', {'command': mls.UI_INFLIGHT_DRONESENGAGING % {'name': name}})



    def ReturnControl(self, droneIDs):
        michelle = sm.StartService('michelle')
        dronesByOwner = {}
        for droneID in droneIDs:
            ownerID = michelle.GetDroneState(droneID).ownerID
            if dronesByOwner.has_key(ownerID):
                dronesByOwner[ownerID].append(droneID)
            else:
                dronesByOwner[ownerID] = [droneID]

        entity = moniker.GetEntityAccess()
        if entity:
            for (ownerID, IDs,) in dronesByOwner.iteritems():
                ret = entity.CmdRelinquishControl(IDs)
                self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')




    def DelegateControl(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            controllerID = targetItem.ownerID
        else:
            controllerID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdDelegateControl(droneIDs, controllerID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def Assist(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            assistID = targetItem.ownerID
        else:
            assistID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdAssist(assistID, droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def Guard(self, charID, droneIDs):
        if charID is None:
            targetID = sm.StartService('target').GetActiveTargetID()
            if targetID is None:
                raise UserError('DroneCommandRequiresActiveTarget')
            michelle = sm.StartService('michelle')
            targetItem = michelle.GetItem(targetID)
            if targetItem.categoryID != const.categoryShip or targetItem.groupID == const.groupCapsule:
                raise UserError('DroneCommandRequiresShipButNotCapsule')
            targetBall = michelle.GetBall(targetID)
            if not targetBall.isInteractive or not sm.GetService('fleet').IsMember(targetItem.ownerID):
                raise UserError('DroneCommandRequiresShipPilotedFleetMember')
            guardID = targetItem.ownerID
        else:
            guardID = charID
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdGuard(guardID, droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def Mine(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdMine(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def MineRepeatedly(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdMineRepeatedly(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def DroneUnanchor(self, droneIDs):
        targetID = sm.StartService('target').GetActiveTargetID()
        if targetID is None:
            raise UserError('DroneCommandRequiresActiveTarget')
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdUnanchor(droneIDs, targetID)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def ReturnAndOrbit(self, droneIDs):
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnHome(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def ReturnToDroneBay(self, droneIDs):
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnBay(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')



    def ScoopToDroneBay(self, objectIDs):
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            ret = ship.ScoopDrone(objectIDs)
            self.HandleMultipleCallError(objectIDs, ret, 'MultiDroneCmdResult')



    def FitDrone(self, invItems):
        if type(invItems) is not list:
            invItems = [invItems]
        itemIDs = [ node.itemID for node in invItems ]
        if session.shipid:
            for itemID in itemIDs:
                sm.StartService('invCache').UnlockItem(itemID)

            eve.GetInventoryFromId(session.shipid).MultiAdd(itemIDs, invItems[0].locationID, flag=const.flagDroneBay)



    def AbandonDrone(self, droneIDs):
        if eve.Message('ConfirmAbandonDrone', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdAbandonDrone(droneIDs)
            self.HandleMultipleCallError(droneIDs, ret, 'MultDroneCmdResult')



    def CopyItemIDAndMaybeQuantityToClipboard(self, invItem):
        txt = str(invItem.itemID)
        if invItem.stacksize > 1:
            txt += '(%s)' % invItem.stacksize
        blue.pyos.SetClipboardData(txt)



    def ItemLockFunction(self, invItem, *args):
        sm.StartService('invCache').TryLockItem(invItem.itemID, 'lockItemMenuFunction', {'itemType': cfg.invtypes.Get(invItem.typeID).typeName,
         'action': args[0]}, 1)
        try:
            return args[1](*((), args[-1])[(len(args) > 2)])

        finally:
            sm.StartService('invCache').UnlockItem(invItem.itemID)




    def SetName(self, invItemsOrSlimItems):
        for invItem in invItemsOrSlimItems:
            cfg.evelocations.Prime([invItem.itemID])
            try:
                setval = cfg.evelocations.Get(invItem.itemID).name
            except:
                setval = ''
                sys.exc_clear()
            maxLength = 100
            setval = setval[:32]
            categoryID = cfg.invtypes.Get(invItem.typeID).Group().Category().id
            if categoryID == const.categoryShip:
                maxLength = 20
            if categoryID == const.categoryStructure:
                maxLength = 32
            nameRet = uix.NamePopup(mls.UI_GENERIC_SETNAME, mls.UI_GENERIC_TYPEINNEWNAME, setvalue=setval, maxLength=maxLength)
            if nameRet:
                eve.inventorymgr.SetLabel(invItem.itemID, nameRet['name'].replace('\n', ' '))
                sm.ScatterEvent('OnItemNameChange')




    def AskNewContainerPwd(self, invItems, desc, which = 1):
        for invItem in invItems:
            self.AskNewContainerPassword(invItem.itemID, desc, which)




    def GetGlobalActiveItemKeyName(self, forWhat):
        key = None
        if forWhat in [mls.UI_CMD_ORBIT, mls.UI_CMD_KEEPATRANGE, self.DefaultWarpToLabel()[0]]:
            key = ['Orbit', 'KeepAtRange', 'WarpTo'][[mls.UI_CMD_ORBIT, mls.UI_CMD_KEEPATRANGE, self.DefaultWarpToLabel()[0]].index(forWhat)]
        return key



    def GetDefaultActionDistance(self, what):
        if what == 'KeepAtRange':
            return int(settings.user.ui.Get('defaultKeepAtRangeDist', 500))
        if what == 'Orbit':
            return int(settings.user.ui.Get('defaultOrbitDist', 5000))
        if what == 'WarpTo':
            return settings.user.ui.Get('defaultWarpToDist', const.minWarpEndDistance)



    def CopyCoordinates(self, itemID):
        ball = self.michelle.GetBall(itemID)
        if ball:
            blue.pyos.SetClipboardData(str((ball.x, ball.y, ball.z)))



    def RepairItems(self, items):
        if items is None or len(items) < 1:
            return 
        wnd = sm.GetService('window').GetWindow('repairshop', decoClass=form.RepairShopWindow, create=1, maximize=1)
        if wnd and not wnd.destroyed:
            wnd.DisplayRepairQuote(items)




class ActionMenu(uicls.Container):
    __guid__ = 'xtriui.ActionMenu'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.actionMenuOptions = {mls.UI_CMD_SHOWINFO: ('ui_44_32_24', 0, 0, 0, 0),
         mls.UI_CMD_LOCKTARGET: ('ui_44_32_17', 0, 0, 0, 0),
         mls.UI_CMD_UNLOCKTARGET: ('ui_44_32_17', 0, 0, 0, 1),
         mls.UI_CMD_APPROACH: ('ui_44_32_23', 0, 0, 0, 0),
         mls.UI_CMD_LOOKAT: ('ui_44_32_20', 0, 0, 0, 0),
         mls.UI_CMD_RESETCAMERA: ('ui_44_32_20', 0, 0, 0, 1),
         mls.UI_CMD_KEEPATRANGE: ('ui_44_32_22', 0, 0, 1, 0),
         mls.UI_CMD_ORBIT: ('ui_44_32_21', 0, 0, 1, 0),
         mls.UI_CMD_DOCK: ('ui_44_32_9', 0, 0, 0, 0),
         mls.UI_CMD_STARTCONVERSATION: ('ui_44_32_33', 0, 0, 0, 0),
         mls.UI_CMD_OPENCARGO: ('ui_44_32_35', 0, 0, 0, 0),
         mls.UI_CMD_OPENMYCARGO: ('ui_44_32_35', 0, 0, 0, 0),
         mls.UI_PI_ACCESSCARGOLINK: ('ui_44_32_35', 0, 0, 0, 0),
         mls.UI_CMD_STOPMYSHIP: ('ui_44_32_38', 0, 0, 0, 0),
         mls.UI_CMD_STOPMYCAPSULE: ('ui_44_32_38', 0, 0, 0, 0),
         mls.UI_CMD_ACTIVATEAUTOPILOT: ('ui_44_32_12', 0, 0, 0, 0),
         mls.UI_CMD_DEACTIVATEAUTOPILOT: ('ui_44_32_12', 0, 0, 0, 1),
         mls.UI_CMD_EJECT: ('ui_44_32_36', 0, 0, 0, 0),
         mls.UI_CMD_SELFDESTRUCT: ('ui_44_32_37', 0, 0, 0, 0),
         mls.UI_CMD_BOARDSHIP: ('ui_44_32_40', 0, 0, 0, 0),
         mls.UI_CMD_JUMP: ('ui_44_32_39', 0, 0, 0, 0),
         mls.UI_CMD_ENTERWORMHOLE: ('ui_44_32_39', 0, 0, 0, 0),
         mls.UI_CMD_ACTIVATEGATE: ('ui_44_32_39', 0, 0, 0, 0),
         mls.UI_CMD_SCOOPTODRONEBAY: ('ui_44_32_1', 0, 0, 0, 0),
         mls.UI_CMD_SCOOPTOCARGOBAY: ('ui_44_32_1', 0, 0, 0, 0),
         mls.UI_CMD_READNEWS: ('ui_44_32_47', 0, 0, 0, 0)}
        self.lastActionSerial = None
        self.sr.actionTimer = None
        self.itemID = None
        self.width = 134
        self.height = 134
        self.pickRadius = -1
        self.oldx = self.oldy = None
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalUp)
        self.mouseMoveCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnGlobalMove)



    def Load(self, slimItem, centerItem = None, setposition = 1):
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return 
        actions = sm.StartService('menu').CelestialMenu(slimItem.itemID, slimItem=slimItem, ignoreTypeCheck=1)
        reasonsWhyNotAvailable = getattr(actions, 'reasonsWhyNotAvailable', {})
        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return 
        self.itemID = slimItem.itemID
        warptoLabel = sm.GetService('menu').DefaultWarpToLabel()[0]
        warpops = {warptoLabel: ('ui_44_32_18', 0, 0, 1, 0)}
        self.actionMenuOptions.update(warpops)
        serial = ''
        valid = {}
        inactive = None
        for each in actions:
            if each:
                if isinstance(each[0], tuple):
                    name = each[0][0]
                else:
                    name = each[0]
                if name == 'Inactive':
                    inactive = each[1]
                elif name in self.actionMenuOptions:
                    valid[name] = each
                    if type(each[1]) not in (str, unicode):
                        serial += '%s_' % name

        if inactive:
            for each in inactive:
                if isinstance(each[0], tuple):
                    name = each[0][0]
                else:
                    name = each[0]
                if name in self.actionMenuOptions:
                    valid[name] = each
                    if type(each[1]) not in (str, unicode):
                        serial += '%s_' % name

        if not (uicore.uilib.leftbtn or uicore.uilib.midbtn):
            return 
        if serial != self.lastActionSerial:
            uix.Flush(self)
            i = 0
            order = [mls.UI_CMD_SHOWINFO,
             [mls.UI_CMD_LOCKTARGET, mls.UI_CMD_UNLOCKTARGET],
             [mls.UI_CMD_APPROACH, warptoLabel],
             mls.UI_CMD_ORBIT,
             mls.UI_CMD_KEEPATRANGE]
            default = [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], None]
            groups = {const.groupStation: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_DOCK],
             const.groupCargoContainer: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupSecureCargoContainer: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupAuditLogSecureContainer: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupFreightContainer: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupSpawnContainer: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupDeadspaceOverseersBelongings: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupWreck: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_OPENCARGO],
             const.groupStargate: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_JUMP],
             const.groupWormhole: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_ENTERWORMHOLE],
             const.groupWarpGate: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_ACTIVATEGATE],
             const.groupBillboard: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_READNEWS],
             const.groupAgentsinSpace: [mls.UI_CMD_STARTCONVERSATION, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], None],
             const.groupDestructibleAgentsInSpace: [mls.UI_CMD_STARTCONVERSATION, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], None],
             const.groupPlanetaryCustomsOffices: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_PI_ACCESSCARGOLINK]}
            categories = {const.categoryShip: [mls.UI_CMD_STARTCONVERSATION, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_BOARDSHIP],
             const.categoryDrone: [None, [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA], mls.UI_CMD_SCOOPTODRONEBAY]}
            if slimItem.itemID == session.shipid:
                order = [mls.UI_CMD_SHOWINFO,
                 mls.UI_CMD_EJECT,
                 [mls.UI_CMD_STOPMYSHIP, mls.UI_CMD_STOPMYCAPSULE],
                 [mls.UI_CMD_ACTIVATEAUTOPILOT, mls.UI_CMD_DEACTIVATEAUTOPILOT]] + [None,
                 None,
                 [mls.UI_CMD_LOOKAT, mls.UI_CMD_RESETCAMERA],
                 mls.UI_CMD_OPENMYCARGO]
            elif slimItem.groupID in groups:
                order += groups[slimItem.groupID]
            elif slimItem.categoryID in categories:
                order += categories[slimItem.categoryID]
            else:
                order += default
            step = 360.0 / 8
            rad = 48
            angle = 180.0
            for actionName in order:
                if actionName is None:
                    angle += step
                    i += 1
                    continue
                if type(actionName) == list:
                    action = None
                    for each in actionName:
                        tryaction = valid.get(each, None)
                        if tryaction and type(tryaction[1]) not in (str, unicode):
                            actionName = each
                            action = tryaction
                            break

                    if action is None:
                        actionName = actionName[0]
                        if actionName in valid:
                            action = valid.get(actionName)
                        elif actionName in reasonsWhyNotAvailable:
                            action = (actionName, reasonsWhyNotAvailable.get(actionName))
                        action = (actionName, mls.UI_SHARED_NOREASONGIVEN)
                elif actionName in valid:
                    action = valid.get(actionName)
                elif actionName in reasonsWhyNotAvailable:
                    action = (actionName, reasonsWhyNotAvailable.get(actionName))
                else:
                    action = (actionName, mls.UI_SHARED_NOREASONGIVEN)
                disabled = type(action[1]) in (str, unicode)
                props = self.actionMenuOptions[actionName]
                btnpar = uicls.Container(parent=self, align=uiconst.TOPLEFT, width=40, height=40, state=uiconst.UI_NORMAL)
                btnpar.left = int(rad * math.cos(angle * math.pi / 180.0)) + (self.width - btnpar.width) / 2
                btnpar.top = int(rad * math.sin(angle * math.pi / 180.0)) + (self.height - btnpar.height) / 2
                btn = uicls.Sprite(parent=btnpar, name='hudBtn', pos=(0, 0, 40, 40), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/actionMenuBtn.png')
                btnpar.actionID = actionName
                btnpar.name = actionName
                btnpar.action = action
                btnpar.itemIDs = [slimItem.itemID]
                btnpar.killsub = props[3]
                btnpar.pickRadius = -1
                icon = uicls.Icon(icon=props[0], parent=btnpar, pos=(4, 4, 0, 0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                if disabled:
                    icon.color.a = 0.5
                    btn.color.a = 0.1
                if props[4]:
                    icon = uicls.Icon(icon='ui_44_32_8', parent=btnpar, pos=(5, 5, 0, 0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                angle += step
                i += 1

            self.lastActionSerial = serial
            if self.sr.actionTimer is None:
                self.sr.actionTimer = base.AutoTimer(1000, self.Load, slimItem, None, 0)
        if centerItem:
            self.left = max(0, min(uicore.desktop.width - self.width, centerItem.absoluteLeft - (self.width - centerItem.width) / 2))
            self.top = max(0, min(uicore.desktop.height - self.height, centerItem.absoluteTop - (self.height - centerItem.height) / 2))
        elif setposition:
            self.left = max(0, min(uicore.desktop.width - self.width, uicore.uilib.x - self.width / 2))
            self.top = max(0, min(uicore.desktop.height - self.height, uicore.uilib.y - self.height / 2))



    def OnGlobalUp(self, *args):
        if not self or self.destroyed:
            return 
        if self.itemID and blue.os.TimeDiffInMs(self.expandTime, blue.os.GetTime()) < 100:
            sm.StartService('state').SetState(self.itemID, state.selected, 1)
        self.sr.actionTimer = None
        self.sr.updateAngle = None
        mo = uicore.uilib.mouseOver
        self.state = uiconst.UI_HIDDEN
        self.lastActionSerial = None
        if mo in self.children:
            uthread.new(self.OnBtnparClicked, mo)
        else:
            uicore.layer.menu.Flush()
        if not self.destroyed:
            uicore.event.UnregisterForTriuiEvents(self.mouseMoveCookie)



    def OnBtnparClicked(self, btnpar):
        sm.StartService('ui').StopBlink(btnpar)
        if btnpar.destroyed:
            uicore.layer.menu.Flush()
            return 
        if btnpar.killsub and isinstance(btnpar.action[1], list):
            uthread.new(btnpar.action[1][0][2][0][0], btnpar.action[1][0][2][0][1][0])
            uicore.layer.menu.Flush()
            return 
        if type(btnpar.action[1]) in types.StringTypes:
            sm.StartService('gameui').Say(btnpar.action[1])
        else:
            try:
                apply(*btnpar.action[1:])
            except Exception as e:
                log.LogError(e, 'Failed executing action:', btnpar.action)
                log.LogException()
                sys.exc_clear()
        uicore.layer.menu.Flush()



    def OnGlobalMove(self, *args):
        mo = uicore.uilib.mouseOver
        lib = uicore.uilib
        for c in self.children:
            c.opacity = 1.0

        if mo in self.children:
            mo.opacity = 0.7
        if not lib.leftbtn:
            self.oldx = self.oldy = None
            return 
        if self.oldx and self.oldy:
            (dx, dy,) = (self.oldx - lib.x, self.oldy - lib.y)
            camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
            if mo.name == 'blocker' and not lib.rightbtn:
                fov = camera.fieldOfView
                camera.OrbitParent(dx * fov * 0.2, -dy * fov * 0.2)
            elif lib.rightbtn:
                nav = uix.GetInflightNav(0)
                if nav:
                    nav.zoomlooking = 1
                uicore.layer.menu.Flush()
        if hasattr(self, 'oldx') and hasattr(self, 'oldy'):
            (self.oldx, self.oldy,) = (lib.x, lib.y)
        return 1



    def OnMouseWheel(self, *args):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera.__typename__ == 'EveCamera':
            camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.StartService('camera').CheckTranslationFromParent(camera.translationFromParent.z)
        return 1




class Action(uicls.Container):
    __guid__ = 'xtriui.Action'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.actionID = None
        self.Prepare_(icon=attributes.icon)



    def Prepare_(self, icon = None):
        self.icon = uicls.Icon(parent=self, align=uiconst.TOALL, icon=icon, state=uiconst.UI_DISABLED)
        self.sr.fill = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN)



    def PrepareHint(self, fromWhere = ''):
        if self and not self.destroyed:
            post = ''
            if type(self.action[1]) in types.StringTypes:
                post = ' (' + self.action[1] + ')'
            elif self.action[0] in [mls.UI_CMD_ORBIT, mls.UI_CMD_KEEPATRANGE]:
                key = sm.GetService('menu').GetGlobalActiveItemKeyName(self.action[0])
                current = sm.GetService('menu').GetDefaultActionDistance(key)
                if current is not None:
                    post = ' (%s)' % util.FmtDist(current)
                else:
                    post = ' ' + mls.UI_INFLIGHT_NODISTANCESET
            if hasattr(self, 'cmdName'):
                post += ' [%s]' % uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
            self.sr.hint = self.actionID.capitalize() + post
            return self.sr.hint



    def GetHint(self):
        return self.PrepareHint()



    def GetMenu(self):
        m = []
        if self.actionID in [mls.UI_CMD_ORBIT, mls.UI_CMD_KEEPATRANGE, sm.GetService('menu').DefaultWarpToLabel()[0]]:
            m.append((mls.UI_INFLIGHT_SETDEFAULTDIST % {'typeName': self.actionID}, self.SetDefaultDist, (self.actionID,)))
        return m



    def OnMouseEnter(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.state = uiconst.UI_DISABLED
            self.sr.fill.color.a = 0.25



    def OnMouseExit(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.state = uiconst.UI_HIDDEN



    def OnMouseDown(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.color.a = 0.5



    def OnMouseUp(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.color.a = 0.25



    def SetDefaultDist(self, forWhat):
        key = sm.GetService('menu').GetGlobalActiveItemKeyName(forWhat)
        if not key:
            return 
        (minDist, maxDist,) = {mls.UI_CMD_ORBIT: (500, 1000000),
         mls.UI_CMD_KEEPATRANGE: (50, 1000000),
         sm.GetService('menu').DefaultWarpToLabel()[0]: (const.minWarpEndDistance, const.maxWarpEndDistance)}.get(forWhat, (500, 1000000))
        current = sm.GetService('menu').GetDefaultActionDistance(key)
        current = current or ''
        hint = mls.UI_INFLIGHT_SETDEFAULTDISTHINT % {'typeName': forWhat,
         'fromDist': util.FmtAmt(minDist),
         'toDist': util.FmtAmt(maxDist)}
        r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=current, hint=hint, caption=mls.UI_SHARED_SETDEFDISTANCE % {'type': forWhat}, label=None, digits=0)
        if r:
            range = max(minDist, min(maxDist, r['qty']))
            settings.user.ui.Set('default%sDist' % key, range)
            sm.ScatterEvent('OnDistSettingsChange')



    def OnMouseMove(self, *args):
        self.PrepareHint()



    def OnClick(self, *args):
        sm.StartService('ui').StopBlink(self)
        if self.destroyed:
            uicore.layer.menu.Flush()
            return 
        if self.killsub and isinstance(self.action[1], list):
            uthread.new(self.action[1][0][2][0][0], self.action[1][0][2][0][1][0])
            uicore.layer.menu.Flush()
            return 
        if type(self.action[1]) in types.StringTypes:
            sm.StartService('gameui').Say(self.action[1])
        else:
            try:
                apply(*self.action[1:])
            except Exception as e:
                log.LogError(e, 'Failed executing action:', self.action)
                log.LogException()
                sys.exc_clear()
        uicore.layer.menu.Flush()




class MenuList(list):
    reasonsWhyNotAvailable = {}


