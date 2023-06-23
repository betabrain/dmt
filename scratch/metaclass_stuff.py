#!/usr/bin/env python3.6


class fake_dict(object):

    def __init__(self):
        print("fake_dict:__init__")
        self._d = {}

    def __setitem__(self, key, value):
        print("fake_dict:__setitem__", key, value)
        self._d[key] = value

    def __getitem__(self, key):
        print("fake_dict:__getitem__", key)
        return self._d[key]

    def __repr__(self):
        return self._d.__repr__()

    def get_dict(self):
        return self._d


class thing(object):

    def __set__(self, *args):
        print("thing:__set__", args)

    def __get__(self, *args):
        print("thing:__get__", args)
        return self

    def __delete__(self, *args):
        print("thing:__delete__", args)
        raise Exception("cannot be deleted")


def marked(thing):
    return "marked: " + str(thing)


class meta(type):

    def __prepare__(cls, bases):
        print("meta:__prepare__", dict(cls=cls, bases=bases))
        return fake_dict()

    def __new__(meta, cls, bases, dct):
        print("meta:__new__", dict(meta=meta, cls=cls, bases=bases, dct=dct))
        return super().__new__(meta, cls, bases, dct.get_dict())


class parent(metaclass=meta):
    a_float = 3.1416926
    an_int = 44553
    abc = marked(int)

    def __init__(self):
        print("parent:__init__")
        self.set_inside_init = True


class child(parent):
    x = thing()


p = parent()
c = child()

c.x = 6
c.x
del c.x
