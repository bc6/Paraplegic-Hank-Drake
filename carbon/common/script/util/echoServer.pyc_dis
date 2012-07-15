#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/echoServer.py
import service

class EchoServer(service.Service):
    __guid__ = 'svc.echo'
    __exportedcalls__ = {'Echo': [service.ROLEMASK_ELEVATEDPLAYER]}

    def Echo(self, arg):
        return arg