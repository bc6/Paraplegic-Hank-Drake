#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveEdit_Parser.py
import parser

class ParserBase(parser.ParserBaseCore):
    __guid__ = 'parser.ParserBase'
    IMAGE_TYPES = {'icon',
     'corplogo',
     'typeicon',
     'factionlogo',
     'portrait',
     'starmap',
     'alliancelogo',
     'racelogo',
     'reward'}

    def OnStart_eve(self, attrs):
        what = getattr(attrs, 'type', None).strip().lower()
        if not what:
            return
        if what == 'charname' and eve.session.charid:
            self.AddTextToBuffer(cfg.eveowners.Get(eve.session.charid).name, fromW='eve')
        elif what == 'corpname' and eve.session.corpid:
            self.AddTextToBuffer(cfg.eveowners.Get(eve.session.corpid).name, fromW='eve')
        elif what == 'alliancename' and eve.session.allianceid:
            self.AddTextToBuffer(cfg.eveowners.Get(eve.session.allianceid).name, fromW='eve')
        elif what == 'solarsystemname' and (eve.session.solarsystemid or eve.session.solarsystemid2):
            self.AddTextToBuffer(cfg.evelocations.Get(eve.session.solarsystemid or eve.session.solarsystemid2).name, fromW='eve')
        elif what == 'constellationname' and eve.session.constellationid:
            self.AddTextToBuffer(cfg.evelocations.Get(eve.session.constellationid).name, fromW='eve')
        elif what == 'regionname' and eve.session.regionid:
            self.AddTextToBuffer(cfg.evelocations.Get(eve.session.regionid).name, fromW='eve')
        elif what == 'stationname' and eve.session.stationid:
            self.AddTextToBuffer(cfg.evelocations.Get(eve.session.stationid).name, fromW='eve')

    def OnStart_img_Game(self, attrs):
        imgType = attrs.src.split(':', 1)[0]
        if imgType in self.IMAGE_TYPES:
            tWidth = tHeight = int(getattr(attrs, 'size', 64))
            texture = None
            return (texture, tWidth, tHeight)

    def CheckForMailAddress(self, attrs):
        if hasattr(attrs, 'href') and attrs.href and attrs.href.startswith('evemail') and (hasattr(attrs, 'subject') or hasattr(attrs, 'message')) and attrs.href.count('::') < 2:
            attrs.href += '::' + getattr(attrs, 'subject', '') + '::' + getattr(attrs, 'message', '')
            attrs.href = attrs.href