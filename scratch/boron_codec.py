import cbor2
import functools
import hashlib
import hmac
import os
import zlib


NONCE = 32
CHECK = 10
CHUNK = 200


class boron_codec(object):

    def __init__(self, secret, nonce=None):
        self.__nonce = nonce
        self.__chksum = functools.partial(
            hmac.new,
            secret,
            digestmod=hashlib.sha3_512
            )
        self.__secret = self.__chksum(secret).digest()

    def __transform(self, data, nonce):
        key = []
        tmp = self.__chksum(nonce).digest()
        for _ in range(len(data)):
            tmp = self.__chksum(nonce + tmp).digest()
            key.append(tmp[:1])
        tmp = (int.from_bytes(b''.join(key), 'little') ^
               int.from_bytes(data, 'little'))
        return tmp.to_bytes(len(data), 'little')

    def dumps(self, obj):
        nonce = self.__nonce if self.__nonce is not None else os.urandom(NONCE)
        data = self.__transform(
            zlib.compress(cbor2.dumps(obj), 9),
            nonce,
            )
        if self.__nonce:
            return data + self.__chksum(nonce + data).digest()[:CHECK]
        else:
            return nonce + data + self.__chksum(nonce + data).digest()[:CHECK]

    def loads(self, data):
        if self.__nonce:
            nonce, data, checksum = self.__nonce, data[:-CHECK], data[-CHECK:]
        else:
            nonce, data, checksum = data[:NONCE], data[NONCE:-CHECK], data[-CHECK:]
        if self.__chksum(nonce + data).digest()[:CHECK] == checksum:
            return cbor2.loads(zlib.decompress(self.__transform(data, nonce)))
        else:
            return None


class boron_stream(object):

    def __init__(self, key):
        self.__nonce = os.urandom(NONCE)
        self.__chunks = []
        self.__chunkid = 0

    def buffer_for_writing(self, data):
        while data:
            chunk, data = data[:CHUNK], data[CHUNK:]
            self.__buffer.append(self.__chunkid.to_bytes(2) + chunk)
            self.__chunkid += 1
            self.__chunkid %= 65536
