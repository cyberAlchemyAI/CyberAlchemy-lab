#!/usr/bin/env python3
"""Run the selected member-18 consumer with isolated module state."""
import hashlib
import json
from pathlib import Path
import stat
import sys


def checked_source(path, expected):
    path = path.absolute()
    for item in (path, *path.parents):
        mode = item.lstat().st_mode
        if stat.S_ISLNK(mode) or (item == path and not stat.S_ISREG(mode)):
            raise ValueError("linked or nonregular consumer origin")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError("consumer source changed")


def main():
    root = Path(sys.argv[1]).resolve(strict=True)
    expected = sys.argv[2]
    dependency_expected = sys.argv[3]
    directory = root / "implementation/lab-runtime/local-host/t10-control-consumer-0001"
    source = directory / "consume_18.py"
    dependency = directory / "consume.py"
    checked_source(source, expected)
    checked_source(dependency, dependency_expected)
    sys.path.insert(0, str(directory))
    import consume_18
    if Path(consume_18.__file__).resolve(strict=True) != source:
        raise ValueError("member-18 consumer origin differs")
    result = consume_18.consume()
    checked_source(source, expected)
    checked_source(dependency, dependency_expected)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
