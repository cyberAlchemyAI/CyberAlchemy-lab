import hashlib,json,sys,stat
from pathlib import Path
R=Path(__file__).absolute().parents[6]
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U03-02'
T=Path(__file__).absolute().parent
P=E/'failed-fixture-retention-0003.json'
raw=P.read_bytes()
if hashlib.sha256(raw).hexdigest()!='f4a2414f40da3fe6de4d10fa6611b6297e7e415a3267c680f8437eae25bd0c63':raise ValueError('retention selection')
v=json.loads(raw);expected={r['path']:r for r in v['entries']}
found={}
for work in E.glob('offline-build-*'):
 for root in (work/'tmp').glob('supervisor-fixture-*'):
  for p in [root,*sorted(root.rglob('*'))]:
   mode=p.lstat().st_mode
   if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):raise ValueError('unselected residue type')
   rel=str(p.relative_to(E));found[rel]={'path':rel,'type':'directory' if p.is_dir() else 'file','sha256':None if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest()}
if found!=expected:raise ValueError('new or changed owned fixture residue')
if list(E.glob('owned-input-negative-*')) or list(T.rglob('*.pyc')) or list(T.rglob('__pycache__')):raise ValueError('unexpected input fixture/cache residue')
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':2,'effect_state':'owned-inert','cleanup':'retained-owned'}))
