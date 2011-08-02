import blue
import uthread
import util
import xtriui
import uix
import uiutil
import form
import listentry
import trinity
import draw
import uiconst
import uicls

class CorpDetails(uicls.Window):
    __guid__ = 'form.CorpDetails'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.ShowLoad()
        self.SetCaption(self.caption)
        self.DefineButtons(uiconst.OK, okLabel=mls.UI_CMD_SUBMIT, okFunc=self.Submit)
        self.SetMinSize([320, 394], 1)
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.pickingTicker = 0
        self.layerNumSelected = None
        self.sr.prefs = [None,
         None,
         None,
         None,
         None,
         None]
        self.sr.priorlogo = (None, None, None, None, None, None)
        self.sr.priordesc = self.description
        self.sr.priorurl = self.url
        self.sr.priortaxRate = self.taxRate
        self.sr.priorapplicationsEnabled = self.applicationsEnabled
        par = uicls.Container(name='logoControl', parent=self.sr.main, align=uiconst.TOTOP, height=100, width=310, padding=(5, 5, 5, 0))
        self.sr.logocontrol = uicls.Container(name='controlpanel', parent=par, height=100, width=160, align=uiconst.CENTER)
        self.sr.inputcontrol = uicls.Container(name='controlpanel', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(5, 5, 5, 0))
        top = uix.GetTextHeight(mls.UI_CORP_CORPNAME)
        self.sr.corpNameEdit_container = uicls.Container(name='corpNameEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=56)
        self.sr.corpNameEdit = uicls.SinglelineEdit(name='nameEdit', parent=self.sr.corpNameEdit_container, setvalue='%s %s' % (cfg.eveowners.Get(eve.session.charid).name, mls.UI_CORP_CORP), align=uiconst.TOTOP, maxLength=100, label=mls.UI_CORP_CORPNAME, top=top)
        self.sr.corpNameEdit_container.height = self.sr.corpNameEdit.height + top + const.defaultPadding
        top = uix.GetTextHeight(mls.UI_GENERIC_TICKER)
        self.sr.corpTickerEdit_container = uicls.Container(name='corpTickerEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=56)
        btn = uicls.Button(parent=self.sr.corpTickerEdit_container, label=mls.UI_GENERIC_TICKER, align=uiconst.BOTTOMRIGHT, func=self.GetPickTicker, idx=0)
        self.sr.corpTickerEdit = uicls.SinglelineEdit(name='corpTickerEdit', parent=self.sr.corpTickerEdit_container, setvalue='', align=uiconst.TOPLEFT, maxLength=5, label=mls.UI_GENERIC_TICKER, top=top, width=min(300 - btn.width, 240))
        self.sr.corpTickerEdit_container.height = self.sr.corpTickerEdit.height + top + const.defaultPadding
        top = uix.GetTextHeight(mls.UI_CORP_MEMBERLIMIT)
        self.sr.memberLimit_container = uicls.Container(name='memberLimit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        btn = uicls.Button(parent=self.sr.memberLimit_container, label=mls.UI_CORP_UPDATEWITHMYSKILLS, align=uiconst.BOTTOMRIGHT, func=self.UpdateWithSkills, idx=0)
        uicls.Label(text=mls.UI_CORP_MEMBERLIMIT, parent=self.sr.memberLimit_container, left=0, top=0, fontsize=10, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        self.sr.memberLimit = uicls.Label(text='123', parent=self.sr.memberLimit_container, left=2, top=top, state=uiconst.UI_DISABLED, idx=0)
        self.sr.memberLimit_container.height = self.sr.memberLimit.height + top + const.defaultPadding
        top = uix.GetTextHeight(mls.UI_GENERIC_RACES)
        self.sr.racesAllowed_container = uicls.Container(name='racesAllowed_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        uicls.Label(text=mls.UI_GENERIC_RACES, parent=self.sr.racesAllowed_container, left=0, top=0, fontsize=10, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        self.sr.racesAllowed = uicls.Label(text=mls.UI_GENERIC_UNKNOWN, parent=self.sr.racesAllowed_container, left=2, top=top, state=uiconst.UI_DISABLED, idx=0)
        self.sr.racesAllowed_container.height = self.sr.racesAllowed.height + top + const.defaultPadding
        top = uix.GetTextHeight(mls.UI_GENERIC_TAXRATE)
        self.sr.taxRateEdit_container = uicls.Container(name='taxRateEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        self.sr.taxRateEdit = uicls.SinglelineEdit(name='taxRateEdit', parent=self.sr.taxRateEdit_container, floats=(0.0, 100.0, 1), setvalue=self.taxRate, align=uiconst.TOPLEFT, label=mls.UI_GENERIC_TAXRATE, top=top)
        self.sr.taxRateEdit_container.height = self.sr.taxRateEdit.height + top + const.defaultPadding
        top = uix.GetTextHeight('http://')
        self.sr.urlEdit_container = uicls.Container(name='urlEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP)
        self.sr.urlEdit = uicls.SinglelineEdit(name='urlEdit', parent=self.sr.urlEdit_container, setvalue=self.url, maxLength=2048, align=uiconst.TOTOP, label=mls.UI_GENERIC_HOMEPAGE, top=top)
        self.sr.urlEdit_container.height = self.sr.urlEdit.height + top + const.defaultPadding + 20
        self.sr.applicationsEnabled_container = uicls.Container(name='applicEnabled_container', parent=self.sr.inputcontrol, align=uiconst.TOBOTTOM, height=22)
        self.sr.applicationsEnabled = uicls.Checkbox(text=mls.UI_CORP_MEMBERSHIP_APPLICATIONS_ENABLED, parent=self.sr.applicationsEnabled_container, configName='applicationsEnabled', retval=None, checked=self.applicationsEnabled, pos=(0, 2, 0, 0))
        top = uix.GetTextHeight(mls.UI_GENERIC_DESCRIPTION)
        self.sr.descEdit_container = uicls.Container(name='descEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Label(text=mls.UI_GENERIC_DESCRIPTION, parent=self.sr.descEdit_container, fontsize=10, letterspace=1, linespace=9, uppercase=1, top=-16)
        self.sr.descEdit = uicls.EditPlainText(setvalue=self.description, parent=self.sr.descEdit_container, maxLength=4000)
        self.logopicker = uicls.CorpLogoPickerContainer(parent=self.sr.logocontrol, pos=(100, 0, 57, 90), align=uiconst.TOPLEFT)



    def GetLogoLibShape(self, graphicID):
        return const.graphicCorpLogoLibShapes.get(graphicID, const.graphicCorpLogoLibShapes[const.graphicCorpLogoLibNoShape])



    def GetLogoLibColor(self, graphicID):
        (color, blendMode,) = const.graphicCorpLogoLibColors.get(graphicID, (1.0, 1.0, 1.0, 1.0))
        return (color, blendMode)



    def SetupLogo(self, shapes = [None, None, None], colors = [None, None, None]):
        i = 0
        self.sr.layerpics = []
        for each in ['layerPic1', 'layerPic2', 'layerPic3']:
            btn = uicls.Sprite(parent=getattr(self.logopicker, each), pos=(0, 0, 0, 0), align=uiconst.TOALL, color=(1.0, 0.0, 1.0, 0.0))
            btn.OnClick = (self.ClickPic, i)
            self.sr.layerpics.append(btn)
            texturePath = self.GetLogoLibShape(shapes[i])
            btn.LoadTexture(texturePath)
            btn.SetRGB(1.0, 1.0, 1.0, 1.0)
            self.corpLogo.SetLayerShapeAndColor(layerNum=i, shapeID=shapes[i], colorID=colors[i])
            self.sr.prefs[i] = shapes[i]
            i += 1

        i = 0
        self.sr.layercols = []
        for each in ['layerStyle1', 'layerStyle2', 'layerStyle3']:
            btn = uicls.Fill(parent=getattr(self.logopicker, each), pos=(0, 0, 0, 0), align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.0), state=uiconst.UI_NORMAL)
            btn.OnClick = (self.ClickCol, i, btn)
            self.sr.layercols.append(btn)
            if colors[i]:
                newshader = blue.os.LoadObject(util.GraphicFile(colors[i]))
                (color, blendMode,) = self.GetLogoLibColor(colors[i])
                btn.SetRGB(*color)
                self.sr.prefs[i + 3] = colors[i]
            i = i + 1




    def PickPic(self, sender, *args):
        if self.layerNumSelected is not None:
            shapeID = sender.sr.identifier
            texturePath = self.GetLogoLibShape(shapeID)
            self.sr.layerpics[self.layerNumSelected].LoadTexture(texturePath)
            self.corpLogo.SetLayerShapeAndColor(layerNum=self.layerNumSelected, shapeID=shapeID)
            if not self.sr.prefs[(self.layerNumSelected + 3)]:
                self.sr.layerpics[self.layerNumSelected].SetRGB(1.0, 1.0, 1.0, 1.0)
            self.sr.prefs[self.layerNumSelected] = sender.sr.identifier



    def PickCol(self, sender, *args):
        if self.layerNumSelected is not None:
            colorID = sender.sr.identifier
            (color, blendMode,) = self.GetLogoLibColor(colorID)
            self.sr.layercols[self.layerNumSelected].SetRGB(*color)
            self.corpLogo.SetLayerShapeAndColor(layerNum=self.layerNumSelected, colorID=colorID)
            self.sr.prefs[self.layerNumSelected + 3] = colorID



    def ClickPic(self, idx):
        if not self.sr.Get('shapes', None):
            top = self.corpLogo.top + self.corpLogo.height
            self.sr.shapes = uicls.Container(name='shapes_container', parent=self.sr.main, align=uiconst.CENTERTOP, height=220, width=280, idx=0, top=top)
            self.sr.shapes.state = uiconst.UI_HIDDEN
            shapescroll = uicls.Scroll(parent=self.sr.shapes, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.AddCloseButton(self.sr.shapes)
            self.sr.underlay = uicls.WindowUnderlay(parent=self.sr.shapes)
            x = 0
            scrolllist = []
            icons = []
            graphicIDs = const.graphicCorpLogoLibShapes.keys()
            graphicIDs.sort()
            for graphicID in graphicIDs:
                texturePath = self.GetLogoLibShape(graphicID)
                icons.append((texturePath,
                 None,
                 graphicID,
                 self.PickPic))
                x += 1
                if x == 4:
                    scrolllist.append(listentry.Get('Icons', {'icons': icons}))
                    icons = []
                    x = 0

            if len(icons):
                scrolllist.append(listentry.Get('Icons', {'icons': icons}))
            self.sr.shapes.state = uiconst.UI_NORMAL
            shapescroll.Load(fixedEntryHeight=64, contentList=scrolllist)
        self.layerNumSelected = idx
        self.sr.shapes.top = self.corpLogo.top + self.corpLogo.height
        if self.sr.Get('colors', None):
            self.sr.colors.state = uiconst.UI_HIDDEN
        self.sr.shapes.state = uiconst.UI_NORMAL
        self.sr.shapes.SetOrder(0)



    def DoNothing(self, *args):
        pass



    def AddCloseButton(self, panel):
        uicls.Container(name='push', parent=panel.children[0], align=uiconst.TOBOTTOM, height=4, idx=0)
        buttondad = uicls.Container(name='btnparent', parent=panel.children[0], align=uiconst.TOBOTTOM, height=16, idx=0)
        btn = uicls.Button(parent=buttondad, label=mls.UI_CMD_CLOSE, align=uiconst.CENTER, func=self.HidePanel, args=panel)



    def HidePanel(self, panel, *args):
        if panel:
            panel.state = uiconst.UI_HIDDEN



    def ClickCol(self, idx, sender):
        if not self.sr.Get('colors', None):
            self.sr.colors = uicls.Container(name='colors_container', parent=self.sr.main, align=uiconst.CENTERTOP, height=128, width=150, idx=0)
            colorscroll = uicls.Scroll(parent=self.sr.colors, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.AddCloseButton(self.sr.colors)
            self.sr.underlay = uicls.WindowUnderlay(parent=self.sr.colors)
            x = 0
            scrolllist = []
            icons = []
            graphicIDs = const.graphicCorpLogoLibColors.keys()
            graphicIDs.sort()
            for graphicID in graphicIDs:
                (color, blendMode,) = self.GetLogoLibColor(graphicID)
                icons.append((None,
                 color,
                 graphicID,
                 self.PickCol))
                x += 1
                if x == 4:
                    scrolllist.append(listentry.Get('Icons', {'icons': icons}))
                    icons = []
                    x = 0

            if len(icons):
                scrolllist.append(listentry.Get('Icons', {'icons': icons[:]}))
            self.sr.colors.state = uiconst.UI_NORMAL
            colorscroll.Load(fixedEntryHeight=32, contentList=scrolllist)
        self.layerNumSelected = idx
        self.sr.colors.top = self.corpLogo.top + self.corpLogo.height
        if self.sr.Get('shapes', None):
            self.sr.shapes.state = uiconst.UI_HIDDEN
        self.sr.colors.state = uiconst.UI_NORMAL
        uiutil.SetOrder(self.sr.colors, 0)



    def Confirm(self, *args):
        pass



    def MouseDown(self, sender, *args):
        if self.sr.Get('colors', None):
            self.sr.colors.state = uiconst.UI_HIDDEN
        if self.sr.Get('shapes', None):
            self.sr.shapes.state = uiconst.UI_HIDDEN



    def UpdateWithSkills(self, *args):
        if sm.GetService('corp').UpdateCorporationAbilities() is None:
            return 
        corp = sm.GetService('corp').GetCorporation(eve.session.corpid, 1)
        self.sr.memberLimit.text = str(corp.memberLimit)
        allowedRaces = ''
        races = [ each for each in sm.GetService('cc').GetData('races') if each.raceID in [const.raceCaldari,
         const.raceMinmatar,
         const.raceGallente,
         const.raceAmarr] ]
        for race in races:
            if race.raceID & corp.allowedMemberRaceIDs:
                rName = Tr(race.raceName, 'character.races.raceName', race.dataID)
                if len(allowedRaces):
                    allowedRaces = '%s, %s' % (allowedRaces, rName)
                else:
                    allowedRaces = rName

        self.sr.racesAllowed.text = allowedRaces



    def GetPickTicker(self, *args):
        if self.pickingTicker == 1:
            return 
        self.pickingTicker = 1
        self.PickTicker()
        self.pickingTicker = 0



    def PickTicker(self, *args):
        corpName = self.sr.corpNameEdit.GetValue()
        if len(corpName.strip()) == 0:
            eve.Message('EnterCorporationName')
            return 
        suggestions = sm.GetService('corp').GetSuggestedTickerNames(corpName)
        if not suggestions or len(suggestions) == 0:
            eve.Message('NoCorpTickerNameSuggestions')
            return 
        tmplist = []
        for each in suggestions:
            tmplist.append((each.tickerName, each.tickerName))

        ret = uix.ListWnd(tmplist, 'generic', mls.UI_CORP_SELECTTICKER, None, 1)
        if ret is not None and len(ret):
            self.sr.corpTickerEdit.SetValue(ret[0])




class EditCorpDetails(CorpDetails):
    __guid__ = 'form.EditCorpDetails'

    def ApplyAttributes(self, attributes):
        corp = sm.GetService('corp').GetCorporation()
        self.caption = mls.UI_CORP_EDITCORPDETAILS
        self.corporationName = corp.corporationName
        self.description = corp.description
        self.url = corp.url
        self.taxRate = corp.taxRate * 100.0
        self.applicationsEnabled = corp.isRecruiting
        form.CorpDetails.ApplyAttributes(self, attributes)
        self.sr.corpNameEdit_container.state = uiconst.UI_HIDDEN
        self.sr.corpTickerEdit_container.state = uiconst.UI_HIDDEN
        self.name = 'editcorp'
        self.result = {}
        self.sr.priorlogo = (corp.shape1,
         corp.shape2,
         corp.shape3,
         corp.color1,
         corp.color2,
         corp.color3)
        shapes = [corp.shape1, corp.shape2, corp.shape3]
        colors = [corp.color1, corp.color2, corp.color3]
        self.corpLogo = uiutil.GetLogoIcon(itemID=session.corpid, acceptNone=False, pos=(0, 0, 90, 90))
        self.sr.logocontrol.children.insert(0, self.corpLogo)
        self.SetupLogo(shapes, colors)
        self.sr.memberLimit.text = str(corp.memberLimit)
        allowedRaces = ''
        races = [ each for each in sm.GetService('cc').GetData('races') if each.raceID in [const.raceCaldari,
         const.raceMinmatar,
         const.raceGallente,
         const.raceAmarr] ]
        for race in races:
            if race.raceID & corp.allowedMemberRaceIDs:
                rName = Tr(race.raceName, 'character.races.raceName', race.dataID)
                if len(allowedRaces):
                    allowedRaces = '%s, %s' % (allowedRaces, rName)
                else:
                    allowedRaces = rName

        self.sr.racesAllowed.text = allowedRaces
        self.sr.main.state = uiconst.UI_NORMAL
        self.HideLoad()



    def Submit(self, *args):
        myCorp = sm.GetService('corp').GetCorporation()
        (shape1, shape2, shape3, color1, color2, color3,) = self.sr.prefs
        if self.sr.priorlogo != (shape1,
         shape2,
         shape3,
         color1,
         color2,
         color3):
            if eve.Message('AskAcceptLogoChangeCost', {'cost': const.corpLogoChangeCost}, uiconst.YESNO, default=uiconst.ID_NO) == uiconst.ID_YES:
                sm.GetService('corp').UpdateLogo(shape1, shape2, shape3, color1, color2, color3, None)
        if self.sr.priordesc != self.sr.descEdit.GetValue() or self.sr.priorurl != self.sr.urlEdit.GetValue() or self.sr.priortaxRate != self.sr.taxRateEdit.GetValue() or self.sr.priorapplicationsEnabled != self.sr.applicationsEnabled.checked:
            urlvalue = self.sr.urlEdit.GetValue() and self.sr.urlEdit.GetValue().strip()
            if urlvalue:
                urlvalue = util.FormatUrl(urlvalue)
            sm.GetService('corp').UpdateCorporation(self.sr.descEdit.GetValue().strip(), urlvalue, self.sr.taxRateEdit.GetValue() / 100.0, self.sr.applicationsEnabled.checked)
            sm.GetService('corpui').ResetWindow(bShowIfVisible=1)
        if self.isModal:
            self.SetModalResult(uiconst.ID_OK)
        else:
            self.SelfDestruct()




class CreateCorp(CorpDetails):
    __guid__ = 'form.CreateCorp'
    __nonpersistvars__ = ['result']

    def ApplyAttributes(self, attributes):
        self.caption = mls.UI_CORP_CREATECORPORATION
        self.corporationName = ''
        self.description = mls.UI_CORP_ENTERDESCRIPTIONHERE
        self.url = 'http://'
        self.taxRate = 0.0
        self.applicationsEnabled = True
        form.CorpDetails.ApplyAttributes(self, attributes)
        self.name = 'createcorp'
        self.sr.racesAllowed_container.state = uiconst.UI_HIDDEN
        self.sr.memberLimit_container.state = uiconst.UI_HIDDEN
        self.result = {}
        import random
        randomNumber = random.choice(const.graphicCorpLogoLibShapes.keys())
        self.corpLogo = uicls.CorpIcon(acceptNone=False, pos=(0, 0, 90, 90))
        self.sr.logocontrol.children.insert(0, self.corpLogo)
        self.SetupLogo([randomNumber, const.graphicCorpLogoLibNoShape, const.graphicCorpLogoLibNoShape], [None, None, None])
        self.sr.main.state = uiconst.UI_NORMAL



    def Submit(self, *args):
        corpName = self.sr.corpNameEdit.GetValue()
        if len(corpName.strip()) == 0:
            raise UserError('EnterCorporationName')
        corpTicker = self.sr.corpTickerEdit.GetValue()
        if len(corpTicker.strip()) == 0:
            raise UserError('EnterTickerName')
        if not session.stationid:
            raise UserError('CanOnlyCreateCorpInStation')
        description = self.sr.descEdit.GetValue().strip()
        taxRate = self.sr.taxRateEdit.GetValue() / 100.0
        url = self.sr.urlEdit.GetValue()
        applicationsEnabled = self.sr.applicationsEnabled.GetValue()
        (shape1, shape2, shape3, color1, color2, color3,) = self.sr.prefs
        sm.GetService('corp').AddCorporation(corpName, corpTicker, description, url, taxRate, shape1, shape2, shape3, color1, color2, color3, applicationsEnabled=applicationsEnabled)
        self.SelfDestruct()




class CorpLogoPicker(uicls.Container):
    __guid__ = 'uicls.CorpLogoPickerContainer'
    default_name = 'corplogosubpar'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        FRAME_COLOR = util.Color.GetGrayRGBA(0.4, 1.0)
        layer1 = uicls.Container(parent=self, name='layer1', pos=(0, 0, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic1 = uicls.Container(parent=layer1, name='layerPic1', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerPic1, color=FRAME_COLOR)
        self.layerStyle1 = uicls.Container(parent=layer1, name='layerStyle1', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerStyle1, color=FRAME_COLOR)
        layer2 = uicls.Container(parent=self, name='layer2', pos=(0, 30, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic2 = uicls.Container(parent=layer2, name='layerPic2', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerPic2, color=FRAME_COLOR)
        self.layerStyle2 = uicls.Container(parent=layer2, name='layerStyle2', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerStyle2, color=FRAME_COLOR)
        layer3 = uicls.Container(parent=self, name='layer3', pos=(0, 60, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic3 = uicls.Container(parent=layer3, name='layerPic3', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerPic3, color=FRAME_COLOR)
        self.layerStyle3 = uicls.Container(parent=layer3, name='layerStyle3', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        uicls.Frame(parent=self.layerStyle3, color=FRAME_COLOR)



