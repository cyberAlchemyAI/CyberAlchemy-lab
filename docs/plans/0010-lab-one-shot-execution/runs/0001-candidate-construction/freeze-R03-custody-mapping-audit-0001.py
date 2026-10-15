"""Freeze terminal mapper output/native selection and every original proof file."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/custody-mapped-context-v2'
PARENT=SELECTED.parent/'custody-participation-v1/receipts/R03-0019.json'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'custody-mapping-audit-source-0001.json';assert not out.exists();parent=json.loads(PARENT.read_bytes());rows={r['path']:r for r in parent['files']}
    def add(row):assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    selected=json.loads((SELECTED/'source-manifest.json').read_bytes())
    for row in selected['files']:add(row)
    exe=selected['selected_native_executable'];add(bind(Path(exe['path'])));assert bind(Path(exe['path']))==exe
    for base in [SELECTED,SELECTED.parent/'custody-mapped-context-v1']:
        for p in base.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    terminal=HERE/'custody-mapping-terminal-0001.json';t=json.loads(terminal.read_bytes());assert t['selected_exit_codes']=={'build':0,'checks':0}
    report=json.loads((SELECTED/'receipts/checks.json').read_bytes());assert report['result']=='PASS' and report['tests_run']==29
    for n in ['audit-R03-custody-mapping-0001.py','freeze-R03-custody-mapping-audit-0001.py']:
        p=HERE/n;ast.parse(p.read_bytes());add(bind(p))
    for p in [PARENT,terminal,HERE/'context-R03-custody-mapping-audit-0001.json']:add(bind(p))
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    m={'schema_version':'lab-qualified-original-source-mapper-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
        'parent_receipt_binding':bind(PARENT),'mapper_source_binding':bind(SELECTED/'source-manifest.json'),'mapper_package_binding':bind(SELECTED/'packages/0001/manifest.json'),
        'terminal_binding':bind(terminal),'native_executable_binding':exe,'frozen_before_independent_native_audit':True,
        'remaining_obligations':parent['remaining_obligations']+['Select this exact qualified original-body/native source in successor Context/OntologyView carrier generation, consistent eligibility namespaces, actual fresh host permission and classified ephemeral Agent/Session lifetimes. Carry full original-byte/qualified-schema/privacy/cut/DDL/watermark/correction/review constraints through all34public APIs and complete original46tasks/S02 before single actualR08ownerdecision.'],
        'authority_effect':'none','actual_owner_outcome':None}
    out.open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'parent_files_retained':len(parent['files']),'source_binding':bind(out)}))
if __name__=='__main__':main()
