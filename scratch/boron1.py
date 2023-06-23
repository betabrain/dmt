import cbor2
import hmac
import hashlib
import ipaddress
import os
import zlib

class boron_stream(object):

    def __init__(self, secret, nonce=None):
        self.__secret = secret
        self.__hash = hashlib.sha3_512(b'boron')
        self._buffer = []

        if nonce is None:
            nonce = os.urandom(32)

        self.__hash.update(self.dumps([
            b'boron',
            1,
            nonce,
            ]))

        self.__hash.update(self.__hash.digest())

    def __keystream(self, n):
        for _ in range(n):
            yield self.__hash.digest()[:1]
            self.__hash.update(self.__hash.digest())

    def __xor(self, data):
        plain = int.from_bytes(data, 'big')
        key = int.from_bytes(b''.join(self.__keystream(len(data))), 'big')
        cipher = plain ^ key
        return cipher.to_bytes(len(data), 'big')

    def __checksum(self, data):
        return hmac.new(self.__secret, data, hashlib.sha3_512).digest()

    def dumps(self, obj):
        data = self.__xor(zlib.compress(cbor2.dumps(obj), 9))
        data = data + self.__checksum(data)[:4]
        self._buffer.append(len(data).to_bytes(1, 'big'))
        self._buffer.append(data)
        return data

    def loads(self, data):
        data, checksum = data[:-4], data[-4:]
        print('checksum is', checksum == self.__checksum(data)[:4])
        return cbor2.loads(zlib.decompress(self.__xor(data)))


class boron(object):

    def __init__(self, secret):
        nonce1 = os.urandom(16)
        self._incoming = boron_stream(secret, nonce)
        self._outgoing

    def __call__(self, name, *args, **kwargs):
        box = nacl.secret.SecretBox(b'a'*32)
        tmp = box.encrypt(cbor2.dumps([name, args, kwargs]))
        print(len(tmp))

    def __getattr__(self, name):
        return functools.partial(self.__call__, name)