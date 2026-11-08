"""Real selected closure metadata and causal mutations; no member body reads."""
import bootstrap
from bootstrap import R, E, checked
import argparse, copy, hashlib, json, unittest
from pathlib import Path
from lab_contracts.codec import Refusal
from environment.body_json import parse_original
from environment.requirements import inspect_execution_requirements, ORIGINAL_BINDINGS, PRIOR_PATH

SELECTED = R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTED_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
RAW = checked(SELECTED, SELECTED_SHA)
PRIOR = checked(R/PRIOR_PATH, ORIGINAL_BINDINGS[PRIOR_PATH])

class RequirementsTests(unittest.TestCase):
    def inspect(self, value=None, digest=None):
        raw=RAW if value is None else (json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n').encode()
        return inspect_execution_requirements(raw,digest or hashlib.sha256(raw).hexdigest(),prior_raw=PRIOR,repository=str(R))

    def change(self, mutate):
        value=json.loads(RAW);mutate(value)
        with self.assertRaisesRegex(Refusal,'^EXECUTION_REQUIREMENTS_REFUSED$'):self.inspect(value)

    def test_full_actual720_inputs_and_order_preserved(self):
        result=self.inspect();original=json.loads(RAW)
        self.assertEqual(result['original_value'],original)
        self.assertEqual(sum(result['counts'].values()),720)
        self.assertEqual(result['counts'],{'wheel':8,'interpreter':1,'native-executable':1,'stdlib':687,'host-abi':23})
        self.assertEqual(result['member_bodies_read'],0);self.assertFalse(result['runtime_verified'])

    def test_coherent_repin_cannot_replace_external_selection(self):
        value=json.loads(RAW);value['supported_scope']='changed'
        with self.assertRaises(Refusal):self.inspect(value,SELECTED_SHA)

    def test_missing_dynamic_executable_origin(self):
        self.change(lambda v:v.update(inputs=[r for r in v['inputs'] if r['kind']!='native-executable']))

    def test_coherently_repinned_unused_stdlib_omission(self):
        def mutate(v):
            row=next(r for r in v['inputs'] if r['kind']=='stdlib' and r['destination'] not in v['elf_graph'])
            v['inputs'].remove(row)
        self.change(mutate)

    def test_coherently_repinned_abi_and_graph_omission(self):
        def mutate(v):
            row=next(r for r in v['inputs'] if r['kind']=='host-abi')
            v['inputs'].remove(row);v['elf_graph'].pop(row['destination'])
        self.change(mutate)

    def test_coherently_repinned_original_input_reordering(self):
        self.change(lambda v:v['inputs'].reverse())

    def test_unknown_origin_kind(self):
        self.change(lambda v:v['inputs'][0].update(kind='dynamic-plugin'))

    def test_unknown_requirement(self):self.change(lambda v:v.update(unknown_runtime_requirement=True))
    def test_host_environment_mismatch(self):self.change(lambda v:v['environment'].update(machine='aarch64'))
    def test_ambient_loader_fallback(self):self.change(lambda v:v['execution_configuration'].update(loader_cache=True))
    def test_duplicate_output(self):self.change(lambda v:v['inputs'].append(copy.deepcopy(v['inputs'][0])))
    def test_original_wheel_digest_substitution(self):self.change(lambda v:v['inputs'][0].update(sha256='0'*64))
    def test_original_proof_omission(self):self.change(lambda v:v['original_bindings'].pop())
    def test_original_proof_repin(self):self.change(lambda v:v['original_full_proof'].update(source_manifest_sha256='0'*64))
    def test_abi_transitive_origin_missing(self):self.change(lambda v:v['elf_graph'].pop('lib/abi/libc.so.6'))
    def test_unselected_elf_graph_member(self):self.change(lambda v:v['elf_graph'].update({'unselected':{'needed':[],'interpreter':None}}))
    def test_unknown_elf_interpreter(self):self.change(lambda v:v['elf_graph']['bin/python'].update(interpreter='other-loader'))
    def test_wheel_native_binding_changed(self):self.change(lambda v:v['wheel_elf_bindings'][0].update(sha256='0'*64))
    def test_wheel_native_graph_omission(self):self.change(lambda v:v['elf_graph'].pop(v['wheel_elf_bindings'][0]['destination']))
    def test_protected_looking_origin(self):
        def mutate(v):
            row=next(r for r in v['inputs'] if r['kind']=='stdlib')
            row.update(path='/usr/lib/python3.14/hidden.key',destination='lib/python3.14/hidden.key')
        self.change(mutate)
    def test_prior_original_selection_cannot_be_replaced(self):
        with self.assertRaises(Refusal):inspect_execution_requirements(RAW,SELECTED_SHA,prior_raw=b'{}',repository=str(R))

class OriginalJsonTests(unittest.TestCase):
    def test_finite_numbers_are_not_signed_control_i64(self):
        raw=b'{"n":9223372036854775808,"f":1.25,"negative_zero":-0.0}'
        value=parse_original(raw);self.assertEqual(value['n'],2**63);self.assertEqual(value['f'],1.25)
        self.assertEqual(raw,b'{"n":9223372036854775808,"f":1.25,"negative_zero":-0.0}')
    def test_lexically_finite_float_overflow_refuses(self):
        for raw in (b'1e309',b'-1e309',b'NaN',b'Infinity',b'{"x":[1e309]}'):
            with self.subTest(raw=raw),self.assertRaises(Refusal):parse_original(raw)
    def test_duplicates_and_unpaired_surrogate_refuse(self):
        for raw in (b'{"x":1,"x":2}',b'"\\ud800"'):
            with self.subTest(raw=raw),self.assertRaises(Refusal):parse_original(raw)
    def test_exact_unicode_combining_identity(self):
        value=parse_original('["é","é","研究😀"]'.encode())
        self.assertNotEqual(value[0],value[1]);self.assertEqual(value[2],'研究😀')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);args=p.parse_args()
    if args.temp_root!=E or not E.is_dir():raise ValueError('owned evidence root required')
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (RequirementsTests,OriginalJsonTests)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    checked(SELECTED,SELECTED_SHA);checked(R/PRIOR_PATH,ORIGINAL_BINDINGS[PRIOR_PATH])
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
