#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/net/eveEmailSvc.py
import svc

class EveEmailSvc(svc.emailSvc):
    __guid__ = 'svc.eveEmailSvc'
    __replaceservice__ = 'emailSvc'

    def AppGetMailServer(self):
        if hasattr(prefs, 'supportEmailServer'):
            server = prefs.supportEmailServer
            self.LogInfo('Email service using mail server from prefs.ini:', server, self.domain)
        elif self.domain == 'EVE.COM':
            server = '10.200.70.21;10.200.70.22'
            self.LogInfo('Email service using internal TQ mailserver', server, self.domain)
        elif self.domain == 'CCP':
            server = 'rkv-it-exch.ccp.ad.local'
            self.LogInfo('Email service using internal mailserver', server, self.domain)
        else:
            server = '10.200.70.21;10.200.70.22'
            self.LogInfo('Email service using default TQ mailserver', server, self.domain)
        return server