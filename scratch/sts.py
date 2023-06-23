################################################################################
# Imports
################################################################################
import atexit
import gzip
import msgpack
import os
import signal
import struct
import threading
import time


################################################################################
# Globals
################################################################################


################################################################################
# Simple Time Series (simplets)
################################################################################


def _create_simplets(path, **meta):
    with gzip.open(path, "wb") as fh:
        tsid = os.urandom(8)
        fh.write(b"simplets" + tsid)
        meta = msgpack.dumps(dict(meta), encoding="utf-8")
        meta_len = len(meta)
        fh.write(struct.pack(">H", meta_len))
        fh.write(meta)
        fh.write(b"\x00" * (990 - meta_len))
        fh.write(b"simplets" + tsid)


def simplets(path):
    if not os.path.exists(path):
        _create_simplets(path, format=">Ld", created=time.time(), filename=path)

    with gzip.open(path, "rb") as fh:
        assert fh.read(8) == b"simplets"
        tsid = fh.read(8)
        meta_len = struct.unpack(">H", fh.read(2))[0]
        meta = fh.read(990)
        assert fh.read(8) == b"simplets"
        assert fh.read(8) == tsid

    tsid = struct.unpack(">Q", tsid)[0]
    meta = msgpack.loads(meta[:meta_len], encoding="utf-8")

    print(tsid)
    print(meta)

    xx = struct.Struct(meta["format"])

    active_queue = list()

    def flusher():
        nonlocal active_queue
        while True:
            if len(active_queue) > 0:
                flush_queue = active_queue
                active_queue = list()
                time.sleep(5)
                print(f"flushing {len(flush_queue)} records")
                with gzip.open(path, "ab") as fh:
                    fh.write(b"".join(flush_queue))
                del flush_queue
                time.sleep(60)
            else:
                time.sleep(90)

            time.sleep(45)

    threading.Thread(target=flusher, daemon=True).start()

    last_ts = 0

    def record_value(value):
        nonlocal last_ts
        ts = int(time.time())
        td = ts - last_ts
        last_ts = ts

        active_queue.append(xx.pack(td, round(value, 9)))

    return record_value


record = simplets("demo.sts")


################################################################################
# Background Threads
################################################################################


################################################################################
# Module Initialisation
################################################################################


def cleanup(*args):
    pass


signal.signal(signal.SIGTERM, cleanup)
atexit.register(cleanup)
