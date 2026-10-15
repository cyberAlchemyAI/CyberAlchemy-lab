#!/usr/bin/env python3
"""Offline API contract authoring checks; no handlers, persistent stores or runtime tests."""
import copy,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,unquote
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Resource
from referencing.jsonschema import DRAFT202012
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE.parent/'0007-lab-integrated-schema-package'
sys.path.insert(0,str(SOURCE))
from resources import build_registry

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)

def main():
    checks=[]
    def passed(name,**detail):checks.append({'check':name,'result':'pass',**detail})
    c=read(HERE/'api-contracts.json');ops=c['operations'];by_name={o['operation']:o for o in ops}
    source_receipt=read(SOURCE/'receipts/schema-authoring.json');source_baseline=read(SOURCE/'SOURCE-BASELINE.json')
    paths={ROOT/e['path'] for e in source_baseline['sources']+source_receipt['package_manifest']}
    paths.add(SOURCE/'receipts/schema-authoring.json')
    for e in source_baseline['sources']+source_receipt['package_manifest']:require(sha(ROOT/e['path'])==e['sha256'],'schema source drift '+e['path'])
    preserve=[]
    for version in ['v1','v2']:
        receipt=read(ROOT/'implementation/lab-runtime'/version/'receipts/validation.json')
        for b in receipt['source_manifest']:
            p=ROOT/b['path'];require(sha(p)==b['sha256'],'frozen runtime source drift '+b['path']);paths.add(p)
        preserve.append({'version':version,'files':len(receipt['source_manifest']),'source_manifest_digest':receipt['source_manifest_digest']})
    baseline_entries=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in sorted(paths)]
    baseline={'schema_version':'lab-api-source-baseline/v1-candidate','authority_effect':'none','sources':baseline_entries,'source_manifest_digest':digest(baseline_entries)}
    (HERE/'SOURCE-BASELINE.json').write_text(json.dumps(baseline,indent=2,sort_keys=True)+'\n')
    passed('exact-schema-package-and-source-closure',source_files=len(paths),schema_authoring_result=source_receipt['result'],source_manifest_digest=baseline['source_manifest_digest'])
    for key in ['call_schema_binding','reply_schema_binding','transport_error_schema_binding','trusted_context_schema_binding','schema_package_binding','schema_review_binding','schema_authoring_receipt_binding']:
        b=c[key];require(sha(ROOT/b['ref'])==b['sha256'],'API package binding drift '+key)
    passed('contract-catalog-exact-input-bindings',bindings=7)
    registry=build_registry();schemas={}
    for f in sorted((HERE/'schemas').glob('*.schema.json')):
        s=read(f);Draft202012Validator.check_schema(s);schemas[f.stem.removesuffix('.schema')]=s;registry=registry.with_resource(s['$id'],Resource.from_contents(s))
    registry=registry.crawl();ref_count=0
    def refs(v,resolver):
        nonlocal ref_count
        if isinstance(v,dict):
            if '$id' in v:resolver=resolver.in_subresource(Resource.from_contents(v,default_specification=DRAFT202012))
            if '$ref' in v:resolver.lookup(v['$ref']);ref_count+=1
            for k,x in v.items():
                if k!='$id':refs(x,resolver)
        elif isinstance(v,list):
            for x in v:refs(x,resolver)
    for s in schemas.values():refs(s,registry.resolver(base_uri=s['$id']))
    passed('api-schema-meta-and-offline-ref-resolution',api_schemas=len(schemas),reference_occurrences=ref_count,network_retrieval=False)
    checker=FormatChecker()
    def valid(name,data):return Draft202012Validator(schemas[name],registry=registry,format_checker=checker).is_valid(data)
    require(valid('api-contract-catalog',c),'invalid machine-readable API catalog')
    services=read(SOURCE/'service-contracts.json')['operations'];service_map={o['operation']:o for o in services}
    require(len(by_name)==len(ops)==34 and set(by_name)==set(service_map),'operation coverage')
    require(len(schemas['api-call']['oneOf'])==34 and len(schemas['api-reply']['oneOf'])==68,'envelope dispatcher coverage')
    source_catalog=read(SOURCE/'schema-catalog.json');all_error_codes=set(read(SOURCE/'schemas/error-result.schema.json')['properties']['code']['enum'])
    for o in ops:
        require(read(HERE/'operations'/f'{o["operation"]}.json')==o,'operation record drift')
        for left,right in [('request_schema','request_schema'),('result_schema','success_schema'),('error_schema','error_schema')]:
            b=o[left];require(b['resource_uri']==service_map[o['operation']][right] and sha(ROOT/b['ref'])==b['sha256'],'operation schema binding drift')
            registry.resolver().lookup(b['resource_uri'])
        require(o['authority']['caller_requirement']==service_map[o['operation']]['caller_requirement'],'caller route mismatch')
        require(set(o['allowed_error_codes'])<=all_error_codes,'undeclared error code')
        require(o['idempotency_required']==(o['effect_kind']!='read-only'),'effect/key policy mismatch')
        require('source-profile' not in o['idempotency_namespace'],'profile must not bypass existing key namespace')
        require(o['repository_admission_possible']==(o['operation']=='admission.apply'),'authority effect collapsed')
        require(o['runtime_activations']==0 and not o['external_effect_refs'],'scope expansion')
    passed('closed-operation-contract-coverage',operations=34,reviewed_protocol_schemas=len(source_catalog['protocols']),domain_versions=source_catalog['registered_artifact_versions'])
    index=read(HERE/'examples/index.json')['examples'];require({x['operation'] for x in index}==set(by_name),'example operation coverage')
    message_count=0
    for e in index:
        op=by_name[e['operation']];call=read(HERE/e['request']);reply=read(HERE/e['response']);failed=read(HERE/e['error_response']);message=read(HERE/e['message'])
        require(valid('api-call',call),'invalid call '+e['operation'])
        require(valid('api-reply',reply) and valid('api-reply',failed),'invalid replies '+e['operation'])
        require(call['message']==message,'domain request material differs from embedded message')
        require(call['operation']==e['operation'] and call['call_id']==reply['call_id']==failed['call_id'],'call correlation')
        require(reply['operation']==failed['operation']==call['operation'],'operation correlation')
        require(sha(HERE/e['request'])==e['wire_request_sha256']==reply['request_binding']['sha256']==failed['request_binding']['sha256'],'wire digest correlation')
        require(sha(HERE/e['message'])==e['message_sha256']==failed['message']['request_binding']['sha256'],'separate message binding')
        if 'request_binding' in reply['message']:require(reply['message']['request_binding']['sha256']==e['message_sha256'],'inner message digest collapsed with outer call')
        if op['inner_idempotency_selector']:require(message['idempotency_key']==call['idempotency_key'],'nested command key mismatch')
        if op['source_cut_selectors']:
            primary=message[op['source_cut_selectors'][0].removeprefix('/')]
            require(primary==call['expected_source_cut'],'primary cut envelope mismatch')
        if op['operation']=='artifact.inspect' and reply['message']['envelope'] is not None:
            require(message['artifact']==reply['message']['artifact']==reply['message']['envelope']['artifact'],'inspection artifact header/body mismatch')
        trusted=read(HERE/'examples/trusted-context.json')
        if 'actor' in message:require(message['actor']['principal_ref']==trusted['principal_ref'],'illustrative actor mismatch')
        require(call['caller_context_ref']==trusted['context_ref'] and reply['trusted_context_binding']['sha256']==sha(HERE/'examples/trusted-context.json'),'illustrative context binding')
        payload={'api_version':c['api_version'],'operation':op['operation'],'authenticated_principal_ref':trusted['principal_ref'],'authority_scope':trusted['authority_scope'],'selected_scope_refs':trusted['scope_refs'],'source_profile_binding':trusted['source_profile_binding'],'expected_source_cut':call['expected_source_cut'],'message':message}
        subset=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
        require(hashlib.sha256(subset).hexdigest()==e['illustrative_subset_fingerprint_sha256'],'illustrative fingerprint binding')
        message_count+=4
    require(valid('trusted-call-context',read(HERE/'examples/trusted-context.json')),'invalid trusted context shape')
    require(valid('transport-error',read(HERE/'examples/transport-malformed.json')) and valid('transport-error',read(HERE/'examples/transport-uncertain-timeout.json')),'invalid transport example')
    passed('operation-examples-and-byte-correlation',operation_messages=message_count,transport_examples=2,context_examples=1,actual_authority_or_handler_execution_established=False,general_jcs_codec_verified=False)
    negative=[]
    def reject(case,name,value):require(not valid(name,value),'invalid shape admitted: '+case);negative.append(case)
    a=read(HERE/'examples/action.dispatch/request.json');a['idempotency_key']=None;reject('effectful-call-without-key','api-call',a)
    a=read(HERE/'examples/artifact.query/request.json');a['idempotency_key']='example:write-key';reject('read-call-with-command-key','api-call',a)
    a=read(HERE/'examples/artifact.query/request.json');a['operation']='example:undeclared';reject('unknown-operation','api-call',a)
    a=read(HERE/'examples/artifact.query/request.json');a['max_response_bytes']=1;reject('undersized-response-ceiling','api-call',a)
    a=read(HERE/'examples/release.prepare/request.json');a['message']['posture']='approved-exact-scope';reject('release-preparation-as-existing-approval','api-call',a)
    a=read(HERE/'examples/artifact.query/request.json');a['client_authority']={'is_owner':True};reject('client-supplied-extra-authority','api-call',a)
    a=read(HERE/'examples/transport-uncertain-timeout.json');a['recovery_policy']='no-retry';reject('uncertain-effect-without-inspection','transport-error',a)
    a=read(HERE/'examples/transport-malformed.json');a['effect_may_have_started']=True;a['recovery_policy']='inspect-first';reject('malformed-input-as-dispatched-effect','transport-error',a)
    a=read(HERE/'examples/trusted-context.json');a['accept_client_supplied_authority_context']=True;reject('trust-client-authority-context','trusted-call-context',a)
    a=read(HERE/'examples/action.dispatch/error-response.json');a['message'].update(code='indeterminate',retry_policy='idempotent-retry');reject('blind-retry-after-uncertain-dispatch','api-reply',a)
    passed('selected-invalid-api-shapes-rejected',cases=negative,runtime_tests_run=False)
    workflows=read(SOURCE/'workflow-catalog.json')['workflows']
    require(all(not read(SOURCE/w['path'])['domain_mapping_bindings'] for w in workflows),'template execution claim changed')
    require(c['implementation_status']=='not-implemented-by-this-package' and not c['transport']['network_listener'],'implementation or deployment claim')
    passed('execution-and-authority-claim-boundaries',workflow_models=len(workflows),templates_executable=False,actual_owner_outcomes_generated=False,network_listener_created=False)
    passed('frozen-runtime-source-preservation',packages=preserve,runtime_suites_run=False)
    links=0
    for f in HERE.rglob('*.md'):
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)',f.read_text()):
            parsed=urlsplit(href.strip('<>'))
            if parsed.scheme or href.startswith('#'):continue
            target=(f.parent/unquote(parsed.path)).resolve()
            require(target.is_relative_to(ROOT),'external local path link '+href)
            require(target.exists() or target==HERE/'receipts/api-authoring.json','broken link '+str(f.relative_to(HERE))+' '+href)
            links+=1
    passed('local-document-navigation',links=links)
    files=[p for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'receipts/api-authoring.json']
    package=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in files]
    receipt={'schema_version':'lab-api-authoring-receipt/v1-candidate','generated_at':datetime.now(timezone.utc).isoformat(),'result':'pass','authority_effect':'none','repository_admission_effect':'none','runtime_effect':'none',
      'claim_ceiling':'Exact local contract/source bindings, schema/ref/catalog/example/selected-invalid-shape validation and illustrative byte correlation only; no real authentication/signature, JCS codec, application handler, idempotency store, crash recovery, semantic conformance, deployment, admission or operational acceptance.',
      'checks':checks,'source_manifest_digest':baseline['source_manifest_digest'],'schema_authoring_receipt_binding':c['schema_authoring_receipt_binding'],'package_manifest':package,'package_manifest_digest':digest(package)}
    (HERE/'receipts/api-authoring.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'pass','checks':len(checks),'api_operations':len(ops),'api_schemas':len(schemas),'operation_messages':message_count,'source_files':len(paths),'package_files':len(files),'package_manifest_digest':receipt['package_manifest_digest']}))

if __name__=='__main__':main()
