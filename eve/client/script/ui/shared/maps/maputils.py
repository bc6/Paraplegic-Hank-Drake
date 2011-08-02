import util
import uiutil
import types
import trinity

def GetValidSolarsystemGroups():
    return [const.groupSun,
     const.groupScannerProbe,
     const.groupPlanet,
     const.groupMoon,
     const.groupStation,
     const.groupAsteroidBelt,
     const.groupBeacon,
     const.groupStargate,
     const.groupSovereigntyClaimMarkers,
     const.groupSovereigntyDisruptionStructures,
     'bookmark',
     'scanresult']



def GetVisibleSolarsystemBrackets():
    return settings.user.ui.Get('groupsInSolarsystemMap', GetValidSolarsystemGroups())



def GetHintsOnSolarsystemBrackets():
    return settings.user.ui.Get('hintsInSolarsystemMap', [const.groupStation])



def GetMyPos():
    import trinity
    bp = sm.GetService('michelle').GetBallpark()
    if bp and bp.ego:
        ego = bp.balls[bp.ego]
        myPos = trinity.TriVector(ego.x, ego.y, ego.z)
    elif eve.session.stationid:
        s = sm.RemoteSvc('stationSvc').GetStation(eve.session.stationid)
        myPos = trinity.TriVector(s.x, s.y, s.z)
    else:
        myPos = trinity.TriVector()
    return myPos



def GetDistance(slimItem = None, mapData = None, ball = None, transform = None):
    if ball:
        return ball.surfaceDist
    if slimItem:
        ballPark = sm.GetService('michelle').GetBallpark()
        if ballPark and slimItem.itemID in ballPark.balls:
            return ballPark.balls[slimItem.itemID].surfaceDist
    myPos = GetMyPos()
    if mapData:
        pos = trinity.TriVector(mapData.x, mapData.y, mapData.z)
    elif transform:
        pos = transform.translation
        if type(pos) == types.TupleType:
            pos = trinity.TriVector(*pos)
    else:
        return None
    return (pos - myPos).Length()



def GetTranslatedViewLevels():
    return {'inflight': mls.UI_CMD_INFLIGHT,
     'systemmap': mls.UI_GENERIC_SOLARSYSTEMMAP,
     'starmap': mls.UI_GENERIC_STARMAP}



def CollapseBubbles(ignore = []):
    bracketWnd = uicore.layer.systemmap
    for bracket in bracketWnd.children[:]:
        if getattr(bracket, 'IsBracket', 0) and getattr(bracket.sr, 'bubble', None) is not None:
            if bracket in ignore:
                continue
            bracket.sr.bubble.ClearSubs()
            _ExpandBubbleHint(bracket.sr.bubble, 0)

    self.expandingHint = 0



def _ExpandBubbleHint(self, bubble, expand = 1):
    bracket = bubble.parent
    if not bracket:
        return 
    if not expand and util.GetAttrs(bubble, 'sr', 'CollapseCleanup'):
        force = bubble.sr.CollapseCleanup(bracket)
    else:
        force = False
    if bubble.destroyed:
        return 
    if not force and expand == bubble.expanded:
        return 
    if expand:
        uiutil.SetOrder(bracket, 0)
        blue.pyos.synchro.Yield()
        CollapseBubbles([bracket])
    elif bracket.name == '__fleetbracket' and len(bracket.collapsedHint) == 1:
        done = False
        if 'fleetmate' not in GetHintsOnSolarsystemBrackets():
            bubble.Close()
            bracket.sr.bubble = None
            done = True
        if 'fleetmate' not in GetVisibleSolarsystemBrackets():
            bracket.Close()
            util.TryDel(self.fleetBrackets, bracket.locationID)
            done = True
        if done:
            return 
    self.expandingHint = id(bracket)
    hint = self.GetBubbleHint(bracket.itemID, getattr(bracket, 'slimItem', None), bracket=bracket, extended=expand)
    if bubble.destroyed:
        return 
    (currentHint, pointer,) = bubble.data
    if hint != currentHint:
        bubble.ShowHint(hint, pointer)
    bubble.expanded = expand
    self.expandingHint = 0



def SortBubbles(self, ignore = []):
    last = getattr(self, 'lastBubbleSort', None)
    if last and blue.os.TimeDiffInMs(last) < 500:
        return 
    bracketWnd = self.GetBracketWindow()
    order = []
    for bracket in bracketWnd.children:
        if getattr(bracket, 'IsBracket', 0) and getattr(bracket, 'trackTransform', None) is not None and getattr(bracket.sr, 'bubble', None) is not None:
            order.append((bracket.trackTransform.cameraDistSq, bracket))

    order = uiutil.SortListOfTuples(order)
    order.reverse()
    for bracket in order:
        uiutil.SetOrder(bracket, 0)

    self.lastBubbleSort = blue.os.GetTime()
    self.UpdateBrackets()


exports = util.AutoExports('maputils', locals())

