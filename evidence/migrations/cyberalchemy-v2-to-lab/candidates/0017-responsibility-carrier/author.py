import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    scalar={'type':['string','integer','boolean']}
    contract=obj({'schema_version':{'const':'cal-responsibility-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.responsibility/v1'},'responsibility_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_ref':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:bound-json-obligation/v1'},'subject':ref,'obligation':TEXT,'criteria':array(obj({'criterion_id':TEXT,'description':TEXT,'field':TEXT,'expected':scalar})),'review_route':TEXT,'escalation_route':TEXT,'authority_boundary':TEXT,'source_direction':obj({'canonical':{'const':'responsibility-record.json'},'human_projection':{'const':'RESPONSIBILITY.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    observation=obj({'responsibility':ref,'scope_ref':TEXT,'subject':ref,'evidence':array(obj({'criterion_ref':TEXT,'binding':ref}),0)})
    dump(PACKAGE/'schema.json',contract); dump(PACKAGE/'observation.schema.json',observation)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/x) for x in ['schema.json','observation.schema.json']]})
    subject=PREVIOUS/'artifact-types/authority-claim/v1/artifact.json'
    example={'schema_version':'cal-responsibility-record/v1','artifact_type_ref':'cal.artifact-type.responsibility/v1','responsibility_id':'EXAMPLE-CANDIDATE-VALIDATION-001','status':'candidate-unadmitted','authority_effect':'none','owner_ref':'role:candidate-maintainer','scope_ref':'scope:example-validation-accountability','profile':'candidate:bound-json-obligation/v1','subject':binding(subject),'obligation':'Maintain reviewable validation evidence for the exact candidate and route failures to its owner.','criteria':[{'criterion_id':'validation-passed','description':'The supplied validation record reports PASS.','field':'result','expected':'PASS'},{'criterion_id':'no-authority-effect','description':'The supplied validation record declares no authority effect.','field':'authority_effect','expected':'none'}],'review_route':'route:candidate-owner-review','escalation_route':'route:unresolved-validation','authority_boundary':'The maintainer must route unresolved outcomes; this obligation grants no admission, mutation or execution authority.','source_direction':{'canonical':'responsibility-record.json','human_projection':'RESPONSIBILITY.md','projection_policy':'generated-only'},'claim_ceiling':'Exact evidence-field checks only; owner acceptance, evidence truth and authority remain unproven.'}
    artifact=load(PREVIOUS/'artifact-types/authority-claim/v1/artifact.json'); path=L1/'definitions/responsibility/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.responsibility',artifact_type_ref='cal.artifact-type.responsibility/v1',name='Responsibility',schema_ref='cal.schema.responsibility-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Defines an accountable obligation without implying authority.')
    artifact['classification'].update(semantic_kind='responsibility',lifecycle_posture_ref='candidate:responsibility-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='responsibility-record.json',human_filename='RESPONSIBILITY.md',identity_field='responsibility_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'RESPONSIBILITY-01','statement':'An accountable obligation does not grant the authority to cause its outcome.'},{'rule_id':'RESPONSIBILITY-02','statement':'Evidence-field support is separate from owner acceptance and actual completion.'}]
    artifact['four_facets']={'classification':'Candidate Responsibility distinct from Authority and Authority Claim.','schema':'Owner, bounded obligation, exact subject, criteria and review/escalation routes.','machine_checkable':'Exact responsibility and subject bindings, criterion closure and strict JSON field comparisons.','human_continuation':'Generated RESPONSIBILITY.md explains accountability, evidence and escalation.'}
    artifact['typed_residue']=[{'residue_id':'RESPONSIBILITY-R1','owner_ref':'role:candidate-maintainer','missing':'Authenticated ownership, evidence relevance and truth, actual outcome completion and owner acceptance.','consequence':'Evidence matches support review only; no completion or authority is inferred.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','grant'),('empty-criteria','criteria',[]),('blank-owner','owner_ref',' '),('extra-field','completed',True),('unknown-profile','profile','trust-owner'),('missing-escalation','escalation_route',' '),('missing-boundary','authority_boundary',' ')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['subject']['sha256']='bad'; invalid['bad-digest']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/responsibility-record.json',positive_projection='fixtures/valid/RESPONSIBILITY.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/responsibility-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/RESPONSIBILITY.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/responsibility-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.responsibility','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    record_path=PACKAGE/'fixtures/valid/responsibility-record.json'
    observation={'responsibility':binding(record_path),'scope_ref':example['scope_ref'],'subject':example['subject'],'evidence':[{'criterion_ref':c['criterion_id'],'binding':binding(PREVIOUS/'receipts/validation.json')} for c in example['criteria']]}
    dump(ROOT/'examples/supported.json',observation)
    missing=copy.deepcopy(observation); missing['evidence']=[]; dump(ROOT/'examples/missing.json',missing)
    dump(ROOT/'examples/failing-evidence.json',{'result':'BLOCK','authority_effect':'none','fixture_only':True})
    failed=copy.deepcopy(observation); failed['evidence'][0]['binding']=binding(ROOT/'examples/failing-evidence.json'); dump(ROOT/'examples/unmet.json',failed)
    selected={'semantic.responsibility'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-responsibility/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.responsibility'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold)],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':load(scaffold)['source_refs'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
