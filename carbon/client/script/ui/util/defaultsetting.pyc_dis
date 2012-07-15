#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/util/defaultsetting.py
"""

    Author:     Fridrik Haraldsson
    Created:    September 2008
    Project:    Core


    Description:

    This file holds default setting values for the uicore. Similar file should be
    done in the gameroot to assing default settings for the game. This is done to prevent 
    different defaultvalues in various classes where the setting is being used.

    If you think the setting you are working with doesn't require registered 
    default value then do;

    myval = settings.sectionName.groupName.Get(settingKey, myDefaultValue)

    (c) CCP 2008

"""
import util
default = {'user': {'ui': {'language': 0}},
 'public': {'device': {'ditherbackbuffer': 1}},
 'char': {}}

def GetSettings():
    ret = {}
    for sectionk, sectionv in default.iteritems():
        for groupk, groupv in sectionv.iteritems():
            for settingk, settingv in groupv.iteritems():
                ret['defaultsetting.%s.%s.%s' % (sectionk, groupk, settingk)] = settingv

    return ret


exports = GetSettings()