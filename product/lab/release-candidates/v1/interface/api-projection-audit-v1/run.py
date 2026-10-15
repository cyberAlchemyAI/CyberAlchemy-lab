"""Independent original byte closure and actual selected API evidence audit."""
import argparse,base64,copy,hashlib,importlib.util,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];BASE=HERE.parent;API=BASE/'api-v16'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:f.write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    assert sha(HERE/'source-manifest.json')==args.source_sha256
    source=load(HERE/'source-manifest.json');checks=[]
    def check(ok,why):
        if not ok:raise ValueError(why)
        checks.append({'check':why,'result':'PASS'})
    output=HERE/'receipts/0001';output.mkdir(parents=True,exist_ok=False)
    report={'result':'FAIL','authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    try:
        for row in source['files']:
            check(sha(ROOT/row['path'])==row['sha256'],'original-file:'+row['path'])
        parent=load(ROOT/source['parent_receipt_binding']['path']);captured={r['path']:r['sha256'] for r in source['files']}
        check(all(captured.get(r['path'])==r['sha256'] for r in parent['files']),'all-6031-parent-bindings-retained')
        name='_cal_api_v16';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        P=__import__(name+'.protocol',fromlist=['Schemas']);W=__import__(name+'.workspace',fromlist=['privacy']);schemas=P.Schemas(source['selected_profile_binding']['sha256'])
        check(len(schemas.operations)==34 and len(P.SUPPORTED)==12 and set(P.SUPPORTED)<=set(schemas.operations),'original-34-API-contracts-retained-with-12-selected-handlers')
        suites=[('api-projection-tests-v3',21),('api-projection-regression-v3',34),('api-projection-preparation-v2',47)]
        counts={}
        for folder,number in suites:
            tests=load(BASE/folder/'receipts/0001/tests.json');counts[folder]=number
            check(tests['result']=='PASS' and tests['tests_run']==number and tests['errors']==tests['failures']==0,folder+':all-original-methods-passed')
            check(len(tests['methods'])==len(set(tests['methods']))==number,folder+':no-method-omission-or-duplication')
            check(tests.get('all_owned_roots_removed',tests.get('owned_fixture_root_removed',tests.get('all_observed_primary_roots_removed',False))),folder+':observed-owned-roots-removed')
            for child in tests.get('children',[]):check(child['exit_code']==0 and child['terminal_observed'],folder+':terminal-'+child['group'])
        process=load(BASE/'api-projection-process-v2/receipts/0001/result.json')
        check(process['result']=='PASS' and len(process['checks'])==61 and process['wire_frames']==9 and process['new_sql_generations']==2,'two-actual-processes-full-positive-proof')
        check(process['owned_roots_removed'] and process['canonical_effects_applied']==0 and not process['private_keys_exported'] and not process['private_memory_exported'],'real-process-scope-and-cleanup')
        for child in process['observed_processes']:check(child['exit_code']==0 and child['terminal_observed'],'actual-process-terminal-'+child['process'])
        actual_operations=set();direct=0;mutated=0;original_frames=0;parsed_noncanonical=0
        for folder in ['api-projection-tests-v3','api-projection-regression-v3']:
            rows=load(BASE/folder/'receipts/0001/wire-observations.json')
            for index,row in enumerate(rows):
                call=row.get('original_call');raw=base64.b64decode(row['original_call_base64'],validate=True) if 'original_call_base64' in row else P.compact(call)
                call=P.frame_parse(raw);reply=row['reply'];W.privacy(reply)
                check(schemas.valid('api-call',call),folder+':original-call-schema-'+str(index))
                if reply['schema_version']=='lab-api-transport-error/v1-candidate':
                    check(schemas.valid('transport-error',reply),folder+':original-transport-error-'+str(index));direct+=1;continue
                check(schemas.valid('api-reply',reply),folder+':original-result-schema-'+str(index))
                observed_sha=row.get('request_byte_sha256',P.source.sha(raw))
                check(reply['request_binding']['sha256']==observed_sha,folder+':observed-outer-byte-binding-'+str(index))
                if observed_sha!=P.source.sha(raw):
                    check(folder=='api-projection-regression-v3' and 'original_call_base64' not in row and call['operation']=='session.open', 'one-retained-test22-parsed-noncanonical-sample')
                    parsed_noncanonical+=1
                if reply['contract_profile_binding']!=schemas.profile_binding:
                    check(False,'selected-current-reply-profile-mismatch')
                    mutated+=1;continue
                if reply['kind']=='result':actual_operations.add(reply['operation'])
                direct+=1
        check(mutated==0 and parsed_noncanonical==1,'selected-current-returned-snapshots-and-one-explicit-parsed-test22-sample')
        for row in load(BASE/'api-projection-process-v2/receipts/0001/wire-transcripts.json'):
            if 'original_call_base64' not in row:
                for key in ['challenge_base64','proof_base64','authenticated_base64']:
                    value=P.frame_parse(base64.b64decode(row[key],validate=True));W.privacy(value);check(schemas.valid('reader-authentication',value),'actual-stdio-authentication:'+row['process']+':'+key)
                continue
            raw=base64.b64decode(row['original_call_base64'],validate=True);call=P.frame_parse(raw);reply=P.frame_parse(base64.b64decode(row['original_reply_base64'],validate=True));W.privacy(reply)
            check(schemas.valid('api-call',call) and schemas.valid('api-reply',reply),'actual-stdio-original-wire-schemas-'+str(original_frames))
            check(reply['contract_profile_binding']==schemas.profile_binding and reply['request_binding']['sha256']==P.source.sha(raw),'actual-stdio-exact-profile-and-wire-'+str(original_frames))
            check(reply['handler_binding']==P.binding(str((API/('projection_refresh.py' if call['operation']=='projection.refresh' else 'candidate.py' if call['operation']=='operation.inspect' else 'handlers.py')).relative_to(ROOT)),(API/('projection_refresh.py' if call['operation']=='projection.refresh' else 'candidate.py' if call['operation']=='operation.inspect' else 'handlers.py')).read_bytes()),'actual-stdio-exact-handler-'+str(original_frames))
            check(reply['kind']=='result','actual-stdio-completed-result-'+str(original_frames));actual_operations.add(reply['operation']);original_frames+=1
        check(actual_operations==set(P.SUPPORTED),'all-12-selected-public-handlers-returned-actual-valid-results')
        portable=ROOT/'implementation/lab-ontology/candidates/v1/currentness/successors/0001';spec=importlib.util.spec_from_file_location('_portable_currentness_audit',portable/'portable.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        errors,observations=module.currentness();check(not errors,'live-portable-currentness-read-only-branch-and-exact-code')
        native=(portable/'proof/0001/native-tests.stdout').read_text();check(sum(int(x) for x in re.findall(r'test result: ok\. (\d+) passed;',native))==23,'full-native-regressions-23-passed')
        guards=load(portable/'guards/0001/terminal.json');check(guards['exit_code']==0 and guards['terminal_observed'],'nine-portable-locator-negative-guards')
        report.update(result='PASS',checks=len(checks),actual_public_api_operations=12,remaining_original_api_operations=22,
            suite_tests=counts,selected_suite_tests=102,actual_stdio_frames=original_frames,actual_direct_samples=direct,
            intentional_client_mutated_samples=mutated,portable_currentness_observations=observations,
            retained_parsed_noncanonical_samples=parsed_noncanonical,
            parent_files_retained=len(parent['files']),checked_file_bindings=len(source['files']),canonical_effects_applied=0,
            private_keys_exported=False,private_memory_exported=False,
            claim_ceiling='Selected candidate source and actual 12 public handlers only. Original R03 whole-journey criteria, byte custody, full semantic/authority/owner/package closure and all final acceptance/admission obligations remain open.')
    except BaseException as error:report['failure']=str(error);report['checks']=len(checks)
    emit(output/'checks.json',checks);emit(output/'result.json',report);print(json.dumps(report),flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
