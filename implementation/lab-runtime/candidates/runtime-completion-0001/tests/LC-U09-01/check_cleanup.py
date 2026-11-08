"""Read-only check; never delete unowned residue."""
import json,sys
from pathlib import Path
R=Path(__file__).absolute().parents[6]
U=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U09-01'
residue=list(U.glob('owned-owner-*'))
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'FAIL' if residue else 'PASS','checks':1,'effect_state':'none','cleanup':'retained-owned' if residue else 'clean'}))
sys.exit(1 if residue else 0)
