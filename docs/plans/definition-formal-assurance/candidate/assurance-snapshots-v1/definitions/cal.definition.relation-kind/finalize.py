"""Seal partial Kind semantics and read-only selected actual carrier evidence."""
import json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def audit():
    context=load('context.json');b.unchanged(context['sources'])
    prior=json.loads((b.BASE/'definitions/cal.definition.typed-relation/delivery-manifest.json').read_bytes());b.unchanged(prior['files'])
    if len(prior['files'])!=1241:raise ValueError('Wrong sealed predecessor count')
    for name in ['A04','C01','E02']:
        rec=json.loads((b.BASE/f'units/{name}/receipt.json').read_bytes());b.unchanged(rec['inputs']+rec['outputs'])
    counts=load('denominator.json')
    if counts!={'source_units':21,'mapped_clauses':43,'encoded_clauses':27,'explanatory_clauses':6,'deferred_clauses':10,'declarations':33,'required_populations':8,'unresolved_populations':16,'direct_semantic_uses':6,'countermodel_queries':9}:raise ValueError('Wrong source/type/population denominator')
    core=load('t.json')['payload'];packet=load('correspondence.json');model=load('model-controls.json');profile=load('pair-profile-checks.json');inventory=load('current-inventory.json')
    if model['control_count']!=38 or len(model['nonentailment_countermodels'])!=9 or len(packet['source_precedence']['conflicts'])!=6:raise ValueError('Wrong controls/targets/findings')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or accepted fidelity')
    if load('contract-stdout.txt')['status']!='structurally-valid':raise ValueError('Declared input contract failed')
    if (profile['profile_controls'],profile['rejected_profile_controls'],profile['selected_registry_kind_count'],len(profile['actual_member_of_controls']))!=(16,12,41,7):raise ValueError('Wrong profile/actual-catalog denominator')
    if (profile['actual_member_of_pair_count'],profile['actual_member_of_cartesian_pair_count'],len(profile['actual_member_of_cartesian_extra_pairs']))!=(24,207,183):raise ValueError('Pair declaration conflated with Cartesian product')
    for key in ['source_profile_embedding_reviewed','semantic_question_orthogonality_proved','natural_language_question_equivalence_decided','unbounded_finiteness_proved','actual_owner_principal_authenticated']:
        if profile[key] is not False:raise ValueError('Actual shape/catalog claims overpromoted: '+key)
    if profile['new_kind_or_relation_instances_created']!=0:raise ValueError('Unexpected source/admission instance mutation')
    b.unchanged(list(profile['selected_inputs'].values())+profile['selected_kind_refs'])
    graph=load('dependency-graph.json');global_graph=load('current-dependency-graph.json')
    if (len(graph['nodes']),len(graph['edges']),len(graph['missing_or_quarantined_interpretations']))!=(17,25,13):raise ValueError('Wrong root closure denominator')
    if len(graph['cycle_reviews'])!=1 or len(graph['cycle_reviews'][0]['members'])!=4 or graph['cycle_reviews'][0]['disposition']!='unresolved-cycle-classification':raise ValueError('Joint semantic component falsely resolved')
    if (len(global_graph['nodes']),len(global_graph['edges']),len(global_graph['missing_or_quarantined_interpretations']),len(global_graph['cycle_reviews']))!=(37,71,27,3):raise ValueError('Wrong current joint graph')
    for g in [graph,global_graph]:
        if g['edge_denominator']!='requires-independent-review' or any(x['disposition']!='unresolved-cycle-classification' for x in g['cycle_reviews']):raise ValueError('Closure/cycle review invented')
    if inventory['partial_drafts']!=10 or len(inventory['missing_current_drafts'])!=173 or inventory['counts']!={'source_units':222,'mapped_clauses':357,'encoded_clauses':113,'explanatory_clauses':81,'deferred_clauses':163,'required_populations':89,'unresolved_populations':123}:raise ValueError('Wrong current inventory')
    if inventory['source_owner_accepted_whole_translations']!=0 or inventory['whole_definition_proofs']!=0:raise ValueError('Whole acceptance fabricated')
    for evidence in [model,profile,inventory]:
        b.unchanged(evidence['checker_bindings']+evidence.get('input_refs',[]))
        if evidence['runtime_bindings']!=v.f.current_bindings():raise ValueError('Checker runtime drift')
        if evidence['semantic_ready'] is not False or evidence['mechanized_proof'] is not False or evidence['source_fidelity']!='pending':raise ValueError('Proof/readiness/fidelity overclaim')
    source=load('source-checks.json');b.unchanged(list(source['selected_inputs'].values()))
    if len(source['checks'])!=9 or not all(x['result'] is True for x in source['checks']) or source['current_registry_entry_lifecycle']!='admitted':raise ValueError('Actual selected source checks failed')
    fresh=load('fresh-command-results.json')
    if len(fresh)!=6 or any(x['exit_code']!=0 or (b.UNIT/x['stderr']).read_bytes() for x in fresh):raise ValueError('Fresh commands incomplete')
    for stem in ['build','model','source','profile','dependency','inventory']:
        if (b.UNIT/(stem+'-stderr.txt')).read_bytes():raise ValueError('Unresolved execution error: '+stem)
    for stem,evidence,key in [('fresh-model',model,'result'),('fresh-source',source,'result'),('fresh-profile',profile,'status'),('fresh-inventory',inventory,'result')]:
        if load(stem+'-stdout.txt')[key]!=evidence['status']:raise ValueError('Fresh replay differs: '+stem)
    if load('fresh-profile-stdout.txt')['profile_controls']!=16 or load('fresh-dependency-stdout.txt')['result']!='PASS-for-exact-authored-and-transitive-uses':raise ValueError('Final profile/dependency replay missing')
    if not (b.UNIT/'REVIEW.md').is_file():raise ValueError('Complete aspect review missing')
    selected=b.r.verify(b.snapshot(),b.ROOT)
    if selected['files']!=201:raise ValueError('Wrong captured source-file denominator')
    return context,core,packet,counts,selected
def main():
    context,core,packet,counts,selected=audit();profile=load('pair-profile-checks.json')
    b.put('episode-status.json',{'authority_effect':'none','goal_status':'active','latest_candidate_draft':'F07-T.cal.definition.relation-kind','current_definitions':183,'admitted_source_versions':189,
          'per_definition_T_candidate_drafts':10,'remaining_current_identities_without_per_definition_T_draft':173,'foundations_family_result':'PARTIAL','typed_relations_family_result':'PARTIAL',
          'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'source_files_current':201,'prior_candidate_files_preserved':1241,
          'selected_actual_relation_kind_carriers':41,'next_definition_priority':'F04-T.cal.definition.artifact-type','independently_ready_workflow_rehearsal':'I05.1',
          'reporting_compatibility':'I04 eight-draft selected report remains valid; evolving current draft counts need a scoped report update.','current_inventory_ref':b.ref(b.UNIT/'current-inventory.json'),'full_project_completion':'not-established'})
    b.put('coverage-row.json',{'authority_effect':'none','definition_id':core['source']['definition_id'],'source':core['source'],'interpretation_ref':b.ref(b.UNIT/'t.json'),
          'correspondence_ref':b.ref(b.UNIT/'correspondence.json'),'static_ir_ref':b.ref(b.UNIT/'static-ir.json'),'review_ref':b.ref(b.UNIT/'REVIEW.md'),
          'model_evidence_ref':b.ref(b.UNIT/'model-controls.json'),'source_checks_ref':b.ref(b.UNIT/'source-checks.json'),'pair_profile_ref':b.ref(b.UNIT/'pair-profile-checks.json'),
          'dependency_graph_ref':b.ref(b.UNIT/'dependency-graph.json'),**counts,'character_accounting_complete':True,
          'logical_status':'typed-partial-versioned-question-closed-ordered-pairs-and-pair-rule-association','source_fidelity':'pending','semantic_ready':False,
          'whole_definition_translation':'pending','whole_definition_proof':None,'semantic_closure':'unresolved-13-counterparts-and-four-definition-component',
          'source_profile_embedding_reviewed':False,'unbounded_finiteness_or_question_orthogonality':'not-established',
          'owner_review':{'status':'pending','source_owner_ref':'role:definition-owner','owner_principal_ref':None,'decision_ref':None,'findings':[x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs=[b.ref(p) for p in sorted(b.UNIT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    inputs={x['path']:x for x in context['sources']+list(profile['selected_inputs'].values())+profile['selected_kind_refs']}
    b.put('receipt.json',{'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'F07-T.cal.definition.relation-kind','authority_effect':'none','goal_status':'active',
          'task_result':'PARTIAL: exact source-accounted Kind question/pair/rule slice, authored countermodels, bounded profiles and selected actual41 carrier checks verified; whole fidelity, actual semantic question/finiteness proofs and closure unresolved',
          'inputs':sorted(inputs.values(),key=lambda x:x['path']),'outputs':outputs,
          'validation':{**counts,'model_controls':38,'synthetic_profile_controls':16,'rejected_profile_controls':12,'actual_kind_carrier_checks':41,'actual_member_of_pair_qualifier_controls':7,'actual_bounded_source_checks':9,
                        'source_files_current':201,'prior_candidate_files_preserved':1241,'fresh_contract_model_source_profile_dependency_inventory_replays':'PASS'},
          'criterion_results':[{'criterion':'Exact source account, signature, assumptions and populations','result':'PARTIAL','evidence':'21 units;43 spans;27 encoded,6 explanatory,10 deferred;33 declarations;8 required,16 unresolved populations; no selected assumptions or owner fidelity.'},
           {'criterion':'One question, ordered pairs and pair-specific rules','result':'PASS for selected authored models and bounded profiles','evidence':'38 denotation controls,9 targets outside T,16 synthetic profile controls; successors may share questions; no marginal Cartesian inference or cross-pair qualifier transfer.'},
           {'criterion':'Actual current Kind carrier/schema and selected declaration closure','result':'PASS for selected exact bytes','evidence':'41 hash-bound/schema-valid carriers,41 declared axes/question strings and550 scoped pair entries; member-of24pairs versus207summary combinations;7 actual pair/qualifier controls.'},
           {'criterion':'Meaning, finiteness, populations, admission and semantic closure','result':'PARTIAL','evidence':'No semantic question equivalence/orthogonality or unbounded finiteness proof. Root17nodes/25edges/13missing with4-member unclassified component; shared qualifier-carrier embedding and endpoint mappings unreviewed.'},
           {'criterion':'Current episode inventory and preservation','result':'PARTIAL','evidence':'10 partial drafts,173 missing;113encoded/163deferred clauses;27missing joint counterparts and3unclassified components;0whole accepted translations/proofs.201captured sources and1241previous candidate files preserved.'}],
          'preserved_attempts':[{'path':'attempt-001-before-family-wildcard-control','result':'superseded-unsealed-profile','cause':'Added wildcard-family syntax rejection and matching16th control; preceding15-control profile/code/logs retained.'}],
          'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Exact partial evidence only; source-owner fidelity, source-profile embedding, unbounded/semantic proofs, actual principal authentication and whole assurance pending.'},
          'source_binding_check':selected,'coverage_row_ref':b.ref(b.UNIT/'coverage-row.json'),'current_inventory_ref':b.ref(b.UNIT/'current-inventory.json'),
          'source_fidelity':'pending','semantic_ready':False,'whole_definition_translation':'pending','mechanized_proof':False,'next_definition_priority':'F04-T.cal.definition.artifact-type','full_project_completion':'not-established'})
    files=[b.ref(p) for folder in [b.BASE,b.IMPL] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    b.put('delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda x:x['path']),
          'claim_ceiling':'Exact preserved bytes, partial Relation Kind theory and bounded/selected actual carrier checks plus ten-draft inventory. No owner fidelity, unbounded finiteness, semantic question orthogonality, full carrier embedding/alignment, principal authentication, whole Definition proof or episode completion.'})
    print(json.dumps({'result':'PARTIAL-DRAFT-VERIFIED','candidate_files':len(files),'prior_candidate_files_preserved':1241,'source_files_current':201,
                      'partial_drafts':10,'missing_current_drafts':173,'model_controls':38,'nonentailment_queries':9,'synthetic_profile_controls':16,'actual_kind_carriers_checked':41,
                      'whole_definition_proofs':0,'goal_status':'active','next_definition_priority':'F04-T.cal.definition.artifact-type'},indent=2,sort_keys=True))
if __name__=='__main__':main()
