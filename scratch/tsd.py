################################################################################
#
################################################################################
import gzip
import msgpack
import os
import queue
import socket
import struct
import sys
import threading
import time


################################################################################
# IO services
################################################################################


def print_server(q, file=sys.stdout):
    while True:
        item = q.get()
        if item:
            print(*item, file=file)
        else:
            break


def stdout(*args):
    series[0].put(args)


def stderr(*args):
    series[18446744073709551615].put(args)


def disk_server(q, path):
    fmt = struct.Struct(">Ld")
    last_write = 0
    while True:
        if (
            q.qsize() > q.maxsize / 2
            or (time.time() - last_write) > 300
            and q.qsize() > 0
        ):
            with gzip.open(path, "ab") as fh:
                while q.qsize():
                    ts, value = q.get()
                    ts = int(ts)
                    value = round(value, 9)
                    fh.write(fmt.pack(ts, value))
        else:
            time.sleep(15)


def start_write_server(path, maxsize=2000, **kwargs):
    q = queue.Queue(maxsize=maxsize)

    if path == "p":
        threading.Thread(target=print_server, args=(q,), kwargs=kwargs).start()
    else:
        threading.Thread(target=disk_server, args=(q, path), kwargs=kwargs).start()

    return q


################################################################################
#
################################################################################


def recv_server(address="./tsd.socket"):
    try:
        os.unlink(address)
    except OSError:
        if os.path.exists(address):
            raise

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    fmt = struct.Struct(">Qdd")

    try:
        sock.bind(address)
        stdout(f"tsd::recv_server running at {address}")

        while True:
            message = sock.recv(32768)

            if message.startswith(b"TSDC"):
                stdout("tsd::recv_server received control message")
                control = msgpack.loads(message[4:], encoding="utf-8")
                stdout(control)
                continue

            if message.startswith(b"TSDD"):
                stdout("tsd::recv_server received data message")
                for sid, timestamp, value in fmt.iter_unpack(message[4:]):
                    q = series.get(sid, None)
                    if q:
                        q.put((timestamp, value))
                continue

    finally:
        sock.close()
        os.unlink(address)


################################################################################
#
################################################################################
series = {
    0: start_write_server("p", file=sys.stdout),
    314159: start_write_server("tsd.data"),
    18446744073709551615: start_write_server("p", file=sys.stderr),
}


################################################################################
#
################################################################################


def main():
    threading.Thread(target=recv_server, daemon=False).start()
    time.sleep(10)


if __name__ == "__main__":
    main()
