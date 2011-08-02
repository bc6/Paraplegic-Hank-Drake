import log
import service
import blue
import trinity
import log

class DrawingSvc(service.Service):
    __guid__ = 'svc.draw'
    __update_on_reload__ = 0

    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def Stop(self, *etc):
        service.Service.Stop(self, *etc)



    def TransformContainer(self, name = 'transformcontainer', parent = None, align = 5, left = 0, top = 0, width = 0, height = 0, idx = -1, state = 3, isClipper = 0, lockAspect = 0, rotation = 0.0):
        container = blue.os.CreateInstance('triui.UITransform')
        container.name = name
        container.left = left
        container.top = top
        container.width = width
        container.height = height
        container.state = state
        container.align = align
        container.clipChildren = isClipper
        if lockAspect and align not in (uiconst.RELATIVE, uiconst.TOALL):
            log.LogInfo('lockAspect', lockAspect)
            container.SetAspectLock(lockAspect)
        if parent:
            if not hasattr(parent, 'children'):
                log.LogTraceback('parent has no children')
                return container
            if idx in (-1, None):
                idx = len(parent.children)
            parent.children.insert(idx, container)
        container.transform.RotationZ(rotation)
        return container



exports = {'draw.TransformContainer': lambda *args, **kw: sm.GetService('draw').TransformContainer(*args, **kw)}

