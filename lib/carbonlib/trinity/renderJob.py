import bluepy
import trinity
import blue

class RenderJob(object):
    __cid__ = 'trinity.TriRenderJob'
    __metaclass__ = bluepy.BlueWrappedMetaclass

    def __init__(self):
        self.cancelled = False



    def ScheduleOnce(self):
        trinity.device.scheduledOnce.append(self)



    def ScheduleChained(self):
        trinity.device.scheduledChained.append(self)



    def CancelChained(self):
        self.cancelled = True
        if self in trinity.device.scheduledChained:
            trinity.device.scheduledChained.remove(self)



    def ScheduleRecurring(self, scheduledRecurring = None, insertFront = False):
        if scheduledRecurring is None:
            scheduledRecurring = trinity.device.scheduledRecurring
        if insertFront == False:
            scheduledRecurring.append(self)
        else:
            scheduledRecurring.insert(0, self)



    def UnscheduleRecurring(self, scheduledRecurring = None):
        if scheduledRecurring is None:
            scheduledRecurring = trinity.device.scheduledRecurring
        if self in scheduledRecurring:
            scheduledRecurring.remove(self)



    def WaitForFinish(self):
        while not (self.status == trinity.RJ_DONE or self.status == trinity.RJ_FAILED or self.cancelled):
            blue.synchro.Yield()





def _GetRenderJobCreationClosure(functionName, doc, classThunker):

    def CreateStep(self, *args):
        step = classThunker(*args)
        self.steps.append(step)
        return step


    CreateStep.__doc__ = doc
    CreateStep.__name__ = functionName
    return CreateStep


for (className, desc,) in trinity.GetClassInfo().iteritems():
    if className.startswith('TriStep'):
        setattr(RenderJob, className[7:], _GetRenderJobCreationClosure(className[7:], desc[3].get('__init__', 'Create a %s render step and add it to the render job' % className), getattr(trinity, className)))


def CreateRenderJob(name = None):
    job = RenderJob()
    if name:
        job.name = name
    return job



