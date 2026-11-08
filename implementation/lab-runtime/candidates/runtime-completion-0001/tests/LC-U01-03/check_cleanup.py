"""Read-only owned fixture residue check; never delete unknown state."""
import json
from pathlib import Path
import sys
R=Path(__file__).absolute().parents[6]
U=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-03'
residue=list(U.glob('owned-index-*'))
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'FAIL' if residue else 'PASS',
    'checks':1,'effect_state':'none','cleanup':'retained-owned' if residue else 'clean'}))
sys.exit(1 if residue else 0)
