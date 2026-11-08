"""Accept only the completed exact-bound unified regression package."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE/'execution'));import support as s
from jsonschema import Draft202012Validator

suite=s.read(HERE/'qualification-suite.json');report=s.read(HERE/'regression-report.json')
Draft202012Validator(s.read(HERE/'qualification-suite.schema.json')).validate(suite)
Draft202012Validator(s.read(HERE/'regression-report.schema.json')).validate(report)
s.require(report['result']=='pass' and report['successful_layout_horn_qualifications']==12 and report['selected_successful_applications']==4,'incomplete full layout suite')
s.require(report['inherited_unique_controls']==342 and report['new_fresh_mapped_qualifications']==1,'missing inherited or active conflict coverage')
for c in suite['cases']:s.check(c['input']);s.check(c['output'])
for ref in suite['source_receipts']:
    receipt=s.read(s.check(ref))
    for r in receipt['artifacts']+receipt['inputs']:s.check(r)
extra=list(HERE.glob('*.py'))+list(HERE.glob('*.schema.json'))+[HERE/'InterfaceSemantics.lean',HERE/'build/InterfaceSemantics.lean',HERE/'build/InterfaceSemantics.olean',HERE/'interface-kernel-evidence.json',HERE/'API.md',BASE/'execution/reviews/P09.md']
for folder in ['layout-evidence','saved-challenges','cli-evidence']:
    extra += [p for p in (HERE/folder).rglob('*') if p.is_file()]
for name in ['layout-suite.json','saved-controls.json','public-hostile-controls.json','inherited-controls.json','cli-controls.json','rich-layout-observation.json','rich-combined-request.json','rich-combined-result.json','active-conflict-request.json','active-conflict-result.json','fixture-origin.json','layout-request.json','cli-policy.json']:
    extra.append(HERE/name)
layout=s.read(HERE/'layout-suite.json');hostile=s.read(HERE/'public-hostile-controls.json')
extra += [p for p in (HERE/'hostile-evidence'/hostile['run_id']).rglob('*') if p.is_file()]
roots={s.ROOT/hostile['runtime_root']}
for c in hostile['cases']:
    value=s.read(s.check(c['answer']));owned=value.get('qualification',{}).get('owned_run')
    if owned:roots.add(s.check(owned).parent)
for c in s.read(HERE/'cli-controls.json')['cases']:
    value=s.read(s.check(c['output']));owned=value.get('qualification',{}).get('owned_run')
    if owned:roots.add(s.check(owned).parent)
for c in layout['cases']:
    roots.add(s.ROOT/c['store'])
    public=s.read(s.check(c['qualification']));roots.add(s.check(public['qualification']['completion']).parent)
    for application in c['applications']:
        roots.add(s.check(application['transaction']['proposal_qualification']).parent)
        reg=s.read(s.check(application['after']['registration']));roots.add(s.check(reg['owned_run']).parent)
    head=s.read(s.ROOT/c['store']/'HEAD.json')
    # Genesis is included through the retained initialization event below.
for e in layout['events']:
    value=s.read(s.check(e['value']))
    if e['name'].endswith('-bootstrap'):roots.add(s.check(value['qualification']).parent)
rich=s.read(HERE/'rich-combined-result.json')['qualification']
if rich.get('owned_run'):roots.add(s.check(rich['owned_run']).parent)
conflict=s.read(HERE/'active-conflict-result.json');roots.add(s.check(conflict['completion']).parent)
# The actual failed proposal run remains immutable evidence of replay refusal.
for root in (BASE/'p07/consumer-runs'/('P09-layout-staged-'+layout['run_id'])).glob('job-*'):roots.add(root)
for root in roots:extra += [p for p in root.rglob('*') if p.is_file()]
extra=list({str(p.resolve()):p for p in extra}.values())
s.accept('P09',[
    'The closed finite suite binds all twenty hard rule-only obligations to actual fresh complete invocations, exact statement-bundle/axiom checks, 342 unique current inherited controls, newly executed decoder/evidence/contract/public refusal controls, an actual active conflict witness and new CLI integration. Reused evidence does not reissue live events.',
    'Combined and staged layouts freshly qualify the same supported profile and commit two real successive extensions each, with distinct fresh registrations and three immutable snapshots. Both normalized theories, complete closures, certificates, supports and observations agree exactly, including the epoch-marker successor; twelve selected fresh Horn invocations support four applications.',
    'Malformed, unsupported, forged-root, unavailable-policy, exhausted and cancelled public requests retain exact challenge/diagnostic evidence without claims or closure. Two structurally reviewed forged-root applications preserve the exact head. The real staged replay timeout preserves generation zero before an unchanged-policy fresh retry; stale reviews and saved/new-context readiness cannot publish. Rich combined scope is reported by its actual observed result.'
],report['controls'],extra=extra)
print('P09 accepted:',len(report['controls']),'finite cases;',report['selected_successful_fresh_horn_qualifications'],'new selected successful Horn qualifications')
