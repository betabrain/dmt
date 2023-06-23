import cbor2
import functools
import nacl.public
import nacl.secret
import os
import socket


class boron(object):

    def __init__(self, mine, peer):
        self._mine = nacl.public.PrivateKey(mine)
        self._peer = nacl.public.PublicKey(peer)
        self._box = nacl.public.Box(self._mine, self._peer)

    def __call__(self, name, *args, **kwargs):
        box = nacl.secret.SecretBox(b'a'*32)
        tmp = box.encrypt(cbor2.dumps([name, args, kwargs]))
        print(len(tmp))

    def __getattr__(self, name):
        return functools.partial(self.__call__, name)


mine = nacl.public.PrivateKey.generate()
peer = nacl.public.PrivateKey.generate()

b1 = boron(mine.encode(), peer.public_key.encode())
b2 = boron(peer.encode(), mine.public_key.encode())

b1('')

b1('demo')

b1.login('user', 'pw')
