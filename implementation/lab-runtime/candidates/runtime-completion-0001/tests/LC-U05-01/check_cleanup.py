"""Observe only unit-owned fixture residue; never deletes it."""
import bootstrap
from bootstrap import E
import argparse,json
from pathlib import Path

PREFIXES=('owned-test-reader-','owned-graph-','owned-full-inventory-','owned-composite-','owned-small-origin-','owned-input-guard-')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    clean=not any(p.name.startswith(PREFIXES) for p in E.iterdir())
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if clean else 'FAIL','checks':1,
        'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if clean else 1)
