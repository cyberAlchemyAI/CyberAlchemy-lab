"""Process-level inert runner and dispatch refusal regression fixtures.

Fixture endorsements select only owned temporary repositories and public source
anchors. No fixture provider is an enrollment for an actual host or effect.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True  # Keep imported dependencies outside the test write surface.
import tempfile
import time
import unittest
from unittest import mock


def fixture_process(mode, target=None):
    """Closed, inert subprocess behaviors; called before importing the system."""
    result = {'schema_version': 'lab-case-command-result/v1', 'result': 'PASS',
              'checks': 1, 'effect_state': 'owned-inert', 'cleanup': 'clean'}
    if mode in ('sleep', 'closed-pipes-sleep', 'provider-sleep'):
        if target:
            Path(target).write_text(str(os.getpid()))
        if mode == 'closed-pipes-sleep':
            os.close(1)
            os.close(2)
        time.sleep(30)
    elif mode == 'flood':
        os.write(1, b'a' * 400)
        os.write(2, b'b' * 400)
        time.sleep(30)
    elif mode == 'provider-flood':
        sys.stdin.buffer.read()
        os.write(1, b'a' * 400)
        os.write(2, b'b' * 400)
    elif mode == 'provider-echo':
        os.write(1, sys.stdin.buffer.read())
    elif mode == 'provider-nonzero':
        sys.stdin.buffer.read()
        raise SystemExit(7)
    elif mode == 'unknown-pass':
        result['effect_state'] = 'unknown'
    elif mode == 'observed-pass':
        result['effect_state'] = 'observed'
    elif mode == 'retained-cleanup':
        result['cleanup'] = 'retained-owned'
    elif mode == 'unknown-cleanup':
        result['cleanup'] = 'unknown'
    elif mode == 'marker':
        with open(target, 'x') as stream:
            stream.write('an inert command actually ran')
    elif mode == 'drift':
        Path(target).write_bytes(b'changed original fixture selector input')
    elif mode != 'pass':
        raise SystemExit('unknown closed fixture mode')
    if not mode.startswith('provider-'):
        print(json.dumps(result))


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == '--fixture-mode':
    fixture_process(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    raise SystemExit(0)

S = Path(__file__).absolute().parents[2]
REPO = S.parents[3]
E = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02'
sys.path[:0] = [str(S / 'contracts'), str(S / 'selectors'), str(Path(__file__).parent)]
from test_contracts import value
from lab_contracts.codec import Refusal, canonical, sha
from lab_selectors.anchors import identity
from lab_selectors.dispatch import prepare, verify_endorsement
from lab_selectors.runner import run, local_command
from lab_selectors.authority import BoundedProvider, authorized_execute, bounded_transport

TEMP_ROOT = Path(os.environ.get('LAB_UNIT_TEST_TMP_ROOT', str(E)))
OWNED_TEMP_PATHS = []
# The budget includes real Python startup. The earlier 250ms fixture could be
# killed before reaching its sleep, which did not prove the intended boundary.
SLEEP_DEADLINE_MS = 2000
SLEEP_ELAPSED_MIN_SECONDS = 1.9
SLEEP_ELAPSED_MAX_SECONDS = 3.5
BASELINE = REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001/control/baseline.json'
ACCEPTANCE = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-01/coordinator-acceptance-0001.json'
PYTHON = Path(sys.executable).resolve()
SCRIPT = Path(__file__).absolute()


def bind(path, root, root_id='repository'):
    raw = path.read_bytes()
    return {'kind': 'execution', 'root_id': root_id, 'relative_path': str(path.relative_to(root)),
            'sha256': sha(raw), 'size_bytes': len(raw)}


def root_record(root, root_id):
    return {'root_id': root_id, 'path': str(root), 'identity': identity(os.stat(root))}


def gate_check(gate):
    return {'gate': gate, 'start_inputs': [], 'before_effect': [],
            'terminal_outputs': [], 'consumed_outputs': []}


def evidence_contract():
    # Declaration only: no fabricated receipt bytes or actual execution.
    roles = ('gate-verification', 'currentness', 'effect', 'prestate', 'poststate', 'cleanup')
    return {'schema_version': 'lab-completion-effect-evidence-contract/v1',
            'slots': [{'id': role, 'role': role, 'locator': {'kind': 'evidence',
                       'root_id': 'repository', 'relative_path': 'evidence/' + role + '.json',
                       'max_bytes': 4096}, 'subject_locators': []} for role in roles],
            'max_total_bytes': 24576, 'disclosure': 'reviewed-public-metadata-only',
            'retention': 'exact-original-bytes-in-owned-attempt'}


class Fixture:
    def __init__(self, root, modes=('pass',)):
        self.root = root
        (root / 'work').mkdir()
        (root / 'evidence').mkdir()
        self.marker = root / 'work' / 'later-marker'
        self.drift = root / 'work' / 'selected-input'
        self.drift.write_bytes(b'original fixture input')
        self.script_binding = bind(SCRIPT, REPO, 'original')
        self.python_binding = bind(PYTHON, PYTHON.parent, 'python')
        self.commands = [self.command('cleanup', 'pass')]
        cases = []
        for number, mode in enumerate(modes):
            name = f'case-{number}'
            target = self.marker if mode == 'marker' else self.drift if mode == 'drift' else None
            self.commands.append(self.command(name, mode, target))
            cases.append({'id': name, 'declared_gates': [], 'declared_effects': [], 'setup': [],
                          'commands': [self.step(name)], 'cleanup': [self.step('cleanup')]})
        self.manifest = {'schema_version': 'lab-completion-case-manifest/v1',
            'unit': 'LC-U01-02-fixture', 'selection_kind': 'code', 'stage': 'fixture', 'cases': cases}
        self.plan = {'units': [{'id': 'LC-U01-02-fixture', 'selection_kind': 'code',
                               'external_gates': [], 'evidence_root': 'evidence', 'gate_checks': [],
                               'verification_kind': 'inert-contract', 'write_scope': ['work/']}]}
        self.write_json('cases.json', self.manifest)
        self.write_json('plan.json', self.plan)
        self.endorsement = {'schema_version': 'lab-completion-dispatch-endorsement/v1',
            'unit': 'LC-U01-02-fixture', 'repository': str(root),
            'roots': [root_record(root, 'repository'), root_record(REPO, 'original'),
                      root_record(PYTHON.parent, 'python')],
            'baseline_binding': bind(BASELINE, REPO, 'original'),
            'predecessor_acceptance_binding': bind(ACCEPTANCE, REPO, 'original'),
            'selection_binding': bind(BASELINE, REPO, 'original'),
            'case_manifest_binding': bind(root / 'cases.json', root),
            'plan_manifest_binding': bind(root / 'plan.json', root),
            'source_bindings': [self.script_binding, self.python_binding, bind(self.drift, root)],
            'commands': self.commands, 'run_root': 'evidence/attempt', 'selection_kind': 'code',
            'stage': 'fixture', 'freeze_binding': None, 'expected_execution_binding': None,
            'provider_binding': None, 'provider_command_id': None, 'provider_kind': 'fixture',
            'issuer_enrollment_binding': None, 'gate_input_bindings': [],
            'external_write_envelope': [], 'authority_effect': 'none'}

    def write_json(self, name, val):
        (self.root / name).write_bytes(canonical(val))

    @staticmethod
    def step(name):
        return {'command_id': name, 'declared_gates': [], 'declared_effects': []}

    def command(self, name, mode, target=None):
        argv = [str(PYTHON), '-B', str(SCRIPT), '--fixture-mode', mode]
        if target is not None:
            argv.append(str(target))
        return {'id': name, 'argv': argv, 'environment': [], 'cwd': 'work',
            'program_bindings': [self.script_binding, self.python_binding], 'required_gates': [],
            'effects': [], 'timeout_ms': 3000, 'max_output_bytes': 4096,
            'terminal_protocol': 'lab-case-command-result/v1', 'effect_evidence_contract': None,
            'gate_checks': [], 'produced_terminal_checks': []}

    def refresh(self):
        self.write_json('cases.json', self.manifest)
        self.write_json('plan.json', self.plan)
        self.endorsement['case_manifest_binding'] = bind(self.root / 'cases.json', self.root)
        self.endorsement['plan_manifest_binding'] = bind(self.root / 'plan.json', self.root)

    def verify(self):
        raw = canonical(self.endorsement)
        return verify_endorsement(raw, sha(raw))

    def prepared(self):
        e, reader = self.verify()
        return prepare(e, reader)

    def run(self, **changes):
        raw = canonical(self.endorsement)
        args = {'requested_unit': self.endorsement['unit'],
                'requested_kind': self.endorsement['selection_kind'], 'selection_path': BASELINE,
                'case_path': self.root / 'cases.json', 'run_path': self.root / 'evidence/attempt'}
        args.update(changes)
        return run(raw, sha(raw), **args)

    def actual_selection_fixture(self):
        # Deliberately incomplete actual-stage input; cannot activate anything.
        self.manifest.update(stage='actual', selection_kind='diagnostic')
        self.plan['units'][0]['selection_kind'] = 'diagnostic'
        self.endorsement.update(stage='actual', selection_kind='diagnostic')
        self.write_json('execution.json', value('ExecutionSelection'))
        self.endorsement['selection_binding'] = bind(self.root / 'execution.json', self.root)
        self.refresh()


class OwnedTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TEMP_ROOT.is_dir(), 'existing owned temp root required')
        self.temp = tempfile.TemporaryDirectory(prefix='owned-test-runner-', dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        OWNED_TEMP_PATHS.append(self.root)

    def fixture(self, *modes):
        return Fixture(self.root, modes or ('pass',))

    def capture_real_children(self, children):
        import subprocess
        original = subprocess.Popen

        def launch(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child

        # Observe actual kernel processes; do not replace child behavior or
        # change the runner's selected deadline/transport implementation.
        return mock.patch('subprocess.Popen', side_effect=launch)

    def assert_sleep_deadline_and_reap(self, started, pidfile, children):
        import signal
        elapsed = time.monotonic() - started
        self.assertGreaterEqual(elapsed, SLEEP_ELAPSED_MIN_SECONDS)
        self.assertLess(elapsed, SLEEP_ELAPSED_MAX_SECONDS)
        self.assertEqual(len(children), 1)
        child = children[0]
        self.assertEqual(child.returncode, -signal.SIGKILL)
        with self.assertRaises(ProcessLookupError):
            os.kill(child.pid, 0)
        self.assertTrue(pidfile.is_file(), 'child must reach its sleep within the bounded startup allowance')
        self.assertEqual(int(pidfile.read_text()), child.pid)


class RunnerTests(OwnedTests):
    def test_positive_uses_real_selected_child_and_exclusive_evidence(self):
        f = self.fixture('marker')
        result = f.run()
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(result['actual_dispatch_count'], 0)
        self.assertEqual(result['actual_effect_state'], 'none')
        self.assertTrue(f.marker.is_file())
        terminal = self.root / 'evidence/attempt/terminal.json'
        before = terminal.read_bytes()
        with self.assertRaisesRegex(Refusal, 'RUN_ROOT_NOT_EXCLUSIVE'):
            f.run()
        self.assertEqual(terminal.read_bytes(), before)

    def test_unknown_effect_cannot_pass_or_dispatch_later_case(self):
        f = self.fixture('unknown-pass', 'marker')
        result = f.run()
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertFalse(f.marker.exists())
        rows = [json.loads(p.read_bytes()) for p in sorted((self.root / 'evidence/attempt').glob('command-*.json'))]
        self.assertEqual(rows[0]['detail']['reason'], 'UNKNOWN_EFFECT_OR_CLEANUP_PASS')
        self.assertEqual(rows[2]['result']['result'], 'NOT_RUN')
        self.assertEqual(result['actual_dispatch_count'], 0)

    def test_first_child_failure_retains_exact_record_and_reason(self):
        f = self.fixture('unknown-pass', 'marker')
        result = f.run()
        self.assertEqual(result['primary_failure'], {
            'command_record': 'command-0001.json', 'case_id': 'case-0', 'phase': 'commands',
            'command_id': 'case-0', 'result': 'UNKNOWN', 'reason': 'UNKNOWN_EFFECT_OR_CLEANUP_PASS'})
        child = json.loads((self.root / 'evidence/attempt/command-0001.json').read_bytes())
        self.assertEqual(child['detail']['reason'], result['primary_failure']['reason'])
        self.assertFalse(f.marker.exists())

    def test_retained_owned_cleanup_is_preserved_at_attempt_terminal(self):
        f = self.fixture('pass')
        f.commands[0]['argv'][-1] = 'retained-cleanup'
        result = f.run()
        self.assertEqual((result['result'], result['cleanup']), ('PASS', 'retained-owned'))
        cleanup = json.loads((self.root / 'evidence/attempt/cleanup.json').read_bytes())
        self.assertEqual(cleanup['state'], 'retained-owned')

    def test_observed_effect_is_not_an_inert_pass(self):
        f = self.fixture('observed-pass')
        self.assertEqual(f.run()['result'], 'UNKNOWN')

    def test_unknown_cleanup_fences_later_case(self):
        f = self.fixture('unknown-cleanup', 'marker')
        self.assertEqual(f.run()['result'], 'UNKNOWN')
        self.assertFalse(f.marker.exists())

    def test_selected_source_drift_fences_later_case_and_preserves_cause(self):
        f = self.fixture('drift', 'marker')
        result = f.run()
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertIn(result['primary_failure']['reason'], ('FILE_TYPE_SIZE', 'CONTENT_DIGEST'))
        self.assertFalse(f.marker.exists())
        self.assertEqual(f.drift.read_bytes(), b'changed original fixture selector input')

    def test_no_actual_dispatch_when_actual_provider_missing(self):
        f = self.fixture('marker')
        f.actual_selection_fixture()
        result = f.run(selection_path=self.root / 'execution.json')
        self.assertEqual(result['result'], 'ERROR')
        self.assertEqual(result['primary_failure']['reason'], 'ACTUAL_PROVIDER_REQUIRED')
        self.assertEqual(result['actual_dispatch_count'], 0)
        self.assertEqual(result['actual_effect_state'], 'none')
        self.assertFalse(f.marker.exists())

    def local(self, mode, *, timeout=3000, output_cap=4096, target=None):
        f = self.fixture()
        command = f.command('local', mode, target)
        command.update(timeout_ms=timeout, max_output_bytes=output_cap)
        output = self.root / 'capture'; output.mkdir()
        fd = os.open(output, os.O_RDONLY | os.O_DIRECTORY)
        try:
            return local_command(command, f.endorsement, fd, 1), output
        finally:
            os.close(fd)

    def test_aggregate_pipe_output_is_hard_capped_and_retains_truncation(self):
        (result, detail), output = self.local('flood', output_cap=600)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(detail['reason'], 'OUTPUT_LIMIT')
        self.assertTrue(detail['output_truncated'])
        self.assertEqual(detail['retained_output_bytes'], 600)
        self.assertEqual(sum(p.stat().st_size for p in output.iterdir()), 600)

    def test_timeout_kills_and_reaps_actual_child(self):
        pidfile = self.root / 'child-pid'
        children = []
        start = time.monotonic()
        with self.capture_real_children(children):
            (result, detail), _ = self.local('sleep', timeout=SLEEP_DEADLINE_MS, target=pidfile)
        self.assertEqual((result['result'], detail['reason']), ('UNKNOWN', 'TIMEOUT'))
        self.assert_sleep_deadline_and_reap(start, pidfile, children)

    def test_closed_pipes_do_not_extend_child_deadline(self):
        pidfile = self.root / 'closed-pipes-pid'
        children = []
        start = time.monotonic()
        with self.capture_real_children(children):
            (result, detail), _ = self.local('closed-pipes-sleep', timeout=SLEEP_DEADLINE_MS, target=pidfile)
        self.assertEqual((result['result'], detail['reason']), ('UNKNOWN', 'TIMEOUT'))
        self.assert_sleep_deadline_and_reap(start, pidfile, children)


class DispatchTests(OwnedTests):
    def test_external_anchor_repin_and_cli_scope_refuse_before_reservation(self):
        f = self.fixture('marker')
        raw = canonical(f.endorsement)
        changed = copy.deepcopy(f.endorsement); changed['run_root'] = 'evidence/coherent-repin'
        with self.assertRaisesRegex(Refusal, 'DISPATCH_ANCHOR_MISMATCH'):
            verify_endorsement(canonical(changed), sha(raw))
        for args, code in [({'requested_unit': 'other'}, 'DISPATCH_REQUEST'),
                           ({'requested_kind': 'final'}, 'DISPATCH_REQUEST'),
                           ({'selection_path': self.root / 'different'}, 'CLI_SELECTION_DRIFT'),
                           ({'case_path': self.root / 'different'}, 'CLI_SELECTION_DRIFT'),
                           ({'run_path': self.root / 'other'}, 'CLI_RUN_ROOT_DRIFT')]:
            with self.subTest(args=list(args)), self.assertRaisesRegex(Refusal, code):
                f.run(**args)
        self.assertFalse((self.root / 'evidence/attempt').exists())
        self.assertFalse(f.marker.exists())

    def test_nested_gate_understatement_refuses(self):
        f = self.fixture()
        for phase in ('setup', 'commands', 'cleanup'):
            f.commands[0]['required_gates'] = []
            f.commands[1]['required_gates'] = []
            f.manifest['cases'][0]['setup'] = []
            if phase == 'cleanup':
                f.commands[0]['required_gates'] = ['G02']
            else:
                f.commands[1]['required_gates'] = ['G02']
                if phase == 'setup':
                    f.manifest['cases'][0]['setup'] = [f.step('case-0')]
            for command in f.commands:
                command['gate_checks'] = [gate_check(g) for g in command['required_gates']]
            f.refresh()
            with self.subTest(phase=phase), self.assertRaisesRegex(Refusal, 'NESTED_GATE_OR_EFFECT_UNDERSTATEMENT'):
                f.prepared()

    def test_original_unit_gate_cannot_be_omitted_by_case(self):
        f = self.fixture()
        f.plan['units'][0]['external_gates'] = ['G03']
        f.plan['units'][0]['gate_checks'] = [gate_check('G03')]; f.refresh()
        with self.assertRaisesRegex(Refusal, 'CASE_GATE_OR_EFFECT_UNDERSTATEMENT'):
            f.prepared()

    def test_nested_effect_envelope_cannot_be_omitted(self):
        f = self.fixture()
        effect = {'root_id': 'repository', 'relative_path': 'work/member', 'kind': 'inert-authoring',
                  'preimage_binding': None, 'expected_absent': True, 'owner_uid': os.getuid(),
                  'mode': 384, 'authority_binding': None}
        f.commands[1]['effects'] = [effect]
        with self.assertRaisesRegex(Refusal, 'NESTED_GATE_OR_EFFECT_UNDERSTATEMENT'):
            f.prepared()
        f.manifest['cases'][0]['commands'][0]['declared_effects'] = [effect]
        f.manifest['cases'][0]['declared_effects'] = [effect]; f.refresh()
        with self.assertRaisesRegex(Refusal, 'UNENDORSED_EFFECT'):
            f.prepared()

    def test_program_outside_independently_selected_source_closure_refuses(self):
        f = self.fixture()
        f.endorsement['source_bindings'].remove(f.script_binding)
        with self.assertRaisesRegex(Refusal, 'PROGRAM_OUTSIDE_REVIEWED_CLOSURE'):
            f.prepared()

    def test_executable_must_be_a_selected_program_not_an_unrelated_binding(self):
        f = self.fixture()
        f.commands[1]['program_bindings'] = [f.script_binding]
        with self.assertRaisesRegex(Refusal, 'EXECUTABLE_OUTSIDE_REVIEWED_CLOSURE'):
            f.prepared()

    def test_script_entrypoint_requires_its_exact_selected_binding(self):
        f = self.fixture()
        f.commands[1]['program_bindings'] = [f.python_binding]
        with self.assertRaisesRegex(Refusal, 'ENTRYPOINT_OUTSIDE_REVIEWED_CLOSURE'):
            f.prepared()
        f.commands[1]['program_bindings'] = [f.python_binding, f.script_binding]
        f.commands[1]['argv'][2] = 'unselected-script.py'
        with self.assertRaisesRegex(Refusal, 'ENTRYPOINT_OUTSIDE_REVIEWED_CLOSURE'):
            f.prepared()

    def test_final_selector_requires_exact_execution_and_freeze(self):
        f = self.fixture()
        f.manifest['selection_kind'] = f.plan['units'][0]['selection_kind'] = 'final'
        f.endorsement['selection_kind'] = 'final'
        f.write_json('execution.json', value('ExecutionSelection'))
        execution = bind(self.root / 'execution.json', self.root)
        f.endorsement['selection_binding'] = execution; f.refresh()
        with self.assertRaisesRegex(Refusal, 'FINAL_SELECTOR'):
            f.prepared()
        freeze = value('Freeze')
        freeze['execution_selection_binding'] = {**execution, 'sha256': '0' * 64}
        f.write_json('freeze.json', freeze)
        f.endorsement.update(freeze_binding=bind(self.root / 'freeze.json', self.root),
                             expected_execution_binding=execution)
        with self.assertRaisesRegex(Refusal, 'FINAL_FREEZE_MISMATCH'):
            f.prepared()

    def test_baseline_cannot_activate_actual_stage(self):
        f = self.fixture(); f.manifest['stage'] = f.endorsement['stage'] = 'actual'; f.refresh()
        with self.assertRaisesRegex(Refusal, 'CODE_ACTUAL_REFUSED'):
            f.prepared()

    def actual_code_review_fixture(self):
        f = self.fixture()
        f.manifest['stage'] = f.endorsement['stage'] = 'actual'
        f.plan['units'][0]['verification_kind'] = 'semantic-review'
        # Structural fixture only; selected public bytes are not authentic
        # provider enrollment. This helper is never passed to run().
        f.endorsement.update(provider_kind='actual', provider_binding=f.script_binding,
                             provider_command_id='case-0', issuer_enrollment_binding=f.script_binding)
        for command in f.commands:
            command['effect_evidence_contract'] = evidence_contract()
        f.refresh()
        return f

    def test_code_actual_review_admission_is_pinned_to_original_unit_kind(self):
        f = self.actual_code_review_fixture()
        manifest, _, _ = f.prepared()
        self.assertEqual((manifest['selection_kind'], manifest['stage']), ('code', 'actual'))
        f.plan['units'][0]['verification_kind'] = 'authority-review'; f.refresh()
        f.prepared()
        f.plan['units'][0]['verification_kind'] = 'runtime-test'; f.refresh()
        with self.assertRaisesRegex(Refusal, 'CODE_ACTUAL_REFUSED'):
            f.prepared()
        self.assertFalse((self.root / 'evidence/attempt').exists())

    def test_code_actual_review_still_requires_provider_and_receipt_contract(self):
        f = self.actual_code_review_fixture()
        f.endorsement['provider_binding'] = None
        with self.assertRaisesRegex(Refusal, 'ACTUAL_PROVIDER_REQUIRED'):
            f.prepared()
        f.endorsement['provider_binding'] = f.script_binding
        f.commands[1]['effect_evidence_contract'] = None
        with self.assertRaisesRegex(Refusal, 'ACTUAL_EVIDENCE_CONTRACT_REQUIRED'):
            f.prepared()

    def test_code_actual_review_refuses_runtime_effect(self):
        f = self.actual_code_review_fixture()
        effect = {'root_id': 'repository', 'relative_path': 'work/member', 'kind': 'candidate-effect',
                  'preimage_binding': None, 'expected_absent': True, 'owner_uid': os.getuid(),
                  'mode': 384, 'authority_binding': f.script_binding}
        f.endorsement['external_write_envelope'] = [effect]
        with self.assertRaisesRegex(Refusal, 'CODE_REVIEW_RUNTIME_EFFECT'):
            f.prepared()
        self.assertFalse((self.root / 'evidence/attempt').exists())


class ProviderTransportTests(OwnedTests):
    def transport(self, mode, data=b'fixture-input', timeout=1000, cap=1024, target=None):
        argv = [str(PYTHON), '-B', str(SCRIPT), '--fixture-mode', mode]
        if target:
            argv.append(str(target))
        return bounded_transport(argv, {}, str(self.root), data, timeout, cap)

    def test_real_child_echo_preserves_exact_input(self):
        self.assertEqual(self.transport('provider-echo', b'bounded\x00fixture'), b'bounded\x00fixture')

    def test_dispatch_counter_changes_only_after_real_transport_launch(self):
        dispatched = []
        args = [str(PYTHON), '-B', str(SCRIPT), '--fixture-mode', 'provider-echo']
        self.assertEqual(bounded_transport(args, {}, str(self.root), b'fixture', 1000, 1024,
                                          on_dispatch=lambda: dispatched.append(True)), b'fixture')
        self.assertEqual(dispatched, [True])
        missing = [str(self.root / 'no-executable')]
        with self.assertRaises(FileNotFoundError):
            bounded_transport(missing, {}, str(self.root), b'fixture', 1000, 1024,
                              on_dispatch=lambda: dispatched.append(True))
        self.assertEqual(dispatched, [True])

    def test_provider_output_aggregate_cap_and_nonzero_are_refusals(self):
        with self.assertRaisesRegex(Refusal, 'PROVIDER_OUTPUT_LIMIT_UNKNOWN'):
            self.transport('provider-flood', cap=600)
        with self.assertRaisesRegex(Refusal, 'PROVIDER_NONZERO_UNKNOWN'):
            self.transport('provider-nonzero')

    def test_provider_deadline_kills_and_reaps_hung_child(self):
        pidfile = self.root / 'provider-pid'
        children = []
        start = time.monotonic()
        with self.capture_real_children(children), self.assertRaisesRegex(Refusal, 'PROVIDER_TIMEOUT_UNKNOWN'):
            self.transport('provider-sleep', timeout=SLEEP_DEADLINE_MS, target=pidfile)
        self.assert_sleep_deadline_and_reap(start, pidfile, children)

    def test_provider_request_bounds_refuse_before_launch(self):
        pidfile = self.root / 'must-not-launch'
        with self.assertRaisesRegex(Refusal, 'PROVIDER_REQUEST_LIMIT'):
            self.transport('provider-sleep', b'x' * 65537, target=pidfile)
        self.assertFalse(pidfile.exists())

    def test_source_refusal_before_provider_launch_does_not_count_dispatch(self):
        class RefusingReader:
            def read(self, binding):
                raise Refusal('FIXTURE_SOURCE_DRIFT_BEFORE_LAUNCH')
        provider = BoundedProvider({'source_bindings': [{'fixture': 'unreadable'}]}, RefusingReader(), {})
        dispatched = []
        with self.assertRaisesRegex(Refusal, 'FIXTURE_SOURCE_DRIFT_BEFORE_LAUNCH'):
            authorized_execute(provider, {}, {}, {}, lambda: dispatched.append(True))
        self.assertEqual(dispatched, [])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp-root', type=Path, default=TEMP_ROOT)
    args = parser.parse_args()
    TEMP_ROOT = args.temp_root.absolute()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    clean = not any(p.exists() or p.is_symlink() for p in OWNED_TEMP_PATHS)
    passed = result.wasSuccessful() and clean
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS' if passed else 'FAIL',
                      'checks': result.testsRun, 'effect_state': 'owned-inert',
                      'cleanup': 'clean' if clean else 'owned-residue'}))
    raise SystemExit(0 if passed else 1)
