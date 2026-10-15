"""Accept original G4 after R06 and actual bounded-use recommendation."""
import argparse
import json
from pathlib import Path
from closure_api import Ledger,decode

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('feedback_reference',help='JSON file containing recorded feedback path/hash')
    parser.add_argument('--expected-head',required=True,help='Exact current entry reference JSON')
    args=parser.parse_args()
    result=Ledger().accept('G4',decode(Path(args.feedback_reference).read_bytes()),expected_head=decode(args.expected_head.encode()))
    Ledger().recover()
    print(json.dumps(result,indent=2))
