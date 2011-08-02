import blue
import geo2
import os

class WorldSpaceBenchmark(object):
    __guid__ = 'world.WorldSpaceBenchmark'

    def __init__(self, boundingBox, worldSpaceTypeID, name = 'wsBenchmark'):
        self.boundingBox = boundingBox
        self.worldSpaceTypeID = worldSpaceTypeID
        self.frameTime = []
        self.testPoints = []
        self.name = name



    def GetCamera(self):
        return None



    def SetPosition(self, pos):
        pass



    def SetFocus(self, focusPos):
        pass



    def PerformBasicBenchmark(self):
        vStep = (1, 1, 1)
        self.GeneratePositions(self.boundingBox[0], self.boundingBox[1], vStep)
        self.StartBenchmark()



    def PerformGridBenchmark(self, gridSteps, y = 0.0, newThread = True):
        self.GeneratePositionsGrid(self.boundingBox[0], self.boundingBox[1], gridSteps, gridSteps, y)
        self.StartBenchmark(newThread=newThread)



    def GeneratePositions(self, vMin, vMax, step):
        x = vMin[0]
        y = vMin[1]
        z = vMin[2]
        self.pointList = []
        while x <= vMax[0]:
            while y <= vMax[1]:
                while z <= vMax[2]:
                    self.GenerateListForPoint((x, y, z), self.pointList)
                    z += step[2]

                y += step[1]
                z = vMin[2]

            x += step[0]
            y = vMin[1]
            z = vMin[2]

        return self.pointList



    def GeneratePositionsGrid(self, vMin, vMax, xSteps, zSteps, yPos):
        y = yPos
        if xSteps > 1:
            xStep = (vMax[0] - vMin[0]) / (xSteps - 1)
        else:
            xStep = 0
        if zSteps > 1:
            zStep = (vMax[2] - vMin[2]) / (zSteps - 1)
        else:
            zStep = 0
        print 'Step Size',
        print xStep,
        print zStep,
        print y,
        print vMin[1],
        print vMax[1]
        self.pointList = []
        x = vMin[0]
        for i in xrange(xSteps):
            z = vMin[2]
            for j in xrange(zSteps):
                self.GenerateListForPoint((x, y, z), self.pointList)
                z += zStep

            x += xStep

        return self.pointList



    def StartBenchmark(self, newThread = True):
        self.cam = self.GetCamera()
        if newThread:
            uthread.new(self.UpdateBenchmark).context = '^WorldSpaceBenchMark::UpdateBenchmark'
        else:
            self.UpdateBenchmark()



    def UpdateBenchmark(self):
        import trinity
        trinity.WaitForResourceLoads()
        blue.resMan.Wait()
        self.frameTimeList = []
        self.maxFrameTime = 0
        self.avgFrameTime = 0
        self.startTime = blue.os.TimeAsDouble(blue.os.GetTime())
        numPoints = len(self.pointList)
        frameTimes = []
        for view in xrange(6):
            print 'View',
            print view
            frameTimes.append([])
            for posNum in xrange(numPoints / 6):
                (position, focus,) = self.pointList[(posNum * 6 + view)]
                self.SetPosition(position)
                self.SetFocus(focus)
                time = blue.os.TimeAsDouble(blue.os.GetTime())
                blue.pyos.synchro.Yield()
                frameTime = blue.os.TimeAsDouble(blue.os.GetTime()) - time
                frameTimes[view].append(frameTime)
                if frameTime > self.maxFrameTime:
                    self.maxFrameTime = frameTime


        for posNum in xrange(numPoints / 6):
            for view in xrange(6):
                self.frameTimeList.append(frameTimes[view][posNum])


        self.timeElapsed = blue.os.TimeAsDouble(blue.os.GetTime()) - self.startTime
        print 'Done!'
        print 'Number of views used ' + str(len(self.frameTimeList))
        print 'Number of positions ' + str(len(self.frameTimeList) / 6)
        print 'Max time ' + str(self.maxFrameTime)
        self.GetAverageFrameTime(self.frameTimeList)
        self.WriteOutFrameInfo(self.pointList, self.frameTimeList)



    def WriteOutFrameInfo(self, pointList, timeList):
        filePath = 'res:/../common/res/wsBenchmarks'
        filePath = os.path.abspath(filePath)
        print 'Desired Path is - ' + filePath
        if not os.access(filePath, os.F_OK):
            print 'Making path - ' + filePath
            os.mkdir(filePath)
        filePath = filePath + '\\' + self.name + '.txt'
        print 'Writing to ' + filePath
        self.f = open(filePath, 'w')
        self.f.write('#Max\n')
        self.f.write(str(self.maxFrameTime) + '\n')
        self.f.write('#Average\n')
        self.f.write(str(self.avg) + '\n')
        self.f.write('#Number of points looked at\n')
        self.f.write(str(len(pointList) / 6) + '\n')
        self.f.write('#Total Time Elapsed\n')
        self.f.write(str(self.timeElapsed) + '\n')
        self.f.write('#Bounding box vMin - vMax\n')
        self.f.write(str(self.boundingBox[0]) + ' - ' + str(self.boundingBox[1]) + '\n')
        f.write('#List of data (position, focus point) - time\n')
        for i in xrange(len(pointList)):
            line = str(pointList[i]) + ' - ' + str(timeList[i]) + '\n'
            f.write(line)

        f.close()



    def GetAverageFrameTime(self, list):
        timesum = sum(list)
        self.avg = timesum / len(list)
        print 'Average ' + str(self.avg)
        return self.avg



    def GenerateListForPoint(self, point, list):
        temp1 = (point[0] + 1, point[1], point[2])
        list.append((point, temp1))
        temp2 = (point[0] - 1, point[1], point[2])
        list.append((point, temp2))
        temp3 = (point[0], point[1] - 1, point[2])
        list.append((point, temp3))
        temp4 = (point[0], point[1] + 1, point[2])
        list.append((point, temp4))
        temp5 = (point[0], point[1], point[2] - 1)
        list.append((point, temp5))
        temp6 = (point[0], point[1], point[2] + 1)
        list.append((point, temp6))



import unittest

class _TestBenchmarks(unittest.TestCase):

    def setUp(self):
        pass



    def tearDown(self):
        pass



    def testPoints(self):
        vMin = geo2.Vector(0, 0, 0)
        vMax = geo2.Vector(1, 1, 1)
        vStep = geo2.Vector(1, 1, 1)
        bench = WorldSpaceBenchmark(None, 'Test')
        pointList = bench.GeneratePositions(vMin, vMax, vStep)
        self.assertTrue(len(pointList) == 48)




