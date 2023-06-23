import base36
import cbor2
import collections
import concurrent.futures
import functools
import nacl.public
import os
import random
import socket
import time


DOMAIN = 'r.stasi.ws'
SERVER = 'rwcv5n2mmaqohxcf709eimdl56057v0fwqxof2zjm2gemm5wm'
SECRET = '2dicxkgjudhhud4za61y4czwgnol97851v05l60cexo05yb4vd'


###############################################################################
# Helpers
###############################################################################

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def query_dns(name, server='159.100.245.6', port=53):
    _socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM,
        proto=socket.IPPROTO_UDP,
    )
    request = os.urandom(2) + 0b00000000_00000000.to_bytes(2, 'big') + \
        b'\x00\x01\x00\x00\x00\x00\x00\x00'
    for label in (name if name.endswith('.') else name+'.').split('.'):
        request += len(label).to_bytes(1, 'big') + label.encode('ascii')
    request += b'\x00\x01\x00\x01'
    print(request.hex())
    print(_socket.sendto(request, (server, port)))
    data, addr = _socket.recvfrom(512)
    _socket.close()
    if addr == (server, port) and data.startswith(request[:2]):
        print(data.hex())

print(query_dns('f.998d498.t.stasi.ws'))

import sys
sys.exit(0)

###############################################################################
# Objects
###############################################################################

class proxy(object):

    def __init__(self, domain, server, secret):
        self.__domain = domain.split('.')
        self.__pubkey = nacl.public.PublicKey(
            base36.loads(server).to_bytes(32, 'big'))
        self.__privkey = nacl.public.PrivateKey(
            base36.loads(secret).to_bytes(32, 'big'))
        self.__box = nacl.public.Box(self.__privkey, self.__pubkey)
        self.__cnt = 0
        self.__futures = {}
        self.__output = collections.deque()
        self.__input = collections.deque()

    def __ref(self):
        return ((int(time.time()) << 16) +
                (self.__cnt % 2**16)).to_bytes(6, 'big')

    def __serialize(self, obj):
        data = cbor2.dumps(obj)
        n_chunks = 0
        ref = self.__ref()
        while data:
            chunklen = random.randint(4, 105)
            chunk, data = data[:chunklen], data[chunklen:]
            self.__output.append(ref + b'\x00' + chunk)
            n_chunks += 1
        self.__output.append(
            ref + b'\xff' + n_chunks.to_bytes(4, 'big'))

    def __handle_output(self):
        while self.__output:
            query = self.__output.popleft()
            query = self.__box.encrypt(query)
            prefix = base36.dumps(len(query)) + '.'
            query = base36.dumps(int.from_bytes(query, 'big'))
            name = prefix + '.'.join(list(chunks(query, 63)) + self.__domain)
            print('query:', len(name), name[-30:])
            for addr in map(lambda x: x[4][0], socket.getaddrinfo(name, None)):
                print(addr)

    def __handle_input(self):
        pass

    def __call__(self, method, *args, **kwargs):
        ref = self.__ref()
        self.__serialize([1, 'call', ref, method, args, kwargs])
        self.__futures[ref] = concurrent.futures.Future()
        self.__handle_output()
        self.__handle_input()
        return self.__futures[ref]

    def __getattr__(self, name):
        return functools.partial(self.__call__, name)


###############################################################################
# Main / Shell Tests
###############################################################################

if __name__ == '__main__':
    p = proxy(DOMAIN, SERVER, SECRET)
    print(p.hello('world', timestamp=time.time()))
    print(p.goodbye('you', timestamp=time.time(), attachment=list(range(500))))
