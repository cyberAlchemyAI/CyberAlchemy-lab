"""Create an append-only technical checkpoint; never endorse it for dispatch."""
import bootstrap
from bootstrap import R, S, E, OLD, IMPORT_BINDINGS, checked
import hashlib, json, os

def bind(path):
    raw=checked(path)
    return {'kind':'evidence','root_id':'repository','relative_path':str(path.relative_to(R)),
            'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}

source_paths=[S/'dependency_graph'/n for n in ('__init__.py','reader.py','READER-CONTRACT.md')]
source_paths += [S/'tests/LC-U05-01'/n for n in ('bootstrap.py','test_reader.py','freeze_reader_checkpoint.py')]
original=R/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'
original_paths=[original/n for n in ('binding-kinds.json','protected-selector.schema.json','protected_inputs.py','semantic_graph.py')]
original_paths += [R/'docs/plans/0011-lab-runtime-completion/work-pack/tasks'/n for n in ('T08.md','T09.md')]
results=[]
for stem in ('reader-tests-normal-0002','reader-tests-optimized-0001'):
    result=json.loads(checked(E/(stem+'.stdout')))
    if result != {'schema_version':'lab-case-command-result/v1','result':'PASS','checks':26,
                  'effect_state':'owned-inert','cleanup':'clean'}:
        raise ValueError('checkpoint tests not complete')
    results.append({'stdout':bind(E/(stem+'.stdout')),'stderr':bind(E/(stem+'.stderr')),'terminal':result})
value={'schema_version':'lab-reader-technical-checkpoint/v1','unit':'LC-U05-01',
       'checkpoint':'reader-before-semantic-consumption-0001',
       'status':'awaiting-independent-review','source_bindings':[bind(p) for p in source_paths],
       'original_contract_bindings':[bind(p) for p in original_paths],
       'accepted_import_bindings':IMPORT_BINDINGS,
       'predecessor_dispatch':bind(OLD/'coordinator-dispatch-0002.json'),
       'test_results':results,'authority_effect':'none','actual_protected_custody':False,
       'semantic_consumer_started':False,'original_task_acceptance_changed':False,
       'remaining':['complete native carrier/fragment/role semantic verifier',
                    'full original table/native closure integration',
                    'CompositeEnvironment and AC07 source mapping',
                    'final planned dispatch and independent whole-unit review']}
raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
target=E/'reader-checkpoint-0001.json'
with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(E,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}))
