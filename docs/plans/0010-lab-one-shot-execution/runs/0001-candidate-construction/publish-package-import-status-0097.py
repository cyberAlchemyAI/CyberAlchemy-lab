"""Publish the verified public import lane and the exact incomplete plan state."""
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
    progress = BASE / 'api-v53/receipts/R03-0097-0002.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0160.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    assert proof['implemented_public_handlers'] == 19 and proof['unimplemented_public_operation_count'] == 15
    assert proof['package_import_same_cut_Work_candidate_qualified']
    terminal = RUN / 'R03-0097-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 1205, 'initial_chunk_id': '3be17d', 'final_chunk_id': '89f9f0',
        'actual_exit_code': 0, 'result': 'PASS', 'currentness_binding': bind(currentness),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'goal_complete': False})
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0097.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

**36/46 tasks are closed.** R03/R06 remain in progress. API53 has **19 authored
handlers and 15 unimplemented operations**, retaining all 34 original public API
contracts and 293 inherited test methods. The full plan remains incomplete. Its
sole final actual owner checkpoint remains R08 after complete S02.

## Actual completed implementation

The actual operator dispatcher now supports package.import for independently
selected controlled Work candidates in the same current target cut. A separate
policy selects the managed generation, native source/target proposals, mapping,
disposition and exact provenance before channel authentication. No caller path,
uploaded archive or message label grants storage or authority.

Preflight uses the original native prospective validator for both proposals before
the durable claim. Required resolved Work references, original dependency bodies,
source metadata/cores and carrier schemas must match the archive and declared
graph. Every selected artifact and material is accounted for. Targets must match
exact independently supplied bytes and stable cores. After the claim, evaluation
repeats and evidence commits only after original source exit checks. The returned
ChangeProposal retains exact package/mapping/disposition provenance. It remains
unadmitted, and source material is never retired automatically.

**Three actual test cases passed, with nine public calls, zero failures/errors and
exit 0.** They cover the validated import and operation inspection, forged Actor,
changed control, stale cut, expired deadline, conflicting key, verified read-only
retry and tampered-package recovery without rewrite. The positive case validates
source and target Work proposals and accounts for four artifacts/ten materials.
Original source exit and owned temporary fixture cleanup completed. No original
source callback, clock, validator, deadline or key was changed.

Package publication permission is explicitly synthetic fixture permission. Actual
import uses the real one-use cryptographic channel and original signed target
replay. This qualifies the same-cut candidate Work lane only. General foreign or
admitted-source import, broader carrier portability and public export remain
unfinished; unsupported use is refused. Current API53 inherited journeys, including
its separately rebound lesson host, require their own full qualification.

## Regression outcome and active continuation

The original API50 full146 suite completed with one failure and one error, both in
the real 70-second expiry tests. One session.open became indeterminate after its
deadline; another Session was already disposed when the test tried to access it.
The old driver stopped on the error. Both original processes and session28245 are
terminal. Completed evidence and original deadlines are preserved.

Across the completed typed10/failure18/controls11/full146 scopes, 185 selected cases
ran: 183 passed, one failed, one errored. These include overlapping runner scopes,
not 185 unique methods. An exclusive continuation scheduler resumes only the six
unexecuted suites, totalling 267 selected cases. It started after the actual API53
import process exited with source/cleanup checks complete. Current live handle is
session67314, driver73615, classification16child73616. Never restart from an
observation timeout. Completed API50 evidence does not qualify current API53.

## Remaining full-plan work

Complete all 15 missing operations, general package import authority/carrier
coverage, complete portable dependency/privacy export, current full API journeys,
and expiry performance/reply behavior while retaining original assertions and
deadlines. Preserve the unresolved original Work references and full-source privacy
refusal. Complete nonempty Lesson/Context/Ontology source qualification, actual
Machine write authority and internal/specialized authority resolvers. Genuine R05
participant evidence, R06/R07, all-member S02, one actual R08 and independently
authorized A01–A04 remain required. Candidate construction grants no canonical
admission, live activation, external effects or push.

Currentness160 passed: 38 active receipts, 77 preparation files and 887 baseline
sources unchanged. The first progress draft's inherited API52 count fields are
preserved; its exclusive successor aligns current counts with frozen API53.
''')
    handoff = load(RUN / 'custody-integration-handoff-0082.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [28245, 49414, 28664, 43802, 13386, 1205]))
    handoff['same_live_jobs'] = [{'session_id': 67314, 'initial_chunk_id': 'c83434',
        'state': 'last-observed-running', 'owned_driver_PID': 73615, 'owned_child_PID': 73616,
        'suite': 'API50 six unexecuted suites267 selected cases; classification16 currently running',
        'driver_binding': bind(RUN / 'run-API50-remaining-regression-0002.py'),
        'whole_API_qualified': False}]
    handoff['new_scoped_evidence']['package_public_import'] = (
        'API53 actual authenticated import: complete3 cases/9 calls PASS/exit0, original native source '
        'and target Work validation, exact4-artifact/10-material accounting/provenance, Actor/control/cut/'
        'deadline/idempotency refusals and verified read-only retry/tampering recovery. Original source '
        'exit and owned cleanup complete. Same-cut controlled candidate Work lane only; publication '
        'permission is synthetic; general foreign/admitted-source import and export remain incomplete.')
    handoff['new_scoped_evidence']['API50_full146_failure'] = (
        'Full146 completed with one real deadline failure and one disposed-resource error in original '
        '70-second expiry cases; old driver stopped with exit1. Retain all185 completed selected cases '
        '(183 PASS/1 FAIL/1 ERROR) and resume only267 unexecuted selections. No deadline extension.')
    handoff['terminal_bindings'].extend([proof['package_import_actual_terminal_binding'],
        proof['API50_full146_terminal_binding'], bind(RUN / 'API50-driver-failed-attempt-terminal-0001.json'), bind(terminal)])
    handoff['next_action'] = [
        'Continue the same67314/driver73615/child73616 remaining-suite scheduler; original185 completed selections and two expiry defects remain preserved. Do not restart from observation timeout.',
        'Repair and qualify Session expiry performance/reply behavior in an implementation successor with the original70-second tests and assertions unchanged; actual expiry must dispose private resources.',
        'Complete general foreign/admitted-source package authority/provenance and carrier coverage and authenticated public export with complete original dependency/privacy proof. The actual same-cut Work import lane does not replace the full package contracts.',
        'Run every current API53 inherited journey and actual new operation scopes; historical API50 and API52 qualifications do not transfer. Preserve all34 original contracts and293 inherited methods.',
        'Complete the other15 unimplemented public operations, nonempty signed Lesson/Context/Ontology source, actual assigned Machine write authority and internal/specialized authority resolvers.',
        'Complete genuine R05/R06/R07 and all-member S02, then sole actual R08 before independently authorized A01–A04. Preserve existing/live stores, keys, unrelated dirty work and original source/privacy failures.']
    path = RUN / 'custody-integration-handoff-0083.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0097.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'closed_tasks': 36, 'total_tasks': 46, 'authored_handlers': 19, 'unimplemented_operations': 15,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
