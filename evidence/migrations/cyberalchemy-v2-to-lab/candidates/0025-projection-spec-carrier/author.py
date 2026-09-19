import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-projection-spec-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.projection-spec/v1'},'projection_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:json-field-view/v1'},'source':ref,'fields':array(obj({'source_field':TEXT,'view_field':TEXT})),'omissions':array(obj({'source_field':TEXT,'reason':TEXT}),0),'view_authority':{'const':'none'},'update_policy':{'const':'regenerate-from-bound-source'},'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'projection-spec-record.json'},'human_projection':{'const':'PROJECTION-SPEC.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract); dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    source=PREVIOUS/'artifact-types/receipt/v1/fixtures/valid/receipt-record.json'; selected=['receipt_id','reported_result','exit_code']
    example={'schema_version':'cal-projection-spec-record/v1','artifact_type_ref':'cal.artifact-type.projection-spec/v1','projection_id':'EXAMPLE-RECEIPT-SUMMARY-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:projection-owner','scope_ref':'scope:receipt-summary','profile':'candidate:json-field-view/v1','source':binding(source),'fields':[{'source_field':x,'view_field':x} for x in selected],'omissions':[{'source_field':x,'reason':'Excluded from the compact view; consult the exact bound Receipt source for this field.'} for x in sorted(set(load(source))-set(selected))],'view_authority':'none','update_policy':'regenerate-from-bound-source','challenge_route':'route:projection-drift-review','source_direction':{'canonical':'projection-spec-record.json','human_projection':'PROJECTION-SPEC.md','projection_policy':'generated-only'},'claim_ceiling':'Deterministic selected-field view only; no source authority promotion, semantic completeness or reverse editing.'}
    artifact=load(PREVIOUS/'artifact-types/receipt/v1/artifact.json'); path=L1/'definitions/projection-specification/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.projection-spec',artifact_type_ref='cal.artifact-type.projection-spec/v1',name='Projection Specification',schema_ref='cal.schema.projection-spec-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Defines deterministic generation of a non-authoritative view.')
    artifact['classification'].update(semantic_kind='projection-spec',lifecycle_posture_ref='candidate:projection-spec-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='projection-spec-record.json',human_filename='PROJECTION-SPEC.md',identity_field='projection_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'PROJECTION-01','statement':'Every source field is selected or explicitly omitted; derived fields never overwrite one another.'},{'rule_id':'PROJECTION-02','statement':'The view binds its source and specification and never acquires authority from generation.'}]
    artifact['four_facets']={'classification':'Candidate Projection Specification bound to its source-qualified meaning.','schema':'Exact source, field mappings, explicit omissions and one-way update policy.','machine_checkable':'Complete field accounting, unique mappings, exact source values and deterministic view bytes.','human_continuation':'Generated PROJECTION-SPEC.md explains the compact view and every omitted field.'}
    artifact['typed_residue']=[{'residue_id':'PROJECTION-R1','owner_ref':'role:projection-owner','missing':'Nested transformations, semantic fidelity, live synchronization and view activation.','consequence':'Only top-level field selection and renaming are implemented; no source mutation or authority transfer.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','promote'),('empty-fields','fields',[]),('blank-owner','owner_route',' '),('extra-field','activated',True),('unknown-profile','profile','execute-template'),('missing-route','challenge_route',' '),('reverse-update','update_policy','write-back')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['view_authority']='governing'; invalid['authoritative-view']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/projection-spec-record.json',positive_projection='fixtures/valid/PROJECTION-SPEC.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/projection-spec-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/PROJECTION-SPEC.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/projection-spec-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.projection-spec','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    from generate import project
    dump(ROOT/'examples/view.json',project(PACKAGE/'fixtures/valid/projection-spec-record.json'))
    selected={'semantic.projection-specification'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-projection-spec/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.projection-specification'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
