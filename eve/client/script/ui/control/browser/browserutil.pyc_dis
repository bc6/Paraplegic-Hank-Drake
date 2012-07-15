#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/browser/browserutil.py
import corebrowserutil
import uiutil
import util
import urlparse
import service
import uicls
import uiconst
import log

def DefaultHomepage():
    hp = 'http://www.eveonline.com/mb2/news.asp'
    if boot.region == 'optic':
        hp = 'http://eve.tiancity.com/client/news.html'
    if eve.session.role & service.ROLE_PLAYER:
        newhp = sm.GetService('sites').GetDefaultHomePage()
        if newhp is not None and newhp != '':
            hp = newhp
    return hp


def GetFixedURL(parent, url):
    browser = uiutil.GetBrowser(parent)
    currentURL = None
    if browser and hasattr(browser.sr, 'currentURL'):
        currentURL = browser.sr.currentURL
    return urlparse.urljoin(currentURL, url)


def SanitizedTypeID(typeID):
    try:
        typeID = int(typeID)
    except:
        log.LogError('Unable to convert typeID into an integer!')
        return

    if typeID is None:
        return
    typeObj = cfg.invtypes.GetIfExists(typeID)
    if typeObj is None:
        return
    return typeID


def SanitizedItemID(itemID):
    try:
        itemID = int(itemID)
    except:
        log.LogError('Unable to convert itemID into an integer!')
        return None

    return itemID


def SanitizedDestinationID(destinationID):
    try:
        destinationID = int(destinationID)
    except:
        log.LogError('Unable to convert destinationID into an integer!')
        return None

    if util.IsSolarSystem(destinationID) or util.IsStation(destinationID):
        return destinationID


def SanitizedSolarsystemID(solarsystemID):
    try:
        solarsystemID = int(solarsystemID)
    except:
        log.LogError('Unable to convert solarsystemID into an integer!')
        return None

    if not util.IsSolarSystem(solarsystemID):
        return None
    return solarsystemID


exports = {'browserutil.DefaultHomepage': DefaultHomepage,
 'browserutil.GetFixedURL': GetFixedURL,
 'browserutil.SanitizedTypeID': SanitizedTypeID,
 'browserutil.SanitizedItemID': SanitizedItemID,
 'browserutil.SanitizedSolarsystemID': SanitizedSolarsystemID,
 'browserutil.SanitizedDestinationID': SanitizedDestinationID}