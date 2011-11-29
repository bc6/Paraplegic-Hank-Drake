import uicls
import uiconst
import trinity
import blue
import bluepy
import yaml

class SlideShow(uicls.Container):
    __guid__ = 'uicls.SlideShow'
    default_name = 'slideshow'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.controls = {}
        self.nextControlId = 0
        self.commandHandlers = {}
        self.commandHandlers['create'] = self._HandleCreate
        self.commandHandlers['close'] = self._HandleClose
        self.commandHandlers['clear'] = self._HandleClose
        self.commandHandlers['wait'] = self._HandleWait
        self.commandHandlers['animate'] = self._HandleAnimate



    def PlayFromList(self, commands):
        for each in commands:
            currentCommand = each[0]
            currentArgs = each[1]
            handler = self.commandHandlers[currentCommand]
            handler(currentArgs)




    def _HandleCreate(self, args):
        name = args[0]
        splitClassName = args[1].split('.')
        if len(splitClassName) == 1:
            moduleName = 'uicls'
            className = splitClassName[0]
        elif len(splitClassName) == 2:
            moduleName = splitClassName[0]
            className = splitClassName[1]
        else:
            raise AttributeError('Invalid class name')
        classArgs = args[2]
        if self.controls.has_key(name):
            raise AttributeError('Control already exists with this name')
        parentName = classArgs.get('parent', None)
        if parentName:
            parent = self.controls[parentName]
        else:
            parent = self
        classArgs['parent'] = parent
        classArgs['name'] = name
        classArgs['idx'] = 0
        module = __import__(moduleName)
        constructor = getattr(module, className)
        self.controls[name] = constructor(**classArgs)



    def _HandleClose(self, args):
        self.controls[args].Close()
        del self.controls[args]



    def _HandleClear(self, args):
        for each in self.controls.itervalues():
            each.Close()

        self.controls = {}



    def _HandleWait(self, args):
        if type(args) == int:
            blue.synchro.SleepWallclock(args)
        elif type(args) == str:
            control = self.controls[args]
            if hasattr(control, 'isFinished'):
                while not control.isFinished:
                    blue.synchro.Yield()




    def _HandleAnimate(self, args):
        animTargetName = args[0]
        animName = args[1]
        animArgs = args[2]
        self.UpdateAlignmentAsRoot()
        animTarget = self.controls[animTargetName]
        animFunc = getattr(uicore.animations, animName)
        animFunc(animTarget, **animArgs)




