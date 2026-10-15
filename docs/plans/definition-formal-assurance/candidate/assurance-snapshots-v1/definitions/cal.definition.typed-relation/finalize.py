"""Seal the partial typed relation, bounded profile and current nine-draft inventory."""
import json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def audit():
    context=load('context.json');b.unchanged(context['sources'])
    prior=json.loads((b.BASE/'units/I04/delivery-manifest.json').read_bytes());b.unchanged(prior['files'])
    if len(prior['files'])!=1166:raise ValueError('Wrong sealed predecessor count')
    for name in ['A04','C01','E02']:
        receipt=json.loads((b.BASE/f'units/{name}/receipt.json').read_bytes());b.unchanged(receipt['inputs']+receipt['outputs'])
    expected={'source_units':21,'mapped_clauses':27,'encoded_clauses':7,'explanatory_clauses':6,'deferred_clauses':14,'declarations':41,'required_populations':13,'unresolved_populations':10,'direct_semantic_uses':6,'countermodel_queries':10}
    counts=load('denominator.json')
    if counts!=expected:raise ValueError('Wrong source/type/population denominator')
    core=load('t.json')['payload'];packet=load('correspondence.json');model=load('model-controls.json');profile=load('record-profile-checks.json');inventory=load('current-inventory.json')
    if model['control_count']!=33 or len(model['nonentailment_countermodels'])!=10 or len(packet['source_precedence']['conflicts'])!=6:raise ValueError('Missing controls or findings')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed conclusion or acceptance')
    if load('contract-stdout.txt')['status']!='structurally-valid':raise ValueError('Contract failed')
    if (profile['controls'],profile['rejected_controls'],profile['actual_relations_created'])!=(26,21,0) or any(profile[k] is not False for k in ['source_profile_embedding_reviewed','actual_kind_admission_authenticated','owner_authorized','subject_runtime_executed']):raise ValueError('Wrong profile denominator or actual authority/runtime claim')
    graph=load('dependency-graph.json')
    if (len(graph['nodes']),len(graph['edges']),len(graph['missing_or_quarantined_interpretations']))!=(16,19,13):raise ValueError('Wrong root closure denominator')
    if len(graph['cycle_reviews'])!=1 or len(graph['cycle_reviews'][0]['members'])!=3 or graph['cycle_reviews'][0]['disposition']!='unresolved-cycle-classification' or graph['edge_denominator']!='requires-independent-review':raise ValueError('Cycle or dependency review simulated')
    global_graph=load('current-dependency-graph.json')
    if (len(global_graph['nodes']),len(global_graph['edges']),len(global_graph['missing_or_quarantined_interpretations']),len(global_graph['cycle_reviews']))!=(36,65,27,3):raise ValueError('Wrong current joint graph')
    if inventory['partial_drafts']!=9 or len(inventory['missing_current_drafts'])!=174 or inventory['counts']!={'source_units':201,'mapped_clauses':314,'encoded_clauses':86,'explanatory_clauses':75,'deferred_clauses':153,'required_populations':81,'unresolved_populations':107}:raise ValueError('Wrong current draft count')
    if inventory['source_owner_accepted_whole_translations']!=0 or inventory['whole_definition_proofs']!=0:raise ValueError('Whole acceptance invented')
    for evidence in [model,profile,inventory]:
        b.unchanged(evidence['checker_bindings']+evidence.get('input_refs',[]))
        if evidence['runtime_bindings']!=v.f.current_bindings():raise ValueError('Runtime drift')
        if evidence['semantic_ready'] is not False or evidence['mechanized_proof'] is not False or evidence['source_fidelity']!='pending':raise ValueError('Fidelity/readiness/proof fabricated')
    source=load('source-checks.json');b.unchanged(list(source['selected_inputs'].values()))
    if len(source['checks'])!=9 or not all(x['result'] is True for x in source['checks']) or source['current_registry_entry_lifecycle']!='admitted':raise ValueError('Selected actual source checks failed')
    fresh=load('fresh-command-results.json')
    if len(fresh)!=6 or any(x['exit_code']!=0 or (b.UNIT/x['stderr']).read_bytes() for x in fresh):raise ValueError('Fresh execution failed')
    for stem in ['build','model','source','profile','dependency','inventory']:
        if (b.UNIT/(stem+'-stderr.txt')).read_bytes():raise ValueError('Unresolved execution error: '+stem)
    for stem,evidence,statuskey in [('fresh-model',model,'result'),('fresh-source',source,'result'),('fresh-profile',profile,'status'),('fresh-inventory',inventory,'result')]:
        if load(stem+'-stdout.txt')[statuskey]!=evidence['status']:raise ValueError('Fresh result differs: '+stem)
    if load('fresh-dependency-stdout.txt')['result']!='PASS-for-exact-authored-and-transitive-uses':raise ValueError('Fresh dependency replay failed')
    if not (b.UNIT/'REVIEW.md').is_file():raise ValueError('Aspect review missing')
    selected=b.r.verify(b.snapshot(),b.ROOT)
    if selected['files']!=201:raise ValueError('Source-file denominator changed')
    return context,core,packet,counts,selected
def main():
    context,core,packet,counts,selected=audit()
    b.put('episode-status.json',{'authority_effect':'none','goal_status':'active','latest_candidate_draft':'F07-T.cal.definition.typed-relation',
          'current_definitions':183,'admitted_source_versions':189,'per_definition_T_candidate_drafts':9,'remaining_current_identities_without_per_definition_T_draft':174,
          'foundations_family_result':'PARTIAL','typed_relations_family_result':'PARTIAL','source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,
          'source_files_current':201,'prior_candidate_files_preserved':1166,'next_definition_priority':'F07-T.cal.definition.relation-kind',
          'independently_ready_workflow_rehearsal':'I05.1','reporting_compatibility':'I04 selected eight-draft inventory remains valid; evolving draft counts need a scoped report update.',
          'current_inventory_ref':b.ref(b.UNIT/'current-inventory.json'),'full_project_completion':'not-established'})
    b.put('coverage-row.json',{'authority_effect':'none','definition_id':core['source']['definition_id'],'source':core['source'],
          'interpretation_ref':b.ref(b.UNIT/'t.json'),'correspondence_ref':b.ref(b.UNIT/'correspondence.json'),'static_ir_ref':b.ref(b.UNIT/'static-ir.json'),
          'review_ref':b.ref(b.UNIT/'REVIEW.md'),'model_evidence_ref':b.ref(b.UNIT/'model-controls.json'),'source_checks_ref':b.ref(b.UNIT/'source-checks.json'),
          'record_profile_ref':b.ref(b.UNIT/'record-profile-checks.json'),'dependency_graph_ref':b.ref(b.UNIT/'dependency-graph.json'),**counts,
          'character_accounting_complete':True,'logical_status':'typed-partial-connection-identity-ordered-endpoints-and-declared-metadata',
          'source_fidelity':'pending','semantic_ready':False,'whole_definition_translation':'pending','whole_definition_proof':None,'semantic_closure':'unresolved-13-counterparts-and-three-definition-component',
          'source_profile_embedding_reviewed':False,'actual_kind_admission_authenticated':False,
          'owner_review':{'status':'pending','source_owner_ref':'role:definition-owner','owner_principal_ref':None,'decision_ref':None,'findings':[x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs=[b.ref(p) for p in sorted(b.UNIT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    b.put('receipt.json',{'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'F07-T.cal.definition.typed-relation','authority_effect':'none','goal_status':'active',
          'task_result':'PARTIAL: exact source-accounted typed connection slice, authored countermodels, bounded ordered-pair/qualifier inspector and nine-draft inventory verified; whole fidelity, live kind/owner contracts and closure unresolved',
          'inputs':context['sources'],'outputs':outputs,'validation':{**counts,'model_controls':33,'record_profile_controls':26,'rejected_record_profile_inputs':21,'actual_bounded_source_checks':9,'source_files_current':201,'prior_candidate_files_preserved':1166,'fresh_contract_model_source_profile_dependency_inventory_replays':'PASS'},
          'criterion_results':[{'criterion':'Exact source clauses and typed signature','result':'PARTIAL','evidence':'21 units;27 spans;7 encoded,6 explanatory,14 deferred;41 declarations; owner fidelity pending.'},
           {'criterion':'Identity, ordered pairs, qualifiers and actual-effects distinction','result':'PASS for selected authored models/profile','evidence':'33 denotation controls,10 targets outside T,26 closed-profile controls; independent connection IDs, self-links and reverse-pair distinctions retained.'},
           {'criterion':'Semantic closure, owner/evidence/lifecycle contracts and cycle safety','result':'PARTIAL','evidence':'Root graph16/19/13missing with one unclassified3-member component; ordinary directed cycle acceptance supplies no constraint-cycle safety proof.'},
           {'criterion':'Currentness and actual source/schema/projection','result':'PASS for exact selected artifacts','evidence':'Nine schema/render/lookup checks,201 captured sources and1166 preceding candidate files rechecked; existing source admission does not admit interpretation/instance.'},
           {'criterion':'Current episode inventory','result':'PARTIAL','evidence':'9 partial drafts,174 missing;86 encoded clauses,153 deferred;27 missing joint counterparts,3 unclassified components;0 whole accepted translations/proofs.'}],
          'preserved_attempts':[{'path':'attempt-001-before-nonentailment-span-split','result':'superseded-unsealed-translation'}, {'path':'attempt-002-outside-root-closure','result':'superseded-failed-dependency-selection'}, {'path':'attempt-003-inventory-result-field','result':'superseded-failed-checker-field-assumption'}],
          'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Exact partial evidence only; owner fidelity, source-profile embedding, live admission/contracts and whole assurance pending.'},
          'source_binding_check':selected,'coverage_row_ref':b.ref(b.UNIT/'coverage-row.json'),'current_inventory_ref':b.ref(b.UNIT/'current-inventory.json'),
          'source_fidelity':'pending','semantic_ready':False,'whole_definition_translation':'pending','mechanized_proof':False,
          'next_definition_priority':'F07-T.cal.definition.relation-kind','full_project_completion':'not-established'})
    files=[b.ref(p) for folder in [b.BASE,b.IMPL] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    b.put('delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda x:x['path']),
          'claim_ceiling':'Exact preserved bytes, partial Typed Relation and bounded synthetic record/profile checks plus current nine-draft inventory. No accepted fidelity, actual Kind/instance/owner admission, cycle-safety proof, shared-meaning consistency, whole definition proof or episode completion.'})
    print(json.dumps({'result':'PARTIAL-DRAFT-VERIFIED','candidate_files':len(files),'prior_candidate_files_preserved':1166,'source_files_current':201,
                      'partial_drafts':9,'missing_current_drafts':174,'model_controls':33,'nonentailment_queries':10,'record_profile_controls':26,
                      'whole_definition_proofs':0,'goal_status':'active','next_definition_priority':'F07-T.cal.definition.relation-kind'},indent=2,sort_keys=True))
if __name__=='__main__':main()
