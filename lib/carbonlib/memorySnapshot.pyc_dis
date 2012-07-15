#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\memorySnapshot.py
import blue
import yaml
import os
import trinity
import datetime
workingSetStatistic = blue.statistics.Find('Blue/Memory/WorkingSet')
CRTHeapUnaccountedStatistic = blue.statistics.Find('Blue/Memory/CrtHeapUnaccounted')
CRTHeapStatistic = blue.statistics.Find('Blue/Memory/CrtHeap')
PageFileStatistic = blue.statistics.Find('Blue/Memory/PageFileUsage')
trackedAllocationsSizeStatistic = blue.statistics.Find('Blue/Memory/trackedAllocationsSize')

def GetDefaultSnapshotsFolder():
    root = blue.paths.ResolvePath(u'root:/')
    return os.path.join(root, u'memorySnapshots')


snapShotsFolder = GetDefaultSnapshotsFolder()

def SetSnapshotsFolder(p):
    global snapShotsFolder
    snapShotsFolder = p


def CreateSnapshotsFolder():
    if not os.path.exists(snapShotsFolder):
        os.mkdir(snapShotsFolder)


def IsAutoSnapshotEnabled():
    args = blue.pyos.GetArg()
    for i, each in enumerate(args):
        if each.startswith('/memorySnapshots'):
            return True

    return False


def AutoMemorySnapshotIfEnabled(name):
    if IsAutoSnapshotEnabled():
        WriteMemorySnapshot(name)


def ClearMemorySnapshots():
    for fn in os.listdir(snapShotsFolder):
        os.remove(os.path.join(snapShotsFolder, fn))


def WriteMemorySnapshot(name = ''):
    global workingSetStatistic
    CreateSnapshotsFolder()
    frameCounter = blue.os.framesTotal
    dateString = datetime.date.today().isoformat()
    if name == '':
        extraName = ''
    else:
        extraName = '_' + name
    dumpFileName = dateString + '_' + str(frameCounter) + extraName + '.txt'
    summaryFileName = dateString + '_' + str(frameCounter) + extraName + '_summary.txt'
    yamlFileName = dateString + '_' + str(frameCounter) + extraName + '.yaml'
    summaryFilePath = os.path.join(snapShotsFolder, summaryFileName)
    dumpFilePath = os.path.join(snapShotsFolder, dumpFileName)
    yamlFilePath = os.path.join(snapShotsFolder, yamlFileName)
    stats = {}
    heaps = blue.memoryTracker.GetAllHeaps()
    fullHeapSize = 0L
    for heapID, heapSize in heaps.iteritems():
        fullHeapSize += heapSize

    stats['heaps'] = heaps
    stats['heapSize'] = fullHeapSize
    stats['workingSet'] = workingSetStatistic.value
    stats['CRTHeapUnaccounted'] = CRTHeapUnaccountedStatistic.value
    stats['CRTHeap'] = CRTHeapStatistic.value
    stats['PageFile'] = PageFileStatistic.value
    stats['trackedAllocationsSize'] = trackedAllocationsSizeStatistic.value
    stats['liveCount'] = blue.classes.LiveCount()
    stats['resources'] = []
    for classname, obj, count, a, b in blue.classes.LiveList():
        if not classname.endswith('Res'):
            continue
        elif obj is not None:
            if hasattr(obj, 'GetMemoryUsage'):
                objInfo = {}
                objInfo['id'] = blue.GetID(obj)
                objInfo['memUsage'] = obj.GetMemoryUsage()
                objInfo['path'] = obj.path
                objInfo['type'] = classname
                if hasattr(obj, 'name'):
                    objInfo['name'] = obj.name
                if classname.endswith('TextureRes'):
                    objInfo['format'] = trinity.TRIFORMAT.GetNameFromValue(obj.format)
                    objInfo['width'] = obj.width
                    objInfo['height'] = obj.height
                stats['resources'].append(objInfo)

    with open(yamlFilePath, 'w') as f:
        yaml.dump(stats, f)
    blue.memoryTracker.SummaryReport(str(summaryFilePath))
    blue.memoryTracker.DumpReportAsText(dumpFilePath)
    print 'Wrote report:', dumpFilePath, 'and', yamlFileName


def LaunchMemorySnapshotInspector():
    root = blue.paths.ResolvePath(u'root:/')
    sharedPython = os.path.abspath(os.path.join(root, u'../../../../shared_tools/python/27/Python.exe'))
    memoryTrackerFolder = os.path.abspath(os.path.join(root, u'../carbon/tools/MemorySnapshotProcessor/'))
    memoryTrackerScript = 'ProcessMemoryReports.py'
    subprocess.Popen((sharedPython, memoryTrackerScript, snapShotsFolder), startupinfo=subprocess.CREATE_NEW_CONSOLE, cwd=memoryTrackerFolder)