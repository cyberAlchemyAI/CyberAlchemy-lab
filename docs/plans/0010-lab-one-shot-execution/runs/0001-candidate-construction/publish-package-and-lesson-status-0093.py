"""Publish completed scoped tests and only the verified continuing regression job."""
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
    progress = BASE / 'api-v52/receipts/R03-0093.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0156.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    assert proof['lesson_selection_empty_inventory_transport_qualified'] and proof['package_transfer_current_pure_cases'] == 61
    terminal = RUN / 'R03-0093-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'session_id': 60047,
        'initial_chunk_id': '12a8fc', 'final_chunk_id': '3ca5d5', 'actual_exit_code': 0,
        'result': 'PASS', 'currentness_binding': bind(currentness), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'goal_complete': False})
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0093.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

The full plan remains active and incomplete: 36/46 tasks closed. R03/R06 are in
progress. Current public candidate API52 has 18 authored handlers and 16 missing
operations; all 34 original contracts and 293 inherited methods remain.

## New verified evidence

API52 completed its three actual lesson transport cases with zero failures/errors
and actual exit 0. Its ten wire calls include three distinct real Agent/Session
openings, one successful zero-Lesson selection, a spoofed Actor and foreign
Assignment refusal, and a disposed peer's unauthenticated transport result. The
actual source exit guard completed. Session RAM disposal and absent restoration
were checked by the original retained assertions. This is qualification of the
selected empty-catalog transport cases only; the signed source still has no
Lessons. Nonempty and generalized behavior remain unqualified. API51's actual
three errors and exit 1 remain preserved.

Package transfer calculation v1 passed all 50 pure cases. The explicit v2
successor passed all 61 cases, retaining every original test assertion. It
preserves original artifact and raw text/binary dependency bytes, checks complete
bounded dependency closure, permits finite closed cycles, binds encoding-aware
privacy review, and accounts for exact import/adaptation/retain/exclude choices.
Source provenance remains separate from target authority; duplicate evidence
basis and excessive complete-plan output are refused. All five new contracts are
internal candidate schemas; no public contract was changed.

These package fixtures are synthetic. The calculation authenticates no host and
does not verify source admission signatures or complete target model semantics.
Import explicitly leaves target-model validation pending. No public package
handlers, managed file publication, source retirement or admission were added.
Actual independently reviewed privacy and full carrier/relationship/core checks
must be supplied by the real host before a public proposal can be exposed.

## Continuing verification and remaining implementation

The same API50 serialized driver is session 28245/PID 21680, full146 child 32885.
Its typed10/failure18/controls11 selections completed PASS39 with actual exits0;
the other 413 selected cases remain pending complete suite results. Its original
source-specific qualifications are not transferred to API52. Never restart from
an observation timeout. API52's lesson runner29782 is closed; do not repoll it.

Next: integrate package.export/import with actual independently selected policies,
source replay, full original carrier/model/typed validation, strict clocks/budgets,
durable claims, managed generations and verified read-only recovery. Qualify a
nonempty signed Lesson source and declared Context/Ontology successor, all current
public suites, the other missing operations, actual assigned Machine typed
authority and internal/specialized authority resolvers.

Then complete genuine R05 participant evidence, R06/R07 and exact all-member S02.
One final actual R08 checkpoint remains before independently authorized A01–A04.
Existing/live stores, private/live keys, service activation, external effects,
push/deployment and unrelated dirty work remain outside construction scope.

Currentness156 passed: 38 active receipts, 77 preparation files and 887 baseline
sources unchanged. R03-0093 binds 15,884 files. No whole API, nonempty lesson use,
genuine pilot, canonical admission or complete plan is claimed.
''')
    handoff = load(RUN / 'custody-integration-handoff-0078.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [29782, 79812, 78747, 5900, 60648, 43694, 76579, 60047]))
    handoff['same_live_jobs'] = [{'session_id': 28245, 'initial_chunk_id': 'c3944a',
        'state': 'last-observed-running', 'owned_driver_PID': 21680, 'owned_child_PID': 32885,
        'suite': 'API50 same452-case regression: complete39; full146 running',
        'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'), 'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        current_API52='Actual lesson transport3 PASS/exit0 with10 wire calls and three distinct real Sessions; empty catalog scope only. All293 inherited methods remain; whole API and nonempty catalog unqualified.',
        package_transfer='Frozen calculation v2:61 pure cases PASS retaining50 original assertions. Exact raw closure/encoding/privacy review and complete import accounting; source signatures, semantic model, actual host/public handlers and managed publication pending.')
    handoff['next_action'] = [
        'Observe same28245/PID21680/full146child32885 and complete all selected original API50 scopes. Closed API52 lesson29782 and package checks must not be repolled.',
        'Integrate package transfer into actual authenticated export/import policies; preserve original public schemas and no-effect claim ceiling until complete runtime/model/public evidence exists.',
        'For package privacy, review text/binary classification and malformed structured inputs; labels and byte scanning cannot replace actual independent privacy evidence.',
        'Qualify actual nonempty signed Lesson source and governed Context/Ontology successor; preserve original zero-catalog guards and source callbacks.',
        'Qualify all current public scopes and16 missing handlers, assigned Machine write permission and actual authority resolvers.',
        'Complete genuine pilot, R06/R07/S02 and sole final owner R08 before A01–A04.']
    handoff['terminal_bindings'].extend(proof['package_transfer_terminal_bindings'] +
        [proof['lesson_selection_public_terminal_binding'], bind(terminal)])
    path = RUN / 'custody-integration-handoff-0079.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0093.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
