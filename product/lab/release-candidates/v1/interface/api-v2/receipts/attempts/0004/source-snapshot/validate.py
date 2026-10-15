"""Exact successor evidence closure; full R03 remains explicitly incomplete."""
import ast
import base64
import json
import re
import time
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from protocol import *

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
EXAMPLE_ROOT=ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api'


def message_span(raw):
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
    raise ValueError('message span missing')


def main():
    start=time.perf_counter();output=HERE/'receipts/R03-0004.json'
    source.require(not output.exists(),'immutable successor receipt already exists')
    files={};checks=[]
    def evidence(path):
        path=path.resolve();b=source.bind(path);source.original(b)
        old=files.get(b['path']);source.require(old is None or old==b,'conflicting exact source binding');files[b['path']]=b
        return source.parse(path.read_bytes()) if path.suffix=='.json' else path.read_bytes()
    def bound(b):
        b={k:b[k] for k in ('path','sha256')};source.original(b);return evidence(ROOT/b['path'])
    def check(name,value):source.require(value,name);checks.append({'test':name,'result':'PASS'})
    manifest=evidence(HERE/'manifest.json')
    for b in manifest['files']:bound(b)
    context=evidence(RUN/'context-R03-query.json');evidence(RUN/'CONTEXT-R03-QUERY.md')
    for b in context['source_bindings']:
        value=bound(b)
        if isinstance(value,dict):
            for key in ('files','source_files','source_bindings'):
                for row in value.get(key,[]):
                    if isinstance(row,dict) and {'path','sha256'}<=row.keys():bound(row)
    schemas=Schemas();check('full original 34 API scope and exact schemas retained',len(schemas.operations)==34 and len(schemas.inputs['files'])==790)
    declared={n.name for name in ['test_api.py','test_readers.py'] for n in ast.walk(ast.parse((HERE/name).read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    log=(HERE/'receipts/attempts/0004/tests.stderr').read_text();cases=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',log,re.MULTILINE)
    check('all 104 inherited/new tests terminal PASS',len(cases)==len(declared)==104 and {name for name,_ in cases}==declared
        and re.search(r'Ran 104 tests in [0-9.]+s\n\nOK\n',log) is not None)
    checks.extend({'suite':'successor-authenticated-reader','test':name,'result':'PASS'} for name,_ in cases)
    expected={'0010':{'authenticated-discovery':0,'wrong-key':2,'foreign-challenge':2,'foreign-cursor':0,
        'oversized-frame':0,'revoked-policy':0,'expired-policy':2,'truncated-frame':0},
        '0009':{'inspection-and-sql-query':0,'historical-query':0,'cold-query-rebuild':0}}
    episodes={};frames_total=0;replies=[];handshakes=0
    for generation,names in expected.items():
        root=EXAMPLE_ROOT/generation;result=evidence(root/'result.json')
        check(generation+': actual child terminal outcomes',result['result']=='PASS' and result['child_processes']==len(names)
            and {row['name']:row['terminal_exit_code'] for row in result['episodes']}==names)
        check(generation+': no authoring/canonical/owner/pilot/memory effects',result['authority_effect']=='none' and result['actual_owner_outcome'] is None
            and result['human_pilot'] is False and result['canonical_effects_applied']==result['local_authoring_transactions']==0
            and result['private_keys_exported'] is False and result['Session_memory_exported'] is False
            and all(row['owned_credentials_removed'] and not row['private_keys_exported'] for row in result['episodes']))
        for name in names:
            directory=root/name;index=evidence(directory/'frames.json');policy=evidence(directory/'original-public-reader-policy.json')
            check(name+': closed public policy',schemas.valid('reader-authentication',policy));check(name+': child stderr empty',evidence(directory/'child.stderr')==b'')
            frames=[];context=None
            for row in index['frames']:
                raw=(directory/row['file']).read_bytes();evidence(directory/row['file'])
                check(name+': exact frame '+row['file'],source.sha(raw)==row['sha256'] and len(raw)==row['size_bytes'])
                try:value=source.parse(raw)
                except Exception:value=None
                frames.append((row['direction'],raw,value));frames_total+=1
            challenge=frames[0][2]
            if challenge['schema_version']=='lab-local-reader-challenge/v1-candidate':
                proof=frames[1][2]
                check(name+': exact challenge/public policy',schemas.valid('reader-authentication',challenge)
                    and schemas.valid('reader-authentication',proof) and challenge['policy_sha256']==source.sha((directory/'original-public-reader-policy.json').read_bytes()))
                key=Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True))
                try:key.verify(base64.b64decode(proof['signature'],validate=True),compact(proof['challenge']));valid=True
                except InvalidSignature:valid=False
                check(name+': independent signature/challenge outcome',valid==(name!='wrong-key') and (proof['challenge']==challenge)==(name!='foreign-challenge'))
                authenticated=frames[2][2]
                if authenticated['schema_version']=='lab-local-reader-authenticated/v1-candidate':
                    context=authenticated['context'];handshakes+=1
                    check(name+': exact host-produced trusted context',schemas.valid('reader-authentication',authenticated)
                        and schemas.valid('trusted-call-context',context) and context['host_instance_ref']==challenge['host_instance_ref']
                        and context['connection_ref']==challenge['connection_ref'] and context['principal_ref']==policy['principal_ref']
                        and context['scope_refs']==policy['scope_refs'] and context['expires_at']==policy['expires_at']
                        and context['authentication_evidence_binding']['sha256']==source.sha(frames[1][1])
                        and context['policy_bindings'][0]['sha256']==challenge['policy_sha256']
                        and authenticated['trusted_context_binding']['sha256']==source.sha(compact(context)))
                    check(name+': no private key/session/owner grants',context['limits']['max_actions']==0
                        and context['role_assignment_bindings']==[] and context['agent_instance_ref'] is context['session_ref'] is context['assignment_ref'] is None
                        and context['private_credentials_in_context'] is False and context['accept_client_supplied_authority_context'] is False)
                    for b in [context['source_profile_binding'],context['policy_bindings'][1]]:bound({'path':b['ref'],'sha256':b['sha256']})
            for i,(direction,raw,value) in enumerate(frames):
                if direction!='server':continue
                if value['schema_version']=='lab-api-reply/v1-candidate':
                    request=frames[i-1][2];wire=frames[i-1][1]
                    check(name+': exact call/reply/schema '+str(i),schemas.valid('api-call',request) and schemas.valid('api-reply',value)
                        and value['operation']==request['operation'] and value['call_id']==request['call_id'])
                    check(name+': four exact independent byte bindings '+str(i),value['request_binding']['sha256']==source.sha(wire)
                        and value['message']['request_binding']['sha256']==source.sha(message_span(wire))
                        and value['trusted_context_binding']['sha256']==source.sha(compact(context))
                        and value['handler_binding']['sha256']==source.sha((HERE/'handlers.py').read_bytes()))
                    replies.append((name,request,value))
                elif value['schema_version']=='lab-api-transport-error/v1-candidate':
                    check(name+': original transport refusal '+str(i),schemas.valid('transport-error',value) and value['effect_may_have_started'] is False)
                    if value['request_byte_sha256'] is not None:check(name+': transport exact wire hash '+str(i),value['request_byte_sha256']==source.sha(frames[i-1][1]))
                else:check(name+': original closed authentication frame '+str(i),schemas.valid('reader-authentication',value))
            episodes[name]=frames
    coverage=evidence(HERE/'receipts/coverage.json')
    check('exact body/schema gaps explicit',coverage['subject_count']==508 and coverage['body_counts']=={'body-fit':375,'body-contract-gap':133}
        and len(coverage['body_contract_gaps'])==133 and all(row['category']=='artifact-type' for row in coverage['body_contract_gaps']))
    check('exact connection and head gaps explicit',coverage['captured_typed_relations']==55 and coverage['closed_api_connections']==45
        and len(coverage['connection_gaps'])==10 and len(coverage['ambiguous_current_heads'])==1)
    # Cold signature replay provides independent original metadata/body oracles.
    with source.replay_source('engineering') as view:
        def header(subject):
            c=subject['carrier_ref'] or subject['record'].get('classification',{}).get('artifact_type_ref')
            if c is None:
                matches=[ref for ref,row in view.data['projection']['contracts'].items() if row['semantic_kind']=='relation-kind'
                    and row['instance_discriminator']['value']==subject['record']['schema_version']]
                source.require(len(matches)==1,'oracle carrier missing');c=matches[0]
            digest=source.sha(view.handle.common.encoded(subject['record'])) if subject['source'].get('selector') else subject['source']['sha256']
            return {'scope_ref':view.data['config']['scope_ref'],'identity_ref':subject['identity'],'version_ref':subject['version_ref'],
                'carrier_ref':c,'byte_sha256':digest}
        all_headers=[header(subject) for _,subject in sorted(view.subjects.items())]
        warm=None;cold=None
        for name,request,reply in replies:
            if reply['kind']!='result':continue
            value=reply['message'];operation=request['operation']
            if operation=='lab.status':check(name+': actual four-handler scope',value['supported_operations']==list(SUPPORTED))
            if operation=='artifact.query':
                check(name+': query applied/requested cuts exact',value['source_cut']==value['requested_source_cut']==request['message']['source_cut'])
                if len(value['results'])==508:
                    check(name+': all exact revisions equal cold signed replay',value['results']==all_headers)
                    if name=='inspection-and-sql-query' and value['query_basis']=='projection':warm=value
                    if name=='cold-query-rebuild':cold=value
                for h in value['results']:
                    # Historical prefix excludes later subjects but each captured
                    # revision's exact metadata must match the original signed cut.
                    check(name+': exact query reference '+h['version_ref'],header(view.subjects[h['version_ref']])==h)
            if operation=='artifact.inspect':
                h=value['artifact'];subject=view.subjects[h['version_ref']]
                check(name+': exact inspected identity',header(subject)==h and value['status_facets']['admission']==subject['effective_state'])
                if value['envelope'] is not None:
                    envelope=value['envelope'];check(name+': original captured body',envelope['decoded_artifact']['body']==subject['record'])
                    if subject['source'].get('selector'):raw=view.handle.common.encoded(subject['record'])
                    else:raw=source.original({'path':subject['source']['path'],'sha256':subject['source']['sha256']})
                    check(name+': encoded original bytes/size',envelope['content']['byte_sha256']==source.sha(raw)
                        and envelope['content']['size_bytes']==len(raw) and envelope['artifact']==h)
                else:check(name+': excluded body genuinely absent','body' not in value['included_sections'])
                for section,key in [('contract','contract_binding'),('authority','authority_bindings'),('provenance','provenance_bindings'),('evidence','evidence_bindings'),('relations','connections'),('gaps','gaps')]:
                    if section not in value['included_sections']:check(name+': excluded '+section+' absent',value[key] is None if section=='contract' else value[key]==[])
        check('cold independent SQL rebuild retains references with new generation',warm is not None and cold is not None
            and warm['results']==cold['results'] and warm['projection_generation']!=cold['projection_generation'])
        historic=[reply['message'] for name,request,reply in replies if name=='historical-query' and request['operation']=='artifact.query' and reply['kind']=='result']
        check('exact historical queries disclose independent earlier cut',len(historic)==2 and all(len(row['results'])==485 and row['freshness']=='historical' and row['source_cut']['commit_sequence']==0 for row in historic))
    for tree in [HERE,EXAMPLE_ROOT/'0009',EXAMPLE_ROOT/'0010',EXAMPLE_ROOT/'0006',EXAMPLE_ROOT/'0007']:
        for path in tree.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path not in [output,HERE/'receipts/validation.stdout',HERE/'receipts/validation.stderr']:evidence(path)
    for b in files.values():source.original(b)
    result={'schema_version':'lab-R03-exact-reader-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Four real authenticated read handlers and exact selected canonical/SQLite parity only; descriptor/root and connection gaps, full R03, other APIs and actual owner/human pilot requirements remain.',
        'verified_obligation_ids':['Q1','Q2','Q3','Q4'],'tests':104,'fresh_child_processes':11,'observed_frames':frames_total,
        'observed_api_replies':len(replies),'verified_authenticated_handshakes':handshakes,
        'implemented_operations':list(SUPPORTED),'remaining_operations':30,'declared_operations':34,
        'current_cut_revisions':508,'historical_cut_revisions':485,'body_contract_gaps':133,'closed_connections':45,'unclosed_connections':10,'ambiguous_current_heads':1,
        'checks':checks,'source_drift':[],'canonical_effects_applied':0,'local_authoring_transactions_applied':0,'human_pilot':False,
        'private_keys_exported':False,'Session_memory_exported':False,'prior_reader_proof':source.bind(HERE.parent/'api/receipts/R03-0003.json'),
        'remaining_obligations':['Implement all remaining 30 original API handlers and complete the full R03 operator/Agent/session journey.',
            'Resolve exact descriptor-envelope body/root mismatch for 133 captured descriptors, ten unclosed connections and the ambiguous current-head identity without inventing authority or collapsing types.',
            'Complete broader persistent SQLite/query/ontology parity, candidate queues, Decision evidence and workflow integration; current disposable generations cover selected captured archives only.',
            'Close full W07, remaining DAG tasks, S02 exact package, actual human pilot/R08 response and A01-A04 boundaries.'],
        'preserved_failed_observations':['Initial projector rejected ambiguous current-head uniqueness; preserved all revisions and declared ambiguity instead of selecting a false head.',
            'New fixture incorrectly selected a nonexistent local Work; corrected to the actual original signed Evidence Set.',
            'Signature adapter collapsed semantic lookup key into Relation Kind subject identity; corrected using exact original record and source byte binding.'],
        'files':sorted(files.values(),key=lambda b:b['path']),'duration_seconds':time.perf_counter()-start}
    with output.open('xb') as stream:stream.write(source.encoded(result))
    print(json.dumps({'result':'PASS','task':'R03','task_complete':False,'tests':104,'children':11,'frames':frames_total,
        'replies':len(replies),'files':len(files),'receipt':source.bind(output),'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':main()
