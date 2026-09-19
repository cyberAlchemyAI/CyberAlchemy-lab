import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT = {'type':'string','pattern':r'\S'}
def obj(p):
    return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    witness=obj({'witness_id':TEXT,'before':ref,'after':ref,'expected_before':{'const':True},'expected_after_on_original':{'type':'boolean'},'expected_after_on_migrated':{'const':True}})
    contract=obj({'schema_version':{'const':'cal-schema-change-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.schema-change/v1'},'change_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_ref':TEXT,'scope_ref':TEXT,'reason':TEXT,'preimage':ref,'postimage':ref,'source_evidence':{'type':'array','minItems':1,'items':ref},'witnesses':{'type':'array','minItems':1,'maxItems':100,'items':witness},'compatibility_claim':{'enum':['breaking-on-witnesses','compatible-on-witnesses']},'migration_obligation':TEXT,'rollout_route':TEXT,'rollback_route':TEXT,'validator_ref':ref,'residue':{'type':'array','minItems':1,'items':obj({'owner_ref':TEXT,'missing':TEXT,'consequence':TEXT})},'source_direction':obj({'canonical':{'const':'schema-change-record.json'},'human_projection':{'const':'SCHEMA-CHANGE.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    pre=PREVIOUS/'artifact-types/schema/v1/fixtures/valid/schema-record.json'
    post=load(pre); post['constraints'][0]['fields'].append({'name':'revision','value_type':'integer','required':True})
    dump(ROOT/'examples/postimage.json',post)
    graph=load(PREVIOUS/'examples/conforming.json'); graph['nodes'][0]['fields']['revision']=1
    dump(ROOT/'examples/migrated.json',graph)
    scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-schema-change/v1/artifact.json'
    example={'schema_version':'cal-schema-change-record/v1','artifact_type_ref':'cal.artifact-type.schema-change/v1','change_id':'EXAMPLE-REQUIRE-REVISION-001','status':'candidate-unadmitted','authority_effect':'none','owner_ref':'role:schema-owner','scope_ref':post['scope_ref'],'reason':'Require an explicit revision number on artifact records.','preimage':binding(pre),'postimage':binding(ROOT/'examples/postimage.json'),'source_evidence':[binding(scaffold)],'witnesses':[{'witness_id':'artifact-owner-example','before':binding(PREVIOUS/'examples/conforming.json'),'after':binding(ROOT/'examples/migrated.json'),'expected_before':True,'expected_after_on_original':False,'expected_after_on_migrated':True}],'compatibility_claim':'breaking-on-witnesses','migration_obligation':'Supply revision as an integer for every artifact; validate all consumers before any rollout. Example revision 1 is fixture data only.','rollout_route':'Owner reviews complete consumer inventory and migration outputs before requesting a separate adoption decision.','rollback_route':'Restore exact preimage schema and original records together; the supplied original witness is checked against the preimage.','validator_ref':binding(PREVIOUS/'check.py'),'residue':[{'owner_ref':'role:schema-owner','missing':'Complete consumer inventory and universal compatibility proof.','consequence':'Only supplied witnesses are assessed; rollout and migration are not executed.'}],'source_direction':{'canonical':'schema-change-record.json','human_projection':'SCHEMA-CHANGE.md','projection_policy':'generated-only'},'claim_ceiling':'Exact versions and supplied regression witnesses only. No universal compatibility, migration execution or adoption.'}
    artifact=load(PREVIOUS/'artifact-types/schema/v1/artifact.json')
    defs=[L1/f'definitions/{x}/v1/definition.json' for x in ['schema','schema-evolution-invariant']]
    bindings=[{**binding(p),'definition_ref':load(p)['definition_id']+'@'+load(p)['version'],'admission_posture':'candidate-unadmitted'} for p in defs]
    artifact.update(artifact_type_id='cal.artifact-type.schema-change',artifact_type_ref='cal.artifact-type.schema-change/v1',name='Schema Change',schema_ref='cal.schema.schema-change-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[x['definition_ref'] for x in bindings],semantic_definition_bindings=bindings,distinct_validation_purpose='Binds exact preimage, postimage, compatibility, migration, and regression obligations.')
    artifact['classification'].update(semantic_kind='schema-change',lifecycle_posture_ref='candidate:schema-change-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='schema-change-record.json',human_filename='SCHEMA-CHANGE.md',identity_field='change_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'SCHEMA-CHANGE-01','statement':'Exact bytes bind both schema versions and every supplied witness.'},{'rule_id':'SCHEMA-CHANGE-02','statement':'Witness compatibility does not prove universal compatibility or authorize rollout.'}]
    artifact['four_facets']={'classification':'Candidate Schema Change under the Schema Evolution Invariant.','schema':'Closed amendment, exact versions, routes and witness obligations.','machine_checkable':'Checks preimage, unchanged witnesses under postimage, supplied migrated witnesses and compatibility claims.','human_continuation':'Generated SCHEMA-CHANGE.md names obligations and remaining uncertainty.'}
    artifact['typed_residue']=[{'residue_id':'SCHEMA-CHANGE-R1',**example['residue'][0]}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','admit'),('empty-witnesses','witnesses',[]),('universal-claim','compatibility_claim','universally-compatible'),('missing-residue','residue',[]),('blank-owner','owner_ref',' '),('extra-field','approved',True),('empty-evidence','source_evidence',[])]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['preimage']['sha256']='bad'; invalid['invalid-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/schema-change-record.json',positive_projection='fixtures/valid/SCHEMA-CHANGE.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/schema-change-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','change_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/SCHEMA-CHANGE.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/schema-change-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.schema-change','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.schema','semantic.schema-evolution-invariant'}; seeds=sorted(selected); edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':seeds,'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
