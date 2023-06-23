import queue
import random
import sys
import threading
import time


def pmap(f, *args, n=80):
    work = queue.Queue()
    done = queue.Queue()

    for item in zip(*args):
        work.put(item)

    n_items = work.qsize()
    x_done = dict()

    def worker():
        item = work.get()
        n = 0
        while item != x_done:
            n += 1
            try:
                done.put(f(*item))
            except Exception as ex:
                done.put(ex)
            item = work.get()

    for tid in range(n):
        work.put(x_done)
        threading.Thread(target=worker, daemon=True).start()

    for _ in range(n_items):
        res = done.get()
        if not isinstance(res, Exception):
            yield res

        else:
            raise res

            sys.exit(1)


def dostuff(x, r):
    time.sleep(r)
    return x * r * ((threading.get_ident() % 11) + 1)


print(sum(pmap(dostuff, range(320), [random.random() for _ in range(320)])))
