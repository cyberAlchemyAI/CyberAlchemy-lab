"""Freeze terminal source outputs and the complete immutable parent before audit."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/custody-participation-v1'
PARENT=SELECTED.parent/'custody-correction-close-v1/receipts/R03-0018.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'custody-participation-audit-source-0001.json';assert not out.exists()
    parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']};selected=json.loads((SELECTED/'source-manifest.json').read_bytes())
    def add(row):assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in selected['files']:add(row)
    for p in SELECTED.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    terminal=HERE/'custody-participation-terminal-0001.json';t=json.loads(terminal.read_bytes())
    assert t['selected_exit_codes']=={'build':0,'eligibility':0,'checks':0,'cold':0}
    for name in ['checks','eligibility','cold']:assert json.loads((SELECTED/'receipts'/f'{name}.json').read_bytes())['result']=='PASS'
    for n in ['audit-R03-custody-participation-0001.py','freeze-R03-custody-participation-audit-0001.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    for p in [PARENT,terminal,HERE/'context-R03-custody-participation-audit-0001.json',HERE/'CONTEXT-R03-custody-participation-audit-0001.md']:add(bind(p))
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    m={'schema_version':'lab-original-participation-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
        'parent_receipt_binding':bind(PARENT),'selected_source_binding':bind(SELECTED/'source-manifest.json'),
        'package_binding':bind(SELECTED/'packages/0001/manifest.json'),'terminal_binding':bind(terminal),
        'frozen_after_actual_producers_exit_before_independent_audit':True,'authority_effect':'none','actual_owner_outcome':None,
        'remaining_obligations':parent['remaining_obligations']+['Carry the newly verified exact original-byte source through complete public API, full SQLite projection, current independent host permissions, newly selected native/context/ontology mappings and full fresh Agent/Session workflows. Preserve all old archives, executable interpretations and expired/current authority distinction. Full original22remaining APIs/46tasks and single final R08 checkpoint still apply.']}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
