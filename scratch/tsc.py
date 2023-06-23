################################################################################
#
################################################################################
import os
import random
import socket
import struct
import time


def tsd_connect(address="./tsd.socket"):
    if os.path.exists(address):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.connect(address)
        return client.send


################################################################################
#
################################################################################


def main():
    x = tsd_connect()

    x(b"TSDC\x82\xa5hello\xa5world\xa2pi\xcb@\t!\xf9\xf0\x1b\x86n")

    for i in range(10):
        i *= random.random()
        x(b"TSDD" + struct.pack(">Qdd", 0, time.time(), 3.14159 * i))
        x(b"TSDD" + struct.pack(">Qdd", 18446744073709551615, time.time(), 3.14159 * i))
        x(b"TSDD" + struct.pack(">Qdd", 314159, time.time(), 3.14159 * i) * 55)


if __name__ == "__main__":
    main()
