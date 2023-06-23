import attr
import kt2


@attr.s
class bigsum(kt2.cqrs):
    s = attr.ib(init=False, default=0)


bs = bigsum()
print(bs.s)

bs.add(55)
print(bs.s)
