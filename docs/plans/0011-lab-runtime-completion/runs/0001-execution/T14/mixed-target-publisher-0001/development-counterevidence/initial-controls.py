"""Pure public original-schema bytes. No publisher/Reader/Store constructors."""
import copy,hashlib,importlib.util,json,sys,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).resolve().parent
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
name='_T14_pure_'+uuid.uuid4().hex
spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
T=__import__(name+'.typed_targets',fromlist=['adapt'])
B=__import__(name+'.component_boundary',fromlist=['verify_actual_owner_response'])
selected=json.loads((HERE/'public-schema-example-selection.json').read_bytes());cases=[];items=[]
def refused(label,callback):
    try:callback()
    except T.Refusal:pass
    else:raise AssertionError(label+' accepted')
    cases.append({'case':label,'result':'PASS-refused'})
for row in selected['rows']:
    raw=(ROOT/row['public_original_fixture']['path']).read_bytes();document=(ROOT/row['schema']['path']).read_bytes()
    assert T.sha(raw)==row['public_original_fixture']['sha256']
    schemas=T.OriginalSchemas([row['schema']],{row['schema']['path']:document})
    spec={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']}
    spec.update(schema_path=row['schema']['path'],raw_sha256=T.sha(raw))
    value=T.adapt(raw,spec,schemas);assert value['original_bytes']==raw
    assert value['metadata']['owner_authority_resolved'] is False and value['metadata']['original_semantic_scope_native_validation'] is False
    items.append({'output_path':'targets/'+row['family']+'.json','adapted':value})
    cases.append({'case':'original public schema+exact bytes: '+row['family'],'result':'PASS-structural-only'})
    refused('wrong independently selected body hash: '+row['family'],lambda:T.adapt(raw,{**spec,'raw_sha256':'0'*64},schemas))
    refused('wrong exact identity: '+row['family'],lambda:T.adapt(raw,{**spec,'identity_ref':'foreign'},schemas))
    if row['family']=='registry-descriptor':
        refused('raw descriptor is not full ArtifactType wrapper',lambda:T.adapt(raw,{**spec,'schema_selector':None},schemas))
    refused('native governance intent cannot use artifact wrapper',lambda:T.adapt(raw,{**spec,'family':'native-governance-event-intent'},schemas))
bundle=T.prepare_byte_bundle(items,'pure-public-examples',schema_binding_sha256=T.sha((HERE/'public-schema-example-selection.json').read_bytes()))
assert T.verify_byte_bundle(bundle['files'],bundle['pins'])['canonical_admission'] is False
cases.append({'case':'heterogeneous pure byte closure and complete distinct technical receipt','result':'PASS-byte-plan-only'})
refused('duplicate selected semantic identity',lambda:T.prepare_byte_bundle(items+[items[0]],'duplicate',schema_binding_sha256='0'*64))
mutated=dict(bundle['files']);mutated['targets/foreign.json']=b'{"inert":true}'
refused('unknown bundle residue',lambda:T.verify_byte_bundle(mutated,bundle['pins']))
mutated=dict(bundle['files']);receipt=T.parse(mutated['technical-receipt.json']);receipt['owner_authority_resolved']=True;mutated['technical-receipt.json']=T.encode(receipt)
refused('whole receipt mutation against independent pins',lambda:T.verify_byte_bundle(mutated,bundle['pins']))
for text in [b'{"a":1,"a":2}',b'{"a":NaN}']:
    refused('strict public JSON duplicate/nonfinite',lambda text=text:T.parse(text))
refused('missing actual independently installed owner ingress',lambda:B.verify_actual_owner_response(None,{}, {},None,None))
refused('unsafe target output path',lambda:T.prepare_byte_bundle([{**items[0],'output_path':'../canonical.json'}],'unsafe',schema_binding_sha256='0'*64))
assert bundle['files']['targets/registry-descriptor.json']==(ROOT/selected['rows'][-1]['public_original_fixture']['path']).read_bytes()
for path in HERE.glob('*.py'):
    import ast;ast.parse(path.read_bytes())
report={'schema_version':'lab-T14-pure-public-target-validation/v1-candidate','authority_effect':'none','task_complete':False,
        'result':'PASS-public-shape-and-byte-plan-only','cases':cases,'case_count':len(cases),'public_examples':len(items),
        'actual_protected_bodies_read':False,'actual_native_or_original_publisher_rehearsal':False,
        'publisher_ProtectedReader_Store_Service_Session_constructor_or_lock_executed':False,
        'native_decision_core_history_scope_or_heterogeneous_replay_qualified':False,
        'actual_owner_or_canonical_admission':False,'final_29_230_88_members_qualified':False}
(HERE/'pure-controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'result':report['result'],'cases':len(cases),'public_examples':len(items),
                  'output_sha256':hashlib.sha256((HERE/'pure-controls-result.json').read_bytes()).hexdigest()}))
