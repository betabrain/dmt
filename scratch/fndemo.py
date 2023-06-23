#!/usr/bin/python3.6
from fn import _


def line():
    print("-" * 76)


fn_abs = (_ ** 2) ** 0.5

print(fn_abs)
print(fn_abs, fn_abs(3))
print(fn_abs, fn_abs(-3))
line()

from fn.op import zipwith

f = zipwith(lambda a, b, c: a ** b ** c)
tmp = f(range(10), range(15), range(3))
print(zipwith, f, tmp)
print(list(tmp))
line()

from fn.immutable import SkewHeap, Stack, Queue, Deque

for cls in [SkewHeap, Stack, Queue, Deque]:
    print(cls)
    for name in sorted(dir(cls)):
        print("", name)
    line()
    print()

sh = SkewHeap()
print(sh, list(sh))

st = Stack()
print(st, list(st))

qu = Queue()
print(qu, list(qu))

de = Deque()
print(de, list(de))
line()

sh1 = sh.insert(73)
print(sh, list(sh))
print(sh1, list(sh1))
line()

st1 = st.push(33)
print(st, list(st))
print(st1, list(st1))
line()

qu1 = qu.enqueue(22)
x, qu2 = qu1.dequeue()
print(qu, list(qu))
print(qu1, list(qu1))
print(qu2, list(qu2))
print(x)
line()

from fn import Stream

s = Stream() << [1, 2, 3, 4, 5]
print(s)
print(list(s))
s << [77, 88, 99]
print(s)
print(list(s))
line()


def gen():
    for a in range(3):
        for b in range(3):
            yield (a ** b) ** 2


s << gen << ("the end",)
print(s)
print(list(s))

from fn.iters import take, drop, map
from operator import add

f = Stream()
fib = f << [0, 1] << map(add, f, drop(1, f))

print(f)
print(fib)

print(list(take(5, fib)))
print(list(take(10, fib)))
print(list(take(15, fib)))
print(list(take(20, fib)))
line()


def sum_up(s):
    t = 0
    for v in s:
        t += v
        yield t


x = Stream()
tot = x << [1] << sum_up(x)

print(list(take(5, tot)))
print(list(take(10, tot)))
print(list(take(15, tot)))
print(list(take(20, tot)))
line()

from fn.recur import tco


@tco
def even(n):
    if n == 0:
        return False, True

    return odd, (n - 1,)


@tco
def odd(n):
    if n == 0:
        return False, False

    return even, (n - 1,)


print(even)
print(odd)
print(5, even, even(5))
print(7, odd, odd(7))
line()

import dis

line()

from fn.func import curried


@curried
def abc(a, b, c):
    return a + b + c


print(abc)
a = abc(1)
print(a)
b = a(2)
print(b)
c = b(3)
print(c)
line()

from fn import F

sum_evens = F() >> (filter, _ % 2 == 0) >> sum
print(sum_evens)

print(sum_evens([1, 2, 3, 4]))
line()
