import cbor2
import collections
import base36
import heapq
import socket

def server_loop(host='127.0.0.1', port=5354):
    _socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM,
        proto=socket.IPPROTO_UDP,
    )
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    _socket.bind((host, port))
    cache = collections.defaultdict(list)
    state = collections.defaultdict(int)
    while True:
        data, addr = _socket.recvfrom(512)
        print(addr, 'received', len(data))
        req = data[:2]
        flags = int.from_bytes(data[2:4], 'big') | 0b10000001_00000000
        labels = []
        pos = 12
        while data[pos] > 0:
            labels.append(data[pos+1:pos+data[pos]+1])
            pos += 1 + data[pos]
        print(addr, 'labels=', labels)
        print(labels[:-3])

for x in server_loop():
    print('*')
