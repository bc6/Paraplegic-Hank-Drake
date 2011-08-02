import blue
import draw
import uix
import uiutil
import util
import xtriui
import types
import form
import listentry
import math
import uthread
import uicls
import uiconst
INFOWIDTH = 170
TREEWIDTH = 420
EXPANDERWIDTH = 16
MINHEIGHT = 450
COLOR = [(0.44,
  0.28,
  0.28,
  0.15),
 (0.53,
  0.53,
  0.29,
  0.15),
 (0.65,
  0.71,
  0.65,
  0.15),
 (0.35,
  0.5,
  0.52,
  0.15)]
RED = 0
YELLOW = 1
GREEN = 2
BLUE = 3

class CertificateWindow(uicls.Window):
    __guid__ = 'form.certificateWindow'
    __notifyevents__ = ['OnCertificateIssued', 'OnGodmaSkillTrained', 'OnGodmaSkillStartTraining']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        certID = attributes.certID
        sm.StartService('certificates')
        self.certID = certID
        self.actualMinSize = 650
        self.SetMinSize([self.actualMinSize, 460])
        self.MakeUnstackable()
        self.SetCaption(mls.UI_SHARED_CERTPLANNER)
        self.SetTopparentHeight(0)
        self.SetWndIcon('ui_79_64_1')
        self.sr.leftframe = uicls.Container(name='leftframe', align=uiconst.TOLEFT, parent=self.sr.main, width=200, top=0, clipChildren=1)
        top = uicls.Container(name='top', parent=self.sr.leftframe, align=uiconst.TOTOP, height=44)
        top.state = uiconst.UI_DISABLED
        uicls.CaptionLabel(text=mls.UI_SHARED_CERTPLANNER, parent=top, align=uiconst.TOALL, linespace=16, left=8, top=4, uppercase=0, letterspace=0, autowidth=0, autoheight=0)
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftframe, 'width', 'x', 200, 350)
        uicls.Line(parent=divider, align=uiconst.TORIGHT)
        uicls.Line(parent=divider, align=uiconst.TOLEFT)
        divider.OnSizeChanging = self._OnSizeChanging
        self.sr.divider = divider
        self.sr.expanderframe = uicls.Container(name='infoframe', align=uiconst.TOLEFT, parent=self.sr.main, width=EXPANDERWIDTH, top=0, clipChildren=0)
        self.sr.infoframe = uicls.Container(name='infoframe', align=uiconst.TOLEFT, parent=self.sr.main, width=INFOWIDTH, top=0, clipChildren=1)
        self.sr.rightframe = uicls.Container(name='rightframe', parent=self.sr.main, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), align=uiconst.TOALL)
        self.sr.buttonPar = uicls.Container(name='buttonParent', align=uiconst.TOBOTTOM, height=20, parent=self.sr.leftframe)
        self.sr.btns = btns = [(mls.UI_SHARED_CERT_APPLYFORALL,
          self.ApplyForAllCerts,
          (),
          84)]
        self.sr.buttonWnd = uicls.ButtonGroup(btns=btns, parent=self.sr.buttonPar, unisize=1, line=0)
        self.sr.scroll = uicls.Scroll(parent=self.sr.leftframe, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.OnSelectionChange = self.CheckTypeScrollSelection
        tabs = uicls.TabGroup(name='tabparent', parent=self.sr.leftframe, idx=0)
        tabs.Startup([[mls.UI_SHARED_CERTIFICATES,
          self.sr.scroll,
          self,
          'cert_groups'], [mls.UI_GENERIC_SETTINGS,
          self.sr.scroll,
          self,
          'cert_settings']], 'cs_certs', autoselecttab=1)
        self.sr.certTabs = tabs
        self.sr.scroll2Parent = uicls.Container(name='scroll2Parent', parent=self.sr.rightframe, align=uiconst.TOTOP, top=const.defaultPadding)
        self.sr.scroll2 = uicls.Scroll(name='scroll2', parent=self.sr.scroll2Parent, align=uiconst.TOBOTTOM, height=100)
        self.scroll2MaxHeight = 0
        self.FormatScroll(self.sr.scroll2)
        self.sr.focusSlotCont = uicls.Container(name='focusSlotCont', align=uiconst.TOTOP, parent=self.sr.rightframe, top=0, clipChildren=0, height=100)
        self.sr.scroll3 = uicls.Scroll(name='scroll3', parent=self.sr.rightframe, align=uiconst.TOTOP)
        self.FormatScroll(self.sr.scroll3)
        self.mySkills = sm.StartService('skills').MySkillLevelsByID()
        self.sr.history = []
        self.sr.historyIdx = None
        self.browsing = 0
        self.applying = 0
        self.showing = None
        self.LoadInfoSection()
        self.LoadExpanderSection()
        self.LoadTree(self.certID)
        minWidth = self.sr.leftframe.width + self.sr.infoframe.width + TREEWIDTH + EXPANDERWIDTH
        self.SetMinSize([minWidth, MINHEIGHT])



    def Load(self, key):
        self.sr.scroll.Load(contentList=[])
        self.sr.scroll.ShowHint('')
        if key == 'cert_settings':
            self.LoadSettings()
        elif key == 'cert_groups':
            self.LoadGroups()
        self.showing = key



    def LoadInfoSection(self):
        uicls.Line(parent=self.sr.infoframe, align=uiconst.TORIGHT)
        self.sr.captionCont = uicls.Container(name='captionCont', align=uiconst.TOTOP, parent=self.sr.infoframe, left=0, top=12, height=0)
        self.sr.caption = uicls.CaptionLabel(text='', parent=self.sr.captionCont, align=uiconst.TOALL, fontsize=16, left=0, autoheight=0, autowidth=0)
        self.sr.gradeCont = uicls.Container(name='gradeCont', align=uiconst.TOTOP, parent=self.sr.infoframe, left=0, height=0)
        self.sr.gradeText = uicls.Label(text='', parent=self.sr.gradeCont, left=0, top=0, align=uiconst.TOALL, fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, uppercase=1, autowidth=False, autoheight=False)
        self.sr.subcaptionCont = uicls.Container(name='subcaptionCont', align=uiconst.TOTOP, parent=self.sr.infoframe, left=0, height=0)
        self.sr.subcaption = uicls.Label(text='', parent=self.sr.subcaptionCont, left=0, top=0, align=uiconst.TOALL, state=uiconst.UI_DISABLED, autowidth=False, autoheight=False)
        self.sr.descCont = uicls.Container(name='descCont', align=uiconst.TOTOP, parent=self.sr.infoframe, left=0, height=220)
        uicls.Container(name='push', parent=self.sr.descCont, align=uiconst.TORIGHT, width=const.defaultPadding)
        self.sr.desc = uicls.Edit(parent=self.sr.descCont, padRight=0, readonly=1, hideBackground=1)
        self.sr.caption2Cont = uicls.Container(name='captionCont', align=uiconst.TOTOP, parent=self.sr.infoframe, left=0, top=12, height=16)
        self.sr.caption2 = uicls.Label(text='%s:' % mls.UI_SHARED_CERT_RECOMMENDEDFOR, parent=self.sr.caption2Cont, left=0, top=0, align=uiconst.TOALL, fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, uppercase=1, mousehilite=1, autowidth=False, autoheight=False)
        uicls.Container(name='push', parent=self.sr.infoframe, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        self.sr.recommendedCont = uicls.Container(name='recommendedCont', align=uiconst.TOALL, parent=self.sr.infoframe, pos=(0, 0, 0, 0))
        self.sr.recommended = uicls.Scroll(name='recommendedScroll', parent=self.sr.recommendedCont, padding=(4, 0, 4, 0))
        self.FormatScroll(self.sr.recommended)



    def LoadExpanderSection(self):
        self.expanded = settings.user.ui.Get('cert_infoExpanded', 1)
        self.sr.expanderIcon = uicls.Transform(name='iconCont', align=uiconst.RELATIVE, parent=self.sr.expanderframe, left=0, width=16, top=0, isClipper=1, height=16, state=uiconst.UI_NORMAL, rotation=0.0)
        expander = uicls.Sprite(parent=self.sr.expanderIcon, pos=(5, 0, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderUp.png', align=uiconst.CENTERLEFT)
        expander.OnClick = self.ToggleInfoSection
        if self.expanded:
            self.RotateIcon(self.sr.expanderIcon, 90)
            self.sr.infoframe.width = INFOWIDTH
        else:
            self.RotateIcon(self.sr.expanderIcon, -90)
            self.sr.infoframe.width = 0



    def LoadTree(self, certID = None, parentID = None, historyData = None):
        uix.Flush(self.sr.focusSlotCont)
        self.certID = certID
        settings.user.ui.Set('cert_lastViewed', certID)
        recommendedFor = self.GetCertificateRecommendations(certID)
        self.SetInfoText(certID, recommendedFor)
        preSkillsList = sm.StartService('certificates').GetParentSkills(certID)
        preCertsList = sm.StartService('certificates').GetParentCertificates(certID)
        preSkills = self.PrepareData(preSkillsList, cert=0)
        preCerts = self.PrepareData(preCertsList, cert=1)
        preEntriesX = preSkills + preCerts
        postCertsList = sm.StartService('certificates').GetChildCertificates(certID)
        postCerts = self.PrepareData(postCertsList, cert=1)
        scrolllist1 = []
        data = util.KeyVal()
        data.entries = preEntriesX
        data.what = 'pre'
        data.name = 'PrepostClass'
        scrolllist1.append(listentry.Get('PrepostClass', data=data))
        self.sr.scroll2.Load(contentList=scrolllist1, scrollTo=1)
        scrolllist2 = []
        data = util.KeyVal()
        data.entries = postCerts
        data.what = 'post'
        test = listentry.Get('PrepostClass', data=data)
        scrolllist2.append(test)
        self.sr.scroll3.Load(contentList=scrolllist2, scrollTo=0.0)
        preHeight = 40 * ((len(preEntriesX) + 1) / 2)
        self.sr.scroll2.height = self.scroll2MaxHeight = preHeight + 4
        entryInfo = self.PrepareData([certID], cert=1)
        if entryInfo:
            entry = entryInfo[0]
            focusSlotHeight = 52
            height = (self.sr.focusSlotCont.height - focusSlotHeight) / 2 + 2
            if preEntriesX:
                self.sr.preIcon = uicls.Container(name='preIcon', align=uiconst.CENTERTOP, parent=self.sr.focusSlotCont, width=16, clipChildren=1, height=16, state=uiconst.UI_NORMAL)
                icon = uicls.Sprite(parent=self.sr.preIcon, idx=0, pos=(1, 0, 11, 11), name='expandericon', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderDown.png', align=uiconst.CENTERTOP)
            if postCerts:
                self.sr.postIcon = uicls.Container(name='postIcon', align=uiconst.CENTERBOTTOM, parent=self.sr.focusSlotCont, width=16, clipChildren=1, height=16, state=uiconst.UI_NORMAL)
                icon = uicls.Sprite(parent=self.sr.postIcon, idx=0, pos=(1, 0, 11, 11), name='expandericon', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderDown.png', align=uiconst.CENTERTOP)
            entry.topOffset = 4
            entry.isFocusSlot = 1
            extraFrameCont = uicls.Container(name='extraFrameCont', align=uiconst.CENTER, parent=self.sr.focusSlotCont, width=208, height=60, state=uiconst.UI_DISABLED)
            color = COLOR[entry.color]
            color = (color[0],
             color[1],
             color[2],
             0.5)
            uicls.Frame(parent=extraFrameCont, weight=2, color=color)
            focusSlot = xtriui.CertSlot(name='%s' % entry.label, parent=self.sr.focusSlotCont, align=uiconst.CENTER, width=200, height=focusSlotHeight, state=uiconst.UI_NORMAL)
            focusSlot.Startup(entry.label, 'ui_7_64_3', entry.label, entry)
            if sm.StartService('certificates').HasPrerequisites(self.certID) and not sm.StartService('certificates').HaveCertificate(self.certID):
                btn = uicls.Button(parent=focusSlot, label=mls.UI_CMD_CLAIM, func=self.ApplyForCert, args=(certID,), pos=(2, 2, 0, 0), idx=1, alwaysLite=True, align=uiconst.BOTTOMRIGHT)
                btn.name = 'certificatesPlannerClaimCertificateBtn'
        self.HideGoBack()
        self.HideGoForward()
        historyIdx = None
        if historyData is None:
            if self.sr.historyIdx is not None:
                self.sr.history = self.sr.history[:(self.sr.historyIdx + 1)]
            self.sr.history.append((certID, parentID, len(self.sr.history)))
            self.sr.historyIdx = None
        else:
            (_certID, _parentID, historyIdx,) = historyData
            self.sr.historyIdx = historyIdx
        if len(self.sr.history) > 1:
            if historyIdx != 0:
                if historyIdx:
                    self.GoBack = (self.Browse, self.sr.history[(historyIdx - 1)], self)
                else:
                    self.GoBack = (self.Browse, self.sr.history[-2], self)
                self.ShowGoBack()
            if historyIdx is not None and historyIdx != len(self.sr.history) - 1:
                self.GoForward = (self.Browse, self.sr.history[(historyIdx + 1)], self)
                self.ShowGoForward()
        self.ShowHeaderButtons(1)



    def Browse(self, settings, wnd, *args):
        if getattr(self, 'browsing', 0):
            return 
        self.browsing = 1
        (certID, parentID, idx,) = settings
        self.LoadTree(certID, parentID, historyData=settings)
        self.browsing = 0



    def ApplyFiltersAndConvertToDict(self, certRs):
        certDict = {}
        for r in certRs:
            certDict[r.certificateID] = r

        certFilter = settings.user.ui.Get('certWnd_showCert', None)
        if certFilter == 'current':
            ret = {}
            for (key, value,) in certDict.iteritems():
                if sm.StartService('certificates').HaveCertificate(key):
                    ret[key] = value

            return ret
        else:
            if certFilter == 'haveSome':
                ret = {}
                for (key, value,) in certDict.iteritems():
                    reqCerts = sm.StartService('certificates').GetParentCertificates(key)
                    reqSkills = sm.StartService('certificates').GetParentSkills(key)
                    for each in reqSkills:
                        (skillID, level,) = each
                        skillStatus = self.SkillStatus(skillID, level)
                        if skillStatus.status == GREEN:
                            ret[key] = value
                            continue

                    for each in reqCerts:
                        if sm.StartService('certificates').HaveCertificate(each):
                            ret[key] = value
                            continue


                return ret
            if certFilter == 'readyCerts':
                ret = {}
                for (key, value,) in certDict.iteritems():
                    if sm.StartService('certificates').HaveCertificate(key):
                        continue
                    hasPrerequisites = sm.StartService('certificates').HasPrerequisites(key)
                    if hasPrerequisites:
                        ret[key] = value

                return ret
            return certDict



    def LoadGroups(self):
        self.sr.scroll.Load(contentList=[], headers=[])
        filteredCerts = self.ApplyFiltersAndConvertToDict(cfg.certificates)
        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        allCategories = sm.StartService('certificates').GetCategories(filteredCerts)
        scrolllist = []
        for (category, value,) in allCategories.iteritems():
            categoryObj = categoryData[category]
            label = Tr(categoryObj.categoryName, 'cert.categories.categoryName', categoryObj.dataID)
            data = {'GetSubContent': self.GetSubContent,
             'label': label,
             'groupItems': value,
             'id': ('certGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked',
             'name': 'certificatesPlanner%sBtn' % label.replace(' ', '').capitalize(),
             'BlockOpenWindow': 1}
            scrolllist.append((label, listentry.Get('Group', data)))

        if not scrolllist:
            self.sr.scroll.Load(contentList=[])
            self.sr.scroll.ShowHint(mls.UI_RMR_TEXT10)
        else:
            scrolllist = uiutil.SortListOfTuples(scrolllist)
            self.sr.scroll.Load(contentList=scrolllist, headers=[])



    def GetSubContent(self, dataX, *args):
        scrolllist = []
        grades = sm.StartService('certificates').GetGrades(dataX.groupItems)
        toggleGroups = settings.user.ui.Get('certWnd_toggleOneCertGroupAtATime', 1)
        if toggleGroups:
            dataWnd = sm.StartService('window').GetWindow(unicode(dataX.id), create=0)
            if not dataWnd:
                for entry in self.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == dataX.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        for (grade, value,) in grades.iteritems():
            id = ('certGroups_grades', '%s_%s' % (dataX.cat, grade))
            label = getattr(mls, 'UI_SHARED_CERTGRADE%s' % grade, 'Basic')
            data = {'GetSubContent': self.GetEntries,
             'label': label,
             'groupItems': value,
             'id': id,
             'sublevel': 1,
             'showlen': 0,
             'showicon': 'hide',
             'state': 'locked'}
            scrolllist.append((grade, listentry.Get('Group', data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GetEntries(self, data, *args):
        scrolllist = []
        for each in data.groupItems:
            entry = self.CreateEntry(each)
            scrolllist.append((entry.text, entry))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def CreateEntry(self, data, *args):
        certID = data.certificateID
        haveCert = sm.StartService('certificates').HaveCertificate(certID)
        inProgress = None
        hasPrerequisites = None
        certInfo = cfg.certificates.Get(certID)
        if not haveCert:
            hasPrerequisites = sm.StartService('certificates').HasPrerequisites(certID)
            if not hasPrerequisites:
                inProgress = self.IsInProgress(certID)
        (label, grade, descr,) = uix.GetCertificateLabel(certID)
        entry = {'line': 1,
         'text': label,
         'indent': 3,
         'haveCert': haveCert,
         'inProgress': inProgress,
         'hasPrereqs': hasPrerequisites,
         'certID': certID,
         'OnClick': self.OnListClick,
         'grade': certInfo.grade}
        return listentry.Get('CertTreeEntry', entry)



    def CheckTypeScrollSelection(self, sel):
        if len(sel) == 1:
            entry = sel[0]
            if entry.__guid__ == 'listentry.CertTreeEntry':
                entry.OnClick(entry.panel)



    def OnListClick(self, entry, *args):
        if not self or self.destroyed:
            return 
        selection = entry.sr.node.scroll.GetSelectedNodes(entry.sr.node)
        if not selection:
            return 
        entry = selection[0]
        certID = entry.certID
        self.LoadTree(certID)



    def LoadSettings(self):
        scrolllist = []
        for (cfgname, value, label, checked, group,) in [['certWnd_showCert',
          'current',
          mls.UI_SHARED_CERT_SHOWCURRENT,
          settings.user.ui.Get('certWnd_showCert', 'allCerts') == 'current',
          'certWnd_group'],
         ['certWnd_showCert',
          'haveSome',
          mls.UI_SHARED_CERT_SHOWOWNPREREQ,
          settings.user.ui.Get('certWnd_showCert', 'allCerts') == 'haveSome',
          'certWnd_group'],
         ['certWnd_showCert',
          'readyCerts',
          mls.UI_SHARED_CERT_SHOWALLPREREQ,
          settings.user.ui.Get('certWnd_showCert', 'allCerts') == 'readyCerts',
          'certWnd_group'],
         ['certWnd_showCert',
          'allCerts',
          mls.UI_SHARED_SHOWALLCERTS,
          settings.user.ui.Get('certWnd_showCert', 'allCerts') == 'allCerts',
          'certWnd_group'],
         ['certWnd_toggleOneCertGroupAtATime',
          None,
          mls.UI_SHARED_TOGGLEONECERTGROUP,
          settings.user.ui.Get('certWnd_toggleOneCertGroupAtATime', 1),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        self.sr.scroll.Load(contentList=scrolllist)



    def FormatScroll(self, scroll):
        scroll.HideBackground(alwaysHidden=1)
        scroll.lineWeight = 0
        scroll.RemoveActiveFrame()



    def _OnSizeChanging(self, *args):
        minWidth = self.sr.leftframe.width + self.sr.infoframe.width + TREEWIDTH + EXPANDERWIDTH
        self.SetMinSize([minWidth, MINHEIGHT])



    def OnClose_(self, *args):
        settings.user.ui.Set('cert_infoExpanded', self.expanded)



    def _OnResize(self, *args):
        uthread.new(self._CertificateWindow__OnResize)



    def __OnResize(self, *args):
        if self and not self.destroyed:
            self.sr.divider.max = 400
            minWidth = self.sr.leftframe.width + self.sr.infoframe.width + TREEWIDTH + EXPANDERWIDTH
            self.SetMinSize([minWidth, MINHEIGHT])
            self.scrollHeight = self.absoluteBottom - self.absoluteTop
            height = (self.absoluteBottom - self.absoluteTop - 120) / 2
            self.sr.scroll2Parent.height = max(64, height)
            if self.scroll2MaxHeight > self.sr.scroll2Parent.height:
                self.sr.scroll2.height = self.sr.scroll2Parent.height - 4
            else:
                self.sr.scroll2.height = self.scroll2MaxHeight
            self.sr.scroll3.height = max(64, height) - 8
            self.sr.scroll2._OnResize()
            self.sr.scroll3._OnResize()



    def CheckBoxChange(self, checkbox):
        if checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'certWnd_showCert':
                if checkbox.data['retval'] is None:
                    settings.user.ui.Set(key, checkbox.checked)
                else:
                    settings.user.ui.Set(key, checkbox.data['retval'])
            else:
                settings.user.ui.Set(key, checkbox.checked)



    def ToggleInfoSection(self, *args):
        self.sr.divider.max = 400
        rFrameWidth = self.sr.rightframe.absoluteRight - self.sr.rightframe.absoluteLeft
        expandWnd = 0
        rotation = 0
        if rFrameWidth < TREEWIDTH:
            expandWnd = 1
        infoframeWidth = self.sr.infoframe.width
        if infoframeWidth == 0:
            self.RotateIcon(self.sr.expanderIcon, 90)
            if expandWnd:
                newWidth = self.width - rFrameWidth + TREEWIDTH + INFOWIDTH
                uicore.effect.MorphUI(self, 'width', newWidth, 100.0, newthread=1, ifWidthConstrain=0)
            uicore.effect.MorphUI(self.sr.infoframe, 'width', INFOWIDTH, 100.0)
            self.expanded = 1
            rotation = 1
        else:
            uicore.effect.MorphUI(self.sr.infoframe, 'width', 0, 100.0)
            self.RotateIcon(self.sr.expanderIcon, -90)
            self.expanded = 0
            rotation = -1
        blue.pyos.synchro.Sleep(100)
        infoWidth = [INFOWIDTH, 0][bool(infoframeWidth)]
        minWidth = self.sr.leftframe.width + infoWidth + TREEWIDTH + EXPANDERWIDTH
        self.SetMinSize([minWidth, MINHEIGHT])



    def SetInfoText(self, certID = None, recommendedFor = {}):
        if not certID:
            return 
        (label, grade, descr,) = uix.GetCertificateLabel(certID)
        certInfo = cfg.certificates.Get(certID)
        self.sr.caption.text = label
        self.sr.captionCont.height = self.sr.caption.textheight
        self.sr.gradeText.text = grade
        self.sr.gradeCont.height = self.sr.gradeText.textheight
        self.sr.subcaption.text = mls.UI_SHARED_ISSUEDVIA % {'corpName': cfg.eveowners.Get(certInfo.corpID).ownerName}
        self.sr.subcaptionCont.height = self.sr.subcaption.textheight
        self.sr.desc.LoadHTML('<body>%s</body>' % descr, newThread=0)
        if not recommendedFor:
            self.sr.caption2.state = uiconst.UI_HIDDEN
            self.sr.recommended.Load(contentList=[])
            return 
        recommended = ''
        scrolllist = []
        for (key, value,) in recommendedFor.iteritems():
            shipsString = ''
            for each in value:
                shipsString += '%s<br>' % cfg.invtypes.Get(each).name

            if len(shipsString) > 4:
                shipsString = shipsString[:-4]
            label = '%s - [%s]' % (mls.UI_SHARED_LIST % {'item': cfg.invgroups.Get(key).name}, len(value))
            entry = util.KeyVal()
            entry.hideLines = 1
            entry.label = label
            entry.hint = shipsString
            entry.sublevel = 0
            entry.selectable = 0
            scrolllist.append((label, listentry.Get('ShipGroups', data=entry)))

        self.sr.caption2.state = uiconst.UI_NORMAL
        self.sr.caption2.OnClick = (self.ShowInfoOnRecommendedFor, certID)
        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.sr.recommended.Load(contentList=scrolllist, headers=[])



    def ShowInfoOnRecommendedFor(self, certID, *args):
        wnd = self.ShowInfo(certID, cfg.certificates.Get(certID).grade)
        uthread.pool('CertificateWindow::ShowPanel', wnd.sr.maintabs.ShowPanelByName, mls.UI_SHARED_CERT_RECOMMENDED)



    def RotateIcon(self, icon, degrees):
        radians = math.pi / 180
        radians = radians * degrees
        self.sr.expanderIcon.SetRotation(radians)



    def PrepareData(self, list, cert = 1):
        ret = []
        for each in list:
            entry = util.KeyVal()
            if cert:
                entry.certID = each
                entry.typeID = 29530
                entry.have = 0
                entry.color = RED
                if sm.StartService('certificates').HaveCertificate(each):
                    entry.have = 1
                    entry.color = GREEN
                elif sm.StartService('certificates').HasPrerequisites(each):
                    entry.color = BLUE
                elif sm.StartService('certificates').IsInProgress(each):
                    entry.color = YELLOW
                (label, grade, descr,) = uix.GetCertificateLabel(each)
                entry.label = label
                entry.descr = descr
                certInfo = cfg.certificates.Get(each)
                entry.icon = 'ui_79_64_%s' % (certInfo.grade + 1)
                entry.grade = certInfo.grade
            else:
                (skillID, level,) = each
                entry.certID = None
                entry.typeID = skillID
                entry.level = level
                skillStatus = self.SkillStatus(skillID, level)
                entry.color = skillStatus.status
                entry.have = bool(entry.color)
                skillInfo = cfg.invtypes.Get(skillID)
                entry.label = '%s' % skillInfo.typeName
                entry.descr = skillInfo.description
                entry.iconID = skillInfo.iconID
                entry.grade = level
                if skillStatus.status == YELLOW:
                    entry.extra = mls.UI_SHARED_CERT_CURRENTLEVEL % {'currentLevel': skillStatus.current}
            entry.width = 180
            entry.height = 40
            ret.append(entry)

        return ret



    def SkillStatus(self, skillID, level):
        status = sm.StartService('certificates').SkillStatus(skillID, level)
        return status



    def IsInProgress(self, certID):
        return sm.StartService('certificates').IsInProgress(certID)



    def ApplyForCert(self, certID, *args):
        if not certID:
            return 
        sm.GetService('certificates').GrantCertificate(certID)



    def ApplyForAllCerts(self, *args):
        if self.applying:
            return 
        certificateSvc = sm.StartService('certificates')
        sm.GetService('loading').ProgressWnd(mls.UI_SHARED_CERT_AWARDING, mls.UI_SHARED_CERT_COLLECTING, 1, 4)
        msgProgress = ''
        msgNotify = ''
        awardedList = []
        try:
            self.applying = 1
            button = self.sr.buttonWnd.GetBtnByLabel(mls.UI_SHARED_CERT_APPLYFORALL)
            if button:
                uthread.new(self.EnableButtonTimer, button)
                button.Disable()
            readyDict = certificateSvc.FindAvailableCerts(showProgress=1)
            readyList = readyDict.keys()
            if readyList:
                sm.GetService('loading').ProgressWnd(mls.UI_SHARED_CERT_AWARDING, mls.UI_SHARED_CERT_REQUESTING, 3, 4)
                certificateSvc.GrantAllCertificates(readyDict.keys())
                msgProgress = mls.UI_SHARED_CERT_AWARDEDALL % {'numCert': len(readyList)}
                for certID in readyList:
                    (label, grade, descr,) = uix.GetCertificateLabel(certID)
                    gradeNumber = cfg.certificates.Get(certID).grade
                    awardedList.append(('%s%s' % (label, gradeNumber), ('%s - %s' % (label, grade), certID)))

            else:
                msgNotify = mls.UI_SHARED_CERT_AWARDEDNONE
                msgProgress = mls.UI_GENERIC_DONE
            self.applying = 0

        finally:
            sm.GetService('loading').ProgressWnd(mls.UI_SHARED_CERT_AWARDING, msgProgress, 4, 4)

        if awardedList:
            awardedList = uiutil.SortListOfTuples(awardedList)
            uix.ListWnd(awardedList, listtype='generic', caption=mls.UI_SHARED_CERT_AWARDEDHEADER, hint=mls.UI_SHARED_CERT_AWARDED, minChoices=0, isModal=0)
        elif msgNotify:
            eve.Message('CustomNotify', {'notify': msgNotify})



    def EnableButtonTimer(self, button):
        blue.pyos.synchro.Sleep(60000)
        try:
            self.applying = 0
            button.Enable()
        except:
            pass



    def OnGodmaSkillTrained(self, skillID):
        if self.showing == 'cert_groups':
            self.LoadGroups()
        self.LoadTree(self.certID)



    def OnGodmaSkillStartTraining(self, skillID, ETA):
        self.LoadTree(self.certID)



    def OnCertificateIssued(self, certificateID = None):
        certIDViewed = self.certID
        if certIDViewed:
            self.LoadTree(certIDViewed)
            self.sr.certTabs.ReloadVisible()



    def GetCertificateRecommendations(self, certID):
        recommendedFor = sm.StartService('certificates').GetCertificateRecommendationsFromCertificateID(certID)
        groupDict = {}
        for each in recommendedFor:
            invtype = cfg.invtypes.Get(each.shipTypeID)
            groupID = invtype.Group().id
            current = groupDict.get(groupID, [])
            current.append(each.shipTypeID)
            groupDict[groupID] = current

        return groupDict



    def ShowInfo(self, certID, grade, *args):
        abstractinfo = util.KeyVal(certificateID=certID, grade=grade)
        wnd = sm.StartService('info').ShowInfo(const.typeCertificate, abstractinfo=abstractinfo)
        return wnd




class PrepostClass(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.PrepostClass'

    def Startup(self, *args):
        self.numRows = 0
        self.height = 0
        self.parentScrolling = None
        self.entries = []
        self.what = 'pre'
        self.state = uiconst.UI_PICKCHILDREN



    def Load(self, node):
        self.parentScrolling = node.scroll.sr.scrollcontrols
        self.sr.node = node
        data = node
        self.entries = data.entries
        self.what = data.what
        self.CreatePanel()



    def CreatePanel(self):
        i = 0
        j = 0
        if not len(self.entries):
            return 
        entriesWidth = 10
        self.rightCont = rightCont = uicls.Container(name='rightCont', parent=self, align=uiconst.TORIGHT, width=entriesWidth, state=uiconst.UI_NORMAL)
        self.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=entriesWidth, state=uiconst.UI_NORMAL)
        for entry in self.entries:
            whereInRow = i % 2
            align = uiconst.TOPRIGHT if whereInRow else uiconst.TOPLEFT
            cont = rightCont if whereInRow else self.leftCont
            slot = xtriui.CertSlot(name='%s' % entry.label, parent=cont, align=align, left=0, top=j * entry.height, width=entry.width, height=entry.height - 4, state=uiconst.UI_NORMAL)
            slot.Startup('%s' % entry.label, 'ui_7_64_3', '%s' % entry.label, entry)
            slot.OnClick = (self.OnClick, entry)
            if self.what == 'pre' and i == 0 and len(self.entries) % 2:
                j += 1
                i += 1
            elif self.what == 'post' and len(self.entries) - 1 == i:
                j += 1
            elif i % 2:
                j += 1
            i += 1
            self.rightCont.width = max(self.rightCont.width, entry.width)
            self.leftCont.width = max(self.leftCont.width, entry.width)

        if len(self.entries) and j == 0:
            j = 1
        self.numRows = j
        self.SetHeight(j)
        self.sr.c = c = uicls.Container(name='linesContainer', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_NORMAL)
        self.MakeLines(c, self.what, self.numRows, rowHeight=40, odd=len(self.entries) % 2)
        self.SetAlign(uiconst.TOTOP)



    def OnClick(self, entry, *args):
        certID = getattr(entry, 'certID', None)
        if certID == None:
            return 
        if type(certID) != types.IntType:
            return 
        wnd = sm.StartService('certificates').FindCertificateWindow()
        if wnd:
            wnd.LoadTree(certID)



    def SetHeight(self, numRows):
        self.sr.node.height = numRows * 40
        self.height = self.sr.node.height



    def GetHeight(self, *args):
        (node, width,) = args
        iconsize = node.Get('iconsize', 32)
        node.height = iconsize
        return node.height



    def MakeLines(self, container, what, rows, rowHeight = 40, odd = 0):
        centerLineHeight = (rows - 1) * rowHeight + rowHeight / 2
        align = [uiconst.TOPLEFT, uiconst.BOTTOMLEFT][(what == 'pre')]
        self.sr.lineCont = uicls.Container(name='lineCont', parent=container, align=uiconst.CENTERBOTTOM, height=centerLineHeight, width=12)
        if what != 'pre':
            self.sr.lineCont.SetAlign(uiconst.CENTERTOP)
        self.sr.center = uicls.Line(parent=self.sr.lineCont, align=align, height=centerLineHeight, width=2, left=5)
        if what != 'pre':
            self.sr.center.height += 1
        for x in range(rows):
            top = x * rowHeight + rowHeight / 2
            lLine = uicls.Line(parent=container, align=uiconst.RELATIVE, height=1, left=0, top=top, width=10)
            lLine.top = top
            setattr(self.sr, '%s_lLine' % x, lLine)
            rLine = uicls.Line(parent=container, align=uiconst.TOPRIGHT, height=1, left=0, top=top, width=10)
            if odd:
                if what == 'pre' and x == 0 or what == 'post' and x == rows - 1:
                    rLine.state = uiconst.UI_HIDDEN
            setattr(self.sr, '%s_rLine' % x, rLine)

        self._OnResize()



    def _OnResize(self, *args):
        if not self or self.destroyed or not self.sr.Get('center'):
            return 
        (rl, rt, rw, rh,) = self.rightCont.GetAbsolute()
        (ll, lt, lw, lh,) = self.leftCont.GetAbsolute()
        (cl, ct, cw, ch,) = self.sr.center.GetAbsolute()
        (l, t, w, h,) = self.GetAbsolute()
        rlineLength = (w - lw - rw - self.sr.center.width) / 2
        for x in range(self.numRows):
            rLine = self.sr.Get('%s_rLine' % x, None)
            lLine = self.sr.Get('%s_lLine' % x, None)
            if lLine:
                lLine.width = rlineLength
                if lLine.left + lLine.width < self.sr.center.left:
                    lLine.width += 1
            if rLine:
                rLine.width = rlineLength
                if rLine.width + lLine.width + self.sr.center.width + lw + rw < w:
                    rLine.width += 1





class CertEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.CertEntry'
    __params__ = ['label']

    def Startup(self, *etc):
        sub = uicls.Container(name='sub', parent=self)
        self.sr.icon = uicls.Icon(parent=sub, align=uiconst.TOLEFT, width=32, state=uiconst.UI_DISABLED)
        uicls.Container(name='push', parent=sub, width=18, align=uiconst.TORIGHT)
        self.sr.levelParent = uicls.Container(parent=sub, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED)
        self.sr.levelHeaderParent = uicls.Container(parent=sub, align=uiconst.TORIGHT, state=uiconst.UI_HIDDEN)
        self.sr.levels = uicls.Container(name='levels', parent=self.sr.levelParent, align=uiconst.TOPLEFT, left=0, top=5, width=48, height=10)
        uicls.Frame(parent=self.sr.levels)
        for i in xrange(5):
            uicls.Fill(parent=self.sr.levels, name='level%d' % i, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=2 + i * 9, top=2, width=8, height=6)

        self.sr.visibilityLabel = uicls.Label(text='', parent=self.sr.levelParent, left=6, top=16, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        self.sr.gradeLabel = uicls.Label(text='', parent=self.sr.levelHeaderParent, left=10, top=5, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0, align=uiconst.TOPRIGHT)
        self.sr.label = uicls.Label(text='', parent=sub, left=3, top=2, align=uiconst.TOALL, state=uiconst.UI_DISABLED, autowidth=False, autoheight=False)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=sub, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo



    def Load(self, node):
        self.sr.node = node
        data = node
        self.certID = data.certID
        (label, grade, descr,) = uix.GetCertificateLabel(self.certID)
        self.sr.label.top = 2
        self.sr.label.text = label
        grade = data.grade
        self.grade = grade
        self.sr.gradeLabel.text = getattr(mls, 'UI_SHARED_CERTGRADE%s' % grade, '')
        if data.Get('icon', None):
            self.sr.icon.LoadIcon(data.icon, ignoreSize=True)
            self.sr.icon.SetSize(32, 32)
        self.sr.visibilityLabel.text = mls.UI_GENERIC_PUBLIC if data.visibility else mls.UI_GENERIC_PRIVATE
        if data.Get('hideBar', None):
            self.sr.levelParent.state = uiconst.UI_HIDDEN
        else:
            self.sr.levelParent.state = uiconst.UI_DISABLED
            self.UpdateGrades(grade)
        self.sr.levelHeaderParent.state = uiconst.UI_DISABLED
        self.sr.levelHeaderParent.width = max(self.sr.gradeLabel.textwidth + 30, 85)
        self.sr.levelParent.width = self.sr.levels.width + const.defaultPadding



    def UpdateGrades(self, newGrades):
        if len(self.sr.levels.children) < newGrades:
            return 
        for each in self.sr.levels.children[1:]:
            each.state = uiconst.UI_HIDDEN

        for each in self.sr.levels.children[1:(1 + newGrades)]:
            each.state = uiconst.UI_DISABLED




    def GetMenu(self):
        m = []
        m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (self.certID,))]
        if session.charid:
            m += [(mls.UI_CMD_OPENCERTIFICATEPLANNER, sm.StartService('certificates').OpenCertificateWindow, (self.certID,))]
        return m



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height



    def ShowInfo(self, *args):
        abstractinfo = util.KeyVal(certificateID=self.certID, grade=self.grade)
        sm.StartService('info').ShowInfo(const.typeCertificate, abstractinfo=abstractinfo)




class CertTreeEntry(listentry.Text):
    __guid__ = 'listentry.CertTreeEntry'

    def Startup(self, *args):
        listentry.Text.Startup(self, args)
        self.sr.text.color.SetRGB(1.0, 1.0, 1.0, 0.75)
        self.sr.have = uicls.Icon(parent=self, align=uiconst.CENTERLEFT, left=5, top=0, height=16, width=16)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.certID = None



    def Load(self, args):
        listentry.Text.Load(self, args)
        data = self.sr.node
        self.certID = data.certID
        self.grade = data.grade
        if data.haveCert:
            self.sr.have.LoadIcon('ui_38_16_193')
            self.sr.have.hint = mls.UI_SHARED_CERTHINT1
        elif data.hasPrereqs:
            self.sr.have.LoadIcon('ui_38_16_177')
            self.sr.have.hint = mls.UI_SHARED_CERTHINT4
        elif data.inProgress:
            self.sr.have.LoadIcon('ui_38_16_195')
            self.sr.have.hint = mls.UI_SHARED_CERTHINT2
        else:
            self.sr.have.LoadIcon('ui_38_16_194')
            self.sr.have.hint = mls.UI_SHARED_CERTHINT3
        self.sr.have.left = 15 * data.indent - 11
        self.sr.text.left = 15 * data.indent + 5
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()



    def ShowInfo(self, *args):
        abstractinfo = util.KeyVal(certificateID=self.certID, grade=self.grade)
        sm.StartService('info').ShowInfo(const.typeCertificate, abstractinfo=abstractinfo)



    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)



    def OnMouseEnter(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            eve.Message('ListEntryEnter')
            self.sr.selection.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            if self.sr.node.Get('selected', 0):
                self.Select()
            else:
                self.Deselect()



    def Select(self):
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_DISABLED



    def Deselect(self):
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN




class CertSlot(xtriui.Slots):
    __guid__ = 'xtriui.CertSlot'

    def Startup(self, *args):
        (flag, iconpath, label, data,) = args
        xtriui.Slots.Startup(self, flag, iconpath, label)
        self.rec = data
        color = COLOR[data.color]
        self.sr.have = uicls.Icon(parent=self, align=uiconst.TOPRIGHT, left=0, top=0, height=16, width=16)
        self.sr.textCont.left = 28
        self.sr.textCont.width = self.width - 44
        self.sr.text.text = label
        statusTop = 16
        if self.sr.text._numLines > 1:
            self.sr.text.top = 2
            statusTop = 20
        if data.certID:
            self.sr.status2 = uicls.Label(text=getattr(mls, 'UI_SHARED_CERTGRADE%s' % data.grade, ''), parent=self.sr.textCont, width=self.width - 32, color=None, autowidth=False, top=statusTop, left=8, state=uiconst.UI_DISABLED, idx=5)
            hint = [mls.UI_SHARED_CERTHINT3,
             mls.UI_SHARED_CERTHINT2,
             mls.UI_SHARED_CERTHINT1,
             mls.UI_SHARED_CERTHINT4][data.color]
        else:
            self.sr.status2 = uicls.Label(text=mls.UI_SHARED_CERTLEVEL % {'level': data.grade}, parent=self.sr.textCont, width=self.width - 32, color=None, autowidth=False, top=statusTop, left=8, state=uiconst.UI_DISABLED, idx=5)
            hint = [mls.UI_SHARED_TRAINEDBUTNOT,
             mls.UI_SHARED_TRAINEDBUTNOTREQLEVEL,
             mls.UI_SHARED_TRAINEDANDOFREQLEVEL,
             mls.UI_SHARED_CERTHINT4][data.color]
            extra = data.Get('extra', None)
            if extra:
                self.sr.status2.text += ' (%s)' % extra
        self.sr.icon.top = 2
        iconID = data.Get('iconID', None)
        icon = data.Get('icon', None)
        self.sr.icon.LoadIcon(iconID or icon, ignoreSize=True)
        self.sr.icon.SetSize(32, 32)
        topOffset = data.Get('topOffset', 0)
        if topOffset:
            self.sr.text.top += topOffset
            self.sr.status2.top += topOffset
            self.sr.icon.top += topOffset
        if data.Get('isFocusSlot', 0):
            color = (color[0],
             color[1],
             color[2],
             0.3)
            uicls.Frame(parent=self, color=color)
        else:
            self.DoubleFrame(self, 1, self.height, self.width, color=color)
        self.sr.color = uicls.Fill(parent=self, name='fill', state=uiconst.UI_DISABLED, color=color)
        icon = ['ui_38_16_194',
         'ui_38_16_195',
         'ui_38_16_193',
         'ui_38_16_177'][data.color]
        self.sr.have.LoadIcon(icon)
        self.sr.have.hint = hint



    def Hilite(self, state):
        if getattr(self.rec, 'isFocusSlot', 0) or not self.rec.certID:
            return 
        self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]



    def GetMenu(self, *args):
        m = []
        data = self.rec
        if not data.certID:
            if not data.typeID:
                return m
            mine = sm.StartService('skills').MySkillLevelsByID()
            skillLevel = mine.get(data.typeID, None)
            skill = sm.StartService('skills').GetMySkillsFromTypeID(data.typeID)
            if skill is not None:
                m += sm.StartService('skillqueue').GetAddMenuForSkillEntries(skill)
            if data.typeID is not None:
                m += sm.StartService('menu').GetMenuFormItemIDTypeID(None, data.typeID, ignoreMarketDetails=0)
        elif data.color == 3:
            m += [(mls.UI_CMD_CLAIMCERTIFICATE, self.ApplyForCert, (data.certID,))]
        m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (data.certID, data.grade))]
        return m



    def OnClick(self, *args):
        pass



    def OnDropData(self, dragObj, nodes):
        pass



    def GetDragData(self, *args):
        return [self]



    def ShowInfo(self, certID, grade, *args):
        abstractinfo = util.KeyVal(certificateID=certID, grade=grade)
        sm.StartService('info').ShowInfo(const.typeCertificate, abstractinfo=abstractinfo)



    def ApplyForCert(self, certID, *args):
        sm.StartService('certificates').GrantCertificate(certID)



    def DoubleFrame(self, container, weigth, height, width, color = (1.0, 1.0, 1.0, 0.25)):
        color1 = (color[0],
         color[1],
         color[2],
         0.75)
        frameContainer = uicls.Container(name='frameContainer', align=uiconst.TOALL, parent=container)
        topLine = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=weigth, left=0, top=0, width=width - weigth, color=color1)
        leftLine = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=height - 2 * weigth, left=0, top=weigth, width=weigth, color=color1)
        bottomLine = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=weigth, left=weigth, top=height - 2 * weigth, width=width - 2 * weigth, color=color1)
        rightLine = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=height - 3 * weigth, left=width - 2 * weigth, top=weigth, width=weigth, color=color1)
        color2 = (0.0, 0.0, 0.0, 0.75)
        topLine2 = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=weigth, left=weigth, top=weigth, width=width - 3 * weigth, color=color2)
        leftLine2 = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=height - 4 * weigth, left=weigth, top=2 * weigth, width=weigth, color=color2)
        bottomLine2 = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=weigth, left=weigth, top=height - weigth, width=width - weigth, color=color2)
        rightLine2 = uicls.Line(parent=frameContainer, align=uiconst.RELATIVE, height=height - weigth, left=width - weigth, top=weigth, width=weigth, color=color2)




class PermissionEntry(listentry.Generic):
    __guid__ = 'listentry.PermissionEntry'
    __params__ = ['label', 'itemID']

    def ApplyAttributes(self, attributes):
        listentry.Generic.ApplyAttributes(self, attributes)
        self.columns = [0, 1, 2]



    def Startup(self, *args):
        listentry.Generic.Startup(self)
        self.sr.checkBoxes = {}
        i = 220
        for column in self.columns:
            cbox = uicls.Checkbox(text='', parent=self, configName='', retval=column, callback=self.VisibilityFlagsChange, align=uiconst.TOPLEFT, pos=(i + 7,
             1,
             16,
             0))
            self.sr.checkBoxes[column] = cbox
            i += 30

        self.sr.label.top = 0
        self.sr.label.left = 6
        self.sr.label.SetAlign(uiconst.CENTERLEFT)
        self.flag = 0



    def Load(self, node):
        listentry.Generic.Load(self, node)
        data = self.sr.node
        self.flag = data.visibilityFlags
        if data.Get('tempFlag', None) is not None:
            self.flag = data.tempFlag
        for (cboxID, cbox,) in self.sr.checkBoxes.iteritems():
            cbox.state = uiconst.UI_NORMAL
            cbox.SetGroup(data.itemID)
            cbox.data.update({'key': data.itemID})
            if self.flag == cboxID:
                cbox.SetChecked(1, 0)
            else:
                cbox.SetChecked(0, 0)

        if self.sr.node.scroll.sr.tabs:
            self.OnColumnChanged()



    def OnColumnChanged(self, *args):
        tabs = self.sr.node.scroll.sr.tabs
        for (i, key,) in enumerate(self.columns):
            width = tabs[(i + 1)] - tabs[i]
            self.sr.checkBoxes[key].left = self.sr.node.scroll.sr.tabs[i] + width / 2 - 8




    def GetHeight(self, *args):
        (node, width,) = args
        node.height = max(19, uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4)
        return node.height



    def VisibilityFlagsChange(self, checkbox):
        self.flag = checkbox.data['value']



    def HasChanged(self):
        return self.flag != self.sr.node.visibilityFlags




class CertificatePermissionsEntry(PermissionEntry):
    __guid__ = 'listentry.CertificatePermissions'
    __params__ = ['label', 'itemID']

    def ApplyAttributes(self, attributes):
        listentry.PermissionEntry.ApplyAttributes(self, attributes)
        self.columns = [0, 1]



    def Startup(self, *args):
        listentry.PermissionEntry.Startup(self)



    def Load(self, node):
        listentry.PermissionEntry.Load(self, node)



    def VisibilityFlagsChange(self, checkbox, *args):
        listentry.PermissionEntry.VisibilityFlagsChange(self, checkbox)
        func = self.sr.node.Get('func', None)
        if func:
            apply(func, (self.sr.node.itemID, self.flag, self.sr.node.visibilityFlags))




class ShipGroups(listentry.Generic):
    __guid__ = 'listentry.ShipGroups'

    def Load(self, data):
        listentry.Generic.Load(self, data)
        self.sr.label.left = -4
        self.sr.hilite = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.0))



    def OnDblClick(self, *args):
        pass




