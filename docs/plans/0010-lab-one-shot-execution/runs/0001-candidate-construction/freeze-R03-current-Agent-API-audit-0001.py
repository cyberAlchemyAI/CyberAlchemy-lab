"""Freeze actual complete API28 outcomes and declared input closure before audit effects."""
import ast,hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v28'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=RUN/'current-Agent-API-audit-source-0001.json';assert not out.exists()
    rows={}
    def add(r):assert rows.get(r['path'],r)==r and bind(ROOT/r['path'])==r,r['path'];rows[r['path']]=r
    # Never consume a pending run, partial log, inferred terminal or smaller suite.
    for name,count in [('checks.json',146),('file-export-checks.json',134),('current-controls.json',6)]:
        value=json.loads((API/'receipts'/name).read_bytes())
        assert value['result']=='PASS' and value['tests_run']==value['expected_tests']==count
        assert len(value['cases'])==count and all(c['result']=='PASS' for c in value['cases'])
    terminal=RUN/'current-Agent-API-terminal-0003.json';t=json.loads(terminal.read_bytes())
    assert t['selected_exit_codes']=={'controls':0,'integration':0,'metadata_export':0}
    for row in json.loads((API/'source-manifest.json').read_bytes())['files']:add(row)
    for p in API.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    for n in ['audit-R03-current-Agent-API-0001.py','freeze-R03-current-Agent-API-audit-0001.py']:
        p=RUN/n;ast.parse(p.read_bytes());add(bind(p))
    context=RUN/'context-R03-current-Agent-API-audit-0001.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for r in c['source_bindings']:add(r)
    for p in [context,terminal]:add(bind(p))
    m={'schema_version':'lab-current-Agent-independent-audit-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'terminal_binding':bind(terminal),'context_binding':bind(context),'frozen_before_independent_owned_host_key_workspace_or_Session_effects':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    with out.open('x') as f:json.dump(m,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(out),'files':len(rows)}),flush=True)
if __name__=='__main__':main()
