import service
import uiutil
import blue
import trinity
import sys
import util
import spaceObject
import string
import xtriui
import svc
import uthread
import uicls
import uiconst
import corebrowserutil
import time
import urllib2
import os
import datetime
import log
import turret
import shutil
from pychartdir import DrawArea, Transparent
from util import ResFile
from collections import defaultdict
MAX_PORTRAIT_THREADS = 5
MAX_CACHE_AGE = 60 * 60 * 24
DEFAULT_PORTRAIT_SIZE = 512
DEFAULT_PORTRAIT_SAVE_SIZE = 1024
PORTRAIT_SIZES = [32,
 64,
 128,
 256,
 512]
BLUEPRINT_RESPATH = 'res:/UI/Texture/Icons/BPO.png'
BLUEPRINT_COPY_RESPATH = 'res:/UI/Texture/Icons/BPC.png'
BLUEPRINT_COLOR = (0.275, 0.615, 1.0)
BLUEPRINT_COPY_COLOR = (BLUEPRINT_COLOR[0] * 1.93, BLUEPRINT_COLOR[1] * 1.39, BLUEPRINT_COLOR[2] * 0.965)
BLUEPRINT_TRANSPARENT_COLOR = (0.679,
 0.848,
 0.902,
 0.0)
BLUEPRINT_TRANSPARENT_COLOR_INT = 11393254
DEFAULT_MARKETING_TEST_IMAGE_SERVER = 'http://cdn1.eveonline.com/marketing/InGameVirtualGoodsStore/TestServersImages/'

def DoLogIt(path):
    if not util.IsFullLogging() and 'portrait' in path.lower():
        return False
    return True



class EvePhoto(svc.photo):
    __guid__ = 'svc.evePhoto'
    __replaceservice__ = 'photo'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetPortrait': [],
     'AddPortrait': [],
     'GetAllianceLogo': [],
     'OrderByTypeID': [],
     'GetPhoto': [],
     'CheckAvail': [],
     'TargetAndStencilAndViewport': [],
     'GetPlanetPhoto': [],
     'GetSunPhoto': [],
     'RenderFromScene': [],
     'GetTextureFromURL': [],
     'CheckDates': [],
     'GetScenePicture': [],
     'GetPictureFileName': [],
     'SavePortraits': [],
     'GetStorebanner': []}
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.notavail = {}
        self.imageServerQueue = defaultdict(list)
        self.currentlyFetching = defaultdict(list)
        self.fetchingFromImageServer = 0
        self.portraitregistrations = {}
        self.byTypeIDQue = []
        self.byTypeID_IsRunning = 0
        self.types = {}
        self.gidque = []
        self.gidrunning = 0
        self.gidcount = 0
        self.faceoptions = {}
        self.chappcache = None
        self.photoscene = None
        self.CheckDates(blue.os.cachepath + '/Browser/Img')
        self.CheckDates(blue.os.cachepath + '/Pictures/Portraits')
        self.CheckDates(blue.os.cachepath + '/Pictures/Gids')
        self.urlloading = {}
        self.pendingPI = {}
        self.portraits = None
        self.allianceLogos = None
        self.storeBannerImages = None
        self.pendingPortraitGeneration = set()
        self.defaultImageServerForUser = None
        self.defaultMarketingImages = None
        if not blue.pyos.packaged:
            username = os.environ.get('USERNAME')
            if username is None:
                username = os.environ.get('USER')
            if username is not None:
                self.defaultImageServerForUser = 'http://%s.dev.image/' % username.replace('.', '_').lower()
                self.LogInfo('Guessing ImageServer url as we are not in a build client: ', self.defaultImageServerForUser)
                self.defaultMarketingImages = DEFAULT_MARKETING_TEST_IMAGE_SERVER



    def GetPictureFileName(self, typeinfo, size):
        shaderModel = trinity.GetShaderModel()
        name = '%s_%s_%s_%s_%s.dds' % (shaderModel,
         typeinfo.graphicID or 0,
         typeinfo.iconID or 0,
         typeinfo.raceID or 0,
         size)
        return name



    def CheckAvail(self, path):
        pathLog = path if DoLogIt(path) else ''
        self.LogInfo('CheckAvail ', pathLog)
        if path in self.notavail:
            self.LogInfo('CheckAvail ', pathLog, ' is in notavail')
            return 
        file = blue.ResFile()
        try:
            if file.Open(path):
                self.LogInfo('CheckAvail ', pathLog, ' exists')
                return path
            else:
                self.LogInfo('CheckAvail ', pathLog, " doesn't exist, and has been added to notavail")
                self.notavail[path] = 1
                return 

        finally:
            del file




    def GetValidBlueprintPath(self, sprite, typeID, size = 64, renderedIcon = False, isCopy = False):
        typeinfo = cfg.invtypes.Get(typeID)
        path = self.GetCachePath(typeinfo, size, None, True, isCopy)
        cachePath = 'cache:/%s' % path
        resFile = blue.ResFile()
        try:
            if resFile.Open(blue.os.cachepath + path):
                self.LogInfo('DoBlueprint ', blue.os.cachepath + path, ' exists')
                return cachePath

        finally:
            del resFile

        rot = blue.os.CreateInstance('blue.Rot')
        dev = trinity.device
        texture = sprite.texture.resPath
        surfaceSize = size if renderedIcon else 256
        iconSurface = dev.CreateOffscreenPlainSurface(surfaceSize, surfaceSize, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        iconSurface.LoadSurfaceFromFile(ResFile(texture))
        iconSurface.LockBuffer()
        bpsurface = dev.CreateOffscreenPlainSurface(size, size, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        bpTemplatePath = BLUEPRINT_COPY_RESPATH if isCopy else BLUEPRINT_RESPATH
        bpsurface.LoadSurfaceFromFile(ResFile(bpTemplatePath))
        bpsurface.LockBuffer()
        tmpCol = trinity.TriColor()
        bpCol = trinity.TriColor()
        scale = float(surfaceSize) / size
        for x in xrange(size):
            for y in xrange(size):
                px = sprite.rectLeft + int(x * scale)
                py = sprite.rectTop + int(y * scale)
                intSheetColor = iconSurface.GetPixel(px, py)
                if renderedIcon:
                    if intSheetColor == BLUEPRINT_TRANSPARENT_COLOR_INT:
                        intSheetColor = 0
                        tmpCol.FromInt(0)
                    else:
                        tmpCol.FromInt(intSheetColor)
                        tmpCol.a = 1.0
                else:
                    tmpCol.FromInt(intSheetColor)
                intBpColor = bpsurface.GetPixel(x, y)
                bpCol.FromInt(intBpColor)
                a = tmpCol.a
                endAlpha = bpCol.a
                tmpCol.r *= 0.5
                tmpCol.g *= 0.7
                a *= 0.75
                tmpCol.Scale(a)
                bpCol.Scale(1.0 - a)
                tmpCol.r = min(1.0, bpCol.r + tmpCol.r)
                tmpCol.g = min(1.0, bpCol.g + tmpCol.g)
                tmpCol.b = min(1.0, bpCol.b + tmpCol.b)
                tmpCol.a = 1.0
                bpsurface.SetPixel(x, y, tmpCol.AsInt())


        iconSurface.FlushBuffer()
        bpsurface.FlushBuffer()
        self._SaveSurfaceToFile(bpsurface, path)
        return cachePath



    def DoBlueprint(self, sprite, typeID, size = 64, renderedIcon = False, isCopy = False):
        texture = sprite.texture.resPath
        bpPath = self.GetValidBlueprintPath(sprite, typeID, size, renderedIcon, isCopy)
        if sprite.texture.resPath == texture:
            sprite.texture.resPath = bpPath
            sprite.rectLeft = 0
            sprite.rectWidth = 0
            sprite.rectTop = 0
            sprite.rectHeight = 0



    def FindNode(self, source, name, typename):
        tr = source.Find(typename)
        for t in tr:
            if t.name[:len(name)] == name:
                return t




    def GetScenePicture(self, res = 128, blur = 0):
        scene = sm.GetService('sceneManager').GetRegisteredScene2(None, defaultOnActiveScene=True)
        camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
        depthTexture = scene.depthTexture
        scene.depthTexture = None
        backbuffer = trinity.device.GetPresentParameters()['BackBufferFormat']
        sampletype = trinity.device.GetPresentParameters()['MultiSampleType']
        samplelevel = trinity.device.GetPresentParameters()['MultiSampleQuality']
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        dev = trinity.device
        sur = dev.CreateOffscreenPlainSurface(res, res, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        target = trinity.TriSurfaceManaged(dev.CreateRenderTarget, res, res, trinity.TRIFMT_A8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 0)
        stencil = trinity.TriSurfaceManaged(dev.CreateDepthStencilSurface, res, res, trinity.TRIFMT_D16, trinity.TRIMULTISAMPLE_NONE, 0, 0)
        viewport = trinity.TriViewport(0, 0, res, res, 0.0, 1.0)
        view = trinity.TriView()
        view.transform = ((camera.view._11,
          camera.view._12,
          camera.view._13,
          camera.view._14),
         (camera.view._21,
          camera.view._22,
          camera.view._23,
          camera.view._24),
         (camera.view._31,
          camera.view._32,
          camera.view._33,
          camera.view._34),
         (camera.view._41,
          camera.view._42,
          camera.view._43,
          camera.view._44))
        projection = camera.triProjection
        renderJob = trinity.CreateRenderJob('StaticScene')
        renderJob.SetRenderTarget(target)
        renderJob.SetProjection(projection)
        renderJob.SetView(view)
        renderJob.SetDepthStencil(stencil)
        renderJob.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        renderJob.RenderScene(scene)
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        scene.depthTexture = depthTexture
        dev.GetRenderTargetData(target, sur)
        if blur:
            gaussBlur = trinity.TriConvolutionMatrix5(2.0, 3.0, 5.0, 3.0, 2.0, 3.0, 4.0, 8.0, 5.0, 3.0, 5.0, 7.0, 13.0, 7.0, 5.0, 3.0, 4.0, 8.0, 5.0, 3.0, 2.0, 3.0, 5.0, 3.0, 2.0)
            sur2 = dev.CreateOffscreenPlainSurface(res, res, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
            sur2.ApplyConvFilter(sur, gaussBlur, 0)
            sur = sur2
        pic = uicls.Sprite(align=uiconst.TOALL)
        pic.texture.atlasTexture = uicore.uilib.CreateTexture(sur.width, sur.height)
        pic.texture.atlasTexture.CopyFromSurface(sur)
        return pic



    def GetTextureFromURL(self, path, currentURL = None, ignoreCache = 0, dontcache = 0, fromWhere = None, sizeonly = 0, retry = 1):
        if path.endswith('.blue'):
            return self.GetPic_blue(path)
        dev = trinity.device
        fullPath = corebrowserutil.ParseURL(path, currentURL)[0]
        if path.startswith('res:'):
            try:
                surface = dev.CreateOffscreenPlainSurface(8, 8, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
                data = surface.LoadSurfaceFromFile(ResFile(path))
                (w, h,) = (data['Width'], data['Height'])
                (bw, bh,) = (uiutil.GetBuffersize(w), uiutil.GetBuffersize(h))
                if sizeonly:
                    return (path,
                     w,
                     h,
                     bw,
                     bh)
                else:
                    return self.ReturnTexture(path, w, h, bw, bh)
            except:
                self.LogError('Failed to load image', path)
                if self.urlloading.has_key(fullPath):
                    del self.urlloading[fullPath]
                sys.exc_clear()
                return self.ErrorPic(sizeonly)
        if ignoreCache:
            sm.GetService('browserCache').InvalidateImage(fullPath)
        while self.urlloading.has_key(fullPath):
            blue.pyos.BeNice()

        if not dontcache:
            cacheData = sm.GetService('browserCache').GetFromCache(fullPath)
            if cacheData and os.path.exists(cacheData[0].replace('cache:/', blue.os.cachepath)):
                if sizeonly:
                    return cacheData
                return self.ReturnTexture(*cacheData)
        try:
            self.urlloading[fullPath] = 1
            ret = corebrowserutil.GetStringFromURL(fullPath)
            cacheID = int(str(blue.os.GetTime()) + str(uthread.uniqueId() or uthread.uniqueId()))
            imagestream = ret.read()
            ext = None
            if 'content-type' in ret.headers.keys() and ret.headers['content-type'].startswith('image/'):
                ext = ret.headers['content-type'][6:]
            if ext == None or ext == 'png':
                header = imagestream[:16]
                for (sig, sext,) in [('PNG', 'PNG'),
                 ('GIF', 'GIF'),
                 ('JFI', 'JPEG'),
                 ('BM8', 'BMP')]:
                    for i in xrange(0, 12):
                        if header[i:(i + 3)] == sig:
                            ext = sext
                            break


                if not ext:
                    header = imagestream[-16:]
                    for (sig, sext,) in [('XFILE', 'TGA')]:
                        for i in xrange(0, 10):
                            if header[i:(i + 5)] == sig:
                                ext = sext
                                break


            if ext:
                filename = '%sBrowser/Img/%s.%s' % (blue.os.cachepath, cacheID, ext)
                resfile = blue.os.CreateInstance('blue.ResFile')
                if not resfile.Open(filename, 0):
                    resfile.Create(filename)
                resfile.Write(imagestream)
                resfile.Close()
                if ext.upper() == 'GIF':
                    g = DrawArea()
                    g.setBgColor(Transparent)
                    g.loadGIF(filename.replace(u'/', u'\\').encode('utf8'))
                    ext = 'PNG'
                    filename = u'%sBrowser/Img/%s.%s' % (blue.os.cachepath, cacheID, ext)
                    g.outPNG(filename.replace(u'/', u'\\').encode('utf8'))
                surface = dev.CreateOffscreenPlainSurface(8, 8, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
                data = surface.LoadSurfaceFromFile(ResFile(filename))
                (w, h,) = (data['Width'], data['Height'])
                (bw, bh,) = (uiutil.GetBuffersize(w), uiutil.GetBuffersize(h))
                cachePath = 'cache:/Browser/Img/%s.%s' % (cacheID, ext)
                if 'pragma' not in ret.headers.keys() or ret.headers['Pragma'].find('no-cache') == -1:
                    sm.GetService('browserCache').Cache(fullPath, (cachePath,
                     w,
                     h,
                     bw,
                     bh))
                del self.urlloading[fullPath]
                if sizeonly:
                    return (cachePath,
                     w,
                     h,
                     bw,
                     bh)
                return self.ReturnTexture(cachePath, w, h, bw, bh)
            else:
                del self.urlloading[fullPath]
                return self.ErrorPic(sizeonly)
        except Exception as e:
            if retry:
                sys.exc_clear()
                if self.urlloading.has_key(fullPath):
                    del self.urlloading[fullPath]
                return self.GetTextureFromURL(path, currentURL, ignoreCache, dontcache, fromWhere, sizeonly, 0)
            self.LogError(e, 'Failed to load image', repr(path))
            if self.urlloading.has_key(fullPath):
                del self.urlloading[fullPath]
            sys.exc_clear()
            return self.ErrorPic(sizeonly)



    def ErrorPic(self, sizeonly = 0):
        if sizeonly:
            return ('res:/UI/Texture/none.dds', 32, 32, 32, 32)
        tex = trinity.Tr2Sprite2dTexture()
        tex.resPath = 'res:/UI/Texture/none.dds'
        return (tex, 32, 32)



    def CleanExt(self, ext):
        validNot3Letters = ('jpeg',)
        for _ext in validNot3Letters:
            if ext.lower().startswith(_ext):
                return _ext

        return ext[:3]



    def ReturnTexture(self, path, width, height, bufferwidth, bufferheight):
        tex = trinity.Tr2Sprite2dTexture()
        tex.resPath = path
        return (tex, width, height)



    def CheckDates(self, path):
        now = long(time.time())
        rem = []
        for fileName in os.listdir(path):
            if fileName.split('.')[-1] in ('blue', 'dat', 'txt'):
                continue
            lastRead = os.path.getatime(path + '/' + fileName)
            age = now - lastRead
            if age / 2592000:
                rem.append(fileName)

        for each in rem:
            os.remove(path + '/' + each)




    def InitializePortraits(self):
        if self.portraits is None:
            imageServer = self.GetImageServerURL('imageserverurl', self.defaultImageServerForUser)
            self.portraits = RemoteImageCacher('Character', self, '.jpg', imageServer)
            self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
            for charID in self.pendingPortraitGeneration:
                self.LogInfo('Character', charID, 'is marked as newly customized.')
                self.portraits.AddToWatchList(charID, self.PortraitDownloaded)
                for size in PORTRAIT_SIZES:
                    if size == DEFAULT_PORTRAIT_SIZE:
                        continue
                    self.portraits.RemoveFromCache(charID, size)





    def PortraitDownloaded(self, charID):
        self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
        if charID in self.pendingPortraitGeneration:
            self.pendingPortraitGeneration.discard(charID)
            settings.user.ui.Set('pendingPortraitGeneration', self.pendingPortraitGeneration)



    def GetPortrait(self, charID, size, sprite = None, orderIfMissing = True, callback = False):
        self.InitializePortraits()
        if size > 64:
            defaultIcon = 'res:/UI/Texture/silhouette.png'
        else:
            defaultIcon = 'res:/UI/Texture/silhouette_64.png'
        if charID in self.pendingPortraitGeneration:
            size = DEFAULT_PORTRAIT_SIZE
        callback = 'OnPortraitCreated' if callback else None
        return self.GetImage(charID, size, self.portraits, sprite, orderIfMissing, callback, defaultIcon)



    def SavePortraits(self, charIDs):
        if type(charIDs) != list:
            charIDs = [charIDs]
        uthread.new(self._SavePortraits, charIDs)



    def GetPortraitSaveSize(self):
        portraitSize = sm.GetService('machoNet').GetClientConfigVals().get('defaultPortraitSaveSize')
        if portraitSize is None:
            portraitSize = DEFAULT_PORTRAIT_SAVE_SIZE
        self.LogInfo('Portrait will be saved at', portraitSize)
        return int(portraitSize)



    def _SavePortraits(self, charIDs):
        length = len(charIDs)
        sm.GetService('loading').ProgressWnd(mls.UI_SHARED_GENERATINGPICTURE, '', 0, length)
        portraitSaveSize = self.GetPortraitSaveSize()
        for (i, charID,) in enumerate(charIDs):
            imagePath = self.portraits.GetImage(charID, portraitSaveSize, forceUpdate=True)
            if imagePath:
                cacheFile = blue.rot.PathToFilename(imagePath)
                shutil.copy2(cacheFile, blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '/EVE/capture/Portraits/%s.jpg' % charID)
            sm.GetService('loading').ProgressWnd(mls.UI_SHARED_GENERATINGPICTURE, '', i + 1, length)

        sm.GetService('loading').ProgressWnd(mls.UI_SHARED_GENERATINGPICTURE, '', length, length)



    def GetAllianceLogo(self, allianceID, size, sprite = None, orderIfMissing = True, callback = False):
        if self.allianceLogos is None:
            imageServer = self.GetImageServerURL('imageserverurl', self.defaultImageServerForUser)
            self.allianceLogos = RemoteImageCacher('Alliance', self, '.png', imageServer)
        callback = 'OnAllianceLogoReady' if callback else None
        return self.GetImage(allianceID, size, self.allianceLogos, sprite, orderIfMissing, callback, 'res:/UI/Texture/defaultAlliance.dds')



    def GetImage(self, itemID, size, handler, sprite = None, orderIfMissing = True, callback = None, defaultIcon = 'res:/UI/Texture/notavailable.dds'):
        (path, isFresh,) = handler.GetCachedImage(itemID, size)
        if sprite is not None:
            sprite.LoadTexture(path or defaultIcon)
        if not isFresh and orderIfMissing and not handler.MissingFromServer(itemID):
            if (itemID, size, handler) in self.currentlyFetching:
                self.currentlyFetching[(itemID, size, handler)].append([sprite, callback])
            else:
                self.imageServerQueue[(itemID, size, handler)].append([sprite, callback])
            if len(self.imageServerQueue) > self.fetchingFromImageServer and self.fetchingFromImageServer < MAX_PORTRAIT_THREADS:
                self.fetchingFromImageServer += 1
                uthread.pool('photo::FetchRemoteImages', self._EvePhoto__FetchFromImageServer)
        if isFresh:
            return path



    def __FetchFromImageServer(self):
        self.LogInfo('Starting a image server thread')
        try:
            while len(self.imageServerQueue) > 0:
                ((itemID, size, handler,), orders,) = self.imageServerQueue.popitem()
                image = handler.GetImage(itemID, size)
                self.currentlyFetching[(itemID, size, handler)] = []
                if image is None:
                    continue
                orders += self.currentlyFetching.pop((itemID, size, handler))
                for (sprite, callback,) in orders:
                    if callback:
                        sm.ScatterEvent(callback, itemID)
                    else:
                        try:
                            sprite.LoadTexture(image)
                        except:
                            log.LogException('Error adding portrait to sprite')
                            sys.exc_clear()



        finally:
            self.fetchingFromImageServer -= 1




    def AddPortrait(self, portraitPath, charID):
        self.LogInfo('Adding portrait of', charID, 'from path', portraitPath)
        shutil.copy2(portraitPath, blue.os.cachepath + '/Pictures/Characters/%s_%s.jpg' % (charID, DEFAULT_PORTRAIT_SIZE))
        shutil.copy2(portraitPath, blue.os.cachepath + '/Pictures/Characters/%s_%s.jpg' % (charID, 256))
        portraitCachePath = 'cache:/Pictures/Characters/%s_%s.jpg' % (charID, DEFAULT_PORTRAIT_SIZE)
        res = blue.resMan.GetResource(portraitCachePath, 'atlas')
        res.Reload()
        portraitCachePath_256 = 'cache:/Pictures/Characters/%s_%s.jpg' % (charID, 256)
        res = blue.resMan.GetResource(portraitCachePath_256, 'atlas')
        res.Reload()
        self.pendingPortraitGeneration = settings.user.ui.Get('pendingPortraitGeneration', set())
        self.pendingPortraitGeneration.add(charID)
        settings.user.ui.Set('pendingPortraitGeneration', self.pendingPortraitGeneration)
        if self.portraits is not None:
            self.portraits.missingImages.pop(charID, None)
            self.portraits.AddToWatchList(charID, self.PortraitDownloaded)



    def _SaveSurfaceToFile(self, surface, outputPath, format = trinity.TRIIFF_DDS):
        cachename = svc.photo._SaveSurfaceToFile(self, surface, outputPath, format)
        try:
            del self.notavail[cachename]
            self.LogInfo('Deleted ', cachename, ' from not avail list')
        except:
            self.LogInfo(cachename, ' was not in the not avail list')
            sys.exc_clear()
        return cachename



    def TargetAndStencilAndViewport(self, size, format = trinity.TRIFMT_A8R8G8B8):
        name = '_cachedTSV%s' % size
        r = getattr(self, name, None)
        if r:
            return r
        dev = trinity.device
        viewport = trinity.TriViewport(0, 0, size, size, 0.0, 1.0)
        target = dev.CreateRenderTarget(size, size, format, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        stencil = dev.CreateDepthStencilSurface(size, size, trinity.TRIFMT_D16, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        r = (target, stencil, viewport)
        return r



    def Get2DMap(self, ids, idLevel, drawLevel, size = 256):
        ssmap = xtriui.Map2D()
        imagePath = ssmap.Draw(ids, idLevel, drawLevel, size)
        return imagePath



    def OrderByTypeID(self, orderlist):
        for each in orderlist:
            if len(each) == 4:
                (typeID, wnd, size, itemID,) = each
                doBlueprint = isCopy = False
            else:
                (typeID, wnd, size, itemID, doBlueprint, isCopy,) = each
            if wnd is None or wnd.destroyed:
                orderlist.remove(each)
                continue
            t = cfg.invtypes.Get(typeID)
            path = 'cache:/' + self.GetCachePath(t, size, itemID, doBlueprint, isCopy)
            if self.CheckAvail(path) is not None:
                wnd.LoadTexture(path)
                orderlist.remove(each)
                continue
            wnd.LoadTexture('res:/UI/Texture/notavailable.dds')

        for each in orderlist:
            self.byTypeIDQue.append(each)

        if not self.byTypeID_IsRunning:
            uthread.pool('photo::OrderByTypeID', self.ProduceTypeIDs)
            self.byTypeID_IsRunning = 1



    def GetCachePath(self, typeinfo, size, itemID, doBlueprint, isCopy = False):
        if typeinfo.groupID in [const.groupSun, const.groupPlanet, const.groupMoon]:
            return 'Pictures/Planets/%s_%s_%s.dds' % (trinity.GetShaderModel(), itemID, size)
        else:
            if doBlueprint:
                return 'Pictures/Blueprints/bp%s_%s' % ('c' if isCopy else '', self.GetPictureFileName(typeinfo, size))
            return 'Pictures/Gids/' + self.GetPictureFileName(typeinfo, size)



    def ProduceTypeIDs(self):
        while self.byTypeIDQue:
            for order in self.byTypeIDQue:
                if len(order) == 4:
                    (typeID, wnd, size, itemID,) = order
                    doBlueprint = isCopy = False
                else:
                    (typeID, wnd, size, itemID, doBlueprint, isCopy,) = order
                if wnd is None or wnd.destroyed:
                    self.byTypeIDQue.remove(order)
                    continue
                typeinfo = cfg.invtypes.Get(typeID)
                path = self.GetCachePath(typeinfo, size, itemID, doBlueprint, isCopy)
                if self.CheckAvail(path) is not None:
                    uicls.Icon.LoadIconByTypeID(wnd, path=path, size=size, ignoreSize=True)
                    self.byTypeIDQue.remove(order)
                    continue
                try:
                    group = typeinfo.Group()
                    if group.categoryID == const.categoryPlanetaryInteraction and group.id not in (const.groupPlanetaryLinks, const.groupPlanetaryCustomsOffices):
                        photopath = self.GetPinPhoto(typeID, typeinfo=typeinfo, size=size)
                    elif group.id == const.groupSun:
                        photopath = self.GetSunPhoto(itemID, typeID, typeinfo, size)
                    elif group.id in [const.groupPlanet, const.groupMoon]:
                        photopath = self.GetPlanetPhoto(itemID, typeID, typeinfo, size)
                    else:
                        photopath = self.GetPhoto(typeID, typeinfo=typeinfo, size=size, transparentBackground=doBlueprint, bgColor=BLUEPRINT_TRANSPARENT_COLOR)
                except Exception as e:
                    photopath = 'res:/UI/Texture/notavailable.dds'
                    self.byTypeIDQue.remove(order)
                    log.LogException('ProduceTypeIDs: Error in getPhoto for %s' % typeID)
                    sys.exc_clear()
                    continue
                if wnd is None or wnd.destroyed:
                    self.byTypeIDQue.remove(order)
                    continue
                if wnd.texture and wnd.texture.resPath[-16:] != 'notavailable.dds':
                    self.byTypeIDQue.remove(order)
                    continue
                wnd.LoadTexture(photopath)
                if photopath[-16:] == 'notavailable.dds':
                    self.byTypeIDQue.remove(order)
                    continue
                if doBlueprint:
                    self.DoBlueprint(wnd, typeID, size, True, isCopy)
                self.byTypeIDQue.remove(order)
                blue.pyos.synchro.Yield()


        self.byTypeID_IsRunning = 0



    def ValidateName(self, name):
        if name[:8] == 'locator_':
            return 0
        if name in ('beam1', 'wormhole'):
            return 0
        return 1



    def FindHierarchicalBoundingBox(self, transform, matrix = None):
        transform.Update(blue.os.GetTime())
        if matrix is None:
            matrix = trinity.TriMatrix()
        (minVector, maxVector,) = (None, None)
        if hasattr(transform, 'translation') and transform.__typename__ in ('TriTransform', 'TriSplTransform', 'TriLODGroup'):
            if transform.__typename__ == 'TriTransform':
                if transform.transformBase != trinity.TRITB_OBJECT:
                    return (None, None)
            test = [0,
             0,
             0,
             0]
            test[0] = hasattr(transform, 'pickable') and transform.pickable == 1
            test[1] = getattr(transform, 'object', None) is not None
            test[2] = transform.display == 1
            test[3] = self.ValidateName(transform.name)
            worldTransform = transform.localTransform.CloneTo()
            worldTransform.Multiply(matrix)
            if test[0] and test[1] and test[2] and test[3]:
                corner1 = None
                corner2 = None
                if transform.object.__typename__ in ('TriMesh', 'TriMultiMesh'):
                    corner1 = transform.object.meshBoxMin.CopyTo()
                    corner2 = transform.object.meshBoxMax.CopyTo()
                elif getattr(transform.object, 'vertexRes', None) is not None:
                    v = transform.object.vertexRes
                    corner1 = transform.object.vertexRes.meshBoxMin.CopyTo()
                    corner2 = transform.object.vertexRes.meshBoxMax.CopyTo()
                if corner1 is not None and corner2 is not None:
                    corner3 = trinity.TriVector(corner1.x, corner1.y, corner2.z)
                    corner4 = trinity.TriVector(corner1.x, corner2.y, corner1.z)
                    corner5 = trinity.TriVector(corner2.x, corner1.y, corner1.z)
                    corner6 = trinity.TriVector(corner2.x, corner2.y, corner1.z)
                    corner7 = trinity.TriVector(corner1.x, corner2.y, corner2.z)
                    corner8 = trinity.TriVector(corner2.x, corner1.y, corner2.z)
                    corner1.TransformCoord(worldTransform)
                    corner2.TransformCoord(worldTransform)
                    corner3.TransformCoord(worldTransform)
                    corner4.TransformCoord(worldTransform)
                    corner5.TransformCoord(worldTransform)
                    corner6.TransformCoord(worldTransform)
                    corner7.TransformCoord(worldTransform)
                    corner8.TransformCoord(worldTransform)
                    minx = min(corner1.x, corner2.x, corner3.x, corner4.x, corner5.x, corner6.x, corner7.x, corner8.x)
                    maxx = max(corner1.x, corner2.x, corner3.x, corner4.x, corner5.x, corner6.x, corner7.x, corner8.x)
                    miny = min(corner1.y, corner2.y, corner3.y, corner4.y, corner5.y, corner6.y, corner7.y, corner8.y)
                    maxy = max(corner1.y, corner2.y, corner3.y, corner4.y, corner5.y, corner6.y, corner7.y, corner8.y)
                    minz = min(corner1.z, corner2.z, corner3.z, corner4.z, corner5.z, corner6.z, corner7.z, corner8.z)
                    maxz = max(corner1.z, corner2.z, corner3.z, corner4.z, corner5.z, corner6.z, corner7.z, corner8.z)
                    minVector = (minx, miny, minz)
                    maxVector = (maxx, maxy, maxz)
            if transform.__typename__ == 'TriLODGroup':
                (childMinVector, childMaxVector,) = self.FindHierarchicalBoundingBox(transform.children[0], worldTransform)
                if minVector is None:
                    minVector = childMinVector
                if maxVector is None:
                    maxVector = childMaxVector
                if childMinVector is not None and minVector is not None:
                    minVector = (min(minVector[0], childMinVector[0]), min(minVector[1], childMinVector[1]), min(minVector[2], childMinVector[2]))
                if childMaxVector is not None and maxVector is not None:
                    maxVector = (max(maxVector[0], childMaxVector[0]), max(maxVector[1], childMaxVector[1]), max(maxVector[2], childMaxVector[2]))
            else:
                for child in transform.children:
                    (childMinVector, childMaxVector,) = self.FindHierarchicalBoundingBox(child, worldTransform)
                    if minVector is None:
                        minVector = childMinVector
                    if maxVector is None:
                        maxVector = childMaxVector
                    if childMinVector is not None and minVector is not None:
                        minVector = (min(minVector[0], childMinVector[0]), min(minVector[1], childMinVector[1]), min(minVector[2], childMinVector[2]))
                    if childMaxVector is not None and maxVector is not None:
                        maxVector = (max(maxVector[0], childMaxVector[0]), max(maxVector[1], childMaxVector[1]), max(maxVector[2], childMaxVector[2]))

        return (minVector, maxVector)



    def HasMiniBalls(self, parent):
        found = 0
        if hasattr(parent, 'children'):
            for tf in parent.children[:]:
                if tf.name == 'miniball' and hasattr(tf, 'localTransform'):
                    found += 1

        if not found:
            return False
        else:
            return True



    def MeasureMiniBalls(self, parent, guides = 0):
        minx = 1e+100
        maxx = -1e+100
        miny = 1e+100
        maxy = -1e+100
        minz = 1e+100
        maxz = -1e+100
        found = 0
        if hasattr(parent, 'children'):
            for tf in parent.children[:]:
                if tf.name == 'miniball' and hasattr(tf, 'localTransform'):
                    found += 1
                    tf.Update(blue.os.GetTime())
                    tf.display = guides
                    pos = tf.translation.CopyTo()
                    xtra = tf.scaling.x * 0.5
                    minx = min(minx, pos.x - xtra)
                    maxx = max(maxx, pos.x + xtra)
                    miny = min(miny, pos.y - xtra)
                    maxy = max(maxy, pos.y + xtra)
                    minz = min(minz, pos.z - xtra)
                    maxz = max(maxz, pos.z + xtra)

        if not found:
            minx = miny = minz = maxx = maxy = maxz = 1
        return (minx,
         maxx,
         miny,
         maxy,
         minz,
         maxz)



    def GetPlanetScene(self):
        scenepath = sm.GetService('sceneManager').GetScene()
        scene = trinity.Load(scenepath)
        scene2 = trinity.EveSpaceScene()
        textures = scene.nebula.children[0].object.areas[0].areaTextures
        scene2.envMap1ResPath = textures[0].pixels.encode('ascii')
        if len(textures) > 1:
            scene2.envMap2ResPath = textures[1].pixels.encode('ascii')
        rot1 = textures[0].rotation
        scene2.envMapRotation = (rot1.x,
         rot1.y,
         rot1.z,
         rot1.w)
        scale1 = textures[0].scaling
        scene2.envMapScaling = (scale1.x, scale1.y, scale1.z)
        scene2.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        if scene2.backgroundEffect is not None:
            for node in scene2.backgroundEffect.resources.Find('trinity.TriTexture2DParameter'):
                if node.name == 'NebulaMap':
                    node.resourcePath = scene2.envMap1ResPath

        scene2.backgroundRenderingEnabled = True
        return scene2



    def GetPlanetPhoto(self, itemID, typeID, typeinfo, size = 512):
        filepath = self.GetCachePath(typeinfo, size, itemID, 0)
        planet = spaceObject.Planet()
        planet.GetPlanetByID(itemID, typeID)
        if planet.model is None or planet.model.highDetail is None:
            return 
        planetTransform = trinity.EveTransform()
        planetTransform.scaling = (100, 100, 100)
        planetTransform.children.append(planet.model.highDetail)
        scene = self.GetPlanetScene()
        try:
            planet.DoPreProcessEffectForPhotoSvc(size)
        except:
            del planetTransform.children[:]
            planetTransform = None
            planet.model = None
            planet = None
            return 
        trinity.WaitForResourceLoads()
        scene.sunDirection = (-1.0, 0.0, 0.0)
        scene.sunDiffuseColor = (1.0, 1.0, 1.0, 1.0)
        scene.objects.append(planetTransform)
        surface = self.TakeSnapShotUsingBoundingSphere(scene, size, 130, (0, 0, 0))
        ret = self._SaveSurfaceToFile(surface, filepath)
        del planetTransform.children[:]
        planetTransform = None
        planet.model = None
        planet = None
        return ret



    def GetSunPhoto(self, itemID, typeID, typeinfo, size = 512):
        filepath = self.GetCachePath(typeinfo, size, itemID, 0)
        graphicURL = cfg.invtypes.Get(typeID).GraphicFile()
        lensflare = trinity.Load(graphicURL)
        lensflare.position = trinity.TriVector(0.0, 0.0, 0.0)
        baseName = string.split(graphicURL, '/')
        baseName = baseName[-1]
        for flare in lensflare.flares:
            seq = trinity.TriScalarSequencer()
            if flare.scaleOverTime and hasattr(flare.scaleOverTime, 'keys'):
                for key in flare.scaleOverTime.keys:
                    key.value = key.value + 1.0

                seq.functions.append(flare.scaleOverTime)
            else:
                normalCurve = trinity.TriScalarCurve()
                normalCurve.value = 1.0
                seq.functions.append(normalCurve)
            flare.scaleOverTime = seq
            if not flare.opacityOverDot:
                dotCurve = trinity.TriScalarCurve()
                dotCurve.value = 1.0
                flare.opacityOverDot = dotCurve

        scenepath = sm.GetService('sceneManager').GetScene()
        scene = trinity.Load(scenepath)
        scene.lensFlare = lensflare
        trinity.WaitForResourceLoads()
        scene.Update(blue.os.GetTime())
        dev = trinity.device
        vec = trinity.TriVector(0.0, 0.0, -1.4)
        view = trinity.TriMatrix()
        projection = trinity.TriMatrix()
        fov = 1.0
        view.LookAtLH(vec, trinity.TriVector(0.0, 0.0, 0.0), trinity.TriVector(0.0, 1.0, 0.0))
        projection.PerspectiveFovLH(fov, 1.0, 1.0, 100000000.0)
        scene.camera.update = 0
        scene.camera.projection = projection
        scene.camera.view = view
        (target, stencil, viewport,) = self.TargetAndStencilAndViewport(size, format=trinity.TRIFMT_X8R8G8B8)
        rgbSource = dev.CreateOffscreenPlainSurface(size, size, trinity.TRIFMT_X8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        dev.RenderScene(scene, target, stencil, viewport, projection, view, blue.os.GetTime(), trinity.TRICLEAR_ZBUFFER | trinity.TRICLEAR_TARGET, rgbSource)
        return self._SaveSurfaceToFile(rgbSource, filepath)



    def RenderFromScene(self, x1, x2, y1, y2, res = 128, scale = 1.0):
        scene = trinity.device.scene
        if scene.pointStarfield:
            scene.pointStarfield.display = 0
        if scene.radar:
            scene.radar.display = 0
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        cX = x1 + (x2 - x1) / 2
        cY = y1 + abs(y1 - y2) / 2
        viewRange = scene.camera.fieldOfView
        pX1 = x1 / float(dw) * viewRange - viewRange * 0.5
        pX2 = x2 / float(dw) * viewRange - viewRange * 0.5
        xRange = (x2 - x1) / float(dw)
        yRange = (y2 - y1) / float(dh)
        dev = trinity.device
        sur = dev.CreateOffscreenPlainSurface(res, res, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        (target, stencil, viewport,) = self.TargetAndStencilAndViewport(res)
        pX1 = scene.camera.fieldOfView * 0.75
        pY1 = pX1 * (uicore.desktop.height / float(uicore.desktop.width))
        left = -pX1 + x1 / float(dw) * (pX1 * 2)
        right = -pX1 + x2 / float(dw) * (pX1 * 2)
        top = -pY1 + y1 / float(dh) * (pY1 * 2)
        bottom = -pY1 + y2 / float(dh) * (pY1 * 2)
        projection = trinity.TriMatrix()
        projection.PerspectiveOffCenterLH(left, right, -bottom, -top, 1.0, 100000000.0)
        try:
            dev.RenderScene(scene, target, stencil, viewport, projection, scene.camera.view, blue.os.GetTime(), trinity.TRICLEAR_ZBUFFER | trinity.TRICLEAR_TARGET, sur)
        except trinity.DeviceLostError:
            sys.exc_clear()
        if scene.pointStarfield:
            scene.pointStarfield.display = 1
        if scene.radar:
            scene.radar.display = 1
        return sur



    def GetPhotoScene(self, raceID):
        scenePaths = {const.raceCaldari: 'res:/Scene/ship_caldari.red',
         const.raceMinmatar: 'res:/Scene/ship_minmatar.red',
         const.raceGallente: 'res:/Scene/ship_gallente.red',
         const.raceAmarr: 'res:/Scene/ship_amarr.red'}
        scenePath = scenePaths.get(raceID, 'res:/Scene/ship_other.red')
        scene = trinity.Load(scenePath)
        scene.ambientColor = (1.0, 1.0, 1.0, 1.0)
        return scene



    def GetModelFromTypeinfo(self, typeinfo):
        modelPath = typeinfo.GraphicFile()
        if modelPath.find(' ') >= 0:
            modelPath = modelPath.split(' ')[0]
        if 'dx9' not in modelPath.lower():
            modelPath = modelPath.replace('res:/', 'res:/dx9/')
        if modelPath.endswith('.blue'):
            modelPath = '%s.red' % modelPath[:-5]
        model = trinity.Load(modelPath)
        if model is None:
            errmsg = 'Cannot generate photo. Failed to load model from path %s' % modelPath
            self.LogWarn(errmsg)
            raise RuntimeError(errmsg)
        return model



    def GetPinPhoto(self, typeID, typeinfo, size = 128):
        self.LogInfo('Getting Photo with typeID: ', typeID)
        outputPath = self.GetCachePath(typeinfo, size, 0, 0)
        model = self.GetModelFromTypeinfo(typeinfo)
        size = int(size)
        if hasattr(model, 'curveSets'):
            model.curveSets.removeAt(-1)
        scene = trinity.EveSpaceScene()
        scene.sunDirection = (-0.5, -0.5, -0.6)
        scene.objects.append(model)
        trinity.WaitForResourceLoads()
        if model.mesh != None:
            bBoxMin = trinity.TriVector(0.0, 0.0, 0.0)
            bBoxMax = trinity.TriVector(0.0, 0.0, 0.0)
            for i in range(model.mesh.geometry.GetMeshAreaCount(0)):
                (boundingBoxMin, boundingBoxMax,) = model.mesh.geometry.GetAreaBoundingBox(0, i)
                if abs(boundingBoxMax.y - boundingBoxMin.y) > 0.005:
                    if bBoxMin.Length() < boundingBoxMin.Length():
                        bBoxMin = boundingBoxMin
                    if bBoxMax.Length() < boundingBoxMax.Length():
                        bBoxMax = boundingBoxMax

            surface = self.TakeSnapShotUsingBoundingBox(scene, size, bBoxMin, bBoxMax)
            return self._SaveSurfaceToFile(surface, outputPath)
        raise StandardError('GetPinPhoto - No mesh found')



    def GetTurretPhoto(self, typeID, typeinfo = None, size = 128, bgColor = None, transparentBackground = True, usePreviewScene = False):
        self.LogInfo('Getting Photo with typeID: ', typeID)
        if transparentBackground:
            outputPath = 'Pictures/Gids/nobg_'
        else:
            outputPath = 'Pictures/Gids/'
        renderPath = outputPath + self.GetPictureFileName(typeinfo, size)
        cachePath = 'cache:/' + renderPath
        if self.CheckAvail(cachePath) is not None:
            return cachePath
        if usePreviewScene:
            model = trinity.Load('res:/dx9/model/ship/IconPreview/PreviewTurretShip.red')
        else:
            model = trinity.Load('res:/dx9/model/ship/IconPreview/PhotoServiceTurretShip.red')
        turretSet = turret.TurretSet.FitTurret(model, None, typeID, 1, checkSettings=False)
        if turretSet is not None and len(turretSet.turretSets):
            boundingSphere = turretSet.turretSets[0].boundingSphere
        else:
            log.LogError('PhotoSvc::GetTurretPhoto - could not determine bounding sphere for turret with typeID %d' % typeID)
            return 
        turretSet.turretSets[0].FreezeHighDetailLOD()
        typeinfo = typeinfo or cfg.invtypes.Get(typeID, None)
        size = int(size)
        if usePreviewScene:
            scene = trinity.Load('res:/dx9/scene/fitting/previewTurrets.red')
        else:
            scene = trinity.Load('res:/Scene/ship_other.red')
            scene.sunDirection = (-0.5, -0.5, 0.6)
            scene.sunDiffuseColor = (2.0, 2.0, 2.0)
            scene.ambientColor = (0.0, 0.0, 0.0)
        scene.objects.append(model)
        if transparentBackground:
            scene.backgroundRenderingEnabled = False
        trinity.WaitForResourceLoads()
        boundingSphereRadius = boundingSphere[3] * 0.9
        boundingSphereCenter = boundingSphere[:3]
        surface = self.TakeSnapShotUsingBoundingSphere(scene, size, boundingSphereRadius, boundingSphereCenter, cameraAngle=(0.7, -0.6, 0.0), transparentBackground=transparentBackground, bgColor=bgColor, fov=0.5)
        return self._SaveSurfaceToFile(surface, renderPath)



    def GetPhoto(self, typeID, typeinfo = None, size = 128, transparentBackground = False, bgColor = None):
        self.LogInfo('Getting Photo with typeID: ', typeID)
        typeinfo = typeinfo or cfg.invtypes.Get(typeID, None)
        model = self.GetModelFromTypeinfo(typeinfo)
        size = int(size)
        if hasattr(model, 'FreezeHighDetailMesh'):
            model.FreezeHighDetailMesh()
        if hasattr(model, 'curveSets'):
            model.curveSets.removeAt(-1)
        if hasattr(model, 'modelRotationCurve'):
            model.modelRotationCurve = None
        if hasattr(model, 'modelTranslationCurve'):
            model.modelTranslationCurve = None
        scene = self.GetPhotoScene(typeinfo.raceID)
        scene.sunDirection = (-0.5, -0.5, -0.6)
        scene.objects.append(model)
        if transparentBackground:
            scene.backgroundRenderingEnabled = False
        trinity.WaitForResourceLoads()
        if hasattr(model, 'GetLocalBoundingBox'):
            surface = self.TakeSnapShotUsingMeshGeometry(scene, size, model.mesh.geometry, model.mesh.meshIndex, boundingSphereRadius=model.GetBoundingSphereRadius(), boundingSphereCenter=model.GetBoundingSphereCenter(), transparentBackground=transparentBackground, bgColor=bgColor)
        else:
            boundingSphereRadius = model.boundingSphereRadius
            boundingSphereCenter = None
            if hasattr(model, 'boundingSphereCenter'):
                boundingSphereCenter = model.boundingSphereCenter
            surface = self.TakeSnapShotUsingBoundingSphere(scene, size, boundingSphereRadius, boundingSphereCenter, transparentBackground=transparentBackground, bgColor=bgColor)
        if transparentBackground:
            outputPath = 'Pictures/Gids/nobg_'
        else:
            outputPath = 'Pictures/Gids/'
        return self._SaveSurfaceToFile(surface, outputPath + self.GetPictureFileName(typeinfo, size))



    def GetCharacterPortrait(self, scene, size, view, projection, outputPath, format = trinity.TRIIFF_PNG):
        target = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, size, size, trinity.TRIFMT_X8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        stencil = trinity.TriSurfaceManaged(trinity.device.CreateDepthStencilSurface, size, size, trinity.TRIFMT_D16, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        surface = trinity.TriSurfaceManaged(trinity.device.CreateOffscreenPlainSurface, size, size, trinity.TRIFMT_X8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        renderJob = trinity.CreateRenderJob('TakeSnapShot')
        renderJob.SetRenderTarget(target)
        renderJob.SetProjection(projection)
        renderJob.SetView(view)
        renderJob.SetDepthStencil(stencil)
        renderJob.Clear((0.0, 0.0, 0.0, 1.0), 1.0)
        renderJob.Update(scene)
        renderJob.RenderScene(scene)
        trinity.WaitForResourceLoads()
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        trinity.device.GetRenderTargetData(target, surface)
        portraits = '/Pictures/Portraits/'
        filename = blue.os.cachepath + portraits + outputPath
        surface.SaveSurfaceToFile(filename, format)
        return surface



    def GetStorebanner(self, imageID, language, sprite):
        if self.storeBannerImages is None:
            server = self.GetImageServerURL('marketingImageServer', self.defaultMarketingImages)
            self.storeBannerImages = RemoteImageCacher('Storebanner', self, '.png', server)
        return self.GetImage(imageID, language, self.storeBannerImages, sprite)



    def GetImageServerURL(self, clientCfgValue = 'imageserverurl', defaultServer = None):
        imageServer = sm.GetService('machoNet').GetClientConfigVals().get(clientCfgValue)
        if imageServer is None:
            imageServer = defaultServer
        return imageServer




class DeviceResource(object):

    def __init__(self, dev, *args):
        self.args = args
        dev.RegisterResource(self)
        self.res = self.Create(dev)



    def OnInvalidate(self, level):
        del self.res



    def OnCreate(self, dev):
        self.res = self.Create(dev)




class OffScreenPlainSurface(DeviceResource):
    __guid__ = 'photoSvc.OffScreenPlainSurface'

    def Create(self, dev):
        return dev.CreateOffscreenPlainSurface(*self.args)



NOT_MODIFIED = 304
TEMP_REDIRECT = 302

class CustomRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        return None




class RemoteImageCacher(object):

    def __init__(self, cacheItem, logger, suffix, imageServer):
        self.initialized = False
        self.LogInfo = logger.LogInfo
        self.LogError = logger.LogError
        self.LogInfo('Initializing Remote Image service for', cacheItem)
        self.opener = urllib2.build_opener(CustomRedirectHandler())
        self.cacheItem = cacheItem
        self.cacheBasePath = 'cache:/Pictures/%ss/' % self.cacheItem
        self.cacheFile = '%s_%s' + suffix
        self.missingImages = {}
        self.watchList = {}
        if imageServer is None:
            self.LogError('RemoteImageCacher can not operate without a server URL!', imageServer)
            return 
        imageServer = imageServer.strip().encode('ascii')
        self.imageUri = imageServer
        if not imageServer.endswith('/'):
            self.imageUri += '/'
        self.imageUri += cacheItem + '/%s_%s' + suffix
        self.LogInfo('RemoteImageCacher initialized with imageUri', self.imageUri)
        self.initialized = True



    def Initialized(self):
        return self.initialized



    def AddToWatchList(self, itemID, callback):
        self.watchList[itemID] = callback



    def GetCachePath(self, itemID, size, createPath = False):
        basePath = self.cacheBasePath
        if self.cacheItem == 'Character' and size in (32, 64):
            basePath = '%sChat/%s/' % (self.cacheBasePath, itemID % 100)
        if createPath:
            pathToFile = blue.rot.PathToFilename(basePath)
            if not os.path.exists(pathToFile):
                os.makedirs(pathToFile)
        return basePath + self.cacheFile % (itemID, size)



    def GetCachedImage(self, itemID, size):
        if not self.Initialized():
            return (None, False)
        cachePath = self.GetCachePath(itemID, size)
        fileSystemPath = blue.rot.PathToFilename(cachePath)
        if os.path.exists(fileSystemPath):
            return (cachePath, self._RemoteImageCacher__IsFresh(cachePath))
        return (None, False)



    def MissingFromServer(self, itemID):
        lastTry = self.missingImages.get(itemID, None)
        if lastTry is not None:
            if time.time() - lastTry > 3600:
                del self.missingImages[itemID]
                return False
            return True
        return False



    def GetImage(self, itemID, size, forceUpdate = False):
        if not self.Initialized() or self.MissingFromServer(itemID) and not forceUpdate:
            return 
        try:
            uthread.Lock(self, itemID)
            try:
                cachePath = self.GetCachePath(itemID, size, createPath=True)
            except Exception as e:
                self.LogError('Failed to get image cache folder', repr(e))
                self.initialized = False
                return 
            cacheFile = blue.rot.PathToFilename(cachePath)
            lastModified = self._RemoteImageCacher__GetLastModified(cachePath)
            if forceUpdate or not self._RemoteImageCacher__IsFresh(cachePath):
                self.LogInfo('Get image for', itemID, 'is fetching/refreshing image. Forced = ', forceUpdate)
                image = self._RemoteImageCacher__GetImageFromUrl(itemID, size, lastModified)
                if image is None:
                    self.LogInfo('No image found for', itemID, 'adding to missing images')
                    self.missingImages[itemID] = time.time()
                    return 
                if image == NOT_MODIFIED:
                    self.LogInfo('Image has not been modified, updating cached image')
                    try:
                        with file(cacheFile, 'a'):
                            os.utime(cacheFile, None)
                    except Exception as e:
                        self.LogError('Failed to update timestamp', repr(e))
                else:
                    resfile = blue.os.CreateInstance('blue.ResFile')
                    try:
                        if not resfile.Open(cachePath, 0):
                            try:
                                resfile.Create(cachePath)
                            except Exception as e:
                                self.LogError('Failed to get image cache folder', repr(e))
                                self.initialized = False
                                return 
                        resfile.Write(image)
                        resfile.Close()
                    except Exception as e:
                        self.LogError('Failed to update cached image', repr(e))
                        return 
                    if itemID in self.watchList:
                        self.LogInfo('RemoteImageCached removed item ', itemID, 'was an item in the watchlist.')
                        self.watchList[itemID](itemID)
                        del self.watchList[itemID]

        finally:
            uthread.UnLock(self, itemID)

        return cachePath



    def __GetImageFromUrl(self, charID, size, lastModified = None):
        if not self.Initialized():
            return 
        url = (self.imageUri % (charID, size)).strip().encode('ascii')
        request = urllib2.Request(url, None)
        self.LogInfo('Getting image from', url)
        if lastModified:
            cacheTime = datetime.datetime.utcfromtimestamp(lastModified)
            cacheStamp = cacheTime.strftime('%a, %d %b %Y %H:%M:%S GMT')
            request.add_header('If-Modified-Since', cacheStamp)
        try:
            ret = self.opener.open(request)
        except urllib2.HTTPError as e:
            if e.code == NOT_MODIFIED:
                return NOT_MODIFIED
            if e.code == TEMP_REDIRECT:
                return 
            self.LogError('Error while fetching remote image', str(e))
            sys.exc_clear()
            return 
        except urllib2.URLError as e:
            self.LogError('Error while fetching remote image', str(e))
            sys.exc_clear()
            return 
        try:
            if 'content-type' not in ret.headers.keys() or not ret.headers['content-type'].startswith('image/'):
                self.LogError(url, 'was not an actual image')
                return 
            else:
                return ret.read()

        finally:
            ret.close()




    def __GetLastModified(self, cachePath):
        filepath = blue.rot.PathToFilename(cachePath)
        if os.path.exists(filepath):
            return os.path.getmtime(filepath)



    def __IsFresh(self, cachePath):
        lastModified = self._RemoteImageCacher__GetLastModified(cachePath)
        if lastModified is None:
            return False
        delta = time.time() - lastModified
        return delta < MAX_CACHE_AGE



    def RemoveFromCache(self, itemID, size):
        cachePath = self.GetCachePath(itemID, size)
        filepath = blue.rot.PathToFilename(cachePath)
        if os.path.exists(filepath):
            os.remove(filepath)



