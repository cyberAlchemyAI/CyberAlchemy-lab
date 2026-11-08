import bootstrap
from bootstrap import E
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
if a.temp_root!=E:raise ValueError('owned root')
remaining=[p for p in E.iterdir() if p.name.startswith(('owned-installer-','owned-cold-'))]
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'FAIL' if remaining else 'PASS','checks':1,
    'effect_state':'owned-inert','cleanup':'retained-owned' if remaining else 'clean'}))
raise SystemExit(1 if remaining else 0)
