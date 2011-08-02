import browser
import browserutil
import corebrowserutil
import blue
import uthread
import urlparse
import uix
import form
import browserConst
import menu
import util
import base64
import log
import os
import uiconst
t = 0

def ThreadDeco(f):

    def wrapper(*args):
        global t
        dt = 0
        dt = blue.os.GetTime() - t
        t = blue.os.GetTime()
        if dt > 900 * const.MSEC:
            uthread.new(f, *args)
        else:
            eve.Message('IGBFunctionThrottling')


    return wrapper



class EveBrowserSession(browser.CoreBrowserSession):

    def AppStartup(self, sessionName, initialUrl = None, browserEventHandler = None, autoHandleLockdown = True, *args):
        self.title = mls.UI_GENERIC_UNTITLEDPAGE



    def AppCleanup(self):
        pass



    def AppGetJavascriptObjectName(self):
        return 'CCPEVE'



    def AppSetupBrowserSession(self):
        self.RegisterCommonJavascriptCallbacks()
        self.browserHostManager.AddToUserAgent('EVE-IGB')



    def AppGetHomepage(self):
        return str(settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage()))



    def AppOnBlockLoading(self, statusCode):
        sm.GetService('sites').LogInfo('Loading was blocked, code ', statusCode)
        errorString = '<html><title>%s</title><body><h1>%s</h1>' % (mls.UI_BROWSER_LOAD_ERROR, mls.UI_BROWSER_LOAD_ERROR)
        errorString += '<p>%s</p>' % corebrowserutil.GetErrorString(statusCode)
        errorString += '<p><i>%s: %i</i></p></body>' % (mls.UI_GENERIC_ERROR_CODE, statusCode)
        self.browser.LoadHTML(errorString)



    def AppOnBlockBlacklistSite(self):
        eve.Message('BrowserSiteCCPBlacklisted')



    def AppOnBlockNonWhitelistSite(self):
        eve.Message('BrowserLockdownEnabled')



    def AppOnOpenContextMenu(self, nodeType, linkUrl, imageUrl, pageUrl, frameUrl, editFlags):
        menuData = []
        eventHandlerCanTab = hasattr(self.browserEventHandler, 'AddTab')
        if nodeType & browserConst.selectedPage and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            pageUrl = str(pageUrl)
            menuData.append((mls.UI_SHARED_BROWSERBACK, self.HistoryBack, []))
            menuData.append((mls.UI_SHARED_BROWSERFORWARD, self.HistoryForward, []))
            menuData.append((mls.UI_BROWSER_RELOADPAGE, self.ReloadPage, []))
            menuData.append((mls.UI_SHARED_BROWSERSTOP, self.StopLoading, []))
            menuData.append(None)
            menuData.append((mls.UI_BROWSER_VIEWPAGESOURCE, self.ViewSourceOfUrl, [pageUrl]))
        if nodeType & browserConst.selectedFrame and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.append((mls.UI_SHARED_BROWSERBACK, self.HistoryBack, []))
            menuData.append((mls.UI_SHARED_BROWSERFORWARD, self.HistoryForward, []))
            menuData.append((mls.UI_SHARED_BROWSERSTOP, self.StopLoading, []))
            menuData.append(None)
            frameUrl = str(frameUrl)
            if eventHandlerCanTab:
                menuData.append((mls.UI_BROWSER_OPENFRAMEINNEWTAB, self.LaunchNewTab, [frameUrl]))
            menuData.append((mls.UI_BROWSER_VIEWFRAMESOURCE, self.ViewSourceOfUrl, [frameUrl]))
            menuData.append(None)
            menuData.append((mls.UI_BROWSER_VIEWPAGESOURCE, self.ViewSourceOfUrl, [pageUrl]))
        if nodeType & browserConst.selectedLink:
            if len(menuData) > 0:
                menuData.append(None)
            linkUrl = str(linkUrl)
            if not self.isViewSourceMode:
                menuData.append((mls.UI_BROWSER_OPENLINK, self.BrowseTo, [linkUrl]))
                if eventHandlerCanTab:
                    menuData.append((mls.UI_BROWSER_OPENLINKINNEWTAB, self.LaunchNewTab, [linkUrl]))
            menuData.append((mls.UI_BROWSER_COPYLINKLOCATION, self.CopyText, [linkUrl]))
        if nodeType & browserConst.selectedImage and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            imageUrl = str(imageUrl)
            menuData.append((mls.UI_BROWSER_VIEWIMAGE, self.BrowseTo, [imageUrl]))
            menuData.append((mls.UI_BROWSER_COPYIMAGELOCATION, self.CopyText, [imageUrl]))
        tempMenu = []
        if editFlags & browserConst.flagCanCut:
            tempMenu.append((mls.UI_CMD_CUT, self.PerformCommand, [browserConst.commandCut]))
        if editFlags & browserConst.flagCanCopy:
            tempMenu.append((mls.UI_CMD_COPY, self.PerformCommand, [browserConst.commandCopy]))
        if editFlags & browserConst.flagCanPaste:
            tempMenu.append((mls.UI_CMD_PASTE, self.PerformCommand, [browserConst.commandPaste]))
        if editFlags & browserConst.flagCanDelete:
            tempMenu.append((mls.UI_CMD_DELETE, self.PerformCommand, [browserConst.commandDelete]))
        if len(tempMenu) > 0:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.extend(tempMenu)
            tempMenu = []
        if editFlags & browserConst.flagCanSelectAll:
            tempMenu.append((mls.UI_CMD_SELECTALL, self.PerformCommand, [browserConst.commandSelectAll]))
        if len(tempMenu) > 0:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.extend(tempMenu)
            tempMenu = []
        if len(menuData) > 0:
            menu.KillAllMenus()
            mv = menu.CreateMenuView(menu.CreateMenuFromList(menuData), None, None)
            (x, y,) = (uicore.uilib.x + 10, uicore.uilib.y)
            (x, y,) = (min(uicore.desktop.width - mv.width, x), min(uicore.desktop.height - mv.height, y))
            (mv.left, mv.top,) = (x, y)
            uicore.layer.menu.children.insert(0, mv)



    def AddJavascriptCallbackForRestrictedFunction(self, callbackName, callbackFunction):
        if not self:
            return 
        if not hasattr(self, 'browser') or self.browser is None:
            return 
        self.browser.RegisterJavaScriptCallback(self.AppGetJavascriptObjectName(), callbackName, callbackFunction)
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'trusted')
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'CCP')
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'COMMUNITY')



    def RegisterCommonJavascriptCallbacks(self):
        self.AddJavascriptCallback('openEveMail', OpenEveMail)
        self.AddJavascriptCallback('showInfo', ShowInfo)
        self.AddJavascriptCallback('showRouteTo', self.ShowRouteTo)
        self.AddJavascriptCallback('showMap', self.ShowMap)
        self.AddJavascriptCallback('showPreview', ShowPreview)
        self.AddJavascriptCallback('showFitting', ShowFitting)
        self.AddJavascriptCallback('showContract', ShowContract)
        self.AddJavascriptCallback('showMarketDetails', ShowMarketDetails)
        self.AddJavascriptCallback('requestTrust', self.RequestTrust)
        self.AddJavascriptCallbackForRestrictedFunction('setDestination', self.SetDestination)
        self.AddJavascriptCallbackForRestrictedFunction('addWaypoint', self.AddWaypoint)
        self.AddJavascriptCallbackForRestrictedFunction('joinChannel', self.JoinChannel)
        self.AddJavascriptCallbackForRestrictedFunction('joinMailingList', self.JoinMailingList)
        self.AddJavascriptCallbackForRestrictedFunction('createContract', self.CreateContract)
        self.AddJavascriptCallbackForRestrictedFunction('sellItem', self.SellItem)
        self.AddJavascriptCallbackForRestrictedFunction('buyType', self.BuyType)
        self.AddJavascriptCallbackForRestrictedFunction('findInContracts', self.FindInContracts)
        self.AddJavascriptCallbackForRestrictedFunction('addToMarketQuickBar', self.AddToMarketQuickBar)
        self.AddJavascriptCallbackForRestrictedFunction('showContents', self.ShowContents)
        self.AddJavascriptCallbackForRestrictedFunction('addContact', self.AddContact)
        self.AddJavascriptCallbackForRestrictedFunction('addCorpContact', self.AddCorpContact)
        self.AddJavascriptCallbackForRestrictedFunction('removeContact', self.RemoveContact)
        self.AddJavascriptCallbackForRestrictedFunction('removeCorpContact', self.RemoveCorpContact)
        self.AddJavascriptCallbackForRestrictedFunction('block', self.Block)
        self.AddJavascriptCallbackForRestrictedFunction('addBounty', self.AddBounty)
        self.AddJavascriptCallbackForRestrictedFunction('inviteToFleet', self.InviteToFleet)
        self.AddJavascriptCallbackForRestrictedFunction('startConversation', self.StartConversation)
        self.AddJavascriptCallbackForRestrictedFunction('showContracts', self.ShowContracts)
        self.AddJavascriptCallbackForRestrictedFunction('showOnMap', self.ShowOnMap)
        self.AddJavascriptCallbackForRestrictedFunction('editMember', self.EditMember)
        self.AddJavascriptCallbackForRestrictedFunction('awardDecoration', self.AwardDecoration)
        self.AddJavascriptCallbackForRestrictedFunction('sendMail', self.SendMail)
        self.AddJavascriptCallbackForRestrictedFunction('bookmark', self.Bookmark)
        self.AddJavascriptCallbackForRestrictedFunction('showSovereignty', self.ShowSovereignty)
        self.AddJavascriptCallbackForRestrictedFunction('clearAllWaypoints', self.ClearAllWaypoints)



    @ThreadDeco
    def _ShowCharacter(self, charid, size):
        filename = os.path.join(blue.os.cachepath, 'Pictures/Portraits/%s_%s.png' % (charid, size))
        image = base64.b64encode(file(filename, 'rb').read())
        self.browser.BrowseTo("JavaScript:updateImage('%s')" % image)



    @ThreadDeco
    def ShowRouteTo(self, *args):
        destinationID = None
        sourceID = None
        if len(args) < 1:
            log.LogError('Insufficient arguments for CCPEVE.ShowRouteTo. You must pass in at least one argument.')
            return 
        if len(args) == 1:
            fromto = args[0].split('::')
            if len(fromto) == 2:
                destinationID = fromto[0]
                sourceID = fromto[1]
            else:
                destinationID = args[0]
        else:
            destinationID = args[0]
            sourceID = args[1]
        if eve.session.stationid:
            sm.GetService('station').CleanUp()
        destinationID = browserutil.SanitizedSolarsystemID(destinationID)
        if sourceID is not None:
            sourceID = browserutil.SanitizedSolarsystemID(sourceID)
        if destinationID is None:
            log.LogError('Error when converting destinationID in CCPEVE.ShowRouteTo. First argument must be an integer.')
            return 
        sm.GetService('map').OpenStarMap()
        sm.GetService('starmap').SetInterest(sourceID if sourceID is not None else eve.session.regionid, forceframe=1)
        sm.GetService('starmap').DrawRouteTo(destinationID, sourceID=sourceID)
        if self.browserEventHandler and hasattr(self.browserEventHandler, 'Minimize'):
            self.browserEventHandler.Minimize()



    @ThreadDeco
    def ShowMap(self, *args):
        interestID = None
        for arg in args:
            solarsystemIDs = [ ssID for ssID in arg.split('//') ]
            for ssID in solarsystemIDs:
                interestID = browserutil.SanitizedSolarsystemID(ssID)
                if interestID is not None:
                    break

            if interestID is not None:
                break

        if interestID is None:
            interestID = session.solarsystemid2
        sm.GetService('map').OpenStarMap()
        sm.GetService('starmap').SetInterest(interestID, forceframe=1)
        if self.browserEventHandler and hasattr(self.browserEventHandler, 'Minimize'):
            self.browserEventHandler.Minimize()



    @ThreadDeco
    def SetDestination(self, *args):
        destinationID = None
        for arg in args:
            destinationID = browserutil.SanitizedSolarsystemID(arg)
            if destinationID is not None:
                break

        sm.GetService('starmap').SetWaypoint(destinationID, 1)



    @ThreadDeco
    def AddWaypoint(self, *args):
        destinationIDs = []
        for arg in args:
            ssID = browserutil.SanitizedSolarsystemID(arg)
            if ssID is not None:
                destinationIDs.append(ssID)

        if len(destinationIDs) > 0:
            starMapSvc = sm.GetService('starmap')
            for destinationID in destinationIDs:
                if destinationID not in starMapSvc.GetWaypoints():
                    starMapSvc.SetWaypoint(destinationID, 0, 0)




    def RequestTrust(self, inputUrl):
        uthread.new(self._RequestTrust, inputUrl)



    def _RequestTrust(self, inputUrl):
        if not inputUrl.startswith('http://') and not inputUrl.startswith('https://'):
            log.LogError('CCPEVE.RequestTrust - Input URL must start with either http:// or https:// -- received', inputUrl)
            return 
        (scheme, netloc, path, query, fragment,) = urlparse.urlsplit(inputUrl)
        if path is None or path == '':
            path = '/'
        trustUrl = '%s://%s%s' % (scheme, netloc, path)
        if sm.GetService('sites').IsTrusted(trustUrl) or sm.GetService('sites').IsIgnored(trustUrl):
            log.LogInfo('CCPEVE.RequestTrust - Received top-level URL is already trusted or ignored:', trustUrl)
            return 
        currentUrl = self.GetCurrentURL()
        if sm.GetService('sites').IsIgnored(currentUrl):
            log.LogInfo('CCPEVE.RequestTrust - Calling URL is ignored, discarding:', currentUrl)
            return 
        wnd = sm.GetService('window').GetWindow('trustPromptWindow_%s' % netloc, maximize=1)
        if wnd:
            log.LogWarn('CCPEVE.RequestTrust - Trust prompt window was already open - skipping!')
            return 
        wnd = sm.GetService('window').GetWindow('trustPromptWindow_%s' % netloc, decoClass=form.TrustedSitePrompt, create=1, maximize=1, trustUrl=inputUrl, inputUrl=currentUrl)



    @ThreadDeco
    def JoinChannel(self, channelName):
        if channelName is None:
            return 
        channelName = channelName.strip()
        if len(channelName) > 0:
            sm.GetService('LSC').CreateOrJoinChannel(channelName, create=False)



    @ThreadDeco
    def JoinMailingList(self, mailingListName):
        if mailingListName is None:
            return 
        listName = mailingListName.strip()
        if len(listName) > 0:
            sm.GetService('mailinglists').JoinMailingList(listName)



    @ThreadDeco
    def CreateContract(self, contractType, stationID = None, itemIDs = None):
        if contractType:
            contractType = int(contractType)
        if itemIDs:
            itemIDs = [ int(i) for i in itemIDs.split(',') ]
        if stationID:
            stationID = int(stationID)
        sm.GetService('contracts').OpenCreateContractFromIGB(contractType, stationID, itemIDs)



    @ThreadDeco
    def SellItem(self, stationID, itemID):
        itemID = int(itemID)
        stationID = int(stationID)
        items = eve.GetInventory(const.containerGlobal).ListStationItems(stationID)
        for item in items:
            if item.itemID == itemID:
                sm.GetService('menu').QuickSell(item)
                return 

        log.LogError('SellItem, item', itemID, 'not found in', stationID)



    @ThreadDeco
    def BuyType(self, typeID):
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('marketutils').Buy(typeID)



    @ThreadDeco
    def FindInContracts(self, typeID):
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('contracts').FindRelated(typeID, 0, 0, 0, 0, 0, 0)



    @ThreadDeco
    def AddToMarketQuickBar(self, typeID):
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('menu').AddToQuickBar(typeID)



    @ThreadDeco
    def AddContact(self, characterID):
        characterID = ValidCharacterID(characterID)
        if characterID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                addressBookSvc.EditContacts([characterID], 'contact')
            else:
                addressBookSvc.AddToAddressBook(characterID, 'contact')



    @ThreadDeco
    def RemoveContact(self, characterID):
        characterID = ValidCharacterID(characterID)
        if characterID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                addressBookSvc.RemoveFromAddressBook([characterID], 'contact')



    @ThreadDeco
    def AddCorpContact(self, corpContactID):
        corpContactID = ValidCorpID(corpContactID)
        if corpContactID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(corpContactID, 'corpcontact'):
                addressBookSvc.EditContacts([corpContactID], 'corpcontact')
            else:
                addressBookSvc.AddToAddressBook(corpContactID, 'corpcontact')



    @ThreadDeco
    def RemoveCorpContact(self, charOrCorpID):
        charOrCorpID = ValidCorpID(charOrCorpID)
        if charOrCorpID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(charOrCorpID, 'corpcontact'):
                addressBookSvc.RemoveFromAddressBook([charOrCorpID], 'corpcontact')



    @ThreadDeco
    def Block(self, characterID):
        if eve.Message('BlockUserConfirmation', {'charName': (OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                addressBookSvc = sm.GetService('addressbook')
                if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                    addressBookSvc.BlockOwner(characterID)



    @ThreadDeco
    def AddBounty(self, characterID):
        characterID = ValidCharacterID(characterID)
        if characterID:
            uicore.cmd.OpenMissions(characterID)



    @ThreadDeco
    def InviteToFleet(self, characterID):
        if eve.Message('InviteToFleetConfirmation', {'charName': (OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                sm.GetService('menu').InviteToFleet(characterID)



    @ThreadDeco
    def StartConversation(self, characterID):
        if eve.Message('StartConversationConfirmation', {'charName': (OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                if util.IsNPC(characterID):
                    sm.GetService('agents').InteractWith(characterID)
                else:
                    sm.GetService('LSC').Invite(characterID)



    @ThreadDeco
    def ShowContracts(self, charOrCorpID):
        charOrCorpID = ValidCharacterID(charOrCorpID)
        if charOrCorpID:
            sm.GetService('contracts').Show(cfg.eveowners.Get(charOrCorpID).ownerName)



    @ThreadDeco
    def ShowOnMap(self, corpID):
        corpID = ValidCorpID(corpID)
        if corpID:
            sm.GetService('menu').ShowInMap(corpID)



    @ThreadDeco
    def EditMember(self, characterID):
        characterID = ValidCharacterID(characterID)
        if characterID:
            sm.GetService('menu').ShowCorpMemberDetails(characterID)



    @ThreadDeco
    def AwardDecoration(self, characterID):
        characterID = ValidCharacterID(characterID)
        if characterID:
            sm.GetService('menu').AwardDecoration(characterID)



    @ThreadDeco
    def SendMail(self, characterID, subject, body):
        characterID = ValidCharacterID(characterID)
        subject = ValidSubject(subject)
        body = ValidBody(body)
        if characterID and subject and body:
            sm.GetService('mailSvc').SendMsgDlg([characterID], subject=subject, body=body)



    @ThreadDeco
    def ShowContents(self, stationID, itemID):
        stationID = ValidItemID(stationID)
        itemID = ValidItemID(itemID)
        sm.GetService('menu').DoGetContainerContents(itemID, stationID, True, mls.UI_GENERIC_CONTAINER)



    @ThreadDeco
    def Bookmark(self, locationID):
        locationID = ValidLocationID(locationID)
        parentID = sm.GetService('map').GetParentLocationID(locationID, 1)
        sm.GetService('addressbook').BookmarkLocationPopup(locationID, None, parentID)



    @ThreadDeco
    def ShowSovereignty(self, ID):
        if IsConstellation(ID):
            constellationID = ID
        if IsSolarSystem(ID):
            systemID = ID
        if IsRegion(ID):
            regionID = ID
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)



    @ThreadDeco
    def ClearAllWaypoints(self):
        sm.GetService('starmap').ClearWaypoints()




def ValidTypeID(typeID):
    return int(typeID)



def ValidItemID(itemID):
    return int(itemID)



def ValidLocationID(locationID):
    return int(locationID)



def ValidCharacterID(characterID):
    return int(characterID)



def ValidCorpID(corpID):
    return int(corpID)



def ValidSubject(subject):
    return str(subject)



def ValidBody(body):
    return str(body)



@ThreadDeco
def OpenEveMail():
    sm.GetService('cmd').OpenMail()



@ThreadDeco
def ShowInfo(*args):
    typeID = None
    itemID = None
    if len(args) <= 0:
        log.LogError('CCPEVE.ShowInfo requires at least one argument!')
        return 
    if len(args) == 1:
        typeID = args[0]
        if typeID.find('//') >= 0:
            log.LogWarn('CCPEVE.ShowInfo: Old-style arguments are being passed in!')
            ids = typeID.split('//')
            typeID = ids[0]
            itemID = None
            if len(ids) > 1:
                try:
                    itemID = int(ids[1])
                except:
                    log.LogError('CCPEVE.ShowInfo failed to convert itemID in string:' + ids[1])
                    return 
    else:
        typeID = args[0]
        itemID = args[1]
    safeTypeID = browserutil.SanitizedTypeID(typeID)
    if safeTypeID is None:
        log.LogError('Type ID passed to CCPEVE.ShowInfo was invalid:', typeID)
        return 
    if itemID is not None:
        itemID = browserutil.SanitizedItemID(itemID)
    typeObj = cfg.invtypes.Get(safeTypeID)
    if typeObj.categoryID == const.categoryAbstract:
        abstractinfo = util.KeyVal()
        if typeID == const.typeCertificate:
            abstractinfo.certificateID = itemID
        sm.GetService('info').ShowInfo(safeTypeID, itemID, abstractinfo=abstractinfo)
    else:
        sm.GetService('info').ShowInfo(safeTypeID, itemID)



@ThreadDeco
def ShowPreview(typeID):
    safeTypeID = browserutil.SanitizedTypeID(int(typeID))
    if safeTypeID is None or not util.IsPreviewable(safeTypeID):
        log.LogError('Type ID passed to Client.ShowPreview was invalid:', typeID)
        return 
    sm.GetService('preview').PreviewType(safeTypeID)



@ThreadDeco
def ShowFitting(fitting):
    sm.GetService('fittingSvc').DisplayFitting(fitting)



@ThreadDeco
def ShowContract(*args):
    if len(args) < 1:
        log.LogError('CCPEVE.ShowContract received insufficient arguments. This method requires a SolarSystemID and a ContractID.')
        return 
    if len(args) == 1:
        ids = args[0].split('//')
        if len(ids) < 2:
            log.LogError('CCPEVE.ShowContract received old-style insufficient arguments. This method requires a SolarSystemID and a ContractID.')
            return 
        contractID = ids[1]
        solarSystemID = ids[0]
    else:
        contractID = args[1]
        solarSystemID = args[0]
    try:
        contractID = int(contractID)
    except:
        log.LogError('CCPEVE.ShowContract failed to convert contractID to an integer:', contractID)
        return 
    solarSystemID = browserutil.SanitizedSolarsystemID(solarSystemID)
    if contractID is None or solarSystemID is None:
        log.LogError('CCPEVE.ShowContract received invalid contract or solarsystem IDs; contractID:', contractID, 'solarSystemID:', solarSystemID)
        return 
    sm.GetService('contracts').ShowContract(contractID)



@ThreadDeco
def ShowMarketDetails(typeID):
    try:
        safeTypeID = browserutil.SanitizedTypeID(int(typeID))
    except:
        safeTypeID = None
    if safeTypeID is None:
        log.LogError('Type ID passed to Client.ShowMarketDetails was invalid:', typeID)
        return 
    sm.GetService('marketutils').ShowMarketDetails(safeTypeID, None)


exports = {'browser.BrowserSession': EveBrowserSession}

