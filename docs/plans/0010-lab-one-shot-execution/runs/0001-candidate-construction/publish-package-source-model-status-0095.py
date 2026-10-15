"""Publish exact completed source/model evidence and continuing regression handle."""
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
    progress = BASE / 'api-v52/receipts/R03-0095.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0158.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(r['task'] == 'R03' and r['receipt'] == progress.relative_to(ROOT).as_posix()
               for r in current['active_receipt_checks'])
    assert proof['package_closed_Work_prospective_target_qualified']
    terminal = RUN / 'R03-0095-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'session_id': 17874,
        'initial_chunk_id': '0ffb27', 'final_chunk_id': '0b77ed', 'actual_exit_code': 0,
        'result': 'PASS', 'currentness_binding': bind(currentness), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'goal_complete': False})
    analysis = RUN / 'PACKAGE-SOURCE-MODEL-0095.md'
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0095.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

The full plan remains active and incomplete:36/46 tasks closed; R03/R06 in progress.
Current public API52 still has18 authored handlers and16 missing operations. All34
original contracts and293 inherited methods remain. Sole final actual R08 remains
after complete S02; no canonical admission is implied by the evidence below.

## Actual completed source/model work

The actual original signed-source replay audit completed with original source exit
guards and unchanged projection. It read two actual current Work bodies and found
five unresolved references under the original current-artifact rules. Current
episode Work closes its Project/Goal/Intent/declared counterpart inputs; its output
protocol is not a current artifact. The older Work also has Goal/input gaps.
Expected outputs are reported separately but remain subject to the unchanged
validator. Audit PASS means observations completed; no portable graph is qualified.

A separately authored Work candidate passed one actual authenticated original
change.validate call. All four original checks passed and all five reference
checks resolved, with zero gaps: source/target/schema/core; explicit typed
connection closure; Work references; privacy. The target uses exact current
Project/Goal/Intent references and names that existing Intent as expected byte-exact
review/delivery output. It invents no output, completed Work or successful delivery.
The original source/schema/validators were unchanged. All owned fixtures were
cleaned up and original source exit completed. This prospective target gives import
a verified shape; it does not implement or qualify a package operation.

The first harness attempt failed before public dispatch because it read the
authentication envelope as context. It remains preserved with actual exit1. The
successor also satisfies the original Work minItems1 output rule using a captured
Intent; no schema or original source field was loosened or rewritten.

See PACKAGE-SOURCE-MODEL-0095.md for exact source gaps and integration boundaries.

## Preserved earlier evidence and remaining implementation

Package-transfer v3 pure78 and publication v1 filesystem33 completed PASS/exit0.
Those fixtures do not authenticate package calls, source admission or target model.
The exact23.5 MB whole-source probe remains FAIL/exit1 at decoded Session metadata
privacy, before construction/publication. Neither new target validation nor fixture
publication permits bypassing that refusal or silently removing a dependency.

API52 lesson transport3/10 wire calls/three actual Sessions completed for the empty
catalog only. Nonempty/generalized Lesson selection and whole API remain unqualified.

The same API50 regression remains session28245/driverPID21680/full146child32885.
Typed10/failure18/controls11 completed PASS39; the other413 selected cases await
complete results. The same full146 child is alive and progressed through custody
Session cases. Do not restart on observation timeout or count partial log lines as
completed selections. Historical API50 scope does not qualify current API52.

Next: construct explicit portable source/candidate selection, complete dependency
and provenance/privacy profiles, and authenticated package export/import around
exact validated candidates and independently selected controls. Preserve bytes,
original callbacks, clocks, budgets, typed/core validation, durable claims, managed
generation and verified read-only recovery. Qualify actual public positive/negative
cases before any package runtime claim. No public package handlers were added.

Full scope still includes the other missing operations, nonempty Lesson source and
governed Context/Ontology successor, all current public suites, assigned Machine
write authority and actual internal/specialized authority resolvers. Complete genuine
R05 participant evidence, R06/R07 and all-member S02, then one actual R08 and
independently authorized A01–A04. Existing/live stores/keys, activation, external
effects, push/deploy and unrelated dirty work remain outside construction.

Currentness158 passed:38 active receipts,77 preparation files and887 baseline
sources unchanged. R03-0095 binds15,928 files. No whole API, portable package,
genuine pilot, admission, successful delivery or complete plan is claimed.
''')
    handoff = load(RUN / 'custody-integration-handoff-0080.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [87494, 25581, 96852, 62943, 63177, 17874]))
    handoff['same_live_jobs'] = [{'session_id': 28245, 'initial_chunk_id': 'c3944a',
        'state': 'last-observed-running', 'owned_driver_PID': 21680, 'owned_child_PID': 32885,
        'suite': 'API50 same452 selected-case regression: complete39; same full146 running in custody Session cases',
        'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'), 'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        package_original_source='Actual original signed replay audit PASS with source exit: two Work bodies/five unresolved references, current inputs and expected outputs separated; source projection unchanged, no portable graph qualification.',
        package_target_Work='One actual authenticated API52 change.validate PASS: four original checks/five resolved references/zero gaps for new candidate Work with exact captured Project/Goal/Intent and expected existing Intent delivery. No new output, successful Work, source rewrite, admission or package operation.')
    handoff['package_source_model_analysis_binding'] = bind(analysis)
    handoff['next_action'] = [
        'Continue same28245/driver21680/full146child32885 and every original selected API50 scope. Never repoll closed handles or restart from observation timeout.',
        'Use exact separately validated candidate source/proposal originals or closed actual selected source roots; carry complete declared dependencies and sufficient original source admission basis when claimed. Missing required references remain refusals.',
        'Use the actual prospective Work target qualification for import; actual public package source/controls/transport/model evidence must still be supplied. The existing Intent expected output is not a produced output or successful delivery.',
        'Preserve full-source privacy FAIL and actual Work-reference gaps; no silent truncation, generic allowlist, output instantiation, schema weakening or changed original callbacks.',
        'Integrate and qualify package.export/import with independently authenticated controls, real budgets/clocks, durable claims and verified managed publication/read-only recovery; then all other16 missing handlers/current suites.',
        'Qualify nonempty signed Lesson/Context/Ontology successor, actual assigned Machine write authority and actual internal/specialized authority resolvers; complete genuine R05/R06/R07/S02 and sole actual R08 before A01–A04.']
    handoff['terminal_bindings'].extend(proof['package_source_model_terminal_bindings'] + [bind(terminal)])
    path = RUN / 'custody-integration-handoff-0081.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0095.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'source_model_analysis_binding': bind(analysis), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
