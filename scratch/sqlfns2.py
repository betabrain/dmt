import typeguard
import typing

################################################################################
# Text Processing
################################################################################


@typeguard.typechecked
def match(string1: str, string2: str) -> bool:
    import re
    return list(re.findall("[a-z0-9]+", string1.lower())) == list(
        re.findall("[a-z0-9]+", string2.lower())
    )


def test_match():
    assert match("this is a test", " this is a test")
    assert match("This is a Test", "this IS  a test")
    assert match("This-is-a-Test", "this_is.a.test")


@typeguard.typechecked
def number(string: str) -> typing.Union[int, float, None]:
    import re

    for tmp in re.finditer("\d+(\.\d+)?", string):
        tmp = tmp.group(0)
        if "." in tmp:
            return float(tmp)

        else:
            return int(tmp)

        break


def test_number():
    assert 8 == number("8 deg")
    assert 8.5 == number("@ 8.5 eur")
    assert None == number("@ _ eur")


################################################################################
# Binary and Text Encodings
################################################################################


@typeguard.typechecked
def binary(data: typing.Union[str, bytes]) -> bytes:
    if isinstance(data, str):
        return data.encode("utf-8")

    return data


@typeguard.typechecked
def hex(data: typing.Union[str, bytes]) -> str:
    return binary(data).hex()


def test_hex():
    assert hex(b"test") == "74657374"


@typeguard.typechecked
def b62encode(data: typing.Union[str, bytes]) -> str:
    import base62
    return base62.encodebytes(binary(data))


@typeguard.typechecked
def b62decode(data: str) -> bytes:
    import base62
    return base62.decodebytes(data)


def test_base62():
    assert b"a" == b62decode(b62encode("a"))
    tmp = nonce()
    assert tmp == b62decode(b62encode(tmp))


@typeguard.typechecked
def b91encode(data: typing.Union[str, bytes]) -> str:
    import base91
    return base91.encode(binary(data))


@typeguard.typechecked
def b91decode(data: str) -> bytes:
    import base91
    return bytes(base91.decode(data))


def test_base91():
    assert "fPNKd" == b91encode("test")
    assert "fPNKd" == b91encode(b"test")
    assert (
        b"May a moody baby doom a yam?\n"
        == b91decode("8D9Kc)=/2$WzeFui#G9Km+<{VT2u9MZil}[A")
    )
    tmp = nonce()
    assert b91decode(b91encode(tmp)) == tmp


################################################################################
# Cryptography
################################################################################


@typeguard.typechecked
def nonce(n: int = 64) -> bytes:
    import os
    return os.urandom(n)


def test_nonce():
    assert len(nonce(22)) == 22


@typeguard.typechecked
def sha3(data: typing.Union[str, bytes]) -> bytes:
    import hashlib
    return hashlib.sha3_512(binary(data)).digest()


def test_cryptography_sha3():
    assert sha3("test")
    assert sha3(b"test")
    assert len(sha3("test")) == len(sha3("aaaaaaaaaaaaaaaaaaaaaaaa"))


@typeguard.typechecked
def blake2b(data: typing.Union[str, bytes]) -> bytes:
    import hashlib
    return hashlib.sha3_512(binary(data)).digest()


def test_cryptography_blake2b():
    assert blake2b("test")
    assert blake2b(b"test")
    assert len(blake2b("test")) == len(blake2b("aaaaaaaaaaaaaaaaaaaaaaaa"))


@typeguard.typechecked
def sha3hmac(key: typing.Union[str, bytes], data: typing.Union[str, bytes]) -> bytes:
    import hashlib, hmac
    return hmac.new(binary(key), binary(data), hashlib.sha3_512).digest()


def test_cryptography_hmac():
    key = nonce()
    tmp = nonce()
    assert sha3hmac("a", tmp) == sha3hmac("a", tmp)
    assert sha3hmac("b", tmp) != sha3hmac("a", tmp)
    assert sha3hmac(key, tmp) == sha3hmac(key, tmp)
    assert sha3hmac(key, "test") == sha3hmac(key, "test")


@typeguard.typechecked
def signing_key() -> bytes:
    import nacl.signing
    return nacl.signing.SigningKey.generate().encode()


@typeguard.typechecked
def verify_key(signing_key: bytes) -> bytes:
    import nacl.signing

    sk = nacl.signing.SigningKey(signing_key)
    return sk.verify_key.encode()


@typeguard.typechecked
def sign(signing_key: bytes, data: typing.Union[str, bytes]) -> bytes:
    import nacl.signing

    sk = nacl.signing.SigningKey(signing_key)
    return sk.sign(binary(data))


@typeguard.typechecked
def verify(verify_key: bytes, data: bytes) -> bytes:
    import nacl.signing

    vk = nacl.signing.VerifyKey(verify_key)
    try:
        return vk.verify(data)

    except nacl.signing.BadSignatureError:
        return None


def test_cryptography_signatures():
    msg = nonce()
    sk = signing_key()
    vk = verify_key(sk)
    sig = sign(sk, msg)
    assert verify(vk, sig) == msg


################################################################################
# Cookies
################################################################################

# def branca_encode(key, data):
#     import branca
#     return branca.Branca(key).dumps(cbor2.dumps(data))

# def branca_decode(key, data):
#     import branca
#     return cbor2.loads(branca.Branca(key).loads(data))

# def test_cbor2_branca():
#     tmp = {'n': 'xyz', 'pi': 3.14}
#     assert tmp == branca_decode('secret', branca_encode('secret', tmp))


################################################################################
# Data Serialisation
################################################################################


@typeguard.typechecked
def json(obj) -> str:
    import json
    return json.dumps(obj)


@typeguard.typechecked
def unjson(string: str):
    import json
    return json.loads(string)


def test_json():
    tmp = dict(name="donald", pi=3.14, lst=[1, 2], dct=dict())
    assert unjson(json(tmp)) == tmp


@typeguard.typechecked
def yaml(obj) -> str:
    import yaml
    return yaml.dump(obj)


@typeguard.typechecked
def unyaml(string: str):
    import yaml
    return yaml.load(string)


def test_yaml():
    tmp = dict(name="donald", pi=3.14, lst=[1, 2], dct=dict())
    assert unyaml(yaml(tmp)) == tmp


@typeguard.typechecked
def cbor(obj) -> bytes:
    import cbor2
    return cbor2.dumps(obj)


@typeguard.typechecked
def uncbor(string: bytes):
    import cbor2
    return cbor2.loads(string)


def test_cbor():
    tmp = dict(name="donald", pi=3.14, lst=[1, 2], dct=dict())
    assert uncbor(cbor(tmp)) == tmp
