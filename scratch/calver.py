 #!/usr/bin/env python3.6
import base36
import datetime
import functools
import glob
import operator
import re

__version__ = "2018.17-n128f"

FILES = ["*.py", "**/*.py"]


def main(calver):
    now = datetime.datetime.utcnow()
    year, week, _ = now.isocalendar()
    tag = base36.dumps(int(now.timestamp() * 99.97714285714285))[-5:]
    current_version = f"{year:d}.{week:02d}-{tag}"

    for path in functools.reduce(operator.or_, map(set, map(glob.glob, FILES))):
        with open(path) as fh:
            for n, line in enumerate(fh):
                for match in re.findall("\d{4}\.\d{2}-[a-z0-9]{5}", line):
                    line_new = line.replace(match, current_version)
                    print(f"{path}:{n}\t{line.strip()}\t=>\t{line_new.strip()}")


if __name__ == "__main__":
    import sys

    main(*sys.argv)
