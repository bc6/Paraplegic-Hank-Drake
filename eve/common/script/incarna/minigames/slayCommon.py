import os
import util
import math
import random
import slayConst
import minigameConst

def GenerateAIID():
    return -random.randrange(1, 1000000)



def GetFactionNameByColor(colorEnum):
    lookup = {slayConst.COLOR_1: 'Magenta',
     slayConst.COLOR_2: 'Purple',
     slayConst.COLOR_3: 'Green',
     slayConst.COLOR_4: 'Blue',
     slayConst.COLOR_5: 'Orange',
     slayConst.COLOR_6: 'Yellow'}
    if colorEnum in lookup:
        return lookup[colorEnum]
    else:
        return 'White'



def ColorEnum():
    return {slayConst.COLOR_1: (226.0 / 255.0, 0.0, 112.0 / 255.0),
     slayConst.COLOR_2: (121.0 / 255.0, 0.0 / 255.0, 156.0 / 255.0),
     slayConst.COLOR_3: (12.0 / 255.0, 244.0 / 255.0, 0.0 / 255.0),
     slayConst.COLOR_4: (23.0 / 255.0, 187.0 / 255.0, 247.0 / 255.0),
     slayConst.COLOR_5: (255.0 / 255.0, 121.0 / 255.0, 1.0 / 255.0),
     slayConst.COLOR_6: (255.0 / 255.0, 255.0 / 255.0, 10.0 / 255.0),
     slayConst.COLOR_7: (1.0, 1.0, 1.0),
     slayConst.UNUSED_SLOT: (0.2, 0.2, 0.2)}



def ColorEnumToRGB(colorEnum):
    lookup = ColorEnum()
    if colorEnum in lookup:
        return lookup[colorEnum]
    else:
        return (1.0, 1.0, 1.0)



def IsAIPlayer(id):
    if not isinstance(id, int):
        return False
    return id < 0



class SlayData():
    __guid__ = 'slaycommon.SlayData'

    def __init__(self):
        self.tiles = {}
        self.length = 0
        self.height = 0



    def LoadMapFromRaw(self, rawTableData, length, height):
        self.length = length
        self.height = height
        self.tiles = {}
        for key in rawTableData:
            tile = SlayTile()
            tile.FromRaw(rawTableData[key])
            self.tiles[tile.tileID] = tile

        self.ReconstructNeighbours()



    def GetLength(self):
        return self.length



    def GetHeight(self):
        return self.height



    def InitData(self, length, height, hexagonMap = False):
        self.tiles = {}
        self.length = length
        self.height = height
        for y in range(0, height):
            for x in range(0, length):
                tileID = '%s.%s' % (x, y)
                tile = SlayTile(x, y, tileID)
                self.tiles[tileID] = tile
                if x > 0:
                    if x % 2 == 0:
                        self.SetNeighbours(self.GetTile(x - 1, y), tile, 2, 5)
                    else:
                        self.SetNeighbours(self.GetTile(x - 1, y), tile, 3, 6)
                if y > 0:
                    self.SetNeighbours(self.GetTile(x, y - 1), tile, 4, 1)
                    if x + 1 < length and x % 2 == 0:
                        self.SetNeighbours(self.GetTile(x + 1, y - 1), tile, 5, 2)
                if x > 0 and y > 0 and x % 2 == 0:
                    self.SetNeighbours(self.GetTile(x - 1, y - 1), tile, 3, 6)


        removeTiles = []
        if hexagonMap:
            for key in self.tiles:
                tile = self.tiles[key]
                if tile.tileID in self.GetNonHexagonTiles():
                    removeTiles.append(tile)

        for tile in removeTiles:
            self.RemoveTile(tile)




    def CompileState(self):
        compiled = {}
        for tileID in self.tiles:
            tile = self.tiles[tileID]
            compiled[tileID] = (tile.owner,
             tile.occupier.unitID,
             tile.color,
             tile.areaKey)

        return compiled



    def RestoreState(self, state):
        for tileID in state:
            inState = state[tileID]
            self.tiles[tileID].owner = inState[0]
            self.tiles[tileID].occupier = SlayUnit(inState[1])
            self.tiles[tileID].color = inState[2]
            self.tiles[tileID].areaKey = inState[3]




    def GetNonHexagonTiles(self):
        return ['0.0',
         '1.0',
         '2.0',
         '3.0',
         '4.0',
         '5.0',
         '6.0',
         '7.0',
         '8.0',
         '10.0',
         '11.0',
         '12.0',
         '13.0',
         '14.0',
         '15.0',
         '16.0',
         '17.0',
         '0.1',
         '1.1',
         '2.1',
         '3.1',
         '6.1',
         '12.1',
         '13.1',
         '14.1',
         '15.1',
         '16.1',
         '17.1',
         '4.1',
         '3.1',
         '5.1',
         '3.2',
         '4.2',
         '0.2',
         '1.2',
         '2.2',
         '14.2',
         '15.2',
         '16.2',
         '17.2',
         '3.15',
         '3.16',
         '5.16',
         '0.3',
         '1.3',
         '2.3',
         '16.3',
         '17.3',
         '9.17',
         '11.16',
         '13.15',
         '15.14',
         '17.13',
         '0.4',
         '0.14',
         '1.14',
         '16.14',
         '17.14',
         '0.15',
         '1.15',
         '2.15',
         '14.15',
         '15.15',
         '16.15',
         '17.15',
         '0.16',
         '1.16',
         '2.16',
         '3.16',
         '4.16',
         '12.16',
         '13.16',
         '14.16',
         '15.16',
         '16.16',
         '17.16',
         '0.17',
         '1.17',
         '2.17',
         '3.17',
         '4.17',
         '5.17',
         '6.17',
         '7.17',
         '10.17',
         '11.17',
         '12.17',
         '13.17',
         '14.17',
         '15.17',
         '16.17',
         '17.17',
         '9.0',
         '10.1',
         '11.1',
         '12.2',
         '13.2',
         '14.3',
         '15.3',
         '16.4',
         '17.4',
         '17.5',
         '17.6',
         '17.7',
         '17.8',
         '17.9',
         '17.10',
         '17.11',
         '17.12']



    def ReconstructNeighbours(self):
        for key in self.tiles:
            tile = self.tiles[key]
            if tile.x % 2 == 0:
                tile.neighbour1 = self.GetTile(tile.x, tile.y - 1)
                tile.neighbours[0] = tile.neighbour1
                tile.neighbour2 = self.GetTile(tile.x + 1, tile.y - 1)
                tile.neighbours[1] = tile.neighbour2
                tile.neighbour3 = self.GetTile(tile.x + 1, tile.y)
                tile.neighbours[2] = tile.neighbour3
                tile.neighbour4 = self.GetTile(tile.x, tile.y + 1)
                tile.neighbours[3] = tile.neighbour4
                tile.neighbour5 = self.GetTile(tile.x - 1, tile.y)
                tile.neighbours[4] = tile.neighbour5
                tile.neighbour6 = self.GetTile(tile.x - 1, tile.y - 1)
                tile.neighbours[5] = tile.neighbour6
            else:
                tile.neighbour1 = self.GetTile(tile.x, tile.y - 1)
                tile.neighbours[0] = tile.neighbour1
                tile.neighbour2 = self.GetTile(tile.x + 1, tile.y)
                tile.neighbours[1] = tile.neighbour2
                tile.neighbour3 = self.GetTile(tile.x + 1, tile.y + 1)
                tile.neighbours[2] = tile.neighbour3
                tile.neighbour4 = self.GetTile(tile.x, tile.y + 1)
                tile.neighbours[3] = tile.neighbour4
                tile.neighbour5 = self.GetTile(tile.x - 1, tile.y + 1)
                tile.neighbours[4] = tile.neighbour5
                tile.neighbour6 = self.GetTile(tile.x - 1, tile.y)
                tile.neighbours[5] = tile.neighbour6




    def LoadMap(self, mapName):
        toHex = lambda x: ''.join([ hex(ord(c))[2:].zfill(2) for c in x ])
        map = open('C:\\depot\\eve\\WiS\\common\\script\\wis\\minigames\\spiral2.isl')
        map.seek(4)
        xSize = 35
        fileSizeX = int(toHex(map.read(1)))
        map.seek(8)
        ySize = 22
        fileSizeY = int(toHex(map.read(1)))
        self.InitData(xSize, ySize)
        rowSize = 140
        fileInfo = os.stat('C:\\depot\\eve\\WiS\\common\\script\\wis\\minigames\\spiral2.isl')
        totalFileRead = int(math.ceil((fileInfo.st_size - 156) / rowSize))
        hexagons = []
        for y in xrange(0, totalFileRead):
            currPos = 156 + y * rowSize
            map.seek(currPos)
            row = []
            toRead = currPos + rowSize
            for filePos in xrange(currPos, toRead):
                row.append(int(toHex(map.read(1))))

            segEqu = 0
            segOdd = 1
            currPos = 0
            while currPos < len(row):
                if currPos < 68:
                    hexagons.append((segEqu, y, row[currPos]))
                    segEqu += 2
                if currPos > 68 and currPos <= 132:
                    hexagons.append((segOdd, y, row[currPos]))
                    segOdd += 2
                currPos += 4


        map.close()
        level = []
        for item in hexagons:
            if item[2] != 0:
                x = item[0]
                y = item[1]
                tile = self.GetTile(x, y)
                level.append(tile)

        removeTiles = []
        for key in self.tiles:
            tile = self.tiles[key]
            if tile not in level:
                removeTiles.append(tile)

        for removeTile in removeTiles:
            self.RemoveTile(removeTile)




    def MakeMapRandom(self, maxNumTiles = None, fixedSeed = None):
        if fixedSeed != None:
            random.seed(fixedSeed)
        if maxNumTiles == None:
            maxNumTiles = len(self.tiles.keys()) / 2
        if maxNumTiles > self.length * self.height:
            self.maxNumTiles = self.length * self.height
        tile = self.GetTile(self.length / 2, self.height / 2)
        level = self._CreateRandomMap(maxNumTiles, tile, [])
        removeTiles = []
        for key in self.tiles:
            tile = self.tiles[key]
            if tile not in level:
                removeTiles.append(tile)

        for removeTile in removeTiles:
            self.RemoveTile(removeTile)

        maxTotal = 660 / 2
        count = 0
        for key in self.tiles:
            if self.tiles[key] is not None:
                count += 1

        perc = float(count) / float(maxTotal)
        numPineTrees = 20 * perc
        maxiter = 50
        while numPineTrees > 0 and maxiter > 0:
            for key in self.tiles:
                tile = self.tiles[key]
                if tile is not None and self.IsCoast(tile) == False and tile.occupier.unitID != slayConst.OCCUPY_PINEFOREST:
                    chance = random.randrange(0, 101)
                    if chance <= 15:
                        tile.occupier = SlayUnit(slayConst.OCCUPY_PINEFOREST)
                        numPineTrees -= 1
                if numPineTrees <= 0:
                    break

            maxiter -= 1

        numPalmTrees = 6 * perc
        maxiter = 50
        while numPalmTrees > 0 and maxiter > 0:
            for key in self.tiles:
                tile = self.tiles[key]
                if tile is not None and self.IsCoast(tile) == True and tile.occupier.unitID != slayConst.OCCUPY_PALMFOREST:
                    chance = random.randrange(0, 101)
                    if chance <= 15:
                        tile.occupier = SlayUnit(slayConst.OCCUPY_PALMFOREST)
                        numPalmTrees -= 1
                if numPalmTrees <= 0:
                    break

            maxiter -= 1




    def _CreateRandomMap(self, maxNumTiles, tile, group):
        if tile != None and len(group) < maxNumTiles and tile not in group:
            group.append(tile)
            isInCenterZone = self.IsCenterZone(tile)
            if isInCenterZone:
                startLimit = 70
            else:
                startLimit = 0
            flip = random.randrange(0, 2)
            if flip == 0:
                for i in range(1, 7):
                    probPursue = random.randrange(startLimit, 101)
                    neighbour = getattr(tile, 'neighbour%s' % i)
                    if probPursue >= 70 and neighbour not in group:
                        self._CreateRandomMap(maxNumTiles, neighbour, group)

            else:
                i = 6
                while i > 0:
                    probPursue = random.randrange(startLimit, 101)
                    neighbour = getattr(tile, 'neighbour%s' % i)
                    if probPursue >= 70 and neighbour not in group:
                        self._CreateRandomMap(maxNumTiles, neighbour, group)
                    i -= 1

            return group
        else:
            return group



    def GetRaw(self):
        rawData = {}
        for key in self.tiles:
            tile = self.tiles[key]
            if tile is not None:
                rawData[tile.tileID] = tile.GetRaw()

        return rawData



    def GetRawDelta(self, lastRaw):
        if lastRaw is None:
            return self.GetRaw()
        rawData = {}
        for key in self.tiles:
            tile = self.tiles[key]
            lastRawTile = SlayTile()
            lastRawTile.FromRaw(lastRaw[tile.tileID])
            if not lastRawTile.Compare(tile):
                rawData[tile.tileID] = tile.GetRaw()

        return rawData



    def PrintOut(self):
        for y in range(0, self.height):
            string = ''
            for x in range(0, self.length):
                tile = self.GetTile(x, y)
                if tile == None:
                    string += 'o'
                else:
                    string += '*'

            print string




    def IsCenterZone(self, tile):
        zoneSizeX = self.length / 4
        zoneSizeY = self.height / 4
        if tile.x < self.length - zoneSizeX and tile.x > zoneSizeX:
            if tile.y < self.height - zoneSizeY and tile.y > zoneSizeY:
                return True
        return False



    def SetNeighbours(self, tile1, tile2, pos1, pos2):
        attribute1 = 'neighbour%s' % pos1
        attribute2 = 'neighbour%s' % pos2
        setattr(tile1, attribute1, tile2)
        setattr(tile2, attribute2, tile1)
        tile1.neighbours[pos1 - 1] = tile2
        tile2.neighbours[pos2 - 1] = tile1



    def GetTile(self, x, y):
        tileID = '%s.%s' % (x, y)
        if self.tiles.has_key(tileID):
            return self.tiles[tileID]
        else:
            return None



    def ConstructPlayerTerritories(self, playerID = None, useExistingIDSchema = False):
        playerTerritories = {}
        tilesTotal = []
        currID = 1
        for key in self.tiles:
            if self.tiles[key] not in tilesTotal:
                area = []
                area = self.GetTerritory(None, self.tiles[key].owner, self.tiles[key], area)
                if len(area) > 0 and area[0].owner != None:
                    if useExistingIDSchema == False:
                        playerTerritories[currID] = area
                    else:
                        playerTerritories[area[0].areaKey] = area
                    currID += 1
                for item in area:
                    tilesTotal.append(item)


        noOwnerArea = []
        for key in self.tiles:
            tile = self.tiles[key]
            if tile.owner == None:
                noOwnerArea.append(tile)

        if len(noOwnerArea) > 0:
            playerTerritories[playerTerritories.keys()[-1] + 1] = noOwnerArea
        if playerID is not None:
            removeAreas = []
            for key in playerTerritories:
                area = playerTerritories[key]
                if len(area) > 0:
                    if area[0].owner != playerID:
                        removeAreas.append(key)

            for areaKey in removeAreas:
                if areaKey in playerTerritories:
                    del playerTerritories[areaKey]

        return playerTerritories



    def GetTerritory(self, parentTile, player, tile, area):
        if tile != None and tile.owner == player and tile not in area:
            area.append(tile)
            if parentTile != tile.neighbour1:
                area = self.GetTerritory(tile, player, tile.neighbour1, area)
            if parentTile != tile.neighbour2:
                area = self.GetTerritory(tile, player, tile.neighbour2, area)
            if parentTile != tile.neighbour3:
                area = self.GetTerritory(tile, player, tile.neighbour3, area)
            if parentTile != tile.neighbour4:
                area = self.GetTerritory(tile, player, tile.neighbour4, area)
            if parentTile != tile.neighbour5:
                area = self.GetTerritory(tile, player, tile.neighbour5, area)
            if parentTile != tile.neighbour6:
                area = self.GetTerritory(tile, player, tile.neighbour6, area)
            return area
        else:
            return area



    def TileArrayToRaw(self, tileArray):
        returnArea = []
        for tile in tileArray:
            returnArea.append(tile.GetRaw())

        return returnArea



    def TileArrayFromRaw(self, rawArray):
        returnArea = []
        for raw in rawArray:
            tile = SlayTile()
            tile.FromRaw(raw)
            returnArea.append(tile)

        return returnArea



    def RemoveTile(self, tile):
        tile.NotifyRemove()
        del self.tiles[tile.tileID]



    def Restart(self):
        self.InitData(self.length, self.height)



    def GetAreaByTile(self, tile):
        area = self.GetTerritory(None, tile.owner, tile, [])
        return area



    def GetAreaNeighbours(self, areaKey):
        borderTiles = []
        area = []
        for key in self.tiles:
            if self.tiles[key].areaKey == areaKey:
                area.append(self.tiles[key])

        for tile in area:
            for neighbour in tile.GetNeighbours():
                if neighbour.areaKey != areaKey and neighbour not in borderTiles:
                    borderTiles.append(neighbour)


        return borderTiles



    def CompareAreas(self, area1, area2):
        if area1 == None or area2 == None:
            return False
        else:
            if len(area1) == len(area2):
                same = True
                for tileX in area1:
                    found = False
                    for tileY in area2:
                        if tileY.tileID == tileX.tileID:
                            found = True

                    if found == False:
                        same = False
                        break

                return same
            return False



    def GetCapitol(self, area):
        if len(area) > 1:
            for tile in area:
                if tile.occupier.unitID == slayConst.OCCUPY_TOWN:
                    return tile




    def IsCoast(self, tile):
        for i in xrange(0, 6):
            neighbour = tile.neighbours[i]
            if neighbour is None:
                return True

        return False



    def IsBorder(self, tile):
        for i in xrange(0, 6):
            neighbour = tile.neighbours[i]
            if neighbour is not None and neighbour.owner != tile.owner:
                return True

        return False



    def IsAttackable(self, tile, area, currPlayer):
        if tile is None or tile.owner == currPlayer:
            return False
        for i in xrange(0, 6):
            neighbour = tile.neighbours[i]
            if neighbour in area:
                return True

        return False



    def IsInOrAround(self, tile, area):
        if tile in area:
            return True
        for i in xrange(0, 6):
            neighbour = tile.neighbours[i]
            if neighbour is not None and neighbour in area:
                return True

        return False



    def GetPower(self, area, evalPlayer):
        high = 0
        for tile in area:
            if tile.owner == evalPlayer:
                continue
            if tile.occupier.unitID == slayConst.OCCUPY_PEASANT:
                if high < 1:
                    high = 1
            elif tile.occupier.unitID == slayConst.OCCUPY_SPEARMAN:
                if high < 2:
                    high = 2
            elif tile.occupier.unitID == slayConst.OCCUPY_KNIGHT:
                if high < 3:
                    high = 3
            else:
                if tile.occupier.unitID == slayConst.OCCUPY_BARON:
                    return 4

        return high



    def FindActiveUnit(self, area, unitID, bannedTiles = None):
        for tile in area:
            if tile is not None and tile.active == True:
                if tile.occupier.unitID == unitID:
                    if bannedTiles is not None:
                        if tile.tileID not in bannedTiles:
                            return tile
                    else:
                        return tile




    def SplitCandidate(self, tile):
        n1 = tile.neighbours[0]
        n2 = tile.neighbours[1]
        n3 = tile.neighbours[2]
        n4 = tile.neighbours[3]
        n5 = tile.neighbours[4]
        n6 = tile.neighbours[5]
        if (n1 is None or n1.owner != tile.owner) and (n3 is None or n3.owner != tile.owner):
            if n2 is not None and n2.owner == tile.owner:
                return True
        if (n2 is None or n2.owner != tile.owner) and (n4 is None or n4.owner != tile.owner):
            if n3 is not None and n3.owner == tile.owner:
                return True
        if (n3 is None or n3.owner != tile.owner) and (n5 is None or n5.owner != tile.owner):
            if n4 is not None and n4.owner == tile.owner:
                return True
        if (n4 is None or n4.owner != tile.owner) and (n6 is None or n6.owner != tile.owner):
            if n5 is not None and n5.owner == tile.owner:
                return True
        if (n5 is None or n5.owner != tile.owner) and (n1 is None or n1.owner != tile.owner):
            if n6 is not None and n6.owner == tile.owner:
                return True
        if (n6 is None or n6.owner != tile.owner) and (n2 is None or n2.owner != tile.owner):
            if n1 is not None and n1.owner == tile.owner:
                return True
        if (n1 is None or n1.owner != tile.owner) and (n4 is None or n4.owner != tile.owner):
            return True
        if (n2 is None or n2.owner != tile.owner) and (n5 is None or n5.owner != tile.owner):
            return True
        if (n6 is None or n6.owner != tile.owner) and (n3 is None or n3.owner != tile.owner):
            return True
        return False



    def GetPattern(self, polygon, color):
        tileID = 0
        tiles = {}
        for line in polygon:
            startPoint = line[0]
            x1 = startPoint[0]
            y1 = startPoint[1]
            endPoint = line[1]
            x2 = endPoint[0]
            y2 = endPoint[1]
            if (x1, y1) != (x2, y2):
                for y in xrange(0, self.height):
                    for x in xrange(0, self.length):
                        if '%d.%d' % (x, y) in self.GetNonHexagonTiles():
                            continue
                        if (x - x1) * (y2 - y1) == (x2 - x1) * (y - y1):
                            tiles[tileID] = (True,
                             1,
                             1,
                             1,
                             1,
                             color,
                             x,
                             y,
                             tileID,
                             0)
                            tileID += 1



        return tiles



    def GetCircularPattern(self, step):
        if step == 0:
            map = [[None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               7,
               1,
               '7.1',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               1,
               '8.1',
               17),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               1,
               '9.1',
               4),
              None,
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               5,
               2,
               '5.2',
               6),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               6,
               2,
               '6.2',
               6),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               10,
               2,
               '10.2',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               11,
               2,
               '11.2',
               4),
              None,
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               3,
               3,
               '3.3',
               13),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               4,
               3,
               '4.3',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               7,
               3,
               '7.3',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               3,
               '8.3',
               17),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               3,
               '9.3',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               3,
               '12.3',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               13,
               3,
               '13.3',
               4),
              None,
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               1,
               4,
               '1.4',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               4,
               '2.4',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               5,
               4,
               '5.4',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               6,
               4,
               '6.4',
               2),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               10,
               4,
               '10.4',
               7),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               11,
               4,
               '11.4',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               14,
               4,
               '14.4',
               3),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               15,
               4,
               '15.4',
               8),
              None,
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               0,
               5,
               '0.5',
               20),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               3,
               5,
               '3.5',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               4,
               5,
               '4.5',
               13),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               7,
               5,
               '7.5',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               5,
               '8.5',
               3),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               5,
               '9.5',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               5,
               '12.5',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               13,
               5,
               '13.5',
               3),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               16,
               5,
               '16.5',
               8),
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               0,
               6,
               '0.6',
               4),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               2,
               6,
               '2.6',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               5,
               6,
               '5.6',
               2),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               6,
               6,
               '6.6',
               2),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               10,
               6,
               '10.6',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               11,
               6,
               '11.6',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               14,
               6,
               '14.6',
               4),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               6,
               '16.6',
               3),
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               0,
               7,
               '0.7',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               7,
               '2.7',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               4,
               7,
               '4.7',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               7,
               7,
               '7.7',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               7,
               '8.7',
               3),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               7,
               '9.7',
               18),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               7,
               '12.7',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               14,
               7,
               '14.7',
               4),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               7,
               '16.7',
               3),
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               0,
               8,
               '0.8',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               8,
               '2.8',
               4),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               4,
               8,
               '4.8',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               6,
               8,
               '6.8',
               4),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               10,
               8,
               '10.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               12,
               8,
               '12.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               14,
               8,
               '14.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               16,
               8,
               '16.8',
               11),
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               0,
               9,
               '0.9',
               2),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               2,
               9,
               '2.9',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               4,
               9,
               '4.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               6,
               9,
               '6.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               8,
               9,
               '8.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               10,
               9,
               '10.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               9,
               '12.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               14,
               9,
               '14.9',
               11),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               9,
               '16.9',
               12),
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               0,
               10,
               '0.10',
               10),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               10,
               '2.10',
               10),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               4,
               10,
               '4.10',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               6,
               10,
               '6.10',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               7,
               10,
               '7.10',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               10,
               '9.10',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               10,
               10,
               '10.10',
               2),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               12,
               10,
               '12.10',
               3),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               14,
               10,
               '14.10',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               16,
               10,
               '16.10',
               11),
              None],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               0,
               11,
               '0.11',
               16),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               11,
               '2.11',
               10),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               4,
               11,
               '4.11',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               5,
               11,
               '5.11',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               8,
               11,
               '8.11',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               11,
               11,
               '11.11',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               11,
               '12.11',
               4),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               14,
               11,
               '14.11',
               3),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               11,
               '16.11',
               14),
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               0,
               12,
               '0.12',
               19),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               12,
               '2.12',
               10),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               3,
               12,
               '3.12',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               6,
               12,
               '6.12',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               7,
               12,
               '7.12',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               9,
               12,
               '9.12',
               4),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               10,
               12,
               '10.12',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               13,
               12,
               '13.12',
               3),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               14,
               12,
               '14.12',
               11),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               12,
               '16.12',
               14),
              None],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               0,
               13,
               '0.13',
               19),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               1,
               13,
               '1.13',
               16),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               4,
               13,
               '4.13',
               10),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               5,
               13,
               '5.13',
               10),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               13,
               '8.13',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               11,
               13,
               '11.13',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               13,
               '12.13',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               15,
               13,
               '15.13',
               11),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               16,
               13,
               '16.13',
               14)],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               2,
               14,
               '2.14',
               10),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               3,
               14,
               '3.14',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               6,
               14,
               '6.14',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               7,
               14,
               '7.14',
               1),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               9,
               14,
               '9.14',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               10,
               14,
               '10.14',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               13,
               14,
               '13.14',
               3),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               14,
               14,
               '14.14',
               3)],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               4,
               15,
               '4.15',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               5,
               15,
               '5.15',
               1),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               8,
               15,
               '8.15',
               1),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               11,
               15,
               '11.15',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               12,
               15,
               '12.15',
               4)],
             [(True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_2,
               6,
               16,
               '6.16',
               1),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               7,
               16,
               '7.16',
               2),
              None,
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               9,
               16,
               '9.16',
               2),
              (True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               10,
               16,
               '10.16',
               2)],
             [(True,
               1,
               1,
               1,
               '2',
               slayConst.COLOR_2,
               8,
               17,
               '8.17',
               2)]]
        else:
            map = [[None],
             [None,
              None,
              None,
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               7,
               2,
               '7.2',
               4),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               8,
               2,
               '8.2',
               17),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               9,
               2,
               '9.2',
               4),
              None,
              None,
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               5,
               3,
               '5.3',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               6,
               3,
               '6.3',
               4),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               3,
               '10.3',
               7),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               11,
               3,
               '11.3',
               7),
              None,
              None,
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               3,
               4,
               '3.4',
               13),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               4,
               4,
               '4.4',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               7,
               4,
               '7.4',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               8,
               4,
               '8.4',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               9,
               4,
               '9.4',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               12,
               4,
               '12.4',
               7),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               13,
               4,
               '13.4',
               4),
              None,
              None,
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               1,
               5,
               '1.5',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               2,
               5,
               '2.5',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               5,
               5,
               '5.5',
               4),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               6,
               5,
               '6.5',
               2),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               5,
               '10.5',
               7),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               11,
               5,
               '11.5',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               14,
               5,
               '14.5',
               3),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               15,
               5,
               '15.5',
               3),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               1,
               6,
               '1.6',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               3,
               6,
               '3.6',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               4,
               6,
               '4.6',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               7,
               6,
               '7.6',
               4),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               8,
               6,
               '8.6',
               3),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               9,
               6,
               '9.6',
               3),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               12,
               6,
               '12.6',
               3),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               13,
               6,
               '13.6',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               6,
               '15.6',
               4),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               1,
               7,
               '1.7',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               3,
               7,
               '3.7',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               5,
               7,
               '5.7',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               6,
               7,
               '6.7',
               4),
              None,
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               7,
               '10.7',
               3),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               11,
               7,
               '11.7',
               3),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               13,
               7,
               '13.7',
               3),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               15,
               7,
               '15.7',
               3),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               1,
               8,
               '1.8',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               3,
               8,
               '3.8',
               4),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               5,
               8,
               '5.8',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               7,
               8,
               '7.8',
               3),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               8,
               8,
               '8.8',
               3),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               9,
               8,
               '9.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               11,
               8,
               '11.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               13,
               8,
               '13.8',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               8,
               '15.8',
               11),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               1,
               9,
               '1.9',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               3,
               9,
               '3.9',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               5,
               9,
               '5.9',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               7,
               9,
               '7.9',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               9,
               9,
               '9.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               11,
               9,
               '11.9',
               4),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               13,
               9,
               '13.9',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               9,
               '15.9',
               11),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               1,
               10,
               '1.10',
               10),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               3,
               10,
               '3.10',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               5,
               10,
               '5.10',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               8,
               10,
               '8.10',
               3),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               11,
               10,
               '11.10',
               4),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               13,
               10,
               '13.10',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               10,
               '15.10',
               11),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               1,
               11,
               '1.11',
               16),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               3,
               11,
               '3.11',
               10),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               6,
               11,
               '6.11',
               4),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               7,
               11,
               '7.11',
               4),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               9,
               11,
               '9.11',
               4),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               11,
               '10.11',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               13,
               11,
               '13.11',
               3),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               11,
               '15.11',
               11),
              None,
              None],
             [None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               1,
               12,
               '1.12',
               16),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               4,
               12,
               '4.12',
               2),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               5,
               12,
               '5.12',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               8,
               12,
               '8.12',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               11,
               12,
               '11.12',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               12,
               12,
               '12.12',
               4),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               15,
               12,
               '15.12',
               11),
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               2,
               13,
               '2.13',
               10),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               3,
               13,
               '3.13',
               10),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               6,
               13,
               '6.13',
               2),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               7,
               13,
               '7.13',
               2),
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               9,
               13,
               '9.13',
               2),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               13,
               '10.13',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               13,
               13,
               '13.13',
               4),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               14,
               13,
               '14.13',
               3),
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               4,
               14,
               '4.14',
               2),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               5,
               14,
               '5.14',
               2),
              None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               8,
               14,
               '8.14',
               1),
              None,
              None,
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               11,
               14,
               '11.14',
               2),
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               12,
               14,
               '12.14',
               4),
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               6,
               15,
               '6.15',
               1),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               7,
               15,
               '7.15',
               2),
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               9,
               15,
               '9.15',
               1),
              (True,
               1,
               1,
               1,
               2,
               slayConst.COLOR_1,
               10,
               15,
               '10.15',
               2),
              None,
              None],
             [None,
              None,
              (True,
               1,
               1,
               1,
               1,
               slayConst.COLOR_1,
               8,
               16,
               '8.16',
               1),
              None,
              None],
             [None]]
        tileID = 0
        dictMap = {}
        for row in map:
            for tile in row:
                if tile is not None:
                    tileInst = SlayTile()
                    tileInst.FromRaw(tile)
                    tileInst.tileID = tileID
                    dictMap[tileID] = tileInst.GetRaw()
                    tileID += 1


        return dictMap



    def MergeUnits(self, unit1, unit2):
        if unit1.unitID == slayConst.OCCUPY_PEASANT:
            if unit2.unitID == slayConst.OCCUPY_PEASANT:
                unit2.SetUnitID(slayConst.OCCUPY_SPEARMAN)
                unit2.mergedID = unit1.ID
                return unit2
            if unit2.unitID == slayConst.OCCUPY_SPEARMAN:
                unit2.SetUnitID(slayConst.OCCUPY_KNIGHT)
                unit2.mergedID = unit1.ID
                return unit2
            if unit2.unitID == slayConst.OCCUPY_KNIGHT:
                unit2.SetUnitID(slayConst.OCCUPY_BARON)
                unit2.mergedID = unit1.ID
                return unit2
            if self.IsNonUnit(unit2.unitID):
                return unit1
        elif unit1.unitID == slayConst.OCCUPY_SPEARMAN:
            if unit2.unitID == slayConst.OCCUPY_PEASANT:
                unit2.SetUnitID(slayConst.OCCUPY_KNIGHT)
                unit2.mergedID = unit1.ID
                return unit2
            if unit2.unitID == slayConst.OCCUPY_SPEARMAN:
                unit2.SetUnitID(slayConst.OCCUPY_BARON)
                unit2.mergedID = unit1.ID
                return unit2
            if self.IsNonUnit(unit2.unitID):
                return unit1
        elif unit1.unitID == slayConst.OCCUPY_KNIGHT:
            if unit2.unitID == slayConst.OCCUPY_PEASANT:
                unit2.SetUnitID(slayConst.OCCUPY_BARON)
                unit2.mergedID = unit1.ID
                return unit2
            if self.IsNonUnit(unit2.unitID):
                return unit1
        else:
            if self.IsNonUnit(unit1.unitID):
                return unit2
            else:
                return None



    def IsNonUnit(self, unitID):
        return unitID in [slayConst.OCCUPY_DEAD,
         slayConst.OCCUPY_NONE,
         slayConst.OCCUPY_PINEFOREST,
         slayConst.OCCUPY_PALMFOREST]




class SlayTile():
    __guid__ = 'slaycommon.SlayTile'

    def __init__(self, x = None, y = None, tileID = None, areaKey = None):
        self.active = True
        self.roundCound = 0
        self.treeGrown = False
        self.expenses = 0
        self.occupier = SlayUnit(slayConst.OCCUPY_NONE)
        self.owner = None
        self.color = slayConst.COLOR_NONE
        self.x = x
        self.y = y
        self.tileID = tileID
        self.areaKey = areaKey
        self.neighbour1 = None
        self.neighbour2 = None
        self.neighbour3 = None
        self.neighbour4 = None
        self.neighbour5 = None
        self.neighbour6 = None
        self.neighbours = []
        for i in xrange(0, 6):
            self.neighbours.append(None)




    def Compare(self, otherTile):
        if self.owner != otherTile.owner:
            return False
        if self.occupier.unitID != otherTile.occupier.unitID:
            return False
        if self.areaKey != otherTile.areaKey:
            return False
        if self.expenses != otherTile.expenses:
            return False
        if self.active != otherTile.active:
            return False
        return True



    def GetRaw(self):
        return (self.active,
         self.occupier.unitID,
         self.occupier.ID,
         self.occupier.mergedID,
         self.owner,
         self.color,
         self.x,
         self.y,
         self.tileID,
         self.areaKey)



    def FromRaw(self, rawData):
        self.active = rawData[0]
        self.occupier = SlayUnit(rawData[1])
        self.occupier.ID = rawData[2]
        self.occupier.mergedID = rawData[3]
        self.owner = rawData[4]
        self.color = rawData[5]
        self.x = rawData[6]
        self.y = rawData[7]
        self.tileID = rawData[8]
        self.areaKey = rawData[9]



    def HasAsNeighbour(self, tile):
        for i in range(1, 7):
            testTile = getattr(self, 'neighbour%s' % i)
            if testTile != None and testTile.tileID == tile.tileID:
                return True

        return False



    def GetNeighbours(self):
        neighbours = []
        for i in range(1, 7):
            testTile = getattr(self, 'neighbour%s' % i)
            if testTile:
                neighbours.append(testTile)

        return neighbours



    def NotifyRemove(self):
        if self.neighbour1 != None:
            self.neighbour1.RemoveNeighbour(self)
            self.neighbour1 = None
            self.neighbours[0] = None
        if self.neighbour2 != None:
            self.neighbour2.RemoveNeighbour(self)
            self.neighbour2 = None
            self.neighbours[1] = None
        if self.neighbour3 != None:
            self.neighbour3.RemoveNeighbour(self)
            self.neighbour3 = None
            self.neighbours[2] = None
        if self.neighbour4 != None:
            self.neighbour4.RemoveNeighbour(self)
            self.neighbour4 = None
            self.neighbours[3] = None
        if self.neighbour5 != None:
            self.neighbour5.RemoveNeighbour(self)
            self.neighbour5 = None
            self.neighbours[4] = None
        if self.neighbour6 != None:
            self.neighbour6.RemoveNeighbour(self)
            self.neighbour6 = None
            self.neighbours[5] = None



    def RemoveNeighbour(self, tile):
        if tile == self.neighbour1:
            self.neighbour1 = None
            self.neighbours[0] = None
        if tile == self.neighbour2:
            self.neighbour2 = None
            self.neighbours[1] = None
        if tile == self.neighbour3:
            self.neighbour3 = None
            self.neighbours[2] = None
        if tile == self.neighbour4:
            self.neighbour4 = None
            self.neighbours[3] = None
        if tile == self.neighbour5:
            self.neighbour5 = None
            self.neighbours[4] = None
        if tile == self.neighbour6:
            self.neighbour6 = None
            self.neighbours[5] = None




class SlayUnit():
    __guid__ = 'slaycommon.SlayUnit'
    unitCounter = 0

    def __init__(self, unitID):
        self.unitID = unitID
        self.Configure()
        self.ID = SlayUnit.unitCounter
        self.mergedID = None
        SlayUnit.unitCounter += 1



    def SetUnitID(self, unitID):
        self.unitID = unitID
        self.Configure()



    def Configure(self):
        if self.unitID == slayConst.OCCUPY_DEAD:
            self.buyCost = 0
            self.supportCost = 0
            self.strength = 0
        elif self.unitID == slayConst.OCCUPY_NONE:
            self.buyCost = 0
            self.supportCost = 0
            self.strength = 0
        elif self.unitID == slayConst.OCCUPY_PINEFOREST:
            self.buyCost = 0
            self.supportCost = 0
            self.strength = 0
        elif self.unitID == slayConst.OCCUPY_PALMFOREST:
            self.buyCost = 0
            self.supportCost = 0
            self.strength = 0
        elif self.unitID == slayConst.OCCUPY_PEASANT:
            self.buyCost = slayConst.BUY_COST_PEASANT
            self.supportCost = slayConst.SUPPORT_COST_PEASANT
            self.strength = 1
        elif self.unitID == slayConst.OCCUPY_TOWN:
            self.buyCost = 0
            self.supportCost = 0
            self.strength = 1
        elif self.unitID == slayConst.OCCUPY_SPEARMAN:
            self.buyCost = 0
            self.supportCost = slayConst.SUPPORT_COST_SPEARMAN
            self.strength = 2
        elif self.unitID == slayConst.OCCUPY_CASTLE:
            self.buyCost = slayConst.BUY_COST_CASTLE
            self.supportCost = 0
            self.strength = 2
        elif self.unitID == slayConst.OCCUPY_KNIGHT:
            self.buyCost = 0
            self.supportCost = slayConst.SUPPORT_COST_KNIGHT
            self.strength = 3
        elif self.unitID == slayConst.OCCUPY_BARON:
            self.buyCost = 0
            self.supportCost = slayConst.SUPPORT_COST_BARON
            self.strength = 4



exports = util.AutoExports('slaycommon', locals())

