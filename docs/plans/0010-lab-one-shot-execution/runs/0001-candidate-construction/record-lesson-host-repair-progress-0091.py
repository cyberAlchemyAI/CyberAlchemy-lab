"""Record authored repair and actual failed predecessor without qualification reuse."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v51/receipts/R03-0090.json'
    old = load(predecessor)
    api = BASE / 'api-v52'
    source, profile = api / 'source-manifest.json', api / 'contract-profile.json'
    assert bind(source)['sha256'] == 'b28af91a974d3039aec4dae206d4dc8dc2007835f69adaee66b800e067da4c93'
    assert bind(profile)['sha256'] == 'e6cab0759faf2f7dc476779145ebd84c7c9a9d0005cd0852b72fde7dace3baea'
    failed_terminal = RUN / 'API51-lesson3-terminal-0001.json'
    assert load(failed_terminal)['actual_exit_code'] == 1
    assert load(failed_terminal)['errors'] == 3
    build_terminal = RUN / 'API52-construction-terminal-0001.json'
    emit(build_terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 75031, 'initial_chunk_id': 'e27ac9', 'final_chunk_id': '55a5f2',
        'actual_exit_code': 0, 'result': 'FROZEN', 'source_binding': bind(source),
        'profile_binding': bind(profile), 'authority_effect': 'none', 'task_complete': False})
    started = RUN / 'API52-lesson3-started-0001.json'
    emit(started, {'schema_version': 'lab-live-candidate-check-observation/v1-candidate',
        'session_id': 29782, 'initial_chunk_id': 'cf7cb3', 'pid': 39122,
        'source_binding': bind(source), 'profile_binding': bind(profile),
        'selected_cases': 3, 'actual_exit_code': None, 'actual_cases_completed': None,
        'source_qualified': False, 'authority_effect': 'none', 'task_complete': False})
    review = RUN / 'GOVERNANCE-BOUNDARY-REVIEW-0091.md'
    text = '''# Lab implementation and final decision boundaries

## Recommendation

Continue the authorized candidate build and verification. Present one complete,
exact package at R08 only after S02 establishes final review readiness. Do not
request admission of intermediate candidates.

## Current boundaries

| Boundary | Required evidence or action | Current disposition |
| --- | --- | --- |
| Candidate construction and full suites | Existing run authorization | Authorized in isolated owned fixtures |
| R03 implementation | All 34 operations and exact-source qualification | 18 authored; 16 missing; API52 checks running |
| R05 real pilot | Named real work, participants, scope and observations | Pending; generated tests cannot supply participant evidence |
| R06 private/public review | Exact package and demonstrated boundary closure | In progress |
| R07 release validation | Complete candidate release and member closure | Pending |
| S02 final review readiness | Exact manifests, member/owner/effect matrix, examples, publisher recovery and carrier fit | Pending |
| R08 admission | Actual accountable owner outcomes for the exact independently scoped members | One final checkpoint, pending S02 |
| A01 application | Exact resolved positive admission outcomes and current preimages | Requires R08 |
| A02 local operations | Separately represented operator, environment, store, action scope, prerequisites and recovery | Must be explicitly selected and authorized in final package |
| A03/A04 operational proof and release | Observed outcomes and exact permitted release effects | No fabricated observations or unselected effects |

One checkpoint may collect several independently scoped outcomes. It does not
merge definition ownership, carrier ownership, identity graph ownership,
implementation admission, adoption, local action permission and release into
one unrestricted grant. The nine member classes in the preparation matrix must
have actual final bytes and verified accountable owner roles at S02/R08.

The original preparation execution-scope.json is narrower and explicitly did
not authorize runtime tests. The later run authorization.json covers candidate
implementation, full suites and owned isolated episodes. Both predecessors are
preserved; the later authorization does not authorize canonical admission,
existing/live store operations, activation, external effects, push or deployment.

## Stops during construction

Stop the affected operation when its source drifts, Actor or carrier binding is
unresolved, applicable authority is missing, the effect leaves selected scope,
or an earlier effect is uncertain and unreconciled. Resolve or narrow the affected
operation before dispatch. These conditions do not justify inventing owner
approval or treating missing evidence as success. Unaffected authorized candidate
work can continue.

API51's actual three-case lesson transport suite ended with three errors and
exit 1. Its first defect registered the Machine channel with the original fact
scope while the live Session checks its parent ReaderChannel. Rejection then
exposed an error reply built from a cleared context. A separate disposed-peer
case raised instead of returning the original unauthenticated transport result.

API52 is an exclusive frozen repair: select the actual live Session's parent
reader bridge, retain the Machine guard inside the scope, and fail closed after
peer disposal/revocation. The original fact kernels, clocks, callbacks, three
lesson assertions and 293 inherited test methods remain. Its three actual cases
are running; no successful transport or nonempty Lesson qualification is claimed.

The complete plan is still 36/46 closed. Genuine pilot input, complete runtime
qualification, release closure and the actual final owner response remain.
'''
    with review.open('x') as stream:
        stream.write(text)
    rows = {row['path']: row for row in old['files']}
    for row in load(source)['files']:
        rows[row['path']] = row
    inputs = [predecessor, source, profile, failed_terminal, build_terminal, started, review,
        BASE / 'api51-lesson-checks-v1/receipts/checks-0001.json',
        BASE / 'api51-lesson-checks-v1/receipts/actual-0001.log',
        BASE / 'api51-lesson-checks-v1/receipts/wire-0001.json',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/execution-scope.json',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/governance/member-matrix.json',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/governance/workflow-decision-profile.json',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/S02.md',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R08.md',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R05.md',
        ROOT / 'docs/plans/0010-lab-one-shot-execution/work-pack/tasks/A02.md', Path(__file__).resolve()]
    for path in inputs:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    remaining = [
        'Observe same API52 lesson3 runner29782/PID39122; require its actual terminal and exact-source successful report before qualification.',
        *old['remaining_obligations'][1:]]
    value = {**old, 'result': 'PASS', 'parent_progress_binding': bind(predecessor),
        'source_binding': bind(source), 'profile_binding': bind(profile),
        'files': [rows[key] for key in sorted(rows)],
        'change': 'Preserved API51 actual FAIL/3 errors/exit1. Authored and froze API52 parent-reader fact-scope repair plus closed-peer transport handling. All293 inherited methods and three lesson assertions retained. Original source kernels/clocks/callbacks unchanged. Current three actual checks running; no qualification.',
        'lesson_selection_public_suite_verdict': None,
        'lesson_selection_actual_live_Session_qualified': False,
        'lesson_selection_public_runner_start_binding': bind(started),
        'lesson_selection_actual_public_calls': None,
        'failed_API51_lesson_terminal_binding': bind(failed_terminal),
        'failed_API51_lesson_cases': 3, 'failed_API51_lesson_errors': 3,
        'API52_construction_terminal_binding': bind(build_terminal),
        'API52_full_public_runtime_qualified': False,
        'governance_boundary_review_binding': bind(review),
        'remaining_obligations': remaining,
        'claim_ceiling': 'Authored/frozen API52 repair and governance boundary review; API51 failed actual suite preserved. API52 runtime and nonempty source qualification pending. No complete API, genuine participant review, admission or full plan completion.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = api / 'receipts/R03-0091.json'
    path.parent.mkdir(exist_ok=False)
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path),
        'bound_files': len(rows), 'handlers': 18, 'missing': 16, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
