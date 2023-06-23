def fib(n):
    if n < 2:
        return n

    else:
        return fib(n - 1) + fib(n - 2)


def trampoline(f, *args, **kwargs):
    while f != None:
        f, args, kwargs = f(*args, **kwargs)
    return args[0]


def tco_fib(n, a=None, b=None):
    if a is None and b is None:
        return tco_fib, (n, 0, 1), {}

    else:
        if n == 0:
            return None, [a], {}

        else:
            return tco_fib, (n - 1, b, a + b), {}


trampoline(tco_fib, 3)


def run_stm(state_func, **state):
    while state_func != None:
        state_func, state = state_func(**state)


def init():
    return counting, dict(count=0)


def counting(count=0):
    count += 1

    if count < 10:
        return counting, dict(count=count)

    else:
        return printing, dict(count=count)


def printing(count=0):
    print(f"count is {count}")
    return None, None


run_stm(init)


def iter_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


if __name__ == "__main__":
    import time

    n = 100000

    try:
        t = -time.time()
        r1 = fib(n)
        t += time.time()
        print("no tco", t)
    except:
        print("no tco error")

    try:
        t = -time.time()
        r2 = trampoline(tco_fib, n)
        t += time.time()
        print("tco", t)
    except:
        print("tco error")

    try:
        t = -time.time()
        r3 = iter_fib(n)
        t += time.time()
        print("iter", t)
    except:
        print("iter error")
