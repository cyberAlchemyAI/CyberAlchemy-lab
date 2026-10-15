"""Retain v3 failure; add exact original-v2 read-only historical interpretation."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'custody-correction-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edit(p,a,b):
    s=p.read_text();assert a in s,(p,a);p.write_text(s.replace(a,b))
assert not (HERE/'runtime').exists()
shutil.copytree(OLD/'runtime',HERE/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
for p in OLD.glob('*.py'):
    if p.name not in ['derive.py','freeze.py']:shutil.copyfile(p,HERE/p.name)
shutil.copyfile(OLD/'freeze.py',HERE/'freeze.py');shutil.copyfile(OLD/'CONTRACT.md',HERE/'CONTRACT.md')
p=HERE/'runtime/profile.json';p.write_text(p.read_text().replace('custody-correction-v3/','custody-correction-v4/'))
edit(HERE/'runtime/lab_runtime/cli.py','custody-correction-v3/store','custody-correction-v4/store')
original=ROOT/'implementation/lab-runtime/v2';legacy=HERE/'runtime/lab_runtime/historical_v2'
legacy.mkdir();(legacy/'__init__.py').write_text('"""Exact immutable original-v2 historical reader namespace."""\n')
for name in ['lab_runtime','schemas']:shutil.copytree(original/name,legacy/name,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(original/'profile.json',legacy/'profile.json')
files=[]
for p in sorted(legacy.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts:
        q=original/p.relative_to(legacy)
        files.append({'path':p.relative_to(legacy).as_posix(),'sha256':sha(p),
            'original_binding':{'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q)} if q.exists() else None})
m={'schema_version':'lab-historical-v2-code/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
    'profile_sha256':sha(original/'profile.json'),'files':files,'effect_scope':'read-only original transaction replay; never successor writes'}
p=HERE/'runtime/lab_runtime/historical-v2-manifest.json';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
historical=HERE/'runtime/lab_runtime/historical.py'
shutil.copyfile(HERE/'historical-template.py',historical)
edit(historical,'MANIFEST_PIN_TO_AUTHOR',sha(p))
p=HERE/'runtime/profile.json';profile=json.loads(p.read_bytes())
profile['runtime_materials'] += [q.relative_to(ROOT).as_posix() for q in sorted((HERE/'runtime/lab_runtime').rglob('*'))
    if q.is_file() and '__pycache__' not in q.parts and (q.is_relative_to(legacy) or q.name in ['historical.py','historical-v2-manifest.json'])]
p.write_text(json.dumps(profile,indent=2,sort_keys=True)+'\n')
edit(HERE/'runtime/lab_runtime/store.py','config, baseline, head = self.roots()\n        fresh = freshness',
    "config, baseline, head = self.roots()\n        from .historical import recognizes, replay_original\n        if recognizes(config, baseline):\n            data=replay_original(self.path,self.repo)\n            data['freshness']['status']='stale'\n            data['freshness']['changed']=sorted(set(data['freshness']['changed']) | {'runtime-source-profile-successor-required','endpoint-mapping-profile-required'})\n            if require_current:require(False,'stale repository sources: runtime-source-profile-successor-required')\n            return data\n        fresh = freshness")
edit(HERE/'freeze.py',"for p in [failed/'source-manifest.json'", "previous=HERE.parent/'custody-correction-v3'\n    for row in json.loads((previous/'source-manifest.json').read_bytes())['files']:inputs[row['path']]=row\n    for p in [previous/'source-manifest.json',*sorted((previous/'receipts/0001').rglob('*')),\n        *previous.glob('*-000*.log'),RUN/'context-R03-custody-correction-0005.json',RUN/'custody-correction-terminal-v3-0001.json',failed/'source-manifest.json'")
# The predecessor receipt folder includes directories; source bindings include files only.
edit(HERE/'freeze.py',"inputs[bind(p)['path']]=bind(p)\n    for p in sorted(HERE.rglob('*')):",
    "if p.is_file():inputs[bind(p)['path']]=bind(p)\n    for p in sorted(HERE.rglob('*')):")
(HERE/'regression-sources').mkdir()
print(json.dumps({'authored':str(HERE),'historical_files':len(files),'historical_profile_sha256':m['profile_sha256'],'authority_effect':'none'}))
