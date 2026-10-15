"""Read-only revalidation of predecessor evidence; output only in this follow-up."""
from pathlib import Path
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
BASE = HERE.parents[1]
sys.path.insert(0, str(BASE))


def binding(path):
    return {'path': str(path.resolve().relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run(output):
    output = Path(output).resolve()
    assert output.is_relative_to(HERE / 'execution'), 'audit write scope'
    output.mkdir(parents=True, exist_ok=True)
    from v3.execution import complete_plan_audit as successor
    from v3.execution import support as support
    captured = {}
    original_write = support.write
    def capture(path, value):
        assert Path(path) == BASE / 'v3/execution/complete-plan-audit.json'
        captured['successor'] = value
    # The existing audit writes its report to a bound historical path. Redirect
    # that one output in this process; never change its accepted source or file.
    support.write = capture
    try:
        successor_result = successor.audit()
    finally:
        support.write = original_write
    assert captured['successor'] == successor_result
    sys.path.insert(0, str(BASE / 'v1/pilot'))
    from prepare_review import audit_plan
    import runtime as cli
    original = audit_plan()
    assert original['counts'] == {'tasks':35, 'working_units':40, 'edges':56, 'accepted':33}
    from v3.p05.bindings import Resolver
    resolver = Resolver()
    closure = json.loads((BASE / 'v3/p05/current-source-report.json').read_text())
    refs = {}
    def verify(ref):
        if ref.get('kind') == 'toolchain':
            path = resolver.check(ref)
        else:
            canonical = {'kind':'repo', 'path':ref['path'], 'sha256':ref['sha256']}
            path = resolver.check(canonical)
        actual = {'path':str(path.relative_to(ROOT)), 'sha256':ref['sha256']}
        refs[(actual['path'], actual['sha256'])] = actual
        return path
    for ref in closure['verified_bindings']:
        verify(ref)
    for task in original['requirements']:
        if task['status'] != 'accepted':
            continue
        receipt = json.loads(verify(task['receipt']).read_text())
        for ref in receipt['artifacts'] + receipt['dependency_bindings']:
            verify(ref)
    for task in successor_result['tasks']:
        receipt = json.loads(verify(task['receipt']).read_text())
        for ref in receipt['artifacts'] + receipt['inputs']:
            verify(ref)
    pilot_path = BASE / 'v1/pilot/shadow-pilot-report.json'
    pilot = json.loads(pilot_path.read_text())
    assert pilot['machine_result'] == 'pass'
    expected = {'endpoint-extension-unsupported':3, 'complete-rule-change':0,
                'protected-head-unsupported':3, 'search-without-checked-witness':4}
    assert len(pilot['fresh_cases']) == 4 and len(pilot['accepted_predecessor_cases']) == 33
    coverage = []
    for case in pilot['fresh_cases']:
        outcome = json.loads(verify(case['outcome']).read_text())
        verify(case['stderr'])
        args = cli.parser().parse_args(case['argv'])
        proposal, _ = cli.read_input(args.input if args.command == 'check-extension' else args.proposal)
        required = [x['id'] for x in cli.g.generate(proposal)['obligations']]
        cli.o.validate(outcome, required)
        assert cli.o.exit_code(outcome) == case['exit_code'] == expected[case['name']]
        if case['name'] == 'complete-rule-change':
            assert len(outcome['results']) == 15 and all(x['verdict']=='satisfied' for x in outcome['results'])
        if case['name'] == 'search-without-checked-witness':
            unresolved = [x for x in outcome['results'] if x['verdict'] != 'satisfied']
            assert len(unresolved) == 1 and unresolved[0]['verdict'] == 'unknown'
            assert unresolved[0]['obligation_id'].endswith(':independence-witnesses')
        coverage.append({'case':case['name'], 'required_obligations':required,
                         'exit_code':case['exit_code'], 'outcome':case['outcome'], 'result':'pass'})
    for case in pilot['accepted_predecessor_cases']:
        verify(case['outcome']); verify(case['stderr'])
    machine = json.loads((BASE / 'v1/pilot/machine-validation-audit.json').read_text())
    assert machine['result'] == 'pass'
    for ref in machine['generated_evidence_dependencies']:
        verify(ref)
    for path in [pilot_path, BASE/'v1/pilot/machine-validation-audit.json',
                 BASE/'v1/pilot/supported-use-matrix.json',
                 ROOT/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json']:
        verify(binding(path))
    result = {'schema':'relational.closure-predecessor-audit/v4', 'result':'pass',
              'original_counts':original['counts'], 'successor_units':19,
              'extension_controls':successor_result['extension_control_records'],
              'extension_final_witnesses':successor_result['extension_full_final_witnesses'],
              'embedded_closure_bindings':len(closure['verified_bindings']),
              'source_bindings':sorted(refs.values(), key=lambda x:x['path']),
              'pilot':binding(pilot_path), 'original_gates':'pending actual artifact-specific human assessment',
              'observations':'Historical executed proofs/pilot recaptured by current source hashing and obligation audit; no fresh authority event or new proof execution.',
              'authority_effect':'none'}
    for name, value in [('predecessor-current-audit.json',result), ('original-plan-audit.json',original),
                        ('successor-plan-audit.json',successor_result),
                        ('pilot-coverage.json',{'result':'pass','cases':coverage,'coverage':pilot['coverage'],'predecessor_executions':33,'authority_effect':'none'}),
                        ('mutation-impact.json',{'result':'preserve-bound-original-plan','bound_original_plan':[r for r in refs.values() if r['path'].endswith('/PLAN-SOURCE.json')],
                          'adopted_strategy':'New checked overlay/current reader; no old finalizer or frozen snapshot mutation.',
                          'proof_effect':'No changed relation meaning or existing proof; new gate model checked separately.','authority_effect':'none'}),
                        ('supported-use-matrix.json',json.loads((BASE/'v1/pilot/supported-use-matrix.json').read_text())),
                        ('obligation-extension-crosswalk.json',{'scope':'No retroactive discharge','inherited_obligations_remaining':263,
                          'mapping':[{'extension':'E'+str(i).zfill(2),'claim':'Separate accepted profile; no original inherited obligation discharged solely by its receipt.'} for i in range(7)],'authority_effect':'none'})]:
        (output/name).write_text(json.dumps(value,indent=2)+'\n')
    return result


if __name__ == '__main__':
    start = time.monotonic()
    result = run(HERE / 'execution/h01')
    print(json.dumps({'result':result['result'],'current_files':len(result['source_bindings']),
                      'original_counts':result['original_counts'],'seconds':time.monotonic()-start},indent=2))
