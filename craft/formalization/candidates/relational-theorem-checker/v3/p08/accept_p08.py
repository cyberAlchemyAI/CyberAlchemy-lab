"""Bind actual current publication, mapped, IO and formal evidence to P08."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE/'execution'));import support as s
pub=s.read(HERE/'publication-controls.json');mapped=s.read(HERE/'mapped-controls.json');meta=s.read(HERE/'metadata-controls.json')
for x in [pub,mapped,meta]:s.require(x['result']=='pass','missing pass')
extra=list(HERE.glob('*.py'))+list(HERE.glob('*.schema.json'))+[HERE/'ShadowTransaction.lean',HERE/'build/ShadowTransaction.lean',HERE/'build/ShadowTransaction.olean',HERE/'transaction-kernel-evidence.json',HERE/'API.md',HERE/'metadata-controls.json',HERE/'mapped-controls.json',HERE/'registration-preflight-review.json',HERE/'registration-preflight-result.json',BASE/'p01/request-fixture.json',BASE/'execution/reviews/P08.md']
refs=[]
for event in pub['events']:
    r=event['result']
    for k in ['qualification','proposal_qualification','successor_registration']:
        if k in r:refs.append(r[k])
    refs+=r.get('mapped_checks',[])
refs += [case['answer']['completion'] for case in mapped['cases']]
for root in {s.check(r).parent for r in refs}:extra += [p for p in root.rglob('*') if p.is_file()]
extra += [p for p in (s.ROOT/pub['store']).rglob('*') if p.is_file()]
for case in meta['actual_process_crashes']:extra += [p for p in (s.ROOT/case['store']).rglob('*') if p.is_file()]
extra += [s.check(pub['initialization_evidence'])]
extra=list({str(p.resolve()):p for p in extra}.values())
controls=meta['controls']+pub['controls']+mapped['controls']
s.accept('P08',[
    'Two actual fresh publishers of the same reviewed generation compete through the transactional API: exactly one applies and the other returns stale-head. Generation, exact request/context/mapping identities and one-time process-local handles are checked.',
    'Five actual process crashes exercise journal, snapshot, registration, metadata-head and mirror windows; 34 explicitly unqualified IO controls recover safely or preserve committed state for reconciliation. A full fresh second application recovers a real injected postcommit mirror exception as applied.',
    'Two real extensions retain three immutable exact snapshots and distinct independent registrations. Seven selected fresh Horn checks include initial registration and fresh proposal/registration pairs for both competitors and the second extension; mapped contexts are freshly checked individually. Saved receipts/new contexts cannot issue application handles.'
],controls,extra=extra)
print('P08 accepted with',len(controls),'controls and six abstract compiled statements')
