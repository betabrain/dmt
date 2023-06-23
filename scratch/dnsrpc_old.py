import attr
import socket
import pytest
import silo


###############################################################################
# Helpers
###############################################################################

def parse_name(data, start):
    labels = []
    pos = start
    end = start
    jumped = False

    while True:
        jmp = int.from_bytes(data[pos:pos+2], 'big')
        cnt = data[pos]

        if jmp >= 49152:
            end = end if jumped else pos + 2
            pos = jmp & 16383
            jumped = True

        elif cnt > 0:
            labels.append(data[pos+1:pos+cnt+1])
            pos += cnt + 1
            end = end if jumped else pos

        elif cnt == 0:
            labels.append(b'')
            if not jumped:
                end += 1
            break

    return b'.'.join(labels) if len(labels) > 1 else b'.', end

def decode_name(packet, data):
    silo.info('decode_name')
    print('start')
    print('packet', packet)
    print('data', data)
    ret = None
    segments = []
    while True:
        jmp = int.from_bytes(data[0:2], 'big')
        cnt = data[0]
        if jmp >= 49152:
            print('jmp')
            jmp = jmp & 16383
            print(jmp)
            if ret is None:
                ret = data[2:]
            data = packet[jmp:]
            continue
        elif cnt > 0:
            print('cnt', cnt)
            segments.append(data[1:1+cnt])
            data = data[1+cnt:]
        elif cnt == 0:
            print('done')
            print('ret', ret)
            print('data', data)
            print(segments)
            return b'.'.join(segments) + b'.', ret if ret is not None else data[1:]
        else:
            raise Exception('should not happen')


@pytest.mark.parametrize("packet,data,expected,remainder", [
    (b'', b'\x00', b'.', b''),
    (b'', b'\x02aa\x01a\x00', b'aa.a.', b''),
    (b'', b'\x02bb\x00\xff\xff', b'bb.', b'\xff\xff'),
])
def test_decode_name_simple(packet, data, expected, remainder):
    name, data = decode_name(packet, data)
    assert name == expected
    assert data == remainder


@pytest.mark.parametrize("packet,data,expected,remainder", [
    (b'\xff'*12 + b'\x00', b'\xc0\x0c', b'.', b''),
    (b'\xff'*12 + b'\x02aa\x01a\x00', b'\xc0\x0c', b'aa.a.', b''),
    (b'\xff'*14 + b'\x02bb\x00\xff\xff', b'\xc0\x0e\xaa\xaa', b'bb.', b'\xaa\xaa'),
])
def test_decode_name_compressed(packet, data, expected, remainder):
    name, data = decode_name(packet, data)
    assert name == expected
    assert data == remainder


def encode_name(name):
    if name == b'.':
        return b'\x00'
    segments = name.split(b'.')
    tmp = []
    for segment in segments:
        tmp.append(len(segment).to_bytes(1, 'big') + segment)
    return b''.join(tmp)


@pytest.mark.parametrize("name,expected", [
    (b'.', b'\x00'),
    (b'aa.a.', b'\x02aa\x01a\x00'),
    (b'bb.', b'\x02bb\x00'),
])
def test_encode_name_simple(name, expected):
    data = encode_name(name)
    assert data == expected


def decode_number(data, length):
    return int.from_bytes(data[0:length], 'big'), data[length:]


def encode_number(number, length):
    return number.to_bytes(length, 'big')


###############################################################################
# DNS Types
###############################################################################

@attr.s(frozen=True, slots=True)
class dns_qd(object):
    QNAME = attr.ib()
    QTYPE = attr.ib()
    QCLASS = attr.ib()

    @classmethod
    def from_bytes(cls, packet, data):
        silo.info('from_bytes')
        QNAME, data = decode_name(packet, data)
        QTYPE, data = decode_number(data, 2)
        QCLASS, data = decode_number(data, 2)
        return cls(QNAME, QTYPE, QCLASS)

    def to_bytes(self):
        return encode_name(self.QNAME) + \
               encode_number(self.QTYPE, 2) + \
               encode_number(self.QCLASS, 2)

    def __len__(self):
        return len(self.to_bytes())


QD_TEST_TABLE = [
    (b'',
     b'\x06\x67\x6f\x6f\x67\x6c\x65\x03\x63\x6f\x6d\x00\x00\x10\x00\x01',
     b'google.com.', 16, 1),
    (b'',
     b'\x06\x67\x6f\x6f\x67\x6c\x65\x03\x63\x6f\x6d\x00\x00\x0f\x00\x01',
     b'google.com.', 15, 1),
    (b'',
     b'\x0d\x69\x6e\x74\x65\x72\x6e\x61\x6c\x63\x68\x65\x63\x6b\x05\x61'
     b'\x70\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x01\x00\x01',
     b'internalcheck.apple.com.', 1, 1),
    (b'',
     b'\x06google\x03com\x00\x00\x01\x00\x01', b'google.com.', 1, 1),
    (b'',
     b'\x01a\x01a\x00\xff\xff\xff\xff', b'a.a.', 65535, 65535),
    (b'',
     b'\x0f012345678912345\x00\x00\x03\x00\x0e', b'012345678912345.', 3, 14),
]


@pytest.mark.parametrize("packet,data,qname,qtype,qclass", QD_TEST_TABLE)
def test_dns_qd_from_bytes(packet, data, qname, qtype, qclass):
    qd = dns_qd.from_bytes(packet, data)
    assert qd.QNAME == qname
    assert qd.QTYPE == qtype
    assert qd.QCLASS == qclass


@pytest.mark.parametrize("packet,data,qname,qtype,qclass", QD_TEST_TABLE)
def test_dns_qd_to_bytes(packet, data, qname, qtype, qclass):
    qd = dns_qd(qname, qtype, qclass).to_bytes()
    assert data == qd


@pytest.mark.parametrize("packet,data,qname,qtype,qclass", QD_TEST_TABLE)
def test_dns_qd_length(packet, data, qname, qtype, qclass):
    qd = dns_qd(qname, qtype, qclass)
    assert len(data) == len(qd)


@attr.s(frozen=True, slots=True)
class dns_rr(object):
    NAME = attr.ib()
    TYPE = attr.ib()
    CLASS = attr.ib()
    TTL = attr.ib()
    RDATA = attr.ib()
    _length = attr.ib(default=None)

    @classmethod
    def from_bytes(cls, packet, data):
        silo.info('from_bytes')
        NAME, data = decode_name(packet, data)
        TYPE, data = decode_number(data, 2)
        CLASS, data = decode_number(data, 2)
        TTL, data = decode_number(data, 4)
        RDLENGTH, data = decode_number(data, 2)
        silo.info('from_bytes', rdlength=RDLENGTH)
        RDATA, data = data[0:RDLENGTH], data[RDLENGTH:]
        silo.info('from_bytes', rdata=RDATA, l=len(RDATA))
        return cls(NAME, TYPE, CLASS, TTL, RDATA)

    def to_bytes(self):
        return encode_name(self.NAME) + \
               encode_number(self.TYPE, 2) + \
               encode_number(self.CLASS, 2) + \
               encode_number(self.TTL, 4) + \
               encode_number(len(self.RDATA), 2) + \
               self.RDATA

    def __len__(self):
        if self._length is None:
            self._length = len(self.to_bytes())
        return self._length


RR_TEST_TABLE = [
    (b'',
     b'\x00\x00\x10\x00\x01\x00\x00\x01\x23\x00\x24\x23\x76\x3d\x73'
     b'\x70\x66\x31\x20\x69\x6e\x63\x6c\x75\x64\x65\x3a\x5f\x73\x70\x66'
     b'\x2e\x67\x6f\x6f\x67\x6c\x65\x2e\x63\x6f\x6d\x20\x7e\x61\x6c\x6c',
     b'.', 16, 1, 291,
     b'\x23\x76\x3d\x73\x70\x66\x31\x20\x69\x6e\x63\x6c\x75\x64\x65\x3a\x5f'
     b'\x73\x70\x66\x2e\x67\x6f\x6f\x67\x6c\x65\x2e\x63\x6f\x6d\x20\x7e'
     b'\x61\x6c\x6c'),
    (b'', b'\x00\x00\x01\x00\x01\x00\x00\x00\x01\x00\x00', b'.', 1, 1, 1, b''),
    (b'',
     b'\x02bb\x00\xff\xff\x00\x00\xff\xff\xff\xff\x00\x05aaaaa',
     b'bb.', 65535, 0, 4294967295, b'aaaaa'),
    (b'',
     b'\x02bb\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x05aaaaa',
     b'bb.', 0, 65535, 4294967295, b'aaaaa'),
    (b'',
     b'\x02bb\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x05aaaaaXXX',
     b'bb.', 0, 65535, 4294967295, b'aaaaa'),
    (b'\x01a\x00',
     b'\xc0\x00\xff\xff\xff\xff\x00\x00\xff\xff\x00\x05aaaaa', b'a.',
     65535, 65535, 65535, b'aaaaa'),
]


@pytest.mark.parametrize("packet,data,name,type_,class_,ttl,rdata", RR_TEST_TABLE)
def test_dns_rr_from_bytes(packet, data, name, type_, class_, ttl, rdata):
    rr = dns_rr.from_bytes(packet, data)
    assert rr.NAME == name
    assert rr.TYPE == type_
    assert rr.CLASS == class_
    assert rr.TTL == ttl
    assert rr.RDATA == rdata



@pytest.mark.parametrize("packet,data,name,type_,class_,ttl,rdata", RR_TEST_TABLE[:-2])
def test_dns_rr_to_bytes(packet, data, name, type_, class_, ttl, rdata):
    rr = dns_rr(name, type_, class_, ttl, rdata).to_bytes()
    assert data == rr


@pytest.mark.parametrize("packet,data,name,type_,class_,ttl,rdata", RR_TEST_TABLE[:-2])
def test_dns_rr_rr_length(packet, data, name, type_, class_, ttl, rdata):
    rr = dns_rr(name, type_, class_, ttl, rdata)
    assert len(data) == len(rr)


@attr.s(frozen=True, slots=True)
class dns_packet(object):
    ID = attr.ib()
    QR = attr.ib(convert=bool)
    OP = attr.ib()
    AA = attr.ib(convert=bool)
    TC = attr.ib(convert=bool)
    RD = attr.ib(convert=bool)
    RA = attr.ib(convert=bool)
    ZZ = attr.ib()
    RC = attr.ib()
    qd_list = attr.ib()
    an_list = attr.ib()
    ns_list = attr.ib()
    ar_list = attr.ib()

    @classmethod
    def from_bytes(cls, data):
        packet = data
        ID, data = decode_number(data, 2)
        flags, data = decode_number(data, 2)
        QR = (0b10000000_00000000 & flags) >> 15
        OP = (0b01111000_00000000 & flags) >> 11
        AA = (0b00000100_00000000 & flags) >> 10
        TC = (0b00000010_00000000 & flags) >> 9
        RD = (0b00000001_00000000 & flags) >> 8
        RA = (0b00000000_10000000 & flags) >> 7
        ZZ = (0b00000000_01110000 & flags) >> 4
        RC = (0b00000000_00001111 & flags) >> 0
        QDCOUNT, data = decode_number(data, 2)
        ANCOUNT, data = decode_number(data, 2)
        NSCOUNT, data = decode_number(data, 2)
        ARCOUNT, data = decode_number(data, 2)

        print('ID', ID)
        print('QDCOUNT', QDCOUNT)
        print('ANCOUNT', ANCOUNT)
        print('NSCOUNT', NSCOUNT)
        print('ARCOUNT', ARCOUNT)
        print('header done')

        qds = []
        for _ in range(QDCOUNT):
            qds.append(dns_qd.from_bytes(packet, data))
            silo.info('qds', data_before=data)
            data = data[len(qds[-1]):]
            silo.info('qds', data_after=data)
        print('qds', qds)

        ans = []
        for _ in range(ANCOUNT):
            ans.append(dns_rr.from_bytes(packet, data))
            silo.info('ans', data_before=data)
            silo.info('[-1]', l=len(ans[-1]))
            data = data[len(ans[-1]):]
            silo.info('ans', data_after=data)
        print('ans', ans)

        nss = []
        for _ in range(NSCOUNT):
            nss.append(dns_rr.from_bytes(packet, data))
            silo.info('nss', data_before=data)
            data = data[len(nss[-1]):]
            silo.info('nss', data_after=data)
        print('nss', nss)

        ars = []
        for _ in range(ARCOUNT):
            ars.append(dns_rr.from_bytes(packet, data))
            silo.info('ars', data_before=data)
            data = data[len(ars[-1]):]
            silo.info('ars', data_after=data)
        print('ars', ars)

        return cls(ID, QR, OP, AA, TC, RD, RA, ZZ, RC, qds, ans, nss, ars)


def test_dns_packet_from_bytes_1():
    p = b'\xff\xff\x00\x00\x00\x01\x00\x02\x00\x03\x00\x04' + \
        b'\x02qd\x00\xff\xff\x00\x01' + \
        b'\x02an\x00\xbb\xbb\xdd\xdd\x00\x00\x00\x00\x00\x05data1' + \
        b'\x02an\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data2' + \
        b'\x02ns\x00\xbb\xbb\xdd\xdd\x00\x00\x00\x00\x00\x05data1' + \
        b'\x02ns\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data2' + \
        b'\x02ns\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data3' + \
        b'\x02ar\x00\xbb\xbb\xdd\xdd\x00\x00\x00\x00\x00\x05data1' + \
        b'\x02ar\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data2' + \
        b'\x02ar\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data3' + \
        b'\x02ar\x00\xbb\xbb\xdd\xdd\xff\xff\xff\xff\x00\x05data4'

    assert dns_packet.from_bytes(p) is not None


def test_dns_packet_from_bytes_2():
    p = b'\xc7\x84\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\x0d\x63\x6f\x6e' + \
        b'\x66\x69\x67\x75\x72\x61\x74\x69\x6f\x6e\x05\x61\x70\x70\x6c\x65' + \
        b'\x03\x63\x6f\x6d\x07\x65\x64\x67\x65\x6b\x65\x79\x03\x6e\x65\x74' + \
        b'\x00\x00\x01\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x01\x22\x00' + \
        b'\x16\x05\x65\x35\x31\x35\x33\x02\x65\x39\x0a\x61\x6b\x61\x6d\x61' + \
        b'\x69\x65\x64\x67\x65\xc0\x2c\xc0\x41\x00\x01\x00\x01\x00\x00\x00' + \
        b'\x0c\x00\x04\x17\xcd\xb5\x1e'

    assert dns_packet.from_bytes(p) is not None


def test_dns_packet_from_bytes_3():
    p = b'\xb8\xe8\x56\x24\xb8\x9e\xe8\xfc\xaf\xfd\x49\x88\x08\x00\x45\x00' + \
        b'\x00\x7a\x00\x00\x40\x00\x40\x11\xb7\x1d\xc0\xa8\x01\x01\xc0\xa8' + \
        b'\x01\x04\x00\x35\xf7\x5d\x00\x66\xc4\x4a\x42\x6b\x81\x80\x00\x01' + \
        b'\x00\x00\x00\x01\x00\x00\x0d\x69\x6e\x74\x65\x72\x6e\x61\x6c\x63' + \
        b'\x68\x65\x63\x6b\x05\x61\x70\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00' + \
        b'\x01\x00\x01\xc0\x1a\x00\x06\x00\x01\x00\x00\x01\x6e\x00\x29\x05' + \
        b'\x61\x64\x6e\x73\x31\xc0\x1a\x0a\x68\x6f\x73\x74\x6d\x61\x73\x74' + \
        b'\x65\x72\xc0\x1a\x77\xcf\xd2\x88\x00\x00\x03\x84\x00\x00\x03\x84' + \
        b'\x00\x1e\xc3\x00\x00\x01\x51\xe4'

    assert dns_packet.from_bytes(p) is not None


class dnsrpc_server(object):

    def __init__(self, host='0.0.0.0', port=53):
        self._host = host
        self._port = port
        self._socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP,
        )
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind((self._host, self._port))

    def handle_packet(self):
        data, addr = self._socket.recvfrom(512)
        print(addr)
        packet = dns_packet.from_bytes(data)
        print(packet)
