import htmlwriter
import util
import re
import blue
import sys
import macho
import notificationUtil
import time
import datetime
import os
from service import ROLE_ANY, ROLEMASK_VIEW, ROLE_ADMIN, ROLE_CONTENT, ROLE_GML, ROLE_GMH, ROLE_PROGRAMMER, ROLE_TRANSLATION, ROLE_TRANSLATIONEDITOR, ROLE_TRANSLATIONADMIN, ROLE_TRANSLATIONTESTER, ROLE_PETITIONEE, ROLE_DBA, ROLE_MARKET, ROLE_MARKETH

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

        def MetaGroupLink(self, metaGroupID, linkText = None, props = ''):
            if metaGroupID is None:
                return ''
            else:
                if linkText is None:
                    linkText = cfg.invmetagroups.Get(metaGroupID).metaGroupName
                    if linkText is None:
                        return self.FontRed(mls.UI_GENERIC_UNKNOWN)
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
            if characterID > const.minDustCharacter:
                return htmlwriter.SPHtmlWriter.CharacterLink(self, characterID, linkText, props)
            if characterID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(characterID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/character.py?action=Character&characterID=%s' % characterID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=1' % characterID, title=linkText, caption=linkText)



        def CharacterLinkActions(self, characterID, linkText = None, actions = []):
            if characterID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(characterID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltipActions(href='/gm/character.py?action=Character&characterID=%s' % characterID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=1' % characterID, title=linkText, caption=linkText, actions=actions)



        def PetitionLink(self, petID, linkText = None, props = ''):
            if petID is None:
                return ''
            else:
                if linkText is None:
                    linkText = 'petition'
                return self.Link('/gm/petitionClient.py', linkText, {'action': 'ViewPetition',
                 'petitionID': petID}, props)



        def CorporationLink(self, corporationID, linkText = None, props = ''):
            if corporationID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(corporationID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/corporation.py?action=Corporation&corporationID=%s' % corporationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=3' % corporationID, title=linkText, caption=linkText)



        def AllianceLink(self, allianceID, linkText = None, props = ''):
            if allianceID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(allianceID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/alliance.py?action=Alliance&allianceID=%s' % allianceID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=9' % allianceID, title=linkText, caption=linkText)



        def WarableEntityLink(self, ownerID, linkText = None, props = ''):
            if ownerID is None:
                return ''
            else:
                if linkText is None:
                    linkText = self.OwnerName(ownerID)
                    if linkText is None:
                        return self.FontRed(mls.UI_GENERIC_UNKNOWN)
                return self.Link('/gm/war.py', linkText, {'action': 'WarableEntity',
                 'ownerID': ownerID}, props)



        def FactionLink(self, factionID, linkText = None, props = ''):
            if factionID is None:
                return ''
            if linkText is None:
                linkText = self.OwnerName(factionID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/faction.py?action=Faction&factionID=%s' % factionID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=8' % factionID, title=linkText, caption=linkText)



        def StationLink(self, stationID, linkText = None, props = ''):
            if stationID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(stationID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/stations.py?action=Station&stationID=%s' % stationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=7' % stationID, title=linkText, caption=linkText)



        def WorldSpaceLink(self, worldSpaceID, linkText = None, props = ''):
            if worldSpaceID is None:
                return ''
            else:
                if linkText is None:
                    linkText = self.LocationName(worldSpaceID)
                    if linkText is None:
                        return self.FontRed(mls.UI_GENERIC_UNKNOWN)
                return self.Link('/gm/worldSpaces.py', linkText, {'action': 'WorldSpace',
                 'worldspaceID': worldSpaceID}, props)



        def SystemLink(self, systemID, linkText = None, props = ''):
            if systemID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(systemID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gd/universe.py?action=System&systemID=%s' % systemID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=4' % systemID, title=linkText, caption=linkText)



        def ConstellationLink(self, constellationID, linkText = None, props = ''):
            if constellationID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(constellationID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gd/universe.py?action=Constellation&constellationID=%s' % constellationID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=6' % constellationID, title=linkText, caption=linkText)



        def RegionLink(self, regionID, linkText = None, props = ''):
            if regionID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(regionID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gd/universe.py?action=Region&regionID=%s' % regionID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=5' % regionID, title=linkText, caption=linkText)



        def PlanetLink(self, planetID, linkText = None, props = ''):
            if planetID is None:
                return ''
            if linkText is None:
                linkText = self.LocationName(planetID)
                if linkText is None:
                    return self.GetSpan([mls.UI_GENERIC_UNKNOWN], className='red')
            return self.GetTooltip(href='/gm/planets.py?action=ViewPlanet&planetID=%s' % planetID, ajax='/gm/worker_info.py?action=FetchInfo&id=%s&idType=10' % planetID, title=linkText, caption=linkText)



        def CombatZoneLink(self, combatZoneID, linkText):
            if combatZoneID is None:
                return ''
            else:
                return self.Link('/gd/combatZones.py', linkText, {'action': 'Zone',
                 'zoneID': combatZoneID}, '')



        def MapLink(self, itemID, linkText = 'Map', props = ''):
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
            return self.Link('/gd/rewards.py', linkText, {'action': 'ViewReward',
             'rewardID': rewardID}, props)



        def PinLink(self, pinID, linkText = None, props = ''):
            pinName = linkText
            if pinName is None:
                pinRow = self.DB2.SQLBigInt('typeID', 'planet.pins', '', '', 'pinID', pinID)
                if len(pinRow) == 0:
                    return 'Deleted pin'
                pinName = cfg.invtypes.Get(pinRow[0].typeID).name
            return self.Link('/gm/planets.py', pinName, {'action': 'ViewPin',
             'pinID': pinID}, props)



        def PinTypeLink(self, pinID, linkText = None, props = ''):
            pinRow = self.DB2.SQLBigInt('typeID', 'planet.pins', '', '', 'pinID', pinID)[0]
            pinTypeID = pinRow.typeID
            pinName = linkText
            if pinName is None:
                pinName = cfg.invtypes.Get(pinRow.typeID).name
            return self.TypeLink(pinTypeID, linkText=pinName, props=props)



        def SchematicLink(self, schematicID, linkText = None, props = ''):
            schematicName = linkText
            if schematicName is None:
                schematicName = cfg.schematics.Get(schematicID).schematicName
            return self.Link('/gd/schematics.py', schematicName, {'action': 'View',
             'schematicID': schematicID})



        def RecipeLink(self, parentID, parentType, text = None):
            if text is None:
                if parentType == const.cef.PARENT_TYPEID:
                    text = cfg.invtypes.Get(parentID).typeName
                elif parentType == const.cef.PARENT_GROUPID:
                    text = cfg.invgroups.Get(parentID).groupName
                else:
                    text = cfg.invcategories.Get(parentID).categoryName
            return self.Link('/gd/entities.py', text, {'action': 'Recipe',
             'parentID': parentID,
             'parentType': parentType})



        def ComboRaces(self, allowNone = 0):
            combo = {}
            if allowNone:
                combo[0] = '(none)'
            for r in self.cache.Rowset(const.cacheChrRaces):
                combo[r.raceID] = r.raceName

            return combo



        def ComboBloodlines(self, allowNone = 0):
            combo = {}
            if allowNone:
                combo[0] = '(none)'
            for b in self.cache.Rowset(const.cacheChrBloodlines):
                r = self.cache.Index(const.cacheChrRaces, b.raceID)
                combo[b.bloodlineID] = r.raceName + ', ' + b.bloodlineName

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
            for r in self.DB2.SQL('SELECT * FROM mapRegions ORDER BY regionName'):
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
                for c in self.DB2.SQLInt('constellationID, constellationName', 'mapConstellations', '', 'constellationName', 'regionID', regionID):
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
                for s in self.DB2.SQLInt('solarSystemID, solarSystemName', 'mapSolarSystems', '', 'solarSystemName', 'constellationID', constellationID):
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
            if location:
                locationName = self.cache.EspItemName(2, r.locationID)
                if locationName == '':
                    line.append(self.ItemID(r.locationID))
                else:
                    line.append(self.ItemID(r.locationID) + ': ' + locationName)
            line.append('%d: %s' % (r.flagID, self.config.GetFlags(r.flagID).flagName))
            line.append(attr)
            act = ''
            if t.groupID == const.groupCharacter:
                act = self.CharacterLink(r.itemID, mls.CHARACTER)
            elif t.groupID == const.groupCorporation:
                act = self.CorporationLink(r.itemID, mls.CORPORATION)
            elif t.groupID == const.groupFaction:
                act = self.FactionLink(r.itemID, mls.FACTION)
            elif t.groupID == const.groupRegion:
                act = self.RegionLink(r.itemID, mls.REGION)
            elif t.groupID == const.groupConstellation:
                act = self.ConstellationLink(r.itemID, mls.CONSTELLATION)
            elif t.groupID == const.groupSolarSystem:
                act = self.SystemLink(r.itemID, mls.SYSTEM)
            elif t.groupID == const.groupStation:
                act = self.StationLink(r.itemID, mls.STATION)
            elif t.groupID == const.groupControlTower:
                act = self.Link('/gm/starbase.py', mls.STARBASE, {'action': 'Starbase',
                 'towerID': r.itemID})
            elif t.groupID == const.groupPlanet:
                act = self.Link('/gd/universe.py', mls.GENERIC_PLANET, {'action': 'Celestial',
                 'celestialID': r.itemID})
            elif t.groupID == const.groupAsteroidBelt:
                act = self.Link('/gd/universe.py', mls.GENERIC_BELT, {'action': 'AsteroidBelt',
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



        def UserTag(self, userID, tagTypeID = -1, tagTypeName = '', redir = None):
            s = ''
            if tagTypeID < 0:
                dbuser = self.DB2.GetSchema('user')
                rs = dbuser.EspTags_SelectUser(userID)
                if len(rs) == 0:
                    tagTypeID = None
                else:
                    r = rs[0]
                tagTypeID = r.tagTypeID
                tagTypeName = self.IsNone(r.tagTypeName, '???')
            if tagTypeID:
                s = 'User tagged as: <font color=orange size=4><b>%s</b></font>' % tagTypeName
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



    def OwnerEventReference(self, row, ownerID):
        eventTypeID = row.eventTypeID
        eventGroupID = self.cache.Index(const.cacheEventTypes, eventTypeID).eventGroupID
        referenceID = row.referenceID
        if eventGroupID == 1 and eventTypeID in (305, 306):
            if eventTypeID == 305:
                return ['', 'User Account', 'The users account is not active, all training paused on all characters! (skills, RP)']
            if eventTypeID == 306:
                return ['', 'User Account', 'The users account has been reactivated, all training resumed on all characters! (skills, RP)']
        if eventGroupID == 31:
            refID = ''
            refType = ''
            refText = 'Unknown event type %d' % eventTypeID
            if eventTypeID in (329, 330):
                refID = self.ItemID(referenceID)
                refText = ''
            elif eventTypeID in (326, 331):
                refID = 'OfferID: %d ' % referenceID
                refText = self.GetTooltip(href='/gd/store.py', ajax='/gm/store.py?action=OfferTooltip&offerID=%d' % referenceID, title='Offer Details', caption='Offer Details')
            elif eventTypeID in (327, 328):
                rx = self.DB2.SQLBigInt('*', 'zevent.genericEvents', "eventTable = 'O'", '', 'eventID', row.eventID)
                refID = '%s %s' % ('Gave' if eventTypeID == 327 else 'Took', 'ISK' if rx[0].int_1 == const.creditsISK else 'AURUM')
                refType = '%10.2f' % (rx[0].money_1 or 0.0,)
                if rx[0].bigint_1 is not None:
                    refText = self.Link('/gm/accounting.py', 'Transaction ID: %s' % rx[0].bigint_1, {'action': 'TxDetail',
                     'transactionID': rx[0].bigint_1})
                else:
                    refText = ''
            elif eventTypeID in (const.eventOfferEdit, const.eventOfferPublished, const.eventOfferClosed):
                rx = self.DB2.SQLBigInt('*', 'zevent.genericEvents', "eventTable = 'O'", '', 'eventID', row.eventID)
                refID = str(referenceID)
                refText = self.GetTooltip(href='/gd/store.py', ajax='/gm/store.py?action=OfferTooltip&offerID=%d' % referenceID, title='Offer Details', caption='Offer Details')
            elif eventTypeID == const.eventOfferDeleted:
                refID = str(referenceID)
                refText = 'it was deleted, and lost for all time!'
            return [refID, refType, refText]
        if referenceID is None:
            return ['', '', '']
        if eventGroupID == 3 or eventTypeID in (2, 113, 116):
            if referenceID >= const.minSolarSystem and referenceID <= const.maxSolarSystem:
                referenceType = 'System'
                referenceName = self.SystemLink(referenceID)
            elif referenceID >= const.minStation and referenceID <= const.maxStation:
                referenceType = 'Station'
                referenceName = self.StationLink(referenceID)
            else:
                referenceName = self.LocationName(referenceID)
                if referenceName is None:
                    referenceName = self.OwnerName(referenceID)
                    if referenceName is None:
                        referenceName = ''
                        referenceType = 'Item'
                    else:
                        referenceType = 'Owner'
                else:
                    referenceType = 'Location'
            return [self.ItemID(referenceID), referenceType, referenceName]
        if eventGroupID in (4, 6, 20, 22):
            nt = self.cache.EspItemNameType(1, referenceID)
            referenceName = nt[0]
            referenceTypeID = nt[1]
            referenceType = ''
            if referenceTypeID:
                group = cfg.invtypes.Get(referenceTypeID).Group()
                if group.groupID == const.groupFaction:
                    referenceType = mls.UI_GENERIC_FACTION
                    referenceName = self.FactionLink(referenceID, referenceName)
                elif group.groupID == const.groupCorporation:
                    if referenceID < const.minPlayerOwner:
                        referenceType = 'NPC Corporation'
                    else:
                        referenceType = 'Corporation'
                    referenceName = self.CorporationLink(referenceID, referenceName)
                elif group.groupID == const.groupCharacter:
                    if referenceID < const.minPlayerOwner:
                        referenceType = 'NPC Character'
                    else:
                        referenceType = 'Character'
                    referenceName = self.CharacterLink(referenceID, referenceName)
            return [self.ItemID(referenceID), referenceType, referenceName]
        if eventGroupID == 9:
            return [self.IsNone(referenceID, ''), 'Mission', '']
        if eventTypeID in (12, 14, 15, 16, 44) or eventTypeID in (206, 207, 210):
            return [self.ItemID(referenceID), 'Character', self.CharacterLink(referenceID)]
        if eventGroupID == 2 and eventTypeID in (149, 150):
            return [self.ItemID(referenceID), 'Corporation', self.CorporationLink(referenceID)]
        if eventGroupID == 11:
            if eventTypeID in (const.eventResearchBlueprintOfferExpired,
             const.eventResearchBlueprintAccepted,
             const.eventResearchBlueprintOfferInvalid,
             const.eventResearchBlueprintRejected,
             const.eventResearchBlueprintOfferRejectedTooLowStandings,
             const.eventResearchBlueprintOfferRejectedRecently,
             const.eventResearchBlueprintOfferRejectedInvalidBlueprint,
             const.eventResearchBlueprintOfferRejectedIncompatibleAgent,
             const.eventResearchBlueprintOffered):
                return [self.TypeLink(referenceID), 'Blueprint type', cfg.invtypes.Get(referenceID).typeName]
            else:
                if eventTypeID == const.eventResearchStarted:
                    return [self.TypeLink(referenceID), mls.LOG_RESEARCHFIELD, cfg.invtypes.Get(referenceID).typeName]
                if eventTypeID == const.eventResearchStopped:
                    return [referenceID, mls.LOG_RESEARCH_POINTS_LOST, '']
                if eventTypeID == const.eventResearchPointsEdited:
                    return [self.ItemID(referenceID), 'Character', self.CharacterLink(referenceID)]
                return ['', '', '']
        if eventTypeID in (143, 144, 145, 146):
            if 'dungeonID' in row.__columns__:
                dungeonName = self.cache.IndexText(const.cacheDungeonDungeons, row.dungeonID)
                return [referenceID, 'Dungeon Instance', self.Link('/gd/dungeons.py', dungeonName, {'action': 'Dungeon',
                  'dungeonID': row.dungeonID})]
        if eventGroupID == 16:
            tutorialIx = sm.GetService('tutorialSvc').GetTutorialsIx()
            if referenceID in tutorialIx:
                return [referenceID, 'Tutorial', self.Link('/gd/tutorials.py', tutorialIx[referenceID].tutorialName, {'action': 'TutorialVersion',
                  'tutorialID': referenceID})]
            else:
                return [referenceID, 'Tutorial', 'Deleted tutorial %d' % referenceID]
        if eventGroupID == 18:
            if referenceID >= const.minStation and referenceID <= const.maxStation:
                referenceType = 'Station'
                referenceName = self.StationLink(referenceID)
            else:
                referenceType = 'Ship'
                referenceName = self.LocationName(referenceID)
            return [self.ItemID(referenceID), referenceType, referenceName]
        if eventTypeID in (const.eventCertificateGranted, const.eventCertificateGrantedGM, const.eventCertificateRevokedGM):
            certstr = self.GetCertificateString(referenceID)
            return [self.Link('/gd/certificates.py', referenceID, {'action': 'ViewCertificate',
              'certificateID': referenceID}), mls.UI_SHARED_CERTIFICATES, self.Link('/gd/certificates.py', certstr, {'action': 'ViewCertificate',
              'certificateID': referenceID})]
        if eventTypeID in (94, 95):
            return [self.ItemID(referenceID), 'Implant', '']
        if eventTypeID == const.eventUnrentOfficeGM:
            return [self.ItemID(referenceID), 'Station', self.StationLink(referenceID)]
        if eventGroupID == 25:
            return [self.Link('/gm/users.py', referenceID, {'action': 'LookupRedeemToken',
              'tokenID': referenceID}), '', '']
        if eventGroupID == const.eventgroupPlanet:
            if eventTypeID in (286, 287, 288, 289, 290):
                return [self.Link('/gm/owner.py', str(referenceID), {'action': 'PlanataryLaunchesInv',
                  'ownID': ownerID or 0,
                  'launchID': referenceID}), mls.UI_PI_LAUNCHES, '']
            else:
                return [self.ItemID(referenceID), mls.PLANET, self.PlanetLink(referenceID)]
        if eventGroupID == const.eventgroupAlliance:
            if util.IsCorporation(referenceID):
                return [self.ItemID(referenceID), 'Corporation', self.CorporationLink(referenceID)]
            else:
                return [self.Link('', str(referenceID), {'action': 'OwnerEvent',
                  'eventID': referenceID}), 'Alliance Event', '']
        if eventTypeID in (113, 140, 141, 142):
            referenceText = ''
            if 'uiItemID' in row.__columns__:
                if row.uiItemID:
                    referenceText = self.ItemID(row.uiItemID)
                    referenceText = self.SplitAdd(referenceText, self.TypeLink(row.uiTypeID))
            return [self.Link('', referenceID, {'action': 'ItemEvent',
              'eventID': referenceID}), 'Item Event', referenceText]
        if eventGroupID == const.eventgroupReward:
            return [self.Link('/gm/tale.py', referenceID, {'taleID': referenceID}), 'Tale ID', 'Tale ID']
        return [referenceID, '', '']



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
                categoryName = category[1]
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
            if coreStatic.characterID > const.minDustCharacter:
                import dust.portrait
                portraitInfo = sm.GetService('dustCharacter').GetCharacterPortraitInfo(coreStatic.characterID)
                return dust.portrait.GetWebFilename(portraitInfo.bloodlineID, portraitInfo.gender, portraitInfo.portraitID)
            image = self.GetOwnerImage('Character', coreStatic.characterID)
            if image == None:
                image = '/img/bloodline%d%s.jpg' % (appStatic.bloodlineID, ['F', 'M'][coreStatic.gender])
            return image



        def AppUserCharactersInfo(self, coreStatic, appStatic):
            bloodline = self.cache.Index(const.cacheChrBloodlines, appStatic.bloodlineID)
            bloodlineName = Tr(bloodline.bloodlineName, 'character.bloodlines.bloodlineName', bloodline.dataID, prefs.languageID)
            race = self.cache.Index(const.cacheChrRaces, bloodline.raceID)
            raceName = Tr(race.raceName, 'character.races.raceName', race.dataID, prefs.languageID)
            if coreStatic.online == 0:
                onlineText = ''
            else:
                onlineText = '<br>' + self.FontBold(self.FontGreen(mls.ONLINE))
            s = raceName + ', ' + bloodlineName + ', ' + [mls.FEMALE, mls.MALE][coreStatic.gender] + onlineText
            if coreStatic.characterID > const.minDustCharacter:
                return s
            s += '<br>%s<br>%s' % (self.CorporationLink(appStatic.corporationID), self.Link('/gm/corporation.py', mls.UI_SHARED_MEMBERDETAILS, {'action': 'MemberDetails',
              'corporationID': appStatic.corporationID,
              'charid': coreStatic.characterID}))
            if appStatic.transferPrepareDateTime:
                s += '<br><b><font color=purple>TRANSFER INITIATED</b></font>'
            return s



        def AppUserCharactersLocation(self, coreStatic, appStatic):
            if coreStatic.characterID > const.minDustCharacter:
                return ''
            return self.CharacterLocationText(coreStatic.characterID, appStatic.locationID, appStatic.locationTypeID, appStatic.locationLocationID)



        def AppUserCharactersAct(self, coreStatic, appStatic):
            if coreStatic.characterID > const.minDustCharacter:
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
                        act += '<br><br>' + self.Link('/gm/character.py', mls.UI_CMD_SELECT.upper(), {'action': 'SelectCharacter',
                         'characterID': coreStatic.characterID})
                        if session.role & ROLE_PETITIONEE > 0:
                            act += '<br>' + self.Link('/gm/character.py', mls.GENERIC_PETITION.upper(), {'action': 'SelectCharacter',
                             'characterID': coreStatic.characterID,
                             'redir': 'p'})
                    else:
                        act += '<br /><span title="Move|By moving character to polaris you can select the character" class="red">Not in Polaris, can\'t select</span>'
                elif session.charid == coreStatic.characterID:
                    act += '<br><br>' + self.Link('/gm/character.py', mls.REPORT_LOGOFF, {'action': 'LogOffCharacter'})
            return act



        def CharacterHeader(self, characterID, small = 1, menuPlacement = 'rMenu'):
            htmlwriter.SPHtmlWriter.CharacterHeader(self, characterID, small, menuPlacement)
            (coreStatic, appStatic,) = self.cache.CharacterDataset(characterID)
            li = []
            if characterID > const.minDustCharacter:
                li.append(self.Link('', 'Currency', {'action': 'DustCharacterCurrency',
                 'characterID': characterID}))
                li.append('-')
                li.append(self.Link('', 'Skills', {'action': 'DustSkills',
                 'characterID': characterID}))
                li.append('>' + self.Link('', 'Extra Skill Points', {'action': 'DustEditExtraSkillPointsForm',
                 'characterID': characterID}) + self.MidDot() + self.Link('', 'History', {'action': 'DustSkillHistory',
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
                self.SubjectActions(li, menuPlacement)
                return 
            eveGateProfileUrl = self.cache.Setting('zcluster', 'CommunityWebsite')
            if coreStatic and eveGateProfileUrl:
                if eveGateProfileUrl[-1] != '/':
                    eveGateProfileUrl += '/'
                li.append(self.Link(eveGateProfileUrl + 'GM/Profile/' + coreStatic.characterName, mls.CHAR_GOTO_COMMUNITY_PROFILE_PAGE))
                li.append('-')
            if characterID < const.minDustCharacter:
                forumUrl = unicode('https://forums.eveonline.com/default.aspx?g=search&postedby=') + unicode(coreStatic.characterName)
                li.append(self.Link(forumUrl, 'Go to Forum History', {}))
                li.append('-')
            li.append(self.Link('/gm/logs.py', mls.CHAR_AUDITLOG, {'action': 'AuditLog',
             'logGroup': const.groupCharacter,
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_BOOKMARKS, {'action': 'Bookmarks',
             'characterID': characterID}))
            now = time.gmtime()
            li.append(self.Link('/gm/calendar.py', mls.UI_CAL_CALENDAR, {'action': 'FindByOwner',
             'ownerID': characterID,
             'ownerType': const.groupCharacter,
             'fromMonth': 1,
             'fromYear': const.calendarStartYear,
             'toMonth': 1,
             'toYear': now[0] + 1}))
            li.append(self.Link('/gm/clones.py', mls.CLONE_CLONES, {'action': 'Clones',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', mls.UI_GENERIC_INSURANCE, {'action': 'Insurance',
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', mls.UI_CONTACTS_CONTACTS, {'action': 'Contacts',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append(self.Link('/gm/corporation.py', mls.CHAR_CORPMEMBERDETAILS, {'action': 'CorpMemberDetailsByCharID',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.CHAR_DESTROYED_JUNK, {'action': 'JunkedItems',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.CHAR_EMPLOYMENTRECORDS, {'action': 'EmploymentRecords',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.CHAR_EPIC_MISSION_ARC, {'action': 'DisplayEpicMissionArcStatus',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.CMD_GIVELOOT, {'action': 'CharacterLootFormNew',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', 'Goodies and Respeccing', {'action': 'EditGoodiesAndRespeccing',
             'characterID': characterID}))
            li.append(self.Link('/gm/faction.py', mls.GENERIC_MILITIASTATS, {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': characterID}))
            li.append(self.Link('/gm/petition.py', mls.GENERIC_PETITION, {'action': 'BriefPetitionHistory',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/character.py', mls.CREATE_NEW_PETITION, {'action': 'CreatePetitionForm',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.CHAR_PUNISHMENTS, {'action': 'PunishCharacterForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/users.py', mls.USER_BANUSER, {'action': 'BanUserByCharacterID',
             'characterID': characterID}))
            li.append(self.Link('/gm/character.py', mls.WAR_RANKS_MEDALS, {'action': 'RanksAndMedals',
             'characterID': characterID}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_STANDINGS, {'action': 'Standings',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append(self.Link('/gm/owner.py', 'LP Report', {'action': 'ShowCorpLPForCharacter',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', mls.GENERIC_ACCOUNTING, {'action': 'Statement',
             'characterID': characterID,
             'groupID': const.groupCharacter}))
            li.append('>' + self.Link('/gm/accounting.py', mls.UI_GENERIC_CASH, {'action': 'Journal',
             'characterID': characterID,
             'keyID': const.accountingKeyCash,
             'entrTypeFilter': None,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/accounting.py', mls.UI_GENERIC_INSURANCE, {'action': 'Journal',
             'characterID': characterID,
             'keyID': 1000,
             'entryTypeFilter': 19,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/owner.py', mls.UI_GENERIC_BILLS, {'action': 'Bills',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/accounting.py', 'Aruum', {'action': 'Journal',
             'characterID': characterID,
             'keyID': const.accountingKeyAUR,
             'entrTypeFilter': None,
             'subAction': 'last25',
             'groupID': 1,
             'submited': 1}) + self.MidDot() + self.Link('/gm/character.py', mls.CHAR_CREDITS, {'action': 'CharacterCreditsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/accounting.py', mls.CHAR_MASSREVERSAL, {'action': 'MassReversal',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', mls.UI_GENERIC_AGENTS, {'action': 'AgentsForm',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', mls.CHAR_AGENTSSPAWNPOINTS, {'action': 'AgentSpawnpoints',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/certificates.py', mls.UI_SHARED_CERTIFICATES, {'action': 'CharacterCertsDisplay',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/certificates.py', mls.UI_CMD_GIVE + ' ' + mls.UI_SHARED_CERTIFICATES, {'action': 'GiveCertsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/certificates.py', mls.UI_GENERIC_JOURNAL, {'action': 'CharacterCertsJournal',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/contracts.py', mls.UI_CONTRACTS_CONTRACTS, {'action': 'ListForEntity',
             'submit': 1,
             'ownerID': characterID}))
            li.append('>' + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ISSUEDBY, {'action': 'List',
             'submit': 1,
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ISSUEDTO, {'action': 'List',
             'submit': 1,
             'acceptedByID': characterID,
             'filtStatus': const.conStatusInProgress}))
            li.append('>' + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ASSIGNEDTO, {'action': 'List',
             'submit': 1,
             'assignedToID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', mls.CHAR_DESTROYED_SHIPS, {'action': 'ShipsKilled',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', mls.UI_GENERIC_KILLRIGHTS, {'action': 'KillRights',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/character.py', mls.COMMON_KILL + ' ' + mls.GENERIC_REPORT, {'action': 'KillReport',
             'characterID': characterID}))
            li.append('-')
            li.append(self.FontGray(mls.GENERIC_ITEMS))
            li.append('>' + self.Link('/gm/inventory.py', mls.SHARED_FINDITEM, {'action': 'FindItem',
             'ownID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', mls.SYSTEM + '-' + mls.UI_GENERIC_ITEMS, {'action': 'SystemItems',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/inventory.py', 'Find traded items', {'action': 'FindTradedItems',
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', mls.STATION + '-' + mls.UI_GENERIC_ITEMS, {'action': 'StationItems',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', mls.UI_PI_LAUNCHES, {'action': 'PlanataryLaunches',
             'ownID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', mls.SHARED_MOVEMENT, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 3}) + self.MidDot() + self.Link('/gm/logs.py', mls.HD_STANDING, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 6}))
            li.append('>' + self.Link('/gm/logs.py', mls.UI_GENERIC_MISSION, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 9}) + self.MidDot() + self.Link('/gm/logs.py', mls.UI_GENERIC_DAMAGE, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 4}))
            li.append('>' + self.Link('/gm/logs.py', mls.UI_MARKET_MARKET, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 13}) + self.MidDot() + self.Link('/gm/logs.py', mls.UI_INFLIGHT_DUNGEON, {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': 14}))
            li.append('>' + self.Link('/gm/logs.py', mls.SHARED_KILLED + '!', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': -1}) + self.MidDot() + self.Link('/gm/logs.py', mls.UI_GENERIC_MISSION + '!', {'action': 'OwnerEvents',
             'ownerType': const.groupCharacter,
             'ownerID': characterID,
             'eventGroupID': -2}) + self.MidDot() + self.Link('/gm/logs.py', mls.UI_GENERIC_BOUNTY + '!', {'action': 'BountyLog',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', mls.LOG_CARGOACCESS_OTHERCARGOS, {'action': 'CargoAccessLogs',
             'charID': characterID}))
            li.append('>' + self.Link('/gm/logs.py', 'Owned by history', {'action': 'CharacterOwnedBy',
             'charID': characterID}))
            li.append('-')
            li.append(self.FontGray(mls.CHAR_NOTIFICATIONS))
            newLine = True
            line = ''
            groupNames = notificationUtil.groupNames.items()
            revNames = [ [v[1], v[0]] for v in groupNames ]
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
            li.append(self.FontGray(mls.UI_MARKET_MARKET))
            li.append('>' + self.Link('/gm/owner.py', mls.UI_GENERIC_ORDERS, {'action': 'Orders',
             'groupID': const.groupCharacter,
             'ownID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', mls.UI_GENERIC_TRANSACTIONS, {'action': 'Transactions',
             'groupID': const.groupCharacter,
             'ownID': characterID}))
            li.append('-')
            li.append(self.FontGray(mls.CHAR_MESSAGES))
            li.append('>' + self.Link('/gm/owner.py', mls.CHAR_RECEIVED, {'action': 'Messages',
             'charID': characterID}) + self.MidDot() + self.Link('/gm/owner.py', mls.CHAR_SENT, {'action': 'SentMessages',
             'charID': characterID}))
            li.append('>' + self.Link('/gm/owner.py', mls.UI_SHARED_MAILINGLISTS, {'action': 'MailingLists',
             'charID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', mls.GENERIC_MOVE, {'action': 'MoveCharacterForm',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', mls.CHAR_LASTSTATION, {'action': 'MoveCharacter',
             'characterID': characterID,
             'stationID': 0,
             'moveShipIfApplicable': 'on'}) + self.MidDot() + self.Link('/gm/character.py', mls.CHAR_LASTSYSTEM, {'action': 'MoveCharacter',
             'characterID': characterID,
             'solarSystemID': 0,
             'moveShipIfApplicable': 'on'}))
            li.append('-')
            li.append(self.FontGray('Science & Industry'))
            li.append('>' + self.Link('/gm/ram.py', mls.UI_CORP_JOBS, {'action': 'JobsOwner',
             'ownerID': characterID,
             'groupID': const.groupCharacter}) + self.MidDot() + self.Link('/gm/ram.py', mls.STATION_ASSEMBLYLINES, {'action': 'AssemblyLinesOwner',
             'ownerID': characterID,
             'groupID': const.groupCharacter}))
            li.append('>' + self.Link('/gm/ram.py', mls.UI_CMD_GIVE + '-' + mls.BLUEPRINT, {'action': 'GiveBlueprint',
             'characterID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/planets.py', mls.UI_GENERIC_PLANETS, {'action': 'PlanetsByOwner',
             'ownerID': characterID}))
            li.append('-')
            li.append(self.Link('/gm/character.py', mls.UI_GENERIC_SKILLS, {'action': 'CharacterSkills',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/skilljournal.py', mls.UI_CMD_GIVE + '-' + mls.UI_GENERIC_SKILLS, {'action': 'CharacterSkillsForm',
             'characterID': characterID}) + self.MidDot() + self.Link('/gm/skilljournal.py', mls.CHAR_SKILLJOURNAL, {'action': 'CharacterSkillsJournal',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', mls.CHAR_SKILLQUEUE, {'action': 'SkillQueue',
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
            li.append('>' + self.Link('/gm/character.py', 'Paper doll history', {'action': 'PaperdollHistory',
             'characterID': characterID}))
            li.append('>' + self.Link('/gm/character.py', 'Flags', {'action': 'PaperdollFlags',
             'characterID': characterID}))
            if prefs.clusterMode != 'LIVE' and session.role & ROLE_CONTENT > 0:
                li.append('>' + self.Link('/gm/character.py', 'Copy paperdoll', {'action': 'PaperdollCharacterCopy',
                 'characterID': characterID}))
            self.SubjectActions(li, menuPlacement)



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
            li.append(self.Link('/gm/corporation.py', mls.CORP_ALLIANCERECORDS, {'action': 'AllianceRecords',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/logs.py', mls.CHAR_AUDITLOG, {'action': 'AuditLog',
             'logGroup': const.groupCorporation,
             'corporationID': corporationID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupCorporation,
             'ownerID': corporationID}) + self.MidDot() + self.Link('/gm/logs.py', mls.LOG_CARGOACCESS_OTHERCARGOS, {'action': 'CargoAccessLogs',
             'charID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Bulletins', {'action': 'Bulletins',
             'ownerID': corporationID}))
            if not util.IsNPC(corporationID):
                now = time.gmtime()
                li.append(self.Link('/gm/calendar.py', mls.UI_CAL_CALENDAR, {'action': 'FindByOwner',
                 'ownerID': corporationID,
                 'ownerType': const.groupCorporation,
                 'fromMonth': 1,
                 'fromYear': const.calendarStartYear,
                 'toMonth': 1,
                 'toYear': now[0] + 1}))
            li.append(self.Link('/gm/owner.py', mls.UI_CONTACTS_CONTACTS, {'action': 'Contacts',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append(self.Link('/gm/corporation.py', '%s %s' % (mls.UI_GENERIC_GAG, mls.UI_CORP_CORP), {'action': 'GagCorporationForm',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', '%s %s' % (mls.UI_GENERIC_UNGAG, mls.UI_CORP_CORP), {'action': 'UnGagCorporation',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.CORP_LOCKEDITEMS, {'action': 'LockedItems',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.COMMON_KILL + ' ' + mls.GENERIC_REPORT, {'action': 'KillReport',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.UI_GENERIC_MEDALS, {'action': 'Medals',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/faction.py', mls.GENERIC_MILITIASTATS, {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Corporate Registry Ads', {'action': 'CorporateRegistry',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/owner.py', mls.UI_CORP_OFFICES, {'action': 'RentableItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID,
             'typID': 26}))
            li.append(self.Link('/gm/corporation.py', mls.SHARED_HDROLES, {'action': 'Roles',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.CORP_SHAREHOLDERS, {'action': 'ViewShareholders',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', mls.UI_GENERIC_SHARES, {'action': 'CreateCorporationSharesForm',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_STANDINGS, {'action': 'Standings',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.UI_GENERIC_STATIONS, {'action': 'Stations',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', 'Starbases', {'action': 'Starbases',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.UI_CORP_TITLES, {'action': 'Titles',
             'corporationID': corporationID}))
            li.append(self.Link('/gm/corporation.py', mls.MARKET_TRADES, {'action': 'Trades',
             'corporationID': corporationID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', mls.GENERIC_ACCOUNTING, {'action': 'Statement',
             'characterID': corporationID,
             'groupID': const.groupCorporation}))
            li.append('>' + self.Link('/gm/accounting.py', mls.UI_GENERIC_CASH, {'action': 'Journal',
             'characterID': corporationID,
             'keyID': const.accountingKeyCash,
             'entryTypeFilter': None,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}) + self.MidDot() + self.Link('/gm/accounting.py', mls.UI_GENERIC_INSURANCE, {'action': 'Journal',
             'characterID': corporationID,
             'keyID': 1000,
             'entryTypeFilter': 19,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}))
            li.append('>' + self.Link('/gm/owner.py', mls.UI_GENERIC_BILLS, {'action': 'Bills',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', mls.CHAR_CREDITS, {'action': 'CorporationCreditsForm',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/accounting.py', mls.CHAR_MASSREVERSAL, {'action': 'MassReversal',
             'characterID': corporationID}) + self.MidDot() + self.Link('/gm/accounting.py', 'Aurum', {'action': 'Journal',
             'characterID': corporationID,
             'keyID': const.accountingKeyAUR,
             'entryTypeFilter': None,
             'subAction': 'last25',
             'groupID': const.groupCorporation,
             'submited': 1}))
            li.append('-')
            li.append(self.Link('/gm/contracts.py', mls.UI_CONTRACTS_CONTRACTS, {'action': 'ListForEntity',
             'submit': 1,
             'ownerID': corporationID}))
            li.append('>' + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ISSUEDBY, {'action': 'List',
             'submit': 1,
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ISSUEDTO, {'action': 'List',
             'submit': 1,
             'acceptedByID': corporationID,
             'filtStatus': const.conStatusInProgress}))
            li.append('>' + self.Link('/gm/contracts.py', mls.UI_CONTRACTS_ASSIGNEDTO, {'action': 'List',
             'submit': 1,
             'assignedToID': corporationID}))
            li.append('-')
            li.append('!Items')
            li.append('>' + self.Link('/gm/inventory.py', mls.SHARED_FINDITEM, {'action': 'FindItem',
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', mls.SYSTEM + '-' + mls.UI_GENERIC_ITEMS, {'action': 'SystemItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('>' + self.Link('/gm/owner.py', mls.STATION + '-' + mls.UI_GENERIC_ITEMS, {'action': 'StationItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', mls.UI_CORP_OFFICE + '-' + mls.UI_GENERIC_ITEMS, {'action': 'OfficeItems',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('>' + self.Link('/gm/corporation.py', mls.SHARED_FINDITEM + ' ' + mls.UI_CORP_MEMBERS, {'action': 'FindItemsOnMembers',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!Market')
            li.append('>' + self.Link('/gm/owner.py', mls.UI_GENERIC_ORDERS, {'action': 'Orders',
             'groupID': const.groupCorporation,
             'ownID': corporationID}) + self.MidDot() + self.Link('/gm/owner.py', mls.UI_GENERIC_TRANSACTIONS, {'action': 'Transactions',
             'groupID': const.groupCorporation,
             'ownID': corporationID}))
            li.append('-')
            li.append(self.Link('/gm/corporation.py', mls.UI_CORP_MEMBERS, {'action': 'SimplyViewMembers',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/corporation.py', mls.CORP_COMPLEXMEMEBERS, {'action': 'ViewMembers',
             'corporationID': corporationID}))
            li.append('>' + self.Link('/gm/petition.py', mls.UI_CORP_MEMBERS + ' Petitions', {'action': 'CorpPetitions',
             'corpID': corporationID}))
            li.append('-')
            li.append('!Notes')
            li.append('>' + self.Link('/gm/corporation.py', mls.UI_CORP_CORP, {'action': 'Notes',
             'corporationID': corporationID}) + self.MidDot() + self.Link('/gm/corporation.py', mls.UI_CORP_MEMBERS + '(' + mls.GENERIC_USERS + ')', {'action': 'NotesForCorp',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!' + mls.CORP_SANCTIONEDACTIONS)
            li.append('>' + self.Link('/gm/corporation.py', mls.UI_CORP_INEFFECT, {'action': 'ViewSanctionableActions',
             'corporationID': corporationID,
             'inEffect': 1}) + self.MidDot() + self.Link('/gm/corporation.py', mls.UI_CORP_NOTINEFFECT, {'action': 'ViewSanctionableActions',
             'corporationID': corporationID,
             'inEffect': 0}))
            li.append('-')
            li.append('!' + mls.UI_RMR_SCIENCEANDINDUSTRY)
            li.append('>' + self.Link('/gm/ram.py', mls.UI_CORP_JOBS, {'action': 'JobsOwner',
             'ownerID': corporationID,
             'groupID': const.groupCorporation}) + self.MidDot() + self.Link('/gm/ram.py', mls.STATION_ASSEMBLYLINES, {'action': 'AssemblyLinesOwner',
             'ownerID': corporationID,
             'groupID': const.groupCorporation}))
            li.append('-')
            li.append('!' + mls.WAR_WARS)
            li.append('>' + self.Link('/gm/war.py', mls.UI_GENERIC_ACTIVE, {'action': 'ViewWars',
             'ownerID': corporationID,
             'onlyActive': 1}) + self.MidDot() + self.Link('/gm/war.py', mls.UI_GENERIC_ALL, {'action': 'ViewWars',
             'ownerID': corporationID,
             'onlyActive': 0}) + self.MidDot() + self.Link('/gm/corporation.py', mls.UI_GENERIC_FACTION, {'action': 'ViewFactionWarsForCorp',
             'corporationID': corporationID}))
            li.append('-')
            li.append('!' + mls.UI_CMD_VOTES)
            li.append('>' + self.Link('/gm/corporation.py', mls.UI_GENERIC_OPEN, {'action': 'ViewVotes',
             'corporationID': corporationID,
             'isOpen': 1}) + self.MidDot() + self.Link('/gm/corporation.py', mls.UI_GENERIC_CLOSED, {'action': 'ViewVotes',
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
            info = self.SplitAdd(info, util.FmtDate(a.startDate, 'ln'), ', ')
            lines.append([0, 'Info', info])
            if a.url:
                lines.append([0, 'web', a.url])
            self.SubjectHeader(smallHeader, 'ALLIANCE', allianceID, self.OwnerName(allianceID), '#D7AFAF', image, '/gm/alliance.py', 'Alliance', 'allianceID', lines)
            li = []
            li.append('#ALLIANCE')
            li.append(self.Link('/gm/alliance.py', 'INFO', {'action': 'Alliance',
             'allianceID': allianceID}))
            li.append('-')
            li.append(self.Link('/gm/accounting.py', mls.GENERIC_ACCOUNTING, {'action': 'Statement',
             'characterID': allianceID,
             'groupID': const.groupAlliance}))
            li.append(self.Link('/gm/alliance.py', mls.UI_CORP_APPLICATIONS, {'action': 'ViewApplications',
             'allianceID': allianceID}))
            now = time.gmtime()
            li.append(self.Link('/gm/calendar.py', mls.UI_CAL_CALENDAR, {'action': 'FindByOwner',
             'ownerID': allianceID,
             'ownerType': const.groupAlliance,
             'fromMonth': 1,
             'fromYear': const.calendarStartYear,
             'toMonth': 1,
             'toYear': now[0] + 1}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_BILLS, {'action': 'Bills',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/alliance.py', mls.ALLI_BILLSPAYABLEBYGMH, {'action': 'ViewBills',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/corporation.py', 'Bulletins', {'action': 'Bulletins',
             'ownerID': allianceID}))
            li.append(self.Link('/gm/owner.py', mls.UI_CONTACTS_CONTACTS, {'action': 'Contacts',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/inventory.py', mls.SHARED_FINDITEM, {'action': 'FindItem',
             'ownID': allianceID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupAlliance,
             'ownerID': allianceID}))
            li.append(self.Link('/gm/alliance.py', mls.UI_CORP_MEMBERS, {'action': 'ViewMembers',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/alliance.py', mls.UI_GENERIC_NOTES, {'action': 'Notes',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/alliance.py', mls.UI_CORP_RANKINGS, {'action': 'Rankings'}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_STANDINGS, {'action': 'Standings',
             'groupID': const.groupAlliance,
             'ownID': allianceID}))
            li.append(self.Link('/gm/alliance.py', mls.UI_SHARED_MAPSOVEREIGNTY + ' ' + mls.GENERIC_BILLCAPB, {'action': 'Sovereignty',
             'allianceID': allianceID}))
            li.append(self.Link('/gm/war.py', mls.WAR_WARS + '(' + mls.UI_GENERIC_ACTIVE + ')', {'action': 'ViewWars',
             'ownerID': allianceID,
             'onlyActive': 1}))
            li.append(self.Link('/gm/war.py', mls.WAR_WARS + '(' + mls.UI_GENERIC_ALL + ')', {'action': 'ViewWars',
             'ownerID': allianceID,
             'onlyActive': 0}))
            self.SubjectActions(li, menuPlacement)
            return a



        def FactionHeader(self, factionID, smallHeader = 1, menuPlacement = 'rMenu'):
            f = self.cache.Index(const.cacheChrFactions, factionID)
            image = '/img/faction%s.jpg' % factionID
            self.SubjectHeader(smallHeader, 'FACTION', factionID, f.factionName, '#E8E8FF', image, '/gm/faction.py', 'Faction', 'factionID', [[1, 'System', self.SystemLink(f.solarSystemID)], [1, 'Corporation', self.CorporationLink(f.corporationID)]])
            li = []
            li.append('#FACTION')
            li.append(self.Link('/gm/faction.py', 'INFO', {'action': 'Faction',
             'factionID': factionID}))
            li.append('-')
            li.append(self.Link('/gm/faction.py', mls.UI_GENERIC_CORPORATIONS, {'action': 'Corporations',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', mls.UI_FACWAR_FACWARCORPS, {'action': 'FactionalWarfareCorporations',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', mls.GENERIC_MILITIASTATS, {'action': 'FactionalWarfareStatisticsForEntity',
             'entityID': factionID}))
            li.append(self.Link('/gm/faction.py', mls.FACTION_DISTRIBUTIONS, {'action': 'Distributions',
             'factionID': factionID}))
            li.append(self.Link('/gm/faction.py', mls.FACTION_TERRITORY, {'action': 'Territory',
             'factionID': factionID}))
            li.append(self.Link('/gm/logs.py', 'Events', {'action': 'OwnerEvents',
             'ownerType': const.groupFaction,
             'ownerID': factionID}))
            li.append(self.Link('/gm/owner.py', mls.UI_GENERIC_STANDINGS, {'action': 'Standings',
             'groupID': const.groupFaction,
             'ownID': factionID}))
            self.SubjectActions(li, menuPlacement)
            return f



        def CharacterLocationText(self, characterID, locationID, locationTypeID, locationLocationID):
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
                    s += self.FontHeaderProperty(mls.SYSTEM.upper())
                    s += ':<br>%s' % self.SystemLink(locationID)
                else:
                    s += self.FontHeaderProperty(mls.STATION.upper())
                    s += ':<br>%s' % self.StationLink(locationID)
                    s += ' - %s' % self.SystemLink(solarSystemID)
                if shipID:
                    s += '<br>' + self.FontHeaderProperty(mls.SHIP.upper()) + ':<br>%s' % self.Link('/gm/character.py', cfg.evelocations.Get(shipID).locationName, {'action': 'Ship',
                     'characterID': characterID,
                     'shipID': shipID})
                    s += '<br>' + self.FontProperty(mls.TYPE) + ': %s' % cfg.invtypes.Get(locationTypeID).typeName
            except:
                s = '<font color=red>Invalid Location: %s</font>' % locationID
            return s



        def FormatDateTime(self, dt):
            dtNow = blue.win32.GetSystemTimeAsFileTime()
            diff = dtNow - dt
            numMinutes = diff / 10000000.0 / 60
            numDays = numMinutes / 60 / 24
            dTimeFmt = util.FmtDate(dt, 'ns')
            dst = util.FmtDate(dt, 'sn')
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
            dn = util.FmtDate(dtNow, 'ns')
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
            image = '/img/type.jpg'
            t = cfg.invtypes.GetIfExists(typeID)
            if t is not None:
                if t.categoryID in (const.categoryBlueprint,
                 const.categoryDeployable,
                 const.categoryDrone,
                 const.categoryShip,
                 const.categoryStructure,
                 const.categoryStation,
                 const.categorySovereigntyStructure,
                 const.categoryPlanetaryInteraction):
                    image = 'http://wiki.eveonline.com/wikiEN/images_icons/%sx%s/%s.png' % (width, width, typeID)
                elif t.iconID:
                    image = 'http://wiki.eveonline.com/wikiEN/images_icons/iconID_%s.png' % t.iconID
            return image



        def TypeHeader(self, typeID, typeAction = 'Type'):
            typeName = ''
            groupID = -1
            categoryID = -1
            rs = self.DB2.SQLInt('*', 'inventory.types', '', '', 'typeID', typeID)
            if len(rs) == 0:
                r = None
            else:
                r = rs[0]
                typeName = r.typeName
                groupID = r.groupID
                group = cfg.invgroups.GetIfExists(groupID)
                if group is None:
                    categoryID = None
                else:
                    categoryID = group.categoryID
            lines = []
            lines.append([1, 'Group', self.GroupLink(groupID)])
            lines.append([1, 'Category', self.CategoryLink(categoryID)])
            self.SubjectHeader(1, 'TYPE', typeID, typeName, '#C0C0C0', self.TypeImage(typeID), '/gd/type.py', 'Type', 'typeID', lines, 64, 64)
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
        dGMH = not session.role & ROLE_GMH
        dGML = not session.role & ROLE_GML
        dCONTENT = not session.role & ROLE_CONTENT
        dADMIN = not session.role & ROLE_ADMIN
        dVIEW = not session.role & ROLEMASK_VIEW
        dDBA = not session.role & ROLE_DBA
        dPROG = not session.role & ROLE_PROGRAMMER
        dMARKET = not session.role & ROLE_MARKET
        dMARKETH = not session.role & ROLE_MARKETH
        dTRL = not session.role & ROLE_TRANSLATION
        dTRE = not session.role & ROLE_TRANSLATIONEDITOR
        dTRADMIN = not session.role & ROLE_TRANSLATIONADMIN
        dTRQA = not session.role & ROLE_TRANSLATIONTESTER
        if macho.mode == 'server':
            writer.inserts['icon'] = writer.Link('/gm/search.py', writer.Image('/img/menu_search32.jpg', 'width=32 height=32'))
            writer.AddTopMenuSubLine('GM')
            writer.AddTopMenuSub('GM', mls.UI_CMD_SEARCH, '/gm/search.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.SHARED_FINDITEM, '/gm/inventory.py?action=FindItem', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.ITEM + ' ' + mls.GENERIC_REPORT, '/gm/inventory.py?action=Item', disabled=dVIEW)
            writer.AddTopMenuSubLine('GM')
            writer.AddTopMenuSub('GM', mls.UI_GENERIC_ALLIANCES, '/gm/alliance.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_CAL_CALENDAR, '/gm/calendar.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_CONTRACTS_CONTRACTS, '/gm/contracts.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_GENERIC_CORPORATIONS, '/gm/corporation.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_GENERIC_FACTIONS, '/gm/faction.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Fleets', '/gm/fleet.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Inventory', '/gm/inventory.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.STARBASE_STARBASES, '/gm/starbase.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_GENERIC_STATIONS, '/gm/stations.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Tale', '/gm/tale.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', mls.UI_GENERIC_PLANETS, '/gm/planets.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Voice Chat', '/gm/voice.py', disabled=dVIEW)
            writer.AddTopMenuSub('GM', 'Virtual Store', '/gm/store.py', disabled=dVIEW)
            if prefs.GetValue('enableDust', 0) == 1:
                writer.AddTopMenuSubLine('GM')
                writer.AddTopMenuSub('GM', 'Battles', '/dust/battles.py', disabled=dVIEW)
            writer.AddTopMenuSub('PETITION', 'My Petitions', '/gm/petitionClient.py?action=ShowMyPetitions', disabled=dVIEW)
            writer.AddTopMenuSubLine('PETITION')
            writer.AddTopMenuSub('PETITION', mls.PETI_ANSWERPETITIONS, '/gm/petitionClient.py?action=ShowClaimedPetitions', disabled=dVIEW)
            writer.AddTopMenuSub('PETITION', mls.UI_GENERIC_KNOWLEDGEBASE, '/gm/knowledgebase.py', disabled=dCONTENT)
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
        elif macho.mode == 'proxy':
            pass
        elif macho.mode == 'client':
            pass
        if macho.mode == 'server':
            if menu == 'GM':
                writer.AddMenu('Search', mls.UI_CMD_SEARCH, '', '/gm/search.py')
                writer.AddMenu('Alliances', mls.UI_GENERIC_ALLIANCES, '', '/gm/alliance.py')
                writer.AddMenu('Contracts', mls.UI_CONTRACTS_CONTRACTS, '', '/gm/contracts.py')
                writer.AddMenu('Corporations', mls.UI_GENERIC_CORPORATIONS, '', '/gm/corporation.py')
                writer.AddMenu('Factions', mls.UI_GENERIC_FACTIONS, '', '/gm/faction.py')
                writer.AddMenu('Inventory', 'Inventory', '', '/gm/inventory.py')
                writer.AddMenu('Starbases', mls.STARBASE_STARBASES, '', '/gm/starbase.py')
                writer.AddMenu('Stations', mls.UI_GENERIC_STATIONS, '', '/gm/stations.py')
            elif menu == 'PETITION':
                writer.AddMenu('AnswerPetitions', mls.PETI_ANSWERPETITIONS, '', '/gm/petitionClient.py?action=ShowClaimedPetitions')
                writer.AddMenu('KnowledgeBase', mls.UI_GENERIC_KNOWLEDGEBASE, '', '/gm/knowledgebase.py')
                writer.AddMenu('PetitionManagement', 'Petition Management', '', '/gm/petition.py')
                writer.AddMenu('SupportManagement', 'Support Management', '', '/gm/supportManagement.py')
                writer.AddMenu('SpamReports', 'Spam Reports', '', '/gm/users.py?action=ListSpamUsers')
                writer.AddMenu('Characters', mls.UI_GENERIC_CHARACTERS, '', '/gm/character.py')
                writer.AddMenu('Users', mls.GENERIC_USERS, '', '/gm/users.py')
                writer.AddMenu('Search', mls.UI_CMD_SEARCH, '', '/gm/search.py')
                writer.AddMenu('ItemReport', mls.ITEM + ' ' + mls.GENERIC_REPORT, '', '/gm/inventory.py?action=Item')
                writer.AddMenu('FindItem', mls.SHARED_FINDITEM, '', '/gm/inventory.py?action=FindItem')
                writer.AddMenu('My Characters', mls.CHAR_MYCHARACTERS, '', '/gm/character.py?action=MyCharacters')
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

