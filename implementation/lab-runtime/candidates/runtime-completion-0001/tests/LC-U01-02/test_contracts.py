"""Behavioral contract negatives and cross-language golden vectors."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest

S = Path(__file__).absolute().parents[2]
DEPS = Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps')
sys.path[:0] = [str(S / 'contracts'), str(S / 'selectors'), str(DEPS)]
from lab_contracts.codec import Refusal, canonical, parse, signing_bytes, MIN_INTEGER, MAX_INTEGER
from lab_contracts.validation import validate
from lab_contracts.schema_catalog import DEFS
from lab_contracts import dispatch_schema
from lab_selectors.chains import phase_remaining, late_lesson, code_family_execution, namespace_chain
from lab_selectors.anchors import RootAnchor, AnchoredReader, identity
from lab_contracts.codec import sha


def sample(spec):
    if '$ref' in spec:
        return sample(DEFS[spec['$ref'].split('/')[-1]])
    if 'const' in spec:
        return spec['const']
    if 'enum' in spec:
        return spec['enum'][0]
    if 'oneOf' in spec:
        return sample(spec['oneOf'][-1])
    kind = spec['type']
    if kind == 'object':
        return {k: sample(v) for k, v in spec['properties'].items()}
    if kind == 'array':
        return [sample(spec['items']) for _ in range(spec['minItems'])]
    if kind == 'integer':
        return spec.get('minimum', 0)
    if kind == 'boolean':
        return False
    if kind == 'null':
        return None
    if spec.get('format') == 'date-time':
        return '2026-10-18T00:00:00Z'
    if spec.get('pattern') == '^[0-9a-f]{64}$':
        return 'a' * 64
    return 'x'


def binding():
    return sample(DEFS['ByteBinding'])


def value(name):
    if name in ('EffectEvidenceContract', 'EffectEvidence'):
        from test_effect_evidence import Fixture
        fixture = Fixture()
        return fixture.command['effect_evidence_contract'] if name == 'EffectEvidenceContract' else fixture.evidence
    v = sample(DEFS[name])
    if 'expires_at' in v:
        v['expires_at'] = '2026-10-19T00:00:00Z'
    if name == 'CommandResult':
        v['checks'] = 1
    if name == 'NamespaceCore':
        v['broker_uid'], v['workload_uid'] = 1001, 1002
    if name == 'PhasePermit':
        v['diagnostic_bounds_binding'] = binding()
    if name in ('DiagnosticBounds', 'MeasuredBudget'):
        v['total_cap_ms'], v['cleanup_reserve_ms'] = 10000, 1000
        v['phase_caps'][0]['hard_cap_ms'] = 1000
    return v


class CodecTests(unittest.TestCase):
    def test_exact_unicode_and_controls(self):
        v = {'schema_version': 'golden/v1', 'é': '\b\f\n\r\t\x00\x1f/\\"', 'a': '😀\u2028e\u0301'}
        self.assertEqual(parse(canonical(v)), v)
        self.assertIn('é'.encode(), canonical(v))
        self.assertNotEqual(canonical({'x': 'é'}), canonical({'x': 'e\u0301'}))

    def test_duplicate_unknown_floats_nonfinite(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":9223372036854775808}', b'{"x":-9223372036854775809}',
                    b'{"x":"\\ud800"}', b'{"x":"\\udfff"}', b'{"x":-0}', b'\xff']:
            with self.subTest(raw=raw), self.assertRaises(Refusal):
                parse(raw)

    def test_integer_boundaries_bool_and_key_order(self):
        a = {'z': MIN_INTEGER, 'a': [True, False, MAX_INTEGER]}
        self.assertEqual(canonical(a), canonical(dict(reversed(list(a.items())))))
        self.assertEqual(parse(canonical(a)), a)
        for v in [1.0, {1: 'x'}, '\ud800', MAX_INTEGER + 1]:
            with self.assertRaises(Refusal):
                canonical(v)
        with self.assertRaises(Refusal):
            signing_bytes({'payload': 'no domain'})

    def test_depth_and_size(self):
        with self.assertRaises(Refusal):
            parse(b'[]', max_bytes=1)
        with self.assertRaises(Refusal):
            parse(b'[' * 66 + b'0' + b']' * 66)


class SchemaTests(unittest.TestCase):
    def test_code_family_execution_exact_join(self):
        with tempfile.TemporaryDirectory(prefix='owned-test-chain-', dir=Path(__file__).parent) as temp:
            root=Path(temp); bindings=[]
            def put(name,obj):
                raw=canonical(obj); (root/name).write_bytes(raw)
                b={'kind':'execution','root_id':'fixture','relative_path':name,'sha256':sha(raw),'size_bytes':len(raw)}
                bindings.append(b); return b
            code=value('CodeSelection'); cb=put('code.json',code)
            family=value('FamilySelection');family['code_selection_binding']=cb;fb=put('family.json',family)
            execution=value('ExecutionSelection');execution.update(code_selection_binding=cb,family_selection_binding=fb)
            eb=put('execution.json',execution)
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            self.assertEqual(code_family_execution(reader,{'code':cb,'family':fb,'execution':eb})[1],family)
            execution['family_selection_binding']=cb
            wrong=put('wrong.json',execution)
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            with self.assertRaisesRegex(Refusal,'FAMILY_CHAIN'):
                code_family_execution(reader,{'code':cb,'family':fb,'execution':wrong})

    def test_namespace_core_review_activation_exact_join(self):
        with tempfile.TemporaryDirectory(prefix='owned-test-namespace-', dir=Path(__file__).parent) as temp:
            root=Path(temp); bindings=[]
            def put(name,obj):
                raw=canonical(obj); (root/name).write_bytes(raw)
                b={'kind':'execution','root_id':'fixture','relative_path':name,'sha256':sha(raw),'size_bytes':len(raw)}
                bindings.append(b);return b
            core=value('NamespaceCore'); cb=put('core.json',core)
            review=value('NamespaceReview');review['core_binding']=cb;rb=put('review.json',review)
            activation=value('NamespaceActivation');activation.update(core_binding=cb,review_binding=rb)
            ab=put('activation.json',activation)
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            self.assertEqual(namespace_chain(reader,{'core':cb,'review':rb,'activation':ab})[0],core)
            review['outcome']='UNKNOWN';badreview=put('badreview.json',review)
            activation['review_binding']=badreview;badactivation=put('badactivation.json',activation)
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            with self.assertRaisesRegex(Refusal,'NAMESPACE_REVIEW_REFUSED'):
                namespace_chain(reader,{'core':cb,'review':badreview,'activation':badactivation})

    def test_every_schema_is_closed_and_valid(self):
        from jsonschema import Draft202012Validator
        from lab_contracts.schema_catalog import schema
        for name, spec in DEFS.items():
            Draft202012Validator.check_schema(schema(name))
            v = value(name)
            validate(name, v)
            with self.subTest(name=name), self.assertRaises(Refusal):
                validate(name, {**v, 'unrecognized': True})

    def test_no_missing_implicit_fields(self):
        for name in ('CodeSelection', 'FamilySelection', 'ExecutionSelection', 'NamespaceCore',
                     'NamespaceReview', 'NamespaceActivation', 'LessonInput', 'PhasePermit'):
            v = value(name)
            for key in list(v):
                bad = copy.deepcopy(v)
                del bad[key]
                with self.subTest(name=name, key=key), self.assertRaises(Refusal):
                    validate(name, bad)

    def test_budget_modes_total_cap_and_censor_separation(self):
        permit = value('PhasePermit')
        cap = value('DiagnosticBounds')
        raw = canonical(cap)
        with tempfile.TemporaryDirectory(prefix='owned-test-budget-', dir=Path(__file__).parent) as temp:
            path = Path(temp); (path/'budget.json').write_bytes(raw)
            selected_budget = {'kind':'evidence','root_id':'fixture','relative_path':'budget.json',
                               'sha256':sha(raw),'size_bytes':len(raw)}
            reader = AnchoredReader([RootAnchor('fixture',str(path),identity(path.stat()))],[selected_budget])
            permit['diagnostic_bounds_binding'] = selected_budget
            self.assertEqual(phase_remaining(permit, reader, selected_budget, 0, 'x', 5000), 1000)
            for elapsed, remaining in [(8000, 5000), (0, 2000)]:
                with self.assertRaises(Refusal):
                    phase_remaining(permit, reader, selected_budget, elapsed, 'x', remaining)
            changed = copy.deepcopy(cap); changed['phase_caps'][0]['hard_cap_ms'] = 1
            (path/'budget.json').write_bytes(canonical(changed))
            with self.assertRaises(Refusal):
                phase_remaining(permit, reader, selected_budget, 0, 'x', 5000)
        bad = copy.deepcopy(permit)
        bad['measured_budget_binding'] = binding()
        with self.assertRaises(Refusal):
            validate('PhasePermit', bad)
        bad['diagnostic_bounds_binding'] = None
        with self.assertRaises(Refusal):
            validate('PhasePermit', bad)
        bad['mode'] = 'qualification'
        validate('PhasePermit', bad)
        with self.assertRaises(Refusal):
            phase_remaining(bad, None, selected_budget, 0, 'x', 5000)

    def test_protected_limit_refuses_before_provider_read(self):
        class Spy:
            calls = 0
            def read(self, binding, *, max_bytes):
                self.calls += 1
                return b'fixture'
        b = {'kind':'protected-input','root_id':'fixture','relative_path':'opaque',
             'sha256':sha(b'fixture'),'size_bytes':7}
        spy = Spy()
        root = Path(__file__).parent
        reader = AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))], [b], protected_provider=spy)
        for limit in [False,0,-1,1,64*1024*1024+1]:
            with self.assertRaises(Refusal):
                reader.read(b,max_bytes=limit)
        self.assertEqual(spy.calls,0)
        self.assertEqual(reader.read(b,max_bytes=7),b'fixture')

    def test_bool_is_not_integer_path_root_and_terminal(self):
        b = binding()
        b['size_bytes'] = True
        with self.assertRaises(Refusal):
            validate('ByteBinding', b)
        b = binding(); b['sha256'] += '\n'
        with self.assertRaises(Refusal):
            validate('ByteBinding', b)
        for path in ['', '/', 'a/../b', './a', 'a//b', 'a/', 'a\\b', 'a\x00b']:
            b = binding(); b['relative_path'] = path
            with self.subTest(path=path), self.assertRaises(Refusal):
                validate('ByteBinding', b)
        slot = value('SlotReceipt'); slot['state'] = 'closed'
        with self.assertRaises(Refusal):
            validate('SlotReceipt', slot)
        slot['terminal_binding'] = binding()
        validate('SlotReceipt', slot)

    def test_linux_uid_gid_representability_and_sentinel(self):
        for name, fields in [('NamespaceCore',['broker_uid','broker_gid','workload_uid','workload_gid']),
                             ('RootIdentity',['owner_uid','owner_gid']),('EffectEnvelope',['owner_uid'])]:
            for field in fields:
                for invalid in [-1,2**32-1,2**32,2**63-1,True]:
                    obj=value(name); obj[field]=invalid
                    with self.subTest(schema=name,field=field,invalid=invalid),self.assertRaises(Refusal):
                        validate(name,obj)

    def test_late_lesson_cannot_replace_family(self):
        execution, family = value('ExecutionSelection'), value('FamilySelection')
        policy, lesson = value('LessonConsumerPolicy'), value('LessonInput')
        execution['allowed_attempt_variations']['lesson_input_contract_binding'] = binding()
        with tempfile.TemporaryDirectory(prefix='owned-test-lesson-', dir=Path(__file__).parent) as temp:
            root = Path(temp)
            bindings = []
            def put(name, obj):
                raw = canonical(obj); (root/name).write_bytes(raw)
                b = {'kind':'execution','root_id':'fixture','relative_path':name,'sha256':sha(raw),'size_bytes':len(raw)}
                bindings.append(b); return b
            shape = {'properties':{'task_lesson':{'type':'object','additionalProperties':False,
                'required':['observations'],'properties':{'observations':{'type':'array','items':{'type':'string'},'maxItems':3}}}}}
            sb = put('source.json',shape); pb = put('profile.json',shape)
            contract = value('LateInputContract')
            contract.update(source_schema_binding=sb,profile_schema_binding=pb,
                source_instance_selector='#/properties/task_lesson',profile_instance_selector='#/properties/task_lesson')
            cb = put('late-contract.json',contract)
            lesson['typed_data_binding'] = put('data.json',{'observations':['temperature']})
            policy.update(late_input_schema_binding=cb,source_constraint_binding=sb,
                          profile_constraint_binding=pb,max_payload_bytes=1024)
            policy_binding = put('policy.json', policy)
            execution['allowed_attempt_variations']['lesson_input_contract_binding'] = policy_binding
            lesson['policy_binding'] = policy_binding
            reader = AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            late_lesson(execution, family, policy, lesson, expected_policy_binding=policy_binding,
                        reader=reader, expected_late_input_binding=cb, expected_family_lesson_binding=binding())
            wrong = binding(); wrong['sha256'] = 'b' * 64
            with self.assertRaises(Refusal):
                late_lesson(execution, family, policy, lesson, expected_policy_binding=policy_binding,
                    reader=reader,expected_late_input_binding=cb,expected_family_lesson_binding=wrong)
            modified = dict(policy, max_payload_bytes=2048)
            with self.assertRaisesRegex(Refusal, 'LESSON_POLICY_BYTES'):
                late_lesson(execution, family, modified, lesson, expected_policy_binding=policy_binding,
                    reader=reader,expected_late_input_binding=cb,expected_family_lesson_binding=binding())
            policy['late_input_schema_binding'] = None
            with self.assertRaises(Refusal):
                late_lesson(execution, family, policy, lesson, expected_policy_binding=policy_binding,
                    reader=reader,expected_late_input_binding=cb,expected_family_lesson_binding=binding())


class RustGoldenTests(unittest.TestCase):
    def test_actual_rust_encoding_and_signature_bytes(self):
        binary = os.environ.get('LAB_CODEC_RUST_BINARY')
        self.assertTrue(binary and Path(binary).is_file(), 'Rust executable required; cannot skip')
        good = [b'{"schema_version":"vector/v1","z":0,"a":true}',
            '{"schema_version":"vector/v1","é":"😀é","c":"\\b\\f\\n\\r\\t\\u0000\\u001f/\\\\\\\""}'.encode(),
            b'{"schema_version":"vector/v1","i":[-9223372036854775808,9223372036854775807],"z":null}',
            b'{"schema_version":"vector/v1","nested":{"z":2,"a":1}}',
            b'{"nested":{"a":1,"z":2},"schema_version":"vector/v1"}']
        bad = [b'{"schema_version":"vector/v1","x":1.0}', b'{"x":1,"x":2}',
               b'{"x":NaN}', b'{"x":9223372036854775808}', b'{"x":"\\ud800"}',
               b'{"schema_version":"vector/v1","x":-0}']
        proc = subprocess.run([binary], input=b'\n'.join(good + bad) + b'\n',
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True)
        rows = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual(len(rows), len(good) + len(bad))
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        fixture_key = Ed25519PrivateKey.from_private_bytes(bytes([7]) * 32)
        for raw, row in zip(good, rows):
            expected = signing_bytes(parse(raw))
            self.assertEqual(row['hex'], expected.hex())
            self.assertEqual(row['signature_hex'], fixture_key.sign(expected).hex())
        for row in rows[len(good):]:
            self.assertEqual(row, {'ok': False})


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    print(json.dumps({'schema_version': 'lab-case-command-result/v1',
        'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'checks': result.testsRun,
        'effect_state': 'owned-inert', 'cleanup': 'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
