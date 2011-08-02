import blue
import base
import log
import os
import defaultsetting
import uiutil
import types

class SettingSection:

    def __init__(self, name, filepath, autoStoreInterval):
        self._SettingSection__name = name
        self._SettingSection__filepath = filepath
        self._SettingSection__dirty = False
        self.datastore = {}
        data = None
        try:
            fn = blue.rot.PathToFilename(filepath)
            data = blue.win32.AtomicFileRead(fn)
        except:
            pass
        if data and data[0]:
            try:
                self.datastore = blue.marshal.Load(data[0])
                for (k, v,) in self.datastore.iteritems():
                    self.CreateGroup(k)

            except:
                log.LogException('Error loading settings data file-- %s' % str(self))
        self.timeoutTimer = base.AutoTimer(autoStoreInterval * 1000, self.WriteToDisk)



    def __str__(self):
        return '%s\nSetting section, %s; holding %s groups.\nFileLocation: %s' % ('-' * 60,
         self._SettingSection__name,
         len(self.datastore),
         self._SettingSection__filepath)



    def __repr__(self):
        s = self.__str__() + '\n'
        for (groupName, groupValue,) in self.datastore.iteritems():
            s += '%s:\n' % groupName
            for (settingName, settingValue,) in groupValue.iteritems():
                s += '    %s: %s\n' % (settingName, settingValue)


        return s



    class Group(dict):

        def __init__(self, name, section):
            self.__dict__['name'] = name
            self.__dict__['section'] = section



        def __getattr__(self, attrName):
            if hasattr(self, 'section'):
                return self.section.Get(self.name, attrName)



        def Get(self, attrName, defValue = None):
            retVal = self.__getattr__(attrName)
            if retVal is None:
                return defValue
            return retVal



        def __setattr__(self, attrName, value):
            if hasattr(self, 'section'):
                self.section.Set(self.name, attrName, value)


        Set = __setattr__

        def Release(self):
            self.section = None



        def HasKey(self, attrName):
            return self.section.HasKey(self.name, attrName)



        def Delete(self, attrName):
            self.section.Delete(self.name, attrName)



        def GetValues(self):
            return self.section.GetValues(self.name)




    def GetValues(self, groupName):
        return self.datastore[groupName]



    def Get(self, groupName, settingName):
        if groupName not in self.datastore:
            self.CreateGroup(groupName)
        if settingName in self.datastore[groupName]:
            value = self.datastore[groupName][settingName][1]
            self.datastore[groupName][settingName] = (blue.os.GetTime(), value)
            return value
        else:
            n = settingName
            if type(n) == types.UnicodeType:
                n = n.encode('UTF-8')
            return uiutil.GetAttrs(defaultsetting, self._SettingSection__name, groupName, n)



    def HasKey(self, groupName, settingName):
        return bool(self.Get(groupName, settingName))



    def Delete(self, groupName, settingName):
        if self.HasKey(groupName, settingName):
            del self.datastore[groupName][settingName]



    def Set(self, groupName, settingName, value):
        if groupName not in self.datastore:
            self.CreateGroup(groupName)
        self.datastore[groupName][settingName] = (blue.os.GetTime(), value)
        self.FlagDirty()



    def Remove(self, groupName, settingName = None):
        if groupName in self.datastore:
            group = self.datastore[groupName]
            if settingName:
                if settingName in group:
                    del group[settingName]
            else:
                del self.datastore[groupName]
            self.FlagDirty()



    def CreateGroup(self, groupName):
        if groupName not in self.__dict__:
            self.__dict__[groupName] = self.Group(groupName, self)
        if groupName not in self.datastore:
            self.datastore[groupName] = {}



    def FlagDirty(self):
        self._SettingSection__dirty = True



    def WriteToDisk(self, force = False):
        if self._SettingSection__dirty or force:
            self._SettingSection__dirty = False
            fn = blue.rot.PathToFilename(self._SettingSection__filepath)
            try:
                if os.access(fn, os.F_OK) and not os.access(fn, os.W_OK):
                    os.chmod(fn, 438)
                k = blue.marshal.Save(self.datastore)
                blue.win32.AtomicFileWrite(fn, k)
            except Exception:
                log.LogException()



    def Unload(self):
        self.timeoutTimer = None
        self.FlushOldEntries()
        self.WriteToDisk()



    def Save(self):
        self.FlushOldEntries()
        self.WriteToDisk()



    def FlushOldEntries(self):
        lastModified = blue.os.GetTime() - WEEK * 6
        for (k, v,) in self.datastore.iteritems():
            for key in v.keys():
                if v[key][0] <= lastModified:
                    del v[key]


        self.FlagDirty()



exports = {'uiutil.SettingSection': SettingSection}

