"""Validate all gate evidence and render/recover the current original task view."""
import argparse
import json
from closure_api import Ledger

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recover',action='store_true',help='Repair the derived view from the checked immutable log')
    args=parser.parse_args()
    ledger=Ledger();view=ledger.recover() if args.recover else ledger.resolve()
    print(json.dumps({k:v for k,v in view.items() if k!='tasks'},indent=2))
