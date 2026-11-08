"""Append exact same-reader-domain correction without rewriting reviewed history."""
import bootstrap
from bootstrap import R, S, E, checked
import hashlib, json, os

def bind(path):
    raw=checked(path)
    return {'kind':'evidence','root_id':'repository','relative_path':str(path.relative_to(R)),
            'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}

previous=json.loads(checked(E/'reader-checkpoint-0002.json',
    '9e39dc1a07d5d4f0e5908f56bd8452561625ef9e803fae4ade6e737674a33007'))
for row in previous['source_bindings']:
    raw=checked(E/'source-revision-0002'/row['relative_path'],row['sha256'])
    if len(raw)!=row['size_bytes']:raise ValueError('reviewed preservation size')
for row in previous['original_contract_bindings']+previous['accepted_import_bindings']:
    checked(R/row['relative_path'],row['sha256'])
checked(E/'reviewer-findings-0001.json','6520388121714d20177856d84a342214cac6092e8c4cf63de194d5ae527af940')
results=[]
for stem,flags in [('reader-tests-normal-0004',[]),('reader-tests-optimized-0003',['-O'])]:
    result=json.loads(checked(E/(stem+'.stdout')))
    if result != {'schema_version':'lab-case-command-result/v1','result':'PASS','checks':36,
                  'effect_state':'owned-inert','cleanup':'clean'}:raise ValueError('tests incomplete')
    results.append({'stdout':bind(E/(stem+'.stdout')),'stderr':bind(E/(stem+'.stderr')),
        'terminal':result,'argv':['/usr/bin/python3.14','-B','-S',*flags,
        str(S/'tests/LC-U05-01/test_reader.py'),'--temp-root',str(E)],
        'environment':{'PATH':'/usr/bin:/bin','PYTHONPYCACHEPREFIX':str(bootstrap.PREFIX)}})
paths=[R/row['relative_path'] for row in previous['source_bindings']]
paths.append(S/'tests/LC-U05-01/freeze_reader_checkpoint_v3.py')
value={**previous,'checkpoint':'reader-before-semantic-consumption-0003',
       'source_bindings':[bind(p) for p in paths],'test_results':results,
       'supersedes':bind(E/'reader-checkpoint-0002.json'),
       'preservation':bind(E/'source-revision-0002/preservation.json'),
       'prior_correction':previous['correction'],
       'correction':{'id':'U0501-D01','finding':bind(E/'reviewer-findings-0001.json'),
         'resolution':'Permission and RoleReader require the identical independently selected AnchoredReader/provider/root enrollment before constructor reads and at each boundary guard. Aliased root IDs and equal digests cannot transfer a permission.',
         'causal_cases':2,'retained_case_count':34,
         'original_task_acceptance_changed':False}}
raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
target=E/'reader-checkpoint-0003.json'
with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(E,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}))
