import form
import uix
import uiutil
import listentry
import draw
import uthread
import util
import blue
import uicls
import uiconst
import contractscommon as cc
from contractutils import GetContractIcon, GetContractTitle, GetContractTimeLeftText, FmtISKWithDescription, GetContractTypeText, GetCurrentBid, CutAt, SelectItemTypeDlg
import log
import copy
import sys
import re
import xtriui
LEFT_WIDTH = 150
MILLION = 1000000
MAXJUMPROUTENUM = 100
PAGINGRANGE = 10
NUM_SAVED_LOCATIONS = 5
MAX_NUM_MILLIONS = 100000

class ContractSearchWindow(uicls.Container):
    __guid__ = 'form.ContractSearchWindow'
    default_clipChildren = True

    def GetTypesFromName(self, itemTypeName, categoryID, groupID):
        itemTypes = {}
        compiled = None
        if '*' in itemTypeName:
            pattern = itemTypeName.lower().replace('*', '.*')
            compiled = re.compile(pattern)
        if itemTypeName:
            itemTypeName = itemTypeName.lower()
            for line in cfg.invtypes:
                if not line.published:
                    continue
                if groupID and line.groupID != groupID:
                    continue
                if categoryID and line.Group().categoryID != categoryID:
                    continue
                if compiled:
                    if not compiled.match(line.typeName.lower()):
                        continue
                elif itemTypeName not in line.typeName.lower():
                    continue
                itemTypes[line.typeID] = line.typeName

        return itemTypes



    def ChangeViewMode(self, viewMode):
        oldViewMode = int(not viewMode)
        prefs.SetValue('contractsSimpleView', viewMode)
        blue.pyos.synchro.Yield()
        self.sr.Get('viewMode%s' % oldViewMode, None).Deselect()
        if self.currPage in self.pageData:
            self.RenderPage()



    def PopulateSortCombo(self):
        contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
        opt = [('%s (%s)' % (mls.UI_CONTRACTS_DATECREATED, mls.UI_CONTRACTS_OLDESTFIRST), (cc.SORT_ID, 0)),
         ('%s (%s)' % (mls.UI_CONTRACTS_DATECREATED, mls.UI_CONTRACTS_NEWESTFIRST), (cc.SORT_ID, 1)),
         ('%s (%s)' % (mls.UI_CONTRACTS_TIMELEFT, mls.UI_CONTRACTS_SHORTESTFIRST), (cc.SORT_EXPIRED, 0)),
         ('%s (%s)' % (mls.UI_CONTRACTS_TIMELEFT, mls.UI_CONTRACTS_LONGESTFIRST), (cc.SORT_EXPIRED, 1))]
        if contractType == const.conTypeCourier:
            opt.extend([('%s (%s)' % (mls.UI_CONTRACTS_REWARD, mls.UI_CONTRACTS_LOWESTFIRST), (cc.SORT_REWARD, 0)),
             ('%s (%s)' % (mls.UI_CONTRACTS_REWARD, mls.UI_CONTRACTS_HIGHESTFIRST), (cc.SORT_REWARD, 1)),
             ('%s (%s)' % (mls.UI_CONTRACTS_COLLATERAL, mls.UI_CONTRACTS_LOWESTFIRST), (cc.SORT_COLLATERAL, 0)),
             ('%s (%s)' % (mls.UI_CONTRACTS_COLLATERAL, mls.UI_CONTRACTS_HIGHESTFIRST), (cc.SORT_COLLATERAL, 1)),
             ('%s (%s)' % (mls.UI_CONTRACTS_VOLUME, mls.UI_CONTRACTS_LOWESTFIRST), (cc.SORT_VOLUME, 0)),
             ('%s (%s)' % (mls.UI_CONTRACTS_VOLUME, mls.UI_CONTRACTS_HIGHESTFIRST), (cc.SORT_VOLUME, 1))])
        else:
            opt.extend([('%s (%s)' % (mls.UI_CONTRACTS_PRICE, mls.UI_CONTRACTS_LOWESTFIRST), (cc.SORT_PRICE, 0)), ('%s (%s)' % (mls.UI_CONTRACTS_PRICE, mls.UI_CONTRACTS_HIGHESTFIRST), (cc.SORT_PRICE, 1))])
        sel = settings.user.ui.Get('contracts_search_sort', None)
        self.sr.fltSort.LoadOptions(opt, sel)



    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.svc = sm.GetService('contracts')
        self.inited = False
        self.searchThread = None
        self.currPage = 0
        self.numPages = 0
        self.pageData = {}
        self.pages = {0: None}
        self.fetchingContracts = 0
        self.mouseCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        pad = 2 * const.defaultPadding
        self.sr.leftSide = uicls.Container(name='leftSide', parent=self, align=uiconst.TOLEFT, width=LEFT_WIDTH, padding=(pad,
         0,
         pad,
         0))
        self.sr.topContainer = uicls.Container(name='topCont', parent=self, pos=(0, 2, 0, 26), align=uiconst.TOTOP)
        self.sr.viewMode0 = icon = xtriui.MiniButton(icon='ui_38_16_157', selectedIcon='ui_38_16_173', mouseOverIcon='ui_38_16_189', parent=self.sr.topContainer, pos=(6, 10, 16, 16), align=uiconst.TOPLEFT)
        icon.hint = mls.UI_GENERIC_DETAILS
        icon.Click = lambda : self.ChangeViewMode(0)
        self.sr.viewMode1 = icon = xtriui.MiniButton(icon='ui_38_16_158', selectedIcon='ui_38_16_174', mouseOverIcon='ui_38_16_190', parent=self.sr.topContainer, pos=(22, 10, 16, 16), align=uiconst.TOPLEFT)
        icon.hint = mls.UI_GENERIC_LIST
        icon.Click = lambda : self.ChangeViewMode(1)
        self.sr.Get('viewMode%s' % int(prefs.GetValue('contractsSimpleView', 0) or 0), None).Select()
        sortCont = c = uicls.Container(name='sortCont', parent=self.sr.topContainer, pos=(0, 12, 0, 20), align=uiconst.TOTOP)
        sortDirWidth = 62
        self.sr.fltSort = c = uicls.Combo(label=mls.UI_CONTRACTS_SORTPAGESBY, parent=sortCont, options=[], name='sort', align=uiconst.TOPRIGHT, callback=self.ComboChange)
        self.PopulateSortCombo()
        c.width = 160
        c.left = 4
        self.sr.contractlistParent = contractlistParent = uicls.Container(name='contractlistParent', align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), parent=self)
        (hint, icon, isFiltered,) = self.GetClientFilterTextAndIcon()
        if settings.user.ui.Get('contracts_search_expander_clientFilterExpander', 0) and prefs.GetValue('contractsClientFilters', 0):
            filterState = uiconst.UI_PICKCHILDREN
        else:
            filterState = uiconst.UI_HIDDEN
        prefs.SetValue('contractsClientFilters', prefs.GetValue('contractsClientFilters', 0))
        self.sr.filterCont = uicls.Container(name='filterCont', parent=self.sr.contractlistParent, pos=(0, 0, 0, 54), align=uiconst.TOBOTTOM, idx=0, state=filterState)
        expanderCont = uicls.Container(name='clientFilterExpander', parent=self.sr.contractlistParent, pos=(0, 0, 0, 28), align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, padTop=0)
        self.sr.expanderTextCont = uicls.Container(name='expanderTextCont', parent=expanderCont, align=uiconst.TOLEFT, pos=(0, 0, 200, 0), state=uiconst.UI_NORMAL)
        if prefs.GetValue('contractsClientFilters', 0):
            self.sr.expanderTextCont.OnClick = self.ToggleClientFilters
        foundLabelText = '%s' % mls.UI_CONTRACTS_NOSEARCH
        self.sr.foundLabel = uicls.Label(text=foundLabelText, parent=self.sr.expanderTextCont, align=uiconst.TOPLEFT, left=2, top=5, fontsize=9, letterspace=1, linespace=9, uppercase=1)
        self.sr.expanderTextCont.width = self.sr.foundLabel.textwidth + 50
        pageArea = uicls.Container(name='pageArea', parent=expanderCont, pos=(10,
         2,
         25 * PAGINGRANGE + 40,
         20), align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        fwdCont = uicls.Container(name='fwdCont', parent=pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.sr.pageFwdBtn = uicls.IconButton(name='pageFwdBtn', icon='ui_38_16_224', parent=fwdCont, pos=(0, 0, 20, 20), align=uiconst.CENTERRIGHT, iconPos=(-2, 0, 16, 16), iconAlign=uiconst.CENTER, func=self.DoPageNext, state=uiconst.UI_HIDDEN)
        self.sr.pagingCont = uicls.Container(name='pagingCont', parent=pageArea, pos=(0,
         0,
         25 * PAGINGRANGE,
         0), align=uiconst.TORIGHT)
        backCont = uicls.Container(name='backCont', parent=pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.sr.pageBackBtn = uicls.IconButton(name='pageBackBtn', icon='ui_38_16_223', parent=backCont, pos=(0, 0, 20, 20), align=uiconst.CENTERLEFT, iconPos=(0, 0, 16, 16), iconAlign=uiconst.CENTER, func=self.DoPagePrev, state=uiconst.UI_HIDDEN)
        self.sr.pageFilterIcon = uicls.IconButton(name='pageFilterIcon', icon=icon, parent=self.sr.expanderTextCont, hint=hint, pos=(10, 0, 16, 16), align=uiconst.CENTERLEFT)
        self.sr.contractlist = contractlist = uicls.Scroll(parent=contractlistParent, name='contractsearchlist')
        contractlist.sr.id = 'contractlist'
        contractlist.multiSelect = 0
        contractlistParent.top = 5
        contractlist.ShowHint(mls.UI_CONTRACTS_CONTRACTLISTHINT_CLICKSEARCH % {'search': mls.UI_CONTRACTS_SEARCH})
        self.sr.loadingWheel = uicls.LoadingWheel(parent=self.sr.contractlist, align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.sr.loadingWheel.Hide()
        contractlist.sr.defaultColumnWidth = {mls.UI_CONTRACTS_PICKUP: 120,
         mls.UI_CONTRACTS_CONTRACT: 200,
         mls.UI_CONTRACTS_BIDS: 20,
         mls.UI_CONTRACTS_JUMPS: 90,
         mls.UI_CONTRACTS_ROUTE: 80,
         mls.UI_CONTRACTS_VOLUME: 60,
         mls.UI_CONTRACTS_TIMELEFT: 70,
         mls.UI_CONTRACTS_PRICE: 100,
         mls.UI_CONTRACTS_LOCATION: 100,
         mls.UI_CONTRACTS_ISSUER: 100}
        self.InitFilters()



    def GetContractFiltersMenu(self, *args):
        m = []
        m.append((mls.UI_CONTRACTS_EXCLUDEUNREACHABLE, self.ToggleExcludeUnreachable, (None,)))
        m.append((mls.UI_CONTRACTS_EXCLUDEIGNORED, self.ToggleExcludeIgnored, (None,)))
        return m



    def ToggleExcludeUnreachable(self, *args):
        k = 'contracts_search_client_excludeunreachable'
        v = 0 if settings.user.ui.Get(k, 0) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()



    def ToggleExcludeIgnored(self, *args):
        k = 'contracts_search_client_excludeignore'
        v = 0 if settings.user.ui.Get(k, 1) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()



    def InitFilters(self):
        leftSide = self.sr.leftSide
        leftSide.Flush()
        EDIT_WIDTH = 61
        self.sr.caption = uicls.CaptionLabel(text=mls.UI_CONTRACTS_CONTRACTSEARCH, parent=leftSide, align=uiconst.TOTOP, top=4, uppercase=False, letterspace=0)
        contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
        MENU_HEIGHT = 28
        self.sr.menu = uicls.Container(name='menu', parent=leftSide, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         MENU_HEIGHT), padding=(2, 0, 2, 0))
        tabs = [[mls.UI_CONTRACTS_BUYANDSELL,
          None,
          self,
          None,
          cc.CONTYPE_AUCTIONANDITEMECHANGE], [mls.UI_CONTRACTS_COURIER,
          None,
          self,
          None,
          const.conTypeCourier]]
        self.pushButtons = uicls.FlatButtonGroup(parent=self.sr.menu, align=uiconst.TOTOP, toggleEnabled=False)
        self.pushButtons.Startup(tabs, selectedArgs=[contractType])
        if contractType != const.conTypeCourier:
            typeCont = uicls.Container(name='typeCont', parent=leftSide, pos=(0, -12, 0, 41), align=uiconst.TOTOP)
            self.sr.typeName = c = uicls.SinglelineEdit(name='type', parent=typeCont, label='', hinttext=mls.UI_CONTRACTS_ITEMTYPE, setvalue=settings.user.ui.Get('contracts_search_typename', ''), align=uiconst.TOTOP, padTop=20, OnReturn=self.DoSearch, OnChange=self.GetTypeClearIcon)
            self.sr.fltTypeClear = uicls.IconButton(icon='ui_73_16_210', parent=c, pos=(6, 0, 16, 16), align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, idx=0, hint=mls.UI_CMD_CLEAR, func=self.ClearEditField, args=(c,))
            self.GetTypeClearIcon(text=c.GetValue())
            self.sr.typeName.OnDropData = self.OnDropType
        locationCont = uicls.Container(name='locationCont', parent=leftSide, padTop=-3, height=40, align=uiconst.TOTOP)
        self.sr.fltLocation = c = uicls.Combo(label=mls.UI_GENERIC_LOCATION, parent=locationCont, options=[], name='location', callback=self.ComboChange, align=uiconst.TOTOP, padTop=20)
        self.PopulateLocationCombo()
        self.sr.advancedCont = advancedCont = uicls.Container(name='advancedCont', parent=leftSide, padTop=const.defaultPadding, align=uiconst.TOTOP)
        expanded = settings.user.ui.Get('contracts_search_expander_advanced', 0)
        self.sr.advancedDivider = self.GetExpanderDivider(leftSide, 'advanced', mls.UI_RMR_SHOWLESSOPTIONS, mls.UI_RMR_SHOWMOREOPTIONS, expanded, self.sr.advancedCont, padTop=const.defaultPadding)
        if contractType != const.conTypeCourier:
            contractOptions = [(mls.UI_CONTRACTS_ALL, None),
             (mls.UI_CONTRACTS_SELLCONTRACTS, 2),
             (mls.UI_CONTRACTS_WANTTOBUYCONTRACTS, 3),
             (mls.UI_CONTRACTS_AUCTIONCONTRACTS, 1),
             (mls.UI_CONTRACTS_EXCLUDEWTB, 4)]
            self.sr.fltContractOptions = c = uicls.Combo(label=mls.UI_CONTRACTS_CONTRACTTYPE, parent=advancedCont, options=contractOptions, name='contractOptions', select=settings.user.ui.Get('contracts_search_contractOptions', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=17)
            catOptions = [(mls.UI_CONTRACTS_ALL, None)]
            categories = []
            principalCategories = [const.categoryBlueprint, const.categoryModule, const.categoryShip]
            for c in cfg.invcategories:
                if c.categoryID > 0 and c.published and c.categoryID not in principalCategories:
                    categories.append([c.categoryName, c.categoryID, 0])

            categories.sort()
            for catID in principalCategories:
                c = cfg.invcategories.Get(catID)
                catOptions.append([c.categoryName, (c.categoryID, 0)])
                if c.categoryID == const.categoryBlueprint:
                    catOptions.append([c.categoryName + ' %s' % mls.UI_GENERIC_ORIGINAL, (c.categoryID, cc.SEARCHHINT_BPO)])
                    catOptions.append([c.categoryName + ' %s' % mls.UI_GENERIC_COPY, (c.categoryID, cc.SEARCHHINT_BPC)])

            catOptions.append(['', -1])
            for c in categories:
                catOptions.append((c[0], (c[1], c[2])))

            self.sr.fltCategories = c = uicls.Combo(label=mls.UI_CONTRACTS_CATEGORY, parent=advancedCont, options=catOptions, name='category', select=settings.user.ui.Get('contracts_search_category', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=17)
            grpOptions = [(mls.UI_CONTRACTS_SELECTCATEGORY, None)]
            self.sr.fltGroups = c = uicls.Combo(label=mls.UI_CONTRACTS_GROUP, parent=advancedCont, options=grpOptions, name='group', select=settings.user.ui.Get('contracts_search_group', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=20)
            self.sr.fltExcludeMultiple = c = uicls.Checkbox(text=mls.UI_CONTRACTS_EXCLUDEMULTIPLEITEMS, configName='contracts_search_excludemultiple', checked=settings.user.ui.Get('contracts_search_excludemultiple', 0), parent=advancedCont, callback=self.CheckBoxChange, padTop=4, align=uiconst.TOTOP)
            self.sr.fltExactType = c = uicls.Checkbox(text=mls.UI_CONTRACTS_EXACTTYPEMATCH, configName='contracts_search_exacttype', checked=settings.user.ui.Get('contracts_search_exacttype', 0), parent=advancedCont, callback=self.CheckBoxChange)
            self.PopulateGroupCombo(isSel=True)
            self.sr.priceCont = cont = uicls.Container(name='priceCont', parent=advancedCont, padTop=19, height=20, align=uiconst.TOTOP)
            self.sr.fltMinPrice = c = uicls.SinglelineEdit(name='minprice', parent=cont, label=mls.UI_CONTRACTS_PRICE_MILLION, width=EDIT_WIDTH, align=uiconst.TOPLEFT, hinttext=mls.UI_CONTRACTS_MIN, ints=(None, None), setvalue=settings.user.ui.Get('contracts_search_minprice', ''), OnReturn=self.DoSearch)
            uicls.Label(text=mls.UI_GENERIC_TONUMBER, parent=cont, align=uiconst.CENTER, fontsize=9, letterspace=1, linespace=9, uppercase=1)
            self.sr.fltMaxPrice = c = uicls.SinglelineEdit(name='maxprice', parent=cont, width=EDIT_WIDTH, align=uiconst.TOPRIGHT, label='', hinttext=mls.UI_CONTRACTS_MAX, ints=(None, None), setvalue=settings.user.ui.Get('contracts_search_maxprice', ''), OnReturn=self.DoSearch)
        options = [(mls.UI_CONTRACTS_PUBLIC, const.conAvailPublic), (mls.UI_CONTRACTS_MYSELF, const.conAvailMyself)]
        if not util.IsNPC(session.corpid):
            options.append((mls.UI_CONTRACTS_MYCORP, const.conAvailMyCorp))
        if session.allianceid:
            options.append((mls.UI_CONTRACTS_MYALLIANCE, const.conAvailMyAlliance))
        if contractType == const.conTypeCourier:
            dropoffCont = uicls.Container(name='dropoffCont', parent=advancedCont, padTop=9, height=20, align=uiconst.TOTOP)
            w = 22 + 2 * const.defaultPadding
            self.sr.fltDropOff = c = uicls.SinglelineEdit(name='dropoff', parent=dropoffCont, setvalue=settings.user.ui.Get('contracts_search_dropoff', ''), align=uiconst.TOTOP, label='', padRight=w, hinttext=mls.UI_CONTRACTS_DROPOFFLOCATION, OnChange=self.GetDropOffClearIcon, OnReturn=self.OnDropOffReturn)
            self.sr.fltDropOffClear = uicls.IconButton(icon='ui_73_16_210', parent=c, pos=(6, 0, 16, 16), align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, idx=0, hint=mls.UI_CMD_CLEAR, func=self.ClearEditField, args=(c,))
            self.GetDropOffClearIcon(text=c.GetValue())
            buttonbox = uicls.Container(name='buttonbox', align=uiconst.TOPRIGHT, parent=dropoffCont, pos=(0, 1, 20, 20))
            btn = uix.GetBigButton(10, buttonbox, width=20, height=20)
            btn.sr.icon.LoadIcon('ui_38_16_228')
            btn.OnClick = self.ParseDropOff
            self.sr.rewardCont = rewardCont = uicls.Container(name='rewardCont', parent=advancedCont, padTop=19, height=20, align=uiconst.TOTOP)
            self.sr.fltMinReward = c = uicls.SinglelineEdit(name='minreward', parent=rewardCont, width=EDIT_WIDTH, label=mls.UI_CONTRACTS_REWARD_MILLION, hinttext=mls.UI_CONTRACTS_MIN, left=0, top=0, ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_minreward', ''), OnReturn=self.DoSearch)
            uicls.Label(text=mls.UI_GENERIC_TONUMBER, parent=rewardCont, align=uiconst.TOPLEFT, pos=(c.width + 8,
             4,
             10,
             0), fontsize=9, letterspace=1, linespace=9, uppercase=1)
            self.sr.fltMaxReward = c = uicls.SinglelineEdit(name='maxreward', parent=rewardCont, label='', hinttext=mls.UI_CONTRACTS_MAX, align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_maxreward', ''), OnReturn=self.DoSearch)
            self.sr.collateralCont = cont = uicls.Container(name='collateralCont', parent=advancedCont, pos=(0, 17, 0, 20), align=uiconst.TOTOP)
            self.sr.fltMinCollateral = c = uicls.SinglelineEdit(name='mincollateral', parent=cont, pos=(0,
             0,
             EDIT_WIDTH,
             0), label=mls.UI_CONTRACTS_COLLATERAL_MILLION, hinttext=mls.UI_CONTRACTS_MIN, ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_mincollateral', ''), OnReturn=self.DoSearch)
            uicls.Label(text=mls.UI_GENERIC_TONUMBER, parent=cont, align=uiconst.TOPLEFT, width=10, left=c.width + 8, top=4, fontsize=9, letterspace=1, linespace=9, uppercase=1)
            self.sr.fltMaxCollateral = c = uicls.SinglelineEdit(name='maxcollateral', parent=cont, align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), label='', hinttext=mls.UI_CONTRACTS_MAX, ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_maxcollateral', ''), OnReturn=self.DoSearch)
            self.sr.volumeCont = cont = uicls.Container(name='volumeCont', parent=advancedCont, pos=(0, 17, 0, 20), align=uiconst.TOTOP)
            self.sr.fltMinVolume = c = uicls.SinglelineEdit(name='minvolume', parent=cont, pos=(0,
             0,
             EDIT_WIDTH,
             0), label=mls.UI_CONTRACTS_VOLUME, hinttext=mls.UI_CONTRACTS_MIN, ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_minvolume', ''), OnReturn=self.DoSearch)
            uicls.Label(text=mls.UI_GENERIC_TONUMBER, parent=cont, align=uiconst.TOPLEFT, width=10, left=c.width + 8, top=4, fontsize=9, letterspace=1, linespace=9, uppercase=1)
            self.sr.fltMaxVolume = c = uicls.SinglelineEdit(name='maxvolume', parent=cont, align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), label='', hinttext=mls.UI_CONTRACTS_MAX, ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_maxvolume', ''), OnReturn=self.DoSearch)
        contractAvailability = settings.user.ui.Get('contracts_search_avail', const.conAvailPublic)
        self.sr.fltAvail = c = uicls.Combo(label=mls.UI_CONTRACTS_AVAILABILITY, parent=advancedCont, options=options, name='avail', select=contractAvailability, callback=self.ComboChange, align=uiconst.TOTOP, pos=(0, 18, 140, 20))
        securityCont = c = uicls.Container(name='securityCont', parent=advancedCont, pos=(0, 6, 0, 30), align=uiconst.TOTOP)
        c = uicls.Label(text=mls.UI_CONTRACTS_SECURITYFILTERS, parent=securityCont, left=5, top=0, fontsize=10, letterspace=1, uppercase=1, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT)
        self.sr.fltSecHigh = c = uicls.Checkbox(text=mls.UI_GENERIC_HIGH, configName='contracts_search_sechigh', checked=settings.user.ui.Get('contracts_search_sechigh', 1), parent=securityCont, callback=self.CheckBoxChange, width=55, left=const.defaultPadding, top=12, align=uiconst.TOPLEFT)
        self.sr.fltSecLow = c = uicls.Checkbox(text=mls.UI_GENERIC_LOW, configName='contracts_search_seclow', checked=settings.user.ui.Get('contracts_search_seclow', 1), parent=securityCont, callback=self.CheckBoxChange, width=55, left=c.left + c.width + 5, top=12, align=uiconst.TOPLEFT)
        self.sr.fltSecNull = c = uicls.Checkbox(text=mls.UI_GENERIC_ZERO, configName='contracts_search_secnull', checked=settings.user.ui.Get('contracts_search_secnull', 1), parent=securityCont, callback=self.CheckBoxChange, width=55, left=c.left + c.width + 5, top=12, align=uiconst.TOPLEFT)
        issuerCont = uicls.Container(name='issuerCont', parent=advancedCont, pos=(0, 6, 0, 20), align=uiconst.TOTOP)
        w = 22 + 2 * const.defaultPadding
        self.sr.fltIssuer = c = uicls.SinglelineEdit(name='issuer', parent=issuerCont, setvalue=settings.user.ui.Get('contracts_search_issuer', ''), align=uiconst.TOTOP, padding=(0,
         0,
         w,
         0), hinttext=mls.UI_CONTRACTS_ISSUER, OnReturn=self.OnIssuerReturn, OnChange=self.GetIssuerClearIcon)
        self.sr.fltIssuerClear = uicls.IconButton(icon='ui_73_16_210', parent=c, pos=(6, 0, 16, 16), align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, idx=0, hint=mls.UI_CMD_CLEAR, func=self.ClearEditField, args=(c,))
        self.GetIssuerClearIcon(text=c.GetValue())
        self.sr.fltIssuer.OnDropData = self.OnDropIssuer
        buttonbox = uicls.Container(name='buttonbox', align=uiconst.TOPRIGHT, parent=issuerCont, pos=(0, 1, 20, 20))
        btn = uix.GetBigButton(10, buttonbox, width=20, height=20)
        btn.sr.icon.LoadIcon('ui_38_16_228')
        btn.OnClick = self.ParseIssuers
        for each in ['fltMinPrice',
         'fltMaxPrice',
         'fltMinReward',
         'fltMaxReward',
         'fltMinCollateral',
         'fltMaxCollateral',
         'fltMinVolume',
         'fltMaxVolume']:
            wnd = getattr(self.sr, each, None)
            try:
                if not settings.user.ui.Get('contracts_search_%s' % wnd.name, ''):
                    wnd.SetText('')
                    wnd.CheckHintText()
            except:
                sys.exc_clear()

        advancedCont.height = sum([ each.height + each.padTop + each.padBottom + each.top for each in advancedCont.children ])
        self.sr.filterCont.Flush()
        uicls.Frame(parent=self.sr.filterCont, color=(0.5, 0.5, 0.5, 0.2))
        leftCont = uicls.Container(name='leftCont', parent=self.sr.filterCont, pos=(14, 0, 220, 0), align=uiconst.TOLEFT)
        rightCont = uicls.Container(name='rightCont', parent=self.sr.filterCont, pos=(0, 0, 0, 0), align=uiconst.TOALL)
        self.sr.fltClientExcludeUnreachable = c = uicls.Checkbox(text=mls.UI_CONTRACTS_EXCLUDEUNREACHABLE, configName='contracts_search_client_excludeunreachable', checked=settings.user.ui.Get('contracts_search_client_excludeunreachable', 0), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        self.sr.fltClientExcludeIgnore = c = uicls.Checkbox(text=mls.UI_CONTRACTS_EXCLUDEIGNORED, configName='contracts_search_client_excludeignore', checked=settings.user.ui.Get('contracts_search_client_excludeignore', 1), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        self.sr.fltClientOnlyCurrentSecurity = c = uicls.Checkbox(text=mls.UI_CONTRACTS_ONLYCURRENTSECURITY, configName='contracts_search_client_currentsecurity', checked=settings.user.ui.Get('contracts_search_client_currentsecurity', 0), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        jumpSettings = settings.user.ui.Get('contracts_search_client_maxjumps', 0)
        self.sr.fltClientMaxJumps = c = uicls.Checkbox(text=mls.UI_CONTRACTS_MAXIMUMJUMPS, configName='maxjumps', checked=jumpSettings, parent=rightCont, callback=self.FilterCheckBoxChange, pos=(0, 6, 160, 20), align=uiconst.TOPLEFT)
        numJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', 10)
        self.sr.maxjumpsInput = c = uicls.SinglelineEdit(name='maxjumpsInput', parent=rightCont, align=uiconst.TOPLEFT, pos=(self.sr.fltClientMaxJumps.width + 20,
         5,
         40,
         10), label='', setvalue=str(numJumps), hinttext=mls.UI_CONTRACTS_MAX, ints=(0, MAXJUMPROUTENUM), OnReturn=self.OnJumpInputReturn, OnFocusLost=self.OnJumpFocusLost)
        if not jumpSettings:
            c.Disable()
        cLabel = self.sr.fltClientMaxJumps.sr.label
        inputLeft = cLabel.textwidth + cLabel.left
        if contractType == const.conTypeCourier:
            routeSettings = settings.user.ui.Get('contracts_search_client_maxroute', 0)
            self.sr.fltClientMaxRoute = c = uicls.Checkbox(text=mls.UI_CONTRACTS_MAXROUTE, configName='maxroute', checked=routeSettings, parent=rightCont, callback=self.FilterCheckBoxChange, pos=(0, 32, 160, 30), align=uiconst.TOPLEFT)
            cLabel = self.sr.fltClientMaxRoute.sr.label
            inputLeft = max(inputLeft, cLabel.textwidth + cLabel.left)
            self.sr.fltClientMaxRoute.width = inputLeft
            numRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', 10)
            self.sr.maxrouteInput = c = uicls.SinglelineEdit(name='maxrouteInput', parent=rightCont, align=uiconst.TOPLEFT, pos=(inputLeft + 30,
             31,
             40,
             10), label='', setvalue=numRoute, hinttext=mls.UI_CONTRACTS_MAX, ints=(0, MAXJUMPROUTENUM), OnReturn=self.OnRouteInputReturn, OnFocusLost=self.OnRouteFocusLost)
            if not routeSettings:
                c.Disable()
        self.sr.fltClientMaxJumps.width = inputLeft
        self.sr.maxjumpsInput.left = inputLeft + 30
        (hint, icon, isFiltered,) = self.GetClientFilterTextAndIcon()
        self.sr.pageFilterIcon.hint = hint
        self.sr.pageFilterIcon.LoadIcon(icon)
        self.sr.pageFilterIcon.state = uiconst.UI_HIDDEN
        buttonbox = uicls.Container(name='buttonbox', align=uiconst.TOBOTTOM, parent=leftSide, pos=(0, 0, 0, 40), idx=0)
        self.sr.SearchButton = btn = uix.GetBigButton(10, buttonbox, width=140, height=32)
        btn.SetInCaption(mls.UI_CONTRACTS_SEARCH)
        btn.SetAlign(uiconst.CENTER)
        btn.OnClick = self.DoSearch
        self.inited = True



    def SetInitialFocus(self):
        uicore.registry.SetFocus(self.sr.contractlist)



    def OnButtonSelected(self, mode):
        if mode == settings.user.ui.Get('contracts_search_type', const.conTypeItemExchange):
            return 
        settings.user.ui.Set('contracts_search_type', mode)
        self.PopulateSortCombo()
        uthread.new(self.InitFilters)



    def ComboChange(self, wnd, *args):
        settings.user.ui.Set('contracts_search_%s' % wnd.name, wnd.GetValue())
        if wnd.name == 'category':
            self.PopulateGroupCombo()
        elif wnd.name == 'type':
            self.InitFilters()
        elif wnd.name == 'location':
            v = wnd.GetValue()
            if v == 10:
                self.PickLocation()
        elif wnd.name == 'sort':
            val = wnd.GetValue()
            sortBy = {cc.SORT_ID: mls.UI_CONTRACTS_CREATED,
             cc.SORT_EXPIRED: mls.UI_CONTRACTS_TIMELEFT,
             cc.SORT_PRICE: mls.UI_CONTRACTS_PRICE,
             cc.SORT_REWARD: mls.UI_CONTRACTS_REWARD,
             cc.SORT_COLLATERAL: mls.UI_CONTRACTS_COLLATERAL}.get(val[0], mls.UI_CONTRACTS_CREATED)
            pr = settings.user.ui.Get('scrollsortby_%s' % uiconst.SCROLLVERSION, {})
            pr[self.sr.contractlist.sr.id] = (sortBy, not not val[1])
            if self.currPage in self.pageData:
                self.DoSearch()



    def PickLocation(self):
        desc = mls.UI_CONTRACTS_ENTERLOCATIONNAME
        ret = uix.NamePopup(mls.UI_CONTRACTS_ENTERNAME_HEADER, desc, '', maxLength=20)
        if ret:
            name = ret['name'].lower()
            locationID = self.SearchLocation(name)
            if locationID:
                self.DoPickLocation(locationID)



    def DoPickLocation(self, locationID):
        settings.user.ui.Set('contracts_search_location', locationID)
        customLocations = settings.user.ui.Get('contracts_search_customlocations', [])
        loc = (cfg.evelocations.Get(locationID).name, locationID)
        try:
            customLocations.remove(loc)
        except:
            pass
        customLocations.append(loc)
        if len(customLocations) > NUM_SAVED_LOCATIONS:
            del customLocations[0]
        settings.user.ui.Set('contracts_search_customlocations', customLocations)
        self.PopulateLocationCombo()



    def CheckBoxChange(self, wnd, *args):
        pass



    def OnGlobalMouseUp(self, obj, msgID, param):
        if uicore.uilib.mouseOver is self.sr.secCont or uiutil.IsUnder(obj, self.sr.secCont):
            return 1
        return 1



    def GetClientFilterTextAndIcon(self, *args):
        contractType = settings.user.ui.Get('contracts_search_type', const.conTypeItemExchange)
        excluded = ''
        for (each, text, default,) in [('excludeunreachable', mls.UI_CONTRACTS_CLIENTFILTER_EXCLUDEUNREACHABLE, 1), ('excludeignore', mls.UI_CONTRACTS_CLIENTFILTER_EXCLUDEIGNORE, 1), ('currentsecurity', mls.UI_CONTRACTS_CLIENTFILTER_ONLYCURRENTSEC, 0)]:
            isChecked = settings.user.ui.Get('contracts_search_client_%s' % each, default)
            if isChecked is None:
                continue
            if isChecked:
                excluded += '<br>%s' % text

        isChecked = settings.user.ui.Get('contracts_search_client_maxjumps', None)
        if isChecked:
            maxJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', '-')
            excluded += '<br>%s (%s)' % (mls.UI_CONTRACTS_CLIENTFILTER_MAXJUMPS, maxJumps)
        if contractType == const.conTypeCourier:
            isChecked = settings.user.ui.Get('contracts_search_client_maxroute', None)
            if isChecked:
                maxRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', '-')
                excluded += '<br>%s (%s)' % (mls.UI_CONTRACTS_CLIENTFILTER_MAXROUTE, maxRoute)
        hintText = '<b>%s</b>' % mls.UI_CONTRACTS_PAGEFILTER
        if excluded:
            hintText += excluded
            icon = 'ui_38_16_205'
        else:
            hintText += '<br>%s' % mls.UI_STATION_SHOWALL
            icon = 'ui_38_16_204'
        return (hintText, icon, bool(excluded))



    def UpdatePaging(self, currentPage, numPages):
        self.sr.pagingCont.Flush()
        if numPages == 1:
            self.sr.pageBackBtn.state = uiconst.UI_HIDDEN
            self.sr.pageFwdBtn.state = uiconst.UI_HIDDEN
            return 
        currentRange = (currentPage - 1) / PAGINGRANGE * PAGINGRANGE
        pages = []
        for i in xrange(0, PAGINGRANGE):
            page = currentRange + i
            if page >= numPages:
                break
            pages.append(page)

        left = 0
        for pageNum in pages:
            pageCont = uicls.IconButton(name='pageNum', parent=self.sr.pagingCont, pos=(left,
             0,
             20,
             0), align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padTop=0, func=self.GoToPage, args=(pageNum,))
            pageName = pageNum + 1
            if pageNum + 1 == currentPage:
                f = uicls.Frame(parent=pageCont, frameConst=uiconst.FRAME_BORDER2_CORNER0)
                f.SetAlpha(1.0)
                bold = 1
            else:
                f = uicls.Frame(parent=pageCont, frameConst=uiconst.FRAME_BORDER1_CORNER0)
                bold = 0
            uicls.Label(text=pageName, parent=pageCont, pos=(1, 1, 0, 0), align=uiconst.CENTER, fontsize=13, bold=bold)
            left = 5

        backState = uiconst.UI_NORMAL
        if currentPage <= 1:
            backState = uiconst.UI_HIDDEN
        fwdState = uiconst.UI_NORMAL
        if currentPage >= numPages:
            fwdState = uiconst.UI_HIDDEN
        self.sr.pageBackBtn.state = backState
        self.sr.pageFwdBtn.state = fwdState
        self.sr.pagingCont.width = 25 * len(pages) - 5



    def GetExpanderDivider(self, parent, name, onText, offText, nowExpanded, collapsingCont, belowCollapsed = 1, padTop = 0, *args):
        expanderCont = uicls.Container(name=name, parent=parent, height=18, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=padTop)
        expanderCont.onText = onText
        expanderCont.offText = offText
        expanderCont.collapsingCont = collapsingCont
        if not belowCollapsed:
            expanderCont.SetAlign(uiconst.TOBOTTOM)
        expandText = [offText, onText][nowExpanded]
        expanderCont.label = uicls.Label(text=expandText, parent=expanderCont, height=12, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=4)
        expanderCont.OnClick = (self.ToggleAdvanced, expanderCont)
        expanderCont.expander = expander = uicls.IconButton(icon='', parent=expanderCont, pos=(4, 4, 11, 11), align=uiconst.TOPRIGHT, ignoreSize=True, func=self.ToggleAdvanced, args=(expanderCont,))
        icon = expander.sr.icon
        if nowExpanded:
            icon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
        else:
            icon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
        collapsingCont.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][nowExpanded]
        return expanderCont



    def ToggleAdvanced(self, expanderCont, force = None, *args):
        settingsName = 'contracts_search_expander_%s' % expanderCont.name
        if force is None:
            expanded = not settings.user.ui.Get(settingsName, 0)
        else:
            expanded = force
        settings.user.ui.Set(settingsName, expanded)
        if expanded:
            expanderCont.expander.sr.icon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
        else:
            expanderCont.expander.sr.icon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
        expanderCont.label.text = [expanderCont.offText, expanderCont.onText][expanded]
        if expanded:
            expanderCont.collapsingCont.state = uiconst.UI_PICKCHILDREN
        else:
            expanderCont.collapsingCont.state = uiconst.UI_HIDDEN



    def ToggleClientFilters(self, *args):
        settingsName = 'contracts_search_expander_clientFilterExpander'
        expanded = not settings.user.ui.Get(settingsName, 0)
        settings.user.ui.Set(settingsName, expanded)
        if expanded:
            self.sr.filterCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.filterCont.state = uiconst.UI_HIDDEN



    def FilterCheckBoxChange(self, cb, *args):
        if cb.name in ('maxjumps', 'maxroute'):
            cfgname = 'contracts_search_client_%s' % cb.name
            cfgnameNum = '%s_num' % cfgname
            inputField = getattr(self.sr, '%sInput' % cb.name, None)
            if cb.checked:
                inputField.Enable()
                input = inputField.GetValue()
                num = min(input, MAXJUMPROUTENUM)
                inputField.SetValue(str(num))
                settings.user.ui.Set(cfgname, 1)
                settings.user.ui.Set(cfgnameNum, num)
            else:
                inputField.Disable()
                settings.user.ui.Set(cfgname, 0)
        if self.currPage in self.pageData:
            self.RenderPage()
        (hint, icon, isFiltered,) = self.GetClientFilterTextAndIcon()
        self.sr.pageFilterIcon.hint = hint
        self.sr.pageFilterIcon.LoadIcon(icon)



    def OnJumpInputReturn(self, *args):
        value = min(self.sr.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxjumps_num', value)
        if self.currPage in self.pageData:
            self.RenderPage()



    def OnJumpFocusLost(self, *args):
        value = min(self.sr.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxjumps_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()



    def OnRouteInputReturn(self, *args):
        value = min(self.sr.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxroute_num', value)
        if self.currPage in self.pageData:
            self.RenderPage()



    def OnRouteFocusLost(self, *args):
        value = min(self.sr.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxroute_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()



    def OnIssuerReturn(self, *args):
        self.ParseIssuers()
        self.DoSearch()



    def OnDropOffReturn(self, *args):
        self.ParseDropOff()
        self.DoSearch()



    def OnDropIssuer(self, dragObj, nodes):
        node = nodes[0]
        if node.Get('__guid__', None) not in ('listentry.User', 'listentry.Sender', 'listentry.ChatUser', 'listentry.SearchedUser'):
            return 
        charID = node.charID
        if util.IsCharacter(charID) or util.IsCorporation(charID):
            issuerName = cfg.eveowners.Get(charID).name
            self.sr.fltIssuer.SetValue(issuerName)



    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        typeID = None
        if guid in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem'):
            typeID = getattr(node, 'typeID', None)
        if typeID:
            typeName = cfg.invtypes.Get(typeID).name
            self.sr.typeName.SetValue(typeName)
            self.sr.fltExactType.SetChecked(1, 0)



    def PopulateLocationCombo(self):
        self.locationOptions = [(mls.UI_CONTRACTS_CURRENTSTATION, 0),
         (mls.UI_CONTRACTS_CURRENTSOLARSYSTEM, 1),
         (mls.UI_CONTRACTS_CURRENTCONSTELLATION, 3),
         (mls.UI_CONTRACTS_CURRENTREGION, 2),
         (mls.UI_CONTRACTS_ALLREGIONS, 7),
         (mls.UI_CONTRACTS_PICKLOCATION, 10)]
        settingsLocationID = settings.user.ui.Get('contracts_search_location', 2)
        customLocations = settings.user.ui.Get('contracts_search_customlocations', [])
        customLocations.reverse()
        if customLocations:
            mrk = ''
            self.locationOptions.append((mrk, None))
            for l in customLocations:
                self.locationOptions.append((l[0], l[1]))

        if settingsLocationID is not None and settingsLocationID > 100:
            try:
                self.locationOptions.insert(0, (cfg.evelocations.Get(settingsLocationID).name, settingsLocationID))
            except:
                pass
        self.sr.fltLocation.LoadOptions(self.locationOptions, settingsLocationID)



    def PopulateGroupCombo(self, isSel = False):
        v = self.sr.fltCategories.GetValue()
        categoryID = v[0] if v and v != -1 else None
        groups = [(mls.UI_CONTRACTS_SELECTCATEGORY, None)]
        if categoryID:
            groups = [(mls.UI_CONTRACTS_ALL, None)]
            if categoryID in cfg.groupsByCategories:
                groupsByCategory = cfg.groupsByCategories[categoryID].Copy()
                groupsByCategory.Sort('groupName')
                for g in groupsByCategory:
                    if g.published:
                        groups.append((cfg.invgroups.Get(g.groupID).name, g.groupID))

        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_search_group', None)
        self.sr.fltGroups.LoadOptions(groups, sel)
        if categoryID is None:
            self.sr.fltGroups.state = uiconst.UI_HIDDEN
        else:
            self.sr.fltGroups.state = uiconst.UI_NORMAL



    def Load(self, args):
        if not self.inited:
            return 



    def Height(self):
        return self.height or self.absoluteBottom - self.absoluteTop



    def Width(self):
        return self.width or self.absoluteRight - self.absoluteLeft



    def ShowLoad(self):
        sm.GetService('window').GetWindow('contracts').ShowLoad()



    def HideLoad(self):
        sm.GetService('window').GetWindow('contracts').HideLoad()



    def DoSearch(self, *args):
        if self.sr.SearchButton.state == uiconst.UI_DISABLED:
            raise UserError('ConPleaseWait')
        self.pageData = {}
        self.sr.SearchButton.state = uiconst.UI_DISABLED
        self.sr.SearchButton.SetInCaption('<color=gray>' + mls.UI_CONTRACTS_SEARCH + '</color>')
        uthread.new(self.EnableSearchButton)
        self.ShowLoad()
        try:
            self.SearchContracts(reset=True)

        finally:
            self.HideLoad()
            self.IndicateLoading(loading=0)




    def EnableSearchButton(self):
        blue.pyos.synchro.Sleep(2000)
        try:
            self.sr.SearchButton.state = uiconst.UI_NORMAL
            self.sr.SearchButton.SetInCaption(mls.UI_CONTRACTS_SEARCH)
        except:
            pass



    def GoToPage(self, pageNum):
        if pageNum < 0:
            return 
        if pageNum >= self.numPages:
            return 
        self.currPage = pageNum
        self.DoPage(nav=0)



    def DoPagePrev(self, *args):
        self.DoPage(-1)



    def DoPageNext(self, *args):
        self.DoPage(1)



    def DoPage(self, nav = 1, *args):
        p = self.currPage + nav
        if p < 0:
            return 
        if p >= self.numPages:
            return 
        self.currPage = p
        if self.currPage in self.pageData:
            self.svc.LogInfo('Page', self.currPage, 'found in cache')
            self.RenderPage()
            return 
        self.svc.LogInfo('Page', self.currPage, 'not found in cache')
        if self.searchThread:
            self.searchThread.kill()
        self.searchThread = uthread.new(self.DoPageThread)



    def DoPageThread(self):
        self.IndicateLoading(loading=1)
        blue.pyos.synchro.Sleep(500)
        self.SearchContracts(page=self.currPage)



    def GetIssuerClearIcon(self, text, *args):
        if len(text) >= 3:
            self.sr.fltIssuerClear.state = uiconst.UI_NORMAL
        else:
            self.sr.fltIssuerClear.state = uiconst.UI_HIDDEN



    def GetTypeClearIcon(self, text, *args):
        if len(text) >= 3:
            self.sr.fltTypeClear.state = uiconst.UI_NORMAL
        else:
            self.sr.fltTypeClear.state = uiconst.UI_HIDDEN



    def GetDropOffClearIcon(self, text, *args):
        if len(text) >= 3:
            self.sr.fltDropOffClear.state = uiconst.UI_NORMAL
        else:
            self.sr.fltDropOffClear.state = uiconst.UI_HIDDEN



    def ClearEditField(self, editField, *args):
        editField.SetValue('')



    def GetIssuer(self, string):
        ownerID = uix.Search(string.lower(), const.groupCharacter, const.categoryOwner, hideNPC=1, filterGroups=[const.groupCharacter, const.groupCorporation], searchWndName='contractIssuerSearch')
        if ownerID:
            return (cfg.eveowners.Get(ownerID).name, ownerID)
        return (string, None)



    def ParseIssuers(self, *args):
        if self.destroyed:
            return 
        wnd = self.sr.fltIssuer
        if not wnd or wnd.destroyed:
            return 
        name = wnd.GetValue().strip()
        if not name:
            return 
        (name, id,) = self.GetIssuer(name)
        if name and id:
            wnd.SetValue(name)



    def GetLocationGroupID(self, locationID):
        if util.IsSolarSystem(locationID):
            return const.groupSolarSystem
        if util.IsConstellation(locationID):
            return const.groupConstellation
        if util.IsRegion(locationID):
            return const.groupRegion



    def ParseDropOff(self, *args):
        if self.destroyed:
            return 
        wnd = self.sr.fltDropOff
        if not wnd or wnd.destroyed:
            return 
        name = wnd.GetValue().strip().lower()
        locationID = self.SearchLocation(name)
        if locationID:
            name = cfg.evelocations.Get(locationID).name
            wnd.SetValue(name)



    def SearchLocation(self, name):
        if not name:
            return None
        else:
            if len(name) < 3:
                raise UserError('ConNeedAtLeastThreeLetters')
            foundList = []
            for l in cfg.evelocations:
                groupID = self.GetLocationGroupID(l.locationID)
                if not groupID:
                    continue
                groupName = {const.groupSolarSystem: mls.UI_GENERIC_SOLARSYSTEM,
                 const.groupConstellation: mls.UI_GENERIC_CONSTELLATION,
                 const.groupRegion: mls.UI_GENERIC_REGION}.get(groupID, '')
                if l.name.lower().startswith(name):
                    foundList.append(('%s (%s)' % (l.name, groupName), l.locationID, const.typeSolarSystem))

            if not foundList:
                raise UserError('NoLocationFound', {'name': name})
            if len(foundList) == 1:
                chosen = foundList[0]
            else:
                chosen = uix.ListWnd(foundList, '', mls.UI_GENERIC_SELECTLOCATION, mls.UI_GENERIC_LOCATIONSEARCHHINT % {'num': len(foundList)}, 1, minChoices=1, isModal=1, windowName='locationsearch', unstackable=1)
            if chosen:
                return chosen[1]
            return None



    def GetLocationIDFromName(self, name):
        for l in cfg.evelocations:
            if self.GetLocationGroupID(l.locationID) and l.name.lower() == name.lower():
                return l.locationID




    def ResetTypeFilters(self):
        self.sr.typeName.SetValue('')
        self.sr.fltExactType.SetChecked(0, 0)
        self.sr.fltCategories.SelectItemByValue(None)
        settings.user.ui.Set('contracts_search_category', None)
        self.PopulateGroupCombo()



    def ResetFields(self, *args):
        fields = ['fltMaxPrice',
         'fltMinPrice',
         'fltMaxVolume',
         'fltMinVolume',
         'fltMaxCollateral',
         'fltMinCollateral',
         'fltMinReward',
         'fltMaxReward']
        for name in fields:
            field = getattr(self.sr, name, None)
            if field is None or field.dead:
                continue
            field.SetValue('')
            field.SetText('')
            field.CheckHintText()

        if self.sr.fltDropOf:
            self.sr.fltDropOff.SetValue('')
        if self.sr.fltIssuer:
            self.sr.fltIssuer.SetValue('')
        try:
            if self.sr.fltDropOff:
                self.sr.fltDropOff.SetValue('')
        except:
            pass



    def ResetCheckboxes(self, *args):
        checkboxes = [('fltExcludeTrade', 0),
         ('fltExcludeMultiple', 0),
         ('fltSecNull', 1),
         ('fltSecLow', 1),
         ('fltSecHigh', 1)]
        for (name, val,) in checkboxes:
            cb = getattr(self.sr, name, None)
            if cb is None or cb.dead:
                continue
            cb.SetValue(val)




    def FindRelated(self, typeID, groupID, categoryID, issuerID, locationID, endLocationID, avail, contractType, reset = True):
        self.ToggleAdvanced(expanderCont=self.sr.advancedDivider, force=1)
        if contractType and settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE) != contractType:
            settings.user.ui.Set('contracts_search_type', contractType)
            self.PopulateSortCombo()
            self.InitFilters()
        if reset:
            if self.sr.fltAvail.GetValue() != avail:
                settings.user.ui.Set('contracts_search_avail', avail)
                self.InitFilters()
            if contractType and contractType != const.conTypeCourier:
                self.ResetTypeFilters()
            self.ResetFields()
            self.sr.fltLocation.SelectItemByValue(7)
        if issuerID:
            issuerName = cfg.eveowners.Get(issuerID).name
            self.sr.fltIssuer.SetValue(issuerName)
        if typeID:
            typeName = cfg.invtypes.Get(typeID).name
            self.sr.typeName.SetValue(typeName)
            self.sr.fltExactType.SetChecked(1, 0)
        elif categoryID:
            self.sr.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
        elif groupID:
            categoryID = cfg.invgroups.Get(groupID).categoryID
            self.sr.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
            self.sr.fltGroups.SelectItemByValue(groupID)
        if locationID:
            self.DoPickLocation(locationID)
        if endLocationID:
            locationName = cfg.evelocations.Get(endLocationID).name
            self.sr.fltDropOff.SetValue(locationName)
        self.SearchContracts()



    def SearchContracts(self, page = 0, reset = False):
        self.IndicateLoading(loading=1)
        self.currPage = page
        advancedVisible = self.sr.advancedCont.state != uiconst.UI_HIDDEN
        issuerID = None
        if advancedVisible:
            issuerName = self.sr.fltIssuer.GetValue()
            if issuerName:
                issuerID = uix.Search(issuerName.lower(), const.groupCharacter, const.categoryOwner, exact=1, hideNPC=1, filterGroups=[const.groupCharacter, const.groupCorporation], getWindow=0)
                if issuerID is None:
                    return 
            settings.user.ui.Set('contracts_search_issuer', issuerName or '')
        contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
        if advancedVisible:
            availability = self.sr.fltAvail.GetValue()
        else:
            availability = const.conAvailPublic
        locationID = self.sr.fltLocation.GetValue()
        if locationID < 100:
            if locationID == 0 and not session.stationid:
                raise UserError('ConNotInStation')
            locationID = {0: session.stationid,
             1: session.solarsystemid2,
             2: session.regionid,
             3: session.constellationid}.get(locationID, None)
        endLocationID = None
        if advancedVisible and contractType == const.conTypeCourier:
            endLocationName = self.sr.fltDropOff.GetValue()
            if endLocationName:
                endLocationID = self.GetLocationIDFromName(endLocationName)
                if endLocationID is None:
                    raise UserError('ConDropOffNotFound', {'name': endLocationName})
            settings.user.ui.Set('contracts_search_dropoff', endLocationName or '')
        securityClasses = None
        if advancedVisible:
            secNull = not not self.sr.fltSecNull.checked
            secLow = not not self.sr.fltSecLow.checked
            secHigh = not not self.sr.fltSecHigh.checked
            if False in (secNull, secLow, secHigh):
                securityClasses = []
                if secNull:
                    securityClasses.append(const.securityClassZeroSec)
                if secLow:
                    securityClasses.append(const.securityClassLowSec)
                if secHigh:
                    securityClasses.append(const.securityClassHighSec)
                securityClasses = securityClasses or None
        minPrice = None
        maxPrice = None
        if advancedVisible and const.conTypeCourier != contractType:
            m = self.sr.fltMinPrice.GetValue()
            settings.user.ui.Set('contracts_search_minprice', m)
            if m:
                minPrice = int(m) * MILLION
            m = self.sr.fltMaxPrice.GetValue()
            settings.user.ui.Set('contracts_search_maxprice', m)
            if m:
                maxPrice = int(m) * MILLION
        minReward = None
        maxReward = None
        minCollateral = None
        maxCollateral = None
        minVolume = None
        maxVolume = None
        if advancedVisible and const.conTypeCourier == contractType:
            m = self.sr.fltMinReward.GetValue()
            settings.user.ui.Set('contracts_search_minreward', m)
            if m:
                minReward = int(m) * MILLION
            m = self.sr.fltMaxReward.GetValue()
            settings.user.ui.Set('contracts_search_maxreward', m)
            if m:
                maxReward = int(m) * MILLION
            m = self.sr.fltMinCollateral.GetValue()
            settings.user.ui.Set('contracts_search_mincollateral', m)
            if m:
                minCollateral = int(m) * MILLION
            m = self.sr.fltMaxCollateral.GetValue()
            settings.user.ui.Set('contracts_search_maxcollateral', m)
            if m:
                maxCollateral = int(m) * MILLION
            m = self.sr.fltMinVolume.GetValue()
            settings.user.ui.Set('contracts_search_minvolume', m)
            if m:
                minVolume = int(m)
            m = self.sr.fltMaxVolume.GetValue()
            settings.user.ui.Set('contracts_search_maxvolume', m)
            if m:
                maxVolume = int(m)
        itemCategoryID = None
        itemGroupID = None
        itemTypes = None
        excludeTrade = None
        excludeMultiple = None
        excludeNoBuyout = None
        itemTypeName = None
        searchHint = None
        if advancedVisible and contractType == const.conTypeAuction:
            if self.sr.fltMinCollateral.GetValue():
                minCollateral = int(self.sr.fltMinCollateral.GetValue()) * MILLION
            if self.sr.fltMaxCollateral.GetValue():
                maxCollateral = int(self.sr.fltMaxCollateral.GetValue()) * MILLION
        if contractType != const.conTypeCourier:
            isExact = False
            if advancedVisible:
                cv = self.sr.fltCategories.GetValue()
                if cv and cv != -1:
                    itemCategoryID = int(cv[0])
                    searchHint = int(cv[1])
                if self.sr.fltGroups.GetValue():
                    itemGroupID = int(self.sr.fltGroups.GetValue())
                isExact = self.sr.fltExactType.checked
            typeName = self.sr.typeName.GetValue()
            if typeName:
                metaLevels = []
                if '|' in typeName:
                    lst = typeName.split('|')
                    typeName = lst[0]
                    metaNames = lst[1].lower()
                    for metaName in metaNames.split(','):
                        groupIDsByName = {'tech i': 1,
                         'tech ii': 2,
                         'tech iii': 14,
                         'storyline': 3,
                         'faction': 4,
                         'officer': 5,
                         'deadspace': 6}
                        vals = groupIDsByName.values()
                        groupIDsByName = {}
                        legalGroups = {}
                        for v in vals:
                            legalGroups[cfg.invmetagroups.Get(v).name] = v

                        groupIDsByName = {k.lower():v for (k, v,) in legalGroups.iteritems()}
                        legalGroups = legalGroups.keys()
                        legalGroups.sort()
                        metaLevel = groupIDsByName.get(metaName, None)
                        if metaName and metaLevel is None:
                            raise UserError('ConMetalevelNotFound', {'level': metaName,
                             'legal': ', '.join(legalGroups)})
                        metaLevels.append(metaLevel)

                groupOrCategory = ''
                if ':' in typeName:
                    lst = typeName.split(':')
                    groupOrCategory = lst[0].lower()
                    found = False
                    for group in cfg.invgroups:
                        if group.groupName.lower() == groupOrCategory:
                            itemGroupID = group.groupID
                            itemCategoryID = group.categoryID
                            found = True
                            sm.GetService('contracts').LogInfo('Found group:', group)
                            break

                    for category in cfg.invcategories:
                        if category.categoryName.lower() == groupOrCategory:
                            itemGroupID = None
                            itemCategoryID = category.categoryID
                            found = True
                            sm.GetService('contracts').LogInfo('Found category:', category)
                            break

                    if found:
                        typeName = lst[1]
                    else:
                        sm.GetService('contracts').LogInfo('Did not find group or category matching', groupOrCategory)
                    groupOrCategory = ''
                if len(typeName) < 3:
                    raise UserError('ConNeedAtLeastThreeLetters')
                itemTypes = self.GetTypesFromName(typeName, itemCategoryID, itemGroupID)
                if metaLevels:
                    typeIDs = itemTypes.keys()
                    itemTypes = set()
                    godma = sm.GetService('godma')
                    for typeID in typeIDs:
                        try:
                            tech = int(godma.GetType(typeID).techLevel)
                            meta = godma.GetTypeAttribute(typeID, const.attributeMetaGroupID)
                            if meta:
                                if meta in metaLevels:
                                    itemTypes.add(typeID)
                            elif tech in metaLevels:
                                itemTypes.add(typeID)
                        except:
                            pass

                else:
                    itemTypes = set(itemTypes.keys())
                if isExact and itemTypes:
                    typeID = None
                    if len(itemTypes) > 1:
                        for checkTypeID in itemTypes:
                            if cfg.invtypes.Get(checkTypeID).typeName.lower() == typeName.lower():
                                typeID = checkTypeID
                                break
                        else:
                            typeID = SelectItemTypeDlg(itemTypes)

                    else:
                        typeID = list(itemTypes)[0]
                    if not typeID:
                        return 
                    name = cfg.invtypes.Get(typeID).typeName
                    if groupOrCategory:
                        name = '%s:%s' % (groupOrCategory, name)
                    self.sr.typeName.SetValue(name)
                    itemTypes = {typeID: None}
            if not itemTypes and typeName:
                raise UserError('ConNoTypeMatchFound', {'name': typeName})
            itemTypeName = self.sr.typeName.GetValue() or None
            settings.user.ui.Set('contracts_search_typename', itemTypeName or '')
            excludeMultiple = self.sr.fltExcludeMultiple.checked
            if contractType != const.conTypeCourier:
                opt = self.sr.fltContractOptions.GetValue()
                if opt:
                    if opt == 1:
                        contractType = const.conTypeAuction
                    elif opt == 2:
                        contractType = const.conTypeItemExchange
                        if not minPrice:
                            minPrice = 1
                        excludeTrade = True
                    elif opt == 3:
                        contractType = const.conTypeItemExchange
                        if not maxPrice:
                            maxPrice = 0
                    elif opt == 4:
                        contractType = cc.CONTYPE_AUCTIONANDITEMECHANGE
                        if not minPrice:
                            minPrice = 1
                        excludeTrade = True
        startNum = page * cc.CONTRACTS_PER_PAGE
        (sortBy, sortDir,) = self.sr.fltSort.GetValue()
        description = None
        ret = sm.ProxySvc('contractProxy').SearchContracts(itemTypes=itemTypes, itemTypeName=itemTypeName, itemCategoryID=itemCategoryID, itemGroupID=itemGroupID, contractType=contractType, securityClasses=securityClasses, locationID=locationID, endLocationID=endLocationID, issuerID=issuerID, minPrice=minPrice, maxPrice=maxPrice, minReward=minReward, maxReward=maxReward, minCollateral=minCollateral, maxCollateral=maxCollateral, minVolume=minVolume, maxVolume=maxVolume, excludeTrade=excludeTrade, excludeMultiple=excludeMultiple, excludeNoBuyout=excludeNoBuyout, availability=availability, description=description, searchHint=searchHint, sortBy=sortBy, sortDir=sortDir, startNum=startNum)
        contracts = ret.contracts
        numFound = ret.numFound
        searchTime = ret.searchTime
        maxResults = ret.maxResults
        self.numPages = int(int(numFound) / cc.CONTRACTS_PER_PAGE)
        if not numFound or self.numPages * cc.CONTRACTS_PER_PAGE < numFound:
            self.numPages += 1
        if numFound >= maxResults:
            numFound = '%s+' % maxResults
        if len(contracts) >= 2:
            self.pages[self.currPage] = contracts[0].contract.contractID
            self.pages[self.currPage + 1] = contracts[-1].contract.contractID - 1
        ownerIDs = set()
        for r in contracts:
            ownerIDs.add(r.contract.issuerID)
            ownerIDs.add(r.contract.issuerCorpID)
            ownerIDs.add(r.contract.assigneeID)

        cfg.eveowners.Prime(ownerIDs)
        self.sr.contractlist.sr.id = None
        pathfinderSvc = sm.GetService('pathfinder')
        mapSvc = sm.StartService('map')
        jumpsCache = {}
        routes = []
        data = []
        i = 1
        for _c in contracts:
            blue.pyos.BeNice()
            title = ''
            items = _c.items
            bids = _c.bids
            c = _c.contract
            typeID = None
            routeLength = 0
            if len(items) == 1:
                typeID = items[0].itemTypeID
            if c.startStationID == session.stationid:
                numJumps = 0
            elif c.startSolarSystemID == session.solarsystemid2:
                numJumps = 0
            else:
                try:
                    n = jumpsCache[c.startSolarSystemID]
                except:
                    n = int(pathfinderSvc.GetJumpCountFromCurrent(c.startSolarSystemID))
                    jumpsCache[c.startSolarSystemID] = n
                numJumps = n
            route = None
            if c.type == const.conTypeCourier:
                r = [c.startSolarSystemID, c.endSolarSystemID]
                r.sort()
                route = (r[0], r[1])
                routes.append(r)
            startSecurityClass = None
            endSecurityClass = None
            if c.startSolarSystemID != session.solarsystemid2:
                startSecurityClass = int(mapSvc.GetSecurityClass(c.startSolarSystemID))
            if c.endSolarSystemID and c.endSolarSystemID != session.solarsystemid2:
                endSecurityClass = int(mapSvc.GetSecurityClass(c.endSolarSystemID))
            issuer = cfg.eveowners.Get(c.issuerCorpID if c.forCorp else c.issuerID).name
            d = {'contract': c,
             'title': GetContractTitle(c, items),
             'startSolarSystemName': cfg.evelocations.Get(c.startSolarSystemID).name,
             'endSolarSystemName': cfg.evelocations.Get(c.endSolarSystemID).name,
             'issuer': issuer,
             'searchresult': _c,
             'contractItems': items,
             'bids': bids,
             'rec': '',
             'text': '',
             'label': '',
             'typeID': typeID,
             'numJumps': numJumps,
             'routeLength': routeLength,
             'route': route,
             'startSecurityClass': startSecurityClass,
             'endSecurityClass': endSecurityClass,
             'dateIssued': c.dateIssued}
            d['sort_%s' % mls.UI_CONTRACTS_CURRENTBID] = (c.price if not bids else bids[0].amount, c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_COLLATERAL] = (c.collateral, c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_LOCATION] = (d['startSolarSystemName'], c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_PRICE] = (int(c.price) or -int(c.reward), c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_REWARD] = (c.reward, c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_VOLUME] = (c.volume, c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_CONTRACT] = (d['title'], c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_TIMELEFT] = (c.dateExpired, c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_JUMPS] = (d['numJumps'], c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_PICKUP] = (d['startSolarSystemName'], c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_DROPOFF] = (d['endSolarSystemName'], c.contractID)
            d['sort_%s' % mls.UI_CONTRACTS_CREATED] = c.dateIssued
            d['sort_%s' % mls.UI_CONTRACTS_ISSUER] = issuer.lower()
            data.append(d)
            i += 1

        routeLengths = pathfinderSvc.GetMultiJumpCounts(routes)
        for d in data:
            if d['route']:
                d['routeLength'] = routeLengths.get(d['route'], 0)

        self.numFound = numFound
        self.contractType = contractType
        self.pageData[self.currPage] = data
        self.RenderPage(reset)
        self.svc.LogInfo('Found', numFound, 'contracts in %.4f seconds' % (searchTime / float(const.SEC)))



    def RenderPage(self, reset = False):
        try:
            data = self.pageData[self.currPage]
            contractType = self.contractType
            if contractType == cc.CONTYPE_AUCTIONANDITEMECHANGE:
                contractType = const.conTypeItemExchange
            scrolllist = []
            className = {const.conTypeAuction: 'ContractEntrySearchAuction',
             const.conTypeItemExchange: 'ContractEntrySearchItemExchange',
             const.conTypeCourier: 'ContractEntrySearchCourier'}[contractType]
            securityClassMe = sm.GetService('map').GetSecurityClass(session.solarsystemid2)
            ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
            for d in data:
                contract = d['contract']
                d['sort_%s' % mls.UI_CONTRACTS_ROUTE] = (d['routeLength'], d['contract'].contractID)
                if settings.user.ui.Get('contracts_search_client_maxjumps', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', 0)
                    if maxNumJumps and d['numJumps'] > maxNumJumps:
                        continue
                if d['route'] and settings.user.ui.Get('contracts_search_client_maxroute', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxroute_num', 0)
                    if maxNumJumps and d['routeLength'] > maxNumJumps:
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeunreachable', 0):
                    if d['numJumps'] > cc.NUMJUMPS_UNREACHABLE or d['routeLength'] > cc.NUMJUMPS_UNREACHABLE or self.svc.IsStationInaccessible(contract.startStationID) or self.svc.IsStationInaccessible(contract.endStationID):
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeignore', 1):
                    skipIt = False
                    for ownerID in ignoreList:
                        if ownerID in [contract.issuerID, contract.issuerCorpID]:
                            skipIt = True
                            break

                    if skipIt:
                        continue
                if settings.user.ui.Get('contracts_search_client_currentsecurity', False):
                    if d['startSecurityClass'] is not None and d['startSecurityClass'] != securityClassMe:
                        continue
                    if d['endSecurityClass'] is not None and d['endSecurityClass'] != securityClassMe:
                        continue
                scrolllist.append(listentry.Get(className, d))

            if contractType == const.conTypeItemExchange:
                columns = [mls.UI_CONTRACTS_CONTRACT,
                 mls.UI_CONTRACTS_LOCATION,
                 mls.UI_CONTRACTS_PRICE,
                 mls.UI_CONTRACTS_JUMPS,
                 mls.UI_CONTRACTS_TIMELEFT,
                 mls.UI_CONTRACTS_ISSUER,
                 mls.UI_CONTRACTS_CREATED]
            elif contractType == const.conTypeAuction:
                columns = [mls.UI_CONTRACTS_CONTRACT,
                 mls.UI_CONTRACTS_LOCATION,
                 mls.UI_CONTRACTS_CURRENTBID,
                 mls.UI_CONTRACTS_BUYOUT,
                 mls.UI_CONTRACTS_BIDS,
                 mls.UI_CONTRACTS_JUMPS,
                 mls.UI_CONTRACTS_TIMELEFT,
                 mls.UI_CONTRACTS_ISSUER,
                 mls.UI_CONTRACTS_CREATED]
            else:
                columns = [mls.UI_CONTRACTS_PICKUP,
                 mls.UI_CONTRACTS_DROPOFF,
                 mls.UI_CONTRACTS_VOLUME,
                 mls.UI_CONTRACTS_REWARD,
                 mls.UI_CONTRACTS_COLLATERAL,
                 mls.UI_CONTRACTS_ROUTE,
                 mls.UI_CONTRACTS_JUMPS,
                 mls.UI_CONTRACTS_TIMELEFT,
                 mls.UI_CONTRACTS_ISSUER,
                 mls.UI_CONTRACTS_CREATED]
            self.sr.contractlist.sr.id = 'contractlist'
            self.sr.contractlist.sr.minColumnWidth = {mls.UI_CONTRACTS_CONTRACT: 100,
             mls.UI_CONTRACTS_BUYOUT: 200}
            reset = False
            self.sr.contractlist.LoadContent(contentList=scrolllist, headers=columns, noContentHint=mls.UI_CONTRACTS_CONTRACTLISTHINT_NOCONTRACTSFOUND, ignoreSort=reset, scrolltotop=True)
            if reset:
                if self.sr.contractlist and self.sr.contractlist.sr.columnHilite:
                    self.sr.contractlist.HiliteSorted(None, None)
                    self.sr.contractlist.sr.columnHilite.state = uiconst.UI_HIDDEN
            txt = mls.UI_CONTRACTS_NUMCONTRACTSFOUND % {'num': self.numFound}
            self.sr.foundLabel.SetText(txt)
            self.sr.expanderTextCont.width = self.sr.foundLabel.textwidth + 50
            self.UpdatePaging(self.currPage + 1, self.numPages)

        finally:
            self.IndicateLoading(loading=0)




    def IndicateLoading(self, loading = 0):
        try:
            if loading:
                self.sr.loadingWheel.Show()
                self.sr.contractlist.sr.maincontainer.opacity = 0.5
            else:
                self.sr.loadingWheel.Hide()
                self.sr.contractlist.sr.maincontainer.opacity = 1.0
        except:
            pass



    def DoNothing(self, *args):
        pass




