#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/depletionPinManager.py
import uicls
import uiconst
import listentry
import util
import uix

class DepletionManager(uicls.Window):
    __guid__ = 'form.DepletionManager'
    default_windowID = 'depletionManager'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.selected = None
        self.SetTopparentHeight(0)
        self.SetCaption('Depletion Manager')
        self.SetMinSize([280, 500])
        headerContainer = uicls.Container(name='headerParent', parent=self.sr.main, align=uiconst.TOTOP, height=100, padding=(2, 2, 2, 2))
        text = "This gives you a list of depletion\npoints that you've placed on the planet.\nYou can edit some aspects of these points\n    * amount - is the base extraction amount\n    * duration - is the in minutes and tells how many times the program will be resubmitted\n    * headRadius - tells the size of the head\n        "
        uicls.EveLabelMedium(parent=headerContainer, text=text, align=uiconst.TOALL)
        timeContainer = uicls.Container(name='timeParent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=40)
        editContainer = uicls.Container(name='editParent', parent=self.sr.main, align=uiconst.TOBOTTOM, top=20, height=50, padTop=12)
        scrollContainer = uicls.Container(name='scrollParent', parent=self.sr.main, align=uiconst.TOALL)
        self.depletionPointScroll = uicls.Scroll(parent=scrollContainer, align=uiconst.TOALL, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.depletionPointScroll.multiSelect = 0
        self.pinManager = attributes.get('pinManager', None)
        amountContainer = uicls.Container(name='amountParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        durationContainer = uicls.Container(name='durationParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        headRadiusContainer = uicls.Container(name='headRadiusParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        self.amountEdit = uicls.SinglelineEdit(name='amount', parent=amountContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), maxLength=40, label='amount', OnReturn=self.OnAmountSubmit)
        self.amountEdit.OnFocusLost = self.OnAmountSubmit
        self.durationEdit = uicls.SinglelineEdit(name='duration', parent=durationContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), maxLength=40, label='duration', OnReturn=self.OnDurationSubmit)
        self.durationEdit.OnFocusLost = self.OnDurationSubmit
        self.headRadiusEdit = uicls.SinglelineEdit(name='headRadius', parent=headRadiusContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), maxLength=40, label='headRadius', OnReturn=self.OnHeadRadiusSubmit)
        self.headRadiusEdit.OnFocusLost = self.OnHeadRadiusSubmit
        self.timeEdit = uicls.SinglelineEdit(name='timeEdit', parent=timeContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), maxLength=40, label='Time in days', setvalue='14')
        self.LoadDepletionPointScroll()
        self.sr.saveDeleteButtons = uicls.ButtonGroup(btns=[['Submit', self.Submit, ()]], parent=self.sr.main, idx=0)

    def LoadDepletionPointScroll(self):
        scrolllist = []
        for point in self.pinManager.depletionPoints:
            data = util.KeyVal(label='%d<t>%d<t>%d<t>%.3f' % (point.index,
             point.GetAmount(),
             point.GetDuration(),
             point.GetHeadRadius()), index=point.index, OnClick=self.OnDepletionPointClicked)
            scrolllist.append(listentry.Get('Generic', data=data))

        self.depletionPointScroll.Load(contentList=scrolllist, headers=['index',
         'amount',
         'duration',
         'headRadius'])

    def Submit(self):
        totalDuration = int(self.timeEdit.GetValue()) * const.DAY
        self.pinManager.GMRunDepletionSim(totalDuration)

    def OnDepletionPointClicked(self, entry):
        index = entry.sr.node.index
        self.selected = index
        depletionPoint = self.pinManager.depletionPoints[index]
        duration = depletionPoint.GetDuration()
        amount = depletionPoint.GetAmount()
        headRadius = depletionPoint.GetHeadRadius()
        self.amountEdit.SetValue(str(amount))
        self.durationEdit.SetValue(str(duration))
        self.headRadiusEdit.SetValue(str(headRadius))
        for i, depletionPoint in enumerate(self.pinManager.depletionPoints):
            if i == index:
                depletionPoint.drillArea.pinColor = util.Color.GREEN
            else:
                depletionPoint.drillArea.pinColor = util.Color.YELLOW

    def GetSelectedDepletionPoint(self):
        if self.selected is None:
            return
        return self.pinManager.depletionPoints[self.selected]

    def OnAmountSubmit(self, *args):
        if not self or self.destroyed:
            return
        newAmount = int(self.amountEdit.GetValue())
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        depletionPoint.amount = newAmount
        self.LoadDepletionPointScroll()

    def OnDurationSubmit(self, *args):
        if not self or self.destroyed:
            return
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        newDuration = int(self.durationEdit.GetValue())
        depletionPoint.duration = newDuration
        self.LoadDepletionPointScroll()

    def OnHeadRadiusSubmit(self, *args):
        if not self or self.destroyed:
            return
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        newHeadRadius = float(self.headRadiusEdit.GetValue())
        depletionPoint.headRadius = newHeadRadius
        depletionPoint.drillArea.pinRadius = newHeadRadius
        self.LoadDepletionPointScroll()

    def _OnClose(self, *args):
        for depletionPoint in self.pinManager.depletionPoints:
            depletionPoint.drillArea.pinColor = util.Color.YELLOW