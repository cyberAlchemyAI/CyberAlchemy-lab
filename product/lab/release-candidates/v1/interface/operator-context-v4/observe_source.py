"""One actual cold signed reader process, metadata only, with no Agent creation."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from source_adapter import open_signed


def main(source_name, pin):
    with open_signed(source_name, pin) as adapter:
        value = adapter.closure_report()
    print(json.dumps(value, indent=2, sort_keys=True), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--source', required=True)
    p.add_argument('--package-sha256', required=True);a = p.parse_args();main(a.source, a.package_sha256)
