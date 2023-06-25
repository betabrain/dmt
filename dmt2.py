import asyncio
import hashlib
import hmac
import os
import random
import socket
import struct

import cbor2


def key_stream(key: bytes, iv: bytes):
    assert len(key) >= 32
    assert len(iv) >= 16
    while True:
        iv = hashlib.sha256(iv).digest()
        yield from hmac.new(key, iv, hashlib.sha256).digest()


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


class DMT:
    def __init__(self, sk, ek, sock, peer):
        self._sk = sk
        self._ek = ek
        self._socket = sock
        self._socket.setblocking(False)
        self._peer = peer
        self._unacknowledged = {}
        self._received = set()
        self._packet_num = 0

    def enqueue(self, obj):
        print(f"sending: {self._packet_num} {obj}")
        packet = struct.pack('>Q', self._packet_num) + cbor2.dumps(obj)
        self._packet_num += 1
        ack = self._calc_ack(packet)
        self._unacknowledged[ack] = packet

    async def receive_loop(self):
        loop = asyncio.get_event_loop()
        while True:
            data, peer = await loop.sock_recvfrom(self._socket, 65536)
            if random.random() < 0.67:
                continue
            plain = self._unwrap(data)
            if plain is not None:
                self._peer = peer
                if plain in self._unacknowledged:
                    del self._unacknowledged[plain]
                else:
                    ack = self._calc_ack(plain)
                    await loop.sock_sendto(self._socket, self._wrap(ack), peer)
                    packet_num = struct.unpack('>Q', plain[:8])[0]
                    if packet_num not in self._received:
                        packet_num = struct.unpack('>Q', plain[:8])[0]
                        self._received.add(packet_num)
                        obj = cbor2.loads(plain[8:])
                        print(f"received: {packet_num} {obj}")

    async def send_loop(self):
        loop = asyncio.get_event_loop()
        while True:
            if self._unacknowledged:
                packet = random.choice(list(self._unacknowledged.values()))
                packet = self._wrap(packet)
                await loop.sock_sendto(self._socket, packet, self._peer)
            await asyncio.sleep(0.5)


    def _calc_ack(self, packet):
        return hashlib.sha256(packet).digest()

    def _wrap(self, packet):
        iv = os.urandom(16)
        packet = iv + xor_bytes(key_stream(self._ek, iv), packet)
        sig = hmac.new(self._sk, packet, digestmod=hashlib.sha256).digest()[:16]
        return sig + packet

    def _unwrap(self, packet):
        vrf = packet[:16]
        sig = hmac.new(self._sk, packet[16:], digestmod=hashlib.sha256).digest()[:16]
        if hmac.compare_digest(vrf, sig):
            return xor_bytes(key_stream(self._ek, packet[16:32]), packet[32:])
        else:
            return None


if __name__ == '__main__':
    sk = os.urandom(32)
    ek = os.urandom(32)

    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s1.bind(('', 0))
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s2.bind(('', 0))

    d1 = DMT(sk, ek, s1, peer=('127.0.0.1', s2.getsockname()[1]))
    d2 = DMT(sk, ek, s2, peer=('127.0.0.1', s1.getsockname()[1]))
    d1.enqueue({"m": "Hello, World!", "r": random.random()})
    d1.enqueue({"m": "Goodbye!", "r": random.random()})
    d2.enqueue({"m": "This is a test!", "r": random.random()})

    loop = asyncio.get_event_loop()
    loop.create_task(d1.receive_loop())
    loop.create_task(d1.send_loop())
    loop.create_task(d2.receive_loop())
    loop.create_task(d2.send_loop())
    loop.run_forever()
