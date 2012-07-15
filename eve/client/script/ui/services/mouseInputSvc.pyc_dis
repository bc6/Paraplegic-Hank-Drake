#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/mouseInputSvc.py
import service
import uiconst

class MouseInputService(service.Service):
    __guid__ = 'svc.mouseInput'
    __translateUIConst__ = {uiconst.MOUSELEFT: const.INPUT_TYPE_LEFTCLICK,
     uiconst.MOUSERIGHT: const.INPUT_TYPE_RIGHTCLICK,
     uiconst.MOUSEMIDDLE: const.INPUT_TYPE_MIDDLECLICK,
     uiconst.MOUSEXBUTTON1: const.INPUT_TYPE_EX1CLICK,
     uiconst.MOUSEXBUTTON2: const.INPUT_TYPE_EX2CLICK}

    def __init__(self):
        self.selectedEntityID = None
        service.Service.__init__(self)
        self.callbacks = {const.INPUT_TYPE_LEFTCLICK: [],
         const.INPUT_TYPE_RIGHTCLICK: [],
         const.INPUT_TYPE_MIDDLECLICK: [],
         const.INPUT_TYPE_EX1CLICK: [],
         const.INPUT_TYPE_EX2CLICK: [],
         const.INPUT_TYPE_DOUBLECLICK: [],
         const.INPUT_TYPE_MOUSEMOVE: [],
         const.INPUT_TYPE_MOUSEWHEEL: [],
         const.INPUT_TYPE_MOUSEDOWN: [],
         const.INPUT_TYPE_MOUSEUP: []}

    def GetSelectedEntityID(self):
        return sm.GetService('selectionClient').GetSelectedEntityID()

    def RegisterCallback(self, type, callback):
        self.callbacks[type].append(callback)

    def UnRegisterCallback(self, type, callback):
        self.callbacks[type].remove(callback)

    def OnDoubleClick(self, entityID):
        for callback in self.callbacks[const.INPUT_TYPE_DOUBLECLICK]:
            callback(entityID)

    def OnMouseUp(self, button, posX, posY, entityID):
        inputType = self.__translateUIConst__[button]
        for callback in self.callbacks[const.INPUT_TYPE_MOUSEUP]:
            callback(inputType, posX, posY, entityID)

        for callback in self.callbacks[inputType]:
            callback(entityID)

    def OnMouseDown(self, button, posX, posY, entityID):
        inputType = self.__translateUIConst__[button]
        for callback in self.callbacks[const.INPUT_TYPE_MOUSEDOWN]:
            callback(inputType, posX, posY, entityID)

    def OnMouseWheel(self, delta):
        for callback in self.callbacks[const.INPUT_TYPE_MOUSEWHEEL]:
            callback(delta)

    def OnMouseMove(self, deltaX, deltaY, entityID):
        for callback in self.callbacks[const.INPUT_TYPE_MOUSEMOVE]:
            callback(deltaX, deltaY, entityID)