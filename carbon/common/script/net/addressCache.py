
class AddressCache:
    __guid__ = 'gps.AddressCache'

    def __init__(self):
        self._addressCache = {}



    def Get(self, service, address):
        try:
            return self._addressCache[(service, address)]
        except KeyError:
            return None



    def Set(self, service, address, nodeID):
        key = (service, address)
        result = not self._addressCache.has_key(key)
        self._addressCache[key] = nodeID
        return result



    def Remove(self, service, address):
        try:
            del self._addressCache[(service, address)]
            return True
        except KeyError:
            return False



    def RemoveAllForNode(self, nodeID):
        to_be_removed = []
        for (k, v,) in self._addressCache.iteritems():
            if v == nodeID:
                to_be_removed.append(k)

        for k in to_be_removed:
            del self._addressCache[k]




    def GetSize(self):
        return len(self._addressCache)



    def Clear(self):
        self._addressCache.clear()



    def GetNodeAddressMap(self):
        nodeMap = {}
        for (k, v,) in self._addressCache.iteritems():
            if v in nodeMap:
                nodeMap[v].append(k)
            else:
                nodeMap[v] = [k]

        return nodeMap




