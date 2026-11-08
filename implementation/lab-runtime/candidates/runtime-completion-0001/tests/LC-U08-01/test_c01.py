"""Exact emitted C01 bytes and acyclic fixture construction, no host authority."""
import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
S = Path(__file__).resolve().parents[2]
DEPS = Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps')
sys.path[:0] = [str(S/'contracts'), str(S/'selectors'), str(S/'tests/LC-U01-02'), str(DEPS)]
from lab_contracts.codec import canonical, parse, sha, Refusal
from lab_contracts.validation import validate
from lab_selectors.anchors import RootAnchor, AnchoredReader, identity
from lab_selectors.chains import namespace_chain
from test_contracts import value
ARGS = None
VECTOR = None

def original(name):
    raw = VECTOR[name].encode('utf-8')
    obj = parse(raw)
    if canonical(obj) != raw:
        raise Refusal('VECTOR_NONCANONICAL')
    return raw, obj

def binding(path, raw, root='fixture'):
    return dict(kind='execution', root_id=root, relative_path=path, sha256=sha(raw), size_bytes=len(raw))

class C01Tests(unittest.TestCase):
    def test_authoritative_pointer_dereferences_actual_closed_c01_manifest(self):
        p = validate('PointerRecord', VECTOR['pointer'])
        raw, manifest = original('pointer_target_original')
        validate('GenerationManifest', manifest)
        self.assertEqual(p['generation_manifest_binding']['sha256'], sha(raw))
        self.assertEqual(p['generation_manifest_binding']['size_bytes'], len(raw))
        self.assertTrue(p['generation_manifest_binding']['relative_path'].endswith('/c01-manifest.json'))
        self.assertEqual(p['logical_store_id'], manifest['logical_store_id'])
        self.assertEqual(p['sequence'], manifest['sequence'])
        self.assertEqual(p['predecessor_pointer_binding'], manifest['predecessor_pointer_binding'])

    def test_rich_manifest_is_separate_and_exactly_projects_original_fields(self):
        _, rich = original('writer_manifest_original')
        _, native = original('pointer_target_original')
        expected = dict(schema_version='lab-completion-generation-manifest/v1', logical_store_id=rich['store_id'], creation_instance_id=rich['creation_instance'], writer_epoch=rich['writer_epoch'], sequence=rich['sequence'], generation_id=rich['generation_id'], predecessor_pointer_binding=rich['predecessor_pointer_binding'], operation_fingerprint=rich['original_fingerprint'], member_bindings=[rich['members'][p] for p in sorted(rich['members'])], source_cut=rich['source_cut'], reader_inventory_binding=rich['reader_inventory_binding'], expected_replay_result_binding=rich['expected_replay_result_binding'])
        self.assertEqual(canonical(expected), canonical(native))
        with self.assertRaises(Refusal):
            validate('GenerationManifest', rich)

    def test_core_store_record_is_exact_declared_projection_not_profile_alias(self):
        raw, store = original('c01_store_original')
        validate('GenerationStoreSelection', store)
        _, profile = original('store_profile_original')
        self.assertEqual(profile['c01_selection_binding']['sha256'], sha(raw))
        self.assertEqual(profile['c01_selection_binding']['size_bytes'], len(raw))
        self.assertEqual(store['logical_store_id'], profile['store_id'])
        self.assertEqual(store['control_root_id'], profile['control_root_id'])
        self.assertEqual(store['broker_writer_domain'], profile['writer_domain'])
        self.assertEqual(store['canonical_member_inventory_binding'], profile['canonical_member_inventory_binding'])
        self.assertEqual(store['canonical_member_inventory_binding']['sha256'], sha(canonical(profile['member_inventory'])))
        with self.assertRaises(Refusal):
            validate('GenerationStoreSelection', profile)

    def test_store_core_review_activation_then_runtime_attachment_is_constructible(self):
        raw_store, store = original('c01_store_original')
        static_profile, profile = original('store_profile_original')
        static_policy, _ = original('control_policy_original')
        with tempfile.TemporaryDirectory(prefix='c01-fixture-', dir=ARGS.temp_root) as tmp:
            root = Path(tmp); bindings=[]
            def put(name, obj):
                raw=canonical(obj); (root/name).write_bytes(raw); b=binding(name,raw); bindings.append(b); return b
            sb=put('c01-store.json',store)
            core=value('NamespaceCore');core['store_selection_binding']=sb;cb=put('core.json',core)
            review=value('NamespaceReview');review.update(core_binding=cb,reviewer_identity='independent-fixture-reviewer',subject_bindings=[cb,sb]);rb=put('review.json',review)
            activation=value('NamespaceActivation');activation.update(core_binding=cb,review_binding=rb);ab=put('activation.json',activation)
            reader=AnchoredReader([RootAnchor('fixture',str(root),identity(root.stat()))],bindings)
            self.assertEqual(namespace_chain(reader,{'core':cb,'review':rb,'activation':ab})[0],core)
            runtime=dict(activation_binding=ab,store_id=store['logical_store_id'],instance_id=store['instance_id'],slot_epoch=1,principal_ref='fixture-principal',core_store_binding=sb,writer_profile_binding=binding('writer-profile.json',static_profile))
            self.assertEqual(runtime['activation_binding']['sha256'],sha(canonical(activation)))
            self.assertEqual(core['store_selection_binding']['sha256'],sha(raw_store))
            self.assertNotIn(ab['sha256'].encode(),static_profile)
            self.assertNotIn(ab['sha256'].encode(),static_policy)
            self.assertEqual(canonical(profile),static_profile)
            # Changing a selected original cannot inherit the earlier review.
            changed=copy.deepcopy(core);changed['store_selection_binding']['sha256']='f'*64
            (root/'core.json').write_bytes(canonical(changed))
            with self.assertRaises(Refusal):namespace_chain(reader,{'core':cb,'review':rb,'activation':ab})

    def test_coherent_pointer_repin_to_rich_profile_still_fails_target_schema(self):
        raw,rich=original('writer_manifest_original')
        pointer=copy.deepcopy(VECTOR['pointer'])
        pointer['generation_manifest_binding'].update(sha256=sha(raw),size_bytes=len(raw),relative_path='commit-operation-1/manifest.json')
        validate('PointerRecord',pointer)
        with self.assertRaises(Refusal):validate('GenerationManifest',rich)

    def test_closed_static_c01_store_rejects_runtime_backreferences(self):
        _,store=original('c01_store_original')
        for field in ('activation_binding','execution_scope','current_confirmation','review_binding'):
            changed=copy.deepcopy(store);changed[field]={'not_yet_created':True}
            with self.assertRaises(Refusal):validate('GenerationStoreSelection',changed)

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--vectors',type=Path,required=True);parser.add_argument('--temp-root',type=Path,required=True);ARGS=parser.parse_args()
    raw=ARGS.vectors.read_bytes()
    if len(raw)>1024*1024:raise Refusal('VECTOR_BOUND')
    VECTOR=parse(raw)
    if VECTOR.get('schema_version')!='lab-generation-c01-fixture-vector/v1':raise Refusal('VECTOR_SCHEMA')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(C01Tests))
    clean=not any(ARGS.temp_root.glob('c01-fixture-*'))
    print(json.dumps(dict(schema_version='lab-case-command-result/v1',result='PASS' if result.wasSuccessful() and clean else 'FAIL',checks=result.testsRun,effect_state='owned-inert',cleanup='clean' if clean else 'unknown')))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
