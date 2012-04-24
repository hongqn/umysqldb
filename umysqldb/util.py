def setdocstring(src):
    def deco(func):
        func.__doc__ = src.__doc__
        return func
    return deco
