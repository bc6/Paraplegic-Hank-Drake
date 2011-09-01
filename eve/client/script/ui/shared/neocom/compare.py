import sys
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import listentry
import util
import lg
import uicls
import uiconst

class TypeCompare(uicls.Window):
    __guid__ = 'form.TypeCompare'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.typeIDs = []
        self.attrDictChecked = []
        self.banAttrs = [const.attributeTechLevel] + sm.GetService('info').GetSkillAttrs()
        self.allowedCategs = [const.categoryCharge,
         const.categoryCommodity,
         const.categoryDrone,
         const.categoryImplant,
         const.categoryMaterial,
         const.categoryModule,
         const.categoryShip,
         const.categorySkill,
         const.categoryStructure,
         const.categoryDeployable,
         const.categorySubSystem]
        self.attributeLimit = 10
        self.typeLimit = 40
        self.settingsinited = 0
        self.graphinited = 0
        self.compareinited = 0
        self.topLevelMarketGroup = None
        self.attrDictIDs = []
        self.SetCaption(mls.UI_INFOWND_COMPARETOOL)
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([350, 400])
        self.LoadPanels()
        self.LoadCompare()



    def LoadPanels(self):
        bottomparent = uicls.Container(name='bottomparent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=25)
        uicls.Line(parent=bottomparent, align=uiconst.TOTOP)
        self.sr.bottomparent = bottomparent
        panel = uicls.Container(name='panel', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.panel = panel



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def LoadCompare(self):
        if not self.compareinited:
            subpanel = uicls.Container(name='subpanel', parent=self.sr.panel, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.sr.subpanel = subpanel
            bottomclear = uicls.Container(name='typecompare_bottomclear', parent=self.sr.subpanel, height=60, align=uiconst.TOBOTTOM)
            uicls.Label(text=mls.UI_INFOWND_COMPARETXT1, parent=bottomclear, align=uiconst.TOALL, width=const.defaultPadding, height=const.defaultPadding, autowidth=False, autoheight=False, state=uiconst.UI_NORMAL)
            attributescroll = uicls.Container(name='typecompare_attributescroll', parent=self.sr.subpanel, align=uiconst.TOLEFT, left=0, width=settings.user.ui.Get('charsheetleftwidth', 125), idx=0)
            self.sr.attributescroll = uicls.Scroll(name='attributescroll', parent=attributescroll, padding=(0,
             const.defaultPadding,
             0,
             const.defaultPadding))
            self.sr.attributescroll.sr.id = 'typecompare_attributescroll'
            self.sr.attributescroll.hiliteSorted = 0
            typescroll = uicls.Container(name='typecompare_typescroll', parent=self.sr.subpanel, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.sr.typescroll = uicls.Scroll(name='typescroll', parent=typescroll, left=0, top=const.defaultPadding, width=2, height=const.defaultPadding)
            divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, idx=1, width=const.defaultPadding, parent=self.sr.subpanel, state=uiconst.UI_NORMAL)
            divider.Startup(attributescroll, 'width', 'x', 160, 200)
            self.sr.typescroll.sr.id = 'typecompare_typescroll'
            btns = uicls.ButtonGroup(btns=[[mls.UI_SHARED_CHECKALL_OFF,
              self.SelectAll,
              (0,),
              None], [mls.UI_GENERIC_RESETALL,
              self.RemoveAllEntries,
              (),
              None]], parent=self.sr.bottomparent, idx=0, unisize=0)
            self.sr.typescroll.sr.content.OnDropData = self.OnDropData
            self.compareinited = 1



    def RemoveAllEntries(self, *args):
        self.typeIDs = []
        self.topLevelMarketGroup = None
        self.SelectAll()



    def SelectAll(self, onOff = 0):
        if onOff:
            return 
        self.attrDictChecked = []
        self.OnColumnChanged()



    def AddEntry(self, nodes):
        if self.compareinited:
            if type(nodes) != type([]):
                nodes = [nodes]
            current = [ node.typeID for node in self.typeIDs ]
            valid = [ node for node in nodes if node.typeID not in current ]
            hasNew = False
            i = 0
            for typeRow in valid:
                topLevelMarketGroupID = self.GetTopLevelMarketGroupID(typeRow)
                if topLevelMarketGroupID == -1:
                    eve.Message('CannotCompareNoneItem')
                    break
                invgroup = typeRow.Group()
                invgroup.categoryID
                if invgroup.categoryID not in self.allowedCategs:
                    eve.Message('CannotCompareFromCategory', {'category': cfg.invcategories.Get(invgroup.categoryID).categoryName})
                    break
                if hasattr(self, 'topLevelMarketGroup') and self.topLevelMarketGroup != topLevelMarketGroupID:
                    self.CompareErrorMessage(topLevelMarketGroupID)
                    break
                else:
                    sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_ADDINGTYPES, typeRow.typeName, i, len(valid))
                    blue.pyos.synchro.Yield()
                    typeRow = self.GetPreparedTypeData(typeRow)
                    if typeRow not in self.typeIDs:
                        hasNew = True
                        self.typeIDs.append(typeRow)
                i = i + 1

            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_ADDINGTYPES, mls.UI_GENERIC_DONE, 1, 1)
            if hasNew:
                self.OnColumnChanged()



    def RemoveEntry(self, item):
        sel = self.sr.typescroll.GetSelected() or [item]
        rem = [ node.typeID for node in sel ]
        self.typeIDs = [ compareData for compareData in self.typeIDs if compareData.typeID not in rem ]
        if not self.typeIDs:
            self.attrDictChecked = []
            self.topLevelMarketGroup = None
        self.OnColumnChanged()



    def OnColumnChanged(self, force = 1, *args):
        self.GetCombinedDogmaAttributes()
        if force:
            self.GetAttributeScroll()
        self.GetTypeCompareScroll()



    def GetTopLevelMarketGroupID(self, data):
        marketGroupIDFromType = None
        if data.marketGroupID is None:
            typeID = sm.GetService('info').GetMetaParentTypeID(data.typeID)
            if typeID is not None:
                marketGroupIDFromType = cfg.invtypes.Get(sm.GetService('info').GetMetaParentTypeID(data.typeID)).marketGroupID
                topLevelMarketGroupID = self.GetTopLevelMarketGroupIDEx(marketGroupIDFromType)
            else:
                return -1
        else:
            topLevelMarketGroupID = self.GetTopLevelMarketGroupIDEx(data.marketGroupID)
        if not self.topLevelMarketGroup:
            if marketGroupIDFromType:
                self.topLevelMarketGroup = self.GetTopLevelMarketGroupIDEx(marketGroupIDFromType)
            else:
                self.topLevelMarketGroup = self.GetTopLevelMarketGroupIDEx(data.marketGroupID)
        return topLevelMarketGroupID



    def GetTopLevelMarketGroupIDEx(self, marketGroupID):
        mg = sm.GetService('marketutils').GetMarketGroup(marketGroupID)
        if mg:
            parentGroupID = mg.parentGroupID
            while parentGroupID:
                mg = sm.GetService('marketutils').GetMarketGroup(parentGroupID)
                parentGroupID = mg.parentGroupID

            return mg.marketGroupID
        else:
            return None



    def CompareErrorMessage(self, topLevelMarketGroupID):
        currentMarketGroup = sm.GetService('marketutils').GetMarketGroup(self.topLevelMarketGroup)
        tryfailMarketGroup = sm.GetService('marketutils').GetMarketGroup(topLevelMarketGroupID)
        eve.Message('CannotCompareFromItemToItem', {'currentMarketGroup': currentMarketGroup.marketGroupName,
         'tryfailMarketGroup': tryfailMarketGroup.marketGroupName})



    def GetCombinedDogmaAttributes(self):
        attrIDDict = []
        attrDict = []
        for typeRow in self.typeIDs:
            ad = sm.GetService('info').GetAttrDict(typeRow.invtype.typeID)
            for (attributeID, value,) in ad.iteritems():
                if attributeID not in self.banAttrs and attributeID not in attrIDDict:
                    attrIDDict.append(attributeID)
                    dgmAttribs = cfg.dgmattribs.Get(attributeID)
                    if dgmAttribs.published or dgmAttribs.attributeID == const.attributeHp:
                        attrDict.append(dgmAttribs)


        attributesToRemove = []
        for attribute in attrDict:
            removeIt = True
            for typeRow in self.typeIDs:
                taa = self.GetAttributeValue(attribute, typeRow.invtype.typeID)
                if taa:
                    removeIt = False
                    break

            if removeIt:
                attributesToRemove.append(attribute)

        self.attrDict = attrDict



    def GetAttributeScroll(self):
        scrolllist = self.GetAttributeContentList()
        self.sr.attributescroll.Load(contentList=scrolllist, noContentHint=mls.UI_INFOWND_COMPAREHINT2)



    def GetAttributeContentList(self):
        scrolllist = []
        if self.attrDict:
            self.attrDictIDs = []
            info = sm.GetService('godma').GetStateManager().GetShipType(const.typeApocalypse)
            tid = self.typeIDs[0]
            attrAndFittings = sm.GetService('info').GetShipAttributes() + self.GetFittings()
            if cfg.invtypes.Get(tid.typeID).Group().Category().categoryID == const.categoryShip:
                for (caption, attrs,) in attrAndFittings:
                    shipAttr = [ each for each in self.attrDict if each.attributeID in attrs ]
                    if shipAttr:
                        scrolllist.append(listentry.Get('Header', {'label': caption}))
                        bd = sm.GetService('info').GetBarData(None, info, caption)
                        attr = None
                        if bd:
                            attr = cfg.dgmattribs.Get(bd.get('attributeID'))
                            scrolllist.append(self.ScrollEntry(attr))
                            self.attrDictIDs.append(attr.attributeID)
                        for attr in shipAttr:
                            scrolllist.append(self.ScrollEntry(attr))
                            self.attrDictIDs.append(attr.attributeID)

                        if caption == mls.UI_GENERIC_PROPULSION:
                            entry = self.ScrollEntry(cfg.dgmattribs.Get(const.attributeBaseWarpSpeed))
                            scrolllist.append(entry)
                            self.attrDictIDs.append(const.attributeBaseWarpSpeed)

            else:
                for each in self.attrDict:
                    scrolllist.append(self.ScrollEntry(each))
                    self.attrDictIDs.append(each.attributeID)

        return scrolllist



    def GetFittings(self):
        list = [(mls.UI_GENERIC_FITTING, [const.attributeCpuOutput,
           const.attributePowerOutput,
           const.attributeUpgradeCapacity,
           const.attributeHiSlots,
           const.attributeMedSlots,
           const.attributeLowSlots,
           const.attributeTurretSlotsLeft,
           const.attributeUpgradeSlotsLeft,
           const.attributeLauncherSlotsLeft])]
        return list



    def ScrollEntry(self, entry):
        sentry = listentry.Get('AttributeCheckbox', {'line': 1,
         'info': entry,
         'label': entry.displayName,
         'iconID': entry.iconID,
         'item': entry,
         'text': sm.GetService('info').FormatUnit(entry.unitID) or ' ',
         'hint': entry.displayName,
         'checked': [True, False][(entry.attributeID not in self.attrDictChecked)],
         'cfgname': entry.attributeID,
         'retval': entry.attributeID,
         'OnChange': self.OnAttributeSelectedChanged})
        return sentry



    def OnAttributeSelectedChanged(self, checkbox):
        attributeID = checkbox.data['retval']
        if checkbox.GetValue():
            if len(self.attrDictChecked) < self.attributeLimit:
                if attributeID not in self.attrDictChecked:
                    self.attrDictChecked.append(attributeID)
                self.LogInfo(attributeID, 'CHECKED')
                self.OnColumnChanged(force=0)
            else:
                checkbox.SetValue(False)
                message = mls.SHARED_CANONLYCOMPAREAMOUNTATTRIBUTES % {'amount': self.attributeLimit}
                eve.Message('CustomInfo', {'info': message})
        elif attributeID in self.attrDictChecked:
            self.attrDictChecked.remove(attributeID)
        self.LogInfo(attributeID, 'UNCHECKED')
        self.OnColumnChanged(force=0)



    def GetTypeCompareScroll(self):
        (scrolllist, headers,) = self.GetCompareTypeInfoContentList()
        self.sr.typescroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_INFOWND_COMPAREHINT1)



    def GetAttributeValue(self, attribute, typeID):
        val = None
        ta = sm.GetService('info').GetAttrDict(typeID)
        if ta.has_key(attribute.attributeID) or attribute.attributeCategory == 9:
            val = ta.get(attribute.attributeID)
        return val



    def GetCompareTypeInfoContentList(self):
        scrolllist = []
        (headers, uniqueHeaders, treatedHeaders, initialHeaders,) = ([],
         [],
         [],
         [])
        if self.typeIDs:
            headers = ['type name', 'meta group']
            for typeRow in self.typeIDs:
                data = typeRow.copy()
                metaGroup = sm.GetService('info').GetMetaTypesFromTypeID(typeRow.invtype.typeID, groupOnly=1)
                text = '%s<t>%s' % (typeRow.invtype.typeName, metaGroup.metaGroupName)
                data.Set('sort_%s' % headers[0], typeRow.invtype.typeName)
                data.Set('sort_%s' % headers[1], metaGroup.metaGroupID)
                attributeLoop = {}
                for each in self.attrDict:
                    if each.attributeID in self.attrDictChecked:
                        attributeLoop[each.attributeID] = each

                for each in self.attrDictIDs:
                    attribute = attributeLoop.get(each, None)
                    if not attribute:
                        continue
                    displayName = attribute.displayName.replace(' ', '<br>')
                    if (displayName, attribute.attributeID) not in uniqueHeaders:
                        uniqueHeaders.append((displayName, attribute.attributeID))
                    if attribute.attributeID == const.attributeBaseWarpSpeed:
                        GTA = sm.GetService('godma').GetTypeAttribute
                        typeID = typeRow.invtype.typeID
                        cmp = max(GTA(typeID, const.attributeBaseWarpSpeed, defaultValue=1), 1.0)
                        cmp *= GTA(typeID, const.attributeWarpSpeedMultiplier, defaultValue=1)
                        cmp *= 3 * const.AU
                        data.Set('sort_%s' % displayName, cmp)
                        taa = sm.GetService('info').GetBaseWarpSpeed(typeRow.invtype.typeID)
                    else:
                        taa = self.GetAttributeValue(attribute, typeRow.invtype.typeID)
                        data.Set('sort_%s' % displayName, taa)
                        if taa != None:
                            taa = sm.GetService('info').GetFormatAndValue(attribute, taa)
                        else:
                            taa = mls.UI_GENERIC_NOTAVAILABLESHORT
                    if typeRow.invtype.Group().Category().categoryID == const.categoryCharge:
                        (bsd, bad,) = sm.GetService('info').GetBaseDamageValue(typeRow.invtype.typeID)
                        if attribute.displayName == mls.UI_INFOWND_BASESHIELDDMG:
                            taa = bsd[0]
                        elif attribute.displayName == mls.UI_INFOWND_BASEARMORDMG:
                            taa = bad[0]
                    text += '<t>%s' % taa

                data.label = text
                data.getIcon = 1
                data.GetMenu = self.GetEntryMenu
                data.viewMode = 'details'
                data.item = data.invtype
                data.ignoreRightClick = 1
                scrolllist.append(listentry.Get('Item', data=data))

            for (header, attributeID,) in uniqueHeaders:
                if header in headers:
                    header = header + ' '
                headers.append(header)

            initialHeaders = headers
            treatedHeaders = []
            for each in initialHeaders:
                treatedHeaders.append(each.replace(' ', '<br>'))

        return (scrolllist, initialHeaders)



    def GetEntryMenu(self, item):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(None, item.typeID, ignoreMarketDetails=0)
        item.DoSelectNode()
        sel = self.sr.typescroll.GetSelected()
        text = mls.UI_CMD_REMOVE
        if len(sel) > 1:
            text += ' (%s)' % len(sel)
        m += [(text, self.RemoveEntry, (item,))]
        return m



    def OnDropData(self, dragObj, nodes):
        for node in nodes:
            if node.__guid__ in ('xtriui.InvItem', 'xtriui.FittingSlot', 'listentry.InvItem'):
                self.AddEntry([node.invtype])




    def GetPreparedTypeData(self, rec):
        attribs = {}
        for attribute in sm.GetService('godma').GetType(rec.typeID).displayAttributes:
            attribs[attribute.attributeID] = attribute.value

        data = util.KeyVal()
        data.godmaattribs = attribs
        data.invtype = cfg.invtypes.Get(rec.typeID)
        data.itemID = None
        data.typeID = rec.typeID
        return data




class AttributeCheckbox(listentry.LabelTextTop):
    __guid__ = 'listentry.AttributeCheckbox'

    def Startup(self, *args):
        listentry.LabelTextTop.Startup(self, args)
        cbox = uicls.Checkbox(align=uiconst.TOPLEFT, callback=self.CheckBoxChange, pos=(4, 4, 0, 0))
        cbox.data = {}
        self.children.insert(0, cbox)
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_DISABLED



    def Load(self, args):
        listentry.LabelTextTop.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data = {'key': data.cfgname,
         'retval': data.retval}
        self.sr.icon.left = 20
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 2
        self.sr.text.left = self.sr.icon.left + self.sr.icon.width + 2



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)



    def OnClick(self, *args):
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        if self.sr.checkbox.groupName is None:
            self.sr.checkbox.SetChecked(not self.sr.checkbox.checked)
            return 
        if self.sr.checkbox.diode is None:
            self.sr.checkbox.Prepare_Diode_()
        for node in self.sr.node.scroll.GetNodes():
            if node.Get('__guid__', None) == 'listentry.Checkbox' and node.Get('group', None) == self.sr.checkbox.groupName:
                if node.panel:
                    node.panel.sr.checkbox.SetChecked(0, 0)
                    node.checked = 0
                else:
                    node.checked = 0

        if not self.destroyed:
            self.sr.checkbox.SetChecked(1)




