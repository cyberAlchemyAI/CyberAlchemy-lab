"""Publish current partial progress with exact evidence and live job identities."""
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--qualification-session', type=int, required=True)
    parser.add_argument('--qualification-initial-chunk', required=True)
    parser.add_argument('--qualification-driver-pid', type=int, required=True)
    parser.add_argument('--qualification-child-pid', type=int, required=True)
    args = parser.parse_args()
    progress = BASE / 'api-v55/receipts/R03-0098.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0161.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    assert proof['implemented_public_handlers'] == 19 and proof['unimplemented_public_operation_count'] == 15
    assert proof['original_expiry_runtime_qualified'] and proof['original_expiry_actual_cases'] == 2
    assert not proof['current_API55_whole_suite_qualified']
    for pid in [args.qualification_driver_pid, args.qualification_child_pid]:
        assert Path('/proc', str(pid), 'stat').exists(), 'verify current job before publishing live identity'
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0098.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

**36/46 tasks closed; R03/R06 in progress.** API55 retains all 34 public
contracts and 293 inherited test methods, with 19 authored handlers and 15
unimplemented operations. The final actual owner checkpoint remains R08 after
complete S02. Candidate construction authorizes no admission or activation.

## Session opening repair

The retained API53 profile failed its unchanged original expiry test and showed
557,450 original-file reads. Profiler overhead prevents treating that result as
a normal latency measurement. API55 groups post-claim eligibility, exact delivery
verification and pure opening metadata in one synchronous verified source scope.
It reuses the exact delivered proof consumed by eligibility and resolves Profile
metadata from the sealed source copy. Full original source/package exit checks
precede creating the live resource and writing the Session journal. Original
source callbacks and registry remain; every policy check still reads current
policy, revocation and real clock. Each policy call also verifies the original Context producer once and reuses its module handle within that invocation. Original preflight and reader selection still run; no source bytes or grants are cached between calls. The failed API54 second expiry case is preserved. A final deadline check follows reply verification.

**Both original real-clock expiry cases passed unchanged: two cases, zero
failures/errors, exit 0.** Their 70-second deadlines and 90-second waits remain.
Each opens an active Session, holds a private RAM note, observes real timer
disposal and verifies erased memory plus expired inspection posture. Full source
exit and owned fixture cleanup completed. The failed predecessor evidence stays.

This proves the selected expiry behavior for API55 only. Seven affected original
Session cases are now running, followed by three actual package-import cases.
Those cover private memory, explicit connections, exact retry, source corruption,
close with invalidated Project State, policy revocation and the retained absolute
Assignment period. This successor's whole API remains unqualified. The previous
API53 three-case/nine-call import proof remains historical evidence for its exact
source; it does not transfer to API55.

## Older regression outcome

API50 classification16 completed with 14 passes and two failures, exit 1. One
expected target count was five while the result contained nine. The invalid-core
case lacked its expected retained failed validation report. Both need investigation;
neither is a pass or automatically a harmless assertion revision. The same driver
has moved to review11 and retains all original failures and clocks.

Across completed API50 selected scopes: 201 ran, 197 passed, three failed and one
errored. The 251 remaining selections include runner overlap. The earlier two
expiry failures and new classification failures remain preserved. Historical
API50 evidence does not qualify current API55.

## Remaining plan

Finish current affected and full API qualification and classification repairs.
Implement all 15 missing public operations. Complete general foreign/admitted
package authority and carrier coverage, public export with full dependency/privacy
closure, nonempty Lesson/Context/Ontology source, actual Machine write authority
and internal/specialized authority resolvers. Genuine R05 participant evidence,
R06/R07, all-member S02, sole actual R08 and independently authorized A01-A04 remain.
Existing/live stores, keys, canonical state and unrelated dirty work stay preserved.

Currentness161 passed; the DAG remains 36/46. No task or goal is marked complete
by this scoped repair. Exact current bindings and job handles are in the paired
progress index and handoff.
''')
    handoff = load(RUN / 'custody-integration-handoff-0083.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] + [89185, 84276, 85413, 59047]))
    handoff['same_live_jobs'] = [
        {'session_id': 67314, 'initial_chunk_id': 'c83434', 'state': 'last-observed-running',
         'owned_driver_PID': 73615, 'owned_child_PID': 79321, 'suite': 'API50 remaining251; review11 currently running',
         'driver_binding': bind(RUN / 'run-API50-remaining-regression-0002.py'), 'whole_API_qualified': False},
        {'session_id': args.qualification_session, 'initial_chunk_id': args.qualification_initial_chunk,
         'state': 'last-observed-running', 'owned_driver_PID': args.qualification_driver_pid,
         'owned_child_PID': args.qualification_child_pid,
         'suite': 'API55 affected Session7 then actual package3, ten selected cases',
         'driver_binding': bind(RUN / 'run-API55-affected-qualification-0001.py'), 'whole_API_qualified': False}]
    handoff['new_scoped_evidence']['API55_original_expiry'] = (
        'Two unchanged original 70-second/90-second real-clock expiry tests PASS, exit0. '
        'API55 pure opening metadata uses the original sealed scope and full source exit '
        'before LiveReader/journal; final reply deadline rechecked. Original callbacks, '
        'policy rereads, disposal, clocks and failures retained. Whole API unqualified.')
    handoff['new_scoped_evidence']['API50_classification_failure'] = (
        'Classification16 completed14 PASS/2 FAIL, exit1. Target count9 versus5 and missing '
        'retained failed native validation report require investigation. Total201 selected '
        'cases197 PASS/3 FAIL/1 ERROR. Remaining251 run under same driver, now review11.')
    handoff['terminal_bindings'].extend([proof['original_expiry_terminal_binding'],
        proof['API50_classification16_terminal_binding']])
    handoff['next_action'] = [
        'Continue both same live drivers without restart; inspect any completed/failed stage before new fixture work.',
        'Finish API55 original affected Session7 and actual package3 qualification, then every current inherited journey. Two expiry cases do not close R03.',
        'Investigate both original API50 classification failures and qualify a successor; preserve original failed reports and test assertions.',
        'Complete all15 missing operations, general package authority/carrier coverage, portable export/privacy, nonempty Lesson/Context/Ontology and actual Machine write/internal authority resolution.',
        'Complete genuine R05/R06/R07 and all-member S02, then sole actual R08 before separately authorized A01-A04.']
    path = RUN / 'custody-integration-handoff-0084.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0098.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'closed_tasks': 36, 'total_tasks': 46, 'authored_handlers': 19, 'unimplemented_operations': 15,
        'original_expiry_cases_passed': 2, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
