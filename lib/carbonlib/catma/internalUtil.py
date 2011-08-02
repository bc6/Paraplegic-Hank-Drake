
def Overwrite(cls):

    def Decorator(function):
        setattr(cls, function.__name__, function)
        return function


    return Decorator



