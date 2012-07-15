#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/graphicLoaderRequest.py
import loadRequest
import weakref

class GraphicLoaderRequest(loadRequest.PrioritizedLoadRequest):
    __guid__ = 'loadRequest.GraphicLoaderRequest'

    def __init__(self, graphicLoaderClient, graphicID):
        self.owner = None
        self.graphicLoaderClient = graphicLoaderClient
        self.graphicID = graphicID
        self.components = weakref.WeakKeyDictionary()

    def GetName(self):
        modelPath = sm.GetService('graphicClient').GetModelFilePath(self.graphicID)
        return 'graphicID %d - %s' % (self.graphicID, modelPath)

    def GetPriority(self):
        return sum((priority for priority, callback in self.components.itervalues()))

    def IsEmpty(self):
        return not bool(self.components)

    def Process(self):
        self.graphicLoaderClient._RemoveRequest(self.graphicID)
        for obj, (priority, callback) in self.components.iteritems():
            self.graphicLoaderClient._TrackObject(self.graphicID, obj)
            callback(obj)

    def AddComponent(self, obj, callback):
        self.components[obj] = (0, callback)

    def SetPriority(self, obj, priority):
        _, callback = self.components[obj]
        self.components[obj] = (priority, callback)