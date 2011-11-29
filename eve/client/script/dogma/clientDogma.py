import svc

class ClientDogma(svc.baseDogma):
    __guid__ = 'svc.dogma'

    def Run(self, *args):
        svc.baseDogma.Run(self, *args)
        self.LoadExpressions()
        self.LoadOperands()



    def LoadOperands(self):
        self.operands = sm.RemoteSvc('dogma').GetOperandsForChar()



    def GetDogmaIM(self):
        if self.dogmaIM is None:
            self.dogmaIM = sm.GetService('dogmaStaticSvc')
        return self.dogmaIM



    def GetEffectCompiler(self):
        if self.effectCompiler is None:
            self.effectCompiler = sm.GetService('clientEffectCompiler')
        return self.effectCompiler




