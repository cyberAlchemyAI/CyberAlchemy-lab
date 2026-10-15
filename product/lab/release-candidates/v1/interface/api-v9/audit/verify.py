"""Independent exact profile, original-wire, source, dependency and custody checks."""
import base64
import importlib.metadata
import json
from pathlib import Path
import re
import sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from protocol import *
from workspace import privacy

EXPECTED_PROFILE='bee1104a921bd6b189eb281a48611f815a26b4898939a63372069445470cfa00'
checks=[]
def check(name,value):
    checks.append({'test':name,'result':'PASS' if value else 'FAIL'});source.require(value,name)
def load(path):return source.parse(Path(path).read_bytes())

def main():
    schemas=Schemas(EXPECTED_PROFILE)
    for name in ('source-manifest.json','derived-manifest.json'):
        doc=load(BASE/name)
        for b in doc['files']:source.original(b)
        check('exact frozen '+name,doc['authority_effect']=='none' and doc['actual_owner_outcome'] is None)
    env=load(BASE/'dependency-selection.json')
    check('exact selected dependency environment',all(importlib.metadata.version(k)==v for k,v in env['distributions'].items())
        and env['distributions']['jsonschema']=='4.23.0')
    check('exact additional codec bytes',source.sha((source.ROOT/env['additional_codec']['path']).read_bytes())==env['additional_codec']['sha256'])
    check('original complete API catalog retained',len(schemas.operations)==34 and schemas.profile['implemented_operations']==list(SUPPORTED) and len(SUPPORTED)==7)
    tests=load(BASE/'receipts/attempts/0002/terminal.json');regression=load(BASE/'receipts/parent-regression/0001/terminal.json')
    check('selected complete new test producer terminal',tests['result']=='PASS' and tests['producer_exit_code']==0 and tests['tests_run']==43)
    check('immutable four-reader parent regression terminal',regression['result']=='PASS' and regression['producer_exit_code']==0 and regression['tests_run']==157)
    proof=load(BASE/'receipts/processes/0001/result.json')
    check('all actual stdio producers terminal',proof['result']=='PASS' and len(proof['children'])==7 and all(c['terminal'] for c in proof['children']))
    check('two actual process interruptions verified',sum(c['exit_code']==-9 and c['intentional_interruption'] for c in proof['children'])==2)
    check('owned custody ended with no Agent memory/key export',proof['owned_fixture_roots_removed'] and proof['active_Sessions_created']==0
        and not proof['Session_memory_exported'] and not proof['private_keys_exported'] and proof['canonical_effects_applied']==0)
    evidence={}
    for b in proof['eligible_evidence_file_bindings']:
        raw=source.original(b);privacy(source.parse(raw));evidence[b['path']]=raw
    check('all eligible input/effect/result bytes independently retained',len(evidence)>30)
    wire_calls={};replies=[];count=0
    for b in proof['transcript_bindings']:
        transcript=load(source.ROOT/b['path']);source.original(b);last=None;context=None
        for row in transcript['frames']:
            raw=base64.b64decode(row['base64_original_bytes'],validate=True);value=frame_parse(raw)
            check('wire original byte identity '+str(count),source.sha(raw)==row['sha256']);count+=1
            privacy(value)
            if row['direction']=='request':
                last=raw
                if value.get('schema_version')=='lab-api-call/v2-candidate':
                    check('exact call contract '+value['call_id'],schemas.valid('api-call',value))
                    wire_calls[source.sha(raw)]=raw
                else:check('exact authentication proof',schemas.valid('reader-authentication',value))
            elif value.get('schema_version')=='lab-local-reader-authenticated/v1-candidate':
                context=value['context'];check('exact verified authentication response',schemas.valid('reader-authentication',value))
            elif value.get('schema_version')=='lab-api-reply/v2-candidate':
                original=frame_parse(last);check('exact reply/domain/error contract '+value['call_id'],schemas.valid('api-reply',value))
                check('wire reply binding '+value['call_id'],value['request_binding']['sha256']==source.sha(last)
                    and value['operation']==original['operation'] and value['call_id']==original['call_id'])
                check('exact current trusted channel binding '+value['call_id'],value['trusted_context_binding']==binding(context['context_ref'],compact(context))
                    and value['contract_profile_binding']==schemas.profile_binding)
                replies.append((original,value))
            else:check('exact host challenge',schemas.valid('reader-authentication',value))
    check('actual seven producers include complete original API wires',len(wire_calls)>=12)
    for request,reply in replies:
        if reply['kind']=='error':continue
        domain=reply['message'];operation=request['operation']
        if operation in ('change.prepare','change.validate'):
            b=domain['proposal_binding'] if operation=='change.prepare' else domain['subject_binding']
            check('exact original domain proposal bytes '+operation,b['sha256']==source.sha(message_bytes(wire_calls[reply['request_binding']['sha256']])))
        elif operation=='operation.inspect':
            original=domain['original_call_binding'];check('independent invocation lookup original wire',original['sha256'] in wire_calls)
            if domain['posture']=='completed':
                digest=domain['result_binding']['sha256'];matches=[raw for path,raw in evidence.items() if path.endswith('/objects/'+digest+'.json')]
                check('exact durable completed domain result',bool(matches) and all(source.sha(raw)==digest for raw in matches))
    check('construction and semantic statuses remain orthogonal',any(r['message'].get('result')=='not-evaluable' for q,r in replies)
        and any(r['message'].get('posture')=='blocked' for q,r in replies)
        and any(r['message'].get('posture')=='indeterminate' for q,r in replies))
    check('final approval and full R03 remain absent',proof['actual_owner_outcome'] is None and proof['task_complete'] is False)
    result={'schema_version':'lab-R03-preparation-independent-audit/v1-candidate','result':'PASS','checks':checks,
        'profile_binding':source.bind(BASE/'contract-profile.json'),'producer_binding':source.bind(Path(__file__).resolve()),
        'evidence_file_count':len(evidence),'wire_frame_count':count,'api_call_count':len(wire_calls),
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    output=BASE/'audit/result.json';source.require(not output.exists(),'audit result already exists');output.write_bytes(source.encoded(result))
    print(json.dumps({'result':'PASS','checks':len(checks),'wire_frames':count,'original_calls':len(wire_calls)}))

if __name__=='__main__':main()
