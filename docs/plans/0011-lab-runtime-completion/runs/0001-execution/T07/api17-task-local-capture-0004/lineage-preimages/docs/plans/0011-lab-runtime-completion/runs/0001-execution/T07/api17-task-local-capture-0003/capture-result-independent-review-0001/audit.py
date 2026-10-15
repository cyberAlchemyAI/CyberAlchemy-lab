"""Independent metadata audit. No imports of Lab code or runtime constructors."""
import hashlib
import json
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
API=INTERFACE/'api-integration-v17'
OLD=INTERFACE/'api-integration-v16'
HERE=Path(__file__).parent
CAP=HERE.parent
reads={}
checks=[]
def digest(raw): return hashlib.sha256(raw).hexdigest()
def logical(path):
    p=Path(path)
    if p.is_absolute() and p.is_relative_to(ROOT): return str(p.relative_to(ROOT))
    return str(p)
def read(path,pin=None):
    p=Path(path);p=p if p.is_absolute() else ROOT/p
    raw=p.read_bytes(); h=digest(raw)
    assert pin is None or h==pin, str(p)
    assert not p.is_symlink() and not any(q.is_symlink() for q in p.parents),str(p)
    assert reads.setdefault(str(p),h)==h,'changed metadata during audit'
    return raw
def pairs(items):
    out={}
    for k,v in items:
        assert k not in out,'duplicate JSON key'
        out[k]=v
    return out
def load(path,pin=None): return json.loads(read(path,pin),object_pairs_hook=pairs)
def binding(path,pin): return {'path':logical(path),'sha256':pin}
def check(name,test):
    assert test,name
    checks.append({'name':name,'result':'PASS'})
def table(rows):
    result={}
    for row in rows:
        assert set(row)=={'path','sha256'}
        p=row['path'];assert Path(p).as_posix()==p and '..' not in Path(p).parts
        assert '\\' not in p and '\0' not in p
        assert len(row['sha256'])==64 and all(c in '0123456789abcdef' for c in row['sha256'])
        assert p not in result,'duplicate table path'
        result[p]=row
    return result

S='e41772f7478253fa2ede056afaa08461a962cc2e1063e541f5f2921f7ebe1195'
P='5c62fe3a14da4499e3a1b08be62b759b322b68e959cc4914e2e0225f94f4a714'
I='8cb8b5c768f1d3f584c468c0f44ae169cbe80ed274e397f5407dc59ef3d865da'
E='a8938ebe500c3e93f618dfffaeafd37b07e266ea60d9bcd5ec786e4eef72e93d'
OS='8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
OP='8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
U='4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'
SELECT='b182a70bf823e1e54cef016496e9acf7f573d32264653c0194c61e1bfe2fe661'
source=load(API/'source-manifest.json',S)
profile=load(API/'contract-profile.json',P)
inventory=load(API/'INPUT-ACCOUNTING.json',I)
schema=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',E)
original=load(OLD/'source-manifest.json',OS)
old_profile=load(OLD/'contract-profile.json',OP)
old_schema=load(OLD/'SCHEMA-EXECUTION-DEPENDENCIES.json')
absent=load(RUN/'T07/accounting-0001/unavailable-original-inputs.json',U)
selection=load(CAP/'component-selection.json',SELECT)
read(CAP/'capture.py','fe7cf43fbd239b88d5b524ff62c3729e96afb5d44cb2fac2c4ba41208e94e665')
result=load(CAP/'capture-result.json')
unavailable=table([row['binding'] for row in absent['rows']])
original_by=table(original['files']); old_profile_by=table(old_profile['files'])
retained=[row for row in original['files'] if row['path'] not in unavailable]
additions=table([row['binding'] for row in inventory['additions']])
current=table(source['files']); current_profile=table(profile['files'])
schema_by=table(schema['files'])
check('Full original row counts and common profile order',len(original_by)==24497 and len(old_profile_by)==24496 and [r for r in original['files'] if r['path'] in old_profile_by]==old_profile['files'])
check('Exact retained original prefix and sorted addition order',len(retained)==24472 and len(additions)==2928 and len(current)==27400 and source['files']==retained+[additions[p] for p in sorted(additions)])
check('Missing original rows retain original exact identities only',len(unavailable)==25 and all(original_by[p]==r for p,r in unavailable.items()) and not set(unavailable)&set(current))
check('Additions do not override any original identity',not set(additions)&set(original_by))
expected_consumption=[{'binding':r,'status':'historical-metadata-only' if r['path'] in unavailable else 'required-current-byte'} for r in original['files']+[additions[p] for p in sorted(additions)]]
check('Original accounting order and every fresh-row obligation',len(inventory['consumption'])==27425 and [{'binding':r['binding'],'status':r['status']} for r in inventory['consumption']]==expected_consumption and all(r['basis'] for r in inventory['consumption']))
check('Every addition classified with an explicit selection reason',all(r['classification'] in {'successor-code','successor-family','host-dependency'} and r['selection_reason'] for r in inventory['additions']))
check('Parent accounting independently binds original source/profile/unavailable',inventory['source_sha256']==OS and inventory['profile_sha256']==OP and inventory['unavailable_sha256']==U and source['parent_source_binding']==binding(OLD/'source-manifest.json',OS) and source['input_accounting']['source_binding']==binding(OLD/'source-manifest.json',OS) and source['input_accounting']['profile_binding']==binding(OLD/'contract-profile.json',OP) and source['input_accounting']['unavailable_binding']==binding(RUN/'T07/accounting-0001/unavailable-original-inputs.json',U))
check('Exact profile, schema, inventory cross bindings',source['profile_binding']==binding(API/'contract-profile.json',P) and source['input_accounting']['selection_binding']==binding(API/'INPUT-ACCOUNTING.json',I) and profile['schema_execution_dependency_binding']==binding(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',E) and current[logical(API/'contract-profile.json')]==source['profile_binding'] and current[logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]==profile['schema_execution_dependency_binding'])
check('Profile table equals current table excluding its own independently pinned body',len(current_profile)==27399 and profile['files']==[r for r in source['files'] if r['path']!=logical(API/'contract-profile.json')])
changed={'files','schema_execution_dependency_binding','historical_parent_source_binding','historical_parent_profile_binding','historical_original_physical_closure','claim_ceiling','external_execution_dependency_bindings','Machine_context_scope_method_binding'}
check('All other original profile metadata preserved literally', {k:v for k,v in profile.items() if k not in changed}=={k:v for k,v in old_profile.items() if k not in changed})
check('Original environment and callback/history refusal ceiling preserved',source['environment']==original['environment'] and source['original_signed_history_schema_callbacks_changed'] is False and source['historical_original_physical_closure']=='REFUSED' and profile['historical_original_physical_closure']=='REFUSED' and source['historical_missing_locators']==25 and all(source[k] is False for k in ['whole_API_qualified','current_Agent_qualified','task_complete','goal_complete']) and source['actual_owner_outcome'] is None and source['authority_effect']=='none')
expected_schema=table(old_schema['files'])
for p,r in current.items():
    if p.startswith(logical(API)+'/') and p not in {logical(API/'contract-profile.json'),logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')} or p in additions and p.endswith('.py'):
        expected_schema[p]=r
check('Full original schemas plus complete true-origin added Python/API eligibility',len(schema_by)==3418 and schema['files']==[expected_schema[p] for p in sorted(expected_schema)] and not set(schema_by)&set(unavailable) and all(current.get(p)==r for p,r in schema_by.items()) and set(schema['selection_reasons'])==set(schema_by))
check('Closed current code expectations and unchanged guard',len(selection['api_expected_files'])==160 and len(selection['helper_expected_files'])==7 and all(current.get(r['path'])==r for r in selection['api_expected_files']+selection['helper_expected_files']+[selection['guard_binding']]))
ledger=load(RUN/'T02/current-selector-staging-0002/patch-ledger.json','c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb')
postpins={'source_bridge.py':'b8d00e373339ce69eb26b7cdbc61d74dc8e8db89379aa5decb8f04fe07c0481e','current_context_sessions.py':'6b9238d608dad8437f24f556e9962dc73291b3396e878d7c939aee8f6428e1f9','authentication.schema.json':'1e70e46a2f5b08f9554bb572bb6f8905736a3251e5d356a812c608fe67997912','machine_auth_scope.py':'958ea8ef21684ae79be823cc606bf7284c44284eeb5dc243476fdb57abef5bf2'}
check('All four independently reviewed selector postimage pins captured',all(current[logical(API/name)]['sha256']==pin for name,pin in postpins.items()))
family_occurrences=0
family_names=[]
for fb in selection['current_family_selections']:
    f=load(fb['path'],fb['sha256']);assert current.get(fb['path'])==fb
    family_names.append(f['instance'])
    if 'bindings' in f:
        roles=[f['bindings'][k] for k in ['source','reader','mapper','context']]
    else: roles=[f[k] for k in ['source_binding','reader_binding','mapper_binding','context_source_binding']]
    for rb in roles:
        role=load(rb['path'],rb['sha256']); assert current.get(rb['path'])==rb
        family_occurrences+=len(role['files'])
        for row in role['files']: assert current.get(logical(row['path']))=={'path':logical(row['path']),'sha256':row['sha256']},row['path']
check('All three distinct family descriptors and 17698 complete role row occurrences',len(family_names)==len(set(family_names))==3 and family_occurrences==17698 and selection['current_family_selections'][2]['sha256']=='6004ecf7533954ee180f87186f46339b4e66a9c816252c40edf6ed2f98ea13bd')
component_occurrences=0;driver_count=0
for cb in selection['component_manifests']:
    comp=load(cb['path'],cb['sha256']); assert current.get(cb['path'])=={'path':cb['path'],'sha256':cb['sha256']}
    component_occurrences+=len(comp['files'])
    if cb['sha256']=='dbccd24d4b621f6f3c4495f686ea42120be36baa81a65a08f73574f5b75c0ed9':driver_count=len(comp['files'])
    for r in comp['files']:
        p=Path(r['path']);p=p if p.is_absolute() else ROOT/cb['base']/p
        assert current.get(logical(p))=={'path':logical(p),'sha256':r['sha256']},str(p)
check('All seven complete frozen components including actual 55-row driver',len(selection['component_manifests'])==7 and component_occurrences==261 and driver_count==55)
check('Every independently selected direct input captured at its true origin',len(selection['direct_inputs'])==49 and all(current.get(r['path'])==r for r in selection['direct_inputs']))
driver_selection=load(RUN/'T35/full-learning-inputs-0001/selection.json','d1a1569c7e290d51f6c47cfecb611fa01b58d49599926558de887657b00f53aa')
check('No global source/profile or accounting self-digest cycle',logical(API/'source-manifest.json') not in current and logical(API/'INPUT-ACCOUNTING.json') not in current and logical(API/'contract-profile.json') not in current_profile and S not in json.dumps(profile) and S not in json.dumps(driver_selection) and P not in json.dumps(driver_selection) and I not in json.dumps(inventory))
check('Capture terminal result matches outputs without runtime qualification',result['source_binding']==source['profile_binding'] if False else result['source_binding']==binding(API/'source-manifest.json',S) and result['profile_binding']==source['profile_binding'] and result['inventory_binding']==source['input_accounting']['selection_binding'] and result['current_guard_rows']==27400 and result['added_execution_rows']==2928 and result['schema_execution_rows']==3418 and result['runtime_qualified'] is False and result['historical_physical_closure']=='REFUSED')
for path,pin in reads.items(): assert digest(Path(path).read_bytes())==pin,'metadata changed on exit'
out={'schema_version':'lab-independent-captured-output-review/v1-candidate','result':'PASS-metadata-only','checks':checks,'metadata_reads_fresh_entry_exit':[binding(p,h) for p,h in sorted(reads.items())],'counts':{'original_source':24497,'original_profile':24496,'unavailable':25,'retained_original':24472,'additions':2928,'current_source':27400,'current_profile':27399,'schema_execution':3418,'family_row_occurrences':family_occurrences,'component_row_occurrences':component_occurrences,'driver_rows':driver_count},'source_binding':binding(API/'source-manifest.json',S),'profile_binding':binding(API/'contract-profile.json',P),'inventory_binding':binding(API/'INPUT-ACCOUNTING.json',I),'scope_ceiling':'Independent metadata/order/accounting/eligibility audit only. The 24472 historical retained physical inputs were not reread by this reviewer; Root owns the full physical guard and actual runtime diagnostic. Preserved original profile scalar metadata is historical and is not relabeled as the optimized current-family identity. No historical physical closure, runtime/whole-API qualification, owner authority, admission or goal completion inferred.','authority_effect':'none','runtime_executed':False,'lease_acquired':False,'task_complete':False}
with (HERE/'controls.json').open('x') as h:json.dump(out,h,sort_keys=True,indent=2);h.write('\n')
print(json.dumps({'result':out['result'],'checks':len(checks),'metadata_inputs':len(reads),'counts':out['counts']}))
