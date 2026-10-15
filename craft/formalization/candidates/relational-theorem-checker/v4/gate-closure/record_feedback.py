"""Capture only a response the operator has actually observed in this chat."""
import argparse
import json
from closure_api import Ledger

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='Actual source-bound human response JSON')
    parser.add_argument('--observed-direct-response',action='store_true',required=True)
    args=parser.parse_args()
    from pathlib import Path
    ref=Ledger().record_feedback(Path(args.input).read_bytes(),observed_direct_response=args.observed_direct_response)
    print(json.dumps({'recorded_feedback':ref,'authority_effect':'none'},indent=2))
