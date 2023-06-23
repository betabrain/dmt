#!/usr/bin/python3.6
import re


def remap(pattern, d):
    r = {}
    for key, value in d.items():
        tmp = re.search(pattern, key)
        if tmp is not None:
            for group in tmp.groups():
                r[group] = value
    return r


def it2d(it, *patterns):
    d = {}
    for val in it:
        for pat in patterns:
            tmp = re.search(pat, val)
            if tmp is not None:
                d.update(tmp.groupdict())
                yield d


xs = [
    "Email: dagobert@example.com",
    "Subject: Just some email",
    "Email: dagobert@superman.com",
]
for i, d in enumerate(
    it2d(xs, "^Email:\s*(?P<email>.+)", "^Subject:\s*(?P<subject>\w.+)")
):
    print(i, d)
