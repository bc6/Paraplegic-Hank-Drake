import xtriui
import uix
import uiutil
import hashlib
import form
import listentry
import draw
import uiconst
import uicls

class EditBookmarks(uicls.Window):
    __guid__ = 'form.EditBookmarks'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        name = attributes.bookmarkName
        url = attributes.url
        self.SetWndIcon()
        self.MakeUnpinable()
        self.SetTopparentHeight(0)
        self.SetCaption(mls.UI_GENERIC_BROWSERBOOKMARKSHEADER)
        self.DefineButtons(uiconst.OKCLOSE, okLabel=mls.UI_CMD_REMOVE, okFunc=self.Remove, okModalResult=uiconst.ID_NONE)
        self.SetMinSize((256, 256))
        main = self.sr.main
        main.clipChildren = 0
        uicls.Container(name='errorParent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=16, state=uiconst.UI_HIDDEN)
        toppar = uicls.Container(name='toppar', align=uiconst.TOTOP, height=66, parent=main, idx=0, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        for (name_, top,) in [('name', 50), ('url', 70)]:
            c = uicls.Container(name=name_ + 'cont', parent=toppar, align=uiconst.TOTOP, height=18, padBottom=5)
            uicls.Label(text=getattr(mls, 'UI_GENERIC_' + name_.upper()), fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, parent=c, width=40, top=2, left=4)
            edit = uicls.SinglelineEdit(name=name_ + 'Edit', parent=c, align=uiconst.TOALL, pos=(35, 0, 0, 0))
            edit.OnReturn = self.OnEnter
            self.sr.Set(name_ + 'Edit', edit)

        b = uicls.Button(parent=toppar, label=mls.UI_CMD_ADD, func=self.OnEnter, align=uiconst.BOTTOMRIGHT)
        edit = uicls.Button(parent=toppar, label=mls.UI_CMD_EDIT, pos=(b.width + const.defaultPadding,
         0,
         0,
         0), func=self.OnEdit, align=uiconst.BOTTOMRIGHT)
        edit.state = uiconst.UI_HIDDEN
        self.sr.Set('editBtn', edit)
        name = uiutil.StripTags(name).strip()
        if name:
            self.sr.nameEdit.SetValue(name)
        if url:
            self.sr.urlEdit.SetValue(url)
        self.scroll = uicls.Scroll(parent=main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        sm.GetService('sites')
        self.RefreshSites()



    def Confirm(self, *etc):
        pass



    def Remove(self, *etc):
        selected = self.scroll.GetSelected()
        if not len(selected):
            self.Error(mls.UI_SHARED_PLEASESELECTSITE)
            return 
        self.Error('')
        for entry in selected:
            sm.GetService('sites').RemoveBookmark(entry.retval)

        self.RefreshSites()



    def Error(self, error):
        eve.Message('error')
        ep = uiutil.GetChild(self, 'errorParent')
        uix.Flush(ep)
        if error:
            t = uicls.Label(text='<center>' + error, parent=ep, left=8, top=6, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 1.0))
            ep.state = uiconst.UI_DISABLED
            ep.height = t.height + t.top * 2
        else:
            ep.state = uiconst.UI_HIDDEN



    def OnEntryClick(self, node):
        kv = node.sr.node.retval
        self.sr.nameEdit.SetValue(kv.name)
        self.sr.urlEdit.SetValue(kv.url)
        self.sr.oldEntry = kv
        self.sr.editBtn.state = uiconst.UI_NORMAL
        self.Error(None)



    def OnEdit(self, node, *args):
        if self.CheckEdit():
            sm.GetService('sites').EditBookmark(self.sr.oldEntry, self.sr.nameEdit.GetValue().strip(), self.sr.urlEdit.GetValue().strip())
            self.sr.oldName = self.sr.nameEdit.GetValue().strip()
            self.sr.oldUrl = self.sr.urlEdit.GetValue().strip()
            self.RefreshSites()



    def OnEnter(self, *etc):
        if self.destroyed:
            return 
        if self.CheckEdit():
            sm.GetService('sites').AddBookmark(self.sr.nameEdit.GetValue().strip(), self.sr.urlEdit.GetValue().strip())
            self.RefreshSites()



    def CheckEdit(self):
        nameValue = self.sr.nameEdit.GetValue()
        urlValue = self.sr.urlEdit.GetValue()
        if not nameValue.strip():
            self.Error(mls.UI_SHARED_PLEASECHOOSENAME)
            return False
        if not urlValue.strip():
            self.Error(mls.UI_SHARED_PLEASEENTERURL)
            return False
        self.Error(None)
        return True



    def RefreshSites(self):
        self.selected = None
        scrolllist = []
        for bookmark in sm.GetService('sites').GetBookmarks():
            if bookmark is not None:
                label = '%s<t>%s' % (bookmark.name, bookmark.url)
                scrolllist.append(listentry.Get('Generic', {'label': label,
                 'retval': bookmark,
                 'OnClick': self.OnEntryClick}))

        self.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_LABEL, mls.UI_GENERIC_URL], noContentHint=mls.UI_GENERIC_NOITEMSFOUND)



exports = {'form.EditBookmarks': EditBookmarks}

