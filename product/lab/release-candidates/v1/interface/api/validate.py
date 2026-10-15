"""Close exact authenticated reader evidence; retain incomplete full R03 scope."""
import ast
import base64
import json
import re
import time
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from protocol import HERE, ROOT, Schemas, source, compact

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
EXAMPLES=ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api/0005'


def received_message(raw):
    # Independent lexical span check over retained original wire bytes.
    text=raw.decode('utf-8');decoder=json.JSONDecoder();position=text.index('{')+1
    while position<len(text):
        while text[position].isspace() or text[position]==',':position+=1
        if text[position]=='}':break
        key,position=decoder.raw_decode(text,position)
        while text[position].isspace():position+=1
        source.require(text[position]==':','original field separator differs');position+=1
        while text[position].isspace():position+=1
        beginning=position;_,position=decoder.raw_decode(text,position)
        if key=='message':return text[beginning:position].encode('utf-8')
    raise ValueError('received message missing')


def main():
    start=time.perf_counter();output=HERE/'receipts/R03-0003.json'
    source.require(not output.exists(),'immutable proof receipt already exists')
    files={};checks=[]
    def evidence(path):
        path=path.resolve();binding=source.bind(path)
        source.original(binding);previous=files.get(binding['path'])
        source.require(previous is None or previous==binding,'conflicting original binding')
        files[binding['path']]=binding
        return source.parse(path.read_bytes()) if path.suffix=='.json' else path.read_bytes()
    def bound(binding):
        binding={key:binding[key] for key in ('path','sha256')}
        source.original(binding);return evidence(ROOT/binding['path'])
    def check(name,value):
        source.require(value,name);checks.append({'test':name,'result':'PASS'})
    manifest=evidence(HERE/'manifest.json')
    for binding in manifest['files']:bound(binding)
    context=evidence(RUN/'context-R03-api.json');evidence(RUN/'CONTEXT-R03-API.md')
    for binding in context['source_bindings']:
        value=bound(binding)
        if isinstance(value,dict):
            for key in ('files','source_files','source_bindings'):
                for item in value.get(key,[]):
                    if isinstance(item,dict) and {'path','sha256'}<=item.keys():bound(item)
    check('full R03 obligations retained',len(context['obligations'])==5 and 'R03 incomplete' in context['claim_ceiling'])
    schemas=Schemas()
    check('exact original API schema closure retained',len(schemas.inputs['files'])==790 and len(schemas.operations)==34)
    log=(HERE/'receipts/attempts/0006/tests.stderr').read_text()
    cases=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',log,re.MULTILINE)
    declared={node.name for node in ast.walk(ast.parse((HERE/'test_api.py').read_text()))
        if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}
    check('complete final 61-check suite terminal PASS',len(cases)==len(declared)==61
        and {name for name,_ in cases}==declared and re.search(r'Ran 61 tests in [0-9.]+s\n\nOK\n',log) is not None)
    checks.extend({'suite':'authenticated-api-guards','test':name,'result':'PASS'} for name,_ in cases)
    execution=evidence(EXAMPLES/'result.json')
    expected_exits={'authenticated-discovery':0,'wrong-key':2,'foreign-challenge':2,'foreign-cursor':0,
        'oversized-frame':0,'revoked-policy':0,'expired-policy':2,'truncated-frame':0}
    check('eight actual child processes terminal PASS',execution['result']=='PASS'
        and execution['child_processes']==len(execution['episodes'])==8
        and {r['name']:r['terminal_exit_code'] for r in execution['episodes']}==expected_exits)
    check('no canonical/authoring/owner/pilot/memory effects',execution['authority_effect']=='none'
        and execution['actual_owner_outcome'] is None and execution['human_pilot'] is False
        and execution['canonical_effects_applied']==execution['local_authoring_transactions']==execution['original_domain_cases_reexecuted']==0
        and execution['private_keys_exported'] is False and execution['Session_memory_exported'] is False
        and all(r['owned_credentials_removed'] and not r['private_keys_exported'] for r in execution['episodes']))
    episodes={};reply_count=0;frame_count=0
    for row in execution['episodes']:
        name=row['name'];directory=EXAMPLES/name
        index=evidence(directory/'frames.json');policy=evidence(directory/'original-public-reader-policy.json')
        check(name+': public policy exact closed schema',schemas.valid('reader-authentication',policy))
        check(name+': no child stderr',evidence(directory/'child.stderr')==b'')
        frames=[]
        for item in index['frames']:
            raw=(directory/item['file']).read_bytes();evidence(directory/item['file'])
            check(name+': exact frame '+item['file'],len(raw)==item['size_bytes'] and source.sha(raw)==item['sha256'])
            try:value=source.parse(raw)
            except Exception:value=None
            frames.append((item['direction'],raw,value));frame_count+=1
        challenge=frames[0][2];trusted=None
        if challenge['schema_version']=='lab-local-reader-challenge/v1-candidate':
            proof=frames[1][2]
            check(name+': challenge/proof schema',schemas.valid('reader-authentication',challenge)
                and schemas.valid('reader-authentication',proof))
            check(name+': exact selected public policy binding',challenge['policy_sha256']==source.sha((directory/'original-public-reader-policy.json').read_bytes())
                and challenge['expires_at']==policy['expires_at'])
            key=Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True))
            try:key.verify(base64.b64decode(proof['signature'],validate=True),compact(proof['challenge']));signature_valid=True
            except InvalidSignature:signature_valid=False
            check(name+': independent public signature outcome',signature_valid==(name!='wrong-key'))
            check(name+': connection-specific challenge outcome',(proof['challenge']==challenge)==(name!='foreign-challenge'))
            if frames[2][2]['schema_version']=='lab-local-reader-authenticated/v1-candidate':
                authenticated=frames[2][2];trusted=authenticated['context']
                check(name+': actual authenticated context schema',schemas.valid('reader-authentication',authenticated)
                    and schemas.valid('trusted-call-context',trusted))
                check(name+': host-created context exact policy/proof',trusted['host_instance_ref']==challenge['host_instance_ref']
                    and trusted['connection_ref']==challenge['connection_ref'] and trusted['principal_ref']==policy['principal_ref']
                    and trusted['scope_refs']==policy['scope_refs'] and trusted['expires_at']==policy['expires_at']
                    and trusted['authentication_evidence_binding']['sha256']==source.sha(frames[1][1])
                    and trusted['policy_bindings'][0]['sha256']==challenge['policy_sha256']
                    and authenticated['trusted_context_binding']['sha256']==source.sha(compact(trusted)))
                check(name+': zero-action ephemeral context',trusted['limits']['max_actions']==0
                    and trusted['role_assignment_bindings']==[] and trusted['agent_instance_ref'] is None
                    and trusted['assignment_ref'] is None and trusted['session_ref'] is None
                    and trusted['private_credentials_in_context'] is False
                    and trusted['accept_client_supplied_authority_context'] is False)
                profile=trusted['source_profile_binding'];bound({'path':profile['ref'],'sha256':profile['sha256']})
                authority=trusted['policy_bindings'][1];bound({'path':authority['ref'],'sha256':authority['sha256']})
        for i,(direction,raw,value) in enumerate(frames):
            if direction!='server':continue
            version=value['schema_version']
            if version=='lab-api-reply/v1-candidate':
                call_raw=frames[i-1][1];call=frames[i-1][2];reply_count+=1
                check(name+': exact call/reply schema '+str(i),schemas.valid('api-call',call) and schemas.valid('api-reply',value))
                check(name+': four separate actual byte bindings '+str(i),value['call_id']==call['call_id'] and value['operation']==call['operation']
                    and value['request_binding']['sha256']==source.sha(call_raw)
                    and value['message']['request_binding']['sha256']==source.sha(received_message(call_raw))
                    and value['trusted_context_binding']['sha256']==source.sha(compact(trusted))
                    and value['handler_binding']['sha256']==source.sha((HERE/'handlers.py').read_bytes()))
            elif version=='lab-api-transport-error/v1-candidate':
                check(name+': original transport-error schema '+str(i),schemas.valid('transport-error',value)
                    and value['authority_effect']=='none' and value['effect_may_have_started'] is False)
                if value['request_byte_sha256'] is not None:
                    check(name+': transport exact received bytes '+str(i),i>0 and value['request_byte_sha256']==source.sha(frames[i-1][1]))
            else:check(name+': closed authentication schema '+str(i),schemas.valid('reader-authentication',value))
        episodes[name]=frames
    # Independent original baseline oracle, rather than asking the same handlers.
    selection=source.source_selection('engineering')
    archive=source.parse(source.original(selection['archive_binding']));bound(selection['archive_binding'])
    def archived(path):return source.parse(base64.b64decode(archive['files'][path]['base64_original_bytes'],validate=True))
    baseline=archived('baseline.json');genesis=archived('transactions/0000000000.json');head=archived('transactions/0000000001.json')
    observed=episodes['authenticated-discovery'];current=observed[4][2]['message']['source_cut'];historical=observed[8][2]['message']['source_cut']
    check('original exact current and genesis transaction cuts',current['commit_sequence']==1 and current['commit_sha256']==head['digest']==selection['expected_head']
        and historical['commit_sequence']==0 and historical['commit_sha256']==genesis['digest']
        and historical['source_profile_sha256']==current['source_profile_sha256']==source.PINS.profile_sha256)
    check('original genesis stream cursors/digests',historical['streams']==[{'stream_ref':name,'cursor':len(record['payload']['events']),
        'head_sha256':source.sha(compact(record))} for name,record in sorted(baseline['histories'].items())])
    expected=[]
    for ref,contract in sorted(baseline['contracts'].items()):
        if contract['lifecycle_state'] not in ('admitted-current','admitted-historical'):continue
        expected.append({'carrier_ref':ref,'schema_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']},
            'descriptor_binding':{'ref':contract['artifact_path'],'sha256':contract['artifact_sha256']},
            'schema_selector':contract['schema_selector'] or None,'semantic_kind':contract['semantic_kind'],
            'write_posture':'current' if contract['lifecycle_state']=='admitted-current' else 'historical-read-only',
            'admission_decision_ref':contract['admission_decision_ref']})
        for path,digest in [(contract['schema_path'],contract['schema_sha256']),(contract['artifact_path'],contract['artifact_sha256'])]:bound({'path':path,'sha256':digest})
    first=observed[6][2]['message'];second=observed[10][2]['message']
    check('catalog pages equal independent original 143-version catalog',len(expected)==143
        and first['contract_entries']==expected[:10] and second['contract_entries']==expected[10:20]
        and observed[9][2]['message']['page_cursor']==first['next_page_cursor'])
    relations=[]
    for ref,record in sorted(baseline['relation_contracts'].items()):
        paths=[path for path,doc in baseline['documents'].items() if doc==record]
        check('unique original signature '+ref,len(paths)==1)
        path=paths[0];bound({'path':path,'sha256':baseline['materials'][path]})
        relations.append({'relation_kind_ref':ref,'axis_ref':record['payload']['axis_id'],
            'signature_binding':{'ref':path,'sha256':baseline['materials'][path]}})
    check('41 original closed signature bindings exact',len(relations)==41 and first['relation_signatures']==second['relation_signatures']==relations)
    check('actual limited handler readiness exposed',observed[4][2]['message']['supported_operations']==['lab.status','catalog.get']
        and observed[4][2]['message']['projection_status_binding'] is None
        and observed[4][2]['message']['implementation_posture']=='implemented-local')
    check('negative actor/unsupported/budget/duplicate outcomes exact',observed[12][2]['message']['code']=='unauthorized'
        and observed[14][2]['code']=='unsupported-operation' and observed[16][2]['message']['code']=='budget-exceeded'
        and observed[18][2]['code']=='malformed-json')
    check('foreign-context cursor rejected',episodes['foreign-cursor'][6][2]['message']['code']=='invalid-cursor')
    with source.replay_source('engineering') as view:
        check('fresh original signed replay matches recorded current streams',current['streams']==[{'stream_ref':name,
            'cursor':len(record['payload']['events']),'head_sha256':view.handle.common.digest(record)}
            for name,record in sorted(view.data['projection']['histories'].items())])
    for tree in [HERE,EXAMPLES]:
        for path in tree.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path not in [HERE/'receipts/validation.stdout',HERE/'receipts/validation.stderr',output]:evidence(path)
    for binding in files.values():source.original(binding)
    receipt={'schema_version':'lab-R03-authenticated-reader-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Actual authenticated local stdio and two exact read handlers over independently selected saved signed candidate archives only; no full R03, human pilot, canonical admission or live authority.',
        'verified_obligation_ids':['T1','T2','T3','T4'],'tests':61,'fresh_child_processes':8,'observed_frames':frame_count,
        'observed_api_replies':reply_count,'implemented_operations':['lab.status','catalog.get'],'declared_operations':34,'remaining_operations':32,
        'eligible_carrier_versions':143,'relation_signatures':41,'checks':checks,'canonical_effects_applied':0,
        'local_authoring_transactions_applied':0,'original_domain_cases_reexecuted':0,'human_pilot':False,
        'private_keys_exported':False,'Session_memory_exported':False,'prior_inspection_proof':source.bind(HERE.parent/'inspection/receipts/R03-0002.json'),
        'preserved_failed_observations':['First real child rejected startup: missing explicit ReaderChannel import; corrected before successor observation.',
            'Historical prefix construction omitted deterministic consequences; projection digest guard rejected all 60 checks and the child. Original signed archives remained valid; complete reconstruction successor passed.',
            'Earlier complete 60-check/8-child proof retained; final successor adds exponent-overflow refusal and reuses the independently verified final projection.'],
        'remaining_obligations':['Complete the other 32 original exact API handlers, including artifact inspection and query; two handler success is not full API completion.',
            'Implement required SQLite/query parity and integrate candidate queues, complete Decision authority/evidence and the third Agent/session owner journey.',
            'Close full W07/R03 criteria, remaining workflows, S02 exact review closure and real human pilot/R08 response.'],
        'source_drift':[],'files':sorted(files.values(),key=lambda b:b['path']),'duration_seconds':time.perf_counter()-start}
    with output.open('xb') as stream:stream.write(source.encoded(receipt))
    print(json.dumps({'result':'PASS','task':'R03','task_complete':False,'tests':61,'child_processes':8,
        'frames':frame_count,'api_replies':reply_count,'files':len(files),'receipt':source.bind(output),'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':main()
