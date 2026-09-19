import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-authority-claim-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.authority-claim/v1'},'claim_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_ref':TEXT,'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:definition-authority-claim/v1'},'authority_surface':ref,'governed_object':obj({'object_ref':TEXT,'binding':ref}),'operation_ref':TEXT,'intended_effect':TEXT,'kind_ref':{'const':'definition'},'posture_ref':{'const':'candidate'},'basis':array(obj({'basis_kind':{'enum':['evidence','decision']},'binding':ref,'supports':TEXT})),'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'authority-claim-record.json'},'human_projection':{'const':'AUTHORITY-CLAIM.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    model_path=PREVIOUS/'artifact-types/authority-model/v1/fixtures/valid/authority-model-record.json'
    object_path=L1/'definitions/authority-claim/v1/definition.json'; target=load(object_path)
    example={'schema_version':'cal-authority-claim-record/v1','artifact_type_ref':'cal.artifact-type.authority-claim/v1','claim_id':'EXAMPLE-DEFINITION-REVIEW-CLAIM-001','status':'candidate-unadmitted','authority_effect':'none','owner_ref':'role:definition-owner','owner_route':'route:definition-owner','scope_ref':load(model_path)['scope_ref'],'profile':'candidate:definition-authority-claim/v1','authority_surface':binding(model_path),'governed_object':{'object_ref':target['definition_id']+'@'+target['version'],'binding':binding(object_path)},'operation_ref':'request-review','intended_effect':'review','kind_ref':'definition','posture_ref':'candidate','basis':[{'basis_kind':'evidence','binding':binding(PREVIOUS/'receipts/validation.json'),'supports':'The illustrative model and its routing checker passed local validation; this does not establish owner authority.'}],'challenge_route':'route:definition-governance-challenge','source_direction':{'canonical':'authority-claim-record.json','human_projection':'AUTHORITY-CLAIM.md','projection_policy':'generated-only'},'claim_ceiling':'Illustrative claim with exact content bindings and model routing only. No authenticated owner, valid grant, gate verdict or execution authority.'}
    artifact=load(PREVIOUS/'artifact-types/authority-model/v1/artifact.json'); definition=target
    bound={**binding(object_path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.authority-claim',artifact_type_ref='cal.artifact-type.authority-claim/v1',name='Authority Claim',schema_ref='cal.schema.authority-claim-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Claims scoped authority over an exact object and operation.')
    artifact['classification'].update(semantic_kind='authority-claim',lifecycle_posture_ref='candidate:authority-claim-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='authority-claim-record.json',human_filename='AUTHORITY-CLAIM.md',identity_field='claim_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'AUTHORITY-CLAIM-01','statement':'An explicit claim and exact evidence do not authenticate the claimant or establish a grant.'},{'rule_id':'AUTHORITY-CLAIM-02','statement':'The governed object, authority surface, claim and basis remain distinct records.'}]
    artifact['four_facets']={'classification':'Candidate Authority Claim with source-qualified meaning and distinct object and model bindings.','schema':'Owner, route, scope, authority surface, exact object, operation, basis, effect and challenge route.','machine_checkable':'Exact bytes, versioned Definition identity and prior authority-model routing with owner-route agreement.','human_continuation':'Generated AUTHORITY-CLAIM.md explains the assertion, evidence and challenge route.'}
    artifact['typed_residue']=[{'residue_id':'AUTHORITY-CLAIM-R1','owner_ref':'role:definition-owner','missing':'Authenticated claimant, basis sufficiency, real gate verdict and authority admission.','consequence':'Only claims about exact Definition records under the prior candidate model profile are inspected.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','grant'),('empty-basis','basis',[]),('blank-owner','owner_ref',' '),('extra-field','authenticated',True),('unknown-profile','profile','trust-owner'),('missing-challenge','challenge_route',' '),('wrong-kind','kind_ref','evidence')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['governed_object']['binding']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/authority-claim-record.json',positive_projection='fixtures/valid/AUTHORITY-CLAIM.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/authority-claim-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/AUTHORITY-CLAIM.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/authority-claim-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.authority-claim','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.authority-claim'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-authority-claim/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.authority-claim'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
