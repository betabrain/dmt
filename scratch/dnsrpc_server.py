'''

    API:
    >>> s = dnsrpc_server()
    >>> def gimme_pi(please=False):
    ...     if please:
    ...         return 3.14159
    >>> s.register(gimme_pi)
    >>> print(s.token())
'''

import socket


###############################################################################
# Helpers
###############################################################################


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
