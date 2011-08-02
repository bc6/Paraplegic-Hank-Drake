import uiconst
import uicls
import uiutil
import trinity
import blue

class HelloWorld(uicls.Container):
    __guid__ = 'uicls.HelloWorld'
    default_name = 'HelloWorld'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        uicls.Label(parent=self, pos=(20, 200, 300, 60), singleline=True, text='Hello_world!')




class HelloWorldWithButton(uicls.Container):
    __guid__ = 'uicls.HelloWorldWithButton'
    default_name = 'HelloWorldWithButton'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        uicls.Label(parent=self, pos=(20, 200, 300, 20), singleline=True, text='Hello_world!')
        uicls.Button(parent=self, pos=(20, 230, 300, 20), label='Push!', mouseupfunc=self.HandleButton)



    def HandleButton(self, *args):
        print "You're pushing me!",
        print args




class HelloWorldWizardPage1(uicls.Container):
    __guid__ = 'uicls.HelloWorldWizardPage1'
    default_name = 'HelloWorldWizardPage1'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        uicls.Label(parent=self, pos=(20, 200, 300, 20), singleline=True, text='First')
        uicls.Button(parent=self, pos=(20, 230, 300, 20), label='Next', mouseupfunc=self.parent.AcceptPage1)




class HelloWorldWizardPage2(uicls.Container):
    __guid__ = 'uicls.HelloWorldWizardPage2'
    default_name = 'HelloWorldWizardPage2'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        uicls.Label(parent=self, pos=(20, 200, 300, 20), singleline=True, text='Second')
        uicls.Button(parent=self, pos=(20, 230, 300, 20), label='Next', mouseupfunc=self.parent.AcceptPage2)




class HelloWorldWizard(uicls.Container):
    __guid__ = 'uicls.HelloWorldWizard'
    default_name = 'HelloWorldWizard'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.page = uicls.HelloWorldWizardPage1(parent=self)



    def AcceptPage1(self, *args):
        self.page.Close()
        self.page = uicls.HelloWorldWizardPage2(parent=self)



    def AcceptPage2(self, *args):
        self.page.Close()




