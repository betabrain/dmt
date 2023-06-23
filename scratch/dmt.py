import hashlib
import hmac
import os


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


if __name__ == "__main__":
    sk = os.urandom(128)
    ek = os.urandom(128)

    msg = "Hallo, Welt!".encode("utf8")
    print(msg.hex(), len(msg))
    print(encode(msg, sk, ek).hex())

    for _ in range(10):
        plain = os.urandom(200)
        cipher = encode(plain, sk, ek)
        result = decode(cipher, sk, ek)
        assert cipher != plain
        assert plain == result
        assert len(cipher) == len(plain) + 32
