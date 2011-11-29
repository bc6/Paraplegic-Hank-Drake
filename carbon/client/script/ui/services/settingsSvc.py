import blue
import service
import uiutil

class SettingsSvc(service.Service):
    __guid__ = 'svc.settings'
    __dependencies__ = []
    __notifyevents__ = ['ProcessShutdown']

    def __init__(self):
        service.Service.__init__(self)
        self.loadedSettings = []



    def Run(self, *etc):
        service.Service.Run(self)
        self.LoadSettings()



    def ProcessShutdown(self):
        self.SaveSettings()



    def LoadSettings(self):
        import __builtin__
        self.SaveSettings()
        if not hasattr(__builtin__, 'settings'):
            __builtin__.settings = uiutil.Bunch()
        settingSections = (('public', None), ('user', session.userid), ('char', session.charid))
        for (sectionName, identifier,) in settingSections:
            key = '%s%s' % (sectionName, identifier)
            if key not in self.loadedSettings:
                filePath = blue.os.ResolvePathForWriting(u'settings:/core_%s_%s.dat' % (sectionName, identifier or '_'))
                section = uiutil.SettingSection(sectionName, filePath, 62, service=self)
                __builtin__.settings.Set(sectionName, section)
                self.loadedSettings.append(key)

        settings.public.CreateGroup('generic')
        settings.public.CreateGroup('device')
        settings.public.CreateGroup('ui')
        settings.public.CreateGroup('audio')
        settings.user.CreateGroup('tabgroups')
        settings.user.CreateGroup('windows')
        settings.user.CreateGroup('suppress')
        settings.user.CreateGroup('ui')
        settings.user.CreateGroup('cmd')
        settings.user.CreateGroup('localization')
        settings.char.CreateGroup('ui')
        settings.char.CreateGroup('zaction')



    def SaveSettings(self):
        import __builtin__
        if hasattr(__builtin__, 'settings'):
            for (sectionName, section,) in settings.iteritems():
                if isinstance(section, uiutil.SettingSection):
                    section.WriteToDisk(True)





