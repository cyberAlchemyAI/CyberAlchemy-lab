"""Verify all frozen helper inputs before importing the actual source fixture."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args();source = HERE / 'source-manifest.json'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == args.source_sha256
    for row in json.loads(source.read_bytes())['files']:
        path = ROOT / row['path']
        assert path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
    name = '_cal_fact_read_scope_v1_checks'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    module = importlib.util.module_from_spec(spec);sys.modules[name] = module;spec.loader.exec_module(module)
    checks = __import__(name + '.checks', fromlist=['main'])
    checks.main()


if __name__ == '__main__':
    main()
