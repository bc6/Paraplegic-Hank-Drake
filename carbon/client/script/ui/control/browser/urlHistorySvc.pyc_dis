#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/browser/urlHistorySvc.py
import blue
import collections
import cPickle
import service
import util
MAX_HISTORY_LENGTH = 1000

class UrlHistorySvc(service.Service):
    __guid__ = 'svc.urlhistory'
    __exportedcalls__ = {'AddToHistory': [],
     'ClearAllHistory': [],
     'GetHistory': [],
     'SaveHistory': []}

    def __init__(self):
        self.historyPath = 'cache:/Browser/browserHistory.txt'
        self.historyIsDirty = False
        service.Service.__init__(self)

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.LoadHistory()

    def GetHistory(self):
        return self.history

    def ClearAllHistory(self):
        self.history = collections.deque()
        self.SaveHistory()

    def AddToHistory(self, url, title, timestamp):
        while len(self.history) > MAX_HISTORY_LENGTH:
            self.history.pop()

        h = util.KeyVal()
        h.url = url
        h.title = title
        h.ts = timestamp
        self.history.appendleft(h)
        self.historyIsDirty = True

    def LoadHistory(self):
        self.history = None
        f = blue.ResFile()
        try:
            if f.Open(self.historyPath):
                self.history = collections.deque([ x for x in cPickle.loads(f.Read()) if type(x.ts) == long ])
                f.Close()
        except:
            self.LogInfo('Error loading history file. Starting new history file')
            self.history = None

        if not self.history:
            self.history = collections.deque()

    def SaveHistory(self):
        if not self.historyIsDirty:
            return
        self.historyIsDirty = False
        f = blue.ResFile()
        try:
            f.Create(self.historyPath)
            f.Write(cPickle.dumps(list(self.history)))
            f.Close()
            self.LogInfo('successfully saved', len(self.history), 'browser history entries to disk')
        except Exception as e:
            self.LogError('Error saving in-game browser history to disk', e)