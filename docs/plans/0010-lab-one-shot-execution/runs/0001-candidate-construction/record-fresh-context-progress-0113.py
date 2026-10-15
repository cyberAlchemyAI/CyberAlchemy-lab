"""Bind complete Context component proof and exact pending20-case API selection."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v77'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parent_path = BASE / 'api-v75/receipts/R03-0112.json'
    parent = load(parent_path)
    rows = {row['path']: row for row in parent['files']}
    context_proof = BASE / 'current-context-delivery-v9/receipts/qualification-0001.json'
    proof = load(context_proof)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert proof['actual_build_exit_code'] == proof['actual_check_exit_code'] == proof['actual_audit_exit_code'] == 0
    source = API / 'source-manifest.json'
    profile = API / 'contract-profile.json'
    manifest = load(source)
    assert manifest['total_retained_method_bodies'] == 323
    assert manifest['unchanged_inherited_method_count'] == 309 and manifest['explicit_revised_methods'] == 14
    assert manifest['authored_handler_count'] == 21 and not manifest['whole_API_qualified']
    for document in [proof, manifest]:
        for row in document['files']:
            assert rows.get(row['path'], row) == row, row['path']
            rows[row['path']] = row
    paths = [parent_path, context_proof, source, profile, Path(__file__).resolve(),
             RUN / 'API77-independent-selection-0001.json', RUN / 'run-API77-machine-lifecycle-full-0001.py']
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'result': 'PASS', 'files': [rows[key] for key in sorted(rows)],
             'parent_progress_binding': bind(parent_path), 'current_API_version': 77,
             'source_binding': bind(source), 'profile_binding': bind(profile),
             'fresh_Context_component_qualified': True, 'fresh_Context_qualification_binding': bind(context_proof),
             'fresh_Context_original_cases': 50, 'fresh_Context_independent_audit_checks': proof['audit_checks'],
             'fresh_Context_generated_artifact_carriers': 30,
             'fresh_API77_frozen': True, 'fresh_API77_retained_methods': 323,
             'fresh_API77_unchanged_methods': 309, 'fresh_API77_exact_binding_revised_methods': 14,
             'current_Machine_qualified': False, 'current_Machine_and_termination_cases_qualified': False,
             'Machine_lifecycle_selection_binding': bind(RUN / 'API77-independent-selection-0001.json'),
             'Machine_lifecycle_live_job': 38356, 'Machine_original_selected_cases': 14,
             'termination_original_selected_cases': 6, 'Machine_lifecycle_terminal_observed': False,
             'remaining_obligations': [
                 'Observe same actual20-case API77 Machine/termination job38356; do not rerun because output is partial. Record actual result without changing clock, permissions or900-second ceiling.',
                 'Qualify all affected inherited selections and carrier resolver ambiguity/wrong-kind/Principal/scope cases.',
                 'Implement all13 missing handlers; complete original R05/R06/R07 and S02 before the sole R08 owner decision. Preserve A01-A04 effects.',
                 *parent['remaining_obligations']],
             'change': 'Context9 actual build and all50 cases passed; independent audit passed43827 checks and retained all11562 parent files.30 derived carriers retain23 original bodies and25 native joins. API77 exact source/profile frozen with all323 method bodies retained:309 unchanged,14 only rebind current path/identity/period/handler-count expectations. Actual20-case original Machine/termination selection running; no runtime outcome claimed.',
             'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False,
             'claim_ceiling': 'Qualified Source5/Reader4/Mapper4/Context9 components plus exact frozen API77 and running original20-case selection. Current Machine, full API, owner decision, admission and activation remain pending actual evidence.'}
    output = API / 'receipts/R03-0113.json'
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(output), 'bound_files': len(rows),
                      'same_live_job': 38356, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
