"""Check only this unit's named scratch prefixes; never remove foreign files."""
import json
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
S = ROOT / 'implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U01-02'
E = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02'
left = sum(1 for base in (S,E) for p in base.glob('owned-test-*'))
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if left==0 else 'FAIL',
                  'checks':2,'effect_state':'none','cleanup':'clean' if left==0 else 'unknown'}))
raise SystemExit(0 if left==0 else 1)
