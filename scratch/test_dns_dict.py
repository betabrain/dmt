import pprint
import pytest
from .dns_dict import dns_dict


@pytest.mark.parametrize("packet,start,expected,end", [
    (b'\x00\x00', 0, b'.', 1),
    (b'\x00\x00', 1, b'.', 2),
    (b'\x00\x01a\x00', 0, b'.', 1),
    (b'\x00\x01a\x00', 1, b'a.', 4),
    (b'\x04aaaa\x00\x00', 0, b'aaaa.', 6),
    (b'\x04aaaa\x00\x00', 5, b'.', 6),
    (b'\x04aaaa\x00\x00', 6, b'.', 7),
    (b'\x01a\x01a\x00\x00', 0, b'a.a.', 5),
    (b'\x01a\x01a\x00\x00', 2, b'a.', 5),
    (b'\x01a\x01a\x00\x00', 4, b'.', 5),
    (b'\x01a\x01a\x00\x00', 5, b'.', 6),
    (b'\x00\xc0\x00', 0, b'.', 1),
    (b'\x00\xc0\x00', 1, b'.', 3),
    (b'\x00\xc0\x00', 2, b'.', 3),
    (b'\x01a\x00\xc0\x05xxxxx\x00', 0, b'a.', 3),
    (b'\x01a\x00\xc0\x05xxxxx\x00', 2, b'.', 3),
    (b'\x01a\x00\xc0\x05\x05xxxxx\x00', 3, b'xxxxx.', 5),
    (b'\x01a\x00\xc0\x05\x05xxxxx\x00', 5, b'xxxxx.', 12),
    (b'\x01a\x00\xc0\x05\x05xxxxx\x00', 11, b'.', 12),
    (b'\x01a\xc0\x07\x01b\x00\x01c\x00', 0, b'a.c.', 4),
    (b'\x01a\xc0\x07\x01b\x00\x01c\x00', 2, b'c.', 4),
    (b'\x01a\xc0\x07\x01b\x00\x01c\x00', 4, b'b.', 7),
    (b'\x01a\xc0\x07\x01b\x00\x01c\x00', 7, b'c.', 10),

])
def test_read_name(packet, start, expected, end):
    dd = dns_dict(packet, pos=start)
    n = dd.read_name()
    e = dd._pos
    assert n == expected
    assert e == end


def test_all_zero():
    packet = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    for value in dns_dict.from_bytes(packet).values():
        if isinstance(value, bool):
            assert value is False
        elif isinstance(value, int):
            assert value == 0
        elif isinstance(value, list):
            assert len(value) == 0
        else:
            assert False


def test_header_full():
    packet = b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00'
    for value in dns_dict.from_bytes(packet).values():
        if isinstance(value, bool):
            assert value is True
        elif isinstance(value, int):
            assert value > 0
        elif isinstance(value, list):
            assert len(value) == 0
        else:
            assert False


def test_single_empty_qd():
    packet = b'\xff\xff\xff\xff\x00\x01\x00\x00\x00\x00\x00\x00' + \
             b'\x00\x00\x00\x00\x00'
    qd = dns_dict.from_bytes(packet).get('qd_list', [])
    assert len(qd) == 1
    pprint.pprint(qd)
    for value in qd[0].values():
        if isinstance(value, bytes):
            assert value == b'.'
        elif isinstance(value, int):
            assert value == 0
        else:
            assert False


def test_double_empty_qd():
    packet = b'\xff\xff\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00' + \
             b'\x00\x00\x00\x00\x00' + \
             b'\x00\x00\x00\x00\x00'
    qd = dns_dict.from_bytes(packet).get('qd_list', [])
    assert len(qd) == 2
    for xx in qd:
        for value in xx.values():
            if isinstance(value, bytes):
                assert value == b'.'
            elif isinstance(value, int):
                assert value == 0
            else:
                assert False


def test_single_full_qd():
    packet = b'\xff\xff\xff\xff\x00\x01\x00\x00\x00\x00\x00\x00' + \
             b'\x00\xff\xff\xff\xff'
    qd = dns_dict.from_bytes(packet).get('qd_list', [])
    assert len(qd) == 1
    for value in qd[0].values():
        if isinstance(value, bytes):
            assert value == b'.'
        elif isinstance(value, int):
            assert value == 65535
        else:
            assert False


def test_double_full_qd():
    packet = b'\xff\xff\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00' + \
             b'\x00\xff\xff\xff\xff' + \
             b'\x00\xff\xff\xff\xff'
    qd = dns_dict.from_bytes(packet).get('qd_list', [])
    assert len(qd) == 2
    for xx in qd:
        for value in xx.values():
            if isinstance(value, bytes):
                assert value == b'.'
            elif isinstance(value, int):
                assert value == 65535
            else:
                assert False


@pytest.mark.parametrize('ancount,nscount,arcount,rr_list', [
    (b'\x00\x01', b'\x00\x00', b'\x00\x00', 'an_list'),
    (b'\x00\x00', b'\x00\x01', b'\x00\x00', 'ns_list'),
    (b'\x00\x00', b'\x00\x00', b'\x00\x01', 'ar_list'),
])
def test_single_empty_rr(ancount, nscount, arcount, rr_list):
    packet = b'\xff\xff\xff\xff\x00\x00' + ancount + nscount + arcount + \
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    rr = dns_dict.from_bytes(packet).get(rr_list, [])
    assert len(rr) == 1
    for value in rr[0].values():
        if isinstance(value, bytes):
            assert value == b'.' or value == b''
        elif isinstance(value, int):
            assert value == 0
        else:
            assert False


@pytest.mark.parametrize('ancount,nscount,arcount,rr_list', [
    (b'\x00\x02', b'\x00\x00', b'\x00\x00', 'an_list'),
    (b'\x00\x00', b'\x00\x02', b'\x00\x00', 'ns_list'),
    (b'\x00\x00', b'\x00\x00', b'\x00\x02', 'ar_list'),
])
def test_double_empty_rr(ancount, nscount, arcount, rr_list):
    packet = b'\xff\xff\xff\xff\x00\x00' + ancount + nscount + arcount + \
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    rr = dns_dict.from_bytes(packet).get(rr_list, [])
    assert len(rr) == 2
    for xx in rr:
        for value in xx.values():
            if isinstance(value, bytes):
                assert value == b'.' or value == b''
            elif isinstance(value, int):
                assert value == 0
            else:
                assert False


@pytest.mark.parametrize('ancount,nscount,arcount,rr_list', [
    (b'\x00\x01', b'\x00\x00', b'\x00\x00', 'an_list'),
    (b'\x00\x00', b'\x00\x01', b'\x00\x00', 'ns_list'),
    (b'\x00\x00', b'\x00\x00', b'\x00\x01', 'ar_list'),
])
def test_single_full_rr(ancount, nscount, arcount, rr_list):
    packet = b'\xff\xff\xff\xff\x00\x00' + ancount + nscount + arcount + \
             b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x01\xff'
    rr = dns_dict.from_bytes(packet).get(rr_list, [])
    assert len(rr) == 1
    for value in rr[0].values():
        if isinstance(value, bytes):
            assert value == b'.' or value == b'\xff'
        elif isinstance(value, int):
            assert value in (65535, 4294967295)
        else:
            assert False


@pytest.mark.parametrize('ancount,nscount,arcount,rr_list', [
    (b'\x00\x02', b'\x00\x00', b'\x00\x00', 'an_list'),
    (b'\x00\x00', b'\x00\x02', b'\x00\x00', 'ns_list'),
    (b'\x00\x00', b'\x00\x00', b'\x00\x02', 'ar_list'),
])
def test_double_full_rr(ancount, nscount, arcount, rr_list):
    packet = b'\xff\xff\xff\xff\x00\x00' + ancount + nscount + arcount + \
             b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x01\xff' + \
             b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x01\xff'
    rr = dns_dict.from_bytes(packet).get(rr_list, [])
    assert len(rr) == 2
    for xx in rr:
        for value in xx.values():
            if isinstance(value, bytes):
                assert value == b'.' or value == b'\xff'
            elif isinstance(value, int):
                assert value in (65535, 4294967295)
            else:
                assert False


@pytest.mark.parametrize('packet,qds,ans,nss,ars', [
    (bytes.fromhex(
        '2af3012000010000000000010d6469676974616c6d656e7363680263680000ff0001'
        '0000291000000000000000'),
     [{'QNAME': b'digitalmensch.ch.', 'QTYPE': 255, 'QCLASS': 1}],
     [],
     [],
     [{'NAME': b'.', 'TYPE': 41, 'CLASS': 4096, 'TTL': 0, 'RDATA': b''}]),
    (bytes.fromhex(
        '2af3818400010000000000010d6469676974616c6d656e7363680263680000ff0001'
        '0000290600000000000000'),
     [{'QNAME': b'digitalmensch.ch.', 'QTYPE': 255, 'QCLASS': 1}],
     [],
     [],
     [{'NAME': b'.', 'TYPE': 41, 'CLASS': 1536, 'TTL': 0, 'RDATA': b''}]),
    (bytes.fromhex(
        '3b0f01000001000000000000026c62075f646e732d7364045f756470013001300332'
        '343402313007696e2d61646472046172706100000c0001'),
     [{'QNAME': b'lb._dns-sd._udp.0.0.244.10.in-addr.arpa.', 'QTYPE': 12,
       'QCLASS': 1}],
     [],
     [],
     []),
    (bytes.fromhex(
        '3b0f81830001000000010000026c62075f646e732d7364045f756470013001300332'
        '343402313007696e2d61646472046172706100000c0001c024000600010000025800'
        '4108707269736f6e65720469616e61036f7267000a686f73746d61737465720c726f'
        '6f742d73657276657273c0530000000100093a800000003c00093a8000093a80'),
     [{'QNAME': b'lb._dns-sd._udp.0.0.244.10.in-addr.arpa.', 'QTYPE': 12,
       'QCLASS': 1}],
     [],
     [{'CLASS': 1, 'NAME': b'10.in-addr.arpa.',
       'RDATA': b'\x08prisoner\x04iana\x03org\x00\nhostmaster\x0croot-servers'
                b'\xc0S\x00\x00\x00\x01\x00\t:\x80\x00\x00\x00<\x00\t:\x80\x00'
                b'\t:\x80',
       'TTL': 600, 'TYPE': 6}],
     []),
    (bytes.fromhex(
        '595b81800001000a000000010d6469676974616c6d656e7363680263680000ff0001'
        'c00c0001000100000e0f000436faae5cc00c0002000100000e0f000f036e73310865'
        '786f7363616c65c01ac00c0002000100000e0f0012036e73310865786f7363616c65'
        '03636f6d00c00c0002000100000e0f0011036e73310865786f7363616c6502696f00'
        'c00c0002000100000e0f0012036e73310865786f7363616c65036e657400c00c0006'
        '000100000e0f0027c0770561646d696e08646e73696d706c65c066598c8776000151'
        '8000001c2000093a800000012cc00c000f000100000e0f0014000a046d61696c0874'
        '7574616e6f746102646500c00c0010000100000e0f002d2c414c49415320666f7220'
        '7570626561742d627261747461696e2d6330636464622e6e65746c6966792e636f6d'
        'c00c0010000100000e0f002423763d7370663120696e636c7564653a7370662e7475'
        '74616e6f74612e6465202d616c6cc00c0063000100000e0f002423763d7370663120'
        '696e636c7564653a7370662e747574616e6f74612e6465202d616c6c000029020000'
        '0000000000'),
     [{'QCLASS': 1, 'QNAME': b'digitalmensch.ch.', 'QTYPE': 255}],
     [{'CLASS': 1, 'NAME': b'digitalmensch.ch.',
       'RDATA': b'\x00\n\x04mail\x08tutanota\x02de\x00',
       'TTL': 3599, 'TYPE': 15},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.',
       'RDATA': b'\x03ns1\x08exoscale\x02io\x00', 'TTL': 3599, 'TYPE': 2},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.',
       'RDATA': b'\x03ns1\x08exoscale\x03com\x00', 'TTL': 3599, 'TYPE': 2},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.',
       'RDATA': b'\x03ns1\x08exoscale\x03net\x00', 'TTL': 3599, 'TYPE': 2},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.',
       'RDATA': b'\x03ns1\x08exoscale\xc0\x1a', 'TTL': 3599, 'TYPE': 2},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.', 'TTL': 3599,
       'RDATA': b'#v=spf1 include:spf.tutanota.de -all', 'TYPE': 16},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.', 'TTL': 3599,
       'RDATA': b'#v=spf1 include:spf.tutanota.de -all', 'TYPE': 99},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.', 'TTL': 3599,
       'RDATA': b',ALIAS for upbeat-brattain-c0cddb.netlify.com', 'TYPE': 16},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.', 'RDATA': b'6\xfa\xae\\',
       'TTL': 3599, 'TYPE': 1},
      {'CLASS': 1, 'NAME': b'digitalmensch.ch.', 'TTL': 3599,
       'RDATA': b'\xc0w\x05admin\x08dnsimple\xc0fY\x8c\x87v\x00\x01Q\x80\x00'
                b'\x00\x1c \x00\t:\x80\x00\x00\x01,', 'TYPE': 6}],
     [],
     [{'NAME': b'.', 'TYPE': 41, 'CLASS': 512, 'TTL': 0, 'RDATA': b''}]),
    (bytes.fromhex(
        '0000840000000001000000000a5f6e6f6d616368696e65045f746370056c6f63616c'
        '00000c000100000078000805666f676779c00c'),
     [],
     [{'CLASS': 1, 'NAME': b'_nomachine._tcp.local.',
       'RDATA': b'\x05foggy\xc0\x0c', 'TTL': 120, 'TYPE': 12}],
     [],
     []),

])
def test_dns_dict_real_packets(packet, qds, ans, nss, ars):
    dd = dns_dict.from_bytes(packet)
    assert dd is not None
    assert set(map(lambda d: tuple(sorted(d.items())), qds)) == \
        set(map(lambda d: tuple(sorted(d.items())), dd['qd_list']))
    assert set(map(lambda d: tuple(sorted(d.items())), ans)) == \
        set(map(lambda d: tuple(sorted(d.items())), dd['an_list']))
    assert set(map(lambda d: tuple(sorted(d.items())), nss)) == \
        set(map(lambda d: tuple(sorted(d.items())), dd['ns_list']))
    assert set(map(lambda d: tuple(sorted(d.items())), ars)) == \
        set(map(lambda d: tuple(sorted(d.items())), dd['ar_list']))
