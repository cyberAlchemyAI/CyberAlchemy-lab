import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    strings={**array(TEXT),'uniqueItems':True}
    contract=obj({'schema_version':{'const':'cal-policy-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.policy/v1'},'policy_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_ref':TEXT,'scope_ref':TEXT,'subject_ref':TEXT,'profile':{'const':'candidate:contestability-routing/v1'},'challenge_response':TEXT,'valid_challenge_modes':strings,'contradiction_edges':{**array(TEXT,0),'uniqueItems':True},'validation_edges':{**array(TEXT,0),'uniqueItems':True},'owner_route':TEXT,'resolution_gate':TEXT,'blocking_questions':array(obj({'question_id':TEXT,'question':TEXT})),'challenge_residue_route':TEXT,'source_direction':obj({'canonical':{'const':'policy-record.json'},'human_projection':{'const':'POLICY.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    query=obj({'policy_ref':TEXT,'scope_ref':TEXT,'subject_ref':TEXT,'challenge_mode':TEXT,'answers':{'type':'object','additionalProperties':{'type':'boolean'}}})
    dump(PACKAGE/'schema.json',contract); dump(PACKAGE/'challenge.schema.json',query)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/x) for x in ['schema.json','challenge.schema.json']]})
    example={'schema_version':'cal-policy-record/v1','artifact_type_ref':'cal.artifact-type.policy/v1','policy_id':'EXAMPLE-CANDIDATE-CHALLENGE-001','status':'candidate-unadmitted','authority_effect':'none','owner_ref':'role:artifact-owner','scope_ref':'scope:example-candidate-review','subject_ref':'candidate:example-1','profile':'candidate:contestability-routing/v1','challenge_response':'Preserve the challenged record and submit the challenge evidence to its owner.','valid_challenge_modes':['contradict','request-validation'],'contradiction_edges':[],'validation_edges':[],'owner_route':'route:artifact-owner-review','resolution_gate':'gate:owner-challenge-resolution','blocking_questions':[{'question_id':'evidence-attached','question':'Has evidence for the challenge been attached?'},{'question_id':'subject-confirmed','question':'Has the exact challenged subject been confirmed?'}],'challenge_residue_route':'route:unresolved-challenge','source_direction':{'canonical':'policy-record.json','human_projection':'POLICY.md','projection_policy':'generated-only'},'claim_ceiling':'Candidate routing preview from supplied answers only. No verdict, confidence change, gate completion or authority grant.'}
    challenge={'policy_ref':example['policy_id'],'scope_ref':example['scope_ref'],'subject_ref':example['subject_ref'],'challenge_mode':'contradict','answers':{'evidence-attached':True,'subject-confirmed':True}}
    dump(ROOT/'examples/ready.json',challenge)
    missing=copy.deepcopy(challenge); missing['answers']={}; dump(ROOT/'examples/missing.json',missing)
    blocked=copy.deepcopy(challenge); blocked['answers']['evidence-attached']=False; dump(ROOT/'examples/blocked.json',blocked)
    artifact=load(PREVIOUS/'artifact-types/architecture-pattern/v1/artifact.json'); path=L1/'definitions/contestability-policy/v1/definition.json'; definition=load(path)
    bound={**binding(path),'definition_ref':definition['definition_id']+'@'+definition['version'],'admission_posture':'candidate-unadmitted'}
    artifact.update(artifact_type_id='cal.artifact-type.policy',artifact_type_ref='cal.artifact-type.policy/v1',name='Policy',schema_ref='cal.schema.policy-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[bound['definition_ref']],semantic_definition_bindings=[bound],distinct_validation_purpose='Defines scoped decision or behavior constraints through an exact policy profile.')
    artifact['classification'].update(semantic_kind='policy',lifecycle_posture_ref='candidate:policy-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='policy-record.json',human_filename='POLICY.md',identity_field='policy_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'POLICY-01','statement':'A challenge response and route are not a verdict or a completed resolution gate.'},{'rule_id':'POLICY-02','statement':'Object confidence and residue remain separate from the challenge contract.'}]
    artifact['four_facets']={'classification':'Policy supporting target from accepted normalization; Contestability Policy is the concrete source example.','schema':'Exact contestability profile with modes, links, owner route, gate, questions and residue route.','machine_checkable':'Scope and subject matching, unique question identities, admissible modes and three-state answer evaluation.','human_continuation':'Generated POLICY.md explains the challenge response and unresolved issue route.'}
    artifact['typed_residue']=[{'residue_id':'POLICY-R1','owner_ref':'role:artifact-owner','missing':'Authenticated evidence, actual route execution, resolved links and gate completion.','consequence':'Supplied answers produce a routing preview only; other policy profiles remain unsupported.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','permit'),('empty-modes','valid_challenge_modes',[]),('empty-questions','blocking_questions',[]),('blank-owner','owner_ref',' '),('confidence-field','evidence_confidence',1),('unknown-profile','profile','allow-all'),('missing-route','challenge_residue_route',' ')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['resolution_gate']=' '; invalid['missing-gate']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/policy-record.json',positive_projection='fixtures/valid/POLICY.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/policy-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/POLICY.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/policy-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.policy','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    selected={'semantic.contestability-policy'}; edges=load(L1/'batches.json')['edges']
    while True:
        expanded=selected|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in selected}
        if expanded==selected: break
        selected=expanded
    registry={x['target_id']:x for x in load(L1/'registry.json')['entries']}; scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-policy/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':['semantic.contestability-policy'],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold),binding(LAB/'docs/normalizations/0001-definition-migration-model/normalization.json')],'definitions':[{'target_id':x,**binding(LAB/registry[x]['path'])} for x in sorted(selected)],'selected_source_sections':[],'normalization_target':load(scaffold)['normalized_contract'],'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in selected]})
if __name__=='__main__': build()
