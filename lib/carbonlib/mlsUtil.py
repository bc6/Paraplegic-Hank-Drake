import sys
import log
import blue
import os
import cPickle
import __builtin__
import types
Log = log.GetChannel('_Mls.General').Log
WARNING_LOG_THRESHOLD = 50
if boot.role != 'client':
    prefs.languageID = 'EN'
    if boot.region == 'optic':
        prefs.languageID = 'ZH'
print 'Multi-Language System: %s using language [%s]' % (boot.role.title(), prefs.languageID)
suppressedWarnings = {}
verifiedTranslations = {}
EXPECTED_PACKAGE_VERSION = 1

class LabelWrap(object):

    def __init__(self, languageID):
        self.languageID = languageID



    def __str__(self):
        return 'LabelWrap for ' + self.languageID



    def __getattr__(self, name):
        if self.languageID == 'EN':
            if name in mls.textLabels:
                (dataID, text,) = mls.textLabels[name]
                return text
            if name in cfg.messages:
                return cfg.messages[name].messageText
            if not name.startswith('__'):
                text = 'LabelWrap: Localization error, text label not defined (or outdated textlabels.pickle files): %s' % name
                log.LogTraceback(extraText=text, channel='_Mls.General', severity=log.LGWARN, toConsole=False)
            return name.lower()
        if name not in mls.textLabels:
            raise AttributeError, name
        (dataID, text,) = mls.textLabels[name]
        return Tr(text, 'zmls.texts.text', dataID, self.languageID)



    def HasLabel(self, name):
        return name in mls.textLabels or name in cfg.messages



    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError, name




class Mls(object):
    __guid__ = 'mlsUtil.Mls'

    def CleanSuppressions(self):
        suppressedWarnings.clear()



    def __init__(self):
        self.langPacks = {}
        self.constants = {}
        self.textLabels = {}
        self.messagePackage = None
        self._Mls__englishWrapper = LabelWrap('EN')
        Mark('^boot::mls::LoadLabelsAndTcIDs', self.LoadLabelsAndTcIDs)



    def LoadPickle(self, filename, default):
        f = blue.ResFile()
        localFilename = 'res:/%s.pickle' % filename
        sharedFilename = 'bin:/../common/res/%s.pickle' % filename
        if not f.Open(localFilename) and not f.Open(sharedFilename):
            LogTr('', "File '%s' does not exist." % filename)
            return default
        data = f.Read()
        f.Close()
        return cPickle.loads(data)



    def GetLanguageID(self):
        languageID = None
        if session and session.languageID:
            languageID = session.languageID
        elif charsession and charsession.languageID:
            languageID = charsession.languageID
        if languageID is None:
            languageID = prefs.languageID
        return languageID



    def LoadLabelsAndTcIDs(self):
        self.messagePackage = self.LoadPickle('messagePackage', None)
        if self.messagePackage is None:
            raise RuntimeError("LoadLabelsAndTcIDs: Can't continue without messagePackage.pickle")
        if self.messagePackage['version'] != EXPECTED_PACKAGE_VERSION:
            args = (self.messagePackage['version'], EXPECTED_PACKAGE_VERSION)
            raise RuntimeError('LoadLabelsAndTcIDs: messagePackage.pickle file format is version %s but I need version %s' % args)
        self.textLabels = self.messagePackage['textLabels']
        self.constants = self.messagePackage['constants']
        args = (self.messagePackage['version'],
         len(self.messagePackage['textLabels']),
         len(self.messagePackage['messages'][1]),
         len(self.messagePackage['constants']))
        Log('LoadLabelsAndTcIDs: version %s, %s labels, %s messages and %s constants,' % args)
        if boot.role != 'server':
            self.LoadTranslations(prefs.languageID)



    def LoadTranslations(self, languageID):
        return Mark('^boot::mls::%s' % languageID, self.LoadTranslations_, languageID)



    def LoadTranslations_(self, languageID):
        if languageID == 'EN':
            Log('LoadTranslations [EN]: English translations are implicit')
            return {}
        translations = self.LoadPickle('translations.%s' % languageID, {})
        self.langPacks[str(languageID)] = translations
        setattr(self, languageID, LabelWrap(languageID))
        Log('LoadTranslations [%s]:  %s entries' % (languageID, len(translations)))
        return translations



    def LoadMessages(self):
        return Mark('^boot::mls::LoadMessages', self.LoadMessages_)



    def LoadMessages_(self):
        if self.messagePackage is None:
            self.LoadLabelsAndTcIDs()
        import dbutil
        (hd, it,) = self.messagePackage['messages']
        rowDescriptor = blue.DBRowDescriptor((('messageKey', const.DBTYPE_STR),
         ('messageType', const.DBTYPE_STR),
         ('messageText', const.DBTYPE_WSTR),
         ('urlAudio', const.DBTYPE_STR),
         ('urlIcon', const.DBTYPE_STR),
         ('dataID', const.DBTYPE_I4)))
        rowset = dbutil.CRowset(rowDescriptor, [])
        for li in it.itervalues():
            rowset.InsertNew(li)

        messages = rowset.Index('messageKey')
        if messages is None:
            raise RuntimeError("Mls::LoadMessages: Can't continue without text messages")
        if prefs.languageID == 'EN':
            return messages
        if prefs.languageID not in self.langPacks:
            translations = self.LoadTranslations(prefs.languageID)
        else:
            translations = self.langPacks[prefs.languageID]
        tcID = self.constants['eve.messages.messageText']
        for msg in messages.itervalues():
            if not msg.messageText:
                continue
            trID = (tcID, msg.dataID)
            if trID not in translations:
                if len(translations) >= WARNING_LOG_THRESHOLD:
                    LogTr("Translation not found for eveMessage '%s'" % msg.dataID, prefs.languageID)
            else:
                transText = translations[trID]
                error = ValidateTranslation(prefs.languageID, (tcID, msg.dataID), msg.messageText, transText)
                if not error:
                    msg.messageText = transText

        self.messagePackage = None
        Log('LoadMessages [%s]: %s entries' % (prefs.languageID, len(messages)))
        return messages



    def Reload(self):
        self.LoadLabelsAndTcIDs()
        self.LoadMessages()



    def __getattr__(self, name):
        try:
            return self.GetLabel(name)
        except KeyError:
            if not name.startswith('__'):
                text = 'Mls: Localization error, text label not defined (or outdated textlabels.pickle files): %s' % name
                log.LogTraceback(extraText=text, channel='_Mls.General', severity=log.LGWARN, toConsole=False)
            return name.lower()



    def HasLabel(self, name):
        return name in self.textLabels or name in cfg.messages



    def GetLabel(self, name):
        if name in self.textLabels:
            (dataID, text,) = self.textLabels[name]
            return Tr(text, 'zmls.texts.text', dataID, textLabel=name)
        try:
            return cfg.messages[name].messageText
        except:
            raise KeyError, name



    def Placeholder(self, text):
        log.LogWarn('MLS: Placeholder text used in game. Please replace hardcoded text with an MLS label. text=', text)
        return u'!__%s__!' % text



    def GetLabelIfExists(self, name):
        try:
            return self.GetLabel(name)
        except:
            sys.exc_clear()
            return None



    def __getitem__(self, index):
        if index == 'EN':
            return self._Mls__englishWrapper
        if index not in self.langPacks:
            if index not in suppressedWarnings:
                suppressedWarnings[index] = 1
                text = "Localization error, language pack '%s' not supported or not loaded." % index
                log.LogTraceback(extraText=text, channel='_Mls.General', severity=log.LGWARN, toConsole=False)
            return self._Mls__englishWrapper
        return getattr(self, index)



    def __str__(self):
        return 'Multi-language wrapper. Loaded languages: %s' % self.langPacks.keys()




def LogTr(text, languageID):
    text = 'Translation error[%s]: %s' % (languageID, text)
    log.general.Log('%s' % text, log.LGINFO)



def Tr(originalText, tcName, keyID, languageID = None, logErrors = True, textLabel = ''):
    if not originalText:
        return originalText
    if languageID is None:
        if session and session.languageID:
            languageID = session.languageID
        elif charsession and charsession.languageID:
            languageID = charsession.languageID
        if languageID is None:
            languageID = prefs.languageID
    if languageID == 'EN':
        return originalText
    if languageID not in mls.langPacks:
        if logErrors and languageID not in suppressedWarnings:
            suppressedWarnings[languageID] = 1
            LogTr('Language pack missing', languageID)
        return originalText
    if not mls.langPacks[languageID] or len(mls.langPacks[languageID]) < WARNING_LOG_THRESHOLD:
        return originalText
    if tcName not in mls.constants:
        if logErrors:
            LogTr("tcID not found for '%s'" % tcName, languageID)
        return originalText
    tcID = mls.constants[tcName]
    key = (tcID, keyID)
    if key not in mls.langPacks[languageID]:
        supp = (languageID, key)
        if supp not in suppressedWarnings:
            suppressedWarnings[supp] = 1
            if textLabel:
                textLabel += ' '
            if logErrors:
                LogTr("ID %s %sfrom '%s' has not been translated. Text=%s" % (keyID,
                 textLabel,
                 tcName,
                 originalText[:100]), languageID)
        return originalText
    translatedText = mls.langPacks[languageID][key]
    error = ValidateTranslation(languageID, key, originalText, translatedText, textLabel, tcName)
    if error:
        return originalText
    debug = prefs.GetValue('debugEnglish', False)
    if debug:
        import re
        pattern = re.compile('%\\(.*\\)s|%s')
        originalText = pattern.sub('', originalText)
        return '%s (%s)' % (translatedText, originalText)
    return translatedText



def MarkInvalid(languageID, key, original, translated, textLabel, tcName, reason):
    supp = (languageID, key)
    if supp not in suppressedWarnings:
        suppressedWarnings[supp] = 1
        if textLabel:
            textLabel += ' '
        LogTr("The translated text for %s %sfrom '%s' cannot be formatted with the same info as the original text. Text=%s.  Reason=%s" % (key,
         textLabel,
         tcName,
         original[:100],
         reason), languageID)
    verifiedTranslations[key] = reason
    return reason



def ValidateTranslation(languageID, key, original, translated, textLabel = 'label unknown', tcName = 'tc unknown', recheck = False):
    prev = verifiedTranslations.get(key, None)
    if not recheck and prev is not None:
        return prev
    if original.find('%(') >= 0:
        current = original
        d = {}
        last = None
        ok = False
        for i in xrange(100):
            ok = False
            try:
                current = current % d
                ok = True
                break
            except ValueError as e:
                if e.args[0] in ('incomplete format',):
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'incomplete format specifier in original message')
                else:
                    if e.args[0].startswith("unsupported format character '"):
                        sys.exc_clear()
                        char = e.args[0][len("unsupported format character 'x' (0x"):]
                        char = char[:char.index(')')]
                        char = unichr(int(char, 16))
                        return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unsupported format specifier "<b>%s</b>" in original message' % char)
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected value error in original message: <b>%s</b>' % strx(e.args))
            except KeyError as e:
                if i > 50:
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Too many key errors in original message')
                d[strx(e.args[0])] = '%(' + strx(e.args[0]) + ')s'
                last = strx(e.args[0])
            except TypeError as e:
                if e.args[0] == 'not enough arguments for format string':
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Dangling <b>%</b> in original message')
                if last:
                    if e.args[0] in ('%d format: a number is required, not str', 'an integer is required', 'int argument required'):
                        d[last] = 1
                    elif e.args[0] in ('float argument required, not str', 'a float is required', 'float argument required'):
                        d[last] = 1.0
                    else:
                        sys.exc_clear()
                        return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected type error in original message: <b>%s</b>' % strx(e.args))
                else:
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected type error in original message without prior context available: <b>%s</b>' % strx(e.args))
            sys.exc_clear()

        if not ok:
            supp = (languageID, key)
            if supp not in suppressedWarnings:
                suppressedWarnings[supp] = 1
                if textLabel:
                    textLabel += ' '
                LogTr("The original text for %s %sfrom '%s' has invalid format specifiers. Text=%s" % (key,
                 textLabel,
                 tcName,
                 original[:100]), languageID)
            return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'The original text could not be formatted')
        try:
            translated % d
        except ValueError as e:
            if e.args[0] in ('incomplete format',):
                sys.exc_clear()
                return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'incomplete format specifier in translated message')
            else:
                if e.args[0].startswith('unsupported format character'):
                    char = e.args[0][len("unsupported format character 'x' (0x"):]
                    char = char[:char.index(')')]
                    char = unichr(int(char, 16))
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unsupported format specifier "<b>%s</b>" in translated message' % char)
                sys.exc_clear()
                return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected value error in translated message: <b>%s</b>' % strx(e.args))
        except KeyError as e:
            sys.exc_clear()
            return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected format identifier <b>%s</b> in translated message' % strx(e.args[0]))
        except TypeError as e:
            if e.args[0] == 'not enough arguments for format string':
                sys.exc_clear()
                return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Dangling <b>%</b> in translated message')
            else:
                if e.args[0] in ('%d format: a number is required, not str', 'an integer is required', 'int argument required'):
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'The translated message required an <b>integer</b> where the original message required a <b>string or float</b>')
                if e.args[0] in ('float argument required, not str', 'a float is required', 'float argument required'):
                    sys.exc_clear()
                    return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'The translated message required a <b>float</b> where the original message required a <b>string or integer</b>')
                sys.exc_clear()
                return MarkInvalid(languageID, key, original, translated, textLabel, tcName, 'Unexpected type error <b>%s</b> in translated message' % strx(e.args))
    verifiedTranslations[key] = ''
    return verifiedTranslations[key]


import __builtin__
if not hasattr(__builtin__, 'Tr'):
    __builtin__.Tr = Tr
    __builtin__.mls = Mls()
    __builtin__.ValidateTranslation = ValidateTranslation

