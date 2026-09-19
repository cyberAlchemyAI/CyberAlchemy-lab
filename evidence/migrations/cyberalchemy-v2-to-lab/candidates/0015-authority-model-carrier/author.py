import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    strings={**array(TEXT),'uniqueItems':True}
    optional_strings={**array(TEXT,0),'uniqueItems':True}
    contract=obj({'schema_version':{'const':'cal-authority-model-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.authority-model/v1'},'model_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_ref':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:closed-authority-routing/v1'},'authority_kinds':strings,'postures':strings,'effects':strings,'operations':array(obj({'operation_id':TEXT,'effect_ref':TEXT})),'rules':array(obj({'rule_id':TEXT,'kind_ref':TEXT,'posture_ref':TEXT,'owner_route':TEXT,'allowed_effects':optional_strings,'blocked_effects':optional_strings,'gate_ref':TEXT,'validation_surface_ref':TEXT,'non_collapse_rules':strings})),'conflict_rule':{'const':'reject-overlapping-kind-posture-rules'},'unknown_kind_rule':{'const':'blocked-until-owner-amends-model'},'amendment_route':TEXT,'source_direction':obj({'canonical':{'const':'authority-model-record.json'},'human_projection':{'const':'AUTHORITY-MODEL.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    query=obj({'model_ref':TEXT,'scope_ref':TEXT,'claim_ref':TEXT,'subject_ref':TEXT,'kind_ref':TEXT,'posture_ref':TEXT,'operation_ref':TEXT,'intended_effect':TEXT})
    dump(PACKAGE/'schema.json',contract); dump(PACKAGE/'claim.schema.json',query)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/x) for x in ['schema.json','claim.schema.json']]})
    example={'schema_version':'cal-authority-model-record/v1','artifact_type_ref':'cal.artifact-type.authority-model/v1','model_id':'EXAMPLE-RECONSTRUCTION-AUTHORITY-001','status':'candidate-unadmitted','authority_effect':'none','owner_ref':'role:authority-model-owner','scope_ref':'scope:example-reconstruction','profile':'candidate:closed-authority-routing/v1','authority_kinds':['definition','evidence'],'postures':['candidate'],'effects':['review','admit'],'operations':[{'operation_id':'request-review','effect_ref':'review'},{'operation_id':'request-admission','effect_ref':'admit'}],'rules':[{'rule_id':'definition-candidate','kind_ref':'definition','posture_ref':'candidate','owner_route':'route:definition-owner','allowed_effects':['review'],'blocked_effects':['admit'],'gate_ref':'gate:definition-review','validation_surface_ref':'surface:definition-validation','non_collapse_rules':['Candidate construction is not admission.']},{'rule_id':'evidence-candidate','kind_ref':'evidence','posture_ref':'candidate','owner_route':'route:evidence-owner','allowed_effects':['review'],'blocked_effects':['admit'],'gate_ref':'gate:evidence-review','validation_surface_ref':'surface:evidence-validation','non_collapse_rules':['Evidence does not become semantic authority by passing a check.']}],'conflict_rule':'reject-overlapping-kind-posture-rules','unknown_kind_rule':'blocked-until-owner-amends-model','amendment_route':'route:authority-model-owner-review','source_direction':{'canonical':'authority-model-record.json','human_projection':'AUTHORITY-MODEL.md','projection_policy':'generated-only'},'claim_ceiling':'Candidate routing map and supplied claim assertions only; no actor authentication, gate verdict or authority grant.'}
    claim={'model_ref':example['model_id'],'scope_ref':example['scope_ref'],'claim_ref':'example:claim-1','subject_ref':'example:definition-1','kind_ref':'definition','posture_ref':'candidate','operation_ref':'request-review','intended_effect':'review'}
    dump(ROOT/'examples/ready.json',claim)
    unknown=copy.deepcopy(claim); unknown['kind_ref']='unlisted'; dump(ROOT/'examples/unknown.json',unknown)
    blocked=copy.deepcopy(claim); blocked.update(operation_ref='request-admission',intended_effect='admit'); dump(ROOT/'examples/blocked.json',blocked)
    artifact=load(PREVIOUS/'artifact-types/policy/v1/artifact.json')
    bindings=[]
    for slug in ['authority-model','closed-authority-kind-invariant']:
        path=L1/f'definitions/{slug}/v1/definition.json'; definition=load(path)
        bindings.append({**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'})
    artifact.update(artifact_type_id='cal.artifact-type.authority-model',artifact_type_ref='cal.artifact-type.authority-model/v1',name='Authority Model',schema_ref='cal.schema.authority-model-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[x['definition_ref'] for x in bindings],semantic_definition_bindings=bindings,distinct_validation_purpose='Defines authority kinds, claims, operations, effects, and conflict rules.')
    artifact['classification'].update(semantic_kind='authority-model',lifecycle_posture_ref='candidate:authority-model-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='authority-model-record.json',human_filename='AUTHORITY-MODEL.md',identity_field='model_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'AUTHORITY-MODEL-01','statement':'Unknown kinds are blocked until an owner amends the model.'},{'rule_id':'AUTHORITY-MODEL-02','statement':'An allowed modeled effect names a review route, not an authenticated grant or recorded gate verdict.'}]
    artifact['four_facets']={'classification':'Candidate Authority Model bound to D41 and the closed-kind invariant from D49.','schema':'Closed kinds, postures, operations, effects and nonoverlapping routing rules.','machine_checkable':'Reference closure, effect partitions, kind coverage, conflict rejection and default blocking.','human_continuation':'Generated AUTHORITY-MODEL.md explains the example routes and authority boundaries.'}
    artifact['typed_residue']=[{'residue_id':'AUTHORITY-MODEL-R1','owner_ref':'role:authority-model-owner','missing':'Authenticated Authority Claims, recorded gate verdicts, lifecycle transitions and delegated authority.','consequence':'Only static exact-match routing previews are supported; no action is authorized.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','grant'),('empty-kinds','authority_kinds',[]),('empty-rules','rules',[]),('blank-owner','owner_ref',' '),('extra-field','authenticated',True),('unknown-profile','profile','allow-all'),('allow-unknown','unknown_kind_rule','allow')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['conflict_rule']='first-match'; invalid['silent-conflict']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/authority-model-record.json',positive_projection='fixtures/valid/AUTHORITY-MODEL.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/authority-model-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/AUTHORITY-MODEL.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/authority-model-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.authority-model','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.authority-model','semantic.closed-authority-kind-invariant'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-authority-model/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.authority-model','semantic.closed-authority-kind-invariant'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
