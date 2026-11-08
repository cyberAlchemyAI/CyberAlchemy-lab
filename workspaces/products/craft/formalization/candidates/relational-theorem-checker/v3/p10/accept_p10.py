"""Bind actual complete/failed instrumented runs and current recorded costs."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE/'execution'));import support as s
from jsonschema import Draft202012Validator

report=s.read(HERE/'stage-measurements.json');controls=s.read(HERE/'performance-controls.json');benchmark=s.read(HERE/'benchmark-results.json')
for name,value in [('performance-report',report),('benchmark-profile',s.read(HERE/'benchmark-profile.json')),('performance-controls',controls)]:
    Draft202012Validator(s.read(HERE/(name+'.schema.json'))).validate(value)
s.require(controls['result']=='pass' and len(report['samples'])==4,'missing actual stress repetition')
s.require([x['status'] for x in report['samples']]==['qualified-candidate','qualified-candidate','unknown-resource','unknown-resource'],'actual boundary differs from author review')
s.require(report['selection']=='no-optimization','unqualified optimization selected')
extra=list(HERE.glob('*.py'))+list(HERE.glob('*.schema.json'))+[HERE/'benchmark-results.json',HERE/'benchmark-results-initial.json',HERE/'stress-repeat.json',HERE/'performance-controls.json',HERE/'timing-controls.json',BASE/'execution/reviews/P10.md']
for p in (HERE/'evidence').rglob('*'):
    if p.is_file():extra.append(p)
for root in benchmark['runtime_roots']:extra += [p for p in (s.ROOT/root).rglob('*') if p.is_file()]
for row in controls['recorded_shadow_timings']:s.check(row['proposal_record']);s.check(row['registration_record']);s.check(row['application_source'])
for sample in report['samples']:
    s.check(sample['input']);s.check(sample['output']);s.check(sample['cache_check'])
extra=list({str(p.resolve()):p for p in extra}.values())
s.accept('P10',[
    'Actual rich cold and warm runs both freshly discharge all twenty obligations and agree on normalized theory, complete closure, certificates, supports and observations. The exact three-variable preflight-valid source repeats a complete-closure tool deadline refusal twice under unchanged policy; four exact samples preserve actual completion/refusal, stage parentage, cache checks, advisory peak RSS and scoped recorded application/registration costs.',
    'Measured compilation, source/import guards and fresh general replay dominate the finite evaluator. Select no optimization; the fixed source-bound timing worker delegates all proof, currentness, supervision and owned finalization to unchanged accepted code. Ten independent interval controls prevent overlapping/nested time inflation, and all successful runs retain actual fresh replay.',
    'Closed reports state workload/build-mode scope, uncontrolled OS cache/host load, monotonic/instrumentation assumptions, advisory memory, enclosing timers and unreached stages. No isolated commit timer, independent-kernel assurance, general speedup or broader-profile completion guarantee is published.'
],controls['controls'],extra=extra)
print('P10 accepted:',len(controls['controls']),'controls; two actual full qualifications and two repeated safe proof refusals')
