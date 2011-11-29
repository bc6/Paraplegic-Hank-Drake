import htmlwriter
import util
import re
import blue
import sys
import macho
import notificationUtil
import time
import os
import localization
try:
    import logConst
except:
    logConst = util.KeyVal()
from service import ROLEMASK_VIEW, ROLE_ADMIN, ROLE_CONTENT, ROLE_GML, ROLE_GMH, ROLE_PROGRAMMER, ROLE_PETITIONEE

class ESPHtmlWriter(htmlwriter.SPHtmlWriter):
    __guid__ = 'htmlwriter.ESPHtmlWriter'

    def SelectCharacter(self):
        if session.charid is None:
            urlparameters = ''
            for q in self.request.query.iteritems():
                if q[0] is not '':
                    urlparameters += '%s=%s&' % q

            session.redirecturl = self.request.path + '?' + urlparameters
            self.response.Redirect('/gm/character.py?action=MyCharacters&')



    def AppBottomLeft(self):
        s = htmlwriter.SPHtmlWriter.AppBottomLeft(self)
        if macho.mode == 'server':
            if session.charid:
                s += ' - <a href="/gm/character.py?action=LogOffCharacter&"><font color=SILVER>Logoff</font></a>'
        return s


    if macho.mode == 'server':

        def GetOperationText(self, operationID, isDescription = False):
            if operationID not in self.cache.Index(const.cacheStaOperations):
                return ''
            if isDescription:
                return localization.GetByMessageID(self.cache.Index(const.cacheStaOperations, operationID).descriptionID)
            return localization.GetByMessageID(self.cache.Index(const.cacheStaOperations, operationID).operationNameID)



        def GetRoleDescription(self, roleID, isShort = False):
            if roleID not in self.cache.Index(const.cacheCrpRoles):
                return ''
            if isShort:
                return localization.GetByMessageID(self.cache.Index(const.cacheCrpRoles, roleID).shortDescriptionID)
            return localization.GetByMessageID(self.cache.Index(const.cacheCrpRoles, roleID).descriptionID)



        def GetCelestialDescription(self, itemID):
            if itemID in self.cache.Index(const.cacheMapCelestialDescriptions):
                return localization.GetByMessageID(self.cache.Index(const.cacheMapCelestialDescriptions, itemID).descriptionID)
            else:
                return ''



        def GetCorpActivityName(self, activityID):
            if activityID in self.cache.Index(const.cacheCrpActivities):
                return ''
            return localization.GetByMessageID(self.cache.Index(const.cacheCrpActivities, activityID).activityNameID)



        def MetaGroupLink(self, metaGroupID, linkText = None, props = ''):
            if metaGroupID is None:
                return ''
            else:
                if linkText is None:
                    linkText = cfg.invmetagroups.Get(metaGroupID).metaGroupName
                    if linkText is None:
                        return self.FontRed('Unknown')
                return self.Link('/gd/type.py', linkText, {'action': 'MetaGroups'}, props)



        def OwnerLink(self, ownerID, ownerTypeID = None, linkText = None, props = ''):
            if ownerID is None:
                return ''
            else:
                if ownerTypeID is None:
                    try:
                        owner = cfg.eveowners.Get(ownerID)
                    except:
                        sys.exc_clear()
                        if linkText is None:
                            return self.FontRed('???')
                        else:
                            return linkText
                    ownerTypeID = owner.typeID
                    if not linkText:
                        linkText = owner.ownerName
                if linkText is not None:
                    linkText = self.HTMLEncode(linkText)
                if ownerTypeID == const.typeFaction:
                    return self.FactionLink(ownerID, linkText, props)
                if ownerTypeID == const.typeCorporation:
                    return self.CorporationLink(ownerID, linkText, props)
                if ownerTypeID == const.typeAlliance:
                    return self.AllianceLink(ownerID, linkText, props)
                if ownerTypeID == const.typeSystem:
                    return linkText
                return self.CharacterLink(ownerID, linkText, props)



        def LocationLink(self, locationID, linkText = None, props = ''):
            if locationID is None:
                return ''
            else:
                if linkText is None:
                    if locationID < 70000000 or locationID > 80000000:
                        try:
                            location = cfg.evelocations.Get(locationID)
                        except:
                            sys.exc_clear()
                            return self.FontRed('???')
                        linkText = location.locationName
                if linkText is not None:
                    linkText = self.HTMLEncode(linkText)
                if locationID < const.minRegion:
                    return linkText
                if locationID < const.minConstellation:
                    return self.RegionLink(locationID, linkText, props)
                if locationID < const.minSolarSystem:
                    return self.ConstellationLink(locationID, linkText, props)
                if locationID < const.minUniverseCelestial:
                    return self.SystemLink(locationID, linkText, props)
                if locationID < const.minStation:
                    return linkText
                if locationID < const.minUniverseAsteroid:
                    return self.StationLink(locationID, linkText, props)
                return linkText



        def CharacterLink(self, characterID, linkText = None, props = '', noHover = False):
            if util.IsDustCharacter(characterID):
                return htmlwriter.SPHtmlWriter.CharacterLink(self, characterID, linkText, props)
            if characterID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(characterID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/character.py?action=Character&characterID=%s' % characterID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=1' % characterID, title=linkText, caption=linkText)



        def CharacterLinkActions(self, characterID, linkText = None, actions = []):
            if characterID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(characterID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltipActions(href='/gm/character.py?action=Character&characterID=%s' % characterID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=1' % characterID, title=linkText, caption=linkText, actions=actions)



        def PetitionLink(self, petID, linkText = None, props = ''):
            if petID is None:
                return ''
            else:
                if linkText is None:
                    linkText = 'petition'
                if linkText is not None:
                    linkText = self.HTMLEncode(linkText)
                return self.Link('/gm/petitionClient.py', linkText, {'action': 'ViewPetition',
                 'petitionID': petID}, props)



        def CorporationLink(self, corporationID, linkText = None, props = ''):
            if corporationID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(corporationID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/corporation.py?action=Corporation&corporationID=%s' % corporationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=3' % corporationID, title=linkText, caption=linkText)



        def AllianceLink(self, allianceID, linkText = None, props = ''):
            if allianceID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(allianceID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/alliance.py?action=Alliance&allianceID=%s' % allianceID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=9' % allianceID, title=linkText, caption=linkText)



        def WarableEntityLink(self, ownerID, linkText = None, props = ''):
            if ownerID is None:
                return ''
            else:
                if linkText is None:
                    linkText = self.OwnerName(ownerID)
                    if linkText is None:
                        return self.FontRed('Unknown')
                if linkText is not None:
                    linkText = self.HTMLEncode(linkText)
                return self.Link('/gm/war.py', linkText, {'action': 'WarableEntity',
                 'ownerID': ownerID}, props)



        def FactionLink(self, factionID, linkText = None, props = ''):
            if factionID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(factionID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/faction.py?action=Faction&factionID=%s' % factionID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=8' % factionID, title=linkText, caption=linkText)



        def StationLink(self, stationID, linkText = None, props = ''):
            if stationID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(stationID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/stations.py?action=Station&stationID=%s' % stationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=7' % stationID, title=linkText, caption=linkText)



        def WorldSpaceLink(self, worldSpaceID, linkText = None, props = ''):
            if worldSpaceID is None:
                return ''
            else:
                if linkText is None:
                    linkText = self.LocationName(worldSpaceID)
                    if linkText is None:
                        return self.FontRed('Unknown')
                if linkText is not None:
                    linkText = self.HTMLEncode(linkText)
                return self.Link('/gm/worldSpaces.py', linkText, {'action': 'WorldSpace',
                 'worldspaceID': worldSpaceID}, props)



        def SystemLink(self, systemID, linkText = None, props = ''):
            if systemID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(systemID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gd/universe.py?action=System&systemID=%s' % systemID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=4' % systemID, title=linkText, caption=linkText)



        def ConstellationLink(self, constellationID, linkText = None, props = ''):
            if constellationID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(constellationID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gd/universe.py?action=Constellation&constellationID=%s' % constellationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=6' % constellationID, title=linkText, caption=linkText)



        def RegionLink(self, regionID, linkText = None, props = ''):
            if regionID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(regionID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gd/universe.py?action=Region&regionID=%s' % regionID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=5' % regionID, title=linkText, caption=linkText)



        def PlanetLink(self, planetID, linkText = None, props = ''):
            if planetID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(planetID)
                if linkText is None:
                    return self.GetSpan(['Unknown'], className='red')
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.GetTooltip(href='/gm/planets.py?action=ViewPlanet&planetID=%s' % planetID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=10' % planetID, title=linkText, caption=linkText)



        def CombatZoneLink(self, combatZoneID, linkText):
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            if combatZoneID is None:
                return ''
            else:
                return self.Link('/gd/combatZones.py', linkText, {'action': 'Zone',
                 'zoneID': combatZoneID}, '')



        def MapLink(self, itemID, linkText = 'Map', props = ''):
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            if itemID is None:
                return ''
            else:
                return self.Link('/gd/universe.py', linkText, {'action': 'Map',
                 'itemID': itemID}, props)



        def RewardLink(self, rewardID, linkText = None, props = ''):
            if linkText is None:
                row = self.DB2.SQLInt('name', 'reward.rewards', '', '', 'rewardID', rewardID)
                if len(row) == 0:
                    return 'Deleted reward'
                linkText = row.name
            if linkText is not None:
                linkText = self.HTMLEncode(linkText)
            return self.Link('/gd/rewards.py', linkText, {'action': 'ViewReward',
             'rewardID': rewardID}, props)



        def PinLink(self, pinID, linkText = None, props = ''):
            pinName = linkText
            if pinName is None:
                pinRow = self.DB2.SQLBigInt('typeID', 'planet.pins', '', '', 'pinID', pinID)
                if len(pinRow) == 0:
                    return 'Deleted pin'
                pinName = cfg.invtypes.Get(pinRow[0].typeID).name
            if pinName is not None:
                pinName = self.HTMLEncode(pinName)
            return self.Link('/gm/planets.py', pinName, {'action': 'ViewPin',
             'pinID': pinID}, props)



        def PinTypeLink(self, pinID, linkText = None, props = ''):
            pinRow = self.DB2.SQLBigInt('typeID', 'planet.pins', '', '', 'pinID', pinID)[0]
            pinTypeID = pinRow.typeID
            pinName = linkText
            if pinName is None:
                pinName = cfg.invtypes.Get(pinRow.typeID).name
            if pinName is not None:
                pinName = self.HTMLEncode(pinName)
            return self.TypeLink(pinTypeID, linkText=pinName, props=props)



        def SchematicLink(self, schematicID, linkText = None, props = ''):
            schematicName = linkText
            if schematicName is None:
                schematicName = cfg.schematics.Get(schematicID).schematicName
            if schematicName is not None:
                schematicName = self.HTMLEncode(schematicName)
            return self.Link('/gd/schematics.py', schematicName, {'action': 'View',
             'schematicID': schematicID})



        def RecipeLink(self, parentID, parentType, text = None):
            if text is None:
                text = self.HTMLEncode(text)
                if parentType == const.cef.PARENT_TYPEID:
                    text = cfg.invtypes.Get(parentID).typeName
                elif parentType == const.cef.PARENT_GROUPID:
                    text = cfg.invgroups.Get(parentID).groupName
                text = cfg.invcategories.Get(parentID).categoryName
            if text is not None:
                text = self.HTMLEncode(text)
            return self.Link('/gd/entities.py', text, {'action': 'Recipe',
             'parentID': parentID,
             'parentType': parentType})



        def ComboRaces(self, allowNone = 0):
            combo = {}
            if allowNone:
                combo[0] = '(none)'
            for r in cfg.races:
                combo[r.raceID] = r.raceName

            return combo



        def ComboBloodlines(self, allowNone = 0):
            combo = {}
            if allowNone:
                combo[0] = '(none)'
            for b in self.cache.Rowset(const.cacheChrBloodlines):
                r = cfg.races.Get(b.raceID)
                combo[b.bloodlineID] = '%i, %s' % (r.raceNameID, localization.GetByMessageID(b.bloodlineNameID))

            return combo



        def SelectCategory(self, action, categoryID, placement = 'rMenu'):
            categories = []
            for c in cfg.invcategories:
                if c.categoryID > 0:
                    bon = ''
                    boff = ''
                    if c.categoryID == categoryID:
                        bon = '<b>'
                        boff = '</b>'
                    categories.append([c.categoryName, bon + self.Link('', c.categoryName, {'action': action,
                      'categoryID': c.categoryID}) + boff])

            categories.sort()
            categories = map(lambda line: line[1:], categories)
            if categoryID is None:
                self.Write(self.WebPart('Categories', self.GetTable([], categories), 'wpCategories'))
                return 0
            else:
                self.WriteDirect(placement, self.WebPart('Categories', self.GetTable([], categories), 'wpCategories'))
                return 1



        def SelectCategoryGroup(self, action, categoryID, groupID, placement = 'rMenu', webPart = None):
            if categoryID is None and groupID is not None:
                categoryID = cfg.invgroups.Get(groupID).categoryID
            categories = []
            for c in cfg.invcategories:
                if c.categoryID > 0:
                    bon = ''
                    boff = ''
                    if c.categoryID == categoryID:
                        bon = '<b>'
                        boff = '</b>'
                    categories.append([c.categoryName, bon + self.Link('', c.categoryName, {'action': action,
                      'categoryID': c.categoryID}) + boff])

            categories.sort()
            categories = map(lambda line: line[1:], categories)
            if categoryID is None:
                self.Write(self.WebPart('Categories', self.GetTable([], categories), 'wpCategories'))
                return 0
            else:
                groups = []
                for g in cfg.groupsByCategories.get(categoryID, []):
                    bon = ''
                    boff = ''
                    if g.groupID == groupID:
                        bon = '<b>'
                        boff = '</b>'
                    groups.append([g.groupName, bon + self.Link('', g.groupName, {'action': action,
                      'categoryID': categoryID,
                      'groupID': g.groupID}) + boff])

                groups.sort()
                groups = map(lambda line: line[1:], groups)
                if groupID is None:
                    self.Write(self.WebPart('Groups', self.GetTable([], groups), 'wpGroups'))
                    self.WriteDirect(placement, self.WebPart('Categories', self.GetTable([], categories), 'wpCategories'))
                    return 0
                if webPart:
                    self.WriteDirect(placement, webPart)
                self.WriteDirect(placement, self.WebPart('Groups', self.GetTable([], groups), 'wpGroups'))
                self.WriteDirect(placement, self.WebPart('Categories', self.GetTable([], categories), 'wpCategories'))
                return 1



        def SelectCategoryGroupType(self, action, categoryID, groupID, placement = 'rMenu'):
            if self.SelectCategoryGroup(action, categoryID, groupID, placement):
                li = []
                for t in cfg.typesByGroups.get(groupID, []):
                    li.append([t.typeID, self.Link('', t.typeName, {'action': action,
                      'categoryID': categoryID,
                      'groupID': groupID,
                      'typeID': t.typeID})])

                self.LinesSortByLink(li, 1)
                self.Write(self.WebPart('Types', self.GetTable(['id', 'name'], li), 'wpTypes'))



        def SelectRegion(self, action, regionID):
            li = []
            for r in self.DB2.SQL('SELECT * FROM map.regionsDx ORDER BY regionName'):
                bon = ''
                boff = ''
                if r.regionID == regionID:
                    bon = '<b>'
                    boff = '</b>'
                li.append([bon + self.Link('', self.IsBlank(r.regionName, r.regionID), {'action': action,
                  'regionID': r.regionID}) + boff])

            regSel = self.GetTable([], li)
            if regionID is None:
                self.Write(self.WebPart('Select Region', regSel, 'wpRegSel'))
                return 0
            else:
                self.WriteDirect('rMenu', self.WebPart('Regions', regSel, 'wpRegSel'))
                return 1



        def SelectRegionConstellation(self, action, regionID, constellationID):
            if self.SelectRegion(action, regionID):
                li = []
                for c in self.DB2.SQLInt('constellationID, constellationName', 'map.constellationsDx', '', 'constellationName', 'regionID', regionID):
                    bon = ''
                    boff = ''
                    if c.constellationID == constellationID:
                        bon = '<b>'
                        boff = '</b>'
                    li.append([bon + self.Link('', self.IsBlank(c.constellationName, c.constellationID), {'action': action,
                      'regionID': regionID,
                      'constellationID': c.constellationID}) + boff])

                conSel = self.GetTable([], li)
                if constellationID is None:
                    self.Write(self.WebPart('Select Constellation', conSel, 'wpConSel'))
                    return 0
                else:
                    self.WriteDirect('rMenu', self.WebPart('Constellations', conSel, 'wpConSel'))
                    return 1



        def SelectRegionConstellationSolarSystem(self, action, regionID, constellationID, solarSystemID):
            if self.SelectRegionConstellation(action, regionID, constellationID):
                li = []
                for s in self.DB2.SQLInt('solarSystemID, solarSystemName', 'map.solarSystemsDx', '', 'solarSystemName', 'constellationID', constellationID):
                    bon = ''
                    boff = ''
                    if s.solarSystemID == solarSystemID:
                        bon = '<b>'
                        boff = '</b>'
                    li.append([bon + self.Link('', self.IsBlank(s.solarSystemName, s.solarSystemID), {'action': action,
                      'regionID': regionID,
                      'constellationID': constellationID,
                      'solarSystemID': s.solarSystemID}) + boff])

                solSel = self.GetTable([], li)
                if solarSystemID is None:
                    self.Write(self.WebPart('Select Solar System', solSel, 'wpSolSel'))
                    return 0
                else:
                    self.WriteDirect('rMenu', self.WebPart('Solar Systems', solSel, 'wpSolSel'))
                    return 1



        def AddTableItem(self, lines, r, owner, location, category = 0, checkBox = 0):
            t = cfg.invtypes.Get(r.typeID)
            g = cfg.invgroups.Get(t.groupID)
            c = cfg.invcategories.Get(g.categoryID)
            cgtn = str(r.typeID) + ': '
            if category:
                if c.categoryName != g.groupName:
                    cgtn += c.categoryName + ', '
            if g.groupName == t.typeName:
                cgtn += self.TypeLink(r.typeID, t.typeName)
            else:
                cgtn += g.groupName + ', ' + self.TypeLink(r.typeID, t.typeName)
            itemName = self.cache.EspItemName(0, r.itemID, r.quantity, r.typeID, t.groupID, g.categoryID)
            if itemName != '':
                cgtn += ': <b>' + itemName + '</b>'
            attr = ''
            if r.quantity < 0:
                attr += ' S'
                if r.quantity != -1:
                    attr += self.FontRed(r.quantity)
            else:
                attr += ' %d' % r.quantity
            line = []
            if checkBox == 1:
                line.append('<input type="checkbox" name="itemID" value="%s">' % r.itemID + ' ' + self.ItemID(r.itemID))
            else:
                line.append(self.ItemID(r.itemID))
            line.append(cgtn)
            if owner:
                ownerName = self.cache.EspItemName(1, r.ownerID)
                if ownerName == '':
                    line.append(self.ItemID(r.ownerID))
                else:
                    line.append(self.ItemID(r.ownerID) + ': ' + ownerName)
            else:
                line.append('')
            if location:
                locationName = self.cache.EspItemName(2, r.locationID)
                if locationName == '':
                    line.append(self.ItemID(r.locationID))
                else:
                    line.append(self.ItemID(r.locationID) + ': ' + locationName)
            else:
                line.append('')
            line.append('%d: %s' % (r.flagID, self.config.GetFlags(r.flagID).flagName))
            line.append(attr)
            act = ''
            if t.groupID == const.groupCharacter:
                act = self.CharacterLink(r.itemID, 'Character')
            elif t.groupID == const.groupCorporation:
                act = self.CorporationLink(r.itemID, 'Corporation')
            elif t.groupID == const.groupFaction:
                act = self.FactionLink(r.itemID, 'Faction')
            elif t.groupID == const.groupRegion:
                act = self.RegionLink(r.itemID, 'Region')
            elif t.groupID == const.groupConstellation:
                act = self.ConstellationLink(r.itemID, 'Constellation')
            elif t.groupID == const.groupSolarSystem:
                act = self.SystemLink(r.itemID, 'System')
            elif t.groupID == const.groupStation:
                act = self.StationLink(r.itemID, 'Station')
            elif t.groupID == const.groupControlTower:
                act = self.Link('/gm/starbase.py', 'Starbase', {'action': 'Starbase',
                 'towerID': r.itemID})
            elif t.groupID == const.groupPlanet:
                act = self.Link('/gd/universe.py', 'Planet', {'action': 'Celestial',
                 'celestialID': r.itemID})
            elif t.groupID == const.groupAsteroidBelt:
                act = self.Link('/gd/universe.py', 'Belt', {'action': 'AsteroidBelt',
                 'asteroidBeltID': r.itemID})
            line.append(act)
            lines.append(line)



        def AddTypeSelector(self, form, name = '', depth = 'type'):
            self.WriteDirect('jscript', '\n                function replaceOptions(sElement, newOptions){\n                    for (i=document.all[sElement].length; i > -1; i--) {\n                        document.all[sElement].options[i]=null\n                    }\n                    for (i = 0; i < newOptions.length; i += 2){\n                        document.all[sElement].add(new Option( newOptions[i], newOptions[i+1]))\n                    }\n                }\n            ')
            self.WriteDirect('jscript', 'c=new ActiveXObject("Scripting.Dictionary");\n')
            self.WriteDirect('jscript', 'g=new ActiveXObject("Scripting.Dictionary");\n')
            s = htmlwriter.UnicodeMemStream()
            for g in cfg.invgroups:
                self.BeNice()
                if g.groupID not in cfg.typesByGroups:
                    continue
                typesByGroup = cfg.typesByGroups[g.groupID].Copy()
                typesByGroup.Sort('typeName')
                s.Write('g.Add("%d", new Array(' % g.groupID)
                for t in typesByGroup:
                    self.BeNice()
                    typeName = t.typeName.replace('"', "'")
                    typeName = typeName.replace('\n', '')
                    typeName = typeName.replace('\r', '')
                    s.Write('"%s",%d,' % (str(typeName), t.typeID))

                s.Seek(s.pos - 1)
                s.Write('));\n')

            cic = {}
            for c in cfg.invcategories:
                self.BeNice()
                if c.categoryID not in cfg.groupsByCategories:
                    continue
                groupsByCategory = cfg.groupsByCategories[c.categoryID].Copy()
                groupsByCategory.Sort('groupName')
                cic[c.categoryID] = c.name
                s.Write('c.Add("%d", new Array(' % c.categoryID)
                for g in groupsByCategory:
                    self.BeNice()
                    s.Write('"%s",%d,' % (str(g.groupName.replace('"', "'")), g.groupID))

                s.Seek(s.pos - 1)
                s.Write('));\n')

            s.Seek(0)
            self.WriteDirect('jscript', str(s.Read()))
            form.AddSelect(name + 'categoryid', cic, 'Category', None, 0, 'onChange="replaceOptions(\'' + name + "groupid',c(this.options[this.selectedIndex].value)); replaceOptions('" + name + "typeid',g(document.all['" + name + 'groupid\'].options[0].value))"')
            if depth == 'type' or depth == 'group':
                form.AddSelect(name + 'groupid', {}, 'Group', None, 0, 'onChange="replaceOptions(\'' + name + 'typeid\',g(this.options[this.selectedIndex].value))"')
            if depth == 'type':
                form.AddSelect(name + 'typeid', {}, 'Type')



        def UserTag(self, userID, tagTypeID = -1, redir = None):
            s = ''
            if tagTypeID < 0:
                rs = self.DB2.SQLInt('tagTypeID', '[user].espTags', '', '', 'userID', userID)
                if len(rs) == 0:
                    tagTypeID = None
                else:
                    tagTypeID = rs[0].tagTypeID
            if tagTypeID:
                s = 'User tagged as: <font color=orange size=4><b>%s</b></font>' % self.cache.IndexText(const.cacheUserEspTagTypes, tagTypeID)
                if session.role & ROLE_GMH:
                    s += '&nbsp;' * 6
                    s += self.Button('/gm/users.py', 'Remove Tag', {'action': 'RemoveTagFromUser',
                     'userID': userID,
                     'redir': redir}, bolConfirm=1)
            elif session.role & ROLE_GML:
                s = self.Button('/gm/users.py', 'Add Tag', {'action': 'AddTagToUser',
                 'userIDs': userID,
                 'redir': redir})
            if s != '':
                self.WriteRight(s)



        def QuickLinks(self, text):
            pup = re.compile('charid\\((\\d+)\\)', re.IGNORECASE)
            text = pup.sub('<a href=character.py?action=Character&characterID=\\1>\\1</a>', text)
            pup = re.compile('userid\\((\\d+)\\)', re.IGNORECASE)
            text = pup.sub('<a href=users.py?action=User&userID=\\1>\\1</a>', text)
            pup = re.compile('itemid\\((\\d+)\\)', re.IGNORECASE)
            text = pup.sub('<a href=../gm/inventory.py?action=Item&itemID=\\1>\\1</a>', text)
            pup = re.compile('petid\\((\\d+)\\)', re.IGNORECASE)
            text = pup.sub('<a href=petitionClient.py?action=ViewPetition&petitionID=\\1>\\1</a>', text)
            return text



        def GetOwnerImage(self, ownerType, ownerID, width = 128):
            serverLink = sm.GetService('machoNet').GetClientConfigVals().get('imageserverurl')
            if serverLink is None:
                serverLink = 'http://%s.dev.image/' % os.environ.get('USERNAME').replace('.', '_').lower()
            serverLink += '%s/%d_%d.%s'
            if ownerType == 'Character':
                extension = 'jpg'
            else:
                extension = 'png'
            return serverLink % (ownerType,
             ownerID,
             width,
             extension)



    def GetPickerAgent(self, ctrlID, ctrlLabel = None, minLength = 4):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/agentds.py', minLength=minLength)



    def GetPickerType(self, ctrlID, ctrlLabel = None, minLength = 4):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/typeds.py', minLength=minLength)



    def GetPickerCharacter(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/characterds.py', minLength=minLength)



    def GetPickerAffiliate(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/affiliateds.py', minLength=minLength)



    def GetPickerStation(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/stationds.py', minLength=minLength)



    def GetPickerCorporation(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/corporationds.py', minLength=minLength)



    def GetPickerRegion(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/regionds.py', minLength=minLength)



    def GetPickerConstellation(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/constellationds.py', minLength=minLength)



    def GetPickerSolarSystem(self, ctrlID, ctrlLabel = None, minLength = 3):
        if ctrlLabel is not None:
            ctrlLabel = self.HTMLEncode(ctrlLabel)
        return self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy='/ds/solarsystemds.py', minLength=minLength)



if macho.mode == 'server':

    class MlsHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.MlsHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/baseNoRight.html', page = ''):
            ESPHtmlWriter.__init__(self, template, 'MLS', page)




    class GMHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.GMHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/base.html', page = ''):
            ESPHtmlWriter.__init__(self, template, 'GM', page)



        def WriteLeftMenu(self, action):
            pass



        def WriteRightMenu(self):
            pass



        def CategorySelector(self, selectName, selectedCategoryID = None, submitOnChange = False):
            categories = []
            (parents, childs, descriptions,) = self.petitioner.GetCategoryHierarchicalInfo()
            for parentID in parents:
                categories.append([parentID, parents[parentID], True])
                for childID in childs[parentID]:
                    categories.append([childID, childs[parentID][childID], False])


            selectorHTML = '<SELECT NAME="%s"' % selectName
            if submitOnChange:
                selectorHTML += ' ONCHANGE="this.form.submit() '
            selectorHTML += '">' + selectName
            for category in categories:
                categoryID = category[0]
                categoryName = category[1][0]
                categoryIsParent = category[2]
                selectorHTML = selectorHTML + '<OPTION VALUE="%s"' % str(categoryID)
                if categoryID == selectedCategoryID:
                    selectorHTML = selectorHTML + ' SELECTED '
                if categoryIsParent == True:
                    selectorHTML = selectorHTML + '>%s' % unicode(categoryName)
                else:
                    selectorHTML = selectorHTML + '>&nbsp &nbsp %s' % unicode(categoryName)

            return selectorHTML



        def AppCharacterImage(self, coreStatic, appStatic):
            image = self.GetOwnerImage('Character', coreStatic.characterID)
            if image == None:
                image = '/img/bloodline%d%s.jpg' % (appStatic.bloodlineID, ['F', 'M'][coreStatic.gender])
            return image



        def AppUserCharactersInfo(self, coreStatic, appStatic):
            bloodline = cfg.bloodlines.Get(appStatic.bloodlineID)
            bloodlineName = localization.GetByMessageID(bloodline.bloodlineNameID, languageID=prefs.languageID)
            if bloodlineName is None:
                bloodlineName = '[bloodline {} has no nameID set]'.format(appStatic.bloodlineID)
            race = cfg.races.Get(bloodline.raceID)
            raceName = localization.GetByMessageID(race.raceNameID, languageID=prefs.languageID)
            if raceName is None:
                raceName = '[race {} has no nameID set]'.format(bloodline.raceID)
            if coreStatic.online == 0:
                onlineText = ''
            else:
                onlineText = '<br>' + self.FontBold(self.FontGreen('Online'))
            s = raceName + ', ' + bloodlineName + ', ' + ['Female', 'Male'][coreStatic.gender] + onlineText
            if util.IsDustCharacter(coreStatic.characterID):
                return s
            s += '<br>%s<br>%s' % (self.CorporationLink(appStatic.corporationID), self.Link('/gm/corporation.py', 'Member Details', {'action': 'MemberDetails',
              'corporationID': appStatic.corporationID,
              'charid': coreStatic.characterID}))
            if appStatic.transferPrepareDateTime:
                s += '<br><b><font color=purple>TRANSFER INITIATED</b></font>'
            return s



        def AppUserCharactersLocation(self, coreStatic, appStatic):
            if util.IsDustCharacter(coreStatic.characterID):
                return ''
            return self.CharacterLocationText(coreStatic.characterID, appStatic.locationID, appStatic.locationTypeID, appStatic.locationLocationID, appStatic.activeShipID, appStatic.activeShipTypeID)



        def AppUserCharactersAct(self, coreStatic, appStatic):
            if util.IsDustCharacter(coreStatic.characterID):
                return ''
            act = ''
            if coreStatic.userID == session.userid:
                if session.charid is None:
                    solarSystemID = None
                    if util.IsSolarSystem(appStatic.locationLocationID):
                        solarSystemID = appStatic.locationLocationID
                    elif util.IsStation(appStatic.locationLocationID):
                        solarSystemID = sm.StartService('stationSvc').GetStation(appStatic.locationLocationID).solarSystemID
                    if solarSystemID == 30000380:
                        act += '<br><br>' + self.Link('/gm/character.py', 'SELECT', {'action': 'SelectCharacter',
                         'characterID': coreStatic.characterID})
                        if session.role & ROLE_PETITIONEE > 0:
                            act += '<br>' + self.Link('/gm/character.py', 'PETITION', {'action': 'SelectCharacter',
                             'characterID': coreStatic.characterID,
                             'redir': 'p'})
                    else:
                        act += '<br /><span title="Move|By moving character to polaris you can select the character" class="red">Not in Polaris, can\'t select</span>'
                elif session.charid == coreStatic.characterID:
                    act += '<br><br>' + self.Link('/gm/character.py', 'Logoff', {'action': 'LogOffCharacter'})
            return act



        def CharacterHeader(self, characterID, small = 1, menuPlacement = 'rMenu'):
            htmlwriter.SPHtmlWriter.CharacterHeader(self, characterID, small, menuPlacement)
            (coreStatic, appStatic,) = self.cache.CharacterDataset(characterID)
            li = []
            if coreStatic is None:
                li.append('Character not found.  No header menu possible.')
            elif util.IsDustCharacter(characterID):
                self.PopulateDustHeaderLinks(li, characterID, coreStatic, appStatic)
            else:
                self.PopulateEveHeaderLinks(li, characterID, coreStatic, appStatic)
            self.SubjectActions(li, menuPlacement)



        def PopulateDustHeaderLinks(self, li, characterID, coreStatic, appStatic):
            li.append(self.Link('', 'Currency', {'action': 'DustCharacterCurrency',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('', 'Skills', {'action': 'DustSkills',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Extra Skill Points', {'action': 'DustEditExtraSkillPointsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'History', {'action': 'DustSkillHistory',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Grant All Skills', {'action': 'DustGrantAllSkillsForm',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('', 'Inventory', {'action': 'DustInventory',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Modify', {'action': 'DustModifyInventoryForm',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'History', {'action': 'DustInventoryHistory',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('', 'Fitting', {'action': 'DustFittings',
             'characterID': characterID}))
            li.append('-')
            li.append(self.FontGray('Fitting (old)'))
            li.append('>' + self.Link('', 'Character', {'action': 'DustCharacterFittings',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'Vehicles', {'action': 'DustVehicleFittings',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('', 'Lifetime Stats', {'action': 'DataLogLifetimeStats',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Kills', {'action': 'DataLogKillsKiller',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'Deaths', {'action': 'DataLogKillsVictim',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'War Points', {'action': 'DataLogWarPoints',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Team Selects', {'action': 'DataLogTeamSelects',
             'characterID': characterID}) + self.MidDot() + self.Link('', 'MCC Surges', {'action': 'DataLogMccSurges',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Object Destructions', {'action': 'DataLogObjectDestructions',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Objective Hacks', {'action': 'DataLogObjectiveHacks',
             'characterID': characterID}))
            li.append('>' + self.Link('', 'Character Positions', {'action': 'DataLogCharacterPositions',
             'characterID': characterID}))



        def PopulateEveHeaderLinks(self, li, characterID, coreStatic, appStatic):
            eveGateProfileUrl = self.cache.Setting('zcluster', 'CommunityWebsite')
            if eveGateProfileUrl:
                if eveGateProfileUrl[-1] != '/':
                    eveGateProfileUrl += '/'
                li.append(self.Link(eveGateProfileUrl + 'GM/Profile/' + coreStatic.characterName, 'Go to Community Profile Page'))
                li.append('-')
            forumUrl = unicode('https://forums.eveonline.com/default.aspx?g=search&postedby=') + unicode(coreStatic.characterName)
            li.append(self.Link(forumUrl, 'Go to Forum History', {}))
            li.append('-')
            li.append(self.Link('/gm/logs.py', 'Audit Log', {'action': 'AuditLog',
             'logGroup': const.groupCharacter,
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', 'Bookmarks', {'action': 'Bookmarks',
             'characterID': characterID}))
            now = time.gmtime()
            li.append(self.Link('/gm/calendar.py', 'Calendar', {'action': 'FindByOwner',
             'ownerID': characterID,
             'ownerType': const.groupCharacter,
             'fromMonth': 1,
             'fromYear': const.calendarStartYear,
             'toMonth': 1,
             'toYear': now[0] + 1}))
            li.append(self.Link('/gm/clones.py', 'Clones', {'action': 'Clones',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', 'Insurance', {'action': 'Insurance',
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', 'Contacts', {'action': 'Contacts',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append(self.Link('/gm/corporation.py', 'Corp. Member Details', {'action': 'CorpMemberDetailsByCharID',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Destroyed Junk', {'action': 'JunkedItems',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Employment Records', {'action': 'EmploymentRecords',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Epic Mission Arc', {'action': 'DisplayEpicMissionArcStatus',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Give Loot', {'action': 'CharacterLootFormNew',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Goodies and Respeccing', {'action': 'EditGoodiesAndRespeccing',
             'characterID': characterID}))
            li.append(self.Link('/gm/faction.py', 'Militia Stats', {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': characterID}))
            li.append(self.Link('/gm/petition.py', 'Petition', {'action': 'BriefPetitionHistory',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/character.py', 'Create New Petition', {'action': 'CreatePetitionForm',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Punishments', {'action': 'PunishCharacterForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/users.py', 'Ban User', {'action': 'BanUserByCharacterID',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Ranks And Medals', {'action': 'RanksAndMedals',
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', 'Standings', {'action': 'Standings',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append(self.Link('/gm/owner.py', 'LP Report', {'action': 'ShowCorpLPForCharacter',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', 'Accounting', {'action': 'Statement',
             'characterID': characterID,
             'groupID': const.groupCharacter}))
            li.append('>' + self.Link('/gm/accounting.py', 'Cash', {'action': 'Journal',
             'characterID': characterID,
             'keyID': const.accountingKeyCash,
             'entrTypeFilter': None,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/accounting.py', 'Insurance', {'action': 'Journal',
             'characterID': characterID,
             'keyID': 1000,
             'entryTypeFilter': 19,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/owner.py', 'Bills', {'action': 'Bills',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/accounting.py', 'Aruum', {'action': 'Journal',
             'characterID': characterID,
             'keyID': const.accountingKeyAUR,
             'entrTypeFilter': None,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/character.py', 'Credits', {'action': 'CharacterCreditsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/accounting.py', 'Mass Reversal', {'action': 'MassReversal',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', 'Agents', {'action': 'AgentsForm',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', 'Agent Spawnpoints', {'action': 'AgentSpawnpoints',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/certificates.py', 'Certificates', {'action': 'CharacterCertsDisplay',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/certificates.py', 'Give Certificates', {'action': 'GiveCertsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/certificates.py', 'Journal', {'action': 'CharacterCertsJournal',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/contracts.py', 'Contracts', {'action': 'ListForEntity',
             'submit': 1,
             'ownerID': characterID}))
            li.append('>' + self.Link('/gm/contracts.py', 'Issued By', {'action': 'List',
             'submit': 1,
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/contracts.py', 'Issued To', {'action': 'List',
             'submit': 1,
             'acceptedByID': characterID,
             'filtStatus': const.conStatusInProgress}))
            li.append('>' + self.Link('/gm/contracts.py', 'Assigned To', {'action': 'List',
             'submit': 1,
             'assignedToID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', 'Destroyed Ships', {'action': 'ShipsKilled',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', 'Kill Rights', {'action': 'KillRights',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/character.py', 'Kill Report', {'action': 'KillReport',
             'characterID': characterID}))
            li.append('-')
            li.append(self.FontGray('Items'))
            li.append('>' + self.Link('/gm/inventory.py', 'Find Item', {'action': 'FindItem',
             'ownID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', 'System - Items', {'action': 'SystemItems',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/inventory.py', 'Find traded items', {'action': 'FindTradedItems',
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', 'Station - Items', {'action': 'StationItems',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', 'Planetary Launches', {'action': 'PlanataryLaunches',
             'ownID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', 'Movement', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 3}) + self.MidDot() + self.Link('/gm/logs.py', 'Standing', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 6}))
            li.append('>' + self.Link('/gm/logs.py', 'Mission', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 9}) + self.MidDot() + self.Link('/gm/logs.py', 'Damage', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 4}))
            li.append('>' + self.Link('/gm/logs.py', 'Market', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 13}) + self.MidDot() + self.Link('/gm/logs.py', 'Dungeon', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 14}))
            li.append('>' + self.Link('/gm/logs.py', 'Killed!', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': -1}) + self.MidDot() + self.Link('/gm/logs.py', 'Mission!', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': -2}) + self.MidDot() + self.Link('/gm/logs.py', 'Bounty!', {'action': 'BountyLog',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', 'Accessed Others Cargo', {'action': 'CargoAccessLogs',
             'charID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', 'Owned by history', {'action': 'CharacterOwnedBy',
             'charID': characterID}))
            li.append('-')
            li.append(self.FontGray('Notifications'))
            newLine = True
            line = ''
            groupNames = notificationUtil.groupNamePaths.items()
            revNames = [ [localization.GetByLabel(v[1]), v[0]] for v in groupNames ]
            revNames.sort()
            for (label, groupID,) in revNames:
                if newLine:
                    line = '>' + self.Link('/gm/owner.py', label, {'action': 'Notifications',
                     'groupID': groupID,
                     'charID': characterID})
                else:
                    line = line + self.MidDot() + self.Link('/gm/owner.py', label, {'action': 'Notifications',
                     'groupID': groupID,
                     'charID': characterID})
                    li.append(line)
                    line = ''
                newLine = not newLine

            if line != '':
                li.append(line)
            li.append('-')
            li.append(self.FontGray('Market'))
            li.append('>' + self.Link('/gm/owner.py', 'orders', {'action': 'Orders',
             'groupID': const.groupCharacter,
             'ownID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', 'Transactions', {'action': 'Transactions',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('-')
            li.append(self.FontGray('Messages'))
            li.append('>' + self.Link('/gm/owner.py', 'Received', {'action': 'Messages',
             'charID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', 'Sent', {'action': 'SentMessages',
             'charID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', 'Mailing Lists', {'action': 'MailingLists',
             'charID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', 'Move', {'action': 'MoveCharacterForm',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', 'Last Station', {'action': 'MoveCharacter',
             'characterID': characterID,
             'stationID': 0,
             'moveShipIfApplicable': 'on'}) + self.MidDot() + self.Link('/gm/character.py', 'Last System', {'action': 'MoveCharacter',
             'characterID': characterID,
             'solarSystemID': 0,
             'moveShipIfApplicable': 'on'}))
            li.append('-')
            li.append(self.FontGray('Science & Industry'))
            li.append('>' + self.Link('/gm/ram.py', 'Jobs', {'action': 'JobsOwner',
             'ownerID': characterID,
             'groupID': const.groupCharacter}) + self.MidDot() + self.Link('/gm/ram.py', 'Assembly Lines', {'action': 'AssemblyLinesOwner',
             'ownerID': characterID,
             'groupID': const.groupCharacter}))
            li.append('>' + self.Link('/gm/ram.py', 'Give  Blueprint', {'action': 'GiveBlueprint',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/planets.py', 'Planets', {'action': 'PlanetsByOwner',
             'ownerID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', 'Skills', {'action': 'CharacterSkills',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/skilljournal.py', 'Give - Skills', {'action': 'CharacterSkillsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/skilljournal.py', 'Skill Journal', {'action': 'CharacterSkillsJournal',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', 'Training Queue', {'action': 'SkillQueue',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/skilljournal.py', 'Set Free Skill Points', {'action': 'SetFreeSkillPointsForm',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/skilljournal.py', 'Check LSR Logs', {'action': 'LSRLogs',
             'characterID': characterID,
             'ownerType': 1}))
            li.append('>' + self.Link('/gm/skilljournal.py', 'Check Connection SR Logs', {'action': 'ConnectionSRLogs',
             'characterID': characterID,
             'ownerType': 1}))
            li.append('-')
            li.append(self.FontGray('Paper doll'))
            li.append('>' + self.Link('/gm/character.py', 'Flags', {'action': 'PaperdollFlags',
             'characterID': characterID}))
            if prefs.clusterMode != 'LIVE' and session.role & ROLE_CONTENT > 0:
                li.append('>' + self.Link('/gm/character.py', 'Copy paperdoll', {'action': 'PaperdollCharacterCopy',
                 'characterID': characterID}))



        def CorporationHeader(self, corporationID, smallHeader = 1, menuPlacement = 'rMenu'):
            c = self.cache.EspCorporation(corporationID)
            stationSvc = sm.GetService('stationSvc')
            station = stationSvc.GetStation(c.stationID)
            image = self.GetOwnerImage('Corporation', corporationID)
            if image == None:
                image = '/img/corporation'
                if corporationID < const.minPlayerOwner:
                    image += str(corporationID)
                image += '.jpg'
            lines = []
            if corporationID < const.minPlayerOwner:
                nc = self.cache.Index(const.cacheCrpNpcCorporations, corporationID)
                lines.append([1, 'Faction', self.FactionLink(nc.factionID)])
            else:
                allianceRegistry = session.ConnectToService('allianceRegistry')
                allianceID = allianceRegistry.AllianceIDFromCorpID(corporationID)
                allianceName = ''
                if allianceID is not None:
                    allianceName = self.AllianceLink(allianceID)
                lines.append([1, 'Alliance', allianceName])
            lines.append([1, 'Station', self.StationLink(c.stationID)])
            if station is not None:
                lines.append([0, 'System', self.SystemLink(station.solarSystemID)])
            else:
                lines.append([0, 'System', ''])
            self.SubjectHeader(smallHeader, 'CORPORATION', corporationID, self.OwnerName(corporationID), '#FFE0C0', image, '/gm/corporation.py', 'Corporation', 'corporationID', lines)
            li = []
            li.append('#CORPORATION')
            li.append(self.Link('/gm/corporation.py', 'INFO', {'action': 'Corporation',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/skilljournal.py', 'Check LSR Logs', {'action': 'LSRLogs',
             'characterID': corporationID,
             'ownerType': 2}))
            li.append(self.Link('/gm/skilljournal.py', 'Check Connection SR Logs', {'action': 'ConnectionSRLogs',
             'characterID': corporationID,
             'ownerType': 2}))
            li.append('-')
            li.append(self.Link('/gm/corporation.py', 'Alliance Records', {'action': 'AllianceRecords',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/logs.py', 'Audit Log', {'action': 'AuditLog',
             'logGroup': const.groupCorporation,
             'corporationID': corporationID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupCorporation,
             'ownerID': corporationID}) + self.MidDot() + self.Link('/gm/logs.py', 'Accessed Others Cargo', {'action': 'CargoAccessLogs',
             'charID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Bulletins', {'action': 'Bulletins',
             'ownerID': corporationID}))
            if not util.IsNPC(corporationID):
                now = time.gmtime()
                li.append(self.Link('/gm/calendar.py', 'Calendar', {'action': 'FindByOwner',
                 'ownerID': corporationID,
                 'ownerType': const.groupCorporation,
                 'fromMonth': 1,
                 'fromYear': const.calendarStartYear,
                 'toMonth': 1,
                 'toYear': now[0] + 1}))
            li.append(self.Link('/gm/owner.py', 'Contacts', {'action': 'Contacts',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Gag Corp', {'action': 'GagCorporationForm',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', 'Ungag Corp', {'action': 'UnGagCorporation',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Locked Items', {'action': 'LockedItems',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Kill Report', {'action': 'KillReport',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Medals', {'action': 'Medals',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/faction.py', 'Militia Stats', {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Corporate Registry Ads', {'action': 'CorporateRegistry',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/owner.py', 'Offices', {'action': 'RentableItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID,
             'typID': 26}))
            li.append(self.Link('/gm/corporation.py', 'Roles', {'action': 'Roles',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Shareholders', {'action': 'ViewShareholders',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', 'Shares', {'action': 'CreateCorporationSharesForm',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/owner.py', 'Standings', {'action': 'Standings',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Stations', {'action': 'Stations',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Starbases', {'action': 'Starbases',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Titles', {'action': 'Titles',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Trades', {'action': 'Trades',
             'corporationID': corporationID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', 'Accounting', {'action': 'Statement',
             'characterID': corporationID,
             'groupID': const.groupCorporation}))
            li.append('>' + self.Link('/gm/accounting.py', 'Cash', {'action': 'Journal',
             'characterID': corporationID,
             'keyID': const.accountingKeyCash,
             'entryTypeFilter': None,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}) + self.MidDot() + self.Link('/gm/accounting.py', 'Insurance', {'action': 'Journal',
             'characterID': corporationID,
             'keyID': 1000,
             'entryTypeFilter': 19,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}))
            li.append('>' + self.Link('/gm/owner.py', 'Bills', {'action': 'Bills',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', 'Credits', {'action': 'CorporationCreditsForm',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/accounting.py', 'Mass Reversal', {'action': 'MassReversal',
             'characterID': corporationID}) + self.MidDot() + self.Link('/gm/accounting.py', 'Aurum', {'action': 'Journal',
             'characterID': corporationID,
             'keyID': const.accountingKeyAUR,
             'entryTypeFilter': None,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}))
            li.append('-')
            li.append(self.Link('/gm/contracts.py', 'Contracts', {'action': 'ListForEntity',
             'submit': 1,
             'ownerID': corporationID}))
            li.append('>' + self.Link('/gm/contracts.py', 'Issued By', {'action': 'List',
             'submit': 1,
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/contracts.py', 'Issued To', {'action': 'List',
             'submit': 1,
             'acceptedByID': corporationID,
             'filtStatus': const.conStatusInProgress}))
            li.append('>' + self.Link('/gm/contracts.py', 'Assigned To', {'action': 'List',
             'submit': 1,
             'assignedToID': corporationID}))
            li.append('-')
            li.append('!Items')
            li.append('>' + self.Link('/gm/inventory.py', 'Find Item', {'action': 'FindItem',
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', 'System-Items', {'action': 'SystemItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('>' + self.Link('/gm/owner.py', 'Station-Items', {'action': 'StationItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', 'Office-Items', {'action': 'OfficeItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('>' + self.Link('/gm/corporation.py', 'Find Item Members', {'action': 'FindItemsOnMembers',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!Market')
            li.append('>' + self.Link('/gm/owner.py', 'orders', {'action': 'Orders',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', 'Transactions', {'action': 'Transactions',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('-')
            li.append(self.Link('/gm/corporation.py', 'Members', {'action': 'SimplyViewMembers',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/corporation.py', 'Complex Members', {'action': 'ViewMembers',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/petition.py', 'Members Petitions', {'action': 'CorpPetitions',
             'corpID': corporationID}))
            li.append('-')
            li.append('!Notes')
            li.append('>' + self.Link('/gm/corporation.py', 'Corp', {'action': 'Notes',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', 'Members(Users)', {'action': 'NotesForCorp',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!Sanctioned Actions')
            li.append('>' + self.Link('/gm/corporation.py', 'In Effect', {'action': 'ViewSanctionableActions',
             'corporationID': corporationID,
             'inEffect': 1}) + self.MidDot() + self.Link('/gm/corporation.py', 'Not In Effect', {'action': 'ViewSanctionableActions',
             'corporationID': corporationID,
             'inEffect': 0}))
            li.append('-')
            li.append('!Science & Industry')
            li.append('>' + self.Link('/gm/ram.py', 'Jobs', {'action': 'JobsOwner',
             'ownerID': corporationID,
             'groupID': const.groupCorporation}) + self.MidDot() + self.Link('/gm/ram.py', 'Assembly Lines', {'action': 'AssemblyLinesOwner',
             'ownerID': corporationID,
             'groupID': const.groupCorporation}))
            li.append('-')
            li.append('!Wars')
            li.append('>' + self.Link('/gm/war.py', 'Active', {'action': 'ViewWars',
             'ownerID': corporationID,
             'onlyActive': 1}) + self.MidDot() + self.Link('/gm/war.py', 'All', {'action': 'ViewWars',
             'ownerID': corporationID,
             'onlyActive': 0}) + self.MidDot() + self.Link('/gm/corporation.py', 'Faction', {'action': 'ViewFactionWarsForCorp',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!Votes')
            li.append('>' + self.Link('/gm/corporation.py', 'Open', {'action': 'ViewVotes',
             'corporationID': corporationID,
             'isOpen': 1}) + self.MidDot() + self.Link('/gm/corporation.py', 'Closed', {'action': 'ViewVotes',
             'corporationID': corporationID,
             'isOpen': 0}))
            self.SubjectActions(li, menuPlacement)
            return c



        def AllianceHeader(self, allianceID, smallHeader = 1, menuPlacement = 'rMenu'):
            a = self.cache.EspAlliance(allianceID)
            image = self.GetOwnerImage('Alliance', allianceID)
            if image == None:
                image = '/img/alliance.jpg'
            lines = []
            info = ''
            info = self.SplitAdd(info, util.FmtDateEng(a.startDate, 'ln'), ', ')
            lines.append([0, 'Info', info])
            if a.url:
                lines.append([0, 'web', a.url])
            self.SubjectHeader(smallHeader, 'ALLIANCE', allianceID, self.OwnerName(allianceID), '#D7AFAF', image, '/gm/alliance.py', 'Alliance', 'allianceID', lines)
            li = []
            li.append('#ALLIANCE')
            li.append(self.Link('/gm/alliance.py', 'INFO', {'action': 'Alliance',
             'allianceID': allianceID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', 'Accounting', {'action': 'Statement',
             'characterID': allianceID,
             'groupID': const.groupAlliance}))
            li.append(self.Link('/gm/alliance.py', 'Applications', {'action': 'ViewApplications',
             'allianceID': allianceID}))
            now = time.gmtime()
            li.append(self.Link('/gm/calendar.py', 'Calendar', {'action': 'FindByOwner',
             'ownerID': allianceID,
             'ownerType': const.groupAlliance,
             'fromMonth': 1,
             'fromYear': const.calendarStartYear,
             'toMonth': 1,
             'toYear': now[0] + 1}))
            li.append(self.Link('/gm/owner.py', 'Bills', {'action': 'Bills',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/alliance.py', 'Bills (Payable by GMH)', {'action': 'ViewBills',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/corporation.py', 'Bulletins', {'action': 'Bulletins',
             'ownerID': allianceID}))
            li.append(self.Link('/gm/owner.py', 'Contacts', {'action': 'Contacts',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/inventory.py', 'Find Item', {'action': 'FindItem',
             'ownID': allianceID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupAlliance,
             'ownerID': allianceID}))
            li.append(self.Link('/gm/alliance.py', 'Members', {'action': 'ViewMembers',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/alliance.py', 'Notes', {'action': 'Notes',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/alliance.py', 'Rankings', {'action': 'Rankings'}))
            li.append(self.Link('/gm/owner.py', 'Standings', {'action': 'Standings',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/alliance.py', 'Sovereignty Bill', {'action': 'Sovereignty',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/war.py', 'Wars(Active)', {'action': 'ViewWars',
             'ownerID': allianceID,
             'onlyActive': 1}))
            li.append(self.Link('/gm/war.py', 'Wars(All)', {'action': 'ViewWars',
             'ownerID': allianceID,
             'onlyActive': 0}))
            self.SubjectActions(li, menuPlacement)
            return a



        def FactionHeader(self, factionID, smallHeader = 1, menuPlacement = 'rMenu'):
            f = cfg.factions.Get(factionID)
            image = '/img/faction%s.jpg' % factionID
            self.SubjectHeader(smallHeader, 'FACTION', factionID, f.factionName, '#E8E8FF', image, '/gm/faction.py', 'Faction', 'factionID', [[1, 'System', self.SystemLink(f.solarSystemID)], [1, 'Corporation', self.CorporationLink(f.corporationID)]])
            li = []
            li.append('#FACTION')
            li.append(self.Link('/gm/faction.py', 'INFO', {'action': 'Faction',
             'factionID': factionID}))
            li.append('-')
            li.append(self.Link('/gm/faction.py', 'Corporations', {'action': 'Corporations',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', 'FacWar Corporations', {'action': 'FactionalWarfareCorporations',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', 'Militia Stats', {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': factionID}))
            li.append(self.Link('/gm/faction.py', 'Distributions', {'action': 'Distributions',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', 'Territory', {'action': 'Territory',
             'factionID': factionID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupFaction,
             'ownerID': factionID}))
            li.append(self.Link('/gm/owner.py', 'Standings', {'action': 'Standings',
             'groupID': const.groupFaction,
             'ownID': factionID}))
            self.SubjectActions(li, menuPlacement)
            return f



        def CharacterLocationText(self, characterID, locationID, locationTypeID, locationLocationID, activeShipID = None, activeShipTypeID = None):
            solarSystemID = None
            if util.IsSolarSystem(locationLocationID):
                solarSystemID = locationLocationID
            elif util.IsStation(locationLocationID):
                solarSystemID = sm.StartService('stationSvc').GetStation(locationLocationID).solarSystemID
            s = ''
            try:
                shipID = None
                if not util.IsSystemOrNPC(locationID):
                    shipID = locationID
                    locationID = locationLocationID
                if util.IsWorldSpace(locationID):
                    s += self.FontHeaderProperty('WorldSpace')
                    s += ':<br>%s' % self.WorldSpaceLink(locationID)
                elif util.IsSolarSystem(locationID):
                    s += self.FontHeaderProperty('SYSTEM')
                    s += ':<br>%s' % self.SystemLink(locationID)
                else:
                    s += self.FontHeaderProperty('STATION')
                    s += ':<br>%s' % self.StationLink(locationID)
                    s += ' - %s' % self.SystemLink(solarSystemID)
                if shipID:
                    s += '<br>' + self.FontHeaderProperty('SHIP') + ':<br>%s' % self.Link('/gm/character.py', cfg.evelocations.Get(shipID).locationName, {'action': 'Ship',
                     'characterID': characterID,
                     'shipID': shipID})
                    s += '<br>' + self.FontProperty('Type') + ': %s' % cfg.invtypes.Get(locationTypeID).typeName
                elif activeShipID:
                    s += '<br>' + self.FontHeaderProperty('SHIP') + ':<br>%s' % self.Link('/gm/character.py', cfg.evelocations.Get(activeShipID).locationName, {'action': 'Ship',
                     'characterID': characterID,
                     'shipID': activeShipID})
                    s += '<br>' + self.FontProperty('Type') + ': %s' % cfg.invtypes.Get(activeShipTypeID).typeName
            except:
                s = '<font color=red>Invalid Location: %s</font>' % locationID
            return s



        def FormatDateTime(self, dt):
            dtNow = blue.win32.GetSystemTimeAsFileTime()
            diff = dtNow - dt
            numMinutes = diff / 10000000.0 / 60
            numDays = numMinutes / 60 / 24
            dTimeFmt = util.FmtDateEng(dt, 'ns')
            dst = util.FmtDateEng(dt, 'sn')
            lst = dst.split('.')
            dDateFmt = lst[2] + '. ' + ['Jan',
             'Feb',
             'Mar',
             'Apr',
             'May',
             'Jun',
             'Jul',
             'Aug',
             'Sep',
             'Oct',
             'Nov',
             'Dec'][(int(lst[1]) - 1)] + ' ' + lst[0]
            dn = util.FmtDateEng(dtNow, 'ns')
            if numDays < 1 and dTimeFmt.split(':')[0] <= dn.split(':')[0]:
                return '<b>Today at %s</b>' % dTimeFmt
            else:
                if numDays < 2:
                    return 'Yesterday at %s' % dTimeFmt
                return dDateFmt + ' ' + dTimeFmt



        def BloodlineGenderImage(self, bloodlineID, gender):
            image = '/img/bloodline%d' % bloodlineID
            if gender == 0:
                image += 'F'
            else:
                image += 'M'
            return self.Image(image + '.jpg')



        def BloodlineDetailCombo(self, detail, colID, colName, bloodlineID, gender):
            s = 'SELECT D.' + colID + ', M.' + colName + ' FROM chrBloodline' + detail + ' D INNER JOIN chr' + detail + ' M ON M.' + colID + ' = D.' + colID
            s += ' WHERE D.bloodlineID = %d AND D.gender = %d' % (bloodlineID, gender)
            rs = self.DB2.SQL(s)
            d = {}
            if len(rs) > 0:
                d[None] = '(random)'
                for r in rs:
                    d[r[colID]] = r[colName]

            return d



        def CatmaEntryLink(self, entryID, linkText = None, props = ''):
            if entryID is None:
                return ''
            if linkText is None:
                from catma import catmaDB
                linkText = catmaDB.GetTypeDisplayNameByID(entryID)
            return self.Link('/catma/catmaMK2.py', linkText, {'action': 'Entry',
             'entryID': entryID}, props)




    class GDHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.GDHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/base.html', page = '', showMenu = True):
            ESPHtmlWriter.__init__(self, template, 'CONTENT', page, showMenu)
            self.inserts['body'] = ''



        def WriteLeftMenu(self, action):
            pass



        def WriteRightMenu(self):
            pass



        def CategoriesPart(self, categoryID, categoryAction = 'Category', placement = 'rMenu'):
            categories = []
            for c in cfg.invcategories:
                if c.categoryID > 0:
                    bon = ''
                    boff = ''
                    if c.categoryID == categoryID:
                        bon = '<b>'
                        boff = '</b>'
                    categories.append([c.categoryName, bon + self.Link('type.py', c.categoryName, {'action': categoryAction,
                      'categoryID': c.categoryID}) + boff])

            categories.sort()
            categories = map(lambda line: line[1:], categories)
            return categories



        def GroupsPart(self, categoryID, groupID, groupAction = 'Group', placement = 'rMenu'):
            groups = []
            for g in cfg.groupsByCategories.get(categoryID, []):
                bon = ''
                boff = ''
                if g.groupID == groupID:
                    bon = '<b>'
                    boff = '</b>'
                groups.append([g.groupName, bon + self.Link('type.py', g.groupName, {'action': groupAction,
                  'categoryID': categoryID,
                  'groupID': g.groupID}) + boff])

            groups.sort()
            groups = map(lambda line: line[1:], groups)
            return groups



        def TypesPart(self, groupID, typeID, typeAction = 'Type', placement = 'rMenu'):
            types = []
            for t in self.DB2.SQLInt('typeID, typeName', 'inventory.types', '', 'typeName', 'groupID', groupID):
                bon = ''
                boff = ''
                if t.typeID == typeID:
                    bon = '<b>'
                    boff = '</b>'
                types.append([bon + self.Link('type.py', t.typeName, {'action': typeAction,
                  'typeID': t.typeID}) + boff])

            return types



        def TypeImage(self, typeID, width = 64):
            imageServerURL = sm.GetService('machoNet').GetClientConfigVals().get('imageserverurl')
            imgURL = imageServerURL + 'Type/%s_64.png' % typeID
            return imgURL



        def TypeHeader(self, typeID, typeAction = 'Type'):
            typeName = ''
            typeNameID = None
            groupID = -1
            categoryID = -1
            rs = self.DB2.SQLInt('*', 'inventory.typesEx', '', '', 'typeID', typeID)
            if len(rs) == 0:
                r = None
            else:
                r = rs[0]
                typeName = r.typeName
                typeNameID = r.typeNameID
                groupID = r.groupID
                group = cfg.invgroups.GetIfExists(groupID)
                if group is None:
                    categoryID = None
                else:
                    categoryID = group.categoryID
            lines = []
            lines.append([1, 'Group', self.GroupLink(groupID)])
            lines.append([1, 'Category', self.CategoryLink(categoryID)])
            self.SubjectHeader(1, 'TYPE', typeID, self.GetLocalizationLabel(typeName, typeNameID), '#C0C0C0', self.TypeImage(typeID), '/gd/type.py', 'Type', 'typeID', lines, 64, 64)
            li = []
            li.append('#TYPE')
            li.append(self.Link('type.py', 'INFO', {'action': 'Type',
             'typeID': typeID}))
            li.append('%s%s%s' % (self.Link('type.py', 'Balls', {'action': 'TypeBalls',
              'typeID': typeID}), self.MidDot(), self.Link('type.py', 'Contraband', {'action': 'TypeContraband',
              'typeID': typeID})))
            li.append(self.Link('type.py', 'Dogma Info', {'action': 'TypeDogma',
             'typeID': typeID}))
            li.append('%s%s%s' % (self.Link('type.py', 'Loot', {'action': 'TypeLoot',
              'typeID': typeID}), self.MidDot(), self.Link('type.py', 'Market', {'action': 'TypeMarket',
              'typeID': typeID})))
            li.append('%s%s%s' % (self.Link('type.py', 'Materials', {'action': 'TypeMaterials',
              'typeID': typeID}), self.MidDot(), self.Link('type.py', 'Requirements', {'action': 'TypeRequirements',
              'typeID': typeID})))
            li.append('%s%s%s' % (self.Link('type.py', 'Reactions', {'action': 'TypeReactions',
              'typeID': typeID}), self.MidDot(), self.Link('type.py', 'Skills', {'action': 'TypeSkills',
              'typeID': typeID})))
            if groupID == const.groupControlTower:
                li.append(self.Link('type.py', 'Tower Resources', {'action': 'TypeTowerResources',
                 'typeID': typeID}))
            li.append('-')
            if r:
                act = self.RevisionLink(r)
                if session.role & ROLE_CONTENT:
                    act = self.Link('type.py', 'EDIT', {'action': 'EditTypeForm',
                     'typeID': typeID}) + self.MidDot() + act
                li.append(act)
            li.append('%s%s%s' % (self.Link('type.py', 'CHANGES', {'action': 'Changes',
              'typeID': typeID}), self.MidDot(), self.Link('type.py', 'RELATIONS', {'action': 'Relations',
              'typeID': typeID})))
            if session.role & ROLE_CONTENT > 0:
                li.append(self.Link('type.py', 'Copy', {'action': 'TypeCopyForm',
                 'typeID': typeID}))
                if categoryID == const.categoryShip:
                    li.append(self.Link('type.py', 'Edit Ship Info', {'action': 'EditTypeShipForm',
                     'typeID': typeID}))
                elif groupID == const.groupStation:
                    li.append(self.Link('type.py', 'Edit Station Info', {'action': 'EditTypeStationForm',
                     'typeID': typeID}))
                li.append(self.Link('type.py', 'Edit Dogma Info', {'action': 'EditTypeDogmaForm',
                 'typeID': typeID}))
                li.append(self.Link('materials.py', 'Edit Materials', {'action': 'EditTypeMaterialsForm',
                 'typeID': typeID}))
                li.append(self.Link('type.py', 'Meta Types', {'action': 'MetaTypes',
                 'parentTypeID': typeID}))
                li.append('>%s%s%s' % (self.Link('type.py', 'Add', {'action': 'InsertMetaTypeForm',
                  'parentTypeID': typeID}), self.MidDot(), self.Link('type.py', 'Associate to Master', {'action': 'InsertMetaTypeReverseForm',
                  'typeID': typeID})))
                li.append(self.Link('type.py', 'REMOVE', {'action': 'RemoveTypeForm',
                 'typeID': typeID}))
            self.SubjectActions(li)
            self.WriteDirect('rMenu', '<br>')
            self.WriteDirect('rMenu', self.WebPart('Types', self.GetTable([], self.TypesPart(groupID, typeID, typeAction)), 'wpTypes'))
            self.WriteDirect('rMenu', self.WebPart('Groups', self.GetTable([], self.GroupsPart(categoryID, groupID)), 'wpGroups'))
            self.WriteDirect('rMenu', self.WebPart('Categories', self.GetTable([], self.CategoriesPart(categoryID)), 'wpCategories'))
            if r is None:
                self.WriteError('Record not found')
            return r




    class SessionHtmlWriter(htmlwriter.HtmlWriterEx):
        __guid__ = 'htmlwriter.SessionHtmlWriter'

        def __init__(self):
            htmlwriter.HtmlWriterEx.__init__(self)



        def Generate(self):
            self.s = htmlwriter.UnicodeMemStream()
            if session is not None and session.charid:
                li = []
                liHead = []
                liHead.append([self.Image('/img/character.py?characterID=%i&size=64' % session.charid), '<Font Size=4 STYLE="Color:purple;">%s</font>' % session.charid])
                self.s.Write(self.WebPart('&nbsp;&nbsp;&nbsp;&nbsp;Character', self.Table([], liHead) + self.GetTable([], li), 'charpart'))
            self.s.Seek(0)
            return str(self.s.Read())




    class PetitionHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.PetitionHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/baseNoRight.html', page = ''):
            ESPHtmlWriter.__init__(self, template, 'PETITION', page)




    class PetitionClientHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.PetitionClientHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/baseWideLeftNoRight.html', page = ''):
            ESPHtmlWriter.__init__(self, template, 'PETITION', page)



if macho.mode in ('server', 'proxy'):

    class AdminHtmlWriter(ESPHtmlWriter):
        __guid__ = 'htmlwriter.AdminHtmlWriter'

        def __init__(self, template = 'script:/wwwroot/lib/template/base.html', page = ''):
            ESPHtmlWriter.__init__(self, template, 'ADMIN', page)




class InfoHtmlWriter(ESPHtmlWriter):
    __guid__ = 'htmlwriter.InfoHtmlWriter'

    def __init__(self, template = 'script:/wwwroot/lib/template/baseNoRight.html', page = ''):
        ESPHtmlWriter.__init__(self, template, 'INFO', page)




def hook_AppServerPages(writer, menu = ''):
    if writer.showMenu:
        dGML = not session.role & ROLE_GML
        dCONTENT = not session.role & ROLE_CONTENT
        dADMIN = not session.role & ROLE_ADMIN
        dVIEW = not session.role & ROLEMASK_VIEW
        dPROG = not session.role & ROLE_PROGRAMMER
        if macho.mode == 'server':
            writer.inserts['icon'] = writer.Link('/gm/search.py', writer.Image('/img/menu_search32.jpg', 'width=32 height=32'))
            writer.AddTopMenuSubLine('GM')
            writer.AddTopMenuSub('GM', 'Search', '/gm/search.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Find Item', '/gm/inventory.py?action=FindItem', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Item Report', '/gm/inventory.py?action=Item', disabled=dVIEW)
            writer.AddTopMenuSubLine('GM')
            writer.AddTopMenuSub('GM', 'Alliances', '/gm/alliance.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Calendar', '/gm/calendar.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Contracts', '/gm/contracts.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Corporations', '/gm/corporation.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Factions', '/gm/faction.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Fleets', '/gm/fleet.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Inventory', '/gm/inventory.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Starbases', '/gm/starbase.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Stations', '/gm/stations.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Tale', '/gm/tale.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Planets', '/gm/planets.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Voice Chat', '/gm/voice.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Virtual Store', '/gm/store.py', disabled=dVIEW)
            if prefs.GetValue('enableDust', 0) == 1:
                writer.AddTopMenuSubLine('GM')
                writer.AddTopMenuSub('GM', 'Quick Battles', '/dust/battleSeriesBattles.py', disabled=dVIEW)
                writer.AddTopMenuSub('GM', 'Corp Battles', '/dust/corporationBattles.py', disabled=dVIEW)
            writer.AddTopMenuSub('PETITION', 'My Petitions', '/gm/petitionClient.py?action=ShowMyPetitions', disabled=dVIEW)
            writer.AddTopMenuSubLine('PETITION')
            writer.AddTopMenuSub('PETITION', 'Answer Petitions', '/gm/petitionClient.py?action=ShowClaimedPetitions', disabled=dVIEW)
            writer.AddTopMenuSub('PETITION', 'Knowledge Base', '/gm/knowledgebase.py', disabled=dCONTENT)
            writer.AddTopMenuSub('PETITION', 'Petition Management', '/gm/petition.py', disabled=dGML)
            writer.AddTopMenuSub('PETITION', 'Support Management', '/gm/supportManagement.py', disabled=dGML)
            writer.AddTopMenuSubLine('CONTENT')
            writer.AddTopMenuSub('CONTENT', 'Agents', '/gd/agents.py', disabled=dGML and dCONTENT and dADMIN)
            writer.AddTopMenuSub('CONTENT', 'Blueprints', '/gd/blueprints.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Certificates', '/gd/certificates.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Characters', '/gd/characters.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Client Setings', '/gd/client.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Combat Zones', '/gd/combatZones.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Corporations', '/gd/corporations.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Dungeons', '/gd/dungeons.py', disabled=dVIEW and dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Dungeon Distribution', '/gd/dungeonDistributions.py', disabled=dVIEW and dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Expo Settings', '/gd/expo.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Market', '/gd/market.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Materials', '/gd/materials.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Names', '/gd/names.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'NPC', '/gd/npc.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Outposts', '/gd/outposts.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Planet Resources', '/gd/planetResource.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Play Ground', '/gd/playGround.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Reactions', '/gd/reactions.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Rewards', '/gd/rewards.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Schematics', '/gd/schematics.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Science & Industry', '/gd/ram.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Spawn List', '/gd/spawnlist.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Tale', '/gd/tale.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Types', '/gd/type.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Type Distribution', '/gd/tdm.py', disabled=dCONTENT)
            writer.AddTopMenuSub('CONTENT', 'Tutorials', '/gd/tutorials.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Universe', '/gd/universe.py', disabled=dVIEW)
            writer.AddTopMenuSub('CONTENT', 'Virtual Store', '/gd/store.py', disabled=dVIEW)
            if prefs.GetValue('enableDust', 0) == 1:
                writer.AddTopMenuSubLine('CONTENT')
                writer.AddTopMenuSub('CONTENT', 'Catma', '/catma/catmaMK2.py', disabled=dVIEW)
                writer.AddTopMenuSub('CONTENT', 'Galaxy', '/dust/galaxy.py', disabled=dVIEW)
            writer.AddTopMenuSubLine('INFO')
            writer.AddTopMenuSub('INFO', 'Beyonce', '/info/beyonce.py', disabled=dVIEW)
            writer.AddTopMenuSub('INFO', 'Map', '/info/map.py', disabled=dVIEW)
            writer.AddTopMenuSub('INFO', 'Dogma', '/info/dogma.py')
            writer.AddTopMenuSub('INFO', 'FW Reports', '/info/facwarreports.py')
            writer.AddTopMenuSub('INFO', 'Inventory', '/info/inventory.py')
            writer.AddTopMenuSub('INFO', 'CEF', '/info/cef.py')
            writer.AddTopMenuSub('INFO', 'Aperture', '/info/aperture.py')
            writer.AddTopMenuSubLine('ADMIN')
            writer.AddTopMenuSub('ADMIN', 'Client Stats', '/admin/clientStats2_2.py', disabled=dADMIN)
            writer.AddTopMenuSub('ADMIN', 'Client Stats (Old)', '/admin/clientStats2.py', disabled=dADMIN)
            writer.AddTopMenuSub('ADMIN', 'Info Gathering', '/admin/infoGathering.py', disabled=dADMIN)
            writer.AddTopMenuSubLine('ADMIN')
            writer.AddTopMenuSub('ADMIN', 'Server Options', '/admin/default.py', disabled=dPROG)
            writer.AddTopMenuSub('ADMIN', 'Live Market', '/admin/liveMarket.py', disabled=dADMIN)
            writer.AddTopMenuSubLine('ADMIN')
            writer.AddTopMenuSub('ADMIN', 'Bulkdata', '/admin/bulkdata.py', disabled=dADMIN)
            writer.AddTopMenuSub('ADMIN', 'Edit ESP', '/admin/editEsp.py', disabled=dPROG)
            if prefs.GetValue('enableDust', 0) == 1:
                writer.AddTopMenuSubLine('ADMIN')
                writer.AddTopMenuSub('ADMIN', 'Dust remote cluster', '/dust/remoteDustCluster.py', disabled=dVIEW)
        elif macho.mode == 'proxy':
            pass
        elif macho.mode == 'client':
            pass
        if macho.mode == 'server':
            if menu == 'GM':
                writer.AddMenu('Search', 'Search', '', '/gm/search.py')
                writer.AddMenu('Alliances', 'Alliances', '', '/gm/alliance.py')
                writer.AddMenu('Contracts', 'Contracts', '', '/gm/contracts.py')
                writer.AddMenu('Corporations', 'Corporations', '', '/gm/corporation.py')
                writer.AddMenu('Factions', 'Factions', '', '/gm/faction.py')
                writer.AddMenu('Inventory', 'Inventory', '', '/gm/inventory.py')
                writer.AddMenu('Starbases', 'Starbases', '', '/gm/starbase.py')
                writer.AddMenu('Stations', 'Stations', '', '/gm/stations.py')
            elif menu == 'PETITION':
                writer.AddMenu('AnswerPetitions', 'Answer Petitions', '', '/gm/petitionClient.py?action=ShowClaimedPetitions')
                writer.AddMenu('KnowledgeBase', 'Knowledge Base', '', '/gm/knowledgebase.py')
                writer.AddMenu('PetitionManagement', 'Petition Management', '', '/gm/petition.py')
                writer.AddMenu('SupportManagement', 'Support Management', '', '/gm/supportManagement.py')
                writer.AddMenu('SpamReports', 'Spam Reports', '', '/gm/users.py?action=ListSpamUsers')
                writer.AddMenu('Characters', 'Characters', '', '/gm/character.py')
                writer.AddMenu('Users', 'Users', '', '/gm/users.py')
                writer.AddMenu('Search', 'Search', '', '/gm/search.py')
                writer.AddMenu('ItemReport', 'Item Report', '', '/gm/inventory.py?action=Item')
                writer.AddMenu('FindItem', 'Find Item', '', '/gm/inventory.py?action=FindItem')
                writer.AddMenu('My Characters', 'My Characters', '', '/gm/character.py?action=MyCharacters')
            elif menu == 'CONTENT':
                writer.AddMenu('Agents', 'Agents', '', '/gd/agents.py')
                writer.AddMenu('Blueprints', 'Blueprints', '', '/gd/blueprints.py')
                writer.AddMenu('Certificates', 'Certificates', '', '/gd/certificates.py')
                writer.AddMenu('Characters', 'Characters', '', '/gd/characters.py')
                writer.AddMenu('Corporations', 'Corporations', '', '/gd/corporations.py')
                writer.AddMenu('Dungeons', 'Dungeons', '', '/gd/dungeons.py')
                writer.AddMenu('Market', 'Market', '', '/gd/market.py')
                writer.AddMenu('Materials', 'Materials', '', '/gd/materials.py')
                writer.AddMenu('NPC', 'NPC', '', '/gd/npc.py')
                writer.AddMenu('Outposts', 'Outposts', '', '/gd/outposts.py')
                writer.AddMenu('Reactions', 'Reactions', '', '/gd/reactions.py')
                writer.AddMenu('Rewards', 'Rewards', '', '/gd/rewards.py')
                writer.AddMenu('Schematics', 'Schematics', '', '/gd/schematics.py')
                writer.AddMenu('S&I', 'S&I', '', '/gd/ram.py')
                writer.AddMenu('Spawnlist', 'Spawn List', '', '/gd/spawnlist.py')
                writer.AddMenu('Tale', 'Tale', '', '/gd/tale.py')
                writer.AddMenu('Types', 'Types', '', '/gd/type.py')
                writer.AddMenu('Tutorials', 'Tutorials', '', '/gd/tutorials.py')
                writer.AddMenu('Universe', 'Universe', '', '/gd/universe.py')
            elif menu == 'INFO':
                writer.AddMenu('Inventory', 'Inventory', '', '/info/inventory.py')
                writer.AddMenu('Dogma', 'Dogma', '', '/info/dogma.py')
                writer.AddMenu('Beyonce', 'Beyonce', '', '/info/beyonce.py')
                writer.AddMenu('Map', 'Map', '', '/info/map.py')
            elif menu == 'ADMIN':
                writer.AddMenu('ClientStats', 'Client-Stats', '', '/admin/clientStats2.py')
        elif macho.mode == 'proxy':
            pass
        elif macho.mode == 'client':
            pass


exports = {'util.hook_AppServerPages': hook_AppServerPages,
 'util.hook_AppSpContentResources': True,
 'util.hook_AppSpContentWorldSpaces': True,
 'util.hook_AppSpContentPaperdolls': True}

