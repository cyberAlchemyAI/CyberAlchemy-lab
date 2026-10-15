"""Freeze exact W07 full-case evidence and independently signed gap closure."""
import ast
import re
import time
from successor import *

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
OBS=PACKAGE/'receipts/integration/W07/0004'


def run():
    start=time.perf_counter();files={};validation=[]
    def capture(b):
        raw=bound(b);require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting proof source')
        files[b['path']]=b['sha256'];return parse(raw) if b['path'].endswith('.json') else raw
    def check(name,value):
        require(value,name);validation.append({'test':name,'result':'PASS'})
    selected=selection();context=capture(binding(RUN/'context-W07-signed-integration.json'))
    for b in context['source_bindings']:
        value=capture({'path':b['path'],'sha256':b['sha256']})
        if isinstance(value,dict):
            for source in value.get('files',[]):capture({'path':source['path'],'sha256':source['sha256']})
    predecessor=capture(selected['parent_workflow_proof_binding'])
    check('all original completed representative workflow checks retained',predecessor['tests']==263 and len(predecessor['checks'])==263
        and all(c['result']=='PASS' for c in predecessor['checks']) and not predecessor['task_complete'])
    check('all exact original upstream construction evidence current',len(parent.verify_upstream())>0)
    def tests(code,log,count):
        declared={n.name for n in ast.walk(ast.parse(code.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
        text=log.read_text();observed=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',text,re.M)
        check(str(log.relative_to(OBS))+': actual complete terminal suite',len(declared)==len(observed)==count and {n for n,_ in observed}==declared
            and re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\n\nOK\s*$',text) is not None)
        return [{'test':full,'result':'PASS'} for name,full in observed]
    original=tests(HERE.parent/'test_integration.py',OBS/'parent-joining-tests.stderr',28)
    strict=tests(HERE/'test_successor.py',OBS/'final/successor-tests.stderr',39)
    check('original joining suite identities preserved',{c['test'] for c in original}=={c['test'] for c in predecessor['checks'] if c['test'].startswith('test_integration.')})
    joined=capture(binding(OBS/'final/signed-join.json'));cold=parse((OBS/'final/cold.stdout').read_bytes())
    capture(binding(OBS/'final/cold.stdout'))
    check('complete selected four-domain model join',joined['result']=='PASS' and joined['candidate_model_integration_result']=='PASS'
        and joined['domain_case_count']==4 and joined['typed_connections_checked']==70 and joined['remaining_runtime_gaps']==0
        and joined['original_join_result']=='FLAG' and len(joined['signed_gap_closures'])==2)
    cases=original_cases(selected);audit=parent.audit_join(cases)
    check('all exact original workflows independently recomputed without redispatch',audit==joined['original_join'] and audit['evidence_coverage']=='PASS')
    for c in cases:
        check(c['domain']+': independent original authority and six status axes',c['actual_owner_outcome'] is None and c['authority_effect']=='none'
            and c['canonical_effects_applied']==0 and c['status_axes']['admission']=='candidate-unadmitted' and len(c['status_axes'])==6)
    for closure,row in zip(joined['signed_gap_closures'],selected['signed_coupling_witnesses']):
        check(closure['domain']+': exact signed witness scope and separate decisions',closure['result']=='PASS' and closure['signed_archive_binding']==row['archive_binding']
            and len(set(closure['independent_decision_refs']))==3 and not closure['original_records_rewritten']
            and closure['original_domain_effects_reexecuted']==0 and closure['canonical_effects_applied']==0 and closure['actual_owner_outcome'] is None
            and not closure['unqualified_global_merge'] and closure['original_case_admission']=='candidate-unadmitted'
            and closure['signed_witness_admission']=='local-admitted-current')
        project=next(v for v in closure['endpoint_views'] if v['version_ref']==closure['endpoint_ref'])
        check(closure['domain']+': raw carrier, represented endpoint and declared Project namespace preserved',project['carrier_kind']=='project-identity'
            and project['source_projection_kind']=='project-identity' and project['represented_endpoint_kind']=='project'
            and not project['raw_subject_rewritten'] and project['record_scope_basis']['field']=='project_id'
            and project['record_scope_basis']['value']==closure['signed_scope_ref'])
    native=capture(binding(OBS/'native-rebuild-result.json'))
    check('original native executable exactly reproduced',native['result']=='PASS' and native['source_files_changed']==0
        and native['expected_executable_sha256']==native['observed_executable_sha256']==cold['native_executable_sha256'])
    native_path=Path(native['executable_path']);check('observed native executable remains exact',byte_sha(native_path.read_bytes())==cold['native_executable_sha256'])
    check('fresh cold signed source and Lesson/Agent reconstruction',cold['result']=='PASS' and cold['warm_join_sha256']==binding(OBS/'final/signed-join.json')['sha256']
        and cold['selection_sha256']==SELECTION_SHA and cold['typed_connections_checked']==70 and cold['remaining_runtime_gaps']==0
        and cold['signed_coupling_archives_replayed']==2 and cold['new_Agent_created_from_verified_state']
        and cold['signed_lesson_cold_context']['signed_original_branch_replayed'] and cold['signed_lesson_cold_context']['new_Agent_lesson_context']
        and cold['original_domain_effects_reexecuted']==0 and not cold['keys_restored'] and not cold['Session_memory_restored']
        and cold['canonical_effects_applied']==0 and cold['actual_owner_outcome'] is None and not cold['global_merge_performed'])
    terminals=capture(binding(OBS/'terminal-observations.json'))
    check('actual observed process completion and failed history retained',terminals['exit_codes']=={'native-build':0,'initial-successor-tests':1,
        'original-joining-tests':0,'scope-revised-successor-tests':1,'scope-revised-warm-join':0,'final-successor-tests':0,'final-warm-join':0,'final-cold':0})
    check('cold terminal stderr empty',(OBS/'final/cold.stderr').read_bytes()==b'')
    manifest=capture(binding(OBS/'manifest.json'))
    for b in manifest['files']:capture(b)
    for p in OBS.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:capture(binding(p))
    review=capture(binding(HERE/'review-members.json'))
    check('exact integration verifier review membership and owner boundary retained',len(review['members'])==2 and review['actual_owner_outcome'] is None
        and review['authority_effect']=='none' and review['complete_final_package'] is False)
    for member in review['members']:
        for b in member['bindings']:capture(b)
        check(member['member_ref']+': no fabricated owner effect',member['actual_owner_outcome'] is None and member['admission_posture']=='candidate-unadmitted')
    checks=predecessor['checks']+strict
    receipt={'schema_version':'lab-W07-signed-integration-evidence/v1-candidate','task':'W07','result':'PASS','task_complete':True,
        'model_integration_result':'PASS','tests':len(checks),'checks':checks,'fresh_original_joining_tests':28,'fresh_successor_tests':39,
        'original_checks_retained':263,'validation_checks':validation,'source_drift':[],'authority_effect':'none','actual_owner_outcome':None,
        'canonical_effects_applied':0,'global_merge_performed':False,'original_domain_effects_reexecuted':0,
        'files':[{'path':path,'sha256':sha} for path,sha in sorted(files.items())],'source_bindings':context['source_bindings'],
        'original_workflow_proof_binding':selected['parent_workflow_proof_binding'],'signed_coupling_proof_binding':selected['parent_coupling_proof_binding'],
        'warm_join_binding':binding(OBS/'final/signed-join.json'),'cold_verification_binding':binding(OBS/'final/cold.stdout'),
        'original_runtime_kind_gaps':2,'closed_runtime_kind_gaps':2,'remaining_runtime_kind_gaps':0,'typed_connections_checked':70,
        'review_members_binding':binding(HERE/'review-members.json'),'remaining_obligations':[],'duration_seconds':time.perf_counter()-start,
        'claim_ceiling':'Complete selected candidate Engineering/Research/Failure/Learning integration, with all original actual observations retained and two exact independent signed coupling witnesses. Original records retain candidate posture; independent local signatures supply no original/canonical admission, unqualified global merge, action permission or general Product benefit. Full DAG, S02/R08 and activation remain open.'}
    path=OBS.parent/'0004.json';emit(path,receipt)
    print(encoded({'result':'PASS','task_complete':True,'tests':len(checks),'validation_checks':len(validation),'files':len(files),
        'receipt':binding(path),'actual_owner_outcome':None}).decode(),end='')


if __name__=='__main__':run()
