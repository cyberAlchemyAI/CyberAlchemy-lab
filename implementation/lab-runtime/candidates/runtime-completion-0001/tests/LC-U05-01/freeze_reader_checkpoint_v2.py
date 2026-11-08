"""Append a corrected reader checkpoint, retaining the original exact postimage."""
import bootstrap
from bootstrap import R, S, E, OLD, IMPORT_BINDINGS, checked
import hashlib, json, os

def bind(path):
    raw=checked(path)
    return {'kind':'evidence','root_id':'repository','relative_path':str(path.relative_to(R)),
            'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}

previous=json.loads(checked(E/'reader-checkpoint-0001.json',
    '91c744375ee104ced2431b5eb6fb95b631a7aab4ece6a6f3cd24eab100997c39'))
for row in previous['source_bindings']:
    raw=checked(E/'source-revision-0001'/row['relative_path'],row['sha256'])
    if len(raw)!=row['size_bytes']:raise ValueError('original preservation size')
source_paths=[S/'dependency_graph'/n for n in ('__init__.py','reader.py','READER-CONTRACT.md')]
source_paths += [S/'tests/LC-U05-01'/n for n in ('bootstrap.py','test_reader.py',
                 'freeze_reader_checkpoint.py','freeze_reader_checkpoint_v2.py')]
for row in previous['original_contract_bindings']+previous['accepted_import_bindings']:
    checked(R/row['relative_path'],row['sha256'])
results=[]
for stem,flags in [('reader-tests-normal-0003',[]),('reader-tests-optimized-0002',['-O'])]:
    result=json.loads(checked(E/(stem+'.stdout')))
    if result != {'schema_version':'lab-case-command-result/v1','result':'PASS','checks':34,
                  'effect_state':'owned-inert','cleanup':'clean'}:
        raise ValueError('checkpoint tests not complete')
    results.append({'stdout':bind(E/(stem+'.stdout')),'stderr':bind(E/(stem+'.stderr')),
        'terminal':result,'argv':['/usr/bin/python3.14','-B','-S',*flags,
        str(S/'tests/LC-U05-01/test_reader.py'),'--temp-root',str(E)],
        'environment':{'PATH':'/usr/bin:/bin','PYTHONPYCACHEPREFIX':str(bootstrap.PREFIX)}})
value={**previous,'checkpoint':'reader-before-semantic-consumption-0002',
       'source_bindings':[bind(p) for p in source_paths], 'test_results':results,
       'supersedes':bind(E/'reader-checkpoint-0001.json'),
       'preservation':bind(E/'source-revision-0001/preservation.json'),
       'correction':{'id':'U0501-S01','source':'independent supplemental source challenge by evidence_review',
         'defect':'Ordinary provider and OS/parser exceptions could expose private text and locators through public adapter errors.',
         'resolution':'Fresh bounded Refusal at public constructor, permission, read, inventory and generator enter/exit boundaries; no arbitrary exception rendering; suppressed chained private frames.',
         'causal_cases':8,'complete_original_case_count':26,
         'ceiling':'Ordinary rendered public errors only; no hostile-code or Python exception-introspection isolation claim.'}}
raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
target=E/'reader-checkpoint-0002.json'
with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(E,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}))
