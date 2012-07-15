#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/pagedCollection.py


class PagedCollection(object):
    __guid__ = 'util.PagedCollection'

    def __init__(self, resultSet = None, perPage = 50, totalCount = 0):
        self.page = 0
        self.collection = []
        self.totalCount = totalCount
        self.perPage = perPage
        if resultSet:
            self.Add(resultSet)

    def Reset(self):
        self.page = 0
        self.collection = []
        self.totalCount = 0
        self.perPage = 50

    def Add(self, resultSet):
        if self.totalCount != resultSet.totalCount:
            if len(self.collection):
                self.collection = []
                self.page = 0
            self.totalCount = resultSet.totalCount
            self.perPage = resultSet.perPage
        start = self.perPage * resultSet.page
        if not self.page:
            self.page = resultSet.page
        elif resultSet.page > self.page:
            self.page = resultSet.page
        self.collection[start:start + self.perPage] = resultSet[0:self.perPage]

    def __len__(self):
        return self.totalCount

    def __getitem__(self, item):
        return self.collection[item]

    def __contains__(self, item):
        return item in self.collection

    def __delitem__(self, key):
        del self.collection[key]
        self.totalCount -= 1

    def append(self, item):
        self.collection.append(item)
        self.totalCount += 1

    def PageCount(self):
        if self.totalCount:
            return self.totalCount / self.perPage + 1
        return 0


class PagedResultSet(object):
    __guid__ = 'util.PagedResultSet'
    __passbyvalue__ = 1

    def __init__(self, collection = None, totalCount = None, page = None, perPage = 50):
        self.collection = collection or []
        self.totalCount = totalCount
        self.page = page
        self.perPage = perPage

    def __len__(self):
        return len(self.collection)

    def __iter__(self):
        return self.collection.__iter__()

    def __getitem__(self, item):
        return self.collection[item]