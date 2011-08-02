
def SlimItemFromCharID(charID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        for item in bp.slimItems.values():
            if item.charID == charID:
                return item




def InBubble(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        return itemID in bp.balls
    else:
        return False


import util
exports = util.AutoExports('util', globals())

