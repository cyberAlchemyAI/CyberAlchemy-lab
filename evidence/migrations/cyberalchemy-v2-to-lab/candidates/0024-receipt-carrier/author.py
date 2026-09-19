import copy
import subprocess
import sys
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-receipt-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.receipt/v1'},'receipt_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:evidence-check-replay/v1'},'operation_ref':{'const':'operation:check-evidence-inventory'},'implementation':ref,'execution_snapshot':ref,'input':ref,'stdout':ref,'stderr':ref,'exit_code':{'enum':[0,2]},'reported_result':{'enum':['passed','invalid-input']},'python_version':TEXT,'limitations':TEXT,'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'receipt-record.json'},'human_projection':{'const':'RECEIPT.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract); dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    # Execute only the fixed predecessor checker after verifying its frozen snapshot.
    for item in load(PREVIOUS/'manifest.json')['materials']:
        if sha(LAB/item['path'])!=item['sha256']: raise ValueError('Predecessor drift: '+item['path'])
    script=PREVIOUS/'check.py'; input_path=PREVIOUS/'artifact-types/evidence-set/v1/fixtures/valid/evidence-set-record.json'
    result=subprocess.run([sys.executable,str(script),str(input_path)],capture_output=True,timeout=30)
    if result.returncode!=0: raise ValueError('Example operation failed: '+result.stderr.decode())
    (ROOT/'examples').mkdir(exist_ok=True)
    (ROOT/'examples/stdout.json').write_bytes(result.stdout); (ROOT/'examples/stderr.txt').write_bytes(result.stderr)
    example={'schema_version':'cal-receipt-record/v1','artifact_type_ref':'cal.artifact-type.receipt/v1','receipt_id':'LOCAL-EVIDENCE-CHECK-RECEIPT-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:local-validation-owner','scope_ref':'scope:local-evidence-inventory-check','profile':'candidate:evidence-check-replay/v1','operation_ref':'operation:check-evidence-inventory','implementation':binding(script),'execution_snapshot':binding(PREVIOUS/'manifest.json'),'input':binding(input_path),'stdout':binding(ROOT/'examples/stdout.json'),'stderr':binding(ROOT/'examples/stderr.txt'),'exit_code':result.returncode,'reported_result':'passed','python_version':sys.version,'limitations':'Records one local checker invocation. It neither establishes evidence truth nor proves publication, external execution or actor authority.','challenge_route':'route:receipt-review','source_direction':{'canonical':'receipt-record.json','human_projection':'RECEIPT.md','projection_policy':'generated-only'},'claim_ceiling':'Exact local operation inputs, code, captured streams and replay agreement only; no external execution, publication or authority proof.'}
    artifact=load(PREVIOUS/'artifact-types/evidence-set/v1/artifact.json'); path=L1/'definitions/traceability/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.receipt',artifact_type_ref='cal.artifact-type.receipt/v1',name='Receipt',schema_ref='cal.schema.receipt-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Records what one bounded operation did and its exact inputs and outputs.')
    artifact['classification'].update(semantic_kind='receipt',lifecycle_posture_ref='candidate:receipt-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='receipt-record.json',human_filename='RECEIPT.md',identity_field='receipt_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'RECEIPT-01','statement':'Operation, input, implementation and captured outputs remain exact separate bindings.'},{'rule_id':'RECEIPT-02','statement':'Replay agreement does not establish external effects, evidence truth or actor authority.'}]
    artifact['four_facets']={'classification':'Candidate Receipt with source-qualified Traceability meaning.','schema':'Bound local operation, frozen checker snapshot, input, output streams, exit code and runtime version.','machine_checkable':'Exact file integrity, fixed-operation allowlist, result agreement and bounded local replay.','human_continuation':'Generated RECEIPT.md states what ran and what its result cannot prove.'}
    artifact['typed_residue']=[{'residue_id':'RECEIPT-R1','owner_ref':'role:local-validation-owner','missing':'Authenticated historical execution, complete environment lock, publication and arbitrary operation profiles.','consequence':'Only the fixed local Evidence Set checker and its frozen example input are replayed.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','publish'),('blank-owner','owner_route',' '),('extra-field','publication_proven',True),('unknown-profile','profile','shell'),('missing-route','challenge_route',' '),('unknown-operation','operation_ref','execute-anything'),('invalid-exit','exit_code',99)]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['stdout']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/receipt-record.json',positive_projection='fixtures/valid/RECEIPT.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/receipt-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/RECEIPT.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/receipt-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.receipt','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.traceability'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-receipt/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.traceability'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
