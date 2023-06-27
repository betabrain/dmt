import re
import sys


class Forth:
    def __init__(self):
        self._tib = []
        self._tib_consumed = 0
        self._ps = []
        self._ds = []
        self._env = {}
        self.define("defn", self._defn)
        self.define("dup", self._lambda(1, lambda a: (a, a)))
        self.define("drop", self._lambda(1, lambda a: tuple()))
        self.define("swap", self._lambda(2, lambda a, b: (b, a)))
        self.define("+", self._lambda(2, lambda a, b: (a + b,)))
        self.define("-", self._lambda(2, lambda a, b: (a - b,)))
        self.define("*", self._lambda(2, lambda a, b: (a * b,)))
        self.define("/", self._lambda(2, lambda a, b: (a / b,)))
        self.define("+1", self._lambda(1, lambda a: (a + 1,)))
        self.define("-1", self._lambda(1, lambda a: (a - 1,)))
        self.define("negate", self._lambda(1, lambda a: (-a,)))
        self.define("if", self._if)

    def define(self, name, func):
        self._env[name] = func

    def _defn(self):
        name = self._ps.pop(0)
        assert name is not None
        assert name[0] == 'symbol'
        body = self._ps.pop(0)
        assert body is not None
        assert body[0] == 'block'

        def _caller():
            self._ps = body[1] + self._ps

        self._env[name[1]] = _caller

    def _if(self):
        truthy = self._ps.pop(0)
        assert truthy[0] == 'block'
        falsy = self._ps.pop(0)
        assert falsy[0] == 'block'
        if self._ds.pop() != 0:
            self._ps = truthy[1] + self._ps
        else:
            self._ps = falsy[1] + self._ps

    def _lambda(self, n, fn):
        def method():
            args = reversed(list(self._ds.pop() for _ in range(n)))
            self._ds.extend(fn(*args))

        return method

    def push_input(self, line):
        self._tib.extend(re.findall("\\S+", line))
        while self._tib:
            token = self._parse_token()
            if token:
                self._tib = self._tib[self._tib_consumed:]
                self._tib_consumed = 0
                if token == ('symbol', '!'):
                    self._evaluate()
                else:
                    self._ps.append(token)
            else:
                self._tib_consumed = 0
                break

    def _current_token(self):
        assert self._tib
        return self._tib[self._tib_consumed]

    def _next_token(self):
        t = self._current_token()
        self._tib_consumed += 1
        return t

    def _parse_token(self):
        if self._tib_consumed < len(self._tib):
            t = self._next_token()
            if re.match("\\d+", t):
                return ('number', int(t))
            elif t == '[':
                block = []
                while self._tib_consumed < len(self._tib) and self._current_token() != "]":
                    block.append(self._parse_token())
                if self._tib_consumed < len(self._tib) and self._current_token() == "]":
                    self._next_token()  # drop ]
                    return ('block', block)
                else:
                    return None
            else:
                return ('symbol', t)
        else:
            return None

    def _evaluate(self):
        while self._ps:
            t = self._ps.pop(0)
            if t[0] == 'number':
                self._ds.append(t[1])
            elif t[0] == 'symbol':
                if t[1] in self._env:
                    self._env[t[1]]()
                else:
                    print(f"unknown: {t[1]}")
                    return
            else:
                print(f"error: {t}")
                return


if __name__ == '__main__':
    f = Forth()

    while True:
        print(f"env: {' '.join(f._env.keys())}")
        print(f"ds: {f._ds}")
        print(f"ps: {f._ps}")
        print(f"tib: {f._tib_consumed} {f._tib}")
        print(f"{f._ds}> ", end="")
        line = sys.stdin.readline().strip()
        if line == "quit":
            break
        elif line:
            f.push_input(line)

    print(f._tib)
    print(f._ps)
