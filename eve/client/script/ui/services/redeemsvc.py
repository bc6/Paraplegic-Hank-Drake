import service
import form
import uix
import listentry
import util
import uicls
import uiconst

class RedeemService(service.Service):
    __guid__ = 'svc.redeem'
    __dependencies__ = ['tactical']

    def __init__(self):
        service.Service.__init__(self)
        self.tokens = None



    def Run(self, *args):
        service.Service.Run(self, *args)



    def GetRedeemTokens(self, force = False):
        if self.tokens is None or force:
            self.tokens = sm.RemoteSvc('userSvc').GetRedeemTokens()
        return self.tokens



    def ReverseRedeem(self, item):
        if eve.Message('ConfirmReverseRedeem', {'type': (TYPEID, item.typeID),
         'quantity': item.stacksize}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        try:
            sm.RemoteSvc('userSvc').ReverseRedeem(item.itemID)

        finally:
            self.tokens = None




    def OpenRedeemWindow(self, charID, stationID):
        if not self.GetRedeemTokens():
            raise UserError('RedeemNoTokens')
        sm.StartService('window').ResetToDefaults('redeem')
        wnd = sm.StartService('window').GetWindow('redeem')
        if wnd is None:
            wnd = sm.StartService('window').GetWindow('redeem', 1, decoClass=form.RedeemWindow, charID=charID, stationID=stationID)
            wnd.left -= 160
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def CloseRedeemWindow(self):
        wnd = sm.StartService('window').GetWindow('redeem')
        if wnd:
            wnd.CloseX()



    def ClaimRedeemTokens(self, tokens, charID):
        try:
            sm.RemoteSvc('userSvc').ClaimRedeemTokens(tokens, charID)
        except (UserError,) as e:
            eve.Message(e.msg, e.dict)
        except (Exception,) as e:
            raise 
        self.tokens = None




class RedeemWindow(uicls.Window):
    __guid__ = 'form.RedeemWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        charID = attributes.charID
        stationID = attributes.stationID
        self.tokens = None
        self.selectedTokens = {}
        self.tokens = sm.StartService('redeem').GetRedeemTokens()
        self.SetWndIcon('ui_76_64_3', mainTop=-10)
        self.SetCaption(mls.UI_GENERIC_REDEEMITEMS)
        self.SetMinSize([700, 260])
        self.NoSeeThrough()
        self.SetScope('all')
        self.charID = charID
        self.stationID = stationID
        h = self.sr.topParent.height - 2
        self.sr.picParent = uicls.Container(name='picpar', parent=self.sr.topParent, align=uiconst.TORIGHT, width=h, height=h, left=const.defaultPadding, top=const.defaultPadding)
        self.sr.pic = uicls.Sprite(parent=self.sr.picParent, align=uiconst.RELATIVE, left=1, top=3, height=h, width=h)
        sm.GetService('photo').GetPortrait(charID, 64, self.sr.pic)
        self.state = uiconst.UI_NORMAL
        self.sr.windowCaption = uicls.CaptionLabel(text=mls.UI_GENERIC_REDEEMITEMS, parent=self.sr.topParent, align=uiconst.RELATIVE, left=60, top=18, state=uiconst.UI_DISABLED, fontsize=18)
        text = mls.UI_GENERIC_REDEEMLINE1 % {'num': len(self.tokens),
         'char': cfg.eveowners.Get(charID).name}
        tp = 5
        t = uicls.Label(text=text, parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        tp += t.textheight
        if stationID:
            text = mls.UI_GENERIC_REDEEMLINE2 % {'station': cfg.evelocations.Get(stationID).name.split(' - ')[0]}
            t = uicls.Label(text=text, parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
            tp += t.height
        else:
            text = mls.UI_GENERIC_REDEEMLINE3
            t = uicls.Label(text=text, parent=self.sr.topParent, top=tp, left=60, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        btns = [(mls.UI_GENERIC_REDEEMSELECTED,
          self.RedeemSelected,
          (),
          84)]
        self.sr.redeemBtn = uicls.ButtonGroup(btns=btns, parent=self.sr.main, unisize=1)
        self.sr.itemsScroll = uicls.Scroll(parent=self.sr.main, padTop=const.defaultPadding)
        self.sr.itemsScroll.hiliteSorted = 0
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOBOTTOM, width=6)
        scrolllist = []
        expireUsed = 0
        for token in self.tokens:
            self.selectedTokens[(token.tokenID, token.massTokenID)] = None
            ty = cfg.invtypes.Get(token.typeID)
            qty = token.quantity
            desc = token.description or token.textLabel
            if token.expireDateTime:
                expireUsed = 1
                desc = '%s<t><br><color=red>%s</color>' % (desc, util.FmtDate(token.expireDateTime, 'sn'))
            if token.stationID:
                desc = '%s<br><color=red>(%s %s)</color>' % (desc, mls.UI_GENERIC_REDEEMABLETO, cfg.evelocations.Get(token.stationID).name)
            label = '%s<t>%s<t>%s' % (ty.typeName, qty, desc)
            scrolllist.append(listentry.Get('RedeemToken', {'itemID': None,
             'tokenID': token.tokenID,
             'massTokenID': token.massTokenID,
             'info': token,
             'typeID': ty.typeID,
             'stationID': token.stationID,
             'label': label,
             'quantity': qty,
             'getIcon': 1,
             'retval': (token.tokenID, token.massTokenID),
             'OnChange': self.OnTokenChange,
             'checked': True}))

        if self.sr.itemsScroll is not None:
            self.sr.itemsScroll.sr.id = 'itemsScroll'
            self.sr.itemsScroll.sr.lastSelected = None
            self.sr.itemsScroll.sr.minColumnWidth = {mls.UI_GENERIC_TYPE: 50}
            headers = [mls.UI_GENERIC_TYPE, mls.UI_GENERIC_QTY, mls.UI_GENERIC_DESCRIPTION]
            if expireUsed == 1:
                headers.append(mls.UI_GENERIC_EXPIRES)
                self.sr.itemsScroll.sr.fixedColumns = {mls.UI_GENERIC_EXPIRES: 80}
            self.sr.itemsScroll.Load(contentList=scrolllist, headers=headers)
        return self



    def RedeemSelected(self, *args):
        if self.stationID is None:
            raise UserError('RedeemOnlyInStation')
        if eve.Message('RedeemConfirmClaim', {'char': cfg.eveowners.Get(self.charID).name,
         'station': cfg.evelocations.Get(self.stationID).name}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
            return 
        sm.StartService('redeem').ClaimRedeemTokens(self.selectedTokens.keys(), self.charID)
        self.Close()



    def OnTokenChange(self, checkbox, *args):
        (tokenID, massTokenID,) = checkbox.data['retval']
        k = (tokenID, massTokenID)
        gv = True
        try:
            gv = checkbox.GetValue()
        except:
            pass
        if gv:
            self.selectedTokens[k] = None
        elif k in self.selectedTokens:
            del self.selectedTokens[k]
        if len(self.selectedTokens) > 0:
            self.sr.redeemBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.redeemBtn.state = uiconst.UI_DISABLED




class RedeemToken(listentry.Item):
    __guid__ = 'listentry.RedeemToken'

    def init(self):
        self.sr.overlay = uicls.Container(name='overlay', align=uiconst.TOPLEFT, parent=self, height=1)
        self.sr.tlicon = None



    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        cbox = uicls.Checkbox(text='checkbox', parent=self, configName='cb', retval=None, checked=1, align=uiconst.TOPLEFT, pos=(6, 4, 0, 0), callback=self.CheckBoxChange)
        cbox.data = {}
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_NORMAL



    def Load(self, args):
        listentry.Item.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data = {'key': (data.tokenID, data.massTokenID),
         'retval': data.retval}
        self.sr.icon.left = 24
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        gdm = sm.StartService('godma').GetType(self.sr.node.info.typeID)
        if gdm.techLevel in (2, 3):
            self.sr.techIcon.left = 24
        elif self.sr.tlicon:
            self.sr.tlicon.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        lastSelected = self.sr.node.scroll.sr.lastSelected
        if lastSelected is None:
            shift = 0
        idx = self.sr.node.idx
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        isIt = not self.sr.checkbox.checked
        self.sr.checkbox.SetChecked(isIt)
        self.sr.node.scroll.sr.lastSelected = idx



    def GetMenu(self):
        return [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (self.sr.node,))]



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)




