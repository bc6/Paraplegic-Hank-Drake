import stackless
import binascii

class A:
    __module__ = 'sys'
    __guid__ = 'sys.A'
    __passbyvalue__ = 1

    def __call__(self, messageID, formatDict = None):
        s = sm.StartService('agentMgr').GetStaticBlob(messageID)
        if formatDict:
            s = s % formatDict
        if type(s) is unicode:
            r = AgentUnicode(s)
        elif type(s) is str:
            r = AgentString(s)
        else:
            try:
                r = AgentUnicode(unicode(s))
            except:
                raise TypeError, "Can't unpickle strange string of type %s" % type(s)
        r.messageID = messageID
        if formatDict:
            r.formatDict = formatDict
        return r




class AgentString(str):
    __module__ = 'sys'
    __guid__ = 'sys.AgentString'

    def __reduce__(self):
        if stackless.getcurrent().frame.f_back.f_code.co_name == 'SaveConfig_170472':
            if hasattr(self, 'messageID'):
                if getattr(self, 'formatDict', False):
                    return (A(), (self.messageID, self.formatDict))
                else:
                    return (A(), (self.messageID,))
        return (str, (str(self),))




class AgentUnicode(unicode):
    __module__ = 'sys'
    __guid__ = 'sys.AgentUnicode'

    def __reduce__(self):
        if stackless.getcurrent().frame.f_back.f_code.co_name == 'SaveConfig_170472':
            if hasattr(self, 'messageID'):
                if getattr(self, 'formatDict', False):
                    return (A(), (self.messageID, self.formatDict))
                else:
                    return (A(), (self.messageID,))
        return (unicode, (unicode(self),))




