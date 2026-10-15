"""Freeze complete parent plus actual terminal129method API evidence."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v17'
PARENT=API.parent/'custody-context-delivery-v1/receipts/R03-0021.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'custody-api-audit-source-0001.json';assert not out.exists();parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']}
    def add(r):assert rows.get(r['path'],r)==r,r['path'];rows[r['path']]=r
    for r in json.loads((API/'source-manifest.json').read_bytes())['files']:add(r)
    for p in API.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    terminal=HERE/'custody-api-terminal-0001.json';assert json.loads(terminal.read_bytes())['exit_code']==0
    tests=json.loads((API/'receipts/checks.json').read_bytes());assert tests['result']=='PASS' and tests['tests_run']==tests['expected_tests']==129
    for n in ['audit-R03-custody-api-0001.py','freeze-R03-custody-api-audit-0001.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    for p in [PARENT,terminal,HERE/'context-R03-custody-api-audit-0001.json']:add(bind(p))
    for r in rows.values():assert bind(ROOT/r['path'])==r,r['path']
    m={'schema_version':'lab-original-source-API-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'parent_receipt_binding':bind(PARENT),'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'terminal_binding':bind(terminal),'frozen_before_independent_API_audit':True,'remaining_obligations':parent['remaining_obligations']+['Implement remaining22originalpublicAPIs and all genuine workflow/review/action/governance/lesson/ontology/materialization/package/installation/extension/adoption/release journeys. Original46task scope and actualR04/S02/R08owneroutcomes remain; no declaration/testfixture substitutes for actualownerdecision.'],'authority_effect':'none','actual_owner_outcome':None}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
