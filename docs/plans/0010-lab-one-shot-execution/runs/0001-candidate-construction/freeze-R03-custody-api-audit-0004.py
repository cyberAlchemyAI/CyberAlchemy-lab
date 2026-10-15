"""Freeze independent observations before effects; full suite remains pending."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v20'
PARENT=API.parent/'custody-context-delivery-v1/receipts/R03-0021.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'custody-api-audit-source-0004.json';assert not out.exists()
    parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']}
    def add(r):assert rows.get(r['path'],r)==r,r['path'];rows[r['path']]=r
    for r in json.loads((API/'source-manifest.json').read_bytes())['files']:add(r)
    for p in [API/'source-manifest.json',API/'contract-profile.json',PARENT,HERE/'context-R03-custody-api-audit-0004.json']:add(bind(p))
    for serial,name in [('0001','api-v17'),('0002','api-v18')]:
        old=API.parent/name;t=HERE/('custody-api-terminal-'+serial+'.json');v=json.loads(t.read_bytes());test=json.loads((old/'receipts/checks.json').read_bytes())
        assert v['exit_code']==1 and test['result']=='FAIL' and test['tests_run']==test['expected_tests']==129
        for field,p in [('source_binding',old/'source-manifest.json'),('profile_binding',old/'contract-profile.json'),('checks_binding',old/'receipts/checks.json'),('log_binding',old/'checks-0001.log'),('wire_observations_binding',old/'receipts/wire-observations.json')]:assert v[field]==bind(p);add(bind(p))
        add(bind(t))
    for n in ['audit-R03-custody-api-0004.py','freeze-R03-custody-api-audit-0004.py','qualify-R03-custody-api-0004.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    for r in rows.values():assert bind(ROOT/r['path'])==r,r['path']
    m={'schema_version':'lab-original-source-API-observation-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'parent_receipt_binding':bind(PARENT),'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'frozen_before_independent_observation':True,'full_suite_qualification':False,'remaining_obligations':parent['remaining_obligations']+['Full146 terminalPASS and full API19 terminal closure before qualification.','Remaining22public APIs/full46criteria/actualR04humanpilot/S02/R08owner outcomes.'],'authority_effect':'none','actual_owner_outcome':None}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
