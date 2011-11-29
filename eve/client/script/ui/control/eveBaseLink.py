import uicls
import util
import log
import blue
import browserutil
import localization
import form
import uiconst
import uiutil
HINTLABELS = {'showinfo': localization.GetByLabel('UI/Commands/ShowInfo'),
 'contract': localization.GetByLabel('UI/Contracts/ShowContract'),
 'note': localization.GetByLabel('UI/Notepad/ShowNote'),
 'fleet': localization.GetByLabel('UI/Fleet/ClickToJoinFleet'),
 'localsvc': None,
 'showrouteto': localization.GetByLabel('UI/Map/Navigation/ShowRoute'),
 'fitting': localization.GetByLabel('UI/Fitting/ShowFitting'),
 'preview': localization.GetByLabel('UI/Preview/Preview'),
 'CertSlot': localization.GetByLabel('UI/Certificates/PlannerWindow/OpenCertificationPlanner')}

class BaseLink(uicls.BaseLinkCore):
    __guid__ = 'uicls.BaseLink'

    def ClickGameLinks(self, parent, URL):
        if URL.startswith('eve:/'):
            self.GetFromCluster(parent, URL)
            return True
        if URL.startswith('showinfo:'):
            self.ShowInfo(URL[9:])
            return True
        if URL.startswith('showrouteto:'):
            self.ShowRouteTo(URL[12:])
            return True
        if URL.startswith('showinmap:'):
            self.ShowInMap(URL[10:])
            return True
        if URL.startswith('cmd:/'):
            sm.GetService('slash').SlashCmd(URL[4:])
            return True
        if URL.startswith('evebrowser:'):
            uicore.cmd.OpenBrowser(URL[11:])
            return True
        if URL.startswith('evemail:'):
            self.EveMail(URL[8:])
            return True
        if URL.startswith('evemailto:'):
            self.EveMail(URL[10:])
            return True
        if URL.startswith('note:'):
            self.Note(URL[5:])
            return True
        if URL.startswith('fleetmission:'):
            self.FleetMission(URL[13:])
            return True
        if URL.startswith('contract:'):
            self.Contract(URL[9:])
            return True
        if URL.startswith('fleet:'):
            self.AskJoinFleet(URL[6:])
            return True
        if URL.startswith('CertSlot:'):
            sm.StartService('certificates').OpenCertificateWindow(URL[9:])
            return True
        if URL.startswith('fleetmenu:'):
            self.FleetMenu(URL[len('fleetmenu:'):])
            return True
        if URL.startswith('celestialmenu:'):
            self.CelestialMenu(URL[len('celestialmenu:'):])
            return True
        if URL.startswith('fitting:'):
            sm.StartService('fittingSvc').DisplayFitting(URL[len('fitting:'):])
            return True
        if URL.startswith('preview:'):
            sm.GetService('preview').PreviewType(URL[len('preview:'):])
            return True
        return False



    def CanOpenBrowser(self, *args):
        return getattr(eve.session, 'charid', None)



    def GetLinkMenu(self, parent, url):
        m = []
        if url.startswith('showinfo:'):
            ids = url[9:].split('//')
            try:
                typeID = int(ids[0])
                itemID = None
                bookmark = None
                filterFunc = None
                if len(ids) > 1:
                    itemID = int(ids[1])
                if len(ids) > 2:
                    invtype = cfg.invtypes.Get(typeID)
                    if invtype.categoryID == const.categoryBlueprint:
                        filterFunc = {localization.GetByLabel('UI/Commands/ShowInfo')}
                    else:
                        bookmark = self.GetBookmark(ids, itemID, typeID)
                m += sm.GetService('menu').GetMenuFormItemIDTypeID(itemID, typeID, bookmark, ignoreMarketDetails=0, filterFunc=filterFunc)
                m += sm.GetService('menu').GetGMTypeMenu(typeID, divs=True)
                for item in m:
                    if item is not None:
                        if item[0] == localization.GetByLabel('UI/Inventory/ItemActions/SetNewPasswordForContainer'):
                            m.remove(item)

            except:
                log.LogTraceback('failed to convert string to ids in Browser:ShowInfo')
                return []
        elif url.startswith('preview:'):
            return []
        if url.startswith('contract:'):
            m += [(localization.GetByLabel('UI/Contracts/ShowContract'), self.Contract, (url[9:],))]
            return m
        if url.startswith('CertSlot:'):
            m += [(localization.GetByLabel('UI/Commands/OpenCertificatePlanner'), sm.StartService('certificates').OpenCertificateWindow, (url[9:],))]
            return m
        if self.ValidateURL(url):
            url = url.replace('&amp;', '&')
            url = browserutil.GetFixedURL(parent, url)
            m += [(localization.GetByLabel('UI/Browser/OpenLinkInNewTab'), self.UrlHandlerDelegate, (parent,
               'NewView',
               url,
               True))]
            m += [(localization.GetByLabel('UI/Common/Open'), self.UrlHandlerDelegate, (parent,
               'GoTo',
               url,
               False))]
        if url.lower().startswith('http'):
            m += [(localization.GetByLabel('/Carbon/UI/Commands/CopyURL'), self.CopyUrl, (url,))]
        return m



    def GetStandardLinkHint(self, url):
        if url.startswith('showinfo'):
            parsedArgs = uicls.BaseLink().ParseShowInfo(url[9:])
            if not parsedArgs:
                return localization.GetByLabel('UI/Commands/ShowInfo')
            (typeID, itemID, data,) = parsedArgs
            return localization.GetByLabel('UI/Common/ShowTypeInfo', groupName=cfg.invtypes.Get(typeID).Group().name)
        for (k, v,) in HINTLABELS.iteritems():
            if url.startswith('%s:' % k):
                return v




    def GetLinkFormat(self, url, linkState = None, linkStyle = None):
        linkState = linkState or uiconst.LINK_IDLE
        linkStyle = linkStyle or uiconst.LINKSTYLE_REGULAR
        fmt = uiutil.Bunch()
        if linkStyle == uiconst.LINKSTYLE_SUBTLE:
            if linkState in (uiconst.LINK_ACTIVE, uiconst.LINK_HOVER):
                fmt.color = -256
            elif linkState in (uiconst.LINK_IDLE, uiconst.LINK_DISABLED):
                if url.startswith('showinfo'):
                    pass
                elif url.startswith('http'):
                    fmt.color = -23040
                else:
                    fmt.color = -552162
        elif linkState in (uiconst.LINK_ACTIVE, uiconst.LINK_HOVER):
            fmt.color = -256
            fmt.underline = True
        elif linkState in (uiconst.LINK_IDLE, uiconst.LINK_DISABLED):
            if url.startswith('showinfo'):
                fmt.color = -23040
            elif url.startswith('http'):
                fmt.color = -23040
            else:
                fmt.color = -552162
        fmt.bold = True
        return fmt



    def GetBookmark(self, ids, itemID, typeID):
        (x, y, z, agentIDString, locationNumber, locationType,) = (float(ids[2]),
         float(ids[3]),
         float(ids[4]),
         ids[5],
         int(ids[6]),
         ids[7])
        agentIDList = [ int(s) for s in agentIDString.split(',') ]
        bookmark = util.KeyVal()
        bookmark.ownerID = eve.session.charid
        bookmark.itemID = itemID
        bookmark.typeID = typeID
        bookmark.flag = None
        bookmark.memo = ''
        bookmark.created = blue.os.GetWallclockTime()
        bookmark.x = x
        bookmark.y = y
        bookmark.z = z
        bookmark.locationID = itemID
        bookmark.agentID = agentIDList[0]
        bookmark.referringAgentID = agentIDList[1] if len(agentIDList) == 2 else None
        bookmark.locationNumber = locationNumber
        bookmark.locationType = locationType
        if bookmark.locationType == 'dungeon' or bookmark.locationType == 'agenthomebase':
            bookmark.deadspace = 1
        return bookmark



    def GetBadUrls(self, *args):
        return ['shellexec:',
         'eve:/',
         'localsvc:',
         'showinfo:',
         'showrouteto:',
         'showinmap:',
         'cmd:/',
         'evemail:',
         'evemailto:',
         'note:',
         'contract:',
         'evebrowser:']



    def UrlHandlerDelegate(self, parent, funcName, args, newTab = False):
        handler = getattr(self, 'URLHandler', None)
        if not handler and getattr(parent, 'sr', None) and getattr(parent.sr, 'node', None):
            handler = getattr(parent.sr.node, 'URLHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                apply(func, (args,))
                return 
        if not args.startswith('http'):
            self.ClickGameLinks(parent, args)
        else:
            uicore.cmd.OpenBrowser(args, newTab=newTab)



    def GetFromCluster(self, parent, url):
        (proto, servicename, action,) = url.split('/')
        html = sm.RemoteSvc(servicename).Request(action)
        parent.sr.browser.LoadHTML(html)



    def Note(self, noteID):
        noteWindow = form.Notepad.Open()
        noteWindow.ShowNote(noteID)



    def FleetMission(self, args):
        ids = args.split('//')
        try:
            agentID = int(ids[0])
            charID = int(ids[1])
        except:
            log.LogError('failed to convert string to ids in Browser:Mission. Args:', args)
            return 
        sm.GetService('agents').PopupMissionJournal(agentID, charID)



    def Contract(self, args):
        ids = args.split('//')
        try:
            contractID = int(ids[1])
            solarSystemID = int(ids[0])
        except:
            log.LogError('failed to convert string to ids in Browser:ShowInfo. Args:', args)
            return 
        sm.GetService('contracts').ShowContract(contractID)



    def AskJoinFleet(self, args):
        try:
            fleetID = int(args)
        except:
            log.LogError('failed to convert string to ids in Browser:AskJoinFleet. Args:', args)
            return 
        sm.GetService('fleet').AskJoinFleetFromLink(fleetID)



    def EveMail(self, url):
        receivers = []
        subject = None
        body = None
        if url.find('::') != -1:
            (r, s, m,) = url.split('::')
            receivers = [r]
            subject = s
            body = m.replace('\r', '').replace('\n', '<br>')
        else:
            receivers = [url]
        sm.GetService('mailSvc').SendMsgDlg(toCharacterIDs=receivers, subject=subject, body=body)



    def ParseShowInfo(self, args):
        if args.startswith('showinfo:'):
            args = args[9:]
        ids = args.split('//')
        try:
            typeID = int(ids[0])
            itemID = None
            data = None
            if len(ids) > 1:
                itemID = int(ids[1])
            if len(ids) > 2:
                data = ids[2:]
            return (typeID, itemID, data)
        except:
            log.LogError('failed to convert string to ids in Browser:ShowInfo. Args:', args)
            return 



    def ShowInfo(self, args):
        parsedArgs = self.ParseShowInfo(args)
        if not parsedArgs:
            return 
        (typeID, itemID, data,) = parsedArgs
        typeObj = cfg.invtypes.Get(typeID)
        if typeObj.categoryID == const.categoryAbstract:
            abstractinfo = util.KeyVal()
            if typeID == const.typeCertificate:
                abstractinfo.certificateID = itemID
            sm.GetService('info').ShowInfo(typeID, itemID, abstractinfo=abstractinfo)
        elif typeObj.categoryID == const.categoryBlueprint and data:
            try:
                (copy, runs, material, productivity,) = data
                abstractinfo = util.KeyVal(categoryID=const.categoryBlueprint, runs=int(runs), isCopy=bool(int(copy)), productivityLevel=int(productivity), materialLevel=int(material))
                if itemID == 0:
                    itemID = None
                sm.GetService('info').ShowInfo(typeID, itemID, abstractinfo=abstractinfo)
            except:
                log.LogInfo('Could not convert blueprint extra data to valid parameters', data)
        else:
            sm.GetService('info').ShowInfo(typeID, itemID)



    def ShowInMap(self, args):
        try:
            solarsystemIDs = [ int(ssID) for ssID in args.split('//') ]
        except:
            log.LogError('failed to convert string to ids in Browser:ShowInMap. Args:', args)
            return 
        sm.GetService('viewState').ActivateView('starmap', interestID=solarsystemIDs[0])



    def ShowRouteTo(self, args):
        fromto = args.split('::')
        if len(fromto) not in (1, 2):
            log.LogError('failed to convert string to id in Browser:ShowRouteTo. Args:', args)
            return 
        for i in fromto:
            try:
                id = int(i)
            except:
                log.LogError('failed to convert string to id in Browser:ShowRouteTo. Args:', args)
                return 

        if eve.session.stationid:
            sm.GetService('station').CleanUp()
        destinationID = int(fromto[0])
        sourceID = None
        if len(fromto) == 2:
            sourceID = int(fromto[1])
        sm.GetService('viewState').ActivateView('starmap', interestID=sourceID or session.regionid, drawRoute=(sourceID, destinationID))



    def FleetMenu(self, text):
        self.menu = sm.GetService('menu').FleetMenu(int(text))
        self.menu.ShowMenu(self)



    def CelestialMenu(self, text):
        self.menu = sm.GetService('menu').CelestialMenu(int(text))
        self.menu.ShowMenu(self)




