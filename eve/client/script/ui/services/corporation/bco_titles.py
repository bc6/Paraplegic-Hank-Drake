import util
import corpObject

class TitlesO(corpObject.base):
    __guid__ = 'corpObject.titles'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.titles = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.titles = None



    def Reset(self):
        self.titles = None



    def OnTitleChanged(self, corpID, titleID, change):
        try:
            if self.titles is None:
                return 
            (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
            key = titleID
            if bAdd:
                header = None
                for example in self.titles.itervalues():
                    header = example.header
                    break

                if header is None:
                    header = change.keys()
                line = []
                for columnName in header:
                    line.append(change[columnName][1])

                title = util.Row(header, line)
                self.titles[key] = title
            elif bRemove:
                if self.titles.has_key(key):
                    del self.titles[key]
            elif self.titles.has_key(key):
                title = self.titles[key]
                for columnName in change.iterkeys():
                    setattr(title, columnName, change[columnName][1])

                self.titles[key] = title

        finally:
            sm.GetService('corpui').OnTitleChanged(corpID, titleID, change)




    def GetTitles(self, titleID = None):
        if self.titles is None:
            self.titles = {}
            titles = self.GetCorpRegistry().GetTitles()
            for title in titles.itervalues():
                key = title.titleID
                if not title.titleName:
                    if title.titleID == 1:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED1
                    elif title.titleID == 2:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED2
                    elif title.titleID == 4:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED3
                    elif title.titleID == 8:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED4
                    elif title.titleID == 16:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED5
                    elif title.titleID == 32:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED6
                    elif title.titleID == 64:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED7
                    elif title.titleID == 128:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED8
                    elif title.titleID == 256:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED9
                    elif title.titleID == 512:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED10
                    elif title.titleID == 1024:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED11
                    elif title.titleID == 2048:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED12
                    elif title.titleID == 4096:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED13
                    elif title.titleID == 8192:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED14
                    elif title.titleID == 16384:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED15
                    elif title.titleID == 32768:
                        title.titleName = mls.UI_CORP_TITLES_UNTITLED16
                self.titles[key] = title

        if titleID is None:
            res = []
            for title in self.titles.itervalues():
                if res == []:
                    res = util.Rowset(title.header)
                res.lines.append(title.line)

            return res
        else:
            key = titleID
            if self.titles.has_key(key):
                return self.titles[key]
            return []



    def UpdateTitle(self, titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther):
        self.GetCorpRegistry().UpdateTitle(titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther)



    def UpdateTitles(self, titles):
        self.GetCorpRegistry().UpdateTitles(titles)



    def DeleteTitle(self, titleID):
        self.GetCorpRegistry().DeleteTitle(titleID)




