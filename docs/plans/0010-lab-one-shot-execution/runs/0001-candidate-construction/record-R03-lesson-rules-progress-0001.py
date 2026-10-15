"""Bind complete pure lesson selection checks without closing R03 or public gaps."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path): return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parent = BASE / 'api-v50/receipts/R03-0088.json'
    prior = load(parent)
    package = BASE / 'lesson-selection-rules-v1'
    source = load(package / 'source-manifest.json')
    report_path = package / 'receipts/checks-0001.json'
    report = load(report_path)
    terminal_path = RUN / 'lesson-selection-rules-terminal-0001.json'
    terminal = load(terminal_path)
    assert terminal['actual_exit_code'] == 0 and terminal['full_selected_suites_completed']
    assert report['result'] == 'PASS' and report['pure_cases'] == 56
    assert report['pure_failures'] == report['pure_errors'] == 0
    assert report['original_W06_cases'] == 53 and report['original_W06_full_suite_completed']
    assert report['original_W06_actual_exit_code'] == 0 and report['source_unchanged_before_and_after']
    assert report['actual_public_calls'] == 0 and not report['public_handler_integrated']
    assert report['source_sha256'] == source['source_sha256']
    rows = {row['path']: row for row in prior['files']}
    for row in source['files'] + source['input_bindings'] + report['files']:
        assert bind(ROOT / row['path']) == row
        rows[row['path']] = row
    for path in [parent, report_path, terminal_path, Path(__file__).resolve()]:
        row = bind(path); rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    result = {**prior, 'files': [rows[key] for key in sorted(rows)], 'parent_progress_binding': bind(parent),
              'change': 'Implemented and froze complete pure lesson selection rules.56 synthetic rule cases and53 unchanged original W06 tests PASS with actual runner exit0 and exact source guards. Public lesson.select composition remains unimplemented;17 handlers/17 missing operations unchanged. API50 serialized452-case regression continues under the same driver.',
              'lesson_selection_rules_source_sha256': source['source_sha256'],
              'lesson_selection_rules_report_binding': bind(report_path),
              'lesson_selection_rules_terminal_binding': bind(terminal_path),
              'lesson_selection_pure_rule_cases': 56, 'lesson_selection_retained_W06_cases': 53,
              'lesson_selection_pure_rules_qualified': True, 'lesson_selection_actual_public_calls': 0,
              'lesson_selection_public_handler_integrated': False, 'lesson_selection_actual_live_Session_qualified': False,
              'superseded_obligations_preserved_in_parent': prior['remaining_obligations'],
              'remaining_obligations': [
                  'Complete all452 selected API50 regression cases with exact original clocks, source and permission boundaries; retained runner overlap does not establish unique coverage.',
                  'Preserve API47 actual exit143 and API48 unknown exit, interrupted controls and failed typed evidence; no cleanup or original terminal outcome is inferred or replaced.',
                  'Implement and qualify every one of17 named missing public operations under the original34 contracts and all current source/permission/refusal/retry/recovery/uncertainty criteria.',
                  'Compose lesson.select with actual authenticated live Agent/Session/Assignment, independently selected policy and complete current signed empty/nonempty inventory. Pure facts and synthetic reviews authenticate nothing.',
                  'Complete assigned Machine typed policy and host participation, governed internal endpoint contracts and specialized canonical authority resolvers.',
                  'Use genuinely reviewed complete model changes and exact independently scoped operational authority where required; synthetic fixtures cannot supply either.',
                  'Complete genuine R05 participant evidence, R06, R07 and full S02 before the sole actual R08 owner decision.',
                  'Actual owner outcomes and independent scoped authorization remain required before A01-A04 effects.'
              ],
              'claim_ceiling': 'Current exact API50 typed operator scoped qualification plus56 synthetic pure lesson rule checks and53 retained W06 tests only. Public lesson.select,17 missing operations, assigned Agent typed permission, genuine use/review, full regression/S02/admission and plan completion remain pending.',
              'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v50/receipts/R03-0089.json'
    with path.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
                      'pure_cases': 56, 'original_W06_cases': 53, 'task_complete': False}), flush=True)


if __name__ == '__main__': main()
