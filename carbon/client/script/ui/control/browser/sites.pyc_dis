#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/sites.py
import cPickle
import hashlib
import blue
import service
import urlparse
import urllib
import util
import os
import log
from fnmatch import fnmatch

class SitesSvc(service.Service):
    __guid__ = 'svc.sites'
    __exportedcalls__ = {'GetBookmarks': [],
     'AddBookmark': [],
     'RemoveBookmark': [],
     'GetTrustedSites': [],
     'AddTrustedSite': [],
     'RemoveTrustedSite': [],
     'AddIgnoredSite': [],
     'IsTrusted': [],
     'IsIgnored': [],
     'OnBrowserLockdownChange': [],
     'GetBrowserWhitelist': [],
     'GetBrowserBlacklist': [],
     'GetBannedInChatList': [],
     'OnFlaggedListsChange': []}
    __notifyevents__ = ['OnBrowserLockdownChange', 'OnFlaggedListsChange']
    __dependencies__ = ['objectCaching', 'urlhistory']

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        browserSettingsPath = blue.paths.ResolvePathForWriting(u'settings:/Browser/')
        if not os.path.exists(browserSettingsPath):
            try:
                os.makedirs(browserSettingsPath)
            except OSError as e:
                self.LogError('SitesSvc.Run: Error creating the browser settings folder')

        self.isBrowserInLockdown = None
        self.bookmarksFile = browserSettingsPath + 'bookmarks.dat'
        self.trustedFile = browserSettingsPath + 'trustedSites.dat'
        self.ignoredFile = browserSettingsPath + 'ignoredSites.dat'
        self.flaggedSitesFile = blue.paths.ResolvePathForWriting(u'cache:/Browser/flaggedSites.dat')
        self.systemLists = None
        self.trustedSites = None
        self.BLACKLIST_FLAG = 1
        self.WHITELIST_FLAG = 2
        self.COMMUNITY_FLAG = 4
        self.AUTOTRUSTED_FLAG = 8
        self.LoadBookmarks()

    def Stop(self, *args):
        sm.GetService('urlhistory').SaveHistory()
        service.Service.Stop(self, args)

    def IsTrusted(self, url):
        splitUrl = urlparse.urlsplit(url)
        urlProtocol = splitUrl.scheme
        urlDomain = splitUrl.netloc
        urlPath = splitUrl.path
        trustedList = self.GetTrustedSiteList()
        for trustUrl, trustData in trustedList.iteritems():
            if trustData.trusted and self.Matches(trustData.protocol, trustData.hostname, trustData.path, urlProtocol, urlDomain, urlPath):
                return True

        return False

    def Matches(self, trustProtocol, trustDomain, trustPath, urlProtocol, urlDomain, urlPath):
        if trustProtocol and trustProtocol != urlProtocol:
            return False
        if not fnmatch(urlPath, trustPath):
            return False
        if not fnmatch(urlDomain, trustDomain):
            if not (trustDomain.startswith('*.') and fnmatch(urlDomain, trustDomain[2:])):
                return False
        return True

    def IsIgnored(self, url):
        splitUrl = urlparse.urlsplit(url)
        urlProtocol = splitUrl.scheme
        urlDomain = splitUrl.hostname
        urlPath = splitUrl.path
        trustedList = self.GetTrustedSiteList()
        for trustUrl, trustData in trustedList.iteritems():
            if trustData.trusted == 0 and self.Matches(trustData.protocol, trustData.hostname, trustData.path, urlProtocol, urlDomain, urlPath):
                return True

        return False

    def SaveSiteList(self, fileName, siteList):
        f = blue.ResFile()
        try:
            f.Create(fileName)
            f.Write(cPickle.dumps(siteList))
            f.Close()
        except:
            self.LogError('SitesSvc.SaveSiteList: Error saving to ', fileName)

    def GetBookmarks(self):
        return self.bookmarkedSites

    def MakeBookmarkEntry(self, name, url):
        return util.KeyVal(name=name, url=url)

    def RemoveBookmark(self, urlKV):
        self.bookmarkedSites.remove(urlKV)
        self.SaveBookmarks()

    def AddBookmark(self, name, url):
        self.bookmarkedSites.append(self.MakeBookmarkEntry(name, url))
        self.SaveBookmarks()

    def EditBookmark(self, oldEntry, name, url):
        for each in self.bookmarkedSites:
            if each == oldEntry:
                oldEntry.name = name
                oldEntry.url = url

        self.SaveBookmarks()

    def LoadBookmarks(self):
        self.bookmarkedSites = None
        f = blue.ResFile()
        if f.Open(self.bookmarksFile):
            self.bookmarkedSites = cPickle.loads(f.Read())
            f.Close()
        if not self.bookmarkedSites:
            self.bookmarkedSites = []

    def SaveBookmarks(self):
        self.SaveSiteList(self.bookmarksFile, self.bookmarkedSites)

    def ReformatUrlForTrustList(self, url):
        if not url:
            return None
        splitUrl = urlparse.urlsplit(url)
        cleanedUrl = ''
        scheme = urllib.quote(splitUrl.scheme.strip())
        if scheme == 'http' or scheme == 'https':
            cleanedUrl = '%s://' % scheme
        elif scheme:
            return None
        netloc = splitUrl.netloc.strip()
        try:
            netloc = str(netloc)
        except UnicodeEncodeError:
            netloc = urllib.quote(netloc, safe=':@*')

        path = splitUrl.path.strip()
        path = urllib.quote(path, safe='/*')
        if netloc == '' and path != '':
            if path.startswith('.'):
                cleanedUrl += '*'
            cleanedUrl += path
            if not cleanedUrl.endswith('/') and not cleanedUrl.endswith('/*'):
                cleanedUrl += '/'
        else:
            if netloc.startswith('.'):
                cleanedUrl += '*'
            cleanedUrl += netloc
            if path == '':
                cleanedUrl += '/'
            else:
                cleanedUrl += path
        if cleanedUrl.endswith('/'):
            cleanedUrl += '*'
        return cleanedUrl

    def GetTrustedSites(self):
        trusted = {}
        trustedList = self.GetTrustedSiteList()
        for site, siteData in trustedList.iteritems():
            if siteData.trusted:
                trusted[site] = siteData

        return trusted

    def GetIgnoredSites(self):
        ignored = {}
        trustedList = self.GetTrustedSiteList()
        for site, siteData in trustedList.iteritems():
            if not siteData.trusted:
                ignored[site] = siteData

        return ignored

    def AddTrustedSite(self, s, store = 1):
        if not s:
            return
        s = self.ReformatUrlForTrustList(s)
        if s is None:
            raise UserError('CannotTrustInvalidUrl')
        temp_s = s
        checkProtocol = True
        if s.find('://') == -1:
            temp_s = 'http://' + s
            checkProtocol = False
        splitUrl = urlparse.urlsplit(temp_s)
        for trustUrl, trustData in self.trustedSites.iteritems():
            if trustData.auto and self.Matches(trustData.protocol, trustData.hostname, trustData.path, splitUrl.scheme, splitUrl.netloc, splitUrl.path):
                raise UserError('CannotTrustCCPTrusted')

        val = self.GetSiteKey()
        val.trusted = 1
        val.temporary = store ^ 1
        val.protocol = splitUrl.scheme if checkProtocol else ''
        val.hostname = splitUrl.netloc
        val.path = splitUrl.path
        self.trustedSites[s] = val
        sm.ScatterEvent('OnTrustedSitesChange')
        if store:
            self.SaveTrusted()

    def RemoveTrustedSite(self, s):
        if s in self.trustedSites:
            if self.trustedSites[s].auto:
                return
            del self.trustedSites[s]
            self.SaveTrusted()
            sm.ScatterEvent('OnTrustedSitesChange')

    def ToggleTrust(self, s):
        if s in self.trustedSites:
            self.trustedSites[s].trusted ^= 1
            sm.ScatterEvent('OnTrustedSitesChange')
            self.SaveTrusted()

    def AddIgnoredSite(self, s):
        if not s:
            return
        s = self.ReformatUrlForTrustList(s)
        if not s:
            raise UserError('CannotTrustInvalidUrl')
        splitUrl = urlparse.urlsplit(s)
        for trustUrl, trustData in self.trustedSites.iteritems():
            if trustData.auto and self.Matches(trustData.protocol, trustData.hostname, trustData.path, splitUrl.scheme, splitUrl.netloc, splitUrl.path):
                raise UserError('CannotIgnoreCCPTrusted')

        val = self.GetSiteKey()
        val.protocol = splitUrl.scheme
        val.hostname = splitUrl.netloc
        val.path = splitUrl.path
        self.trustedSites[s] = val
        self.SaveTrusted()
        sm.ScatterEvent('OnTrustedSitesChange')

    def GetSiteKey(self):
        return util.KeyVal(trusted=0, temporary=0, auto=0, community=0, protocol='', hostname='', path='')

    def GetTrustedSiteList(self):
        if self.trustedSites is None:
            ret = {}
            trusted = []
            ignored = []
            f = blue.ResFile()
            if f.Open(self.trustedFile):
                trusted = cPickle.loads(f.Read())
                f.Close()
            if f.Open(self.ignoredFile):
                ignored = cPickle.loads(f.Read())
                f.Close()

            def SplitSiteURL(key):
                checkProtocol = True
                if key.find('://') == -1:
                    key = 'http://' + key
                    checkProtocol = False
                splitUrl = urlparse.urlsplit(key)
                protocol = splitUrl.scheme if checkProtocol else ''
                return (protocol, splitUrl.netloc, splitUrl.path)

            for key in self.GetAutoTrustedSites():
                val = self.GetSiteKey()
                val.trusted = 1
                val.auto = 1
                val.protocol, val.hostname, val.path = SplitSiteURL(key)
                ret[key] = val

            for key in self.GetCommunitySites():
                if key in ret:
                    self.LogWarn('GetTrustedSiteList: Skipping community Autosite because it was already listed as a CCP site', key)
                    continue
                val = self.GetSiteKey()
                val.trusted = 1
                val.auto = 1
                val.community = 1
                val.protocol, val.hostname, val.path = SplitSiteURL(key)
                ret[key] = val

            for key in trusted:
                if key in ret:
                    self.LogWarn('GetTrustedSiteList: Skipping user-trusted site because it was already listed as a CCP site', key)
                    continue
                cleanedUrl = self.ReformatUrlForTrustList(key)
                if cleanedUrl is None:
                    self.LogInfo('SitesSvc.LoadTrusted rejecting trusted url', key, 'due to failed sanitization')
                    continue
                if cleanedUrl not in ret:
                    val = self.GetSiteKey()
                    val.trusted = 1
                    val.protocol, val.hostname, val.path = SplitSiteURL(key)
                    ret[cleanedUrl] = val

            for key in ignored:
                if key in ret:
                    self.LogWarn('GetTrustedSiteList: Skipping user-trusted site because it was already listed as a CCP or user-trusted site', key)
                    continue
                cleanedUrl = self.ReformatUrlForTrustList(key)
                if cleanedUrl is None:
                    self.LogInfo('SitesSvc.LoadTrusted rejecting ignored url', key, 'due to failed sanitization')
                    continue
                if cleanedUrl not in ret:
                    val = self.GetSiteKey()
                    val.protocol, val.hostname, val.path = SplitSiteURL(key)
                    ret[cleanedUrl] = val

            self.trustedSites = ret
        return self.trustedSites

    def SaveTrusted(self):
        trustedList = self.GetTrustedSiteList()
        trusted = [ key for key, value in trustedList.iteritems() if value.auto == 0 and value.temporary == 0 and value.trusted == 1 ]
        ignored = [ key for key, value in trustedList.iteritems() if value.auto == 0 and value.temporary == 0 and value.trusted == 0 ]
        f = blue.ResFile()
        self.SaveSiteList(self.trustedFile, trusted)
        self.SaveSiteList(self.ignoredFile, ignored)

    def GetDefaultHomePage(self):
        return sm.RemoteSvc('browserLockdownSvc').GetDefaultHomePage()

    def IsBrowserInLockdown(self):
        if self.isBrowserInLockdown is None:
            self.isBrowserInLockdown = sm.RemoteSvc('browserLockdownSvc').IsBrowserInLockdown()
        return self.isBrowserInLockdown

    def OnBrowserLockdownChange(self, newValue):
        self.isBrowserInLockdown = newValue
        self.objectCaching.InvalidateCachedMethodCall('browserLockdownSvc', 'IsBrowserInLockdown')
        sm.ScatterEvent('OnClientBrowserLockdownChange')

    def GetBrowserBlacklist(self):
        if self.systemLists is None:
            self.__PopulateSystemLists()
        if self.systemLists is None:
            return []
        return self.systemLists.blacklist

    def GetBannedInChatList(self):
        if self.systemLists is None:
            self.__PopulateSystemLists()
        if self.systemLists is None:
            return []
        return self.systemLists.bannedInChat

    def GetBrowserWhitelist(self):
        if self.systemLists is None:
            self.__PopulateSystemLists()
        if self.systemLists is None:
            return []
        return self.systemLists.whitelist

    def GetCommunitySites(self):
        if self.systemLists is None:
            self.__PopulateSystemLists()
        if self.systemLists is None:
            return []
        return self.systemLists.community

    def GetAutoTrustedSites(self):
        if self.systemLists is None:
            self.__PopulateSystemLists()
        if self.systemLists is None:
            return []
        return self.systemLists.autotrusted

    def __PopulateSystemLists(self):
        flaggedSites = []
        try:
            f = blue.ResFile()
            if f.Open(self.flaggedSitesFile):
                flaggedSites = cPickle.loads(f.Read())
        except:
            log.LogException('Error reading file from disk')
        finally:
            f.Close()

        try:
            m = hashlib.md5()
            m.update(str(flaggedSites))
            if m.hexdigest() != sm.RemoteSvc('browserLockdownSvc').GetFlaggedSitesHash():
                self.LogInfo('FlaggedSites: Download full list from server')
                flaggedSites = sm.RemoteSvc('browserLockdownSvc').GetFlaggedSitesList()
                try:
                    f = blue.ResFile()
                    f.Create(self.flaggedSitesFile)
                    f.Write(cPickle.dumps(flaggedSites))
                except:
                    log.LogException('Error writing flaggedSites list to disk')
                finally:
                    f.Close()

        except:
            log.LogException('Error connecting to database')
            return

        self.systemLists = util.KeyVal(blacklist=[], bannedInChat=[], whitelist=['about:blank'], community=[], autotrusted=[])

        def GetDomainOnly(uStr):
            if uStr.find(u'//') != -1:
                uStr = uStr.split(u'//')[1]
            if uStr.startswith(u'*'):
                uStr = uStr[1:]
            if uStr.startswith(u'.'):
                uStr = uStr[1:]
            if uStr.endswith(u'/*'):
                uStr = uStr[:-2]
            return uStr

        for flaggedSiteRow in flaggedSites:
            if flaggedSiteRow['siteFlag'] & self.BLACKLIST_FLAG:
                self.systemLists.blacklist.append(flaggedSiteRow['siteUrl'])
                uStr = GetDomainOnly(unicode(flaggedSiteRow['siteUrl'])).strip()
                if uStr:
                    self.systemLists.bannedInChat.append(uStr)
            if flaggedSiteRow['siteFlag'] & self.WHITELIST_FLAG:
                self.systemLists.whitelist.append(flaggedSiteRow['siteUrl'])
            if flaggedSiteRow['siteFlag'] & self.COMMUNITY_FLAG:
                self.systemLists.community.append(flaggedSiteRow['siteUrl'])
            if flaggedSiteRow['siteFlag'] & self.AUTOTRUSTED_FLAG:
                self.systemLists.autotrusted.append(flaggedSiteRow['siteUrl'])

    def OnFlaggedListsChange(self):
        self.objectCaching.InvalidateCachedMethodCall('browserLockdownSvc', 'GetFlaggedSitesList')
        self.objectCaching.InvalidateCachedMethodCall('browserLockdownSvc', 'GetFlaggedSitesHash')
        self.systemLists = None
        self.trustedSites = None
        sm.ScatterEvent('OnClientFlaggedListsChange')


exports = {'svc.sites': SitesSvc}