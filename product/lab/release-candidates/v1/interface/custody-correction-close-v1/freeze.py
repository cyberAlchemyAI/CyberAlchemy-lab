"""Freeze complete parent proof and every terminal selected output before audit."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
SELECTED=HERE.parent/'custody-correction-v4'
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'runtime-byte-custody-close-v1/receipts/R03-0017.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p)}
def main():
    assert not (HERE/'source-manifest.json').exists()
    for p in HERE.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
    parent=json.loads(PARENT.read_bytes());inputs={r['path']:r for r in parent['files']}
    selected=json.loads((SELECTED/'source-manifest.json').read_bytes())
    for r in selected['files']:
        if r['path'] in inputs:assert inputs[r['path']]==r
        inputs[r['path']]=r
    terminal=RUN/'custody-correction-terminal-0001.json'
    observations=json.loads(terminal.read_bytes())
    assert set(observations['selected_exit_codes'])==set(['guards','runtime','custody','schemas','journey','coupling'])
    assert all(x==0 for x in observations['selected_exit_codes'].values())
    for name in ['guards','runtime','custody','schemas','journey']:
        p=SELECTED/'receipts/0001'/f'{name}.json';assert json.loads(p.read_bytes())['result']=='PASS'
    for base in [SELECTED,HERE]:
        for p in sorted(base.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:inputs[bind(p)['path']]=bind(p)
    for p in [PARENT,terminal,RUN/'context-R03-custody-correction-0004.json',
        RUN/'R03-CUSTODY-CORRECTION-IMPLEMENTATION-0001.md',RUN/'R03-CUSTODY-API-INTEGRATION-0002.md',
        RUN/'context-R03-custody-correction-0005.json',RUN/'custody-correction-terminal-v3-0001.json',
        RUN/'S02-ORIGINAL-BYTE-CUSTODY-MEMBER-0002.json',
        RUN/'custody-terminal-observations-0002.json']:
        inputs[bind(p)['path']]=bind(p)
    for r in inputs.values():assert sha(ROOT/r['path'])==r['sha256'],r['path']
    m={'schema_version':'lab-exact-schema-correction-audit-source/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'frozen_before_audit_effects':True,'parent_receipt_binding':bind(PARENT),'selected_runtime_source_binding':bind(SELECTED/'source-manifest.json'),
        'selected_runtime_root':SELECTED.relative_to(ROOT).as_posix(),'terminal_observations_binding':bind(terminal),
        'coupling_log_binding':bind(SELECTED/'coupling-0001.log'),
        'files':sorted(inputs.values(),key=lambda r:r['path']),'remaining_obligations':parent['remaining_obligations']+
            ['The exact-schema/correction engine composition is now verified in owned fixtures. Carry its original bytes through the complete governed public API and independently provision a fresh successor source; original protocol/history/archive authority must not be silently widened.'],
        'claim_ceiling':'Scoped exact-schema/correction engine; original complete plan and single final owner checkpoint remain.'}
    (HERE/'source-manifest.json').open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'files':len(inputs),'parent_files_retained':len(parent['files'])}))
if __name__=='__main__':main()
