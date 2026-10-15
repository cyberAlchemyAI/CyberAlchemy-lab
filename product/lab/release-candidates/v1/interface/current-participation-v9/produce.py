"""Start the frozen producer once in its explicit package namespace."""
import argparse
import importlib.util
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    args=parser.parse_args();name='_cal_current_participation_producer_0008'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    builder=__import__(name+'.build',fromlist=['main'])
    builder.main(args.source_sha256)
if __name__=='__main__':main()
