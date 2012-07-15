#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/net/httpSettings.py
import blue
import os
ORIGINAL_TEMPLATES = ['script:/wwwroot/assets/views', 'script:/wwwroot/assets/views/old']

def ResolveUrl(scriptUrl):
    path = blue.paths.ResolvePathForWriting(scriptUrl)
    if '\\eve\\' in path and not os.path.isdir(path):
        path = path.replace('\\eve\\', '\\carbon\\')
    return path


TEMPLATES_DIR = [ ResolveUrl(p) for p in ORIGINAL_TEMPLATES ]
exports = {'httpSettings.TEMPLATES_DIR': TEMPLATES_DIR}