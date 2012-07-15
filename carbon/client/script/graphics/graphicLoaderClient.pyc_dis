#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicLoaderClient.py
import loadRequest
import service
import weakref

class GraphicLoaderClient(service.Service):
    __guid__ = 'svc.graphicLoaderClient'
    __dependencies__ = ['prioritizedLoadManager']

    def __init__(self):
        service.Service.__init__(self)
        self.graphicRequests = {}
        self.loadedGraphics = {}

    def LoadComponent(self, graphicID, component, callback):
        loadedObjects = self.loadedGraphics.get(graphicID)
        if loadedObjects:
            loadedObjects.add(component)
            callback(component)
        else:
            graphicRequest = self.graphicRequests.get(graphicID)
            if graphicRequest is None:
                graphicRequest = loadRequest.GraphicLoaderRequest(self, component.graphicID)
                graphicRequest.AddComponent(component, callback)
                self.graphicRequests[component.graphicID] = graphicRequest
                self.prioritizedLoadManager.Add(False, graphicRequest)
            else:
                graphicRequest.AddComponent(component, callback)

    def _RemoveRequest(self, graphicID):
        del self.graphicRequests[graphicID]

    def _TrackObject(self, graphicID, component):
        objectSet = self.loadedGraphics.get(graphicID)
        if objectSet is None:
            objectSet = weakref.WeakSet()
            self.loadedGraphics[graphicID] = objectSet
        objectSet.add(component)