import blue

class LoggingComponent:
    __guid__ = 'entities.LoggingComponent'

    def __init__(self):
        self.history = []



    def Log(self, text):
        self.history.append((blue.os.GetTime(1), text))




