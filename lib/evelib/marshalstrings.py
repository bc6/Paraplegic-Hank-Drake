import blue
oldTables = None

def DoIt():
    global oldTables
    strings = [ intern(eval(i)) for i in rawstrings.splitlines() if i ]
    smap = {}
    for (n, s,) in enumerate(strings):
        n += 1
        if n > 255:
            raise RuntimeError('Invalid n', n)
        smap[s] = n

    oldTables = SwapTables((smap, strings))
    SwapTables(oldTables)



def SwapTables(n):
    a = dict(blue.marshal.stringTable)
    b = blue.marshal.stringTableRev[:]
    if n:
        blue.marshal.stringTable.clear()
        blue.marshal.stringTable.update(n[0])
        blue.marshal.stringTableRev[:] = n[1]
    return (a, b)



def LoadOld(s):
    return blue.marshal.Load(s, stringTable=oldTables[1])



def SaveNotable(o):
    return blue.marshal.Save(o, stringMap={})


rawstrings = "\n'*fleetid'\n'*multicastID'\n'*solarsystemid&corpid'\n'*stationid&corpid'\n'*stationid&corpid&corprole'\n'+clientID'\n'1 minute'\n'AccessControl'\n'CacheOK'\n'DoDestinyUpdate'\n'EN'\n'EVE-EVE-RELEASE'\n'GetCachableObject'\n'GetExpiryDate'\n'GetLocationsEx'\n'GetNewPriceHistory'\n'GetOldPriceHistory'\n'GetOrders'\n'HANDSHAKE_INCOMPATIBLEREGION'\n'InvalidateCachedObjects'\n'JoinChannel'\n'LSC'\n'LeaveChannel'\n'MarketRegion'\n'Method Call'\n'OID-'\n'OnAccountChange'\n'OnAgentMissionChange'\n'OnAggressionChange'\n'OnCfgDataChanged'\n'OnCharNoLongerInStation'\n'OnCharNowInStation'\n'OnContactLoggedOn'\n'OnCorporationMemberChanged'\n'OnCorporationVoteCaseOptionChanged'\n'OnDockingAccepted'\n'OnFleetActive'\n'OnFleetJoin'\n'OnFleetLeave'\n'OnFleetMemberChanged'\n'OnFleetStateChange'\n'OnItemsChanged'\n'OnJumpQueueUpdate'\n'OnLSC'\n'OnMachoObjectDisconnect'\n'OnMessage'\n'OnMultiEvent'\n'OnNotifyPreload'\n'OnOwnOrderChanged'\n'OnProbeStateChanged'\n'OnProbeWarpEnd'\n'OnProbeWarpStart'\n'OnRemoteMessage'\n'OnSquadActive'\n'OnStandingsModified'\n'OnSystemScanStarted'\n'OnSystemScanStopped'\n'OnTarget'\n'PlaceCharOrder'\n'ProcessGodmaPrimeLocation'\n'SendMessage'\n'__MultiEvent'\n'account'\n'address'\n'allianceid'\n'authentication'\n'autodepth_stencilformat'\n'avgPrice'\n'baseID'\n'beyonce'\n'bid'\n'bloodlineID'\n'boot_build'\n'boot_codename'\n'boot_region'\n'boot_version'\n'build'\n'ccp'\n'challenge_responsehash'\n'channel'\n'character'\n'charid'\n'charmgr'\n'clientID'\n'clock'\n'codename'\n'columns'\n'compressedPart'\n'config'\n'config.Attributes'\n'config.Bloodlines'\n'config.BulkData.allianceshortnames'\n'config.BulkData.billtypes'\n'config.BulkData.bptypes'\n'config.BulkData.categories'\n'config.BulkData.certificaterelationships'\n'config.BulkData.certificates'\n'config.BulkData.dgmattribs'\n'config.BulkData.dgmeffects'\n'config.BulkData.dgmtypeattribs'\n'config.BulkData.dgmtypeeffects'\n'config.BulkData.graphics'\n'config.BulkData.groups'\n'config.BulkData.invmetatypes'\n'config.BulkData.invtypereactions'\n'config.BulkData.locations'\n'config.BulkData.locationwormholeclasses'\n'config.BulkData.mapcelestialdescriptions'\n'config.BulkData.metagroups'\n'config.BulkData.owners'\n'config.BulkData.ramactivities'\n'config.BulkData.ramaltypes'\n'config.BulkData.ramaltypesdetailpercategory'\n'config.BulkData.ramaltypesdetailpergroup'\n'config.BulkData.ramcompletedstatuses'\n'config.BulkData.invtypematerials'\n'config.BulkData.ramtyperequirements'\n'config.BulkData.shiptypes'\n'config.BulkData.tickernames'\n'config.BulkData.types'\n'config.BulkData.units'\n'config.Flags'\n'config.InvContrabandTypes'\n'config.Races'\n'config.StaticLocations'\n'config.StaticOwners'\n'config.Units'\n'constellationid'\n'contractMgr'\n'corpAccountKey'\n'corpRegistry'\n'corpStationMgr'\n'corpid'\n'corporationSvc'\n'corprole'\n'crypting_securityprovidertype'\n'crypting_sessionkeylength'\n'crypting_sessionkeymethod'\n'dogmaIM'\n'duration'\n'entity'\n'explosioneffectssenabled'\n'facWarMgr'\n'fittingMgr'\n'fullscreen_resolution'\n'fleetSvc'\n'fleetObjectHandler'\n'fleetbooster'\n'fleetid'\n'fleetrole'\n'genderID'\n'handshakefunc_output'\n'handshakefunc_result'\n'header'\n'highPrice'\n'historyDate'\n'hqID'\n'inDetention'\n'invbroker'\n'issued'\n'jit'\n'jumps'\n'languageID'\n'locationid'\n'loggedOnUserCount'\n'lowPrice'\n'macho.CallReq'\n'macho.CallRsp'\n'macho.ErrorResponse'\n'macho.MachoAddress'\n'macho.Notification'\n'macho.PingReq'\n'macho.PingRsp'\n'macho.SessionChangeNotification'\n'macho.SessionInitialStateNotification'\n'machoNet'\n'machoNet.serviceInfo'\n'machoVersion'\n'macho_version'\n'map'\n'market'\n'marketProxy'\n'maxSessionTime'\n'minVolume'\n'network_computername'\n'objectCaching'\n'objectCaching.CachedMethodCallResult'\n'objectCaching.CachedObject'\n'orderID'\n'orders'\n'origin'\n'pixel_shader_version'\n'presentation_interval'\n'price'\n'processor_architecture'\n'processor_identifier'\n'raceID'\n'range'\n'reason'\n'reasonArgs'\n'reasonCode'\n'region'\n'regionID'\n'regionid'\n'role'\n'rolesAtAll'\n'rolesAtBase'\n'rolesAtHQ'\n'rolesAtOther'\n'scanMgr'\n'sessionInfo'\n'sessionMgr'\n'sessionchange'\n'shipid'\n'sn'\n'solarSystemID'\n'solarsystemid'\n'solarsystemid2'\n'squadid'\n'standing2'\n'station'\n'stationID'\n'stationSvc'\n'stationid'\n'tutorialSvc'\n'typeID'\n'userType'\n'user_logonqueueposition'\n'userid'\n'utcmidnight'\n'utcmidnight_or_3hours'\n'util.CachedObject'\n'util.KeyVal'\n'util.Rowset'\n'version'\n'versionCheck'\n'vertex_shader_version'\n'volEntered'\n'volRemaining'\n'volume'\n'warRegistry'\n'warfactionid'\n'wingid'\n"
DoIt()
del DoIt
del rawstrings

