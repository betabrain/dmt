#!/usr/bin/python3.6
from random import randint

N = 15

prev = [randint(1000, 1500) for _ in range(N)]
curr = [randint(1000, 1500) for _ in range(N)]
diff = [b - a for a, b in zip(prev, curr)]
adif = [abs(x) for x in diff]
tadi = sum(adif)
radi = [100.0 * x / tadi for x in diff]


for row in zip(prev, curr, diff, adif, radi):
    print(*row)

print(sum(radi))
print((100 * sum(diff) / sum(prev)))
