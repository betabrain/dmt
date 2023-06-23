class Window:
    def __init__(self):
        self.queue = []

    def add(self, v):
        assert v is not None
        assert v not in self.queue
        self.queue.append(v)

    def remove(self, v):
        assert v is not None
        if v in self.queue:
            self.queue[self.queue.index(v)] = None
            while self.queue and self.queue[-1] is None:
                self.queue.pop()
            while self.queue and self.queue[0] is None:
                self.queue.pop(0)

    @property
    def window(self):
        bitfield = 0
        for i, v in enumerate(reversed(self.queue)):
            if v is not None:
                bitfield += 2**i
        return bitfield

    @property
    def min(self):
        if self.queue:
            return self.queue[0]

    @property
    def max(self):
        if self.queue:
            return self.queue[-1]


if __name__ == "__main__":
    w = Window()
    assert w.window == 0
    assert w.min is None
    assert w.max is None
    w.add("A")
    assert w.window == 1
    assert w.min == "A"
    assert w.max == "A"
    w.add("B")
    assert w.window == 3
    assert w.min == "A"
    assert w.max == "B"
    w.add("C")
    assert w.window == 7
    assert w.min == "A"
    assert w.max == "C"
    w.remove("A")
    assert w.window == 3
    assert w.min == "B"
    assert w.max == "C"
    w.add("X")
    w.remove("C")
    assert w.window == 5
    assert w.min == "B"
    assert w.max == "X"
