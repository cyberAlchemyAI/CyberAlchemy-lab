"""Actual signed Project State/native reader integration and custody checks."""
import base64
import copy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from local_context import *
from custody import ReadCustodian
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.replay import ReplayPins
sys.path.insert(0,str(SOURCE_CONTEXT/'tests'))
from native_fixture import fixture

MANIFEST=HERE/'packages/0001/generator-manifest.json'
GENERATOR_SHA=os.environ['R03_GENERATOR_SHA']
ARCHIVE=ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
ARCHIVE_SHA='03850c8aa4cf7a994f3ce66c25cb68d4567c170ed38e40dc24e115a3e900f944'
NATIVE=Path('/tmp/cal-W07-native-build-5nic80ww/debug/lab-context-native-reader')
NATIVE_SHA='62f4244cfe23b8f0252e99b3778ed9a78807a2e67657f069882c823ed97e7f59'
PRINCIPAL='principal:R03-session-foundation-reader'
SCOPE='project:cyberalchemy-v2-to-lab-migration'


def source_selection():
    row=next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
    return row,capture(select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']}))


def restore(root):
    raw=regular(ARCHIVE);require(byte_digest(raw)==ARCHIVE_SHA,'original C12 archive differs')
    archive=loads(raw);root.mkdir(mode=0o700)
    require(set(archive['files'])=={'config.json','baseline.json','HEAD.json','transactions/0000000000.json','transactions/0000000001.json'},'archive closure differs')
    for name,row in archive['files'].items():
        raw=base64.b64decode(row['base64_original_bytes'],validate=True)
        require(byte_digest(raw)==row['sha256'],'original archive bytes differ')
        file=root/name
        if not file.parent.exists():file.parent.mkdir(mode=0o700)
        file.write_bytes(raw);file.chmod(0o600)
    store=VerifiedLegacyReadStore(root,ROOT,ROOT,ReplayPins(**archive['project_pins']))
    store.verify_full(require_current=True)
    return store


def actual_consumer(store,snapshot,native,ttl=900):
    row,_=source_selection()
    return ContextSession(store,snapshot,native,generator_manifest=MANIFEST,
        generator_pins=GeneratorPins(GENERATOR_SHA,IMPLEMENTATION_VERSION),
        owner_ref='principal:repository-owner@candidate.1',context_ref='context:cyberalchemy-v2-to-lab-migration',scope_ref=SCOPE,
        capability_ref='product-capability:cyberalchemy-lab:governed-knowledge-lifecycle',
        expected_profile_sha256=row['profile_sha256'],expected_snapshot_digest=snapshot['snapshot_digest'],
        subject_ref=store.replay(require_current=True)['projection']['state']['node_id'],references={},ttl=ttl)


def setup(root):
    require(byte_digest(regular(NATIVE))==NATIVE_SHA,'independent native executable pin differs')
    store=restore(root/'source');row,snapshot=source_selection()
    (root/'native').mkdir(mode=0o700)
    native=fixture(root/'native',NATIVE,snapshot)
    # Fixture is protected development input; never a public artifact export.
    for p in (root/'native').rglob('*'):p.chmod(0o700 if p.is_dir() else 0o600)
    return store,snapshot,native


def custodian(root,store,snapshot,native,factory=None):
    cut={'ref':'C12:'+store.pins.expected_head,'sha256':store.pins.expected_head}
    control={'generator':GENERATOR_SHA,'native':asdict(native.pins),'root_kind':'ProjectState',
        'source_snapshot':snapshot['snapshot_digest'],'ttl_seconds':900,'assignment':None,'max_items':32,'max_bytes':1048576}
    return ReadCustodian(root,principal_ref=PRINCIPAL,scope_ref=SCOPE,source_cut_binding=cut,
        consumer_control_binding={'ref':'read-consumer-control','sha256':digest(control)},
        source_guard=lambda:verify_generator(MANIFEST,GeneratorPins(GENERATOR_SHA,IMPLEMENTATION_VERSION)),
        factory=factory or (lambda:actual_consumer(store,snapshot,native)))


class FoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owned=TemporaryDirectory(prefix='cal-R03-context-foundation-');cls.addClassCleanup(cls.owned.cleanup)
        cls.root=Path(cls.owned.name);cls.store,cls.snapshot,cls.native=setup(cls.root)
        cls.source_before={p.relative_to(cls.store.path).as_posix():byte_digest(regular(p)) for p in cls.store.path.rglob('*') if p.is_file()}

    def setUp(self):
        self.temp=TemporaryDirectory(prefix='cal-R03-custody-test-');self.addCleanup(self.temp.cleanup)
        self.journal=Path(self.temp.name);self.c=custodian(self.journal,self.store,self.snapshot,self.native)
        self.addCleanup(self.c.close)

    def open(self,key='first'):
        return self.c.open(PRINCIPAL,key)

    def test_selected_environment_generator_successor(self):
        self.assertEqual(environment()['packages']['jsonschema'],'4.23.0')
        m=verify_generator(MANIFEST,GeneratorPins(GENERATOR_SHA,IMPLEMENTATION_VERSION))
        self.assertEqual(m['implementation_version_ref'],'implementation:lab-committed-context-generator@candidate.2')
        self.assertEqual(load(ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json')['environment']['packages']['jsonschema'],'4.19.2')

    def test_actual_signed_state_and_native_context(self):
        x=self.open();s=self.c.live[x['session_ref']];pack=s.context()
        self.assertEqual(pack['project_state'],self.store.verify_full()['projection']['state'])
        self.assertEqual(pack['project_state']['node_id'],'project-state:c12-source-audit-0002:1')
        self.assertEqual(pack['head'],self.store.pins.expected_head)
        self.assertEqual(pack['native_ontology']['cut']['semantic_cursor'],3)
        self.assertEqual(len(pack['native_ontology']['governed_nodes']),2)
        self.assertTrue(all(r['identity']['ontology_id']=='lab-c08-native-fixture' for r in pack['native_references']))
        for kind,record in pack['candidate_artifacts'].items():validate(record,kind,self.snapshot)

    def test_original_transaction_custody_separate_from_reconstructed_body(self):
        x=self.open();pack=self.c.live[x['session_ref']].context()
        rows=[r for r in pack['source_material_provenance'] if r['reference_class']=='local-committed-original-bytes']
        self.assertTrue(rows)
        for row in rows:
            raw=regular(self.store.path/row['path']);record=pointer(loads(raw),row['selector'])
            self.assertEqual(byte_digest(raw),row['original_file_sha256'])
            self.assertEqual(byte_digest(encoded(record)),row['reconstructed_body_sha256'])
            self.assertNotEqual(row['original_file_sha256'],row['reconstructed_body_sha256'])

    def test_unassigned_reader_never_reuses_old_assignment(self):
        x=self.open();pack=self.c.live[x['session_ref']].context()
        self.assertEqual(x['assignment_authority'],'unresolved');self.assertEqual(x['action_permission'],'none')
        self.assertFalse(any(r.get('role')=='assignment_ref' for r in pack['resolved_references']))
        self.assertTrue(any(r['reference']=='assignment_ref' for r in pack['reference_diagnostics']))

    def test_private_note_is_RAM_only(self):
        x=self.open();session=self.c.live[x['session_ref']]
        token='R03 private RAM marker '+os.urandom(16).hex()
        self.c.note(PRINCIPAL,x['session_ref'],token)
        self.assertEqual(session.core._memory,[token])
        self.assertNotIn(token,json.dumps(session.context()))
        self.assertNotIn(token,json.dumps(self.c.inspect(PRINCIPAL,x['session_ref'])))
        self.assertFalse(any(token.encode() in regular(p) for p in self.journal.iterdir()))
        result=self.c.close_consumer(PRINCIPAL,x['session_ref'],x['metadata_binding'])
        self.assertTrue(result['disposal_observed']);self.assertEqual(result['posture'],'closed');self.assertEqual(session.core._memory,[])

    def test_fresh_key_fresh_instance_and_empty_memory(self):
        first=self.open();s=self.c.live[first['session_ref']];self.c.note(PRINCIPAL,first['session_ref'],'private scratch')
        self.c.close_consumer(PRINCIPAL,first['session_ref'],first['metadata_binding'])
        second=self.open('second')
        self.assertNotEqual(first['session_ref'],second['session_ref']);self.assertNotEqual(first['agent_instance_ref'],second['agent_instance_ref'])
        self.assertEqual(self.c.live[second['session_ref']].core._memory,[])
        self.assertEqual(s.core._memory,[])

    def test_same_key_never_recreates_consumer(self):
        first=self.open();self.assertEqual(self.open(),first)
        self.c.close_consumer(PRINCIPAL,first['session_ref'],first['metadata_binding'])
        self.assertEqual(self.open()['posture'],'closed');self.assertEqual(self.c.live,{})

    def test_other_principal_cannot_inspect_or_close_or_note(self):
        x=self.open()
        for fn in [lambda:self.c.inspect('principal:other',x['session_ref']),
            lambda:self.c.close_consumer('principal:other',x['session_ref'],x['metadata_binding']),
            lambda:self.c.note('principal:other',x['session_ref'],'private')]:
            with self.assertRaisesRegex(Exception,'principal scope'):fn()
        self.assertEqual(self.c.inspect(PRINCIPAL,x['session_ref'])['posture'],'active')

    def test_wrong_exact_close_binding_no_disposal(self):
        x=self.open()
        with self.assertRaisesRegex(Exception,'binding differs'):
            self.c.close_consumer(PRINCIPAL,x['session_ref'],{**x['metadata_binding'],'sha256':'0'*64})
        self.assertEqual(self.c.inspect(PRINCIPAL,x['session_ref'])['posture'],'active')

    def test_unknown_consumer_is_scoped_not_found(self):
        with self.assertRaisesRegex(Exception,'principal scope'):self.c.inspect(PRINCIPAL,'protocol:ephemeral-agent-session:00000000-0000-0000-0000-000000000000')

    def test_close_disposes_without_source_freshness(self):
        x=self.open();s=self.c.live[x['session_ref']];self.c.note(PRINCIPAL,x['session_ref'],'private stale scratch')
        s.core.clock=lambda:s.core.deadline+1
        self.c.guard=lambda:(_ for _ in ()).throw(ValueError('source stale'))
        result=self.c.close_consumer(PRINCIPAL,x['session_ref'],x['metadata_binding'])
        self.assertEqual(result['posture'],'closed');self.assertEqual(s.core._memory,[])

    def test_expiry_inspection_observes_disposal(self):
        x=self.open();s=self.c.live[x['session_ref']];self.c.note(PRINCIPAL,x['session_ref'],'private expiry scratch')
        s.core.clock=lambda:s.core.deadline+1
        result=self.c.inspect(PRINCIPAL,x['session_ref'])
        self.assertEqual(result['posture'],'expired');self.assertTrue(result['disposal_observed']);self.assertEqual(s.core._memory,[])

    def test_source_guard_invalidation_disposes_and_retains_gap(self):
        x=self.open();s=self.c.live[x['session_ref']];self.c.note(PRINCIPAL,x['session_ref'],'private invalidation scratch')
        self.c.guard=lambda:(_ for _ in ()).throw(ValueError('source code changed'))
        result=self.c.inspect(PRINCIPAL,x['session_ref'])
        self.assertEqual(result['posture'],'indeterminate');self.assertTrue(result['disposal_observed']);self.assertEqual(s.core._memory,[])

    def test_native_source_byte_drift_disposes(self):
        x=self.open();s=self.c.live[x['session_ref']]
        file=next(self.native.semantic_directory.iterdir());raw=regular(file)
        try:
            file.write_bytes(raw+b'\n')
            result=self.c.inspect(PRINCIPAL,x['session_ref'])
            self.assertEqual(result['posture'],'indeterminate');self.assertTrue(result['disposal_observed']);self.assertTrue(s.closed)
        finally:file.write_bytes(raw)

    def test_actual_transaction_byte_drift_disposes(self):
        with TemporaryDirectory(prefix='cal-R03-drift-source-') as tmp:
            store=restore(Path(tmp)/'source');self.c.close()
            self.c=custodian(self.journal,store,self.snapshot,self.native)
            x=self.open();s=self.c.live[x['session_ref']]
            file=store.path/'transactions/0000000001.json';file.write_bytes(regular(file)+b'\n')
            result=self.c.inspect(PRINCIPAL,x['session_ref'])
            self.assertEqual(result['posture'],'indeterminate');self.assertTrue(result['disposal_observed']);self.assertEqual(s.core._memory,[])

    def test_exclusive_custody_lock(self):
        with self.assertRaises(BlockingIOError):custodian(self.journal,self.store,self.snapshot,self.native)

    def test_symlink_root_rejected(self):
        with TemporaryDirectory(prefix='cal-R03-custody-link-') as tmp:
            link=Path(tmp)/'link';link.symlink_to(self.journal,target_is_directory=True)
            with self.assertRaisesRegex(Exception,'canonical custody'):custodian(link,self.store,self.snapshot,self.native)

    def test_permissive_root_rejected(self):
        with TemporaryDirectory(prefix='cal-R03-mode-') as tmp:
            root=Path(tmp);root.chmod(0o755)
            with self.assertRaisesRegex(Exception,'private development'):custodian(root,self.store,self.snapshot,self.native)

    def test_metadata_private_permissions(self):
        self.open()
        self.assertTrue(all(p.stat().st_mode & 0o777==0o600 for p in self.journal.iterdir()))

    def test_metadata_byte_drift_detected(self):
        x=self.open();self.c.close_consumer(PRINCIPAL,x['session_ref'],x['metadata_binding'])
        p=self.journal/x['metadata_binding']['ref'];p.write_bytes(regular(p)+b'\n')
        with self.assertRaisesRegex(Exception,'byte drift'):self.c.inspect(PRINCIPAL,x['session_ref'])

    def test_closed_revision_cannot_resume(self):
        x=self.open();closed=self.c.close_consumer(PRINCIPAL,x['session_ref'],x['metadata_binding'])
        p=self.journal/closed['metadata_binding']['ref'];row=loads(regular(p));row['sequence']=2;row['previous_binding']=closed['metadata_binding']
        q=self.journal/p.name.replace('-0001.json','-0002.json');q.write_bytes(encoded(row));q.chmod(0o600)
        with self.assertRaisesRegex(Exception,'cannot resume'):self.c.inspect(PRINCIPAL,x['session_ref'])

    def test_allocated_failure_cannot_redispatch(self):
        self.c.factory=lambda:(_ for _ in ()).throw(ValueError('failure after durable claim'))
        with self.assertRaisesRegex(ValueError,'durable claim'):self.open()
        self.c.factory=lambda:actual_consumer(self.store,self.snapshot,self.native)
        with self.assertRaisesRegex(Exception,'without redispatch'):self.open()
        self.assertEqual(self.c.live,{})

    def test_cleanup_erases_RAM_even_if_metadata_corrupt(self):
        x=self.open();s=self.c.live[x['session_ref']];self.c.note(PRINCIPAL,x['session_ref'],'private corruption scratch')
        (self.journal/x['metadata_binding']['ref']).write_bytes(b'{}\n')
        with self.assertRaises(Exception):self.c.close()
        self.assertEqual(s.core._memory,[]);self.assertTrue(s.closed);self.assertTrue(self.c.closed)

    def test_source_store_bytes_unchanged(self):
        self.open()
        current={p.relative_to(self.store.path).as_posix():byte_digest(regular(p)) for p in self.store.path.rglob('*') if p.is_file()}
        self.assertEqual(current,self.source_before)

    def test_no_action_authority_methods(self):
        for name in ['apply','authorize','admit','execute','publish','grant','resume']:
            self.assertFalse(hasattr(self.c,name))


if __name__=='__main__':
    unittest.main(verbosity=2)
