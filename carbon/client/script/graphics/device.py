import trinity
import __builtin__

def SetEnvMipLevelSkipCount():
    trinity.device.mipLevelSkipCount = 0



def SetCharMipLevelSkipCount():
    trinity.device.mipLevelSkipCount = 0


exports = {'device.SetEnvMipLevelSkipCount': SetEnvMipLevelSkipCount,
 'device.SetCharMipLevelSkipCount': SetCharMipLevelSkipCount}

