import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-residue-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.residue/v1'},'residue_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:json-field-preservation/v1'},'source_operation':TEXT,'source':ref,'result':ref,'preservation_condition':obj({'description':TEXT,'required_fields':{'type':'array','minItems':1,'maxItems':100,'uniqueItems':True,'items':TEXT}}),'residue_type':{'const':'representation-loss'},'observed_remainder':array(obj({'field':TEXT,'issue':{'enum':['missing','changed']}})),'treatment':{'enum':['repair','type','gate','climb','accept','defer']},'treatment_route':TEXT,'closure_condition':TEXT,'source_direction':obj({'canonical':{'const':'residue-record.json'},'human_projection':{'const':'RESIDUE.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract); dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    dump(ROOT/'examples/source.json',{'id':'example-1','owner':'role:example-owner','meaning':'An illustrative owned record.'})
    dump(ROOT/'examples/result.json',{'id':'example-1'})
    example={'schema_version':'cal-residue-record/v1','artifact_type_ref':'cal.artifact-type.residue/v1','residue_id':'EXAMPLE-PROJECTION-LOSS-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:representation-owner','scope_ref':'scope:example-json-projection','profile':'candidate:json-field-preservation/v1','source_operation':'example:project-record-to-id','source':binding(ROOT/'examples/source.json'),'result':binding(ROOT/'examples/result.json'),'preservation_condition':{'description':'Preserve id, owner and meaning fields without changing their JSON values.','required_fields':['id','owner','meaning']},'residue_type':'representation-loss','observed_remainder':[{'field':'meaning','issue':'missing'},{'field':'owner','issue':'missing'}],'treatment':'repair','treatment_route':'route:projection-repair-review','closure_condition':'Supply a revised representation preserving all required fields and an owner-reviewed closure record.','source_direction':{'canonical':'residue-record.json','human_projection':'RESIDUE.md','projection_policy':'generated-only'},'claim_ceiling':'Exact field-preservation remainder only; no semantic equivalence, actual operation execution, treatment completion or promotion.'}
    artifact=load(PREVIOUS/'artifact-types/withdrawal-record/v1/artifact.json'); path=L1/'definitions/residue/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.residue',artifact_type_ref='cal.artifact-type.residue/v1',name='Residue',schema_ref='cal.schema.residue-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Records meaningful information not carried by the current representation.')
    artifact['classification'].update(semantic_kind='residue',lifecycle_posture_ref='candidate:residue-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='residue-record.json',human_filename='RESIDUE.md',identity_field='residue_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'RESIDUE-01','statement':'Residue requires an operation, preservation condition, observed remainder, type, evidence and owner treatment route.'},{'rule_id':'RESIDUE-02','statement':'Naming acceptance, repair or promotion-related treatment does not execute it or close the residue.'}]
    artifact['four_facets']={'classification':'Candidate Residue bound to source-qualified D18.','schema':'Exact source and result evidence, preservation fields, observed loss and typed treatment.','machine_checkable':'Strict JSON field preservation, complete remainder agreement and immutable evidence bindings.','human_continuation':'Generated RESIDUE.md explains what was not carried forward and the next treatment route.'}
    artifact['typed_residue']=[{'residue_id':'RESIDUE-R1','owner_ref':'role:representation-owner','missing':'Semantic preservation, actual transformation provenance, treatment execution and owner-approved closure.','consequence':'Only top-level JSON field preservation is inspected; probabilistic and higher-layer residue profiles remain unsupported.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','promote'),('empty-remainder','observed_remainder',[]),('blank-owner','owner_route',' '),('extra-field','closed',True),('unknown-profile','profile','entropy'),('missing-treatment','treatment','resolve'),('missing-route','treatment_route',' ')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['source']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/residue-record.json',positive_projection='fixtures/valid/RESIDUE.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/residue-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/RESIDUE.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/residue-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.residue','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.residue'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-residue/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.residue'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
