import service

class EchoServer(service.Service):
    __guid__ = 'svc.echo'
    __exportedcalls__ = {'Echo': [service.ROLEMASK_ELEVATEDPLAYER]}

    def Echo(self, arg):
        return arg




