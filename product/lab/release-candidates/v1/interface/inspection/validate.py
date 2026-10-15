"""Verify exact CLI examples and original evidence; R03 stays incomplete."""
import ast
import base64
import json
import re
import time
from pathlib import Path
from collections import Counter
from jsonschema import Draft202012Validator
import lab_operator as op

RUN=op.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
EXAMPLES=op.ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/inspection/0001'


def main():
    start=time.perf_counter();output=op.HERE/'receipts/R03-0002.json'
    op.require(not output.exists(),'immutable receipt already exists')
    files={};checks=[]
    def evidence(path):
        b=op.bind(path);old=files.get(b['path']);op.require(old is None or old==b,'conflicting source binding')
        op.original(b);files[b['path']]=b
        return op.parse(Path(path).read_bytes()) if Path(path).suffix=='.json' else Path(path).read_bytes()
    def bound(b):
        op.require(op.sha((op.ROOT/b['path']).read_bytes())==b['sha256'],'source drift: '+b['path'])
        return evidence(op.ROOT/b['path'])
    def check(name,value):
        op.require(value,name);checks.append({'test':name,'result':'PASS'})
    manifest=evidence(op.HERE/'manifest.json')
    for b in manifest['files']:bound(b)
    context=evidence(RUN/'context-R03-inspection.json');evidence(RUN/'CONTEXT-R03-INSPECTION.md')
    for b in context['source_bindings']:
        v=bound(b)
        if isinstance(v,dict):
            for key in ['files','source_files','source_bindings']:
                for item in v.get(key,[]):
                    if isinstance(item,dict) and {'path','sha256'}<=item.keys():bound(item)
    check('original full obligations remain explicit',len(context['obligations'])==5 and 'full R03' in context['claim_ceiling'])
    testlog=(op.HERE/'receipts/attempts/0002/tests.stderr').read_text()
    cases=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',testlog,re.MULTILINE)
    declared=sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse((op.HERE/'test_inspection.py').read_text())))
    check('complete 49-check suite passed',len(cases)==declared==49
        and re.search(r'Ran 49 tests in [0-9.]+s\n\nOK\n',testlog) is not None)
    checks.extend({'suite':'inspection-guards','test':name,'result':'PASS'} for name,_ in cases)
    schema=evidence(op.HERE/'report.schema.json');Draft202012Validator.check_schema(schema)
    checker=Draft202012Validator(schema)
    execution=evidence(EXAMPLES/'execution.json')
    check('all twelve fresh CLI episodes terminal PASS',execution['result']=='PASS' and len(execution['examples'])==12
        and all(r['exit_code']==0 for r in execution['examples']) and execution['human_pilot'] is False)
    reports={}
    for row in execution['examples']:
        stdout=EXAMPLES/(row['name']+'.stdout');stderr=EXAMPLES/(row['name']+'.stderr')
        check(row['name']+': exact original CLI output',op.sha(stdout.read_bytes())==row['stdout_sha256']
            and op.sha(stderr.read_bytes())==row['stderr_sha256'] and stderr.read_bytes()==b'')
        report=op.parse(stdout.read_bytes());reports[row['name']]=report
        check(row['name']+': six-branch CLI schema valid',checker.is_valid(report))
        check(row['name']+': actual bounded pinned cut',report['currentness']['status']=='current'
            and report['authority_effect']=='none' and report['actual_owner_outcome'] is None
            and report['source_cut']['signed_head']==op.source_selection(report['selected_source'])['expected_head'])
        from render import readable
        check(row['name']+': exact readable explanation', (EXAMPLES/(row['name']+'.txt')).read_text()==readable(report))
    # Independent original registry comparison, rather than a second invocation
    # of the same list method as the sole oracle.
    selection=op.source_selection('engineering')
    archive=op.parse(op.original(selection['archive_binding']))
    baseline=op.parse(base64.b64decode(archive['files']['baseline.json']['base64_original_bytes'],validate=True))
    registry_path='authority/definitions/registry.json'
    registry_binding={'path':registry_path,'sha256':baseline['materials'][registry_path]}
    registry=op.parse(op.original(registry_binding));bound(registry_binding)
    expected_current=set(registry['current_lookup'].values())
    expected_all={r['definition_id']+'@'+r['version'] for r in registry['entries']}
    check('current Definitions match independently captured registry',
        {r['version_ref'] for r in reports['definitions-current']['items']}==expected_current
        and len(expected_current)==183)
    check('historical Definitions match independently captured registry',
        {r['version_ref'] for r in reports['definitions-historical']['items']}==expected_all-expected_current
        and len(expected_all)==189)
    check('empty unadmitted selection does not assert global absence',reports['definitions-unadmitted']['total']==0
        and 'does not prove' in reports['definitions-unadmitted']['coverage'])
    for name in ['current-definition','historical-definition']:
        v=reports[name];binding=v['artifact']['source_binding']
        check(name+': original body bytes and effective admission independent',v['body']==op.parse(op.original(binding))
            and v['artifact']['status_facets']['admission']==('admitted-current' if name=='current-definition' else 'admitted-historical')
            and '/candidates/' in binding['path'])
        bound(binding)
    tx=op.parse(base64.b64decode(archive['files']['transactions/0000000001.json']['base64_original_bytes'],validate=True))
    review=reports['recorded-review'];receipt=reports['recorded-receipt']
    check('recorded target and independent Decision scopes exact',
        [r['target_ref'] for r in review['targets']]==[t['version_ref'] for t in tx['proposal']['targets']]
        and [r['decision_core'] for r in review['targets']]==tx['decision_cores']
        and review['effects']==tx['consequences']['admission_transaction']['payload']['admission_targets'])
    check('original receipt and why-path exact',receipt['application_receipt']==tx['consequences']['receipt']
        and receipt['approval']==tx['approval'] and receipt['transaction_digest']==tx['digest']
        and receipt['transaction_file_sha256']==archive['files']['transactions/0000000001.json']['sha256']
        and len(receipt['why_path'])==6)
    check('no final owner response or API implementation inferred',review['final_owner_review'] is False
        and reports['status']['api_operations_implemented']==[] and reports['status']['remaining_api_operations']==34)
    for name,kind in [('project-connections','project'),('product-connections','product')]:
        rows=reports[name]['connections']
        check(name+': exact raw/represented endpoint and direction preserved',any(r['target']['kind']==kind
            and r['validation_posture']=='validated-selected-cut'
            and r['endpoint_views'][1]['carrier_kind']==kind+'-identity'
            and r['endpoint_views'][1]['represented_endpoint_kind']==kind for r in rows))
    # Fresh signature replay at proof closure; no authoring transaction rerun.
    with op.replay_source('engineering') as view:
        check('proof closure independently replays original signatures',view.data['head']['transaction_digest']==selection['expected_head'])
    for tree in [op.HERE,EXAMPLES]:
        for p in tree.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p not in [op.HERE/'receipts/validation.stdout',op.HERE/'receipts/validation.stderr']:
                evidence(p)
    for b in files.values():op.original(b)
    durations=[r['duration_seconds'] for r in execution['examples']]
    result={'schema_version':'lab-R03-operator-inspection-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Six usable private candidate CLI read journeys and exact signed-source examples only; all 34 APIs, authenticated stdio, SQLite joins, complete third owner journey and human pilot remain incomplete.',
        'verified_obligation_ids':['J1','J2','J3','J4'],'tests':49,'checks':checks,'fresh_cli_examples':12,
        'definition_counts':{'admitted-current':183,'admitted-historical':6},'source_profile_cut_definition_revisions':189,
        'canonical_effects_applied':0,'local_authoring_transactions_applied':0,'original_domain_cases_reexecuted':0,'human_pilot':False,
        'measurement':{'python':__import__('sys').version,'example_duration_seconds_total':sum(durations),'example_duration_seconds_min':min(durations),'example_duration_seconds_max':max(durations),'sla_established':False},
        'prior_signed_coupling_proof':op.bind(op.HERE.parent/'coupling/receipts/R03-0001.json'),
        'preserved_failed_observations':['Initial operator.py entrypoint shadowed the Python standard operator module; renamed before evidence capture.',
            'First suite: 47 checks, one failure/eight errors. Corrected encoded byte digest versus structural digest, explicit historical-read flag and Decision core field selector; complete 49-check successor passed.'],
        'remaining_obligations':['Finish actual authenticated local API/stdio and all 34 exact handler result/error contracts; this CLI implements no API handler.',
            'Integrate complete candidate catalog/queue and exact Decision evidence closure; selected cuts do not cover unselected proposals.',
            'Join Project State, Context/Ontology Views, Sessions and learning/failure outcomes for the complete third owner journey.',
            'Required SQLite/query parity, full W07 integration, S02 closure and real human pilot/owner R08 outcome remain.'],
        'source_drift':[],'files':sorted(files.values(),key=lambda b:b['path']),'duration_seconds':time.perf_counter()-start}
    with output.open('xb') as stream:stream.write(op.encoded(result))
    print(json.dumps({'result':'PASS','task':'R03','task_complete':False,'tests':49,'examples':12,'files':len(files),'receipt':op.bind(output),'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':main()
