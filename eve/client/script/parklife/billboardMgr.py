from service import *
import uthread
import blue
import base
import uix
import urllib2
import string
import sys
import util
import nodemanager
import random
import trinity
import uiutil
import uiconst
import uicls
from timerstuff import ClockThis
TQ_NEWS_HEADLINES_URL = 'http://www.eveonline.com/mb/news-headlines.asp'
SERENITY_NEWS_HEADLINES_URL = 'http://eve.gtgame.com.cn/gamenews/indexhl.htm'
UPDATE_TIME = 30000

class BillboardMgr(Service):
    __guid__ = 'svc.billboard'
    __exportedcalls__ = {'Update': [],
     'GenerateAdvert': []}
    __dependencies__ = ['michelle', 'photo', 'patch']

    def __init__(self):
        Service.__init__(self)
        self.updateTimer = None



    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.updateCount = 0
        self.DoNewsHeadlines()
        self.advertPath = self.GenerateAdvert()
        self.facePath = None
        self.bountyInfo = sm.RemoteSvc('charMgr').GetTopBounties()
        Service.Run(self, memStream)
        self.state = SERVICE_RUNNING



    def GetLocalBillboards(self):
        bp = self.michelle.GetBallpark()
        billboards = []
        if bp is not None:
            for ballID in bp.balls.iterkeys():
                slimItem = bp.GetInvItem(ballID)
                if slimItem == None:
                    continue
                groupID = slimItem.groupID
                if groupID == const.groupBillboard:
                    billboardBall = bp.GetBall(ballID)
                    if billboardBall is not None:
                        billboards.append(billboardBall)

        return billboards



    def GenerateAdvert(self):
        URL = 'http://www.eveonline.com/billboard.asp?%s' % self.patch.GetWebRequestParameters()
        pictureName = URL
        (tex, tWidth, tHeight,) = self.photo.GetTextureFromURL(pictureName)
        codefile = blue.os.CreateInstance('blue.ResFile')
        try:
            if not codefile.Open(tex.resPath):
                self.LogWarn('Cannot open texture file', tex.resPath, '- aborting refresh')
                return None
            modified = codefile.GetFileInfo()['ftLastWriteTime']
        except:
            self.LogWarn('Unable to open texture file', tex.resPath, '- skipping refresh for now')
            sys.exc_clear()
            return None
        if 'none.dds' in tex.resPath:
            return None
        else:
            return tex.resPath



    def DoNewsHeadlines(self):
        newsHeadlinesURL = TQ_NEWS_HEADLINES_URL
        if boot.region == 'optic':
            newsHeadlinesURL = SERENITY_NEWS_HEADLINES_URL
        newsHeadlinesURL += '?%s' % self.patch.GetWebRequestParameters()
        try:
            f = urllib2.urlopen(newsHeadlinesURL)
        except:
            f = None
            self.LogError('Failed to get news headlines from:', newsHeadlinesURL)
            sys.exc_clear()
            return 
        txt = f.read()
        lines = string.split(txt, '\r\n')
        headlines = []
        for each in lines:
            c = string.split(each, ';', 1)
            if len(c) > 1:
                (date, caption,) = c
                headlines.append(caption)

        totaltext = ' '
        for caption in headlines:
            if (len(totaltext) + len(caption) + 3) * 8 > 2048:
                break
            totaltext = totaltext + ' - ' + caption

        self.RenderText(totaltext, 'headlines')



    def Update(self, model = None):
        self._BillboardMgr__UpdateBillboard(model)



    def __UpdateBillboard(self, model):
        if not hasattr(eve.session, 'solarsystemid') or eve.session.solarsystemid is None or model is None:
            return 
        self.LogInfo('Updating billboard')
        if self.updateCount % 10 == 0:
            self.UpdateBounty()
        self.updateCount += 1
        model.UpdateBillboardContents(self.advertPath, self.facePath)



    def UpdateBounty(self):
        self.LogInfo('Updating bounty')
        currBounty = None
        if len(self.bountyInfo):
            m = self.bountyInfo[random.randint(0, len(self.bountyInfo) - 1)]
            currBounty = [m.characterID,
             m.ownerName,
             m.bounty,
             m.online]
        self.facePath = None
        if currBounty is not None:
            (characterID, charName, bounty, online,) = currBounty
            serverLink = sm.RemoteSvc('charMgr').GetImageServerLink()
            if not serverLink:
                self.LogWarn("UpdateBounty: Couldn't find server Link")
                self.facePath = 'res:/UI/Texture/defaultFace.jpg'
                portraitURL = '<serverlink not found>'
                width = 256
                height = 32
            else:
                portraitURL = '%sCharacter/%d_256.jpg' % (serverLink, characterID)
                tex = self.photo.GetTextureFromURL(portraitURL, None)
                texture = tex[0]
                if 'none.dds' in texture.resPath:
                    self.facePath = None
                    self.LogError('Failed opening jpg picture for character', characterID)
                else:
                    self.facePath = texture.resPath
                    width = 256
                    height = 32
            nameText = '%s: <b>%s</b>' % (uiutil.UpperCase(mls.UI_GENERIC_WANTED), charName)
            amountText = util.FmtISK(bounty, showFractionsAlways=0) + ' ' + mls.UI_INFLIGHT_UPONTERMINATION
            extraText = mls.UI_INFLIGHT_WANTEDFORCRIMES
            totaltext = ' <color=0xffdd4444>%s</color> - %s - %s - ' % (nameText, amountText, extraText)
            self.RenderText(totaltext, 'bounty_caption')
            self.LogInfo('Updating billboard with bounty portrait', portraitURL, 'for character', charName, ', ID= ', characterID)



    def RenderText(self, text, name):
        txt = uicls.Label(text=text, parent=None, uppercase=1, letterspace=1, shadow=[], state=uiconst.UI_NORMAL)
        txt.Render()
        surface = trinity.device.CreateOffscreenPlainSurface(txt.width, txt.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        txt.texture.atlasTexture.CopyToSurface(surface)
        surface.SaveSurfaceToFile('%sTemp/%s.dds' % (blue.os.cachepath, name), trinity.TRIIFF_DDS)




