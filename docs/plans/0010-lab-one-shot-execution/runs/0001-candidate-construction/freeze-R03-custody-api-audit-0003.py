"""Freeze complete parent plus actual terminal129method API evidence."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v19'
PARENT=API.parent/'custody-context-delivery-v1/receipts/R03-0021.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'custody-api-audit-source-0003.json';assert not out.exists();parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']}
    def add(r):assert rows.get(r['path'],r)==r,r['path'];rows[r['path']]=r
    for r in json.loads((API/'source-manifest.json').read_bytes())['files']:add(r)
    for p in API.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    terminal=HERE/'custody-api-terminal-0003.json';assert json.loads(terminal.read_bytes())['exit_code']==0
    tests=json.loads((API/'receipts/checks.json').read_bytes());assert tests['result']=='PASS' and tests['tests_run']==tests['expected_tests']==129
    failed_terminal=HERE/'custody-api-terminal-0002.json';old=API.parent/'api-v18'
    failed=json.loads((old/'receipts/checks.json').read_bytes());actual=json.loads(failed_terminal.read_bytes())
    assert actual['exit_code']==1 and failed['result']=='FAIL' and failed['tests_run']==failed['expected_tests']==129
    assert actual['source_binding']==bind(old/'source-manifest.json') and actual['checks_binding']==bind(old/'receipts/checks.json') and actual['log_binding']==bind(old/'checks-0001.log')
    for p in [failed_terminal,old/'checks-0001.log',old/'receipts/checks.json',old/'receipts/wire-observations.json']:add(bind(p))
    first=API.parent/'api-v17';first_terminal=HERE/'custody-api-terminal-0001.json';first_tests=json.loads((first/'receipts/checks.json').read_bytes());assert json.loads(first_terminal.read_bytes())['exit_code']==1 and first_tests['result']=='FAIL' and first_tests['tests_run']==first_tests['expected_tests']==129
    for p in [first_terminal,first/'source-manifest.json',first/'checks-0001.log',first/'receipts/checks.json',first/'receipts/wire-observations.json']:add(bind(p))
    for n in ['audit-R03-custody-api-0003.py','freeze-R03-custody-api-audit-0003.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    for p in [PARENT,terminal,HERE/'context-R03-custody-api-audit-0003.json',HERE/'R03-SINGLE-REVIEW-PREPARATION-0001.md']:add(bind(p))
    for r in rows.values():assert bind(ROOT/r['path'])==r,r['path']
    m={'schema_version':'lab-original-source-API-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'parent_receipt_binding':bind(PARENT),'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'terminal_binding':bind(terminal),'failed_parent_terminal_binding':bind(failed_terminal),'frozen_before_independent_API_audit':True,'remaining_obligations':parent['remaining_obligations']+['Implement remaining22originalpublicAPIs and all genuine workflow/review/action/governance/lesson/ontology/materialization/package/installation/extension/adoption/release journeys. Original46task scope and actualR04/S02/R08owneroutcomes remain; no declaration/testfixture substitutes for actualownerdecision.'],'authority_effect':'none','actual_owner_outcome':None}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
