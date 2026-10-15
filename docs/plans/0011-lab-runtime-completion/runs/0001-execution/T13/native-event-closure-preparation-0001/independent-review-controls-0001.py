"""Independent pure public-metadata conservation review. No native or private reads."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,types
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable)==INSTALL/'bin/python'
sys.path.insert(0,str(INSTALL/'deps'))
import jsonschema
checks=[]
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
sha=lambda b:hashlib.sha256(b).hexdigest()
fd_start=len(os.listdir('/proc/self/fd'))
pins={'HANDOFF.json':'4588f8399d4d7f0d1a4c46a907ae741af64d8e343e33d4d413baeb3a497f8077','source-manifest.json':'1e5426221f58425297c25835b00846a907e85e89cf8abc8c69804e7f87341f09','ACCOUNTING-88.json':'c783761f5180365cbec59ef8ab654cb3d9bb3376e408eee37f06216ccaf46f1d','CONDITIONAL-PROOF.json':'918982dc4c4f90fb61593986cf9b9046101c708758f85b3139a5dc7584e324cf','account.py':'872cbbec0c01d5419414493c35130c30d2577fb4a892162355c5660446461486','input-selection.json':'e7ed0c7b5bedd13795e71117a336d25e7ab80a71679817cc97b3f020446119c7'}
for name,pin in pins.items():check('Root independent pin '+name,sha((HERE/name).read_bytes())==pin)
raw=(HERE/'account.py').read_bytes();tree=ast.parse(raw)
check('Selected accounting imports only ordinary public-byte modules',{n.names[0].name for n in tree.body if isinstance(n,ast.Import)} <= {'argparse','hashlib','json','os','stat'})
module=types.ModuleType('_T13_independent_public_review_0001');module.__file__=str(HERE/'account.py')
exec(compile(raw,str(HERE/'account.py'),'exec',dont_inherit=True),module.__dict__)
selection=module.parse((HERE/'input-selection.json').read_bytes())
manifest=module.parse((HERE/'source-manifest.json').read_bytes())
for row in manifest['files']:
 check('Fresh frozen MF row '+row['path'],len(module.capture(row))==row['size_bytes'])
value=module.analyze(selection)
check('Regenerated exact all88 accounting bytes',(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()==(HERE/'ACCOUNTING-88.json').read_bytes())
original=module.parse(module.capture(selection['original_preparation_binding']))
original_members=[m for m in original['members'] if m['member_class']=='representation-adoption-intent']
final=module.parse(module.capture(selection['final_selection_binding']))
final_members=[m for m in final['members'] if m['member_class']=='representation-adoption-intent']
check('Original all323 package members remain declared',len(original['members'])==323)
check('All88 accounting preserves original list order',[r['member_ref'] for r in value['rows']]==[r['member_ref'] for r in original_members])
check('Final selection contains same88 exact intent identities',{r['member_ref'] for r in final_members}=={r['member_ref'] for r in original_members})
schema_row=next(r for r in selection['files'] if r['path'].endswith('O06/schemas/adoption-intent.schema.json'))
schema=module.parse(module.capture(schema_row));jsonschema.Draft202012Validator.check_schema(schema)
validator=jsonschema.Draft202012Validator(schema)
for row,member in zip(value['rows'],original_members):
 intent=module.parse(module.capture(row['intent_binding']));validator.validate(intent)
 fields={'original_scope':'scope','original_dependencies':'dependencies','original_proposed_owner_roles':'proposed_owner_roles','original_requested_axes':'requested_axes','original_exclusions':'exclusions'}
 check('Original member obligations preserved '+row['member_ref'],all(row[a]==member[b] for a,b in fields.items()))
 check('Original intent tuples and schema preserved '+row['member_ref'],row['semantic_tuple']==intent['semantic_tuple'] and row['predecessor_governance_tuple']==intent['predecessor_governance_tuple'] and row['metadata_record_binding']==intent['metadata_record_binding'] and row['original_consequence_rule']==intent['consequence_rule'])
 check('All actual native/authority values remain absent '+row['member_ref'],all(row[k] is None for k in ['actual_owner_Decision_binding','actual_owner_response','native_event_bytes','native_event_digest','stable_unsigned_core']) and not row['T10_dependency_complete'] and not row['T11_dependency_complete'] and not row['single_checkpoint_ready'])
for key,change in [('expected_intent_count',87),('real_owner_response_allowed',True),('private_body_export_allowed',True),('shared_or_native_changes_allowed',True)]:
 modified=copy.deepcopy(selection);modified[key]=change
 try:module.analyze(modified)
 except ValueError:check('Inert packet refusal '+key,True)
 else:raise AssertionError('Packet incorrectly accepted '+key)
for bad in [{'path':'inert/native.snapshot','sha256':'0'*64},{'path':'inert/branch.snapshot','sha256':'0'*64},{'path':'../inert','sha256':'0'*64}]:
 try:module.capture(bad)
 except ValueError:check('Rejected locator before private/archive read '+bad['path'],True)
 else:raise AssertionError('Bad locator accepted')
proof=module.parse((HERE/'CONDITIONAL-PROOF.json').read_bytes())
check('Proof explicitly conditional with known counterexample',proof['schema_cannot_alone_prove_universal_cycle'] is True and proof['selected_original_adoption_materializer_exists_in_packet'] is False and 'external witness' in proof['counterexample_to_universal_schema_claim'])
check('All88 blocked conditional scope retained',proof['applies_to_intent_count']==88 and proof['actual_native_event_or_core_or_Decision'] is None)
for row in selection['files']:module.capture(row)
check('All199 fresh guarded public inputs',len(selection['files'])==199)
check('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_start)
report={'schema_version':'lab-T13-independent-public-review-controls/v1','authority_effect':'none','result':'PASS-scoped-public-accounting-and-conditional-proof-controls','check_count':len(checks),'checks':checks,'actual_interpreter':str(sys.executable),'Root_pins':pins,'public_inputs':199,'manifest_rows':len(manifest['files']),'intents':88,'original_package_members':323,'FD_delta':0,'native_calls_or_events_or_cores_or_Decisions':False,'private_archive_read_or_body_export':False,'shared_or_original_mutation':False,'full_T13_complete':False}
with (HERE/'independent-review-controls-0001.json').open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','Root_pins']}))
