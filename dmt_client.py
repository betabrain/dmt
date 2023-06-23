import hashlib
import hmac
import os
import socket

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


def sendto(obj: object, host="localhost", port=8443):
    sk = binascii.a2b_hex(
        "d124e42376b5a9aac99ce1e36e99abdcdba02cb47b4180c9def31f540de0ef9f"
    )
    ek = binascii.a2b_hex(
        "740c4dc406a63c6fe5ece80eb30866fda75cfe579cc0781a1e306d47c49359e0"
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.sendto(encode(cbor2.dumps(obj), sk, ek), (host, port))
    sock.close()


if __name__ == "__main__":
    import dmt_client
    for i in range(1000):
        dmt_client.sendto({"i": i, "value": None, "message": "This is a test!"})
