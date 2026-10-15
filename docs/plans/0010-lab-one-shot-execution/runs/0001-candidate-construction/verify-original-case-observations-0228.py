"""Independent frozen-plan/AST/event ledger; no domain or fixture execution.

Completeness of observations is distinct from source-guarded qualification,
unittest outcome, process exit and cleanup. Original failures stay failures.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v12'
SOURCE = '5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PROFILE = '2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'
SEEDS = {
    'final-api-regression-plan-0177.json': '8447e875378112d2fe73a158da75f40c02dc6e63fc65ad08c7e2ef7a6025f03a',
    'final-api-regression-recovery-plan-0213.json': '8ca9836e47740b7aa921c70ce81f40d2918bd70497814c41292c48afdf889b17',
    'final-api-regression-fixture-recovery-plan-0215.json': '25d0b54f0c9110d9ae25d66d93e3825b5e2714310c6bb7682c92a4f8e5c124d4',
    'API12-worker0-terminal-verification-0204.json': '2173341e00c6107b18ff9c4acebd07247fd517b3d7519205d7973a228cd2c16d',
    'machine-terminal-recovery-0223.json': '9485578eac32611647dde423d80eaa9fa1d9f195689ee6fdb1085a46150e74a2',
    'package-export-diagnostic-0219.json': '6bebb034ff1c17b4ba56805917947a90506e533edbb5620a00ad9f0638d6b180',
    'ARE-original-case-ledger-0228.json': 'a38bb71b2d603e286300ceb20f5f09fc281585638d39c262cbc0f4d8e13d5d7b',
}
STEMS = [
    ('session34', 'final-api-regression-0173-0177.sequential-fcffea20c78446ae', 'final-api-regression-0173-0177-session.log', 34, 0),
    ('old-worker0', 'final-api-regression-0173-0183.worker-0', 'final-api-regression-0173-0183-worker-0.log', 48, 143),
    ('old-worker1', 'final-api-regression-0173-0183.worker-1', 'final-api-regression-0173-0183-worker-1.log', 38, None),
    ('old-worker2', 'final-api-regression-0173-0183.worker-2', 'final-api-regression-0173-0183-worker-2.log', 49, 1),
    ('old-worker3', 'final-api-regression-0173-0183.worker-3', 'final-api-regression-0173-0183-worker-3.log', 34, None),
    ('old-worker4', 'final-api-regression-0173-0183.worker-4', 'final-api-regression-0173-0183-worker-4.log', 49, None),
    ('old-worker5', 'final-api-regression-0173-0183.worker-5', 'final-api-regression-0173-0183-worker-5.log', 46, 1),
    ('IR-ordinary19', 'final-api-regression-0173-0190.sequential-37cb619094fd309d', 'final-api-regression-0173-0190-ir-ordinary.log', 19, 0),
    ('recovery11', 'final-api-regression-0173-0213.worker-remaining-1', 'final-api-regression-0173-0213-worker-remaining-1.log', 11, 1),
    ('setup-NameError0', 'final-api-regression-0173-0213.worker-remaining-3', 'final-api-regression-0173-0213-worker-remaining-3.log', 0, 1),
    ('Machine14', 'final-api-regression-0173-0215.worker-machine', 'final-api-regression-0173-0215-worker-machine.log', 14, 1),
    ('IR-tamper3', 'final-api-regression-0173-0224.sequential-b0f69bf2edbeceb9', 'final-api-regression-0173-0224-ir3.log', 3, 0),
]
PINS = {}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        value = {}
        for key, entry in items:
            require(key not in value, 'duplicate JSON key')
            value[key] = entry
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def bind(path, expected=None):
    path = Path(path)
    require(path.is_file() and not path.is_symlink() and not any(x.is_symlink() for x in path.parents), 'missing/unsafe ledger material: ' + str(path))
    raw = path.read_bytes()
    digest = sha(raw)
    require(expected is None or digest == expected, 'selected original binding differs: ' + str(path))
    name = str(path.relative_to(ROOT))
    old = PINS.setdefault(name, {'path': name, 'sha256': digest, 'size_bytes': len(raw)})
    require(old['sha256'] == digest, 'ledger input changed within verification')
    return {'path': name, 'sha256': digest}


def load(path):
    bind(path)
    return parse(Path(path).read_bytes())


def bound_rows(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            yield value
        for child in value.values():
            yield from bound_rows(child)
    elif isinstance(value, list):
        for child in value:
            yield from bound_rows(child)


def verify_bound_rows(value):
    for row in bound_rows(value):
        path = Path(row['path'])
        # Protocol row paths are exact repository bindings, not store selectors.
        if not path.is_absolute() and (ROOT / path).is_file():
            bind(ROOT / path, row['sha256'])


def discover(directory):
    methods, modules = {}, {}
    for path in sorted(directory.glob('*.py')):
        tree = ast.parse(path.read_bytes(), filename=str(path))
        found = False
        normalized = copy.deepcopy(tree)
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                for method in cls.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith('test_'):
                        key = path.name + ':' + cls.name + '.' + method.name
                        require(key not in methods, 'duplicate declared method AST')
                        methods[key] = sha(ast.dump(method, annotate_fields=True, include_attributes=False).encode())
                        found = True
        if found:
            bind(path)
            for cls in normalized.body:
                if isinstance(cls, ast.ClassDef):
                    cls.body = [x for x in cls.body if not (isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name.startswith('test_'))]
            modules[path.name] = sha(ast.dump(normalized, annotate_fields=True, include_attributes=False).encode())
    return methods, modules


def failure_class(row):
    method, detail = row['declared_method'], row['detail']
    if '34 != 24' in detail:
        return 'stale-literal-supported-operation-count'
    if method.endswith('OriginalAPI.test_04_actual_product_revision_witness') and 'current-episode-0003.candidate.1' in detail and 'KeyError' in detail:
        return 'stale-exact-product-revision-selector'
    if 'datetime.datetime' in detail and 'not less than datetime.datetime' in detail and 'assert_live' in detail:
        return 'real-outer-request-deadline-missed-before-intended-case-assertion'
    if method.startswith('test_package_export.py:PackageExportAPI.') and 'closure-missing' in detail and 'Original native proposal validation did not close all export obligations.' in detail:
        return 'invalid-positive-package-export-fixture-native-Work-relation_refs-empty'
    return 'unclassified-retained-failure-needs-investigation'


def main():
    out = RUN / 'original-case-observations-0228.json'
    require(not out.exists(), '0228 observation receipt already exists')
    began = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    for name, digest in SEEDS.items():
        bind(RUN / name, digest)
    source_binding = bind(API / 'source-manifest.json', SOURCE)
    profile_binding = bind(API / 'contract-profile.json', PROFILE)
    source = load(API / 'source-manifest.json')
    require(len(source['files']) == 23062, 'original full source closure differs')
    guard_path = API / 'guard.py'
    guard_pin = next(x['sha256'] for x in source['files'] if x['path'] == str(guard_path.relative_to(ROOT)))
    bind(guard_path, guard_pin)
    spec = importlib.util.spec_from_file_location('_independent_original_source_guard_0228', guard_path)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    require(Path(guard.__file__).resolve() == guard_path, 'unselected original source guard')
    first = guard.verify(SOURCE)
    require(first == source, 'original full-history entry guard differs')
    plan = load(RUN / 'final-api-regression-plan-0177.json')
    wanted = set(plan['all_declared_methods'])
    require(len(wanted) == len(plan['all_declared_methods']) == 345 and len(plan['original_declared_methods']) == 323
            and len(plan['added_installation_release_methods']) == 22, 'exact original 323+22 plan differs')
    current, current_modules = discover(API)
    old, _ = discover(ROOT / plan['original_api_directory'])
    require(set(current) == wanted and set(old) == set(plan['original_declared_methods']), 'original/current declared AST sets differ')
    require(all(current[k] == v['method_ast_sha256'] for k, v in plan['method_inventory']['methods'].items()), 'frozen Plan0177 method AST differs')
    require(all(current_modules[k] == v['non_test_module_ast_sha256'] for k, v in plan['method_inventory']['modules'].items()), 'frozen setup/teardown/helpers/module AST differs')
    require(all(old[k] == v['method_ast_sha256'] for k, v in plan['original_method_inventory']['methods'].items()), 'API96 original AST differs')
    revisions = {r['method']: r for r in plan['method_ast_comparison']['changed_original_methods']}
    require({k for k in old if old[k] != current[k]} == set(revisions) and len(revisions) == 2, 'documented existing method revisions differ')
    verify_bound_rows(plan)
    recoveries = {name: load(RUN / name) for name in ['final-api-regression-recovery-plan-0213.json',
        'final-api-regression-fixture-recovery-plan-0215.json', 'API12-worker0-terminal-verification-0204.json',
        'machine-terminal-recovery-0223.json', 'package-export-diagnostic-0219.json',
        'final-api-regression-ir-disposition-0190.json', 'final-api-regression-recovery-disposition-0213.json',
        'original-ir3-recovery-disposition-0224.json']}
    for value in recoveries.values():
        verify_bound_rows(value)
    diagnostic = recoveries['package-export-diagnostic-0219.json']
    reasons = [obj['original_json']['details']['reason'] for row in diagnostic['native_validation_returns']
               for obj in row['retained_original_check_objects']]
    require(reasons and all("['relation_refs'] [] should be non-empty" in reason for reason in reasons), 'retained actual package-export native check cause differs')
    work_schema = load(ROOT / 'authority/artifact-types/work/v1/schema.json')
    require(work_schema['properties']['relation_refs']['minItems'] == 1, 'original Work schema relation requirement differs')
    ledgers, methods, extra_failures = [], {}, []
    for label, stem, log_name, count, process_exit in STEMS:
        event_path, report_path, log_path = RUN / (stem + '.events.jsonl'), RUN / (stem + '.json'), RUN / log_name
        events_binding, log_binding = bind(event_path), bind(log_path)
        events = [parse(line) for line in event_path.read_bytes().splitlines()]
        log = log_path.read_text()
        opening = events[0]
        require(opening['phase'] == 'starting' and opening['source_pin'] == SOURCE and opening['profile_pin'] == PROFILE, 'wrong original source/profile event')
        bind(ROOT / opening['worker_plan_binding']['path'], opening['worker_plan_binding']['sha256'])
        completed = [x for x in events if x['phase'] == 'case-completed']
        running = [x for x in events if x['phase'] == 'running']
        terminal = [x for x in events if x['phase'] == 'terminal']
        require(len(completed) == count and len({x['declared_method'] for x in completed}) == count, 'bucket completed count/uniqueness differs')
        require(any(x['phase'] == 'full-history-entry-guard-passed' for x in events), 'original bucket entry guard unavailable')
        for event in completed:
            key = event['declared_method']
            require(key in wanted and key not in methods and event['result'] in ('PASS', 'FAIL', 'ERROR'), 'unplanned/duplicate/unsupported completed observation')
            require(any(x['declared_method'] == key and x['test'] == event['test'] and x['at'] <= event['at'] for x in running), 'completed observation lacks actual matching start')
            methods[key] = {'bucket': label, 'original_event_binding': events_binding, 'original_event': event,
                            'current_method_AST_sha256': current[key], 'original_method_AST_sha256': old.get(key),
                            'documented_existing_revision': revisions.get(key), 'installation_release_addition': key in plan['added_installation_release_methods']}
        report = load(report_path) if report_path.exists() else None
        if report:
            verify_bound_rows(report)
            require(report['events_binding'] == events_binding and report['actual_methods'] == count, 'saved report/event count binding differs')
            reported = [{k: v for k, v in x.items() if k not in ('at', 'phase')} for x in completed]
            require(report['cases'] == reported and report['source_guarded_entry_completed'], 'saved report does not preserve actual cases')
            require(not report['whole_API_qualified'] and not report['goal_complete'] and not report['method_or_fixture_monkeypatches']
                    and not report['original_clocks_or_callbacks_changed'], 'original report exceeds qualification/effect boundary')
        full_exit = bool(terminal and terminal[-1].get('full_history_exit_guard_passed'))
        if label in ('old-worker1', 'old-worker3', 'old-worker4'):
            require(not terminal and report is None, 'interrupted original bucket unexpectedly has a full terminal')
        else:
            require(len(terminal) == 1 and terminal[0]['actual_methods'] == count and full_exit, 'actual original terminal/full exit guard missing')
        fixture_errors = report['fixture_errors'] if report else []
        if label == 'setup-NameError0':
            require(count == 0 and len(fixture_errors) == 1 and "NameError: name 'PROFILE' is not defined" in fixture_errors[0]['detail'], 'original zero-method fixture NameError differs')
            extra_failures.append({'kind': 'zero-method-original-fixture-setup-error', 'bucket': label, 'original_fixture_errors': fixture_errors,
                                   'report_binding': bind(report_path), 'counts_as_completed_method': False})
        if label == 'Machine14':
            require(report is None and terminal[-1]['result'] == 'PASS' and 'Ran 14 tests' in log and '\nOK\n' in log
                    and "is not in the subpath of '/home/vlad_/projects/CyberAlchemy-lab'" in log, 'original late serialization failure differs')
            recovered = recoveries['machine-terminal-recovery-0223.json']
            require(recovered['original_event_terminal_binding'] == events_binding and recovered['original_actual_process_exit_code'] == 1
                    and recovered['original_unittest_cleanup_completed'], 'independent Machine recovery does not preserve original exit')
            extra_failures.append({'kind': 'late-caller-report-path-serialization-failure', 'bucket': label,
                                   'actual_original_exit': 1, 'recovery_binding': bind(RUN / 'machine-terminal-recovery-0223.json'),
                                   'counts_as_method_failure': False, 'original_log_binding': log_binding})
        pending_starts = [x for x in running if x['declared_method'] not in {y['declared_method'] for y in completed}]
        unittest_summary = 'Ran ' + str(count) + ' tests' in log
        cleanup = {'original_unittest_finished_log_observed': unittest_summary,
                   'original_full_outer_exit_guard_observed': full_exit,
                   'individual_owned_temporary_roots_independently_enumerated': False,
                   'physical_absence_cannot_be_inferred_from_reboot': True,
                   'ceiling': 'Terminal report/log can support completed unittest cleanup hooks with no fixture cleanup error; original individual root paths were not retained. Interrupted outer lifetimes do not establish full cleanup.'}
        ledgers.append({'bucket': label, 'completed_methods': count, 'observed_results': dict(Counter(x['result'] for x in completed)),
                        'original_events_binding': events_binding, 'original_log_binding': log_binding,
                        'original_report_binding': bind(report_path) if report else None, 'original_terminal_event': terminal[-1] if terminal else None,
                        'full_history_entry_guard_observed': True, 'full_history_exit_guard_observed': full_exit,
                        'original_process_exit': process_exit,
                        'process_exit_provenance': ('Independent recovery receipt retains original actual exit; it never replaces that exit.' if label in ('old-worker0', 'Machine14')
                                                    else 'Parent actual tool terminal observation supplied with this bounded verification task; retained original log/report corroborates observed outcome, not a standalone tool-exit attestation.'),
                        'interrupted_outer_lifetime': not full_exit, 'uncompleted_started_cases': pending_starts,
                        'fixture_errors': fixture_errors, 'cleanup': cleanup})
    require(set(methods) == wanted and len(methods) == 345, 'original observation coverage is incomplete')
    failures = []
    for key, row in methods.items():
        if row['original_event']['result'] != 'PASS':
            reason = failure_class(row['original_event'])
            require(reason != 'unclassified-retained-failure-needs-investigation', 'unclassified original failure: ' + key)
            failures.append({'declared_method': key, 'cause_classification': reason, 'original_observation': row,
                             'diagnostic_binding': bind(RUN / 'package-export-diagnostic-0219.json') if reason.startswith('invalid-positive-package') else None,
                             'claim_ceiling': 'Classified retained original failure; no repaired/successor result substitutes for it.'})
    counts = Counter(row['original_event']['result'] for row in methods.values())
    causes = Counter(row['cause_classification'] for row in failures)
    require(counts == {'PASS': 336, 'FAIL': 8, 'ERROR': 1} and len(failures) == 9, 'known original failure accounting differs')
    require(causes == {'stale-literal-supported-operation-count': 2, 'stale-exact-product-revision-selector': 1,
                      'real-outer-request-deadline-missed-before-intended-case-assertion': 2,
                      'invalid-positive-package-export-fixture-native-Work-relation_refs-empty': 4}, 'retained cause accounting differs')
    require(guard.verify(SOURCE) == source, 'full original history exit guard differs')
    for row in list(PINS.values()):
        bind(ROOT / row['path'], row['sha256'])
    report = {'schema_version': 'lab-original-case-observation-ledger/v1-candidate',
              'result': 'OBSERVATIONS_COMPLETE_WITH_FAILURES_AND_INTERRUPTED_QUALIFICATION', 'independent_integrity_verification': 'PASS',
              'started_at': began, 'completed_at': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - started,
              'source_binding': source_binding, 'profile_binding': profile_binding, 'full_history_source_files_freshly_guarded_at_entry_and_exit': 23062,
              'original_plan_binding': bind(RUN / 'final-api-regression-plan-0177.json'), 'verifier_binding': bind(Path(__file__)),
              'original_declared_methods': 323, 'added_original_installation_release_methods': 22, 'observed_unique_completed_methods': 345,
              'observation_counts': dict(counts), 'all_original_method_observations_complete': True, 'all_original_methods_passed': False,
              'method_AST_accounting': {'all_345_equal_frozen_Plan0177_AST': True, 'original_API96_methods': 323,
                                        'API96_AST_unchanged_methods': 321, 'documented_existing_revisions': list(revisions.values()),
                                        'new_IR_methods': 22, 'original_setup_teardown_helper_module_ASTs_equal_frozen_plan': True},
              'buckets': ledgers, 'methods': dict(sorted(methods.items())), 'retained_method_failures': failures,
              'non_method_fixture_or_terminal_failures': extra_failures,
              'partial_outer_guard_completed_observations': sum(x['completed_methods'] for x in ledgers if not x['full_history_exit_guard_observed']),
              'full_outer_guard_completed_observations': sum(x['completed_methods'] for x in ledgers if x['full_history_exit_guard_observed']),
              'all_original_buckets_have_guarded_terminals': False, 'all_original_processes_exited_zero': False,
              'immutable_input_bindings': sorted(PINS.values(), key=lambda x: x['path']), 'domain_cases_reexecuted': 0,
              'original_report_events_logs_or_tests_modified': False, 'Original0190_aggregate_PASS_created': False,
              'conformance345_claimed': False, 'whole_API_qualified': False, 'qualification_transferred_to_API13': False,
              'actual_owner_outcome': None, 'authority_effect': 'none', 'goal_complete': False,
              'claim_ceiling': 'Complete original observations and fresh immutable closure/AST verification, preserving 9 method failures, interrupted outer lifetimes, original 143/1 terminals, zero-method setup error and late serialization failure. No aggregate qualification, final API13 result, owner approval or whole Lab completion.'}
    with out.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'verifier_exit': 0, 'observed_methods': 345, 'counts': dict(counts),
                      'full_outer_guard_observations': report['full_outer_guard_completed_observations'],
                      'partial_outer_guard_observations': report['partial_outer_guard_completed_observations'], 'report_binding': bind(out)}), flush=True)


if __name__ == '__main__':
    main()
