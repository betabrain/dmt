#!/usr/bin/python3.6
""" Flow.Py
"""
import attr
import collections
import glob
import os

################################################################################
# Flow Core
################################################################################


@attr.s(slots=True)
class Task:
    _func = attr.ib()
    _inputs = attr.ib()
    _result = attr.ib(init=False, default=None)

    def _input_tuples(self):
        return zip(*[x.value() if isinstance(x, Task) else x for x in self._inputs])

    def value(self):
        if self._result is None:
            print(f"flow: {self._func.__name__} on {[id(i) for i in self._inputs]}")
            self._result = list(self.do())
        return self._result

    def do(self):
        return self()


def _flatten(it):
    for x in it:
        if isinstance(x, collections.Iterable) and not isinstance(x, str):
            yield from _flatten(x)

        else:
            yield x


class MapTask(Task):

    def __init__(self, func, inputs):
        Task.__init__(self, func, inputs)

    def __call__(self):
        yield from _flatten(self._func(*tup) for tup in self._input_tuples())


def map(*inputs):

    def _map_decorator(func):
        return MapTask(func, inputs)

    return _map_decorator


class ReduceTask(Task):

    def __init__(self, func, inputs):
        Task.__init__(self, func, inputs)

    def __call__(self):
        yield from self._func(self._input_tuples())


def reduce(*inputs):

    def _reduce_decorator(func):
        return ReduceTask(func, inputs)

    return _reduce_decorator


################################################################################
# Utility Functions
################################################################################


def find(pattern):
    root = os.getcwd()
    for result in glob.iglob(pattern):
        yield os.path.abspath(os.path.join(root, result))


################################################################################
# Main / Tests
################################################################################

if __name__ == "__main__":
    import flow
    import csv

    @flow.map(flow.find("../**/*.csv"))
    def read_file(path):
        with open(path, errors="ignore") as fh:
            yield from fh.read().split("\n")

    @flow.map(read_file)
    def row_len(row):
        yield len(row)

    @flow.reduce(read_file)
    def count_rows(rs):
        yield len(list(rs)) or 1

    @flow.reduce(row_len)
    def sum_row_lens(xs):
        s = 0
        for (x,) in xs:
            s += x
        yield s

    @flow.map(sum_row_lens, count_rows)
    def avg_fields_per_row(srl, cr):
        yield srl / cr

    # print('sum of all row lengths in csv files:', sum_row_lens.value())
    # print('count of rows:', count_rows.value())
    # print('avg. fields/row:', avg_fields_per_row.value())

    @flow.reduce(read_file)
    def calc_stats(rows):
        rc = 0
        rs = 0
        for row in rows:
            rc += 1
            rs += len(row)
        yield rs / rc

    @flow.map(read_file)
    def count_as(row):
        yield row.count("a") + row.count("A")

    @flow.map(read_file)
    def count_bs(row):
        yield row.count("b") + row.count("B")

    @flow.reduce(count_as, count_bs)
    def a_to_b(xs):
        a = 0
        b = 0
        for (xa, xb) in xs:
            a += xa
            b += xb
        yield a / b

    print("faster:", calc_stats.value())
    print("xxxxxx:", a_to_b.value())
