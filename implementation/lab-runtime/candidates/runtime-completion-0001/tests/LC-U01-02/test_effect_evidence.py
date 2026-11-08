"""Public effect-evidence fixtures. No real permission, custody or effects."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from test_contracts import value
from lab_contracts.codec import Refusal, canonical, parse, sha
from lab_contracts.validation import validate
from lab_selectors.effect_evidence import validate_and_retain, EffectEvidenceRefusal
from lab_selectors.authority import BoundedProvider, authorized_execute
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity
from lab_selectors.runner import exclusive_bytes


def bind(raw, name, kind='evidence'):
    return {'kind': kind, 'root_id': 'fixture', 'relative_path': name,
            'sha256': sha(raw), 'size_bytes': len(raw)}


class Fixture:
    def __init__(self):
        enrollment = bind(b'fixture enrollment, not actual authority', 'enrollment')
        gate_input = bind(b'public admission receipt fixture', 'admission')
        selection = bind(b'fixture selection', 'selection', 'execution')
        self.command = value('SelectedCommand')
        self.request = {'schema_version': 'lab-completion-gate-request/v1', 'unit': 'fixture-unit',
            'command_sha256': 'a'*64, 'required_gates': ['G01'], 'effects': [],
            'selection_binding': selection, 'gate_input_bindings': [gate_input],
            'produced_terminal_checks': [{'gate': 'G01', 'requirement': 'activation'}],
            'gate_checks': [{'gate': 'G01', 'start_inputs': ['administrator_identity'],
                'before_effect': ['current_permission'], 'terminal_outputs': ['activation'],
                'consumed_outputs': [{'producer': 'predecessor-unit', 'output': 'namespace-review'}]}]}
        self.endorsement = {'issuer_enrollment_binding': enrollment, 'gate_input_bindings': [gate_input]}
        self.result = {'schema_version': 'lab-case-command-result/v1', 'result': 'PASS',
                       'checks': 1, 'effect_state': 'observed', 'cleanup': 'retained-owned'}
        self.proof = {'schema_version': 'lab-completion-gate-verification/v1',
            'request_sha256': sha(canonical(self.request)), 'verified_gate_ids': ['G01'],
            'original_input_bindings': [gate_input], 'enrollment_binding': enrollment,
            'effect_envelope': [], 'verdict': 'PERMITTED', 'currentness_witness_binding': None,
            'admission_checks': [{'gate': 'G01', 'phase': phase, 'requirement': req,
                'producer': producer, 'evidence_bindings': [gate_input]} for phase, req, producer in [
                    ('start_inputs', 'administrator_identity', None), ('before_effect', 'current_permission', None),
                    ('consumed_outputs', 'namespace-review', 'predecessor-unit')]]}
        self.docs = {}
        for role in ['currentness', 'effect', 'prestate', 'poststate', 'cleanup', 'output']:
            self.docs[role] = {'schema_version': 'lab-completion-public-effect-receipt/v1',
                'role': role, 'request_sha256': self.proof['request_sha256'], 'command_sha256': self.request['command_sha256'],
                'selection_binding': selection, 'enrollment_binding': enrollment, 'effect_envelope': [],
                'original_input_bindings': [gate_input], 'subject_bindings': [],
                'result': 'PASS', 'effect_state': 'observed', 'cleanup': 'retained-owned'}
        self.proof['currentness_witness_binding'] = bind(canonical(self.docs['currentness'])+b'\n', 'currentness.json')
        self.docs['gate-verification'] = self.proof
        self.refresh()

    def refresh(self):
        originals = []
        slots = []
        for role, doc in self.docs.items():
            raw = canonical(doc)+b'\n'
            b = bind(raw, role+'.json')
            originals.append({'slot_id': role, 'binding': b, 'original_utf8': raw.decode()})
            slots.append({'id': role, 'role': role, 'locator': {'kind': 'evidence', 'root_id': 'fixture',
                'relative_path': role+'.json', 'max_bytes': 8192}, 'subject_locators': []})
        self.command['effect_evidence_contract'] = {'schema_version': 'lab-completion-effect-evidence-contract/v1',
            'slots': slots, 'max_total_bytes': 32768, 'disclosure': 'reviewed-public-metadata-only',
            'retention': 'exact-original-bytes-in-owned-attempt'}
        post = next(o['binding'] for o in originals if o['slot_id']=='poststate')
        self.evidence = {'schema_version': 'lab-completion-effect-evidence/v1', 'originals': originals,
                        'terminal_checks': [{'gate': 'G01', 'requirement': 'activation', 'evidence_bindings': [post]}]}

    def verify(self, retain):
        return validate_and_retain(self.evidence, self.proof, self.result, self.request,
                                   self.command, self.endorsement, retain)


class EffectEvidenceTests(unittest.TestCase):
    def test_exact_original_bytes_persist_and_no_replace(self):
        f = Fixture()
        with tempfile.TemporaryDirectory(prefix='owned-test-evidence-', dir=Path(__file__).parent) as tmp:
            fd = os.open(tmp, os.O_RDONLY | os.O_DIRECTORY)
            try:
                def retain(n, raw):
                    name = str(n)+'.json'; exclusive_bytes(fd, name, raw); return bind(raw, name)
                detail = f.verify(retain)
                self.assertEqual(len(detail['retained_originals']), 7)
                for n, original in enumerate(f.evidence['originals'], 1):
                    self.assertEqual((Path(tmp)/(str(n)+'.json')).read_bytes(), original['original_utf8'].encode())
                with self.assertRaisesRegex(EffectEvidenceRefusal, 'RECEIPT_RETENTION_UNKNOWN'):
                    f.verify(retain)
            finally:
                os.close(fd)

    def test_missing_duplicate_extra_roles_refuse_before_storage(self):
        for mode in ('missing','duplicate','extra','role','locator'):
            f=Fixture(); called=[]
            if mode=='missing': f.evidence['originals'].pop()
            elif mode=='duplicate': f.evidence['originals'][-1]=copy.deepcopy(f.evidence['originals'][0])
            elif mode=='extra': f.evidence['originals'].append(copy.deepcopy(f.evidence['originals'][0]))
            elif mode=='role': f.command['effect_evidence_contract']['slots'][-1]['role']='output'
            else:f.command['effect_evidence_contract']['slots'][-1]['locator']=copy.deepcopy(f.command['effect_evidence_contract']['slots'][0]['locator'])
            with self.subTest(mode=mode), self.assertRaises(Refusal): f.verify(lambda *args: called.append(args))
            self.assertEqual(called, [])

    def test_original_substitution_disclosure_and_aggregate_bounds(self):
        for mode in ('hash','locator','private','aggregate','unknown-field','subject'):
            f=Fixture(); called=[]
            if mode=='hash': f.evidence['originals'][0]['binding']['sha256']='b'*64
            elif mode=='locator': f.evidence['originals'][0]['binding']['relative_path']='unreviewed.json'
            elif mode=='private': f.evidence['originals'][0]['binding']['kind']='protected-input'
            elif mode=='aggregate': f.command['effect_evidence_contract']['max_total_bytes']=1
            else:
                if mode=='unknown-field':f.docs['effect']['body']='not allowed'
                else:f.docs['effect']['subject_bindings']=[bind(b'private metadata','unselected')]
                f.refresh()
            with self.subTest(mode=mode), self.assertRaises(Refusal): f.verify(lambda *args: called.append(args))
            self.assertEqual(called, [])

    def test_valid_negative_receipts_retained_without_positive_eligibility(self):
        for role, field, val, expected in [('poststate','result','FAIL','FAIL'),('cleanup','cleanup','unknown','UNKNOWN'),
                                  ('effect','effect_state','none','UNKNOWN'),('poststate','result','UNKNOWN','UNKNOWN')]:
            f=Fixture();f.docs[role][field]=val;f.refresh();stored=[]
            with self.subTest(role=role,field=field):
                detail=f.verify(lambda n,b:(stored.append(b) or bind(b,str(n)+'.json')))
                self.assertEqual(detail['evidence_result'],expected)
                self.assertEqual(len(stored),7)
                self.assertIn(canonical(f.docs[role])+b'\n', stored)

    def test_wrong_scope_is_refused_before_any_storage(self):
        f=Fixture();f.docs['output']['command_sha256']='b'*64;f.refresh();stored=[]
        with self.assertRaises(Refusal):f.verify(lambda *args:stored.append(args))
        self.assertEqual(stored,[])

    def test_admission_excludes_future_terminal_and_covers_predecessors(self):
        for mode in ('future','missing','ownfuture','terminal-as-admission'):
            f=Fixture()
            if mode=='future': f.proof['admission_checks'][0]['phase']='terminal_outputs'
            elif mode=='missing': f.proof['admission_checks'].pop()
            elif mode=='ownfuture':f.request['gate_checks'][0]['consumed_outputs'][0]['producer']='fixture-unit'
            else:f.proof['admission_checks'][0]['requirement']='activation'
            f.refresh()
            with self.subTest(mode=mode),self.assertRaises(Refusal):f.verify(lambda *args: None)

    def test_setup_does_not_claim_future_unit_terminal(self):
        f=Fixture(); f.request['produced_terminal_checks']=[]
        f.proof['request_sha256']=sha(canonical(f.request))
        for doc in f.docs.values():doc['request_sha256']=f.proof['request_sha256']
        f.proof['currentness_witness_binding']=bind(canonical(f.docs['currentness'])+b'\n','currentness.json')
        f.refresh(); f.evidence['terminal_checks']=[]
        detail=f.verify(lambda n,b:bind(b,str(n)+'.json'))
        self.assertEqual(detail['terminal_checks'],[])

    def test_terminal_outputs_require_actual_retained_output_receipts(self):
        for mode in ('missing','input','wrong_requirement'):
            f=Fixture()
            if mode=='missing':f.evidence['terminal_checks']=[]
            elif mode=='input':f.evidence['terminal_checks'][0]['evidence_bindings']=f.proof['original_input_bindings']
            else:f.evidence['terminal_checks'][0]['requirement']='invented'
            with self.subTest(mode=mode),self.assertRaises(Refusal):f.verify(lambda *args: None)

    def test_currentness_and_gate_original_must_match(self):
        for mode in ('currentness','gate'):
            f=Fixture()
            if mode=='currentness':f.proof['currentness_witness_binding']['sha256']='b'*64;f.refresh()
            else:
                f.docs['gate-verification']=dict(f.proof,request_sha256='b'*64);f.refresh()
            with self.subTest(mode=mode),self.assertRaises(Refusal):f.verify(lambda *args: None)

    def test_empty_or_unknown_pass_universally_refused(self):
        for field,val in [('checks',0),('cleanup','unknown'),('effect_state','unknown')]:
            result=Fixture().result;result[field]=val
            with self.subTest(field=field),self.assertRaises(Refusal):validate('CommandResult',result)

    def test_bounded_transport_receipt_retention_failure_preserves_observed(self):
        f=Fixture()
        with tempfile.TemporaryDirectory(prefix='owned-test-transport-',dir=Path(__file__).parent) as tmp:
            root=Path(tmp);reply={'schema_version':'lab-actual-authority-provider-result/v1',
                'gate_verification':f.proof,'command_result':f.result,'effect_evidence':f.evidence}
            raw=canonical(reply)
            script=root/'adapter.py';script.write_text('import sys\nsys.stdin.buffer.read()\nsys.stdout.buffer.write('+repr(raw)+')\n')
            enrollment=root/'enrollment';enrollment.write_bytes(b'fixture enrollment, not actual authority')
            sb=bind(script.read_bytes(),'adapter.py','execution');eb=bind(enrollment.read_bytes(),'enrollment')
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],[sb,eb])
            endorsement={**f.endorsement,'source_bindings':[sb],'provider_binding':sb}
            launch={'argv':[str(Path(sys.executable).resolve()),'-B',str(script)],'environment':[],
                    'cwd':str(root),'timeout_ms':2000,'max_output_bytes':65536}
            endorsement['repository']=str(root)
            provider=BoundedProvider(endorsement,reader,launch)
            f.command.update(timeout_ms=2000,max_output_bytes=65536)
            dispatched=[]
            def failed_store(*args):raise OSError('owned storage failed')
            with self.assertRaises(EffectEvidenceRefusal) as caught:
                authorized_execute(provider,f.request,f.command,endorsement,lambda:dispatched.append(True),failed_store)
            self.assertEqual(caught.exception.effect_state,'observed')
            self.assertEqual(dispatched,[True])
            stored=[]
            result, detail=authorized_execute(provider,f.request,f.command,endorsement,lambda:dispatched.append(True),
                lambda n,b: (stored.append(b) or bind(b,str(n)+'.json')))
            self.assertEqual(result,f.result);self.assertEqual(len(stored),7)
            self.assertEqual(detail['gate_verification'],f.proof)
            # A launched but unbound claim of no effect cannot clear uncertainty.
            reply['command_result']['effect_state']='none'
            reply['gate_verification']['request_sha256']='b'*64
            script.write_text('import sys\nsys.stdin.buffer.read()\nsys.stdout.buffer.write('+repr(canonical(reply))+')\n')
            sb=bind(script.read_bytes(),'adapter.py','execution')
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],[sb,eb])
            endorsement.update(source_bindings=[sb],provider_binding=sb)
            provider=BoundedProvider(endorsement,reader,launch)
            with self.assertRaises(EffectEvidenceRefusal) as caught:
                authorized_execute(provider,f.request,f.command,endorsement,lambda:dispatched.append(True),failed_store)
            self.assertEqual(caught.exception.effect_state,'unknown')
            self.assertEqual(len(dispatched),3)



if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
