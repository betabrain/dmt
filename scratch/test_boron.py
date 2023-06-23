import os
import pytest
from .boron_codec import boron_codec


@pytest.mark.parametrize('value', [
    1,
    3.141519,
    None,
    'a string',
    b'some bytes',
    ['list', 'of', 'stuff', 1.2, 44439],
    {'a': 'dict', 'of': 'stuff', 3.14: 999},
    {'nested': {77: [{'b': [1, b'byte']}, {'a': 8.8}]}},

])
def test_encode_values(value):
    codec = boron_codec(b'a-bad-secret')
    tmp = codec.dumps(value)
    assert isinstance(tmp, bytes)
    assert len(tmp) > 20
    print(tmp.hex())


@pytest.mark.parametrize('expected,data', [
    (1,
     bytes.fromhex('016d4068e7533078d2238009650cc3399a241a5e8a6a97e978417cbf'
                   '5c9f4bd5c7fa80972d0ad93642364520e92620fcb0658d')),
    (3.141519,
     bytes.fromhex('af4ebfb397ded4b3d94fa5bf804a22cd705e9efa0f388ceb39f5c76f'
                   '1fd8e668d94a8e106639ba5b8b9f29e11d7182f0523608107d3ee242'
                   'a1fa39')),
    (None,
     bytes.fromhex('80924199972aee443e76c093003aece9b11c8f3ccf933b67d012d8b4'
                   '5c808d1e840e19ee9a7872b4d83dd3ce71d45b34b7d6a6')),
    ('a string',
     bytes.fromhex('b5d53fd1232172770d191de695603c9fd98b9fccbb041da7a21ca280'
                   '74d32a61eb97e9a6c3e8f5edc9b57f1748e90af563475f07ae2fcdef'
                   'f3d0d6')),
    (b'some bytes',
     bytes.fromhex('764254d6eb878488d675ac8e32c6d792b847bd9beca54c1f937038d1'
                   '0221ecc78a20617ba978d738833a097841f5b9f9137d5dbeaff3ed62'
                   'a7a01145eb')),
    (['list', 'of', 'stuff', 1.2, 44439],
     bytes.fromhex('911e4e09590317f982af8f807a5dd2059b9ca768d099c5aff9eb1231'
                   '3710021dad8d4768bea09506f094bdc5491b2cc31a310cf8226a4020'
                   '5f14a87f72e7c3ea6a474b06c1e555da4652')),
    ({'a': 'dict', 'of': 'stuff', 3.14: 999},
     bytes.fromhex('de520f292e8b22cdfc6c070bb8168104ac7edaf375a53a2369cfc0b2'
                   '3e504b4d647ce66102f4da8a789a883efb774bbb0d2b6e8f890bcebb'
                   '8a4c09dd6ec30f7d39ea7bcffc296c5220908102e957b3')),
    ({'nested': {77: [{'b': [1, b'byte']}, {'a': 8.8}]}},
     bytes.fromhex('c79d6de8812f7056df215dc23c34903c1548094b1562914adbe26414'
                   '2cbbdbd161efdf0b8cf7c70e304ee0e533ffbe9ec970c734989f538e'
                   'a564282a5b4f5d14005377b204c0509418e24b3c98e25122d507')),

])
def test_decode_known_values(expected, data):
    codec = boron_codec(b'a-bad-secret')
    tmp = codec.loads(data)
    assert tmp == expected


@pytest.mark.parametrize('value', [
    1,
    3.141519,
    None,
    'a string',
    b'some bytes',
    ['list', 'of', 'stuff', 1.2, 44439],
    {'a': 'dict', 'of': 'stuff', 3.14: 999},
    {'nested': {77: [{'b': [1, b'byte']}, {'a': 8.8}]}},

])
def test_decode_encode_values(value):
    codec = boron_codec(os.urandom(32))
    tmp = codec.loads(codec.dumps(value))
    assert tmp == value


@pytest.mark.parametrize('value', [
    1,
    3.141519,
    None,
    'a string',
    b'some bytes',
    ['list', 'of', 'stuff', 1.2, 44439],
    {'a': 'dict', 'of': 'stuff', 3.14: 999},
    {'nested': {77: [{'b': [1, b'byte']}, {'a': 8.8}]}},

])
def test_decode_encode_values_fixed_nonce(value):
    key = os.urandom(32)
    nonce = os.urandom(24)
    codec1 = boron_codec(key, nonce)
    codec2 = boron_codec(key, nonce)
    codec3 = boron_codec(os.urandom(32))
    xxx = codec1.dumps(value)
    val = codec2.loads(xxx)
    yyy = codec3.dumps(value)
    assert len(xxx) < len(yyy)
    assert value == val
    assert codec3.loads(xxx) is None
    assert codec1.loads(yyy) is None


@pytest.mark.parametrize('value', [
    1,
    3.141519,
    None,
    'a string',
    b'some bytes',
    ['list', 'of', 'stuff', 1.2, 44439],
    {'a': 'dict', 'of': 'stuff', 3.14: 999},
    {'nested': {77: [{'b': [1, b'byte']}, {'a': 8.8}]}},

])
def test_decode_encode_values_other_nonce(value):
    key = os.urandom(32)
    codec1 = boron_codec(key, os.urandom(24))
    codec2 = boron_codec(key, os.urandom(24))
    xxx = codec1.dumps(value)
    yyy = codec2.dumps(value)
    assert xxx != yyy
