import json
from pathlib import Path
import check

r=check.run()
assert r['counts']=={'business_concepts':25,'business_relations':23,'system_concepts':10,'system_relations':0}
assert r['stale_binding_count']==9
assert len({c['path'] for c in r['exact_bindings'] if c['result']=='BLOCK'})==6
assert len(r['missing_selected_sources'])==1
assert r['missing_selected_sources'][0]['id']=='GCC-SEL-GOVERNANCE-PRODUCT-RECORDS'
assert r['decision_cases_passed']==r['decision_cases_total']==19
assert r['reused_rust_tests']==29
assert check.read(check.HERE/'build-check.json')['changed_generated_artifacts']==[]
assert not (check.HERE/'bundle.json').exists()
check.dump('verification.json',{
    'result':'PASS','import_status':'BLOCK','authority_effect':'none',
    'checks':['predecessor evidence and snapshot fingerprints verified',
              'business and system graph identities and endpoints valid',
              'nine stale references across six files identified',
              'missing governance Product selection explicitly recorded',
              'all generated artifacts reproduced without writes',
              'six positive and thirteen hostile CLI cases pass',
              '29 prior Rust tests bound to unchanged snapshot',
              'original source rejection preserved and no import emitted'],
    'bindings':[{'path':str(p.relative_to(check.ROOT)),'sha256':check.sha(p)} for p in sorted(check.HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eight preparation checks. Import blocked by nine stale references and one missing snapshot selection.')
