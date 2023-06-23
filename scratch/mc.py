
def deco(x):
    print('deco', x)
    return x

@deco
class meta(type):

    def __new__(cls, clsname, bases, dct):
        print(cls, '__new__', clsname, bases, dct)

        tmp = {}
        for k, v in dct.items():
            if not k.startswith('__'):
                tmp[k.upper()] = v
            else:
                tmp[k] = v

        return type.__new__(cls, clsname, bases, tmp)

    def __init__(cls, *args, **kwargs):
        print(cls, '__init__', args, kwargs)

    def __call__(cls, *args, **kwargs):
        print(cls, '__call__', args, kwargs)
        return type.__call__(cls, *args, **kwargs)

print('-------------------------------------------------------------------')

@deco
class parent(metaclass=meta):
    abc = 3.14

    def __init__(self):
        print('hello from parent')

print('-------------------------------------------------------------------')

@deco
class child(parent):
    ghi = 5.55

    def __init__(self):
        super(child, self).__init__()

print('-------------------------------------------------------------------')

@deco
class grandchild(child):
    jkl = 333

print('-------------------------------------------------------------------')
p = parent()
print(dir(p))
print('-------------------------------------------------------------------')
c1 = child()
print(dir(c1))
print('-------------------------------------------------------------------')
c2 = child()
print(dir(c2))
print('-------------------------------------------------------------------')
gc = grandchild()
print(dir(gc))

print('-------------------------------------------------------------------')

class devspec(type):
    pass

class lorawan_device(metaclass=devspec):
    pass

def handler(*args, **kwargs):
    def _deco(f):
        return f
    return _deco

def action(f):
    return f

class comtac_cm1(lorawan_device):
    temperature : float = None
    humidity : float = None

    @handler(length=41, port=2)
    def on_data_uplink(self, payload):
        self.temperature.record(...)
        self.humidity.record(...)

    @handler(length=17, port=11)
    def on_keepalive(self, payload):
        pass

    @action
    def set_temp_low(self, low):
        return b'...'

    @action
    def set_temp_high(self, high):
        return b'...'

print('-------------------------------------------------------------------')

from mc import comtac_cm1

# comtac_cm1(deveui='70b3d5fffe29724c', appeui='70b3d5fffe297000', appkey='ab89efcd2301674554761032dcfe98ba', description='R630BEL Klima Raum B3.11')
