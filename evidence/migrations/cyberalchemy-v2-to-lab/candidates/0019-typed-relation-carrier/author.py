import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    endpoint=obj({'object_ref':TEXT,'binding':ref})
    contract=obj({'schema_version':{'const':'cal-typed-relation-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.typed-relation/v1'},'relation_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:artifact-definition-binding/v1'},'relation_kind_ref':{'const':'candidate:binds-definition/v1'},'direction':{'const':'source-to-target'},'source':endpoint,'target':endpoint,'evidence':array(ref),'declared_effect':obj({'category':{'const':'validation'},'description':TEXT}),'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'typed-relation-record.json'},'human_projection':{'const':'TYPED-RELATION.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    dump(PACKAGE/'schema.json',contract); dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/'schema.json')]})
    source=PREVIOUS/'artifact-types/gate/v1/artifact.json'; target=L1/'definitions/gate/v1/definition.json'; definition=load(target)
    example={'schema_version':'cal-typed-relation-record/v1','artifact_type_ref':'cal.artifact-type.typed-relation/v1','relation_id':'EXAMPLE-GATE-DEFINITION-BINDING-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:artifact-type-owner','scope_ref':'scope:lab-candidate-definition-bindings','profile':'candidate:artifact-definition-binding/v1','relation_kind_ref':'candidate:binds-definition/v1','direction':'source-to-target','source':{'object_ref':load(source)['artifact_type_ref'],'binding':binding(source)},'target':{'object_ref':definition['definition_id']+'@'+definition['version'],'binding':binding(target)},'evidence':[binding(PREVIOUS/'receipts/validation.json')],'declared_effect':{'category':'validation','description':'Require the Gate artifact to retain its exact declared Definition binding before relying on the link.'},'challenge_route':'route:artifact-definition-binding-review','source_direction':{'canonical':'typed-relation-record.json','human_projection':'TYPED-RELATION.md','projection_policy':'generated-only'},'claim_ceiling':'Exact directed binding checks only; owner-local meaning, relation-kind adoption and endpoint promotion remain unproven.'}
    artifact=load(source); path=L1/'definitions/typed-coupling-invariant/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.typed-relation',artifact_type_ref='cal.artifact-type.typed-relation/v1',name='Typed Relation',schema_ref='cal.schema.typed-relation-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Records directed owner-qualified coupling without interpreting owner-local semantics.')
    artifact['classification'].update(semantic_kind='typed-relation',lifecycle_posture_ref='candidate:typed-relation-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='typed-relation-record.json',human_filename='TYPED-RELATION.md',identity_field='relation_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'TYPED-RELATION-01','statement':'Direction, endpoint identities, kind, owner, evidence and effect remain explicit.'},{'rule_id':'TYPED-RELATION-02','statement':'A verified binding does not interpret owner-local semantics or automatically promote a relation or endpoint.'}]
    artifact['four_facets']={'classification':'Candidate Typed Relation governed by the source-qualified Typed Coupling Invariant.','schema':'Directed source and target bindings, explicit candidate kind, owner route, evidence and validation effect.','machine_checkable':'Exact endpoint versions and digests, type direction and agreement with the source artifact semantic binding.','human_continuation':'Generated TYPED-RELATION.md explains the exact link and its review route.'}
    artifact['typed_residue']=[{'residue_id':'TYPED-RELATION-R1','owner_ref':'role:artifact-type-owner','missing':'Other relation-kind profiles, Project relations, owner authentication and owner-local semantic interpretation.','consequence':'Only the candidate artifact-to-Definition binding profile is implemented; no relation kind is admitted.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','promote'),('empty-evidence','evidence',[]),('blank-owner','owner_route',' '),('extra-field','interpreted',True),('unknown-profile','profile','any-link'),('reverse-direction','direction','target-to-source'),('unknown-kind','relation_kind_ref','relation:any')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['source']['binding']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/typed-relation-record.json',positive_projection='fixtures/valid/TYPED-RELATION.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/typed-relation-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/TYPED-RELATION.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/typed-relation-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.typed-relation','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.typed-coupling-invariant'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-typed-relation/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.typed-coupling-invariant'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
