import json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0045-agent-reasoning-context-preparation'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=read(HERE/'recovery.json');recovered=[r for r in rows if r['matches']]
assert len(recovered)==5
for r in recovered:
    for match in r['matches']:assert sha(HERE/match['snapshot'])==r['expected']
remaining={r['id'] for r in rows if not r['matches']}
assert remaining=={'CAP-SEL-ARE-JOURNALED-CODEX-WRAPPER','CAP-SEL-ARE-EVOLUTION-RUNTIME'}
bridge=read(PREV/'source/bridge.json')
for r in read(HERE/'remaining-impact.json'):
    assert r['source_id'] in remaining
    assert sha(Path(r['current_path']))==r['current_sha256']
    expected={e['id'] for e in bridge['edges'] if r['source_id'] in e['evidence_refs']}
    assert {e['id'] for e in r['affected_bridge_edges']}==expected
contract=read(PREV/'repair-plan.json')['ontology_contract_predecessor'];assert sha(ROOT/contract['path'])==contract['sha256']
for b in read(PREV/'verification.json')['bindings']:assert sha(ROOT/b['path'])==b['sha256']
receipt={'result':'PASS','scope':'evidence recovery only; context not imported','authority_effect':'none','checks':['five exact evidence fingerprints','two remaining references identified','complete bridge impact mapping','current implementation versions pinned','prior preparation and admitted schema unchanged'],'bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']}
(HERE/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('PASS: five recovery checks; two implementation references still require successor evidence.')
