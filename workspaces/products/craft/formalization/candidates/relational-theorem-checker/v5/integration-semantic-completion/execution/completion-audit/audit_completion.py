"""Audit every successor-plan item without promoting preparation to completion."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, subprocess

HERE=Path(__file__).resolve().parent
H=HERE.parents[1]
ROOT=H.parents[5]
N=H/'execution/n01'
BASE=H.parents[1]
def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def check_bindings(value):
    if isinstance(value,dict):
        if {'path','sha256'}<=value.keys():
            assert binding(ROOT/value['path'])=={k:value[k] for k in ['path','sha256']}
        for child in value.values():check_bindings(child)
    elif isinstance(value,list):
        for child in value:check_bindings(child)

def run():
    plan_path=H/'execution/plan.json'
    plan=read(plan_path);check_bindings(plan)
    seq=read(N/'sequential-review.json');check_bindings(seq)
    gate=read(N/'decision-gate.json');check_bindings(gate)
    inventory=read(ROOT/plan['source_obligation_inventory']['path']);check_bindings(inventory)
    index=read(N/'formal-preparation-index.json');check_bindings(index)
    current=read(N/'review-state-validation.json');check_bindings(current)
    assert current['result']=='current-review-binding-audit-pass'
    assert current['execution_plan']==binding(plan_path)
    assert current['sequential_review']==binding(N/'sequential-review.json')
    registry_path=BASE/'v1/registry/normalized-registry.json'
    registry=read(registry_path)
    assert registry['kind_count']==41 and registry['ordered_pair_count']==550 and len(registry['node_kinds'])==109
    assert len(plan['tasks'])==20 and sum(len(t['depends_on']) for t in plan['tasks'])==52
    assert len(inventory['obligations'])==inventory['total_pending']==263
    assert inventory['retained_discharged_count']==90
    categories=Counter(row['category'] for row in inventory['obligations'])
    assert dict(categories)==inventory['counts']=={'qualifier-meaning':74,'operational-effect':41,'forbidden-inference':148}
    assert all(row['proposed_status']=='not-started' and not row['discharge_evidence'] for row in inventory['obligations'])
    assert current['candidate_fragment_theorems']==index['total_distinct_new_candidate_theorems']==1984
    assert current['inherited_discharges']==seq['new_inherited_discharges']==0
    accepted={t['id'] for t in plan['tasks'] if t['status']=='accepted'}
    assert accepted=={'N00'}
    assert seq['accepted_meaning_count']==4 and seq['current_unit']==gate['current_unit']=='K04'
    request=read(N/'K04-assessment-request.json');assert request['actual_response'] is None
    pending_meanings=[u for u in seq['units'] if not u.get('actual_assessment')]
    assert len(pending_meanings)==37 and all(v is None for v in seq['global_policy_assessments'].values())
    supporting_path=N/'formal/K02-supporting-sources/verification.json'
    supporting=read(supporting_path);check_bindings(supporting)
    assert supporting['result']=='candidate-fragment-pass' and supporting['profile_count']==8
    assert not supporting['all_original_payload_roles_supported']
    gaps_path=N/'formal/K02-supporting-sources/source-role-gap-map.json'
    gaps=read(gaps_path);check_bindings(gaps)

    # References are not instances. Check every authority JSON file containing
    # these tokens for exact identity-field values; do not infer a source kind.
    tokens=['test:all-definitions-realized','test:all-relations-closed','runtime:unapproved-cutover']
    schemas=sorted((ROOT/'authority/artifact-types').rglob('schema.json'))
    artifact_files=sorted((ROOT/'authority/artifact-types').rglob('artifact.json'))
    identity_fields={'node_id','goal_id','test_id','runtime_id'}
    for path in artifact_files:
        artifact=read(path);field=artifact.get('instance_contract',{}).get('identity_field')
        if isinstance(field,str):identity_fields.add(field)
    argv=['rg','-l','--fixed-strings','--glob','*.json']
    for token in tokens:argv+=['-e',token]
    result=subprocess.run(argv+['authority'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode in [0,1] and not result.stderr
    hit_files=[ROOT/name for name in result.stdout.splitlines()]
    found={token:[] for token in tokens}
    def inspect(value,path,location):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in identity_fields and isinstance(child,str) and child in found:
                    found[child].append({'file':binding(path),'json_path':location+[key]})
                inspect(child,path,location+[key])
        elif isinstance(value,list):
            for i,child in enumerate(value):inspect(child,path,location+[i])
    for path in hit_files:inspect(read(path),path,[])
    schema_inventory=[binding(path) for path in schemas]
    save=lambda name,value:(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
    source_scan={'result':'exact-reference-versus-identity-scan-complete',
                 'method':'rg exact token hits, then JSON identity fields from existing instance contracts; identity matches would still not establish authenticity or admission.',
                 'searched_root':'authority','tokens':tokens,'identity_fields':sorted(identity_fields),
                 'matched_files':[binding(path) for path in hit_files],
                 'identity_matches':found,'schema_inventory':schema_inventory,
                 'schema_file_count':len(schemas),'owned_source_mapping_established':False,
                 'authority_effect':'none'}
    save('supporting-source-scan.json',source_scan)
    tasks=[]
    for task in plan['tasks']:
        done=task['id'] in accepted
        receipt=read(ROOT/task['acceptance']['path']) if done else None
        if receipt:
            check_bindings(receipt)
            assert receipt['result']=='accepted' and {c['source'] for c in receipt['criteria']}==set(task['exit_criteria'])
        unmet=[dep for dep in task['depends_on'] if dep not in accepted]
        status='supported-by-current-scoped-task-acceptance' if done else 'completion-not-established'
        tasks.append({'id':task['id'],'title':task['title'],'declared_status':task['status'],
                      'depends_on':task['depends_on'],'unaccepted_dependencies':unmet,
                      'completion_status':status,
                      'criteria':[{'text':c,'status':status,'evidence':task.get('acceptance'),
                                   'limit':'Preparation elsewhere is not this task/profile acceptance.' if not done else 'Retains the exact N00 scope.'} for c in task['exit_criteria']],
                      'deliverables':[{'name':o,'status':status} for o in task['outputs']],
                      'required_failure_controls':[{'name':c,'status':status} for c in task['failure_controls']],
                      'formalization_before_runtime':task['formalization_before_runtime']})
    original_path=BASE/'v4/gate-closure/execution/closure-completion.json'
    original=binding(original_path)
    assert original['sha256']=='1285904666f64cae5e586eb8a556c6e4e6e1be4aeb5d14af71e3a8c0effbfc04'
    report={'schema':'relational.full-plan-completion-gap-audit/v1',
            'result':'full-plan-incomplete-with-explicit-owner-and-source-gates',
            'captured_at_utc':datetime.now(timezone.utc).isoformat(),'driver':binding(Path(__file__)),
            'plan':binding(plan_path),'source_plan':plan['source_plan'],'review_gate':binding(N/'decision-gate.json'),
            'review_state':binding(N/'sequential-review.json'),'binding_validation':binding(N/'review-state-validation.json'),
            'original_closure':original,'registry':binding(registry_path),
            'obligation_inventory':plan['source_obligation_inventory'],
            'source_scan':binding(HERE/'supporting-source-scan.json'),'supporting_verification':binding(supporting_path),
            'supporting_role_gaps':binding(gaps_path),
            'scope':{'tasks':20,'dependency_edges':52,'relations':41,'ordered_pairs':550,'node_kinds':109,
                     'extensions':['condition expressions','multiple evidence references','redelegation','fulfillment','lifecycle','checked IR','independent checking'],
                     'inherited_pending':263,'inherited_categories':dict(categories),'original_discharges_retained':90},
            'current':{'accepted_tasks':1,'actual_relation_meaning_assessments':4,'unassessed_relations':37,
                       'unassessed_shared_policies':8,'candidate_declarations':1984,'candidate_body_profiles':8,
                       'inherited_discharges':0,'current_review':'K04'},
            'tasks':tasks,
            'mandatory_discharge_inventory':[{'id':row['id'],'category':row['category'],'kind':row['kind'],
                                              'status':'open','discharge_evidence':[]} for row in inventory['obligations']],
            'next_required_actions':[
                {'order':1,'action':'Complete actual sequential K04–K40 and D01–D08 intended-meaning/policy assessments.',
                 'basis':'N01 exit criterion requires actual assigned owners to review choices and policy ambiguity.',
                 'current_pending_request':binding(N/'K04-assessment-request.json')},
                {'order':2,'action':'Bind authentic supporting-role source mappings and complete independent source meanings; retain unresolved owner/admission/evidence slots.'},
                {'order':3,'action':'Complete N01 source refinement and satisfiable meanings across all 41 kinds and 550 pairs, then prove exact N02 obligations and freeze N03 contracts.'},
                {'order':4,'action':'Execute N04–N14 in dependency order, including all seven integrations and both independent-checking milestones.'},
                {'order':5,'action':'Run N15 whole-profile pilot, audit N16 exact 263 discharges plus retained 90, obtain actual N17 successor assessment and publish the N18 local readout.'}],
            'independent_preparation_ceiling':gate['independent_work_allowed'],
            'cannot_infer':['Pending owner decisions from prior version approvals','Owned source kinds from reference prefixes',
                            'Semantic discharges from theorem or fixture counts','Independent checking from same-kernel replay'],
            'goal_complete':False,'plan_or_acceptance_mutated':False,'authority_effect':'none'}
    assert len(report['tasks'])==20 and sum(len(t['criteria']) for t in tasks)==42
    assert len(report['mandatory_discharge_inventory'])==len({r['id'] for r in report['mandatory_discharge_inventory']})==263
    save('completion-gap-audit.json',report)
    lines=['Completion audit of the full successor plan','',
           'The full plan is incomplete. N00 is accepted; N01 is in progress. N02–N18',
           'retain their declared dependencies. The scope remains all seven extensions,',
           '41 relations, 550 endpoint pairs, 109 node kinds and 263 inherited obligations.',
           'The 90 original discharges retain their original scope.','',
           'The audit accounts for every task, all 42 exit criteria, every named deliverable',
           'and every required failure control in completion-gap-audit.json. Existing',
           'candidate preparation is not relabeled acceptance of a dependent task.','',
           '| Task | Current status | Unaccepted dependencies |',
           '|---|---|---|']
    for task in tasks:lines.append('| '+task['id']+' | '+task['declared_status']+' | '+(', '.join(task['unaccepted_dependencies']) or 'none')+' |')
    lines += ['',
              'The 1,984 checked candidate declarations establish useful decoding, catalog,',
              'provenance and conditional semantic facts. They discharge zero of the 263',
              'successor IDs. The outstanding inventory is 74 qualifier meanings, 41 effects',
              'and 148 forbidden-inference claims. Proof closure must bind each exact ID,',
              'its owner-reviewed meaning, the complete applicable theory and current evidence.','',
              'N01 requires actual assigned owners to review choices and policy ambiguity.',
              'Four meanings have actual assessments: K00–K03. K04–K40 and D01–D08 remain',
              'unassessed. K04 is the existing next question. It records actual use or deliberate',
              'non-use of an exact lesson revision in a session, with applicability and precedence',
              'basis and retained conflicts/overrides. The relation alone establishes no compliance,',
              'benefit, authority or method execution. Its assessment does not accept other meanings.','',
              'N02 depends on N01, and N03 depends on N00/N01. Their acceptance and frozen',
              'semantic commitments cannot be supplied by additional candidate helper proofs.',
              'The current review gate permits consistency/source/branch checks and non-accepting',
              'formal model preparation; it holds N01 acceptance, N02 semantic discharges and',
              'N03 frozen contracts. This audit preserves that boundary.','',
              'Eight complete body profiles are implemented: Intent, Assignment, Goal, Product,',
              'Capability, Project, Inquiry and Decision. Decision retains its complete shape, but',
              'actual admission, decision-maker authority and role interpretation remain unresolved.',
              'The satisfaction-test and excluded/unused source families remain missing. The exact',
              'token/identity scan is recorded in supporting-source-scan.json; references are not',
              'owned source instances, and identity matches alone would not prove authentication.','',
              'Formalization comes first after the assessments and actual source mappings are',
              'available: finish all independent meanings/source refinements, prove each inherited',
              'claim, then freeze successor contracts. Execute the catalog, seven integration,',
              'independent-checking and resource tasks in their declared order. The composed',
              'pilot and exact discharge audit must precede the new actual final use assessment.',
              'Earlier R06/G4 and v3 feedback retain their earlier scope.','',
              'No task, assessment, source policy, inherited obligation or publication state was',
              'changed by this completion audit. The full goal remains unachieved.','']
    (HERE/'REVIEW.md').write_text('\n'.join(lines))
    print(json.dumps({'result':report['result'],'tasks':20,'criteria':42,
                      'deliverables':sum(len(t['deliverables']) for t in tasks),
                      'failure_controls':sum(len(t['required_failure_controls']) for t in tasks),
                      'source_schema_files':len(schemas),'source_hit_files':len(hit_files),
                      'source_identity_matches':{k:len(v) for k,v in found.items()},
                      'current_review':'K04','inherited_open':263,'goal_complete':False},indent=2))

if __name__=='__main__':run()
