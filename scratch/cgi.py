#!/usr/bin/python3.6


def page(CLIENT_PORT=None, **kwargs):
    headers = {}
    content = []

    for i in range(int(CLIENT_PORT)):
        content.append(f"not yet...{i}")

    print("\n".join(map(lambda k, v: f"{k}: {v}", headers.items())))
    print()
    print()
    print("\n".join(content))


if __name__ == "__name__":
    import os

    page(**os.environ)
