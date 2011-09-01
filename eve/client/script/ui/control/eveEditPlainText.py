import uix
import util
import blue
import fontflags
import uicls
import uiconst
import uiutil
import trinity
import listentry
import _weakref

class EditPlainText(uicls.EditPlainTextCore):
    __guid__ = 'uicls.EditPlainText'
    default_align = uiconst.TOALL
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_fontcolor = (1.0, 1.0, 1.0, 0.75)
    allowPrivateDrops = 0

    def OnDropDataDelegate(self, node, nodes):
        uicls.EditCore.OnDropDataDelegate(self, node, nodes)
        if self.readonly:
            return 
        for entry in nodes:
            if entry.__guid__ in ('listentry.User', 'listentry.ChatUser', 'listentry.Sender'):
                link = 'showinfo:' + str(entry.info.typeID) + '//' + str(entry.charID)
                self.AddLink(entry.info.name, link)
            elif entry.__guid__ == 'listentry.PlaceEntry' and self.allowPrivateDrops:
                bookmarkID = entry.bm.bookmarkID
                bms = sm.GetService('addressbook').GetBookmarks()
                if bookmarkID in bms:
                    bookmark = bms[bookmarkID]
                    (hint, comment,) = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
                link = 'showinfo:' + str(bms[bookmarkID].typeID) + '//' + str(bms[bookmarkID].itemID)
                self.AddLink(hint, link)
            elif entry.__guid__ == 'listentry.NoteItem' and self.allowPrivateDrops:
                link = 'note:' + str(entry.noteID)
                self.AddLink(entry.label, link)
            elif entry.__guid__ in ('listentry.InvItem', 'xtriui.InvItem', 'xtriui.ShipUIModule', 'listentry.InvAssetItem'):
                if type(entry.rec.itemID) is tuple:
                    link = 'showinfo:' + str(entry.rec.typeID)
                else:
                    link = 'showinfo:' + str(entry.rec.typeID) + '//' + str(entry.rec.itemID)
                self.AddLink(entry.name, link)
            elif entry.__guid__ in ('listentry.VirtualAgentMissionEntry',):
                link = 'fleetmission:' + str(entry.agentID) + '//' + str(entry.charID)
                self.AddLink(entry.label, link)
            elif entry.__guid__ in ('xtriui.CertSlot',):
                if entry.rec.certID:
                    link = 'CertSlot:%s' % entry.rec.certID
                    self.AddLink(entry.rec.label, link)
                else:
                    link = 'showinfo:%s' % entry.rec.typeID
                    self.AddLink(entry.rec.label, link)
            elif entry.__guid__.startswith('listentry.ContractEntry'):
                link = 'contract:' + str(entry.solarSystemID) + '//' + str(entry.contractID)
                self.AddLink(entry.name.replace('&gt;', '>'), link)
            elif entry.__guid__ in ('listentry.FleetFinderEntry',):
                link = 'fleet:%s' % entry.fleet.fleetID
                self.AddLink(entry.fleet.fleetName or mls.UI_GENERIC_UNKNOWN, link)
            elif entry.__guid__ == 'xtriui.ListSurroundingsBtn':
                if not entry.typeID and not entry.itemID:
                    return 
                link = 'showinfo:' + str(entry.typeID) + '//' + str(entry.itemID)
                self.AddLink(entry.label, link)
            elif entry.__guid__ == 'listentry.FittingEntry':
                PADDING = 12
                link = 'fitting:' + sm.StartService('fittingSvc').GetStringForFitting(entry.fitting)
                roomLeft = self.RoomLeft() - PADDING
                if len(link) >= roomLeft:
                    if roomLeft < 14:
                        raise UserError('LinkTooLong')
                    if eve.Message('ConfirmTruncateLink', {'numchar': len(link),
                     'maxchar': roomLeft}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                        return 
                    link = link[:roomLeft]
                self.AddLink(entry.fitting.name, link)
            elif entry.__guid__ == 'listentry.GenericMarketItem':
                link = 'showinfo:' + str(entry.typeID)
                self.AddLink(entry.label, link)

        uicore.registry.SetFocus(self)



    def ApplyGameSelection(self, what, data, changeObjs):
        if what == 6 and len(changeObjs):
            key = {}
            if data:
                key['link'] = data['link']
                t = self.DoSearch(key['link'], data['text'])
                if not t:
                    return 
            else:
                format = [{'type': 'checkbox',
                  'label': '_hide',
                  'text': 'http://',
                  'key': 'http://',
                  'required': 1,
                  'setvalue': 1,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': mls.UI_GENERIC_CHARACTER,
                  'key': 'char',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': mls.UI_GENERIC_CORPORATION,
                  'key': 'corp',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': mls.UI_GENERIC_ITEMTYPE,
                  'key': 'type',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': mls.UI_GENERIC_SOLARSYSTEM,
                  'key': 'solarsystem',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': mls.UI_GENERIC_STATION,
                  'key': 'station',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'edit',
                  'label': mls.GENERIC_LINK,
                  'text': 'http://',
                  'width': 170,
                  'required': 1,
                  'key': 'txt',
                  'frame': 1}]
                key = self.AskLink(mls.UI_GENERIC_ENTERLINK, format, width=400)
            anchor = -1
            if key:
                link = key['link']
                if link == None:
                    return 
                if link in ('char', 'corp', 'solarsystem', 'station', 'type'):
                    if not self.typeID:
                        t = self.DoSearch(link, key['txt'])
                        if not t:
                            return 
                    anchor = 'showinfo:' + str(self.typeID)
                    if self.itemID:
                        anchor += '//' + str(self.itemID)
                elif link == 'fleet':
                    anchor = 'fleet:' + str(self.itemID)
                anchor = key['link'] + key['txt']
            return anchor
        return -1



    def OnLinkTypeChange(self, chkbox, *args):
        if chkbox.GetValue():
            self.itemID = self.typeID = 0
            self.key = chkbox.data['key']
            text = uiutil.GetChild(chkbox, 'text')
            wnd = chkbox.FindParentByName(mls.UI_SHARED_GENERATELINK)
            if not wnd:
                return 
            editParent = uiutil.FindChild(wnd, 'editField')
            if editParent is not None:
                label = uiutil.FindChild(editParent, 'label')
                label.text = text.text
                edit = uiutil.FindChild(editParent, 'edit_txt')
                edit.SetValue('')
                self.sr.searchbutt = uiutil.FindChild(editParent, 'button')
                if self.key in ('char', 'corp', 'type', 'solarsystem', 'station'):
                    if self.sr.searchbutt == None:
                        self.sr.searchbutt = uicls.Button(parent=editParent, label=mls.UI_CMD_SEARCH, func=self.OnSearch, btn_default=0, align=uiconst.TOPRIGHT)
                    else:
                        self.sr.searchbutt.state = uiconst.UI_NORMAL
                elif self.sr.searchbutt != None:
                    self.sr.searchbutt.state = uiconst.UI_HIDDEN



    def OnSearch(self, *args):
        wnd = self.sr.searchbutt.FindParentByName(mls.UI_SHARED_GENERATELINK)
        if not wnd:
            return 
        editParent = uiutil.FindChild(wnd, 'editField')
        edit = uiutil.FindChild(editParent, 'edit_txt')
        val = edit.GetValue().strip().lower()
        name = self.DoSearch(self.key, val)
        if name is not None:
            edit.SetValue(name)



    def DoSearch(self, key, val):
        self.itemID = None
        self.typeID = None
        id = None
        name = ''
        if key == 'type':
            if getattr(self, 'markettypes', None) == None:
                from contractutils import GetMarketTypes
                self.markettypes = GetMarketTypes()
            itemTypes = []
            for t in self.markettypes:
                if t.typeName.lower().find(val.lower()) >= 0:
                    itemTypes.append((cfg.invtypes.Get(t.typeID).name, None, t.typeID))

            if not itemTypes:
                eve.Message('NoItemTypesFound')
                return 
            id = uix.ListWnd(itemTypes, 'item', mls.UI_GENERIC_SELECTITEMTYPE, None, 1)
        else:
            group = None
            cat = None
            filterGroups = []
            hideNPC = 0
            if key == 'solarsystem':
                group = const.groupSolarSystem
            elif key == 'station':
                group = const.groupStation
            elif key == 'char':
                cat = const.categoryOwner
                filterGroups = [const.groupCharacter]
            elif key == 'corp':
                cat = const.categoryOwner
                filterGroups = [const.groupCorporation]
            id = uix.Search(val, group, cat, hideNPC=hideNPC, filterGroups=filterGroups)
        name = ''
        if id:
            self.itemID = id
            self.typeID = 0
            if key in ('char', 'corp'):
                o = cfg.eveowners.Get(id)
                self.typeID = o.typeID
                name = o.name
            elif key == 'solarsystem':
                self.typeID = const.typeSolarSystem
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'station':
                self.typeID = sm.GetService('ui').GetStation(id).stationTypeID
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'type':
                self.typeID = id[2]
                self.itemID = None
                name = id[0]
        return name



    def AskLink(self, label = '', lines = [], width = 280):
        icon = uiconst.QUESTION
        format = [{'type': 'btline'}, {'type': 'text',
          'text': label,
          'frame': 1}] + lines + [{'type': 'bbline'}]
        btns = uiconst.OKCANCEL
        retval = uix.HybridWnd(format, mls.UI_SHARED_GENERATELINK, 1, None, uiconst.OKCANCEL, minW=width, minH=110, icon=icon)
        if retval:
            return retval
        else:
            return 



    def AddLink(self, text, link = None):
        self.SetSelectionRange(None, None)
        node = self.GetActiveNode()
        if node is None:
            return 
        shiftCursor = len(text)
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        shift = 0
        if stackCursorIndex != 0:
            currentParams = self._activeParams.Copy()
            self.InsertToGlyphString(glyphString, currentParams, ' ', stackCursorIndex)
            shift += 1
        currentParams = self._activeParams.Copy()
        currentParams.url = link
        self.InsertToGlyphString(glyphString, currentParams, text, stackCursorIndex + shift)
        shift += shiftCursor
        currentParams = self._activeParams.Copy()
        self.InsertToGlyphString(glyphString, currentParams, ' ', stackCursorIndex + shift)
        shift += 1
        self.UpdateGlyphString(glyphString, advance=shiftCursor, stackCursorIndex=stackCursorIndex)
        self.SetCursorPos(self.globalCursorPos + shift)
        cursorAdvance = 1



    def GetMenuDelegate(self, node = None):
        m = uicls.EditPlainTextCore.GetMenuDelegate(self, node)
        if not self.readonly:
            m.append(None)
            linkmenu = [(mls.UI_GENERIC_CHARACTER, self.LinkCharacter),
             (mls.UI_GENERIC_CORPORATION, self.LinkCorp),
             (mls.UI_GENERIC_SOLARSYSTEM, self.LinkSolarSystem),
             (mls.UI_GENERIC_STATION, self.LinkStation),
             (mls.UI_GENERIC_ITEMTYPE, self.LinkItemType)]
            m.append((mls.UI_CMD_AUTOLINK, linkmenu))
            sm.GetService('ime').GetMenuDelegate(self, node, m)
        return m



    def LinkCharacter(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        print 'txt',
        print repr(txt)
        self.ApplySelection(6, data={'text': txt,
         'link': 'char'})



    def LinkCorp(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'corp'})



    def LinkSolarSystem(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'solarsystem'})



    def LinkStation(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'station'})



    def LinkItemType(self):
        if self.GetSelection() == 0:
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        self.ApplySelection(6, data={'text': txt,
         'link': 'type'})




