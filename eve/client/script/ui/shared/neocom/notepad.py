import service
import blue
import uthread
import uix
import uiutil
import xtriui
import util
import form
import listentry
import base
import dbg
import uicls
import uiconst

class NotepadSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'ShowNote': [],
     'NewFolder': [],
     'RemoveFolder': [],
     'GetNotes': [],
     'AddNote': [],
     'DeleteNote': [],
     'RenameNote': [],
     'GetSetting': [],
     'SetSetting': [],
     'WriteNote': [],
     'GetNotesByType': [],
     'GetFolders': [],
     'GetNoteText': []}
    __guid__ = 'svc.notepad'
    __notifyevents__ = []
    __servicename__ = 'notepad'
    __displayname__ = 'Notepad Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.starting = 1
        self.LogInfo('Starting Notepad')
        self.Reset()
        notes = sm.RemoteSvc('charMgr').GetOwnerNoteLabels()
        folders = []
        self.folderIDs = []
        badNotes = [ note for note in notes if note.label[0] not in ('I', 'B', 'N', 'S') ]
        bms = sm.GetService('addressbook').GetBookmarks()
        for entry in notes:
            if entry.label[0] in ('I', 'B', 'N') and entry.label[1] == ':':
                n = util.KeyVal()
                n.noteID = entry.noteID
                n.text = None
                if entry.label[0] == 'N':
                    n.label = entry.label[2:]
                    self.notes['N:' + str(entry.noteID)] = n
                elif entry.label[0] == 'B':
                    n.bookmarkID = entry.label[2:]
                    if int(n.bookmarkID) in bms:
                        self.bookmarknotes['B:' + str(n.bookmarkID)] = n
                    else:
                        badNotes.append(entry)
            if entry.label.startswith('S:'):
                label = entry.label[2:]
                if self.settings.has_key(label):
                    self.settings[label].append(entry.noteID)
                else:
                    self.settings[label] = [entry.noteID]

        parallelCalls = []
        for note in badNotes:
            parallelCalls.append((sm.RemoteSvc('charMgr').RemoveOwnerNote, (note.noteID,)))

        if len(parallelCalls):
            uthread.parallel(parallelCalls)
        folders = self.GetSetting('Folders')
        if folders is not None:
            for entry in folders.split('|'):
                tmp = entry.split('::')
                if len(tmp) != 4:
                    continue
                (id, type, parentID, label,) = tmp
                n = util.KeyVal()
                n.type = type
                if parentID == 'None':
                    parentID = 0
                n.parent = int(parentID)
                n.data = label
                self.folders[int(id)] = n
                self.lastid = max(self.lastid, int(id))

        else:
            n = util.KeyVal()
            n.type = 'F'
            n.parent = 0
            n.data = mls.UI_GENERIC_MAIN
            self.folders[1] = n
            self.lastid = 1
        self.starting = 0



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.CloseX()
        self.Reset()



    def Reset(self):
        self.bms = None
        self.folders = {}
        self.notes = {}
        self.bookmarknotes = {}
        self.charnotes = {}
        self.settings = {}
        self.settingStrs = {}
        self.notedata = {}
        self.lastid = 0



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def GetWnd(self, new = 0):
        wnd = sm.GetService('window').GetWindow('notepad')
        if not wnd and new:
            wnd = sm.GetService('window').GetWindow('notepad', create=1, decoClass=form.Notepad)
            wnd.OnClose_ = self.OnCloseWnd
            wnd.SetCaption(mls.UI_SHARED_NOTEPAD)
            wnd.SetWndIcon('ui_49_64_2')
            wnd.SetTopparentHeight(0)
            wnd.HideMainIcon()
            wnd.sr.hint = None
            wnd.sr.main.left = wnd.sr.main.top = wnd.sr.main.width = wnd.sr.main.height = const.defaultPadding
            wnd.sr.nav = uicls.Container(name='nav', align=uiconst.TOLEFT, width=settings.user.ui.Get('notepadscrollistwidth', 128), parent=wnd.sr.main, idx=0)
            divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, idx=1, width=const.defaultPadding, parent=wnd.sr.main, state=uiconst.UI_NORMAL)
            divider.Startup(wnd.sr.nav, 'width', 'x', 100, 256)
            wnd.sr.navbuttons = uicls.Container(name='navbuttons', align=uiconst.TOBOTTOM, parent=wnd.sr.nav, height=38)
            wnd.sr.newfolder = uicls.Button(parent=wnd.sr.navbuttons, label=mls.UI_CMD_NEWFOLDER, padTop=4, align=uiconst.TOTOP, func=self.NewFolderClick)
            wnd.sr.newnote = uicls.Button(parent=wnd.sr.navbuttons, label=mls.UI_CMD_NEWNOTE, padTop=4, align=uiconst.TOTOP, func=self.NewNote, args=(0,))
            wnd.sr.navbuttons.height = sum([ each.height + each.padTop + each.padBottom for each in wnd.sr.navbuttons.children ]) + 4
            wnd.sr.senderlist = uicls.Scroll(name='senderlist', parent=wnd.sr.nav)
            wnd.sr.senderlist.OnDelete = self.OnDelete
            wnd.sr.senderlist.multiSelect = 0
            wnd.sr.note = uicls.Container(name='notecontainer', align=uiconst.TOALL, parent=wnd.sr.main, pos=(0, 0, 0, 0))
            wnd.SetMinSize((256, 128))
            wnd.sr.titlecont = uicls.Container(name='titlecontainer', align=uiconst.TOTOP, height=48, parent=wnd.sr.note)
            uicls.Frame(parent=wnd.sr.titlecont, padBottom=const.defaultPadding)
            uicls.Container(name='push', align=uiconst.TORIGHT, width=7, parent=wnd.sr.titlecont)
            uicls.Container(name='push', align=uiconst.TOTOP, height=9, parent=wnd.sr.titlecont)
            wnd.sr.icon = uicls.Icon(parent=wnd.sr.titlecont, pos=(7, 7, 32, 32))
            wnd.sr.titletext = uicls.Label(text='', parent=wnd.sr.titlecont, align=uiconst.TOALL, left=46, autowidth=False, autoheight=False)
            wnd.sr.browser = uicls.EditPlainText(parent=wnd.sr.note, showattributepanel=1)
            wnd.sr.browser.sr.window = self
            wnd.sr.browser.allowPrivateDrops = 1
            wnd.OnScale_ = self._OnResize
            divider.OnSizeChanging = self.OnDividerMove
            wnd.CloseX = self.AskClose
            self.LoadNotes()
            wnd.sr.autosaveTimer = base.AutoTimer(60000, self.SaveNote)
            self.activeNode = None
            self.ShowNote(settings.char.notepad.Get('activeNote', None))
        return wnd



    def AskClose(self, *args):
        notepadWnd = self.GetWnd(new=0)
        uicls.WindowCore._CloseClick(notepadWnd)



    def OnCloseWnd(self, wnd, *args):
        self.SaveNote()
        settings.user.ui.Set('notepadscrollistwidth', wnd.sr.nav.width)
        wnd.OnClose_ = None
        wnd.sr.main = None
        wnd.sr.browser = None
        wnd.sr.senderlist = None
        wnd = None
        folderstr = ''
        folderIDs = self.folderIDs[:]
        for (key, value,) in self.folders.items():
            folderstr += '%s::%s::%s::%s|' % (key,
             value.type,
             value.parent,
             value.data)

        uthread.new(self.SetSetting, 'Folders', folderstr)



    def SetSetting(self, id, string):
        if self.settingStrs.has_key(id) and self.settingStrs[id] == string:
            return 
        if self.settings.has_key(id):
            dbIDs = self.settings[id]
            dbIDs.sort()
        else:
            dbIDs = []
        idStr = 'S:' + str(id)
        newIDs = []
        while len(string) > 0:
            part = string[:6000]
            string = string[6000:]
            if len(dbIDs):
                noteID = int(dbIDs.pop(0))
                sm.RemoteSvc('charMgr').EditOwnerNote(noteID, idStr, part)
            else:
                noteID = sm.RemoteSvc('charMgr').AddOwnerNote(idStr, part)
            newIDs.append(noteID)

        parallelCalls = []
        for noteID in dbIDs:
            parallelCalls.append((sm.RemoteSvc('charMgr').RemoveOwnerNote, (int(noteID),)))

        if len(parallelCalls):
            uthread.parallel(parallelCalls)
        self.settings[id] = newIDs



    def GetSetting(self, id):
        if self.settingStrs.has_key(id):
            return self.settingStrs[id]
        if not self.settings.has_key(id):
            return None
        parallelCalls = []
        for noteID in self.settings[id]:
            parallelCalls.append((sm.RemoteSvc('charMgr').GetOwnerNote, (int(noteID),)))

        if len(parallelCalls):
            notes = uthread.parallel(parallelCalls)
        self.settingStrs[id] = ''
        for note in notes:
            self.settingStrs[id] += note[0].note

        return self.settingStrs[id]



    def WriteNote(self, name, text, folderID, noteID = None):
        if not noteID:
            noteID = sm.RemoteSvc('charMgr').AddOwnerNote('N:' + name, '<br>')
        self.AddNote(folderID, 'N', noteID)
        n = util.KeyVal()
        n.noteID = noteID
        n.label = name
        n.text = text
        self.notes['N:' + str(noteID)] = n
        uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').EditOwnerNote, int(noteID), 'N:' + self.notes[('N:' + str(noteID))].label, text)
        return noteID



    def GetNotesByType(self, t = 'N'):
        notes = []
        for n in self.notes:
            if n.find(t + ':') == 0:
                v = self.notes[n]
                v.parentID = self.GetParentFolder(v.noteID)
                v.parentName = ''
                parent = self.folders.get(v.parentID)
                if parent:
                    v.parentName = parent.data
                notes.append(v)

        return notes



    def GetFolders(self):
        folders = []
        for f in self.folders:
            folder = self.folders[f]
            if folder.type == 'F':
                v = util.KeyVal()
                v.noteID = f
                v.label = folder.data
                folders.append(v)

        return folders



    def GetNoteText(self, noteID):
        ret = None
        ret = note = self.notes.get('N:' + str(noteID), None)
        if not note or note.text is None:
            _note = sm.RemoteSvc('charMgr').GetOwnerNote(noteID)
            note = util.KeyVal()
            note.text = _note[0].note.strip()
            note.label = _note[0].label[2:]
            self.notes[('N:' + str(noteID))].text = note.text
            self.notes[('N:' + str(noteID))].label = note.label
            ret = note
        return ret



    def _OnResize(self, *etc):
        self.OnDividerMove()



    def OnDividerMove(self, *etc):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            (l, t, wndWidth, h,) = wnd.GetAbsolute()
            wnd.sr.nav.width = max(100, min(wnd.sr.nav.width, wndWidth - 154))



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        uicore.cmd.OpenBrowser(URL, data=data, args=args)



    def LoadNotepad(self):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.ShowLoad()



    def LoadNotes(self):
        while self.starting:
            blue.pyos.BeNice()

        scrolllist = []
        notes = self.GetNotes(0)
        for (id, n,) in notes.items():
            groupID = ('notepad', id)
            data = {'GetSubContent': self.GetGroupSubContent,
             'label': n.data,
             'id': groupID,
             'groupItems': self.GroupGetContentIDList(groupID),
             'iconMargin': 18,
             'showlen': 1,
             'state': 0,
             'sublevel': 0,
             'MenuFunction': self.GroupMenu,
             'allowGuids': ['listentry.User',
                            'listentry.Sender',
                            'listentry.PlaceEntry',
                            'listentry.NoteItem'],
             'DropData': self.GroupDropNode,
             'ChangeLabel': self.GroupChangeLabel,
             'DeleteFolder': self.GroupDeleteFolder,
             'GetContentIDList': self.GroupGetContentIDList,
             'CreateEntry': self.GroupCreateEntry,
             'RefreshScroll': self.RefreshNotes}
            scrolllist.append(listentry.Get('Group', data))

        data = {'GetSubContent': self.GetAllFolderContent,
         'label': mls.UI_GENERIC_ALLNOTES,
         'id': ('All Notes', 0),
         'groupItems': self.notes,
         'iconMargin': 18,
         'showlen': 1,
         'state': 0,
         'sublevel': 0,
         'showicon': '_22_45',
         'state': 'locked'}
        scrolllist.append(listentry.Get('Group', data))
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.sr.senderlist.Load(fixedEntryHeight=17, contentList=scrolllist, scrollTo=wnd.sr.senderlist.GetScrollProportion())
            wnd.sr.senderlist.hiliteSorted = 0



    def RefreshNotes(self):
        self.LoadNotes()



    def GetAllFolderContent(self, nodedata, newitems = 0):
        scrolllist = []
        for (key, note,) in self.notes.iteritems():
            data = {'itemID': None,
             'typeID': None,
             'id': (note.label, 'N:' + str(note.noteID)),
             'label': note.label,
             'sublevel': 1,
             'noteID': 'N:' + str(note.noteID),
             'type': 'NA',
             'ignoreRightClick': 1}
            entry = listentry.Get('NoteItem', data)
            if entry is not None:
                scrolllist.append(entry)

        return scrolllist



    def GetGroupSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        notelist = sm.GetService('notepad').GetNotes(nodedata.id[1])
        if len(notelist):
            qi = 1
            NoteListLength = len(notelist)
            for (id, note,) in notelist.items():
                entry = self.GroupCreateEntry((note.data, id), nodedata.sublevel + 1)
                if entry is not None:
                    scrolllist.append(entry)

            if len(nodedata.groupItems) != len(scrolllist):
                nodedata.groupItems = self.GroupGetContentIDList(nodedata.id)
        return scrolllist



    def GroupMenu(self, node):
        m = []
        if node.sublevel < 5:
            m.append((mls.UI_CMD_NEWFOLDER, self.NewFolder, (node.id[1], node)))
        m.append((mls.UI_CMD_NEWNOTE, self.NewNote, (node.id[1], node)))
        return m



    def GroupDropNode(self, id, nodes):
        for node in nodes:
            if not uicore.uilib.Key(uiconst.VK_SHIFT):
                if node.id:
                    self.RemoveFolder(node.id[1], ask=0)
            if node.__guid__ in ('listentry.User', 'listentry.Sender') and node.charID != eve.session.charid:
                self.AddNote(id[1], 'I', node.charID)
            if node.__guid__ == 'listentry.PlaceEntry' and type(node.bm.bookmarkID) == int:
                self.AddNote(id[1], 'B', node.bm.bookmarkID)
            if node.__guid__ == 'listentry.NoteItem':
                noteID = node.noteID
                if noteID in self.notes:
                    noteID = self.notes[noteID].noteID
                self.AddNote(id[1], 'N', noteID)

        self.LoadNotes()



    def GroupChangeLabel(self, id, newname):
        self.RenameFolder(id[1], name=newname)



    def GroupDeleteFolder(self, id):
        noteID = id[1]
        parentID = self.GetParentFolder(noteID)
        notes = self.GetNotes(noteID)
        for (id, note,) in notes.items():
            if note.type == 'F':
                self.GroupDeleteFolder((0, id))
                continue
            self.DeleteFolderNote(id)

        self.DeleteFolderNote(noteID)
        self.LoadNotes()



    def GroupCreateEntry(self, id, sublevel):
        (note, id,) = (self.folders[id[1]], id[1])
        if note.type == 'F':
            groupID = ('notepad', id)
            data = {'GetSubContent': self.GetGroupSubContent,
             'label': note.data,
             'id': groupID,
             'groupItems': self.GroupGetContentIDList(groupID),
             'iconMargin': 18,
             'showlen': 1,
             'state': 0,
             'sublevel': sublevel,
             'MenuFunction': self.GroupMenu,
             'allowGuids': ['listentry.User',
                            'listentry.Sender',
                            'listentry.PlaceEntry',
                            'listentry.NoteItem'],
             'DropData': self.GroupDropNode,
             'ChangeLabel': self.GroupChangeLabel,
             'DeleteFolder': self.GroupDeleteFolder,
             'GetContentIDList': self.GroupGetContentIDList,
             'CreateEntry': self.GroupCreateEntry,
             'RefreshScroll': self.RefreshNotes}
            return listentry.Get('Group', data)
        if note.type == 'I':
            charinfo = cfg.eveowners.Get(note.data)
            data = {'charID': int(note.data),
             'id': (note.data, id),
             'info': charinfo,
             'color': None,
             'GetMenu': self.GetCharMenu,
             'OnClick': self.OnCharClick,
             'sublevel': sublevel,
             'noteID': 'I:' + str(note.data)}
            return listentry.Get('User', data)
        if note.type == 'B':
            if self.bms is None:
                self.bms = sm.GetService('addressbook').GetBookmarks()
            if int(note.data) in self.bms:
                bookmark = self.bms[int(note.data)]
                (hint, comment,) = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
                text = '%s' % hint
                data = {'itemID': bookmark.itemID,
                 'typeID': bookmark.typeID,
                 'bm': bookmark,
                 'text': text,
                 'hint': hint,
                 'listGroupID': (note.data, id),
                 'id': (note.data, id),
                 'label': hint,
                 'GetMenu': self.GetBMMenu,
                 'OnClick': self.OnBookmarkClick,
                 'sublevel': sublevel,
                 'noteID': 'B:' + str(note.data)}
                return listentry.Get('PlaceEntry', data)
        if note.type == 'N':
            if 'N:' + str(note.data) in self.notes:
                data = {'itemID': None,
                 'typeID': None,
                 'id': (note.data, id),
                 'label': self.notes[('N:' + str(note.data))].label,
                 'sublevel': sublevel,
                 'noteID': 'N:' + str(note.data),
                 'type': 'N'}
                return listentry.Get('NoteItem', data)
        del self.folders[id]



    def GroupGetContentIDList(self, id):
        ids = self.GetNotes(id[1])
        return [ (self.folders[id].data, id) for id in ids ]



    def GetBMMenu(self, node):
        return [None] + [(mls.UI_CMD_REMOVEBOOKMARK, sm.GetService('notepad').RemoveFolder, (node.id[1],))]



    def GetCharMenu(self, node):
        m = [None] + [(mls.UI_CMD_REMOVECHAR, sm.GetService('notepad').RemoveFolder, (node.id[1],))]
        return m



    def OnDelete(self, *args):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            sel = wnd.sr.senderlist.GetSelected()
            for entry in sel[:]:
                if not entry.noteID:
                    continue
                if entry.noteID.startswith('F'):
                    self.GroupDeleteFolder(entry.id)
                elif entry.noteID.startswith('N') and entry.type == 'NA':
                    self.DeleteNote(entry.id[1])
                else:
                    self.RemoveFolder(entry.id[1])

            self.LoadNotes()



    def OnCharClick(self, entry):
        sm.GetService('notepad').ShowNote(entry.sr.node.noteID)



    def OnBookmarkClick(self, entry):
        sm.GetService('notepad').ShowNote(entry.sr.node.noteID)



    def ShowNote(self, id, force = 0):
        wnd = self.GetWnd()
        if not wnd:
            return self.GetWnd(1)
        while getattr(wnd.sr.browser, 'loading', 0):
            blue.pyos.synchro.Yield()

        if not force and hasattr(self, 'activeNode') and id is not None and self.activeNode == id:
            return True
        if not force and not self.SaveNote():
            return False
        if id is None or not id.upper().startswith('I:') and str(id) not in self.bookmarknotes and str(id) not in self.notes:
            wnd.sr.titletext.text = mls.UI_GENERIC_GENERALINFO
            wnd.sr.icon.LoadIcon('ui_49_64_2')
            wnd.sr.icon.width = wnd.sr.icon.height = 32
            wnd.sr.browser.SetValue('<font size="20">%s</font><br><br>%s<br>' % (mls.UI_SHARED_NOTEPAD, mls.UI_SHARED_NOTEPADINTRO))
            wnd.sr.browser.ReadOnly()
            self.activeNote = None
            return True
        wnd.sr.browser.Editable()
        noteID = id.split(':')
        if len(noteID) != 2:
            return True
        (t, id,) = noteID
        if not force and self.activeNode == t + ':' + str(id):
            return True
        if t == 'I':
            charid = int(id)
            note = sm.RemoteSvc('charMgr').GetNote(charid)
            charinfo = cfg.eveowners.Get(charid)
            sm.GetService('photo').GetPortrait(charid, 64, wnd.sr.icon)
            wnd.sr.titletext.text = charinfo.name
            wnd.sr.browser.SetValue(note)
        if t == 'N':
            if 'N:' + str(id) in self.notes:
                noteID = int(id)
                if self.notes[('N:' + str(id))].text is None:
                    note = sm.RemoteSvc('charMgr').GetOwnerNote(noteID)
                    self.notes[('N:' + str(id))].text = note[0].note.strip()
                    self.notes[('N:' + str(id))].label = note[0].label[2:]
                wnd.sr.icon.LoadIcon('ui_49_64_3')
                wnd.sr.icon.SetSize(32, 32)
                wnd.sr.titletext.text = self.notes[('N:' + str(id))].label
                wnd.sr.browser.SetValue(self.notes[('N:' + str(id))].text)
        self.activeNode = t + ':' + str(id)
        settings.char.notepad.Set('activeNote', self.activeNode)
        uicore.registry.SetFocus(wnd.sr.browser)
        return True



    def SaveNote(self, *args):
        if getattr(self, 'activeNode', None) is not None:
            (t, id,) = self.activeNode.split(':')
            wnd = self.GetWnd()
            if not wnd:
                return False
            txt = wnd.sr.browser.GetValue()
            if len(txt) >= 3900:
                return not eve.Message('NoteTooLong', {'total': len(txt)}, uiconst.YESNO) == uiconst.ID_YES
            if t == 'I':
                uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').SetNote, int(id), txt)
            if t == 'B':
                if 'B:' + str(id) not in self.bookmarknotes or self.bookmarknotes[('B:' + str(id))].text != txt:
                    if 'B:' + str(id) in self.bookmarknotes:
                        self.bookmarknotes[('B:' + str(id))].text = txt
                    sm.GetService('addressbook').UpdateBookmark(int(id), note=txt)
            if t == 'N':
                if 'N:' + str(id) in self.notes and self.notes[('N:' + str(id))].text != txt:
                    self.notes[('N:' + str(id))].text = txt
                    uthread.pool('notepad::SetNote', sm.RemoteSvc('charMgr').EditOwnerNote, int(id), 'N:' + self.notes[('N:' + str(id))].label, txt)
        return True



    def GetNotes(self, folderID):
        notes = {}
        for (id, n,) in self.folders.iteritems():
            if n.parent != folderID:
                continue
            notes[id] = n

        return notes



    def GetNote(self, noteID):
        if noteID in self.folders.keys():
            return self.folders[noteID]



    def GetParentFolder(self, nodeID):
        n = self.folders.get(nodeID, None)
        if n:
            return n.parent
        else:
            return 



    def RenameFolder(self, folderID = 0, entry = None, name = None, *args):
        if name is None:
            ret = uix.NamePopup(mls.UI_GENERIC_FOLDERNAME, mls.UI_SHARED_TYPENEWFOLDERNAME, maxLength=20)
            if ret is None:
                return self.folders[folderID].data
            name = ret['name']
        if self.AlreadyExists('F', name):
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_FOLDEREXISTS})
            return 
        self.folders[folderID].data = name
        return name



    def NewFolder(self, folderID = 0, node = None, *args):
        ret = uix.NamePopup(mls.UI_GENERIC_FOLDERNAME, mls.UI_SHARED_TYPEFOLDERNAME, maxLength=20)
        if ret is not None:
            name = ret['name']
            if self.AlreadyExists('F', name):
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_FOLDEREXISTS})
                return 
            self.AddNote(folderID, 'F', name)
            data = {'label': name,
             'folderid': self.lastid,
             'parent': folderID}
            self.LoadNotes()
            return data



    def NewFolderClick(self, *args):
        self.NewFolder()



    def RemoveFolder(self, folderID = 0, entry = None, ask = 1):
        if folderID in self.folders:
            if not ask or eve.Message('DeleteEntry', {}, uiconst.YESNO) == uiconst.ID_YES:
                if self.activeNode == self.folders[folderID].type + ':' + str(self.folders[folderID].data):
                    self.activeNode = None
                    self.ShowNote(None)
                parent = self.GetParentFolder(folderID)
                del self.folders[folderID]
                self.LoadNotes()



    def NewNote(self, folderID = 0, node = None, *args):
        ret = uix.NamePopup(mls.UI_GENERIC_NOTENAME, mls.UI_SHARED_ENTERNOTELABEL, maxLength=80)
        if ret is not None:
            name = ret['name']
            if self.AlreadyExists('N', name):
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_NOTEEXISTS})
                return 
            noteID = sm.RemoteSvc('charMgr').AddOwnerNote('N:' + name, '<br>')
            if folderID:
                self.AddNote(folderID, 'N', noteID)
            n = util.KeyVal()
            n.noteID = noteID
            n.label = name
            n.text = '<br>'
            self.notes['N:' + str(noteID)] = n
            self.LoadNotes()
            self.ShowNote('N:' + str(noteID))



    def AlreadyExists(self, type, name):
        if type == 'N':
            for (key, value,) in self.notes.iteritems():
                if value.label == name:
                    return True

        if type == 'F':
            for (key, value,) in self.folders.iteritems():
                if value.type == type and value.data == name:
                    return True

        return False



    def AddNote(self, parent, type, data):
        self.lastid += 1
        n = util.KeyVal()
        n.type = type
        n.parent = parent
        n.data = data
        self.folders[self.lastid] = n



    def DeleteFolderNote(self, noteID):
        del self.folders[noteID]



    def DeleteNote(self, noteID):
        if noteID in self.notes:
            if eve.Message('DeleteNote', {}, uiconst.YESNO) == uiconst.ID_YES:
                if self.activeNode == noteID:
                    self.activeNode = None
                    self.ShowNote(None)
                (t, id,) = noteID.split(':')
                for (key, value,) in self.folders.items():
                    if value.type == t and str(value.data) == id:
                        del self.folders[key]

                note = self.notes[noteID]
                sm.RemoteSvc('charMgr').RemoveOwnerNote(int(note.noteID))
                del self.notes[noteID]
                self.LoadNotes()



    def RenameNote(self, noteID):
        if noteID in self.folders:
            noteID = self.folders[noteID].type + ':' + str(self.folders[noteID].data)
        if noteID not in self.notes:
            return 
        ret = uix.NamePopup(mls.UI_GENERIC_NOTENAME, mls.UI_SHARED_ENTERNOTELABEL, self.notes[noteID].label, maxLength=80)
        if ret is not None:
            if self.AlreadyExists('N', ret['name']):
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_NOTEEXISTS})
                return 
            self.notes[noteID].label = ret['name']
            sm.RemoteSvc('charMgr').EditOwnerNote(self.notes[noteID].noteID, 'N:' + ret['name'])
            self.LoadNotes()
            if getattr(self, 'activeNode', None) == noteID:
                wnd = self.GetWnd()
                if wnd:
                    wnd.sr.titletext.text = ret['name']




class NoteItem(listentry.Generic):
    __guid__ = 'listentry.NoteItem'

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        self.sr.icon = uicls.Icon(icon='ui_49_64_3', parent=self, left=0, top=-4, size=24, ignoreSize=True)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.sublevel = node.Get('sublevel', 0)
        self.sr.icon.state = uiconst.UI_NORMAL
        self.sr.label.left = 24 + max(0, self.sr.sublevel * 16)
        self.sr.icon.left = 0 + max(0, self.sr.sublevel * 16)
        self.sr.label.text = node.label



    def OnClick(self, *args):
        if self.sr.node:
            if not uicore.uilib.Key(uiconst.VK_CONTROL):
                if not sm.GetService('notepad').ShowNote(self.sr.node.noteID):
                    return 
            self.sr.node.scroll.SelectNode(self.sr.node)



    def GetMenu(self):
        m = listentry.Generic.GetMenu(self)
        if self.sr.node.type == 'N':
            m += [(mls.UI_CMD_RENAMENOTE, sm.GetService('notepad').RenameNote, (self.sr.node.id[1],))]
            m += [(mls.UI_CMD_REMOVENOTE, sm.GetService('notepad').RemoveFolder, (self.sr.node.id[1],))]
        if self.sr.node.type == 'NA':
            m += [(mls.UI_CMD_RENAMENOTE, sm.GetService('notepad').RenameNote, (self.sr.node.id[1],))]
            m += [(mls.UI_CMD_DELETENOTE, sm.GetService('notepad').DeleteNote, (self.sr.node.id[1],))]
        return m



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 18
        return node.height



    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes




class NotepadWindow(uicls.Window):
    __guid__ = 'form.Notepad'
    default_width = 400
    default_height = 300


