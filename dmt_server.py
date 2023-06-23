import hashlib
import hmac
import os
import socket
import time

import binascii
import cbor2


def key_stream(key: bytes, iv: bytes):
    assert len(key) >= 32
    assert len(iv) >= 16
    while True:
        iv = hashlib.sha256(iv).digest()
        yield from hmac.new(key, iv, hashlib.sha256).digest()


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def encode(data: bytes, sk: bytes, ek: bytes) -> bytes:
    assert len(sk) >= 32
    assert len(ek) >= 32
    iv = os.urandom(16)
    encrypted = iv + xor_bytes(data, key_stream(ek, iv))
    signature = hmac.new(sk, encrypted, hashlib.sha256).digest()[:16]
    return signature + encrypted


def decode(data: bytes, sk: bytes, ek: bytes) -> bytes:
    assert len(sk) >= 32
    assert len(ek) >= 32
    signature = hmac.new(sk, data[16:], hashlib.sha256).digest()[:16]
    if signature == data[:16]:
        return xor_bytes(data[32:], key_stream(ek, data[16:32]))
    else:
        return None


def server(*, sk: bytes, ek: bytes, port: int = 0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("", port))
    print(f"listening on {sock.getsockname()[0]}:{sock.getsockname()[1]}")

    sock.sendto(b"Hello, World!", sock.getsockname())
    sock.sendto(encode(b"Hello, World!", sk, ek), sock.getsockname())
    for i in range(10):
        sock.sendto(
            encode(
                cbor2.dumps([55.34, {0: None, 1: 2.1, "msg": "Hello, World!", "i": i}]),
                sk,
                ek,
            ),
            sock.getsockname(),
        )

    while True:
        cipher, peer = sock.recvfrom(65536)
        plain = decode(cipher, sk, ek)
        if plain:
            try:
                plain = cbor2.loads(plain)
                print(
                    f"{time.time():.6f} {peer[0]:>15s} {peer[1]:5d} {len(cipher):5d} >>> {plain}"
                )
            except Exception as ex:
                print(
                    f"{time.time():.6f} {peer[0]:>15s} {peer[1]:5d} {len(cipher):5d} ERR {ex}"
                )
        else:
            print(f"{time.time():.6f} {peer[0]:>15s} {peer[1]:5d} {len(cipher):5d} SIG")


if __name__ == "__main__":
    server(
        port=8080,
        sk=binascii.a2b_hex(
            "d124e42376b5a9aac99ce1e36e99abdcdba02cb47b4180c9def31f540de0ef9f"
        ),
        ek=binascii.a2b_hex(
            "740c4dc406a63c6fe5ece80eb30866fda75cfe579cc0781a1e306d47c49359e0"
        ),
    )
