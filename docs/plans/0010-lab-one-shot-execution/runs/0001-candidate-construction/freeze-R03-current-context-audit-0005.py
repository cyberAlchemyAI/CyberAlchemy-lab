"""Freeze full original parent plus terminal Context build/check evidence."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/current-context-delivery-v5'
PARENT=SELECTED.parent/'current-context-delivery-v4/receipts/R03-0036.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'current-context-audit-source-0005.json';assert not out.exists();parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']}
    def add(row):assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in json.loads((SELECTED/'source-manifest.json').read_bytes())['files']:add(row)
    for p in SELECTED.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    terminal=HERE/'current-context-delivery-terminal-0005.json';t=json.loads(terminal.read_bytes());assert t['selected_exit_codes']=={'build':0,'checks':0} and t['build']['terminal_observed'] and t['checks']['terminal_observed']
    report=json.loads((SELECTED/'receipts/checks.json').read_bytes());assert report['result']=='PASS' and report['tests_run']==50
    for n in ['audit-R03-current-context-0005.py','freeze-R03-current-context-audit-0005.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    context=HERE/'context-R03-current-context-audit-0005.json'
    for row in json.loads(context.read_bytes())['source_bindings']:add(row)
    for p in [PARENT,terminal,context]:add(bind(p))
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    m={'schema_version':'lab-original-source-context-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'parent_receipt_binding':bind(PARENT),'authorization_binding':bind(HERE/'authorization.json'),'delivery_source_binding':bind(SELECTED/'source-manifest.json'),'delivery_package_binding':bind(SELECTED/'packages/0001/manifest.json'),'mapped_package_binding':bind(SELECTED.parent/'current-mapped-context-v2/packages/0001/manifest.json'),'terminal_binding':bind(terminal),'qualified_fact_scope_binding':bind(SELECTED.parent/'fact-read-scope-v1/receipts/proof-0001.json'),'frozen_before_independent_context_audit':True,'remaining_obligations':parent['remaining_obligations']+['Select this exact original-source Context producer in successor API and ephemeral Session paths, preserve all former branches, full disposable SQL DDL/privacy/gaps/watermarks and exactbody/schema originals. Complete remaining21APIs and all34APIs and46tasks/S02 before single actualR08ownerdecision.'],'authority_effect':'none','actual_owner_outcome':None}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
