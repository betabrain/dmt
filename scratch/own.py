from hypothesis import given, example
from hypothesis.strategies import text


def encode(t):
    b = t.encode('utf8')
    return (len(b), int.from_bytes(b, 'big'))


def decode(x):
    l, v = x
    return v.to_bytes(l, 'big').decode('utf-8')


@given(text())
@example('Hello')
def test_decode_inverts_encode(s):
    assert decode(encode(s)) == s
