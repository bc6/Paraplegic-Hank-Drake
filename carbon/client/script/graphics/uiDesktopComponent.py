import service
import trinity
import blue
import uthread
import log
import sys
import uicls
import uiconst
import collections
import weakref

class UIDesktopComponent(object):
    __guid__ = 'component.UIDesktopComponent'

    def __init__(self):
        self.uiDesktopName = ''
        self.uiDesktop = None
        self.renderTarget = None
        self.width = 1280
        self.height = 720
        self.liveUpdates = False
        self.updateFunction = None
        self.renderJob = None
        self.active = True
        self.autoMipMap = False
        self.entityID = None
        self.format = trinity.TRIFORMAT.TRIFMT_X8R8G8B8
        if blue.win32.IsTransgaming():
            self.format = trinity.TRIFORMAT.TRIFMT_A8R8G8B8




class UIDesktopComponentManager(service.Service):
    __guid__ = 'svc.UIDesktopComponentManager'
    __componentTypes__ = ['UIDesktopComponent']
    __notifyevents__ = []

    def __init__(self):
        service.Service.__init__(self)
        trinity.device.RegisterResource(self)
        self.uiDesktops = []
        self.updateThreadsByID = weakref.WeakValueDictionary()



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['uiDesktopName'] = component.uiDesktopName
        report['uiDesktop'] = str(component.uiDesktop)
        report['renderTarget'] = component.renderTarget is not None
        report['width'] = component.width
        report['height'] = component.height
        report['live'] = component.liveUpdates
        report['renderJob'] = str(component.renderJob)
        report['updateFunction'] = component.updateFunction is not None
        report['active'] = component.active
        return report



    def OnInvalidate(self, *args):
        for desktop in self.uiDesktops:
            desktop.renderTarget.AttachToTexture(None)




    def OnCreate(self, device):
        for desktop in self.uiDesktops:
            self.CreateUIDesktopRendertarget(desktop)
            if desktop.liveUpdates == False:
                uthread.new(self.UpdateAndRenderUIDesktop, desktop)




    def UpdateUIDesktop_t(self, component):
        while component.active:
            self.UpdateUIDesktop(component)




    def UpdateUIDesktop(self, component):
        if component.updateFunction is not None:
            try:
                component.updateFunction(component.width, component.height, component.uiDesktop, component.entityID)
            except Exception:
                log.LogException()
                sys.exc_clear()



    def RenderUIDesktop(self, component):
        if component.renderJob is not None:
            component.renderJob.ScheduleOnce()



    def UpdateAndRenderUIDesktop(self, component):
        self.UpdateUIDesktop(component)
        self.RenderUIDesktop(component)



    def CreateUIDesktopRendertarget(self, component):
        if component.renderTarget is not None:
            if component.autoMipMap:
                rt = trinity.device.CreateTexture(component.width, component.height, 0, trinity.TRIUSAGE_RENDERTARGET | trinity.TRIUSAGE_AUTOGENMIPMAP, component.format, trinity.TRIPOOL_DEFAULT)
            else:
                rt = trinity.device.CreateTexture(component.width, component.height, 1, trinity.TRIUSAGE_RENDERTARGET, component.format, trinity.TRIPOOL_DEFAULT)
            component.renderTarget.AttachToTexture(rt)
            if hasattr(component.renderTarget, 'name'):
                component.renderTarget.name = component.uiDesktopName
            if component.uiDesktop is not None:
                component.uiDesktop.renderTargetStep.target = rt.GetSurfaceLevel(0)



    def CreateComponent(self, name, state):
        component = UIDesktopComponent()
        if 'uiDesktopName' in state:
            component.uiDesktopName = str(state['uiDesktopName'])
            component.renderTarget = blue.resMan.GetResource('dynamic:/%s' % component.uiDesktopName)
            if component.renderTarget is None:
                log.LogError('Failed to acquire a render target texture for %s' % component.uiDesktopName)
            try:
                import screens
                (component.width, component.height, component.format, component.liveUpdates, component.autoMipMap, component.updateFunction,) = getattr(screens, component.uiDesktopName)
            except AttributeError as ImportError:
                log.LogException()
            if not component.liveUpdates:
                component.active = False
                component.renderJob = trinity.CreateRenderJob()
        else:
            log.LogError('No uiDesktopName set')
        self.uiDesktops.append(component)
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        component.entityID = entityID
        try:
            self.CreateUIDesktopRendertarget(component)
        except trinity.D3DError:
            sys.exc_clear()
        if component.renderTarget is not None:
            rt = component.renderTarget.GetSurfaceLevel(0)
        else:
            rt = None
        if component.liveUpdates:
            component.uiDesktop = uicore.uilib.CreateRootObject(component.uiDesktopName, width=component.width, height=component.height, renderTarget=rt, renderJob=component.renderJob)
        else:
            component.uiDesktop = uicls.UIRoot(name=component.uiDesktopName, width=component.width, height=component.height, renderTarget=rt, renderJob=component.renderJob)



    def SetupComponent(self, entity, component):
        interiorPlaceable = entity.GetComponent('interiorPlaceable')
        desktopComponent = entity.GetComponent('UIDesktopComponent')
        if interiorPlaceable is not None and desktopComponent.uiDesktop is not None:
            desktopComponent.uiDesktop.sceneObject = interiorPlaceable.renderObject
        if not component.liveUpdates:
            updateThread = uthread.new(self.UpdateAndRenderUIDesktop, component)
            updateThread.context = 'svc.UIDesktopComponentManager.UpdateAndRenderUIDesktop'
            self.updateThreadsByID[entity.entityID] = updateThread
            return 
        if component.uiDesktop is None:
            return 
        desktopComponent.uiDesktop.positionComponent = entity.GetComponent('position')
        updateThread = uthread.new(self.UpdateUIDesktop_t, component)
        self.updateThreadsByID[entity.entityID] = updateThread



    def UnRegisterComponent(self, entity, component):
        if component.uiDesktop:
            component.uiDesktop.sceneObject = None
            component.uiDesktop.Close()
            component.active = False
            if component.liveUpdates:
                try:
                    uicore.uilib.RemoveRootObject(component.uiDesktop)
                except KeyError:
                    log.LogWarn('UIDesktop root object for was already removed somehow:', component.uiDesktopName)
        if entity.entityID in self.updateThreadsByID:
            self.updateThreadsByID.pop(entity.entityID).kill()
        self.uiDesktops.remove(component)




