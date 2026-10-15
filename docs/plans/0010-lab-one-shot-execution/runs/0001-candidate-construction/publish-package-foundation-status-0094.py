"""Publish completed fixture proof, preserved source refusal and continuing actual job."""
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
    progress = BASE / 'api-v52/receipts/R03-0094.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0157.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    assert proof['package_transfer_current_pure_cases'] == 78
    assert proof['package_publication_complete_filesystem_fixture_cases'] == 33
    assert proof['package_full_source_size_probe_verdict'] == 'FAIL'
    terminal = RUN / 'R03-0094-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'session_id': 11543,
        'initial_chunk_id': '8f3141', 'final_chunk_id': '5475ea', 'actual_exit_code': 0,
        'result': 'PASS', 'currentness_binding': bind(currentness), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'goal_complete': False})
    source_analysis = RUN / 'PACKAGE-SOURCE-BOUNDARY-0094.md'
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0094.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

The full plan remains active and incomplete: 36/46 tasks closed, R03/R06 in
progress. Current public candidate API52 still has18 authored handlers and16
missing operations. All34 original contracts and293 inherited methods remain.
The sole final actual owner checkpoint is R08 after complete S02.

## New implementation and complete scoped proof

Package transfer v3 passed all78 pure cases with zero failures/errors and actual
exit0. All61 predecessor assertions, including the50 original assertions, were
retained. Public controls, requests, import mappings/dispositions, target bodies
and complete import plans retain1 MiB limits. Individual source originals are
capped at32 MiB, aggregate originals at40 MiB and complete archives at64 MiB,
further limited by the independent export contract. Archive/v3 and export
contract/v2 are explicit internal successors. Structured-looking text/binary
must pass strict parsing/privacy checks; labels cannot suppress malformed or
duplicate-key JSON errors. Archive verification checks frozen source on both
entry and exit. These values authenticate no Actor and grant no source authority.

Managed package publication v1 passed all33 real isolated filesystem fixture
cases with zero failures/errors and actual exit0. It uses pinned owned root
identity/scope, no-follow descriptors, private modes and exact bytes; exclusive
generation allocation, fsync and a final durable marker; bounded generation
counts and output bytes; read-only retries and preserved uncertainty. Tampering,
symlinks/hardlinks, FIFO, source/permission changes and interrupted writes were
covered. It returns the original File Materialization Receipt shape. All source
and permission callbacks in this suite are explicitly synthetic. No authenticated
package.export/import call or source replay is qualified by these cases.

## Actual source refusal retained

The size probe selected the exact API52-bound23,542,012-byte public snapshot.
It failed with actual exit1 while recursively scanning decoded baseline originals,
before package construction or publication. Persisted Agent Session descriptors
and a schema declaration contain session_memory fields; the descriptor's reference
and question arrays are not all empty. The generic privacy scan refuses them.
The failed attempt, source bindings and metadata-only finding are preserved.
This does not prove live RAM disclosure and grants no exemption, rewritten source,
omitted dependency, source privacy review or safe full-snapshot export.

The original public contract requests selected portable originals and complete
required dependencies. The next authenticated host implementation must prove
the selected artifact/carrier/reference/typed-edge/evidence closure. Unrelated
branch membership alone is not a semantic dependency. If a required original
fails privacy, refuse that package and expose the exact gap. For admission claims,
carry and verify the sufficient original source admission basis; a cut or receipt
label cannot replace it. Whole-branch export remains unqualified.

See PACKAGE-SOURCE-BOUNDARY-0094.md for the complete recommended integration.

## Existing scoped proof and continuing job

API52's completed lesson transport3/10 actual wire calls/three real Sessions remain
qualified only for the selected empty Lesson catalog. Nonempty/generalized Lesson
selection and the whole API remain unqualified.

The original API50 regression continues as session28245/driverPID21680/full146
child32885. Its typed10/failure18/controls11 selections completed PASS39 with actual
exits0;413 other selected cases await complete suite results. The same full146
runner remains alive and progressed into custody Session cases. Do not restart
it from an observation timeout or infer completion from individual live log lines.
Its source-specific scope does not transfer to API52.

## Next and remaining full scope

Integrate package export/import through actual current authentication, source
guards, complete portable closure, declared privacy, real deadlines/budgets and
durable claims. Import must pass original carrier/reference/typed/core/prospective
model validation before exposing a candidate Change Proposal. Add actual public
positive/negative/recovery cases. None of this is supplied by the new fixtures.

Complete the other missing operations, actual nonempty Lesson source and governed
Context/Ontology successor, current full public suites, assigned Machine write
authority and actual internal/specialized authority resolvers. Obtain genuine R05
participant evidence; complete R06/R07 and exact all-member S02; then the one R08
owner checkpoint, followed by independently authorized A01–A04.

Currentness157 passed:38 active receipts,77 preparation files,887 baseline sources
unchanged. R03-0094 binds15,916 files and explicitly retains incomplete task/goal
status and the failed full-source probe. No public package handlers, canonical
admission, genuine pilot, whole API, service activation or complete plan is claimed.
''')
    handoff = load(RUN / 'custody-integration-handoff-0079.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [63926, 73528, 18533, 71912, 15069, 11543]))
    handoff['same_live_jobs'] = [{'session_id': 28245, 'initial_chunk_id': 'c3944a',
        'state': 'last-observed-running', 'owned_driver_PID': 21680, 'owned_child_PID': 32885,
        'suite': 'API50 same452-case regression: complete39; same full146 running into custody Session cases',
        'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'), 'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        package_transfer='Frozen v3:78 pure PASS retaining61 predecessor assertions; separate1 MiB controls/32 MiB material/40 MiB originals/64 MiB archive bounds. No authenticated source/public qualification.',
        package_publication='Frozen v1:33 actual owned filesystem fixtures PASS. Exclusive fsync-marker generations/read-only retry/tampering and uncertainty; callbacks explicitly synthetic. Public/authenticated integration pending.',
        package_actual_snapshot='Exact23,542,012-byte source probe FAIL/exit1 before construction/publication: decoded Session descriptor/schema triggers privacy. Preserve failure; no full-source/privacy exemption or source truncation.')
    handoff['next_action'] = [
        'Continue same28245/PID21680/full146child32885 and complete every original selected API50 scope. Do not repoll closed jobs or restart on observation timeout.',
        'Use the original package contract to prove complete selected artifact/carrier/reference/typed-edge/evidence closure, and exact sufficient source admission basis when claimed. Unrelated whole-branch records are not automatically required dependencies; required privacy failures must refuse the package.',
        'Review exact persisted Agent Session descriptor/schema semantics versus actual runtime RAM. Preserve source-size-probe FAIL; no generic privacy allowlist or implicit safe binary label.',
        'Integrate package.export/import through actual authenticated policy, original source guards, budgets/clocks, durable claims, managed generations and verified readonly recovery; original prospective model validation must PASS before import result.',
        'Qualify nonempty signed Lesson source and governed Context/Ontology successor, every current public scope,16 missing handlers, assigned Machine write permission and actual authority resolvers.',
        'Complete genuine R05 participant evidence, R06/R07/S02 and sole final actual R08 before A01–A04.']
    handoff['package_source_boundary_analysis_binding'] = bind(source_analysis)
    handoff['terminal_bindings'].extend([bind(RUN / 'package-transfer-pure-terminal-0003.json'),
        bind(RUN / 'package-publication-terminal-0001.json'),
        bind(RUN / 'package-public-source-size-terminal-0001.json'), bind(terminal)])
    path = RUN / 'custody-integration-handoff-0080.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0094.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'source_boundary_analysis_binding': bind(source_analysis), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
