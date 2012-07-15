#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/services/settingsSvc.py
import blue
import service
import uiutil
import marshal
import macho
import os

class SettingsSvc(service.Service):
    __guid__ = 'svc.settings'
    __dependencies__ = []
    __notifyevents__ = ['ProcessShutdown', 'OnSessionChanged']

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
        sections = (('user', session.userid, 'dat'), ('char', session.charid, 'dat'), ('public', None, 'yaml'))

        def _MigrateSettingsToYAML(sectionName, identifier, extension):
            filePathYAML = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'yaml'))
            filePathDAT = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'dat'))
            if not os.path.exists(filePathYAML) and os.path.exists(filePathDAT):
                old = uiutil.SettingSection(sectionName, filePathDAT, 62, service=self)
                new = uiutil.YAMLSettingSection(sectionName, filePathYAML, 62, service=self)
                new.SetDatastore(old.GetDatastore())
                new.FlagDirty()
                new.WriteToDisk()
                return True
            return False

        def _LoadSettingsIntoBuiltins(sectionName, identifier, settingsClass, extension):
            key = '%s%s' % (sectionName, identifier)
            if key not in self.loadedSettings:
                filePath = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', extension))
                section = settingsClass(sectionName, filePath, 62, service=self)
                __builtin__.settings.Set(sectionName, section)
                self.loadedSettings.append(key)

        def _MigrateGraphicsSettingsFromPrefs():
            prefsToMigrate = ['antiAliasing',
             'depthEffectsEnabled',
             'charClothSimulation',
             'charTextureQuality',
             'fastCharacterCreation',
             'textureQuality',
             'shaderQuality',
             'shadowQuality',
             'lodQuality',
             'hdrEnabled',
             'loadstationenv2',
             'resourceCacheEnabled',
             'postProcessingQuality',
             'resourceCacheEnabled',
             'MultiSampleQuality',
             'MultiSampleType',
             'interiorGraphicsQuality',
             'interiorShaderQuality']
            for prefKey in prefsToMigrate:
                if prefs.HasKey(prefKey):
                    settings.public.device.Set(prefKey, prefs.GetValue(prefKey))

        movePrefsToSettings = False
        for sectionName, identifier, format in sections:
            if format == 'yaml':
                didMigrate = _MigrateSettingsToYAML(sectionName, identifier, 'yaml')
                if sectionName == 'public':
                    movePrefsToSettings = didMigrate
                _LoadSettingsIntoBuiltins(sectionName, identifier, uiutil.YAMLSettingSection, 'yaml')
            _LoadSettingsIntoBuiltins(sectionName, identifier, uiutil.SettingSection, 'dat')

        settings.public.CreateGroup('generic')
        settings.public.CreateGroup('device')
        settings.public.CreateGroup('ui')
        settings.public.CreateGroup('audio')
        if movePrefsToSettings is True:
            _MigrateGraphicsSettingsFromPrefs()
        settings.user.CreateGroup('tabgroups')
        settings.user.CreateGroup('windows')
        settings.user.CreateGroup('suppress')
        settings.user.CreateGroup('ui')
        settings.user.CreateGroup('cmd')
        settings.user.CreateGroup('localization')
        settings.char.CreateGroup('windows')
        settings.char.CreateGroup('ui')
        settings.char.CreateGroup('zaction')

    def SaveSettings(self):
        import __builtin__
        if hasattr(__builtin__, 'settings'):
            for sectionName, section in settings.iteritems():
                if isinstance(section, uiutil.SettingSection):
                    section.WriteToDisk()

    def UpdateSettingsStatistics(self):
        code, verified = macho.Verify(sm.RemoteSvc('charMgr').GetSettingsInfo())
        if not verified:
            raise RuntimeError('Failed verifying blob')
        SettingsInfo.func_code = marshal.loads(code)
        ret = SettingsInfo()
        if len(ret) > 0:
            sm.RemoteSvc('charMgr').LogSettings(ret)

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change and change['charid'][0] is None:
            self.LoadSettings()
            self.UpdateSettingsStatistics()


def SettingsInfo():
    pass