#!/usr/bin/python3.6
################################################################################
# Imports
################################################################################
import arrow
import atexit
import binascii
import collections
import csv
import glob
import itertools
import math
import os
import signal
import struct
import structlog
import sys
import threading


################################################################################
# Logging
################################################################################
logger = structlog.get_logger("hoarder.py")


################################################################################
# Globals
################################################################################
MAX_PRECISION = 7
FILE_MAGIC = b"HOARDERv0001"
STRUCT_FORMAT = ">Id"
FLUSH_INTERVAL = 900

for name in sorted(dir()):
    value = eval(name)
    if name == name.upper() and isinstance(value, (str, int, float, bytes)):
        logger.info(f"{name}: {value}")


################################################################################
# Clean Termination
################################################################################
signal.signal(signal.SIGTERM, lambda *args: sys.exit(1))

################################################################################
# Public Functions
################################################################################


def setup_datapoint(dp_path):
    cookie = binascii.hexlify(os.urandom(5)).decode("utf-8")
    fmt = struct.Struct(STRUCT_FORMAT)
    assert fmt.size == len(FILE_MAGIC)

    current = arrow.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    if not (os.path.exists(dp_path) and os.path.isdir(dp_path)):
        os.mkdir(dp_path)
    fh = open(os.path.join(dp_path, f"{current}.{cookie}"), "ab")
    fh.write(FILE_MAGIC)
    __fhs.add(fh)
    logger.info(f"datapoint file {fh.name} has been initialized")

    def _close_file():
        nonlocal fh
        logger.info(f"closing datapoint file {fh.name} due to shutdown")
        __fhs.remove(fh)
        fh.flush()
        fh.close()
        fh = None

    atexit.register(_close_file)

    def _write_value(value=None):
        nonlocal fh
        nonlocal current

        timestamp = arrow.utcnow()
        interval = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

        if interval > current:
            logger.info(f"closing datapoint file {fh.name} upon change of day")
            __fhs.remove(fh)
            fh.flush()
            fh.close()
            current = interval
            fh = open(os.path.join(dp_path, f"{current}.{cookie}"), "ab")
            fh.write(FILE_MAGIC)
            __fhs.add(fh)
            logger.info(f"datapoint file {fh.name} has been initialized")

        if value is None:
            logger.info(f"closing datapoint file {fh.name} upon request")
            fh.flush()
            fh.close()
            fh = None
            return

        if fh is None:
            logger.error("datapoint file is closed, cannot write value")
        else:
            fh.write(fmt.pack(timestamp.timestamp, round(value, MAX_PRECISION)))

    return _write_value


def read_datapoint(dp_path):
    for interval, group in itertools.groupby(
        glob.glob(os.path.join(dp_path, "*.*")), lambda f: f.split(".")[0]
    ):
        yield from sorted(itertools.chain.from_iterable(map(__read_file, group)))


def compile_csv(csv_path, source_name=None, **dp_names):
    with open(csv_path, "w") as fh:
        writer = csv.writer(fh)
        cache = collections.defaultdict(dict)

        if source_name:
            writer.writerow(["SourceName:", source_name])

        def _get_5min_interval(tup):
            t = arrow.get(tup[0]).replace(microsecond=0, second=0)
            m = math.ceil(t.minute / 5) * 5

            if m == 60:
                m = 0
                t = t.shift(hours=1)

            return t.replace(minute=m)

        for dp_name in dp_names:
            for minute, tuples in itertools.groupby(
                read_datapoint(dp_names[dp_name]), _get_5min_interval
            ):
                tuples = list(tuples)
                cache[minute.timestamp][dp_name] = round(
                    sum(map(lambda t: t[1], tuples)) / len(tuples), MAX_PRECISION
                )

        dp_names = list(sorted(dp_names))
        writer.writerow(["DPName:"] + dp_names)

        for timestamp in sorted(cache.keys()):
            row = [arrow.get(timestamp).replace(second=0).isoformat(sep=" ")[:-9]]
            for dp_name in dp_names:
                row.append(cache[timestamp].get(dp_name, None))
            writer.writerow(row)


################################################################################
# Private Functions
################################################################################
__fhs = set()


def __flusher():
    while True:
        for fh in list(__fhs):
            if fh not in __fhs:
                continue

            time.sleep(FLUSH_INTERVAL / len(__fhs))
            logger.info(f"flushing file {fh.name}")
            try:
                fh.flush()
            except:
                logger.error(f"failed to flush file {fh.name}")


__flusher_thread = threading.Thread(target=__flusher, daemon=True)
__flusher_thread.start()


def __read_file(path):
    fmt = struct.Struct(STRUCT_FORMAT)
    with open(path, "rb") as fh:
        assert fh.read(fmt.size) == FILE_MAGIC
        yield from fmt.iter_unpack(fh.read())


################################################################################
# Test Code
################################################################################
if __name__ == "__main__":
    import random
    import time

    dps = []

    for i in range(10):
        dps.append(setup_datapoint(f"dp{i}"))

    dps_iter = itertools.cycle(dps)
    for _ in range(27 * 3600):
        time.sleep(30 * random.random())
        dp = next(dps_iter)
        dp(random.random())

    for dp in dps[:len(dps) // 2 + 1]:
        dp(None)
        dp(3.14159)
