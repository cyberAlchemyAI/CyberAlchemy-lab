import json,hashlib,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read(HERE/'test-run.json');assert run['exit_code']==0 and run['inputs_unchanged']
text=(HERE/'runtime-tests.tap').read_text()
for line in ['# tests 81','# pass 81','# fail 0','# skipped 0']:assert line in text
assert not re.search(r'^not ok ',text,re.M)
records=read(HERE/'replacement-bindings.json');assert len(records['bindings'])==2
impact=read(HERE.parent/'0046-agent-reasoning-evidence-recovery/remaining-impact.json')
for row in records['bindings']:
    assert sha(HERE/row['snapshot'])==row['successor']['sha256']
    assert row['predecessor']['sha256']!=row['successor']['sha256']
    expected={**row['predecessor'],'sha256':row['successor']['sha256']};assert row['successor']==expected
    original=next(i for i in impact if i['source_id']==row['source_id'])
    assert set(row['affected_bridge_edges'])=={e['id'] for e in original['affected_bridge_edges']}
for ref in read(HERE/'tested-inputs.json'):assert sha(ROOT.parent/'cyberAlchemy-v2'/ref['path'])==ref['sha256']
for ref in read(HERE.parent/'0046-agent-reasoning-evidence-recovery/verification.json')['bindings']:assert sha(ROOT/ref['path'])==ref['sha256']
receipt={'result':'PASS','authority_effect':'none','checks':['81 fixture tests pass with no skipped tests','two exact replacement snapshots','replacement changes limited to source fingerprints','complete affected edge mapping','tested package inputs unchanged','predecessor recovery preserved'],'bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']}
(HERE/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print('PASS: six evidence checks; 81 runtime fixture tests passed.')
