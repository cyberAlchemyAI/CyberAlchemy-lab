"""Freeze the complete technical T08 successor; no self-issued acceptance."""
import bootstrap
from bootstrap import R,S,E,checked
import hashlib,json,os

def bind(path):
    raw=checked(path)
    return {'kind':'evidence','root_id':'repository','relative_path':str(path.relative_to(R)),
            'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}

def verify(row):
    raw=checked(R/row['relative_path'],row['sha256'])
    if len(raw)!=row['size_bytes']:raise ValueError('selected size')

reader=json.loads(checked(E/'reader-checkpoint-0003.json',
    'ee440fc6d34f98c3bd30cd524955b69c3b69e61cdc227ad9fda9fda4cc41e2f4'))
review=checked(E/'reviewer-reader-checkpoint-0003-review.json',
    '094c511bb4e23cfea5a004785394e84e254fa26281abe32c903757138486a584')
for row in reader['source_bindings']+reader['accepted_import_bindings']+reader['original_contract_bindings']:verify(row)
paths=[R/b['relative_path'] for b in reader['source_bindings']]
paths += [S/'dependency_graph'/n for n in ('semantic.py','semantic-policy.schema.json','SEMANTIC-CONTRACT.md','SEMANTIC-REFUSALS.md')]
paths += [S/'environment'/n for n in ('__init__.py','body_json.py')]
paths += [S/'tests/LC-U05-01'/n for n in ('semantic_fixture.py','test_semantic.py','test_full_inventory.py','freeze_semantic_checkpoint.py')]
results=[]
for stem,count,flags in [('semantic-tests-normal-0004',40,[]),('semantic-tests-optimized-0001',40,['-O']),
                         ('full-inventory-normal-0001',8,[])]:
    terminal=json.loads(checked(E/(stem+'.stdout')))
    if terminal!={'schema_version':'lab-case-command-result/v1','result':'PASS','checks':count,
                  'effect_state':'owned-inert','cleanup':'clean'}:raise ValueError('incomplete checkpoint test')
    results.append({'stdout':bind(E/(stem+'.stdout')),'stderr':bind(E/(stem+'.stderr')),
        'terminal':terminal,'observed_outer_exit_code':0,'python_flags':['-B','-S',*flags],
        'source_selection':'this frozen technical successor; author runs do not self-endorse dispatch',
        'environment':{'PATH':'/usr/bin:/bin','PYTHONPYCACHEPREFIX':str(bootstrap.PREFIX)}})
observations=[];originals={}
for name in ('semantic-observation-normal-0001.json','semantic-observation-optimized-0001.json'):
    value=json.loads(checked(E/name));observations.append(bind(E/name))
    if (value['tests_run'],value['errors'],value['failures'],value['actual_protected_reads'])!=(40,0,0,0):raise ValueError('semantic observation')
    for row in value['original_read_bindings']:
        key=row['root_id'],row['relative_path']
        if key in originals and originals[key]!=row:raise ValueError('conflicting original input')
        originals[key]=row
    selection=value['original_selection'];checked(R/selection['relative_path'],selection['sha256'])
    originals[('repository',selection['relative_path'])]=bind(R/selection['relative_path'])
inventory=json.loads(checked(E/'full-inventory-observation-0001.json'))
for row in [inventory['policy_binding'],*inventory['input_bindings']]:
    key=row['root_id'],row['relative_path']
    if key in originals and originals[key]!=row:raise ValueError('conflicting public input')
    originals[key]=row
for row in originals.values():verify(row)
value={'schema_version':'lab-t08-adapter-technical-checkpoint/v1','unit':'LC-U05-01',
    'checkpoint':'complete-reader-and-semantic-adapter-0001','status':'awaiting-independent-review',
    'accepted_reader_checkpoint':bind(E/'reader-checkpoint-0003.json'),
    'independent_reader_review':bind(E/'reviewer-reader-checkpoint-0003-review.json'),
    'source_bindings':[bind(p) for p in paths],
    'original_contract_bindings':reader['original_contract_bindings'],
    'accepted_import_bindings':reader['accepted_import_bindings'],
    'original_selected_inputs':list(originals.values()),'test_results':results,
    'semantic_observations':observations,'full_inventory_observation':bind(E/'full-inventory-observation-0001.json'),
    'retained_counterevidence':[bind(E/(stem+suffix)) for stem in ('semantic-tests-normal-0001','semantic-tests-normal-0002','semantic-tests-normal-0003') for suffix in ('.stdout','.stderr')],
    'counterevidence_resolution':'Author run0002 exposed loss of semantic reason codes across the reader boundary and one stale diagnostic assertion. Semantic failure is now held until the reader post-check completes, then mapped through a finite literal catalogue. Final40 normal and optimized checks pass.',
    'metadata_tables':22,'metadata_occurrences':241598,'protected_original_bodies_read':0,
    'authority_effect':'none','actual_host_custody':False,'original_task_acceptance_changed':False,
    'T09_semantic_consumption_started':False,
    'remaining_original_obligations':['actual selected protected provider/custody and current body eligibility',
        'actual original proof member validation under current authority','original T08/T09 acceptance'],
    'remaining_unit_work':['CompositeEnvironment and exact execution origin adapter',
        'final selected command dispatch','independent whole-unit review']}
raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
target=E/'semantic-checkpoint-0001.json'
with target.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
fd=os.open(E,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),
                  'sources':len(paths),'original_selected_inputs':len(originals)}))
