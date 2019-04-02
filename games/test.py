class BigBoi(object):
    def __init__(self, val):
        self.val = val
    def fake_method(self):
        str_cpy = BigBoi(self.val)
        print(type(self))
        print(self.__class__)
        return str_cpy

class Boi(BigBoi):
    def __init__(self, val):
        super().__init__(val)
        self.true = True
    def fake_method(self):
        res =super().fake_method()
        print(type(res))
        print(res.__class__)

