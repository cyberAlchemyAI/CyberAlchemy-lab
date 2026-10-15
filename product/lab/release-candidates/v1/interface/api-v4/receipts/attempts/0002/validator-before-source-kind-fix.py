"""Verify exact corrected-reader source closure and real original-wire evidence."""
import ast
import base64
import json
import re
import time
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from protocol import *
import artifact_model as model
from handlers import cut

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
EXAMPLES=ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api'


def message_span(raw):
    text=raw.decode('utf-8');decoder=json.JSONDecoder();position=text.index('{')+1
    while position<len(text):
        while text[position].isspace() or text[position]==',':position+=1
        if text[position]=='}':break
        key,position=decoder.raw_decode(text,position)
        while text[position].isspace():position+=1
        source.require(text[position]==':','exact original separator differs');position+=1
        while text[position].isspace():position+=1
        start=position;_,position=decoder.raw_decode(text,position)
        if key=='message':return text[start:position].encode('utf-8')
    raise ValueError('exact message span unavailable')


def run():
    start=time.perf_counter();files={};checks=[]
    def capture(path):
        b=source.bind(Path(path));source.original(b)
        source.require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting proof source')
        files[b['path']]=b['sha256'];return b
    def bound(b):capture(ROOT/b['path']);return source.parse(source.original(b))
    def check(name,value):source.require(value,name);checks.append({'test':name,'result':'PASS'})
    context=bound(capture(RUN/'context-R03-corrected-readers.json'))
    for b in context['source_bindings']:
        v=bound(b)
        for b0 in v.get('files',[]):capture(ROOT/b0['path']);source.original(b0)
    manifest=bound(capture(HERE/'manifest.json'))
    for b in manifest['files']:source.original(b);capture(ROOT/b['path'])
    schemas=Schemas();check('all original 34 operation/schema scope retained',len(schemas.operations)==34 and len(schemas.inputs['files'])==790 and len(SUPPORTED)==4)
    suite_rows=[(['test_api.py','test_readers.py','test_representations.py'],'0001/tests.stderr',126),(['test_corrected.py'],'0002/corrected-tests.stderr',31)]
    for names,log_name,count in suite_rows:
        names_declared={n.name for name in names for n in ast.walk(ast.parse((HERE/name).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
        log=(HERE/'receipts/attempts'/log_name).read_text();observed=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',log,re.M)
        check(log_name+': complete terminal cases',len(observed)==len(names_declared)==count and {n for n,_ in observed}==names_declared
            and re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\n\nOK\s*$',log) is not None)
        checks.extend({'suite':log_name,'test':n,'result':'PASS'} for n,_ in observed)
    for name in ['test_api.py','test_readers.py','test_representations.py']:
        check(name+': original 126 assertions unchanged',(HERE/name).read_bytes()==(HERE.parent/'api-v3'/name).read_bytes())
    expected={'0015':{'inspection-and-sql-query':0,'historical-query':0,'cold-query-rebuild':0},
        '0016':{'authenticated-discovery':0,'wrong-key':2,'foreign-challenge':2,'foreign-cursor':0,'oversized-frame':0,'revoked-policy':0,'expired-policy':2,'truncated-frame':0},
        '0018':{'corrected-head':0,'corrected-genesis':0,'corrected-cold-rebuild':0}}
    frames_total=0;replies=[];handshakes=0
    for episode,names in expected.items():
        root=EXAMPLES/episode;result=bound(capture(root/'result.json'))
        check(episode+': actual completed child cases',result['result']=='PASS' and {r['name']:r['terminal_exit_code'] for r in result['episodes']}==names
            and result['child_processes']==len(names))
        check(episode+': owned credential cleanup and no canonical/owner effects',result['authority_effect']=='none' and result['actual_owner_outcome'] is None
            and result['canonical_effects_applied']==result['local_authoring_transactions']==0 and not result['private_keys_exported'] and not result['Session_memory_exported']
            and not result['human_pilot'] and all(r['owned_credentials_removed'] and not r['private_keys_exported'] for r in result['episodes']))
        for name in names:
            directory=root/name;index=bound(capture(directory/'frames.json'));policy=bound(capture(directory/'original-public-reader-policy.json'))
            check(name+': exact closed policy and empty child stderr',schemas.valid('reader-authentication',policy) and (directory/'child.stderr').read_bytes()==b'')
            frames=[];context0=None
            for row in index['frames']:
                path=directory/row['file'];capture(path);raw=path.read_bytes()
                check(name+': original wire '+row['file'],source.sha(raw)==row['sha256'] and len(raw)==row['size_bytes'])
                try:value=source.parse(raw)
                except Exception:value=None
                frames.append((row['direction'],raw,value));frames_total+=1
            challenge=frames[0][2]
            if challenge['schema_version']=='lab-local-reader-challenge/v1-candidate':
                proof=frames[1][2];check(name+': independent challenge/policy binding',schemas.valid('reader-authentication',challenge)
                    and schemas.valid('reader-authentication',proof) and challenge['policy_sha256']==source.sha((directory/'original-public-reader-policy.json').read_bytes()))
                key=Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True))
                try:key.verify(base64.b64decode(proof['signature'],validate=True),compact(proof['challenge']));valid=True
                except InvalidSignature:valid=False
                check(name+': actual signature/refusal posture',valid==(name!='wrong-key') and (proof['challenge']==challenge)==(name!='foreign-challenge'))
                authenticated=frames[2][2]
                if authenticated['schema_version']=='lab-local-reader-authenticated/v1-candidate':
                    context0=authenticated['context'];handshakes+=1
                    check(name+': exact host-produced trusted context',schemas.valid('reader-authentication',authenticated) and schemas.valid('trusted-call-context',context0)
                        and context0['host_instance_ref']==challenge['host_instance_ref'] and context0['connection_ref']==challenge['connection_ref']
                        and context0['scope_refs']==policy['scope_refs'] and context0['authentication_evidence_binding']['sha256']==source.sha(frames[1][1])
                        and context0['policy_bindings'][0]['sha256']==challenge['policy_sha256']
                        and authenticated['trusted_context_binding']['sha256']==source.sha(compact(context0)))
                    check(name+': zero action/Agent/private key grants',context0['limits']['max_actions']==0 and context0['role_assignment_bindings']==[]
                        and context0['agent_instance_ref'] is context0['session_ref'] is context0['assignment_ref'] is None
                        and not context0['private_credentials_in_context'] and not context0['accept_client_supplied_authority_context'])
            for i,(direction,raw,value) in enumerate(frames):
                if direction!='server':continue
                if value['schema_version']=='lab-api-reply/v2-candidate':
                    request=frames[i-1][2];wire=frames[i-1][1]
                    check(name+': exact selected call/reply '+str(i),schemas.valid('api-call',request) and schemas.valid('api-reply',value)
                        and value['call_id']==request['call_id'] and value['operation']==request['operation']
                        and value['contract_profile_binding']==request['expected_contract_profile_binding']==schemas.profile_binding)
                    check(name+': four independent byte bindings '+str(i),value['request_binding']['sha256']==source.sha(wire)
                        and value['message']['request_binding']['sha256']==source.sha(message_span(wire))
                        and value['trusted_context_binding']['sha256']==source.sha(compact(context0))
                        and value['handler_binding']['sha256']==source.sha((HERE/'handlers.py').read_bytes()))
                    replies.append((name,request,value))
                elif value['schema_version']=='lab-api-transport-error/v1-candidate':
                    check(name+': declared refusal '+str(i),schemas.valid('transport-error',value) and value['effect_may_have_started'] is False)
                    if value['request_byte_sha256'] is not None:check(name+': exact refused wire '+str(i),value['request_byte_sha256']==source.sha(frames[i-1][1]))
                else:check(name+': closed authentication frame '+str(i),schemas.valid('reader-authentication',value))
    coverage=bound(capture(HERE/'receipts/coverage.json'));rows={r['name']:r for r in coverage['cuts']}
    check('preserved 508-source engineering coverage remains independently unchanged',rows['engineering']['subjects']==508
        and rows['engineering']['connection_coverage']=={'current':{'closed':45,'unclosed':10},'historical':{'closed':0,'unclosed':0},'excluded':[],'total':55})
    corrected=rows['reference-corrected'];check('546 complete representations and original descriptor mismatches remain separate',corrected['subjects']==546
        and corrected['representations']=={'catalog-representations':143,'domain-instances':403,'representation-fit':546}
        and corrected['representation_gaps']==[] and len(corrected['original_domain_mismatches'])==133)
    check('70 exact relations accounted for with independent lifecycle closure',corrected['connection_coverage']=={'current':{'closed':60,'unclosed':0},'historical':{'closed':0,'unclosed':10},'excluded':[],'total':70})
    warm=None;gen=None;cold_items=None;cold_gen=None;hist=None
    with source.replay_source('reference-corrected') as view:
        expected_headers=model.references(view);members=[source.parse(source.original(b)) for b in source.parse(source.original(view.handle.manifest['correction_profile_binding']))['member_bindings']]
        old_refs={m['predecessor_version_ref'] for m in members};new_refs={m['version_ref'] for m in members}
        check('historical gap exact predecessor identities preserved',{g['subject_ref'] for g in corrected['connection_gaps']}==old_refs
            and all('Historical relation remains unresolved' in g['reason'] for g in corrected['connection_gaps']))
        for name,request,reply in replies:
            if name not in ['corrected-head','corrected-genesis','corrected-cold-rebuild'] or reply['kind']!='result':continue
            value=reply['message']
            if request['operation']=='artifact.query' and request['message']['carrier_refs']==sorted(view.data['projection']['contracts']):
                if name=='corrected-head':
                    check(name+': exact signed canonical/SQL inventory',value['results']==expected_headers)
                    if value['query_basis']=='projection':warm=value['results'];gen=value['projection_generation']
                if name=='corrected-cold-rebuild':cold_items=value['results'];cold_gen=value['projection_generation']
                if name=='corrected-genesis':
                    hist=value['results'];check(name+': exact 485-prefix without later corrections',len(hist)==485 and value['freshness']=='historical'
                        and old_refs<={h['version_ref'] for h in hist} and not new_refs&{h['version_ref'] for h in hist})
            if request['operation']=='artifact.inspect' and request['message']['artifact']['version_ref'] in new_refs|old_refs:
                subject=view.subjects[request['message']['artifact']['version_ref']]
                check(name+': exact current/historical original body and status',value['envelope']['decoded_artifact']['body']==subject['record']
                    and value['status_facets']['admission']==subject['effective_state'])
        check('new cold disposable generation retains exact warm revisions',warm==cold_items==expected_headers and gen is not None and cold_gen is not None and gen!=cold_gen and hist is not None)
    review=bound(capture(HERE/'review-members.json'));check('four independent unadmitted reader review members',len(review['members'])==4
        and len({m['member_ref'] for m in review['members']})==4 and not review['complete_final_package'])
    for member in review['members']:
        check(member['member_ref']+': no invented owner outcome',member['authority_effect']=='none' and member['actual_owner_outcome'] is None)
        for b in member['bindings']:source.original(b);capture(ROOT/b['path'])
    for directory in [HERE,*[EXAMPLES/n for n in ['0015','0016','0017','0018']]]:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name!='R03-0007.json':capture(path)
    drift=[path for path,digest in files.items() if source.sha((ROOT/path).read_bytes())!=digest];check('complete retained/candidate source closure current',not drift)
    result={'schema_version':'lab-R03-corrected-reader-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'tests':157,'fresh_child_processes':14,'observed_frames':frames_total,'observed_api_replies':len(replies),'verified_authenticated_handshakes':handshakes,
        'declared_operations':34,'implemented_operations':list(SUPPORTED),'remaining_operations':30,'current_cut_revisions':546,'historical_cut_revisions':485,
        'current_closed_connections':60,'current_unclosed_connections':0,'historical_unclosed_connections':10,'catalog_representations':143,
        'unchanged_original_domain_mismatches':133,'read_representation_gaps':0,'review_members':4,'local_authoring_transactions_applied':0,'canonical_effects_applied':0,
        'private_keys_exported':False,'Session_memory_exported':False,'human_pilot':False,'checks':checks,'source_drift':drift,
        'files':[{'path':path,'sha256':digest} for path,digest in sorted(files.items())],'verified_obligation_ids':[o['id'] for o in context['obligations']],
        'parent_reader_proof':manifest['parent_reader_binding'],'parent_correction_proof':manifest['parent_correction_binding'],
        'preserved_failed_observations':['stale profile construction probe','test predecessor field lookup','overly narrow total evidence-count harness'],
        'remaining_obligations':['Remaining thirty exact operations, complete external candidate/Decision coverage and actual Agent/operator journey.',
            'W07 complete integration, O03 source-backed three-lens questions and persistent SQLite/ontology query joins.',
            'Complete S02 exact canonical targets/roles/publisher closure, actual R08 response and authorized observed A01–A04.'],
        'claim_ceiling':'Four actual reader operations over selected signed candidate cuts, exact current/historical coverage and parity only. No original source rewrite, canonical admission, human pilot or full R03/plan completion.',
        'duration_seconds':time.perf_counter()-start}
    output=HERE/'receipts/R03-0007.json';source.require(not output.exists(),'exact reader proof already captured');output.write_bytes(source.encoded(result))
    print(json.dumps({k:result[k] for k in ['result','task_complete','tests','fresh_child_processes','observed_frames','observed_api_replies','current_cut_revisions',
        'current_closed_connections','current_unclosed_connections','historical_unclosed_connections']},sort_keys=True))


if __name__=='__main__':run()
