import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-lineage-map-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.lineage-map/v1'},'map_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:normalized-successor-map/v1'},'normalization':ref,'target_index':ref,'coverage':{'type':'array','minItems':1,'maxItems':100,'uniqueItems':True,'items':TEXT},'mappings':array(obj({'legacy_id':TEXT,'disposition':{'enum':['retain','revise','reclassify','split','collapse']},'successors':array(obj({'target_id':TEXT,'binding':ref}))})),'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'lineage-map-record.json'},'human_projection':{'const':'LINEAGE-MAP.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract); dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    normalization=LAB/'docs/normalizations/0001-definition-migration-model/normalization.json'
    base=ROOT.parent/'0003-review-led-reconstruction'; index=base/'target-candidate-index.json'
    entries={x['target_id']:x for x in load(index)['entries']}; decisions={x['legacy_id']:x for x in load(normalization)['migration_decisions']}
    coverage=['CAV2-D9','CAV2-D34']
    example={'schema_version':'cal-lineage-map-record/v1','artifact_type_ref':'cal.artifact-type.lineage-map/v1','map_id':'EXAMPLE-NORMALIZED-LINEAGE-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:migration-owner','scope_ref':'scope:selected-normalized-identities','profile':'candidate:normalized-successor-map/v1','normalization':binding(normalization),'target_index':binding(index),'coverage':coverage,'mappings':[{'legacy_id':legacy,'disposition':decisions[legacy]['decision'],'successors':[{'target_id':target,'binding':binding(base/entries[target]['machine_path'])} for target in decisions[legacy]['targets']]} for legacy in coverage],'challenge_route':'route:migration-lineage-review','source_direction':{'canonical':'lineage-map-record.json','human_projection':'LINEAGE-MAP.md','projection_policy':'generated-only'},'claim_ceiling':'Exact selected normalization mappings and successor scaffold identities only; no identity equivalence, authority transfer or successor admission.'}
    artifact=load(PREVIOUS/'artifact-types/typed-relation/v1/artifact.json'); path=L1/'definitions/cyberalchemy-repository-identity/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.lineage-map',artifact_type_ref='cal.artifact-type.lineage-map/v1',name='Lineage Map',schema_ref='cal.schema.lineage-map-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Maps legacy identities to active successors without transferring authority.')
    artifact['classification'].update(semantic_kind='lineage-map',lifecycle_posture_ref='candidate:lineage-map-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='lineage-map-record.json',human_filename='LINEAGE-MAP.md',identity_field='map_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'LINEAGE-MAP-01','statement':'Every selected legacy identity retains its complete declared successor set and disposition.'},{'rule_id':'LINEAGE-MAP-02','statement':'Lineage is not identity equivalence, current admission, or authority transfer.'}]
    artifact['four_facets']={'classification':'Candidate Lineage Map derived from the accepted D9 target with a source-qualified repository identity example.','schema':'Exact normalization and target index, declared coverage and explicit successor mappings.','machine_checkable':'Legacy coverage, disposition agreement, complete successor sets, index hashes and target identity closure.','human_continuation':'Generated LINEAGE-MAP.md explains the selected split and reclassification without authority inheritance.'}
    artifact['typed_residue']=[{'residue_id':'LINEAGE-MAP-R1','owner_ref':'role:migration-owner','missing':'Multi-hop lineage, withdrawals, current admission resolution and full migration coverage.','consequence':'Only explicitly covered identities are mapped to their exact normalized prototype targets.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','transfer'),('empty-mappings','mappings',[]),('blank-owner','owner_route',' '),('extra-field','identity_equivalent',True),('unknown-profile','profile','infer-renames'),('empty-coverage','coverage',[]),('missing-route','challenge_route',' ')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['normalization']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/lineage-map-record.json',positive_projection='fixtures/valid/LINEAGE-MAP.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/lineage-map-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/LINEAGE-MAP.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/lineage-map-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.lineage-map','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.cyberalchemy-repository-identity'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-lineage-map/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.cyberalchemy-repository-identity'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold),binding(normalization),binding(index)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
