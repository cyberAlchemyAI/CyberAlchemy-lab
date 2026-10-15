"""Record original lesson.assess implementation and explicit qualification gaps."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v82'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parent_path = BASE / 'api-v81/receipts/R03-0117.json'
    parent = load(parent_path)
    source = API / 'source-manifest.json'
    manifest = load(source)
    rows = {row['path']: row for row in parent['files']}
    for row in manifest['files']:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    authoring = RUN / 'API82-lesson-application-authoring-checks-0001.json'
    checked = load(authoring)
    assert checked['result'] == 'PASS' and checked['authored_handlers'] == 23
    assert checked['original_inherited_methods'] == 323 and not checked['actual_runtime_qualified']
    for row in checked['files']:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    paths = [source, API / 'contract-profile.json', parent_path, authoring, RUN / 'API82-application-context-clarification-0001.json', RUN / 'API80-Machine-context-query-diagnosis-0001.json', Path(__file__).resolve()]
    for path in paths:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    missing = ['checkpoint.resolve', 'admission.apply', 'action.evaluate', 'action.dispatch', 'action.reconcile',
               'workflow.transition', 'challenge.resolve', 'ontology.project', 'installation.execute',
               'capability.adoption.prepare', 'release.prepare']
    value = {**parent, 'result': 'PASS', 'files': [rows[key] for key in sorted(rows)],
             'parent_progress_binding': bind(parent_path), 'current_API_version': 82,
             'source_binding': bind(source), 'profile_binding': bind(API / 'contract-profile.json'),
             'authored_public_handlers': 23, 'remaining_unimplemented_operations': missing,
             'lesson_apply_authored': True, 'lesson_apply_actual_runtime_qualified': False,
             'lesson_application_authoring_checks_binding': bind(authoring),
             'recorded_outcome_method_claim_ceiling': 'Exact recorded application outcome only; no general or causal effectiveness inferred.',
             'current_source_lesson_application_records': 0, 'positive_application_episode_required': True,
             'retained_predecessor_methods': 323, 'unchanged_method_ASTs': 320,
             'exact_handler_count_expectation_revisions': 3,
             'remaining_obligations': [
                 'Observe same actual API79 job35646 and API80 job19391; bind actual full20-case results without restarting on partial output.',
                 'Qualify original lesson.apply with actual live Session, current selected lesson, applicability/instruction, conflict override and delegated operation bounds; qualify lesson.assess against an actual recorded application/evidence source.',
                 'Implement remaining11 public operations: ' + ','.join(missing) + '.',
                 'Qualify all affected original API selections including current/historical reads and reference wrong-kind/Principal/scope/ambiguity refusals.',
                 'Complete original R03,R05 journeys,R06 privacy,R07 acceptance and S02 exact whole package before sole actual R08 owner response; preserve A01-A04 effect scope.'],
             'change': 'Original lesson.apply candidate handler authored with actual parent operator/Session custody, current lesson, exact selection/applicability/instruction, scoped conflict overrides and delegated operation bounds. Original prospective core/schema validation returns attributed application ChangeProposal through current guarded calculation/journal path;0tool dispatches.23handlers authored,11missing.323method bodies retained;3exact registry-count expectations22to23. Authoring checks passed; actual runtime qualification remains pending. Original API80 immediate Machine Context construction diagnostic passed1actual case, separating bridge construction from long read case. Complete original20case jobs remain running',
             'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False,
             'claim_ceiling': 'Existing qualified components plus exact lesson.apply implementation/authoring evidence. No actual application, interpreted outcome, causal/general efficacy, current Machine/full API, owner decision or admission inferred.'}
    output = API / 'receipts/R03-0118.json'
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(output), 'bound_files': len(rows),
                      'authored_handlers': 23, 'remaining_handlers': 11, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
