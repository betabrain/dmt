import functools
import os

from . import boron_codec
from . import dns_dict


class dnsrpc(object):

    def __init__(self, domain, secret, nonce=None):
        self.__domain = domain
        nonce = os.urandom(boron_codec.NONCE) if nonce is None else nonce
        self._incoming = None
        self._outgoing = boron_codec.boron_codec(secret, nonce)

    def __call__(self, name, *args, **kwargs):
        msg = self._outgoing.dumps(['dnsrpc', 1, name, args, kwargs]).hex()
        labels = []
        while msg:
            label, msg = msg[:63], msg[63:]
            labels.append(label+'.')
        labels.append(self.__domain)
        return ''.join(labels)

    def __getattr__(self, name):
        return functools.partial(self.__call__, name)
