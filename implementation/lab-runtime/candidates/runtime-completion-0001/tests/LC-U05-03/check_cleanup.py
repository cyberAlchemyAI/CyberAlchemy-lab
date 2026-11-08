import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);a=p.parse_args()
residue=list(a.temp_root.glob('owned-startup-*'))+list(a.temp_root.glob('owned-endpoint-*'))
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'FAIL'if residue else'PASS','checks':1,
                  'effect_state':'owned-inert','cleanup':'retained-owned'if residue else'clean'}))
raise SystemExit(1 if residue else 0)
