"""Negative guards over actual original signed source cuts and native events."""
import os
import unittest
from dataclasses import replace
from unittest.mock import patch

from mapping import *
from lab_runtime.common import RuntimeFault, sealed

FAULTS=(RepresentationFault,RuntimeFault)


class WithdrawalGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='cal-O02-withdrawal-guards-')
        cls.root=Path(cls.temp.name)
        cls.episode=Path(os.environ['O02_WITHDRAWAL_EPISODE'])
        cls.witness=parse((cls.episode/'witnesses.json').read_bytes())
        cls.archive=parse(original(cls.witness['source_archive_binding']))
        cls.cuts={k:restore_cut(cls.archive,k,cls.root/k,ReplayPins(**cls.witness['source_pins'][k])) for k in ('admit','withdraw')}
        cls.catalog_context=signed_catalog();catalog,operations=cls.catalog_context.__enter__()
        cls.adapter=CandidateRepresentationAdapter(catalog,operations)
        cls.translator=RichTranslation(cls.adapter,bind(PROFILE))
        cls.view=cls.adapter.represent({**bind(WORK),'kind':'work','version_ref':REF})
        cls.spec=cls.translator.node_spec(cls.view)

    @classmethod
    def tearDownClass(cls):
        for cut in cls.cuts.values():cut.closed=True
        cls.catalog_context.__exit__(None,None,None);cls.temp.cleanup()
        require(not cls.root.exists(), 'guard-owned source root retained')

    def native(self):
        store=NativeCandidateStore(self.translator,os.environ['O02_NATIVE_EXECUTABLE'],os.environ['O02_NATIVE_SHA256'])
        self.addCleanup(store.close)
        node,_=store.map_node(self.view)
        return store,node,SourceEligibilityMapping(store)

    def changed_spec(self, field, value):
        spec=copy.deepcopy(self.spec);spec['subject'][field]=value
        with self.assertRaises(RepresentationFault):joined_effect(spec,self.cuts['withdraw'])

    def test_scope_cannot_allow_revision(self):
        with self.assertRaises(RepresentationFault):replace(WithdrawalScope(),allowed_effects=('admit','revise','withdraw')).check()

    def test_scope_cannot_select_other_store_or_actor(self):
        for field,value in [('store_id','existing-store'),('operator_ref','role:owner'),('candidate_only',False)]:
            with self.subTest(field=field),self.assertRaises(RepresentationFault):replace(WithdrawalScope(),**{field:value}).check()

    def test_scope_requires_exact_work_bytes(self):
        record=parse(WORK.read_bytes());record['name']='changed'
        with self.assertRaises(RepresentationFault):WithdrawalScope().target('admit',record)

    def test_withdrawal_cannot_carry_record(self):
        with self.assertRaises(RepresentationFault):WithdrawalScope().target('withdraw',parse(WORK.read_bytes()))

    def test_verified_source_handle_cannot_be_fabricated(self):
        with self.assertRaises(RepresentationFault):VerifiedSourceCut(self.root,ReplayPins(**self.witness['source_pins']['admit']),{},WithdrawalScope(),None)

    def test_metadata_is_not_source_replay(self):
        with self.assertRaises(RepresentationFault):joined_effect(self.spec,{'source_posture':'local-withdrawn'})

    def test_source_kind_join_is_exact(self):self.changed_spec('kind','project')
    def test_source_identity_join_is_exact(self):self.changed_spec('identity','work:other')
    def test_source_version_join_is_exact(self):self.changed_spec('version_ref',REF+'-different')
    def test_source_record_digest_join_is_exact(self):self.changed_spec('carrier_bytes_sha256','0'*64)

    def test_source_carrier_join_is_exact(self):
        spec=copy.deepcopy(self.spec);spec['source_view']['carrier']['ref']='cal.artifact-type.method/v1'
        with self.assertRaises(RepresentationFault):joined_effect(spec,self.cuts['withdraw'])

    def test_original_record_cannot_be_replaced(self):
        spec=copy.deepcopy(self.spec);spec['source_view']['record']['name']='poison'
        with self.assertRaises(RepresentationFault):joined_effect(spec,self.cuts['withdraw'])

    def test_caller_cannot_change_replay_projection(self):
        cut=copy.copy(self.cuts['withdraw']);cut.data=copy.deepcopy(cut.data)
        cut.data['projection']['subjects'][REF]['effective_state']='local-admitted-current'
        with self.assertRaises(RepresentationFault):cut.effect()

    def test_original_byte_change_invalidates_cut(self):
        cut=self.cuts['withdraw'];path=cut.path/'transactions/0000000002.json';raw=path.read_bytes()
        try:
            path.write_bytes(raw+b' ')
            with self.assertRaises(RepresentationFault):cut.effect()
        finally:path.write_bytes(raw)

    def test_closed_source_cut_rejected(self):
        cut=copy.copy(self.cuts['withdraw']);cut.closed=True
        with self.assertRaises(RepresentationFault):cut.effect()

    def test_wrong_independent_head_pin_rejected(self):
        pins=replace(self.cuts['withdraw'].pins,expected_head='0'*64)
        with self.assertRaises(FAULTS):replay_cut(self.cuts['withdraw'].path,pins,WithdrawalScope())

    def test_wrong_independent_profile_manifest_rejected(self):
        pins=replace(self.cuts['withdraw'].pins,manifest_sha256='0'*64)
        with self.assertRaises(RepresentationFault):replay_cut(self.cuts['withdraw'].path,pins,WithdrawalScope())

    def test_forged_signature_rejected_by_full_replay(self):
        with tempfile.TemporaryDirectory(prefix='cal-O02-invalid-signature-') as temp:
            dest=Path(temp)/'source';shutil.copytree(self.cuts['withdraw'].path,dest)
            txpath=dest/'transactions/0000000002.json';tx=parse(txpath.read_bytes())
            tx['approval']['signature']='0'*128;tx=sealed({k:v for k,v in tx.items() if k!='digest'})
            txpath.write_bytes(encoded(tx))
            head=parse((dest/'HEAD.json').read_bytes());head['transaction_digest']=tx['digest']
            (dest/'HEAD.json').write_bytes(encoded(sealed({k:v for k,v in head.items() if k!='digest'})))
            pins=replace(self.cuts['withdraw'].pins,expected_head=tx['digest'])
            with self.assertRaisesRegex(FAULTS,'signature'):replay_cut(dest,pins,WithdrawalScope())

    def test_source_archive_path_closure_rejected(self):
        archive=copy.deepcopy(self.archive);archive['files']['../key.pem']={}
        with self.assertRaises(RepresentationFault):restore_cut(archive,'withdraw',self.root/'bad-path',self.cuts['withdraw'].pins)

    def test_private_archive_posture_rejected(self):
        archive=copy.deepcopy(self.archive);archive['private_key_included']=True
        with self.assertRaises(RepresentationFault):restore_cut(archive,'withdraw',self.root/'bad-private',self.cuts['withdraw'].pins)

    def test_withdrawal_requires_prior_exact_mapping(self):
        native,node,mapper=self.native();before=native.files()
        with self.assertRaises(RepresentationFault):mapper.apply(node,self.cuts['withdraw'])
        self.assertEqual(before,native.files())

    def test_duplicate_mapping_does_not_append(self):
        native,node,mapper=self.native();mapper.apply(node,self.cuts['admit']);mapper.apply(node,self.cuts['withdraw'])
        before=native.files();self.assertTrue(mapper.apply(node,self.cuts['withdraw'])['idempotent'])
        self.assertEqual(before,native.files())

    def test_withdrawn_and_stale_source_use_rejected(self):
        native,node,mapper=self.native();mapper.apply(node,self.cuts['admit'])
        self.assertEqual(mapper.current_source(node,self.cuts['admit']),parse(WORK.read_bytes()))
        mapper.apply(node,self.cuts['withdraw'])
        for cut in self.cuts.values():
            with self.subTest(cut=cut.data['head']['sequence']),self.assertRaises(RepresentationFault):mapper.current_source(node,cut)
        self.assertEqual(mapper.historical_representation(node)['state']['lifecycle'],'active')
        self.assertEqual(len(native.semantic_events),1)

    def test_exact_governance_tuple_cannot_change(self):
        native,node,mapper=self.native();semantic=native.latest_semantic(node)
        state=governance_state(native.latest_governance(semantic)['complete_resulting_governance_state'],self.cuts['admit'].effect())
        state['semantic_ref']['semantic_event_digest']='0'*64
        with self.assertRaises(RepresentationFault):native.governance_draft(semantic,state)

    def test_source_configuration_predecessor_join_rejected(self):
        native,node,mapper=self.native();mapper.apply(node,self.cuts['admit'])
        mapper.effects[node]['config_sha256']='0'*64;before=native.files()
        with self.assertRaises(RepresentationFault):mapper.apply(node,self.cuts['withdraw'])
        self.assertEqual(before,native.files())

    def test_uncertain_native_append_blocks_redispatch(self):
        native,node,mapper=self.native()
        with patch.object(native,'append',side_effect=RepresentationFault('controlled uncertain append')):
            with self.assertRaises(RepresentationFault):mapper.apply(node,self.cuts['admit'])
        self.assertIn(node,mapper.uncertain)
        with self.assertRaisesRegex(RepresentationFault,'uncertain'):mapper.apply(node,self.cuts['admit'])
        self.assertEqual(len(native.governance_events),1)

    def test_withdrawal_does_not_modify_native_semantics(self):
        native,node,mapper=self.native();mapper.apply(node,self.cuts['admit'])
        before={k:v for k,v in native.files().items() if k.startswith('semantic/')}
        mapper.apply(node,self.cuts['withdraw'])
        self.assertEqual(before,{k:v for k,v in native.files().items() if k.startswith('semantic/')})
        self.assertEqual(len(native.read()['cut']['subjects']),1)

    def test_cached_eligibility_cannot_restore_withdrawn_source(self):
        native,node,mapper=self.native();mapper.apply(node,self.cuts['admit']);mapper.apply(node,self.cuts['withdraw'])
        mapper.effects[node]=self.cuts['admit'].effect()
        with self.assertRaisesRegex(RepresentationFault,'cached state'):mapper.current_source(node,self.cuts['admit'])

    def test_native_source_specification_cannot_be_changed(self):
        native,node,mapper=self.native();native.specs[node]['properties']['version_ref']=REF+'-other'
        before=native.files()
        with self.assertRaisesRegex(RepresentationFault,'specification changed'):mapper.apply(node,self.cuts['admit'])
        self.assertEqual(before,native.files())


if __name__=='__main__':unittest.main()
