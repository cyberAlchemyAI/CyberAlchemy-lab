#!/usr/bin/env python3
"""Check candidate schema authoring only; no runtime actions or persistent DB."""
import hashlib,json,re,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,unquote
from jsonschema import Draft202012Validator,FormatChecker,validators
from referencing import Resource
from referencing.jsonschema import DRAFT202012
from resources import HERE,ROOT,build_registry

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def require(v,message):
    if not v:raise ValueError(message)

def main():
    checks=[]
    def passed(name,**detail):checks.append({'check':name,'result':'pass',**detail})
    cat=read(HERE/'schema-catalog.json');bindings=read(HERE/'domain-bindings.json')['bindings']
    baseline=read(HERE/'SOURCE-BASELINE.json')
    for b in baseline['sources']:
        p=ROOT/b['path'];require(p.is_file() and sha(p)==b['sha256'] and p.stat().st_size==b['size_bytes'],'source drift: '+b['path'])
    require(digest(baseline['sources'])==baseline['source_manifest_digest'],'source manifest digest')
    passed('exact-source-baseline',files=len(baseline['sources']),digest=baseline['source_manifest_digest'])
    registry_source=read(ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json')
    entries={e['artifact_type_ref']:e for e in registry_source['admitted_contracts']};current=set(registry_source['current_by_identity'].values())
    require({b['carrier_ref'] for b in bindings}==set(entries),'domain registry coverage')
    for b in bindings:
        e=entries[b['carrier_ref']]
        for left,right in [('schema_path','schema_path'),('schema_sha256','schema_sha256'),('descriptor_path','artifact_path'),('descriptor_sha256','artifact_sha256'),('semantic_kind','semantic_kind'),('schema_selector','schema_selector')]:
            require(b.get(left)==e.get(right),'domain binding mismatch '+b['carrier_ref']+' '+left)
        require(b['write_posture']==('current' if b['carrier_ref'] in current else 'historical-read-only'),'write posture mismatch')
    passed('domain-carrier-coverage',registered_versions=len(bindings),current=len(current),historical=len(bindings)-len(current))
    reg=build_registry();files=set((HERE/'schemas').glob('*.schema.json'))
    files.update(ROOT/b['schema_path'] for b in bindings)
    files.update(ROOT/b['path'] for b in cat['reused_storage_schemas'])
    files.add(ROOT/cat['ephemeral_memory_binding']['path'])
    deps=read(HERE/'schema-dependencies.json')['bindings'];files.update(ROOT/b['target_path'] for b in deps)
    for p in files:validators.validator_for(read(p),default=Draft202012Validator).check_schema(read(p))
    passed('json-schema-meta-validation',candidate_protocols=len(cat['protocols']),unique_schema_files=len(files))
    ref_count=0
    def refs(v,resolver):
        nonlocal ref_count
        if isinstance(v,dict):
            if '$id' in v:resolver=resolver.in_subresource(Resource.from_contents(v,default_specification=DRAFT202012))
            if '$ref' in v:resolver.lookup(v['$ref']);ref_count+=1
            for k,x in v.items():
                if k!='$id':refs(x,resolver)
        elif isinstance(v,list):
            for x in v:refs(x,resolver)
    for p in files:
        raw=read(p)
        uri=raw['$id'] if p.parent==HERE/'schemas' else p.resolve().as_uri()
        # Reused storage and memory resources are registered by their pinned ids.
        if p.parent!=HERE/'schemas' and p not in {ROOT/b['schema_path'] for b in bindings} and p not in {ROOT/b['target_path'] for b in deps}:
            uri=next((b['resource_uri'] for b in cat['reused_storage_schemas'] if ROOT/b['path']==p),cat['ephemeral_memory_binding']['resource_uri'])
        resolved=reg.resolver().lookup(uri)
        # Contents include only declared offline compatibility substitutions.
        refs(resolved.contents,resolved.resolver)
    for b in bindings:reg.resolver().lookup(b['schema_resource_uri']+(b['schema_selector'] or ''))
    passed('offline-reference-and-selector-resolution',reference_occurrences=ref_count,compatibility_mappings=len(deps),network_retrieval=False)
    fc=FormatChecker();example_count=0
    def validate(name,value):
        schema=read(HERE/'schemas'/f'{name}.schema.json')
        errors=list(Draft202012Validator(schema,registry=reg,format_checker=fc).iter_errors(value))
        require(not errors,name+' invalid: '+ '; '.join(str(list(e.path))+': '+e.message[:300] for e in errors[:3]))
    for b in cat['protocols']:
        require((HERE/b['path']).is_file(),'missing protocol')
        if b['name']=='common':continue
        validate(b['name'],read(HERE/'examples'/f'{b["name"]}.json'));example_count+=1
    validate('protocol-package-manifest',read(HERE/'package-manifest.json'))
    manifest=read(HERE/'package-manifest.json')
    for b in manifest['schema_bindings']+manifest['workflow_model_bindings']+[manifest['domain_catalog_binding'],manifest['obligation_catalog_binding'],manifest['source_baseline_binding']]:
        require(sha(ROOT/b['ref'])==b['sha256'],'package manifest binding drift '+b['ref'])
    require(manifest['authoring_receipt_binding'] is None,'receipt cycle')
    passed('illustrative-message-and-package-manifest-validation',examples=example_count,actual_candidate_manifest=True,authority_or_readiness_established=False)
    scenarios=read(HERE/'reviews/0001/schema-scenarios.json')['cases']
    for case in scenarios:
        schema=read(HERE/'schemas'/f"{case['schema']}.schema.json")
        actual=Draft202012Validator(schema,registry=reg,format_checker=fc).is_valid(case['instance'])
        require(actual==case['expected_valid'],'schema review scenario '+case['case'])
    passed('schema-review-0001-shapes',cases=len(scenarios),allowed=sum(c['expected_valid'] for c in scenarios),rejected=sum(not c['expected_valid'] for c in scenarios),runtime_behavior_established=False)

    coverage=read(ROOT/'docs/plans/0009-lab-integrated-roadmap/contract-coverage.json')
    dispatch=read(HERE/'schemas/typed-connection.schema.json')['oneOf']
    require(len(dispatch)==len(coverage['relations']),'relation dispatcher count')
    pairs=0
    for branch,r in zip(dispatch,coverage['relations']):
        p=branch['properties'];require(p['relation_kind_ref']['const']==r['ref'] and p['axis_ref']['const']==r['axis_id'] and p['signature_sha256']['const']==r['source_sha256'],'relation signature mismatch')
        expected=[{'properties':{'source':{'properties':{'semantic_kind':{'const':e['source_kind']}}},'target':{'properties':{'semantic_kind':{'const':e['target_kind']}}}}} for e in r['exact_endpoint_pairs']]
        require(branch['allOf']==[{'anyOf':expected}],'endpoint pair mismatch')
        require(p['qualifiers']['properties']==r['qualifier_contract']['properties'] and p['qualifiers']['required']==r['qualifier_contract']['required_axes'] and p['qualifiers']['additionalProperties'] is False,'qualifier shape mismatch')
        pairs+=len(expected)
    passed('exact-relation-dispatch-coverage',kinds=len(dispatch),pairs=pairs,semantic_fit_established=False)
    workflows=read(HERE/'workflow-catalog.json')['workflows']
    for w in workflows:
        m=read(HERE/w['path']);validate('workflow-definition',m);states=set(m['states'])
        require(m['initial_state'] in states and set(m['terminal_states'])<=states,'workflow states')
        require(len({t['transition_ref'] for t in m['transitions']})==len(m['transitions']),'duplicate transition')
        for t in m['transitions']:
            require({t[k] for k in ['from_state','to_state','failure_state','indeterminate_state']}<=states,'transition states')
            require(set(t['input_carriers']+t['output_carriers'])<=current,'non-current workflow carrier')
        require(m['single_goal_coordination'] is True and m['domain_mapping_bindings']==[],'template posture changed')
    passed('workflow-model-authoring',models=len(workflows),domain_lifecycle_bindings_complete=False,executable=False)
    ops=read(HERE/'service-contracts.json')['operations'];require(len({o['operation'] for o in ops})==len(ops),'duplicate operation')
    req=read(HERE/'schemas/tool-service-request.schema.json')['oneOf'];res=read(HERE/'schemas/tool-service-result.schema.json')['oneOf']
    require(len(req)==len(res)==len(ops),'service dispatcher length')
    for operation,r,s in zip(ops,req,res):
        for key in ['request_schema','success_schema','error_schema']:reg.resolver().lookup(operation[key])
        require(r['properties']['operation']['const']==s['properties']['operation']['const']==operation['operation'],'operation dispatch')
        require(r['properties']['message']['$ref']==operation['request_schema'],'request dispatch')
        require(s['properties']['message']['oneOf']==[{'$ref':operation['success_schema']},{'$ref':operation['error_schema']}],'result dispatch')
    obligations=read(HERE/'obligations.json')['obligations'];obligation_ids={o['obligation_ref'] for o in obligations}
    require({o for p in cat['protocols'] for o in p['runtime_obligations']}==obligation_ids,'runtime obligation coverage')
    for p in cat['protocols']:require(set(p['domain_carriers'])<=set(entries),'unbound domain carrier in catalog '+p['name'])
    passed('service-and-obligation-catalog-coverage',operations=len(ops),obligations=len(obligations),services_implemented=False)
    db=sqlite3.connect(':memory:');db.executescript((ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/sqlite-read-model.sql').read_text())
    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    require(len(tables)==12,'SQL table count');db.close()
    passed('reused-sql-ddl-authoring',tables=len(tables),sqlite_version=sqlite3.sqlite_version,persistent_database_created=False)
    preserved=[]
    for version in ['v1','v2']:
        receipt=read(ROOT/'implementation/lab-runtime'/version/'receipts/validation.json')
        for b in receipt['source_manifest']:require(sha(ROOT/b['path'])==b['sha256'],'frozen runtime drift '+b['path'])
        preserved.append({'version':version,'source_files':len(receipt['source_manifest']),'source_manifest_digest':receipt['source_manifest_digest']})
    passed('frozen-runtime-source-preservation',packages=preserved,runtime_tests_run=False)
    link_count=0
    for p in HERE.rglob('*.md'):
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            href=href.strip('<>');url=urlsplit(href)
            if url.scheme or href.startswith('#'):continue
            target=(p.parent/unquote(url.path)).resolve()
            require(target.is_relative_to(ROOT),'link escapes repo '+href)
            require(target.exists() or target==HERE/'receipts/schema-authoring.json','broken local link '+str(p.relative_to(HERE))+' '+href)
            link_count+=1
    passed('local-document-links',links=link_count)
    files=[p for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'receipts/schema-authoring.json']
    package_manifest=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in files]
    result={'schema_version':'lab-integrated-schema-authoring-receipt/v1-candidate','generated_at':datetime.now(timezone.utc).isoformat(),'result':'pass','authority_effect':'none','repository_admission_effect':'none','runtime_effect':'none',
        'claim_ceiling':'Offline schema and model authoring, exact local bindings, illustrative message validation and in-memory SQL DDL compilation only; no authority verification, semantic noncollapse verdict, runtime implementation verification, operational pilot, admission, migration or release acceptance.',
        'checks':checks,'source_manifest_digest':baseline['source_manifest_digest'],'package_manifest':package_manifest,'package_manifest_digest':digest(package_manifest)}
    (HERE/'receipts/schema-authoring.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'pass','checks':len(checks),'candidate_protocols':len(cat['protocols']),'examples':example_count,'workflows':len(workflows),'package_files_bound':len(files),'package_manifest_digest':result['package_manifest_digest']}))

if __name__=='__main__':main()
