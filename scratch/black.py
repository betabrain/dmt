#!/usr/bin/python3.6
import collections
import secrets
import itertools

class subspace(object):

    def __init__(self):
        self.tuples = dict()
        self.ready  = set()
        self.old_tuples  = set()
        self.new_tuples  = set()
        self.old_readers = set()
        self.new_readers = set()
        self.old_takers  = set()
        self.new_takers  = set()
        self.strategy = itertools.cycle([
            self._new_readers,
            self._new_takers,
            ...
        ])

    def add_tuple(self, tup):
        tid = secrets.randbits(160)
        self.tuples[tid] = tup
        self.new_tuples.add(tid)
        return tid

    def add_reader(self, coro, pattern):
        self.new_readers.add((coro, pattern))

    def add_taker(self, coro, pattern):
        self.new_takers.add((coro, pattern))

    def

class blackboard(object):

    def __init__(self):
        self.spaces = collections.defaultdict(subspace)

################################################################################
# Examples
################################################################################

if __name__ == '__main__':
    import black
    b = black.blackboard()

    async def time_server():
        t = 0
        while True:
            await b.emit('time', t)
            await b.sleep(1.0)
            await b.take('time', t)
            t += 1

    async def trigger(message, delay):
        t = await b.read('time', int)
        await b.read('time', t[-1] + delay)
        print(message)


    ts.spawn(time_server())
    ts.spawn(trigger('hello', 2))
    ts.spawn(trigger('world', 3))
    ts.run()
