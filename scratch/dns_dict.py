''' This is the DNS handling code for dnsrpc

    API:
    dns_dict - a dict-subtype that parses/creates DNS packets
    >>> data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    >>> packet = dns_dict.from_bytes(data)
    >>> packet.to_bytes() == data
    True
'''


class dns_dict(dict):

    def __init__(self, packet=b'', pos=0):
        super().__init__(self)
        self._data = packet
        self._pos = pos

    def read_name(self):
        labels = []
        pos = self._pos
        end = self._pos
        jumped = False

        while True:
            jmp = int.from_bytes(self._data[pos:pos+2], 'big')
            cnt = self._data[pos]

            if jmp >= 49152:
                end = end if jumped else pos + 2
                pos = jmp & 16383
                jumped = True

            elif cnt > 0:
                labels.append(self._data[pos+1:pos+cnt+1])
                pos += cnt + 1
                end = end if jumped else pos

            elif cnt == 0:
                labels.append(b'')
                if not jumped:
                    end += 1
                break

        self._pos = end
        return b'.'.join(labels) if len(labels) > 1 else b'.'

    def read_number(self, length):
        if self._pos + length <= len(self._data):
            num = int.from_bytes(self._data[self._pos:self._pos+length], 'big')
            self._pos += length
            return num
        else:
            raise ValueError('packet too short')

    def decode_qd(self):
        self['QNAME'] = self.read_name()
        self['QTYPE'] = self.read_number(2)
        self['QCLASS'] = self.read_number(2)
        return self._pos

    def decode_rr(self):
        self['NAME'] = self.read_name()
        self['TYPE'] = self.read_number(2)
        self['CLASS'] = self.read_number(2)
        self['TTL'] = self.read_number(4)
        RDLENGTH = self.read_number(2)
        self['RDATA'] = self._data[self._pos:self._pos+RDLENGTH]
        self._pos += RDLENGTH
        return self._pos

    def decode_packet(self):
        self['ID'] = self.read_number(2)
        flags = self.read_number(2)
        self['QR'] = bool((0b10000000_00000000 & flags) >> 15)
        self['OP'] = (0b01111000_00000000 & flags) >> 11
        self['AA'] = bool((0b00000100_00000000 & flags) >> 10)
        self['TC'] = bool((0b00000010_00000000 & flags) >> 9)
        self['RD'] = bool((0b00000001_00000000 & flags) >> 8)
        self['RA'] = bool((0b00000000_10000000 & flags) >> 7)
        self['ZZ'] = (0b00000000_01110000 & flags) >> 4
        self['RC'] = (0b00000000_00001111 & flags) >> 0
        QDCOUNT = self.read_number(2)
        ANCOUNT = self.read_number(2)
        NSCOUNT = self.read_number(2)
        ARCOUNT = self.read_number(2)
        self['qd_list'] = []
        for _ in range(QDCOUNT):
            self['qd_list'].append(dns_dict(self._data, self._pos))
            self._pos = self['qd_list'][-1].decode_qd()
        self['an_list'] = []
        for _ in range(ANCOUNT):
            self['an_list'].append(dns_dict(self._data, self._pos))
            self._pos = self['an_list'][-1].decode_rr()
        self['ns_list'] = []
        for _ in range(NSCOUNT):
            self['ns_list'].append(dns_dict(self._data, self._pos))
            self._pos = self['ns_list'][-1].decode_rr()
        self['ar_list'] = []
        for _ in range(ARCOUNT):
            self['ar_list'].append(dns_dict(self._data, self._pos))
            self._pos = self['ar_list'][-1].decode_rr()
        return self._pos

    @classmethod
    def from_bytes(cls, packet):
        tmp = cls(packet)
        tmp.decode_packet()
        return tmp
